#!/usr/bin/env bash
# Fase 2 — descoberta de integrações a partir dos JSONs normalizados do Utilitário 1.
# Uso: bin/integration-discovery.sh [run] --csv discovery/input/componentes-squad.csv [--target-org dev] [--api-version 67.0]
#      bin/integration-discovery.sh review --cluster cluster-001 --decision APPROVED --by "Nome" [--notes "..."] [--name "..."]
# Não acessa a org: só lê inventory/**/normalized/*.json. Requer python3 (>= 3.8).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m integration_discovery "$@"
