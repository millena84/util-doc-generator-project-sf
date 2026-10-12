"""Onda 1 — cobertura explícita por metadata type e resultado final que nunca
representa cobertura completa quando falta modelo. CLI SIMULADA; nenhuma org real."""

import json
import unittest

from tests.helpers import FIXTURES
from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.pipeline.document_pipeline import EXIT_GAPS, EXIT_OK, DocumentPipeline


class TypeCoverageTest(P3Base):
    def test_full_run_type_coverage(self):
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        types = state.data["coverage"]["types"]
        org = json.loads((FIXTURES / "org/metadata-types.json").read_text())["result"]["metadataObjects"]
        discovered = {o["xmlName"] for o in org} | {c for o in org for c in o.get("childXmlNames") or []}
        self.assertEqual(types["discovered"], {"count": len(discovered), "available": True})
        self.assertIn("CspTrustedSite", types["discoveredNotConfigured"])
        self.assertIn("ListView", types["discoveredNotConfigured"])
        self.assertNotIn("Flow", types["discoveredNotConfigured"])
        self.assertEqual(types["excluded"]["byConfig"], ["ExtlClntAppGlobalOauthSettings"])
        for t in ("Flow", "FlowDefinition", "CustomObject", "CustomField", "CustomMetadata",
                  "NamedCredential", "ExternalCredential", "Certificate"):
            self.assertIn(t, types["processed"])
        self.assertIn("Flow", types["documented"])
        self.assertIn("FlowDefinition", types["documentedAsRelated"])
        self.assertIn("CustomField", types["documentedAsRelated"])
        self.assertEqual(types["withoutModel"], [])
        self.assertIn("Tipos: configurados", self.log.getvalue())

    def test_warnings_only_is_success_with_warning_coverage(self):
        code, state = self.run_pipeline(groups=["ExternalCredential"])
        self.assertEqual(state.data["status"], st.SUCCESS)
        cov = state.data["coverage"]
        self.assertEqual(cov["status"], "COMPLETE_WITH_WARNINGS")
        self.assertEqual((cov["blockingGapCount"], cov["warningCount"]), (0, 1))

    def test_out_of_scope_and_not_enabled_are_listed(self):
        cfg = self.root / "config/metadata-types-mvp.json"
        data = json.loads(cfg.read_text())
        for g in data["metadataTypeGroups"]:
            if g["group"] == "Certificate":
                g["primaryMetadataType"] = "PublicKeyCertificate"
        cfg.write_text(json.dumps(data))
        code, state = self.run_pipeline(groups=["Certificate", "RemoteSiteSetting"])
        excl = state.data["coverage"]["types"]["excluded"]
        self.assertEqual(excl["notEnabledInOrg"], ["PublicKeyCertificate"])
        self.assertIn("Flow", excl["outOfScope"])
        self.assertNotIn("RemoteSiteSetting", excl["outOfScope"])

    def test_failure_before_listing_has_no_discovery(self):
        self.config(approvedOrgs=[])
        code, state = self.run_pipeline()
        types = state.data["coverage"]["types"]
        self.assertEqual(types["discovered"], {"count": None, "available": False})
        self.assertIsNone(types["discoveredNotConfigured"])
        self.assertEqual(types["processed"], [])


class MissingModelTest(P3Base):
    MODEL = "documentation/models/api-v67/modelo-doc-remote-site-setting-vapi-67.md"

    def test_missing_model_continues_but_never_complete(self):
        (self.root / self.MODEL).unlink()
        code, state = self.run_pipeline(groups=["RemoteSiteSetting", "Certificate"])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(self.primary(state, "Meu_Site")["status"], st.NO_TEMPLATE)
        self.assertEqual(self.primary(state, "Meu_Certificado")["status"], st.SUCCESS)  # continuidade
        self.assertTrue((self.root / self.primary(state, "Meu_Site")["normalized"]).is_file())
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        cov = state.data["coverage"]
        self.assertEqual(cov["status"], "INCOMPLETE")
        self.assertEqual(cov["gaps"]["noTemplate"], ["RemoteSiteSetting:Meu_Site"])
        self.assertIn("RemoteSiteSetting", cov["types"]["withoutModel"])
        self.assertIn("RemoteSiteSetting", cov["types"]["processed"])
        self.assertNotIn("RemoteSiteSetting", cov["types"]["documented"])
        self.assertIn("WARN  Cobertura: INCOMPLETE", self.log.getvalue())

    def test_missing_contract_is_also_a_gap(self):
        (self.root / "documentation/contracts/remote-site-setting.schema.json").unlink()
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        self.assertTrue(any("estático" in t for t in state.data["coverage"]["types"]["withoutModel"]))

    def test_missing_subdocument_model_is_a_gap(self):
        (self.root / "documentation/models/api-v67/modelo-doc-flow-trigger-vapi-67.md").unlink()
        code, state = self.run_pipeline(groups=["Flow"])
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        self.assertIn("Flow (subdocumento)", state.data["coverage"]["types"]["withoutModel"])

    def test_strict_coverage_exit_code(self):
        (self.root / self.MODEL).unlink()
        self.config(execution={"strictCoverage": True})
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_GAPS)
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)

    def test_regenerate_with_missing_model_is_not_success(self):
        code, first = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(first.data["status"], st.SUCCESS)
        (self.root / self.MODEL).unlink()
        code, state = DocumentPipeline(self.root, stream=self.log).regenerate(first.run_id)
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)


if __name__ == "__main__":
    unittest.main()
