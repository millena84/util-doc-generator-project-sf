"""Leitura de metadata do OmniStudio (Onda 10) — DataRaptor, Integration Procedure, OmniScript e FlexCard.

Formato lido: o XML da Metadata API (`OmniDataTransform`, `OmniIntegrationProcedure`, `OmniScript`,
`OmniUiCard`), recuperado por `sf project retrieve`. Os `.json` do Vlocity Build Tool (datapacks do
pacote gerenciado) não são lidos. O XML é raw e só é lido; os nomes de elemento não foram
confirmados na documentação oficial nesta adaptação, por isso a leitura é genérica:

- folhas da raiz como estão (o contrato escolhe o que mostrar);
- elementos de processo (`omniProcessElements`, aninhados em `childElements`): nome, tipo, nível,
  ordem no XML e as referências encontradas no `propertySetConfig` (texto JSON);
- itens do DataRaptor (`omniDataTransformItem`): objeto/campo de entrada e de saída, filtro e se há
  fórmula;
- FlexCard: fonte de dados (`dataSourceConfig`) e ações (`actionList` no `propertySetConfig`).

Segurança: o texto de `propertySetConfig`, `dataSourceConfig` e `sampleDataSourceResponse` nunca
vai para a saída (pode ter cabeçalhos HTTP, valores fixos e dados de exemplo). Só as referências
extraídas (nomes de componentes) entram no normalizado.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

PARSER_PROCESS = "omni-process-xml/v1"
PARSER_TRANSFORM = "omni-data-transform-xml/v1"
PARSER_CARD = "omni-ui-card-xml/v1"

# Chave no JSON de configuração -> tipo de componente referenciado (nomes a confirmar no piloto).
REFERENCE_KEYS = {
    "bundle": "DataRaptor",
    "integrationProcedureKey": "Integration Procedure",
    "ipMethod": "Integration Procedure",
    "remoteClass": "Classe Apex",
    "namedCredential": "Named Credential",
}
ELEMENT_CONTAINERS = ("omniProcessElements", "childElements")
CONFIG_TEXTS = ("propertySetConfig", "dataSourceConfig", "sampleDataSourceResponse")


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _leaves(el):
    return {_local(c.tag): (c.text or "").strip() for c in el if not len(c)}


def _json(text):
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


def _references(node, element=None, out=None):
    """Referências (tipo, nome, elemento) em qualquer nível de um JSON de configuração."""
    out = [] if out is None else out
    if isinstance(node, dict):
        for k, v in node.items():
            if k in REFERENCE_KEYS and isinstance(v, str) and v.strip():
                out.append({"kind": REFERENCE_KEYS[k], "name": v.strip(), "element": element, "key": k})
            else:
                _references(v, element, out)
    elif isinstance(node, list):
        for v in node:
            _references(v, element, out)
    return out


def _dedupe(refs):
    seen, out = set(), []
    for r in refs:
        key = (r["kind"], r["name"], r.get("element"))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def _root_summary(root):
    leaves = _leaves(root)
    key = "_".join(v for v in (leaves.get("type"), leaves.get("subType")) if v) or None
    return leaves, key


def parse_omni_process(text: str) -> dict:
    """Integration Procedure e OmniScript (mesma estrutura de processo)."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_PROCESS, "parsed": False, "error": f"XML inválido: {exc}"}
    leaves, key = _root_summary(root)
    elements, refs = [], []

    def walk(el, parent, level):
        for c in el:
            if _local(c.tag) not in ELEMENT_CONTAINERS:
                continue
            lv = _leaves(c)
            name = lv.get("name") or None
            config = _json(lv.get("propertySetConfig"))
            found = _dedupe(_references(config, name)) if config is not None else []
            refs.extend(found)
            elements.append({
                "order": len(elements) + 1, "name": name, "type": lv.get("type") or None,
                "level": lv.get("level") or level, "parent": parent, "active": lv.get("isActive") or None,
                "sequence": lv.get("sequenceNumber") or None,
                "references": "; ".join(f"{r['kind']} {r['name']}" for r in found) or None,
                "config": "não lida (JSON inválido)" if lv.get("propertySetConfig") and config is None else None,
            })
            walk(c, name, (int(level) + 1) if str(level).isdigit() else level)

    walk(root, None, 0)
    return {"parser": PARSER_PROCESS, "parsed": True, "procedureKey": key, "elements": elements,
            "references": _dedupe(refs), **_reference_names(refs)}


