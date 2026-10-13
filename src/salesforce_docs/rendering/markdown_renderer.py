"""Renderiza um modelo Markdown a partir do contrato + contexto (Passo 10).

Regras aplicadas:
- só placeholders previstos no contrato são preenchidos; placeholder sem
  definição invalida o documento;
- toda linha de tabela com coluna "Fonte" precisa de uma fonte permitida e
  igual à declarada no contrato;
- dado ausente vira "Não informado" e dado inexistente para o tipo vira
  "Não aplicável" (quando o describeValueType comprova que o campo não existe).
"""

from __future__ import annotations

import re

from salesforce_docs import status as st
from salesforce_docs.parsing import (access_builders, custom_metadata_parser, custom_object_parser,
                                     external_client_app_parser, flow_parser, generic_builders)
from salesforce_docs.rendering.context import empty_text, format_value, resolve

PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")

TABLE_BUILDERS = {}
BLOCK_BUILDERS = {}
for _mod in (access_builders, generic_builders, flow_parser, external_client_app_parser,
             custom_object_parser, custom_metadata_parser):
    TABLE_BUILDERS.update(_mod.TABLE_BUILDERS)
    BLOCK_BUILDERS.update(_mod.BLOCK_BUILDERS)


class RenderResult:
    def __init__(self, text, errors, warnings):
        self.text = text
        self.errors = errors
        self.warnings = warnings

    @property
    def ok(self):
        return not self.errors


def escape_cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\r\n", "\n").replace("\n", "<br>")


def render_properties(ctx, properties):
    """(nome, valor formatado, fonte) para cada propriedade do contrato."""
    out = []
    for prop in properties:
        value, state = resolve(ctx, prop["path"])
        text = format_value(value, prop.get("format"), ctx.sensitive)
        if text is None:
            text = empty_text(state, prop.get("emptyValue", st.NOT_INFORMED))
        out.append((prop["name"], escape_cell(text), prop["source"]))
    return out


def _cells(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    inner = s[1:-1] if s.endswith("|") and not s.endswith("\\|") else s[1:]
    return [c.strip() for c in re.split(r"(?<!\\)\|", inner)]


def _fonte_of(line):
    cells = _cells(line)
    return cells[-1] if cells else None


class MarkdownRenderer:
    def render(self, template_text: str, contract: dict, ctx) -> RenderResult:
        errors, warnings = [], []
        props = contract.get("properties", [])
        tables = {t["markdownSection"]: t for t in contract.get("tables", [])}
        blocks = {b["placeholder"]: b for b in contract.get("blocks", [])}
        title_path = contract.get("titlePath", "@fullName")
        section = None
        out = []
        for line in template_text.splitlines():
            if line.startswith("## "):
                section = line[3:].strip()
            names = PLACEHOLDER_RE.findall(line)
            if not names:
                out.append(line)
                continue
            if section in tables and _cells(line) is not None:
                out.extend(self._table_rows(line, tables[section], ctx, errors))
                continue
            rendered = line
            for name in names:
                value, source = self._scalar(name, section, props, blocks, title_path, ctx,
                                             errors, warnings, line)
                if value is None:
                    continue
                rendered = re.sub(r"\{\{\s*" + name + r"\s*\}\}", lambda _m, v=value: v, rendered, count=1)
            out.append(rendered)
        text = "\n".join(out) + "\n"
        errors.extend(validate_document(text))
        return RenderResult(text, errors, warnings)

    # ------------------------------------------------------------------
    def _scalar(self, name, section, props, blocks, title_path, ctx, errors, warnings, line):
        if name == "component_name" and section is None:
            value, state = resolve(ctx, title_path)
            return escape_cell(format_value(value) or empty_text(state)), None
        prop = _find_prop(props, name, section)
        if prop is not None:
            value, state = resolve(ctx, prop["path"])
            text = format_value(value, prop.get("format"), ctx.sensitive)
            if text is None:
                text = empty_text(state, prop.get("emptyValue", st.NOT_INFORMED))
                if prop.get("required") and state != "NOT_APPLICABLE":
                    warnings.append(f"Propriedade obrigatória sem valor: {prop['name']}")
            fonte = _fonte_of(line)
            if fonte is not None and fonte != prop["source"]:
                errors.append(f"Fonte divergente para {prop['name']}: modelo '{fonte}', "
                              f"contrato '{prop['source']}'")
            return escape_cell(text), prop["source"]
        block = blocks.get(name)
        if block is not None:
            builder = BLOCK_BUILDERS.get(block["builder"])
            if builder is None:
                errors.append(f"Builder de bloco desconhecido: {block['builder']}")
                return None, None
            body = builder(ctx, block.get("args") or {}, render_properties)
            return f"{body}\n\n_Fonte: {block['source']}_", block["source"]
        errors.append(f"Placeholder '{name}' (seção '{section}') não previsto no contrato")
        return None, None

    def _table_rows(self, line, table, ctx, errors):
        builder = TABLE_BUILDERS.get(table["builder"])
        if builder is None:
            errors.append(f"Builder de tabela desconhecido: {table['builder']}")
            return [line]
        fonte = _fonte_of(line)
        if fonte != table["source"]:
            errors.append(f"Fonte divergente na seção '{table['markdownSection']}': "
                          f"modelo '{fonte}', contrato '{table['source']}'")
        rows = builder(ctx, table.get("args") or {})
        empty = table.get("emptyValue", st.NOT_APPLICABLE)
        names = PLACEHOLDER_RE.findall(line)
        if not rows:
            rows = [{n: None for n in names}]
        out = []
        for row in rows:
            rendered = line
            for n in names:
                cell = row.get(n)
                state = None
                if isinstance(cell, tuple):
                    cell, state = cell
                text = cell if cell not in (None, "") else (
                    st.NOT_APPLICABLE if state == "NOT_APPLICABLE" else
                    (empty if all(row.get(x) is None for x in names) else st.NOT_INFORMED))
                rendered = re.sub(r"\{\{\s*" + n + r"\s*\}\}", lambda _m, v=escape_cell(text): v,
                                  rendered, count=1)
            out.append(rendered)
        return out


def _find_prop(props, placeholder, section):
    fallback = None
    for p in props:
        if p.get("placeholder") != placeholder:
            continue
        if p.get("markdownSection") == section:
            return p
        fallback = fallback or p
    return fallback


def validate_document(text: str):
    """Validações do documento final (prompt, seção 11)."""
    errors = []
    if PLACEHOLDER_RE.search(text):
        errors.append("Documento contém placeholders não preenchidos")
    fonte_idx = None
    for line in text.splitlines():
        cells = _cells(line)
        if cells is None:
            fonte_idx = None
            continue
        if "Fonte" in cells:
            fonte_idx = cells.index("Fonte")
            continue
        if fonte_idx is None or all(set(c) <= set("-: ") for c in cells):
            continue
        value = cells[fonte_idx] if fonte_idx < len(cells) else ""
        if value not in st.ALLOWED_SOURCES:
            errors.append(f"Fonte não permitida/ausente na linha: {line.strip()}")
    # "N/A" é proibido (prompt, 6.2). "None"/"null" não entram: são valores legítimos de
    # enums Salesforce (ex.: startPage=None) e o formatador nunca converte None em texto.
    for bad in ("N/A",):
        for line in text.splitlines():
            cells = _cells(line) or []
            if bad in cells:
                errors.append(f"Valor proibido '{bad}' na linha: {line.strip()}")
    return errors
