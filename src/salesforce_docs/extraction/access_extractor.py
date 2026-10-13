"""Onde cada componente está configurado: índice de acesso a partir do XML.

Fontes (config `accessSources` em config/metadata-types-mvp.json):
- Profile e PermissionSet: elementos de concessão (`classAccesses`, `flowAccesses`,
  `objectPermissions`, `fieldPermissions`, ...) → quem concede acesso a qual componente;
- PermissionSetGroup: permission sets do grupo → acesso "via" grupo;
- Queue: objetos aceitos pela fila; SharingRules: regras por objeto (role, grupo, fila...).

Todos os XMLs são recuperados num retrieve único junto com os componentes documentados:
o XML de Profile (e possivelmente de PermissionSet) só traz permissões dos componentes
presentes no mesmo retrieve. Os arquivos ficam intactos (raw); o índice é derivado e
regenerável a partir deles. Usuários atribuídos (PermissionSetAssignment) não entram.
"""

from __future__ import annotations

from pathlib import Path

from salesforce_docs.extraction.xml_retriever import retrieve_specs
from salesforce_docs.parsing.xml_parser import as_list, parse_xml_file
from salesforce_docs.utils import rel, write_json

TRUE = ("true", "1")


def _is_true(value) -> bool:
    return str(value).strip().lower() in TRUE


def access_specs(cfg, doc_specs, available_types):
    """Especificações do retrieve: tipos de origem de acesso (todos) + componentes documentados."""
    specs = [t for t in cfg.get("retrieveTypes", []) if t in available_types]
    missing = [t for t in cfg.get("retrieveTypes", []) if t not in available_types]
    # Tipo de origem que também é documentado (ex.: PermissionSet) já está coberto por `Tipo`.
    extra = sorted({s for s in doc_specs if s not in specs and s.split(":", 1)[0] not in specs})
    return specs + extra, missing


def retrieve_access_sources(runner, session, specs, access_dir, errors_dir, project_root):
    return retrieve_specs(runner, session, specs, components_dir=access_dir / "components",
                          raw_path=access_dir / "retrieve.raw.json",
                          errors_raw_path=errors_dir / "access-sources.raw.json",
                          project_root=project_root)


def _empty_index():
    return {"grants": {}, "permissionSetGroups": {}, "queues": {}, "sharingRules": {}, "sourceFiles": []}


def _add(index, key, name, row):
    index["grants"].setdefault(key, {}).setdefault(name, [])
    if row not in index["grants"][key][name]:
        index["grants"][key][name].append(row)


def build_access_index(files, project_root, cfg):
    """Índice derivado: {grants: {chave: {componente: [linhas]}}, queues, sharingRules, ...}."""
    root = Path(project_root)
    index = _empty_index()
    containers = cfg.get("grantContainers") or {}
    psg_cfg = cfg.get("permissionSetGroups") or {}
    queue_cfg = cfg.get("queues") or {}
    rules_cfg = cfg.get("sharingRules") or {}
    by_type = {}
    for f in files:
        if str(f.get("path", "")).endswith(".xml"):
            by_type.setdefault(f.get("type"), []).append(f)
            index["sourceFiles"].append({"type": f.get("type"), "fullName": f.get("fullName"),
                                         "path": f.get("path"), "sha256": f.get("sha256")})
    # Permission set groups: PS -> [grupos]
    groups_of = {}
    for f in by_type.get(psg_cfg.get("metadataType"), []):
        _, data = parse_xml_file(root / f["path"])
        for ps in as_list(data.get(psg_cfg.get("element"))):
            if isinstance(ps, str) and ps:
                groups_of.setdefault(ps, []).append(f["fullName"])
                index["permissionSetGroups"].setdefault(ps, []).append(f["fullName"])
    # Concessões em Profile / PermissionSet
    for ctype, label in containers.items():
        for f in by_type.get(ctype, []):
            _, data = parse_xml_file(root / f["path"])
            for g in cfg.get("grants", []):
                for item in as_list(data.get(g["element"])):
                    if not isinstance(item, dict):
                        continue
                    name = item.get(g["nameField"])
                    if not name:
                        continue
                    if g.get("flags"):
                        granted = [lbl for fld, lbl in g["flags"].items() if _is_true(item.get(fld))]
                    elif _is_true(item.get(g.get("enabledField", "enabled"))):
                        granted = [g.get("accessLabel", "Habilitado")]
                    else:
                        granted = []
                    if not granted:
                        continue  # acesso explicitamente desabilitado não é concessão
                    access = ", ".join(granted)
                    row = {"originType": label, "origin": f["fullName"], "access": access, "via": None,
                           "source": f["path"]}
                    _add(index, g["accessKey"], name, row)
                    if ctype == "PermissionSet":
                        for psg in groups_of.get(f["fullName"], []):
                            _add(index, g["accessKey"], name,
                                 {"originType": psg_cfg.get("label", "Permission Set Group"), "origin": psg,
                                  "access": access, "via": f"Permission Set {f['fullName']}",
                                  "source": f["path"]})
    # Onde o próprio permission set está configurado: grupos que o incluem
    for ps, psgs in groups_of.items():
        for psg in psgs:
            _add(index, "PermissionSet", ps, {"originType": psg_cfg.get("label", "Permission Set Group"),
                                              "origin": psg, "access": "Inclui o permission set",
                                              "via": None, "source": None})
    # Filas: objeto -> filas
    for f in by_type.get(queue_cfg.get("metadataType"), []):
        _, data = parse_xml_file(root / f["path"])
        for item in as_list(data.get(queue_cfg.get("element"))):
            obj = item.get(queue_cfg.get("field")) if isinstance(item, dict) else None
            if obj:
                index["queues"].setdefault(obj, []).append(
                    {"kind": queue_cfg.get("label", "Fila"), "name": f["fullName"], "sharedTo": None,
                     "accessLevel": None, "source": f["path"]})
    # Regras de compartilhamento: arquivo por objeto
    for f in by_type.get(rules_cfg.get("metadataType"), []):
        _, data = parse_xml_file(root / f["path"])
        for element, label in (rules_cfg.get("elements") or {}).items():
            for rule in as_list(data.get(element)):
                if not isinstance(rule, dict):
                    continue
                shared = rule.get(rules_cfg.get("sharedTo", "sharedTo"))
                targets = []
                if isinstance(shared, dict):
                    for ttype, tval in shared.items():
                        for v in as_list(tval):
                            targets.append(f"{ttype}: {v}")
                index["sharingRules"].setdefault(f["fullName"], []).append(
                    {"kind": label, "name": rule.get("fullName") or rule.get("label"),
                     "sharedTo": "; ".join(targets) or None,
                     "accessLevel": rule.get(rules_cfg.get("accessLevel", "accessLevel")),
                     "source": f["path"]})
    for key in index["grants"]:
        for name in index["grants"][key]:
            index["grants"][key][name].sort(key=lambda r: (r["originType"], r["origin"], r["via"] or ""))
    return index


def save_access_index(index, access_dir, project_root, retrieve_raw=None):
    index = dict(index, retrieveRaw=retrieve_raw)
    path = Path(access_dir) / "access-index.json"
    write_json(path, index, private=True)
    return rel(path, project_root)
