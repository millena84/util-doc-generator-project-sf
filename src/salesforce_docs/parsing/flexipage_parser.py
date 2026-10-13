"""Leitura estrutural de FlexiPage (`.flexipage-meta.xml`) — regiões, componentes e visibilidade.

O XML é raw e só é lido. O parser achata a árvore (regiões → itemInstances → componentInstance
ou fieldInstance) em listas para o documento, sem inventar elementos: cada valor vem do XML.
Aceita o formato com `itemInstances` e o antigo, com `componentInstances` direto na região.

Referências extraídas: componentes `c:` (LWC/Aura do projeto), Flows (`flowruntime:interview`,
propriedade `flowName`) e Custom Permissions usadas em regras de visibilidade
(`$Permission.CustomPermission.<Nome>`). Contexto do critério (Record, User, Permission,
Client...) vem do texto de `leftValue`, com ou sem `{!` e `$`.

Fontes oficiais: Metadata API "FlexiPage"; Salesforce Help "Visibility Rules on Lightning Pages".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

PARSER_ID = "flexipage-xml/v1"
CUSTOM_PERMISSION_RE = re.compile(r"\$?Permission\.CustomPermission\.([A-Za-z0-9_]+)")
CONTEXT_RE = re.compile(r"^\{?!?\s*\$?([A-Za-z]+)")


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _text(el, name):
    for child in el:
        if _local(child.tag) == name:
            return (child.text or "").strip()
    return None


def _children(el, name):
    return [c for c in el if _local(c.tag) == name]


def component_kind(name: str) -> str:
    low = (name or "").lower()
    if low == "flowruntime:interview":
        return "Flow"
    if low.startswith("c:"):
        return "Componente do projeto (c:)"
    if low.split(":", 1)[0] in ("force", "flexipage", "forcecommunity", "console", "runtime_sales_activities",
                                "lightning", "home", "runtime_sales_pipelineboard", "platform"):
        return "Componente da plataforma"
    if ":" in low:
        return f"Componente de namespace ({low.split(':', 1)[0]})"
    return "Outro"


def _context(left):
    m = CONTEXT_RE.match(left or "")
    return m.group(1) if m else None


def parse_flexipage(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_ID, "parsed": False, "error": f"XML inválido: {exc}"}
    template = next((_text(t, "name") for t in _children(root, "template")), None)
    regions, components, properties, visibility, fields = [], [], [], [], []
    flows, perms = [], []
    for region in _children(root, "flexiPageRegions"):
        rname, rtype = _text(region, "name"), _text(region, "type")
        instances = []
        for item in _children(region, "itemInstances"):
            instances += [("component", c) for c in _children(item, "componentInstance")]
            instances += [("field", f) for f in _children(item, "fieldInstance")]
        instances += [("component", c) for c in _children(region, "componentInstances")]  # formato antigo
        regions.append({"name": rname, "type": rtype, "mode": _text(region, "mode"), "items": len(instances)})
        for kind, inst in instances:
            ident = _text(inst, "identifier")
            rules = _children(inst, "visibilityRule")
            if kind == "field":
                fields.append({"region": rname, "field": _text(inst, "fieldItem"), "identifier": ident,
                               "hasVisibility": "Sim" if rules else "Não"})
            else:
                cname = _text(inst, "componentName")
                components.append({"region": rname, "regionType": rtype, "componentName": cname,
                                   "identifier": ident, "kind": component_kind(cname),
                                   "hasVisibility": "Sim" if rules else "Não"})
                for prop in _children(inst, "componentInstanceProperties"):
                    pname, pvalue = _text(prop, "name"), _text(prop, "value")
                    properties.append({"identifier": ident, "componentName": cname, "name": pname,
                                       "value": pvalue})
                    if (cname or "").lower() == "flowruntime:interview" and pname == "flowName" and pvalue:
                        flows.append(pvalue)
            for rule in rules:
                logic = _text(rule, "booleanFilter")
                for crit in _children(rule, "criteria"):
                    left = _text(crit, "leftValue")
                    visibility.append({"identifier": ident, "booleanFilter": logic, "leftValue": left,
                                       "operator": _text(crit, "operator"), "rightValue": _text(crit, "rightValue"),
                                       "context": _context(left)})
                    perms += CUSTOM_PERMISSION_RE.findall(left or "")
    return {
        "parser": PARSER_ID,
        "parsed": True,
        "template": template,
        "regions": regions,
        "components": components,
        "componentProperties": properties,
        "fields": fields,
        "visibility": visibility,
        "projectComponents": sorted({c["componentName"][2:] for c in components
                                     if (c["componentName"] or "").lower().startswith("c:")}),
        "flows": sorted(set(flows)),
        "customPermissions": sorted(set(perms)),
    }
