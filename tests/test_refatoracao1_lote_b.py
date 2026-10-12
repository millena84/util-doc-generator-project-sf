"""Refatoração 1 — Lote B: NamedCredential, RemoteSiteSetting, Certificate e parâmetros da EC.

Tudo com Salesforce CLI SIMULADA e fixtures sintéticas; nenhuma org real.
"""

import json
import unittest

from tests.helpers import ROOT
from tests.test_document_pipeline import PipelineTestBase
from salesforce_docs import status as st
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.parsing.external_client_app_parser import values_at
from salesforce_docs.pipeline import deviation_handler as dh
from salesforce_docs.pipeline.component_pipeline import ComponentRecord

GROUPS = ["NamedCredential", "RemoteSiteSetting", "Certificate", "ExternalCredential"]
SECRETS = ["SENTINELA_SENHA_LEGADA_NAO_RENDERIZAR"]
BLOCKED = ["SENTINELA_HEADER_NAO_RENDERIZAR", "SENTINELA_PARAM_EC_NAO_RENDERIZAR",
           "https://sentinela-endpoint-interno.example.invalid", "https://sentinela-legado.example.invalid",
           "PS_SENTINELA_PERMISSION_SET", "SENTINELA_CONTEUDO_CRT_NAO_LER"]


class _Log:
    def warn(self, _m):
        pass


class _Proc:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def process(self, metadata_type, full_name, item=None, role="primary", folder_type=None):
        self.calls.append((metadata_type, full_name))
        return ComponentRecord(metadataType=metadata_type, fullName=full_name, status=st.SUCCESS,
                               data=self.data.get(full_name, {}), files=[], xml=f"x/{full_name}.xml",
                               children=[])


class NamedCredentialRelationTest(unittest.TestCase):
    def setUp(self):
        self.group = load_metadata_types(ROOT).group("NamedCredential")

    def related(self, nc_data, ecs):
        invs = {"NamedCredential": [{"fullName": "NC"}], "ExternalCredential": [{"fullName": n} for n in ecs]}
        proc = _Proc({"NC": nc_data})
        unit = dh.build_units(self.group, invs, None)[0]
        rel, _ = dh.resolve_related(unit, proc.process("NamedCredential", "NC"), self.group, proc,
                                    invs, {"NamedCredential", "ExternalCredential"}, _Log())
        return [r["fullName"] for r in rel], proc.calls

    def test_relation_only_when_xml_references_existing_ec(self):
        data = {"namedCredentialParameters": [{"parameterType": "Url"},
                                              {"externalCredential": "EC_A", "parameterType": "Authentication"}]}
        names, calls = self.related(data, ["EC_A", "EC_B"])
        self.assertEqual(names, ["EC_A"])
        self.assertNotIn(("ExternalCredential", "EC_B"), calls)  # não recupera EC não referenciada

    def test_no_relation_for_legacy_or_unknown_ec(self):
        self.assertEqual(self.related({"namedCredentialType": "Legacy"}, ["EC_A"])[0], [])
        data = {"namedCredentialParameters": {"externalCredential": "EC_X"}}
        self.assertEqual(self.related(data, ["EC_A"])[0], [])  # EC citada mas inexistente

    def test_no_relation_by_name_similarity(self):
        data = {"description": "usa EC_A", "namedCredentialParameters": {"parameterName": "EC_A"}}
        self.assertEqual(self.related(data, ["EC_A"])[0], [])

    def test_values_at_crosses_lists(self):
        data = {"p": [{"e": "A"}, {"e": ["B", "C"]}, {"x": "D"}]}
        self.assertEqual(values_at(data, "p.e"), {"A", "B", "C"})


