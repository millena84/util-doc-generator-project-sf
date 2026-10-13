"""Leitura estrutural de classes Apex (`.cls`) — sem executar nem renderizar o código.

Regras:
- o arquivo `.cls` é raw: nunca é alterado; este módulo só lê;
- comentários e literais de string são neutralizados antes da análise, para que um
  `implements Database.Batchable` dentro de comentário ou string não conte como evidência;
- Apex não diferencia maiúsculas/minúsculas: comparações são case-insensitive e as
  interfaces conhecidas são devolvidas no nome canônico;
- só fatos estruturais são extraídos (assinaturas, anotações, interfaces, chamadas
  assíncronas com argumentos literais). O corpo dos métodos nunca vai para a saída;
- o que não é literal (ex.: SOQL montado em tempo de execução, classe guardada em
  variável sem declaração local) é marcado como dinâmico, nunca inferido.

Interfaces e métodos confirmados no Apex Developer Guide (Batch Apex, Queueable,
Schedulable, Transaction Finalizers, `@future`).
"""

from __future__ import annotations

import re

PARSER_ID = "apex-lexical/v1"

# Nome canônico das interfaces relevantes (chave em minúsculas, sem o prefixo opcional `System.`).
KNOWN_INTERFACES = {
    "database.batchable": "Database.Batchable",
    "database.stateful": "Database.Stateful",
    "database.allowscallouts": "Database.AllowsCallouts",
    "database.raisesplatformevents": "Database.RaisesPlatformEvents",
    "queueable": "System.Queueable",
    "schedulable": "System.Schedulable",
    "finalizer": "System.Finalizer",
}

MODIFIERS = ("public", "private", "protected", "global", "static", "virtual", "abstract", "override",
             "final", "transient", "webservice", "testmethod")
SHARING_RE = re.compile(r"\b(with|without|inherited)\s+sharing\b", re.I)
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
QUALIFIED = rf"{IDENT}(?:\.{IDENT})*"
STRING_TOKEN = "§S{}§"  # marcador do literal de string N no código neutralizado
STRING_TOKEN_RE = re.compile("§S(\\d+)§")


# ---------------------------------------------------------------------------
# Léxico
# ---------------------------------------------------------------------------
def neutralize(text: str):
    """Remove comentários e substitui strings por marcadores.

    Retorna (código, literais, comentários_doc) — `comentários_doc` lista (posição, texto)
    dos blocos `/** ... */`, usados para a descrição ApexDoc.
    """
    out, literals, docs = [], [], []
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
            j = n if j < 0 else j + 2
            if text.startswith("/**", i) and not text.startswith("/**/", i):
                docs.append((len("".join(out)), text[i + 3:j - 2]))
            out.append(" ")
            i = j
            continue
        if c == "'":
            j, buf = i + 1, []
            while j < n and text[j] != "'":
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                buf.append(text[j])
                j += 1
            literals.append(_unescape("".join(buf)))
            out.append("'" + STRING_TOKEN.format(len(literals) - 1) + "'")
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out), literals, docs


def _unescape(s: str) -> str:
    """Interpreta as sequências de escape de string Apex (\\', \\\\, \\n, \\t...)."""
    table = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}
    return re.sub(r"\\(.)", lambda m: table.get(m.group(1), m.group(1)), s)


def restore(code: str, literals) -> str:
    return STRING_TOKEN_RE.sub(lambda m: literals[int(m.group(1))], code)


def _literal(arg: str, literals):
    """Valor de um argumento que é exatamente um literal de string (senão None)."""
    m = re.fullmatch(r"\s*'" + STRING_TOKEN_RE.pattern + r"'\s*", arg)
    return literals[int(m.group(1))] if m else None


