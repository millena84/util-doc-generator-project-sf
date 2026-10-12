"""Testes de ponta a ponta com Salesforce CLI SIMULADA (tests/fixtures/bin/sf)."""

import io
import json
import os
import subprocess
import unittest

from tests.helpers import (FAKE_SF, FAKE_TOKEN, ROOT, FakeMetadataClient, TempProject,
                           fake_sf_env)
from salesforce_docs import status as st
from salesforce_docs.pipeline.document_pipeline import (EXIT_FAILURE, EXIT_OK, EXIT_SESSION,
                                                        DocumentPipeline)
from salesforce_docs.salesforce.cli_runner import CliRunner


class PipelineTestBase(unittest.TestCase):
    def setUp(self):
        self.proj = TempProject()
        self.root = self.proj.dir
        self.calls_file = self.root / "sf-calls.log"
        os.environ["FAKE_SF_STATE"] = str(self.calls_file)

    def tearDown(self):
        self.proj.cleanup()
        for k in ("FAKE_SF_SCENARIO", "FAKE_SF_STATE"):
            os.environ.pop(k, None)

    def run_pipeline(self, scenario="", md_kwargs=None, **kwargs):
        fake_sf_env(scenario)
        self.log = io.StringIO()
        md_kwargs = md_kwargs or {}
        pipeline = DocumentPipeline(self.root, runner=CliRunner(executable=str(FAKE_SF)),
                                    metadata_client_factory=lambda s: FakeMetadataClient(s, **md_kwargs),
                                    stream=self.log)
        return pipeline.run(**kwargs)

    def primary(self, state, component):
        for c in state.data["components"]:
            if c.get("role") == "primary" and c["component"] == component:
                return c
        self.fail(f"componente {component} não registrado")

    def read(self, relpath):
        return (self.root / relpath).read_text(encoding="utf-8")


