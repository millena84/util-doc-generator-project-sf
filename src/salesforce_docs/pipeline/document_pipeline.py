"""Orquestra os passos 1–10 na ordem obrigatória e a regeneração offline."""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

from salesforce_docs import status as st
from salesforce_docs.config.config_loader import load_config
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs import __version__
from salesforce_docs.config.scope import WILDCARD, describe_effective, resolve_scope
from salesforce_docs.errors import ConfigError, GlobalFailure, SessionExpiredError
from salesforce_docs.extraction import (access_extractor, inventory_extractor, metadata_types_extractor,
                                        schema_extractor)
from salesforce_docs.extraction.internal_data_extractor import developer_name, extract_internal_data
from salesforce_docs.extraction.source_directory import SourceRepository, find_repository_entry
from salesforce_docs.pipeline import deviation_handler, run_index
from salesforce_docs.pipeline.component_pipeline import ComponentProcessor, normalize_record
from salesforce_docs.rendering.context import RenderContext
from salesforce_docs.rendering.markdown_renderer import MarkdownRenderer
from salesforce_docs.rendering.template_loader import ContractStore, TemplateLoader
from salesforce_docs.runs.run_logger import RunLogger
from salesforce_docs.runs.run_state import RunState
from salesforce_docs.salesforce.cli_runner import CliRunner, sanitized_error_path
from salesforce_docs.salesforce.metadata_api_client import MetadataApiClient
from salesforce_docs.parsing.xml_parser import redact
from salesforce_docs.salesforce.org_session import OrgSession, looks_like_session_token
from salesforce_docs.salesforce.tooling_api_client import ToolingApiClient
from salesforce_docs.pipeline.output_writer import OutputWriter, claim_org_folder, folder_org, same_org
from salesforce_docs.pipeline.run_summary import write_summary
from salesforce_docs.utils import (Masker, now_local, read_json, rel, set_private_files, sha256_file,
                                   sha256_text, slugify, write_json, write_text_raw)
from salesforce_docs.validation import cli_validator, org_session_validator
from salesforce_docs.validation.metadata_type_validator import check_enabled
from salesforce_docs.validation.git_guard import check_git
from salesforce_docs.validation.project_validator import validate_project

EXIT_OK, EXIT_FAILURE, EXIT_SESSION, EXIT_GAPS = 0, 1, 2, 3
# Chaves de `sf org display --json` que carregam credenciais (algumas só com --verbose).
ORG_DISPLAY_SECRET_KEYS = ("accessToken", "refreshToken", "sfdxAuthUrl", "password", "clientSecret")


class PipelineContext:
    """Dependências compartilhadas entre as etapas."""

    def __init__(self, root, app, mvp, runner, run_state, log, masker):
        self.root = Path(root).resolve()
        self.app = app
        self.mvp = mvp
        self.runner = runner
        self.run_state = run_state
        self.log = log
        self.masker = masker
        self.session = None
        self.catalog_dir = None
        self.schemas_dir = None
        self.inventory_dir = None
        self.errors_dir = None
        self.docs_dir = None
        self.writer = None
        self.discovered_types = None   # passo 4 (None = listagem não executada)
        self.access_index = None       # passo 6b (None = índice de acesso indisponível)
        self.prefetched = {}           # (tipo, nome) -> arquivos já recuperados no retrieve de acesso
        self.run_index = None          # automações por objeto e classes processadas (run_index.py)
        self.class_inventory = None    # nomes de ApexClass da org (lookupInventories); None = não listado
        self.processed_types = set()   # retrieve + normalização com sucesso
        self.contracts = ContractStore(app.contracts_dir, mvp)
        self.templates = None
        self.tooling = None
        self.source = None             # modo pasta: SourceRepository (None = modo com login na org)
        self.source_note = None        # modo pasta: origem exibida no topo de cada documento

    def bind_session(self, session):
        self.session = session
        self.catalog_dir = self.app.catalog_dir(session.alias, session.api_version)
        self.schemas_dir = self.catalog_dir / "schemas"
        self.inventory_dir = self.app.inventory_dir(session.alias, session.api_version)
        self.templates = TemplateLoader(self.app.models_dir(session.api_version), session.api_version)
        self.tooling = ToolingApiClient(self.runner, session)


