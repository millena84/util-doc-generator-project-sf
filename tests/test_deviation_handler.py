import json
import unittest

from tests.helpers import ROOT
from salesforce_docs import status as st
from salesforce_docs.config.metadata_types_loader import MetadataTypesConfig, load_metadata_types
from salesforce_docs.pipeline import deviation_handler as dh
from salesforce_docs.pipeline.component_pipeline import ComponentRecord


class _Log:
    def warn(self, _m):
        pass


class FakeProcessor:
    def __init__(self, data_by_key, failing=()):
        self.data = data_by_key
        self.failing = set(failing)
        self.calls = []

    def process(self, metadata_type, full_name, item=None, role="primary", folder_type=None):
        self.calls.append((metadata_type, full_name))
        status = st.RETRIEVE_FAILED if (metadata_type, full_name) in self.failing else st.SUCCESS
        return ComponentRecord(metadataType=metadata_type, fullName=full_name, status=status,
                               data=self.data.get((metadata_type, full_name), {}),
                               files=[{"type": metadata_type, "fullName": full_name,
                                       "path": f"x/components/{metadata_type}/{full_name}.xml"}],
                               xml=f"x/{full_name}.xml", children=[])


def inv(*names):
    return [{"fullName": n} for n in names]


def mvp_with_reference_scan(*types):
    """Config do MVP com relações REFERENCE_SCAN extras no grupo ExternalClientApp (só para teste)."""
    data = json.loads((ROOT / "config" / "metadata-types-mvp.json").read_text(encoding="utf-8"))
    group = next(g for g in data["metadataTypeGroups"] if g["group"] == "ExternalClientApp")
    group["relatedMetadataTypes"] += list(types)
    group["relations"] += [{"metadataType": t, "match": "REFERENCE_SCAN"} for t in types]
    return MetadataTypesConfig(data)


