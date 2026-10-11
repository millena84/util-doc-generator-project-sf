# Fixtures de teste (SIMULADAS)

Todos os arquivos desta pasta são **simulados** para testes automatizados.
Nenhum dado aqui veio de uma org real e nenhum deve ser usado como documentação.

- `bin/sf`: Salesforce CLI simulada (Python) usada pelos testes de pipeline.
- `org/`: respostas simuladas de `sf org list`, `sf org display` e `sf org list metadata-types`.
- `inventory/<Tipo>.json`: respostas simuladas de `sf org list metadata`.
- `source/`: XMLs em formato source usados pelo retrieve simulado.
- `query/<Objeto>.json`: respostas simuladas de `sf data query`.

O token em `org/org-display.json` é um valor fictício.
