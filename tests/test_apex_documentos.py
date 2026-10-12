"""Documentos de classes Apex (entrega 1): classe + subdocumentos por papel assíncrono.

Usa a CLI simulada e as classes SIMULADAS de tests/fixtures/source/classes.
"""

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.helpers import FIXTURES, fake_sf_env
from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.pipeline.component_pipeline import attach_source
from salesforce_docs.pipeline.document_pipeline import EXIT_OK, DocumentPipeline
from salesforce_docs.salesforce.cli_runner import CliRunner

EXPECTED_SUBDOCS = {
    "OrderCleanupBatch": ["apex-batch"],
    "AccountSyncQueueable": ["apex-queueable"],
    "DailyOrderCleanupScheduler": ["apex-scheduler"],
    "MultiRoleJob": ["apex-batch", "apex-scheduler"],
    "IntegrationAsyncHelper": ["apex-future", "apex-future"],
    "PedidoService": [],
}


class ApexDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=["ApexClass"])

    def entry(self, name):
        return self.primary(self.state, name)

    def doc(self, name):
        return self.read(self.entry(name)["document"])

    def subdoc(self, name, suffix, index=0):
        docs = [s for s in self.entry(name)["subDocuments"] if s["document"].endswith(f"-{suffix}.md")]
        return self.read(docs[index]["document"])

    def test_one_document_per_class_and_subdocument_per_role(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        for name, suffixes in EXPECTED_SUBDOCS.items():
            e = self.entry(name)
            self.assertEqual(e["status"], st.SUCCESS, name)
            self.assertTrue(e["document"].endswith(f"doc-{name.lower()}-apex-class.md"))
            got = sorted(s["document"].rsplit("-apex-", 1)[1].replace(".md", "") for s in e["subDocuments"])
            self.assertEqual(got, sorted(s.replace("apex-", "") for s in suffixes), name)

    def test_managed_package_class_is_not_retrieved(self):
        self.assertIn("pkg__ClasseGerenciada", json.dumps(self.state.data.get("ignoredByFilter")))
        self.assertNotIn("ApexClass:pkg__ClasseGerenciada", self.calls())

    def test_class_document(self):
        doc = self.doc("OrderCleanupBatch")
        self.assertIn("| Sharing | with sharing | Código Apex |", doc)
        self.assertIn("| Database.Batchable<sObject> | Código Apex |", doc)
        self.assertIn("| start(Database.BatchableContext bc) | Database.QueryLocator | public |", doc)
        self.assertIn("| finish | executeBatch | InvoiceSyncBatch | 50 |", doc)
        self.assertIn("| LengthWithoutComments | 404 | Objeto interno |", doc)

    def test_batch_document(self):
        doc = self.subdoc("OrderCleanupBatch", "apex-batch")
        self.assertIn("| Tipo de escopo | QueryLocator | Código Apex |", doc)
        self.assertIn("| Database.Stateful | True | Código Apex |", doc)
        self.assertIn("| Objeto da consulta | Order__c | Código Apex |", doc)
        self.assertIn("- Segue a convenção: Sim", doc)
        multi = self.subdoc("MultiRoleJob", "apex-batch")
        self.assertIn("| Consulta dinâmica | True | Código Apex |", multi)
        self.assertIn("| Consulta do start() | Não informado | Código Apex |", multi)
        self.assertIn("- Segue a convenção: Não", multi)

    def test_queueable_document(self):
        doc = self.subdoc("AccountSyncQueueable", "apex-queueable")
        self.assertIn("| Classe do Finalizer | IntegrationFinalizerHandler | Código Apex |", doc)
        self.assertIn("| accounts | List<Account> | Código Apex |", doc)
        self.assertIn("| AccountSyncQueueable | 5 | Código Apex |", doc)

    def test_future_documents_one_per_method(self):
        docs = {s["component"]: self.read(s["document"]) for s in self.entry("IntegrationAsyncHelper")["subDocuments"]}
        self.assertEqual(set(docs), {"IntegrationAsyncHelper.processOrdersAsync", "IntegrationAsyncHelper.recalc"})
        self.assertIn("| callout=true | True | Código Apex |", docs["IntegrationAsyncHelper.processOrdersAsync"])
        self.assertIn("| callout=true | False | Código Apex |", docs["IntegrationAsyncHelper.recalc"])
        self.assertIn("| Classe | IntegrationAsyncHelper | XML |", docs["IntegrationAsyncHelper.recalc"])

    def test_scheduler_document(self):
        doc = self.subdoc("DailyOrderCleanupScheduler", "apex-scheduler")
        self.assertIn("| Classes delegadas | OrderCleanupBatch | Código Apex |", doc)
        self.assertIn("| Limpeza Diaria de Pedidos | 0 0 1 * * ? | DailyOrderCleanupScheduler | Código Apex |", doc)

    def test_code_is_raw_and_never_rendered(self):
        src = (FIXTURES / "source" / "classes" / "OrderCleanupBatch.cls").read_bytes()
        copied = [f for f in self.entry("OrderCleanupBatch")["files"] if f["path"].endswith(".cls")][0]
        self.assertEqual((self.root / copied["path"]).read_bytes(), src)  # raw intacto
        norm = json.loads(self.read(self.entry("OrderCleanupBatch")["normalized"]))
        self.assertEqual(norm["source"]["code"], copied["path"])
        self.assertEqual(norm["source"]["codeParser"], "apex-lexical/v1")
        leaks = [str(p.relative_to(self.root)) for p in self.root.rglob("*")
                 if p.is_file() and p.suffix != ".cls" and "SENTINELA_APEX_SEGREDO" in p.read_text(errors="ignore")]
        self.assertEqual(leaks, [])
        for e in self.state.data["components"]:
            for d in [e.get("document")] + [s.get("document") for s in e.get("subDocuments") or []]:
                if d:
                    self.assertNotIn("processados +=", self.read(d))

    def test_regenerate_offline_reproduces_documents(self):
        docs = {e["component"]: self.read(e["document"]) for e in self.state.data["components"]
                if e.get("role") == "primary" and e.get("document")}
        fake_sf_env("old_cli")
        pipeline = DocumentPipeline(self.root, runner=CliRunner(executable="/nao/existe/sf"), stream=io.StringIO())
        code, state2 = pipeline.regenerate(self.state.run_id)
        self.assertEqual(code, EXIT_OK)
        for e in state2.data["components"]:
            if e.get("role") == "primary" and e.get("document"):
                self.assertEqual(self.read(e["document"]), docs[e["component"]], e["component"])


class MissingSourceFileTest(unittest.TestCase):
    def test_missing_cls_is_warning_not_failure(self):
        class Mvp:
            def source_parser(self, _t):
                return {"name": "apex", "suffix": ".cls", "key": "apex"}

        class Ctx:
            mvp = Mvp()
            root = Path(tempfile.mkdtemp())

        self.addCleanup(shutil.rmtree, Ctx.root, ignore_errors=True)
        record = {"fullName": "X", "files": [{"type": "ApexClass", "fullName": "X", "path": "x/X.cls-meta.xml"}],
                  "warnings": []}
        normalized = {"data": {}, "source": {}}
        attach_source(Ctx, record, "ApexClass", normalized)
        self.assertFalse(normalized["data"]["apex"]["parsed"])
        self.assertTrue(any(".cls não recuperado" in w for w in record["warnings"]))


if __name__ == "__main__":
    unittest.main()
