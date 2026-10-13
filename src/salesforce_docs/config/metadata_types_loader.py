"""Carrega config/metadata-types-mvp.json: grupos, desvios e ajustes por tipo."""

from __future__ import annotations

import re
from pathlib import Path

from salesforce_docs.errors import ConfigError
from salesforce_docs.utils import kebab, read_json

# documentStrategy -> forma de montar as unidades de documento.
STRATEGY_UNIT_MODES = {
    "ONE_DOCUMENT_PER_COMPONENT": "PER_COMPONENT",
    "SINGLE_DOCUMENT_PER_FLOW_WITH_RELATED_COMPONENTS": "PER_COMPONENT",
    "SINGLE_DOCUMENT_PER_APP_WITH_RELATED_COMPONENTS": "PER_COMPONENT",
    "SINGLE_DOCUMENT_PER_OBJECT_WITH_RELATED_COMPONENTS": "PER_COMPONENT",
    "SINGLE_DOCUMENT_PER_NAMED_CREDENTIAL_WITH_RELATED_COMPONENTS": "PER_COMPONENT",
    "ONE_DOCUMENT_PER_TYPE_AND_RECORDS": "PER_TYPE_WITH_RECORDS",
    # Documento único da org (ex.: Settings:Security), declarado em fixedComponents.
    "ONE_DOCUMENT_PER_ORG": "PER_COMPONENT",
}

RELATION_MATCHES = {"SAME_FULL_NAME", "CHILD_OF_PRIMARY", "FIELD_EQUALS_PRIMARY", "REFERENCE_SCAN",
                    "PRIMARY_FIELD_REFERENCES", "FIELD_EQUALS_PRIMARY_NAME", "NAME_PREFIX"}


class MetadataTypeGroup:
    def __init__(self, data: dict, catalog: "MetadataTypesConfig"):
        self.data = data
        self.name = data.get("group")
        self.primary_type = data.get("primaryMetadataType")
        self.related_types = list(data.get("relatedMetadataTypes") or [])
        self.document_strategy = data.get("documentStrategy")
        self.relations = list(data.get("relations") or [])
        self.sub_documents = list(data.get("subDocuments") or [])
        self.component_filter = data.get("componentFilter") or {}
        self.type_definition = data.get("typeDefinition")
        self.contract_file = data.get("contract") or catalog.contract_file(self.primary_type)
        if not self.name or not self.primary_type:
            raise ConfigError(f"Grupo inválido (group/primaryMetadataType ausente): {data}")
        if self.document_strategy not in STRATEGY_UNIT_MODES:
            raise ConfigError(
                f"Grupo {self.name}: documentStrategy desconhecida '{self.document_strategy}'. "
                f"Valores aceitos: {', '.join(sorted(STRATEGY_UNIT_MODES))}"
            )
        for rel in self.relations:
            if rel.get("match") not in RELATION_MATCHES:
                raise ConfigError(f"Grupo {self.name}: relation.match inválido em {rel}")
            if rel.get("metadataType") not in self.related_types:
                raise ConfigError(
                    f"Grupo {self.name}: relation para {rel.get('metadataType')} "
                    "não consta em relatedMetadataTypes"
                )
            if rel["match"] in ("FIELD_EQUALS_PRIMARY", "PRIMARY_FIELD_REFERENCES", "FIELD_EQUALS_PRIMARY_NAME") \
                    and not rel.get("field"):
                raise ConfigError(f"Grupo {self.name}: {rel['match']} exige 'field' em {rel}")
        if self.unit_mode == "PER_TYPE_WITH_RECORDS" and not self.type_definition:
            raise ConfigError(f"Grupo {self.name}: {self.document_strategy} exige 'typeDefinition'")

    @property
    def unit_mode(self) -> str:
        return STRATEGY_UNIT_MODES[self.document_strategy]

    @property
    def all_types(self):
        return [self.primary_type] + self.related_types

    def relation_for(self, metadata_type):
        for rel in self.relations:
            if rel.get("metadataType") == metadata_type:
                return rel
        return None

    def accepts(self, full_name: str) -> bool:
        inc = self.component_filter.get("includeRegex")
        exc = self.component_filter.get("excludeRegex")
        if inc and not re.search(inc, full_name):
            return False
        if exc and re.search(exc, full_name):
            return False
        return True


