"""Orquestra a descoberta: CSV -> JSON normalizado -> referências -> grafo -> clusters ->
propostas de nome -> relatório. Também registra a revisão humana de um cluster.

Saídas em `discovery/` (configurável em `config.json` -> `discovery.outputDir`):
- `graphs/graph.json`, `clusters/cluster-NNN.json`, `proposals/cluster-NNN.proposal.json`,
  `orphans/orphans.json`, `report/discovery-report.md`, `report/component-status.json`;
- `state/extraction-cache.json`: retomada — componente cujo JSON normalizado (sha256), lista de
  componentes do CSV e regras não mudaram não é reprocessado;
- `state/cluster-registry.json`: número estável por composição (assinatura) e histórico das
  revisões humanas (ver `cluster_registry.py`).

O `review` confere o número no registro: número aposentado (composição mudou) é recusado, para
que uma decisão nunca caia em outro cluster. Nenhum dossiê é gerado nesta fase.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

from integration_discovery import cluster_builder, csv_loader, graph_builder, name_proposer
from integration_discovery import normalized_json_loader as loader
from integration_discovery import reference_extractor, report_generator
from integration_discovery.cluster_registry import RETIRED, ClusterRegistry
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


def _registry(out):
    """Registro de números e revisões. Na primeira vez, migra os arquivos de cluster gerados antes
    dele (mesmo número e mesma decisão para a mesma composição)."""
    path = out / "state" / "cluster-registry.json"
    registry = ClusterRegistry(path)
    if not path.is_file():
        for p in sorted((out / "clusters").glob("cluster-*.json")):
            c = _read_json(p) or {}
            if not c.get("signature") or not c.get("clusterId"):
                continue
            registry.seed(c["signature"], c["clusterId"], [x["id"] for x in c.get("components") or []])
            review = c.get("humanReview") or {}
            if review.get("decision") not in (None, "PENDING"):
                registry.add_review(c["signature"], c["clusterId"], review, c.get("approvedName"))
    return registry


def _apply_review(cluster, review):
    decision = (review or {}).get("decision") or "PENDING"
    cluster["humanReview"] = {"decision": decision, "reviewedBy": (review or {}).get("reviewedBy"),
                              "notes": (review or {}).get("notes"), "reviewedAt": (review or {}).get("reviewedAt")}
    cluster["status"] = {"APPROVED": "APPROVED", "REJECTED": "REJECTED"}.get(decision, "CANDIDATE")
    if decision == "APPROVED":
        cluster["approvedName"] = (review or {}).get("approvedName") or cluster.get("proposedName")
    else:
        cluster.pop("approvedName", None)


def _same_name_relations(entries, pairs):
    """Mesmo fullName em dois tipos do CSV que formam um só componente no Utilitário 1 (ex.: Flow e
    FlowDefinition, relação SAME_FULL_NAME do metadata-types-mvp.json): evidência de manifesto."""
    found = {(e["componentType"], e["componentName"].lower()): e for e in entries if e["status"] == loader.FOUND}
    out = []
    for pair in pairs:
        for (t, name), src in sorted(found.items()):
            dst = found.get((pair["to"], name)) if t == pair["from"] else None
            if dst:
                out.append({"from": src["key"], "to": dst["key"], "relationship": pair["relationship"],
                            "evidence": reference_extractor.MANIFEST, "sourceFile": dst["path"],
                            "sourceField": "fullName", "jsonPath": "fullName",
                            "matchedText": dst["componentName"], "line": None})
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
    relations += _same_name_relations(entries, settings.same_name_pairs)
    _write_json(cache_path, {"version": CACHE_VERSION, "contextKey": ctx_key, "updatedAt": generated_at,
                             "components": new_cache})

    graph = graph_builder.build_graph(entries, relations, settings.rules, generated_at)
    clusters, orphans = cluster_builder.build_clusters(graph, settings.bridge_types)

    # Números estáveis por composição e decisões vigentes (histórico em state/cluster-registry.json).
    registry = _registry(out)
    registry.assign(clusters, generated_at)
    for c in clusters:
        review = registry.latest_review(c["signature"])
        if review and review.get("decision") not in (None, "PENDING"):
            _apply_review(c, review)
    stale = registry.stale_reviews({c["clusterId"] for c in clusters if c["status"] != "CANDIDATE"})
    registry.save()

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
                        "relatedSources": [{"component": f"{x.get('metadataType')}:{x['fullName']}", "path": x["path"],
                                            **(x.get("link") or {})} for x in e.get("extraSources") or []],
                        **({"error": e["error"]} if e.get("error") else {})} for e in entries]})
    report = report_generator.generate_report({
        "csv": csv_res, "entries": entries, "graph": graph, "clusters": clusters, "proposals": proposals,
        "orphans": orphans, "csvPath": _rel(csv_path, settings.project_root),
        "inventoryDir": _rel(settings.inventory_dir(alias, api_version), settings.project_root),
        "cacheHits": hits})
    if stale:
        report += ("\n## 9. Revisões que não se aplicam mais\n\nA composição destes clusters mudou e o número "
                   "foi aposentado (nunca é reutilizado). Revise os clusters que receberam os componentes:\n\n"
                   + "\n".join(f"- {p['clusterId']} (decisão anterior: {p['decision']}"
                                + (f" por {p['reviewedBy']}" if p.get("reviewedBy") else "")
                                + (f"; nota: {p['notes']}" if p.get("notes") else "") + ") → componentes agora em: "
                                + (", ".join(p["successors"]) or "nenhum cluster") for p in stale) + "\n")
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


def review_cluster(project_root, cluster_id, decision, reviewed_by=None, notes=None, name=None, stream=None,
                   signature=None):
    """Registra a decisão humana no histórico (registro) e no arquivo do cluster e da proposta.

    O número é conferido no registro: número aposentado (composição mudou) ou inexistente é
    recusado; `signature`, se informada, precisa ser a da composição atual do número."""
    say = (lambda m: print(m, file=stream)) if stream is not None else print
    settings = DiscoverySettings(project_root)
    decision = str(decision).upper()
    if decision not in DECISIONS:
        raise ValueError(f"decisão deve ser uma de {', '.join(DECISIONS)}")
    if decision != "PENDING" and not reviewed_by:
        raise ValueError("--by é obrigatório para APPROVED/REJECTED")
    registry = _registry(settings.output_dir)
    sig, entry = registry.find(cluster_id)
    if entry is None:
        raise ValueError(f"{cluster_id} não existe (rode a descoberta e confira o relatório)")
    if entry.get("status") == RETIRED:
        succ = ", ".join(entry.get("successors") or []) or "nenhum cluster atual"
        raise ValueError(f"{cluster_id} não existe mais (a composição mudou); os componentes dele agora estão em: "
                         f"{succ}. Nenhuma decisão foi registrada.")
    if signature and signature != sig:
        raise ValueError(f"assinatura informada ({signature}) não é a de {cluster_id} ({sig}); "
                         "o cluster mudou desde o relatório lido. Nenhuma decisão foi registrada.")
    path = settings.output_dir / "clusters" / f"{cluster_id}.json"
    cluster = _read_json(path)
    if cluster is None or cluster.get("signature") != sig:
        raise ValueError(f"arquivo {path} ausente ou de outra composição; rode a descoberta de novo")
    review = {"decision": decision, "reviewedBy": reviewed_by if decision != "PENDING" else None,
              "notes": notes, "reviewedAt": _now()}
    approved = (name or cluster.get("proposedName")) if decision == "APPROVED" else None
    registry.add_review(sig, cluster_id, review, approved)
    registry.save()
    _apply_review(cluster, dict(review, approvedName=approved))
    _write_json(path, cluster)
    ppath = settings.output_dir / "proposals" / f"{cluster_id}.proposal.json"
    proposal = _read_json(ppath)
    if proposal is not None:
        proposal["status"] = cluster["status"]
        _write_json(ppath, proposal)
    say(f"{cluster_id}: {cluster['status']}" + (f" — nome aprovado: {cluster['approvedName']}"
                                                  if decision == "APPROVED" else ""))
    return cluster