def _match_close(code: str, start: int, open_ch="{", close_ch="}") -> int:
    """Índice do fechamento correspondente a code[start] (== open_ch); -1 se não houver."""
    depth = 0
    for i in range(start, len(code)):
        if code[i] == open_ch:
            depth += 1
        elif code[i] == close_ch:
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_top(s: str, sep=","):
    """Divide por `sep` fora de <>, (), [] e {}."""
    parts, depth, buf = [], 0, []
    for ch in s:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    if "".join(buf).strip():
        parts.append("".join(buf).strip())
    return parts


def canonical_interface(name: str) -> str:
    base = re.sub(r"\s+", "", name.split("<", 1)[0])
    key = base.lower()
    if key.startswith("system."):
        key = key[len("system."):]
    return KNOWN_INTERFACES.get(key, base)


# ---------------------------------------------------------------------------
# Anotações, assinaturas e corpo
# ---------------------------------------------------------------------------
ANNOTATION_RE = re.compile(rf"@({QUALIFIED})(\s*\(([^)]*)\))?", re.I)


def _annotations(text: str):
    out = []
    for m in ANNOTATION_RE.finditer(text):
        params = {k.lower(): v.lower() for k, v in
                  re.findall(r"(\w+)\s*=\s*([^\s,]+)", m.group(3) or "")}
        out.append({"name": m.group(1), "params": params})
    return out


def _strip_annotations(text: str) -> str:
    return ANNOTATION_RE.sub(" ", text)


def _params(text: str):
    out = []
    for p in _split_top(text):
        p = re.sub(r"\bfinal\s+", "", p, flags=re.I).strip()
        m = re.fullmatch(rf"(.+?)\s+({IDENT})", p, flags=re.S)
        if m:
            out.append({"type": re.sub(r"\s+", "", m.group(1)), "name": m.group(2)})
    return out


def _signature(name, params):
    return f"{name}({', '.join(p['type'] + ' ' + p['name'] for p in params)})"


def _members(body: str, class_name: str):
    """Declarações no nível 1 do corpo da classe: (kind, info, corpo)."""
    members, i, start = [], 0, 0
    while i < len(body):
        ch = body[i]
        if ch in ";}":
            start = i + 1
        elif ch == "{":
            header = body[start:i].strip()
            close = _match_close(body, i)
            if close < 0:
                break
            members.append((header, body[i + 1:close]))
            i = close + 1
            start = i
            continue
        i += 1
    out = []
    for header, inner in members:
        annotations = _annotations(header)
        bare = re.sub(r"\s+", " ", _strip_annotations(header)).strip()
        if re.search(r"\b(class|interface|enum)\b", bare, re.I):
            m = re.search(rf"\b(?:class|interface|enum)\s+({IDENT})", bare, re.I)
            out.append(("inner", {"name": m.group(1) if m else bare}, ""))
            continue
        m = re.fullmatch(rf"((?:(?:{'|'.join(MODIFIERS)})\s+)*)(?:(.+?)\s+)?({IDENT})\s*\((.*)\)", bare,
                         flags=re.I | re.S)
        if not m:
            continue  # propriedade { get; set; }, bloco de inicialização etc.
        mods = [x.lower() for x in m.group(1).split()]
        ret, name, params = m.group(2), m.group(3), _params(m.group(4))
        if ret is None and name.lower() == class_name.lower():
            out.append(("constructor", {"modifiers": mods, "parameters": params,
                                        "annotations": annotations}, inner))
        elif ret is not None:
            out.append(("method", {"name": name, "signature": _signature(name, params),
                                   "modifiers": mods, "static": "static" in mods,
                                   "returnType": re.sub(r"\s+", "", ret), "parameters": params,
                                   "annotations": annotations}, inner))
    return out


