"""CLI da Fase 2: `python -m integration_discovery [run] --csv ... | review ...`.

Separada do CLI do Utilitário 1 (`python -m salesforce_docs`), que não é alterado nesta fase.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from integration_discovery import __version__
from integration_discovery.discovery_pipeline import review_cluster, run_discovery

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def build_parser():
    parser = argparse.ArgumentParser(prog="integration_discovery",
                                     description="Fase 2: descobre clusters candidatos de integração "
                                                 "a partir dos JSONs normalizados do Utilitário 1.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run", help="Executa a descoberta (padrão quando nenhum subcomando é dado)")
    run.add_argument("--project-root", help="Raiz do projeto (padrão: diretório do utilitário)")
    run.add_argument("--csv", help="CSV curado; caminho relativo é resolvido a partir da pasta atual "
                                   "(padrão: <raiz do projeto>/discovery/input/componentes-squad.csv)")
    run.add_argument("--target-org", "-o", help="Alias da org do inventário (padrão: config.json orgAlias)")
    run.add_argument("--api-version", help="Versão da API do inventário (padrão: config.json defaultApiVersion)")
    run.add_argument("--no-cache", action="store_true", help="Reprocessa todos os componentes (ignora o cache)")
    rv = sub.add_parser("review", help="Registra a revisão humana de um cluster")
    rv.add_argument("--project-root", help="Raiz do projeto (padrão: diretório do utilitário)")
    rv.add_argument("--cluster", required=True, help="Ex.: cluster-001")
    rv.add_argument("--decision", required=True, type=str.upper, choices=["APPROVED", "REJECTED", "PENDING"])
    rv.add_argument("--by", help="Quem revisou (obrigatório para APPROVED/REJECTED)")
    rv.add_argument("--notes", help="Observações da revisão")
    rv.add_argument("--name", help="Nome escolhido (APPROVED; padrão: o nome proposto)")
    rv.add_argument("--signature",
                    help="Obrigatório: ao menos os 6 primeiros caracteres da assinatura mostrada no relatório "
                         "(validado pelo review, que explica o erro e não grava nada)")
    rv.add_argument("--target-org", "-o", help="Alias da org da descoberta (padrão: config.json orgAlias)")
    rv.add_argument("--api-version", help="Versão da API da descoberta (padrão: config.json defaultApiVersion)")
    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("run", "review", "-h", "--help", "--version"):
        argv = ["run"] + argv  # `python -m integration_discovery --csv ...` (sem subcomando)
    args = build_parser().parse_args(argv)
    root = Path(args.project_root) if args.project_root else DEFAULT_ROOT
    if args.command == "review":
        try:
            review_cluster(root, args.cluster, args.decision, args.by, args.notes, args.name,
                           signature=args.signature, alias=args.target_org, api_version=args.api_version)
        except ValueError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2
        return 0
    # --csv informado: relativo à pasta atual (como qualquer caminho de linha de comando);
    # sem --csv: o padrão dentro da raiz do projeto.
    csv_path = Path(args.csv).resolve() if args.csv else root / "discovery" / "input" / "componentes-squad.csv"
    code, _ = run_discovery(root, csv_path, args.target_org, args.api_version, use_cache=not args.no_cache)
    return code


if __name__ == "__main__":
    sys.exit(main())
