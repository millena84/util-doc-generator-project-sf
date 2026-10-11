import json
import unittest

from tests.helpers import FIXTURES
from salesforce_docs import status as st
from salesforce_docs.validation.metadata_type_validator import build_index, check_enabled


class MetadataTypeValidatorTest(unittest.TestCase):
    def setUp(self):
        raw = json.loads((FIXTURES / "org" / "metadata-types.json").read_text())
        self.index = build_index(raw["result"])

    def test_enabled_top_level(self):
        self.assertEqual(check_enabled(self.index, "Flow")["status"], st.ENABLED)

    def test_enabled_child(self):
        info = check_enabled(self.index, "CustomField")
        self.assertEqual(info["status"], st.ENABLED)
        self.assertEqual(info["kind"], "CHILD")
        self.assertEqual(info["parents"], ["CustomObject"])

    def test_not_enabled(self):
        self.assertEqual(check_enabled(self.index, "CorsWhitelistOrigin")["status"], st.NOT_ENABLED)
        self.assertEqual(check_enabled(self.index, "ExternalClientApp")["status"], st.NOT_ENABLED)

    def test_index_is_deterministic(self):
        raw = json.loads((FIXTURES / "org" / "metadata-types.json").read_text())
        self.assertEqual(build_index(raw["result"]), self.index)


if __name__ == "__main__":
    unittest.main()
