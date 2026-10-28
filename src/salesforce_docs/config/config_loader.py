"""Carrega config/config.json (fonte de configuração geral)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from salesforce_docs.config.scope import ScopeConfig
from salesforce_docs.errors import ConfigError
from salesforce_docs.utils import api_major, read_json

REQUIRED_PATHS = ("catalog", "inventory", "models", "contracts", "runs", "outputDocs")


class AppConfig:
    def __init__(self, data: dict, project_root: Path):
        self.data = data
        self.project_root = Path(project_root).resolve()
        self.project_name = data.get("projectName")
        self.org_alias = data.get("orgAlias") or "dev"
        self.minimum_cli_version = (data.get("salesforceCli") or {}).get("minimumVersion", "2.0.0")
        self.default_api_version = data.get("defaultApiVersion")
        execution = data.get("execution") or {}
        self.mode = execution.get("mode")
        self.save_raw_responses = execution.get("saveRawResponses", True)
        self.allow_partial_success = execution.get("allowPartialSuccess", True)
        # true => COMPLETED_WITH_GAPS termina com código 3 (útil em automação/CI).
        self.strict_coverage = bool(execution.get("strictCoverage", False))
        self.cli_timeout_seconds = execution.get("cliTimeoutSeconds", 900)
        self.http_timeout_seconds = execution.get("httpTimeoutSeconds", 120)
        paths = data.get("paths") or {}
        missing = [p for p in REQUIRED_PATHS if p not in paths]
        if missing:
            raise ConfigError(f"config.json sem paths obrigatórios: {', '.join(missing)}")
        self.paths = {k: (self.project_root / v) for k, v in paths.items()}
        # Arquivo de grupos/tipos (opcional; padrão config/metadata-types-mvp.json).
        self.metadata_types_path = self.paths.get(
            "metadataTypesConfig", self.project_root / "config" / "metadata-types-mvp.json")
        # Seleção: ALL (tudo o que estiver configurado) ou SELECTED (tipos/componentes listados).
        self.selection = ScopeConfig(data.get("selection"), legacy_scope=data.get("scope"))
        # Orgs aprovadas: nenhuma coleta (inventário/retrieve) sem identidade aprovada.
        self.approved_orgs = _parse_approved_orgs(data.get("approvedOrgs"))
        # Modo pasta (run --source-dir): de-para pasta do repositório clonado -> nome da org.
        # Só pastas listadas aqui são lidas (equivale ao approvedOrgs do modo com login).
        self.source_repositories = _parse_source_repositories(data.get("sourceRepositories"))
        protection = data.get("dataProtection") or {}
        if not isinstance(protection, dict):
            raise ConfigError("config.json: dataProtection deve ser um objeto")
        self.private_files = bool(protection.get("privateFiles", True))
        self.org_display_raw_policy = str(protection.get("orgDisplayRaw", "KEEP_PRIVATE")).upper()
        if self.org_display_raw_policy not in ("KEEP_PRIVATE", "DELETE_AFTER_RUN"):
            raise ConfigError("config.json: dataProtection.orgDisplayRaw deve ser KEEP_PRIVATE ou DELETE_AFTER_RUN")
        self.output_layout = str(execution.get("outputLayout", "BY_DATE")).upper()
        if self.output_layout not in ("BY_DATE", "BY_RUN"):
            raise ConfigError("config.json: execution.outputLayout deve ser BY_DATE ou BY_RUN")
        # Retomada/regeneração: grava na pasta da execução de origem (padrão) ou na do dia atual.
        self.resume_output = str(execution.get("resumeOutput", "ORIGINAL_FOLDER")).upper()
        if self.resume_output not in ("ORIGINAL_FOLDER", "TODAY"):
            raise ConfigError("config.json: execution.resumeOutput deve ser ORIGINAL_FOLDER ou TODAY")
        warn_days = execution.get("resumeWarnAfterDays", 1)
        if not isinstance(warn_days, int) or isinstance(warn_days, bool) or warn_days < 0:
            raise ConfigError("config.json: execution.resumeWarnAfterDays deve ser inteiro >= 0")
        self.resume_warn_after_days = warn_days

    # Diretórios por org/versão -------------------------------------------
    def catalog_dir(self, alias: str, api_version: str) -> Path:
        return self.paths["catalog"] / f"org-{alias}" / f"api-v{api_major(api_version)}"

    def inventory_dir(self, alias: str, api_version: str) -> Path:
        return self.paths["inventory"] / f"org-{alias}" / f"api-v{api_major(api_version)}"

    def models_dir(self, api_version: str) -> Path:
        return self.paths["models"] / f"api-v{api_major(api_version)}"

    @property
    def contracts_dir(self) -> Path:
        return self.paths["contracts"]

    @property
    def runs_dir(self) -> Path:
        return self.paths["runs"]

    @property
    def output_docs_dir(self) -> Path:
        return self.paths["outputDocs"]


_ORG_ID = re.compile(r"^00D[0-9A-Za-z]{12}([0-9A-Za-z]{3})?$")
_APPROVAL_KEYS = {"orgId", "alias", "username", "instanceUrl", "note"}


def _parse_approved_orgs(value):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError("config.json: approvedOrgs deve ser uma lista")
    out = []
    for i, item in enumerate(value):
        where = f"config.json: approvedOrgs[{i}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{where}: deve ser um objeto")
        extra = set(item) - _APPROVAL_KEYS
        if extra:
            raise ConfigError(f"{where}: chaves desconhecidas {sorted(extra)}")
        org_id = item.get("orgId")
        if not isinstance(org_id, str) or not _ORG_ID.match(org_id):
            raise ConfigError(f"{where}: orgId obrigatório no formato 00D... (15 ou 18 caracteres)")
        out.append({k: v for k, v in item.items() if k != "note"})
    return out


_SOURCE_REPO_KEYS = {"folder", "orgName", "alias", "metadataPath", "note"}
_ALIAS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _parse_source_repositories(value):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError("config.json: sourceRepositories deve ser uma lista")
    out, folders, aliases = [], set(), set()
    for i, item in enumerate(value):
        where = f"config.json: sourceRepositories[{i}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{where}: deve ser um objeto")
        extra = set(item) - _SOURCE_REPO_KEYS
        if extra:
            raise ConfigError(f"{where}: chaves desconhecidas {sorted(extra)}")
        folder, org_name = item.get("folder"), item.get("orgName")
        if not isinstance(folder, str) or not folder.strip() or folder != folder.strip() \
                or "/" in folder or "\\" in folder:
            raise ConfigError(f"{where}: folder obrigatório: só o nome da pasta do repositório "
                              "(sem caminho e sem espaço no início/fim)")
        if not isinstance(org_name, str) or not org_name.strip():
            raise ConfigError(f"{where}: orgName obrigatório (nome da org que o repositório representa)")
        alias = item.get("alias")
        if alias is not None and (not isinstance(alias, str) or not _ALIAS.match(alias)):
            raise ConfigError(f"{where}: alias deve ter só letras, números, '_' ou '-'")
        meta = item.get("metadataPath")
        if meta is not None and (not isinstance(meta, str) or not meta.strip()
                                 or Path(meta).is_absolute() or ".." in Path(meta).parts):
            raise ConfigError(f"{where}: metadataPath deve ser um caminho relativo dentro do repositório")
        if folder.lower() in folders:
            raise ConfigError(f"{where}: pasta {folder!r} repetida")
        folders.add(folder.lower())
        entry = {k: v for k, v in item.items() if k != "note"}
        if alias and alias.lower() in aliases:
            raise ConfigError(f"{where}: alias {alias!r} repetido")
        if alias:
            aliases.add(alias.lower())
        out.append(entry)
    return out


def load_config(project_root, config_path=None) -> AppConfig:
    project_root = Path(project_root)
    path = Path(config_path) if config_path else project_root / "config" / "config.json"
    if not path.is_file():
        raise ConfigError(f"Arquivo de configuração não encontrado: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=_no_duplicate_keys)
    except ConfigError:
        raise
    except ValueError as exc:
        raise ConfigError(f"config.json inválido: {exc}") from exc
    return AppConfig(data, project_root)


def _no_duplicate_keys(pairs):
    """O leitor JSON padrão manteria só a última ocorrência de uma chave repetida;
    aqui isso é erro (ex.: o mesmo metadata type duas vezes em selection)."""
    out = {}
    for key, value in pairs:
        if key in out:
            raise ConfigError(f"config.json: chave JSON repetida {key!r} (só a última seria considerada)")
        out[key] = value
    return out
