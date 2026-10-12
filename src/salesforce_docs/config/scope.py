"""Seleção do escopo da execução (config.json → `selection`).

Modos:
- ALL (padrão): todos os grupos documentáveis configurados em metadata-types-mvp.json,
  com todos os componentes encontrados na org (comportamento original).
- SELECTED: somente os metadata types (tipos PRINCIPAIS de grupo) listados em
  `metadataTypes`, cada um com `components` = "ALL" ou lista explícita de fullNames.

Exemplo:
    "selection": {
      "mode": "SELECTED",
      "metadataTypes": {
        "Flow":         { "components": "ALL" },
        "CustomObject": { "components": ["Pedido__c"] }
      }
    }

Regras (validadas antes de qualquer chamada à org):
- `selection` aceita só as chaves `mode` e `metadataTypes`; cada tipo aceita só `components`.
- `mode` é exatamente "ALL" ou "SELECTED". Em ALL, `metadataTypes` deve estar ausente ou vazio.
- Em SELECTED, `metadataTypes` é obrigatório e não vazio; tipo ausente não é processado.
- `components`: "ALL" ou lista não vazia de textos únicos. Lista vazia é rejeitada
  (nunca significa "todos"). Nomes com espaço no início/fim são rejeitados (não corrigidos).
- A chave é o tipo PRINCIPAL (ex.: `ExternalClientApplication`), não o nome do grupo
  (`ExternalClientApp`). Tipos relacionados/filhos (FlowDefinition, CustomField,
  RecordType, ValidationRule, WebLink, ExtlClntApp*...) são rejeitados com o principal
  a selecionar — eles entram como dependência do principal.
- Para Custom Metadata o componente é o tipo (`Config__mdt`).
- `--group` / `--component` só restringem a seleção; pedir algo fora dela é erro.
"""

from __future__ import annotations

from salesforce_docs.errors import ConfigError

MODES = ("ALL", "SELECTED")
ALL_COMPONENTS = "ALL"
WILDCARD = "*"  # representação interna de "todos os componentes"
_SELECTION_KEYS = {"mode", "metadataTypes"}
_TYPE_KEYS = {"components"}


def _check_name(value, where):
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{where}: deve ser texto não vazio")
    if value != value.strip():
        raise ConfigError(f"{where}: {value!r} tem espaço no início/fim (corrija o nome)")
    return value


class ScopeConfig:
    """Seleção validada. `selection` = [{"metadataType", "components": [...] | ["*"]}]."""

    def __init__(self, data, legacy_scope=None):
        if legacy_scope is not None:
            raise ConfigError(
                "config.json: a chave `scope` foi substituída por `selection`. Exemplo: "
                '"selection": {"mode": "SELECTED", "metadataTypes": {"Flow": {"components": "ALL"}}}')
        data = {"mode": "ALL"} if data is None else data
        if not isinstance(data, dict):
            raise ConfigError("config.json: `selection` deve ser um objeto")
        unknown = set(data) - _SELECTION_KEYS
        if unknown:
            raise ConfigError(f"config.json: selection tem chaves desconhecidas {sorted(unknown)} "
                              f"(aceitas: {sorted(_SELECTION_KEYS)})")
        mode = data.get("mode", "ALL")
        if mode not in MODES:
            raise ConfigError(f"config.json: selection.mode inválido {mode!r}; use \"ALL\" ou \"SELECTED\"")
        self.mode = mode
        types = data.get("metadataTypes")
        if types is not None and not isinstance(types, dict):
            raise ConfigError("config.json: selection.metadataTypes deve ser um objeto "
                              "{\"<TipoPrincipal>\": {\"components\": \"ALL\" | [..]}}")
        if mode == "ALL":
            if types:
                raise ConfigError("config.json: selection.metadataTypes só é permitido com "
                                  "mode = \"SELECTED\" (configuração ambígua)")
            self.selection = []
            return
        if not types:
            raise ConfigError("config.json: selection.mode = \"SELECTED\" exige selection.metadataTypes "
                              "com ao menos um tipo")
        self.selection = []
        for mtype, spec in types.items():
            where = f"config.json: selection.metadataTypes[{mtype!r}]"
            _check_name(mtype, f"{where} (nome do tipo)")
            if not isinstance(spec, dict):
                raise ConfigError(f"{where}: deve ser um objeto {{\"components\": \"ALL\" | [..]}}")
            extra = set(spec) - _TYPE_KEYS
            if extra:
                raise ConfigError(f"{where}: chaves desconhecidas {sorted(extra)} (aceita: components)")
            if "components" not in spec:
                raise ConfigError(f"{where}: `components` é obrigatório (\"ALL\" ou lista de fullNames)")
            comps = spec["components"]
            if comps == ALL_COMPONENTS:
                names = [WILDCARD]
            elif isinstance(comps, list):
                if not comps:
                    raise ConfigError(f"{where}: `components` vazio não é permitido "
                                      "(use \"ALL\" para todos ou liste os fullNames)")
                names = [_check_name(c, f"{where}.components") for c in comps]
                if WILDCARD in names or ALL_COMPONENTS in names:
                    raise ConfigError(f"{where}: use `\"components\": \"ALL\"` (não dentro da lista)")
                dup = sorted({n for n in names if names.count(n) > 1})
                if dup:
                    raise ConfigError(f"{where}: componentes repetidos {dup}")
            else:
                raise ConfigError(f"{where}: `components` deve ser \"ALL\" ou lista de textos "
                                  f"(recebido {type(comps).__name__})")
            self.selection.append({"metadataType": mtype, "components": names})

    def describe(self):
        """Seleção no formato do config.json (para o run state)."""
        return {"mode": self.mode,
                "metadataTypes": {i["metadataType"]: {"components": ALL_COMPONENTS if i["components"] == [WILDCARD]
                                                       else list(i["components"])}
                                  for i in self.selection}}


