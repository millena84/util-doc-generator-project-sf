"""Leitura estrutural de Lightning Web Components (bundle `lwc/<nome>/`) — sem executar código.

Entrada: {caminho relativo no bundle: texto} com `.js`, `.html` e `<nome>.js-meta.xml`.
Os arquivos são raw: só são lidos. Testes Jest (`__tests__/`) são ignorados.

Regras (iguais às do parser Apex):
- comentários e literais de string do JavaScript são neutralizados antes da análise
  (texto em comentário não é evidência); o código nunca vai para a saída;
- só fatos estruturais: imports `@salesforce/*` e `lightning/*`, membros `@api`, adaptadores
  `@wire`, hooks de ciclo de vida, eventos criados com nome literal, componentes usados no
  HTML e a configuração do `.js-meta.xml` (inclusive atributos de `targetConfig`/`property`,
  que o normalizador XML genérico não guarda).

Fontes oficiais: LWC Developer Guide — "XML Configuration File Elements", "@salesforce
Modules", "Configure a Component for Flow Screens", "Configure a Component for Quick Actions",
"Create Headless Quick Actions", "Wire Apex Methods to Components".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath

PARSER_ID = "lwc-lexical/v1"
IDENT = r"[A-Za-z_$][A-Za-z0-9_$]*"
TOKEN = "§S{}§"
TOKEN_RE = re.compile("§S(\\d+)§")

LIFECYCLE_HOOKS = ("constructor", "connectedCallback", "renderedCallback", "disconnectedCallback",
                   "errorCallback")
# Componentes base que leem/gravam registro pelo Lightning Data Service.
LDS_BASE_COMPONENTS = ("lightning-record-form", "lightning-record-edit-form", "lightning-record-view-form",
                       "lightning-input-field", "lightning-output-field", "lightning-record-picker")


# ---------------------------------------------------------------------------
# Léxico JavaScript
# ---------------------------------------------------------------------------
def neutralize_js(text: str):
    """Remove comentários e troca strings ('', "", ``) por marcadores. Retorna (código, literais)."""
    out, literals = [], []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "/" and nxt == "*":
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            out.append(" ")
            continue
        if c in "'\"`":
            j, buf = i + 1, []
            while j < n and text[j] != c:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                buf.append(text[j])
                j += 1
            literals.append("".join(buf))
            out.append(c + TOKEN.format(len(literals) - 1) + c)
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out), literals


def _lit(token_text, literals):
    m = TOKEN_RE.search(token_text or "")
    return literals[int(m.group(1))] if m else None


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
IMPORT_RE = re.compile(r"\bimport\s+([^;]*?)\s+from\s+(['\"])(§S\d+§)\2", re.S)
SIDE_IMPORT_RE = re.compile(r"\bimport\s+(['\"])(§S\d+§)\1")


def _import_names(clause: str):
    """{nome local: nome importado} de `default, { a as b }, * as ns`."""
    names = {}
    clause = clause.strip()
    braces = re.search(r"\{([^}]*)\}", clause)
    if braces:
        for part in braces.group(1).split(","):
            part = part.strip()
            if not part:
                continue
            m = re.fullmatch(rf"({IDENT})\s+as\s+({IDENT})", part)
            if m:
                names[m.group(2)] = m.group(1)
            else:
                names[part] = part
        clause = clause[:braces.start()] + clause[braces.end():]
    star = re.search(rf"\*\s+as\s+({IDENT})", clause)
    if star:
        names[star.group(1)] = "*"
        clause = clause[:star.start()] + clause[star.end():]
    default = clause.strip().strip(",").strip()
    if re.fullmatch(IDENT, default or ""):
        names[default] = "default"
    return names


def module_kind(module: str) -> str:
    if module.startswith("@salesforce/apex/"):
        return "Apex"
    if module.startswith("@salesforce/"):
        return "@salesforce/" + module.split("/")[1]
    if module.startswith("lightning/ui") or module == "lightning/graphql":
        return "Lightning Data Service"
    if module.startswith("lightning/"):
        return "Módulo da plataforma"
    if module.startswith("c/"):
        return "Componente/módulo do projeto"
    if module == "lwc":
        return "Núcleo LWC"
    return "Outro"


def _imports(code, literals):
    out = []
    for m in IMPORT_RE.finditer(code):
        module = _lit(m.group(3), literals)
        out.append({"module": module, "kind": module_kind(module), "names": _import_names(m.group(1))})
    for m in SIDE_IMPORT_RE.finditer(code):
        module = _lit(m.group(2), literals)
        out.append({"module": module, "kind": module_kind(module), "names": {}})
    return out


# ---------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------
def _api_members(code):
    out, seen = [], set()
    for m in re.finditer(rf"@api\s+(?:(get|set)\s+)?({IDENT})\s*(\()?", code):
        accessor, name, paren = m.group(1), m.group(2), m.group(3)
        if name in ("get", "set", "static"):
            continue
        kind = "getter/setter" if accessor else ("método" if paren else "propriedade")
        if name not in seen:
            seen.add(name)
            out.append({"name": name, "kind": kind})
    return out


def _hooks(code):
    return [h for h in LIFECYCLE_HOOKS if re.search(rf"(?<![.\w]){h}\s*\([^)]*\)\s*\{{", code)]


def _parse_js(code, literals, imports):
    local = {}  # nome local -> (módulo, nome importado)
    for imp in imports:
        for loc, orig in imp["names"].items():
            local[loc] = (imp["module"], orig)
    wires = []
    for m in re.finditer(rf"@wire\s*\(\s*({IDENT})", code):
        module = local.get(m.group(1), (None, None))[0]
        wires.append({"adapter": m.group(1), "module": module})
    apex = []
    for loc, (module, _orig) in local.items():
        if not module.startswith("@salesforce/apex/"):
            continue
        ref = module[len("@salesforce/apex/"):]
        cls, _, method = ref.rpartition(".")
        usage = []
        if re.search(rf"@wire\s*\(\s*{re.escape(loc)}\b", code):
            usage.append("@wire")
        if re.search(rf"(?<![\w.$]){re.escape(loc)}\s*\(", code):
            usage.append("imperativo")
        apex.append({"className": cls or None, "method": method, "importName": loc,
                     "usage": ", ".join(usage) or "importado, uso não detectado",
                     "wire": "@wire" in usage})
    events = []
    for m in re.finditer(r"\bnew\s+CustomEvent\s*\(\s*(['\"`])(§S\d+§)\1", code):
        events.append({"kind": "Evento customizado", "name": _lit(m.group(2), literals), "detail": "CustomEvent"})
    for m in re.finditer(rf"\bnew\s+({IDENT})\s*\(", code):
        module = local.get(m.group(1), (None, None))[0]
        if module and module.startswith("lightning/") and m.group(1).endswith("Event"):
            events.append({"kind": "Evento da plataforma", "name": m.group(1), "detail": module})
    dyn = len(re.findall(r"\bnew\s+CustomEvent\s*\(\s*(?!['\"`])", code))
    if dyn:
        events.append({"kind": "Evento customizado", "name": None, "detail": f"nome não literal ({dyn}x)"})
    calls = {name: bool(re.search(rf"(?<![\w.$]){name}\s*\(", code))
             for name in ("publish", "subscribe", "unsubscribe")}
    return {"wires": wires, "apex": apex, "events": _dedupe(events), "lmsCalls": calls,
            "api": _api_members(code), "hooks": _hooks(code)}


def _dedupe(rows):
    out, seen = [], set()
    for r in rows:
        key = tuple(sorted((k, str(v)) for k, v in r.items()))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def _parse_html(text):
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    tags = set(m.group(1).lower() for m in re.finditer(r"<((?:c|lightning)-[a-z0-9-]+)", text, re.I))
    children = sorted(t for t in tags if t.startswith("c-"))
    base = sorted(t for t in tags if t.startswith("lightning-"))
    return children, base


def _kebab_to_module(tag):
    parts = tag.split("-")[1:]
    return "c/" + parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


# ---------------------------------------------------------------------------
# .js-meta.xml (com atributos)
# ---------------------------------------------------------------------------
def _local(tag):
    return tag.rsplit("}", 1)[-1]


PROPERTY_ATTRS = ("name", "type", "label", "role", "required", "default", "datasource", "placeholder")


def _parse_meta(text):
    root = ET.fromstring(text)
    out = {"targets": [], "targetConfigs": []}
    for el in root:
        tag = _local(el.tag)
        if tag == "targets":
            out["targets"] = [(t.text or "").strip() for t in el if _local(t.tag) == "target"]
        elif tag == "targetConfigs":
            for tc in el:
                if _local(tc.tag) != "targetConfig":
                    continue
                cfg = {"targets": [t.strip() for t in (tc.get("targets") or "").split(",") if t.strip()],
                       "properties": [], "objects": [], "actionType": None, "supportedFormFactors": [],
                       "other": []}
                for child in tc:
                    ctag = _local(child.tag)
                    if ctag == "property":
                        cfg["properties"].append({a: child.get(a) for a in PROPERTY_ATTRS if child.get(a) is not None})
                    elif ctag == "objects":
                        cfg["objects"] = [(o.text or "").strip() for o in child if _local(o.tag) == "object"]
                    elif ctag == "actionType":
                        cfg["actionType"] = (child.text or "").strip()
                    elif ctag == "supportedFormFactors":
                        cfg["supportedFormFactors"] = [f.get("type") for f in child
                                                       if _local(f.tag) == "supportedFormFactor"]
                    else:
                        cfg["other"].append(ctag)
                out["targetConfigs"].append(cfg)
    return out


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------
def _kind_of(path):
    if path.endswith(".js-meta.xml"):
        return "Configuração (.js-meta.xml)"
    if path.endswith(".js"):
        return "JavaScript"
    if path.endswith(".html"):
        return "Template HTML"
    if path.endswith(".css"):
        return "CSS"
    if path.endswith(".svg"):
        return "Ícone SVG"
    return "Outro"


def parse_lwc_bundle(files: dict) -> dict:
    files = {p: t for p, t in files.items() if "__tests__" not in PurePosixPath(p).parts}
    meta_path = next((p for p in files if p.endswith(".js-meta.xml")), None)
    if meta_path is None:
        return {"parser": PARSER_ID, "parsed": False, "error": "arquivo .js-meta.xml não encontrado no bundle"}
    try:
        meta = _parse_meta(files[meta_path])
    except ET.ParseError as exc:
        return {"parser": PARSER_ID, "parsed": False, "error": f".js-meta.xml inválido: {exc}"}
    imports, api, hooks, wires, apex, events = [], [], [], [], [], []
    lms = {"publish": False, "subscribe": False, "unsubscribe": False}
    children, base = set(), set()
    for path in sorted(files):
        if path.endswith(".js"):
            code, literals = neutralize_js(files[path])
            imps = _imports(code, literals)
            js = _parse_js(code, literals, imps)
            imports += imps
            api += [a for a in js["api"] if a["name"] not in {x["name"] for x in api}]
            hooks += [h for h in js["hooks"] if h not in hooks]
            wires += js["wires"]
            apex += js["apex"]
            events += js["events"]
            lms = {k: lms[k] or v for k, v in js["lmsCalls"].items()}
        elif path.endswith(".html"):
            c, b = _parse_html(files[path])
            children.update(c)
            base.update(b)

    by_kind = {}
    for imp in imports:
        by_kind.setdefault(imp["kind"], []).append(imp["module"])

    def names_after(prefix):
        return sorted({m[len(prefix):] for m in by_kind.get("@salesforce/" + prefix.split("/")[1], [])
                       if m.startswith(prefix)})

    custom_perms = names_after("@salesforce/customPermission/")
    user_perms = names_after("@salesforce/userPermission/")
    channels = names_after("@salesforce/messageChannel/")

    data_access = []
    for m in sorted(set(by_kind.get("Lightning Data Service", []))):
        data_access.append({"kind": "Módulo LDS (UI API)", "name": m, "detail": "—"})
    for w in wires:
        if w["module"] and module_kind(w["module"]) == "Lightning Data Service":
            data_access.append({"kind": "Adaptador @wire", "name": w["adapter"], "detail": w["module"]})
    for ref in names_after("@salesforce/schema/"):
        data_access.append({"kind": "Referência de schema", "name": ref,
                            "detail": "campo" if "." in ref else "objeto"})
    for tag in sorted(base):
        if tag in LDS_BASE_COMPONENTS:
            data_access.append({"kind": "Componente base LDS (HTML)", "name": tag, "detail": "—"})
    data_access = _dedupe(data_access)

    ops = ", ".join(k for k in ("publish", "subscribe", "unsubscribe") if lms[k]) or "—"
    communication = list(events)
    communication += [{"kind": "Message channel (LMS)", "name": c, "detail": f"chamadas no componente: {ops}"}
                      for c in channels]
    communication += [{"kind": "Componente filho (HTML)", "name": _kebab_to_module(t), "detail": t}
                      for t in sorted(children)]
    communication += [{"kind": "Módulo do projeto (import)", "name": m, "detail": "—"}
                      for m in sorted(set(by_kind.get("Componente/módulo do projeto", [])))]

    target_props, restrictions = [], []
    for cfg in meta["targetConfigs"]:
        targets = ", ".join(cfg["targets"])
        for p in cfg["properties"]:
            target_props.append(dict(p, targets=targets,
                                     roleText=p.get("role") or "entrada e saída (role ausente)",
                                     hasApi=_has_api(p.get("name"), api)))
        for o in cfg["objects"]:
            restrictions.append({"targets": targets, "kind": "Objeto", "value": o})
        if cfg["actionType"]:
            restrictions.append({"targets": targets, "kind": "Tipo de ação (actionType)", "value": cfg["actionType"]})
        for f in cfg["supportedFormFactors"]:
            restrictions.append({"targets": targets, "kind": "Form factor", "value": f})
        for o in cfg["other"]:
            restrictions.append({"targets": targets, "kind": "Outro elemento", "value": o})

    api_names = {a["name"] for a in api}
    action_cfg = next((c for c in meta["targetConfigs"] if "lightning__RecordAction" in c["targets"]), None)
    action_type = action_cfg["actionType"] if action_cfg else None
    has_invoke = any(a["name"] == "invoke" and a["kind"] == "método" for a in api)
    if (action_type or "ScreenAction") == "Action":
        headless = "Atende: @api invoke() declarado" if has_invoke else \
            "Não atende: actionType Action sem @api invoke()"
    else:
        headless = "Não aplicável (ScreenAction)"
    flow_events = [e for e in events if e.get("detail") == "lightning/flowSupport"]
    action_events = [e for e in events if e.get("detail") == "lightning/actions"]

    return {
        "parser": PARSER_ID,
        "parsed": True,
        "files": [{"path": p, "kind": _kind_of(p)} for p in sorted(files)],
        "targets": meta["targets"],
        "targetConfigs": meta["targetConfigs"],
        "targetProperties": target_props,
        "targetRestrictions": restrictions,
        "imports": [{"module": i["module"], "kind": i["kind"]} for i in _dedupe(
            [{"module": i["module"], "kind": i["kind"]} for i in imports])],
        "apiMembers": api,
        "lifecycleHooks": hooks,
        "wireAdapters": wires,
        "apexMethods": apex,
        "apexClasses": sorted({a["className"] for a in apex if a["className"]}),
        "dataAccess": data_access,
        "communication": communication,
        "customPermissions": custom_perms,
        "permissionChecks": [{"kind": "Custom Permission", "name": n} for n in custom_perms] +
                            [{"kind": "User Permission", "name": n} for n in user_perms],
        "messageChannels": channels,
        "quickAction": {
            "actionType": action_type,
            "hasInvoke": has_invoke,
            "headlessCheck": headless,
            "recordIdApi": "recordId" in api_names,
            "closeEvents": [e["name"] for e in action_events],
            "propertiesDeclared": len(action_cfg["properties"]) if action_cfg else 0,
        },
        "flowScreen": {
            "properties": [p for p in target_props if "lightning__FlowScreen" in p["targets"].split(", ")],
            "hasValidate": any(a["name"] == "validate" and a["kind"] == "método" for a in api),
            "flowEvents": [e["name"] for e in flow_events],
        },
    }


def _has_api(name, api):
    if not name:
        return None
    return "Sim" if any(a["name"] == name for a in api) else "Não"
