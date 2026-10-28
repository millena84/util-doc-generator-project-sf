"""Modo pasta (`run --source-dir`): documentação a partir de repositório já clonado, sem login.

Os repositórios são cópias das fixtures SIMULADAS (tests/fixtures/source, formato source do SFDX)
ou a conversão delas para o formato metadata da Metadata API (tests/source_format.py).
Nenhuma chamada à Salesforce CLI pode acontecer.
"""

import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.helpers import FIXTURES, TempProject
from tests.source_format import to_metadata_format
from salesforce_docs import status as st
from salesforce_docs.cli import main as cli_main
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.errors import ConfigError
from salesforce_docs.extraction.source_directory import SourceRepository
from salesforce_docs.pipeline.document_pipeline import EXIT_OK, DocumentPipeline

ROOT = Path(__file__).resolve().parents[1]
ACCESS_GROUPS = ["Role", "Profile", "PermissionSet", "PermissionSetGroup", "OrgSecurity", "SharingRules",
                 "CustomObject", "PublicGroup"]
NS = "http://soap.sforce.com/2006/04/metadata"


class NoCliRunner:
    """Qualquer chamada à Salesforce CLI no modo pasta é erro."""

    def __init__(self):
        self.history = []
        self.masker = None

    def run(self, args, **_kwargs):
        raise AssertionError(f"modo pasta chamou a Salesforce CLI: sf {' '.join(args)}")


def tree_hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(path).rglob("*")) if p.is_file()}


def source_repo(dest):
    shutil.copytree(FIXTURES / "source", dest)
    (dest / "manifest.json").unlink()
    return dest


