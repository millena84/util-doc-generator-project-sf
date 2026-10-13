"""Experience Cloud (Onda 09): Network, CustomSite e ExperienceBundle.

Usa a CLI simulada e os arquivos SIMULADOS de tests/fixtures/source. Usuários e remetente de
e-mail das fixtures são sentinelas: nunca podem aparecer nos documentos.
"""

import json
import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.experience_parser import parse_custom_site, parse_experience_bundle, parse_network
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

GROUPS = ["Network", "CustomSite", "ExperienceBundle", "LightningComponentBundle", "SharingRules"]
VIEW = {"id": "home", "label": "Home", "componentName": "layout:x", "regions": [
    {"name": "header", "type": "region", "components": [
        {"componentName": "c:meuLwc", "id": "a", "type": "component", "audienceId": "VIP"},
        {"componentName": "ns:outro", "id": "b", "type": "component",
         "regions": [{"name": "interna", "type": "region",
                      "components": [{"componentName": "c:filho", "id": "c", "type": "component"}]}]}]}]}


class ExperienceParsersTest(unittest.TestCase):
    def test_network_members_and_sender_never_stored(self):
        r = parse_network('<Network xmlns="x"><emailSenderAddress>s@example.invalid</emailSenderAddress>'
                          '<networkMemberGroups><profile>P</profile><permissionSet>PS</permissionSet></networkMemberGroups>'
                          '<selfRegProfile>R</selfRegProfile><welcomeTemplate>T</welcomeTemplate><site>S</site></Network>')
        self.assertNotIn("@", json.dumps(r))
        self.assertEqual([(m["type"], m["name"]) for m in r["members"]],
                         [("Perfil", "P"), ("Permission Set", "PS"), ("Perfil de autorregistro", "R")])
        self.assertEqual((r["site"], r["emailSender"]), ("S", "Configurado (não documentado)"))
        self.assertEqual(r["emailTemplates"], [{"element": "welcomeTemplate", "template": "T"}])

    def test_custom_site_users_never_stored(self):
        r = parse_custom_site('<CustomSite xmlns="x"><siteAdmin>a@example.invalid</siteAdmin>'
                              '<guestProfile>G</guestProfile></CustomSite>')
        self.assertNotIn("@", json.dumps(r))
        self.assertEqual(r["guestProfile"], "G")
        self.assertEqual(r["siteUsers"][0]["state"], "Configurado (usuário não documentado)")

    def test_bundle_views_routes_nested_components_and_targeting(self):
        r = parse_experience_bundle({"B.site-meta.xml": "<x/>", "B/views/home.json": json.dumps(VIEW),
                                     "B/routes/home.json": json.dumps({"id": "home", "urlPrefix": "", "pageAccess": "Public"}),
                                     "B/themes/t.json": "{}"})
        self.assertTrue(r["parsed"])
        self.assertEqual([(c["region"], c["componentName"]) for c in r["components"]],
                         [("header", "c:meuLwc"), ("header", "ns:outro"), ("interna", "c:filho")])
        self.assertEqual(r["customComponents"], ["filho", "meuLwc"])
        self.assertEqual(r["targeting"], [{"view": "home", "component": "c:meuLwc", "key": "audienceId", "value": "VIP"}])
        self.assertEqual((r["routes"][0]["urlPrefix"], r["routes"][0]["pageAccess"]), ("(vazio)", "Public"))
        self.assertEqual([f["folder"] for f in r["folders"]], ["routes", "themes", "views"])

    def test_invalid_inputs(self):
        self.assertFalse(parse_network("<x>")["parsed"])
        self.assertFalse(parse_custom_site("<x>")["parsed"])
        self.assertFalse(parse_experience_bundle({"B/views/a.json": "{"})["parsed"])


class ExperienceDocumentsTest(P3Base):
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

    def test_normalized_has_no_users_or_emails(self):
        # ADD-02: usuários do site e remetente da Network redigidos no normalizado.
        for name in ("Portal_Clientes",):
            for e in (c for c in self.state.data["components"] if c.get("component") == name and c.get("normalized")):
                text = (self.root / e["normalized"]).read_text().lower()
                self.assertNotIn("sentinela", text, e["unitId"])
                self.assertNotIn("@example.invalid", text, e["unitId"])

    def test_network(self):
        doc = self.doc("network")
        self.assertIn("| Remetente de e-mail | Configurado (não documentado) | XML |", doc)
        self.assertIn("| welcomeTemplate | unfiled$public/CommunityWelcomeEmail | XML |", doc)
        self.assertIn("| Portal_Clientes | true | clientes | Portal Clientes Profile | ChatterNetwork | XML |", doc)
        self.assertIn("| Permission Set | Leitura_Pedidos | Membro do site | — | XML |", doc)
        self.assertIn("| Perfil de autorregistro | Customer Community User | Membro do site | — | XML |", doc)

    def test_custom_site_guest_security(self):
        doc = self.doc("site")
        self.assertIn("| Administrador do site (siteAdmin) | Configurado (usuário não documentado) | XML |", doc)
        self.assertIn("| Account | Ler, Editar | Sim | XML |", doc)
        self.assertIn("| Pedido__c | Ler, Criar | Não | XML |", doc)
        self.assertIn("| Portal_Clientes | Live | true | XML |", doc)
        self.assertIn("| Regra de compartilhamento | Pedidos_Portal | Read | Objeto Pedido__c; "
                      "Regra de compartilhamento para convidado | XML |", doc)

    def test_experience_bundle(self):
        doc = self.doc("experience")
        self.assertIn("| login | login | Public | login | login-main | routes/login.json | JSON do ExperienceBundle |", doc)
        self.assertIn("| home | (vazio) | RequiresLogin |", doc)
        self.assertIn("| home | header | c:pedidoPainel | painel_cmp | JSON do ExperienceBundle |", doc)
        self.assertIn("| home | c:pedidoPainel | targetAudience | Audiencia_Clientes_VIP |", doc)
        self.assertIn("| Perfil | Admin | Executar | Classe Apex PedidoController (LWC pedidoPainel) | XML |", doc)
        self.assertIn("| Não verificado | portalBanner não processado nesta execução |", doc)

    def test_lwc_and_sharing_rules_show_the_site(self):
        self.assertIn("| Portal_Clientes1/home | Experience Cloud | header | painel_cmp | Sim | JSON do ExperienceBundle |",
                      self.read(self.primary(self.state, "pedidoPainel")["document"]))
        self.assertIn("| Pedidos_Portal | Pedidos do Portal | Read | guestUser=Portal_Clientes |", self.doc("sharing-rules"))

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        e = next(c for c in state.data["components"] if c.get("component") == "Portal_Clientes1")
        self.assertIn("Classe Apex PedidoController (LWC pedidoPainel)", self.read(e["document"]))


if __name__ == "__main__":
    unittest.main()
