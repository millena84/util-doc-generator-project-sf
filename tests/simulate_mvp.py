"""Simulação SIMULADA de ponta a ponta de todas as documentações do MVP.

Executa o pipeline real com a Salesforce CLI simulada (tests/fixtures/bin/sf, cenário
`mvp_complete`) e a Metadata API simulada, em um diretório isolado, e escreve um
relatório Markdown passo a passo com comandos, arquivos gerados e documentos finais.

Uso:
    python3 -m tests.simulate_mvp [--out DIR] [--report ARQUIVO.md]

Nada é escrito em catalog/, inventory/, runs/ ou saida/ do repositório.
"""

import argparse
import io
import json
import os
import shutil
import tempfile
from pathlib import Path

from tests.helpers import SIMULATED_ORG_ID, FAKE_SF, ROOT, FakeMetadataClient, fake_sf_env
from salesforce_docs.pipeline.document_pipeline import DocumentPipeline
from salesforce_docs.salesforce.cli_runner import CliRunner

TRACE = [  # componente rastreado em detalhe: (passo, arquivo, máx. linhas)
    ("3", "catalog/org-dev/api-v67/org-display.raw.json", 0),
    ("4", "catalog/org-dev/api-v67/metadata-types.index.json", 20),
    ("5", "catalog/org-dev/api-v67/schemas/flow.schema.json", 20),
    ("6", "inventory/org-dev/api-v67/flows/inventory.index.json", 20),
    ("7", "inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json", 0),
    ("7", "inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml", 0),
    ("8", "inventory/org-dev/api-v67/flows/normalized/meu-flow.json", 0),
    ("9", "inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json", 0),
]
STEP_OF_COMMAND = [
    ("--version", "1"), ("org list --json", "2"), ("org display", "3"),
    ("org list metadata-types", "4"), ("org list metadata ", "6"),
    ("project retrieve start", "7"), ("data query", "9"),
]


def step_of(cmd):
    for prefix, step in STEP_OF_COMMAND:
        if cmd.startswith(prefix):
            return step
    return "?"


def fence(text, lang=""):
    return f"```{lang}\n{text.rstrip()}\n```\n"


def head(text, n):
    lines = text.splitlines()
    if n and len(lines) > n:
        return "\n".join(lines[:n] + [f"... ({len(lines) - n} linhas omitidas)"])
    return text


