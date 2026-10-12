"""Gravação dos documentos finais sem colisão nem sobrescrita silenciosa.

- Layout BY_DATE (padrão, estrutura original): saida/docs/doc-org-MMDDAA/.
  Um manifesto (.manifest.json) registra qual execução gerou cada arquivo.
  Se um arquivo de OUTRA execução (ou de origem desconhecida) for ser substituído
  por conteúdo diferente, a versão anterior é movida para
  `_substituidos/<runId anterior>/` e a troca fica registrada no run state.
- Layout BY_RUN: saida/docs/doc-org-MMDDAA/<runId>/ — cada execução isolada.
- Dentro da mesma execução, dois componentes que gerariam o mesmo nome de arquivo
  (ex.: `Meu_Flow` e `Meu-Flow`) recebem sufixo com hash do fullName; nada é sobrescrito.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from salesforce_docs.utils import read_json, rel, sha256_text, write_json, write_text

MANIFEST = ".manifest.json"
ARCHIVE = "_substituidos"


class OutputWriter:
    def __init__(self, base_dir: Path, run_id: str, layout: str, project_root: Path, run_state, log):
        self.run_id = run_id
        self.root = Path(project_root)
        self.dir = Path(base_dir) / run_id if layout == "BY_RUN" else Path(base_dir)
        self.layout = layout
        self.state = run_state
        self.log = log
        self.written = {}  # nome do arquivo -> identificador do componente (nesta execução)
        self.manifest_path = self.dir / MANIFEST
        self.manifest = read_json(self.manifest_path) if self.manifest_path.is_file() else {}
        self.state.data.setdefault("output", {"layout": layout, "dir": rel(self.dir, self.root),
                                              "replaced": [], "collisions": []})

    def write(self, filename: str, text: str, component_key: str) -> Path:
        name = filename
        if name in self.written and self.written[name] != component_key:
            digest = hashlib.sha256(component_key.encode("utf-8")).hexdigest()[:8]
            stem, ext = os.path.splitext(filename)
            name = f"{stem}-{digest}{ext}"
            self.state.data["output"]["collisions"].append(
                {"file": filename, "component": component_key, "writtenAs": name,
                 "conflictsWith": self.written[filename]})
            self.log.warn(f"Colisão de nome de documento: {filename} já gerado por {self.written[filename]}; "
                          f"{component_key} gravado como {name}")
        path = self.dir / name
        new_sha = sha256_text(text)
        if path.is_file():
            prev = self.manifest.get(name) or {}
            prev_run = prev.get("runId")
            same_run = prev_run == self.run_id
            old_sha = sha256_text(path.read_text(encoding="utf-8"))
            if not same_run and old_sha != new_sha:
                archive = self.dir / ARCHIVE / (prev_run or "origem-desconhecida") / name
                n = 1
                while archive.exists():
                    n += 1
                    archive = archive.with_name(f"{Path(name).stem}-{n}{Path(name).suffix}")
                archive.parent.mkdir(parents=True, exist_ok=True)
                os.replace(path, archive)
                self.state.data["output"]["replaced"].append(
                    {"file": rel(path, self.root), "previousRun": prev_run,
                     "archivedAs": rel(archive, self.root)})
                self.log.warn(f"{rel(path, self.root)} de {prev_run or 'origem desconhecida'} "
                              f"substituído; versão anterior em {rel(archive, self.root)}")
        write_text(path, text)
        self.written[name] = component_key
        self.manifest[name] = {"runId": self.run_id, "component": component_key, "sha256": new_sha}
        write_json(self.manifest_path, self.manifest)
        return path
