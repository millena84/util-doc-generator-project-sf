"""Localiza e carrega o JSON normalizado de cada componente do CSV.

Caminho (gerado pelo Utilitário 1): `inventory/org-<alias>/api-v<N>/<pasta>/normalized/<slug>.json`,
onde `<slug>` é o `slugify` do Utilitário 1 (ex.: `IntegracaoRHService` -> `integracaorhservice`).
Só o JSON normalizado é lido — nunca o XML bruto nem o Markdown.

Status por componente: FOUND, NORMALIZED_JSON_NOT_FOUND, NORMALIZED_JSON_INVALID (JSON malformado)
e NORMALIZED_JSON_MISMATCH (o arquivo existe, mas é de outro tipo/componente).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from salesforce_docs.utils import slugify  # mesma regra de nome de arquivo do Utilitário 1

FOUND = "FOUND"
NOT_FOUND = "NORMALIZED_JSON_NOT_FOUND"
INVALID = "NORMALIZED_JSON_INVALID"
MISMATCH = "NORMALIZED_JSON_MISMATCH"


def _rel(path, root):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def _read(path):
    raw = Path(path).read_bytes()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def expected_path(settings, component, alias=None, api_version=None) -> Path:
    folder = settings.folders.get(component["componentType"])
    return settings.inventory_dir(alias, api_version) / folder / "normalized" / f"{slugify(component['componentName'])}.json"


def _cmdt_records(folder_dir, type_name, root):
    """Records de Custom Metadata do tipo `X__mdt` (fullName `X.Registro`), na mesma pasta."""
    prefix = type_name[:-len("__mdt")] + "." if type_name.endswith("__mdt") else None
    out = []
    if not prefix or not folder_dir.is_dir():
        return out
    for p in sorted(folder_dir.glob("*.json")):
        try:
            data, sha = _read(p)
        except (ValueError, OSError):
            continue
        if data.get("metadataType") == "CustomMetadata" and str(data.get("fullName", "")).startswith(prefix):
            out.append({"path": _rel(p, root), "sha256": sha, "fullName": data.get("fullName"),
                        "data": data.get("data"), "codeBody": data.get("codeBody")})
    return out


def load_component(settings, component, alias=None, api_version=None) -> dict:
    key = f"{component['componentType']}:{component['componentName']}"
    path = expected_path(settings, component, alias, api_version)
    entry = {"key": key, "componentType": component["componentType"],
             "componentName": component["componentName"], "expectedPath": _rel(path, settings.project_root),
             "status": None, "path": None, "sha256": None, "metadataType": None, "label": None,
             "data": None, "codeBody": None, "extraSources": []}
    if not path.is_file():
        entry["status"] = NOT_FOUND
        return entry
    try:
        doc, sha = _read(path)
    except (ValueError, OSError) as exc:
        entry.update(status=INVALID, path=entry["expectedPath"], error=f"JSON inválido: {type(exc).__name__}")
        return entry
    if not isinstance(doc, dict) or not isinstance(doc.get("data"), (dict, type(None))):
        entry.update(status=INVALID, path=entry["expectedPath"], error="estrutura inesperada (sem objeto data)")
        return entry
    entry.update(path=entry["expectedPath"], sha256=sha, metadataType=doc.get("metadataType"))
    full_name = str(doc.get("fullName") or "")
    if doc.get("metadataType") not in settings.expected_metadata_types(component["componentType"]) \
            or full_name.lower() != component["componentName"].lower():
        entry.update(status=MISMATCH, error=f"arquivo é de {doc.get('metadataType')}:{full_name}")
        return entry
    data = doc.get("data") or {}
    entry.update(status=FOUND, data=data, codeBody=doc.get("codeBody") or data.get("codeBody"),
                 label=data.get("label") if isinstance(data.get("label"), str) else None)
    if component["componentType"] == "CustomMetadata":
        entry["extraSources"] = _cmdt_records(path.parent, full_name, settings.project_root)
    return entry


def load_all(settings, components, alias=None, api_version=None):
    return [load_component(settings, c, alias, api_version) for c in components]