class FullRunTest(PipelineTestBase):
    def test_full_run_success(self):
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["status"], st.SUCCESS)
        self.assertEqual(state.data["apiVersion"], "67.0")
        cat = self.root / "catalog" / "org-dev" / "api-v67"
        for f in ("org-display.raw.json", "metadata-types.raw.json", "metadata-types.index.json",
                  "schemas/flow.describevaluetype.raw.json", "schemas/flow.schema.json"):
            self.assertTrue((cat / f).is_file(), f)
        flow = self.primary(state, "Meu_Flow")
        self.assertEqual(flow["status"], st.SUCCESS)
        self.assertEqual(flow["xml"], "inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml")
        self.assertEqual(flow["normalized"], "inventory/org-dev/api-v67/flows/normalized/meu-flow.json")
        self.assertEqual(flow["internalData"], "inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json")
        self.assertRegex(flow["document"], r"^saida/docs/doc-org-\d{6}/run-[\d-]+/doc-meu-flow-flow\.md$")
        self.assertIn(state.run_id, flow["document"])  # saída isolada por execução (BY_RUN)
        self.assertTrue(self.read(flow["retrieveRaw"]))
        self.assertTrue((self.root / "runs" / f"{state.run_id}.json").is_file())

    def test_raw_is_byte_identical_to_cli_output(self):
        self.run_pipeline()
        fake_sf_env("")
        out = subprocess.run([str(FAKE_SF), "org", "list", "metadata-types", "--json"],
                             capture_output=True, text=True).stdout
        self.assertEqual(self.read("catalog/org-dev/api-v67/metadata-types.raw.json"), out)
        xml_src = (ROOT / "tests/fixtures/source/flows/Meu_Flow.flow-meta.xml").read_bytes()
        xml_dst = (self.root / "inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml").read_bytes()
        self.assertEqual(xml_src, xml_dst)

    def test_flow_with_flow_definition_same_document(self):
        code, state = self.run_pipeline(groups=["Flow"])
        doc = self.read(self.primary(state, "Meu_Flow")["document"])
        self.assertIn("**FlowDefinition: Meu_Flow**", doc)
        self.assertIn("| ActiveVersionNumber | 2 | XML |", doc)
        self.assertIn("| Meu_Flow | FlowDefinition | XML |", doc)
        self.assertIn("| Status | v1: Obsolete; v2: Active | Objeto interno |", doc)
        subs = self.primary(state, "Meu_Flow")["subDocuments"]
        self.assertEqual([s["status"] for s in subs], [st.SUCCESS])
        self.assertIn("RecordAfterSave", self.read(subs[0]["document"]))
        screens = self.primary(state, "Tela_Cadastro")["subDocuments"]
        self.assertIn("| Nome | InputField | true | XML |", self.read(screens[0]["document"]))

    def test_external_client_app_with_related_components(self):
        code, state = self.run_pipeline(groups=["ExternalClientApp"])
        eca = self.primary(state, "Minha_ECA")
        self.assertEqual(eca["status"], st.SUCCESS)
        self.assertEqual(eca["relatedComponents"],
                         [{"metadataType": "ExtlClntAppOauthSettings", "fullName": "Minha_ECA_oauth"}])
        doc = self.read(eca["document"])
        self.assertIn("| Minha_ECA_oauth | ExtlClntAppOauthSettings | XML |", doc)
        self.assertNotIn("Outra_ECA_oauth", doc)
        self.assertIn("| extlClntAppOauthSettings | ExtlClntAppOauthSettings | XML |", doc)
        types = {(t["metadataType"], t.get("stage")): t["status"] for t in state.data["metadataTypes"]}
        # ExternalCredential/ConnectedApp têm documento próprio; NamedCredential etc. não são do MVP
        self.assertNotIn(("NamedCredential", "enabled"), types)
        self.assertNotIn(("CorsWhitelistOrigin", "enabled"), types)

    def test_custom_object_and_custom_metadata(self):
        code, state = self.run_pipeline(groups=["CustomObject", "CustomMetadata"])
        obj = self.read(self.primary(state, "Pedido__c")["document"])
        self.assertIn("| Valor__c | Valor | Currency | XML |", obj)
        self.assertIn("| Pedido__c.Padrao | Padrão | true | XML |", obj)
        cmdt = self.primary(state, "Config__mdt")
        self.assertEqual(cmdt["metadataType"], "CustomMetadata")
        self.assertIn("inventory/org-dev/api-v67/custom-metadata/", cmdt["xml"])
        doc = self.read(cmdt["document"])
        self.assertIn("| Config.Padrao | Config Padrao | false | XML |", doc)
        self.assertIn("| Visibility | Public | XML |", doc)

    def test_token_never_leaks(self):
        code, state = self.run_pipeline()
        leaks = []
        for p in self.root.rglob("*"):
            if p.is_file() and p.name != "org-display.raw.json" and FAKE_TOKEN in p.read_text(errors="ignore"):
                leaks.append(str(p))
        self.assertEqual(leaks, [])
        self.assertNotIn(FAKE_TOKEN, self.log.getvalue())

    def test_session_token_cleared_after_run(self):
        sessions = []
        fake_sf_env("")
        self.log = io.StringIO()

        def factory(session):
            sessions.append(session)
            return FakeMetadataClient(session)

        pipeline = DocumentPipeline(self.root, runner=CliRunner(executable=str(FAKE_SF)),
                                    metadata_client_factory=factory, stream=self.log)
        code, _ = pipeline.run(groups=["Flow"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertTrue(sessions and all(s.cleared for s in sessions))

    @unittest.skipIf(os.name != "posix", "permissões POSIX")
    def test_org_display_raw_is_private(self):
        self.run_pipeline(groups=["Flow"])
        raw = self.root / "catalog" / "org-dev" / "api-v67" / "org-display.raw.json"
        self.assertEqual(raw.stat().st_mode & 0o777, 0o600)

    def test_sensitive_xml_warning_and_not_rendered(self):
        code, state = self.run_pipeline(groups=["ConnectedApp"])
        app = self.primary(state, "Meu_App")
        self.assertTrue(any("consumerSecret" in w for w in app["warnings"]))
        self.assertNotIn("SEGREDO_SIMULADO", self.read(app["document"]))

    def test_api_version_override(self):
        code, state = self.run_pipeline(api_version="66.0", groups=["Flow"])
        self.assertEqual(state.data["session"]["apiVersion"], "66.0")
        self.assertEqual(state.data["session"]["detectedApiVersion"], "67.0")
        self.assertTrue((self.root / "catalog/org-dev/api-v66/org-display.raw.json").is_file())
        # Não existe documentation/models/api-v66 => NO_TEMPLATE, dados preservados.
        flow = self.primary(state, "Meu_Flow")
        self.assertEqual(flow["status"], st.NO_TEMPLATE)
        self.assertIsNone(flow["document"])
        self.assertTrue((self.root / flow["normalized"]).is_file())


class FailureModesTest(PipelineTestBase):
    def test_cli_below_minimum_stops(self):
        code, state = self.run_pipeline("old_cli")
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["status"], st.FAILED)
        self.assertEqual(state.data["failure"]["code"], "CLI_VERSION_TOO_LOW")
        self.assertFalse((self.root / "catalog").exists())

    def test_org_not_authenticated_stops(self):
        code, state = self.run_pipeline("no_alias")
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_AUTHENTICATED")
        self.assertEqual(state.data["failure"]["suggestion"], "sf org login web --alias dev")
        self.assertIn("sf org login web --alias dev", self.log.getvalue())

    def test_org_disconnected_stops(self):
        code, state = self.run_pipeline("disconnected")
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_CONNECTED")
        self.assertFalse((self.root / "catalog").exists())

    def test_metadata_type_not_enabled(self):
        cfg_path = self.root / "config" / "metadata-types-mvp.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["metadataTypeGroups"][1]["primaryMetadataType"] = "ExternalClientApp"
        cfg_path.write_text(json.dumps(cfg))
        code, state = self.run_pipeline(groups=["ExternalClientApp"])
        statuses = [t for t in state.data["metadataTypes"] if t["metadataType"] == "ExternalClientApp"]
        self.assertEqual(statuses[0]["status"], st.NOT_ENABLED)
        self.assertEqual([c for c in state.data["components"] if c["group"] == "ExternalClientApp"], [])

    def test_type_without_components(self):
        code, state = self.run_pipeline("empty=Flow", groups=["Flow"])
        inv = [t for t in state.data["metadataTypes"]
               if t["metadataType"] == "Flow" and t.get("stage") == "inventory"]
        self.assertEqual(inv[0]["status"], st.NO_COMPONENTS)
        self.assertEqual(state.data["components"], [])

    def test_retrieve_failed_does_not_stop_others(self):
        code, state = self.run_pipeline("fail_retrieve=Meu_Flow", groups=["Flow"])
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.RETRIEVE_FAILED)
        self.assertEqual(self.primary(state, "Tela_Cadastro")["status"], st.SUCCESS)
        self.assertEqual(state.data["status"], st.PARTIAL_SUCCESS)
        self.assertEqual(code, EXIT_OK)

    def test_retrieve_mismatch(self):
        code, state = self.run_pipeline("mismatch_retrieve=Meu_Flow", groups=["Flow"])
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.MISMATCH)

    def test_missing_template(self):
        (self.root / "documentation/models/api-v67/modelo-doc-connectedapp-vapi-67.md").unlink()
        code, state = self.run_pipeline(groups=["ConnectedApp"])
        app = self.primary(state, "Meu_App")
        self.assertEqual(app["status"], st.NO_TEMPLATE)
        self.assertIsNone(app["document"])
        self.assertTrue((self.root / app["normalized"]).is_file())
        self.assertFalse(list((self.root / "saida").rglob("*connected-app.md")) if (self.root / "saida").exists() else [])

    def test_schema_unavailable_is_not_blocking(self):
        code, state = self.run_pipeline(groups=["Flow"], md_kwargs={"unavailable": {"Flow"}})
        schema = [t for t in state.data["metadataTypes"]
                  if t["metadataType"] == "Flow" and t.get("stage") == "schema"]
        self.assertEqual(schema[0]["status"], st.SCHEMA_UNAVAILABLE)
        self.assertIn("INSUFFICIENT_ACCESS", schema[0]["detail"])
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.SUCCESS)
        self.assertTrue(list((self.root / "runs").rglob("flow.describevaluetype.raw.json")))

    def test_internal_data_unavailable_is_not_blocking(self):
        code, state = self.run_pipeline(groups=["ExternalCredential"])
        ec = self.primary(state, "Minha_EC")
        self.assertEqual(ec["status"], st.SUCCESS)
        self.assertEqual(ec["internalDataStatus"], st.INTERNAL_DATA_UNAVAILABLE)
        self.assertIn("| Não informado | Não informado | Objeto interno |", self.read(ec["document"]))

    def test_session_expired_on_metadata_api(self):
        code, state = self.run_pipeline(md_kwargs={"expired": True})
        self.assertEqual(code, EXIT_SESSION)
        self.assertEqual(state.data["status"], st.INTERRUPTED)
        self.assertEqual(state.data["failure"]["code"], "SESSION_EXPIRED")

    def test_session_expired_then_resume(self):
        code, state = self.run_pipeline("expire_on_retrieve=Pedido__c")
        self.assertEqual(code, EXIT_SESSION)
        self.assertEqual(state.data["status"], st.INTERRUPTED)
        self.assertEqual(self.primary(state, "Pedido__c")["status"], st.RETRY_REQUIRED)
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.SUCCESS)
        self.assertIn("sf org login web --alias dev", self.log.getvalue())
        self.calls_file.write_text("")
        code2, state2 = self.run_pipeline("", resume=state.run_id)
        self.assertEqual(code2, EXIT_OK, self.log.getvalue())
        self.assertEqual(state2.data["resumedFrom"], state.run_id)
        self.assertEqual(self.primary(state2, "Pedido__c")["status"], st.SUCCESS)
        self.assertEqual(self.primary(state2, "Meu_Flow").get("carriedFrom"), state.run_id)
        calls = self.calls_file.read_text()
        self.assertNotIn("Flow:Meu_Flow", calls)
        self.assertIn("CustomObject:Pedido__c", calls)


