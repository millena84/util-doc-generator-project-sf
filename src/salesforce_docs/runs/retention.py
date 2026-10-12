"""Retenção de execuções (`purge`): DESCONTINUA, não apaga.

Padrão (sem --apply): só lista as execuções mais antigas que o corte; nada muda.

--apply: marca cada execução listada como DESCONTINUADA no próprio run state
(`discontinued = {at, reason}`) e, no layout BY_RUN, grava `DESCONTINUADO.md` na
pasta de documentos da execução. Execuções descontinuadas deixam de ser usadas por
`--resume latest` e `regenerate --run latest`; um id explícito é recusado. Nenhum
arquivo é apagado (raws, XMLs e documentos permanecem).

--apply --delete-sensitive (opt-in explícito): além de marcar, apaga os artefatos
SENSÍVEIS referenciados somente por execuções descontinuadas — erros sanitizados
(runs/<id>/errors), raw do `sf org display`, XMLs recuperados, normalizados e
dados internos (SOQL). Arquivo referenciado por execução ativa nunca é apagado,
e só são apagados caminhos dentro de catalog/, inventory/ e runs/.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

from salesforce_docs.errors import ConfigError
from salesforce_docs.utils import iso_now, now_local, read_json, rel, write_json, write_text

MARKER = "DESCONTINUADO.md"


def _load_runs(runs_dir):
    runs = []
    for f in sorted(Path(runs_dir).glob("run-*.json")):
        try:
            runs.append((f, read_json(f)))
        except (OSError, ValueError):
            continue
    return runs


def _started(data):
    try:
        value = datetime.fromisoformat(str(data.get("startedAt")))
    except ValueError:
        return None
    return value if value.tzinfo else value.astimezone()


def _sensitive_refs(data):
    """Caminhos (relativos à raiz) de artefatos sensíveis citados pela execução."""
    refs = set()
    for c in data.get("components") or []:
        for key in ("xml", "normalized", "internalData"):
            if c.get(key):
                refs.add(c[key])
        for f in c.get("files") or []:
            if f.get("path"):
                refs.add(f["path"])
    for s in data.get("steps") or []:
        detail = s.get("detail")
        if s.get("step") == "3-org-display" and isinstance(detail, str) and detail:
            refs.add(detail)
    return refs


def _inside(path, roots):
    path = path.resolve()
    for r in roots:
        try:
            path.relative_to(r.resolve())
            return True
        except ValueError:
            continue
    return False


def purge(app, older_than_days, apply=False, delete_sensitive=False, now=None, stream=None):
    out = stream or sys.stdout
    if older_than_days is None or older_than_days < 0:
        raise ConfigError("purge: --older-than-days deve ser um inteiro >= 0")
    if delete_sensitive and not apply:
        raise ConfigError("purge: --delete-sensitive exige --apply")
    root = Path(app.project_root)
    cutoff = (now or now_local()) - timedelta(days=older_than_days)
    runs = _load_runs(app.runs_dir)
    selected, active = [], []
    for path, data in runs:
        if data.get("discontinued"):
            continue
        started = _started(data)
        if started is not None and started < cutoff:
            selected.append((path, data))
        else:
            active.append((path, data))

    mode = "APLICAR" if apply else "SOMENTE LISTAR"
    print(f"purge ({mode}): {len(selected)} execução(ões) iniciada(s) antes de "
          f"{cutoff.isoformat(timespec='seconds')}", file=out)
    for path, data in selected:
        print(f"  - {data.get('runId')} ({data.get('startedAt')}, {data.get('status')})", file=out)
    if not apply:
        if selected:
            print("Nada alterado. Use --apply para marcar como DESCONTINUADAS.", file=out)
        return 0

    reason = f"purge --older-than-days {older_than_days}"
    # Retomada com resumeOutput = ORIGINAL_FOLDER reaproveita a pasta da execução de origem:
    # pasta ainda usada por execução ativa não recebe o marcador de descontinuada.
    active_dirs = {(d.get("output") or {}).get("dir") for _, d in active}
    for path, data in selected:
        data["discontinued"] = {"at": iso_now(), "reason": reason}
        out_info = data.get("output") or {}
        if out_info.get("layout") == "BY_RUN" and out_info.get("dir") and out_info["dir"] not in active_dirs:
            out_dir = root / out_info["dir"]
            if out_dir.is_dir():
                write_text(out_dir / MARKER,
                           f"# Execução `{data.get('runId')}` DESCONTINUADA\n\n"
                           f"- Em: {data['discontinued']['at']}\n- Motivo: {reason}\n\n"
                           "Os documentos desta pasta não são mais mantidos pelo utilitário.\n")

    if delete_sensitive:
        keep = set()
        for _, data in active:
            keep |= _sensitive_refs(data)
        roots = [app.paths["catalog"], app.paths["inventory"], app.paths["runs"]]
        for path, data in selected:
            deleted = []
            errors_dir = Path(app.runs_dir) / str(data.get("runId")) / "errors"
            if errors_dir.is_dir() and data.get("runId"):
                shutil.rmtree(errors_dir)
                deleted.append(rel(errors_dir, root))
            for ref in sorted(_sensitive_refs(data) - keep):
                target = root / ref
                if target.is_file() and _inside(target, roots):
                    target.unlink()
                    deleted.append(ref)
            data["discontinued"]["deletedSensitive"] = deleted
            print(f"  {data.get('runId')}: {len(deleted)} artefato(s) sensível(is) apagado(s)", file=out)

    for path, data in selected:
        write_json(path, data, private=True)
    print(f"{len(selected)} execução(ões) marcada(s) como DESCONTINUADA(S).", file=out)
    return 0
