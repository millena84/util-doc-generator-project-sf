"""Orquestra os passos 1–10 na ordem obrigatória e a regeneração offline."""

from __future__ import annotations

from pathlib import Path

from salesforce_docs import status as st
from salesforce_docs.config.config_loader import load_config
from salesforce_docs.config.metadata_types_loader import load_metadata_types
from salesforce_docs.errors import ConfigError, GlobalFailure, SessionExpiredError
from salesforce_docs.extraction import inventory_extractor, metadata_types_extractor, schema_extractor
from salesforce_docs.extraction.internal_data_extractor import developer_name, extract_internal_data
from salesforce_docs.pipeline import deviation_handler
from salesforce_docs.pipeline.component_pipeline import ComponentProcessor, normalize_record
from salesforce_docs.rendering.context import RenderContext
from salesforce_docs.rendering.markdown_renderer import MarkdownRenderer
from salesforce_docs.rendering.template_loader import ContractStore, TemplateLoader
from salesforce_docs.runs.run_logger import RunLogger
from salesforce_docs.runs.run_state import RunState
from salesforce_docs.salesforce.cli_runner import CliRunner
from salesforce_docs.salesforce.metadata_api_client import MetadataApiClient
from salesforce_docs.salesforce.org_session import OrgSession
from salesforce_docs.salesforce.tooling_api_client import ToolingApiClient
from salesforce_docs.utils import Masker, now_local, read_json, rel, slugify, write_text, write_text_raw
from salesforce_docs.validation import cli_validator, org_session_validator
from salesforce_docs.validation.metadata_type_validator import check_enabled
from salesforce_docs.validation.project_validator import validate_project

EXIT_OK, EXIT_FAILURE, EXIT_SESSION = 0, 1, 2


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
        self.contracts = ContractStore(app.contracts_dir, mvp)
        self.templates = None
        self.tooling = None

    def bind_session(self, session):
        self.session = session
        self.catalog_dir = self.app.catalog_dir(session.alias, session.api_version)
        self.schemas_dir = self.catalog_dir / "schemas"
        self.inventory_dir = self.app.inventory_dir(session.alias, session.api_version)
        self.templates = TemplateLoader(self.app.models_dir(session.api_version), session.api_version)
        self.tooling = ToolingApiClient(self.runner, session)


