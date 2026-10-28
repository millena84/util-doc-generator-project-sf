#!/usr/bin/env bash
# Invólucro do utilitário único util-doc-generator-project-sf.
# Uso: bin/sf-docs.sh run [--group Flow] [--api-version 67.0] [--resume latest]
#      bin/sf-docs.sh run --source-dir <pasta do repositório clonado> [--group Profile]
#      bin/sf-docs.sh regenerate [--run latest]
#      bin/sf-docs.sh validate-config
# Requer apenas: bash, python3 (>= 3.8) e Salesforce CLI (`sf`). Sem pip install.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "ERRO: $PYTHON não encontrado no PATH." >&2
  exit 1
fi
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
  echo "ERRO: Python >= 3.8 é obrigatório." >&2
  exit 1
fi
# Modo pasta (run --source-dir) não usa a Salesforce CLI.
if [[ "${1:-}" == "run" ]] && [[ " $* " != *" --source-dir"* ]] && ! command -v sf >/dev/null 2>&1; then
  echo "ERRO: Salesforce CLI (sf) não encontrada. https://developer.salesforce.com/tools/salesforcecli" >&2
  exit 1
fi

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m salesforce_docs --project-root "$ROOT" "$@"
