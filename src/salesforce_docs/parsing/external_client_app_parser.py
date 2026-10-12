"""Particularidades de External Client App: relações por conteúdo do XML."""

from __future__ import annotations


def leaf_values(data):
    """Todos os valores-folha (strings) de um JSON normalizado."""
    out = set()
    stack = [data]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
        elif isinstance(cur, str) and cur:
            out.add(cur)
    return out


def field_equals_primary(primary_full_name, related_data, field):
    """Relacionado aponta explicitamente para o app (ex.: externalClientApplication)."""
    return isinstance(related_data, dict) and related_data.get(field) == primary_full_name


def reference_scan(primary_full_name, primary_data, related_full_name, related_data):
    """Relação comprovada por valor exato em um dos XMLs (sem heurística de substring)."""
    return (related_full_name in leaf_values(primary_data)
            or primary_full_name in leaf_values(related_data or {}))


def values_at(data, path):
    """Valores-folha em `path` pontuado, atravessando listas (ex.: params.externalCredential)."""
    current = [data]
    for part in path.split("."):
        nxt = []
        for c in current:
            for item in (c if isinstance(c, list) else [c]):
                if isinstance(item, dict) and part in item:
                    nxt.append(item[part])
        current = nxt
    out = set()
    for c in current:
        for v in (c if isinstance(c, list) else [c]):
            if isinstance(v, str) and v:
                out.add(v)
    return out


TABLE_BUILDERS = {}
BLOCK_BUILDERS = {}
