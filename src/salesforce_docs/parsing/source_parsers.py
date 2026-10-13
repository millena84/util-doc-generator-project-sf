"""Parsers de arquivos-fonte não XML recuperados junto do metadata (ex.: `.cls`).

Configuração em `metadataTypeSettings.<Tipo>.sourceParser` (config/metadata-types-mvp.json):
`{"name": "apex", "suffix": ".cls", "key": "apex"}` — o resultado do parser entra no JSON
normalizado do componente, em `data[<key>]`. O arquivo-fonte (raw) nunca é alterado.
"""

from __future__ import annotations

from salesforce_docs.parsing.apex_parser import parse_apex_source

SOURCE_PARSERS = {
    "apex": parse_apex_source,
}


def source_file(files, metadata_type, suffix):
    """Arquivo-fonte do componente (mesmo tipo, extensão `suffix`) entre os recuperados."""
    for f in files or []:
        if f.get("type") == metadata_type and str(f.get("path", "")).endswith(suffix):
            return f
    return None
