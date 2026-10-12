"""DA-05: aviso quando componente de pacote tem dados internos sem filtro de namespace."""

import json
import os
import shutil
import tempfile
from unittest import mock

from tests.helpers import FIXTURES, fake_sf_env
from tests.test_prioridade3 import P3Base
from salesforce_docs.pipeline.document_pipeline import namespace_warning, with_internal_note


class NamespaceWarningUnitTest(P3Base):
    def test_warning_only_for_namespaced_component_without_filter(self):
        cfg = {"query": "SELECT Id FROM Flow WHERE Definition.DeveloperName = '{developerName}'"}
        self.assertIsNone(namespace_warning(cfg, None, [{"Id": "1"}]))
        self.assertIsNone(namespace_warning(cfg, "ns", []))  # sem registros: nada a misturar
        filtered = {"query": cfg["query"] + " AND Definition.NamespacePrefix = '{namespacePrefix}'"}
        self.assertIsNone(namespace_warning(filtered, "ns", [{"Id": "1"}]))
        self.assertIn("namespace 'ns'", namespace_warning(cfg, "ns", [{"Id": "1"}]))
        by_full_name = {"query": "SELECT QualifiedApiName FROM EntityDefinition "
                                 "WHERE QualifiedApiName = '{fullName}'"}
        self.assertIsNone(namespace_warning(by_full_name, "ns", [{"Id": "1"}]))

    def test_note_goes_right_after_internal_data_table(self):
        text = "# X\n\n## Dados internos\n\n| a | Fonte |\n|---|---|\n| 1 | XML |\n\n## Depois\n"
        out = with_internal_note(text, "AVISO")
        self.assertLess(out.index("> **Atenção:** AVISO"), out.index("## Depois"))
        self.assertGreater(out.index("> **Atenção:** AVISO"), out.index("| 1 | XML |"))
        self.assertEqual(with_internal_note(text, None), text)


class NamespacedFlowTest(P3Base):
    def setUp(self):
        super().setUp()
        self.fixtures = tempfile.mkdtemp(prefix="sfdocs-fixtures-")
        self.addCleanup(shutil.rmtree, self.fixtures, ignore_errors=True)
        shutil.copytree(FIXTURES, self.fixtures, dirs_exist_ok=True)
        inv = os.path.join(self.fixtures, "inventory", "Flow.json")
        items = json.load(open(inv))
        for item in items:
            if item["fullName"] == "Meu_Flow":
                item["namespacePrefix"] = "ns"
        json.dump(items, open(inv, "w"))

    def run_ns(self, **kwargs):
        def env(scenario=""):
            fake_sf_env(scenario)
            os.environ["FAKE_SF_FIXTURES"] = self.fixtures
        with mock.patch("tests.test_document_pipeline.fake_sf_env", env):
            return self.run_pipeline(**kwargs)

    def test_document_and_state_warn_about_namespace(self):
        code, state = self.run_ns(groups=["Flow"])
        flow = self.primary(state, "Meu_Flow")
        doc = self.read(flow["document"])
        self.assertIn("> **Atenção:** Componente do namespace 'ns'", doc)
        self.assertTrue(any("namespace 'ns'" in w for w in flow["warnings"]))
        self.assertIn("namespace 'ns'", self.log.getvalue())
        sub = flow["subDocuments"][0]
        self.assertIn("namespace 'ns'", self.read(sub["document"]))
        other = self.read(self.primary(state, "Tela_Cadastro")["document"])
        self.assertNotIn("Atenção:** Componente do namespace", other)