class DocumentPipeline:
    def __init__(self, root, runner=None, metadata_client_factory=None, stream=None,
                 config_path=None, metadata_types_path=None, interactive=None, confirm_org=None):
        self.root = Path(root).resolve()
        self.masker = Masker()
        self.app = load_config(self.root, config_path)
        self.metadata_types_file = Path(metadata_types_path or self.app.metadata_types_path)
        self.mvp = load_metadata_types(self.root, self.metadata_types_file)
        # Confirmação interativa de org fora da allowlist: só com terminal (stdin e stderr TTY).
        # Sem terminal (CI/headless) a org não aprovada é sempre recusada.
        if interactive is None:
            interactive = (not os.environ.get("SFDOCS_NON_INTERACTIVE")
                           and sys.stdin.isatty() and sys.stderr.isatty())
        self.interactive = bool(interactive)
        self.confirm_org = confirm_org or _prompt_org_confirmation
        self.runner = runner or CliRunner(timeout=self.app.cli_timeout_seconds,
                                          save_raw=self.app.save_raw_responses, masker=self.masker)
        self.runner.masker = self.masker
        self.metadata_client_factory = metadata_client_factory or (
            lambda s: MetadataApiClient(s.instance_url, lambda: s.access_token, s.api_version,
                                        timeout=self.app.http_timeout_seconds))
        self.stream = stream
        self.renderer = MarkdownRenderer()

    # ==================================================================
    def run(self, org_alias=None, api_version=None, groups=None, components=None, resume=None,
            source_dir=None):
        """source_dir: modo pasta — lê os metadados de um repositório já clonado (sem login e sem
        Salesforce CLI); a pasta precisa estar em config.json sourceRepositories (de-para com a org)."""
        repo = None
        if source_dir:
            if org_alias:
                raise ConfigError("--source-dir e --target-org não podem ser usados juntos: o modo pasta "
                                  "não acessa a org")
            repo = find_repository_entry(self.app, source_dir)
            org_alias = repo[1].get("alias") or slugify(repo[1]["folder"])
        self.mvp.source_mode = repo is not None
        # Precedência do alias: --target-org > config.json (orgAlias).
        alias = org_alias or self.app.org_alias
        previous = None
        if resume:
            prev_path = RunState.find(self.app.runs_dir, resume, purpose="resume")
            if prev_path is None:
                raise ConfigError(f"Execução para retomar não encontrada (ou descontinuada/regeneração): {resume}")
            previous = RunState.load(prev_path)
        set_private_files(self.app.private_files)
        state = RunState.create(self.app.runs_dir, alias, resumed_from=previous.run_id if previous else None)
        state.masker = self.masker
        log = RunLogger(self.masker, stream=self.stream, run_state=state)
        p = PipelineContext(self.root, self.app, self.mvp, self.runner, state, log, self.masker)
        p.errors_dir = self.app.runs_dir / state.run_id / "errors"
        p.source_run = previous  # retomada: a saída pode seguir na pasta da execução de origem
        current_unit = {"entry": None}
        try:
            warnings = validate_project(self.app, self.mvp, p.contracts)
            for w in warnings:
                log.warn(w)
            effective = self._resolve_scope(p, alias, org_alias, groups, components)
            self._git_guard(p)
            # RESTRIÇÃO ATUAL (2026-10-13): os passos 1–7 e 9 exigem org autenticada pela CLI. Login em
            # org PRODUTIVA não é permitido por ora; use só org de desenvolvimento ou sandbox aprovada.
            # Produção: modo pasta (`--source-dir`), que lê o repositório já clonado (ex.: Flosum) e
            # substitui os passos 1–7; dados internos (passo 9) ficam "Não informado".
            if repo is None:
                self._step1_cli(p)
                self._step2_org_list(p, alias)
                self._step3_org_display(p, alias, api_version)
                self._check_org_approval(p, alias)  # nenhuma coleta antes de aprovar a org
                self._acquire_token(p, alias)       # token só depois da aprovação; nunca gravado
            else:
                self._open_source(p, repo[0], repo[1], api_version)
            fingerprint = self._fingerprint(p, alias, effective)
            state.set("fingerprint", fingerprint)
            skip_units = self._carry_compatible(p, previous, fingerprint, effective) if previous else set()
            if repo is None:
                enabled = self._step4_metadata_types(p, effective)
                self._step5_schemas(p, enabled)
                inventories = self._step6_inventories(p, enabled)
            else:
                enabled = self._source_step4(p, effective)
                inventories = self._source_step6(p, enabled)
            self._step6b_access_sources(p, enabled, inventories, effective)
            self._steps7_to_10(p, enabled, inventories, skip_units, effective, current_unit)
        except SessionExpiredError as exc:
            if current_unit["entry"] is not None:
                state.upsert_component(dict(current_unit["entry"], status=st.RETRY_REQUIRED,
                                            error=self.masker(exc.message)))
            suggestion = org_session_validator.login_suggestion(alias)
            state.finish(st.INTERRUPTED, {"code": "SESSION_EXPIRED", "message": self.masker(exc.message),
                                          "suggestion": suggestion})
            log.error(f"Sessão expirada: {exc.message}")
            log.error(f"Execute `{suggestion}` e retome com: --resume {state.run_id}")
            return EXIT_SESSION, state
        except GlobalFailure as exc:
            state.finish(st.FAILED, {"code": exc.code, "message": self.masker(exc.message),
                                     "suggestion": exc.suggestion})
            log.error(f"{exc.code}: {exc.message}")
            if exc.suggestion:
                log.error(f"Sugestão: {exc.suggestion}")
            return EXIT_FAILURE, state
        except ConfigError as exc:
            state.finish(st.FAILED, {"code": "CONFIG_ERROR", "message": self.masker(str(exc))})
            log.error(f"Configuração inválida: {exc}")
            return EXIT_FAILURE, state
        except Exception as exc:  # erro inesperado: estado coerente e mensagem mascarada
            message = self.masker(f"{type(exc).__name__}: {exc}")
            try:
                state.finish(st.FAILED, {"code": "UNEXPECTED_ERROR", "message": message})
            except OSError:
                pass  # ex.: disco cheio — o erro segue para o CLI (mascarado)
            log.error(f"Erro inesperado: {message}")
            raise
        finally:
            # O token só vive durante a execução, inclusive em caso de exceção não tratada.
            if p.session is not None:
                p.session.clear()
            try:
                self._apply_org_display_policy(p)
                state.data["metrics"] = self._metrics()
                state.set("coverage", self._coverage(state, p))
                if state.data["status"] != st.IN_PROGRESS:  # caminhos de falha já finalizados
                    write_summary(self, state, p)
            except OSError as exc:
                log.error(f"Não foi possível gravar estado/resumo: {self.masker(str(exc))}")
        final = self._final_status(state)
        state.data["commands"] = self.runner.history
        state.finish(final)
        try:
            write_summary(self, state, p)
        except OSError as exc:
            log.error(f"Não foi possível gravar o resumo: {self.masker(str(exc))}")
        cov = state.data["coverage"]
        log.info(f"Execução {state.run_id} finalizada: {final} {state.summary()}")
        line = (f"Cobertura: {cov['status']} — {cov['documented']} documentada(s) de {cov['inScope']} "
                f"no escopo; lacunas bloqueantes: {cov['blockingGapCount']}; avisos: {cov['warningCount']}")
        (log.info if cov["status"] == "COMPLETE" else log.warn)(line)
        types = cov["types"]
        log.info(f"Tipos: configurados {len(types['configured'])}, processados {len(types['processed'])}, "
                 f"documentados {len(types['documented'])}, sem modelo {len(types['withoutModel'])}, "
                 f"fora do escopo {len(types['excluded']['outOfScope'])}, "
                 f"não habilitados {len(types['excluded']['notEnabledInOrg'])}"
                 + (f", descobertos e não configurados {len(types['discoveredNotConfigured'])}"
                    if types["discoveredNotConfigured"] is not None else ""))
        log.info(f"Log: {rel(state.path, self.root)}")
        if final == st.COMPLETED_WITH_GAPS and self.app.strict_coverage:
            return EXIT_GAPS, state
        return (EXIT_OK if final in (st.SUCCESS, st.PARTIAL_SUCCESS, st.COMPLETED_WITH_GAPS)
                else EXIT_FAILURE), state

    def _git_guard(self, p):
        """O .gitignore não basta: arquivo sensível já rastreado bloqueia a execução
        antes de qualquer chamada à org; caminho sensível não ignorado gera aviso."""
        result = check_git(self.app)
        p.run_state.set("gitGuard", result)
        if not result["available"]:
            p.log.warn(f"Verificação de Git indisponível ({result['reason']}): proteção de versionamento "
                       "não verificada")
            return
        if result["tracked"]:
            raise GlobalFailure(
                "SENSITIVE_FILES_TRACKED",
                f"{len(result['tracked'])} arquivo(s) sensível(is) rastreado(s) pelo Git: "
                f"{', '.join(result['tracked'][:5])}{' ...' if len(result['tracked']) > 5 else ''}",
                "Remova do índice (git rm --cached <arquivo>) e avalie expurgo do histórico.")
        for path in result["notIgnored"]:
            p.log.warn(f"Caminho sensível não ignorado pelo .gitignore: {path}")

    # Aprovação da org (Prioridade 3) -----------------------------------
    def _check_org_approval(self, p, alias):
        s = p.session
        identity = {"orgId": s.org_id, "alias": alias, "username": s.username, "instanceUrl": s.instance_url}
        shown = ", ".join(f"{k}={v}" for k, v in identity.items())
        missing = [k for k in ("orgId", "username", "instanceUrl") if not identity[k]]
        if missing:
            raise GlobalFailure(
                "ORG_IDENTITY_UNVERIFIABLE",
                f"`sf org display` não informou {', '.join(missing)}; a identidade da org não pode ser "
                f"verificada ({shown}).",
                "Confira a autenticação/versão da CLI; nenhuma coleta será feita sem identidade.")
        candidates = [e for e in self.app.approved_orgs if e["orgId"][:15] == s.org_id[:15]]
        if not candidates:
            reason = ("Nenhuma org aprovada em config.json (approvedOrgs)" if not self.app.approved_orgs
                      else f"Org {s.org_id} não está em approvedOrgs")
            if self._interactive_confirmation(p, identity):
                return
            raise GlobalFailure(
                "ORG_NOT_APPROVED", f"{reason}. Org detectada: {shown}.",
                f'Confirme que é a org pretendida e adicione {{"orgId": "{s.org_id}", "alias": "{alias}"}} '
                "em approvedOrgs do config.json (ou confirme interativamente em um terminal).")
        mismatches = []
        for entry in candidates:
            diff = []
            if entry.get("alias") and entry["alias"] != alias:
                diff.append(f"alias ({entry['alias']} ≠ {alias})")
            if entry.get("username") and entry["username"].lower() != (s.username or "").lower():
                diff.append(f"username ({entry['username']} ≠ {s.username})")
            if entry.get("instanceUrl") and entry["instanceUrl"].rstrip("/").lower() != s.instance_url.lower():
                diff.append(f"instanceUrl ({entry['instanceUrl']} ≠ {s.instance_url})")
            if not diff:
                p.run_state.set("orgApproval", {"approved": True, "method": "ALLOWLIST", "entry": entry,
                                                "detected": identity})
                p.run_state.step("3b-org-approval", st.SUCCESS, f"orgId {s.org_id}")
                p.log.info(f"Passo 3b: org {s.org_id} aprovada (approvedOrgs)")
                return
            mismatches.append("; ".join(diff))
        raise GlobalFailure("ORG_NOT_APPROVED",
                            f"Org {s.org_id} aprovada, mas a identidade diverge: {' | '.join(mismatches)}.",
                            "Revise approvedOrgs ou o alias usado.")

    def _interactive_confirmation(self, p, identity):
        """Org fora da allowlist: em terminal, exige digitar o orgId exato; sem terminal, recusa."""
        if not self.interactive:
            p.run_state.set("orgApproval", {"approved": False, "method": "NON_INTERACTIVE_REFUSED",
                                            "detected": identity})
            return False
        typed = self.confirm_org(identity)
        ok = isinstance(typed, str) and typed.strip() != "" and \
            typed.strip()[:15] == identity["orgId"][:15] and len(typed.strip()) in (15, 18)
        p.run_state.set("orgApproval", {"approved": ok, "method": "INTERACTIVE", "detected": identity})
        if ok:
            p.run_state.step("3b-org-approval", st.SUCCESS, f"orgId {identity['orgId']} (confirmação interativa)")
            p.log.warn(f"Passo 3b: org {identity['orgId']} aprovada INTERATIVAMENTE apenas para esta execução; "
                       "para aprovação permanente, inclua-a em approvedOrgs")
        return ok

    def _acquire_token(self, p, alias):
        """Token para a Metadata API. CLIs recentes não exibem segredos em `sf org display`;
        nesse caso usa `sf org auth show-access-token --json` (resposta nunca gravada)."""
        token = getattr(p, "display_token", None)
        source = "sf org display"
        if not looks_like_session_token(token):
            res = p.runner.run(["org", "auth", "show-access-token", "--target-org", alias, "--json"],
                               check_session=False)
            data = res.result
            token = data.get("accessToken") if isinstance(data, dict) else (data if isinstance(data, str) else None)
            source = "sf org auth show-access-token"
            if res.ok and token:
                p.masker.add(token)
            if not res.ok or not looks_like_session_token(token):
                raise GlobalFailure(
                    "ACCESS_TOKEN_UNAVAILABLE",
                    "Token de acesso indisponível: `sf org display` não o exibe e "
                    f"`sf org auth show-access-token` falhou ({self.masker(res.error_message)[:200]}).",
                    "Atualize a Salesforce CLI ou reautentique: sf org login web --alias " + alias)
        p.masker.add(token)
        p.session.set_access_token(token)
        p.display_token = None
        p.run_state.set("tokenSource", source)
        p.log.info(f"Passo 3c: token de acesso obtido via `{source}` (não persistido)")

    def _save_org_display(self, p, result, raw_path):
        """Política R1: resposta com credencial não vira raw.

        CLIs que ainda exibem o token em `sf org display` geram só o envelope
        `org-display.sanitized.json` (credenciais como [REDACTED]); sem credencial
        na resposta, o raw é gravado intacto. Retorna o caminho gravado.
        """
        data = json.loads(json.dumps(result.data)) if isinstance(result.data, dict) else None
        display = (data or {}).get("result") if isinstance((data or {}).get("result"), dict) else {}
        has_secret = looks_like_session_token(display.get("accessToken")) or any(
            display.get(k) not in (None, "") for k in ORG_DISPLAY_SECRET_KEYS if k != "accessToken")
        if not has_secret:
            write_text_raw(raw_path, result.stdout, private=True)  # bruto, inalterado
            return raw_path
        redacted = redact(data, set(ORG_DISPLAY_SECRET_KEYS))
        path = raw_path.with_name("org-display.sanitized.json")
        write_json(path, {"sanitized": True,
                          "note": "Resposta de `sf org display` com credenciais; não é raw intacto.",
                          "redacted": redacted, "response": data}, private=True)
        p.log.info("Passo 3: `sf org display` exibiu credenciais; gravado só o envelope sanitizado")
        return path

    def _apply_org_display_policy(self, p):
        if self.app.org_display_raw_policy != "DELETE_AFTER_RUN":
            return
        removed = []
        for path in ([p.catalog_dir / "org-display.raw.json"] if p.catalog_dir else []) + \
                [sanitized_error_path(p.errors_dir / "org-display.raw.json")]:
            if path.is_file():
                path.unlink()
                removed.append(rel(path, self.root))
        p.run_state.data["dataProtection"] = {"orgDisplayRaw": "DELETE_AFTER_RUN", "removed": removed}

    # Retomada compatível (Prioridade 3) --------------------------------
    def _group_files(self, group, contracts_store, templates):
        """Contratos e modelos que influenciam os documentos de um grupo."""
        contracts = [group.contract_file] + [s.get("contract") for s in group.sub_documents]
        contracts += [self.mvp.contract_file(t) for t in group.related_types]
        models = []
        for name in contracts:
            c = contracts_store.get_file(name)
            if c and c.get("template"):
                models.append(templates.resolve_name(c["template"]))
        return sorted(set(x for x in contracts if x)), sorted(set(models))

    def _fingerprint(self, p, alias, effective):
        contracts = {f.name: sha256_file(f) for f in sorted(self.app.contracts_dir.glob("*.schema.json"))}
        models_dir = p.templates.models_dir
        models = {f.name: sha256_file(f) for f in sorted(models_dir.glob("*.md"))} if models_dir.is_dir() else {}
        policy = {"sensitive": sorted(self.mvp.sensitive_elements),
                  "omit": sorted(self.mvp.omit_from_documentation)}
        source = p.source.content_fingerprint() if p.source is not None else None
        return {"orgId": p.session.org_id, "orgAlias": alias, "apiVersion": p.session.api_version,
                "sourceRepository": source,
                "utilVersion": __version__, "selection": describe_effective(effective),
                "contracts": contracts, "models": models,
                "metadataTypesConfigSha256": sha256_file(self.metadata_types_file)
                if self.metadata_types_file.is_file() else None,
                "policySha256": sha256_text(json.dumps(policy, sort_keys=True))}

    def _carry_compatible(self, p, previous, fp, effective):
        prev_fp = previous.data.get("fingerprint")
        report = {"from": previous.run_id, "reused": [], "reprocessed": []}
        p.run_state.data["resume"] = report
        global_reasons = []
        if not prev_fp:
            global_reasons.append("execução anterior sem fingerprint (formato antigo)")
        else:
            for key, label in (("orgId", "org"), ("apiVersion", "API version"),
                               ("sourceRepository", "repositório de origem (pasta ou conteúdo)"),
                               ("policySha256", "política de dados sensíveis"),
                               ("utilVersion", "versão do utilitário"),
                               ("metadataTypesConfigSha256", "configuração de metadata types")):
                if prev_fp.get(key) != fp.get(key):
                    global_reasons.append(f"{label} mudou ({prev_fp.get(key)} → {fp.get(key)})")
        candidates = previous.successful_units()
        if global_reasons:
            for unit_id in sorted(candidates):
                report["reprocessed"].append({"unitId": unit_id, "reasons": global_reasons})
            p.log.warn(f"Retomada de {previous.run_id}: nada reaproveitado — {'; '.join(global_reasons)}")
            p.run_state.save()
            return set()
        allowed = set()
        for unit_id, entry in sorted(candidates.items()):
            reasons = []
            group = self.mvp.group(entry.get("group"))
            comps = effective.get(entry.get("group"), "OUT")
            if group is None or comps == "OUT" or (comps is not None and entry.get("component") not in comps):
                reasons.append("fora do escopo atual")
            else:
                contracts, models = self._group_files(group, p.contracts, p.templates)
                for name in contracts:
                    if prev_fp["contracts"].get(name) != fp["contracts"].get(name):
                        reasons.append(f"contrato {name} mudou")
                for name in models:
                    if prev_fp["models"].get(name) != fp["models"].get(name):
                        reasons.append(f"modelo {name} mudou")
            doc = entry.get("document")
            if doc and not (self.root / doc).is_file():
                reasons.append(f"documento {doc} não existe mais")
            xml_reason = self._xml_source_problem(entry)
            if xml_reason:
                reasons.append(xml_reason)
            if reasons:
                report["reprocessed"].append({"unitId": unit_id, "reasons": reasons})
            else:
                allowed.add(unit_id)
                report["reused"].append(unit_id)
        p.run_state.carry_successes_from(previous, only=allowed)
        p.log.info(f"Retomando {previous.run_id}: {len(allowed)} unidade(s) reaproveitada(s), "
                   f"{len(report['reprocessed'])} reprocessada(s)")
        for item in report["reprocessed"]:
            p.log.warn(f"{item['unitId']}: reprocessado — {'; '.join(item['reasons'])}")
        return allowed

    def _regenerate_differences(self, p, source):
        """Regeneração usa contratos/modelos/política ATUAIS sobre raws antigos: registra o que mudou."""
        prev_fp = source.data.get("fingerprint")
        diffs = []
        if not prev_fp:
            diffs.append("execução de origem sem fingerprint (formato antigo): diferenças não verificáveis")
        else:
            current = self._fingerprint(p, source.data.get("orgAlias"), {})
            for key, label in (("policySha256", "política de dados sensíveis"),
                               ("utilVersion", "versão do utilitário"),
                               ("metadataTypesConfigSha256", "configuração de metadata types")):
                if prev_fp.get(key) != current.get(key):
                    diffs.append(f"{label} mudou")
            for kind, label in (("contracts", "contrato"), ("models", "modelo")):
                before, now = prev_fp.get(kind) or {}, current.get(kind) or {}
                for name in sorted(set(before) | set(now)):
                    if before.get(name) != now.get(name):
                        diffs.append(f"{label} {name} mudou")
        p.run_state.data["regenerate"] = {"source": source.run_id, "differences": diffs}
        p.run_state.save()
        for d in diffs:
            p.log.warn(f"Regeneração de {source.run_id}: {d} (documentos usam a versão atual)")

    def _xml_source_problem(self, entry):
        """XML de origem ausente ou com sha256 diferente do registrado na execução."""
        xml = entry.get("xml")
        if not xml:
            return "XML de origem não registrado"
        path = self.root / xml
        if not path.is_file():
            return f"XML de origem ausente ({xml})"
        recorded = next((f.get("sha256") for f in entry.get("files") or [] if f.get("path") == xml), None)
        if recorded and sha256_file(path) != recorded:
            return f"XML de origem alterado ({xml})"
        return None

    # Cobertura (Prioridade 3) ------------------------------------------
    # Lacunas que impedem cobertura completa x avisos que só degradam o conteúdo.
    BLOCKING_GAPS = ("noTemplate", "failed", "subDocuments", "notFound")
    WARNING_GAPS = ("internalDataUnavailable", "notEnabled", "schemaUnavailable", "relatedNotResolved")

    def _coverage(self, state, p=None):
        prim = [c for c in state.data["components"] if c.get("role") == "primary"]
        gaps = {"noTemplate": [], "failed": [], "subDocuments": [], "internalDataUnavailable": [],
                "notFound": list((state.data.get("selection") or {}).get("notFound") or []),
                "notEnabled": [], "schemaUnavailable": [], "relatedNotResolved": []}
        documented = 0
        documented_types, related_types, no_template_types = set(), set(), set()
        for c in prim:
            key = f"{c.get('metadataType')}:{c.get('component')}"
            if c.get("status") == st.SUCCESS and c.get("document"):
                documented += 1
                documented_types.add(c.get("metadataType"))
                related_types.update(r["metadataType"] for r in c.get("relatedComponents") or [])
            elif c.get("status") == st.NO_TEMPLATE:
                gaps["noTemplate"].append(key)
                no_template_types.add(c.get("metadataType"))
            else:
                gaps["failed"].append({"component": key, "status": c.get("status")})
            for sub in c.get("subDocuments") or []:
                if sub.get("status") != st.SUCCESS:
                    gaps["subDocuments"].append({"component": sub.get("component"), "status": sub.get("status")})
                    if sub.get("status") == st.NO_TEMPLATE:
                        no_template_types.add(f"{c.get('metadataType')} (subdocumento)")
            if c.get("internalDataStatus") == st.INTERNAL_DATA_UNAVAILABLE:
                gaps["internalDataUnavailable"].append(key)
            for u in c.get("relatedNotResolved") or []:
                gaps["relatedNotResolved"].append(f"{key} → {u.get('metadataType')}")
        not_enabled, out_of_scope_groups = set(), set()
        for t in state.data.get("metadataTypes") or []:
            if t.get("stage") == "enabled" and t.get("status") == st.NOT_ENABLED:
                gaps["notEnabled"].append(f"{t.get('group')}/{t.get('metadataType')}")
                not_enabled.add(t.get("metadataType"))
            if t.get("stage") == "schema" and t.get("status") == st.SCHEMA_UNAVAILABLE:
                gaps["schemaUnavailable"].append(t.get("metadataType"))
            if t.get("stage") == "scope":
                out_of_scope_groups.add(t.get("group"))
        blocking = sum(len(gaps[k]) for k in self.BLOCKING_GAPS)
        warnings = sum(len(gaps[k]) for k in self.WARNING_GAPS)
        finished = state.data.get("failure") is None
        if not finished or blocking:
            status = "INCOMPLETE"
        elif warnings:
            status = "COMPLETE_WITH_WARNINGS"
        else:
            status = "COMPLETE"
        return {
            "status": status,
            "executionFinished": finished,
            "inScope": len(prim) + len(gaps["notFound"]),
            "documented": documented,
            "gapCount": blocking + warnings,
            "blockingGapCount": blocking,
            "warningCount": warnings,
            "gaps": gaps,
            "outOfScopeGroups": sorted(out_of_scope_groups),
            "types": self._type_coverage(p, out_of_scope_groups, not_enabled, documented_types,
                                         related_types, no_template_types),
        }

    def _type_coverage(self, p, out_of_scope_groups, not_enabled, documented, related, no_template):
        """Cobertura por metadata type: descobertos, configurados, excluídos, processados,
        documentados e sem modelo."""
        configured = set()
        for g in self.mvp.groups:
            configured.update(g.all_types)
            if g.type_definition:
                configured.add(g.type_definition["metadataType"])
        out_of_scope = set()
        for g in self.mvp.groups:
            if g.name in out_of_scope_groups:
                out_of_scope.add(g.primary_type)
        discovered = getattr(p, "discovered_types", None) if p is not None else None
        processed = set(getattr(p, "processed_types", set())) if p is not None else set()
        missing_model = set(no_template)
        for g in self.mvp.groups:
            contract = p.contracts.get_file(g.contract_file) if p is not None else None
            if contract is None or (p is not None and p.templates is not None
                                    and p.templates.load(contract.get("template")) is None):
                missing_model.add(f"{g.primary_type} (estático: contrato/modelo ausente)")
        return {
            "discovered": {"count": len(discovered) if discovered is not None else None,
                           "available": discovered is not None},
            "configured": sorted(configured),
            "discoveredNotConfigured": sorted(discovered - configured) if discovered is not None else None,
            "excluded": {
                "byConfig": sorted(self.mvp.excluded),
                "outOfScope": sorted(out_of_scope),
                "notEnabledInOrg": sorted(not_enabled),
            },
            "processed": sorted(processed),
            "documented": sorted(documented),
            "documentedAsRelated": sorted(related - documented),
            "withoutModel": sorted(missing_model),
        }

    def _resolve_scope(self, p, alias, cli_alias, groups, components):
        """Valida e registra o escopo antes de qualquer chamada à org."""
        effective = resolve_scope(self.app.selection, self.mvp, groups, components)
        if self.mvp.org_alias and self.mvp.org_alias != self.app.org_alias:
            p.log.warn(f"orgAlias de metadata-types-mvp.json ({self.mvp.org_alias}) difere do config.json "
                       f"({self.app.org_alias}); vale o config.json")
        p.run_state.set("selection", {
            "mode": self.app.selection.mode,
            "requested": self.app.selection.describe(),
            "cli": {"targetOrg": None if self.mvp.source_mode else cli_alias, "groups": groups or [],
                    "components": components or []},
            "orgAlias": alias,
            "orgAliasSource": ("sourceRepositories (modo pasta)" if self.mvp.source_mode
                               else "--target-org" if cli_alias else "config.json"),
            "effective": describe_effective(effective),
            "notFound": [],
            "relatedNotResolved": [],
        })
        p.log.info(f"Seleção {self.app.selection.mode}: {describe_effective(effective)}")
        return effective

    def _final_status(self, state):
        """SUCCESS só com cobertura sem lacunas bloqueantes.

        - componentes com falha => PARTIAL_SUCCESS (ou FAILED);
        - execução sem falhas, mas com modelo ausente, subdocumento sem modelo ou
          componente pedido não encontrado => COMPLETED_WITH_GAPS (nunca SUCCESS).
        """
        statuses = [c.get("status") for c in state.data["components"] if c.get("role") == "primary"]
        failed = [s for s in statuses if s not in (st.SUCCESS, st.NO_TEMPLATE)]
        if failed:
            if self.app.allow_partial_success and len(failed) < len(statuses):
                return st.PARTIAL_SUCCESS
            return st.FAILED
        coverage = state.data.get("coverage") or {}
        if coverage.get("blockingGapCount"):
            return st.COMPLETED_WITH_GAPS
        return st.SUCCESS

    # Passo 1 ------------------------------------------------------------
    def _step1_cli(self, p):
        version = cli_validator.validate_cli(p.runner, self.app.minimum_cli_version)
        p.run_state.set("cli", {"version": version, "minimumVersion": self.app.minimum_cli_version})
        p.run_state.step("1-cli-version", st.SUCCESS, version)
        p.log.info(f"Passo 1: Salesforce CLI {version} (mínima {self.app.minimum_cli_version})")

    # Passo 2 ------------------------------------------------------------
    def _step2_org_list(self, p, alias):
        # A saída de `sf org list` é dado local da CLI (pode conter tokens): não é persistida.
        result = p.runner.run(["org", "list", "--json"], check_session=False)
        org_session_validator.validate_alias_present(result, alias)
        p.run_state.step("2-org-list", st.SUCCESS, f"alias '{alias}' encontrado")
        p.log.info(f"Passo 2: alias '{alias}' autenticado")

    # Passo 3 ------------------------------------------------------------
    def _step3_org_display(self, p, alias, api_version_override):
        result = p.runner.run(["org", "display", "--target-org", alias, "--json"], check_session=False)
        display = result.result if isinstance(result.result, dict) else {}
        p.masker.add(display.get("accessToken"))
        if not (result.ok and display.get("apiVersion") and display.get("connectedStatus") == "Connected"):
            if self.app.save_raw_responses and (result.stdout.strip() or result.stderr.strip()):
                # Erro de `org display` pode conter token: só envelope sanitizado.
                write_json(sanitized_error_path(p.errors_dir / "org-display.raw.json"), {
                    "sanitized": True, "note": "Resposta de erro mascarada; não é raw intacto.",
                    "returncode": result.returncode, "stdout": self.masker(result.stdout),
                    "stderr": self.masker(result.stderr)}, private=True)
            org_session_validator.validate_display(result, alias)
            raise GlobalFailure("ORG_DISPLAY_INCOMPLETE", "`sf org display` sem apiVersion",
                                org_session_validator.login_suggestion(alias))
        session = OrgSession.from_display_result(alias, display, api_version_override)
        session.set_access_token(None)  # token só em _acquire_token, após a aprovação
        p.display_token = display.get("accessToken")
        p.bind_session(session)
        raw_path = p.catalog_dir / "org-display.raw.json"
        if self.app.save_raw_responses:
            raw_path = self._save_org_display(p, result, raw_path)
        org_session_validator.validate_display(result, alias)
        p.run_state.data["apiVersion"] = session.api_version
        p.run_state.set("session", session.describe())
        p.run_state.step("3-org-display", st.SUCCESS, rel(raw_path, self.root))
        p.log.info(f"Passo 3: {session.username} conectado; API {session.api_version} "
                   f"(detectada {session.detected_api_version}, fonte: {session.api_version_source})")

    # Passo 4 ------------------------------------------------------------
    def _step4_metadata_types(self, p, effective):
        group_filter = set(effective)
        index, raw_path, _ = metadata_types_extractor.extract_metadata_types(
            p.runner, p.session, p.catalog_dir, p.errors_dir)
        p.discovered_types = set(index.get("metadataTypes", {})) | set(index.get("childMetadataTypes", {}))
        p.run_state.step("4-metadata-types", st.SUCCESS, rel(raw_path, self.root))
        enabled = {}
        for group in self.mvp.groups:
            if group.name not in group_filter:
                # Configurado, mas fora do escopo desta execução (≠ NOT_ENABLED / NO_TEMPLATE).
                p.run_state.type_status(group.primary_type, st.OUT_OF_SCOPE, group=group.name,
                                        stage="scope", detail=f"selection.mode={self.app.selection.mode}")
                continue
            types = list(group.all_types)
            if group.type_definition:
                types.append(group.type_definition["metadataType"])
            group_types = {}
            for t in types:
                info = check_enabled(index, t)
                p.run_state.type_status(t, info["status"], group=group.name, stage="enabled",
                                        kind=info.get("kind"))
                if info["status"] == st.ENABLED:
                    group_types[t] = info
                else:
                    p.log.warn(f"Passo 4: {group.name}/{t} -> NOT_ENABLED")
            if group.primary_type not in group_types:
                continue
            enabled[group.name] = group_types
        p.log.info(f"Passo 4: grupos habilitados: {', '.join(enabled) or 'nenhum'}")
        return enabled

    # Passo 5 ------------------------------------------------------------
    def _step5_schemas(self, p, enabled):
        client = self.metadata_client_factory(p.session)
        done = set()
        for group_name, types in enabled.items():
            for t in types:
                if t in done:
                    continue
                done.add(t)
                res = schema_extractor.extract_schema(client, t, p.schemas_dir, p.errors_dir,
                                                      save_raw=self.app.save_raw_responses)
                p.run_state.type_status(t, res["status"], group=None, stage="schema",
                                        detail=self.masker(res.get("error")),
                                        errorClass=classify_error(res.get("error")),
                                        raw=rel(res["raw"], self.root) if res.get("raw") else None,
                                        schema=rel(res["schema"], self.root) if res.get("schema") else None)
                if res["status"] != st.SUCCESS:
                    p.log.warn(f"Passo 5: {t} -> SCHEMA_UNAVAILABLE ({res.get('error')})")
        p.run_state.step("5-describe-value-type", st.SUCCESS, f"{len(done)} tipo(s)")

    # Passo 6 ------------------------------------------------------------
    def _step6_inventories(self, p, enabled):
        inventories = {}
        for group_name, types in enabled.items():
            group = self.mvp.group(group_name)
            if group.data.get("fixedComponents"):
                continue  # componente fixo (ex.: Settings:Security): nada a listar
            listable = [t for t in group.all_types if t in types and not self.mvp.retrieved_with(t)]
            for t in listable:
                if t in inventories:
                    continue
                type_dir = p.inventory_dir / self.mvp.folder(t)
                res = inventory_extractor.extract_inventory(p.runner, p.session, t, type_dir, p.errors_dir)
                inventories[t] = res["components"]
                p.run_state.type_status(t, res["status"], group=None, stage="inventory",
                                        detail=self.masker(res.get("error")), count=len(res["components"]),
                                        errorClass=classify_error(res.get("error")),
                                        raw=rel(res["raw"], self.root) if res.get("raw") else None)
                if res["status"] == st.NO_COMPONENTS:
                    p.log.info(f"Passo 6: {t} -> NO_COMPONENTS")
                elif res["status"] != st.SUCCESS:
                    p.log.warn(f"Passo 6: {t} -> {res['status']}: {res.get('error')}")
                else:
                    p.log.info(f"Passo 6: {t} -> {len(res['components'])} componente(s)")
        self._lookup_inventories(p, enabled, inventories)
        p.run_state.step("6-list-metadata", st.SUCCESS, f"{len(inventories)} tipo(s)")
        return inventories

    def _lookup_inventories(self, p, enabled, inventories):
        """Inventários só para conferência (grupo.lookupInventories), ex.: ApexClass para a trigger
        saber se o nome referenciado é uma classe da org. Não documenta nem recupera componentes."""
        available = getattr(p, "discovered_types", None) or set()
        for group_name in enabled:
            for t in self.mvp.group(group_name).data.get("lookupInventories") or []:
                if t in inventories or t not in available:
                    continue
                type_dir = p.inventory_dir / self.mvp.folder(t)
                res = inventory_extractor.extract_inventory(p.runner, p.session, t, type_dir, p.errors_dir)
                if res["status"] in (st.SUCCESS, st.NO_COMPONENTS):
                    inventories[t] = res["components"]
                    p.log.info(f"Passo 6: {t} (conferência) -> {len(res['components'])} componente(s)")
                else:
                    p.log.warn(f"Passo 6: inventário de conferência {t} falhou: {self.masker(res.get('error'))}")
        if "ApexClass" in inventories:
            p.class_inventory = [i["fullName"] for i in inventories["ApexClass"]]

    # Modo pasta (run --source-dir) ---------------------------------------
    def _open_source(self, p, path, entry, api_version_override):
        """Substitui os passos 1–3c: sem CLI, sem login e sem token. A pasta só é lida se estiver no
        de-para sourceRepositories (equivale ao approvedOrgs); o repositório nunca é alterado."""
        repo = SourceRepository(path, entry, self.mvp.source_directory, self.root)
        api = api_version_override or self.app.default_api_version or self.mvp.api_version
        if not api:
            raise ConfigError("Modo pasta: informe --api-version ou defaultApiVersion no config.json")
        session = OrgSession(repo.alias, None, "", None, api)
        session.api_version_source = "--api-version" if api_version_override else "config.json defaultApiVersion"
        p.bind_session(session)
        p.source = repo
        manifest = repo.write_manifest(p.catalog_dir / "source-manifest.json")
        info = dict(repo.describe(), manifest=rel(manifest, self.root))
        p.source_note = source_note(info)
        p.run_state.data["mode"] = "SOURCE_DIRECTORY"
        p.run_state.data["apiVersion"] = session.api_version
        p.run_state.set("session", session.describe())
        p.run_state.set("source", info)
        p.run_state.step("3-source-directory", st.SUCCESS, info["manifest"])
        p.log.info(f"Modo pasta: repositório {repo.folder} (org: {repo.org_name}), formato {repo.format}, "
                   f"{len(repo.files)} arquivo(s) de metadata em {info['metadataPath']}; sem login e sem "
                   f"Salesforce CLI; API {session.api_version} ({session.api_version_source})")
        p.log.info("Modo pasta: dados internos (passo 9) e describeValueType (passo 5) exigem a org e não "
                   "são feitos; essas linhas ficam 'Não informado'")
        if repo.unmapped_folders:
            p.log.info(f"Modo pasta: pastas sem metadata type configurado (não documentadas): "
                       f"{', '.join(repo.unmapped_folders)}")
        for folder, count in sorted(repo.ignored.items()):
            p.log.info(f"Modo pasta: {count} arquivo(s) de {folder}/ sem metadata type configurado "
                       "(ex.: listViews de objetos); não usados")
        for problem in repo.problems:
            p.log.warn(f"Modo pasta: {problem}")

    def _source_step4(self, p, effective):
        """Passo 4 no modo pasta: o tipo é lido se tiver pasta configurada em sourceDirectory.
        A habilitação na org não é verificável; o describeValueType (passo 5) não é feito."""
        readable = p.source.readable_types()
        p.discovered_types = p.source.found_types()
        p.run_state.step("4-metadata-types", st.SUCCESS, "modo pasta: tipos com pasta em sourceDirectory")
        enabled = {}
        for group in self.mvp.groups:
            if group.name not in effective:
                p.run_state.type_status(group.primary_type, st.OUT_OF_SCOPE, group=group.name,
                                        stage="scope", detail=f"selection.mode={self.app.selection.mode}")
                continue
            types = list(group.all_types)
            if group.type_definition:
                types.append(group.type_definition["metadataType"])
            fixed = [c.get("retrieveType") or group.primary_type for c in group.data.get("fixedComponents") or []]
            group_types = {}
            for t in types:
                ok = t in readable or (t == group.primary_type and fixed and all(r in readable for r in fixed))
                status = st.ENABLED if ok else st.NOT_ENABLED
                p.run_state.type_status(t, status, group=group.name, stage="enabled",
                                        detail="modo pasta: lido do repositório" if ok
                                        else "modo pasta: tipo sem pasta em sourceDirectory")
                if ok:
                    group_types[t] = {"status": st.ENABLED}
                else:
                    p.log.warn(f"Passo 4: {group.name}/{t} -> NOT_ENABLED (sem pasta em sourceDirectory)")
            if group.primary_type in group_types:
                enabled[group.name] = group_types
        for t in sorted({t for types in enabled.values() for t in types}):
            p.run_state.type_status(t, st.SCHEMA_UNAVAILABLE, group=None, stage="schema",
                                    detail="modo pasta: describeValueType exige a org")
        p.log.info(f"Passo 4: grupos lidos do repositório: {', '.join(enabled) or 'nenhum'}")
        return enabled

    def _source_step6(self, p, enabled):
        """Passo 6 no modo pasta: inventário = componentes encontrados no repositório."""
        inventories = {}
        manifest = rel(p.source.manifest, self.root)

        def list_type(t, label=""):
            type_dir = p.inventory_dir / self.mvp.folder(t)
            items = p.source.inventory(t)
            index = inventory_extractor.build_inventory_index(t, items, manifest)
            write_json(type_dir / "inventory.index.json", index)
            inventories[t] = index["components"]
            return index["components"]

        for group_name, types in enabled.items():
            group = self.mvp.group(group_name)
            if group.data.get("fixedComponents"):
                continue
            for t in [t for t in group.all_types if t in types and not self.mvp.retrieved_with(t)]:
                if t in inventories:
                    continue
                comps = list_type(t)
                status = st.SUCCESS if comps else st.NO_COMPONENTS
                p.run_state.type_status(t, status, group=None, stage="inventory", count=len(comps),
                                        raw=manifest, detail="modo pasta: componentes do repositório")
                p.log.info(f"Passo 6: {t} -> {len(comps)} componente(s) no repositório")
        for group_name in enabled:
            for t in self.mvp.group(group_name).data.get("lookupInventories") or []:
                if t not in inventories and t in p.source.readable_types():
                    p.log.info(f"Passo 6: {t} (conferência) -> {len(list_type(t))} componente(s) no repositório")
        if "ApexClass" in inventories:
            p.class_inventory = [i["fullName"] for i in inventories["ApexClass"]]
        p.run_state.step("6-list-metadata", st.SUCCESS, f"{len(inventories)} tipo(s) (modo pasta)")
        return inventories

    # Passo 6b -----------------------------------------------------------
    def _doc_specs(self, enabled, inventories, effective):
        """Componentes documentados que entram no retrieve de acesso.

        selection.mode ALL sem filtro de componentes: o tipo inteiro (`Tipo`). Com filtro de
        componentes (`--component` no ALL) ou SELECTED: sempre `Tipo:Nome` dos componentes
        documentados (mesmo com `components: ALL` no SELECTED) — nada fora do pedido é recuperado
        (minimização de dados: pedir um componente não pode trazer o código do tipo inteiro).
        """
        whole_types = str(self.app.selection.mode).upper() == "ALL"
        specs = set()
        for group_name in enabled:
            group = self.mvp.group(group_name)
            component_filter = effective.get(group_name)
            for unit in deviation_handler.build_units(group, inventories, self.mvp):
                if component_filter is not None and unit["fullName"] not in component_filter:
                    continue
                whole = whole_types and component_filter is None and not group.data.get("fixedComponents")
                specs.add(unit["metadataType"] if whole else f"{unit['metadataType']}:{unit['fullName']}")
        return specs

    def _step6b_access_sources(self, p, enabled, inventories, effective):
        """Retrieve único de Profile/PermissionSet/PermissionSetGroup/Queue/SharingRules junto com
        os componentes documentados; índice derivado de 'onde cada componente está configurado'."""
        cfg = self.mvp.access_sources
        if not cfg or not cfg.get("enabled", True):
            p.run_state.set("access", {"status": "DISABLED"})
            return
        available = (p.source.readable_types() if p.source is not None
                     else getattr(p, "discovered_types", None) or set())
        specs, missing = access_extractor.access_specs(cfg, self._doc_specs(enabled, inventories, effective),
                                                       available)
        access_dir = p.inventory_dir / cfg.get("folder", "access")
        info = {"status": None, "specs": specs, "missingTypes": missing, "index": None}
        if missing:
            p.log.warn(f"Passo 6b: tipos de acesso não habilitados na org: {', '.join(missing)}")
        if not any(t in specs for t in cfg.get("retrieveTypes", [])):
            info["status"] = st.NOT_ENABLED
            p.run_state.set("access", info)
            return
        if p.source is not None:  # modo pasta: arquivos do repositório clonado
            res = p.source.collect(specs, access_dir / "components")
        else:
            res = access_extractor.retrieve_access_sources(p.runner, p.session, specs, access_dir,
                                                           p.errors_dir, self.root)
        if not res["ok"]:
            info.update(status=st.RETRIEVE_FAILED, error=self.masker(res["error"]))
            p.run_state.set("access", info)
            p.log.warn(f"Passo 6b: retrieve das fontes de acesso falhou ({self.masker(res['error'])}); "
                       "seções de acesso ficam 'Não informado'")
            return
        source_types = set(cfg.get("retrieveTypes", []))
        index = access_extractor.build_access_index(
            [f for f in res["files"] if f.get("type") in source_types], self.root, cfg)
        info.update(status=st.SUCCESS, retrieveRaw=res["retrieveRaw"],
                    index=access_extractor.save_access_index(index, access_dir, self.root, res["retrieveRaw"]),
                    sourceFiles=len(index["sourceFiles"]), problems=res["problems"])
        p.access_index = index
        # Fontes que também são documentadas (ex.: PermissionSet) reaproveitam o XML completo.
        for f in res["files"]:
            if f.get("type") in source_types:
                p.prefetched.setdefault((f["type"], f["fullName"]), []).append(f)
        p.prefetched_raw = res["retrieveRaw"]
        p.run_state.set("access", info)
        p.run_state.step("6b-access-sources", st.SUCCESS, info["index"])
        p.log.info(f"Passo 6b: {len(index['sourceFiles'])} fonte(s) de acesso; índice em {info['index']}")

    def _load_access_index(self, p, source):
        """Regeneração: reconstrói o índice a partir dos XMLs de acesso da execução de origem."""
        info = source.data.get("access") or {}
        cfg = self.mvp.access_sources
        if not cfg or not info.get("index") or not (self.root / info["index"]).is_file():
            return
        saved = read_json(self.root / info["index"])
        files = [f for f in saved.get("sourceFiles", []) if (self.root / f["path"]).is_file()]
        if len(files) != len(saved.get("sourceFiles", [])):
            p.log.warn("Regeneração: fontes de acesso ausentes; seções de acesso podem ficar incompletas")
        p.access_index = access_extractor.build_access_index(files, self.root, cfg)
        p.run_state.set("access", dict(info, regeneratedFrom=source.run_id))

    # Pasta de saída ------------------------------------------------------
    def _open_writer(self, p, alias, org_id, source=None):
        """Define a pasta dos documentos e cria o OutputWriter.

        - Pasta do dia por org: saida/docs/doc-<alias>-MMDDAA/. Orgs diferentes nunca
          compartilham pasta: se a pasta do dia já pertence a outro orgId (mesmo alias
          apontando para outra org), usa doc-<alias>-<orgId>-MMDDAA/.
        - Retomada/regeneração com resumeOutput = ORIGINAL_FOLDER (padrão): grava na
          pasta da execução de origem, mesmo que tenha sido em outro dia.
        """
        day = now_local().strftime("%m%d%y")
        out = {"resumeOutput": self.app.resume_output}
        prev_out = (source.data.get("output") or {}) if source is not None else {}
        override = None
        base = None
        if source is not None and self.app.resume_output == "ORIGINAL_FOLDER" and prev_out.get("dir"):
            prev_dir = self.root / prev_out["dir"]
            if prev_out.get("baseDir"):
                prev_base = self.root / prev_out["baseDir"]
            else:  # execuções anteriores a este campo
                prev_base = prev_dir.parent if prev_out.get("layout") == "BY_RUN" else prev_dir
            owner = folder_org(prev_base)
            if owner and org_id and not same_org(owner, org_id):
                p.log.warn(f"Pasta da execução de origem {rel(prev_base, self.root)} pertence a outra org "
                           f"({owner}); documentos desta execução vão para a pasta do dia")
            else:
                base, override = prev_base, prev_dir
                out["originFolder"] = {"runId": source.run_id, "startedAt": source.data.get("startedAt")}
        if base is None:
            base = self.app.output_docs_dir / f"doc-{slugify(alias or 'org')}-{day}"
            owner = folder_org(base)
            if owner and org_id and not same_org(owner, org_id):
                separate = self.app.output_docs_dir / f"doc-{slugify(alias or 'org')}-{org_id}-{day}"
                p.log.warn(f"{rel(base, self.root)} pertence à org {owner}; o alias '{alias}' aponta "
                           f"agora para {org_id}: documentos em {rel(separate, self.root)}")
                out["orgFolderConflict"] = {"folder": rel(base, self.root), "owner": owner}
                base = separate
        claim_org_folder(base, org_id, alias)
        p.docs_dir = base
        p.writer = OutputWriter(base, p.run_state.run_id, self.app.output_layout, self.root,
                                p.run_state, p.log, dir_override=override)
        p.run_state.data["output"].update(out, baseDir=rel(base, self.root), orgId=org_id)
        if source is not None:
            self._report_resume_output(p, source, override)
        p.run_state.save()

    def _report_resume_output(self, p, source, override):
        """Orientação ao retomar/regenerar: onde os documentos ficam e defasagem entre os dias."""
        started = str(source.data.get("startedAt") or "")[:10]
        try:
            age = (now_local().date() - datetime.date.fromisoformat(started)).days
        except ValueError:
            age = None
        where = rel(p.writer.dir, self.root)
        if override is not None:
            msg = (f"Documentos em {where}: pasta da execução de origem {source.run_id}"
                   + (f" (coleta de {started})" if started else ""))
        else:
            prev_dir = (source.data.get("output") or {}).get("dir")
            msg = (f"Documentos em {where} (pasta do dia)"
                   + (f"; os herdados de {source.run_id} continuam em {prev_dir}" if prev_dir else ""))
        p.log.info(msg)
        p.run_state.data["output"]["resumeNote"] = msg
        if age is not None and age > self.app.resume_warn_after_days:
            warn = (f"Execução de origem {source.run_id} tem {age} dia(s): a pasta mistura coletas de "
                    "datas diferentes e a org pode ter mudado. Se a defasagem for relevante, faça uma "
                    "execução completa nova (sem --resume).")
            p.log.warn(warn)
            p.run_state.data["output"]["resumeAgeWarning"] = warn

    # Passos 7–10 --------------------------------------------------------
    def _steps7_to_10(self, p, enabled, inventories, skip_units, effective, current_unit):
        self._open_writer(p, p.session.alias, p.session.org_id, getattr(p, "source_run", None))
        processor = ComponentProcessor(p)
        # Plano completo antes de processar: permite registrar pendentes em interrupção.
        plan, ignored, not_selected = [], {}, {}
        for group_name, types in enabled.items():
            group = self.mvp.group(group_name)
            units = deviation_handler.build_units(group, inventories, self.mvp)
            component_filter = effective.get(group_name)
            self._report_not_found(p, group, units, inventories, component_filter)
            if group.unit_mode == "PER_COMPONENT":
                built = {u["fullName"] for u in units}
                skipped = sorted(i["fullName"] for i in inventories.get(group.primary_type) or []
                                 if i["fullName"] not in built)
                if skipped:
                    ignored[group.name] = {"count": len(skipped), "sample": skipped[:20],
                                           "reason": "componentFilter do grupo"}
            if not units:
                p.run_state.type_status(group.primary_type, st.NO_COMPONENTS, group=group.name, stage="units")
                continue
            outside = [u["fullName"] for u in units
                       if component_filter is not None and u["fullName"] not in component_filter]
            if outside:
                not_selected[group.name] = {"count": len(outside), "sample": sorted(outside)[:20]}
            for unit in units:
                if component_filter is not None and unit["fullName"] not in component_filter:
                    continue  # fora da seleção: não é recuperado
                if unit["unitId"] in skip_units:
                    p.log.info(f"{unit['unitId']}: SUCCESS em execução anterior, ignorado")
                    continue
                plan.append((group, types, unit))
        # Grupos que usam o índice da execução (ex.: ApexTrigger) vão por último: os documentos
        # deles mostram automações de outros grupos processados antes nesta execução.
        plan.sort(key=lambda item: bool(item[0].data.get("usesRunIndex")))
        progress = {"planned": len(plan), "completed": 0, "pending": [u["unitId"] for _, _, u in plan]}
        p.run_state.data.update(ignoredByFilter=ignored, notSelected=not_selected, progress=progress)
        p.run_state.save()
        for index, (group, types, unit) in enumerate(plan, start=1):
            if group.data.get("usesRunIndex") and p.run_index is None:
                self._prepare_run_index(p, plan, processor)
            entry = {"unitId": unit["unitId"], "group": group.name, "role": "primary",
                     "metadataType": unit["documentType"], "component": unit["fullName"],
                     "status": st.IN_PROGRESS}
            current_unit["entry"] = entry
            p.run_state.upsert_component(entry)
            p.log.info(f"[{index}/{len(plan)}] {unit['unitId']}")
            try:
                entry = self._process_unit(p, group, unit, types, inventories, processor)
            except SessionExpiredError:
                raise
            except Exception as exc:  # falha por componente não derruba a execução
                entry = dict(entry, status=st.FAILED, error=self.masker(f"{type(exc).__name__}: {exc}"))
                p.log.error(f"{unit['unitId']}: FAILED {self.masker(str(exc))}")
            entry["errorClass"] = classify_error(entry.get("error"))
            entry["processedOn"] = now_local().date().isoformat()
            p.run_state.upsert_component(entry)
            progress["completed"] += 1
            progress["pending"].remove(unit["unitId"])
            p.run_state.save()
            current_unit["entry"] = None
            self._record_processed(p, processor)

    def _prepare_run_index(self, p, plan, processor):
        """Processa antes (retrieve + normalização) todas as unidades dos grupos que usam o índice,
        para que cada documento enxergue as demais (ex.: outras triggers do mesmo objeto), e
        monta o índice com tudo o que foi processado ou herdado (retomada)."""
        for group, _types, unit in plan:
            if not group.data.get("usesRunIndex"):
                continue
            try:
                processor.process(unit["metadataType"], unit["fullName"], unit["inventoryItem"],
                                  folder_type=unit["documentType"])
            except SessionExpiredError:
                raise
            except Exception as exc:  # a falha reaparece (e é registrada) no processamento da unidade
                p.log.warn(f"{unit['unitId']}: pré-processamento para o índice falhou: "
                           f"{self.masker(str(exc))}")
        records = [r for rec in processor._cache.values() if rec.get("status") == st.SUCCESS
                   for r in run_index.records_of(rec)]
        cached = set(processor._cache)
        carried = [e for e in p.run_state.data.get("components", [])
                   if e.get("role") == "primary" and (e.get("metadataType"), e.get("component")) not in cached]
        records.extend(run_index.records_from_entries(carried, self.root))
        p.run_index = run_index.build_run_index(records, self.mvp.automation_index, p.class_inventory,
                                                 record_fields=self.mvp.record_index)

    def _metrics(self):
        """Chamadas e duração por tipo de comando e por metadata type (CLI)."""
        by_kind, by_type = {}, {}
        total = 0.0
        for h in self.runner.history:
            cmd = h.get("command", "")
            parts = cmd.split()
            kind = " ".join(p for p in parts[1:4] if not p.startswith("-"))
            mtype = None
            if "--metadata-type" in parts:
                mtype = parts[parts.index("--metadata-type") + 1]
            elif "--metadata" in parts:
                mtype = parts[parts.index("--metadata") + 1].split(":", 1)[0]
            elif kind.startswith("data query"):
                mtype = "SOQL"
            dur = float(h.get("durationSeconds") or 0)
            total += dur
            failed = h.get("returncode") != 0
            for bucket, key in ((by_kind, kind), (by_type, mtype)):
                if key is None:
                    continue
                m = bucket.setdefault(key, {"calls": 0, "seconds": 0.0, "failures": 0})
                m["calls"] += 1
                m["seconds"] = round(m["seconds"] + dur, 3)
                m["failures"] += 1 if failed else 0
        return {"commands": len(self.runner.history), "totalSeconds": round(total, 3),
                "timeoutSeconds": self.app.cli_timeout_seconds, "retries": 0,
                "byCommand": by_kind, "byMetadataType": by_type}

    def _report_not_found(self, p, group, units, inventories, component_filter):
        """Componentes pedidos em selection.metadataTypes que não viraram unidade de documento."""
        if self.app.selection.mode != "SELECTED" or component_filter is None:
            return
        requested = next((set(i["components"]) for i in self.app.selection.selection
                          if i["metadataType"] == group.primary_type), set())
        requested -= {WILDCARD}
        listed = {i["fullName"] for i in inventories.get(group.primary_type) or []}
        built = {u["fullName"] for u in units}
        for name in sorted((requested & component_filter) - built):
            reason = ("existe no inventário, mas foi excluído por componentFilter do grupo"
                      if name in listed else "não encontrado no inventário da org")
            p.run_state.data["selection"]["notFound"].append(
                {"group": group.name, "metadataType": group.primary_type, "component": name,
                 "reason": reason})
            p.run_state.type_status(group.primary_type, st.NOT_FOUND, group=group.name,
                                    stage="selection", component=name, detail=reason)
            p.log.warn(f"{group.primary_type}:{name} pedido em selection.metadataTypes: NOT_FOUND ({reason})")

    def _record_processed(self, p, processor):
        types = set()
        for rec in processor._cache.values():
            if rec.get("status") == st.SUCCESS:
                types.add(rec["metadataType"])
                types.update(c["metadataType"] for c in rec.get("children") or [])
        p.processed_types |= types

    def _process_unit(self, p, group, unit, types, inventories, processor):
        log = p.log
        log.info(f"{unit['unitId']}: processando")
        primary = processor.process(unit["metadataType"], unit["fullName"], unit["inventoryItem"],
                                    folder_type=unit["documentType"])
        base = {"unitId": unit["unitId"], "group": group.name, "role": "primary",
                "metadataType": unit["documentType"], "component": unit["fullName"]}
        if primary["status"] != st.SUCCESS:
            return dict(base, **_entry_fields(primary), status=primary["status"])
        unresolved = []
        related, failures = deviation_handler.resolve_related(
            unit, primary, group, processor, inventories, set(types), log,
            restrict_candidates=self.app.selection.mode == "SELECTED", unresolved=unresolved)
        for u in unresolved:
            p.run_state.data["selection"]["relatedNotResolved"].append(dict(u, unitId=unit["unitId"]))
            log.warn(f"{unit['unitId']}: relacionados {u['metadataType']} não verificados "
                     f"({u['candidates']} candidato(s) fora da seleção não recuperados)")
        for rec in related + [dict(f) for f in failures]:
            p.run_state.upsert_component({
                "unitId": unit["unitId"], "group": group.name, "role": "related",
                "metadataType": rec["metadataType"], "component": rec["fullName"],
                "status": rec.get("status"), "xml": rec.get("xml"), "normalized": rec.get("normalized"),
                "retrieveRaw": rec.get("retrieveRaw"), "files": rec.get("files", []),
                "error": rec.get("error"),
            })
        contract = p.contracts.get_file(group.contract_file)
        internal = self._internal_data(p, unit, primary, contract)
        result = self.render_unit(p, group, unit, primary, related, internal, contract,
                                  unresolved_types={u["metadataType"] for u in unresolved})
        warnings = list(primary.get("warnings", [])) + result.pop("warnings", [])
        if unresolved:
            warnings.append("Relacionados não verificados na seleção: " + ", ".join(
                f"{u['metadataType']} ({u['candidates']} candidato(s))" for u in unresolved))
        if failures:
            warnings.append("Relacionados candidatos com falha: " + ", ".join(
                f"{f['metadataType']}:{f['fullName']} ({f['status']})" for f in failures))
        if internal.get("status") == st.INTERNAL_DATA_UNAVAILABLE:
            warnings.append(f"INTERNAL_DATA_UNAVAILABLE: {internal.get('error')}")
        entry = dict(base, **_entry_fields(primary))
        entry.update(result)
        entry.update(internalData=rel(internal["raw"], self.root) if internal.get("raw") else None,
                     internalDataStatus=internal.get("status"),
                     relatedComponents=[{"metadataType": r["metadataType"], "fullName": r["fullName"]}
                                        for r in related],
                     relatedNotResolved=unresolved,
                     warnings=[self.masker(w) for w in warnings])
        log.info(f"{unit['unitId']}: {entry['status']}"
                 + (f" -> {entry.get('document')}" if entry.get("document") else ""))
        return entry

    def _internal_data(self, p, unit, primary, contract):
        cfg = (contract or {}).get("internalData") or {}
        if not cfg.get("enabled"):
            return {"status": None, "records": None, "raw": None}
        if p.source is not None:  # modo pasta: sem consulta à org (aviso único em _open_source)
            return {"status": st.INTERNAL_DATA_UNAVAILABLE, "records": None, "raw": None, "query": None,
                    "error": "modo pasta: dados internos exigem consulta à org (não feita)",
                    "namespaceWarning": None}
        type_dir = p.inventory_dir / self.mvp.folder(unit["metadataType"])
        slug = slugify(unit["fullName"])
        res = extract_internal_data(
            p.tooling, cfg, unit["fullName"],
            raw_path=type_dir / "internal-data" / f"{slug}.raw.json",
            errors_raw_path=p.errors_dir / f"internal-{self.mvp.folder(unit['metadataType'])}-{slug}.raw.json",
            namespace_prefix=primary.get("namespacePrefix"))
        if res["status"] == st.INTERNAL_DATA_UNAVAILABLE:
            p.log.warn(f"{unit['unitId']}: INTERNAL_DATA_UNAVAILABLE ({res.get('error')})")
        res["namespaceWarning"] = namespace_warning(cfg, primary.get("namespacePrefix"), res.get("records"))
        if res["namespaceWarning"]:
            p.log.warn(f"{unit['unitId']}: {res['namespaceWarning']}")
        return res

    # Passo 10 -----------------------------------------------------------
    def render_unit(self, p, group, unit, primary, related, internal, contract, unresolved_types=()):
        # Grupos com o mesmo tipo principal (ex.: CustomObject __c e platform event __e) usam slug próprio.
        doc_slug = group.data.get("documentSlug") or self.mvp.document_slug(unit["documentType"])
        if contract is None:
            msg = self._missing_message(p, unit["documentType"], unit["fullName"],
                                        group.contract_file, None, group.data.get("referenceDoc"))
            p.log.warn(msg)
            return {"status": st.NO_TEMPLATE, "document": None, "warnings": [msg]}
        template = p.templates.load(contract.get("template"))
        if template is None:
            msg = self._missing_message(p, unit["documentType"], unit["fullName"], group.contract_file,
                                        contract.get("template"), contract.get("referenceDoc"))
            p.log.warn(msg)
            return {"status": st.NO_TEMPLATE, "document": None, "warnings": [msg]}
        ctx = RenderContext(unit["metadataType"], unit["fullName"], primary.get("data"),
                            schema_fields=primary.get("schemaFields"), internal=internal,
                            related=related, files=primary.get("files"), contracts=p.contracts,
                            sensitive=self.mvp.render_blocked_elements,
                            developer_name=developer_name(unit["fullName"], primary.get("namespacePrefix")))
        ctx.unresolved_related = set(unresolved_types)
        ctx.access_index = p.access_index
        ctx.run_index = p.run_index
        result = self.renderer.render(template, contract, ctx)
        if not result.ok:
            p.log.error(f"{unit['unitId']}: documento inválido: {result.errors}")
            return {"status": st.FAILED, "document": None, "warnings": result.warnings,
                    "error": "; ".join(result.errors)}
        leak = self._sensitive_leak(result.text)
        if leak:
            p.log.error(f"{unit['unitId']}: {leak}")
            return {"status": st.FAILED, "document": None, "warnings": result.warnings, "error": leak}
        ns_note = (internal or {}).get("namespaceWarning")
        doc_path = p.writer.write(f"doc-{slugify(unit['fullName'])}-{doc_slug}.md",
                                  with_source_note(with_internal_note(result.text, ns_note), p.source_note),
                                  f"{unit['documentType']}:{unit['fullName']}")
        subdocs = self._render_subdocuments(p, group, unit, primary, ctx)
        warnings = list(result.warnings) + [w for s in subdocs for w in s.pop("warnings", [])]
        if ns_note:
            warnings.append(ns_note)
        return {"status": st.SUCCESS, "document": rel(doc_path, self.root),
                "template": p.templates.resolve_name(contract["template"]),
                "contract": group.contract_file,
                "subDocuments": subdocs, "warnings": warnings,
                "omittedProperties": sorted(ctx.omitted)}

    def _sensitive_leak(self, text):
        """Barreira final: o Markdown não pode conter token nem valor de elemento sensível
        visto no XML (mesmo que chegue por outro campo, ex.: description)."""
        if self.masker(text) != text:
            return ("conteúdo sensível conhecido detectado no documento (token ou valor de elemento "
                    "sensível); documento NÃO gravado")
        return None

    def _missing_message(self, p, metadata_type, component, contract_file, template, reference):
        """Aviso de NO_TEMPLATE: tipo, componente, referência ajudAI, contrato e modelo esperados."""
        contract_path = rel(self.app.contracts_dir / contract_file, self.root) if contract_file else "(nenhum)"
        if template:
            model = rel(p.templates.path(template), self.root)
            what = f"modelo ausente: {model}"
        else:
            what = f"contrato ausente: {contract_path}"
        return (f"NO_TEMPLATE {metadata_type}:{component} — {what}; contrato {contract_path}; "
                f"referência {reference or 'não declarada'}. Dados extraídos preservados; "
                "documento não gerado.")

    def _render_subdocuments(self, p, group, unit, primary, ctx):
        out = []
        for sub, item, item_name in deviation_handler.sub_document_targets(
                group, primary.get("data"), unit["fullName"]):
            contract = p.contracts.get_file(sub.get("contract"))
            template = p.templates.load((contract or {}).get("template"))
            suffix = sub.get("documentSuffix") or slugify(sub.get("contract", "sub"))
            name = unit["fullName"] if item_name is None else f"{unit['fullName']}.{item_name}"
            if contract is None or template is None:
                msg = self._missing_message(p, unit["documentType"], name, sub.get("contract"),
                                            (contract or {}).get("template"),
                                            (contract or {}).get("referenceDoc") or sub.get("referenceDoc"))
                p.log.warn(msg)
                out.append({"component": name, "status": st.NO_TEMPLATE, "document": None,
                            "warnings": [msg]})
                continue
            sctx = ctx if item is None else ctx.child(item, full_name=item_name)
            res = self.renderer.render(template, contract, sctx)
            if not res.ok:
                out.append({"component": name, "status": st.FAILED, "error": "; ".join(res.errors)})
                continue
            leak = self._sensitive_leak(res.text)
            if leak:
                p.log.error(f"{unit['unitId']} ({name}): {leak}")
                out.append({"component": name, "status": st.FAILED, "error": leak})
                continue
            path = p.writer.write(f"doc-{slugify(name)}-{suffix}.md",
                                  with_source_note(with_internal_note(res.text, ctx.internal.get("namespaceWarning")),
                                                   p.source_note),
                                  f"{unit['documentType']}:{name}:{suffix}")
            out.append({"component": name, "status": st.SUCCESS, "document": rel(path, self.root),
                        "template": p.templates.resolve_name(contract["template"])})
        return out

    def _regenerate_class_inventory(self, p):
        """Inventário de ApexClass da execução de origem (raw), se foi listado."""
        type_dir = p.inventory_dir / self.mvp.folder("ApexClass")
        if not (type_dir / "inventory.raw.json").is_file():
            return None
        index = inventory_extractor.regenerate_inventory_index("ApexClass", type_dir)
        return [c["fullName"] for c in index["components"]]

    # ==================================================================
    def regenerate(self, run_id="latest"):
        """Regera derivados e documentos SOMENTE a partir dos raws/XMLs (sem org)."""
        path = RunState.find(self.app.runs_dir, run_id, purpose="regenerate")
        if path is None:
            raise ConfigError(f"Execução não encontrada: {run_id}")
        source = RunState.load(path)
        session = OrgSession(source.data["orgAlias"], None, "", None,
                             source.data.get("apiVersion") or self.app.default_api_version)
        state = RunState.create(self.app.runs_dir, session.alias, resumed_from=source.run_id)
        state.data["mode"] = "REGENERATE"
        state.masker = self.masker
        set_private_files(self.app.private_files)
        log = RunLogger(self.masker, stream=self.stream, run_state=state)
        p = PipelineContext(self.root, self.app, self.mvp, self.runner, state, log, self.masker)
        p.bind_session(session)
        self._open_writer(p, session.alias, (source.data.get("session") or {}).get("orgId"), source)
        origin = source.data.get("source")
        self.mvp.source_mode = bool(origin)
        if origin:  # execução de origem no modo pasta: a origem continua no topo dos documentos
            p.source_note = source_note(origin)
            state.set("source", dict(origin, regeneratedFrom=source.run_id))
        self._load_access_index(p, source)
        state.set("apiVersion", session.api_version)
        self._regenerate_differences(p, source)
        if (p.catalog_dir / "metadata-types.raw.json").is_file():
            metadata_types_extractor.regenerate_index(p.catalog_dir)
        if p.schemas_dir.is_dir():
            schema_extractor.regenerate_schemas(p.schemas_dir, session.api_version)
        units = {}
        for c in source.data["components"]:
            units.setdefault(c.get("unitId"), []).append(c)
        prepared = []
        for unit_id, entries in units.items():
            primary_entry = next((e for e in entries if e.get("role") == "primary"), None)
            if not primary_entry or not primary_entry.get("xml"):
                continue
            group = self.mvp.group(primary_entry["group"])
            problem = self._xml_source_problem(primary_entry)
            if group is None or problem:
                reason = problem or f"grupo {primary_entry.get('group')} não configurado"
                state.upsert_component(dict(primary_entry, status=st.FAILED, document=None,
                                            error=f"regeneração recusada: {reason}",
                                            errorClass="SOURCE_UNAVAILABLE",
                                            regeneratedFrom=source.run_id))
                log.error(f"{unit_id}: regeneração recusada — {reason}")
                continue
            inv_dir = p.inventory_dir / self.mvp.folder(group.primary_type)
            if (inv_dir / "inventory.raw.json").is_file():
                inventory_extractor.regenerate_inventory_index(group.primary_type, inv_dir)
            primary = _record_from_entry(primary_entry, _record_type(group))
            primary["folderType"] = group.primary_type
            normalize_record(p, primary)
            related = []
            children = {c["xml"]: c for c in primary.get("children", [])}
            for e in entries:
                if e.get("role") != "related" or e.get("status") != st.SUCCESS or not e.get("xml"):
                    continue
                if e["xml"] in children:
                    related.append(dict(children[e["xml"]], status=st.SUCCESS))
                    continue
                rec = _record_from_entry(e, e["metadataType"])
                rec["role"] = "related"
                normalize_record(p, rec)
                related.append(deviation_handler._related_from_record(rec))
            prepared.append((unit_id, group, primary_entry, primary, related))
        # Índice da execução só depois de normalizar tudo: um documento pode mostrar outros
        # componentes (ex.: automações no mesmo objeto da trigger).
        if any(g.data.get("usesRunIndex") for _, g, _, _, _ in prepared):
            p.class_inventory = self._regenerate_class_inventory(p)
            records = [r for _, _, _, prim, _ in prepared for r in run_index.records_of(prim)]
            p.run_index = run_index.build_run_index(records, self.mvp.automation_index, p.class_inventory,
                                                 record_fields=self.mvp.record_index)
        for unit_id, group, primary_entry, primary, related in prepared:
            internal = {"status": None, "records": None, "raw": None}
            if primary_entry.get("internalData") and (self.root / primary_entry["internalData"]).is_file():
                raw = read_json(self.root / primary_entry["internalData"])
                internal = {"status": st.SUCCESS, "raw": self.root / primary_entry["internalData"],
                            "records": ((raw or {}).get("result") or {}).get("records")}
            unit = {"unitId": unit_id, "metadataType": _record_type(group),
                    "documentType": group.primary_type, "fullName": primary_entry["component"]}
            contract = p.contracts.get_file(group.contract_file)
            internal["namespaceWarning"] = namespace_warning(
                (contract or {}).get("internalData") or {}, primary_entry.get("namespacePrefix"),
                internal.get("records"))
            result = self.render_unit(
                p, group, unit, primary, related, internal, contract,
                unresolved_types={u["metadataType"] for u in primary_entry.get("relatedNotResolved") or []})
            entry = dict(primary_entry, **_entry_fields(primary))
            entry.update(result)
            entry["regeneratedFrom"] = source.run_id
            state.upsert_component(entry)
            log.info(f"{unit_id}: regenerado {entry['status']} {entry.get('document') or ''}")
        state.data["metrics"] = self._metrics()
        state.set("coverage", self._coverage(state, p))
        final = self._final_status(state)
        state.finish(final)
        try:
            write_summary(self, state, p)
        except OSError as exc:
            log.error(f"Resumo não gravado: {exc}")
        return (EXIT_OK if final in (st.SUCCESS, st.PARTIAL_SUCCESS, st.COMPLETED_WITH_GAPS)
                else EXIT_FAILURE), state


