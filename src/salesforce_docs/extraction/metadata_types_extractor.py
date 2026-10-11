"""Passo 4 — `sf org list metadata-types` (raw + index derivado)."""

from __future__ import annotations

from salesforce_docs.errors import GlobalFailure
from salesforce_docs.utils import read_json, write_json
from salesforce_docs.validation.metadata_type_validator import build_index


def extract_metadata_types(runner, session, catalog_dir, errors_dir):
    raw_path = catalog_dir / "metadata-types.raw.json"
    result = runner.run(
        ["org", "list", "metadata-types", "--target-org", session.alias,
         "--api-version", session.api_version, "--json"],
        raw_path=raw_path,
        error_raw_path=errors_dir / "metadata-types.raw.json",
    )
    if not result.ok:
        raise GlobalFailure("METADATA_TYPES_FAILED",
                            f"`sf org list metadata-types` falhou: {result.error_message}")
    index = build_index(result.result)
    index_path = catalog_dir / "metadata-types.index.json"
    write_json(index_path, dict(index, sourceRaw=raw_path.name))
    return index, raw_path, index_path


def regenerate_index(catalog_dir):
    raw_path = catalog_dir / "metadata-types.raw.json"
    data = read_json(raw_path)
    index = build_index((data or {}).get("result"))
    write_json(catalog_dir / "metadata-types.index.json", dict(index, sourceRaw=raw_path.name))
    return index
