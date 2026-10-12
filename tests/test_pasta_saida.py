"""Pasta de saída: uma pasta por org e por dia; retomada na pasta da coleta original."""

import io
import json
from datetime import timedelta

from tests.helpers import SIMULATED_ORG_ID
from tests.test_prioridade3 import P3Base
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
from salesforce_docs.pipeline.output_writer import ORG_MARKER
from salesforce_docs.runs.retention import MARKER, purge
from salesforce_docs.utils import now_local

OTHER_ORG = "00D000000000001AAA"
TODAY = now_local().strftime("%m%d%y")


class OrgFoldersTest(P3Base):
    def approve_other_org(self, alias):
        cfg = json.loads((self.root / "config" / "config.json").read_text())
        self.config(approvedOrgs=cfg["approvedOrgs"] + [{"orgId": OTHER_ORG, "alias": alias}])

    def folder(self, state):
        return state.data["output"]["baseDir"]

    def test_default_is_one_folder_per_org_and_day(self):
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(state.data["output"]["layout"], "BY_DATE")
        self.assertEqual(self.folder(state), f"saida/docs/doc-dev-{TODAY}")
        marker = json.loads((self.root / self.folder(state) / ORG_MARKER).read_text())
        self.assertEqual(marker, {"orgId": SIMULATED_ORG_ID, "alias": "dev"})

    def test_two_orgs_same_day_never_share_folder(self):
        code, s1 = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.approve_other_org("prod")
        code, s2 = self.run_pipeline(f"extra_alias=prod,org_id={OTHER_ORG}", groups=["RemoteSiteSetting"],
                                     org_alias="prod")
        self.assertEqual(self.folder(s2), f"saida/docs/doc-prod-{TODAY}")
        self.assertNotEqual(self.folder(s1), self.folder(s2))
        self.assertIn(f"doc-prod-{TODAY}/", self.primary(s2, "Meu_Site")["document"])

    def test_same_alias_pointing_to_other_org_gets_own_folder(self):
        code, s1 = self.run_pipeline(groups=["RemoteSiteSetting"])
        first_doc = self.root / self.primary(s1, "Meu_Site")["document"]
        before = first_doc.read_text()
        self.approve_other_org("dev")
        code, s2 = self.run_pipeline(f"org_id={OTHER_ORG}", groups=["RemoteSiteSetting"])
        self.assertEqual(self.folder(s2), f"saida/docs/doc-dev-{OTHER_ORG}-{TODAY}")
        self.assertEqual(s2.data["output"]["orgFolderConflict"]["owner"], SIMULATED_ORG_ID)
        self.assertEqual(first_doc.read_text(), before)  # pasta da primeira org intacta
        self.assertIn("pertence à org", self.log.getvalue())
        summary = (self.root / s2.data["summary"]).read_text()
        self.assertIn("orgs diferentes nunca compartilham pasta", summary)


class ResumeFolderTest(P3Base):
    def interrupted(self):
        code, state = self.run_pipeline("expire_on_retrieve=Pedido__c")
        self.calls_file.write_text("")
        return state

    def age_run(self, state, days):
        """Simula que a execução interrompida foi feita `days` dias atrás (pasta e datas)."""
        old_day = (now_local() - timedelta(days=days))
        old_folder = f"doc-dev-{old_day.strftime('%m%d%y')}"
        docs = self.root / "saida" / "docs"
        (docs / f"doc-dev-{TODAY}").rename(docs / old_folder)
        text = state.path.read_text().replace(f"doc-dev-{TODAY}", old_folder)
        data = json.loads(text)
        data["startedAt"] = old_day.isoformat(timespec="seconds")
        for c in data["components"]:
            if c.get("processedOn"):
                c["processedOn"] = old_day.date().isoformat()
        state.path.write_text(json.dumps(data))
        return f"saida/docs/{old_folder}", old_day.date().isoformat()

    def documents(self, state):
        return [c["document"] for c in state.data["components"]
                if c.get("role") == "primary" and c.get("document")]

    def test_same_day_resume_keeps_everything_in_one_folder(self):
        first = self.interrupted()
        code, state = self.run_pipeline("", resume=first.run_id)
        folders = {d.rsplit("/", 1)[0] for d in self.documents(state)}
        self.assertEqual(folders, {f"saida/docs/doc-dev-{TODAY}"})
        self.assertNotIn("resumeAgeWarning", state.data["output"])

    def test_resume_other_day_writes_to_original_folder_with_guidance(self):
        first = self.interrupted()
        folder, old_date = self.age_run(first, 3)
        code, state = self.run_pipeline("", resume=first.run_id)
        docs = self.documents(state)
        self.assertTrue(docs)
        self.assertTrue(all(d.startswith(folder + "/") for d in docs), docs)
        self.assertFalse((self.root / "saida" / "docs" / f"doc-dev-{TODAY}").exists())
        out = state.data["output"]
        self.assertIn("pasta da execução de origem", out["resumeNote"])
        self.assertIn("3 dia(s)", out["resumeAgeWarning"])
        days = {c.get("processedOn") for c in state.data["components"] if c.get("role") == "primary"}
        self.assertEqual(days, {old_date, now_local().date().isoformat()})
        summary = (self.root / state.data["summary"]).read_text()
        self.assertIn("Componentes por dia de processamento", summary)
        self.assertIn("execução completa nova", summary)

    def test_resume_output_today(self):
        first = self.interrupted()
        folder, _ = self.age_run(first, 3)
        self.config(execution={"resumeOutput": "TODAY"})
        code, state = self.run_pipeline("", resume=first.run_id)
        new_docs = [c["document"] for c in state.data["components"]
                    if c.get("role") == "primary" and c.get("document") and not c.get("carriedFrom")]
        self.assertTrue(new_docs)
        self.assertTrue(all(d.startswith(f"saida/docs/doc-dev-{TODAY}/") for d in new_docs), new_docs)
        self.assertIn(f"continuam em {folder}", state.data["output"]["resumeNote"])

    def test_purge_does_not_mark_folder_still_used_by_resumed_run(self):
        self.config(execution={"outputLayout": "BY_RUN"})
        first = self.interrupted()
        code, state = self.run_pipeline("", resume=first.run_id)
        self.assertEqual(state.data["output"]["dir"], first.data["output"]["dir"])  # mesma pasta
        data = json.loads(first.path.read_text())
        data["startedAt"] = (now_local() - timedelta(days=40)).isoformat(timespec="seconds")
        first.path.write_text(json.dumps(data))
        code = purge(DocumentPipeline(self.root).app, 30, apply=True, stream=io.StringIO())
        self.assertEqual(code, 0)
        self.assertIn("discontinued", json.loads(first.path.read_text()))
        self.assertFalse((self.root / state.data["output"]["dir"] / MARKER).exists())

    def test_invalid_resume_output_is_config_error(self):
        self.config(execution={"resumeOutput": "AMANHA"})
        with self.assertRaisesRegex(ConfigError, "resumeOutput"):
            DocumentPipeline(self.root)


if __name__ == "__main__":
    import unittest
    unittest.main()
