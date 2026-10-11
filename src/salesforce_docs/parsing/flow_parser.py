"""Particularidades de Flow / FlowDefinition."""

from __future__ import annotations

from salesforce_docs import status as st
from salesforce_docs.parsing.xml_parser import as_list
from salesforce_docs.rendering.context import format_value, resolve


def flow_trigger_conditions(ctx, args, _render_props=None):
    """Bloco com as condições de entrada (start.filters / start.filterLogic)."""
    start, _ = resolve(ctx, "start")
    if not isinstance(start, dict):
        return st.NOT_APPLICABLE
    filters = as_list(start.get("filters"))
    lines = []
    for f in filters:
        if not isinstance(f, dict):
            continue
        field = f.get("field") or st.NOT_INFORMED
        op = f.get("operator") or st.NOT_INFORMED
        value = format_value(f.get("value"), None, ctx.sensitive) or st.NOT_INFORMED
        lines.append(f"- `{field}` {op} {value}")
    logic = start.get("filterLogic")
    formula = start.get("filterFormula")
    if logic:
        lines.append(f"- filterLogic: {logic}")
    if formula:
        lines.append(f"- filterFormula: `{formula}`")
    return "\n".join(lines) if lines else st.NOT_INFORMED


def flow_definition_matches(flow_full_name, flow_data, definition):
    """FlowDefinition relacionado: mesmo fullName (convenção da Metadata API)."""
    return definition.get("fullName") == flow_full_name


TABLE_BUILDERS = {}
BLOCK_BUILDERS = {"flow_trigger_conditions": flow_trigger_conditions}
