"""Valida a configuração de dados internos declarada no contrato (Passo 9)."""

from __future__ import annotations

INTERNAL_SOURCES = {"Tooling API", "Objeto interno"}


def validate_internal_data_config(contract_name: str, internal: dict):
    """Retorna lista de erros (vazia = válido)."""
    errors = []
    if not internal or not internal.get("enabled"):
        return errors
    if internal.get("source") not in INTERNAL_SOURCES:
        errors.append(f"{contract_name}: internalData.source deve ser um de {sorted(INTERNAL_SOURCES)}")
    if not internal.get("object"):
        errors.append(f"{contract_name}: internalData.object é obrigatório quando enabled=true")
    query = internal.get("query") or ""
    if not query.strip().upper().startswith("SELECT"):
        errors.append(f"{contract_name}: internalData.query deve ser uma consulta SOQL SELECT")
    return errors


def query_result_records(cli_result):
    """Extrai registros de `sf data query --json` (ou None se indisponível)."""
    if not cli_result.ok:
        return None
    result = cli_result.result
    if isinstance(result, dict) and isinstance(result.get("records"), list):
        return result["records"]
    return None
