"""Aplica os desvios declarados em config/metadata-types-mvp.json.

- monta as unidades de documento conforme `documentStrategy`;
- resolve componentes relacionados conforme `relations` (evidência no XML ou
  nos componentes recuperados — nunca por suposição);
- resolve subdocumentos (`subDocuments`).
"""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.parsing.custom_metadata_parser import group_records_by_type
from salesforce_docs.parsing.custom_object_parser import child_files
from salesforce_docs.parsing.external_client_app_parser import (field_equals_primary, leaf_values,
                                                                reference_scan, values_at)
from salesforce_docs.parsing.flow_parser import flow_definition_matches
from salesforce_docs.parsing.generic_builders import matches_conditions
from salesforce_docs.parsing.xml_parser import as_list


class DocumentUnit(dict):
    """Uma unidade = um documento principal."""


def build_units(group, inventories, mvp):
    primary_items = inventories.get(group.primary_type) or []
    fixed = group.data.get("fixedComponents")
    if fixed:
        # Componente único conhecido (ex.: Settings:Security): sem inventário; o retrieve usa
        # retrieveType:fullName e a pasta/documento seguem o tipo principal do grupo.
        return [DocumentUnit(
            unitId=f"{group.name}:{group.primary_type}:{c['fullName']}", group=group.name,
            metadataType=c.get("retrieveType") or group.primary_type, documentType=group.primary_type,
            fullName=c["fullName"], inventoryItem={}, records=[]) for c in fixed]
    if group.unit_mode == "PER_COMPONENT":
        units = []
        for item in primary_items:
            name = item["fullName"]
            if not group.accepts(name):
                continue
            units.append(DocumentUnit(
                unitId=f"{group.name}:{group.primary_type}:{name}", group=group.name,
                metadataType=group.primary_type, documentType=group.primary_type,
                fullName=name, inventoryItem=item, records=[]))
        return units
    if group.unit_mode == "PER_TYPE_WITH_RECORDS":
        td = group.type_definition
        by_name = {i["fullName"]: i for i in primary_items}
        grouped = group_records_by_type(by_name.keys(), td.get("recordSeparator", "."),
                                        td.get("typeNameSuffix", "__mdt"))
        units = []
        for type_name, records in grouped.items():
            if not group.accepts(type_name):
                continue
            units.append(DocumentUnit(
                unitId=f"{group.name}:{group.primary_type}:{type_name}", group=group.name,
                metadataType=td["metadataType"], documentType=group.primary_type,
                fullName=type_name, inventoryItem={}, records=[by_name[r] for r in records]))
        return units
    raise ValueError(f"unit_mode desconhecido: {group.unit_mode}")


def _related_from_record(rec):
    return {"metadataType": rec["metadataType"], "fullName": rec["fullName"],
            "data": rec.get("data"), "schemaFields": rec.get("schemaFields"),
            "files": rec.get("files", []), "xml": rec.get("xml"),
            "normalized": rec.get("normalized"), "status": rec.get("status"),
            "retrieveRaw": rec.get("retrieveRaw")}


# Relações que só se comprovam lendo o XML de CADA candidato (exigem retrieve de
# componentes que podem não pertencer ao principal selecionado).
CANDIDATE_SCAN_MATCHES = ("FIELD_EQUALS_PRIMARY", "REFERENCE_SCAN")


