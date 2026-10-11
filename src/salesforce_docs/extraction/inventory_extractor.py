"""Passo 6 — `sf org list metadata` por tipo (raw + index derivado)."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.utils import read_json, write_json

INDEX_KEYS = ("fullName", "type", "fileName", "id", "namespacePrefix", "manageableState",
              "lastModifiedDate", "lastModifiedByName")


def build_inventory_index(metadata_type, result, raw_name) -> dict:
    items = result if isinstance(result, list) else ([result] if isinstance(result, dict) else [])
    components = [{k: item.get(k) for k in INDEX_KEYS if k in item} for item in items
                  if isinstance(item, dict) and item.get("fullName")]
    components.sort(key=lambda c: c["fullName"])
    return {"metadataType": metadata_type, "sourceRaw": raw_name,
            "count": len(components), "components": components}


def extract_inventory(runner, session, metadata_type, type_dir, errors_dir):
    raw_path = type_dir / "inventory.raw.json"
    result = runner.run(
        ["org", "list", "metadata", "--metadata-type", metadata_type,
         "--target-org", session.alias, "--api-version", session.api_version, "--json"],
        raw_path=raw_path,
        error_raw_path=errors_dir / f"inventory-{type_dir.name}.raw.json",
    )
    if not result.ok:
        return {"metadataType": metadata_type, "status": st.FAILED, "components": [],
                "raw": result.raw_path, "error": result.error_message}
    index = build_inventory_index(metadata_type, result.result, raw_path.name)
    write_json(type_dir / "inventory.index.json", index)
    status = st.SUCCESS if index["components"] else st.NO_COMPONENTS
    return {"metadataType": metadata_type, "status": status, "components": index["components"],
            "raw": raw_path, "error": None}


def regenerate_inventory_index(metadata_type, type_dir):
    raw_path = type_dir / "inventory.raw.json"
    data = read_json(raw_path)
    index = build_inventory_index(metadata_type, (data or {}).get("result"), raw_path.name)
    write_json(type_dir / "inventory.index.json", index)
    return index
