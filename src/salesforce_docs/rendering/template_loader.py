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

    @staticmethod
    def unsafe_reason(name: str):
        """Motivo se o nome do modelo puder sair de documentation/models/api-vN/ (ou None)."""
        if not isinstance(name, str) or not name.strip():
            return "nome vazio"
        if "/" in name or "\\" in name or ".." in name or ":" in name or name.startswith("~"):
            return "o modelo deve ser um nome de arquivo dentro do diretório de modelos (sem / \\ .. :)"
        if not name.endswith(".md"):
            return "o modelo deve ter extensão .md"
        return None

    def path(self, template_pattern: str) -> Path:
        name = self.resolve_name(template_pattern)
        reason = self.unsafe_reason(name)
        if reason:
            raise ValueError(f"Caminho de modelo inválido {name!r}: {reason}")
        path = (self.models_dir / name).resolve()
        if path.parent != self.models_dir.resolve():
            raise ValueError(f"Caminho de modelo inválido {name!r}: fora de {self.models_dir}")
        return path

    def load(self, template_pattern):
        """Texto do modelo ou None (=> NO_TEMPLATE). Nome inseguro => ValueError."""
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
