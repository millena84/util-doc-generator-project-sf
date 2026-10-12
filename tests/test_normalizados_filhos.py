"""DA-03: filhos de tipos diferentes com o mesmo fullName não sobrescrevem o normalizado."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT  # noqa: F401  (ajusta sys.path)
from salesforce_docs.pipeline.component_pipeline import normalize_record
from salesforce_docs.utils import Masker

MD = "http://soap.sforce.com/2006/04/metadata"


class _Mvp:
    sensitive_elements = {"consumerSecret"}

    def folder(self, _metadata_type):
        return "custom-objects"


class _Ctx:
    def __init__(self, root):
        self.root = root
        self.inventory_dir = root / "inventory"
        self.schemas_dir = root / "schemas"
        self.mvp = _Mvp()
        self.masker = Masker()


class ChildNormalizedNamesTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def xml(self, rel_path, root_tag, body):
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'<?xml version="1.0"?><{root_tag} xmlns="{MD}">{body}</{root_tag}>')
        return rel_path

    def test_children_with_same_full_name_keep_separate_files(self):
        base = "inventory/custom-objects/components/objects/Pedido__c"
        obj = self.xml(f"{base}/Pedido__c.object-meta.xml", "CustomObject", "<label>Pedido</label>")
        rt = self.xml(f"{base}/recordTypes/Padrao.recordType-meta.xml", "RecordType", "<label>RT Padrão</label>")
        vr = self.xml(f"{base}/validationRules/Padrao.validationRule-meta.xml", "ValidationRule",
                      "<errorMessage>Regra padrão</errorMessage>")
        record = {"metadataType": "CustomObject", "fullName": "Pedido__c", "xml": obj, "role": "primary",
                  "files": [{"type": "CustomObject", "fullName": "Pedido__c", "path": obj},
                            {"type": "RecordType", "fullName": "Pedido__c.Padrao", "path": rt},
                            {"type": "ValidationRule", "fullName": "Pedido__c.Padrao", "path": vr}]}
        normalize_record(_Ctx(self.root), record)
        children = {c["metadataType"]: c for c in record["children"]}
        paths = {c["normalized"] for c in record["children"]}
        self.assertEqual(len(paths), 2)
        self.assertTrue(children["RecordType"]["normalized"].endswith("record-type--pedido-c-padrao.json"))
        self.assertTrue(children["ValidationRule"]["normalized"].endswith(
            "validation-rule--pedido-c-padrao.json"))
        rt_data = json.loads((self.root / children["RecordType"]["normalized"]).read_text())
        vr_data = json.loads((self.root / children["ValidationRule"]["normalized"]).read_text())
        self.assertEqual(rt_data["data"]["label"], "RT Padrão")
        self.assertEqual(vr_data["data"]["errorMessage"], "Regra padrão")
        self.assertTrue(record["normalized"].endswith("normalized/pedido-c.json"))  # principal inalterado


if __name__ == "__main__":
    unittest.main()
