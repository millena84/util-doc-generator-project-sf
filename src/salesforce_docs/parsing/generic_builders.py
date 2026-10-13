"""Builders genéricos referenciados pelos contratos (tabelas e blocos).

Um builder de tabela retorna lista de dicts {placeholder: valor}.
Um builder de bloco retorna texto Markdown.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from salesforce_docs import status as st
from salesforce_docs.parsing.xml_parser import as_list
from salesforce_docs.rendering.context import format_value, resolve


def _columns(ctx, columns: dict, fmt_map=None):
    row = {}
    for placeholder, path in columns.items():
        value, state = resolve(ctx, path)
        row[placeholder] = (format_value(value, (fmt_map or {}).get(placeholder), ctx.sensitive), state)
    return row


def related_components(ctx, args):
    """Componentes relacionados encontrados (tipo + fullName)."""
    include = set(args.get("types") or [])
    exclude = set(args.get("excludeTypes") or [])
    rows = []
    for r in sorted(ctx.related, key=lambda r: (r["metadataType"], r["fullName"])):
        if include and r["metadataType"] not in include:
            continue
        if r["metadataType"] in exclude:
            continue
        rows.append({"related_component": r["fullName"], "related_type": r["metadataType"]})
    if not rows and ctx.unresolved_related - exclude:
        # Relacionados existem mas não foram verificados (seleção restrita): não é "Não aplicável".
        return [{"related_component": st.NOT_INFORMED, "related_type": st.NOT_INFORMED}]
    return rows


def related_rows(ctx, args):
    """Uma linha por componente relacionado de `metadataType`, colunas por path."""
    rows = []
    for r in sorted(ctx.related_of(args["metadataType"]), key=lambda r: r["fullName"]):
        rctx = ctx.child(r.get("data") or {}, full_name=r["fullName"],
                         schema_fields=r.get("schemaFields"), metadata_type=r["metadataType"])
        rows.append(_columns(rctx, args["columns"], args.get("formats")))
    return rows


def matches_conditions(item, conditions):
    """Filtro `where`: lista de {path, equals|in|notIn|present|contains} avaliada sobre o item.

    `contains`: o valor no caminho é uma lista que contém o texto (sem diferenciar maiúsculas).
    """
    for cond in conditions or []:
        cur = item
        for part in cond["path"].split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if "equals" in cond and cur != cond["equals"]:
            return False
        if "in" in cond and cur not in cond["in"]:
            return False
        if "notIn" in cond and cur in cond["notIn"]:
            return False
        if "present" in cond and (cur not in (None, "", [], {})) != bool(cond["present"]):
            return False
        if "contains" in cond:
            wanted = str(cond["contains"]).lower()
            if not isinstance(cur, list) or wanted not in [str(v).lower() for v in cur]:
                return False
    return True


def path_rows(ctx, args):
    """Uma linha por item da lista em `path` do XML (opcionalmente filtrada por `where`)."""
    value, _ = resolve(ctx, args["path"])
    rows = []
    for item in as_list(value):
        if not isinstance(item, dict) or not matches_conditions(item, args.get("where")):
            continue
        rows.append(_columns(ctx.child(item), args["columns"], args.get("formats")))
    return rows


def child_properties(ctx, args):
    """Propriedade/valor dos filhos diretos de um elemento (ex.: oauthConfig).

    `allow` (opcional) restringe às propriedades aprovadas; as demais e as sensíveis
    são omitidas do Markdown e registradas no estado da execução.
    """
    value, _ = resolve(ctx, args["path"])
    rows = []
    key_ph = args.get("keyPlaceholder", "property")
    val_ph = args.get("valuePlaceholder", "value")
    allow = set(args["allow"]) if args.get("allow") is not None else None
    for item in as_list(value):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            if k in ctx.sensitive or (allow is not None and k not in allow):
                ctx.omit(f"{args['path']}.{k}")
                continue
            rows.append({key_ph: k, val_ph: format_value(v, None, ctx.sensitive)})
    return rows


def _blocked_field(ctx, name):
    """Campos de SOQL vêm em PascalCase (ex.: Endpoint); a lista de bloqueio, em camelCase."""
    return isinstance(name, str) and name.lower() in {str(s).lower() for s in ctx.sensitive}


def internal_record_properties(ctx, args):
    """Campo/valor do primeiro registro do dado interno."""
    records = ctx.internal.get("records") or []
    if not records:
        return []
    rows = []
    for k, v in records[0].items():
        if k == "attributes" or _blocked_field(ctx, k):
            continue
        rows.append({args.get("keyPlaceholder", "property"): k,
                     args.get("valuePlaceholder", "value"): format_value(v, None, ctx.sensitive)})
    return rows


def internal_rows(ctx, args):
    """Uma linha por registro do dado interno; colunas = {placeholder: campo}."""
    rows = []
    for rec in ctx.internal.get("records") or []:
        row = {}
        for placeholder, field in args["columns"].items():
            if _blocked_field(ctx, field):
                raise ValueError(f"Campo sensível não pode ser documentado: {field}")
            row[placeholder] = format_value(rec.get(field), None, ctx.sensitive)
        rows.append(row)
    return rows


def related_folders(ctx, args):
    """Pastas (formato source) dos XMLs do componente e dos relacionados."""
    seen = {}
    files = list(ctx.files)
    for r in ctx.related:
        files.extend(r.get("files") or [])
    for f in files:
        path = str(f.get("path", ""))
        if "/components/" not in path:
            continue
        folder = str(PurePosixPath(path.split("/components/", 1)[1]).parent)
        seen.setdefault(folder, set()).add(f.get("type") or "")
    return [{"folder": folder, "purpose": ", ".join(sorted(t for t in types if t))}
            for folder, types in sorted(seen.items())]


def related_properties_table(ctx, args, render_props):
    """Bloco: propriedades (do contrato do tipo relacionado) de cada relacionado."""
    related = sorted(ctx.related_of(args["metadataType"]), key=lambda r: r["fullName"])
    if not related:
        return st.NOT_INFORMED if args["metadataType"] in ctx.unresolved_related else st.NOT_APPLICABLE
    contract = ctx.contracts.for_type(args["metadataType"]) if ctx.contracts else None
    if not contract:
        return st.NOT_APPLICABLE
    chunks = []
    for r in related:
        rctx = ctx.child(r.get("data") or {}, full_name=r["fullName"],
                         schema_fields=r.get("schemaFields"), metadata_type=r["metadataType"])
        lines = [f"**{args['metadataType']}: {r['fullName']}**", ""]
        origin = _provenance(r)
        if origin:
            lines += [origin, ""]
        lines += ["| Propriedade | Valor | Fonte |", "|---|---|---|"]
        for name, value, source in render_props(rctx, contract.get("properties", [])):
            lines.append(f"| {name} | {value} | {source} |")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks)


def _provenance(related):
    """Arquivo XML de origem e sha256 do componente relacionado."""
    xml = related.get("xml")
    if not xml:
        return None
    sha = next((f.get("sha256") for f in related.get("files") or [] if f.get("path") == xml), None)
    text = f"_Arquivo: `{xml}`"
    if sha:
        text += f" · sha256 `{sha[:16]}…`"
    return text + "_"


def list_values(ctx, args):
    """Uma linha por valor de uma lista simples em `path` (ex.: interfaces implementadas)."""
    value, _ = resolve(ctx, args["path"])
    ph = args.get("valuePlaceholder", "value")
    return [{ph: format_value(v, None, ctx.sensitive)} for v in as_list(value) if v not in (None, "")]


def naming_convention(ctx, args, _render_props=None):
    """Bloco: o nome do componente segue a convenção do projeto (`args.pattern`, regex)?

    A convenção é configuração do time (contrato), não regra da Salesforce: o papel do
    componente nunca é deduzido do nome — só se compara o nome com o esperado.
    """
    name = ctx.parent.full_name if ctx.parent is not None and args.get("useParentName") else ctx.full_name
    pattern = args.get("pattern")
    if not pattern:
        return st.NOT_APPLICABLE
    ok = re.search(pattern, name or "") is not None
    expected = args.get("description") or f"padrão `{pattern}`"
    return (f"- Nome: `{name}`\n- Convenção do projeto: {expected}\n"
            f"- Segue a convenção: {'Sim' if ok else 'Não'}")


TABLE_BUILDERS = {
    "list_values": list_values,
    "related_components": related_components,
    "related_rows": related_rows,
    "path_rows": path_rows,
    "child_properties": child_properties,
    "internal_record_properties": internal_record_properties,
    "internal_rows": internal_rows,
    "related_folders": related_folders,
}

BLOCK_BUILDERS = {
    "naming_convention": naming_convention,
    "related_properties_table": related_properties_table,
}
