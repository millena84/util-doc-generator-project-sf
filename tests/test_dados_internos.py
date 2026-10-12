"""Dados internos em todos os documentos principais e envelope sanitizado do org display."""

import json
import unittest

from tests.helpers import FAKE_TOKEN
from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st
from salesforce_docs.extraction.internal_data_extractor import extract_internal_data
from salesforce_docs.salesforce.cli_runner import CliResult
from salesforce_docs.validation.internal_object_validator import validate_internal_data_config

ALL_GROUPS = ["Flow", "ExternalClientApp", "ExternalCredential", "ConnectedApp", "CustomObject",
              "CustomMetadata", "NamedCredential", "RemoteSiteSetting", "Certificate"]


class InternalDataInDocumentsTest(PipelineTestBase):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=ALL_GROUPS)

    def doc(self, component):
        return self.read(self.primary(self.state, component)["document"])

    def test_every_primary_document_has_internal_data_section(self):
        docs = [c for c in self.state.data["components"]
                if c.get("role") == "primary" and c.get("document")]
        self.assertTrue(docs)
        for c in docs:
            self.assertIn("## Dados internos", self.read(c["document"]), c["component"])
            for sub in c.get("subDocuments") or []:
                if sub.get("document"):
                    self.assertIn("## Dados internos", self.read(sub["document"]), sub["component"])

    def test_values_from_internal_objects(self):
        self.assertIn("| KeyPrefix | a01 | Tooling API |", self.doc("Pedido__c"))
        self.assertIn("| QualifiedApiName | Config__mdt | Tooling API |", self.doc("Config__mdt"))
        app = self.doc("Meu_App")
        self.assertIn("| OptionsAllowAdminApprovedUsersOnly | True | Objeto interno |", app)
        self.assertNotIn("Outro_App", app)
        self.assertIn("| KeySize | 2048 | Tooling API |", self.doc("Meu_Certificado"))
        self.assertIn("| DeveloperName | Minha_NC | Objeto interno |", self.doc("Minha_NC"))
        flow = self.primary(self.state, "Meu_Flow")
        self.assertIn("| 2 | Active | 301000000000002AAA | Tooling API |", self.read(flow["document"]))

    def test_blocked_field_returned_by_query_is_not_rendered(self):
        # O fixture devolve Endpoint (omitFromDocumentation) mesmo sem ser pedido.
        doc = self.doc("Minha_NC")
        self.assertNotIn("sentinela-endpoint-interno", doc)
        self.assertNotIn("| Endpoint |", doc)

    def test_not_applicable_without_confirmed_internal_object(self):
        for comp in ("Minha_ECA", "Meu_Site"):
            self.assertIn("| Não aplicável | Não aplicável | Objeto interno |", self.doc(comp), comp)

    def test_internal_data_unavailable_is_not_informed(self):
        self.assertIn("| Não informado | Não informado | Objeto interno |", self.doc("NC_Legada"))


class _Tooling:
    def __init__(self, records):
        self.records = records

    def query(self, soql, raw_path=None, error_raw_path=None, use_tooling_api=True):
        return CliResult(["sf"], 0, json.dumps({"status": 0, "result": {"records": self.records}}), "", 0)


CFG = {"enabled": True, "source": "Objeto interno", "object": "X",
       "query": "SELECT Id FROM X WHERE Name = '{developerName}'", "expectSingleRecord": True}


class InternalDataUnitTest(unittest.TestCase):
    def test_single_record(self):
        self.assertEqual(extract_internal_data(_Tooling([{"Id": "1"}]), CFG, "A", None, None)["status"],
                         st.SUCCESS)

    def test_ambiguous_records_are_discarded(self):
        res = extract_internal_data(_Tooling([{"Id": "1"}, {"Id": "2"}]), CFG, "A", None, None)
        self.assertEqual(res["status"], st.INTERNAL_DATA_UNAVAILABLE)
        self.assertIsNone(res["records"])
        self.assertIn("ambíguo", res["error"])

    def test_query_selecting_blocked_field_is_invalid(self):
        bad = dict(CFG, query="SELECT Id, ConsumerSecret, Endpoint FROM X")
        errors = validate_internal_data_config("x.schema.json", bad, {"consumerSecret", "endpoint"})
        self.assertEqual(len(errors), 1)
        self.assertIn("['consumersecret', 'endpoint']", errors[0])
        self.assertEqual(validate_internal_data_config("x.schema.json", CFG, {"endpoint"}), [])


class OrgDisplayTokenTest(PipelineTestBase):
    def test_token_never_written_to_any_file(self):
        code, state = self.run_pipeline(groups=["Flow"])
        leaks = [str(p.relative_to(self.root)) for p in self.root.rglob("*")
                 if p.is_file() and FAKE_TOKEN in p.read_text(errors="ignore")]
        self.assertEqual(leaks, [])


if __name__ == "__main__":
    unittest.main()
