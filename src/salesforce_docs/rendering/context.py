"""Contexto de renderização e resolução de caminhos de propriedades.

Sintaxe de `path` nos contratos:
- `@fullName`, `@developerName`, `@parent.fullName`
- `internal:records` (lista de registros do dado interno), `internal:first.Campo`
- caminho pontuado sobre o JSON normalizado (`label`, `start.triggerType`)
"""

from __future__ import annotations

from salesforce_docs import status as st

PRESENT, ABSENT, NOT_APPLICABLE = "PRESENT", "ABSENT", "NOT_APPLICABLE"


class RenderContext:
    def __init__(self, metadata_type, full_name, data, schema_fields=None, internal=None,
                 related=None, files=None, parent=None, contracts=None, sensitive=(),
                 developer_name=None, normalized_path=None, omitted=None):
        self.metadata_type = metadata_type
        self.full_name = full_name
        self.data = data or {}
        self.schema_fields = schema_fields
        self.internal = internal or {}
        self.related = related or []
        self.files = files or []
        self.parent = parent
        self.contracts = contracts
        self.sensitive = set(sensitive)
        self.developer_name = developer_name or full_name
        self.normalized_path = normalized_path
        # Propriedades encontradas no XML e omitidas por política (compartilhado com filhos).
        self.omitted = omitted if omitted is not None else set()

    def omit(self, name):
        self.omitted.add(f"{self.metadata_type}:{self.full_name}:{name}")

    def child(self, data, full_name=None, schema_fields=None, metadata_type=None):
        return RenderContext(metadata_type or self.metadata_type, full_name or self.full_name, data,
                             schema_fields=schema_fields, internal=self.internal,
                             related=self.related, files=self.files, parent=self,
                             contracts=self.contracts, sensitive=self.sensitive,
                             omitted=self.omitted)

    def related_of(self, metadata_type):
        return [r for r in self.related if r["metadataType"] == metadata_type]


def resolve(ctx: RenderContext, path: str):
    """Retorna (valor, estado)."""
    if path == "@fullName":
        return ctx.full_name, PRESENT
    if path == "@developerName":
        return ctx.developer_name, PRESENT
    if path.startswith("@parent."):
        if ctx.parent is None:
            return None, NOT_APPLICABLE
        return resolve(ctx.parent, "@" + path[len("@parent."):])
    if path.startswith("internal:"):
        records = ctx.internal.get("records")
        if records is None:
            return None, ABSENT
        rest = path[len("internal:"):]
        if rest == "records":
            return (records, PRESENT) if records else (None, ABSENT)
        if rest.startswith("first."):
            if not records:
                return None, ABSENT
            v = records[0].get(rest[len("first."):])
            return (v, PRESENT) if v not in (None, "") else (None, ABSENT)
        return None, ABSENT
    parts = path.split(".")
    if parts[-1] in ctx.sensitive:
        raise ValueError(f"Caminho sensível não pode ser documentado: {path}")
    top = parts[0]
    if top not in ctx.data:
        if ctx.schema_fields is not None and top not in ctx.schema_fields:
            return None, NOT_APPLICABLE
        return None, ABSENT
    cur = ctx.data
    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None, ABSENT
    if cur is None or cur == "":
        return None, ABSENT
    return cur, PRESENT


def format_value(value, fmt=None, sensitive=()):
    """Formata valor do XML/dado interno sem alterá-lo semanticamente."""
    if value is None or value == "":
        return None
    if isinstance(value, list):
        parts = [format_value(v, fmt, sensitive) for v in value]
        parts = [p for p in parts if p]
        return ("; " if fmt or any(isinstance(v, dict) for v in value) else ", ").join(parts) or None
    if isinstance(value, dict):
        if fmt:
            try:
                return fmt.format_map(_SafeDict({k: v for k, v in value.items() if k not in sensitive}))
            except (ValueError, IndexError):
                pass
        items = []
        for k, v in value.items():
            if k in sensitive or k == "attributes":
                continue
            fv = format_value(v, None, sensitive)
            if fv is not None:
                items.append(f"{k}={fv}")
        return ", ".join(items) or None
    return str(value)


class _SafeDict(dict):
    def __missing__(self, key):
        return st.NOT_INFORMED


def empty_text(state, default=st.NOT_INFORMED):
    return st.NOT_APPLICABLE if state == NOT_APPLICABLE else default
