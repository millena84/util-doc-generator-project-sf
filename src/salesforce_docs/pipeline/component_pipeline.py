"""Pipeline por componente: retrieve (Passo 7) -> normalização (Passo 8).

Cada componente é extraído de forma independente, mesmo quando vários
componentes compõem um único documento (desvios).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from salesforce_docs import status as st
from salesforce_docs.extraction.schema_extractor import load_schema
from salesforce_docs.extraction.xml_retriever import retrieve_component
from salesforce_docs.parsing.xml_parser import local_name, normalize_component, schema_field_names
from salesforce_docs.utils import rel, slugify, write_json


class ComponentRecord(dict):
    """Resultado de um componente. Chaves não serializáveis: data, schemaFields."""

    def entry(self) -> dict:
        skip = {"data", "schemaFields", "children"}
        out = {k: v for k, v in self.items() if k not in skip}
        out["children"] = [{"metadataType": c["metadataType"], "fullName": c["fullName"],
                            "xml": c.get("xml"), "normalized": c.get("normalized")}
                           for c in self.get("children", [])]
        return out


class ComponentProcessor:
    def __init__(self, pctx):
        self.p = pctx
        self._cache = {}

    def type_dir(self, metadata_type) -> Path:
        return self.p.inventory_dir / self.p.mvp.folder(metadata_type)

    def process(self, metadata_type, full_name, inventory_item=None, role="primary",
                folder_type=None) -> ComponentRecord:
        """folder_type: tipo cuja pasta do inventory recebe o componente (padrão: o próprio)."""
        key = (metadata_type, full_name)
        if key in self._cache:
            return self._cache[key]
        record = self._process(metadata_type, full_name, inventory_item or {}, role,
                               folder_type or metadata_type)
        self._cache[key] = record
        return record

    def _process(self, metadata_type, full_name, inventory_item, role, folder_type):
        type_dir = self.type_dir(folder_type)
        slug = slugify(full_name)
        record = ComponentRecord(metadataType=metadata_type, fullName=full_name, role=role,
                                 status=None, xml=None, normalized=None, retrieveRaw=None,
                                 files=[], children=[], warnings=[], error=None,
                                 folderType=folder_type,
                                 namespacePrefix=inventory_item.get("namespacePrefix") or None)
        outcome = retrieve_component(
            self.p.runner, self.p.session, metadata_type, full_name,
            components_dir=type_dir / "components",
            raw_path=type_dir / "retrieve" / f"{slug}.raw.json",
            errors_raw_path=self.p.errors_dir / f"retrieve-{self.p.mvp.folder(folder_type)}-{slug}.raw.json",
            project_root=self.p.root,
        )
        record.update(retrieveRaw=outcome.get("retrieveRaw"), files=outcome.get("files", []))
        if outcome["status"] != st.SUCCESS:
            record.update(status=outcome["status"], error=outcome.get("error"))
            self.p.log.warn(f"{metadata_type}:{full_name} -> {outcome['status']}: {outcome.get('error')}")
            return record
        if outcome.get("error"):
            record["warnings"].append(f"Retrieve com avisos: {outcome['error']}")
        record["xml"] = outcome["xml"]
        record["warnings"].extend(self.sensitive_warnings(record["files"]))
        normalize_record(self.p, record)
        record["status"] = st.SUCCESS
        return record

    def sensitive_warnings(self, files):
        warnings = []
        for f in files:
            path = self.p.root / f["path"]
            if not str(path).endswith(".xml"):
                continue
            try:
                root = ET.parse(str(path)).getroot()
            except ET.ParseError:
                continue
            hits = sorted({local_name(e.tag) for e in root.iter()
                           if local_name(e.tag) in self.p.mvp.sensitive_elements and (e.text or "").strip()})
            if hits:
                warnings.append(f"{f['path']} contém elementos sensíveis {hits}: não versionar; "
                                "omitidos do Markdown")
        return warnings


def normalize_record(pctx, record):
    """(Re)gera o normalizado do componente e dos filhos a partir do XML."""
    metadata_type, full_name = record["metadataType"], record["fullName"]
    type_dir = pctx.inventory_dir / pctx.mvp.folder(record.get("folderType") or metadata_type)
    schema = load_schema(pctx.schemas_dir, metadata_type)
    normalized = normalize_component(metadata_type, full_name, pctx.root / record["xml"],
                                     pctx.root, schema, role=record.get("role", "primary"),
                                     retrieve_raw=record.get("retrieveRaw"),
                                     secret_keys=pctx.mvp.sensitive_elements, on_secret=pctx.masker.add)
    norm_path = type_dir / "normalized" / f"{slugify(full_name)}.json"
    write_json(norm_path, normalized, private=True)
    record.update(normalized=rel(norm_path, pctx.root), data=normalized["data"],
                  schemaFields=schema_field_names(schema))
    children = []
    for f in record.get("files", []):
        if f["path"] == record["xml"] or not f["path"].endswith(".xml"):
            continue
        child_schema = load_schema(pctx.schemas_dir, f["type"])
        child_norm = normalize_component(f["type"], f["fullName"], pctx.root / f["path"], pctx.root,
                                         child_schema, role="child", retrieve_raw=record.get("retrieveRaw"),
                                         secret_keys=pctx.mvp.sensitive_elements, on_secret=pctx.masker.add)
        child_path = type_dir / "normalized" / f"{slugify(f['fullName'])}.json"
        write_json(child_path, child_norm, private=True)
        children.append({"metadataType": f["type"], "fullName": f["fullName"], "xml": f["path"],
                         "normalized": rel(child_path, pctx.root), "data": child_norm["data"],
                         "schemaFields": schema_field_names(child_schema), "files": [f]})
    record["children"] = children
    return record
