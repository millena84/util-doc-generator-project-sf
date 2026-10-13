"""Refatoração 2 — `selection` no config.json (migração de `scope`) e opção (b):
em SELECTED nada fora da seleção é recuperado, nem candidatos de relações que só se
comprovam lendo o XML de cada candidato. CLI SIMULADA; nenhuma org real."""

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from tests.helpers import ROOT
from tests.test_prioridade3 import P3Base
from tests.test_scope import sel
from salesforce_docs import cli
from salesforce_docs import status as st
from salesforce_docs.config.config_loader import load_config
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.config.scope import ScopeConfig, resolve_scope
from salesforce_docs.errors import ConfigError


class SelectionConfigTest(unittest.TestCase):
    def setUp(self):
        self.mvp = load_metadata_types(ROOT)

    def resolve(self, data):
        return resolve_scope(ScopeConfig(data), self.mvp)

    def test_repository_config_uses_selection_all(self):
        app = load_config(ROOT)
        self.assertEqual(app.selection.mode, "ALL")
        self.assertIn("selection", json.loads((ROOT / "config/config.json").read_text()))

    def test_group_name_is_not_a_type(self):
        with self.assertRaises(ConfigError) as ctx:
            self.resolve(sel(("ExternalClientApp", ["*"])))
        self.assertIn("nome de GRUPO", str(ctx.exception))
        self.assertIn("ExternalClientApplication", str(ctx.exception))
        self.assertEqual(list(self.resolve(sel(("ExternalClientApplication", ["*"])))), ["ExternalClientApp"])

    def test_every_related_type_is_rejected_with_owner(self):
        cases = {"FlowDefinition": "Flow", "CustomField": "CustomObject", "RecordType": "CustomObject",
                 "ValidationRule": "CustomObject", "WebLink": "CustomObject",
                 "ExtlClntAppOauthSettings": "ExternalClientApplication"}
        for related, owner in cases.items():
            with self.assertRaises(ConfigError, msg=related) as ctx:
                self.resolve(sel((related, ["X"])))
            self.assertIn("relacionado", str(ctx.exception))
            self.assertIn(owner, str(ctx.exception))

    def test_whitespace_is_rejected_not_fixed(self):
        for data in (sel(("Flow", ["Meu_Flow "])), sel(("Flow ", ["Meu_Flow"]))):
            with self.assertRaises(ConfigError) as ctx:
                ScopeConfig(data)
            self.assertIn("espaço", str(ctx.exception))

    def test_components_all_and_list(self):
        eff = self.resolve({"mode": "SELECTED", "metadataTypes": {
            "Flow": {"components": "ALL"}, "CustomObject": {"components": ["Pedido__c"]}}})
        self.assertEqual(eff, {"Flow": None, "CustomObject": {"Pedido__c"}})
        self.assertEqual(ScopeConfig({"mode": "SELECTED", "metadataTypes": {"Flow": {"components": "ALL"}}})
                         .describe(), {"mode": "SELECTED", "metadataTypes": {"Flow": {"components": "ALL"}}})


class SelectionLoadTest(P3Base):
    def write_config_text(self, transform):
        path = self.root / "config/config.json"
        path.write_text(transform(path.read_text()))

    def test_duplicate_json_key_is_rejected(self):
        self.write_config_text(lambda t: t.replace(
            '"selection": {\n    "mode": "ALL"\n  }',
            '"selection": {"mode": "SELECTED", "metadataTypes": {'
            '"Flow": {"components": ["Meu_Flow"]}, "Flow": {"components": "ALL"}}}'))
        with self.assertRaises(ConfigError) as ctx:
            load_config(self.root)
        self.assertIn("chave JSON repetida 'Flow'", str(ctx.exception))

    def test_legacy_scope_key_explains_migration(self):
        self.config(scope={"mode": "ALL"})
        with self.assertRaises(ConfigError) as ctx:
            load_config(self.root)
        self.assertIn("substituída por `selection`", str(ctx.exception))

    def test_validate_config_shows_selection(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["--project-root", str(self.root), "validate-config"]), 0)
        self.assertIn("Seleção: ALL", out.getvalue())


