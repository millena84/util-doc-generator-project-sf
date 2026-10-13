"""Parsers de arquivos-fonte não XML recuperados junto do metadata (ex.: `.cls`, `.trigger`).

Configuração em `metadataTypeSettings.<Tipo>.sourceParser` (config/metadata-types-mvp.json):
`{"name": "apex", "suffix": ".cls", "key": "apex"}` — o resultado do parser entra no JSON
normalizado do componente, em `data[<key>]`. O arquivo-fonte (raw) nunca é alterado.
"""

from __future__ import annotations

from salesforce_docs.parsing.apex_parser import parse_apex_source
from salesforce_docs.parsing.apex_trigger_parser import parse_apex_trigger
from salesforce_docs.parsing.event_channel_parser import parse_event_channel_member
from salesforce_docs.parsing.flexipage_parser import parse_flexipage
from salesforce_docs.parsing.lwc_parser import parse_lwc_bundle
from salesforce_docs.parsing.sales_parser import parse_business_process, parse_lead_convert
from salesforce_docs.parsing.service_rules_parser import parse_queue, parse_service_rules

SOURCE_PARSERS = {
    "apex": parse_apex_source,
    "apex-trigger": parse_apex_trigger,
    # bundle: recebe {caminho relativo: texto} de todos os arquivos com os sufixos configurados
    "lwc": parse_lwc_bundle,
    # lê o próprio XML (FlexiPage) e achata regiões/componentes/visibilidade
    "flexipage": parse_flexipage,
    # lê o próprio XML do membro de canal (CDC) e deriva o objeto de origem
    "event-channel-member": parse_event_channel_member,
    # regras de atendimento e filas: leem o próprio XML, mascarando dado pessoal
    "service-rules": parse_service_rules,
    "queue": parse_queue,
    # Sales Cloud (Onda 08): leem o próprio XML
    "business-process": parse_business_process,
    "lead-convert": parse_lead_convert,
}


def source_file(files, metadata_type, suffix):
    """Arquivo-fonte do componente (mesmo tipo, extensão `suffix`) entre os recuperados."""
    for f in files or []:
        if f.get("type") == metadata_type and str(f.get("path", "")).endswith(suffix):
            return f
    return None
