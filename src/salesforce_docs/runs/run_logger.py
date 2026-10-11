"""Log de execução: stderr + eventos no run state, sempre mascarando segredos."""

from __future__ import annotations

import sys
from datetime import datetime


class RunLogger:
    def __init__(self, masker, stream=None, run_state=None, verbose=True):
        self.masker = masker
        self.stream = stream or sys.stderr
        self.run_state = run_state
        self.verbose = verbose

    def _emit(self, level, message):
        message = self.masker(message)
        if self.verbose or level != "DEBUG":
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {level:<5} {message}", file=self.stream)
        if self.run_state is not None and level != "DEBUG":
            self.run_state.event(level, message)

    def debug(self, message):
        self._emit("DEBUG", message)

    def info(self, message):
        self._emit("INFO", message)

    def warn(self, message):
        self._emit("WARN", message)

    def error(self, message):
        self._emit("ERROR", message)
