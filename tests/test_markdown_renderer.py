import unittest

from tests.helpers import ROOT
from salesforce_docs import status as st
from salesforce_docs.parsing.xml_parser import parse_xml_file
from salesforce_docs.rendering.context import RenderContext
from salesforce_docs.rendering.markdown_renderer import MarkdownRenderer, validate_document
from salesforce_docs.rendering.template_loader import ContractStore, TemplateLoader
from salesforce_docs.utils import read_json
from tests.helpers import FIXTURES

MODELS = ROOT / "documentation" / "models" / "api-v67"
CONTRACTS = ROOT / "documentation" / "contracts"


def contract(name):
    return read_json(CONTRACTS / name)


class MarkdownRendererTest(unittest.TestCase):
    def setUp(self):
        self.r = MarkdownRenderer()
        self.loader = TemplateLoader(MODELS, "67.0")

    def _flow_ctx(self, schema_fields=None, internal=None, related=None):
        _, data = parse_xml_file(FIXTURES / "source" / "flows" / "Meu_Flow.flow-meta.xml")
        return RenderContext("Flow", "Meu_Flow", data, schema_fields=schema_fields,
                             internal=internal or {}, related=related or [],
                             contracts=ContractStore(CONTRACTS))

    def test_flow_document_with_sources(self):
        tpl = self.loader.load(contract("flow.schema.json")["template"])
        res = self.r.render(tpl, contract("flow.schema.json"), self._flow_ctx())
        self.assertTrue(res.ok, res.errors)
        self.assertIn("| DeveloperName | Meu_Flow | XML |", res.text)
        self.assertIn("| MasterLabel | Meu Flow | XML |", res.text)
        self.assertIn("| Status | Não informado | Objeto interno |", res.text)
        self.assertNotIn("{{", res.text)

    def test_not_informed_when_schema_has_field_but_xml_not(self):
        tpl = self.loader.load(contract("flow.schema.json")["template"])
        ctx = self._flow_ctx(schema_fields=["label", "start", "apiVersion"])
        ctx.data.pop("apiVersion")
        res = self.r.render(tpl, contract("flow.schema.json"), ctx)
        self.assertIn("| ApiVersion | Não informado | XML |", res.text)

    def test_not_applicable_when_schema_lacks_field(self):
        tpl = self.loader.load(contract("flow.schema.json")["template"])
        ctx = self._flow_ctx(schema_fields=["label", "start"])
        ctx.data.pop("apiVersion")
        res = self.r.render(tpl, contract("flow.schema.json"), ctx)
        self.assertIn("| ApiVersion | Não aplicável | XML |", res.text)

    def test_internal_status_formatted(self):
        tpl = self.loader.load(contract("flow.schema.json")["template"])
        internal = {"records": [{"VersionNumber": 3, "Status": "Active"}]}
        res = self.r.render(tpl, contract("flow.schema.json"), self._flow_ctx(internal=internal))
        self.assertIn("| Status | v3: Active | Objeto interno |", res.text)

    def test_missing_template_returns_none(self):
        self.assertIsNone(self.loader.load("modelo-inexistente-vapi-{apiMajor}.md"))
        self.assertIsNone(TemplateLoader(MODELS, "99.0").load(contract("flow.schema.json")["template"]))

    def test_source_mismatch_is_error(self):
        c = contract("flow.schema.json")
        c["properties"][1]["source"] = "Tooling API"
        tpl = self.loader.load(c["template"])
        res = self.r.render(tpl, c, self._flow_ctx())
        self.assertFalse(res.ok)
        self.assertTrue(any("Fonte divergente" in e for e in res.errors))

    def test_placeholder_without_contract_is_error(self):
        c = contract("flow.schema.json")
        c["properties"] = [p for p in c["properties"] if p["placeholder"] != "status"]
        res = self.r.render(self.loader.load(c["template"]), c, self._flow_ctx())
        self.assertFalse(res.ok)
        self.assertTrue(any("'status'" in e for e in res.errors))

    def test_sensitive_values_never_rendered(self):
        _, data = parse_xml_file(FIXTURES / "source" / "connectedApps" / "Meu_App.connectedApp-meta.xml")
        c = contract("connected-app.schema.json")
        ctx = RenderContext("ConnectedApp", "Meu_App", data, sensitive={"consumerSecret"})
        res = self.r.render(self.loader.load(c["template"]), c, ctx)
        self.assertTrue(res.ok, res.errors)
        self.assertNotIn("SEGREDO_SIMULADO", res.text)
        self.assertNotIn("consumerSecret", res.text)
        self.assertIn("| scopes | Api, RefreshToken | XML |", res.text)

    def test_empty_table_uses_allowed_value(self):
        c = contract("custom-object.schema.json")
        ctx = RenderContext("CustomObject", "X__c", {"label": "X"})
        res = self.r.render(self.loader.load(c["template"]), c, ctx)
        self.assertTrue(res.ok, res.errors)
        self.assertIn(f"| {st.NOT_APPLICABLE} | {st.NOT_APPLICABLE} | {st.NOT_APPLICABLE} | XML |", res.text)

    def test_validate_document_rejects_bad_source_and_na(self):
        text = "| Propriedade | Valor | Fonte |\n|---|---|---|\n| A | N/A | Inventado |\n"
        errors = validate_document(text)
        self.assertTrue(any("Fonte não permitida" in e for e in errors))
        self.assertTrue(any("N/A" in e for e in errors))

    def test_pipe_in_value_is_escaped(self):
        c = contract("flow.schema.json")
        ctx = self._flow_ctx()
        ctx.data["label"] = "A | B"
        res = self.r.render(self.loader.load(c["template"]), c, ctx)
        self.assertTrue(res.ok, res.errors)
        self.assertIn("A \\| B", res.text)


if __name__ == "__main__":
    unittest.main()
