# Entrada da Fase 2 (`integration_discovery`)

- `componentes-squad.example.csv`: exemplo **simulado** do formato.
- `componentes-squad.csv`: o CSV real, curado à mão pela usuária. Copie o exemplo e edite.

Formato, validação e uso: [`documentation/fase-2-integration-discovery.md`](../../documentation/fase-2-integration-discovery.md).

As saídas ficam em `discovery/org-<alias>/api-v<N>/` (`graphs`, `clusters`, `proposals`, `orphans`, `report` e `state`), separadas por org e versão. São derivadas do inventário da org e ficam fora do Git (`.gitignore`).