class SelectedEcaOptionBTest(P3Base):
    def retrieved(self):
        # O retrieve das fontes de acesso (passo 6b) é verificado em tests/test_acesso.py.
        return sorted(l.split("--metadata ")[1].split(" ")[0] for l in self.calls().splitlines()
                      if l.startswith("project retrieve start") and "--metadata Profile" not in l)

    def test_selected_eca_does_not_retrieve_candidates(self):
        self.config(selection=sel(("ExternalClientApplication", ["*"])))
        code, state = self.run_pipeline("mvp_complete")
        self.assertEqual(code, 0, self.log.getvalue())
        self.assertEqual(self.retrieved(), ["ExternalClientApplication:Minha_ECA"])
        entry = self.primary(state, "Minha_ECA")
        self.assertEqual(entry["status"], st.SUCCESS)
        self.assertEqual(sorted(u["metadataType"] for u in entry["relatedNotResolved"]),
                         ["ExtlClntAppConfigurablePolicies", "ExtlClntAppOauthConfigurablePolicies",
                          "ExtlClntAppOauthSettings"])
        self.assertEqual(len(state.data["selection"]["relatedNotResolved"]), 3)
        text = self.read(entry["document"])
        self.assertIn("## Configuração OAuth\n\nNão informado", text)
        self.assertIn("| Não informado | Não informado | XML |", text)  # componentes relacionados
        self.assertNotIn("Não aplicável\n\n_Fonte: XML_\n\n## Políticas OAuth", text)
        cov = state.data["coverage"]
        self.assertEqual(cov["status"], "COMPLETE_WITH_WARNINGS")
        self.assertEqual(len(cov["gaps"]["relatedNotResolved"]), 3)
        self.assertEqual(state.data["status"], st.SUCCESS)
        self.assertIn("relacionados ExtlClntAppOauthSettings não verificados", self.log.getvalue())

    def test_all_mode_still_resolves_eca_relations(self):
        code, state = self.run_pipeline("mvp_complete", groups=["ExternalClientApp"])
        entry = self.primary(state, "Minha_ECA")
        self.assertEqual(entry["relatedNotResolved"], [])
        self.assertIn("ExtlClntAppOauthSettings:Outra_ECA_oauth", self.retrieved())  # comportamento ALL
        self.assertEqual(len(entry["relatedComponents"]), 3)

    def test_proven_relations_still_work_in_selected(self):
        # FlowDefinition (mesmo nome), filhos do objeto e EC referenciada pela NC são comprovados
        # sem recuperar candidatos alheios.
        self.config(selection=sel(("Flow", ["Meu_Flow"]), ("CustomObject", ["Pedido__c"]),
                                  ("NamedCredential", ["Minha_NC"])))
        code, state = self.run_pipeline()
        self.assertEqual(self.retrieved(), sorted([
            "Flow:Meu_Flow", "FlowDefinition:Meu_Flow", "CustomObject:Pedido__c",
            "NamedCredential:Minha_NC", "ExternalCredential:Minha_EC"]))
        self.assertEqual(state.data["selection"]["relatedNotResolved"], [])
        self.assertEqual(state.data["coverage"]["status"], "COMPLETE")

    def test_missing_model_in_selection_does_not_stop_others(self):
        (self.root / "documentation/models/api-v67/modelo-doc-remote-site-setting-vapi-67.md").unlink()
        self.config(selection=sel(("RemoteSiteSetting", ["*"]), ("Certificate", ["Meu_Certificado"])))
        code, state = self.run_pipeline()
        self.assertEqual(self.primary(state, "Meu_Site")["status"], st.NO_TEMPLATE)
        self.assertEqual(self.primary(state, "Meu_Certificado")["status"], st.SUCCESS)
        self.assertEqual(state.data["status"], st.COMPLETED_WITH_GAPS)
        self.assertIn("Seleção SELECTED", self.log.getvalue())
        self.assertEqual(state.data["selection"]["requested"],
                         {"mode": "SELECTED", "metadataTypes": {
                             "RemoteSiteSetting": {"components": "ALL"},
                             "Certificate": {"components": ["Meu_Certificado"]}}})


if __name__ == "__main__":
    unittest.main()
