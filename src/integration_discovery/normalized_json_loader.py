"""Localiza e carrega o JSON normalizado de cada componente do CSV.

Caminho (gerado pelo Utilitário 1): `inventory/org-<alias>/api-v<N>/<pasta>/normalized/<slug>.json`,
onde `<slug>` é o `slugify` do Utilitário 1 (ex.: `IntegracaoRHService` -> `integracaorhservice`).
Só o JSON normalizado é lido — nunca o XML bruto nem o Markdown.

Status por componente: FOUND, NORMALIZED_JSON_NOT_FOUND, NORMALIZED_JSON_INVALID (JSON malformado)
e NORMALIZED_JSON_MISMATCH (o arquivo existe, mas é de outro tipo/componente).

Relacionados lidos junto (`discovery.relatedSources`): JSONs normalizados de outros tipos que o
Utilitário 1 grava ao lado do componente (políticas da External Client App, filhos do objeto,
records de Custom Metadata). Ficam em `extraSources`, com o vínculo (`link`) que os prendeu ao
componente; não viram nós do grafo.
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


def _folder_index(settings, inv_dir, folder):
    """JSONs normalizados de uma pasta, lidos uma vez por execução (cache no objeto settings)."""
    cache = settings.__dict__.setdefault("_folder_index", {})
    key = str(inv_dir / folder)
    if key not in cache:
        items = []
        for p in sorted((inv_dir / folder / "normalized").glob("*.json")):
            try:
                doc, sha = _read(p)
            except (ValueError, OSError):
                continue
            if isinstance(doc, dict):
                items.append({"path": _rel(p, settings.project_root), "sha256": sha,
                              "metadataType": doc.get("metadataType"), "fullName": str(doc.get("fullName") or ""),
                              "data": doc.get("data"), "codeBody": doc.get("codeBody")})
        cache[key] = items
    return cache[key]


def related_sources(settings, component, full_name, own_path, inv_dir):
    """Relacionados declarados em `discovery.relatedSources` para o tipo do componente."""
    out, seen = [], {own_path}
    for spec in settings.related_sources.get(component["componentType"]) or []:
        types = set(spec.get("metadataTypes") or [])
        if spec["match"] == "CHILD_OF":
            base = full_name
            if spec.get("stripSuffix") and base.endswith(spec["stripSuffix"]):
                base = base[:-len(spec["stripSuffix"])]
            link = {"match": "CHILD_OF", "evidence": "MANIFEST_REFERENCE", "via": f"fullName {base}.*"}
        else:
            link = {"match": "FIELD_EQUALS_NAME", "evidence": "MANIFEST_REFERENCE",
                    "via": f"data.{spec['field']} = {full_name}"}
        for folder in spec.get("folders") or []:
            for item in _folder_index(settings, inv_dir, folder):
                if item["path"] in seen or (types and item["metadataType"] not in types):
                    continue
                if spec["match"] == "CHILD_OF":
                    ok = item["fullName"].startswith(base + ".")
                else:
                    ok = isinstance(item["data"], dict) and item["data"].get(spec["field"]) == full_name
                if ok:
                    seen.add(item["path"])
                    out.append(dict(item, link=link))
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
    entry["extraSources"] = related_sources(settings, component, full_name, entry["path"],
                                            settings.inventory_dir(alias, api_version))
    return entry


def load_all(settings, components, alias=None, api_version=None):
    return [load_component(settings, c, alias, api_version) for c in components]
