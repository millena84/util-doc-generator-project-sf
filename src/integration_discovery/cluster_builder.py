"""Agrupa componentes ligados (direta ou indiretamente) em clusters CANDIDATE.

- Ligação = aresta confirmada do grafo, em qualquer sentido.
- Tipos ponte (`discovery.bridgeTypes`, padrão PermissionSet) não unem clusters: os demais
  componentes formam os grupos e cada ponte entra em todo cluster com que se liga. Assim um
  componente pode estar em mais de um cluster, e um permission set que libera classes de duas
  integrações não as funde sem evidência.
- Nó sem nenhuma aresta confirmada é órfão (ORPHAN).
- `orphanComponents` de um cluster: órfãos cujo nome compartilha o prefixo dominante do
  cluster — só dica de convenção de nome (NAMING_CONVENTION), nunca relação.
- Confiança (relações distintas, sem inversas): HIGH (>= 3 relações, alguma CODE_REFERENCE e um componente de endpoint/app),
  MEDIUM (>= 2 relações, ou 1 relação com componente de endpoint/app), LOW (demais).
"""

from __future__ import annotations

import hashlib

ENDPOINT_TYPES = {"NamedCredential", "ExternalCredential", "ConnectedApp", "ExternalClientApp",
                  "RemoteSiteSetting", "Certificate", "SelfSignedCertificate"}


def _components(nodes, adj, bridges):
    seen, groups = set(), []
    for n in sorted(nodes):
        if n in seen or n in bridges or not adj.get(n):
            continue
        stack, group = [n], set()
        while stack:
            cur = stack.pop()
            if cur in group:
                continue
            group.add(cur)
            stack.extend(x for x in adj.get(cur, ()) if x not in bridges and x not in group)
        seen |= group
        groups.append(group)
    return groups


def signature(members):
    return hashlib.sha256("\n".join(sorted(members)).encode("utf-8")).hexdigest()[:16]


def unique_relations(edges):
    """Relações distintas (de, para, relação), sem as inversas; a mesma relação achada em vários
    campos conta uma vez (as evidências ficam todas registradas)."""
    return {(e["from"], e["to"], e["relationship"]) for e in edges if not e.get("inverseOf")}


def confidence(members, edges):
    types = {m.split(":", 1)[0] for m in members}
    has_endpoint = bool(types & ENDPOINT_TYPES)
    has_code = any(e["evidence"] == "CODE_REFERENCE" for e in edges)
    direct = unique_relations(edges)
    if len(direct) >= 3 and has_code and has_endpoint:
        return "HIGH"
    if len(direct) >= 2 or (len(direct) == 1 and has_endpoint):
        return "MEDIUM"
    return "LOW"


def build_clusters(graph, bridge_types):
    node_type = {n["id"]: n["type"] for n in graph["nodes"]}
    bridges = {n for n, t in node_type.items() if t in set(bridge_types)}
    adj = {}
    for e in graph["edges"]:
        adj.setdefault(e["from"], set()).add(e["to"])
        adj.setdefault(e["to"], set()).add(e["from"])
    groups = _components(node_type, adj, bridges)
    # Pontes ligadas só entre si (ou a nada fora das pontes) formam o próprio grupo.
    covered = set().union(*groups) if groups else set()
    for b in sorted(bridges):
        if adj.get(b) and not any(x not in bridges for x in adj[b]) and b not in covered:
            group = {b} | {x for x in adj[b]}
            covered |= group
            groups.append(group)
    clusters = []
    for group in groups:
        members = set(group) | {b for b in bridges if adj.get(b, set()) & group}
        edges = [e for e in graph["edges"] if e["from"] in members and e["to"] in members]
        clusters.append({"members": members, "edges": edges})
    in_cluster = set().union(*(c["members"] for c in clusters)) if clusters else set()
    orphans = sorted(n for n in node_type if n not in in_cluster)
    clusters.sort(key=lambda c: (-len([e for e in c["edges"] if not e.get("inverseOf")]), sorted(c["members"])[0]))
    out = []
    for i, c in enumerate(clusters, start=1):
        members = sorted(c["members"])
        out.append({
            "clusterId": f"cluster-{i:03d}",
            "status": "CANDIDATE",
            "signature": signature(members),
            "components": [{"id": m, "type": node_type[m], "bridge": m in bridges} for m in members],
            "relationships": c["edges"],
            "relationCount": len(unique_relations(c["edges"])),
            "evidenceCount": len([e for e in c["edges"] if not e.get("inverseOf")]),
            "orphanComponents": [],
            "confidence": confidence(members, c["edges"]),
            "proposedName": None,
            "alternativeNames": [],
            "humanReview": {"decision": "PENDING", "reviewedBy": None, "notes": None},
        })
    return out, orphans
