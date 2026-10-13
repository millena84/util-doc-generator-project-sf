"""Builders que usam o índice da execução (`run_index`): documentos de Apex Trigger e LWC.

- `automation_rows`: automações no mesmo objeto, na ordem oficial de execução
  (fases em `automationIndex.phases`, config/metadata-types-mvp.json);
- `referenced_class_rows`: classes chamadas pela trigger, conferidas no inventário de ApexClass;
- `code_fact_rows`: fatos de código (leituras de configuração, controles de segurança) da
  trigger e das classes que ela chama, quando essas classes foram processadas na execução.

Sem índice (ex.: documento renderizado fora do pipeline): "Não informado".
"""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.rendering.context import format_value, resolve

DASH = "—"
BUILDER_PLACEHOLDERS = {
    "automation_rows": ("exec_order", "exec_phase", "automation_type", "automation_name",
                        "automation_events", "automation_status", "automation_order_detail"),
    "referenced_class_rows": ("class_name", "class_reference", "class_members", "class_in_org"),
    "apex_method_check_rows": ("apex_class", "apex_method", "aura_enabled", "method_modifiers",
                               "apex_check"),
}


def _index(ctx):
    return getattr(ctx.root(), "run_index", None)


def _confirmed(index, name):
    """True/False quando o inventário de ApexClass foi listado; None = não verificado."""
    inv = (index or {}).get("classInventory")
    if inv is None:
        return None
    return name.lower() in {n.lower() for n in inv}


def _classes(ctx, path, index):
    value, _ = resolve(ctx, path)
    out = []
    for item in value or []:
        if isinstance(item, dict) and item.get("className"):
            if _confirmed(index, item["className"]) is False:
                continue  # não é classe da org (ex.: sObject padrão, classe de sistema)
            out.append(item)
    return out


def automation_rows(ctx, args):
    """args: objectPath (objeto do componente), metadataType (tipo do próprio documento)."""
    index = _index(ctx)
    obj, _ = resolve(ctx, args.get("objectPath", "apex.sObject"))
    if index is None or not obj:
        return []
    phases = index.get("phases") or []
    pos = {p["key"]: i for i, p in enumerate(phases)}
    by_key = {p["key"]: p for p in phases}
    root = ctx.root()
    rows = []
    entries = sorted(index["automations"].get(str(obj).lower(), []),
                     key=lambda e: (pos.get(e["phase"], len(pos)), e["kind"], e["name"].lower()))
    for e in entries:
        phase = by_key.get(e["phase"], {})
        own = e["metadataType"] == args.get("metadataType") and e["name"] == root.full_name
        detail = []
        if e.get("orderValue"):
            detail.append(f"{phase.get('orderValueLabel', 'Ordem')} {e['orderValue']}")
        if phase.get("note"):
            detail.append(phase["note"])
        rows.append({
            "exec_order": str(phase["order"]) if phase.get("order") is not None else "Não confirmado",
            "exec_phase": phase.get("label") or e["phase"],
            "automation_type": e["kind"],
            "automation_name": e["name"] + (" (este documento)" if own else ""),
            "automation_events": e.get("events") or DASH,
            "automation_status": e.get("status") or st.NOT_INFORMED,
            "automation_order_detail": "; ".join(detail) or DASH,
        })
    return rows


def referenced_class_rows(ctx, args):
    """args: path (lista apex.referencedClasses)."""
    index = _index(ctx)
    rows = []
    for item in _classes(ctx, args.get("path", "apex.referencedClasses"), index):
        confirmed = _confirmed(index, item["className"])
        rows.append({
            "class_name": item["className"],
            "class_reference": ", ".join(item.get("references") or []) or DASH,
            "class_members": ", ".join(item.get("members") or []) or DASH,
            "class_in_org": "Sim (inventário ApexClass)" if confirmed else
            "Não verificado (inventário ApexClass não listado)",
        })
    return rows


