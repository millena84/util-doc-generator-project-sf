"""Leitura de metadata de Experience Cloud (Onda 09) — Network, CustomSite e ExperienceBundle.

O XML/JSON é raw e só é lido. Os nomes de elemento não foram confirmados na documentação oficial
nesta adaptação; o que não está no arquivo fica "Não informado" (nada é deduzido do nome).

- `Network` (`networks/X.network-meta.xml`): membros (`networkMemberGroups` com `profile` /
  `permissionSet`), perfil de autorregistro, site (`site`) e templates de e-mail (folhas `*Template`).
- `CustomSite` (`sites/X.site-meta.xml`): perfil de convidado (`guestProfile`, se houver).
- `ExperienceBundle` (`experiences/X.site-meta.xml` + `experiences/X/**.json`): páginas (`views`),
  rotas (`routes`), componentes embarcados e referências de público/visibilidade.

Proteção de dados (nunca vão para a saída): usuários (administrador do site, dono padrão dos
registros de convidado) e endereço/nome do remetente de e-mail. No lugar, só "configurado".
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath

PARSER_NETWORK = "network-xml/v1"
PARSER_SITE = "custom-site-xml/v1"
PARSER_BUNDLE = "experience-bundle/v1"

MEMBER_LABELS = {"profile": "Perfil", "permissionset": "Permission Set"}
# Folhas com usuário ou e-mail: só se registra que estão configuradas.
SITE_USERS = {"siteadmin": "Administrador do site (siteAdmin)",
              "siteguestrecorddefaultowner": "Dono padrão dos registros de convidado (siteGuestRecordDefaultOwner)"}
NETWORK_SENDER = ("emailsenderaddress", "emailsendername", "emailsenderemail")
TARGETING_HINTS = ("audience", "visibility")


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _text(el):
    return (el.text or "").strip()


def parse_network(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_NETWORK, "parsed": False, "error": f"XML inválido: {exc}"}
    members, templates, leaves = [], [], {}
    sender = False
    for el in root:
        name = _local(el.tag)
        if name == "networkMemberGroups":
            for m in el:
                if _text(m):
                    members.append({"type": MEMBER_LABELS.get(_local(m.tag).lower(), _local(m.tag)),
                                    "name": _text(m)})
        elif not len(el):
            if name.lower() in NETWORK_SENDER:
                sender = sender or bool(_text(el))
            elif name.endswith("Template") and _text(el):
                templates.append({"element": name, "template": _text(el)})
            else:
                leaves[name] = _text(el)
    if leaves.get("selfRegProfile"):
        members.append({"type": "Perfil de autorregistro", "name": leaves["selfRegProfile"]})
    return {"parser": PARSER_NETWORK, "parsed": True, "members": members, "emailTemplates": templates,
            "site": leaves.get("site") or None, "selfRegProfile": leaves.get("selfRegProfile") or None,
            "emailSender": "Configurado (não documentado)" if sender else None}


def parse_custom_site(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_SITE, "parsed": False, "error": f"XML inválido: {exc}"}
    users, guest = [], None
    for el in root:
        name = _local(el.tag)
        if len(el):
            continue
        if name.lower() in SITE_USERS:
            users.append({"role": SITE_USERS[name.lower()],
                          "state": "Configurado (usuário não documentado)" if _text(el) else "Não configurado"})
        elif name == "guestProfile" and _text(el):
            guest = _text(el)
    return {"parser": PARSER_SITE, "parsed": True, "siteUsers": users, "guestProfile": guest}


def _walk_components(node, region, out, targeting, view):
    """Componentes de uma view (regiões aninhadas), com referências de público/visibilidade."""
    if isinstance(node, list):
        for item in node:
            _walk_components(item, region, out, targeting, view)
        return
    if not isinstance(node, dict):
        return
    if node.get("type") == "region" and node.get("name"):
        region = node["name"]
    if node.get("componentName") and node.get("type") == "component":
        out.append({"view": view, "region": region, "componentName": node["componentName"],
                    "identifier": node.get("id")})
        for k, v in node.items():
            if any(h in k.lower() for h in TARGETING_HINTS):
                targeting.append({"view": view, "component": node["componentName"], "key": k,
                                  "value": v if isinstance(v, (str, int, float, bool)) else "presente (estrutura)"})
    for k in ("regions", "components"):
        if k in node:
            _walk_components(node[k], region, out, targeting, view)


def parse_experience_bundle(texts: dict) -> dict:
    """texts: {caminho relativo à pasta do XML principal: conteúdo} (`X.site-meta.xml`, `X/views/a.json`...)."""
    views, routes, components, targeting, folders, errors = [], [], [], [], {}, []
    for name in sorted(texts):
        parts = PurePosixPath(name).parts
        if len(parts) < 3 or not name.endswith(".json"):
            continue  # XML principal (lido pelo normalizador) ou arquivo fora de subpasta
        folder = parts[1]
        folders[folder] = folders.get(folder, 0) + 1
        if folder not in ("views", "routes"):
            continue
        try:
            data = json.loads(texts[name])
        except ValueError as exc:
            errors.append(f"{name}: JSON inválido ({exc})")
            continue
        if not isinstance(data, dict):
            continue
        file_id = PurePosixPath(name).stem
        if folder == "views":
            view = data.get("id") or file_id
            found = []
            _walk_components(data.get("regions") or [], None, found, targeting, view)
            components.extend(found)
            views.append({"view": view, "file": "/".join(parts[1:]), "label": data.get("label"),
                          "layout": data.get("componentName"), "viewType": data.get("viewType"),
                          "components": len(found)})
        else:
            routes.append({"route": data.get("id") or file_id, "file": "/".join(parts[1:]),
                           # "" no JSON é um valor (raiz do site), não ausência
                           "label": data.get("label"), "urlPrefix": "(vazio)" if data.get("urlPrefix") == "" else data.get("urlPrefix"),
                           "pageAccess": data.get("pageAccess"), "routeType": data.get("routeType"),
                           "activeViewId": data.get("activeViewId")})
    custom = sorted({c["componentName"].split(":", 1)[1] for c in components
                     if c["componentName"].lower().startswith("c:")}, key=str.lower)
    return {"parser": PARSER_BUNDLE, "parsed": not errors or bool(views or routes),
            "error": "; ".join(errors) or None, "views": views, "routes": routes,
            "components": components, "customComponents": custom, "targeting": targeting,
            "folders": [{"folder": k, "files": v} for k, v in sorted(folders.items())]}
