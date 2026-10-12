# Proteção de dados e retenção

> Prioridade 3 do roadmap. Inventário dos artefatos gerados pelo utilitário, sensibilidade, proteção aplicada e retenção recomendada.

## Controles antes da coleta

1. **Configuração e escopo** são validados antes de qualquer chamada à org (`selection`, contratos, modelos).
2. **Identidade da org** (passo 3b): depois de `sf org display`, a identidade precisa ser verificável — sem `orgId`, `username` ou `instanceUrl` a execução para com `ORG_IDENTITY_UNVERIFIABLE`. O `orgId` (e, se informados, `alias`, `username`, `instanceUrl`) precisa constar em `approvedOrgs` do `config.json`. Fora da allowlist:
   - **em terminal interativo** (stdin e stderr são TTY): a identidade detectada é exibida e a execução só continua se o usuário digitar o `orgId` exato (15 ou 18 caracteres). A aprovação vale **só para essa execução** (`orgApproval.method = INTERACTIVE`) e nada é gravado no `config.json`;
   - **sem terminal** (CI, `--non-interactive` ou `SFDOCS_NON_INTERACTIVE`): nunca pergunta; para com `ORG_NOT_APPROVED` (`orgApproval.method = NON_INTERACTIVE_REFUSED`).

   Em qualquer recusa, nada é coletado: a execução para **antes** do token, de `sf org list metadata-types`, inventário ou retrieve, e informa a identidade detectada para conferência.
3. **Token só depois da aprovação** (passo 3c). Campos de `sf org display` usados: `id`, `username`, `instanceUrl`, `apiVersion`, `connectedStatus`, `alias`. A documentação oficial da Salesforce CLI informa que `sf org display`/`sf org list` não exibem mais informações sensíveis de autenticação; nesse caso o token é obtido com `sf org auth show-access-token --target-org <alias> --json` (o `--json` dispensa o prompt de confirmação). Essa resposta **nunca é gravada** (nem raw, nem erro); o token vai direto ao `Masker` e à sessão em memória, e a origem fica em `tokenSource`. Falha → `ACCESS_TOKEN_UNAVAILABLE`, antes do inventário. Compatibilidade: o fluxo foi testado **somente com a CLI simulada** (`2.60.0`, com e sem token no `org display`); nenhuma org ou CLI real foi usada nesta refatoração.

```json
"approvedOrgs": [
  { "orgId": "00D...", "alias": "dev", "username": "integracao@empresa.com", "note": "sandbox de documentação" }
]
```

## Inventário de artefatos

| Artefato | Local | Conteúdo / sensibilidade | Proteção | Git | Retenção recomendada |
|---|---|---|---|---|---|
| `org-display.raw.json` | `catalog/org-<alias>/api-v<N>/` | username, instanceUrl, orgId — **só gravado quando a resposta não tem credencial** | 0600; `dataProtection.orgDisplayRaw = DELETE_AFTER_RUN` apaga ao fim | ignorado | apagar ao fim (`DELETE_AFTER_RUN`) |
| `org-display.sanitized.json` | `catalog/org-<alias>/api-v<N>/` | resposta de `sf org display` de CLIs que ainda exibem o token, com `accessToken`/`refreshToken`/`sfdxAuthUrl`/`password`/`clientSecret` como `[REDACTED]` (derivado, não raw); sem segredo, mas com a identidade da org (username, orgId, instanceUrl) | 0600 | **não ignorado** (mantido acessível para uso local); revisar antes de versionar — reavaliar ao adotar GitHub Actions | junto do catálogo |
| Respostas de erro | `runs/<runId>/errors/*.sanitized.json` (CLI) e `*.describevaluetype.raw.json` (SOAP, sem token na requisição) | erros da CLI/API; os da CLI são gravados **mascarados** (envelope sanitizado, não raw) | 0600 | ignorado | apagar após análise da falha |
| `metadata-types.raw.json`, `*.describevaluetype.raw.json`, `*.schema.json`, `*.index.json` | `catalog/` | catálogo/estrutura da org; baixa sensibilidade | 0600 (raws) | versionável após revisão | enquanto a API version for usada |
| `inventory.raw.json` / `inventory.index.json` | `inventory/.../<tipo>/` | nomes de componentes, IDs, usuários que alteraram | 0600 (raw) | versionável após revisão | por execução documental |
| XML recuperado (raw) | `inventory/.../components/` | conteúdo integral do metadata: pode ter `consumerSecret`, senhas legadas, valores de CMDT, URLs internas; `.crt` | 0600 | **ignorado** | mínimo necessário para regenerar; apagar após publicação aprovada |
| Retrieve raw | `inventory/.../retrieve/` | lista de arquivos recuperados | 0600 | versionável após revisão | junto do XML |
| Normalizado | `inventory/.../normalized/` | dados do XML; segredos (`sensitiveXmlElements`) como `[REDACTED]`; `consumerKey`, valores CMDT etc. preservados | 0600 | **ignorado** | junto do XML |
| Dados internos (SOQL) | `inventory/.../internal-data/` | IDs, datas, nomes | 0600 | versionável após revisão | por execução |
| Resumo da execução | `runs/<runId>/resumo.md` | status, cobertura, identidade da org, lacunas e métricas; gerado a partir do run state já mascarado e mascarado de novo | padrão | versionável após revisão | junto do run state |
| Run state | `runs/run-*.json` | status, caminhos, avisos; todo texto passa pela máscara (token e valores secretos encontrados no XML) | 0600 | versionável após revisão | histórico de auditoria (ex.: 90 dias) |
| Logs (stderr) | terminal / CI | mesmas mensagens do run state, mascaradas | — | — | conforme política do ambiente |
| Markdown | `saida/docs/doc-<alias>-MMDDAA/` (+ `.org.json` com o orgId dono da pasta) | só propriedades do contrato; nunca `sensitiveXmlElements` nem `omitFromDocumentation` | padrão do sistema | revisar antes de publicar | conforme documentação do projeto |
| Versões substituídas | `saida/docs/.../_substituidos/<runId>/` | documento anterior quando outra execução gera conteúdo diferente | padrão | revisar | apagar após conferência |