def simulate(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for d in ("config", "documentation"):
        shutil.copytree(ROOT / d, out_dir / d)
    # Aprova a org SIMULADA (sem aprovação o utilitário para antes de qualquer coleta).
    cfg_path = out_dir / "config" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["approvedOrgs"] = [{"orgId": SIMULATED_ORG_ID, "alias": "dev", "note": "org SIMULADA"}]
    cfg_path.write_text(json.dumps(cfg, indent=2))
    calls = out_dir / "sf-calls.log"
    fake_sf_env("mvp_complete")
    os.environ["FAKE_SF_STATE"] = str(calls)
    log = io.StringIO()
    pipeline = DocumentPipeline(out_dir, runner=CliRunner(executable=str(FAKE_SF)),
                                metadata_client_factory=lambda s: FakeMetadataClient(s), stream=log)
    code, state = pipeline.run()
    return code, state, log.getvalue(), calls.read_text().splitlines()


def build_report(out_dir, code, state, log_text, calls):
    data = state.data
    rel = lambda p: p.relative_to(out_dir).as_posix()  # noqa: E731
    r = ["# Relatório de simulação — todas as documentações do MVP\n",
         "> **SIMULADO.** CLI `sf` simulada (`tests/fixtures/bin/sf`, cenário `mvp_complete`) e "
         "Metadata API simulada. Nenhum dado veio de uma org real. Gerado por "
         "`python3 -m tests.simulate_mvp`.\n",
         f"- Execução: `{data['runId']}` — status **{data['status']}** — código de saída `{code}`",
         f"- Org: `{data['orgAlias']}` — API `{data['apiVersion']}`",
         f"- Cobertura: **{data['coverage']['status']}** — {data['coverage']['documented']} documentada(s) "
         f"de {data['coverage']['inScope']} no escopo; lacunas: {data['coverage']['gapCount']} "
         f"({', '.join(k for k, v in data['coverage']['gaps'].items() if v) or 'nenhuma'})\n",
         "## 1. Saída no terminal\n", fence(log_text),
         "## 2. Comandos executados na CLI (por passo)\n",
         "| # | Passo | Comando |", "|---|---|---|"]
    for i, c in enumerate(calls, 1):
        r.append(f"| {i} | {step_of(c)} | `sf {c}` |")
    r.append("\nO passo 5 (`describeValueType`) é SOAP direto na Metadata API, fora da CLI; "
             "o passo 8 (XML → JSON) e o passo 10 (Markdown) são locais.\n")

    r += ["## 3. Situação por metadata type\n",
          "| Metadata type | Habilitado (4) | Schema (5) | Inventário (6) | Componentes |",
          "|---|---|---|---|---|"]
    by_type = {}
    for t in data["metadataTypes"]:
        by_type.setdefault(t["metadataType"], {})[t["stage"]] = t
    for name in sorted(by_type):
        s = by_type[name]
        inv = s.get("inventory", {})
        r.append(f"| {name} | {s.get('enabled', {}).get('status', '—')} | "
                 f"{s.get('schema', {}).get('status', '—')} | "
                 f"{inv.get('status', 'via retrieve do CustomObject')} | {inv.get('count', '—')} |")

    r += ["\n## 4. Documentos gerados (passo 10)\n",
          "| Documento | Modelo | Principal | Relacionados no documento | Status |",
          "|---|---|---|---|---|"]
    docs = []
    for c in data["components"]:
        if c.get("role") != "primary":
            continue
        related = ", ".join(f"{x['fullName']} ({x['metadataType']})"
                            for x in c.get("relatedComponents") or []) or "—"
        for d in [c] + list(c.get("subDocuments") or []):
            if d.get("document"):
                docs.append(d["document"])
                r.append(f"| `{d['document'].rsplit('/', 1)[1]}` | `{d['template']}` | "
                         f"{c['metadataType']}:{c['component']} | "
                         f"{related if d is c else '(subdocumento)'} | {d['status']} |")

    r += ["\n## 5. Rastreamento de um componente: `Flow:Meu_Flow`\n"]
    for step, path, n in TRACE:
        p = out_dir / path
        if p.is_file():
            lang = "xml" if path.endswith(".xml") else "json"
            text = p.read_text(encoding="utf-8")
            if path.endswith("org-display.raw.json"):
                # o raw em disco fica inalterado; só a cópia no relatório é mascarada
                raw = json.loads(text)
                raw["result"]["accessToken"] = "********"
                text = json.dumps(raw, indent=2) + "\n"
            r += [f"**Passo {step}** — `{path}`\n", fence(head(text, n), lang)]

    r += ["## 6. Árvore de arquivos gerados\n"]
    tree = []
    for top in ("catalog", "inventory", "runs", "saida"):
        tree += [rel(p) for p in sorted((out_dir / top).rglob("*")) if p.is_file()]
    r.append(fence("\n".join(tree)))

    r += ["## 7. Conteúdo dos documentos finais\n"]
    for d in docs:
        r += [f"### `{d}`\n", fence((out_dir / d).read_text(encoding="utf-8"), "markdown")]
    return "\n".join(r) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", help="Diretório da simulação (padrão: temporário)")
    ap.add_argument("--report", help="Arquivo do relatório (padrão: <out>/relatorio-simulacao-mvp.md)")
    args = ap.parse_args(argv)
    out_dir = Path(args.out).resolve() if args.out else Path(tempfile.mkdtemp(prefix="sfdocs-sim-"))
    if out_dir.exists() and any(out_dir.iterdir()):
        ap.error(f"diretório não vazio: {out_dir}")
    code, state, log_text, calls = simulate(out_dir)
    report = Path(args.report) if args.report else out_dir / "relatorio-simulacao-mvp.md"
    report.write_text(build_report(out_dir, code, state, log_text, calls), encoding="utf-8")
    print(f"Simulação em: {out_dir}\nRelatório: {report}\nStatus: {state.data['status']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
