"""Carrega config/config.json (fonte de configuração geral)."""

from __future__ import annotations

from pathlib import Path

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
        self.cli_timeout_seconds = execution.get("cliTimeoutSeconds", 900)
        self.http_timeout_seconds = execution.get("httpTimeoutSeconds", 120)
        paths = data.get("paths") or {}
        missing = [p for p in REQUIRED_PATHS if p not in paths]
        if missing:
            raise ConfigError(f"config.json sem paths obrigatórios: {', '.join(missing)}")
        self.paths = {k: (self.project_root / v) for k, v in paths.items()}

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


def load_config(project_root, config_path=None) -> AppConfig:
    project_root = Path(project_root)
    path = Path(config_path) if config_path else project_root / "config" / "config.json"
    if not path.is_file():
        raise ConfigError(f"Arquivo de configuração não encontrado: {path}")
    try:
        data = read_json(path)
    except ValueError as exc:
        raise ConfigError(f"config.json inválido: {exc}") from exc
    return AppConfig(data, project_root)
