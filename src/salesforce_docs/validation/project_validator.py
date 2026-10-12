"""Validação estática do projeto: config, contratos, modelos e builders."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.validation.internal_object_validator import validate_internal_data_config


def validate_project(app_config, mvp_config, contracts) -> list:
    """Erros de configuração global (lança) e avisos (retorna)."""
    errors, warnings = [], []
    used = set()
    for group in mvp_config.groups:
        contract = contracts.get_file(group.contract_file)
        used.add(group.contract_file)
        if contract is None:
            warnings.append(f"Grupo {group.name}: contrato {group.contract_file} ausente "
                            "(componentes serão extraídos, sem documento)")
        for sub in group.sub_documents:
            used.add(sub.get("contract"))
            if contracts.get_file(sub.get("contract")) is None:
                warnings.append(f"Grupo {group.name}: contrato de subdocumento {sub.get('contract')} ausente")
    for name, contract in contracts.all().items():
        for prop in contract.get("properties", []):
            if prop.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: propriedade {prop.get('name')} com fonte inválida {prop.get('source')!r}")
            if not prop.get("placeholder") or not prop.get("path"):
                errors.append(f"{name}: propriedade {prop.get('name')} sem placeholder/path")
            last = str(prop.get("path", "")).split(".")[-1]
            if last in mvp_config.render_blocked_elements:
                errors.append(f"{name}: propriedade {prop.get('name')} aponta para elemento "
                              f"bloqueado para documentação ({last})")
        for table in contract.get("tables", []):
            if table.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: tabela {table.get('markdownSection')} com fonte inválida")
        for block in contract.get("blocks", []):
            if block.get("source") not in st.ALLOWED_SOURCES:
                errors.append(f"{name}: bloco {block.get('placeholder')} com fonte inválida")
        errors.extend(validate_internal_data_config(name, contract.get("internalData")))
        if contract.get("template"):
            e, w = validate_template(name, contract, app_config)
            errors.extend(e)
            warnings.extend(w)
    warnings.extend(_unused_models(app_config, contracts))
    if errors:
        raise ConfigError("Contratos/modelos inválidos:\n- " + "\n- ".join(errors))
    return warnings


def validate_template(contract_name, contract, app_config):
    """Cada placeholder do modelo precisa de propriedade, bloco ou tabela no contrato,
    com builder existente e a mesma fonte declarada no modelo."""
    from salesforce_docs.rendering.markdown_renderer import (BLOCK_BUILDERS, PLACEHOLDER_RE,
                                                             TABLE_BUILDERS, _cells, _find_prop)
    from salesforce_docs.rendering.template_loader import TemplateLoader

    errors, warnings = [], []
    api = app_config.default_api_version or "67.0"
    loader = TemplateLoader(app_config.models_dir(api), api)
    text = loader.load(contract["template"])
    if text is None:
        ref = contract.get("referenceDoc")
        warnings.append(f"{contract_name}: modelo {loader.path(contract['template'])} ausente "
                        f"(NO_TEMPLATE em execução{'; referência ' + ref if ref else ''})")
        return errors, warnings
    tables = {t["markdownSection"]: t for t in contract.get("tables", [])}
    blocks = {b["placeholder"]: b for b in contract.get("blocks", [])}
    props = contract.get("properties", [])
    tname = loader.resolve_name(contract["template"])
    seen_sections = set()
    section = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            seen_sections.add(section)
        names = PLACEHOLDER_RE.findall(line)
        if not names:
            continue
        cells = _cells(line)
        if section in tables and cells is not None:
            t = tables[section]
            if t.get("builder") not in TABLE_BUILDERS:
                errors.append(f"{contract_name}/{tname}: builder de tabela desconhecido {t.get('builder')!r}")
            if cells[-1] != t.get("source"):
                errors.append(f"{contract_name}/{tname}: seção '{section}' com Fonte '{cells[-1]}' "
                              f"no modelo e '{t.get('source')}' no contrato")
            expected = table_placeholders(t)
            for n in names:
                if expected is not None and n not in expected:
                    errors.append(f"{contract_name}/{tname}: placeholder '{n}' (seção '{section}') "
                                  f"não é coluna do builder {t.get('builder')} {sorted(expected)}")
            continue
        for n in names:
            if n == "component_name" and section is None:
                continue
            prop = _find_prop(props, n, section)
            if prop is not None:
                if cells is not None and cells[-1] != prop["source"]:
                    errors.append(f"{contract_name}/{tname}: {prop['name']} com Fonte '{cells[-1]}' "
                                  f"no modelo e '{prop['source']}' no contrato")
                continue
            if n in blocks:
                if blocks[n].get("builder") not in BLOCK_BUILDERS:
                    errors.append(f"{contract_name}/{tname}: builder de bloco desconhecido "
                                  f"{blocks[n].get('builder')!r}")
                continue
            errors.append(f"{contract_name}/{tname}: placeholder '{n}' (seção '{section}') "
                          "sem propriedade, bloco ou tabela no contrato")
    for sec in tables:
        if sec not in seen_sections:
            errors.append(f"{contract_name}/{tname}: tabela do contrato para seção inexistente '{sec}'")
    return errors, warnings


def table_placeholders(table):
    """Placeholders que o builder da tabela preenche (None = desconhecido)."""
    args = table.get("args") or {}
    builder = table.get("builder")
    if "columns" in args:
        return set(args["columns"])
    if builder == "related_components":
        return {"related_component", "related_type"}
    if builder == "related_folders":
        return {"folder", "purpose"}
    if builder in ("child_properties", "internal_record_properties"):
        return {args.get("keyPlaceholder", "property"), args.get("valuePlaceholder", "value")}
    return None


def _unused_models(app_config, contracts):
    api = app_config.default_api_version or "67.0"
    models_dir = app_config.models_dir(api)
    if not models_dir.is_dir():
        return []
    from salesforce_docs.rendering.template_loader import TemplateLoader
    loader = TemplateLoader(models_dir, api)
    referenced = {loader.resolve_name(c["template"]) for c in contracts.all().values()
                  if c and c.get("template")}
    return [f"Modelo {p.name} sem contrato que o referencie"
            for p in sorted(models_dir.glob("*.md")) if p.name not in referenced]
