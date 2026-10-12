"""Passos 2 e 3 — alias autenticado e sessão conectada."""

from __future__ import annotations

from salesforce_docs.errors import GlobalFailure

# Campos de `sf org display --json` usados (result.*). O accessToken NÃO é exigido aqui:
# CLIs recentes não exibem segredos nesse comando; o token é obtido depois da aprovação
# da org (`sf org auth show-access-token --json`). Ver documentation/protecao-de-dados.md.
REQUIRED_DISPLAY_FIELDS = ("instanceUrl", "apiVersion", "username")


def login_suggestion(alias: str) -> str:
    return f"sf org login web --alias {alias}"


def find_alias(org_list_result, alias: str):
    """Procura o alias em todas as listas de `sf org list --json`."""
    if not isinstance(org_list_result, dict):
        return None
    for value in org_list_result.values():
        if not isinstance(value, list):
            continue
        for org in value:
            if not isinstance(org, dict):
                continue
            aliases = org.get("aliases") or []
            if org.get("alias") == alias or alias in aliases:
                return org
    return None


def validate_alias_present(cli_result, alias: str) -> dict:
    if not cli_result.ok:
        raise GlobalFailure("ORG_LIST_FAILED", f"`sf org list` falhou: {cli_result.error_message}",
                            login_suggestion(alias))
    org = find_alias(cli_result.result, alias)
    if org is None:
        raise GlobalFailure("ORG_NOT_AUTHENTICATED",
                            f"Alias '{alias}' não encontrado em `sf org list`.",
                            login_suggestion(alias))
    return org


def validate_display(cli_result, alias: str) -> dict:
    if not cli_result.ok:
        raise GlobalFailure("ORG_DISPLAY_FAILED", f"`sf org display` falhou: {cli_result.error_message}",
                            login_suggestion(alias))
    result = cli_result.result or {}
    status = result.get("connectedStatus")
    if status != "Connected":
        raise GlobalFailure("ORG_NOT_CONNECTED",
                            f"connectedStatus da org '{alias}' é {status!r} (esperado 'Connected').",
                            login_suggestion(alias))
    missing = [f for f in REQUIRED_DISPLAY_FIELDS if not result.get(f)]
    if missing:
        raise GlobalFailure("ORG_DISPLAY_INCOMPLETE",
                            f"`sf org display` sem campos obrigatórios: {', '.join(missing)}",
                            login_suggestion(alias))
    return result
