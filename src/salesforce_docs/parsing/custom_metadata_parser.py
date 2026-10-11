"""Particularidades de Custom Metadata: agrupa records por tipo (__mdt)."""

from __future__ import annotations


def group_records_by_type(record_full_names, separator=".", suffix="__mdt"):
    """{'Config__mdt': ['Config.Default', ...]} a partir de fullNames 'Tipo.Record'."""
    groups = {}
    for name in record_full_names:
        if separator not in name:
            continue
        type_name = name.split(separator, 1)[0] + suffix
        groups.setdefault(type_name, []).append(name)
    return {k: sorted(v) for k, v in sorted(groups.items())}


TABLE_BUILDERS = {}
BLOCK_BUILDERS = {}
