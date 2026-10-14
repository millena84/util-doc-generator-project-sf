"""Relatório Markdown da descoberta (`discovery/report/discovery-report.md`).

Só nomes de componentes, tipos, caminhos JSON e o texto casado (o próprio nome). Nenhum valor
do normalizado é copiado para o relatório.
"""

from __future__ import annotations


def _cell(v):
    return str(v if v not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")


def _table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return out if rows else out + ["| " + " | ".join(["—"] * len(headers)) + " |"]


def generate_report(ctx):
    csv_res, entries, graph = ctx["csv"], ctx["entries"], ctx["graph"]
    clusters, proposals, orphans = ctx["clusters"], ctx["proposals"], ctx["orphans"]
    found = [e for e in entries if e["status"] == "FOUND"]
    missing = [e for e in entries if e["status"] != "FOUND"]
    direct = [e for e in graph["edges"] if not e.get("inverseOf")]
    L = ["# Relatório de descoberta de integrações", "",
         f"- Gerado em: {graph['generatedAt']}",
         f"- CSV: `{ctx['csvPath']}`",
         f"- Inventário lido: `{ctx['inventoryDir']}` (somente `normalized/*.json`)",
         f"- Extrações reaproveitadas do cache (JSON inalterado): {ctx['cacheHits']} de {len(found)}",
         "",
         "> Todos os clusters são **CANDIDATE** e todos os nomes são **PROPOSTA** até a revisão humana "
         "(`python -m integration_discovery review`). Nenhum dossiê é gerado nesta fase.", "",
         "## 1. Resumo", ""]
    L += _table(["Item", "Total"], [
        ["Linhas no CSV (sem cabeçalho)", csv_res.total_rows],
        ["Componentes válidos (após validação e deduplicação)", len(csv_res.components)],
        ["Componentes com JSON encontrado", len(found)],
        ["Componentes sem JSON ou com JSON inválido", len(missing)],
        ["Relações confirmadas distintas (de, para, relação; sem inversas)",
         len({(e["from"], e["to"], e["relationship"]) for e in direct})],
        ["Evidências dessas relações (campos JSON onde o nome foi achado)", len(direct)],
        ["Menções não verificadas (fora do grafo)", len(graph["unverifiedMentions"])],
        ["Clusters candidatos", len(clusters)],
        ["Órfãos", len(orphans)],
    ])
    L += ["", "## 2. Componentes sem JSON normalizado", ""]
    L += _table(["Componente", "Status", "Caminho esperado", "Detalhe"],
                [[e["key"], e["status"], f"`{e['expectedPath']}`", e.get("error")] for e in missing])
    L += ["", "## 3. Clusters (ordenados por número de evidências)", ""]
    L += _table(["Cluster", "Evidências", "Relações", "Confiança", "Componentes", "Nome proposto", "Revisão"],
                [[c["clusterId"], c["evidenceCount"], c["relationCount"], c["confidence"],
                  ", ".join(x["id"] for x in c["components"]), c["proposedName"],
                  c["humanReview"]["decision"]] for c in clusters])
    for c in clusters:
        p = proposals.get(c["clusterId"]) or {}
        L += ["", f"### {c['clusterId']} — {c['proposedName']} (PROPOSTA)", "",
              f"- Status: `{c['status']}` · confiança `{c['confidence']}` · assinatura `{c['signature']}`",
              f"- Alternativas: {', '.join(c['alternativeNames']) or '—'}",
              f"- Pontes (entram em mais de um cluster quando ligadas a vários): "
              f"{', '.join(x['id'] for x in c['components'] if x['bridge']) or '—'}", ""]
        L += _table(["De", "Relação", "Para", "Evidência", "Campo (JSON)", "Texto casado"],
                    [[e["from"], e["relationship"] + (" (inversa)" if e.get("inverseOf") else ""), e["to"],
                      e["evidence"], f"`{e['jsonPath']}`", f"`{e['matchedText']}`"] for e in c["relationships"]])
        if p.get("rationale"):
            L += ["", "Justificativa do nome:", ""] + [f"- {r}" for r in p["rationale"]]
        if c["orphanComponents"]:
            L += ["", "Possíveis membros sem relação confirmada (só convenção de nome): "
                  + ", ".join(o["id"] for o in c["orphanComponents"])]
    L += ["", "## 4. Órfãos (sem relação confirmada)", ""]
    L += _table(["Componente"], [[o] for o in orphans])
    L += ["", "## 5. Menções não verificadas (não entram no grafo)", ""]
    L += _table(["De", "Para", "Campo (JSON)", "Texto casado", "Motivo"],
                [[m["from"], m["to"], f"`{m['jsonPath']}`", f"`{m['matchedText']}`",
                  m.get("ambiguity") or "texto livre (comentário/descrição)"] for m in graph["unverifiedMentions"]])
    L += ["", "## 6. Referências a componentes do CSV sem JSON (não entram no grafo)", ""]
    L += _table(["De", "Para", "Relação", "Campo (JSON)"],
                [[m["from"], m["to"], m["relationship"], f"`{m['jsonPath']}`"]
                 for m in graph["referencesToComponentsWithoutJson"]])
    L += ["", "## 7. Erros e avisos de validação do CSV", ""]
    if csv_res.fatal:
        L += [f"- **Erro que impediu a leitura:** {csv_res.fatal}"]
    L += _table(["Linha", "Tipo", "Motivo"],
                [[e["line"], "erro (linha ignorada)", e["reason"]] for e in csv_res.errors]
                + [[w["line"], "aviso", w["reason"]] for w in csv_res.warnings])
    L += ["", "## 8. Pendências e dúvidas", ""]
    pend = []
    if missing:
        pend.append(f"{len(missing)} componente(s) sem JSON normalizado: rode o Utilitário 1 para eles "
                    "(`bin/sf-docs.sh run --group <Grupo> --component <nome>`) ou corrija tipo/nome no CSV.")
    if graph["unverifiedMentions"]:
        pend.append("Menções não verificadas: confirmar manualmente; não foram usadas nos clusters.")
    if orphans:
        pend.append("Órfãos: confirmar se pertencem a alguma integração (ligação pode estar em componente "
                    "fora do CSV ou em código que o normalizado não guarda, como `callout:` em Apex).")
    low = [c["clusterId"] for c in clusters if c["confidence"] == "LOW"]
    if low:
        pend.append(f"Clusters com confiança LOW: {', '.join(low)} — revisar antes de aprovar.")
    pend.append("O normalizado do Utilitário 1 não guarda o corpo do código Apex: chamadas `callout:<NamedCredential>` "
                "só aparecem se estiverem em outro campo (ex.: Custom Metadata). Relação ausente não prova ausência.")
    L += [f"- {p}" for p in pend]
    return "\n".join(L) + "\n"