`dataProtection.privateFiles = true` (padrão) grava raws, cópias de XML, normalizados e run state com permissão `0600`.

## Política de raw (R1 — adotada na Refatoração 3)

Há um conflito entre "raw sem alteração" (regra 3 do `CLAUDE.md`) e "não persistir segredos". A política adotada é **R1**:

- O raw **permanece intacto** — nenhum `.raw.json` ou XML recuperado é redigido, filtrado ou reescrito. Um arquivo modificado não seria raw, e o utilitário não chama de raw nada que tenha alterado.
- A proteção vem de **onde e como** o raw é guardado, não de alterá-lo: permissão `0600`, caminhos no `.gitignore` **e** verificação ativa do Git (abaixo), segredos redigidos apenas nos **derivados** (normalizado, run state, logs, Markdown).
- Respostas que são **só** credencial não viram raw: `sf org list` (passo 2) e `sf org auth show-access-token` (passo 3c) não são gravadas.
- Resposta que **contém** credencial também não vira raw: se `sf org display` exibir o token (CLIs antigas), grava-se só o envelope `org-display.sanitized.json` com as credenciais como `[REDACTED]`. O token usado pela Metadata API vem da resposta em memória, nunca do arquivo. Respostas de erro da CLI são gravadas como envelope `*.sanitized.json` (derivado mascarado), não como raw.
- O raw do `sf org display` pode ser apagado ao fim (`dataProtection.orgDisplayRaw = DELETE_AFTER_RUN`) — exclusão, não alteração.
- A exclusão dos demais artefatos sensíveis é **explícita** e por retenção (`purge --apply --delete-sensitive`, abaixo); nunca automática.

Risco residual aceito: o XML recuperado em disco pode conter segredos (ex.: `consumerSecret`, campos legados de Named Credential) enquanto não for removido por retenção.

## Retenção: `purge` descontinua, não apaga

```bash
bin/sf-docs.sh purge --older-than-days 90                               # só lista; nada muda
bin/sf-docs.sh purge --older-than-days 90 --apply                       # marca como DESCONTINUADAS
bin/sf-docs.sh purge --older-than-days 90 --apply --delete-sensitive    # + apaga artefatos sensíveis
```

- Sem `--apply`: lista as execuções iniciadas antes do corte.
- `--apply`: grava `discontinued = {at, reason}` no run state e, no layout `BY_RUN`, `DESCONTINUADO.md` na pasta de documentos da execução. **Nenhum arquivo é apagado.** Execuções descontinuadas deixam de ser usadas por `--resume latest` e `regenerate --run latest`; um id explícito é recusado.
- `--delete-sensitive` (exige `--apply`): apaga `runs/<runId>/errors/` e os artefatos sensíveis (raw do `org display`, XMLs, normalizados, dados internos) citados **somente** por execuções descontinuadas — o que uma execução ativa ainda cita é mantido. Só apaga dentro de `catalog/`, `inventory/` e `runs/`; a lista apagada fica em `discontinued.deletedSensitive`. Execuções descontinuadas desse modo não podem mais ser regeneradas.

## Elementos sensíveis: revisão

A lista não é considerada completa. `sensitiveXmlElements` (redigidos no normalizado e registrados no `Masker`):

| Elemento | Situação |
|---|---|
| `consumerSecret`, `privateKey`, `password`, `secret`, `accessToken`, `refreshToken`, `oauthToken` | lista anterior |
| `oauthRefreshToken` | **adicionado**: campo de Named Credential legado (Metadata API), ao lado de `password` e `oauthToken`, depreciados na API 56 |

A confirmar em documentação oficial antes de entrar na lista (não adicionados para não inventar elementos): segredos de provedores de autenticação (`AuthProvider`), de `ExternalCredential` (parâmetros de principal) e chaves de serviços externos citadas em outros metadata types. Novos tipos do MVP devem passar por essa revisão antes do primeiro retrieve.

## Git não é controle suficiente

`validate-config` e `run` usam `git ls-files` e `git check-ignore`:

