"""Passo 5 — describeValueType() via Metadata API (raw + schema derivado)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from salesforce_docs import status as st
from salesforce_docs.parsing.xml_parser import element_to_value, local_name
from salesforce_docs.salesforce.metadata_api_client import MD_NS, raise_if_session_expired
from salesforce_docs.utils import kebab, read_json, sha256_file, write_json, write_text_raw

LIST_KEYS = ("valueTypeFields", "fields", "picklistValues", "foreignKeyDomain")


def raw_schema_path(schemas_dir, metadata_type):
    return schemas_dir / f"{kebab(metadata_type)}.describevaluetype.raw.json"


def derived_schema_path(schemas_dir, metadata_type):
    return schemas_dir / f"{kebab(metadata_type)}.schema.json"


def parse_describe_body(body: str) -> dict:
    root = ET.fromstring(body.encode("utf-8"))
    result = root.find(f".//{{{MD_NS}}}describeValueTypeResponse/{{{MD_NS}}}result")
    if result is None:
        raise ValueError("Resposta sem describeValueTypeResponse/result")
    value = element_to_value(result, force_list=LIST_KEYS)
    return value if isinstance(value, dict) else {}


def build_schema(metadata_type, api_version, raw_path) -> dict:
    raw = read_json(raw_path)
    parsed = parse_describe_body(raw["response"]["body"])
    fields = parsed.get("valueTypeFields") or []
    return {
        "metadataType": metadata_type,
        "apiVersion": api_version,
        "sourceRaw": raw_path.name,
        "sourceRawSha256": sha256_file(raw_path),
        "apiCreatable": parsed.get("apiCreatable"),
        "apiDeletable": parsed.get("apiDeletable"),
        "apiReadable": parsed.get("apiReadable"),
        "apiUpdatable": parsed.get("apiUpdatable"),
        "parentField": parsed.get("parentField"),
        "fieldNames": [f.get("name") for f in fields if isinstance(f, dict) and f.get("name")],
        "valueTypeFields": fields,
    }


def extract_schema(client, metadata_type, schemas_dir, errors_dir, save_raw=True):
    """Retorna dict com status, raw, schema (path) e erro. Sessão expirada lança."""
    response = client.describe_value_type(metadata_type)
    raw = response.to_raw()
    raw_text = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"
    target = raw_schema_path(schemas_dir if response.ok else errors_dir, metadata_type)
    if save_raw:
        write_text_raw(target, raw_text)
    raise_if_session_expired(response)
    if not response.ok:
        fault = response.fault()
        detail = (f"{fault[0]}: {fault[1]}" if fault
                  else response.error or f"HTTP {response.http_status}")
        return {"metadataType": metadata_type, "status": st.SCHEMA_UNAVAILABLE,
                "raw": target, "schema": None, "error": detail}
    try:
        schema = build_schema(metadata_type, client.api_version, target)
    except (ValueError, ET.ParseError, KeyError) as exc:
        return {"metadataType": metadata_type, "status": st.SCHEMA_UNAVAILABLE,
                "raw": target, "schema": None, "error": f"Resposta não interpretável: {exc}"}
    schema_path = derived_schema_path(schemas_dir, metadata_type)
    write_json(schema_path, schema)
    return {"metadataType": metadata_type, "status": st.SUCCESS, "raw": target,
            "schema": schema_path, "error": None}


def load_schema(schemas_dir, metadata_type):
    path = derived_schema_path(schemas_dir, metadata_type)
    return read_json(path) if path.is_file() else None


def regenerate_schemas(schemas_dir, api_version):
    done = []
    for raw_path in sorted(schemas_dir.glob("*.describevaluetype.raw.json")):
        raw = read_json(raw_path)
        qname = (raw.get("request") or {}).get("arguments", {}).get("type", "")
        metadata_type = local_name(qname)
        if not metadata_type:
            continue
        write_json(derived_schema_path(schemas_dir, metadata_type),
                   build_schema(metadata_type, api_version, raw_path))
        done.append(metadata_type)
    return done