class DocumentPipeline:
    def __init__(self, root, runner=None, metadata_client_factory=None, stream=None,
                 config_path=None, metadata_types_path=None):
        self.root = Path(root).resolve()
        self.masker = Masker()
        self.app = load_config(self.root, config_path)
        self.mvp = load_metadata_types(self.root, metadata_types_path)
        self.runner = runner or CliRunner(timeout=self.app.cli_timeout_seconds,
                                          save_raw=self.app.save_raw_responses, masker=self.masker)
        self.runner.masker = self.masker
        self.metadata_client_factory = metadata_client_factory or (
            lambda s: MetadataApiClient(s.instance_url, lambda: s.access_token, s.api_version,
                                        timeout=self.app.http_timeout_seconds))
        self.stream = stream
        self.renderer = MarkdownRenderer()

    # ==================================================================
    def run(self, org_alias=None, api_version=None, groups=None, components=None, resume=None):
        alias = org_alias or self.app.org_alias
        previous = None
        if resume:
            prev_path = RunState.find(self.app.runs_dir, resume)
            if prev_path is None:
                raise ConfigError(f"Execução para retomar não encontrada: {resume}")
            previous = RunState.load(prev_path)
        state = RunState.create(self.app.runs_dir, alias, resumed_from=previous.run_id if previous else None)
        log = RunLogger(self.masker, stream=self.stream, run_state=state)
        p = PipelineContext(self.root, self.app, self.mvp, self.runner, state, log, self.masker)
        p.errors_dir = self.app.runs_dir / state.run_id / "errors"
        skip_units = state.carry_successes_from(previous) if previous else set()
        if skip_units:
            log.info(f"Retomando {previous.run_id}: {len(skip_units)} unidade(s) SUCCESS não serão reprocessadas")
        current_unit = {"entry": None}
        try:
            warnings = validate_project(self.app, self.mvp, p.contracts)
            for w in warnings:
                log.warn(w)
            self._step1_cli(p)
            self._step2_org_list(p, alias)
            self._step3_org_display(p, alias, api_version)
            enabled = self._step4_metadata_types(p, groups)
            self._step5_schemas(p, enabled)
            inventories = self._step6_inventories(p, enabled)
            self._steps7_to_10(p, enabled, inventories, skip_units, components, current_unit)
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
            state.finish(st.FAILED, {"code": "CONFIG_ERROR", "message": str(exc)})
            log.error(f"Configuração inválida: {exc}")
            return EXIT_FAILURE, state
        finally:
            # O token só vive durante a execução, inclusive em caso de exceção não tratada.
            if p.session is not None:
                p.session.clear()
        final = self._final_status(state)
        state.data["commands"] = self.runner.history
        state.finish(final)
        log.info(f"Execução {state.run_id} finalizada: {final} {state.summary()}")
        log.info(f"Log: {rel(state.path, self.root)}")
        return (EXIT_OK if final in (st.SUCCESS, st.PARTIAL_SUCCESS) else EXIT_FAILURE), state

    def _final_status(self, state):
        statuses = [c.get("status") for c in state.data["components"] if c.get("role") == "primary"]
        bad = [s for s in statuses if s not in (st.SUCCESS, st.NO_TEMPLATE)]
        if not bad:
            return st.SUCCESS
        if self.app.allow_partial_success and len(bad) < len(statuses):
            return st.PARTIAL_SUCCESS
        return st.FAILED

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
            if self.app.save_raw_responses and result.stdout.strip():
                write_text_raw(p.errors_dir / "org-display.raw.json", result.stdout, private=True)
            org_session_validator.validate_display(result, alias)
            raise GlobalFailure("ORG_DISPLAY_INCOMPLETE", "`sf org display` sem apiVersion",
                                org_session_validator.login_suggestion(alias))
        session = OrgSession.from_display_result(alias, display, api_version_override)
        p.bind_session(session)
        raw_path = p.catalog_dir / "org-display.raw.json"
        if self.app.save_raw_responses:
            # bruto, inalterado; contém token: .gitignore + permissão restrita ao dono (0600)
            write_text_raw(raw_path, result.stdout, private=True)
        org_session_validator.validate_display(result, alias)
        p.run_state.data["apiVersion"] = session.api_version
        p.run_state.set("session", session.describe())
        p.run_state.step("3-org-display", st.SUCCESS, rel(raw_path, self.root))
        p.log.info(f"Passo 3: {session.username} conectado; API {session.api_version} "
                   f"(detectada {session.detected_api_version}, fonte: {session.api_version_source})")

    # Passo 4 ------------------------------------------------------------
    def _step4_metadata_types(self, p, group_filter):
        index, raw_path, _ = metadata_types_extractor.extract_metadata_types(
            p.runner, p.session, p.catalog_dir, p.errors_dir)
        p.run_state.step("4-metadata-types", st.SUCCESS, rel(raw_path, self.root))
        enabled = {}
        for group in self.mvp.groups:
            if group_filter and group.name not in group_filter:
                # Configurado, mas fora do escopo desta execução (≠ NOT_ENABLED / NO_TEMPLATE).
                p.run_state.type_status(group.primary_type, st.OUT_OF_SCOPE, group=group.name,
                                        stage="scope", detail="--group")
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
            listable = [t for t in group.all_types if t in types and not self.mvp.retrieved_with(t)]
            for t in listable:
                if t in inventories:
                    continue
                type_dir = p.inventory_dir / self.mvp.folder(t)
                res = inventory_extractor.extract_inventory(p.runner, p.session, t, type_dir, p.errors_dir)
                inventories[t] = res["components"]
                p.run_state.type_status(t, res["status"], group=None, stage="inventory",
                                        detail=res.get("error"), count=len(res["components"]),
                                        raw=rel(res["raw"], self.root) if res.get("raw") else None)
                if res["status"] == st.NO_COMPONENTS:
                    p.log.info(f"Passo 6: {t} -> NO_COMPONENTS")
                elif res["status"] != st.SUCCESS:
                    p.log.warn(f"Passo 6: {t} -> {res['status']}: {res.get('error')}")
                else:
                    p.log.info(f"Passo 6: {t} -> {len(res['components'])} componente(s)")
        p.run_state.step("6-list-metadata", st.SUCCESS, f"{len(inventories)} tipo(s)")
        return inventories

    # Passos 7–10 --------------------------------------------------------
    def _steps7_to_10(self, p, enabled, inventories, skip_units, component_filter, current_unit):
        p.docs_dir = self.app.output_docs_dir / f"doc-org-{now_local().strftime('%m%d%y')}"
        processor = ComponentProcessor(p)
        for group_name, types in enabled.items():
            group = self.mvp.group(group_name)
            units = deviation_handler.build_units(group, inventories, self.mvp)
            if not units:
                p.run_state.type_status(group.primary_type, st.NO_COMPONENTS, group=group.name, stage="units")
                continue
            for unit in units:
                if component_filter and unit["fullName"] not in component_filter:
                    continue
                if unit["unitId"] in skip_units:
                    p.log.info(f"{unit['unitId']}: SUCCESS em execução anterior, ignorado")
                    continue
                entry = {"unitId": unit["unitId"], "group": group.name, "role": "primary",
                         "metadataType": unit["documentType"], "component": unit["fullName"],
                         "status": st.IN_PROGRESS}
                current_unit["entry"] = entry
                p.run_state.upsert_component(entry)
                try:
                    entry = self._process_unit(p, group, unit, types, inventories, processor)
                except SessionExpiredError:
                    raise
                except Exception as exc:  # falha por componente não derruba a execução
                    entry = dict(entry, status=st.FAILED, error=self.masker(f"{type(exc).__name__}: {exc}"))
                    p.log.error(f"{unit['unitId']}: FAILED {exc}")
                p.run_state.upsert_component(entry)
                current_unit["entry"] = None

    def _process_unit(self, p, group, unit, types, inventories, processor):
        log = p.log
        log.info(f"{unit['unitId']}: processando")
        primary = processor.process(unit["metadataType"], unit["fullName"], unit["inventoryItem"],
                                    folder_type=unit["documentType"])
        base = {"unitId": unit["unitId"], "group": group.name, "role": "primary",
                "metadataType": unit["documentType"], "component": unit["fullName"]}
        if primary["status"] != st.SUCCESS:
            return dict(base, **_entry_fields(primary), status=primary["status"])
        related, failures = deviation_handler.resolve_related(
            unit, primary, group, processor, inventories, set(types), log)
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
        result = self.render_unit(p, group, unit, primary, related, internal, contract)
        warnings = list(primary.get("warnings", [])) + result.pop("warnings", [])
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
                     warnings=[self.masker(w) for w in warnings])
        log.info(f"{unit['unitId']}: {entry['status']}"
                 + (f" -> {entry.get('document')}" if entry.get("document") else ""))
        return entry

    def _internal_data(self, p, unit, primary, contract):
        cfg = (contract or {}).get("internalData") or {}
        if not cfg.get("enabled"):
            return {"status": None, "records": None, "raw": None}
        type_dir = p.inventory_dir / self.mvp.folder(unit["metadataType"])
        slug = slugify(unit["fullName"])
        res = extract_internal_data(
            p.tooling, cfg, unit["fullName"],
            raw_path=type_dir / "internal-data" / f"{slug}.raw.json",
            errors_raw_path=p.errors_dir / f"internal-{self.mvp.folder(unit['metadataType'])}-{slug}.raw.json",
            namespace_prefix=primary.get("namespacePrefix"))
        if res["status"] == st.INTERNAL_DATA_UNAVAILABLE:
            p.log.warn(f"{unit['unitId']}: INTERNAL_DATA_UNAVAILABLE ({res.get('error')})")
        return res

    # Passo 10 -----------------------------------------------------------
    def render_unit(self, p, group, unit, primary, related, internal, contract):
        doc_slug = self.mvp.document_slug(unit["documentType"])
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
        result = self.renderer.render(template, contract, ctx)
        if not result.ok:
            p.log.error(f"{unit['unitId']}: documento inválido: {result.errors}")
            return {"status": st.FAILED, "document": None, "warnings": result.warnings,
                    "error": "; ".join(result.errors)}
        doc_path = p.docs_dir / f"doc-{slugify(unit['fullName'])}-{doc_slug}.md"
        write_text(doc_path, result.text)
        subdocs = self._render_subdocuments(p, group, unit, primary, ctx)
        warnings = list(result.warnings) + [w for s in subdocs for w in s.pop("warnings", [])]
        return {"status": st.SUCCESS, "document": rel(doc_path, self.root),
                "template": p.templates.resolve_name(contract["template"]),
                "subDocuments": subdocs, "warnings": warnings,
                "omittedProperties": sorted(ctx.omitted)}

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
            path = p.docs_dir / f"doc-{slugify(name)}-{suffix}.md"
            write_text(path, res.text)
            out.append({"component": name, "status": st.SUCCESS, "document": rel(path, self.root),
                        "template": p.templates.resolve_name(contract["template"])})
        return out

    # ==================================================================
    def regenerate(self, run_id="latest"):
        """Regera derivados e documentos SOMENTE a partir dos raws/XMLs (sem org)."""
        path = RunState.find(self.app.runs_dir, run_id)
        if path is None:
            raise ConfigError(f"Execução não encontrada: {run_id}")
        source = RunState.load(path)
        session = OrgSession(source.data["orgAlias"], None, "", None,
                             source.data.get("apiVersion") or self.app.default_api_version)
        state = RunState.create(self.app.runs_dir, session.alias, resumed_from=source.run_id)
        state.data["mode"] = "REGENERATE"
        log = RunLogger(self.masker, stream=self.stream, run_state=state)
        p = PipelineContext(self.root, self.app, self.mvp, self.runner, state, log, self.masker)
        p.bind_session(session)
        p.docs_dir = self.app.output_docs_dir / f"doc-org-{now_local().strftime('%m%d%y')}"
        state.set("apiVersion", session.api_version)
        if (p.catalog_dir / "metadata-types.raw.json").is_file():
            metadata_types_extractor.regenerate_index(p.catalog_dir)
        if p.schemas_dir.is_dir():
            schema_extractor.regenerate_schemas(p.schemas_dir, session.api_version)
        units = {}
        for c in source.data["components"]:
            units.setdefault(c.get("unitId"), []).append(c)
        for unit_id, entries in units.items():
            primary_entry = next((e for e in entries if e.get("role") == "primary"), None)
            if not primary_entry or not primary_entry.get("xml"):
                continue
            group = self.mvp.group(primary_entry["group"])
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
            internal = {"status": None, "records": None, "raw": None}
            if primary_entry.get("internalData") and (self.root / primary_entry["internalData"]).is_file():
                raw = read_json(self.root / primary_entry["internalData"])
                internal = {"status": st.SUCCESS, "raw": self.root / primary_entry["internalData"],
                            "records": ((raw or {}).get("result") or {}).get("records")}
            unit = {"unitId": unit_id, "metadataType": _record_type(group),
                    "documentType": group.primary_type, "fullName": primary_entry["component"]}
            contract = p.contracts.get_file(group.contract_file)
            result = self.render_unit(p, group, unit, primary, related, internal, contract)
            entry = dict(primary_entry, **_entry_fields(primary))
            entry.update(result)
            entry["regeneratedFrom"] = source.run_id
            state.upsert_component(entry)
            log.info(f"{unit_id}: regenerado {entry['status']} {entry.get('document') or ''}")
        final = self._final_status(state)
        state.finish(final)
        return (EXIT_OK if final in (st.SUCCESS, st.PARTIAL_SUCCESS) else EXIT_FAILURE), state


def _record_type(group):
    """Tipo do XML principal da unidade (CustomMetadata usa o tipo __mdt)."""
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
