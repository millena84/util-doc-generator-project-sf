"""Extrai referências a outros componentes do CSV a partir do JSON normalizado.

Fonte: SOMENTE `data` (folhas de texto, percorridas com o caminho JSON) e `codeBody`, quando o
normalizado tiver esse campo. O Utilitário 1 hoje NÃO grava o corpo do código: grava fatos
estruturados (`data.apex.referencedClasses`, `data.apex.sObject`, `configReads`, SOQL literal...).

Regras de busca:
- nome exato com fronteira de identificador (letra, dígito ou `_` não podem encostar no nome),
  sensível a maiúsculas; cobre `'Nome'`, `"Nome"`, `callout:Nome`, `Nome__c` e `Nome__mdt`
  (sufixos acrescentados quando o CSV traz o nome do objeto/tipo sem o sufixo);
- nunca por partes do nome;
- valores redigidos (`[REDACTED]`) não são lidos;
- `matchedText` guarda só o nome casado (com `callout:` quando for o caso), nunca o valor em
  volta: o normalizado pode ter valores sensíveis (cabeçalhos, valores de Custom Metadata).

Evidência: CODE_REFERENCE (caminho em `codePaths`, ex.: `data.apex.*`, ou `codeBody`),
CONFIGURATION_REFERENCE (demais campos do XML) e UNVERIFIED (texto livre, ex.: `description`,
ou nome compartilhado por componentes de tipos diferentes sem dica no caminho). UNVERIFIED nunca
vira aresta do grafo.
"""

from __future__ import annotations

import re

CODE = "CODE_REFERENCE"
CONFIG = "CONFIGURATION_REFERENCE"
MANIFEST = "MANIFEST_REFERENCE"
NAMING = "NAMING_CONVENTION"
UNVERIFIED = "UNVERIFIED"
EVIDENCE_VALUES = (CODE, CONFIG, MANIFEST, NAMING, UNVERIFIED)
REDACTED = "[REDACTED]"
_SUFFIX = {"CustomObject": "__c", "CustomMetadata": "__mdt"}


def name_variants(component_type, name):
    names = [name]
    sfx = _SUFFIX.get(component_type)
    if sfx and not name.endswith(("__c", "__mdt", "__e")):
        names.append(name + sfx)
    return names


def _pattern(name):
    return re.compile(r"(?<![A-Za-z0-9_])(callout:)?" + re.escape(name) + r"(?![A-Za-z0-9_])")


def build_targets(components):
    """{nome: [componente]} para os componentes válidos do CSV (um nome pode ter vários tipos)."""
    targets = {}
    for c in components:
        for n in name_variants(c["componentType"], c["componentName"]):
            targets.setdefault(n, []).append(c)
    return {n: (cs, _pattern(n)) for n, cs in targets.items()}


def _walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def _last_key(path):
    return re.sub(r"\[\d+\]$", "", path).rsplit(".", 1)[-1]


def _relationship(rules, from_type, to_type, path):
    for r in rules.get("relationships") or []:
        if r["from"] != from_type or r["to"] not in (to_type, "*"):
            continue
        if r.get("pathEndsWith") and not re.sub(r"\[\d+\]", "", path).endswith(r["pathEndsWith"]):
            continue
        return r["relationship"]
    return rules.get("defaultRelationship", "REFERENCES")


def _evidence(rules, path, field):
    if field == "codeBody":
        return CODE
    if _last_key(path) in set(rules.get("unverifiedKeys") or []):
        return UNVERIFIED
    first = path.split(".")[1] if path.count(".") >= 1 else ""
    first = re.sub(r"\[\d+\]$", "", first)
    return CODE if first in set(rules.get("codePaths") or []) else CONFIG


def _texts(entry):
    """(arquivo de origem, campo, caminho, texto, linha-base) de um componente carregado."""
    out = [(entry["path"], "data", path, text) for path, text in _walk(entry.get("data") or {}, "data")]
    for extra in entry.get("extraSources") or []:  # records de Custom Metadata do tipo
        out += [(extra["path"], "data", f"{path} (record {extra['fullName']})", text)
                for path, text in _walk(extra.get("data") or {}, "data")]
    if isinstance(entry.get("codeBody"), str):
        out.append((entry["path"], "codeBody", "codeBody", entry["codeBody"]))
    return out


def extract_references(entry, targets, rules):
    """Relações do componente `entry` (status FOUND) para outros componentes do CSV."""
    src_key = entry["key"]
    hints = rules.get("typeHintsByKey") or {}
    found, seen = [], set()
    for source_file, field, path, text in _texts(entry):
        if text == REDACTED or not text:
            continue
        for name, (candidates, pattern) in targets.items():
            if name not in text:
                continue
            for m in pattern.finditer(text):
                cands = [c for c in candidates if f"{c['componentType']}:{c['componentName']}" != src_key]
                if not cands:
                    continue
                evidence = _evidence(rules, path, field)
                if len(cands) > 1:  # mesmo nome em tipos diferentes: só resolve com dica do caminho
                    hinted = [c for c in cands if c["componentType"] == hints.get(_last_key(path))]
                    if len(hinted) == 1:
                        cands = hinted
                    else:
                        evidence = UNVERIFIED
                line = text.count("\n", 0, m.start()) + 1 if field == "codeBody" else None
                for c in cands:
                    to_key = f"{c['componentType']}:{c['componentName']}"
                    rel = {"from": src_key, "to": to_key,
                           "relationship": _relationship(rules, entry["componentType"], c["componentType"], path),
                           "evidence": evidence, "sourceFile": source_file, "sourceField": field,
                           "jsonPath": path, "matchedText": m.group(0), "line": line}
                    if len(cands) > 1:
                        rel["ambiguity"] = "nome presente em mais de um tipo do CSV, sem dica no caminho"
                    dedupe = (to_key, rel["relationship"], source_file, path, rel["matchedText"], line)
                    if dedupe not in seen:
                        seen.add(dedupe)
                        found.append(rel)
    return found
