"""Ponto de entrada único: `python -m salesforce_docs <comando>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from salesforce_docs import __version__
from salesforce_docs.errors import ConfigError
from salesforce_docs.utils import normalize_api_version


def _project_root(value):
    if value:
        return Path(value).resolve()
    # src/salesforce_docs/cli.py -> raiz do projeto
    return Path(__file__).resolve().parents[2]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="salesforce_docs",
        description="Utilitário único de documentação Markdown de componentes Salesforce.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--project-root", help="Raiz do projeto (padrão: diretório do utilitário)")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Executa o pipeline completo (passos 1–10)")
    run.add_argument("--target-org", "-o", help="Alias da org (padrão: config.json orgAlias)")
    run.add_argument("--api-version", help="Sobrepõe a API version detectada em `sf org display`")
    run.add_argument("--group", action="append",
                     help="Restringe o escopo do config.json ao(s) grupo(s) informado(s) (ex.: --group Flow)")
    run.add_argument("--component", action="append",
                     help="Restringe o escopo do config.json ao(s) componente(s) informado(s) (fullName)")
    run.add_argument("--resume", metavar="RUN_ID",
                     help="Retoma execução (ou 'latest') sem reprocessar componentes SUCCESS")

    regen = sub.add_parser("regenerate",
                           help="Regera derivados e Markdown a partir dos raws/XMLs (sem acessar a org)")
    regen.add_argument("--run", default="latest", help="Execução de origem (padrão: latest)")

    sub.add_parser("validate-config", help="Valida config, contratos e modelos (sem acessar a org)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = _project_root(args.project_root)
    from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
    try:
        pipeline = DocumentPipeline(root)
        if args.command == "run":
            api = normalize_api_version(args.api_version) if args.api_version else None
            code, _ = pipeline.run(org_alias=args.target_org, api_version=api, groups=args.group,
                                   components=args.component, resume=args.resume)
            return code
        if args.command == "regenerate":
            code, _ = pipeline.regenerate(args.run)
            return code
        if args.command == "validate-config":
            from salesforce_docs.validation.project_validator import validate_project
            from salesforce_docs.rendering.template_loader import ContractStore
            warnings = validate_project(pipeline.app, pipeline.mvp,
                                        ContractStore(pipeline.app.contracts_dir, pipeline.mvp))
            for w in warnings:
                print(f"AVISO: {w}", file=sys.stderr)
            from salesforce_docs.config.scope import describe_effective, resolve_scope
            effective = resolve_scope(pipeline.app.scope, pipeline.mvp)
            print(f"Org alias: {pipeline.app.org_alias} (config.json)")
            if pipeline.app.approved_orgs:
                ids = ", ".join(e["orgId"] for e in pipeline.app.approved_orgs)
                print(f"Orgs aprovadas: {ids}")
            else:
                print("AVISO: approvedOrgs vazio — `run` para antes de qualquer coleta até a org ser aprovada",
                      file=sys.stderr)
            print(f"Proteção de dados: privateFiles={pipeline.app.private_files}, "
                  f"orgDisplayRaw={pipeline.app.org_display_raw_policy}, "
                  f"outputLayout={pipeline.app.output_layout}")
            print(f"Escopo: {pipeline.app.scope.mode}")
            for group, comps in describe_effective(effective).items():
                print(f"  - {group}: {', '.join(comps)}")
            print("Configuração válida.")
            return 0
    except (ConfigError, ValueError) as exc:
        print(f"ERRO de configuração: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