- arquivo sensível **já rastreado** (raw de `org display`, XML recuperado, normalizado, resposta de erro, `.ecaGlblOauth-meta.xml`, `.crt`; `tests/fixtures/` é isento por ser sintético) → `validate-config` falha e `run` para com `SENSITIVE_FILES_TRACKED` antes de qualquer chamada à org;
- caminho sensível **não ignorado** → aviso (erro com `--strict`);
- fora de repositório Git → registrado como verificação indisponível (`gitGuard.available = false`), nunca como aprovada.

## Mascaramento

- `accessToken`: registrado no `Masker` assim que lido; nunca aparece em run state, logs ou Markdown.
- Valores de elementos em `sensitiveXmlElements` encontrados no XML são redigidos no normalizado **e** registrados no `Masker`, de modo que mensagens de erro, avisos e exceções que os contenham também são mascarados.
- O run state é mascarado recursivamente (estruturas aninhadas) antes de cada gravação.
- Respostas de erro da CLI (stdout e stderr) são gravadas mascaradas em `*.sanitized.json`.
- Barreira final: se o Markdown renderizado contiver um valor conhecido como sensível (token ou valor redigido do XML, mesmo vindo de outro campo), o documento não é gravado e a unidade fica `FAILED`.

## Saída e retomada

- `execution.outputLayout = BY_DATE` (padrão) mantém tudo o que for processado no dia, para a org, em `saida/docs/doc-<alias>-MMDDAA/`; um manifesto registra a execução de cada arquivo e versões de outras execuções com conteúdo diferente vão para `_substituidos/`. `BY_RUN` isola cada execução em `saida/docs/doc-<alias>-MMDDAA/<runId>/`.
- Orgs diferentes nunca compartilham pasta: `.org.json` guarda o `orgId` dono da pasta do dia. Mesmo alias apontando para outra org no mesmo dia → `doc-<alias>-<orgId>-MMDDAA/`, com aviso no log e no `resumo.md` (`output.orgFolderConflict`).
- Retomada e `regenerate` gravam, por padrão, na pasta da execução de origem (`execution.resumeOutput = ORIGINAL_FOLDER`), mesmo em outro dia, para a coleta ficar completa numa pasta só; `TODAY` (ou `--resume-output TODAY`) grava na pasta do dia. Cada componente registra o dia em que foi processado (`processedOn`); acima de `execution.resumeWarnAfterDays` dias, o log e o `resumo.md` recomendam uma execução completa nova.
- Colisão de nome na mesma execução (ex.: `Meu_Flow` × `Meu-Flow`) gera sufixo com hash; nada é sobrescrito.
- Retomada (`--resume`) só reaproveita unidades `SUCCESS` quando org, API version, versão do utilitário, política de dados sensíveis e `config/metadata-types-mvp.json` são iguais, a unidade está no escopo atual, os contratos/modelos do grupo não mudaram, o documento ainda existe e o XML de origem existe com o mesmo sha256. O motivo de cada reprocessamento fica em `resume.reprocessed`.
- `--resume latest` ignora execuções de regeneração e descontinuadas.
- `regenerate` usa contratos, modelos e política **atuais** sobre os raws da execução de origem: as diferenças em relação à origem ficam em `regenerate.differences` (e no log), e unidades cujo XML sumiu ou mudou são recusadas (`FAILED`, `errorClass = SOURCE_UNAVAILABLE`).
- Documentos e resumo são gravados de forma atômica (arquivo temporário + `os.replace`).

## Resumo e erros inesperados

- Toda execução (inclusive com falha) grava `runs/<runId>/resumo.md`: status e significado, cobertura, identidade e aprovação da org, origem do token, seleção, tipos descobertos/configurados/selecionados/excluídos/processados/documentados/sem modelo, componentes com falha (com `errorClass`: `PERMISSION_DENIED`, `TIMEOUT`, `SESSION_EXPIRED`, `NOT_FOUND_IN_ORG`, `SENSITIVE_CONTENT_BLOCKED`, `ERROR`), pendentes e chamadas à CLI por metadata type (`metrics`).
- Erro inesperado: o run state termina `FAILED` com `UNEXPECTED_ERROR` e mensagem mascarada; o CLI imprime só `ERRO inesperado (Tipo): mensagem` mascarada (traceback, também mascarado, apenas com `--debug`).

## Cobertura

O run state separa **término da execução** (`status`) de **cobertura** (`coverage`):

- `coverage.status`: `COMPLETE`, `COMPLETE_WITH_WARNINGS` (só `internalDataUnavailable`, `notEnabled`, `schemaUnavailable`) ou `INCOMPLETE` (lacunas bloqueantes: `noTemplate`, `failed`, `subDocuments`, `notFound`, ou execução interrompida).
- Execução sem falhas de componente mas com lacuna bloqueante termina como `COMPLETED_WITH_GAPS`, nunca `SUCCESS` (código `3` com `execution.strictCoverage = true`).
- `coverage.types`: tipos descobertos (`sf org list metadata-types`), configurados, excluídos (por configuração, fora do escopo, não habilitados na org), processados, documentados (como principal ou relacionado) e sem modelo.
