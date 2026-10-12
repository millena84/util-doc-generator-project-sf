"""Refatoração 1 — Lote A: modelos/contratos adaptados das referências ajudAI.

Tudo com Salesforce CLI SIMULADA e fixtures sintéticas; nenhuma org real.
"""

import json
import unittest

from tests.helpers import ROOT, TempProject
from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st
from salesforce_docs.config.config_loader import load_config
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline import deviation_handler as dh
from salesforce_docs.rendering.context import RenderContext
from salesforce_docs.rendering.markdown_renderer import MarkdownRenderer
from salesforce_docs.rendering.template_loader import ContractStore, TemplateLoader
from salesforce_docs.validation.project_validator import validate_project

SECRET_SENTINELS = ["SEGREDO_SIMULADO_NAO_RENDERIZAR"]
POLICY_SENTINELS = ["CHAVE_SIMULADA", "https://example.com/callback", "admin@example.com",
                    "SENTINELA_VALOR_CMDT_NAO_RENDERIZAR"]


def _validate(root):
    app = load_config(root)
    mvp = load_metadata_types(root)
    return validate_project(app, mvp, ContractStore(app.contracts_dir, mvp))


class ValidateConfigTest(unittest.TestCase):
    def setUp(self):
        self.proj = TempProject()
        self.models = self.proj.dir / "documentation/models/api-v67"

    def tearDown(self):
        self.proj.cleanup()

    def test_repository_contracts_and_models_are_consistent(self):
        warnings = _validate(ROOT)
        self.assertEqual([w for w in warnings if "sem contrato" in w], [])

    def test_placeholder_without_contract_is_error(self):
        p = self.models / "modelo-doc-flow-autolaunched-vapi-67.md"
        p.write_text(p.read_text() + "\n| Extra | {{ inventado }} | XML |\n")
        with self.assertRaises(ConfigError) as ctx:
            _validate(self.proj.dir)
        self.assertIn("'inventado'", str(ctx.exception))

    def test_source_divergence_is_error(self):
        p = self.models / "modelo-doc-custom-object-vapi-67.md"
        p.write_text(p.read_text().replace("| SharingModel | {{ sharing_model }} | XML |",
                                           "| SharingModel | {{ sharing_model }} | Tooling API |"))
        with self.assertRaises(ConfigError) as ctx:
            _validate(self.proj.dir)
        self.assertIn("SharingModel", str(ctx.exception))

    def test_unknown_builder_is_error(self):
        p = self.proj.dir / "documentation/contracts/custom-object.schema.json"
        c = json.loads(p.read_text())
        c["tables"][1]["builder"] = "nao_existe"
        p.write_text(json.dumps(c))
        with self.assertRaises(ConfigError):
            _validate(self.proj.dir)

    def test_missing_model_is_only_a_warning(self):
        (self.models / "modelo-doc-flow-autolaunched-vapi-67.md").unlink()
        warnings = _validate(self.proj.dir)
        self.assertTrue(any("modelo-doc-flow-autolaunched-vapi-67.md" in w and
                            "contexto-flow-autolaunched.md" in w for w in warnings), warnings)

    def test_contract_pointing_to_blocked_element_is_error(self):
        p = self.proj.dir / "documentation/contracts/connected-app.schema.json"
        c = json.loads(p.read_text())
        c["properties"].append({"name": "Key", "placeholder": "k", "path": "oauthConfig.consumerKey",
                                "source": "XML", "required": False, "markdownSection": "OAuth"})
        p.write_text(json.dumps(c))
        with self.assertRaises(ConfigError) as ctx:
            _validate(self.proj.dir)
        self.assertIn("consumerKey", str(ctx.exception))


class FlowClassificationTest(unittest.TestCase):
    def setUp(self):
        self.group = load_metadata_types(ROOT).group("Flow")

    def kinds(self, data):
        return sorted(t[0]["documentSuffix"] for t in dh.sub_document_targets(self.group, data, "F"))

    def test_autolaunched_without_trigger(self):
        self.assertEqual(self.kinds({"processType": "AutoLaunchedFlow"}), ["flow-autolaunched"])

    def test_record_triggered_is_trigger_only(self):
        data = {"processType": "AutoLaunchedFlow", "start": {"triggerType": "RecordAfterSave"}}
        self.assertEqual(self.kinds(data), ["flow-trigger"])

    def test_scheduled_and_platform_event(self):
        for t in ("Scheduled", "PlatformEvent"):
            data = {"processType": "AutoLaunchedFlow", "start": {"triggerType": t}}
            self.assertEqual(self.kinds(data), ["flow-trigger"], t)

    def test_start_without_trigger_type_is_autolaunched(self):
        data = {"processType": "AutoLaunchedFlow", "start": {"locationX": "0"}}
        self.assertEqual(self.kinds(data), ["flow-autolaunched"])

    def test_screen_flow(self):
        data = {"processType": "Flow", "screens": [{"name": "S1"}]}
        self.assertEqual(self.kinds(data), ["flow-screen"])

    def test_unknown_process_type_has_no_subdocument(self):
        self.assertEqual(self.kinds({"processType": "Workflow"}), [])


