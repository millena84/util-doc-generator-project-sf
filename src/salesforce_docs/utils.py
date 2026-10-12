"""Funções utilitárias sem dependências externas."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path


def kebab(name: str) -> str:
    """ExternalClientApp -> external-client-app; CustomField -> custom-field."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", s)
    return slugify(s)


def slugify(value: str) -> str:
    """Meu_Flow -> meu-flow. Usado apenas em nomes de arquivo derivados."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return s or "sem-nome"


def api_major(api_version: str) -> str:
    """"67.0" -> "67"."""
    return str(api_version).split(".")[0]


def normalize_api_version(api_version) -> str:
    v = str(api_version).strip()
    if not re.fullmatch(r"\d+(\.\d+)?", v):
        raise ValueError(f"API version inválida: {api_version!r}")
    return v if "." in v else f"{v}.0"


def now_local() -> datetime:
    return datetime.now().astimezone()


def iso_now() -> str:
    return now_local().isoformat(timespec="seconds")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Proteção de dados: raws, cópias de XML, normalizados e run state são gravados com
# permissão 0600 (somente o dono) quando habilitado (config.json → dataProtection.privateFiles).
_PRIVATE_FILES = {"enabled": True}


def set_private_files(enabled: bool) -> None:
    _PRIVATE_FILES["enabled"] = bool(enabled)


def _open_for_write(tmp: Path, private: bool):
    if private:
        if tmp.exists():
            tmp.unlink()
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        return os.fdopen(fd, "w", encoding="utf-8", newline="")
    return open(tmp, "w", encoding="utf-8", newline="")


def write_text_raw(path, text: str, private=None) -> None:
    """Grava resposta bruta exatamente como recebida (sem reformatar).

    private=None segue dataProtection.privateFiles (padrão: 0600). Raws com
    credenciais (`sf org display`) sempre usam private=True.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with _open_for_write(tmp, _PRIVATE_FILES["enabled"] if private is None else private) as f:
        f.write(text)
    os.replace(tmp, path)


def write_json(path, data, private: bool = False) -> None:
    """Grava derivado JSON de forma determinística."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with _open_for_write(tmp, private and _PRIVATE_FILES["enabled"]) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def copy_private(src, dest) -> None:
    """Cópia byte a byte (raw intacto), com permissão 0600 se habilitado."""
    import shutil
    shutil.copyfile(src, dest)
    if _PRIVATE_FILES["enabled"]:
        os.chmod(dest, 0o600)


def write_text(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def rel(path, root) -> str:
    """Caminho relativo ao projeto, sempre com '/'."""
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


class Masker:
    """Remove segredos de qualquer texto antes de exibir ou registrar."""

    def __init__(self):
        self._secrets = set()

    def add(self, secret) -> None:
        if secret and isinstance(secret, str) and len(secret) >= 8:
            self._secrets.add(secret)

    def __call__(self, text):
        if text is None:
            return None
        text = str(text)
        for s in self._secrets:
            text = text.replace(s, "***")
        return text