def code_fact_rows(ctx, args):
    """Fatos de código da própria trigger e das classes que ela chama.

    args: path (lista no código do componente, ex.: apex.configReads), classKey (mesma lista
    no índice da classe, ex.: configReads), classesPath, locationPlaceholder, columns
    {placeholder: campo}, emptyClassText.
    """
    index = _index(ctx)
    loc = args.get("locationPlaceholder", "fact_location")
    columns = args.get("columns") or {}
    rows = []
    own, own_state = resolve(ctx, args["path"])
    root = ctx.root()
    for item in own or []:
        row = {loc: f"Trigger {root.full_name}"}
        row.update({ph: format_value(item.get(f)) or DASH for ph, f in columns.items()})
        rows.append(row)
    if index is None:
        return rows
    for cls in _classes(ctx, args.get("classesPath", "apex.referencedClasses"), index):
        info = index["classes"].get(cls["className"].lower())
        if info is None:
            row = {ph: None for ph in columns}
            row[loc] = f"Classe {cls['className']}"
            first = next(iter(columns), None)
            if first:
                row[first] = args.get("emptyClassText", "Classe não processada nesta execução")
            rows.append(row)
            continue
        for item in info.get(args["classKey"]) or []:
            row = {loc: f"Classe {info['name']}"}
            row.update({ph: format_value(item.get(f)) or DASH for ph, f in columns.items()})
            rows.append(row)
    if not rows and own_state == "PRESENT":
        row = {ph: DASH for ph in columns}
        row[loc] = "Nenhuma ocorrência no código lido"
        rows.append(row)
    return rows


def apex_method_check_rows(ctx, args):
    """Métodos Apex chamados (ex.: LWC) conferidos no código da classe processada na execução.

    Regras (LWC Developer Guide, "Call Apex Methods" / "Wire Apex Methods to Components"): o método
    precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, `cacheable=true`.
    args: path (lista com className, method, wire).
    """
    index = _index(ctx)
    value, _ = resolve(ctx, args.get("path", "lwc.apexMethods"))
    if index is None:
        return []
    calls = {}
    for item in value or []:
        if not isinstance(item, dict) or not item.get("className") or not item.get("method"):
            continue
        key = (item["className"], item["method"])
        calls[key] = calls.get(key, False) or bool(item.get("wire"))
    rows = []
    for (cls, method), wired in calls.items():
        row = {"apex_class": cls, "apex_method": method}
        info = index["classes"].get(cls.lower())
        if info is None:
            row["aura_enabled"] = "Classe não processada nesta execução"
            rows.append(row)
            continue
        m = (info.get("methods") or {}).get(method.lower())
        if m is None:
            row["aura_enabled"] = "Método não encontrado na leitura da classe"
            rows.append(row)
            continue
        aura = next((a for a in m["annotations"] if str(a.get("name", "")).lower() == "auraenabled"), None)
        cacheable = aura is not None and (aura.get("params") or {}).get("cacheable") == "true"
        mods = m.get("modifiers") or []
        problems = []
        if aura is None:
            problems.append("sem @AuraEnabled")
        if wired and not cacheable:
            problems.append("@wire exige @AuraEnabled(cacheable=true)")
        if "static" not in mods:
            problems.append("método não é static")
        if not {"public", "global"} & set(mods):
            problems.append("método não é public/global")
        row.update(aura_enabled=("Sim (cacheable=true)" if cacheable else "Sim") if aura else "Não",
                   method_modifiers=", ".join(mods) or DASH,
                   apex_check="Atende" if not problems else "Não atende: " + "; ".join(problems))
        rows.append(row)
    return rows


TABLE_BUILDERS = {"automation_rows": automation_rows, "referenced_class_rows": referenced_class_rows,
                  "code_fact_rows": code_fact_rows, "apex_method_check_rows": apex_method_check_rows}
BLOCK_BUILDERS = {}