class LoteBPipelineTest(PipelineTestBase):
    def run_b(self):
        code, state = self.run_pipeline(groups=GROUPS)
        self.assertEqual(code, 0, self.log.getvalue())
        return state

    def test_named_credential_document(self):
        state = self.run_b()
        entry = self.primary(state, "Minha_NC")
        text = self.read(entry["document"])
        self.assertIn("| NamedCredentialType | SecuredEndpoint | XML |", text)
        self.assertIn("| AllowMergeFieldsInHeader | true | XML |", text)
        self.assertIn("| Description | NC sintética \\| testes<br>segunda linha – ç | XML |", text)
        self.assertIn("| x-api-key | HttpHeader | XML |", text)
        self.assertIn("**ExternalCredential: Minha_EC**", text)
        self.assertRegex(text, r"_Arquivo: `inventory/org-dev/api-v67/external-credentials/components/"
                               r"externalCredentials/Minha_EC\.externalCredential-meta\.xml` · sha256 `[0-9a-f]{16}…`_")
        self.assertIn("| Minha_EC | ExternalCredential | XML |", text)
        self.assertEqual(entry["relatedComponents"],
                         [{"metadataType": "ExternalCredential", "fullName": "Minha_EC"}])

    def test_legacy_named_credential_without_relations(self):
        state = self.run_b()
        entry = self.primary(state, "NC_Legada")
        text = self.read(entry["document"])
        self.assertIn("| NamedCredentialType | Legacy | XML |", text)
        self.assertIn("## Credencial externa\n\nNão aplicável", text)
        self.assertEqual(entry["relatedComponents"], [])
        self.assertTrue(any("['password']" in w for w in entry["warnings"]))
        norm = json.loads((self.root / entry["normalized"]).read_text())
        self.assertEqual(norm["data"]["password"], "[REDACTED]")

    def test_external_credential_parameters_and_principals(self):
        state = self.run_b()
        text = self.read(self.primary(state, "Minha_EC")["document"])
        self.assertIn("| x-api-key | AuthHeader | DefaultGroup | XML |", text)
        self.assertIn("| Principal_Integracao | NamedPrincipal | 1 | XML |", text)
        params = text.split("## Parâmetros")[1].split("## Principais")[0]
        self.assertNotIn("NamedPrincipal", params)

    def test_remote_site_setting_document(self):
        state = self.run_b()
        text = self.read(self.primary(state, "Meu_Site")["document"])
        for row in ("| Url | https://api.example.com | XML |", "| IsActive | true | XML |",
                    "| DisableProtocolSecurity | false | XML |"):
            self.assertIn(row, text)

    def test_certificate_only_meta_xml(self):
        state = self.run_b()
        entry = self.primary(state, "Meu_Certificado")
        self.assertTrue(entry["xml"].endswith("Meu_Certificado.crt-meta.xml"))
        self.assertEqual(entry["children"], [])  # o .crt não é normalizado
        text = self.read(entry["document"])
        self.assertIn("| CaSigned | false | XML |", text)
        self.assertIn("| KeySize | 2048 | XML |", text)
        self.assertIn("| EncryptedWithPlatformEncryption | false | XML |", text)
        crt = self.root / "inventory/org-dev/api-v67/certificates/components/certs/Meu_Certificado.crt"
        self.assertTrue(crt.is_file())  # raw preservado (fora do Git)

    def test_sentinels_never_leak(self):
        self.run_b()
        log = self.log.getvalue()
        for p in self.root.rglob("*"):
            if not p.is_file() or "/components/" in p.as_posix():
                continue  # XML/CRT originais (raw) preservados intactos
            text = p.read_text(errors="ignore")
            for s in SECRETS:
                self.assertNotIn(s, text, f"segredo em {p}")
            rel = p.as_posix().split(self.root.as_posix())[1]
            if rel.startswith(("/saida/", "/runs/")):
                for s in BLOCKED:
                    self.assertNotIn(s, text, f"valor bloqueado em {p}")
        for s in SECRETS + BLOCKED:
            self.assertNotIn(s, log)

    def test_crt_content_not_in_any_derivative(self):
        self.run_b()
        for p in self.root.rglob("*"):
            if p.is_file() and not p.name.endswith(".crt"):
                self.assertNotIn("SENTINELA_CONTEUDO_CRT_NAO_LER", p.read_text(errors="ignore"), str(p))

    def test_certificate_type_not_enabled_is_distinct(self):
        # O cenário base tem Certificate; aqui o grupo aponta para um tipo ausente da org.
        cfg = self.root / "config/metadata-types-mvp.json"
        data = json.loads(cfg.read_text())
        for g in data["metadataTypeGroups"]:
            if g["group"] == "Certificate":
                g["primaryMetadataType"] = "PublicKeyCertificate"
        cfg.write_text(json.dumps(data))
        code, state = self.run_pipeline(groups=["Certificate"])
        enabled = [t for t in state.data["metadataTypes"] if t.get("stage") == "enabled"]
        self.assertEqual([(t["metadataType"], t["status"]) for t in enabled],
                         [("PublicKeyCertificate", st.NOT_ENABLED)])
        self.assertEqual(state.data["components"], [])


if __name__ == "__main__":
    unittest.main()
