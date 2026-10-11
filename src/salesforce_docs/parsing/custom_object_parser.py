"""Particularidades de Custom Object: filhos recuperados junto com o objeto."""

from __future__ import annotations


def child_files(primary_files, primary_full_name, child_type):
    """Arquivos filhos (CustomField, RecordType...) do retrieve do objeto."""
    out = []
    prefix = f"{primary_full_name}."
    for f in primary_files:
        if f.get("type") != child_type:
            continue
        name = str(f.get("fullName") or "")
        if name.startswith(prefix) or name.lower().startswith(prefix.lower()):
            out.append(f)
    return sorted(out, key=lambda f: f["fullName"])


TABLE_BUILDERS = {}
BLOCK_BUILDERS = {}
