"""Orquestra a descoberta: CSV -> JSON normalizado -> referências -> grafo -> clusters ->
propostas de nome -> relatório. Também registra a revisão humana de um cluster.

Saídas em `discovery/` (configurável em `config.json` -> `discovery.outputDir`):
- `graphs/graph.json`, `clusters/cluster-NNN.json`, `proposals/cluster-NNN.proposal.json`,
  `orphans/orphans.json`, `report/discovery-report.md`, `report/component-status.json`;
- `state/extraction-cache.json`: retomada — componente cujo JSON normalizado (sha256), lista de
  componentes do CSV e regras não mudaram não é reprocessado.

A revisão humana fica no próprio arquivo do cluster e é mantida nas execuções seguintes enquanto
a composição do cluster (assinatura) for a mesma. Nenhum dossiê é gerado nesta fase.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

from integration_discovery import cluster_builder, csv_loader, graph_builder, name_proposer
from integration_discovery import normalized_json_loader as loader
from integration_discovery import reference_extractor, report_generator
from integration_discovery.settings import DiscoverySettings

CACHE_VERSION = 1
DECISIONS = ("APPROVED", "REJECTED", "PENDING")


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _rel(path, root):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def _context_key(rules, components):
    """Muda quando as regras ou a lista de componentes do CSV mudam (invalida o cache inteiro)."""
    payload = json.dumps({"rules": rules, "targets": sorted(f"{c['componentType']}:{c['componentName']}"
                                                            for c in components)}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _entry_fingerprint(entry):
    return [entry["sha256"]] + [x["sha256"] for x in entry.get("extraSources") or []]


def _previous_reviews(clusters_dir):
    out = {}
    for p in sorted(Path(clusters_dir).glob("cluster-*.json")):
        c = _read_json(p) or {}
        review = c.get("humanReview") or {}
        if c.get("signature") and review.get("decision") not in (None, "PENDING"):
            out[c["signature"]] = {"clusterId": c.get("clusterId"), "status": c.get("status"),
                                   "humanReview": review, "approvedName": c.get("approvedName")}
    return out


def run_discovery(project_root, csv_path, alias=None, api_version=None, use_cache=True,
                  extractor=None, stream=None):
    """Executa a descoberta. Retorna (código de saída, resumo)."""
    say = (lambda m: print(m, file=stream)) if stream is not None else print
    settings = DiscoverySettings(project_root)
    out = settings.output_dir
    extractor = extractor or reference_extractor.extract_references
    generated_at = _now()
    csv_res = csv_loader.load_csv(csv_path)
    if csv_res.fatal:
        # Nada é sobrescrito: clusters, propostas e revisões anteriores ficam intactos.
        say(f"ERRO no CSV: {csv_res.fatal}. Nenhuma saída foi alterada.")
        return 2, {"fatal": csv_res.fatal}
    for e in csv_res.errors:
        say(f"CSV linha {e['line']}: {e['reason']} (ignorada)")
    for w in csv_res.warnings:
        say(f"CSV linha {w['line']}: {w['reason']}")
    components = csv_res.components
    entries = loader.load_all(settings, components, alias, api_version)
    suspect = {f"{c['componentType']}:{c['componentName']}": c["squadSuspect"] for c in components}
    for e in entries:
        e["squadSuspect"] = suspect.get(e["key"])
        if e["status"] != loader.FOUND:
            say(f"{e['key']}: {e['status']} ({e['expectedPath']})")

    # Referências (com cache para retomada)
    cache_path = out / "state" / "extraction-cache.json"
    ctx_key = _context_key(settings.rules, components)
    cache = _read_json(cache_path) if use_cache else None
    if not cache or cache.get("version") != CACHE_VERSION or cache.get("contextKey") != ctx_key:
        cache = {"version": CACHE_VERSION, "contextKey": ctx_key, "components": {}}
    targets = reference_extractor.build_targets(components)
    relations, hits, new_cache = [], 0, {}
    for e in entries:
        if e["status"] != loader.FOUND:
            continue
        fp = _entry_fingerprint(e)
        cached = cache["components"].get(e["key"])
        if cached and cached.get("fingerprint") == fp:
            rels = cached["relations"]
            hits += 1
        else:
            rels = extractor(e, targets, settings.rules)
        new_cache[e["key"]] = {"fingerprint": fp, "relations": rels}
        relations += rels
    _write_json(cache_path, {"version": CACHE_VERSION, "contextKey": ctx_key, "updatedAt": generated_at,
                             "components": new_cache})

    graph = graph_builder.build_graph(entries, relations, settings.rules, generated_at)
    clusters, orphans = cluster_builder.build_clusters(graph, settings.bridge_types)

    # Revisões anteriores: mantidas quando a composição (assinatura) é a mesma.
    previous = _previous_reviews(out / "clusters")
    applied = set()
    for c in clusters:
        prev = previous.get(c["signature"])
        if prev:
            c.update(status=prev["status"], humanReview=prev["humanReview"])
            if prev.get("approvedName"):
                c["approvedName"] = prev["approvedName"]
            applied.add(c["signature"])
    stale = [p for sig, p in previous.items() if sig not in applied]

    labels = {n["id"]: n.get("label") for n in graph["nodes"]}
    descriptions = {}
    for e in entries:
        apex = (e.get("data") or {}).get("apex") if e["status"] == loader.FOUND else None
        if isinstance(apex, dict) and isinstance(apex.get("description"), str):
            descriptions[e["key"]] = apex["description"]
    proposals = {c["clusterId"]: name_proposer.propose(c, labels, descriptions, settings.stopwords, orphans)
                 for c in clusters}
    for c in clusters:  # proposta acompanha a decisão já registrada
        if c["status"] != "CANDIDATE":
            proposals[c["clusterId"]]["status"] = c["status"]

    # Escrita (arquivos de execuções anteriores são substituídos)
    for d in ("clusters", "proposals"):
        for old in (out / d).glob("cluster-*.json"):
            old.unlink()
    _write_json(out / "graphs" / "graph.json", graph)
    for c in clusters:
        _write_json(out / "clusters" / f"{c['clusterId']}.json", c)
        _write_json(out / "proposals" / f"{c['clusterId']}.proposal.json", proposals[c["clusterId"]])
    node_by_id = {n["id"]: n for n in graph["nodes"]}
    _write_json(out / "orphans" / "orphans.json", {
        "generatedAt": generated_at, "status": "ORPHAN",
        "orphans": [{"id": o, "type": node_by_id[o]["type"], "name": node_by_id[o]["name"],
                     "normalizedJson": node_by_id[o]["normalizedJson"]} for o in orphans]})
    _write_json(out / "report" / "component-status.json", {
        "generatedAt": generated_at, "csv": csv_res.to_dict(),
        "components": [{"componentType": e["componentType"], "componentName": e["componentName"],
                        "status": e["status"], "expectedPath": e["expectedPath"],
                        **({"error": e["error"]} if e.get("error") else {})} for e in entries]})
    report = report_generator.generate_report({
        "csv": csv_res, "entries": entries, "graph": graph, "clusters": clusters, "proposals": proposals,
        "orphans": orphans, "csvPath": _rel(csv_path, settings.project_root),
        "inventoryDir": _rel(settings.inventory_dir(alias, api_version), settings.project_root),
        "cacheHits": hits})
    if stale:
        report += ("\n## 9. Revisões que não se aplicam mais\n\nA composição destes clusters mudou; "
                   "revise de novo:\n\n" + "\n".join(
                       f"- {p['clusterId']} (decisão anterior: {p['humanReview'].get('decision')})" for p in stale) + "\n")
    (out / "report").mkdir(parents=True, exist_ok=True)
    (out / "report" / "discovery-report.md").write_text(report, encoding="utf-8")

    summary = {"csvRows": csv_res.total_rows, "validComponents": len(components),
               "found": sum(1 for e in entries if e["status"] == loader.FOUND),
               "notFound": sum(1 for e in entries if e["status"] != loader.FOUND),
               "relations": len(cluster_builder.unique_relations(graph["edges"])),
               "evidences": len([e for e in graph["edges"] if not e.get("inverseOf")]),
               "clusters": len(clusters), "orphans": len(orphans), "cacheHits": hits,
               "csvErrors": len(csv_res.errors), "report": _rel(out / "report" / "discovery-report.md",
                                                                settings.project_root)}
    say(f"Descoberta concluída: {summary['clusters']} cluster(s) candidato(s), {summary['orphans']} órfão(s), "
        f"{summary['relations']} relação(ões); relatório em {summary['report']}")
    return 0, summary


def review_cluster(project_root, cluster_id, decision, reviewed_by=None, notes=None, name=None, stream=None):
    """Registra a decisão humana no arquivo do cluster (e na proposta)."""
    say = (lambda m: print(m, file=stream)) if stream is not None else print
    settings = DiscoverySettings(project_root)
    decision = str(decision).upper()
    if decision not in DECISIONS:
        raise ValueError(f"decisão deve ser uma de {', '.join(DECISIONS)}")
    if decision != "PENDING" and not reviewed_by:
        raise ValueError("--by é obrigatório para APPROVED/REJECTED")
    path = settings.output_dir / "clusters" / f"{cluster_id}.json"
    cluster = _read_json(path)
    if cluster is None:
        raise ValueError(f"cluster não encontrado: {path}")
    cluster["humanReview"] = {"decision": decision, "reviewedBy": reviewed_by if decision != "PENDING" else None,
                              "notes": notes, "reviewedAt": _now() if decision != "PENDING" else None}
    cluster["status"] = {"APPROVED": "APPROVED", "REJECTED": "REJECTED"}.get(decision, "CANDIDATE")
    if decision == "APPROVED":
        cluster["approvedName"] = name or cluster.get("proposedName")
    else:
        cluster.pop("approvedName", None)
    _write_json(path, cluster)
    ppath = settings.output_dir / "proposals" / f"{cluster_id}.proposal.json"
    proposal = _read_json(ppath)
    if proposal is not None:
        proposal["status"] = cluster["status"]
        _write_json(ppath, proposal)
    say(f"{cluster_id}: {cluster['status']}" + (f" — nome aprovado: {cluster['approvedName']}"
                                                  if decision == "APPROVED" else ""))
    return cluster
