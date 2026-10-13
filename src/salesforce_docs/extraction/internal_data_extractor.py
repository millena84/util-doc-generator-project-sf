"""Passo 9 — dados internos (somente se o contrato prever)."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.salesforce.tooling_api_client import soql_literal
from salesforce_docs.validation.internal_object_validator import query_result_records


def developer_name(full_name: str, namespace_prefix=None) -> str:
    if namespace_prefix and full_name.startswith(f"{namespace_prefix}__"):
        return full_name[len(namespace_prefix) + 2:]
    return full_name


def build_query(template: str, full_name: str, namespace_prefix=None) -> str:
    obj, _, short = full_name.partition(".")
    return template.format(
        fullName=soql_literal(full_name),
        developerName=soql_literal(developer_name(full_name, namespace_prefix)),
        namespacePrefix=soql_literal(namespace_prefix or ""),
        # Componentes `Objeto.Nome` (ex.: BusinessProcess Opportunity.Venda).
        objectName=soql_literal(obj if short else ""),
        shortName=soql_literal(short or full_name),
    )


def extract_internal_data(tooling, internal_cfg, full_name, raw_path, errors_raw_path,
                          namespace_prefix=None):
    if not internal_cfg or not internal_cfg.get("enabled"):
        return {"status": None, "records": None, "raw": None, "query": None}
    query = build_query(internal_cfg["query"], full_name, namespace_prefix)
    use_tooling = internal_cfg.get("useToolingApi", internal_cfg.get("source") == "Tooling API")
    result = tooling.query(query, raw_path=raw_path, error_raw_path=errors_raw_path,
                           use_tooling_api=use_tooling)
    records = query_result_records(result)
    if records is None:
        return {"status": st.INTERNAL_DATA_UNAVAILABLE, "records": None, "raw": result.raw_path,
                "query": query, "error": result.error_message}
    if internal_cfg.get("expectSingleRecord") and len(records) > 1:
        # Mais de um registro para o mesmo componente: escolher um seria suposição.
        return {"status": st.INTERNAL_DATA_UNAVAILABLE, "records": None, "raw": result.raw_path,
                "query": query, "error": f"{len(records)} registros para um componente (ambíguo)"}
    return {"status": st.SUCCESS, "records": records, "raw": result.raw_path, "query": query,
            "error": None}