class SourceIndexTest(unittest.TestCase):
    def setUp(self):
        self.mvp = load_metadata_types(ROOT)
        self.tmp = Path(tempfile.mkdtemp(prefix="sfdocs-repo-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def repo(self, path, **entry):
        return SourceRepository(path, dict({"folder": path.name, "orgName": "Org simulada"}, **entry),
                                self.mvp.source_directory, self.tmp)

    def test_index_matches_simulated_retrieve(self):
        """Cada `Tipo:Nome` da CLI simulada tem exatamente os mesmos arquivos no índice da pasta."""
        repo = self.repo(FIXTURES / "source")
        manifest = json.loads((FIXTURES / "source" / "manifest.json").read_text())
        manifest.update(json.loads((FIXTURES / "mvp-complete" / "source" / "manifest.json").read_text()))
        index = {}
        for f in repo.files:
            index.setdefault((f["type"], f["fullName"]), set()).add(f["relpath"])
        for key, entries in manifest.items():
            mtype, name = key.split(":", 1)
            expected = {e["path"] for e in entries if e["type"] == mtype}
            self.assertEqual(index.get((mtype, name)), expected, key)
        self.assertEqual(repo.format, "SOURCE")
        self.assertEqual(repo.problems, [])

    def test_metadata_format_has_same_components(self):
        src = self.repo(FIXTURES / "source")
        to_metadata_format(FIXTURES / "source", self.tmp / "Org02Repo")
        md = self.repo(self.tmp / "Org02Repo")
        self.assertEqual(md.format, "METADATA")
        keys = lambda r: {(f["type"], f["fullName"]) for f in r.files}  # noqa: E731
        # O conversor de teste cria Opportunity.object (no formato source só há os filhos).
        self.assertEqual(keys(md) - {("CustomObject", "Opportunity")}, keys(src))

    def test_metadata_folder_detection_and_encoded_names(self):
        repo = self.tmp / "OrgRepo"
        (repo / "src" / "profiles").mkdir(parents=True)
        (repo / "src" / "package.xml").write_text("<Package/>")
        (repo / "src" / "profiles" / "Custom%3A Marketing Profile.profile").write_text(
            f'<Profile xmlns="{NS}"><custom>false</custom></Profile>')
        r = self.repo(repo)
        self.assertEqual(r.describe()["metadataPath"], "src")
        self.assertEqual([i["fullName"] for i in r.inventory("Profile")], ["Custom: Marketing Profile"])

    def test_ambiguous_or_missing_metadata_folder_is_refused(self):
        repo = self.tmp / "OrgRepo"
        (repo / "roles").mkdir(parents=True)
        (repo / "src" / "roles").mkdir(parents=True)
        with self.assertRaisesRegex(ConfigError, "mais de um lugar"):
            self.repo(repo)
        self.assertEqual(self.repo(repo, metadataPath="src").describe()["metadataPath"], "src")
        empty = self.tmp / "Vazio"
        empty.mkdir()
        with self.assertRaisesRegex(ConfigError, "nenhuma pasta de metadata"):
            self.repo(empty)

    @unittest.skipIf(os.name == "nt", "links simbólicos")
    def test_symlinks_and_hidden_folders_are_ignored(self):
        repo = source_repo(self.tmp / "OrgRepo")
        outside = self.tmp / "fora.role-meta.xml"
        outside.write_text(f'<Role xmlns="{NS}"><name>Fora</name></Role>')
        os.symlink(outside, repo / "roles" / "Fora.role-meta.xml")
        (repo / ".git" / "roles").mkdir(parents=True)
        (repo / "roles" / ".oculto.role-meta.xml").write_text("<Role/>")
        names = [i["fullName"] for i in self.repo(repo).inventory("Role")]
        self.assertEqual(names, ["Diretoria", "Gerente_Vendas", "Vendas"])

    def test_same_component_in_both_formats_is_reported(self):
        repo = source_repo(self.tmp / "OrgRepo")
        shutil.copyfile(repo / "roles" / "Vendas.role-meta.xml", repo / "roles" / "Vendas.role")
        r = self.repo(repo)
        self.assertEqual(len(r._by_key[("Role", "Vendas")]), 1)
        self.assertTrue(any("Role:Vendas" in p for p in r.problems))


class SourcePipelineTest(unittest.TestCase):
    def setUp(self):
        self.proj = TempProject()
        self.root = self.proj.dir
        self.repos = Path(tempfile.mkdtemp(prefix="sfdocs-repos-"))
        cfg_path = self.root / "config" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["sourceRepositories"] = [{"folder": "Org01Repo", "orgName": "Org 01 (simulada)"},
                                     {"folder": "Org02Repo", "orgName": "Org 02 (simulada)"}]
        cfg_path.write_text(json.dumps(cfg, indent=2))

    def tearDown(self):
        self.proj.cleanup()
        shutil.rmtree(self.repos, ignore_errors=True)

    def run_source(self, repo, **kwargs):
        self.log = io.StringIO()
        pipeline = DocumentPipeline(self.root, runner=NoCliRunner(), stream=self.log,
                                    metadata_client_factory=lambda s: self.fail("Metadata API chamada"))
        return pipeline.run(source_dir=str(repo), **kwargs)

    def docs(self, state):
        return {Path(c["document"]).name: (self.root / c["document"]).read_text(encoding="utf-8")
                for c in state.data["components"] if c.get("role") == "primary" and c.get("document")}

    def test_access_documentation_without_login(self):
        repo = source_repo(self.repos / "Org01Repo")
        before = tree_hashes(repo)
        code, state = self.run_source(repo, groups=ACCESS_GROUPS)
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["status"], st.SUCCESS)
        self.assertEqual(state.data["mode"], "SOURCE_DIRECTORY")
        self.assertEqual(tree_hashes(repo), before, "o repositório não pode ser alterado")
        docs = self.docs(state)
        for name in ("doc-admin-profile.md", "doc-gerente-vendas-role.md", "doc-integracao-api-permission-set.md",
                     "doc-psg-integracao-permission-set-group.md", "doc-security-org-security.md",
                     "doc-pedido-c-sharing-rules.md", "doc-pedido-c-custom-object.md"):
            self.assertIn(name, docs)
            self.assertIn("> **Origem:** repositório `Org01Repo` (org: **Org 01 (simulada)**)", docs[name])
        self.assertIn("| Acima | Diretoria | 2 acima | Derivado |", docs["doc-gerente-vendas-role.md"])
        self.assertIn("| Pedido__c | Pedido | ReadWrite |", docs["doc-security-org-security.md"])
        # Dados internos não são consultados: "Não informado", sem inventar valores.
        self.assertIn("| Não informado | Não informado | Objeto interno |", docs["doc-admin-profile.md"])
        # Registro do raw: caminho no repositório e sha256 de cada arquivo lido.
        manifest = json.loads((self.root / state.data["source"]["manifest"]).read_text())
        paths = {f["path"]: f["sha256"] for f in manifest["fileList"]}
        self.assertEqual(paths["Org01Repo/profiles/Admin.profile-meta.xml"],
                         before["profiles/Admin.profile-meta.xml"])
        summary = (self.root / "runs" / state.run_id / "resumo.md").read_text(encoding="utf-8")
        self.assertIn("## Origem (modo pasta, sem login)", summary)
        self.assertIn("`Org01Repo` → org **Org 01 (simulada)**", summary)
        self.assertNotIn("## Org-alvo", summary)

    def test_folder_without_mapping_is_refused_before_reading(self):
        repo = source_repo(self.repos / "OutraPasta")
        with self.assertRaisesRegex(ConfigError, "não está em sourceRepositories"):
            self.run_source(repo)
        self.assertFalse(list((self.root / "runs").glob("run-*.json")) if (self.root / "runs").is_dir() else [])
        with self.assertRaisesRegex(ConfigError, "não podem ser usados juntos"):
            self.run_source(source_repo(self.repos / "Org01Repo"), org_alias="dev")

    def test_both_formats_generate_the_same_documents(self):
        code1, s1 = self.run_source(source_repo(self.repos / "Org01Repo"))
        to_metadata_format(FIXTURES / "source", self.repos / "Org02Repo")
        code2, s2 = self.run_source(self.repos / "Org02Repo")
        self.assertEqual((code1, code2), (EXIT_OK, EXIT_OK), self.log.getvalue())
        self.assertEqual(s2.data["source"]["format"], "METADATA")
        d1, d2 = self.docs(s1), self.docs(s2)
        d2.pop("doc-opportunity-custom-object.md")  # Opportunity.object criado só pelo conversor de teste
        self.assertEqual(set(d1), set(d2))
        def strip(text, alias):
            return "\n".join(line.replace(alias, "ALIAS") for line in text.split("\n")
                             if "Origem:" not in line and "| Opportunity |" not in line)
        for name in d1:
            self.assertEqual(strip(d1[name], "org01repo"), strip(d2[name], "org02repo"), name)
        for name, text in d1.items():  # sentinelas das fixtures nunca chegam ao Markdown
            for sentinel in ("SEGREDO_SIMULADO", "sentinela", "@example.invalid"):
                self.assertNotIn(sentinel, text, name)

    def test_standard_object_owd_only_in_source_mode(self):
        repo = source_repo(self.repos / "Org01Repo")
        (repo / "objects" / "Account").mkdir()
        (repo / "objects" / "Account" / "Account.object-meta.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<CustomObject xmlns="{NS}">\n'
            "    <sharingModel>Read</sharingModel>\n</CustomObject>\n")
        code, state = self.run_source(repo, groups=["CustomObject", "OrgSecurity"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        docs = self.docs(state)
        self.assertIn("doc-account-custom-object.md", docs)
        self.assertIn("| Account | Não informado | Read |", docs["doc-security-org-security.md"])
        mvp = load_metadata_types(self.root)
        self.assertFalse(mvp.group("CustomObject").accepts("Account"))  # modo com login: só __c

    def test_unreadable_object_fails_only_that_component(self):
        to_metadata_format(FIXTURES / "source", self.repos / "Org02Repo")
        (self.repos / "Org02Repo" / "objects" / "Quebrado__c.object").write_text("<CustomObject><fields>")
        code, state = self.run_source(self.repos / "Org02Repo", groups=["CustomObject", "Profile"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["status"], st.PARTIAL_SUCCESS)
        statuses = {c["component"]: c["status"] for c in state.data["components"] if c.get("role") == "primary"}
        self.assertEqual(statuses["Pedido__c"], st.SUCCESS)
        self.assertEqual(statuses["Admin"], st.SUCCESS)
        self.assertNotEqual(statuses["Quebrado__c"], st.SUCCESS)

    def test_regenerate_and_resume_from_source_run(self):
        repo = source_repo(self.repos / "Org01Repo")
        code, state = self.run_source(repo, groups=["Role"])
        self.assertEqual(code, EXIT_OK)
        pipeline = DocumentPipeline(self.root, runner=NoCliRunner(), stream=io.StringIO())
        code, regen = pipeline.regenerate(state.run_id)
        self.assertEqual(code, EXIT_OK)
        doc = self.docs(regen)["doc-vendas-role.md"]
        self.assertIn("repositório `Org01Repo`", doc)
        code, resumed = self.run_source(repo, groups=["Role"], resume=state.run_id)
        self.assertEqual(len(resumed.data["resume"]["reused"]), 3)
        (repo / "roles" / "Vendas.role-meta.xml").write_text(
            (repo / "roles" / "Vendas.role-meta.xml").read_text().replace("Vendas", "Vendas Sul", 1))
        code, changed = self.run_source(repo, groups=["Role"], resume=state.run_id)
        self.assertEqual(changed.data["resume"]["reused"], [])
        self.assertIn("repositório de origem", json.dumps(changed.data["resume"]["reprocessed"],
                                                          ensure_ascii=False))

    def test_cli_source_dir(self):
        repo = source_repo(self.repos / "Org01Repo")
        err = io.StringIO()
        from contextlib import redirect_stderr
        with redirect_stderr(err):
            code = cli_main(["--project-root", str(self.root), "run", "--source-dir", str(repo),
                             "--group", "Role", "--component", "Vendas"])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("Modo pasta: repositório Org01Repo", err.getvalue())


if __name__ == "__main__":
    unittest.main()