class DeviationHandlerTest(unittest.TestCase):
    def setUp(self):
        self.mvp = load_metadata_types(ROOT)

    def test_flow_with_flow_definition(self):
        g = self.mvp.group("Flow")
        invs = {"Flow": inv("Meu_Flow", "Outro"), "FlowDefinition": inv("Meu_Flow")}
        units = dh.build_units(g, invs, self.mvp)
        self.assertEqual([u["fullName"] for u in units], ["Meu_Flow", "Outro"])
        proc = FakeProcessor({})
        primary = proc.process("Flow", "Meu_Flow")
        related, failures = dh.resolve_related(units[0], primary, g, proc, invs,
                                               {"Flow", "FlowDefinition"}, _Log())
        self.assertEqual([(r["metadataType"], r["fullName"]) for r in related],
                         [("FlowDefinition", "Meu_Flow")])
        related2, _ = dh.resolve_related(units[1], proc.process("Flow", "Outro"), g, proc, invs,
                                         {"Flow", "FlowDefinition"}, _Log())
        self.assertEqual(related2, [])

    def test_flow_related_not_enabled_is_skipped(self):
        g = self.mvp.group("Flow")
        invs = {"Flow": inv("Meu_Flow"), "FlowDefinition": inv("Meu_Flow")}
        unit = dh.build_units(g, invs, self.mvp)[0]
        proc = FakeProcessor({})
        related, _ = dh.resolve_related(unit, proc.process("Flow", "Meu_Flow"), g, proc, invs,
                                        {"Flow"}, _Log())
        self.assertEqual(related, [])

    def test_external_client_app_related_components(self):
        """Só ExtlClntApp* ligados por externalClientApplication; os demais tipos não são da ECA."""
        g = self.mvp.group("ExternalClientApp")
        invs = {
            "ExternalClientApplication": inv("Minha_ECA"),
            "ExtlClntAppOauthSettings": inv("Minha_ECA_oauth", "Outra_oauth"),
            "ExtlClntAppConfigurablePolicies": inv("Minha_ECA_plcy"),
            "ExtlClntAppOauthConfigurablePolicies": inv("Minha_ECA_oauthPlcy"),
            "NamedCredential": inv("NC_Referenciada"),
            "ConnectedApp": inv("App_Que_Cita_ECA"),
        }
        data = {
            ("ExternalClientApplication", "Minha_ECA"): {"label": "x", "description": "NC_Referenciada"},
            ("ExtlClntAppOauthSettings", "Minha_ECA_oauth"): {"externalClientApplication": "Minha_ECA"},
            ("ExtlClntAppOauthSettings", "Outra_oauth"): {"externalClientApplication": "Outra"},
            ("ExtlClntAppConfigurablePolicies", "Minha_ECA_plcy"): {"externalClientApplication": "Minha_ECA"},
            ("ExtlClntAppOauthConfigurablePolicies", "Minha_ECA_oauthPlcy"):
                {"externalClientApplication": "Minha_ECA"},
            ("ConnectedApp", "App_Que_Cita_ECA"): {"plugin": {"name": "Minha_ECA"}},
        }
        proc = FakeProcessor(data)
        unit = dh.build_units(g, invs, self.mvp)[0]
        primary = proc.process("ExternalClientApplication", "Minha_ECA")
        enabled = set(g.all_types) | {"NamedCredential", "ConnectedApp"}
        related, failures = dh.resolve_related(unit, primary, g, proc, invs, enabled, _Log())
        found = sorted((r["metadataType"], r["fullName"]) for r in related)
        self.assertEqual(found, [("ExtlClntAppConfigurablePolicies", "Minha_ECA_plcy"),
                                 ("ExtlClntAppOauthConfigurablePolicies", "Minha_ECA_oauthPlcy"),
                                 ("ExtlClntAppOauthSettings", "Minha_ECA_oauth")])
        self.assertEqual(failures, [])
        self.assertNotIn(("NamedCredential", "NC_Referenciada"), proc.calls)
        self.assertNotIn(("ConnectedApp", "App_Que_Cita_ECA"), proc.calls)

    def test_reference_scan_engine(self):
        """REFERENCE_SCAN segue disponível no motor para quem configurar (fora do MVP)."""
        mvp = mvp_with_reference_scan("NamedCredential", "ConnectedApp")
        g = mvp.group("ExternalClientApp")
        invs = {"ExternalClientApplication": inv("Minha_ECA"),
                "NamedCredential": inv("NC_Referenciada", "NC_Solta"),
                "ConnectedApp": inv("App_Que_Cita_ECA")}
        data = {("ExternalClientApplication", "Minha_ECA"): {"description": "NC_Referenciada"},
                ("NamedCredential", "NC_Solta"): {"label": "NC"},
                ("ConnectedApp", "App_Que_Cita_ECA"): {"plugin": {"name": "Minha_ECA"}}}
        proc = FakeProcessor(data)
        unit = dh.build_units(g, invs, mvp)[0]
        related, _ = dh.resolve_related(unit, proc.process("ExternalClientApplication", "Minha_ECA"), g,
                                        proc, invs, set(g.all_types), _Log())
        self.assertEqual(sorted((r["metadataType"], r["fullName"]) for r in related),
                         [("ConnectedApp", "App_Que_Cita_ECA"), ("NamedCredential", "NC_Referenciada")])

    def test_reference_scan_requires_exact_value(self):
        mvp = mvp_with_reference_scan("NamedCredential")
        g = mvp.group("ExternalClientApp")
        invs = {"ExternalClientApplication": inv("App"), "NamedCredential": inv("App_NC")}
        data = {("ExternalClientApplication", "App"): {"description": "App_NC_outro"},
                ("NamedCredential", "App_NC"): {"label": "App plus"}}
        proc = FakeProcessor(data)
        unit = dh.build_units(g, invs, mvp)[0]
        related, _ = dh.resolve_related(unit, proc.process("ExternalClientApplication", "App"), g,
                                        proc, invs, set(g.all_types), _Log())
        self.assertEqual(related, [])

    def test_related_failure_reported(self):
        g = self.mvp.group("ExternalClientApp")
        invs = {"ExternalClientApplication": inv("App"), "ExtlClntAppOauthSettings": inv("App_oauth")}
        proc = FakeProcessor({}, failing={("ExtlClntAppOauthSettings", "App_oauth")})
        unit = dh.build_units(g, invs, self.mvp)[0]
        _, failures = dh.resolve_related(unit, proc.process("ExternalClientApplication", "App"), g,
                                         proc, invs, set(g.all_types), _Log())
        self.assertEqual([f["fullName"] for f in failures], ["App_oauth"])

    def test_custom_object_filter_and_children(self):
        g = self.mvp.group("CustomObject")
        units = dh.build_units(g, {"CustomObject": inv("Account", "Pedido__c", "Config__mdt")}, self.mvp)
        self.assertEqual([u["fullName"] for u in units], ["Pedido__c"])
        files = [{"type": "CustomObject", "fullName": "Pedido__c", "path": "a/Pedido__c.object-meta.xml"},
                 {"type": "CustomField", "fullName": "Pedido__c.Valor__c", "path": "a/fields/Valor__c.field-meta.xml"}]
        child = {"metadataType": "CustomField", "fullName": "Pedido__c.Valor__c",
                 "xml": "a/fields/Valor__c.field-meta.xml", "data": {"label": "Valor"}}
        primary = ComponentRecord(metadataType="CustomObject", fullName="Pedido__c", files=files,
                                  children=[child], data={})
        related, _ = dh.resolve_related(units[0], primary, g, FakeProcessor({}), {},
                                        set(g.all_types), _Log())
        self.assertEqual([r["fullName"] for r in related], ["Pedido__c.Valor__c"])

    def test_custom_metadata_groups_type_and_records(self):
        g = self.mvp.group("CustomMetadata")
        units = dh.build_units(g, {"CustomMetadata": inv("Config.B", "Config.A", "Outro.X")}, self.mvp)
        self.assertEqual([(u["fullName"], u["metadataType"]) for u in units],
                         [("Config__mdt", "CustomObject"), ("Outro__mdt", "CustomObject")])
        self.assertEqual([r["fullName"] for r in units[0]["records"]], ["Config.A", "Config.B"])

    def test_sub_documents(self):
        g = self.mvp.group("Flow")
        trig = dh.sub_document_targets(g, {"start": {"triggerType": "RecordAfterSave"}}, "F")
        self.assertEqual([t[0]["documentSuffix"] for t in trig], ["flow-trigger"])
        scr = dh.sub_document_targets(g, {"screens": [{"name": "S1"}, {"name": "S2"}]}, "F")
        self.assertEqual([t[2] for t in scr], ["S1", "S2"])
        self.assertEqual(dh.sub_document_targets(g, {"start": {}}, "F"), [])


if __name__ == "__main__":
    unittest.main()
