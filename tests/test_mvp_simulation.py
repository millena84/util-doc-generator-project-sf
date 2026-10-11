"""Simulação de ponta a ponta de TODAS as documentações do MVP (cenário `mvp_complete`).

Usa a Salesforce CLI SIMULADA com a camada tests/fixtures/mvp-complete, em que todo
metadata type declarado em config/metadata-types-mvp.json tem ao menos um componente.
"""

import re
import unittest

from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st

API = "inventory/org-dev/api-v67"

# Documento -> modelo esperado (os 8 modelos de documentation/models/api-v67).
EXPECTED_DOCS = {
    "doc-meu-flow-flow.md": "modelo-doc-flow-vapi-67.md",
    "doc-tela-cadastro-flow.md": "modelo-doc-flow-vapi-67.md",
    "doc-meu-flow-flow-trigger.md": "modelo-doc-flow-trigger-vapi-67.md",
    "doc-tela-cadastro-dados-cliente-flow-screen.md": "modelo-doc-flow-screen-vapi-67.md",
    "doc-minha-eca-external-client-app.md": "modelo-doc-cea-vapi-67.md",
    "doc-minha-ec-external-credential.md": "modelo-doc-external-credential-vapi-67.md",
    "doc-meu-app-connected-app.md": "modelo-doc-connectedapp-vapi-67.md",
    "doc-pedido-c-custom-object.md": "modelo-doc-custom-object-vapi-67.md",
    "doc-config-mdt-custom-metadata.md": "modelo-doc-custom-metadata-vapi-67.md",
}

# Componentes relacionados que precisam aparecer no documento do principal.
EXPECTED_RELATED = {
    "doc-meu-flow-flow.md": ["| Meu_Flow | FlowDefinition | XML |"],
    "doc-minha-eca-external-client-app.md": [
        "| Minha_ECA_oauth | ExtlClntAppOauthSettings | XML |",
        "| Minha_ECA_plcy | ExtlClntAppConfigurablePolicies | XML |",
        "| Minha_ECA_oauthPlcy | ExtlClntAppOauthConfigurablePolicies | XML |"],
    "doc-pedido-c-custom-object.md": [
        "| Status__c | Status | Picklist | XML |",
        "| Valor__c | Valor | Currency | XML |",
        "| Pedido__c.Padrao | RecordType | XML |",
        "| Pedido__c.Valor_Positivo | ValidationRule | XML |",
        "| Pedido__c.Imprimir_Pedido | WebLink | XML |"],
    "doc-config-mdt-custom-metadata.md": [
        "| Config.Padrao | Config Padrao | XML |",
        "| Config.Secundario | Config Secundario | XML |"],
    "doc-minha-ec-external-credential.md": ["| DeveloperName | Minha_EC | Objeto interno |"],
}

# Tipos listados (passo 6) e respectiva pasta em /inventory.
LISTED_TYPES = {
    "Flow": "flows", "FlowDefinition": "flow-definitions",
    "ExternalClientApplication": "external-client-apps",
    "ExtlClntAppOauthSettings": "extl-clnt-app-oauth-settings",
    "ExtlClntAppConfigurablePolicies": "extl-clnt-app-configurable-policies",
    "ExtlClntAppOauthConfigurablePolicies": "extl-clnt-app-oauth-configurable-policies",
    "ExternalCredential": "external-credentials", "NamedCredential": "named-credentials",
    "ConnectedApp": "connected-apps", "RemoteSiteSetting": "remote-site-settings",
    "CorsWhitelistOrigin": "cors-whitelist-origins", "CspTrustedSite": "csp-trusted-sites",
    "CustomObject": "custom-objects", "CustomMetadata": "custom-metadata",
}
# Tipos que só chegam pelo retrieve do CustomObject (passo 7).
CHILD_TYPES = ["CustomField", "RecordType", "ValidationRule", "WebLink"]


class MvpCompleteSimulationTest(PipelineTestBase):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline("mvp_complete")
        self.assertEqual(self.code, 0, self.log.getvalue())

    def docs(self):
        return {c["document"].rsplit("/", 1)[1]: c for c in self.state.data["components"]
                if c.get("role") == "primary" and c.get("document")}

    def all_documents(self):
        out = {}
        for c in self.state.data["components"]:
            if c.get("role") != "primary":
                continue
            for d in [c] + list(c.get("subDocuments") or []):
                if d.get("document"):
                    out[d["document"].rsplit("/", 1)[1]] = d
        return out

    def test_every_mvp_type_enabled_with_components(self):
        types = {(t["metadataType"], t["stage"]): t for t in self.state.data["metadataTypes"]}
        for t in list(LISTED_TYPES) + CHILD_TYPES:
            self.assertEqual(types[(t, "enabled")]["status"], st.ENABLED, t)
            self.assertEqual(types[(t, "schema")]["status"], st.SUCCESS, t)
        for t, folder in LISTED_TYPES.items():
            self.assertEqual(types[(t, "inventory")]["status"], st.SUCCESS, t)
            self.assertGreater(types[(t, "inventory")]["count"], 0, t)
            for f in ("inventory.raw.json", "inventory.index.json"):
                self.assertTrue((self.root / API / folder / f).is_file(), f"{folder}/{f}")
            self.assertTrue(list((self.root / API / folder / "normalized").glob("*.json")), folder)
            self.assertTrue(list((self.root / API / folder / "retrieve").glob("*.raw.json")), folder)
        excluded = [t for t in self.state.data["metadataTypes"]
                    if t["metadataType"] == "ExtlClntAppGlobalOauthSettings"]
        self.assertEqual(excluded, [])

    def test_all_eight_models_rendered(self):
        docs = self.all_documents()
        self.assertEqual(set(docs), set(EXPECTED_DOCS))
        for name, template in EXPECTED_DOCS.items():
            self.assertEqual(docs[name]["template"], template, name)
            self.assertEqual(docs[name]["status"], st.SUCCESS, name)
        self.assertEqual(self.state.data["status"], st.SUCCESS)

    def test_documents_complete_and_with_source(self):
        for name, doc in self.all_documents().items():
            text = self.read(doc["document"])
            self.assertNotIn("{{", text, name)
            self.assertNotIn("SEGREDO_SIMULADO", text, name)
            for line in text.splitlines():
                if line.startswith("| ") and not set(line) <= set("|- "):
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    self.assertTrue(cells[-1], f"{name}: linha sem fonte: {line}")

    def test_related_components_in_parent_document(self):
        docs = self.all_documents()
        for name, rows in EXPECTED_RELATED.items():
            text = self.read(docs[name]["document"])
            for row in rows:
                self.assertIn(row, text, name)

    def test_reference_scan_candidates_retrieved_but_not_linked(self):
        """Sem citação exata no XML da ECA, REFERENCE_SCAN não relaciona (nada é suposto)."""
        text = self.read(self.all_documents()["doc-minha-eca-external-client-app.md"]["document"])
        for name in ("Minha_NC", "Parceiro_API", "Parceiro_CDN", "Parceiro_Portal"):
            self.assertNotIn(name, text)
            self.assertTrue(re.search(rf"--metadata \w+:{name} ", self.calls_file.read_text()), name)

    def test_regenerate_is_identical_and_offline(self):
        before = {d: self.read(c["document"]) for d, c in self.all_documents().items()}
        self.calls_file.write_text("")
        from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
        code, _ = DocumentPipeline(self.root, stream=self.log).regenerate("latest")
        self.assertEqual(code, 0, self.log.getvalue())
        self.assertEqual(self.calls_file.read_text(), "")
        after = {d: self.read(c["document"]) for d, c in self.all_documents().items()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
