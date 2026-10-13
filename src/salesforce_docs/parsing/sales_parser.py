"""Leitura de metadata de Sales Cloud (Onda 08) — processo de negócio e conversão de Lead.

O XML é raw e só é lido.

- `BusinessProcess` (`Objeto.Processo`): objeto, nome e valores (`values/fullName`, `default`).
  Processo de negócio acompanha ciclos de vendas, lead, suporte e solução mostrando valores de
  picklist diferentes; o record type liga processo, valores e layouts (Metadata API).
- `LeadConvertSettings`: mapeamentos de campos do Lead para Account/Contact/Opportunity. Os nomes
  dos elementos não foram confirmados: a leitura é genérica — cada grupo repetido com filhos é um
  mapeamento de objeto; dentro dele, cada grupo com folhas `input*`/`output*` é um par de campos.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

PARSER_PROCESS = "business-process-xml/v1"
PARSER_LEAD_CONVERT = "lead-convert-xml/v1"


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _leaves(el):
    return {_local(c.tag): (c.text or "").strip() for c in el if not len(c)}


def parse_business_process(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_PROCESS, "parsed": False, "error": f"XML inválido: {exc}"}
    values = []
    for el in root:
        if _local(el.tag) == "values":
            leaves = _leaves(el)
            if leaves.get("fullName"):
                values.append({"value": leaves["fullName"], "default": leaves.get("default"),
                               "order": len(values) + 1})
    return {"parser": PARSER_PROCESS, "parsed": True, "values": values,
            "defaultValue": next((v["value"] for v in values if str(v["default"]).lower() == "true"), None)}


def parse_lead_convert(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_LEAD_CONVERT, "parsed": False, "error": f"XML inválido: {exc}"}
    mappings, objects = [], []
    for group in root:
        if not len(group):
            continue
        leaves = _leaves(group)
        src = next((v for k, v in leaves.items() if k.lower().startswith("input")), None)
        dst = next((v for k, v in leaves.items() if k.lower().startswith("output")), None)
        objects.append({"element": _local(group.tag), "inputObject": src, "outputObject": dst,
                        "details": "; ".join(f"{k}={v}" for k, v in leaves.items()
                                             if not k.lower().startswith(("input", "output"))) or None})
        for pair in group:
            if not len(pair):
                continue
            pl = _leaves(pair)
            fin = next((v for k, v in pl.items() if k.lower().startswith("input")), None)
            fout = next((v for k, v in pl.items() if k.lower().startswith("output")), None)
            mappings.append({"sourceObject": src, "sourceField": fin, "targetObject": dst, "targetField": fout,
                             "element": f"{_local(group.tag)}/{_local(pair.tag)}"})
    return {"parser": PARSER_LEAD_CONVERT, "parsed": True, "objectMappings": objects, "fieldMappings": mappings,
            # Nomes Objeto.Campo para cruzar com fieldPermissions (FLS) no índice de acesso.
            "sourceFieldNames": sorted({f"{m['sourceObject']}.{m['sourceField']}" for m in mappings
                                        if m["sourceObject"] and m["sourceField"]}),
            "targetFieldNames": sorted({f"{m['targetObject']}.{m['targetField']}" for m in mappings
                                        if m["targetObject"] and m["targetField"]})}