def _group_for_type(mvp, metadata_type):
    for g in mvp.groups:
        if g.primary_type == metadata_type:
            return g
    return None


def _owners_of_related(mvp, metadata_type):
    return [g for g in mvp.groups if metadata_type in g.related_types
            or (g.type_definition or {}).get("metadataType") == metadata_type]


def resolve_scope(scope, mvp, cli_groups=None, cli_components=None):
    """Escopo efetivo: {grupo: None (todos) | set(componentes)}.

    Lança ConfigError para tipos desconhecidos, nomes de grupo usados como tipo,
    tipos relacionados e filtros de CLI fora da seleção do config.json.
    """
    effective = {}
    if scope.mode == "ALL":
        for g in mvp.groups:
            effective[g.name] = None
    else:
        for item in scope.selection:
            mtype = item["metadataType"]
            group = _group_for_type(mvp, mtype)
            if group is None:
                by_name = mvp.group(mtype)
                if by_name is not None:
                    raise ConfigError(
                        f"config.json: {mtype!r} é nome de GRUPO; a seleção usa o tipo principal "
                        f"— use \"{by_name.primary_type}\".")
                owners = _owners_of_related(mvp, mtype)
                if owners:
                    principal = ", ".join(sorted({o.primary_type for o in owners}))
                    raise ConfigError(
                        f"config.json: {mtype} é tipo relacionado/filho e não pode ser selecionado "
                        f"sozinho; selecione o principal ({principal}) — ele traz os relacionados.")
                known = ", ".join(sorted(g.primary_type for g in mvp.groups))
                raise ConfigError(f"config.json: metadataType {mtype} não está configurado em "
                                  f"metadata-types-mvp.json (principais: {known})")
            comps = item["components"]
            effective[group.name] = None if comps == [WILDCARD] else set(comps)

    if cli_groups:
        unknown = [g for g in cli_groups if mvp.group(g) is None]
        if unknown:
            raise ConfigError(f"--group desconhecido: {', '.join(unknown)}")
        outside = [g for g in cli_groups if g not in effective]
        if outside:
            raise ConfigError(f"--group {', '.join(outside)} fora da seleção do config.json "
                              f"(selection.mode = {scope.mode})")
        effective = {g: c for g, c in effective.items() if g in cli_groups}

    if cli_components:
        wanted = set(cli_components)
        if scope.mode == "SELECTED":
            allowed = set()
            open_groups = [g for g, c in effective.items() if c is None]
            for c in effective.values():
                allowed |= c or set()
            outside = sorted(n for n in wanted if n not in allowed) if not open_groups else []
            if outside:
                raise ConfigError(f"--component {', '.join(outside)} fora da seleção do config.json")
        narrowed = {}
        for g, comps in effective.items():
            narrowed[g] = set(wanted) if comps is None else (comps & wanted)
        effective = {g: c for g, c in narrowed.items() if c}
        if not effective:
            raise ConfigError("--component não corresponde a nenhum componente da seleção")
    return effective


def describe_effective(effective):
    return {g: (sorted(c) if c is not None else [ALL_COMPONENTS]) for g, c in sorted(effective.items())}
