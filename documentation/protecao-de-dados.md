# Proteção de dados e retenção

> Prioridade 3 do roadmap. Inventário dos artefatos gerados pelo utilitário, sensibilidade, proteção aplicada e retenção recomendada.

## Controles antes da coleta

1. **Configuração e escopo** são validados antes de qualquer chamada à org (`scope`, contratos, modelos).
2. **Identidade da org**: depois de `sf org display`, o `orgId` (e, se informados, `alias`, `username`, `instanceUrl`) precisa constar em `approvedOrgs` do `config.json`. Sem aprovação, a execução para com `ORG_NOT_APPROVED` **antes** de `sf org list metadata-types`, inventário ou retrieve, e informa a identidade detectada para conferência.

```json
"approvedOrgs": [
  { "orgId": "00D...", "alias": "dev", "username": "integracao@empresa.com", "note": "sandbox de documentação" }
]
```

## Inventário de artefatos

| Artefato | Local | Conteúdo / sensibilidade | Proteção | Git | Retenção recomendada |
|---|---|---|---|---|---|
| `org-display.raw.json` | `catalog/org-<alias>/api-v<N>/` | **accessToken**, username, instanceUrl | 0600; `dataProtection.orgDisplayRaw = DELETE_AFTER_RUN` apaga ao fim | ignorado | apagar ao fim (`DELETE_AFTER_RUN`) ou até o token expirar |
| Raws de erro | `runs/<runId>/errors/` | respostas de erro da CLI/API (podem conter dados de sessão) | 0600 | ignorado | apagar após análise da falha |
| `metadata-types.raw.json`, `*.describevaluetype.raw.json`, `*.schema.json`, `*.index.json` | `catalog/` | catálogo/estrutura da org; baixa sensibilidade | 0600 (raws) | versionável após revisão | enquanto a API version for usada |
| `inventory.raw.json` / `inventory.index.json` | `inventory/.../<tipo>/` | nomes de componentes, IDs, usuários que alteraram | 0600 (raw) | versionável após revisão | por execução documental |
| XML recuperado (raw) | `inventory/.../components/` | conteúdo integral do metadata: pode ter `consumerSecret`, senhas legadas, valores de CMDT, URLs internas; `.crt` | 0600 | **ignorado** | mínimo necessário para regenerar; apagar após publicação aprovada |
| Retrieve raw | `inventory/.../retrieve/` | lista de arquivos recuperados | 0600 | versionável após revisão | junto do XML |
| Normalizado | `inventory/.../normalized/` | dados do XML; segredos (`sensitiveXmlElements`) como `[REDACTED]`; `consumerKey`, valores CMDT etc. preservados | 0600 | **ignorado** | junto do XML |
| Dados internos (SOQL) | `inventory/.../internal-data/` | IDs, datas, nomes | 0600 | versionável após revisão | por execução |
| Run state | `runs/run-*.json` | status, caminhos, avisos; todo texto passa pela máscara (token e valores secretos encontrados no XML) | 0600 | versionável após revisão | histórico de auditoria (ex.: 90 dias) |
| Logs (stderr) | terminal / CI | mesmas mensagens do run state, mascaradas | — | — | conforme política do ambiente |
| Markdown | `saida/docs/doc-org-MMDDAA/` | só propriedades do contrato; nunca `sensitiveXmlElements` nem `omitFromDocumentation` | padrão do sistema | revisar antes de publicar | conforme documentação do projeto |
| Versões substituídas | `saida/docs/.../_substituidos/<runId>/` | documento anterior quando outra execução gera conteúdo diferente | padrão | revisar | apagar após conferência |

`dataProtection.privateFiles = true` (padrão) grava raws, cópias de XML, normalizados e run state com permissão `0600`.

## Mascaramento

- `accessToken`: registrado no `Masker` assim que lido; nunca aparece em run state, logs ou Markdown.
- Valores de elementos em `sensitiveXmlElements` encontrados no XML são redigidos no normalizado **e** registrados no `Masker`, de modo que mensagens de erro, avisos e exceções que os contenham também são mascarados.
- O run state é mascarado recursivamente (estruturas aninhadas) antes de cada gravação.

## Saída e retomada

- `execution.outputLayout = BY_DATE` (padrão) mantém `saida/docs/doc-org-MMDDAA/`; um manifesto registra a execução de cada arquivo e versões de outras execuções com conteúdo diferente vão para `_substituidos/`. `BY_RUN` isola em `doc-org-MMDDAA/<runId>/`.
- Colisão de nome na mesma execução (ex.: `Meu_Flow` × `Meu-Flow`) gera sufixo com hash; nada é sobrescrito.
- Retomada (`--resume`) só reaproveita unidades `SUCCESS` quando org, API version, versão do utilitário e política de dados sensíveis são iguais, a unidade está no escopo atual, os contratos/modelos do grupo não mudaram e o documento ainda existe. O motivo de cada reprocessamento fica em `resume.reprocessed`.

## Cobertura

O run state separa **término da execução** (`status`) de **cobertura** (`coverage.status = COMPLETE | INCOMPLETE`). Lacunas listadas: `noTemplate`, `failed`, `subDocuments`, `internalDataUnavailable`, `notFound`, `notEnabled`, `schemaUnavailable`. Grupos fora do escopo aparecem em `outOfScopeGroups` (não são lacuna).
