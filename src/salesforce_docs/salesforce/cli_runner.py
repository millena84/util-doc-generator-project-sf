"""Executa comandos `sf` via subprocesso (regras do prompt, seção 8.2).

- usa `--json` (exceto `sf --version`, que é a forma pedida no Passo 1);
- captura stdout/stderr e valida o código de saída;
- grava o stdout bruto ANTES de qualquer parse;
- detecta sessão expirada.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

from salesforce_docs.errors import CliNotFoundError, SessionExpiredError
from salesforce_docs.utils import write_json, write_text_raw

SESSION_EXPIRED_MARKERS = (
    "INVALID_SESSION_ID",
    "Session expired or invalid",
    "expired access/refresh token",
    "RefreshTokenAuthError",
    "invalid_grant",
)


class CliResult:
    def __init__(self, args, returncode, stdout, stderr, duration):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout or ""
        self.stderr = stderr or ""
        self.duration = duration
        self.raw_path = None
        self.data = None
        try:
            self.data = json.loads(self.stdout) if self.stdout.strip() else None
        except ValueError:
            self.data = None

    @property
    def ok(self) -> bool:
        if self.returncode != 0:
            return False
        if isinstance(self.data, dict) and self.data.get("status") not in (None, 0):
            return False
        return True

    @property
    def result(self):
        return self.data.get("result") if isinstance(self.data, dict) else None

    @property
    def error_name(self):
        return self.data.get("name") if isinstance(self.data, dict) else None

    @property
    def error_message(self) -> str:
        if isinstance(self.data, dict) and self.data.get("message"):
            return str(self.data.get("message"))
        return (self.stderr or self.stdout or f"exit code {self.returncode}").strip()

    def session_expired(self) -> bool:
        blob = f"{self.stdout}\n{self.stderr}"
        return any(m in blob for m in SESSION_EXPIRED_MARKERS)


class CliRunner:
    def __init__(self, executable="sf", timeout=900, save_raw=True, masker=None):
        self.executable = executable
        self.timeout = timeout
        self.save_raw = save_raw
        self.masker = masker or (lambda s: s)
        self.history = []

    def _resolve(self):
        path = shutil.which(self.executable)
        if not path:
            raise CliNotFoundError(
                f"Salesforce CLI ('{self.executable}') não encontrada no PATH. "
                "Instale: https://developer.salesforce.com/tools/salesforcecli"
            )
        return path

    def _env(self):
        env = dict(os.environ)
        env.setdefault("SF_JSON_TO_STDOUT", "true")
        env.setdefault("SF_DISABLE_AUTOUPDATE", "true")
        env.setdefault("SF_AUTOUPDATE_DISABLE", "true")
        env["NO_COLOR"] = "1"
        env["FORCE_COLOR"] = "0"
        return env

    def run(self, args, raw_path=None, error_raw_path=None, cwd=None, check_session=True) -> CliResult:
        """Executa `sf <args>`.

        raw_path: onde gravar o stdout bruto em caso de sucesso (código 0).
        error_raw_path: onde gravar o stdout bruto em caso de falha, para não
        sobrescrever um raw válido anterior com uma resposta de erro.
        """
        exe = self._resolve()
        cmd = [exe] + list(args)
        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=self._env(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            rc = -1
            out = exc.stdout if isinstance(exc.stdout, str) else ""
            err = f"Timeout após {self.timeout}s"
        duration = round(time.monotonic() - started, 3)

        result = CliResult(["sf"] + list(args), rc, out, err, duration)
        result.raw_path = None
        if rc == 0:
            if self.save_raw and raw_path and (out or "").strip():
                write_text_raw(raw_path, out)  # bruto, antes de qualquer parse
                result.raw_path = raw_path
        elif self.save_raw and error_raw_path and ((out or "").strip() or (err or "").strip()):
            # Resposta de ERRO: não é raw canônico e pode ecoar credenciais (ex.: token em
            # mensagem de falha). Grava envelope SANITIZADO (stdout/stderr mascarados),
            # identificado como tal — nunca como raw intacto.
            target = sanitized_error_path(error_raw_path)
            write_json(target, {
                "sanitized": True,
                "note": "Resposta de erro mascarada; não é raw intacto.",
                "command": self.masker(" ".join(result.args)),
                "returncode": rc,
                "stdout": self.masker(out or ""),
                "stderr": self.masker(err or ""),
            }, private=True)
            result.raw_path = target
        self.history.append(
            {"command": " ".join(result.args), "returncode": rc, "durationSeconds": duration}
        )
        if check_session and not result.ok and result.session_expired():
            raise SessionExpiredError(self.masker(result.error_message))
        return result


def sanitized_error_path(path):
    """runs/<id>/errors/x.raw.json -> runs/<id>/errors/x.sanitized.json"""
    from pathlib import Path
    path = Path(path)
    name = path.name
    for suffix in (".raw.json", ".json"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return path.with_name(name + ".sanitized.json")
