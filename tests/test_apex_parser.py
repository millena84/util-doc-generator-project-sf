"""Parser estrutural de classes Apex (.cls) — fixtures SIMULADAS em tests/fixtures/source/classes."""

import json
import unittest

from tests.helpers import FIXTURES
from salesforce_docs.parsing.apex_parser import canonical_interface, neutralize, parse_apex_source

CLASSES = FIXTURES / "source" / "classes"


def parse(name):
    return parse_apex_source((CLASSES / f"{name}.cls").read_text())


class NeutralizeTest(unittest.TestCase):
    def test_comments_and_strings_are_not_code(self):
        code, literals, _ = neutralize("x = 'a // b'; // implements Queueable\n/* class Y */ y = 'it\\'s';")
        self.assertNotIn("Queueable", code)
        self.assertNotIn("class Y", code)
        self.assertEqual(literals, ["a // b", "it's"])

    def test_canonical_names_ignore_case_and_system_prefix(self):
        self.assertEqual(canonical_interface("database.batchable<SObject>"), "Database.Batchable")
        self.assertEqual(canonical_interface("System.Queueable"), "System.Queueable")
        self.assertEqual(canonical_interface("schedulable"), "System.Schedulable")
        self.assertEqual(canonical_interface("Minha.Interface"), "Minha.Interface")


class BatchTest(unittest.TestCase):
    def setUp(self):
        self.r = parse("OrderCleanupBatch")

    def test_identification(self):
        self.assertEqual(self.r["className"], "OrderCleanupBatch")
        self.assertEqual(self.r["sharing"], "with sharing")
        self.assertEqual(self.r["description"], "Limpa pedidos cancelados (classe SIMULADA para testes).")
        self.assertEqual(self.r["implements"],
                         ["Database.Batchable", "Database.Stateful", "Database.AllowsCallouts"])

    def test_batch_capabilities(self):
        b = self.r["batch"]
        self.assertEqual(b["scopeType"], "QueryLocator")
        self.assertEqual(b["soqlQuery"], "SELECT Id, Status__c FROM Order__c WHERE Status__c = 'Cancelled'")
        self.assertEqual(b["targetSObject"], "Order__c")
        self.assertTrue(b["isStateful"] and b["allowsCallouts"])
        self.assertFalse(b["raisesPlatformEvents"])
        self.assertEqual(b["lifecycleMethods"], ["start", "execute", "finish"])
        self.assertEqual([(c["targetClass"], c["batchSize"]) for c in b["chainedJobs"]], [("InvoiceSyncBatch", 50)])

    def test_comments_and_strings_are_not_evidence(self):
        self.assertIsNone(self.r["queueable"])  # "implements Queueable" só em comentário
        self.assertEqual([i["targetClass"] for i in self.r["asyncInvocations"]], ["InvoiceSyncBatch"])

    def test_no_code_body_or_literal_secret_in_output(self):
        dump = json.dumps(self.r)
        self.assertNotIn("SENTINELA_APEX_SEGREDO", dump)
        self.assertNotIn("processados +=", dump)


class QueueableTest(unittest.TestCase):
    def test_finalizer_chaining_and_constructor(self):
        q = parse("AccountSyncQueueable")["queueable"]
        self.assertEqual(q["finalizerClassName"], "IntegrationFinalizerHandler")
        self.assertTrue(q["supportsChaining"])
        self.assertEqual(q["chainedJobs"][0]["delayMinutes"], 5)
        self.assertTrue(q["allowsCallouts"])
        self.assertEqual(q["inputParameters"], [{"type": "List<Account>", "name": "accounts"},
                                                {"type": "Boolean", "name": "retry"}])


class FutureTest(unittest.TestCase):
    def test_future_methods(self):
        r = parse("IntegrationAsyncHelper")
        self.assertEqual(r["sharing"], "without sharing")
        fut = {f["name"]: f for f in r["futureMethods"]}
        self.assertEqual(set(fut), {"processOrdersAsync", "recalc"})  # helper() não é @future
        self.assertTrue(fut["processOrdersAsync"]["callout"])
        self.assertFalse(fut["recalc"]["callout"])
        self.assertEqual(fut["processOrdersAsync"]["parameterTypes"], ["List<Id>"])
        self.assertIn("static", fut["recalc"]["modifiers"])


class SchedulableTest(unittest.TestCase):
    def test_delegation_and_schedule_call(self):
        r = parse("DailyOrderCleanupScheduler")
        s = r["schedulable"]
        self.assertEqual(s["delegatedClassNames"], ["OrderCleanupBatch"])  # via variável local
        self.assertEqual(s["delegatedJobs"][0]["batchSize"], 200)
        sched = [i for i in r["asyncInvocations"] if i["kind"] == "schedule"][0]
        self.assertEqual((sched["jobName"], sched["cronExpression"], sched["targetClass"]),
                         ("Limpeza Diaria de Pedidos", "0 0 1 * * ?", "DailyOrderCleanupScheduler"))


class MultiRoleTest(unittest.TestCase):
    def test_batch_and_schedulable_in_same_class(self):
        r = parse("MultiRoleJob")
        self.assertEqual(r["implements"], ["Database.Batchable", "System.Schedulable"])
        self.assertEqual(r["sharing"], "inherited sharing")
        self.assertIn("global", r["classModifiers"])
        self.assertTrue(r["batch"]["soqlDynamic"])
        self.assertIsNone(r["batch"]["soqlQuery"])
        self.assertEqual(r["batch"]["chainedJobs"], [])  # o executeBatch está no execute de Schedulable
        self.assertEqual(r["schedulable"]["delegatedClassNames"], ["MultiRoleJob"])  # `this`

    def test_iterable_scope(self):
        r = parse_apex_source("public class X implements Database.Batchable<Account> {"
                              " public Iterable<Account> start(Database.BatchableContext bc) { return lista; }"
                              " public void execute(Database.BatchableContext bc, List<Account> s) {}"
                              " public void finish(Database.BatchableContext bc) {} }")
        self.assertEqual(r["batch"]["scopeType"], "Iterable")
        self.assertFalse(r["batch"]["soqlDynamic"])


class PlainClassTest(unittest.TestCase):
    def test_no_async_role(self):
        r = parse("PedidoService")
        self.assertEqual(r["implements"], [])
        self.assertIsNone(r["batch"])
        self.assertEqual(r["futureMethods"], [])
        self.assertEqual(r["innerTypes"], ["PedidoException"])
        self.assertEqual([m["name"] for m in r["methods"]], ["buscar"])

    def test_interface_and_enum_are_parsed_without_roles(self):
        r = parse_apex_source("/** forma */ public interface Shape { Decimal area(); }")
        self.assertEqual((r["parsed"], r["kind"], r["className"]), (True, "interface", "Shape"))
        self.assertEqual(r["implements"], [])
        e = parse_apex_source("public enum Cor { AZUL, VERDE }")
        self.assertEqual((e["kind"], e["className"]), ("enum", "Cor"))
        inner = parse_apex_source("public class Externa { public enum Tipo { A } }")
        self.assertEqual((inner["kind"], inner["className"]), ("class", "Externa"))

    def test_without_class_declaration(self):
        r = parse_apex_source("// nada aqui")
        self.assertFalse(r["parsed"])


if __name__ == "__main__":
    unittest.main()
