"""Propõe de 1 a 3 nomes por cluster, sempre como PROPOSTA (status CANDIDATE).

Base (nada além disso):
1. prefixos/termos comuns nos nomes dos componentes (ex.: `RH` em `IntegracaoRHService`,
   `RH_Endpoint`), ignorando `discovery.nameStopwords`;
2. rótulos e nomes de ConnectedApp/ExternalClientApp, NamedCredential, CustomObject principal,
   CustomMetadata e PermissionSet (rótulo = `data.label` do normalizado);
3. o termo aparecendo em comentário de código já normalizado (`data.apex.description`, ApexDoc).

Confiança: a do cluster; cai para LOW quando não há termo comum nem app/endpoint para dar nome.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

THEME_ORDER = ["CustomObject", "ConnectedApp", "ExternalClientApp", "NamedCredential",
               "CustomMetadata", "PermissionSet"]
_TOKEN = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")
_VERB = {"CALLS_ENDPOINT": "chama o endpoint", "REFERENCES_OBJECT": "referencia o objeto",
         "INVOKES_CLASS": "invoca", "USES_METADATA": "usa o metadata", "TRIGGERS_ON_OBJECT": "dispara no objeto",
         "DEFINES_ENDPOINT": "define o endpoint", "REFERENCES_APP": "referencia o app",
         "GRANTS_ACCESS_TO_CLASS": "concede acesso à classe", "GRANTS_ACCESS_TO_OBJECT": "concede acesso ao objeto",
         "GRANTS_ACCESS_TO_APP": "concede acesso ao app", "USES_CERTIFICATE": "usa o certificado",
         "RELATED_COMPONENT": "está relacionado a", "USES_CREDENTIAL": "usa a credencial",
         "HAS_TRIGGER": "tem a trigger", "REFERENCES": "referencia"}


def tokens(name):
    base = re.sub(r"__(c|mdt|e)$", "", name)
    out = []
    for part in re.split(r"[_.\-\s]+", base):
        out += _TOKEN.findall(part)
    return out


def _norm(word):
    return unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode().lower()


def _clean_label(label, prefix, stopwords):
    """Rótulo sem o termo comum e sem palavras genéricas (evita "Integração RH - Integração RH")."""
    words = [w for w in re.split(r"[\s\-_]+", label) if w]
    keep = [w for w in words if _norm(w) not in stopwords and _norm(w) != _norm(prefix or "")]
    return " ".join(keep)


def _split(member_id):
    t, _, n = member_id.partition(":")
    return t, n


def common_terms(members, stopwords):
    counts, forms = Counter(), {}
    for m in members:
        _, name = _split(m)
        seen = set()
        for tok in tokens(name):
            low = tok.lower()
            if low in stopwords or len(tok) < 2 or low in seen:
                continue
            seen.add(low)
            counts[low] += 1
            forms.setdefault(low, Counter())[tok] += 1
    terms = [(low, n) for low, n in counts.items() if n >= 2]
    terms.sort(key=lambda x: (-x[1], not forms[x[0]].most_common(1)[0][0].isupper(), -len(x[0]), x[0]))
    return [(forms[low].most_common(1)[0][0], n,
             sorted(m for m in members if low in {t.lower() for t in tokens(_split(m)[1])}))
            for low, n in terms]


def _themes(cluster, labels):
    by_type = {}
    for c in cluster["components"]:
        by_type.setdefault(c["type"], []).append(c["id"])
    out = []
    for t in THEME_ORDER:
        for m in sorted(by_type.get(t, [])):
            label = labels.get(m) or re.sub(r"__(c|mdt)$", "", _split(m)[1]).replace("_", " ")
            if label not in [x[0] for x in out]:
                out.append((label, t, m))
    return out


def propose(cluster, labels, descriptions, stopwords, orphans):
    members = [c["id"] for c in cluster["components"]]
    terms = common_terms(members, stopwords)
    themes = _themes(cluster, labels)
    rationale = []
    names = []
    prefix = terms[0][0] if terms else None
    if prefix:
        n, who = terms[0][1], terms[0][2]
        rationale.append(f"Termo {prefix} aparece no nome de {n} componentes: {', '.join(_split(w)[1] for w in who)}.")
        for t in themes:
            cleaned = _clean_label(t[0], prefix, stopwords)
            if cleaned and len(names) < 3:
                names.append(f"Integração {prefix} - {cleaned}")
        if len(names) < 3:
            names.append(f"Integração {prefix} - Salesforce")
    else:
        for t in themes[:3]:
            names.append(t[0] if _norm(t[0]).startswith(("integracao", "integration")) else f"Integração {t[0]}")
    if not names:
        names.append(f"Integração {_split(members[0])[1]}")
    for t in themes[:3]:
        rationale.append(f"{t[1]} {_split(t[2])[1]} (rótulo/nome: {t[0]}) usado como tema.")
    for e in [e for e in cluster["relationships"] if not e.get("inverseOf")][:8]:
        ft, fn = _split(e["from"])
        tt, tn = _split(e["to"])
        rationale.append(f"{ft} {fn} {_VERB.get(e['relationship'], 'referencia')} {tt} {tn} "
                         f"({e['relationship']}, {e['evidence']}, `{e['jsonPath']}`).")
    if prefix:
        for m, desc in sorted(descriptions.items()):
            if m in members and desc and re.search(r"(?<![A-Za-z0-9_])" + re.escape(prefix) + r"(?![A-Za-z0-9_])", desc):
                rationale.append(f"Termo {prefix} aparece no comentário (ApexDoc) de {_split(m)[1]}.")
        hints = [o for o in orphans if prefix.lower() in {t.lower() for t in tokens(_split(o)[1])}]
        cluster["orphanComponents"] = [{"id": o, "evidence": "NAMING_CONVENTION",
                                        "note": f"nome contém {prefix}; sem relação confirmada"} for o in hints]
    conf = cluster["confidence"]
    if not prefix and not any(t[1] in ("ConnectedApp", "ExternalClientApp", "NamedCredential") for t in themes):
        conf = "LOW"
        rationale.append("Sem termo comum nem app/endpoint no cluster: nome com evidência fraca.")
    names = list(dict.fromkeys(names))[:3]
    cluster.update(proposedName=names[0], alternativeNames=names[1:])
    return {"clusterId": cluster["clusterId"], "proposedName": names[0], "confidence": conf,
            "rationale": rationale, "alternativeNames": names[1:], "status": "CANDIDATE"}
