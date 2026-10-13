"""Segurança, acesso e governança (Onda 05): perfil, permission set group, regras de
compartilhamento, papéis, grupos públicos e documento único de segurança da org.

Usa a CLI simulada e os XMLs SIMULADOS de tests/fixtures/source.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.access_builders import sharing_targets
from salesforce_docs.parsing.governance_builders import role_hierarchy_rows
from salesforce_docs.pipeline.document_pipeline import EXIT_OK
from salesforce_docs.rendering.context import RenderContext

GROUPS = ["OrgSecurity", "Role", "PublicGroup", "Profile", "PermissionSetGroup", "SharingRules",
          "PermissionSet", "CustomObject"]


class GovernanceBuildersTest(unittest.TestCase):
    def ctx(self, name, roles):
        ctx = RenderContext("Role", name, {})
        ctx.run_index = {"records": {"Role": roles}}
        return ctx

    def test_hierarchy_up_and_down(self):
        roles = {"A": {"parentRole": None}, "B": {"parentRole": "A"}, "C": {"parentRole": "B"},
                 "D": {"parentRole": "B"}}
        rows = role_hierarchy_rows(self.ctx("B", roles), {})
        self.assertEqual([(r["hierarchy_relation"], r["hierarchy_role"]) for r in rows],
                         [("Acima", "A"), ("Subordinado direto", "C"), ("Subordinado direto", "D")])
        top = role_hierarchy_rows(self.ctx("A", roles), {})
        self.assertEqual(top[0]["hierarchy_relation"], "Topo da hierarquia (sem parentRole)")

    def test_parent_outside_run_and_cycle(self):
        rows = role_hierarchy_rows(self.ctx("B", {"B": {"parentRole": "Fora"}}), {})
        self.assertEqual(rows[0]["hierarchy_relation"], "Acima (papel não processado nesta execução)")
        cycle = {"X": {"parentRole": "Y"}, "Y": {"parentRole": "X"}}
        self.assertLessEqual(len(role_hierarchy_rows(self.ctx("X", cycle), {})), 3)  # termina

    def test_no_index_is_not_informed(self):
        self.assertEqual(role_hierarchy_rows(RenderContext("Role", "A", {}), {}), [])

    def test_sharing_targets_match_type_and_name(self):
        index = {"sharingRules": {"Obj__c": [
            {"name": "R1", "sharedTo": "role: Vendas", "kind": "k", "accessLevel": "Read"},
            {"name": "R2", "sharedTo": "roleAndSubordinates: Vendas; group: G", "kind": "k", "accessLevel": "Edit"},
            {"name": "R3", "sharedTo": "role: Vendas_2", "kind": "k", "accessLevel": "Read"}]}}
        self.assertEqual([r["name"] for _, r in sharing_targets(index, ["role", "roleAndSubordinates"], "Vendas")],
                         ["R1", "R2"])
        self.assertEqual([r["name"] for _, r in sharing_targets(index, ["group"], "G")], ["R2"])


class GovernanceDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=GROUPS)

    def doc(self, name, suffix):
        e = next(c for c in self.state.data["components"]
                 if c.get("role") == "primary" and c["component"] == name and suffix in str(c.get("document")))
        self.assertEqual(e["status"], st.SUCCESS, name)
        return self.read(e["document"])

    def test_all_documents(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        for name, suffix in (("Security", "org-security"), ("Admin", "profile"), ("Vendas", "profile"),
                             ("PSG_Integracao", "permission-set-group"), ("Pedido__c", "sharing-rules"),
                             ("Diretoria", "role"), ("Vendas", "role"), ("Gerente_Vendas", "role"),
                             ("Grupo_Suporte", "public-group")):
            self.assertNotIn("{{", self.doc(name, suffix))

    def test_org_security_document(self):
        doc = self.doc("Security", "org-security")
        self.assertIn("| sessionTimeout | TwoHours | XML |", doc)
        self.assertIn("| minimumPasswordLength | 8 | XML |", doc)
        self.assertIn("| description=Rede corporativa (simulada), end=10.0.0.254, start=10.0.0.1 | XML |", doc)
        self.assertIn("| Pedido__c | Pedido | ReadWrite | Não informado | XML |", doc)
        self.assertIn("| DefaultAccountAccess | Edit | Objeto interno |", doc)
        calls = self.calls()
        self.assertIn("--metadata Settings:Security", calls)
        self.assertNotIn("--metadata-type SecuritySettings", calls)  # componente fixo: nada a listar
        self.assertNotIn("--metadata Settings ", calls)              # nunca o tipo Settings inteiro

    def test_profile_document(self):
        doc = self.doc("Admin", "profile")
        self.assertIn("| UserLicense | Salesforce | XML |", doc)
        self.assertIn("| Pedido__c-Pedido Layout Venda | Pedido__c.Padrao | XML |", doc)
        self.assertIn("| Pedido__c | DefaultOn | XML |", doc)
        self.assertIn("| mondayStart | 480 | XML |", doc)
        self.assertIn("| ModifyAllData | XML |", doc)
        self.assertIn("startAddress=10.0.0.1", doc)
        # Perfil padrão: Name (System Administrator) ≠ fullName (Admin) — pendência de piloto.
        internal = doc.split("## Dados internos", 1)[1].split("## ", 1)[0]
        self.assertIn("| Não informado | Não informado | Objeto interno |", internal)
        self.assertIn("| Description | Perfil de vendas (simulado) | Objeto interno |", self.doc("Vendas", "profile"))

    def test_permission_set_group_and_permission_set(self):
        psg = self.doc("PSG_Integracao", "permission-set-group")
        self.assertIn("| Integracao_API | XML |", psg)
        self.assertIn("| PSG_Integracao_Muting | XML |", psg)
        ps = self.doc("Integracao_API", "permission-set")
        self.assertIn("| Aprova_Pedido | XML |", ps)
        self.assertIn("| PedidoResumo | XML |", ps)
        self.assertIn("| Pedido__c | Visible | XML |", ps)

    def test_sharing_rules_document(self):
        doc = self.doc("Pedido__c", "sharing-rules")
        self.assertIn("| Pedidos_Altos | Pedidos Altos | Read | role=Gerente_Vendas | "
                      "field=Valor__c, operation=greaterThan, value=1000 |", doc)
        self.assertIn("| Pedidos_Suporte | Pedidos Suporte | Edit | group=Grupo_Suporte | "
                      "roleAndSubordinates=Vendas | XML |", doc)
        self.assertIn("| Pedido__c | ReadWrite | Não informado | XML |", doc)

    def test_roles_hierarchy_and_sharing(self):
        vendas = self.doc("Vendas", "role")
        self.assertIn("| Acima | Diretoria | 1 acima | Derivado |", vendas)
        self.assertIn("| Subordinado direto | Gerente_Vendas | 1 abaixo | Derivado |", vendas)
        self.assertIn("| Nenhuma regra de compartilhamento compartilha com este componente |", vendas)
        gerente = self.doc("Gerente_Vendas", "role")
        self.assertIn("| Acima | Vendas | 1 acima |", gerente)
        self.assertIn("| Acima | Diretoria | 2 acima |", gerente)
        self.assertIn("| Regra de compartilhamento | Pedidos_Altos | Read | Objeto Pedido__c; "
                      "Regra de compartilhamento por critério | XML |", gerente)
        self.assertIn("| Topo da hierarquia (sem parentRole) | Diretoria | 0 |", self.doc("Diretoria", "role"))

    def test_public_group(self):
        doc = self.doc("Grupo_Suporte", "public-group")
        self.assertIn("| DoesIncludeBosses | true | XML |", doc)
        self.assertIn("| Regra de compartilhamento | Pedidos_Suporte | Edit |", doc)

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        e = next(c for c in state.data["components"] if c.get("component") == "Security")
        self.assertEqual(e["status"], st.SUCCESS)
        doc = self.read(e["document"])
        self.assertIn("| sessionTimeout | TwoHours | XML |", doc)
        self.assertIn("| Pedido__c | Pedido | ReadWrite |", doc)
        g = next(c for c in state.data["components"] if c.get("component") == "Gerente_Vendas")
        self.assertIn("| Acima | Diretoria | 2 acima |", self.read(g["document"]))


class OrgSecurityAloneTest(P3Base):
    def test_without_custom_object_owd_is_not_informed(self):
        code, state = self.run_pipeline(groups=["OrgSecurity"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        e = next(c for c in state.data["components"] if c.get("component") == "Security")
        owd = self.read(e["document"]).split("## Padrão de compartilhamento por objeto (OWD)", 1)[1].split("## ", 1)[0]
        self.assertIn("| Não informado | Não informado | Não informado | Não informado | XML |", owd)


if __name__ == "__main__":
    unittest.main()
