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


RESUME_OUTPUT_CHOICES = ("ORIGINAL_FOLDER", "TODAY")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="salesforce_docs",
        description="Utilitário único de documentação Markdown de componentes Salesforce.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--project-root", help="Raiz do projeto (padrão: diretório do utilitário)")
    parser.add_argument("--debug", action="store_true",
                        help="Em erro inesperado, mostra o traceback (sempre mascarado)")
    sub = parser.add_subparsers(dest="command", required=True)

    # `run` com login exige org autenticada (Salesforce CLI). Por ora, login em org produtiva NÃO é
    # permitido: use só desenvolvimento/sandbox. Produção: `run --source-dir` (modo pasta), que lê o
    # repositório já clonado (ex.: Flosum), sem login e sem Salesforce CLI.
    run = sub.add_parser("run", help="Executa o pipeline completo (passos 1–10)")
    run.add_argument("--target-org", "-o", help="Alias da org (padrão: config.json orgAlias)")
    run.add_argument("--source-dir", metavar="PASTA",
                     help="Modo pasta: lê os metadados do repositório já clonado nesta pasta, sem login e "
                          "sem Salesforce CLI. A pasta precisa estar em config.json sourceRepositories")
    run.add_argument("--api-version", help="Sobrepõe a API version detectada em `sf org display`")
    run.add_argument("--group", action="append",
                     help="Restringe o escopo do config.json ao(s) grupo(s) informado(s) (ex.: --group Flow)")
    run.add_argument("--component", action="append",
                     help="Restringe o escopo do config.json ao(s) componente(s) informado(s) (fullName)")
    run.add_argument("--non-interactive", action="store_true",
                     help="Nunca pergunta: org fora de approvedOrgs é recusada (padrão sem terminal)")
    run.add_argument("--resume", metavar="RUN_ID",
                     help="Retoma execução (ou 'latest') sem reprocessar componentes SUCCESS")
    run.add_argument("--resume-output", choices=RESUME_OUTPUT_CHOICES, type=str.upper,
                     help="Na retomada: grava na pasta da execução de origem (ORIGINAL_FOLDER) "
                          "ou na pasta do dia atual (TODAY). Padrão: config.json execution.resumeOutput")

    regen = sub.add_parser("regenerate",
                           help="Regera derivados e Markdown a partir dos raws/XMLs (sem acessar a org)")
    regen.add_argument("--run", default="latest", help="Execução de origem (padrão: latest)")
    regen.add_argument("--resume-output", choices=RESUME_OUTPUT_CHOICES, type=str.upper,
                       help="Grava na pasta da execução de origem (ORIGINAL_FOLDER) ou na do dia (TODAY)")

    pg = sub.add_parser("purge", help="Retenção: marca execuções antigas como DESCONTINUADAS "
                                      "(padrão: só lista; nada é apagado)")
    pg.add_argument("--older-than-days", type=int, required=True, help="Idade mínima (dias) da execução")
    pg.add_argument("--apply", action="store_true", help="Aplica a marcação (sem isso, só lista)")
    pg.add_argument("--delete-sensitive", action="store_true",
                    help="Com --apply: apaga também os artefatos sensíveis usados SÓ por execuções "
                         "descontinuadas (raw do org display, erros, XML e normalizados)")

    vc = sub.add_parser("validate-config", help="Valida config, contratos e modelos (sem acessar a org)")
    vc.add_argument("--strict", action="store_true",
                    help="Trata avisos (modelo ausente, propriedade sem uso etc.) como erro")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = _project_root(args.project_root)
    from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
    pipeline = None
    try:
        interactive = False if getattr(args, "non_interactive", False) else None
        pipeline = DocumentPipeline(root, interactive=interactive)
        if getattr(args, "resume_output", None):
            pipeline.app.resume_output = args.resume_output  # sobrepõe o config.json nesta execução
        if args.command == "purge":
            from salesforce_docs.runs.retention import purge
            return purge(pipeline.app, args.older_than_days, apply=args.apply,
                         delete_sensitive=args.delete_sensitive)
        if args.command == "run":
            api = normalize_api_version(args.api_version) if args.api_version else None
            code, _ = pipeline.run(org_alias=args.target_org, api_version=api, groups=args.group,
                                   components=args.component, resume=args.resume,
                                   source_dir=args.source_dir)
            return code
        if args.command == "regenerate":
            code, _ = pipeline.regenerate(args.run)
            return code
        if args.command == "validate-config":
            from salesforce_docs.validation.project_validator import validate_project
            from salesforce_docs.rendering.template_loader import ContractStore
            warnings = validate_project(pipeline.app, pipeline.mvp,
                                        ContractStore(pipeline.app.contracts_dir, pipeline.mvp),
                                        strict=args.strict)
            for w in warnings:
                print(f"AVISO: {w}", file=sys.stderr)
            from salesforce_docs.validation.git_guard import check_git
            git = check_git(pipeline.app)
            if not git["available"]:
                print(f"AVISO: verificação de Git indisponível ({git['reason']})", file=sys.stderr)
            else:
                if git["tracked"]:
                    print("ERRO: arquivos sensíveis rastreados pelo Git (o .gitignore não protege "
                          "o que já foi commitado):", file=sys.stderr)
                    for f in git["tracked"]:
                        print(f"  - {f}", file=sys.stderr)
                    return 1
                for f in git["notIgnored"]:
                    print(f"AVISO: caminho sensível não ignorado pelo .gitignore: {f}", file=sys.stderr)
                if git["notIgnored"] and args.strict:
                    print("ERRO: [strict] caminhos sensíveis não ignorados", file=sys.stderr)
                    return 1
                print("Git: nenhum arquivo sensível rastreado; caminhos sensíveis ignorados.")
            from salesforce_docs.config.scope import describe_effective, resolve_scope
            effective = resolve_scope(pipeline.app.selection, pipeline.mvp)
            print(f"Org alias: {pipeline.app.org_alias} (config.json)")
            for repo in pipeline.app.source_repositories:
                print(f"Repositório (modo pasta): {repo['folder']} -> org {repo['orgName']}")
            if pipeline.app.approved_orgs:
                ids = ", ".join(e["orgId"] for e in pipeline.app.approved_orgs)
                print(f"Orgs aprovadas: {ids}")
            else:
                print("AVISO: approvedOrgs vazio — `run` para antes de qualquer coleta até a org ser aprovada",
                      file=sys.stderr)
            print(f"Proteção de dados: privateFiles={pipeline.app.private_files}, "
                  f"orgDisplayRaw={pipeline.app.org_display_raw_policy}, "
                  f"outputLayout={pipeline.app.output_layout}, "
                  f"resumeOutput={pipeline.app.resume_output}")
            print(f"Seleção: {pipeline.app.selection.mode}")
            for group, comps in describe_effective(effective).items():
                print(f"  - {group}: {', '.join(comps)}")
            print("Configuração válida.")
            return 0
    except (ConfigError, ValueError) as exc:
        mask = pipeline.masker if pipeline is not None else (lambda t: t)
        print(f"ERRO de configuração: {mask(str(exc))}", file=sys.stderr)
        return 1
    except Exception as exc:  # nunca imprimir traceback/mensagem sem máscara
        mask = pipeline.masker if pipeline is not None else (lambda t: t)
        print(f"ERRO inesperado ({type(exc).__name__}): {mask(str(exc))}", file=sys.stderr)
        if args.debug:
            import traceback
            print(mask(traceback.format_exc()), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
