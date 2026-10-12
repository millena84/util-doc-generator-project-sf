"""Parser XML genérico: XML original -> JSON normalizado (Passo 8).

Regras:
- não inventa propriedades: só converte o que está no XML;
- campos do schema (describeValueType) ausentes no XML ficam como null;
- registra campos presentes e ausentes;
- saída determinística, regenerável a partir do XML (inclui sha256 do XML).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from salesforce_docs.utils import rel, sha256_file

XSI_NIL = "{http://www.w3.org/2001/XMLSchema-instance}nil"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def element_to_value(elem, force_list=()):
    """Converte elemento em valor JSON.

    Folha -> texto (string, sem conversão de tipo); xsi:nil -> None.
    Elemento com filhos -> dict; tags repetidas -> lista.
    """
    children = list(elem)
    if not children:
        if elem.get(XSI_NIL) == "true":
            return None
        return elem.text if elem.text is not None else ""
    out = {}
    lists = set()
    for child in children:
        key = local_name(child.tag)
        value = element_to_value(child, force_list)
        if key in lists:
            out[key].append(value)
        elif key in out:
            out[key] = [out[key], value]
            lists.add(key)
        elif key in force_list:
            out[key] = [value]
            lists.add(key)
        else:
            out[key] = value
    return out


def parse_xml_file(path):
    """Retorna (rootElementName, data) sem modificar o arquivo."""
    tree = ET.parse(str(path))
    root = tree.getroot()
    value = element_to_value(root)
    if not isinstance(value, dict):
        value = {"_text": value}
    return local_name(root.tag), value


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


REDACTED = "[REDACTED]"


def redact(data, secret_keys, prefix=""):
    """Substitui valores de elementos secretos por REDACTED; retorna os caminhos afetados.

    O XML original (raw) não é alterado; só o derivado normalizado recebe a máscara,
    de forma determinística (continua regenerável a partir do XML).
    """
    hits = []
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            if k in secret_keys and v not in (None, ""):
                data[k] = REDACTED
                hits.append(path)
            else:
                hits.extend(redact(v, secret_keys, path))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, (dict, list)):
                hits.extend(redact(v, secret_keys, f"{prefix}[{i}]"))
    return hits


def normalize_component(metadata_type, full_name, xml_path, project_root, schema=None,
                        role="primary", retrieve_raw=None, secret_keys=()):
    """Gera o documento normalizado de um componente."""
    root_name, data = parse_xml_file(xml_path)
    redacted = sorted(redact(data, set(secret_keys))) if secret_keys else []
    present = sorted(data.keys())
    schema_fields = schema_field_names(schema) if schema else None
    absent = []
    if schema_fields is not None:
        for name in schema_fields:
            if name not in data:
                absent.append(name)
                data[name] = None
        absent.sort()
    return {
        "metadataType": metadata_type,
        "fullName": full_name,
        "role": role,
        "source": {
            "xml": rel(xml_path, project_root),
            "xmlSha256": sha256_file(xml_path),
            "rootElement": root_name,
            "retrieveRaw": retrieve_raw,
        },
        "schema": {
            "available": schema_fields is not None,
            "fieldNames": schema_fields,
        },
        "fields": {"present": present, "absent": absent, "redacted": redacted},
        "data": data,
    }


def schema_field_names(schema):
    if not schema:
        return None
    names = []
    for f in schema.get("valueTypeFields") or []:
        name = f.get("name") if isinstance(f, dict) else None
        if name and name not in names:
            names.append(name)
    return names


def is_regenerable(normalized: dict, project_root) -> bool:
    """O XML de origem existe e não mudou desde a normalização."""
    xml = Path(project_root) / normalized["source"]["xml"]
    return xml.is_file() and sha256_file(xml) == normalized["source"]["xmlSha256"]
