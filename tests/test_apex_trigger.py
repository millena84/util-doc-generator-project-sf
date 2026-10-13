"""Documento de Apex Trigger (Onda 02): parser `.trigger`, coexistência no objeto e acesso.

Usa a CLI simulada e as triggers SIMULADAS de tests/fixtures/source/triggers.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.apex_parser import parse_apex_source
from salesforce_docs.parsing.apex_trigger_parser import parse_apex_trigger
from salesforce_docs.pipeline.document_pipeline import EXIT_OK, EXIT_SESSION
from salesforce_docs.pipeline.run_index import build_run_index


class TriggerParserTest(unittest.TestCase):
    def test_declaration_events_and_context(self):
        r = parse_apex_trigger(
            "/** Doc */\nTRIGGER T on Pedido__c (Before Insert, after   UPDATE, after undelete) {\n"
            "  // Falso.run(); Trigger.isDelete\n  String s = 'Trigger.old OutraClasse.run()';\n"
            "  if (Trigger.IsBefore) { Handler.run(Trigger.NEW); }\n}")
        self.assertTrue(r["parsed"])
        self.assertEqual((r["triggerName"], r["sObject"], r["description"]), ("T", "Pedido__c", "Doc"))
        self.assertEqual(r["events"], ["before insert", "after update", "after undelete"])
        self.assertEqual(r["contextVariables"], ["Trigger.isBefore", "Trigger.new"])
        self.assertEqual([c["className"] for c in r["referencedClasses"]], ["Handler"])

    def test_variable_resolves_declared_type(self):
        r = parse_apex_trigger("trigger T on Account (after insert) {\n"
                               " MyHandler h = new MyHandler();\n h.execute();\n"
                               " List<Account> l = new List<Account>();\n Account a = new Account();\n}")
        classes = {c["className"]: c for c in r["referencedClasses"]}
        self.assertEqual(sorted(classes), ["MyHandler"])  # sObject do trigger e List descartados
        self.assertEqual(classes["MyHandler"]["members"], ["execute"])
        self.assertIn("instância (variável)", classes["MyHandler"]["references"])

    def test_config_reads_and_security_patterns(self):
        r = parse_apex_trigger(
            "trigger T on Account (before insert) {\n"
            " if (FeatureManagement.checkPermission('Bypass')) return;\n"
            " if (FeatureManagement.checkPermission(nome)) return;\n"
            " Cfg__c c = Cfg__c.getOrgDefaults();\n"
            " for (Bypass__mdt b : [SELECT Id FROM Bypass__mdt]) {}\n"
            " Database.query('SELECT Id FROM Account', AccessLevel.USER_MODE);\n}")
        reads = {(x["mechanism"], x["component"], x["call"]) for x in r["configReads"]}
        self.assertEqual(reads, {("Custom Permission", "Bypass", "FeatureManagement.checkPermission"),
                                 ("Custom Permission", None, "FeatureManagement.checkPermission"),
                                 ("Custom Setting", "Cfg__c", "Cfg__c.getOrgDefaults"),
                                 ("Custom Metadata Type", "Bypass__mdt", "SOQL")})
        self.assertEqual(r["securityPatterns"], [{"pattern": "AccessLevel.USER_MODE", "occurrences": 1}])

    def test_class_parser_also_reports_reads(self):
        r = parse_apex_source("public class H { void run() { X__mdt.getInstance('A'); "
                              "List<Account> l = [SELECT Id FROM Account WITH USER_MODE]; } }")
        self.assertEqual(r["configReads"][0]["record"], "A")
        self.assertEqual(r["securityPatterns"][0]["pattern"], "WITH USER_MODE")

    def test_not_a_trigger(self):
        self.assertFalse(parse_apex_trigger("public class X {}")["parsed"])


class RunIndexTest(unittest.TestCase):
    def test_phases_from_config(self):
        from salesforce_docs.config.metadata_types_loader import load_metadata_types
        from pathlib import Path
        cfg = load_metadata_types(Path(__file__).resolve().parents[1]).automation_index
        records = [
            {"metadataType": "Flow", "fullName": "F1", "data": {
                "status": "Active", "start": {"object": "Pedido__c", "triggerType": "RecordBeforeSave",
                                              "recordTriggerType": "Create"}}},
            {"metadataType": "Flow", "fullName": "F2", "data": {"start": {"object": "Pedido__c",
                                                                          "triggerType": "Scheduled"}}},
            {"metadataType": "ApexTrigger", "fullName": "T", "data": {
                "status": "Active", "apex": {"sObject": "PEDIDO__C",
                                             "events": ["before insert", "after delete"]}}},
            {"metadataType": "ValidationRule", "fullName": "Pedido__c.V", "data": {"active": "true"}},
        ]
        idx = build_run_index(records, cfg)
        got = sorted((e["name"], e["phase"], e["events"]) for e in idx["automations"]["pedido__c"])
        self.assertEqual(got, [("F1", "flowBeforeSave", "Create"), ("Pedido__c.V", "validation", None),
                               ("T", "triggerAfterDelete", "after delete"),
                               ("T", "triggerBefore", "before insert")])


class TriggerDocumentTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=["ApexTrigger", "Flow", "CustomObject"])

    def doc(self, name):
        return self.read(self.primary(self.state, name)["document"])

    def test_documents_generated_after_other_groups(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        for name in ("PedidoTrigger", "PedidoAuditoriaTrigger"):
            e = self.primary(self.state, name)
            self.assertEqual(e["status"], st.SUCCESS, name)
            self.assertTrue(e["document"].endswith(f"doc-{name.lower()}-apex-trigger.md"))
        order = [c["unitId"] for c in self.state.data["components"] if c.get("role") == "primary"]
        self.assertGreater(min(i for i, u in enumerate(order) if "ApexTrigger" in u),
                           max(i for i, u in enumerate(order) if "ApexTrigger" not in u))

    def test_identification_events_and_context(self):
        doc = self.doc("PedidoTrigger")
        self.assertIn("| Objeto | Pedido__c | Código Apex |", doc)
        self.assertIn("| Status | Active | XML |", doc)
        self.assertIn("| Descrição (ApexDoc) | Trigger do Pedido: delega a lógica ao PedidoTriggerHandler. |", doc)
        self.assertIn("| before update | before | update | Código Apex |", doc)
        self.assertIn("| Trigger.operationType | Código Apex |", doc)
        self.assertNotIn("{{", doc)

    def test_classes_checked_against_apex_class_inventory(self):
        doc = self.doc("PedidoTrigger")
        self.assertIn("| PedidoTriggerHandler | instância (new), instância (variável) | run | "
                      "Sim (inventário ApexClass) | Código Apex |", doc)
        self.assertIn("| PedidoService | chamada estática | buscar |", doc)
        self.assertNotIn("| Account |", doc)               # sObject: fora do inventário
        self.assertNotIn("PedidoLegadoHandler", doc)        # só em comentário
        self.assertIn("org list metadata --metadata-type ApexClass", self.calls())

    def test_config_reads_and_security_from_trigger_and_handler(self):
        doc = self.doc("PedidoTrigger")
        self.assertIn("| Trigger PedidoTrigger | Custom Permission | Bypass_Pedido_Trigger |", doc)
        self.assertIn("| Trigger PedidoTrigger | Custom Metadata Type | Trigger_Setting__mdt | "
                      "Trigger_Setting__mdt.getInstance | PedidoTrigger |", doc)
        # ApexClass fora do escopo da execução: a classe não foi processada.
        self.assertIn("| Classe PedidoTriggerHandler | Classe não processada nesta execução |", doc)

    def test_coexistence_in_official_order(self):
        doc = self.doc("PedidoTrigger")
        section = doc.split("## Coexistência no objeto e ordem de execução", 1)[1].split("## ", 1)[0]
        rows = [ln for ln in section.splitlines() if ln.startswith("| ") and "Derivado" in ln]
        self.assertEqual([r.split(" | ")[0] for r in rows], ["| 2", "| 2", "| 3", "| 4", "| 5", "| Não confirmado"])
        self.assertIn("| Apex Trigger | PedidoTrigger (este documento) | before insert, before update | Active |",
                      section)
        self.assertIn("| Apex Trigger | PedidoAuditoriaTrigger | before update | Inactive |", section)
        self.assertIn("| Regra de validação | Pedido__c.Valor_Positivo |", section)
        self.assertIn("| Record-Triggered Flow | Meu_Flow | Update | Active |", section)
        self.assertIn("Sem ordem garantida entre triggers do mesmo objeto e evento", section)
        self.assertIn("| Trigger after delete |", section)

    def test_access_via_object_and_called_classes(self):
        doc = self.doc("PedidoTrigger")
        access = doc.split("## Acesso e configuração", 1)[1]
        self.assertIn("| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto Pedido__c |",
                      access)
        self.assertIn("| Perfil | Vendas | Executar | Classe chamada PedidoTriggerHandler |", access)
        self.assertIn("| Perfil | Admin | Executar | Classe chamada PedidoService |", access)

    def test_internal_data(self):
        doc = self.doc("PedidoAuditoriaTrigger")
        self.assertIn("| UsageAfterDelete | True | Objeto interno |", doc)
        self.assertNotIn("namespace", doc)

    def test_regenerate_rebuilds_coexistence(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        e = self.primary(state, "PedidoTrigger")
        doc = self.read(e["document"])
        self.assertIn("| PedidoAuditoriaTrigger | before update | Inactive |", doc)
        self.assertIn("| Record-Triggered Flow | Meu_Flow |", doc)


class TriggerResumeTest(P3Base):
    def test_resume_uses_carried_components_in_coexistence(self):
        groups = ["ApexTrigger", "Flow", "CustomObject"]
        code, state = self.run_pipeline("expire_on_retrieve=PedidoAuditoriaTrigger", groups=groups)
        self.assertEqual(code, EXIT_SESSION, self.log.getvalue())
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.SUCCESS)
        self.calls_file.write_text("")
        code, state2 = self.run_pipeline("", groups=groups, resume=state.run_id)
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertNotIn("Flow:Meu_Flow", self.calls())  # herdado, não recuperado de novo
        doc = self.read(self.primary(state2, "PedidoTrigger")["document"])
        self.assertIn("| Record-Triggered Flow | Meu_Flow | Update | Active |", doc)
        self.assertIn("| Regra de validação | Pedido__c.Valor_Positivo |", doc)


class TriggerWithHandlerTest(P3Base):
    def test_handler_facts_when_class_is_processed(self):
        code, state = self.run_pipeline(groups=["ApexTrigger", "ApexClass"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "PedidoTrigger")["document"])
        self.assertIn("| Classe PedidoTriggerHandler | Custom Setting | Automation_Settings__c | "
                      "Automation_Settings__c.getInstance |", doc)
        self.assertIn("| Classe PedidoTriggerHandler | WITH USER_MODE | 1 | Código Apex |", doc)
        self.assertIn("| Classe PedidoTriggerHandler | Security.stripInaccessible | 1 | Código Apex |", doc)
        # Sem Flow/CustomObject no escopo: só as triggers aparecem na coexistência.
        self.assertNotIn("Meu_Flow", doc)


if __name__ == "__main__":
    unittest.main()