def _record_type(group):
    """Tipo do XML principal da unidade (CustomMetadata usa o tipo __mdt; componente fixo, o
    retrieveType, ex.: Settings)."""
    fixed = group.data.get("fixedComponents")
    if fixed:
        return fixed[0].get("retrieveType") or group.primary_type
    if group.unit_mode == "PER_TYPE_WITH_RECORDS":
        return group.type_definition["metadataType"]
    return group.primary_type


def _record_from_entry(entry, metadata_type):
    from salesforce_docs.pipeline.component_pipeline import ComponentRecord
    return ComponentRecord(metadataType=metadata_type, fullName=entry["component"],
                           role=entry.get("role", "primary"), status=st.SUCCESS, xml=entry["xml"],
                           files=entry.get("files", []), retrieveRaw=entry.get("retrieveRaw"),
                           children=[], warnings=[], error=None,
                           namespacePrefix=entry.get("namespacePrefix"))


def classify_error(text):
    """Classe do erro para o relatório (não altera o status oficial)."""
    if not text:
        return None
    t = str(text)
    if "INSUFFICIENT_ACCESS" in t or "insufficient access" in t.lower():
        return "PERMISSION_DENIED"
    if "Timeout" in t:
        return "TIMEOUT"
    if "INVALID_SESSION_ID" in t:
        return "SESSION_EXPIRED"
    if "cannot be found" in t or "not found" in t.lower():
        return "NOT_FOUND_IN_ORG"
    if "conteúdo sensível" in t:
        return "SENSITIVE_CONTENT_BLOCKED"
    return "ERROR"


