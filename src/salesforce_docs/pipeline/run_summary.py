"""Resumo auditável da execução: runs/<runId>/resumo.md (gerado também em falha).

Só usa o run state (já mascarado) e a configuração; nunca lê raws/XMLs. O texto final
passa novamente pelo Masker antes de ser gravado.
"""

from __future__ import annotations

from salesforce_docs.utils import rel, write_text

STATUS_MEANING = {
    "SUCCESS": "concluída; cobertura sem lacunas bloqueantes",
    "COMPLETED_WITH_GAPS": "concluída sem falhas de componente, mas a documentação NÃO está completa",
    "PARTIAL_SUCCESS": "concluída com falha em parte dos componentes",
    "FAILED": "falha (global ou de todos os componentes)",
    "INTERRUPTED": "interrompida (sessão expirada); retome com --resume",
    "IN_PROGRESS": "não finalizada",
}


def _lst(values, limit=30):
    values = list(values or [])
    if not values:
        return "—"
    shown = ", ".join(f"`{v}`" for v in values[:limit])
    return shown + (f" … (+{len(values) - limit})" if len(values) > limit else "")


def build_summary(pipeline, state) -> str:
    d = state.data
    cov = d.get("coverage") or {}
    types = cov.get("types") or {}
    gaps = cov.get("gaps") or {}
    sel = d.get("selection") or {}
    approval = d.get("orgApproval") or {}
    detected = approval.get("detected") or {}
    session = d.get("session") or {}
    prim = [c for c in d.get("components") or [] if c.get("role") == "primary"]
    documented = [f"{c['metadataType']}:{c['component']}" for c in prim
                  if c.get("status") == "SUCCESS" and c.get("document")]
    failed = [f"{c['metadataType']}:{c['component']} ({c.get('status')}"
              f"{', ' + c['errorClass'] if c.get('errorClass') else ''})" for c in prim
              if c.get("status") not in ("SUCCESS", "NO_TEMPLATE")]
    lines = [
        f"# Resumo da execução `{d.get('runId')}`",
        "",
        f"- **Status:** `{d.get('status')}` — {STATUS_MEANING.get(d.get('status'), '')}",
        f"- **Cobertura:** `{cov.get('status')}` — {cov.get('documented', 0)} documentada(s) de "
        f"{cov.get('inScope', 0)} no escopo; lacunas bloqueantes {cov.get('blockingGapCount', 0)}, "
        f"avisos {cov.get('warningCount', 0)}",
        f"- **Início/fim:** {d.get('startedAt')} → {d.get('finishedAt') or '—'}",
    ]
    if d.get("failure"):
        f = d["failure"]
        lines.append(f"- **Falha global:** `{f.get('code')}` — {f.get('message')}"
                     + (f" (sugestão: {f.get('suggestion')})" if f.get("suggestion") else ""))
    if d.get("resumedFrom"):
        lines.append(f"- **Retomada de:** `{d['resumedFrom']}`")
    source = d.get("source")
    if source:  # modo pasta: nada é lido da org
        lines += [
            "",
            "## Origem (modo pasta, sem login)",
            "",
            f"- Repositório: `{source.get('folder')}` → org **{source.get('orgName')}** "
            "(de-para em config.json sourceRepositories)",
            f"- Pasta lida: `{source.get('path')}` (metadata em `{source.get('metadataPath')}`); "
            f"formato `{source.get('format')}`; {source.get('files')} arquivo(s) reconhecido(s)",
            f"- Registro do que foi lido (caminho e sha256): `{source.get('manifest') or '—'}`",
            f"- Alias das pastas de saída: `{sel.get('orgAlias') or d.get('orgAlias')}`",
            f"- API version: `{d.get('apiVersion') or '—'}`",
            "- Não feitos (exigem a org): dados internos (passo 9) e describeValueType (passo 5)",
        ]
        if source.get("unmappedFolders"):
            lines.append(f"- Pastas sem metadata type configurado (não documentadas): "
                         f"{_lst(source['unmappedFolders'])}")
        for folder, count in sorted((source.get("ignoredFiles") or {}).items()):
            lines.append(f"- Arquivos não reconhecidos em `{folder}/`: {count}")
        for problem in source.get("problems") or []:
            lines.append(f"- Aviso: {problem}")
    else:
        lines += [
            "",
            "## Org-alvo",
            "",
            f"- Alias: `{sel.get('orgAlias') or d.get('orgAlias')}` (origem: {sel.get('orgAliasSource', '—')})",
            f"- Org ID: `{detected.get('orgId') or session.get('orgId') or '—'}`",
            f"- Usuário: `{detected.get('username') or session.get('username') or '—'}`",
            f"- Instance URL: `{detected.get('instanceUrl') or session.get('instanceUrl') or '—'}`",
            f"- Aprovação: {'aprovada' if approval.get('approved') else 'NÃO aprovada'} "
            f"({approval.get('method', '—')})",
            f"- Token obtido via: {d.get('tokenSource', '—')} (nunca persistido)",
            f"- API version: `{d.get('apiVersion') or '—'}`",
        ]
    lines += [
        "",
        "## Seleção",
        "",
        f"- Modo: `{sel.get('mode', '—')}`",
        f"- Pedida (config.json): `{sel.get('requested')}`",
        f"- CLI: `{sel.get('cli')}`",
        f"- Efetiva: `{sel.get('effective')}`",
        "",
        "## Metadata types",
        "",
        "| Categoria | Qtde | Tipos |",
        "|---|---|---|",
    ]
    disc = types.get("discovered") or {}
    rows = [
        ("Descobertos no repositório" if source else "Descobertos na org",
         disc.get("count") if disc.get("available") else "não listado", None),
        ("Descobertos e não configurados", len(types.get("discoveredNotConfigured") or []),
         types.get("discoveredNotConfigured")),
        ("Configurados", len(types.get("configured") or []), types.get("configured")),
        ("Selecionados (grupos efetivos)", len(sel.get("effective") or {}), list((sel.get("effective") or {}))),
        ("Não selecionados (fora da seleção)", len((types.get("excluded") or {}).get("outOfScope") or []),
         (types.get("excluded") or {}).get("outOfScope")),
        ("Excluídos por configuração", len((types.get("excluded") or {}).get("byConfig") or []),
         (types.get("excluded") or {}).get("byConfig")),
        ("Não habilitados na org", len((types.get("excluded") or {}).get("notEnabledInOrg") or []),
         (types.get("excluded") or {}).get("notEnabledInOrg")),
        ("Processados", len(types.get("processed") or []), types.get("processed")),
        ("Documentados", len(types.get("documented") or []), types.get("documented")),
        ("Documentados como relacionados", len(types.get("documentedAsRelated") or []),
         types.get("documentedAsRelated")),
        ("Sem modelo/contrato", len(types.get("withoutModel") or []), types.get("withoutModel")),
    ]
    for label, qty, values in rows:
        lines.append(f"| {label} | {qty} | {_lst(values) if values is not None else '—'} |")
    ignored = d.get("ignoredByFilter") or {}
    not_selected = d.get("notSelected") or {}
    progress = d.get("progress") or {}
    subdocs = ["{} ({})".format(x.get("component"), x.get("status")) for x in gaps.get("subDocuments") or []]
    not_found = ["{}:{}".format(n.get("metadataType"), n.get("component")) for n in gaps.get("notFound") or []]
    ignored_txt = ["{}: {}".format(g, v.get("count")) for g, v in ignored.items()]
    not_selected_txt = ["{}: {}".format(g, v.get("count")) for g, v in not_selected.items()]
    lines += [
        "",
        "## Componentes",
        "",
        f"- Documentados ({len(documented)}): {_lst(documented)}",
        f"- Sem modelo/contrato ({len(gaps.get('noTemplate') or [])}): {_lst(gaps.get('noTemplate'))}",
        f"- Subdocumentos não gerados ({len(subdocs)}): {_lst(subdocs)}",
        f"- Com falha ({len(failed)}): {_lst(failed)}",
        f"- Não encontrados ({len(not_found)}): {_lst(not_found)}",
        f"- Ignorados por componentFilter: {_lst(ignored_txt)}",
        f"- Não selecionados (dentro de grupos selecionados): {_lst(not_selected_txt)}",
        f"- Relacionados não verificados: {_lst(gaps.get('relatedNotResolved'))}",
        f"- Dados internos indisponíveis: {_lst(gaps.get('internalDataUnavailable'))}",
        f"- Progresso: {progress.get('completed', 0)}/{progress.get('planned', 0)}; pendentes: "
        f"{_lst(progress.get('pending'))}",
    ]
    metrics = d.get("metrics") or {}
    if metrics.get("byMetadataType"):
        lines += ["", "## Chamadas à CLI", "",
                  f"Total: {metrics.get('commands')} comando(s), {metrics.get('totalSeconds')} s; "
                  f"timeout por comando {metrics.get('timeoutSeconds')} s; retries {metrics.get('retries')}.",
                  "", "| Metadata type | Chamadas | Segundos | Falhas |", "|---|---|---|---|"]
        for mtype, m in sorted(metrics["byMetadataType"].items()):
            lines.append(f"| {mtype} | {m['calls']} | {m['seconds']} | {m['failures']} |")
    out = d.get("output") or {}
    guard = d.get("gitGuard") or {}
    lines += [
        "",
        "## Saída e proteção",
        "",
        f"- Documentos: `{out.get('dir', '—')}` (layout {out.get('layout', '—')}); "
        f"substituídos {len(out.get('replaced') or [])}; colisões {len(out.get('collisions') or [])}",
    ] + _output_notes(d, out) + [
        f"- Git: {'verificado' if guard.get('available') else 'verificação indisponível'}"
        f"{'; rastreados sensíveis: ' + str(len(guard.get('tracked') or [])) if guard.get('available') else ''}",
        f"- Run state: `{rel(state.path, pipeline.root)}`",
        "",
    ]
    return pipeline.masker("\n".join(lines))


def _output_notes(d, out):
    """Orientação sobre a pasta de saída: retomada, defasagem entre dias e conflito de org."""
    notes = []
    if out.get("resumeNote"):
        notes.append(f"- Retomada/regeneração: {out['resumeNote']}")
    if out.get("resumeAgeWarning"):
        notes.append(f"- **Atenção:** {out['resumeAgeWarning']}")
    conflict = out.get("orgFolderConflict")
    if conflict:
        notes.append(f"- **Atenção:** `{conflict['folder']}` pertence à org {conflict['owner']}; "
                     "esta execução usou uma pasta separada (orgs diferentes nunca compartilham pasta)")
    days = {}
    for c in d.get("components") or []:
        if c.get("role") == "primary" and c.get("processedOn"):
            days[c["processedOn"]] = days.get(c["processedOn"], 0) + 1
    if len(days) > 1:
        notes.append("- Componentes por dia de processamento: "
                     + "; ".join(f"{day}: {n}" for day, n in sorted(days.items())))
    return notes


def write_summary(pipeline, state, p=None):
    path = pipeline.app.runs_dir / state.run_id / "resumo.md"
    write_text(path, build_summary(pipeline, state))
    state.data["summary"] = rel(path, pipeline.root)
    state.save()
    return path