def _reference_names(refs):
    by_kind = {}
    for r in refs:
        by_kind.setdefault(r["kind"], set()).add(r["name"])
    return {"apexClasses": sorted(by_kind.get("Classe Apex", ())),
            "namedCredentials": sorted(by_kind.get("Named Credential", ())),
            "dataRaptors": sorted(by_kind.get("DataRaptor", ())),
            "integrationProcedures": sorted(by_kind.get("Integration Procedure", ()))}


def parse_data_transform(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_TRANSFORM, "parsed": False, "error": f"XML inválido: {exc}"}
    leaves = _leaves(root)
    items = []
    for c in root:
        if _local(c.tag) != "omniDataTransformItem":
            continue
        lv = _leaves(c)
        flt = " ".join(v for v in (lv.get("filterOperator"), lv.get("filterValue")) if v) or None
        items.append({
            "order": len(items) + 1, "inputObject": lv.get("inputObjectName") or None,
            "inputField": lv.get("inputFieldName") or None, "outputObject": lv.get("outputObjectName") or None,
            "outputField": lv.get("outputFieldName") or None, "filter": flt,
            "formula": "Sim" if lv.get("formulaExpression") else None,
            "lookupObject": lv.get("lookupObjectName") or None,
        })
    kind = (leaves.get("type") or "").lower()
    # Extract/Turbo leem os objetos de entrada; Load grava nos objetos de saída. Transform não usa o banco.
    read = sorted({i["inputObject"] for i in items if i["inputObject"] and ("extract" in kind or "turbo" in kind)}
                  | {i["lookupObject"] for i in items if i["lookupObject"]})
    written = sorted({i["outputObject"] for i in items if i["outputObject"] and "load" in kind})
    return {"parser": PARSER_TRANSFORM, "parsed": True, "items": items, "objectsRead": read,
            "objectsWritten": written, "name": leaves.get("name") or None}


def _actions(node, out, refs):
    """Ações (`actionList`) em qualquer nível; as referências de cada ação levam o rótulo dela."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "actionList" and isinstance(v, list):
                for a in v:
                    if isinstance(a, dict):
                        state = a.get("stateAction") if isinstance(a.get("stateAction"), dict) else {}
                        found = _dedupe(_references(a, a.get("label")))
                        refs.extend(found)
                        out.append({"label": a.get("label"), "type": state.get("type") or a.get("type"),
                                    "references": "; ".join(f"{r['kind']} {r['name']}" for r in found) or None})
            else:
                _actions(v, out, refs)
    elif isinstance(node, list):
        for v in node:
            _actions(v, out, refs)
    return out


def parse_ui_card(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_CARD, "parsed": False, "error": f"XML inválido: {exc}"}
    leaves = _leaves(root)
    source = _json(leaves.get("dataSourceConfig"))
    props = _json(leaves.get("propertySetConfig"))
    source_refs = _dedupe(_references(source, "Fonte de dados")) if source is not None else []
    action_refs = []
    actions = _actions(props, [], action_refs) if props is not None else []
    refs = _dedupe(source_refs + action_refs)
    return {"parser": PARSER_CARD, "parsed": True,
            "dataSourceType": source.get("type") if isinstance(source, dict) else None,
            "dataSource": "; ".join(f"{r['kind']} {r['name']}" for r in source_refs) or None,
            "actions": actions, "references": refs, **_reference_names(refs)}