class MetadataTypesConfig:
    def __init__(self, data: dict):
        self.data = data
        self.mvp = bool(data.get("mvp"))
        self.org_alias = data.get("orgAlias")
        self.api_version = data.get("apiVersion")
        self.type_settings = data.get("metadataTypeSettings") or {}
        self.excluded = {e["metadataType"]: e.get("reason", "") for e in data.get("excludedMetadataTypes") or []}
        self.sensitive_elements = set(data.get("sensitiveXmlElements") or [])
        # Não são segredos, mas exigem decisão de segurança: nunca vão para o Markdown.
        self.omit_from_documentation = set(data.get("omitFromDocumentation") or [])
        # Onde cada componente está configurado (perfis, permission sets, filas...): ver accessSources.
        self.access_sources = data.get("accessSources") or {}
        # Automações por objeto e ordem oficial de execução (documento de Apex Trigger).
        self.automation_index = data.get("automationIndex") or {}
        # Campos de outros componentes guardados no índice da execução (ex.: OWD do CustomObject
        # para o documento de segurança da org; parentRole para a hierarquia de papéis).
        self.record_index = data.get("recordIndex") or {}
        if self.access_sources and not isinstance(self.access_sources.get("retrieveTypes"), list):
            raise ConfigError("metadata-types-mvp.json: accessSources.retrieveTypes deve ser uma lista")
        groups = data.get("metadataTypeGroups")
        if not isinstance(groups, list) or not groups:
            raise ConfigError("metadata-types-mvp.json sem metadataTypeGroups")
        self.groups = [MetadataTypeGroup(g, self) for g in groups]
        names = [g.name for g in self.groups]
        if len(names) != len(set(names)):
            raise ConfigError("metadata-types-mvp.json possui grupos duplicados")
        for g in self.groups:
            for t in g.all_types:
                if t in self.excluded:
                    raise ConfigError(f"Grupo {g.name} usa tipo excluído {t}: {self.excluded[t]}")
        from salesforce_docs.parsing.source_parsers import SOURCE_PARSERS
        for mtype, settings in self.type_settings.items():
            sp = (settings or {}).get("sourceParser")
            if sp is None:
                continue
            if not isinstance(sp, dict) or sp.get("name") not in SOURCE_PARSERS \
                    or not sp.get("suffix") or not sp.get("key"):
                raise ConfigError(f"metadataTypeSettings.{mtype}.sourceParser inválido: {sp} "
                                  f"(name em {sorted(SOURCE_PARSERS)}, suffix e key obrigatórios)")

    @property
    def render_blocked_elements(self):
        return self.sensitive_elements | self.omit_from_documentation

    def setting(self, metadata_type: str, key: str, default=None):
        return (self.type_settings.get(metadata_type) or {}).get(key, default)

    def folder(self, metadata_type: str) -> str:
        return self.setting(metadata_type, "folder") or kebab(metadata_type)

    def contract_file(self, metadata_type: str) -> str:
        return self.setting(metadata_type, "contract") or f"{kebab(metadata_type)}.schema.json"

    def document_slug(self, metadata_type: str) -> str:
        return self.setting(metadata_type, "documentSlug") or kebab(metadata_type)

    def source_parser(self, metadata_type: str):
        return self.setting(metadata_type, "sourceParser")

    def retrieved_with(self, metadata_type: str):
        return self.setting(metadata_type, "retrievedWith")

    def group(self, name: str):
        for g in self.groups:
            if g.name == name:
                return g
        return None


def load_metadata_types(project_root, path=None) -> MetadataTypesConfig:
    path = Path(path) if path else Path(project_root) / "config" / "metadata-types-mvp.json"
    if not path.is_file():
        raise ConfigError(f"Arquivo não encontrado: {path}")
    try:
        data = read_json(path)
    except ValueError as exc:
        raise ConfigError(f"metadata-types-mvp.json inválido: {exc}") from exc
    return MetadataTypesConfig(data)
