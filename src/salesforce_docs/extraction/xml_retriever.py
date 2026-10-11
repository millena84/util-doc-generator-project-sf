"""Passo 7 — `sf project retrieve start` e cópia fiel do XML original.

O retrieve roda em um projeto SFDX temporário (o utilitário não exige que o
usuário tenha um projeto). Os arquivos recuperados são copiados byte a byte
para inventory/.../<tipo>/components/, preservando a estrutura de pastas do
formato source (ex.: objects/Obj__c/fields/Campo__c.field-meta.xml).
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from salesforce_docs import status as st
from salesforce_docs.utils import rel, sha256_file

PACKAGE_DIR = "force-app"


def _project_json(api_version):
    return json.dumps({
        "packageDirectories": [{"path": PACKAGE_DIR, "default": True}],
        "name": "util-doc-generator-retrieve",
        "sourceApiVersion": api_version,
    }, indent=2)


def _relative_to_package(file_path: Path, project_dir: Path) -> Path:
    base = project_dir / PACKAGE_DIR / "main" / "default"
    for candidate in (base, project_dir / PACKAGE_DIR, project_dir):
        try:
            return file_path.resolve().relative_to(candidate.resolve())
        except ValueError:
            continue
    return Path(file_path.name)


def _files_from_result(result):
    if not isinstance(result, dict):
        return []
    files = result.get("files") or []
    return files if isinstance(files, list) else [files]


def _messages_from_result(result):
    if not isinstance(result, dict):
        return []
    msgs = result.get("messages") or []
    msgs = msgs if isinstance(msgs, list) else [msgs]
    out = []
    for m in msgs:
        out.append(m.get("problem") or m.get("message") or json.dumps(m) if isinstance(m, dict) else str(m))
    return out


def retrieve_component(runner, session, metadata_type, full_name, components_dir, raw_path,
                       errors_raw_path, project_root):
    spec = f"{metadata_type}:{full_name}"
    with tempfile.TemporaryDirectory(prefix="sfdocs-retrieve-") as tmp:
        project_dir = Path(tmp)
        (project_dir / "sfdx-project.json").write_text(_project_json(session.api_version), encoding="utf-8")
        (project_dir / PACKAGE_DIR).mkdir()
        result = runner.run(
            ["project", "retrieve", "start", "--metadata", spec, "--target-org", session.alias,
             "--api-version", session.api_version, "--json"],
            raw_path=raw_path, error_raw_path=errors_raw_path, cwd=str(project_dir),
        )
        outcome = {"metadataType": metadata_type, "fullName": full_name,
                   "retrieveRaw": rel(result.raw_path, project_root) if result.raw_path else None,
                   "files": [], "status": None, "error": None}
        if not result.ok:
            outcome.update(status=st.RETRIEVE_FAILED, error=result.error_message)
            return outcome
        files = _files_from_result(result.result)
        failed = [f for f in files if str(f.get("state", "")).lower() == "failed"]
        copied = []
        for f in files:
            if f in failed or not f.get("filePath"):
                continue
            src = Path(f["filePath"])
            if not src.is_absolute():
                src = project_dir / src
            if not src.is_file():
                continue
            dest = components_dir / _relative_to_package(src, project_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)  # cópia byte a byte: XML original intacto
            copied.append({"type": f.get("type"), "fullName": f.get("fullName"),
                           "path": rel(dest, project_root), "sha256": sha256_file(dest)})
    outcome["files"] = copied
    problems = [f"{f.get('type')}:{f.get('fullName')}: {f.get('error') or f.get('problem') or 'Failed'}"
                for f in failed] + _messages_from_result(result.result)
    main = find_main_file(copied, metadata_type, full_name)
    if not copied:
        outcome.update(status=st.RETRIEVE_FAILED,
                       error="; ".join(problems) or "Retrieve não retornou arquivos")
    elif main is None:
        outcome.update(status=st.MISMATCH,
                       error=f"Nenhum arquivo recuperado corresponde a {spec}. "
                             f"Recebidos: {[(c['type'], c['fullName']) for c in copied]}")
    else:
        outcome.update(status=st.SUCCESS, xml=main["path"],
                       error="; ".join(problems) or None)
    return outcome


def find_main_file(files, metadata_type, full_name):
    """Arquivo XML principal do componente (valida tipo + fullName)."""
    candidates = [f for f in files if f.get("type") == metadata_type and str(f.get("path", "")).endswith(".xml")]
    for f in candidates:
        if f.get("fullName") == full_name:
            return f
    for f in candidates:
        if str(f.get("fullName", "")).lower() == full_name.lower():
            return f
    return None
