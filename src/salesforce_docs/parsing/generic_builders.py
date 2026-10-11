"""Builders genéricos referenciados pelos contratos (tabelas e blocos).

Um builder de tabela retorna lista de dicts {placeholder: valor}.
Um builder de bloco retorna texto Markdown.
"""

from __future__ import annotations

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
    return rows


def related_rows(ctx, args):
    """Uma linha por componente relacionado de `metadataType`, colunas por path."""
    rows = []
    for r in sorted(ctx.related_of(args["metadataType"]), key=lambda r: r["fullName"]):
        rctx = ctx.child(r.get("data") or {}, full_name=r["fullName"],
                         schema_fields=r.get("schemaFields"))
        rows.append(_columns(rctx, args["columns"], args.get("formats")))
    return rows


def path_rows(ctx, args):
    """Uma linha por item da lista em `path` do XML."""
    value, _ = resolve(ctx, args["path"])
    rows = []
    for item in as_list(value):
        if not isinstance(item, dict):
            continue
        rows.append(_columns(ctx.child(item), args["columns"], args.get("formats")))
    return rows


def child_properties(ctx, args):
    """Propriedade/valor dos filhos diretos de um elemento (ex.: oauthConfig)."""
    value, _ = resolve(ctx, args["path"])
    rows = []
    key_ph = args.get("keyPlaceholder", "property")
    val_ph = args.get("valuePlaceholder", "value")
    for item in as_list(value):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            if k in ctx.sensitive:
                continue
            rows.append({key_ph: k, val_ph: format_value(v, None, ctx.sensitive)})
    return rows


def internal_record_properties(ctx, args):
    """Campo/valor do primeiro registro do dado interno."""
    records = ctx.internal.get("records") or []
    if not records:
        return []
    rows = []
    for k, v in records[0].items():
        if k == "attributes" or k in ctx.sensitive:
            continue
        rows.append({args.get("keyPlaceholder", "property"): k,
                     args.get("valuePlaceholder", "value"): format_value(v, None, ctx.sensitive)})
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
        return st.NOT_APPLICABLE
    contract = ctx.contracts.for_type(args["metadataType"]) if ctx.contracts else None
    if not contract:
        return st.NOT_APPLICABLE
    chunks = []
    for r in related:
        rctx = ctx.child(r.get("data") or {}, full_name=r["fullName"],
                         schema_fields=r.get("schemaFields"))
        lines = [f"**{args['metadataType']}: {r['fullName']}**", "",
                 "| Propriedade | Valor | Fonte |", "|---|---|---|"]
        for name, value, source in render_props(rctx, contract.get("properties", [])):
            lines.append(f"| {name} | {value} | {source} |")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks)


TABLE_BUILDERS = {
    "related_components": related_components,
    "related_rows": related_rows,
    "path_rows": path_rows,
    "child_properties": child_properties,
    "internal_record_properties": internal_record_properties,
    "related_folders": related_folders,
}

BLOCK_BUILDERS = {
    "related_properties_table": related_properties_table,
}
