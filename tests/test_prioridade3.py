"""Prioridade 3 — segurança e execução: aprovação da org, mascaramento, proteção de
arquivos, cobertura, saída sem sobrescrita silenciosa, retomada compatível,
timeouts e escala. CLI e Metadata API SIMULADAS; nenhuma org real.
"""

import io
import json
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path

from tests.helpers import FAKE_SF, FAKE_TOKEN, SIMULATED_ORG_ID, FakeMetadataClient, fake_sf_env
from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import EXIT_FAILURE, EXIT_OK, EXIT_SESSION, DocumentPipeline
from salesforce_docs.pipeline.output_writer import OutputWriter
from salesforce_docs.runs.run_logger import RunLogger
from salesforce_docs.runs.run_state import RunState
from salesforce_docs.salesforce.cli_runner import CliRunner
from salesforce_docs.utils import Masker


class P3Base(PipelineTestBase):
    def config(self, **changes):
        path = self.root / "config" / "config.json"
        cfg = json.loads(path.read_text())
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
        path.write_text(json.dumps(cfg))

    def calls(self):
        return self.calls_file.read_text() if self.calls_file.exists() else ""

    def pipeline(self, scenario="", timeout=900):
        fake_sf_env(scenario)
        self.log = io.StringIO()
        return DocumentPipeline(self.root, runner=CliRunner(executable=str(FAKE_SF), timeout=timeout),
                                metadata_client_factory=lambda s: FakeMetadataClient(s), stream=self.log)


class OrgApprovalTest(P3Base):
    def test_no_collection_without_approved_org(self):
        self.config(approvedOrgs=[])
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_APPROVED")
        self.assertIn(SIMULATED_ORG_ID, state.data["failure"]["message"])
        self.assertIn(SIMULATED_ORG_ID, state.data["failure"]["suggestion"])
        calls = self.calls().splitlines()
        self.assertEqual([c.split(" --")[0] for c in calls], ["--version", "org list", "org display"])
        self.assertFalse((self.root / "inventory").exists())

    def test_identity_mismatch_blocks(self):
        self.config(approvedOrgs=[{"orgId": SIMULATED_ORG_ID, "alias": "producao"}])
        code, state = self.run_pipeline()
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_APPROVED")
        self.assertIn("alias (producao ≠ dev)", state.data["failure"]["message"])
        self.config(approvedOrgs=[{"orgId": SIMULATED_ORG_ID, "username": "outro@example.com"}])
        code, state = self.run_pipeline()
        self.assertIn("username", state.data["failure"]["message"])
        self.config(approvedOrgs=[{"orgId": "00D000000000001AAA"}])
        code, state = self.run_pipeline()
        self.assertIn("não está em approvedOrgs", state.data["failure"]["message"])
        self.assertNotIn("org list metadata", self.calls())

    def test_15_char_org_id_and_full_identity_are_accepted(self):
        self.config(approvedOrgs=[{"orgId": SIMULATED_ORG_ID[:15], "alias": "dev",
                                   "username": "usuario.simulado@example.com",
                                   "instanceUrl": "https://simulado.my.salesforce.com/"}])
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertTrue(state.data["orgApproval"]["approved"])

    def test_invalid_approved_orgs_rejected_at_load(self):
        for bad in ([{"orgId": "123"}], [{"alias": "dev"}], {"orgId": SIMULATED_ORG_ID},
                    [{"orgId": SIMULATED_ORG_ID, "senha": "x"}]):
            self.config(approvedOrgs=bad)
            with self.assertRaises(ConfigError, msg=str(bad)):
                DocumentPipeline(self.root)


