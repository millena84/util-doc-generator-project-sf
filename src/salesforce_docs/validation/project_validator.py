"""Validação estática do projeto: config, contratos, modelos e builders."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.validation.internal_object_validator import validate_internal_data_config


def validate_project(app_config, mvp_config, contracts, strict=False) -> list:
    """Erros de configuração global (lança) e avisos (retorna).

    strict=True (opt-in, `validate-config --strict`): avisos também viram erro.
    """
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
    errors.extend(validate_automation_index(mvp_config.automation_index))
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
        errors.extend(validate_internal_data_config(name, contract.get("internalData"),
                                                    mvp_config.render_blocked_elements))
        if contract.get("template"):
            e, w = validate_template(name, contract, app_config)
            errors.extend(e)
            warnings.extend(w)
            errors.extend(validate_access_section(name, contract, app_config))
        else:
            warnings.extend(_templateless_usage(name, contract, contracts, mvp_config))
    warnings.extend(_unused_models(app_config, contracts))
    if strict and warnings:
        errors.extend(f"[strict] {w}" for w in warnings)
    if errors:
        raise ConfigError("Contratos/modelos inválidos:\n- " + "\n- ".join(errors))
    return warnings


ACCESS_BUILDER = "access_rows"


def validate_access_section(name, contract, app_config):
    """Todo documento termina com "onde o componente está configurado".

    Exige exatamente uma tabela `access_rows` no contrato (tipos sem atribuição declaram
    `args.notApplicable` com o motivo) e que a seção dela seja a ÚLTIMA do modelo.
    """
    from salesforce_docs.rendering.template_loader import TemplateLoader

    tables = [t for t in contract.get("tables", []) if t.get("builder") == ACCESS_BUILDER]
    if len(tables) != 1:
        return [f"{name}: o contrato precisa de exatamente uma tabela '{ACCESS_BUILDER}' "
                "(seção 'Acesso e configuração'; use args.notApplicable com o motivo quando o tipo "
                "não tiver atribuição por perfil/permission set)"]
    api = app_config.default_api_version or "67.0"
    loader = TemplateLoader(app_config.models_dir(api), api)
    try:
        text = loader.load(contract["template"])
    except ValueError:
        return []  # nome de modelo inválido já é erro em validate_template
    if text is None:
        return []  # modelo ausente: NO_TEMPLATE já é aviso
    sections = [ln[3:].strip() for ln in text.splitlines() if ln.startswith("## ")]
    expected = tables[0].get("markdownSection")
    if not sections or sections[-1] != expected:
        return [f"{name}: a seção '{expected}' deve ser a última do modelo "
                f"{loader.resolve_name(contract['template'])} (última atual: "
                f"'{sections[-1] if sections else '—'}')"]
    return []


def _templateless_usage(name, contract, contracts, mvp_config):
    """Contrato sem modelo próprio: intencional se outro contrato o renderiza por bloco
    (related_properties_table) ou se declara `renderedVia`; caso contrário, aviso."""
    mtype = contract.get("metadataType")
    for other_name, other in contracts.all().items():
        for block in (other or {}).get("blocks", []):
            if block.get("builder") == "related_properties_table" and \
                    (block.get("args") or {}).get("metadataType") == mtype and \
                    mvp_config.contract_file(mtype) == name:
                return []
    if contract.get("renderedVia"):
        return []
    return [f"{name}: contrato sem modelo próprio e sem uso por bloco de outro contrato "
            "(declare `renderedVia` se for intencional)"]


def validate_template(contract_name, contract, app_config):
    """Cada placeholder do modelo precisa de propriedade, bloco ou tabela no contrato,
    com builder existente e a mesma fonte declarada no modelo."""
    from salesforce_docs.rendering.markdown_renderer import (BLOCK_BUILDERS, PLACEHOLDER_RE,
                                                             TABLE_BUILDERS, _cells, _find_prop)
    from salesforce_docs.rendering.template_loader import TemplateLoader

    errors, warnings = [], []
    api = app_config.default_api_version or "67.0"
    loader = TemplateLoader(app_config.models_dir(api), api)
    try:
        text = loader.load(contract["template"])
    except ValueError as exc:
        return [f"{contract_name}: {exc}"], warnings
    if text is None:
        ref = contract.get("referenceDoc")
        warnings.append(f"{contract_name}: modelo esperado ausente {loader.path(contract['template'])} "
                        f"(NO_TEMPLATE em execução{'; referência ' + ref if ref else ''})")
        return errors, warnings
    tables = {t["markdownSection"]: t for t in contract.get("tables", [])}
    blocks = {b["placeholder"]: b for b in contract.get("blocks", [])}
    props = contract.get("properties", [])
    tname = loader.resolve_name(contract["template"])
    where = f"{contract_name} [{contract.get('metadataType')}] / {tname}"
    seen_sections = set()
    used_placeholders = set()
    block_sections = {}
    section = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            section = line[3:].strip()
            seen_sections.add(section)
        names = PLACEHOLDER_RE.findall(line)
        leftovers = PLACEHOLDER_RE.sub("", line)
        if "{{" in leftovers or "}}" in leftovers:
            errors.append(f"{where}:{lineno}: placeholder malformado: {line.strip()}")
        if not names:
            continue
        used_placeholders.update(names)
        cells = _cells(line)
        if section in tables and cells is not None:
            t = tables[section]
            if t.get("builder") not in TABLE_BUILDERS:
                errors.append(f"{where}: builder de tabela desconhecido {t.get('builder')!r} "
                              f"(seção '{section}')")
            if cells[-1] != t.get("source"):
                errors.append(f"{where}: seção '{section}' com Fonte '{cells[-1]}' "
                              f"no modelo e '{t.get('source')}' no contrato")
            expected = table_placeholders(t)
            for n in names:
                if expected is not None and n not in expected:
                    errors.append(f"{where}: placeholder '{n}' (seção '{section}') "
                                  f"não é coluna do builder {t.get('builder')} {sorted(expected)}")
            continue
        for n in names:
            if n == "component_name" and section is None:
                continue
            prop = _find_prop(props, n, section)
            if prop is not None:
                if cells is not None and cells[-1] != prop["source"]:
                    errors.append(f"{where}: {prop['name']} com Fonte '{cells[-1]}' "
                                  f"no modelo e '{prop['source']}' no contrato")
                continue
            if n in blocks:
                block_sections[n] = section
                if blocks[n].get("builder") not in BLOCK_BUILDERS:
                    errors.append(f"{where}: builder de bloco desconhecido "
                                  f"{blocks[n].get('builder')!r} (placeholder '{n}')")
                continue
            errors.append(f"{where}: placeholder '{n}' (seção '{section}') "
                          "sem propriedade, bloco ou tabela no contrato")
    for sec in tables:
        if sec not in seen_sections:
            errors.append(f"{where}: tabela do contrato para seção inexistente '{sec}'")
    for ph, block in blocks.items():
        if ph not in block_sections:
            errors.append(f"{where}: bloco '{ph}' declarado no contrato não aparece no modelo")
        elif block.get("markdownSection") and block["markdownSection"] != block_sections[ph]:
            errors.append(f"{where}: bloco '{ph}' está na seção '{block_sections[ph]}' do modelo, "
                          f"mas o contrato declara '{block['markdownSection']}'")
    for prop in props:
        ph = prop.get("placeholder")
        if ph and ph not in used_placeholders and not (ph == "component_name"):
            if prop.get("intentionallyNotRendered"):
                continue
            warnings.append(f"{where}: propriedade {prop.get('name')} (placeholder '{ph}') declarada no "
                            "contrato e ausente do modelo — não será renderizada "
                            "(marque `intentionallyNotRendered` se for intencional)")
    return errors, warnings


def validate_automation_index(cfg):
    """automationIndex: fases únicas e toda fonte apontando para fases declaradas."""
    if not cfg:
        return []
    errors = []
    keys = [p.get("key") for p in cfg.get("phases") or []]
    if len(keys) != len(set(keys)) or None in keys:
        errors.append("automationIndex.phases: chaves ausentes ou duplicadas")
    for src in cfg.get("sources") or []:
        where = f"automationIndex.sources[{src.get('metadataType')}]"
        targets = ([src["phase"]] if src.get("phase") else []) + \
            list(((src.get("phaseByPath") or {}).get("map") or {}).values()) + \
            list(((src.get("phaseByEvent") or {}).get("map") or {}).values())
        if not targets:
            errors.append(f"{where}: declare phase, phaseByPath ou phaseByEvent")
        for t in targets:
            if t not in keys:
                errors.append(f"{where}: fase '{t}' não declarada em automationIndex.phases")
    return errors


def table_placeholders(table):
    """Placeholders que o builder da tabela preenche (None = desconhecido)."""
    args = table.get("args") or {}
    builder = table.get("builder")
    if builder == "index_record_rows":
        return set(args.get("columns") or {}) | {args.get("namePlaceholder", "record_name")}
    if builder in ("role_hierarchy_rows", "page_usage_rows", "event_reference_rows"):
        from salesforce_docs.parsing.governance_builders import BUILDER_PLACEHOLDERS as GB
        return set(GB[builder])
    if builder == "code_fact_rows":
        return set(args.get("columns") or {}) | {args.get("locationPlaceholder", "fact_location")}
    if builder in ("automation_rows", "referenced_class_rows", "apex_method_check_rows"):
        from salesforce_docs.parsing.trigger_builders import BUILDER_PLACEHOLDERS
        return set(BUILDER_PLACEHOLDERS[builder])
    if "columns" in args:
        return set(args["columns"])
    if builder == "related_components":
        return {"related_component", "related_type"}
    if builder == "related_folders":
        return {"folder", "purpose"}
    if builder == "access_rows":
        from salesforce_docs.parsing.access_builders import ACCESS_PLACEHOLDERS
        return set(ACCESS_PLACEHOLDERS)
    if builder == "object_sharing_rows":
        from salesforce_docs.parsing.access_builders import SHARING_PLACEHOLDERS
        return set(SHARING_PLACEHOLDERS)
    if builder == "list_values":
        return {args.get("valuePlaceholder", "value")} | (
            {args["labelPlaceholder"]} if args.get("labelPlaceholder") else set())
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
