"""Onda 2 — validação complementar de modelos/contratos e segurança/isolamento.
CLI e Metadata API SIMULADAS; nenhuma org real."""

import io
import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tests.helpers import FAKE_SF, FAKE_TOKEN, FIXTURES, ROOT, FakeMetadataClient, TempProject
from tests.test_prioridade3 import P3Base
from salesforce_docs import cli
from salesforce_docs import status as st
from salesforce_docs.config.config_loader import load_config
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
from salesforce_docs.rendering.template_loader import ContractStore, TemplateLoader
from salesforce_docs.salesforce.cli_runner import CliRunner
from salesforce_docs.validation.project_validator import validate_project


def validate(root, strict=False):
    app = load_config(root)
    mvp = load_metadata_types(root)
    return validate_project(app, mvp, ContractStore(app.contracts_dir, mvp), strict=strict)


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.proj = TempProject()
        self.contracts = self.proj.dir / "documentation/contracts"
        self.models = self.proj.dir / "documentation/models/api-v67"

    def tearDown(self):
        self.proj.cleanup()

    def edit_contract(self, name, fn):
        p = self.contracts / name
        c = json.loads(p.read_text())
        fn(c)
        p.write_text(json.dumps(c))

    def test_repository_is_clean_in_strict_mode(self):
        self.assertEqual(validate(ROOT, strict=True), [])

    def test_template_path_cannot_escape_models_dir(self):
        for bad in ("../../config/config.json", "../modelo.md", "sub/modelo.md", "modelo.txt", "/etc/x.md"):
            self.edit_contract("remote-site-setting.schema.json", lambda c, b=bad: c.update(template=b))
            with self.assertRaises(ConfigError, msg=bad) as ctx:
                validate(self.proj.dir)
            self.assertIn("remote-site-setting.schema.json", str(ctx.exception))
            self.assertIn("Caminho de modelo inválido", str(ctx.exception))
        loader = TemplateLoader(self.models, "67.0")
        with self.assertRaises(ValueError):
            loader.load("../../config/config.json")

    def test_block_missing_from_model_or_in_wrong_section(self):
        p = self.models / "modelo-doc-named-credential-vapi-67.md"
        original = p.read_text()
        p.write_text(original.replace("{{ external_credential }}", ""))
        with self.assertRaises(ConfigError) as ctx:
            validate(self.proj.dir)
        self.assertIn("bloco 'external_credential' declarado no contrato não aparece no modelo", str(ctx.exception))
        self.assertIn("[NamedCredential]", str(ctx.exception))
        p.write_text(original)
        self.edit_contract("named-credential.schema.json",
                           lambda c: c["blocks"][0].update(markdownSection="Parâmetros"))
        with self.assertRaises(ConfigError) as ctx:
            validate(self.proj.dir)
        self.assertIn("está na seção 'Credencial externa' do modelo", str(ctx.exception))

    def test_contract_property_not_in_model_is_warning_or_intentional(self):
        extra = {"name": "Extra", "placeholder": "extra", "path": "label", "source": "XML",
                 "required": False, "markdownSection": "Identificação"}
        self.edit_contract("remote-site-setting.schema.json", lambda c: c["properties"].append(extra))
        warnings = validate(self.proj.dir)
        self.assertTrue(any("placeholder 'extra'" in w and "ausente do modelo" in w for w in warnings))
        with self.assertRaises(ConfigError):
            validate(self.proj.dir, strict=True)
        self.edit_contract("remote-site-setting.schema.json",
                           lambda c: c["properties"][-1].update(intentionallyNotRendered=True))
        self.assertEqual(validate(self.proj.dir, strict=True), [])

    def test_malformed_placeholder(self):
        p = self.models / "modelo-doc-certificate-vapi-67.md"
        p.write_text(p.read_text() + "| Quebrado | {{ ca_signed | XML |\n")
        with self.assertRaises(ConfigError) as ctx:
            validate(self.proj.dir)
        self.assertIn("placeholder malformado", str(ctx.exception))
        self.assertIn("modelo-doc-certificate-vapi-67.md:", str(ctx.exception))

    def test_templateless_contract_usage(self):
        self.edit_contract("custom-field.schema.json", lambda c: c.pop("renderedVia"))
        warnings = validate(self.proj.dir)
        self.assertTrue(any(w.startswith("custom-field.schema.json: contrato sem modelo próprio") for w in warnings))
        self.assertFalse(any("flow-definition" in w for w in warnings))  # usado por bloco do Flow

    def test_cli_strict_flag(self):
        (self.models / "modelo-doc-certificate-vapi-67.md").unlink()
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(cli.main(["--project-root", str(self.proj.dir), "validate-config"]), 0)
            self.assertEqual(cli.main(["--project-root", str(self.proj.dir), "validate-config", "--strict"]), 1)
        self.assertIn("modelo esperado ausente", err.getvalue())


