"""Refatoração 3 — mitigação de riscos de segurança, cobertura e execução.
CLI e Metadata API SIMULADAS; nenhuma org real.
"""

import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import timedelta
from pathlib import Path
from unittest import mock

from tests.helpers import FAKE_SF, FAKE_TOKEN, SIMULATED_ORG_ID, FakeMetadataClient, fake_sf_env
from tests.test_prioridade3 import P3Base
from salesforce_docs import cli
from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import EXIT_FAILURE, EXIT_OK, EXIT_SESSION, DocumentPipeline
from salesforce_docs.pipeline.output_writer import OutputWriter
from salesforce_docs.runs.retention import MARKER, purge
from salesforce_docs.runs.run_state import RunState
from salesforce_docs.salesforce.cli_runner import CliRunner
from salesforce_docs.utils import now_local

SENTINEL = "SENTINELA-SEGREDO-NAO-DEVE-VAZAR-7f3a"


class R3Base(P3Base):
    def make(self, scenario="", **kwargs):
        fake_sf_env(scenario)
        self.log = io.StringIO()
        return DocumentPipeline(self.root, runner=CliRunner(executable=str(FAKE_SF)),
                                metadata_client_factory=lambda s: FakeMetadataClient(s),
                                stream=self.log, **kwargs)

    def files_containing(self, needle):
        hits = []
        for f in self.root.rglob("*"):
            if f.is_file() and needle in f.read_text(encoding="utf-8", errors="ignore"):
                hits.append(str(f.relative_to(self.root)))
        return hits

    def summary_text(self, state):
        return (self.root / state.data["summary"]).read_text(encoding="utf-8")


