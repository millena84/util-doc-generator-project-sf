"""Prioridade 2 — escopo de execução no config.json (ALL x SELECTED).

CLI e Metadata API SIMULADAS; nenhuma org real.
"""

import json
import unittest

from tests.helpers import ROOT
from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.config.scope import ScopeConfig, describe_effective, resolve_scope
from salesforce_docs.errors import ConfigError
from salesforce_docs.pipeline.document_pipeline import EXIT_FAILURE, EXIT_OK, DocumentPipeline


def sel(*items):
    """Seleção no formato do config.json; ["*"] nos testes = "ALL"."""
    return {"mode": "SELECTED",
            "metadataTypes": {t: {"components": "ALL" if c == ["*"] else c} for t, c in items}}


class ScopeConfigTest(unittest.TestCase):
    def setUp(self):
        self.mvp = load_metadata_types(ROOT)

    def test_default_is_all(self):
        eff = resolve_scope(ScopeConfig(None), self.mvp)
        self.assertEqual(set(eff), {g.name for g in self.mvp.groups})
        self.assertTrue(all(v is None for v in eff.values()))

    def test_selected_types_and_components(self):
        eff = resolve_scope(ScopeConfig(sel(("Flow", ["Meu_Flow"]), ("ConnectedApp", ["*"]),
                                            ("CustomMetadata", ["Config__mdt"]))), self.mvp)
        self.assertEqual(describe_effective(eff), {"ConnectedApp": ["ALL"], "CustomMetadata": ["Config__mdt"],
                                                   "Flow": ["Meu_Flow"]})

    def test_invalid_configurations_are_rejected(self):
        bad = [
            {"mode": "TUDO"},
            {"mode": "all"},
            {"mode": "SELECTED"},
            {"mode": "SELECTED", "metadataTypes": {}},
            {"mode": "ALL", "metadataTypes": {"Flow": {"components": "ALL"}}},
            {"mode": "SELECTED", "metadataTypes": [{"metadataType": "Flow"}]},
            sel(("Flow", [])),
            sel(("Flow", ["*", "Meu_Flow"])),
            sel(("Flow", ["ALL", "Meu_Flow"])),
            sel(("Flow", ["A", "A"])),
            sel(("Flow", [""])),
            sel(("Flow", [" Meu_Flow"])),
            sel((" Flow", ["Meu_Flow"])),
            {"mode": "SELECTED", "metadataTypes": {"Flow": {"components": "all"}}},
            {"mode": "SELECTED", "metadataTypes": {"Flow": {"components": 1}}},
            {"mode": "SELECTED", "metadataTypes": {"Flow": {}}},
            {"mode": "SELECTED", "metadataTypes": {"Flow": ["Meu_Flow"]}},
            {"mode": "SELECTED", "metadataTypes": {"Flow": {"components": "ALL", "componentes": ["A"]}}},
            {"mode": "SELECTED", "selecao": 1, "metadataTypes": {"Flow": {"components": "ALL"}}},
            "ALL",
        ]
        for data in bad:
            with self.assertRaises(ConfigError, msg=str(data)):
                ScopeConfig(data)

    def test_unknown_and_related_types_are_rejected(self):
        with self.assertRaises(ConfigError) as ctx:
            resolve_scope(ScopeConfig(sel(("CustomApplication", ["X"]))), self.mvp)
        self.assertIn("não está configurado", str(ctx.exception))
        for related, principal in (("FlowDefinition", "Flow"), ("CustomField", "CustomObject"),
                                   ("ExtlClntAppOauthSettings", "ExternalClientApplication")):
            with self.assertRaises(ConfigError) as ctx:
                resolve_scope(ScopeConfig(sel((related, ["X"]))), self.mvp)
            self.assertIn("relacionado", str(ctx.exception))
            self.assertIn(principal, str(ctx.exception))

    def test_cli_only_narrows_config(self):
        scope = ScopeConfig(sel(("Flow", ["Meu_Flow", "Tela_Cadastro"])))
        self.assertEqual(describe_effective(resolve_scope(scope, self.mvp, cli_components=["Meu_Flow"])),
                         {"Flow": ["Meu_Flow"]})
        with self.assertRaises(ConfigError):
            resolve_scope(scope, self.mvp, cli_components=["Processa_Pedido"])
        with self.assertRaises(ConfigError):
            resolve_scope(scope, self.mvp, cli_groups=["ConnectedApp"])
        with self.assertRaises(ConfigError):
            resolve_scope(ScopeConfig(None), self.mvp, cli_groups=["NaoExiste"])

    def test_cli_in_all_mode_keeps_previous_behavior(self):
        eff = resolve_scope(ScopeConfig(None), self.mvp, cli_groups=["Flow"], cli_components=["Meu_Flow"])
        self.assertEqual(describe_effective(eff), {"Flow": ["Meu_Flow"]})