class SanitizedErrorRawTest(P3Base):
    def test_cli_error_raw_is_sanitized_envelope(self):
        code, state = self.run_pipeline("leak_token_on_retrieve=Meu_Flow", groups=["Flow"])
        errors = self.root / "runs" / state.run_id / "errors"
        sanitized = errors / "retrieve-flows-meu-flow.sanitized.json"
        self.assertTrue(sanitized.is_file())
        self.assertFalse((errors / "retrieve-flows-meu-flow.raw.json").exists())
        data = json.loads(sanitized.read_text())
        self.assertTrue(data["sanitized"])
        self.assertIn("***", data["stdout"])
        self.assertIn("Erro interno com sessão ***", data["stderr"])
        for p in self.root.rglob("*"):
            if p.is_file() and p.name != "org-display.raw.json":
                self.assertNotIn(FAKE_TOKEN, p.read_text(errors="ignore"), str(p))

    def test_org_display_error_is_sanitized(self):
        code, state = self.run_pipeline("disconnected")
        errors = self.root / "runs" / state.run_id / "errors"
        self.assertTrue((errors / "org-display.sanitized.json").is_file())
        self.assertFalse((errors / "org-display.raw.json").exists())
        self.assertNotIn(FAKE_TOKEN, (errors / "org-display.sanitized.json").read_text())


class DocumentLeakBarrierTest(P3Base):
    def test_secret_value_in_other_field_blocks_document(self):
        fixtures = Path(tempfile.mkdtemp(prefix="sfdocs-fix-"))
        shutil.copytree(FIXTURES, fixtures, dirs_exist_ok=True)
        xml = fixtures / "source/namedCredentials/NC_Legada.namedCredential-meta.xml"
        secret = "SENTINELA_SENHA_LEGADA_NAO_RENDERIZAR"
        xml.write_text(xml.read_text().replace("<label>NC Legada</label>",
                                               f"<description>senha: {secret}</description>\n    <label>NC Legada</label>"))
        os.environ["FAKE_SF_FIXTURES"] = str(fixtures)
        os.environ["FAKE_SF_SCENARIO"] = ""
        log = io.StringIO()
        try:
            code, state = DocumentPipeline(self.root, runner=CliRunner(executable=str(FAKE_SF)),
                                           metadata_client_factory=lambda s: FakeMetadataClient(s),
                                           stream=log).run(groups=["NamedCredential"])
        finally:
            shutil.rmtree(fixtures, ignore_errors=True)
        entry = self.primary(state, "NC_Legada")
        self.assertEqual(entry["status"], st.FAILED)
        self.assertIn("conteúdo sensível", entry["error"])
        self.assertIsNone(entry.get("document"))
        self.assertEqual(self.primary(state, "Minha_NC")["status"], st.SUCCESS)
        for p in (self.root / "saida").rglob("*.md"):
            self.assertNotIn(secret, p.read_text())
        self.assertNotIn(secret, log.getvalue())


class GitGuardTest(P3Base):
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), "-c", "user.email=t@example.com",
                               "-c", "user.name=t"] + list(args), capture_output=True, text=True)

    def init_repo(self, with_gitignore):
        self.git("init", "-q")
        if with_gitignore:
            shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")

    def test_outside_repo_is_unavailable_not_approved(self):
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertFalse(state.data["gitGuard"]["available"])
        self.assertIn("Verificação de Git indisponível", self.log.getvalue())

    def test_tracked_sensitive_file_blocks_before_org(self):
        self.init_repo(with_gitignore=True)
        raw = self.root / "catalog/org-dev/api-v67/org-display.raw.json"
        raw.parent.mkdir(parents=True)
        raw.write_text("{}")
        self.git("add", "-f", str(raw))
        self.git("commit", "-q", "-m", "x")
        code, state = self.run_pipeline()
        self.assertEqual(state.data["failure"]["code"], "SENSITIVE_FILES_TRACKED")
        self.assertIn("catalog/org-dev/api-v67/org-display.raw.json", state.data["failure"]["message"])
        self.assertEqual(self.calls(), "")  # nenhuma chamada à CLI/org
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(cli.main(["--project-root", str(self.root), "validate-config"]), 1)

    def test_missing_gitignore_is_reported(self):
        self.init_repo(with_gitignore=False)
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        guard = state.data["gitGuard"]
        self.assertTrue(guard["available"])
        self.assertEqual(guard["tracked"], [])
        self.assertIn("catalog/org-x/api-v0/org-display.raw.json", guard["notIgnored"])
        self.assertIn("Caminho sensível não ignorado", self.log.getvalue())

    def test_repository_gitignore_covers_sensitive_paths(self):
        self.init_repo(with_gitignore=True)
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        self.assertEqual(state.data["gitGuard"]["notIgnored"], [])


class ByRunLayoutTest(P3Base):
    def test_each_run_has_its_own_directory(self):
        self.config(execution={"outputLayout": "BY_RUN"})
        code, s1 = self.run_pipeline(groups=["RemoteSiteSetting"])
        time.sleep(1.1)
        code, s2 = self.run_pipeline(groups=["RemoteSiteSetting"])
        d1 = self.primary(s1, "Meu_Site")["document"]
        d2 = self.primary(s2, "Meu_Site")["document"]
        self.assertNotEqual(d1, d2)
        self.assertIn(s1.run_id, d1)
        self.assertIn(s2.run_id, d2)
        self.assertTrue((self.root / d1).is_file() and (self.root / d2).is_file())
        self.assertEqual(s2.data["output"]["layout"], "BY_RUN")
        self.assertEqual(s2.data["output"]["replaced"], [])


if __name__ == "__main__":
    unittest.main()
