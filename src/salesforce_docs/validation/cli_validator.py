"""Passo 1 — validar a Salesforce CLI (`sf --version`)."""

from __future__ import annotations

import re

from salesforce_docs.errors import CliNotFoundError, GlobalFailure

_VERSION_RE = re.compile(r"@salesforce/cli/(\d+(?:\.\d+){0,2})")


def parse_cli_version(text: str):
    m = _VERSION_RE.search(text or "")
    return m.group(1) if m else None


def version_tuple(v: str):
    parts = [int(p) for p in str(v).split(".") if p.isdigit()]
    return tuple((parts + [0, 0, 0])[:3])


def is_version_at_least(found: str, minimum: str) -> bool:
    return version_tuple(found) >= version_tuple(minimum)


def validate_cli(runner, minimum_version: str) -> str:
    try:
        result = runner.run(["--version"], check_session=False)
    except CliNotFoundError as exc:
        raise GlobalFailure("CLI_NOT_FOUND", str(exc)) from exc
    if result.returncode != 0:
        raise GlobalFailure("CLI_ERROR", f"`sf --version` falhou: {result.error_message}")
    found = parse_cli_version(result.stdout)
    if not found:
        raise GlobalFailure("CLI_VERSION_UNKNOWN",
                            f"Não foi possível identificar a versão em: {result.stdout.strip()!r}")
    if not is_version_at_least(found, minimum_version):
        raise GlobalFailure(
            "CLI_VERSION_TOO_LOW",
            f"Salesforce CLI {found} é inferior à mínima {minimum_version}.",
            "npm install --global @salesforce/cli@latest (ou `sf update`)",
        )
    return found
