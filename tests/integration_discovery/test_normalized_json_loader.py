from tests.integration_discovery.base import DiscoveryBase, INV
from integration_discovery import normalized_json_loader as L


def comp(t, n):
    return {"componentType": t, "componentName": n}


class NormalizedJsonLoaderTest(DiscoveryBase):
    def test_found(self):
        e = L.load_component(self.settings(), comp("ApexClass", "IntegracaoRHService"))
        self.assertEqual(e["status"], L.FOUND)
        self.assertEqual(e["path"], f"{INV}/apex-classes/normalized/integracaorhservice.json")
        self.assertEqual(e["data"]["apex"]["className"], "IntegracaoRHService")
        self.assertEqual(len(e["sha256"]), 64)

    def test_not_found_reports_expected_path(self):
        e = L.load_component(self.settings(), comp("ApexClass", "ClasseX"))
        self.assertEqual(e["status"], "NORMALIZED_JSON_NOT_FOUND")
        self.assertEqual(e["expectedPath"], f"{INV}/apex-classes/normalized/classex.json")

    def test_malformed_json(self):
        p = self.root / INV / "apex-classes" / "normalized" / "quebrada.json"
        p.write_text("{ isso não é json", encoding="utf-8")
        e = L.load_component(self.settings(), comp("ApexClass", "Quebrada"))
        self.assertEqual(e["status"], L.INVALID)

    def test_mismatch_when_file_is_other_component(self):
        src = self.root / INV / "apex-classes" / "normalized" / "sapordersync.json"
        (src.parent / "outra.json").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        e = L.load_component(self.settings(), comp("ApexClass", "Outra"))
        self.assertEqual(e["status"], L.MISMATCH)

    def test_alias_and_api_version_select_inventory(self):
        e = L.load_component(self.settings(), comp("ApexClass", "IntegracaoRHService"), alias="prod", api_version="66.0")
        self.assertEqual(e["expectedPath"], "inventory/org-prod/api-v66/apex-classes/normalized/integracaorhservice.json")

    def test_custom_metadata_type_and_records(self):
        e = L.load_component(self.settings(), comp("CustomMetadata", "Endpoint_Config__mdt"))
        self.assertEqual((e["status"], e["metadataType"]), (L.FOUND, "CustomObject"))
        self.assertEqual([x["fullName"] for x in e["extraSources"]], ["Endpoint_Config.Producao"])
        self.assertEqual(e["extraSources"][0]["link"]["evidence"], "MANIFEST_REFERENCE")

    def test_external_client_app_reads_its_policies(self):
        # D22-04: as políticas ficam em outras pastas e apontam para a ECA em externalClientApplication
        self.put_normalized("external-client-apps/normalized/integracaorh-eca.json", "ExternalClientApplication",
                            "IntegracaoRH_ECA", {"label": "ECA RH", "distributionState": "Local"})
        self.put_normalized("extl-clnt-app-oauth-configurable-policies/normalized/integracaorh-eca-oauthplcy.json",
                            "ExtlClntAppOauthConfigurablePolicies", "IntegracaoRH_ECA_oauthPlcy",
                            {"externalClientApplication": "IntegracaoRH_ECA", "commaSeparatedPermissionSet": "IntegracaoRH_User"},
                            role="related")
        self.put_normalized("extl-clnt-app-oauth-settings/normalized/outra-oauth.json", "ExtlClntAppOauthSettings",
                            "Outra_oauth", {"externalClientApplication": "Outra_ECA"}, role="related")
        e = L.load_component(self.settings(), comp("ExternalClientApp", "IntegracaoRH_ECA"))
        self.assertEqual((e["status"], e["metadataType"]), (L.FOUND, "ExternalClientApplication"))
        self.assertEqual([(x["fullName"], x["link"]["via"]) for x in e["extraSources"]],
                         [("IntegracaoRH_ECA_oauthPlcy", "data.externalClientApplication = IntegracaoRH_ECA")])

    def test_custom_object_reads_its_children_only(self):
        # D22-07: filhos do objeto (campos, record types, regras) entram como relacionados
        self.put_normalized("custom-objects/normalized/custom-field--colaborador-c-empresa-c.json", "CustomField",
                            "Colaborador__c.Empresa__c", {"fullName": "Empresa__c", "referenceTo": "Empresa__c"}, "child")
        self.put_normalized("custom-objects/normalized/custom-field--colaborador2-c-x-c.json", "CustomField",
                            "Colaborador2__c.X__c", {"fullName": "X__c"}, "child")
        e = L.load_component(self.settings(), comp("CustomObject", "Colaborador__c"))
        self.assertEqual([x["fullName"] for x in e["extraSources"]], ["Colaborador__c.Empresa__c"])