class MaskingAndFilesTest(P3Base):
    def test_token_in_cli_error_never_reaches_state_or_log(self):
        code, state = self.run_pipeline("leak_token_on_retrieve=Meu_Flow", groups=["Flow"])
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.RETRIEVE_FAILED)
        self.assertNotIn(FAKE_TOKEN, state.path.read_text())
        self.assertNotIn(FAKE_TOKEN, self.log.getvalue())
        for p in (self.root / "saida").rglob("*"):
            if p.is_file():
                self.assertNotIn(FAKE_TOKEN, p.read_text())
        self.assertIn("***", json.dumps(state.data))

    def test_secret_values_from_xml_are_masked_everywhere(self):
        pipeline = self.pipeline()
        code, state = pipeline.run(groups=["ConnectedApp", "NamedCredential"])
        self.assertEqual(pipeline.masker("x SEGREDO_SIMULADO_NAO_RENDERIZAR y"), "x *** y")
        self.assertEqual(pipeline.masker("SENTINELA_SENHA_LEGADA_NAO_RENDERIZAR"), "***")
        # Máscara recursiva em estruturas aninhadas do run state.
        state.data["events"].append({"nested": [{"deep": "SEGREDO_SIMULADO_NAO_RENDERIZAR"}]})
        state.save()
        self.assertNotIn("SEGREDO_SIMULADO_NAO_RENDERIZAR", state.path.read_text())

    @unittest.skipIf(os.name == "nt", "permissões POSIX")
    def test_private_file_permissions(self):
        code, state = self.run_pipeline(groups=["ConnectedApp"])
        api = self.root / "inventory/org-dev/api-v67/connected-apps"
        for path in (api / "inventory.raw.json", api / "retrieve/meu-app.raw.json",
                     api / "components/connectedApps/Meu_App.connectedApp-meta.xml",
                     api / "normalized/meu-app.json", state.path,
                     self.root / "catalog/org-dev/api-v67/org-display.sanitized.json"):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600, str(path))

    def test_delete_org_display_raw_after_run(self):
        self.config(dataProtection={"orgDisplayRaw": "DELETE_AFTER_RUN"})
        # CLI que não exibe o token: o raw é gravado intacto e apagado ao fim.
        code, state = self.run_pipeline("redact_display_token", groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_OK)
        self.assertFalse((self.root / "catalog/org-dev/api-v67/org-display.raw.json").exists())
        self.assertEqual(state.data["dataProtection"]["removed"],
                         ["catalog/org-dev/api-v67/org-display.raw.json"])


class CoverageTest(P3Base):
    def test_complete_coverage(self):
        code, state = self.run_pipeline(groups=["RemoteSiteSetting", "Certificate"])
        cov = state.data["coverage"]
        self.assertEqual(cov["status"], "COMPLETE")
        self.assertEqual((cov["documented"], cov["inScope"], cov["gapCount"]), (2, 2, 0))
        self.assertIn("Cobertura: COMPLETE", self.log.getvalue())

    def test_gaps_make_coverage_incomplete_even_when_run_succeeds(self):
        (self.root / "documentation/models/api-v67/modelo-doc-flow-autolaunched-vapi-67.md").unlink()
        code, state = self.run_pipeline(groups=["Flow", "ExternalCredential"])
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)  # terminou, mas não é SUCCESS
        cov = state.data["coverage"]
        self.assertEqual(cov["status"], "INCOMPLETE")      # ...mas a cobertura tem lacunas
        self.assertEqual(cov["gaps"]["subDocuments"],
                         [{"component": "Processa_Pedido", "status": st.NO_TEMPLATE}])
        self.assertEqual(cov["gaps"]["internalDataUnavailable"], ["ExternalCredential:Minha_EC"])
        self.assertIn("ConnectedApp", cov["outOfScopeGroups"])

    def test_failed_run_is_incomplete(self):
        self.config(approvedOrgs=[])
        code, state = self.run_pipeline()
        self.assertFalse(state.data["coverage"]["executionFinished"])
        self.assertEqual(state.data["coverage"]["status"], "INCOMPLETE")


class OutputIsolationTest(P3Base):
    def doc(self, state, comp):
        return self.root / self.primary(state, comp)["document"]

    def test_second_run_archives_different_content(self):
        self.config(execution={"outputLayout": "BY_DATE"})  # layout compartilhado por data
        code, s1 = self.run_pipeline(groups=["RemoteSiteSetting"])
        first = self.doc(s1, "Meu_Site")
        original = first.read_text()
        time.sleep(1.1)  # runId distinto
        code, s2 = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(s2.data["output"]["replaced"], [])  # mesmo conteúdo: nada a arquivar
        model = self.root / "documentation/models/api-v67/modelo-doc-remote-site-setting-vapi-67.md"
        model.write_text(model.read_text().replace("## Identificação", "## Identificação do site"))
        time.sleep(1.1)
        code, s3 = self.run_pipeline(groups=["RemoteSiteSetting"])
        replaced = s3.data["output"]["replaced"]
        self.assertEqual(len(replaced), 1)
        self.assertEqual(replaced[0]["previousRun"], s2.run_id)
        archived = self.root / replaced[0]["archivedAs"]
        self.assertEqual(archived.read_text(), original)
        self.assertIn("Identificação do site", self.doc(s3, "Meu_Site").read_text())

    def test_by_run_layout_isolates_each_run(self):
        self.config(execution={"outputLayout": "BY_RUN"})
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        doc = self.primary(state, "Meu_Site")["document"]
        self.assertIn(f"/{state.run_id}/doc-meu-site-remote-site-setting.md", doc)

    def test_writer_collision_and_unknown_origin(self):
        tmp = Path(tempfile.mkdtemp())
        state = RunState.create(tmp / "runs", "dev")
        log = RunLogger(Masker(), stream=io.StringIO())
        out = tmp / "docs"
        out.mkdir()
        (out / "doc-x-flow.md").write_text("manual\n")
        w = OutputWriter(out, state.run_id, "BY_DATE", tmp, state, log)
        p1 = w.write("doc-x-flow.md", "A\n", "Flow:Meu_Flow")
        p2 = w.write("doc-x-flow.md", "B\n", "Flow:Meu-Flow")
        self.assertNotEqual(p1, p2)
        self.assertEqual((p1.read_text(), p2.read_text()), ("A\n", "B\n"))
        self.assertEqual(state.data["output"]["collisions"][0]["component"], "Flow:Meu-Flow")
        archived = state.data["output"]["replaced"][0]["archivedAs"]
        self.assertIn("_substituidos/origem-desconhecida", archived)
        self.assertEqual((tmp / archived).read_text(), "manual\n")