class RendererEdgeCasesTest(unittest.TestCase):
    def test_empty_variable_lists_are_explicit(self):
        loader = TemplateLoader(ROOT / "documentation/models/api-v67", "67.0")
        c = json.loads((ROOT / "documentation/contracts/flow-autolaunched.schema.json").read_text())
        ctx = RenderContext("Flow", "F", {"label": "F", "processType": "AutoLaunchedFlow"})
        res = MarkdownRenderer().render(loader.load(c["template"]), c, ctx)
        self.assertTrue(res.ok, res.errors)
        self.assertEqual(res.text.count("| Não aplicável | Não aplicável | Não aplicável | Não aplicável | XML |"), 2)


class LoteAPipelineTest(PipelineTestBase):
    def doc(self, state, component, suffix=None):
        entry = self.primary(state, component)
        if suffix is None:
            return self.read(entry["document"])
        sub = next(s for s in entry["subDocuments"] if s["document"] and s["document"].endswith(suffix))
        return self.read(sub["document"])

    def test_autolaunched_interface_contract(self):
        code, state = self.run_pipeline(groups=["Flow"])
        text = self.doc(state, "Processa_Pedido", "flow-autolaunched.md")
        self.assertIn("| recordId | String | Não informado | false | XML |", text)
        self.assertIn("| pedidos | SObject | Pedido__c | true | XML |", text)
        self.assertIn("| sucesso | Boolean | Não informado | false | XML |", text)
        self.assertNotIn("varInterna", text)
        self.assertIn("Processa pedidos \\| lote<br>linha 2 – ação ✓ çãõ", text)
        self.assertIn("x" * 400, text)
        # Record-triggered não gera documento autolaunched.
        meu = self.primary(state, "Meu_Flow")["subDocuments"]
        self.assertEqual([s["document"].rsplit("-", 1)[0][-4:] for s in meu], ["flow"])
        self.assertTrue(meu[0]["document"].endswith("flow-trigger.md"))

    def test_flow_main_document_new_rows(self):
        code, state = self.run_pipeline(groups=["Flow"])
        text = self.doc(state, "Processa_Pedido")
        self.assertIn("| ProcessType | AutoLaunchedFlow | XML |", text)
        self.assertIn("| Status (versão recuperada) | Active | XML |", text)
        trig = self.doc(state, "Meu_Flow", "flow-trigger.md")
        self.assertIn("| RecordTriggerType | Update | XML |", trig)

    def test_custom_metadata_fields_records_without_values(self):
        code, state = self.run_pipeline(groups=["CustomMetadata", "CustomObject"])
        cmdt = self.doc(state, "Config__mdt")
        self.assertIn("| Ativo__c | Ativo | Checkbox | XML |", cmdt)
        self.assertIn("| Chave_API__c | Chave API | Text | XML |", cmdt)
        self.assertNotIn("Valor__c", cmdt)  # campos de outro objeto não entram
        self.assertNotIn("SENTINELA_VALOR_CMDT", cmdt)
        obj = self.doc(state, "Pedido__c")
        self.assertNotIn("Ativo__c", obj)

    def test_eca_sections_with_provenance(self):
        code, state = self.run_pipeline("mvp_complete", groups=["ExternalClientApp"])
        text = self.doc(state, "Minha_ECA")
        self.assertIn("**ExtlClntAppOauthSettings: Minha_ECA_oauth**", text)
        self.assertRegex(text, r"_Arquivo: `inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/"
                               r"components/extlClntAppOauthSettings/Minha_ECA_oauth\.ecaOauth-meta\.xml`"
                               r" · sha256 `[0-9a-f]{16}…`_")
        self.assertIn("| CommaSeparatedOauthScopes | Api, RefreshToken | XML |", text)
        self.assertIn("| IsEnabled | true | XML |", text)
        self.assertIn("| StartPage | None | XML |", text)
        self.assertIn("| IsProtected | false | XML |", text)
        self.assertIn("| DistributionState | Local | XML |", text)
        self.assertNotIn("Outra_ECA_oauth", text)
        self.assertNotIn("admin@example.com", text)

    def test_connected_app_only_allowed_oauth_properties(self):
        code, state = self.run_pipeline(groups=["ConnectedApp"])
        entry = self.primary(state, "Meu_App")
        text = self.read(entry["document"])
        self.assertIn("| scopes | Api, RefreshToken | XML |", text)
        for name in ("consumerKey", "callbackUrl", "consumerSecret"):
            self.assertNotIn(name, text)
        omitted = entry["omittedProperties"]
        self.assertIn("ConnectedApp:Meu_App:oauthConfig.consumerKey", omitted)
        self.assertIn("ConnectedApp:Meu_App:oauthConfig.callbackUrl", omitted)

    def test_sentinels_never_leak(self):
        code, state = self.run_pipeline("mvp_complete")
        self.assertEqual(code, 0, self.log.getvalue())
        log = self.log.getvalue()
        for p in self.root.rglob("*"):
            if not p.is_file() or "/components/" in p.as_posix():
                continue  # XML original (raw) é preservado intacto
            text = p.read_text(errors="ignore")
            for s in SECRET_SENTINELS:
                self.assertNotIn(s, text, f"segredo em {p}")
            if p.as_posix().split(self.root.as_posix())[1].startswith(("/saida/", "/runs/")):
                for s in POLICY_SENTINELS:
                    self.assertNotIn(s, text, f"valor bloqueado em {p}")
        for s in SECRET_SENTINELS + POLICY_SENTINELS:
            self.assertNotIn(s, log)
        norm = json.loads((self.root / "inventory/org-dev/api-v67/connected-apps/normalized/meu-app.json").read_text())
        self.assertEqual(norm["data"]["oauthConfig"]["consumerSecret"], "[REDACTED]")
        self.assertEqual(norm["fields"]["redacted"], ["oauthConfig.consumerSecret"])

    def test_missing_model_is_no_template_and_others_continue(self):
        (self.root / "documentation/models/api-v67/modelo-doc-flow-autolaunched-vapi-67.md").unlink()
        code, state = self.run_pipeline(groups=["Flow"])
        self.assertEqual(code, 0)
        entry = self.primary(state, "Processa_Pedido")
        self.assertEqual(entry["status"], st.SUCCESS)  # documento principal continua
        sub = entry["subDocuments"][0]
        self.assertEqual(sub["status"], st.NO_TEMPLATE)
        self.assertIsNone(sub["document"])
        warning = next(w for w in entry["warnings"] if w.startswith("NO_TEMPLATE"))
        for piece in ("Flow:Processa_Pedido", "contexto-flow-autolaunched.md",
                      "documentation/models/api-v67/modelo-doc-flow-autolaunched-vapi-67.md",
                      "documentation/contracts/flow-autolaunched.schema.json"):
            self.assertIn(piece, warning)
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.SUCCESS)
        self.assertIn("NO_TEMPLATE Flow:Processa_Pedido", self.log.getvalue())

    def test_missing_primary_contract_is_no_template(self):
        (self.root / "documentation/contracts/connected-app.schema.json").unlink()
        code, state = self.run_pipeline(groups=["ConnectedApp", "ExternalCredential"])
        app = self.primary(state, "Meu_App")
        self.assertEqual(app["status"], st.NO_TEMPLATE)
        self.assertTrue(any("contrato ausente: documentation/contracts/connected-app.schema.json" in w
                            for w in app["warnings"]))
        self.assertTrue((self.root / app["normalized"]).is_file())
        self.assertEqual(self.primary(state, "Minha_EC")["status"], st.SUCCESS)

    def test_out_of_scope_is_distinct_from_not_enabled(self):
        code, state = self.run_pipeline(groups=["Flow"])
        scope = {t["group"]: t["status"] for t in state.data["metadataTypes"] if t.get("stage") == "scope"}
        self.assertEqual(scope.get("ConnectedApp"), st.OUT_OF_SCOPE)
        self.assertNotIn("Flow", scope)
        enabled = [t for t in state.data["metadataTypes"] if t.get("stage") == "enabled"]
        self.assertTrue(all(t["group"] == "Flow" for t in enabled))


if __name__ == "__main__":
    unittest.main()