def namespace_warning(internal_cfg, namespace_prefix, records):
    """DA-05: componente de pacote (com namespace) e consulta sem filtro de namespace.

    O filtro definitivo depende de confirmar, na org, o campo de namespace de cada objeto
    interno; até lá o documento avisa que pode haver homônimo de outro namespace.
    """
    query = str((internal_cfg or {}).get("query") or "")
    # Só `{developerName}` remove o prefixo do namespace; `{fullName}` (ex.: QualifiedApiName)
    # já identifica o componente com o namespace.
    if (not namespace_prefix or not records or "{developerName}" not in query
            or "namespaceprefix" in query.lower()):
        return None
    return (f"Componente do namespace '{namespace_prefix}': a consulta de dados internos não filtra "
            "namespace e pode incluir componente homônimo de outro namespace (DA-05, pendente de piloto).")


def source_note(info):
    """Origem do documento no modo pasta: pasta do repositório e org do de-para (sourceRepositories)."""
    return (f"> **Origem:** repositório `{info['folder']}` (org: **{info['orgName']}**). XML lido da pasta "
            "do repositório clonado, sem acesso à org; dados internos não consultados.")


def with_source_note(text, note):
    """Insere a origem logo após o título (primeira linha `# ...`)."""
    if not note:
        return text
    lines = text.split("\n")
    i = next((n for n, line in enumerate(lines) if line.startswith("# ")), -1)
    return "\n".join(lines[:i + 1] + ["", note] + lines[i + 1:])


