"""Estados oficiais de execução (SKILL.md e prompt, seção 9)."""

SUCCESS = "SUCCESS"
NO_TEMPLATE = "NO_TEMPLATE"
NO_COMPONENTS = "NO_COMPONENTS"
NOT_ENABLED = "NOT_ENABLED"
SCHEMA_UNAVAILABLE = "SCHEMA_UNAVAILABLE"
RETRIEVE_FAILED = "RETRIEVE_FAILED"
INTERNAL_DATA_UNAVAILABLE = "INTERNAL_DATA_UNAVAILABLE"
RETRY_REQUIRED = "RETRY_REQUIRED"
MISMATCH = "MISMATCH"
FAILED = "FAILED"

# Estados auxiliares de execução/tipo (não substituem os oficiais).
IN_PROGRESS = "IN_PROGRESS"
ENABLED = "ENABLED"
EXCLUDED = "EXCLUDED"
INTERRUPTED = "INTERRUPTED"
PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
OUT_OF_SCOPE = "OUT_OF_SCOPE"  # grupo configurado, mas excluído do escopo da execução

# Componentes nestes estados são reprocessados na retomada.
REPROCESS_STATES = {RETRY_REQUIRED, FAILED, IN_PROGRESS}

# Fontes permitidas na coluna "Fonte" (prompt, seção 6.1).
ALLOWED_SOURCES = (
    "XML",
    "Metadata API",
    "Tooling API",
    "Objeto interno",
    "Salesforce CLI",
    "Derivado",
)

# Valores permitidos para dado ausente (prompt, seção 6.2).
NOT_INFORMED = "Não informado"
NOT_APPLICABLE = "Não aplicável"
