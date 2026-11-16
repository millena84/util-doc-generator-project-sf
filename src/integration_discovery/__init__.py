"""Fase 2 — `integration_discovery`: cruzamento de integrações.

Consome SOMENTE os JSONs normalizados já gerados pelo Utilitário 1 (`salesforce_docs`) em
`inventory/org-<alias>/api-v<N>/<pasta>/normalized/`, a partir de uma lista de componentes
curada pela usuária (CSV), e propõe clusters candidatos de integração com evidência.

Não altera o Utilitário 1, não lê XML bruto nem Markdown, não acessa a org e não gera dossiê:
todo cluster é CANDIDATE e todo nome é PROPOSTA até a aprovação humana.
"""

__version__ = "0.1.0"