def with_internal_note(text, note):
    """Insere o aviso logo após a tabela da seção "Dados internos" (ou no fim do documento)."""
    if not note:
        return text
    lines = text.split("\n")
    block = ["", f"> **Atenção:** {note}"]
    try:
        start = lines.index("## Dados internos")
    except ValueError:
        return text.rstrip("\n") + "\n" + "\n".join(block) + "\n"
    i, seen_table = start + 1, False
    while i < len(lines):
        if lines[i].startswith("|"):
            seen_table = True
        elif seen_table or lines[i].startswith("## "):
            break
        i += 1
    return "\n".join(lines[:i] + block + lines[i:])


def _entry_fields(record):
    return {
        "xml": record.get("xml"),
        "normalized": record.get("normalized"),
        "retrieveRaw": record.get("retrieveRaw"),
        "files": record.get("files", []),
        "namespacePrefix": record.get("namespacePrefix"),
        "error": record.get("error"),
        "children": [{"metadataType": c["metadataType"], "fullName": c["fullName"],
                      "xml": c.get("xml"), "normalized": c.get("normalized")}
                     for c in record.get("children", [])],
    }


def _prompt_org_confirmation(identity):
    """Pergunta no terminal (stderr) e lê a confirmação do stdin."""
    print("\nORG NÃO APROVADA em config.json (approvedOrgs):", file=sys.stderr)
    for key in ("orgId", "alias", "username", "instanceUrl"):
        print(f"  {key}: {identity.get(key)}", file=sys.stderr)
    print("Para coletar metadata desta org NESTA execução, digite o orgId exato "
          "(Enter cancela): ", end="", file=sys.stderr, flush=True)
    try:
        return input()
    except EOFError:
        return ""
