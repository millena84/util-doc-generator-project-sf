"""Leitura e validação do CSV curado pela usuária (`discovery/input/componentes-squad.csv`).

Linha inválida é registrada (linha + motivo) e ignorada; as válidas seguem. Duplicadas
(mesmo tipo + nome, sem diferenciar maiúsculas no tipo) são removidas com aviso.
"""

from __future__ import annotations

import csv
from pathlib import Path

HEADER = ["component_type", "component_name", "squad_suspect", "notes"]

ACCEPTED_TYPES = (
    "ConnectedApp", "ExternalClientApp", "NamedCredential", "ExternalCredential", "ApexClass",
    "ApexTrigger", "CustomObject", "CustomMetadata", "PermissionSet", "RemoteSiteSetting",
    "Certificate", "SelfSignedCertificate", "Flow", "FlowDefinition",
)
_CANONICAL = {t.lower(): t for t in ACCEPTED_TYPES}


class CsvLoadResult:
    def __init__(self):
        self.components = []   # [{componentType, componentName, squadSuspect, notes, line}]
        self.errors = []       # [{line, reason}]
        self.warnings = []     # [{line, reason}]
        self.total_rows = 0
        self.fatal = None      # erro que impede ler o arquivo (cabeçalho, arquivo ausente)

    def to_dict(self):
        return {"totalRows": self.total_rows, "validComponents": len(self.components),
                "errors": self.errors, "warnings": self.warnings, "fatal": self.fatal}


def load_csv(path) -> CsvLoadResult:
    res = CsvLoadResult()
    path = Path(path)
    if not path.is_file():
        res.fatal = f"CSV não encontrado: {path}"
        return res
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    rows = [r for r in rows if any(c.strip() for c in r)]  # ignora linhas em branco
    if not rows:
        res.fatal = "CSV vazio (sem cabeçalho)"
        return res
    header = [h.strip() for h in rows[0]]
    if header != HEADER:
        res.fatal = (f"cabeçalho inválido: esperado exatamente {','.join(HEADER)} "
                     f"(nesta ordem); encontrado {','.join(header)}")
        return res
    seen = {}
    for line_no, row in enumerate(rows[1:], start=2):
        res.total_rows += 1
        if len(row) > len(HEADER):
            res.errors.append({"line": line_no, "reason": f"{len(row)} colunas (máximo {len(HEADER)}); "
                                                          "use aspas em notes com vírgula"})
            continue
        row = [c.strip() for c in row] + [""] * (len(HEADER) - len(row))
        ctype, name, suspect, notes = row
        reasons = []
        canonical = _CANONICAL.get(ctype.lower())
        if not ctype:
            reasons.append("component_type vazio")
        elif canonical is None:
            reasons.append(f"component_type inválido: {ctype!r}")
        if not name:
            reasons.append("component_name vazio")
        if suspect.lower() not in ("true", "false"):
            reasons.append(f"squad_suspect deve ser true ou false (recebido {suspect!r})")
        if reasons:
            res.errors.append({"line": line_no, "reason": "; ".join(reasons)})
            continue
        key = (canonical, name)
        if key in seen:
            res.warnings.append({"line": line_no, "reason": f"duplicada da linha {seen[key]} "
                                                            f"({canonical}:{name}); ignorada"})
            continue
        seen[key] = line_no
        res.components.append({"componentType": canonical, "componentName": name,
                               "squadSuspect": suspect.lower() == "true", "notes": notes or None,
                               "line": line_no})
    return res
