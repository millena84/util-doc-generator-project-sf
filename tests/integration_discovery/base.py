"""Base dos testes da Fase 2: projeto temporário com config e o inventário SIMULADO de fixtures."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests" / "fixtures" / "integration_discovery"
CSV = FIX / "componentes-squad.csv"
INV = "inventory/org-dev/api-v67"


class DiscoveryBase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="discovery-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "config").mkdir()
        for f in ("config.json", "integration-discovery-rules.json"):
            shutil.copy(REPO / "config" / f, self.root / "config" / f)
        shutil.copytree(FIX / "inventory", self.root / "inventory")

    def settings(self):
        from integration_discovery.settings import DiscoverySettings
        return DiscoverySettings(self.root)

    def write_csv(self, text, name="in.csv"):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return p

    def out(self, *parts):
        """Saídas da descoberta da org de teste (`discovery/org-dev/api-v67/...`)."""
        return self.root.joinpath("discovery", "org-dev", "api-v67", *parts)

    def sig(self, cluster_id):
        """Os 6 primeiros caracteres da assinatura do cluster, como mostrados no relatório."""
        return self.read_json("clusters", f"{cluster_id}.json")["signature"][:6]

    def put_normalized(self, rel, metadata_type, full_name, data, role="primary"):
        """Grava um JSON normalizado no formato do Utilitário 1 dentro do inventário do teste."""
        p = self.root / INV / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"metadataType": metadata_type, "fullName": full_name, "role": role,
                                 "source": {"xml": f"{INV}/{rel}.xml", "xmlSha256": "0" * 64},
                                 "schema": {"available": True, "fieldNames": []},
                                 "fields": {"present": [], "absent": [], "redacted": []}, "data": data},
                                ensure_ascii=False), encoding="utf-8")
        return p

    def read_json(self, *parts):
        return json.loads(self.out(*parts).read_text(encoding="utf-8"))
