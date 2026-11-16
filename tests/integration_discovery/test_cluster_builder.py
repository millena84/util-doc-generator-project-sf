import unittest

from integration_discovery.cluster_builder import build_clusters


def graph(nodes, edges):
    return {"nodes": [{"id": n, "type": n.split(":")[0]} for n in nodes],
            "edges": [{"from": f, "to": t, "relationship": r, "evidence": ev, "jsonPath": "data.x"}
                      for f, t, r, ev in edges]}


class ClusterBuilderTest(unittest.TestCase):
    def test_multi_component_cluster_and_orphan(self):
        g = graph(["ApexTrigger:T", "ApexClass:C", "CustomObject:O__c", "NamedCredential:NC", "RemoteSiteSetting:R"],
                  [("ApexTrigger:T", "ApexClass:C", "INVOKES_CLASS", "CODE_REFERENCE"),
                   ("ApexTrigger:T", "CustomObject:O__c", "TRIGGERS_ON_OBJECT", "CODE_REFERENCE"),
                   ("ApexClass:C", "NamedCredential:NC", "CALLS_ENDPOINT", "CODE_REFERENCE")])
        clusters, orphans = build_clusters(g, ["PermissionSet"])
        self.assertEqual(len(clusters), 1)
        c = clusters[0]
        self.assertEqual((c["clusterId"], c["status"], c["confidence"], c["relationCount"]), ("cluster-001", "CANDIDATE", "HIGH", 3))
        self.assertEqual({x["id"] for x in c["components"]},
                         {"ApexTrigger:T", "ApexClass:C", "CustomObject:O__c", "NamedCredential:NC"})
        self.assertEqual(c["humanReview"], {"decision": "PENDING", "reviewedBy": None, "notes": None})
        self.assertEqual(orphans, ["RemoteSiteSetting:R"])

    def test_bridge_component_in_two_clusters_without_merging(self):
        g = graph(["PermissionSet:PS", "ApexClass:A", "ApexClass:B"],
                  [("PermissionSet:PS", "ApexClass:A", "GRANTS_ACCESS_TO_CLASS", "CONFIGURATION_REFERENCE"),
                   ("PermissionSet:PS", "ApexClass:B", "GRANTS_ACCESS_TO_CLASS", "CONFIGURATION_REFERENCE")])
        clusters, orphans = build_clusters(g, ["PermissionSet"])
        self.assertEqual(sorted(sorted(x["id"] for x in c["components"]) for c in clusters),
                         [["ApexClass:A", "PermissionSet:PS"], ["ApexClass:B", "PermissionSet:PS"]])
        self.assertTrue(all(c["confidence"] == "LOW" for c in clusters))
        self.assertEqual(orphans, [])

    def test_without_bridge_types_the_permission_set_merges(self):
        g = graph(["PermissionSet:PS", "ApexClass:A", "ApexClass:B"],
                  [("PermissionSet:PS", "ApexClass:A", "GRANTS_ACCESS_TO_CLASS", "CONFIGURATION_REFERENCE"),
                   ("PermissionSet:PS", "ApexClass:B", "GRANTS_ACCESS_TO_CLASS", "CONFIGURATION_REFERENCE")])
        clusters, _ = build_clusters(g, [])
        self.assertEqual(len(clusters), 1)

    def test_no_edges_all_orphans(self):
        clusters, orphans = build_clusters(graph(["ApexClass:A", "PermissionSet:PS"], []), ["PermissionSet"])
        self.assertEqual((clusters, orphans), ([], ["ApexClass:A", "PermissionSet:PS"]))
