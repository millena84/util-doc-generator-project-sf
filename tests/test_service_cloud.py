"""Service Cloud (Onda 07): regras de atribuição, resposta automática e escalonamento, e filas.

Usa a CLI simulada e os XMLs SIMULADOS de tests/fixtures/source. Usuários e e-mails das
fixtures são sentinelas: nunca podem aparecer nos documentos.
"""

import json
import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.service_rules_parser import parse_queue, parse_service_rules
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

GROUPS = ["AssignmentRules", "AutoResponseRules", "EscalationRules", "Queue"]
RULES = """<AssignmentRules xmlns="http://soap.sforce.com/2006/04/metadata">
  <assignmentRule><fullName>A</fullName><active>true</active>
    <ruleEntry><assignedTo>Fila</assignedTo><assignedToType>Queue</assignedToType>
      <criteriaItems><field>Case.Origin</field><operation>equals</operation><value>Web</value></criteriaItems>
      <booleanFilter>1</booleanFilter></ruleEntry>
    <ruleEntry><assignedTo>pessoa@example.invalid</assignedTo><assignedToType>User</assignedToType>
      <senderEmail>x@example.invalid</senderEmail></ruleEntry>
  </assignmentRule>
  <assignmentRule><fullName>B</fullName><active>true</active></assignmentRule>
</AssignmentRules>"""


class ServiceParsersTest(unittest.TestCase):
    def test_rules_order_destinations_and_privacy(self):
        r = parse_service_rules(RULES)
        self.assertNotIn("@", json.dumps(r))
        self.assertEqual([(e["order"], e["destination"]) for e in r["entries"]],
                         [(1, "Queue: Fila"), (2, "User: usuário (não documentado)")])
        self.assertEqual(r["entries"][0]["criteria"], "Case.Origin equals Web")
        self.assertEqual(r["entries"][1]["criteria"], "(sem critério: pega tudo)")
        self.assertIn("e-mail do remetente (não documentado)", r["entries"][1]["details"])
        self.assertEqual([t["name"] for t in r["targets"]], ["Fila"])  # usuário nunca vira destino indexado
        self.assertIn("2 regras ativas", r["activeCheck"])

    def test_queue_users_only_counted(self):
        q = parse_queue('<Queue xmlns="http://soap.sforce.com/2006/04/metadata"><email>f@example.invalid</email>'
                        '<queueMembers><roles><role>R</role></roles><users><user>u@example.invalid</user>'
                        '<user>v@example.invalid</user></users></queueMembers>'
                        '<queueSobject><sobjectType>Case</sobjectType></queueSobject></Queue>')
        self.assertNotIn("@", json.dumps(q))
        self.assertEqual((q["members"], q["userMembers"], q["objects"]), ([{"type": "roles", "name": "R"}], 2, ["Case"]))

    def test_invalid_xml(self):
        self.assertFalse(parse_service_rules("<x>")["parsed"])
        self.assertFalse(parse_queue("<x>")["parsed"])


class ServiceDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=GROUPS)

    def doc(self, suffix):
        e = next(c for c in self.state.data["components"]
                 if c.get("role") == "primary" and str(c.get("document")).endswith(f"-{suffix}.md"))
        self.assertEqual(e["status"], st.SUCCESS)
        return self.read(e["document"])

    def test_no_personal_data_in_any_document(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        for c in self.state.data["components"]:
            if c.get("role") == "primary" and c.get("document"):
                text = self.read(c["document"]).lower()
                self.assertNotIn("sentinela", text, c["unitId"])
                self.assertNotIn("@example.invalid", text, c["unitId"])

    def test_assignment_rules(self):
        doc = self.doc("assignment-rules")
        self.assertIn("| Situação | Uma regra ativa | Derivado |", doc)
        self.assertIn("| Atribuicao_Antiga | false |", doc)
        self.assertIn("| Atribuicao_Case | 1 | Case.Origin equals Email; Case.Priority equals High | Não informado | "
                      "Queue: Fila_Pedidos | template=unfiled$public/Caso_Atribuido | XML |", doc)
        self.assertIn("| Atribuicao_Case | 2 | (sem critério: pega tudo) | Não informado | "
                      "User: usuário (não documentado) |", doc)
        self.assertIn("| 01Q000000000001AAA | Atribuicao_Antiga | False | Objeto interno |", doc)

    def test_auto_response_rules(self):
        doc = self.doc("auto-response-rules")
        self.assertIn("e-mail do remetente (não documentado)", doc)
        self.assertIn("nome do remetente (não documentado)", doc)
        self.assertIn("template=unfiled$public/Caso_Recebido", doc)

    def test_escalation_rules(self):
        doc = self.doc("escalation-rules")
        self.assertIn("| Escalonamento_Case | 1 | escalationAction 1 | Queue: Fila_Pedidos | minutesToEscalation=240;", doc)
        self.assertIn("1 usuário(s) notificado(s) (não documentados)", doc)

    def test_queue(self):
        doc = self.doc("queue")
        self.assertIn("| Usuários membros | 1 usuário(s) (não documentados) | XML |", doc)
        self.assertIn("| AssignmentRules | Case | Atribuicao_Case | 1 | true | Derivado |", doc)
        self.assertIn("| EscalationRules | Case | Escalonamento_Case | 1 | true | Derivado |", doc)
        self.assertIn("| roles | Vendas | Membro da fila | — | XML |", doc)
        self.assertIn("| Usuários | 1 (não documentados) | Membro da fila |", doc)

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        e = next(c for c in state.data["components"] if c.get("component") == "Fila_Pedidos")
        self.assertIn("| AssignmentRules | Case | Atribuicao_Case |", self.read(e["document"]))


if __name__ == "__main__":
    unittest.main()
