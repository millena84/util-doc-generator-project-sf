"""Leitura estrutural de triggers Apex (`.trigger`) — sem executar nem renderizar o código.

Mesmas regras do parser de classes (`apex_parser`): o arquivo é raw e só é lido;
comentários e strings são neutralizados; comparação case-insensitive; o corpo da
trigger nunca vai para a saída.

Extrai: nome, objeto (`on <sObject>`), eventos declarados, variáveis de contexto
`Trigger.*` usadas, classes referenciadas (`new X(`, `X.metodo(`, `variavel.metodo(` com
declaração local), leituras de configuração e controles de segurança explícitos.

Não extrai (não verificável por leitura estática): se o código é "bulkificado" ou se há
controle de recursão. Eventos e variáveis de contexto: Apex Developer Guide, "Triggers" e
"Trigger Context Variables".
"""

from __future__ import annotations

import re

from salesforce_docs.parsing.apex_parser import (IDENT, QUALIFIED, _apexdoc, config_reads, neutralize,
                                                 platform_event_refs, security_patterns)

PARSER_ID = "apex-trigger-lexical/v1"

TRIGGER_RE = re.compile(rf"\btrigger\s+({IDENT})\s+on\s+({QUALIFIED})\s*\(([^)]*)\)\s*\{{", re.I)

# Eventos aceitos na declaração `trigger X on Obj (eventos)`.
EVENTS = ("before insert", "before update", "before delete",
          "after insert", "after update", "after delete", "after undelete")

# Nome canônico das variáveis de contexto (chave em minúsculas).
CONTEXT_VARIABLES = {
    "isexecuting": "Trigger.isExecuting", "isinsert": "Trigger.isInsert",
    "isupdate": "Trigger.isUpdate", "isdelete": "Trigger.isDelete",
    "isbefore": "Trigger.isBefore", "isafter": "Trigger.isAfter",
    "isundelete": "Trigger.isUndelete", "new": "Trigger.new", "newmap": "Trigger.newMap",
    "old": "Trigger.old", "oldmap": "Trigger.oldMap", "operationtype": "Trigger.operationType",
    "size": "Trigger.size",
}

# Namespaces/classes de sistema que não são classes da org (comparação em minúsculas).
SYSTEM_TYPES = {
    "trigger", "system", "database", "schema", "featuremanagement", "test", "limits", "userinfo",
    "json", "string", "math", "date", "datetime", "time", "integer", "decimal", "long", "double",
    "boolean", "id", "blob", "object", "crypto", "encodingutil", "http", "httprequest",
    "httpresponse", "messaging", "eventbus", "type", "set", "list", "map", "url", "triggeroperation",
    "approval", "auth", "site", "apexpages", "cache", "search", "connectapi", "formula",
    "pattern", "matcher", "label", "dmlexception", "exception", "queryexception", "security",
    "accesslevel", "sobject", "sobjecttype", "sobjectfield", "domain", "request", "logginglevel",
    "this", "super",
}
KEYWORDS = {"return", "new", "else", "throw", "if", "for", "while", "do", "switch", "when", "case",
            "insert", "update", "delete", "undelete", "upsert", "merge", "final", "static"}


def _is_candidate(name: str, sobject: str | None) -> bool:
    low = name.lower()
    return (low not in SYSTEM_TYPES and low not in KEYWORDS and "__" not in low
            and low != (sobject or "").lower())


def _variables(code: str):
    """Variáveis declaradas no corpo: nome (minúsculas) -> tipo declarado."""
    out = {}
    for m in re.finditer(rf"(?<![\w.])({QUALIFIED})(?:\s*<[^;=(){{}}]*>)?\s+({IDENT})\s*(?:=|;)", code):
        typ, var = m.group(1), m.group(2)
        if typ.lower() in KEYWORDS:
            continue
        out.setdefault(var.lower(), typ)
    return out


def _referenced_classes(code: str, sobject: str | None):
    """Classes referenciadas: `new X(`, `X.metodo(` e `v.metodo(` (v declarada como `X v`)."""
    variables = _variables(code)
    found = {}

    def add(name, reference, member=None):
        if not _is_candidate(name, sobject):
            return
        item = found.setdefault(name.lower(), {"className": name, "references": [], "members": []})
        if reference not in item["references"]:
            item["references"].append(reference)
        if member and member not in item["members"]:
            item["members"].append(member)

    for m in re.finditer(rf"\bnew\s+({IDENT})\s*\(", code, re.I):
        add(m.group(1), "instância (new)")
    for m in re.finditer(rf"(?<![\w.])({IDENT})\s*\.\s*({IDENT})\s*\(", code):
        target, member = m.group(1), m.group(2)
        declared = variables.get(target.lower())
        if declared is not None:
            add(declared.split(".")[-1], "instância (variável)", member)
        else:
            add(target, "chamada estática", member)
    return sorted(found.values(), key=lambda c: c["className"].lower())


def parse_apex_trigger(text: str) -> dict:
    code, literals, docs = neutralize(text)
    m = TRIGGER_RE.search(code)
    if not m:
        return {"parser": PARSER_ID, "parsed": False, "error": "declaração de trigger não encontrada"}
    declared = [re.sub(r"\s+", " ", e).strip().lower() for e in m.group(3).split(",") if e.strip()]
    events = [e for e in EVENTS if e in declared]
    body = code[m.end():]
    doc = None
    for pos, raw in docs:
        if pos <= m.start():
            doc = raw
    used = set()
    for v in re.finditer(rf"\bTrigger\s*\.\s*({IDENT})\b", body, re.I):
        name = CONTEXT_VARIABLES.get(v.group(1).lower())
        if name:
            used.add(name)
    sobject = m.group(2)
    return {
        "parser": PARSER_ID,
        "parsed": True,
        "kind": "trigger",
        "triggerName": m.group(1),
        "sObject": sobject,
        "description": _apexdoc(doc) if doc else None,
        "events": events,
        "unknownEvents": [e for e in declared if e not in EVENTS],
        "eventRows": [{"event": e, "timing": e.split()[0], "operation": e.split()[1]} for e in events],
        "contextVariables": [v for v in CONTEXT_VARIABLES.values() if v in used],
        "referencedClasses": _referenced_classes(body, sobject),
        "configReads": config_reads(body, literals),
        "securityPatterns": security_patterns(body),
        "platformEvents": platform_event_refs(body),
    }
