"""Leitura de regras de atendimento (AssignmentRules, AutoResponseRules, EscalationRules) e de filas.

O XML é raw e só é lido. Os nomes dos elementos internos não foram confirmados na documentação
oficial nesta adaptação; por isso a leitura é genérica:
- cada filho da raiz que tem filhos é uma regra (`fullName`, `active` e demais folhas);
- cada `ruleEntry` é uma entrada, na ordem do XML (a plataforma avalia em ordem e para na
  primeira que casa); `criteriaItems` viram texto `campo operador valor`; grupos aninhados
  (ex.: `escalationAction`) viram ações;
- demais folhas aparecem como `nome=valor`.

Proteção de dados (nunca vão para a saída): usuário de destino (`assignedTo` quando o tipo é
User), usuários notificados e endereços/nomes de e-mail. No lugar, um texto "não documentado".
Fila: membros usuários só entram como contagem; e-mail da fila não é lido.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

PARSER_RULES = "service-rules-xml/v1"
PARSER_QUEUE = "queue-xml/v1"

# Folhas com dado pessoal: nunca renderizadas (substituídas por texto fixo).
PERSONAL_LEAVES = {
    "notifyto": "usuário(s) notificado(s) (não documentados)",
    "notifyemail": "e-mail(s) de notificação (não documentados)",
    "senderemail": "e-mail do remetente (não documentado)",
    "sendername": "nome do remetente (não documentado)",
    "replytoemail": "e-mail de resposta (não documentado)",
    "email": "e-mail (não documentado)",
}
USER_TYPES = {"user"}


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _leaf(el, name):
    for c in el:
        if _local(c.tag) == name:
            return (c.text or "").strip()
    return None


def _criteria(items):
    out = []
    for it in items:
        field = _leaf(it, "field") or "?"
        op = _leaf(it, "operation") or "?"
        value = _leaf(it, "value")
        if value is None:
            value = _leaf(it, "valueField")
        out.append(f"{field} {op} {value if value is not None else ''}".strip())
    return "; ".join(out) or None


def _destination(el):
    target, kind = _leaf(el, "assignedTo"), _leaf(el, "assignedToType")
    if target is None:
        return None
    if (kind or "").lower() in USER_TYPES:
        return f"{kind}: usuário (não documentado)"
    return f"{kind}: {target}" if kind else target


def _details(el, skip):
    """Folhas restantes como `nome=valor`; dado pessoal vira texto fixo (com contagem)."""
    parts, personal = [], {}
    for c in el:
        name = _local(c.tag)
        if len(c) or name in skip:
            continue
        if name.lower() in PERSONAL_LEAVES:
            personal[name.lower()] = personal.get(name.lower(), 0) + 1
            continue
        parts.append(f"{name}={(c.text or '').strip()}")
    parts += [f"{n} {PERSONAL_LEAVES[k]}" for k, n in personal.items()]
    return "; ".join(parts) or None


ENTRY_SKIP = {"assignedTo", "assignedToType", "booleanFilter", "formula"}


def parse_service_rules(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_RULES, "parsed": False, "error": f"XML inválido: {exc}"}
    rules, entries, actions, targets = [], [], [], []
    for rule in root:
        if not len(rule):
            continue
        name = _leaf(rule, "fullName")
        active = _leaf(rule, "active")
        rules.append({"rule": name, "kind": _local(rule.tag), "active": active,
                      "details": _details(rule, {"fullName", "active"})})
        order = 0
        for entry in rule:
            if _local(entry.tag) != "ruleEntry":
                continue
            order += 1
            crit = [c for c in entry if _local(c.tag) == "criteriaItems"]
            dest = _destination(entry)
            entries.append({"rule": name, "active": active, "order": order,
                            "criteria": _criteria(crit) or _leaf(entry, "formula") or "(sem critério: pega tudo)",
                            "logic": _leaf(entry, "booleanFilter"), "destination": dest,
                            "details": _details(entry, ENTRY_SKIP)})
            if dest and (_leaf(entry, "assignedToType") or "").lower() not in USER_TYPES:
                targets.append({"type": _leaf(entry, "assignedToType"), "name": _leaf(entry, "assignedTo"),
                                "rule": name, "order": order, "active": active})
            n = 0
            for group in entry:
                if not len(group) or _local(group.tag) == "criteriaItems":
                    continue
                n += 1
                adest = _destination(group)
                actions.append({"rule": name, "order": order, "action": f"{_local(group.tag)} {n}",
                                "destination": adest, "details": _details(group, ENTRY_SKIP)})
                if adest and (_leaf(group, "assignedToType") or "").lower() not in USER_TYPES:
                    targets.append({"type": _leaf(group, "assignedToType"), "name": _leaf(group, "assignedTo"),
                                    "rule": name, "order": order, "active": active})
    active_rules = [r["rule"] for r in rules if str(r["active"]).lower() == "true"]
    return {"parser": PARSER_RULES, "parsed": True, "rules": rules, "entries": entries, "actions": actions,
            "targets": targets, "activeRules": active_rules,
            "activeCheck": ("Uma regra ativa" if len(active_rules) == 1 else
                            "Nenhuma regra ativa" if not active_rules else
                            f"{len(active_rules)} regras ativas no XML (a plataforma mantém uma ativa por tipo)")}


def parse_queue(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"parser": PARSER_QUEUE, "parsed": False, "error": f"XML inválido: {exc}"}
    objects, members, users = [], [], 0
    for el in root:
        tag = _local(el.tag)
        if tag == "queueSobject":
            obj = _leaf(el, "sobjectType")
            if obj:
                objects.append(obj)
        elif tag == "queueMembers":
            for container in el:
                ctype = _local(container.tag)
                values = [(c.text or "").strip() for c in container if (c.text or "").strip()]
                if ctype.lower() == "users":
                    users += len(values)
                    continue
                members += [{"type": ctype, "name": v} for v in values]
    return {"parser": PARSER_QUEUE, "parsed": True, "objects": objects, "members": members,
            "userMembers": users,
            "userMembersText": f"{users} usuário(s) (não documentados)" if users else "Nenhum usuário direto",
            "routingConfig": _leaf(root, "queueRoutingConfig")}
