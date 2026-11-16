"""Grafo direcionado: nó = componente do CSV com JSON normalizado encontrado; aresta = referência
confirmada (evidência diferente de UNVERIFIED) entre dois nós.

Arestas inversas declaradas em `inverseRelationships` (ex.: TRIGGERS_ON_OBJECT -> HAS_TRIGGER)
são a mesma evidência lida no sentido contrário; levam `inverseOf` e o arquivo de origem.
"""

from __future__ import annotations

from integration_discovery.reference_extractor import UNVERIFIED


def build_graph(entries, relations, rules, generated_at):
    nodes = [{"id": e["key"], "type": e["componentType"], "name": e["componentName"],
              "label": e.get("label"), "normalizedJson": e["path"], "sha256": e["sha256"],
              "squadSuspect": e.get("squadSuspect")}
             for e in entries if e["status"] == "FOUND"]
    ids = {n["id"] for n in nodes}
    edges, unverified, outside = [], [], []
    inverse = rules.get("inverseRelationships") or {}
    for r in relations:
        if r["evidence"] == UNVERIFIED:
            unverified.append(r)
        elif r["to"] not in ids:
            outside.append(r)  # destino está no CSV, mas sem JSON normalizado
        else:
            edges.append(r)
            if r["relationship"] in inverse:
                edges.append(dict(r, **{"from": r["to"], "to": r["from"],
                                        "relationship": inverse[r["relationship"]],
                                        "inverseOf": r["relationship"]}))
    edges.sort(key=lambda e: (e["from"], e["to"], e["relationship"], e["jsonPath"]))
    return {"generatedAt": generated_at, "nodes": sorted(nodes, key=lambda n: n["id"]), "edges": edges,
            "unverifiedMentions": unverified, "referencesToComponentsWithoutJson": outside}
