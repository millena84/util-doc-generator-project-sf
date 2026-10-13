"""Onde cada componente está configurado (perfil, permission set, PSG, fila, compartilhamento).

Fonte: XML de Profile/PermissionSet/PermissionSetGroup/Queue/SharingRules (fixtures SIMULADAS),
recuperados num retrieve único junto com os componentes documentados.
"""

import io
import json
import unittest

from tests.helpers import fake_sf_env
from tests.test_prioridade3 import P3Base
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import EXIT_OK, DocumentPipeline
from salesforce_docs.rendering.template_loader import ContractStore
from salesforce_docs.salesforce.cli_runner import CliRunner
from salesforce_docs.validation.project_validator import validate_project

ACCESS = "## Acesso e configuração"


def section(text, title):
    start = text.index(title)
    nxt = text.find("\n## ", start + 1)
    return text[start:] if nxt < 0 else text[start:nxt]


class AccessDocumentsTest(P3Base):
    @classmethod
    def setUpClass(cls):
        cls.scenario = "mvp_complete"

    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(self.scenario)

    def doc(self, component):
        return self.read(self.primary(self.state, component)["document"])

    def test_every_document_ends_with_access_section(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        docs = []
        for c in self.state.data["components"]:
            if c.get("role") == "primary" and c.get("document"):
                docs.append(c["document"])
                docs += [s["document"] for s in c.get("subDocuments") or [] if s.get("document")]
        self.assertGreater(len(docs), 20)
        for d in docs:
            text = self.read(d)
            sections = [ln for ln in text.splitlines() if ln.startswith("## ")]
            self.assertEqual(sections[-1], ACCESS, d)

    def test_single_retrieve_with_documented_components(self):
        calls = [ln for ln in self.calls().splitlines() if "--metadata Profile" in ln]
        self.assertEqual(len(calls), 1)
        for spec in ("--metadata PermissionSet ", "--metadata Queue ", "--metadata SharingRules ",
                     "--metadata ApexClass ", "--metadata CustomObject ", "--metadata Flow "):
            self.assertIn(spec, calls[0] + " ")
        self.assertEqual(self.state.data["access"]["status"], "SUCCESS")

    def test_custom_object_access_and_sharing(self):
        text = self.doc("Pedido__c")
        acc = section(text, ACCESS)
        self.assertIn("| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | — | XML |", acc)
        self.assertIn("| Perfil | Vendas | Ler | — | XML |", acc)
        self.assertIn("| Permission Set Group | PSG_Integracao | Ler, Editar | Permission Set Integracao_API | XML |", acc)
        sharing = section(text, "## Compartilhamento e filas")
        self.assertIn("| Fila | Fila_Pedidos | — | — | XML |", sharing)
        self.assertIn("| Regra de compartilhamento por critério | Pedidos_Altos | role: Gerente_Vendas | Read | XML |",
                      sharing)
        self.assertIn("group: Grupo_Suporte | Edit", sharing)

    def test_disabled_grant_is_not_access(self):
        acc = section(self.doc("OrderCleanupBatch"), ACCESS)
        self.assertIn("| Perfil | Admin | Executar |", acc)
        self.assertNotIn("Vendas", acc)  # <enabled>false</enabled> no perfil Vendas

    def test_subdocuments_inherit_component_access(self):
        flow = self.primary(self.state, "Meu_Flow")
        trigger = [s for s in flow["subDocuments"] if s["document"].endswith("flow-trigger.md")][0]
        self.assertIn("| Perfil | Admin | Executar |", section(self.read(trigger["document"]), ACCESS))
        future = self.primary(self.state, "IntegrationAsyncHelper")["subDocuments"][0]
        self.assertIn("Nenhuma concessão encontrada", section(self.read(future["document"]), ACCESS))

    def test_credentials_and_apps(self):
        ec = section(self.doc("Minha_EC"), ACCESS)
        self.assertIn("| Permission Set | Integracao_API | Usar principal | Principal Principal_Integracao | XML |", ec)
        nc = section(self.doc("Minha_NC"), ACCESS)
        self.assertIn("ExternalCredential Minha_EC (principal Principal_Integracao)", nc)
        app = section(self.doc("Meu_App"), ACCESS)
        self.assertIn("| Perfil | Vendas | Autorizado no componente | — | XML |", app)
        self.assertIn("| Permission Set | Integracao_API | Autorizado no componente | — | XML |", app)
        eca = section(self.doc("Minha_ECA"), ACCESS)
        self.assertIn("| Permission Set | Leitura_Pedidos | Autorizado no componente | "
                      "ExtlClntAppOauthConfigurablePolicies Minha_ECA_oauthPlcy | XML |", eca)
        self.assertIn("| Não aplicável | Remote Site Setting vale para a org inteira",
                      section(self.doc("Meu_Site"), ACCESS))
        self.assertIn("| Perfil | Admin | Ler |", section(self.doc("Config__mdt"), ACCESS))

    def test_permission_set_document(self):
        text = self.doc("Integracao_API")
        self.assertIn("| Pedido__c | true | false | true | false | false | false | XML |", text)
        self.assertIn("| Pedido__c.Status__c | true | false | XML |", text)
        self.assertIn("| AccountSyncQueueable | XML |", text)
        self.assertIn("| Minha_EC-Principal_Integracao | XML |", text)
        self.assertIn("| Permission Set Group | PSG_Integracao | Inclui o permission set |", section(text, ACCESS))
        retrieves = [ln for ln in self.calls().splitlines() if "PermissionSet:Integracao_API" in ln]
        self.assertEqual(retrieves, [])  # XML reaproveitado do retrieve de acesso

    def test_queue_members_and_users_never_rendered(self):
        for c in self.state.data["components"]:
            if c.get("document"):
                self.assertNotIn("usuario.membro.sentinela", self.read(c["document"]))

    def test_regenerate_offline_rebuilds_access(self):
        before = {c["component"]: self.read(c["document"]) for c in self.state.data["components"]
                  if c.get("role") == "primary" and c.get("document")}
        fake_sf_env("old_cli")
        pipeline = DocumentPipeline(self.root, runner=CliRunner(executable="/nao/existe/sf"), stream=io.StringIO())
        code, state2 = pipeline.regenerate(self.state.run_id)
        self.assertEqual(code, EXIT_OK)
        for c in state2.data["components"]:
            if c.get("role") == "primary" and c.get("document"):
                self.assertEqual(self.read(c["document"]), before[c["component"]], c["component"])


class AccessUnavailableTest(P3Base):
    def test_failed_access_retrieve_is_not_informed_not_no_access(self):
        code, state = self.run_pipeline("fail_access_retrieve", groups=["ApexClass"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["access"]["status"], "RETRIEVE_FAILED")
        acc = section(self.read(self.primary(state, "OrderCleanupBatch")["document"]), ACCESS)
        self.assertIn("| Não informado | Não informado | Não informado | Não informado | XML |", acc)
        self.assertNotIn("Nenhuma concessão", acc)

    def test_disabled_by_config(self):
        cfg = self.root / "config" / "metadata-types-mvp.json"
        data = json.loads(cfg.read_text())
        data["accessSources"]["enabled"] = False
        cfg.write_text(json.dumps(data))
        code, state = self.run_pipeline(groups=["ApexClass"])
        self.assertEqual(state.data["access"]["status"], "DISABLED")
        self.assertNotIn("--metadata Profile", self.calls())

    def test_selected_mode_restricts_documented_components(self):
        self.config(selection={"mode": "SELECTED", "metadataTypes": {"ApexClass": {"components": ["PedidoService"]}}})
        code, state = self.run_pipeline()
        call = [ln for ln in self.calls().splitlines() if "--metadata Profile" in ln][0]
        self.assertIn("--metadata ApexClass:PedidoService", call)
        self.assertNotIn("OrderCleanupBatch", call)
        self.assertNotIn("--metadata CustomObject", call)


class AccessRuleTest(P3Base):
    def store(self):
        p = DocumentPipeline(self.root)
        return p, ContractStore(p.app.contracts_dir, p.mvp)

    def test_contract_without_access_table_is_invalid(self):
        c = self.root / "documentation/contracts/flow.schema.json"
        data = json.loads(c.read_text())
        data["tables"] = [t for t in data["tables"] if t["builder"] != "access_rows"]
        c.write_text(json.dumps(data))
        p, store = self.store()
        with self.assertRaisesRegex(ConfigError, "flow.schema.json: o contrato precisa de exatamente uma tabela"):
            validate_project(p.app, p.mvp, store)

    def test_access_section_must_be_last(self):
        m = self.root / "documentation/models/api-v67/modelo-doc-flow-vapi-67.md"
        m.write_text(m.read_text() + "\n## Depois\n\nTexto.\n")
        p, store = self.store()
        with self.assertRaisesRegex(ConfigError, "deve ser a última do modelo"):
            validate_project(p.app, p.mvp, store)


if __name__ == "__main__":
    unittest.main()
