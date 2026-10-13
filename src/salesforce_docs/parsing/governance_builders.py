"""Builders de segurança e governança que usam o índice da execução (`run_index`).

- `index_record_rows`: uma linha por componente de um tipo processado na execução, com campos
  copiados do XML (`recordIndex` no config), ex.: OWD (`sharingModel`) de cada objeto;
- `role_hierarchy_rows`: papéis acima (cadeia de `parentRole`) e subordinados diretos;
- `page_usage_rows`: páginas Lightning (FlexiPage) que usam o componente (LWC, Flow).

Sem índice: "Não informado". Só entram componentes processados na execução.
"""

from __future__ import annotations

from salesforce_docs import status as st

DASH = "—"
BUILDER_PLACEHOLDERS = {
    "role_hierarchy_rows": ("hierarchy_relation", "hierarchy_role", "hierarchy_level"),
    "page_usage_rows": ("usage_page", "usage_page_type", "usage_region", "usage_identifier", "usage_visibility"),
    "event_reference_rows": ("event_role", "event_kind", "event_component", "event_detail", "event_subscriber_config"),
    "rule_target_rows": ("target_rule_type", "target_object", "target_rule", "target_order", "target_active"),
}


def _index(ctx):
    return getattr(ctx.root(), "run_index", None)


def index_record_rows(ctx, args):
    """args: metadataType, namePlaceholder, columns {placeholder: campo do recordIndex}, only=self."""
    index = _index(ctx)
    if index is None:
        return []
    records = (index.get("records") or {}).get(args["metadataType"]) or {}
    names = sorted(records, key=str.lower)
    if args.get("only") == "self":  # só o registro com o mesmo nome do componente (ex.: objeto da regra)
        names = [n for n in names if n.lower() == ctx.root().full_name.lower()]
    rows = []
    for name in names:
        row = {args.get("namePlaceholder", "record_name"): name}
        row.update({ph: records[name].get(f) for ph, f in (args.get("columns") or {}).items()})
        rows.append(row)
    return rows


def role_hierarchy_rows(ctx, args):
    """Cadeia de papéis acima (parentRole) e subordinados diretos, entre os papéis processados."""
    index = _index(ctx)
    if index is None:
        return []
    roles = (index.get("records") or {}).get(args.get("metadataType", "Role")) or {}
    field = args.get("parentField", "parentRole")
    me = ctx.root().full_name
    rows, seen, level = [], {me}, 0
    parent = (roles.get(me) or {}).get(field)
    while parent:
        level += 1
        known = parent in roles
        rows.append({"hierarchy_relation": "Acima" if known else "Acima (papel não processado nesta execução)",
                     "hierarchy_role": parent, "hierarchy_level": f"{level} acima"})
        if not known or parent in seen:
            break
        seen.add(parent)
        parent = roles[parent].get(field)
    if not rows and me in roles:
        rows.append({"hierarchy_relation": "Topo da hierarquia (sem parentRole)", "hierarchy_role": me,
                     "hierarchy_level": "0"})
    for name in sorted(n for n, r in roles.items() if r.get(field) == me):
        rows.append({"hierarchy_relation": "Subordinado direto", "hierarchy_role": name, "hierarchy_level": "1 abaixo"})
    return rows


def page_usage_rows(ctx, args):
    """Páginas Lightning (FlexiPage) processadas na execução que usam o componente.

    args: keyPrefix — "c:" (LWC/Aura do projeto: c:<nome>) ou "flow:" (Flow em flowruntime:interview);
      indexKey — "pageUsage" (FlexiPage, padrão) ou "experienceUsage" (views do ExperienceBundle);
      noneText — texto quando nenhuma página processada usa o componente.
    """
    index = _index(ctx)
    if index is None:
        return []
    key = f"{args.get('keyPrefix', 'c:')}{ctx.root().full_name}".lower()
    rows = [{"usage_page": u["page"], "usage_page_type": u.get("pageType"), "usage_region": u.get("region") or DASH,
             "usage_identifier": u.get("identifier") or DASH, "usage_visibility": u.get("hasVisibility") or DASH}
            for u in (index.get(args.get("indexKey", "pageUsage")) or {}).get(key, [])]
    if not rows:
        return [{"usage_page": args.get("noneText", "Nenhuma página processada nesta execução usa o componente"),
                 "usage_page_type": DASH,
                 "usage_region": DASH, "usage_identifier": DASH, "usage_visibility": DASH}]
    return rows


def event_reference_rows(ctx, args):
    """Quem publica e quem assina o evento, entre os componentes processados na execução.

    args: path — nome do evento (ex.: @fullName para `X__e`; cdc.selectedEntity no CDC).
    Trigger assinante: configuração de PlatformEventSubscriberConfig (XML do passo 6b), sem o usuário.
    """
    from salesforce_docs.rendering.context import resolve
    index = _index(ctx)
    name, _ = resolve(ctx, args.get("path", "@fullName"))
    if index is None or not name:
        return []
    configs = (getattr(ctx.root(), "access_index", None) or {}).get("subscriberConfigs") or {}
    rows = []
    for r in sorted((index.get("eventRefs") or {}).get(str(name).lower(), []),
                    key=lambda r: (r["role"] != "Publica", r["kind"], r["component"].lower())):
        cfg_text = DASH
        if r["role"] == "Assina" and r["kind"] == "Apex Trigger":
            cfg = configs.get(r["component"])
            cfg_text = (f"{cfg['name']}: batchSize {cfg.get('batchSize') or 'não informado'}; "
                        f"usuário {'configurado (não documentado)' if cfg.get('userConfigured') else 'não configurado'}"
                        if cfg else "Sem PlatformEventSubscriberConfig nos XMLs recuperados")
        rows.append({"event_role": r["role"], "event_kind": r["kind"], "event_component": r["component"],
                     "event_detail": r.get("detail") or DASH, "event_subscriber_config": cfg_text})
    if not rows:
        return [{"event_role": "Nenhum publicador ou assinante entre os componentes processados",
                 "event_kind": DASH, "event_component": DASH, "event_detail": DASH,
                 "event_subscriber_config": DASH}]
    return rows


def rule_target_rows(ctx, args):
    """Regras de atribuição/escalonamento processadas na execução que direcionam para o componente."""
    index = _index(ctx)
    if index is None:
        return []
    rows = [{"target_rule_type": t["ruleType"], "target_object": t["object"], "target_rule": t.get("rule") or DASH,
             "target_order": str(t.get("order")), "target_active": t.get("active") or DASH}
            for t in (index.get("ruleTargets") or {}).get(ctx.root().full_name.lower(), [])]
    return rows or [{"target_rule_type": "Nenhuma regra processada nesta execução direciona para o componente",
                     "target_object": DASH, "target_rule": DASH, "target_order": DASH, "target_active": DASH}]


TABLE_BUILDERS = {"index_record_rows": index_record_rows, "role_hierarchy_rows": role_hierarchy_rows,
                  "page_usage_rows": page_usage_rows, "event_reference_rows": event_reference_rows,
                  "rule_target_rows": rule_target_rows}
BLOCK_BUILDERS = {}
