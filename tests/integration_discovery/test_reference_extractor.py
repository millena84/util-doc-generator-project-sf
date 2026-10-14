import json

from tests.integration_discovery.base import DiscoveryBase
from integration_discovery import normalized_json_loader as L
from integration_discovery.reference_extractor import build_targets, extract_references


def c(t, n):
    return {"componentType": t, "componentName": n}


CSV = [c("NamedCredential", "RH_Endpoint"), c("ApexClass", "IntegracaoRHService"), c("ApexTrigger", "ColaboradorTrigger"),
       c("CustomObject", "Colaborador__c"), c("CustomMetadata", "Endpoint_Config__mdt"), c("PermissionSet", "IntegracaoRH_User")]


def entry(t, n, data=None, code=None, path="x.json", extra=None):
    return {"key": f"{t}:{n}", "componentType": t, "componentName": n, "path": path, "data": data or {},
            "codeBody": code, "extraSources": extra or []}


class ReferenceExtractorTest(DiscoveryBase):
    def setUp(self):
        super().setUp()
        self.rules = self.settings().rules
        self.targets = build_targets(CSV)

    def refs(self, e):
        return extract_references(e, self.targets, self.rules)

    def test_apex_class_calls_named_credential(self):
        code = "public class IntegracaoRHService {\n  void enviar() {\n    req.setEndpoint('callout:RH_Endpoint/admissoes');\n  }\n}"
        r = self.refs(entry("ApexClass", "IntegracaoRHService", code=code))
        self.assertEqual(len(r), 1)
        self.assertEqual((r[0]["to"], r[0]["relationship"], r[0]["evidence"], r[0]["sourceField"], r[0]["line"],
                          r[0]["matchedText"]),
                         ("NamedCredential:RH_Endpoint", "CALLS_ENDPOINT", "CODE_REFERENCE", "codeBody", 3,
                          "callout:RH_Endpoint"))

    def test_trigger_invokes_class_and_triggers_on_object(self):
        e = L.load_component(self.settings(), c("ApexTrigger", "ColaboradorTrigger"))
        r = {(x["to"], x["relationship"], x["jsonPath"]) for x in self.refs(e)}
        self.assertIn(("ApexClass:IntegracaoRHService", "INVOKES_CLASS", "data.apex.referencedClasses[0].className"), r)
        self.assertIn(("CustomObject:Colaborador__c", "TRIGGERS_ON_OBJECT", "data.apex.sObject"), r)
        self.assertIn(("CustomMetadata:Endpoint_Config__mdt", "USES_METADATA", "data.apex.configReads[0].component"), r)
        self.assertTrue(all(x["evidence"] == "CODE_REFERENCE" for x in self.refs(e)))

    def test_custom_metadata_record_defines_endpoint_without_leaking_values(self):
        e = L.load_component(self.settings(), c("CustomMetadata", "Endpoint_Config__mdt"))
        r = self.refs(e)
        self.assertEqual([(x["to"], x["relationship"], x["evidence"]) for x in r],
                         [("NamedCredential:RH_Endpoint", "DEFINES_ENDPOINT", "CONFIGURATION_REFERENCE")])
        self.assertTrue(r[0]["sourceFile"].endswith("endpoint-config-producao.json"))
        self.assertNotIn("SENTINELA", json.dumps(r).upper())

    def test_permission_set_grants_class(self):
        e = L.load_component(self.settings(), c("PermissionSet", "IntegracaoRH_User"))
        r = {(x["to"], x["relationship"]) for x in self.refs(e)}
        self.assertIn(("ApexClass:IntegracaoRHService", "GRANTS_ACCESS_TO_CLASS"), r)
        self.assertIn(("CustomObject:Colaborador__c", "GRANTS_ACCESS_TO_OBJECT"), r)

    def test_no_reference(self):
        self.assertEqual(self.refs(entry("ApexClass", "IntegracaoRHService", {"label": "nada aqui", "n": ["x"]})), [])

    def test_exact_name_only_no_partial_or_self_match(self):
        data = {"a": "RH_Endpoint2", "b": "Meu_RH_Endpoint", "c": "rh_endpoint", "d": "IntegracaoRHService",
                "e": "[REDACTED]"}
        self.assertEqual(self.refs(entry("ApexClass", "IntegracaoRHService", data)), [])

    def test_quotes_and_suffix_variants(self):
        targets = build_targets([c("CustomObject", "Colaborador"), c("NamedCredential", "RH_Endpoint")])
        r = extract_references(entry("ApexClass", "X", {"q": "SELECT Id FROM Colaborador__c", "s": "'RH_Endpoint'"}),
                               targets, self.rules)
        self.assertEqual(sorted(x["matchedText"] for x in r), ["Colaborador__c", "RH_Endpoint"])

    def test_description_mention_is_unverified(self):
        e = L.load_component(self.settings(), c("ApexClass", "IntegracaoRHService"))
        unverified = [x for x in self.refs(e) if x["evidence"] == "UNVERIFIED"]
        self.assertEqual([(x["to"], x["jsonPath"]) for x in unverified], [("NamedCredential:RH_Endpoint", "data.apex.description")])

    def test_same_name_in_two_types_needs_path_hint(self):
        targets = build_targets([c("ApexClass", "Pedido"), c("Flow", "Pedido")])
        r = extract_references(entry("PermissionSet", "PS", {"classAccesses": {"apexClass": "Pedido"}, "x": "Pedido"}),
                               targets, self.rules)
        by_path = {}
        for x in r:
            by_path.setdefault(x["jsonPath"], []).append((x["to"], x["evidence"]))
        self.assertEqual(by_path["data.classAccesses.apexClass"], [("ApexClass:Pedido", "CONFIGURATION_REFERENCE")])
        self.assertEqual(sorted(by_path["data.x"]), [("ApexClass:Pedido", "UNVERIFIED"), ("Flow:Pedido", "UNVERIFIED")])
