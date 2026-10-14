"""Configuração da descoberta: `config/config.json` → `discovery` (todos os campos opcionais).

Padrões abaixo; o `config.json` sobrepõe chave a chave. Regras de relação (tipo de origem x
tipo de destino -> relação) ficam em `config/integration-discovery-rules.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_FOLDERS = {
    "ConnectedApp": "connected-apps",
    "ExternalClientApp": "external-client-apps",
    "NamedCredential": "named-credentials",
    "ExternalCredential": "external-credentials",
    "ApexClass": "apex-classes",
    "ApexTrigger": "apex-triggers",
    "CustomObject": "custom-objects",
    "CustomMetadata": "custom-metadata",
    "PermissionSet": "permission-sets",
    "RemoteSiteSetting": "remote-site-settings",
    "Certificate": "certificates",
    "SelfSignedCertificate": "self-signed-certificates",
    "Flow": "flows",
    "FlowDefinition": "flow-definitions",
}

# metadataType gravado no normalizado pelo Utilitário 1, por tipo do CSV (padrão: o próprio tipo).
# Custom Metadata: o tipo (`X__mdt`) é gravado como CustomObject; os records, como CustomMetadata.
DEFAULT_NORMALIZED_TYPES = {
    "ExternalClientApp": ["ExternalClientApplication"],
    "CustomMetadata": ["CustomObject", "CustomMetadata"],
}

# Tipos "ponte": concedem acesso a muitos componentes sem formar a integração (ex.: um
# permission set que libera classes de integrações diferentes). Não unem clusters: entram em
# cada cluster com que se ligam (por isso um componente pode estar em mais de um cluster).
DEFAULT_BRIDGE_TYPES = ["PermissionSet"]

# Palavras que não servem de prefixo/tema na proposta de nome.
DEFAULT_NAME_STOPWORDS = [
    "integracao", "integration", "service", "services", "svc", "trigger", "handler", "controller",
    "helper", "util", "utils", "batch", "queueable", "scheduler", "job", "config", "configuration",
    "setting", "settings", "endpoint", "user", "users", "app", "cert", "certificate", "remote",
    "site", "credential", "named", "external", "c", "mdt", "e", "test", "tests", "api", "rest",
    "callout", "flow", "the", "de", "do", "da", "dos", "das",
]

# Componentes lidos JUNTO com o componente do CSV (não viram nós do grafo): as referências achadas
# neles contam como do componente do CSV, e o vínculo fica registrado (MANIFEST_REFERENCE).
# - FIELD_EQUALS_NAME: JSON da pasta cujo `data.<field>` é o nome do componente (ex.: políticas da
#   External Client App apontam para ela em `externalClientApplication`);
# - CHILD_OF: JSON da pasta cujo fullName é `<nome>.<filho>` (ex.: campos, record types e regras
#   de validação do objeto; records de Custom Metadata, com `stripSuffix` "__mdt").
DEFAULT_RELATED_SOURCES = {
    "ExternalClientApp": [
        {"match": "FIELD_EQUALS_NAME", "field": "externalClientApplication",
         "folders": ["extl-clnt-app-oauth-settings", "extl-clnt-app-configurable-policies",
                     "extl-clnt-app-oauth-configurable-policies"]},
    ],
    "CustomObject": [
        {"match": "CHILD_OF", "folders": ["custom-objects"],
         "metadataTypes": ["CustomField", "RecordType", "ValidationRule", "WebLink"]},
    ],
    "CustomMetadata": [
        {"match": "CHILD_OF", "folders": ["custom-metadata"], "metadataTypes": ["CustomMetadata"],
         "stripSuffix": "__mdt"},
        {"match": "CHILD_OF", "folders": ["custom-metadata"], "metadataTypes": ["CustomField"]},
    ],
}

# Mesmo fullName em dois tipos do CSV que formam um só componente no Utilitário 1 (relação
# SAME_FULL_NAME do metadata-types-mvp.json): ligados com evidência MANIFEST_REFERENCE.
DEFAULT_SAME_NAME_PAIRS = [
    {"from": "Flow", "to": "FlowDefinition", "relationship": "HAS_DEFINITION"},
]

DEFAULT_RULES_FILE = "config/integration-discovery-rules.json"


class DiscoverySettings:
    def __init__(self, project_root, config_path=None):
        self.project_root = Path(project_root).resolve()
        cfg_path = Path(config_path) if config_path else self.project_root / "config" / "config.json"
        data = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
        disc = data.get("discovery") or {}
        self.org_alias = data.get("orgAlias") or "dev"
        self.api_version = data.get("defaultApiVersion") or "67.0"
        paths = data.get("paths") or {}
        self.inventory_root = self.project_root / (paths.get("inventory") or "inventory")
        self.output_dir = self.project_root / (disc.get("outputDir") or "discovery")
        self.folders = dict(DEFAULT_FOLDERS, **(disc.get("metadataTypeFolders") or {}))
        self.normalized_types = dict(DEFAULT_NORMALIZED_TYPES, **(disc.get("normalizedMetadataTypes") or {}))
        self.bridge_types = list(disc.get("bridgeTypes", DEFAULT_BRIDGE_TYPES))
        self.stopwords = {w.lower() for w in disc.get("nameStopwords", DEFAULT_NAME_STOPWORDS)}
        self.related_sources = dict(DEFAULT_RELATED_SOURCES, **(disc.get("relatedSources") or {}))
        self.same_name_pairs = list(disc.get("sameNamePairs", DEFAULT_SAME_NAME_PAIRS))
        rules_path = self.project_root / (disc.get("rulesFile") or DEFAULT_RULES_FILE)
        self.rules_path = rules_path
        self.rules = json.loads(rules_path.read_text(encoding="utf-8")) if rules_path.is_file() else {}

    def inventory_dir(self, alias=None, api_version=None) -> Path:
        major = str(api_version or self.api_version).split(".")[0]
        return self.inventory_root / f"org-{alias or self.org_alias}" / f"api-v{major}"

    def expected_metadata_types(self, csv_type):
        return self.normalized_types.get(csv_type) or [csv_type]
