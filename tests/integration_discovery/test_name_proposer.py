import unittest

from integration_discovery.name_proposer import propose
from integration_discovery.settings import DEFAULT_NAME_STOPWORDS

STOP = set(DEFAULT_NAME_STOPWORDS)


def cluster(members, edges, confidence="MEDIUM", bridges=()):
    return {"clusterId": "cluster-001", "confidence": confidence,
            "components": [{"id": m, "type": m.split(":")[0], "bridge": m in bridges} for m in members],
            "relationships": [{"from": f, "to": t, "relationship": r, "evidence": "CODE_REFERENCE", "jsonPath": p}
                              for f, t, r, p in edges], "orphanComponents": []}


class NameProposerTest(unittest.TestCase):
    def test_common_prefix(self):
        c = cluster(["ApexClass:IntegracaoRHService", "NamedCredential:RH_Endpoint", "CustomObject:Colaborador__c"],
                    [("ApexClass:IntegracaoRHService", "NamedCredential:RH_Endpoint", "CALLS_ENDPOINT", "codeBody")])
        p = propose(c, {"CustomObject:Colaborador__c": "Colaborador", "NamedCredential:RH_Endpoint": "Endpoint do RH"},
                    {}, STOP, ["RemoteSiteSetting:RH_Remote_Site", "ApexClass:Outra"])
        self.assertEqual(p["proposedName"], "Integração RH - Colaborador")
        self.assertEqual(p["status"], "CANDIDATE")
        self.assertLessEqual(len(p["alternativeNames"]), 2)
        self.assertIn("Termo RH aparece no nome de 2 componentes: IntegracaoRHService, RH_Endpoint.", p["rationale"])
        self.assertEqual([o["id"] for o in c["orphanComponents"]], ["RemoteSiteSetting:RH_Remote_Site"])
        self.assertEqual(c["proposedName"], p["proposedName"])

    def test_rationale_cites_references(self):
        c = cluster(["ApexTrigger:ColaboradorTrigger", "CustomObject:Colaborador__c"],
                    [("ApexTrigger:ColaboradorTrigger", "CustomObject:Colaborador__c", "TRIGGERS_ON_OBJECT", "data.apex.sObject")])
        p = propose(c, {"CustomObject:Colaborador__c": "Colaborador"}, {}, STOP, [])
        self.assertTrue(any("ApexTrigger ColaboradorTrigger dispara no objeto CustomObject Colaborador__c" in r
                            for r in p["rationale"]))
        self.assertTrue(p["proposedName"].startswith("Integração Colaborador"))

    def test_low_confidence_when_evidence_is_weak(self):
        c = cluster(["PermissionSet:Acesso_Geral", "ApexClass:Utilitario"],
                    [("PermissionSet:Acesso_Geral", "ApexClass:Utilitario", "GRANTS_ACCESS_TO_CLASS", "data.classAccesses")],
                    confidence="MEDIUM", bridges=("PermissionSet:Acesso_Geral",))
        p = propose(c, {"PermissionSet:Acesso_Geral": "Acesso Geral"}, {}, STOP, [])
        self.assertEqual(p["confidence"], "LOW")
        self.assertIn("evidência fraca", p["rationale"][-1])
