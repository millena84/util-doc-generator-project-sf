"""Leitura do membro de canal de eventos (`PlatformEventChannelMember`) — Change Data Capture.

O XML é raw e só é lido. Extrai `eventChannel`, `selectedEntity`, `enrichedFields` e
`filterExpression` e deriva, só pela convenção de nomes documentada:
- objeto de origem: `AccountChangeEvent` -> `Account`; `Pedido__ChangeEvent` -> `Pedido__c`;
- tipo de canal: `ChangeEvents` = canal padrão do CDC; outro nome = canal customizado.

Fontes oficiais: Change Data Capture Developer Guide ("Example Diagrams for Channels and Channel
Members", "Enrich Change Events with Extra Fields", "Add a Filter with Metadata API").
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

PARSER_ID = "event-channel-member-xml/v1"
STANDARD_CHANNEL = "ChangeEvents"


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def base_object(entity: str | None):
    """Objeto que gera o change event, pela convenção de nomes (None se não for change event)."""
    if not entity:
        return None
    if entity.endswith("__ChangeEvent"):
        return entity[: -len("__ChangeEvent")] + "__c"
    if entity.endswith("ChangeEvent"):
        return entity[: -len("ChangeEvent")] or None
    return None


def parse_event_channel_member(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_ID, "parsed": False, "error": f"XML inválido: {exc}"}
    values, enriched = {}, []
    for el in root:
        tag = _local(el.tag)
        if tag == "enrichedFields":
            name = next(((c.text or "").strip() for c in el if _local(c.tag) == "name"), None)
            if name:
                enriched.append(name)
        elif len(el) == 0:
            values[tag] = (el.text or "").strip()
    entity, channel = values.get("selectedEntity"), values.get("eventChannel")
    channel_name = (channel or "").split("/")[-1]
    return {
        "parser": PARSER_ID,
        "parsed": True,
        "selectedEntity": entity,
        "eventChannel": channel,
        "filterExpression": values.get("filterExpression"),
        "enrichedFields": enriched,
        "baseObject": base_object(entity),
        "isChangeEvent": base_object(entity) is not None,
        "channelKind": None if not channel else (
            "Canal padrão do CDC (ChangeEvents)" if channel_name == STANDARD_CHANNEL else "Canal customizado"),
    }