# ---------------------------------------------------------------------------
# Chamadas assíncronas
# ---------------------------------------------------------------------------
CALL_PATTERNS = {
    "executeBatch": re.compile(r"\bDatabase\s*\.\s*executeBatch\s*\(", re.I),
    "enqueueJob": re.compile(r"\bSystem\s*\.\s*enqueueJob\s*\(", re.I),
    "schedule": re.compile(r"\bSystem\s*\.\s*schedule\s*\(", re.I),
    "scheduleBatch": re.compile(r"\bSystem\s*\.\s*scheduleBatch\s*\(", re.I),
    "attachFinalizer": re.compile(r"\bSystem\s*\.\s*attachFinalizer\s*\(", re.I),
}


def _calls(body: str, kind: str):
    for m in CALL_PATTERNS[kind].finditer(body):
        open_at = m.end() - 1
        close = _match_close(body, open_at, "(", ")")
        if close > 0:
            yield _split_top(body[open_at + 1:close])


def _resolve_class(arg: str, body: str, own_class: str):
    """Classe instanciada no argumento: `new X(...)`, `this` ou variável local `X v = new X(`."""
    arg = arg.strip()
    m = re.match(rf"new\s+({QUALIFIED})\s*\(", arg, re.I)
    if m:
        return m.group(1), False
    if arg.lower() == "this":
        return own_class, False
    if re.fullmatch(IDENT, arg):
        decl = re.search(rf"\b({QUALIFIED})\s+{re.escape(arg)}\s*=\s*new\s+({QUALIFIED})\s*\(", body, re.I)
        if decl:
            return decl.group(2), False
    return None, True  # não comprovado por literal: dinâmico


def _int_literal(arg):
    return int(arg) if arg is not None and re.fullmatch(r"\s*\d+\s*", arg) else None


def async_invocations(method_name: str, body: str, literals, own_class: str, caller_params=()):
    """Chamadas assíncronas no corpo de um método; `callerContext` = tipo do 1º parâmetro do método
    (distingue, por exemplo, o execute de Batch do execute de Schedulable na mesma classe)."""
    out = []
    context = caller_params[0]["type"] if caller_params else None
    for kind in ("executeBatch", "enqueueJob", "schedule", "scheduleBatch"):
        for args in _calls(body, kind):
            inv = {"callerMethod": method_name, "callerContext": context, "kind": kind}
            if kind == "schedule" and len(args) >= 3:
                inv["jobName"] = _literal(args[0], literals)
                inv["cronExpression"] = _literal(args[1], literals)
                cls, dyn = _resolve_class(args[2], body, own_class)
            elif kind == "scheduleBatch" and len(args) >= 3:
                cls, dyn = _resolve_class(args[0], body, own_class)
                inv["jobName"] = _literal(args[1], literals)
                inv["delayMinutes"] = _int_literal(args[2])
                inv["batchSize"] = _int_literal(args[3]) if len(args) > 3 else None
            elif args:
                cls, dyn = _resolve_class(args[0], body, own_class)
                if kind == "executeBatch":
                    inv["batchSize"] = _int_literal(args[1]) if len(args) > 1 else None
                if kind == "enqueueJob" and len(args) > 1:
                    inv["delayMinutes"] = _int_literal(args[1])
            else:
                continue
            inv["targetClass"] = cls
            inv["dynamicTarget"] = dyn
            out.append(inv)
    return out


# ---------------------------------------------------------------------------
# SOQL do start()
# ---------------------------------------------------------------------------
def _start_query(body: str, literals):
    """(soql, dinâmico) do `start()`: `[SELECT ...]` inline ou `getQueryLocator('...')` literal."""
    m = re.search(r"\[\s*SELECT\b", body, re.I)
    if m:
        close = _match_close(body, m.start(), "[", "]")
        if close > 0:
            return re.sub(r"\s+", " ", restore(body[m.start() + 1:close], literals)).strip(), False
    for args in _calls_named(body, r"\bDatabase\s*\.\s*getQueryLocator\s*\("):
        lit = _literal(args[0], literals) if args else None
        if lit is not None:
            return re.sub(r"\s+", " ", lit).strip(), False
        return None, True
    return None, None  # sem consulta no start()


