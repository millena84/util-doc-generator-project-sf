"""Validação estática do projeto: config, contratos e modelos."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.validation.internal_object_validator import validate_internal_data_config


def validate_project(app_config, mvp_config, contracts) -> list:
    """Erros de configuração global (lança) e avisos (retorna)."""
    errors, warnings = [], []
    for group in mvp_config.groups:
        contract = contracts.get_file(group.contract_file)
        if contract is None:
            warnings.append(f"Grupo {group.name}: contrato {group.contract_file} ausente "
                            "(componentes serão extraídos, sem documento)")
        for sub in group.sub_documents:
            if contracts.get_file(sub.get("contract")) is None:
                warnings.append(f"Grupo {group.name}: contrato de subdocumento {sub.get('contract')} ausente")
    for name, contract in contracts.all().items():
        for prop in contract.get("properties", []):
            if prop.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: propriedade {prop.get('name')} com fonte inválida {prop.get('source')!r}")
            if not prop.get("placeholder") or not prop.get("path"):
                errors.append(f"{name}: propriedade {prop.get('name')} sem placeholder/path")
        for table in contract.get("tables", []):
            if table.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: tabela {table.get('markdownSection')} com fonte inválida")
        for block in contract.get("blocks", []):
            if block.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: bloco {block.get('placeholder')} com fonte inválida")
        errors.extend(validate_internal_data_config(name, contract.get("internalData")))
    if errors:
        raise ConfigError("Contratos inválidos:\n- " + "\n- ".join(errors))
    return warnings
