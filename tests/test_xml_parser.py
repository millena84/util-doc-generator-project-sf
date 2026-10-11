import shutil
import tempfile
import unittest
from pathlib import Path

from tests.helpers import FIXTURES
from salesforce_docs.parsing.xml_parser import is_regenerable, normalize_component, parse_xml_file
from salesforce_docs.utils import sha256_file

SRC = FIXTURES / "source"


class XmlParserTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_repeated_tags_become_lists(self):
        root, data = parse_xml_file(SRC / "connectedApps" / "Meu_App.connectedApp-meta.xml")
        self.assertEqual(root, "ConnectedApp")
        self.assertEqual(data["oauthConfig"]["scopes"], ["Api", "RefreshToken"])
        self.assertEqual(data["label"], "Meu App")

    def test_values_are_strings_not_converted(self):
        _, data = parse_xml_file(SRC / "flowDefinitions" / "Meu_Flow.flowDefinition-meta.xml")
        self.assertEqual(data["activeVersionNumber"], "2")

    def test_absent_schema_fields_are_null_and_registered(self):
        xml = SRC / "flows" / "Meu_Flow.flow-meta.xml"
        schema = {"valueTypeFields": [{"name": n} for n in ("apiVersion", "label", "description", "start")]}
        norm = normalize_component("Flow", "Meu_Flow", xml, SRC, schema)
        self.assertIsNone(norm["data"]["description"])
        self.assertIn("description", norm["fields"]["absent"])
        self.assertIn("label", norm["fields"]["present"])
        self.assertNotIn("description", norm["fields"]["present"])

    def test_without_schema_no_invented_fields(self):
        xml = SRC / "flows" / "Meu_Flow.flow-meta.xml"
        norm = normalize_component("Flow", "Meu_Flow", xml, SRC, None)
        self.assertFalse(norm["schema"]["available"])
        self.assertEqual(norm["fields"]["absent"], [])
        self.assertNotIn("description", norm["data"])

    def test_original_xml_untouched_and_regenerable(self):
        xml = self.tmp / "Meu_Flow.flow-meta.xml"
        shutil.copyfile(SRC / "flows" / "Meu_Flow.flow-meta.xml", xml)
        before = sha256_file(xml)
        n1 = normalize_component("Flow", "Meu_Flow", xml, self.tmp, None)
        n2 = normalize_component("Flow", "Meu_Flow", xml, self.tmp, None)
        self.assertEqual(sha256_file(xml), before)
        self.assertEqual(n1, n2)
        self.assertTrue(is_regenerable(n1, self.tmp))
        xml.write_text(xml.read_text().replace("Meu Flow", "Outro"))
        self.assertFalse(is_regenerable(n1, self.tmp))

    def test_xsi_nil_and_namespaced_values(self):
        _, data = parse_xml_file(SRC / "customMetadata" / "Config.Padrao.md-meta.xml")
        self.assertEqual(data["values"]["field"], "Ativo__c")
        self.assertEqual(data["values"]["value"], "true")


if __name__ == "__main__":
    unittest.main()