def _calls_named(body, pattern):
    for m in re.finditer(pattern, body, re.I):
        open_at = m.end() - 1
        close = _match_close(body, open_at, "(", ")")
        if close > 0:
            yield _split_top(body[open_at + 1:close])


def _from_object(soql):
    m = re.search(rf"\bFROM\s+({IDENT})", soql or "", re.I)
    return m.group(1) if m else None


def _apexdoc(raw: str) -> str | None:
    lines = [re.sub(r"^\s*\*\s?", "", ln).rstrip() for ln in raw.splitlines()]
    text = []
    for ln in lines:
        if ln.lstrip().startswith("@"):
            break
        text.append(ln)
    desc = re.sub(r"\s+", " ", " ".join(text)).strip()
    return desc or None


# ---------------------------------------------------------------------------
# Leituras de configuração e padrões de segurança (classes e triggers)
# ---------------------------------------------------------------------------
CUSTOM_SETTING_CALL_RE = re.compile(
    rf"\b({IDENT}__c)\s*\.\s*(getInstance|getOrgDefaults|getValues|getAll)\s*\(", re.I)
CUSTOM_METADATA_CALL_RE = re.compile(rf"\b({IDENT}__mdt)\s*\.\s*(getInstance|getAll)\s*\(", re.I)
SOQL_FROM_MDT_RE = re.compile(rf"\[\s*SELECT\b[^\]]*?\bFROM\s+({IDENT}__mdt)\b", re.I | re.S)


def config_reads(code: str, literals):
    """Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código.

    Só registra a leitura (onde e o quê). Se ela desativa a lógica (bypass) não é inferido.
    """
    out, seen = [], set()

    def add(mechanism, component, call, record=None):
        key = (mechanism, (component or "").lower(), call, (record or "").lower())
        if key not in seen:
            seen.add(key)
            out.append({"mechanism": mechanism, "component": component, "call": call,
                        "record": record, "dynamic": component is None})

    for args in _calls_named(code, r"\bFeatureManagement\s*\.\s*checkPermission\s*\("):
        add("Custom Permission", _literal(args[0], literals) if args else None,
            "FeatureManagement.checkPermission")
    for m in CUSTOM_SETTING_CALL_RE.finditer(code):
        open_at = m.end() - 1
        close = _match_close(code, open_at, "(", ")")
        args = _split_top(code[open_at + 1:close]) if close > 0 else []
        add("Custom Setting", m.group(1), f"{m.group(1)}.{m.group(2)}",
            _literal(args[0], literals) if args and m.group(2).lower() == "getvalues" else None)
    for m in CUSTOM_METADATA_CALL_RE.finditer(code):
        open_at = m.end() - 1
        close = _match_close(code, open_at, "(", ")")
        args = _split_top(code[open_at + 1:close]) if close > 0 else []
        add("Custom Metadata Type", m.group(1), f"{m.group(1)}.{m.group(2)}",
            _literal(args[0], literals) if args else None)
    for m in SOQL_FROM_MDT_RE.finditer(code):
        add("Custom Metadata Type", m.group(1), "SOQL")
    return out


SECURITY_PATTERNS = (
    ("WITH USER_MODE", re.compile(r"\bWITH\s+USER_MODE\b", re.I)),
    ("WITH SYSTEM_MODE", re.compile(r"\bWITH\s+SYSTEM_MODE\b", re.I)),
    ("WITH SECURITY_ENFORCED", re.compile(r"\bWITH\s+SECURITY_ENFORCED\b", re.I)),
    ("AccessLevel.USER_MODE", re.compile(r"\bAccessLevel\s*\.\s*USER_MODE\b", re.I)),
    ("AccessLevel.SYSTEM_MODE", re.compile(r"\bAccessLevel\s*\.\s*SYSTEM_MODE\b", re.I)),
    ("Security.stripInaccessible", re.compile(r"\bSecurity\s*\.\s*stripInaccessible\s*\(", re.I)),
    ("Describe (isAccessible/isCreateable/isUpdateable/isDeletable)",
     re.compile(r"\.\s*is(?:Accessible|Createable|Updateable|Deletable)\s*\(", re.I)),
)