class OrgIdentityAndConfirmationTest(R3Base):
    def test_org_without_id_is_blocked_before_inventory(self):
        code, state = self.run_pipeline("no_org_id")
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["failure"]["code"], "ORG_IDENTITY_UNVERIFIABLE")
        self.assertNotIn("org list metadata", self.calls())
        self.assertNotIn("show-access-token", self.calls())

    def test_interactive_confirmation_with_exact_org_id(self):
        self.config(approvedOrgs=[])
        seen = []
        pipeline = self.make(interactive=True, confirm_org=lambda ident: seen.append(ident) or SIMULATED_ORG_ID)
        code, state = pipeline.run(groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(seen[0]["orgId"], SIMULATED_ORG_ID)
        self.assertEqual(state.data["orgApproval"]["method"], "INTERACTIVE")
        self.assertIn("apenas para esta execução", self.log.getvalue())
        # A aprovação interativa não é gravada na configuração.
        cfg = json.loads((self.root / "config/config.json").read_text())
        self.assertEqual(cfg["approvedOrgs"], [])

    def test_interactive_confirmation_wrong_or_empty_refuses(self):
        self.config(approvedOrgs=[])
        for typed in ("00D000000000001AAA", "", "sim", SIMULATED_ORG_ID[:10]):
            self.calls_file.write_text("")
            pipeline = self.make(interactive=True, confirm_org=lambda ident, t=typed: t)
            code, state = pipeline.run(groups=["RemoteSiteSetting"])
            self.assertEqual(code, EXIT_FAILURE, typed)
            self.assertEqual(state.data["failure"]["code"], "ORG_NOT_APPROVED")
            self.assertNotIn("org list metadata", self.calls())
            self.assertNotIn("show-access-token", self.calls())

    def test_without_terminal_never_prompts(self):
        self.config(approvedOrgs=[])
        asked = []
        pipeline = self.make(interactive=False, confirm_org=lambda ident: asked.append(1) or SIMULATED_ORG_ID)
        code, state = pipeline.run(groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(asked, [])
        self.assertEqual(state.data["orgApproval"]["method"], "NON_INTERACTIVE_REFUSED")


class TokenAcquisitionTest(R3Base):
    def test_hidden_display_token_uses_show_access_token_and_is_never_persisted(self):
        code, state = self.run_pipeline("redact_display_token", groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["tokenSource"], "sf org auth show-access-token")
        calls = [c.split(" --")[0] for c in self.calls().splitlines()]
        self.assertLess(calls.index("org display"), calls.index("org auth show-access-token"))
        self.assertLess(calls.index("org auth show-access-token"), calls.index("org list metadata"))
        self.assertEqual(self.files_containing(FAKE_TOKEN), [])
        self.assertNotIn(FAKE_TOKEN, self.log.getvalue())

    def test_token_unavailable_fails_before_inventory(self):
        code, state = self.run_pipeline("redact_display_token,no_show_access_token")
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["failure"]["code"], "ACCESS_TOKEN_UNAVAILABLE")
        self.assertIn("sf org login web --alias dev", state.data["failure"]["suggestion"])
        self.assertNotIn("org list metadata", self.calls())

    def test_token_is_only_requested_after_approval(self):
        self.config(approvedOrgs=[])
        code, state = self.run_pipeline("redact_display_token")
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_APPROVED")
        self.assertNotIn("show-access-token", self.calls())


class UnexpectedErrorTest(R3Base):
    def test_unexpected_exception_is_masked_and_state_is_consistent(self):
        pipeline = self.make()

        def boom(*a, **k):
            raise RuntimeError(f"falha com {FAKE_TOKEN}")
        pipeline._steps7_to_10 = boom
        with self.assertRaises(RuntimeError):
            pipeline.run(groups=["RemoteSiteSetting"])
        path = RunState.find(self.root / "runs", "latest")
        data = json.loads(path.read_text())
        self.assertEqual(data["status"], st.FAILED)
        self.assertEqual(data["failure"]["code"], "UNEXPECTED_ERROR")
        self.assertIn("RuntimeError", data["failure"]["message"])
        self.assertNotIn(FAKE_TOKEN, path.read_text())
        self.assertNotIn(FAKE_TOKEN, self.log.getvalue())
        self.assertTrue((self.root / data["summary"]).is_file())
        self.assertNotIn(FAKE_TOKEN, (self.root / data["summary"]).read_text())

    def test_cli_masks_unexpected_error(self):
        def boom(self_, **kwargs):
            self_.masker.add(SENTINEL)
            raise RuntimeError(f"erro {SENTINEL}")
        err, out = io.StringIO(), io.StringIO()
        with mock.patch.object(DocumentPipeline, "run", boom), redirect_stderr(err), redirect_stdout(out):
            code = cli.main(["--project-root", str(self.root), "run", "--non-interactive"])
        self.assertEqual(code, 1)
        self.assertIn("ERRO inesperado (RuntimeError)", err.getvalue())
        self.assertNotIn(SENTINEL, err.getvalue() + out.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_document_write_error_fails_only_that_unit(self):
        original = OutputWriter.write

        def write(self_, filename, text, component_key):
            if "Meu_Flow" in component_key:
                raise PermissionError(13, "Permission denied", filename)
            return original(self_, filename, text, component_key)
        with mock.patch.object(OutputWriter, "write", write):
            code, state = self.run_pipeline(groups=["Flow"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.FAILED)
        self.assertEqual(self.primary(state, "Tela_Cadastro")["status"], st.SUCCESS)
        self.assertEqual(state.data["status"], st.PARTIAL_SUCCESS)
        self.assertEqual(state.data["progress"]["pending"], [])


class SummaryAndMetricsTest(R3Base):
    def test_summary_lists_status_coverage_and_gaps(self):
        (self.root / "documentation/models/api-v67/modelo-doc-remote-site-setting-vapi-67.md").unlink()
        code, state = self.run_pipeline(groups=["RemoteSiteSetting", "Flow"])
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        text = self.summary_text(state)
        self.assertIn("`COMPLETED_WITH_GAPS`", text)
        self.assertIn("NÃO está completa", text)
        self.assertIn("Sem modelo/contrato (", text)
        self.assertIn(SIMULATED_ORG_ID, text)
        self.assertIn("ALLOWLIST", text)
        self.assertIn("## Chamadas à CLI", text)
        self.assertNotIn(FAKE_TOKEN, text)

    def test_metrics_by_metadata_type(self):
        code, state = self.run_pipeline(groups=["Flow"])
        metrics = state.data["metrics"]
        self.assertGreater(metrics["commands"], 0)
        self.assertIn("Flow", metrics["byMetadataType"])
        self.assertEqual(metrics["retries"], 0)
        self.assertIn("timeoutSeconds", metrics)

    def test_interrupted_run_records_pending_units(self):
        code, state = self.run_pipeline("expire_on_retrieve=Pedido__c")
        self.assertEqual(code, EXIT_SESSION)
        progress = state.data["progress"]
        self.assertTrue(progress["pending"])
        self.assertTrue(any("Pedido__c" in u for u in progress["pending"]))
        self.assertEqual(progress["completed"] + len(progress["pending"]), progress["planned"])
        self.assertIn("INTERRUPTED", self.summary_text(state))


class ResumeAndRegenerateTest(R3Base):
    def interrupted(self):
        code, state = self.run_pipeline("expire_on_retrieve=Pedido__c")
        self.assertEqual(code, EXIT_SESSION)
        self.calls_file.write_text("")
        return state

    def test_resume_rejects_changed_xml(self):
        first = self.interrupted()
        xml = self.root / self.primary(first, "Meu_Flow")["xml"]
        xml.write_text(xml.read_text() + "<!-- alterado -->")
        code, state = self.run_pipeline("", resume=first.run_id)
        rep = {r["unitId"]: r["reasons"] for r in state.data["resume"]["reprocessed"]}
        self.assertTrue(any("XML de origem alterado" in r for r in rep["Flow:Flow:Meu_Flow"]))

    def test_resume_with_changed_metadata_config_reuses_nothing(self):
        first = self.interrupted()
        cfg = self.root / "config/metadata-types-mvp.json"
        data = json.loads(cfg.read_text())
        data["sensitiveXmlElements"].append("outroCampoSimulado")
        cfg.write_text(json.dumps(data, indent=2))
        code, state = self.run_pipeline("", resume=first.run_id)
        self.assertEqual(state.data["resume"]["reused"], [])
        reasons = state.data["resume"]["reprocessed"][0]["reasons"]
        self.assertTrue(any("configuração de metadata types mudou" in r for r in reasons))

    def test_resume_with_different_api_reuses_nothing(self):
        first = self.interrupted()
        code, state = self.run_pipeline("", resume=first.run_id, api_version="66.0")
        self.assertEqual(state.data["resume"]["reused"], [])
        self.assertTrue(any("API version mudou" in r
                            for r in state.data["resume"]["reprocessed"][0]["reasons"]))

    def test_regenerate_refuses_changed_xml_and_records_differences(self):
        code, first = self.run_pipeline(groups=["Flow"])
        self.assertEqual(code, EXIT_OK)
        xml = self.root / self.primary(first, "Meu_Flow")["xml"]
        xml.write_text(xml.read_text() + "<!-- alterado -->")
        model = self.root / "documentation/models/api-v67/modelo-doc-flow-vapi-67.md"
        model.write_text(model.read_text() + "\n")
        code, regen = self.make().regenerate(first.run_id)
        entry = self.primary(regen, "Meu_Flow")
        self.assertEqual(entry["status"], st.FAILED)
        self.assertEqual(entry["errorClass"], "SOURCE_UNAVAILABLE")
        self.assertIn("XML de origem alterado", entry["error"])
        self.assertEqual(self.primary(regen, "Tela_Cadastro")["status"], st.SUCCESS)
        diffs = regen.data["regenerate"]["differences"]
        self.assertIn("modelo modelo-doc-flow-vapi-67.md mudou", diffs)
        self.assertTrue((self.root / regen.data["summary"]).is_file())

    def test_latest_skips_regenerations_and_discontinued_runs(self):
        code, first = self.run_pipeline(groups=["Flow"])
        code, regen = self.make().regenerate(first.run_id)
        runs = self.root / "runs"
        self.assertEqual(RunState.find(runs, "latest", purpose="regenerate"), first.path)
        self.assertEqual(RunState.find(runs, "latest", purpose="resume"), first.path)
        data = json.loads(first.path.read_text())
        data["discontinued"] = {"at": "x", "reason": "teste"}
        first.path.write_text(json.dumps(data))
        self.assertIsNone(RunState.find(runs, "latest", purpose="regenerate"))
        with self.assertRaises(ConfigError):
            RunState.find(runs, first.run_id)


class PurgeTest(R3Base):
    def old_run(self, days=40, **kwargs):
        code, state = self.run_pipeline(**kwargs)
        data = json.loads(state.path.read_text())
        data["startedAt"] = (now_local() - timedelta(days=days)).isoformat(timespec="seconds")
        state.path.write_text(json.dumps(data))
        return state

    def purge(self, days, **kwargs):
        out = io.StringIO()
        code = purge(DocumentPipeline(self.root).app, days, stream=out, **kwargs)
        return code, out.getvalue()

    def test_listing_changes_nothing(self):
        old = self.old_run(groups=["Flow"])
        before = old.path.read_text()
        code, out = self.purge(30)
        self.assertEqual(code, 0)
        self.assertIn(old.run_id, out)
        self.assertEqual(old.path.read_text(), before)

    def test_apply_marks_discontinued_without_deleting(self):
        old = self.old_run(groups=["Flow"])
        recent = self.run_pipeline(groups=["RemoteSiteSetting"])[1]
        files_before = sorted(str(f) for f in self.root.rglob("*") if f.is_file())
        code, out = self.purge(30, apply=True)
        data = json.loads(old.path.read_text())
        self.assertEqual(data["discontinued"]["reason"], "purge --older-than-days 30")
        self.assertNotIn("discontinued", json.loads(recent.path.read_text()))
        out_dir = self.root / data["output"]["dir"]
        self.assertTrue((out_dir / MARKER).is_file())
        files_after = sorted(str(f) for f in self.root.rglob("*") if f.is_file())
        self.assertEqual(sorted(set(files_before) - set(files_after)), [])
        self.assertTrue((self.root / self.primary(old, "Meu_Flow")["xml"]).is_file())
        with self.assertRaises(ConfigError):
            self.make().regenerate(old.run_id)

    def test_delete_sensitive_requires_apply_and_keeps_active_references(self):
        with self.assertRaises(ConfigError):
            self.purge(30, delete_sensitive=True)
        old = self.old_run(groups=["Flow", "RemoteSiteSetting"])
        recent = self.run_pipeline(groups=["RemoteSiteSetting"])[1]
        flow_xml = self.root / self.primary(old, "Meu_Flow")["xml"]
        shared_xml = self.root / self.primary(recent, self.primary_names(recent)[0])["xml"]
        code, out = self.purge(30, apply=True, delete_sensitive=True)
        self.assertFalse(flow_xml.exists())
        self.assertTrue(shared_xml.exists())  # ainda citado por execução ativa
        data = json.loads(old.path.read_text())
        self.assertIn(self.primary(old, "Meu_Flow")["xml"], data["discontinued"]["deletedSensitive"])

    def primary_names(self, state):
        return [c["component"] for c in state.data["components"] if c.get("role") == "primary"]

    def test_cli_purge(self):
        self.old_run(groups=["Flow"])
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["--project-root", str(self.root), "purge", "--older-than-days", "30"])
        self.assertEqual(code, 0)
        self.assertIn("SOMENTE LISTAR", out.getvalue())


class AtomicWriteTest(unittest.TestCase):
    def test_write_text_leaves_no_partial_file(self):
        import tempfile
        from salesforce_docs.utils import write_text
        d = Path(tempfile.mkdtemp())
        target = d / "doc.md"
        write_text(target, "original")
        with mock.patch("builtins.open", side_effect=OSError("disco cheio")):
            with self.assertRaises(OSError):
                write_text(target, "novo")
        self.assertEqual(target.read_text(), "original")
        self.assertEqual([f.name for f in d.iterdir()], ["doc.md"])


if __name__ == "__main__":
    unittest.main()
