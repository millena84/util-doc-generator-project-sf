"""Consultas SOQL (Tooling API ou API padrão) via `sf data query --json`."""

from __future__ import annotations


class ToolingApiClient:
    def __init__(self, runner, session):
        self.runner = runner
        self.session = session

    def query(self, soql, raw_path=None, error_raw_path=None, use_tooling_api=True):
        args = [
            "data", "query",
            "--query", soql,
            "--target-org", self.session.alias,
            "--api-version", self.session.api_version,
            "--json",
        ]
        if use_tooling_api:
            args.insert(4, "--use-tooling-api")
        return self.runner.run(args, raw_path=raw_path, error_raw_path=error_raw_path)


def soql_literal(value: str) -> str:
    """Escapa valor para uso entre aspas simples em SOQL."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")
