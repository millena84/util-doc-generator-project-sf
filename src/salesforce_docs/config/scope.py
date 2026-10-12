"""Escopo da execução (config.json → `scope`).

Modos:
- ALL: todos os grupos configurados em metadata-types-mvp.json, com todos os
  componentes que a org tiver (comportamento original).
- SELECTED: somente os metadata types e componentes listados em `scope.selection`.

Exemplo:
    "scope": {
      "mode": "SELECTED",
      "selection": [
        { "metadataType": "Flow", "components": ["Meu_Flow", "Outro_Flow"] },
        { "metadataType": "ConnectedApp", "components": ["*"] }
      ]
    }

Regras:
- `metadataType` deve ser o tipo principal de um grupo configurado. Tipos
  relacionados/filhos (FlowDefinition, CustomField, ExtlClntApp*...) não são
  selecionáveis: entram como dependência do principal selecionado.
- `components` é obrigatório e não vazio; "*" (sozinho) = todos os componentes do tipo.
  Para CustomMetadata o componente é o tipo (`Config__mdt`).
- Configuração inválida ou ambígua é rejeitada antes de qualquer chamada à org.
- `--group` / `--component` na linha de comando só restringem o escopo do
  config.json; pedir algo fora dele é erro.
"""

from __future__ import annotations

from salesforce_docs.errors import ConfigError

MODES = ("ALL", "SELECTED")
WILDCARD = "*"


class ScopeConfig:
    def __init__(self, data):
        data = data if data is not None else {"mode": "ALL"}
        if not isinstance(data, dict):
            raise ConfigError("config.json: `scope` deve ser um objeto")
        self.mode = str(data.get("mode", "ALL")).upper()
        if self.mode not in MODES:
            raise ConfigError(f"config.json: scope.mode inválido {data.get('mode')!r}; use ALL ou SELECTED")
        selection = data.get("selection")
        if self.mode == "ALL":
            if selection:
                raise ConfigError("config.json: scope.selection só é permitido com scope.mode = SELECTED "
                                  "(configuração ambígua)")
            self.selection = []
            return
        if not isinstance(selection, list) or not selection:
            raise ConfigError("config.json: scope.mode = SELECTED exige scope.selection com ao menos um item")
        seen = set()
        self.selection = []
        for i, item in enumerate(selection):
            where = f"config.json: scope.selection[{i}]"
            if not isinstance(item, dict) or not isinstance(item.get("metadataType"), str) \
                    or not item["metadataType"].strip():
                raise ConfigError(f"{where}: `metadataType` (texto) é obrigatório")
            mtype = item["metadataType"].strip()
            if mtype in seen:
                raise ConfigError(f"{where}: metadataType {mtype} repetido; agrupe os componentes em um item")
            seen.add(mtype)
            comps = item.get("components")
            if not isinstance(comps, list) or not comps:
                raise ConfigError(f"{where} ({mtype}): `components` deve ser lista não vazia "
                                  f"(use [\"{WILDCARD}\"] para todos)")
            if any(not isinstance(c, str) or not c.strip() for c in comps):
                raise ConfigError(f"{where} ({mtype}): nomes de componente devem ser textos não vazios")
            names = [c.strip() for c in comps]
            if WILDCARD in names and len(names) > 1:
                raise ConfigError(f"{where} ({mtype}): \"{WILDCARD}\" não pode ser combinado com nomes")
            if len(set(names)) != len(names):
                raise ConfigError(f"{where} ({mtype}): componentes repetidos")
            self.selection.append({"metadataType": mtype, "components": names})

    def describe(self):
        return {"mode": self.mode, "selection": self.selection}


def _group_for_type(mvp, metadata_type):
    for g in mvp.groups:
        if g.primary_type == metadata_type:
            return g
    return None


def _owner_of_related(mvp, metadata_type):
    owners = [g for g in mvp.groups if metadata_type in g.related_types
              or (g.type_definition or {}).get("metadataType") == metadata_type]
    return owners


def resolve_scope(scope, mvp, cli_groups=None, cli_components=None):
    """Escopo efetivo: {grupo: None (todos) | set(componentes)}.

    Lança ConfigError para tipos desconhecidos, tipos relacionados e filtros de CLI
    fora do escopo do config.json.
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
                owners = _owner_of_related(mvp, mtype)
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
            raise ConfigError(f"--group {', '.join(outside)} fora do escopo do config.json "
                              f"(scope.mode = {scope.mode})")
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
                raise ConfigError(f"--component {', '.join(outside)} fora do escopo do config.json")
        narrowed = {}
        for g, comps in effective.items():
            narrowed[g] = set(wanted) if comps is None else (comps & wanted)
        effective = {g: c for g, c in narrowed.items() if c}
        if not effective:
            raise ConfigError("--component não corresponde a nenhum componente do escopo")
    return effective


def describe_effective(effective):
    return {g: (sorted(c) if c is not None else [WILDCARD]) for g, c in sorted(effective.items())}