class RegenerateTest(PipelineTestBase):
    def test_regenerate_from_raw_without_org(self):
        code, state = self.run_pipeline()
        docs = {c["unitId"]: self.read(c["document"]) for c in state.data["components"]
                if c.get("role") == "primary" and c.get("document")}
        for c in state.data["components"]:
            if c.get("role") == "primary" and c.get("document"):
                (self.root / c["document"]).unlink()
        for n in (self.root / "inventory").rglob("normalized/*.json"):
            n.unlink()
        (self.root / "catalog/org-dev/api-v67/metadata-types.index.json").unlink()
        fake_sf_env("old_cli")  # qualquer chamada à CLI falharia
        pipeline = DocumentPipeline(self.root, runner=CliRunner(executable="/nao/existe/sf"),
                                    stream=io.StringIO())
        code2, state2 = pipeline.regenerate(state.run_id)
        self.assertEqual(code2, EXIT_OK)
        regenerated = {c["unitId"]: c for c in state2.data["components"] if c.get("document")}
        self.assertEqual(set(regenerated), set(docs))
        for unit_id, content in docs.items():
            self.assertIn(state2.run_id, regenerated[unit_id]["document"])  # nova pasta da execução
            self.assertEqual(self.read(regenerated[unit_id]["document"]), content, unit_id)
        self.assertTrue((self.root / "catalog/org-dev/api-v67/metadata-types.index.json").is_file())
        self.assertTrue((self.root / "inventory/org-dev/api-v67/flows/normalized/meu-flow.json").is_file())


class ShellWrapperTest(unittest.TestCase):
    def test_validate_config_via_shell(self):
        proc = subprocess.run(["bash", str(ROOT / "bin" / "sf-docs.sh"), "validate-config"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Configuração válida", proc.stdout)


if __name__ == "__main__":
    unittest.main()