def resolve_related(unit, primary, group, processor, inventories, enabled_types, log,
                    restrict_candidates=False, unresolved=None):
    """Retorna (related, failures). `failures` são componentes candidatos que falharam.

    restrict_candidates=True (selection.mode = SELECTED): relações em
    CANDIDATE_SCAN_MATCHES NÃO recuperam candidatos (nada fora da seleção é recuperado);
    a lacuna é anexada a `unresolved`.
    """
    related, failures = [], []

    def fetch(metadata_type, item):
        rec = processor.process(metadata_type, item["fullName"], item, role="related")
        if rec["status"] != st.SUCCESS:
            failures.append(rec)
            return None
        return rec

    # Records (ONE_DOCUMENT_PER_TYPE_AND_RECORDS)
    for item in unit.get("records") or []:
        rec = fetch(unit["documentType"], item)
        if rec:
            related.append(_related_from_record(rec))

    for rel_cfg in group.relations:
        rtype = rel_cfg["metadataType"]
        if rtype not in enabled_types:
            continue
        match = rel_cfg["match"]
        if match == "CHILD_OF_PRIMARY":
            by_path = {c["xml"]: c for c in primary.get("children", [])}
            for f in child_files(primary.get("files", []), primary["fullName"], rtype):
                child = by_path.get(f["path"])
                if child:
                    related.append(dict(child, status=st.SUCCESS))
            continue
        candidates = inventories.get(rtype) or []
        if restrict_candidates and match in CANDIDATE_SCAN_MATCHES:
            if candidates and unresolved is not None:
                unresolved.append({
                    "metadataType": rtype, "match": match, "candidates": len(candidates),
                    "reason": "selection.mode = SELECTED: o vínculo só se comprova lendo o XML de cada "
                              "candidato; candidatos fora da seleção não são recuperados"})
            continue
        if match == "SAME_FULL_NAME":
            for item in candidates:
                if item["fullName"] != primary["fullName"]:
                    continue
                rec = fetch(rtype, item)
                if rec and flow_definition_matches(primary["fullName"], primary.get("data"),
                                                   {"fullName": rec["fullName"]}):
                    related.append(_related_from_record(rec))
        elif match == "FIELD_EQUALS_PRIMARY":
            for item in candidates:
                rec = fetch(rtype, item)
                if rec and field_equals_primary(primary["fullName"], rec.get("data"), rel_cfg["field"]):
                    related.append(_related_from_record(rec))
        elif match == "PRIMARY_FIELD_REFERENCES":
            # Relação comprovada pelo XML do principal: o valor exato em `field` é o fullName
            # de um componente existente no inventário do tipo relacionado.
            referenced = values_at(primary.get("data") or {}, rel_cfg["field"])
            for item in candidates:
                if item["fullName"] in referenced:
                    rec = fetch(rtype, item)
                    if rec:
                        related.append(_related_from_record(rec))
        elif match == "REFERENCE_SCAN":
            primary_values = leaf_values(primary.get("data") or {})
            for item in candidates:
                if item["fullName"] in primary_values:
                    rec = fetch(rtype, item)
                    if rec:
                        related.append(_related_from_record(rec))
                    continue
                rec = fetch(rtype, item)
                if rec and reference_scan(primary["fullName"], primary.get("data"),
                                          rec["fullName"], rec.get("data")):
                    related.append(_related_from_record(rec))
    if failures:
        log.warn(f"{unit['unitId']}: {len(failures)} componente(s) relacionado(s) candidato(s) falharam")
    return related, failures


def sub_document_targets(group, primary_data, primary_full_name):
    """[(subdoc_cfg, item_data|None, item_name|None)] conforme `subDocuments`."""
    targets = []
    for sub in group.sub_documents:
        if sub.get("forEach"):
            cur = primary_data or {}
            for part in sub["forEach"].split("."):  # caminho pontuado (ex.: apex.futureMethods)
                cur = cur.get(part) if isinstance(cur, dict) else None
            for item in as_list(cur):
                if isinstance(item, dict):
                    name = item.get(sub.get("itemName", "name"))
                    if name:
                        targets.append((sub, item, name))
        elif sub.get("when"):
            # `when`: condição ou lista de condições (todas devem valer) sobre o XML do Flow:
            # {path, present} | {path, equals} | {path, in} | {path, contains}
            conds = sub["when"] if isinstance(sub["when"], list) else [sub["when"]]
            conds = [dict(c, present=c.get("present", True))
                     if not ({"equals", "in", "present", "contains"} & set(c)) else c for c in conds]
            if matches_conditions(primary_data or {}, conds):
                targets.append((sub, None, None))
        else:
            targets.append((sub, None, None))
    return targets
