"""Carrega modelos Markdown e contratos de metadata type."""

from __future__ import annotations

from pathlib import Path

from salesforce_docs.utils import api_major, read_json


class TemplateLoader:
    def __init__(self, models_dir: Path, api_version: str):
        self.models_dir = Path(models_dir)
        self.api_version = api_version

    def resolve_name(self, template_pattern: str) -> str:
        return template_pattern.replace("{apiMajor}", api_major(self.api_version))

    def path(self, template_pattern: str) -> Path:
        return self.models_dir / self.resolve_name(template_pattern)

    def load(self, template_pattern):
        """Texto do modelo ou None (=> NO_TEMPLATE)."""
        if not template_pattern:
            return None
        p = self.path(template_pattern)
        return p.read_text(encoding="utf-8") if p.is_file() else None


class ContractStore:
    def __init__(self, contracts_dir: Path, mvp_config=None):
        self.contracts_dir = Path(contracts_dir)
        self.mvp_config = mvp_config
        self._cache = {}

    def get_file(self, name):
        if not name:
            return None
        if name not in self._cache:
            p = self.contracts_dir / name
            self._cache[name] = read_json(p) if p.is_file() else None
        return self._cache[name]

    def for_type(self, metadata_type):
        if self.mvp_config is None:
            return None
        return self.get_file(self.mvp_config.contract_file(metadata_type))

    def all(self) -> dict:
        out = {}
        if self.contracts_dir.is_dir():
            for p in sorted(self.contracts_dir.glob("*.schema.json")):
                out[p.name] = self.get_file(p.name)
        return out
