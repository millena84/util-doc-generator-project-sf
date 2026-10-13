"""Índice da execução: fatos de OUTROS componentes usados por um documento.

Usado pelo documento de Apex Trigger para mostrar:
- automações que convivem no mesmo objeto (Flows record-triggered, regras de validação e
  outras triggers), na ordem oficial de execução (config `automationIndex`);
- leituras de configuração e controles de segurança das classes chamadas pela trigger;
- se a classe referenciada existe no inventário de ApexClass da org.

Fonte: JSON normalizado (XML e código lidos) dos componentes processados na execução
(ou herdados na retomada). Nada é consultado fora do que foi recuperado: componente fora
do escopo não aparece, e o documento avisa isso.
"""

from __future__ import annotations

from salesforce_docs.utils import read_json


def _get(data, path, full_name=None):
    if path == "@fullName":
        return full_name
    if path == "@parent":
        return (full_name or "").split(".", 1)[0] or None
    cur = data
    for part in str(path).split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _text(value):
    if value is None or value == "":
        return None
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v not in (None, ""))
    return str(value)


def _automation_entries(cfg, metadata_type, full_name, data):
    out = []
    for src in cfg.get("sources") or []:
        if src.get("metadataType") != metadata_type:
            continue
        obj = _text(_get(data, src.get("objectPath", "@parent"), full_name))
        if not obj:
            continue
        phases = []
        if src.get("phase"):
            phases = [src["phase"]]
        elif src.get("phaseByPath"):
            pb = src["phaseByPath"]
            key = _text(_get(data, pb["path"], full_name))
            if key in (pb.get("map") or {}):
                phases = [pb["map"][key]]
        elif src.get("phaseByEvent"):
            pe = src["phaseByEvent"]
            for event in _get(data, pe["path"], full_name) or []:
                phase = (pe.get("map") or {}).get(str(event).lower())
                if phase and phase not in phases:
                    phases.append(phase)
        events = _get(data, src["eventsPath"], full_name) if src.get("eventsPath") else None
        for phase in phases:
            if src.get("phaseByEvent"):
                ev = [e for e in (events or [])
                      if (src["phaseByEvent"].get("map") or {}).get(str(e).lower()) == phase]
            else:
                ev = events
            out.append((obj.lower(), {
                "metadataType": metadata_type,
                "name": full_name,
                "kind": src.get("label") or metadata_type,
                "phase": phase,
                "events": _text(ev),
                "status": _text(_get(data, src["statusPath"], full_name)) if src.get("statusPath") else None,
                "orderValue": _text(_get(data, src["orderPath"], full_name)) if src.get("orderPath") else None,
            }))
    return out


def build_run_index(records, cfg, class_inventory=None, class_type="ApexClass", code_key="apex"):
    """records: iteráveis de {metadataType, fullName, data} (primários e filhos).

    class_inventory: nomes do inventário de ApexClass (None = inventário não listado).
    """
    cfg = cfg or {}
    index = {"automations": {}, "classes": {},
             "classInventory": sorted(class_inventory, key=str.lower) if class_inventory is not None else None,
             "phases": cfg.get("phases") or [], "reference": cfg.get("officialReference")}
    seen = set()
    for rec in records:
        key = (rec.get("metadataType"), rec.get("fullName"))
        if None in key or key in seen or not isinstance(rec.get("data"), dict):
            continue
        seen.add(key)
        data = rec["data"]
        for obj, entry in _automation_entries(cfg, key[0], key[1], data):
            index["automations"].setdefault(obj, []).append(entry)
        if key[0] == class_type and isinstance(data.get(code_key), dict) and data[code_key].get("parsed"):
            code = data[code_key]
            index["classes"][key[1].lower()] = {
                "name": key[1], "sharing": code.get("sharing"),
                "configReads": code.get("configReads") or [],
                "securityPatterns": code.get("securityPatterns") or [],
            }
    return index


def records_of(record):
    """Registro processado + filhos (ex.: ValidationRule do CustomObject)."""
    yield {"metadataType": record.get("metadataType"), "fullName": record.get("fullName"),
           "data": record.get("data")}
    for c in record.get("children") or []:
        yield {"metadataType": c.get("metadataType"), "fullName": c.get("fullName"), "data": c.get("data")}


def records_from_entries(entries, project_root):
    """Componentes herdados (retomada): lê o normalizado gravado (primário e filhos)."""
    for e in entries:
        if e.get("status") != "SUCCESS":
            continue
        items = [e] + list(e.get("children") or [])
        for item in items:
            path = item.get("normalized")
            if not path or not (project_root / path).is_file():
                continue
            norm = read_json(project_root / path) or {}
            yield {"metadataType": norm.get("metadataType") or item.get("metadataType"),
                   "fullName": norm.get("fullName") or item.get("fullName") or item.get("component"),
                   "data": norm.get("data")}
