import unittest

from integration_discovery.graph_builder import build_graph

RULES = {"inverseRelationships": {"TRIGGERS_ON_OBJECT": "HAS_TRIGGER"}}


def node(key, status="FOUND"):
    t, n = key.split(":")
    return {"key": key, "componentType": t, "componentName": n, "status": status, "path": f"{n}.json",
            "sha256": "0" * 64, "label": None}


def rel(f, t, r="INVOKES_CLASS", ev="CODE_REFERENCE"):
    return {"from": f, "to": t, "relationship": r, "evidence": ev, "jsonPath": "data.x", "sourceFile": "f",
            "sourceField": "data", "matchedText": t.split(":")[1], "line": None}


class GraphBuilderTest(unittest.TestCase):
    def test_nodes_edges_inverse_and_exclusions(self):
        entries = [node("ApexTrigger:T"), node("ApexClass:C"), node("CustomObject:O__c"),
                   node("NamedCredential:NC", status="NORMALIZED_JSON_NOT_FOUND")]
        rels = [rel("ApexTrigger:T", "ApexClass:C"), rel("ApexTrigger:T", "CustomObject:O__c", "TRIGGERS_ON_OBJECT"),
                rel("ApexClass:C", "NamedCredential:NC", "CALLS_ENDPOINT"),
                rel("ApexClass:C", "CustomObject:O__c", "REFERENCES_OBJECT", "UNVERIFIED")]
        g = build_graph(entries, rels, RULES, "2026-10-13T20:00:00-03:00")
        self.assertEqual(g["generatedAt"], "2026-10-13T20:00:00-03:00")
        self.assertEqual([n["id"] for n in g["nodes"]], ["ApexClass:C", "ApexTrigger:T", "CustomObject:O__c"])
        self.assertEqual({(e["from"], e["to"], e["relationship"]) for e in g["edges"]},
                         {("ApexTrigger:T", "ApexClass:C", "INVOKES_CLASS"),
                          ("ApexTrigger:T", "CustomObject:O__c", "TRIGGERS_ON_OBJECT"),
                          ("CustomObject:O__c", "ApexTrigger:T", "HAS_TRIGGER")})
        self.assertEqual(len(g["unverifiedMentions"]), 1)
        self.assertEqual(g["referencesToComponentsWithoutJson"][0]["to"], "NamedCredential:NC")

    def test_empty_graph(self):
        g = build_graph([], [], RULES, "t")
        self.assertEqual((g["nodes"], g["edges"]), ([], []))
