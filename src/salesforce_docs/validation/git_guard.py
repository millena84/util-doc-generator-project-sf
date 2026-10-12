"""Verificação de Git: o `.gitignore` não é tratado como controle suficiente.

1. Arquivos sensíveis JÁ RASTREADOS pelo Git (o .gitignore não protege o que já foi
   commitado): raw de `sf org display`, XMLs recuperados, normalizados, respostas de
   erro e material de certificado.
2. Caminhos sensíveis que o .gitignore NÃO ignora (testados com `git check-ignore`).

Fora de um repositório Git (ou sem `git` instalado) a verificação é registrada como
indisponível — nunca como aprovada.
"""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
from pathlib import Path

# tests/fixtures contém apenas dados SINTÉTICOS e fica fora da verificação.
EXEMPT_PREFIXES = ("tests/fixtures/",)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sensitive_patterns(app):
    root = app.project_root
    catalog = _rel(app.paths["catalog"], root)
    inventory = _rel(app.paths["inventory"], root)
    runs = _rel(app.paths["runs"], root)
    return [
        f"{catalog}/*org-display.raw.json",
        f"{runs}/*org-display*",
        f"{runs}/*/errors/*",
        f"{inventory}/*/components/*",
        f"{inventory}/*/normalized/*",
        "*.ecaGlblOauth-meta.xml",
        "*.crt",
    ]


def sample_paths(app):
    """Caminhos representativos que precisam estar ignorados."""
    root = app.project_root
    catalog = _rel(app.paths["catalog"], root)
    inventory = _rel(app.paths["inventory"], root)
    runs = _rel(app.paths["runs"], root)
    return [
        f"{catalog}/org-x/api-v0/org-display.raw.json",
        f"{inventory}/org-x/api-v0/tipo/components/pasta/Exemplo.xml",
        f"{inventory}/org-x/api-v0/tipo/normalized/exemplo.json",
        f"{runs}/run-x/errors/exemplo.sanitized.json",
        f"{inventory}/org-x/api-v0/certificates/components/certs/Exemplo.crt",
    ]


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root)] + list(args), capture_output=True, text=True)


def check_git(app):
    """{"available": bool, "tracked": [...], "notIgnored": [...], "reason": str|None}"""
    root = Path(app.project_root)
    if not shutil.which("git"):
        return {"available": False, "tracked": [], "notIgnored": [], "reason": "git não instalado"}
    probe = _git(root, "rev-parse", "--show-toplevel")
    if probe.returncode != 0:
        return {"available": False, "tracked": [], "notIgnored": [], "reason": "fora de repositório Git"}
    top = Path(probe.stdout.strip()).resolve()
    prefix = _rel(root, top)
    prefix = "" if prefix in (".", "") else prefix + "/"
    listed = _git(top, "ls-files", "-z")
    tracked_all = [f for f in listed.stdout.split("\0") if f]
    patterns = sensitive_patterns(app)
    tracked = []
    for f in tracked_all:
        if prefix and not f.startswith(prefix):
            continue
        rel = f[len(prefix):]
        if rel.startswith(EXEMPT_PREFIXES):
            continue
        if any(fnmatch.fnmatch(rel, p) for p in patterns):
            tracked.append(rel)
    not_ignored = []
    for sample in sample_paths(app):
        res = _git(top, "check-ignore", "-q", "--no-index", prefix + sample)
        if res.returncode != 0:
            not_ignored.append(sample)
    return {"available": True, "tracked": sorted(tracked), "notIgnored": not_ignored, "reason": None}