class ScopePipelineTest(PipelineTestBase):
    def set_scope(self, scope, **extra):
        cfg_path = self.root / "config" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg.pop("scope", None)
        cfg["selection"] = scope
        cfg.update(extra)
        cfg_path.write_text(json.dumps(cfg))

    def calls(self):
        return self.calls_file.read_text() if self.calls_file.exists() else ""

    def retrieved(self):
        out = []
        for line in self.calls().splitlines():
            # O retrieve das fontes de acesso (passo 6b) é verificado em tests/test_acesso.py.
            if line.startswith("project retrieve start") and "--metadata Profile" not in line:
                out.append(line.split("--metadata ")[1].split(" ")[0])
        return sorted(out)

    def test_selected_only_retrieves_scope_and_dependencies(self):
        self.set_scope(sel(("Flow", ["Meu_Flow"]), ("CustomMetadata", ["Config__mdt"]),
                           ("RemoteSiteSetting", ["*"])))
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(self.retrieved(), sorted([
            "Flow:Meu_Flow", "FlowDefinition:Meu_Flow",                       # dependência do Flow
            "CustomObject:Config__mdt", "CustomMetadata:Config.Padrao",
            "CustomMetadata:Config.Secundario", "RemoteSiteSetting:Meu_Site"]))
        listed = [l for l in self.calls().splitlines() if l.startswith("org list metadata ")]
        types = sorted(l.split("--metadata-type ")[1].split(" ")[0] for l in listed)
        self.assertEqual(types, ["CustomMetadata", "Flow", "FlowDefinition", "RemoteSiteSetting"])
        primaries = sorted(c["component"] for c in state.data["components"] if c["role"] == "primary")
        self.assertEqual(primaries, ["Config__mdt", "Meu_Flow", "Meu_Site"])
        scope = state.data["selection"]
        self.assertEqual(scope["mode"], "SELECTED")
        self.assertEqual(scope["effective"], {"CustomMetadata": ["Config__mdt"], "Flow": ["Meu_Flow"],
                                              "RemoteSiteSetting": ["ALL"]})
        out = {t["group"]: t["status"] for t in state.data["metadataTypes"] if t.get("stage") == "scope"}
        self.assertEqual(out.get("ConnectedApp"), st.OUT_OF_SCOPE)
        self.assertNotIn("Flow", out)

    def test_not_found_and_filtered_are_explicit(self):
        self.set_scope(sel(("Flow", ["Meu_Flow", "Flow_Inexistente"]), ("CustomObject", ["Account"])))
        code, state = self.run_pipeline()
        nf = {(n["metadataType"], n["component"]): n["reason"] for n in state.data["selection"]["notFound"]}
        self.assertIn("não encontrado", nf[("Flow", "Flow_Inexistente")])
        self.assertIn("componentFilter", nf[("CustomObject", "Account")])
        statuses = [(t["component"], t["status"]) for t in state.data["metadataTypes"]
                    if t.get("stage") == "selection"]
        self.assertEqual(sorted(statuses), [("Account", st.NOT_FOUND), ("Flow_Inexistente", st.NOT_FOUND)])
        self.assertEqual(self.primary(state, "Meu_Flow")["status"], st.SUCCESS)
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        self.assertNotIn("CustomObject:Account", self.calls())

    def test_invalid_scope_fails_before_any_org_call(self):
        self.set_scope(sel(("FlowDefinition", ["Meu_Flow"])))
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_FAILURE)
        self.assertEqual(state.data["failure"]["code"], "CONFIG_ERROR")
        self.assertEqual(self.calls(), "")

    def test_malformed_scope_rejected_at_load(self):
        self.set_scope({"mode": "SELECTED"})
        with self.assertRaises(ConfigError):
            DocumentPipeline(self.root)

    def test_cli_outside_selected_scope_fails_before_org(self):
        self.set_scope(sel(("Flow", ["Meu_Flow"])))
        code, state = self.run_pipeline(components=["Tela_Cadastro"])
        self.assertEqual(code, EXIT_FAILURE)
        self.assertIn("fora da seleção", state.data["failure"]["message"])
        self.assertEqual(self.calls(), "")

    def test_all_mode_documents_everything_configured(self):
        self.set_scope({"mode": "ALL"})
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_OK)
        primaries = {c["component"] for c in state.data["components"] if c["role"] == "primary"}
        self.assertTrue({"Meu_Flow", "Tela_Cadastro", "Processa_Pedido", "Pedido__c", "Minha_NC",
                         "Meu_Site", "Meu_Certificado"} <= primaries)
        self.assertEqual(state.data["selection"]["effective"]["Flow"], ["ALL"])

    def test_org_alias_and_paths_from_config_json(self):
        self.set_scope({"mode": "ALL"}, orgAlias="outra")
        cfg_path = self.root / "config" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["paths"]["outputDocs"] = "docs-geradas"
        cfg_path.write_text(json.dumps(cfg))
        code, state = self.run_pipeline(groups=["RemoteSiteSetting"])
        # A CLI simulada só conhece o alias "dev": prova que o alias veio do config.json.
        self.assertEqual(state.data["failure"]["code"], "ORG_NOT_AUTHENTICATED")
        self.assertEqual(state.data["selection"]["orgAlias"], "outra")
        self.assertEqual(state.data["selection"]["orgAliasSource"], "config.json")
        code, state = self.run_pipeline(org_alias="dev", groups=["RemoteSiteSetting"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(state.data["selection"]["orgAliasSource"], "--target-org")
        self.assertTrue(self.primary(state, "Meu_Site")["document"].startswith("docs-geradas/"))

    def test_custom_metadata_types_path(self):
        src = self.root / "config" / "metadata-types-mvp.json"
        dst = self.root / "config" / "tipos-alternativos.json"
        data = json.loads(src.read_text())
        data["metadataTypeGroups"] = [g for g in data["metadataTypeGroups"] if g["group"] == "RemoteSiteSetting"]
        dst.write_text(json.dumps(data))
        src.unlink()
        cfg_path = self.root / "config" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["paths"]["metadataTypesConfig"] = "config/tipos-alternativos.json"
        cfg_path.write_text(json.dumps(cfg))
        code, state = self.run_pipeline()
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        self.assertEqual(list(state.data["selection"]["effective"]), ["RemoteSiteSetting"])


if __name__ == "__main__":
    unittest.main()