class ResumeCompatibilityTest(P3Base):
    def interrupted(self):
        code, state = self.run_pipeline("expire_on_retrieve=Pedido__c")
        self.assertEqual(code, EXIT_SESSION)
        self.calls_file.write_text("")
        return state

    def test_changed_contract_reprocesses_only_affected_units(self):
        first = self.interrupted()
        contract = self.root / "documentation/contracts/flow.schema.json"
        data = json.loads(contract.read_text())
        data["notes"] = "alterado"
        contract.write_text(json.dumps(data))
        code, state = self.run_pipeline("", resume=first.run_id)
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        rep = {r["unitId"]: r["reasons"] for r in state.data["resume"]["reprocessed"]}
        self.assertIn("contrato flow.schema.json mudou", rep["Flow:Flow:Meu_Flow"])
        self.assertIn("ConnectedApp:ConnectedApp:Meu_App", state.data["resume"]["reused"])
        self.assertIn("Flow:Meu_Flow", self.calls())
        self.assertNotIn("ConnectedApp:Meu_App", self.calls())

    def test_different_org_reuses_nothing(self):
        first = self.interrupted()
        data = json.loads(first.path.read_text())
        data["fingerprint"]["orgId"] = "00D000000000009AAA"
        first.path.write_text(json.dumps(data))
        code, state = self.run_pipeline("", resume=first.run_id)
        self.assertEqual(state.data["resume"]["reused"], [])
        self.assertTrue(all("org mudou" in r["reasons"][0] for r in state.data["resume"]["reprocessed"]))
        self.assertIn("ConnectedApp:Meu_App", self.calls())

    def test_scope_change_and_missing_document(self):
        first = self.interrupted()
        (self.root / self.primary(first, "Meu_App")["document"]).unlink()
        code, state = self.run_pipeline("", resume=first.run_id, groups=["ConnectedApp", "Flow"])
        rep = {r["unitId"]: r["reasons"] for r in state.data["resume"]["reprocessed"]}
        self.assertIn("fora do escopo atual", rep["ExternalCredential:ExternalCredential:Minha_EC"])
        self.assertTrue(any("não existe mais" in r for r in rep["ConnectedApp:ConnectedApp:Meu_App"]))
        self.assertIn("Flow:Flow:Meu_Flow", state.data["resume"]["reused"])
        self.assertIn("ConnectedApp:Meu_App", self.calls())


class ExecutionRobustnessTest(P3Base):
    def test_timeout_fails_component_and_others_continue(self):
        pipeline = self.pipeline("sleep_on_retrieve=Meu_Flow", timeout=3)
        code, state = pipeline.run(groups=["Flow"])
        self.assertEqual(code, EXIT_OK)
        entry = self.primary(state, "Meu_Flow")
        self.assertEqual(entry["status"], st.RETRIEVE_FAILED)
        self.assertIn("Timeout", entry["error"])
        self.assertEqual(self.primary(state, "Tela_Cadastro")["status"], st.SUCCESS)
        self.assertEqual(state.data["status"], st.PARTIAL_SUCCESS)

    def test_scale_many_components(self):
        n = 40
        started = time.monotonic()
        code, state = self.run_pipeline(f"scale_flows={n}", groups=["Flow"])
        elapsed = time.monotonic() - started
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        prim = [c for c in state.data["components"] if c["role"] == "primary"]
        self.assertEqual(len(prim), n)
        self.assertTrue(all(c["status"] == st.SUCCESS for c in prim))
        docs = {c["document"] for c in prim}
        self.assertEqual(len(docs), n)  # nenhum documento sobrescrito
        self.assertEqual(state.data["coverage"]["documented"], n)
        self.assertLess(elapsed, 180)


if __name__ == "__main__":
    unittest.main()
