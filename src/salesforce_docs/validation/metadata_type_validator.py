"""Passo 4 — validar se os tipos mockados estão habilitados na org."""

from __future__ import annotations

from salesforce_docs import status as st


def build_index(list_metadata_types_result) -> dict:
    """Derivado de metadata-types.raw.json (regenerável)."""
    objects = []
    if isinstance(list_metadata_types_result, dict):
        objects = list_metadata_types_result.get("metadataObjects") or []
    types = {}
    children = {}
    for obj in objects:
        name = obj.get("xmlName")
        if not name:
            continue
        child_names = obj.get("childXmlNames") or []
        if isinstance(child_names, str):
            child_names = [child_names]
        types[name] = {
            "directoryName": obj.get("directoryName"),
            "suffix": obj.get("suffix"),
            "inFolder": obj.get("inFolder"),
            "metaFile": obj.get("metaFile"),
            "childXmlNames": sorted(child_names),
        }
        for child in child_names:
            children.setdefault(child, []).append(name)
    return {
        "metadataTypes": dict(sorted(types.items())),
        "childMetadataTypes": {k: sorted(v) for k, v in sorted(children.items())},
    }


def check_enabled(index: dict, metadata_type: str) -> dict:
    if metadata_type in index.get("metadataTypes", {}):
        return {"metadataType": metadata_type, "status": st.ENABLED, "kind": "TOP_LEVEL"}
    parents = index.get("childMetadataTypes", {}).get(metadata_type)
    if parents:
        return {"metadataType": metadata_type, "status": st.ENABLED, "kind": "CHILD", "parents": parents}
    return {"metadataType": metadata_type, "status": st.NOT_ENABLED}