EVENT_NEW_RE = re.compile(rf"\bnew\s+({IDENT}__e)\s*\(", re.I)
EVENTBUS_PUBLISH_RE = re.compile(r"\bEventBus\s*\.\s*publish\s*\(", re.I)


def platform_event_refs(code: str):
    """Platform events (`X__e`) instanciados no código e se há `EventBus.publish(`.

    Publicação só é afirmada quando o código chama EventBus.publish; o tipo publicado é o
    `__e` instanciado no mesmo arquivo (não se rastreia a variável até a chamada).
    """
    types = sorted({m.group(1) for m in EVENT_NEW_RE.finditer(code)}, key=str.lower)
    return {"publishCall": bool(EVENTBUS_PUBLISH_RE.search(code)), "eventTypes": types}


def security_patterns(code: str):
    """Controles explícitos de modo de acesso/CRUD/FLS encontrados no código (com contagem)."""
    out = []
    for label, rx in SECURITY_PATTERNS:
        n = len(rx.findall(code))
        if n:
            out.append({"pattern": label, "occurrences": n})
    return out


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------
CLASS_RE = re.compile(rf"\bclass\s+({IDENT})(\s+extends\s+({QUALIFIED}(?:<[^{{]*?>)?))?"
                      rf"(\s+implements\s+([^{{]+?))?\s*\{{", re.I)


def parse_apex_source(text: str) -> dict:
    code, literals, docs = neutralize(text)
    m = CLASS_RE.search(code)
    other = re.search(rf"\b(interface|enum)\s+({IDENT})", code, re.I)
    if other and (not m or other.start() < m.start()):
        # Interfaces e enums também são metadata ApexClass: sem papel assíncrono.
        return {"parser": PARSER_ID, "parsed": True, "kind": other.group(1).lower(),
                "className": other.group(2), "implements": [], "implementsDeclared": [],
                "methods": [], "futureMethods": [], "asyncInvocations": [],
                "batch": None, "queueable": None, "schedulable": None,
                "configReads": [], "securityPatterns": [],
                "platformEvents": {"publishCall": False, "eventTypes": []}}
    if not m:
        return {"parser": PARSER_ID, "parsed": False, "error": "declaração de classe não encontrada"}
    head_start = max(code.rfind(";", 0, m.start()), code.rfind("}", 0, m.start())) + 1
    header = code[head_start:m.start()]
    class_name = m.group(1)
    annotations = _annotations(header)
    bare_header = _strip_annotations(header).lower().split()
    sharing = SHARING_RE.search(header)
    declared = _split_top(m.group(5) or "")
    implements = [canonical_interface(x) for x in declared]
    open_at = m.end() - 1
    close = _match_close(code, open_at)
    body = code[open_at + 1:close] if close > 0 else code[open_at + 1:]
    doc = None
    for pos, raw in docs:
        if pos <= m.start():
            doc = raw  # o último bloco /** */ antes da declaração
    members = _members(body, class_name)

    methods, constructors, inner, invocations = [], [], [], []
    by_name = {}
    for kind, info, inner_body in members:
        if kind == "inner":
            inner.append(info["name"])
            continue
        if kind == "constructor":
            constructors.append(info)
            continue
        methods.append(info)
        by_name.setdefault(info["name"].lower(), []).append((info, inner_body))
        invocations.extend(async_invocations(info["name"], inner_body, literals, class_name,
                                             info["parameters"]))

    def called_from(name, context_type):
        return [i for i in invocations if i["callerMethod"].lower() == name
                and context_type.lower() in str(i["callerContext"] or "").lower()]

    def body_of(name, context_type=None):
        for info, b in by_name.get(name, []):
            if context_type is None or any(context_type.lower() in p["type"].lower()
                                           for p in info["parameters"]):
                return info, b
        return None, ""

    result = {
        "parser": PARSER_ID,
        "parsed": True,
        "kind": "class",
        "className": class_name,
        "description": _apexdoc(doc) if doc else None,
        "classAnnotations": [a["name"] for a in annotations],
        "isTest": any(a["name"].lower() == "istest" for a in annotations),
        "classModifiers": [w for w in bare_header if w in MODIFIERS],
        "sharing": (sharing.group(1).lower() + " sharing") if sharing else None,
        "extends": re.sub(r"\s+", "", m.group(3)) if m.group(3) else None,
        "implementsDeclared": [re.sub(r"\s+", "", x) for x in declared],
        "implements": implements,
        "constructors": constructors,
        "methods": methods,
        "innerTypes": inner,
        "asyncInvocations": invocations,
        "futureMethods": [],
        "batch": None,
        "queueable": None,
        "schedulable": None,
        "configReads": config_reads(body, literals),
        "securityPatterns": security_patterns(body),
        "platformEvents": platform_event_refs(body),
    }
    for info in methods:
        fut = next((a for a in info["annotations"] if a["name"].lower() == "future"), None)
        if fut:
            result["futureMethods"].append({
                "name": info["name"], "signature": info["signature"],
                "modifiers": info["modifiers"], "returnType": info["returnType"],
                "parameters": info["parameters"],
                "parameterTypes": [p["type"] for p in info["parameters"]],
                "callout": fut["params"].get("callout") == "true"})

    if "Database.Batchable" in implements:
        start, start_body = body_of("start", "BatchableContext")
        ret = start["returnType"] if start else None
        soql, dynamic = _start_query(start_body, literals) if start else (None, None)
        scope = None
        if ret:
            scope = "QueryLocator" if ret.lower().endswith("querylocator") else (
                "Iterable" if ret.lower().startswith("iterable") else ret)
        result["batch"] = {
            "startReturnType": ret, "scopeType": scope, "soqlQuery": soql,
            "soqlDynamic": bool(dynamic), "targetSObject": _from_object(soql),
            "isStateful": "Database.Stateful" in implements,
            "allowsCallouts": "Database.AllowsCallouts" in implements,
            "raisesPlatformEvents": "Database.RaisesPlatformEvents" in implements,
            "lifecycleMethods": [n for n in ("start", "execute", "finish") if by_name.get(n)],
            "chainedJobs": called_from("finish", "BatchableContext"),
        }
    if "System.Queueable" in implements:
        _execute, exec_body = body_of("execute", "QueueableContext")
        finalizer = None
        for args in _calls(exec_body, "attachFinalizer"):
            finalizer, _dyn = _resolve_class(args[0], exec_body, class_name) if args else (None, True)
            finalizer = finalizer or "(dinâmico)"
        chained = [i for i in called_from("execute", "QueueableContext") if i["kind"] == "enqueueJob"]
        result["queueable"] = {
            "allowsCallouts": "Database.AllowsCallouts" in implements,
            "supportsChaining": bool(chained),
            "chainedJobs": chained,
            "hasFinalizerAttached": finalizer is not None,
            "finalizerClassName": finalizer,
            "implementsFinalizer": "System.Finalizer" in implements,
            "inputParameters": [p for c in constructors for p in c["parameters"]],
        }
    if "System.Schedulable" in implements:
        delegated = [i for i in called_from("execute", "SchedulableContext")
                     if i["kind"] in ("executeBatch", "enqueueJob")]
        result["schedulable"] = {
            "delegatesToBatchOrQueueable": bool(delegated),
            "delegatedJobs": delegated,
            "delegatedClassNames": sorted({i["targetClass"] for i in delegated if i["targetClass"]}),
        }
    return result
