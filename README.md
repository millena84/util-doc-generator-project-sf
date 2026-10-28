# util-doc-generator-project-sf

Utilitário único para gerar documentação Markdown de componentes Salesforce, combinando dados da org, XMLs recuperados, objetos internos e modelos por metadata type.

> ⚠️ **Restrição atual — produção sem login.** Por ora **não é permitido login** (`sf org login ...`) em org **produtiva**. O `run` com login só deve ser usado em org de desenvolvimento ou sandbox autorizada. Para produção, use o **modo pasta** (`run --source-dir`): o utilitário lê o **repositório já clonado** (ex.: Flosum), sem login e sem Salesforce CLI. Dados internos exportados pelo Salesforce Inspector ainda não são lidos. Ver a seção "Modo pasta" e [`documentation/checklist-acessos-modo-pasta.md`](documentation/checklist-acessos-modo-pasta.md).

**Como testar o MVP** (sem org, org não produtiva e produção): [`documentation/como-testar-o-mvp.md`](documentation/como-testar-o-mvp.md).

## Requisitos

- Python **3.8+** — somente biblioteca padrão. **Nenhum `pip install`** é necessário.
- Salesforce CLI (`sf`) **2.0.0+** (mínima configurada em `config/config.json`). Não é usada no modo pasta.
- Bash (para o invólucro `bin/sf-docs.sh`; opcional — o módulo Python roda direto).
- Org **não produtiva** autenticada: `sf org login web --alias dev` (produção: login não permitido por ora; ver a restrição acima).

## Uso

```bash
# Pipeline completo (passos 1–10), alias e API version detectados automaticamente
bin/sf-docs.sh run

# Piloto: só o grupo Flow (pode repetir --group / --component)
bin/sf-docs.sh run --group Flow
bin/sf-docs.sh run --group Flow --component Meu_Flow

# Forçar API version (prevalece sobre a detectada em `sf org display`)
bin/sf-docs.sh run --api-version 67.0

# Retomar após sessão expirada (não reprocessa componentes SUCCESS)
bin/sf-docs.sh run --resume latest          # ou --resume run-20261010-210000
# Por padrão a retomada grava na pasta da coleta original (mesmo em outro dia);
# para gravar na pasta do dia atual:
bin/sf-docs.sh run --resume latest --resume-output TODAY

# Regerar derivados (index/schema/normalized) e Markdown SOMENTE a partir dos raws/XMLs
bin/sf-docs.sh regenerate --run latest

# Validar config, contratos e modelos (sem acessar a org)
bin/sf-docs.sh validate-config

# CI / sem terminal: nunca pergunta (org fora de approvedOrgs → para)
bin/sf-docs.sh run --non-interactive

# Retenção: lista execuções antigas; --apply marca como DESCONTINUADAS (nada é apagado)
bin/sf-docs.sh purge --older-than-days 90 [--apply [--delete-sensitive]]

# Erro inesperado com traceback (mascarado)
bin/sf-docs.sh --debug run

# Modo pasta: repositório já clonado (ex.: Flosum), sem login e sem Salesforce CLI
bin/sf-docs.sh run --source-dir /caminho/Org01Repo --group Profile --group Role
```

Sem Bash (ex.: Windows): `PYTHONPATH=src python -m salesforce_docs run`.

Códigos de saída: `0` sucesso (inclui `PARTIAL_SUCCESS` e `COMPLETED_WITH_GAPS`), `1` falha global ou erro inesperado (mensagem mascarada), `2` sessão expirada (estado salvo para retomada), `3` `COMPLETED_WITH_GAPS` com `execution.strictCoverage = true`. Toda execução grava `runs/<runId>/resumo.md`.

## Modo pasta (`run --source-dir`) — repositório clonado, sem login

Lê os metadados de um projeto Salesforce **já clonado** (ex.: repositório do Flosum). O utilitário não clona, não faz login, não usa a Salesforce CLI e nunca altera o repositório.

1. Cadastre o de-para pasta → org em `config/config.json` (só pastas cadastradas são lidas):

   ```json
   "sourceRepositories": [
     { "folder": "Org01Repo", "orgName": "Nome da org 01" },
     { "folder": "Org02Repo", "orgName": "Nome da org 02", "alias": "org02", "metadataPath": "src" }
   ]
   ```

   `folder` é só o nome da pasta. `alias` (opcional, padrão: nome da pasta em minúsculas) nomeia as pastas de saída. `metadataPath` (opcional) é a subpasta com `profiles/`, `objects/`...; sem ele, procura em `.`, `src` e `force-app/main/default`.
2. `bin/sf-docs.sh run --source-dir /caminho/Org01Repo [--group ...] [--component ...]`.

| Item | Comportamento |
|---|---|
| Passos | 1–3c não existem; 4, 6, 6b e 7 leem o repositório; 8 e 10 são os mesmos do modo com login; 5 e 9 (exigem a org) não são feitos |
| Formatos | source do SFDX (`Admin.profile-meta.xml`, objeto em subpastas) e metadata da Metadata API (`Admin.profile`, campos dentro do `.object`); detectados sozinhos; não precisa de `sfdx-project.json` nem `package.xml` |
| Pasta e sufixo por tipo | `config/metadata-types-mvp.json` → `sourceDirectory` (Metadata API Developer Guide, *File Suffix and Directory Location*) |
| Raw | o repositório; `catalog/org-<alias>/api-v<N>/source-manifest.json` registra caminho e sha256 de cada arquivo lido; arquivos usados copiados byte a byte para `inventory/.../components/` (no formato metadata, o `.object` original fica em `components/_repositorio/` e objeto + filhos são derivados) |
| Origem no documento | logo abaixo do título: "**Origem:** repositório `Org01Repo` (org: **Nome da org 01**)". A coluna "Fonte" continua `XML` |
| Dados internos | "Não informado" (aviso `INTERNAL_DATA_UNAVAILABLE`; cobertura `COMPLETE_WITH_WARNINGS`) |
| Valor ausente | "Não informado" (sem `describeValueType` não há como provar "Não aplicável") |
| OWD de objetos padrão | só no modo pasta, o grupo CustomObject inclui objetos padrão (ex.: Account) que tenham arquivo no repositório (`sourceDirectoryComponentFilter`) |
| Retomada | `--resume` reaproveita só se a pasta e o conteúdo do repositório não mudaram |
| Ignorados | links simbólicos, pastas ocultas (ex.: `.git`), pastas sem tipo configurado e arquivos de filhos não configurados (ex.: `listViews`); listados no log e no `resumo.md` |

## Ordem de execução

| Passo | Ação | Raw | Derivado |
|---|---|---|---|
| 1 | `sf --version` ≥ mínima | — | — |
| 2 | `sf org list --json` contém o alias | não persistido (dado local da CLI, pode conter tokens) | — |
| 3 | `sf org display --target-org <alias> --json` | `catalog/org-<alias>/api-v<N>/org-display.raw.json` se a resposta não tiver credencial; senão só `org-display.sanitized.json` (credenciais como `[REDACTED]`) | — |
| 3b | Aprovação da org (`approvedOrgs` ou confirmação interativa do `orgId`) | — | `orgApproval` no run state |
| 3c | Token: do `org display` (CLIs antigas) ou `sf org auth show-access-token --json` | não persistido | `tokenSource` no run state |
| 4 | `sf org list metadata-types` | `catalog/.../metadata-types.raw.json` | `metadata-types.index.json` |
| 5 | `describeValueType()` via Metadata API (SOAP, `urllib`) | `catalog/.../schemas/<tipo>.describevaluetype.raw.json` | `<tipo>.schema.json` |
| 6 | `sf org list metadata --metadata-type <tipo>` | `inventory/.../<pasta>/inventory.raw.json` | `inventory.index.json` |
| 6b | Fontes de acesso: `sf project retrieve start` **único** com Profile, PermissionSet, PermissionSetGroup, Queue, SharingRules **e** os componentes documentados | `inventory/.../access/retrieve.raw.json` + XMLs em `access/components/` | `access/access-index.json` |
| 7 | `sf project retrieve start --metadata <tipo>:<nome>` | `inventory/.../<pasta>/retrieve/<comp>.raw.json` + XML original em `components/` | — |
| 8 | XML → JSON | — | `inventory/.../<pasta>/normalized/<comp>.json` (filhos: `<tipo>--<comp>.json`, ex.: `record-type--pedido-c-padrao.json`) |
| 9 | `sf data query` (se o contrato prever) | `inventory/.../<pasta>/internal-data/<comp>.raw.json` | — |
| 10 | Modelo + contrato → Markdown | — | `saida/docs/doc-<alias>-<MMDDAA>/doc-<comp>-<tipo>.md` |

Estado da execução: `runs/run-<AAAAMMDD-HHMMSS>.json`. Respostas de erro ficam em `runs/<runId>/errors/` (não sobrescrevem raws válidos).

## Decisões de implementação

- **Raw do `describeValueType`**: a Metadata API responde em XML (SOAP). O raw é um envelope JSON (`rawFormat: metadata-api-soap-capture/v1`) com `request` (endpoint, tipo, data — **sem token**) e `response.body` contendo o **XML exatamente como recebido**. O `.schema.json` é derivado desse corpo e pode ser regenerado.
- **Token**: obtido só depois da aprovação da org — de `sf org display` quando a CLI ainda o exibe, senão de `sf org auth show-access-token --json` (resposta não gravada) —, mantido só em memória, mascarado em logs/`repr`/`str`, não serializável (pickle/deepcopy) e descartado (`OrgSession.clear()`) ao fim de cada execução. Se a CLI ainda exibir o token em `sf org display`, a resposta **não vira raw**: grava-se apenas `org-display.sanitized.json`, com `accessToken` e demais credenciais como `[REDACTED]` (política R1: resposta com credencial não é persistida em bruto). Sem credencial na resposta, `org-display.raw.json` é salvo inalterado, `0600` e no `.gitignore`.
- **Retrieve**: roda em um projeto SFDX temporário; o XML é copiado byte a byte, preservando as pastas do formato source (ex.: `objects/Obj__c/fields/...`).
- **Valores ausentes**: `Não aplicável` quando o `describeValueType` comprova que o campo não existe no tipo; `Não informado` quando existe mas não veio no XML/dado interno.
- **Dados sensíveis**: elementos listados em `sensitiveXmlElements` (ex.: `consumerSecret`; também a configuração JSON do OmniStudio e os elementos de usuário/e-mail) nunca são renderizados e são substituídos por `[REDACTED]` no JSON normalizado (o XML original fica intacto); o run log avisa quando um XML recuperado os contém. `ExtlClntAppGlobalOauthSettings` é tipo excluído (contém consumer secret).
- **Valores sujeitos a decisão de segurança** (`omitFromDocumentation`: `consumerKey`, `callbackUrl`, `contactEmail/Phone`, `certificate`, `parameterValue`, usuários de execução; permission sets e perfis autorizados **saíram** da lista — ver "Acesso e configuração"): nunca entram no Markdown. A linha é **omitida** (sem criar valor além de `Não informado`/`Não aplicável`) e o nome da propriedade fica em `omittedProperties` no run state. Valores (`<values>`) de records de Custom Metadata também não são renderizados.
- **`inventory/**/components/` e `inventory/**/normalized/` estão no `.gitignore`**: o raw é preservado em disco, mas pode conter valores sensíveis.
- **External Client App**: o nome correto do metadata type é `ExternalClientApplication` (Metadata API). O grupo continua chamado `ExternalClientApp`.
- **Dados internos**: todo documento principal (e os subdocumentos de Flow) tem a seção "Dados internos". As consultas não bloqueiam a execução; objeto inacessível → "Não informado". Com `expectSingleRecord`, mais de um registro para o componente é descartado como ambíguo. `validate-config` recusa consulta que selecione campo de `sensitiveXmlElements` ou `omitFromDocumentation`, e campos bloqueados devolvidos pela org não são renderizados.

  | Documento | Objeto interno | API | Situação |
  |---|---|---|---|
  | Flow (e subdocumentos trigger/autolaunched/tela) | `Flow` (versões e status) | Tooling | `validationPending` |
  | Custom Object / Custom Metadata | `EntityDefinition` | Tooling | `validationPending` |
  | Connected App | `ConnectedApplication` | padrão | `validationPending` (confirmar se `Name` = fullName) |
  | Named Credential | `NamedCredential` (sem `Endpoint`, que é omitido) | padrão | `validationPending` |
  | Certificate | `Certificate` | Tooling | `validationPending` |
  | External Credential | `ExternalCredential` | padrão | `validationPending` |
  | External Client App | — | — | "Não aplicável": nenhum objeto consultável confirmado em documentação oficial |
  | Remote Site Setting | — | — | "Não aplicável": `RemoteProxy` (Tooling) não documenta campo de nome filtrável |

## Acesso e configuração (onde cada componente está configurado)

Todo documento termina com a seção **"Acesso e configuração"**: perfis, permission sets e permission set groups que concedem acesso ao componente, com o acesso concedido (ex.: `Ler, Editar`, `Executar`) e o caminho (`via Permission Set X`). Fonte: **XML**.

- **Retrieve único (passo 6b)**: Profile, PermissionSet, PermissionSetGroup, Queue e SharingRules são recuperados **junto com os componentes documentados**, porque o XML de Profile (e possivelmente de PermissionSet) só traz permissões dos componentes presentes no mesmo retrieve. Em `selection.mode = SELECTED` entram só os componentes selecionados; as fontes de acesso entram sempre (todas), pois sem elas não há como saber quem tem acesso — desligável com `accessSources.enabled = false`.
- **Configuração** (`accessSources` em `config/metadata-types-mvp.json`): quais elementos do XML concedem acesso a qual tipo (`classAccesses` → ApexClass, `flowAccesses` → Flow, `objectPermissions` → CustomObject, `fieldPermissions` → campos, `recordTypeVisibilities`, `customMetadataTypeAccesses`, `externalCredentialPrincipalAccesses`). Concessão com `enabled`/flag `false` não é acesso.
- **Por tipo**: Connected App usa `profileName`/`permissionSetName` do próprio XML; External Client App, `commaSeparatedProfile`/`commaSeparatedPermissionSet` da política OAuth; Named Credential, os principals da External Credential relacionada; Remote Site Setting e Certificate: "Não aplicável" (sem atribuição por perfil/permission set). Subdocumentos herdam a lista do componente principal.
- **Role, fila e grupo** controlam acesso a **registros**, não a componentes: aparecem no Custom Object, na seção **"Compartilhamento e filas"** (filas que aceitam o objeto e regras de compartilhamento para role, grupo ou fila).
- **Documento de Permission Set** (`modelo-doc-permission-set`): objetos (ler, criar, editar, excluir, ver/modificar todos), **campos** (ler/editar), classes, flows, Custom Metadata Types, record types, principals de External Credential, permissões de sistema e os grupos que o incluem. O XML vem do retrieve de acesso (completo); o permission set não é recuperado de novo.
- **Não entram**: usuários atribuídos (`PermissionSetAssignment`) e membros de filas/grupos — dados pessoais que não descrevem o componente.
- **Sem índice** (retrieve de acesso falhou ou desligado): a seção fica "Não informado" — nunca "sem acesso". Com índice e nenhuma concessão: "Nenhuma concessão encontrada".
- **Regra**: `validate-config` falha se um contrato com modelo não tiver exatamente uma tabela `access_rows` (tipos sem atribuição declaram `args.notApplicable` com o motivo) ou se "Acesso e configuração" não for a **última** seção do modelo — vale para os tipos que vierem nas próximas ondas.
- `regenerate` reconstrói o índice a partir dos XMLs de acesso da execução de origem, sem acessar a org.

## Riscos conhecidos (tratar futuramente, se necessário)

Registro da auditoria de segurança de 2026-10-11 (10 riscos: 1 crítico, 2 altos, 5 médios, 2 baixos). Só o risco crítico foi detalhado e tratado até agora; os demais ainda precisam ser descritos aqui quando o relatório completo estiver disponível.

| # | Risco | Situação | Possível tratamento futuro |
|---|---|---|---|
| 1 | 🔴 `accessToken` mantido em memória durante a execução | **Mitigado**: mascarado em `repr`/`str`, serialização bloqueada, descartado em `finally` ao fim da execução; `MetadataApiClient` obtém o token da sessão a cada chamada (sem cópia própria). | Risco residual: Python não permite zerar uma `str` na memória; um dump do processo durante a execução ainda expõe o token. Aceitável para uso local. |
| 1a | 🔴 `accessToken` gravado em disco em `catalog/.../org-display.raw.json` (e em `runs/*/errors/`) | **Resolvido**: resposta com token gera só `org-display.sanitized.json` (token como `[REDACTED]`); o token segue apenas em memória. `DELETE_AFTER_RUN` continua disponível para o raw sem credencial. | Raws antigos com token: apagar com `purge --apply --delete-sensitive` ou manualmente. |
| P3 | Coleta em org errada; segredos em mensagens; sobrescrita silenciosa; retomada incompatível; cobertura não informada | **Tratados na Prioridade 3**: `approvedOrgs` (nada é coletado sem aprovação), máscara de valores secretos do XML e run state mascarado recursivamente, arquivos `0600`, manifesto/`_substituidos`/`BY_RUN`, fingerprint de retomada, `coverage`. | Ver `documentation/protecao-de-dados.md`. |
| R3 | Raw × segredo; confirmação de org; CLI sem token no `org display`; erro inesperado sem estado; retomada/regeneração com fonte alterada; retenção | **Tratados na Refatoração 3** (seção abaixo). | CLI real ainda não validada (só simulada). |
| DA-08 | 🟡 Documentação de uma mesma coleta dividida entre pastas após `--resume`; orgs diferentes na mesma pasta do dia | **Resolvido**: padrão `BY_DATE` com pasta por org (`doc-<alias>-MMDDAA`, dono registrado em `.org.json`); retomada/regeneração gravam na pasta da coleta original (`resumeOutput`). | Retomada muito antiga mistura datas na pasta: o `resumo.md` lista componentes por dia e recomenda execução nova. |
| DA-12 | 🟢 `org-display.sanitized.json` (identidade da org, sem segredo) fora do `.gitignore` | **Decisão**: mantido acessível e não ignorado para uso local; tabela de `protecao-de-dados.md` corrigida. | Reavaliar (ignorar no Git) ao adotar GitHub Actions. |
| DA-03 | 🟡 Normalizado de um filho sobrescrito por outro filho de tipo diferente com o mesmo fullName (ex.: RecordType e ValidationRule `Pedido__c.Padrao`) | **Resolvido**: o nome do normalizado de filho inclui o tipo (`<tipo>--<comp>.json`). | Normalizados antigos (sem o tipo) ficam órfãos após a próxima execução/`regenerate`; podem ser apagados. |
| DA-05 | 🟡 Dados internos de componente de pacote podem incluir homônimo de outro namespace (consultas não filtram `NamespacePrefix`) | **Mitigado**: o documento (logo após "Dados internos"), o run state e o log avisam quando o componente tem namespace e a consulta não filtra. | Filtrar por namespace depois de confirmar os campos no piloto (`documentation/piloto-org-real.md`, Apêndice B). |
| DA-10, DA-13, DA-14 | 🟢 Premissas da CLI/org não confirmadas: `connectedStatus` em JWT/scratch, `ConnectedApplication.Name` × fullName, formato de `sf org auth show-access-token --json` | **Pendente de piloto**: erro nessas premissas não vaza dados (a execução para com mensagem clara ou a seção fica "Não informado"). | Roteiro com comandos e resultado esperado: `documentation/piloto-org-real.md`. |
| 2–10 | Demais riscos da auditoria (2 altos, 5 médios, 2 baixos) | **Não detalhados** neste registro. | Incluir descrição, localização e decisão quando o relatório completo estiver disponível. |

## Desvios (configuráveis em `config/metadata-types-mvp.json`)

| Grupo | `documentStrategy` | Como os relacionados são encontrados (`relations`) |
|---|---|---|
| Flow | `SINGLE_DOCUMENT_PER_FLOW_WITH_RELATED_COMPONENTS` | `FlowDefinition` com mesmo fullName (`SAME_FULL_NAME`); subdocumentos via `subDocuments`: trigger (`start.triggerType` presente), autolaunched (`processType = AutoLaunchedFlow` **e** sem `start.triggerType`) e uma tela por `screens` |
| ExternalClientApp | `SINGLE_DOCUMENT_PER_APP_WITH_RELATED_COMPONENTS` | `ExtlClntAppOauthSettings`, `ExtlClntAppConfigurablePolicies` e `ExtlClntAppOauthConfigurablePolicies` cujo `externalClientApplication` = app (`FIELD_EQUALS_PRIMARY`). ExternalCredential e ConnectedApp têm documento próprio e não fazem parte da ECA. |
| CustomObject | `SINGLE_DOCUMENT_PER_OBJECT_WITH_RELATED_COMPONENTS` | filhos retornados no retrieve do objeto (`CHILD_OF_PRIMARY`) |
| CustomMetadata | `ONE_DOCUMENT_PER_TYPE_AND_RECORDS` | records `Tipo.Record` agrupados no tipo `Tipo__mdt` (`typeDefinition`); campos do `__mdt` como filhos (`CHILD_OF_PRIMARY`) |
| NamedCredential | `SINGLE_DOCUMENT_PER_NAMED_CREDENTIAL_WITH_RELATED_COMPONENTS` | `ExternalCredential` cujo fullName aparece exatamente em `namedCredentialParameters.externalCredential` do XML da NC (`PRIMARY_FIELD_REFERENCES`); as propriedades da EC vêm do XML da própria EC, com arquivo e sha256 |
| ExternalCredential, ConnectedApp, RemoteSiteSetting, Certificate | `ONE_DOCUMENT_PER_COMPONENT` | — (Certificate: só o `.crt-meta.xml` é lido; o `.crt` fica só como raw) |
| PermissionSet | `ONE_DOCUMENT_PER_COMPONENT` | — (XML do retrieve de acesso, passo 6b) |
| Profile, PermissionSetGroup, SharingRules | `ONE_DOCUMENT_PER_COMPONENT` | — (XML do retrieve de acesso, passo 6b; SharingRules: um documento por objeto, com o OWD do CustomObject processado) |
| Role | `ONE_DOCUMENT_PER_COMPONENT` | — (hierarquia por `parentRole` entre os papéis processados; `usesRunIndex`) |
| PublicGroup (`Group`) | `ONE_DOCUMENT_PER_COMPONENT` | — (membros não documentados) |
| OrgSecurity (`SecuritySettings`) | `ONE_DOCUMENT_PER_ORG` | — (componente fixo `Settings:Security` em `fixedComponents`, sem inventário; OWD dos CustomObject processados; `Organization` nos dados internos) |
| ApexClass | `ONE_DOCUMENT_PER_COMPONENT` + subdocumentos por papel | — (o `.cls` é lido pelo parser estrutural configurado em `sourceParser`; classes de pacote gerenciado `ns__*` são excluídas por `componentFilter`) |
| ApexTrigger | `ONE_DOCUMENT_PER_COMPONENT` | — (o `.trigger` é lido pelo parser `apex-trigger`; grupo com `usesRunIndex`: processado por último, mostra Flows, regras de validação e triggers do mesmo objeto; `lookupInventories` lista ApexClass só para conferência) |
| LightningComponentBundle | `ONE_DOCUMENT_PER_COMPONENT` + subdocumentos por target | — (o bundle inteiro — `.js`, `.html`, `.css`, `.svg`, `.js-meta.xml` — é lido pelo parser `lwc` com `sourceParser.bundle`; `usesRunIndex` para conferir os métodos Apex chamados nas classes processadas) |
| FlexiPage | `ONE_DOCUMENT_PER_COMPONENT` | — (XML achatado pelo parser `flexipage`; ativação pelo `actionOverrides` do CustomObject processado e pelo CustomApplication do passo 6b; `usesRunIndex`) |
| PlatformEvent (`CustomObject` `__e`) | `SINGLE_DOCUMENT_PER_OBJECT_WITH_RELATED_COMPONENTS` | CustomField do evento (`CHILD_OF_PRIMARY`); grupo com `contract`/`documentSlug` próprios, `componentFilter` `__e$` (o grupo CustomObject segue com `__c$`) |
| ChangeDataCapture (`PlatformEventChannelMember`) | `ONE_DOCUMENT_PER_COMPONENT` | — (XML lido pelo parser `event-channel-member`; objeto de origem pela convenção de nomes) |
| AssignmentRules, AutoResponseRules, EscalationRules | `ONE_DOCUMENT_PER_COMPONENT` | — (um documento por objeto; XML lido pelo parser `service-rules`, que mascara usuários e e-mails) |
| Queue | `ONE_DOCUMENT_PER_COMPONENT` | — (XML do retrieve de acesso, passo 6b; parser `queue`; regras que direcionam para a fila via `recordIndex.rules`) |
| BusinessProcess | `ONE_DOCUMENT_PER_COMPONENT` | RecordType do mesmo objeto cujo `businessProcess` é o processo (`FIELD_EQUALS_PRIMARY_NAME`; inventário de RecordType via `lookupInventories`) |
| LeadConvertSettings | `ONE_DOCUMENT_PER_ORG` | — (componente fixo `LeadConvertSettings:LeadConvertSettings`; parser `lead-convert`) |
| Territory2Model | `ONE_DOCUMENT_PER_COMPONENT` | Territory2 e Territory2Rule com nome `<modelo>.*` (`NAME_PREFIX`) |
| OpportunitySplitType | `ONE_DOCUMENT_PER_COMPONENT` | — (folhas do XML como estão, `leaf_properties`) |
| Network | `ONE_DOCUMENT_PER_COMPONENT` | CustomSite cujo nome é o `<site>` da Network (`PRIMARY_FIELD_REFERENCES`); parser `network` (remetente de e-mail nunca guardado) |
| CustomSite | `ONE_DOCUMENT_PER_COMPONENT` | Network cujo `<site>` é o site (`FIELD_EQUALS_PRIMARY`); parser `custom-site` (usuários nunca guardados) |
| ExperienceBundle | `ONE_DOCUMENT_PER_COMPONENT` | — (bundle: `.site-meta.xml` + `views/`, `routes/`... em JSON, parser `experience-bundle`; índice da execução liga as views aos LWC) |
| OmniDataTransform, OmniIntegrationProcedure, OmniScript, OmniUiCard | `ONE_DOCUMENT_PER_COMPONENT` | — (XML da Metadata API; parsers `omni-data-transform`, `omni-process` e `omni-ui-card`; quem chama quem via `recordIndex.omni`) |

Cada componente (principal ou relacionado) é extraído e normalizado de forma independente; a agregação acontece apenas no documento.

## Seleção da execução (`config.json` → `selection`)

| Item | Onde | Precedência |
|---|---|---|
| Alias da org | `orgAlias` | `--target-org` > `config.json` (o `orgAlias` de `metadata-types-mvp.json` é só informativo; divergência gera aviso) |
| Diretórios | `paths` (`catalog`, `inventory`, `models`, `contracts`, `runs`, `outputDocs`, `metadataTypesConfig`) | `config.json` |
| O que documentar | `selection.mode` = `ALL` ou `SELECTED` | `config.json`; `--group`/`--component` só **restringem** |

- **`ALL`** (padrão; também quando `selection` está ausente): todos os grupos documentáveis configurados em `metadataTypesConfig`, com todos os componentes encontrados na org. Não usa automaticamente a lista inteira de `sf org list metadata-types` (tipos sem grupo/contrato não são processados).
- **`SELECTED`**: somente os tipos principais listados em `metadataTypes`:

```json
"selection": {
  "mode": "SELECTED",
  "metadataTypes": {
    "Flow":                      { "components": "ALL" },
    "CustomObject":              { "components": ["Pedido__c"] },
    "CustomMetadata":            { "components": ["Config__mdt"] },
    "ExternalClientApplication": { "components": ["Minha_ECA"] }
  }
}
```

Regras (validadas **antes de qualquer chamada à org**):

- `selection` aceita só `mode` e `metadataTypes`; cada tipo aceita só `components`. Chave desconhecida é erro.
- `mode` é exatamente `"ALL"` ou `"SELECTED"`; em `ALL`, `metadataTypes` deve estar ausente ou vazio.
- Em `SELECTED`, `metadataTypes` é obrigatório e não vazio; tipo ausente não é processado.
- `components`: `"ALL"` (todos do tipo) ou lista não vazia de fullNames únicos. Lista vazia é erro (nunca significa "todos"); `"ALL"`/`"*"` dentro da lista é erro.
- Nomes com espaço no início/fim são rejeitados (não corrigidos). Chave JSON repetida (ex.: `"Flow"` duas vezes) é erro — o leitor JSON padrão manteria só a última.
- A chave é o **tipo principal** (`ExternalClientApplication`), não o nome do grupo (`ExternalClientApp`) — usar o nome do grupo gera erro indicando o tipo correto. Para Custom Metadata o componente é o tipo (`Config__mdt`).
- Tipos relacionados/filhos (`FlowDefinition`, `CustomField`, `RecordType`, `ValidationRule`, `WebLink`, `ExtlClntApp*`…) são **rejeitados** com o principal a selecionar; entram como dependência do principal.
- `--group`/`--component` fora da seleção é erro (antes de chamar a org). A chave antiga `scope` é rejeitada com instrução de migração.

Comportamento:

- Componentes fora da seleção **não são recuperados**. Dependências comprovadas do principal selecionado continuam: `FlowDefinition` de mesmo nome, filhos do objeto, records do `__mdt`, EC referenciada no XML da NC.
- Em `SELECTED`, relações que só se comprovam lendo o XML de **cada candidato** (`FIELD_EQUALS_PRIMARY`, `REFERENCE_SCAN` — ex.: `ExtlClntApp*` de uma ECA) **não recuperam candidatos**: as seções correspondentes mostram `Não informado`, a lacuna fica em `selection.relatedNotResolved` e a cobertura é `COMPLETE_WITH_WARNINGS`. Em `ALL` os candidatos são recuperados e o vínculo é verificado normalmente.
- Componente pedido e não encontrado (ou excluído pelo `componentFilter` do grupo) vira `NOT_FOUND` (`selection.notFound`) e a execução termina como `COMPLETED_WITH_GAPS` — nunca vira "todos os componentes".
- O run state registra `selection.requested` (formato do config.json), `selection.cli`, `selection.effective`, o alias e sua origem; grupos fora da seleção aparecem como `OUT_OF_SCOPE`. `bin/sf-docs.sh validate-config` mostra alias e seleção.

## Segurança e execução (Prioridade 3)

- **Org aprovada**: preencha `approvedOrgs` no `config.json` (o `run` informa o `orgId` detectado). Sem aprovação, nada é coletado (`ORG_NOT_APPROVED`).
- **Proteção de dados**: `dataProtection.privateFiles` (padrão `true`, arquivos `0600`), `dataProtection.orgDisplayRaw` (`KEEP_PRIVATE` | `DELETE_AFTER_RUN`).
- **Saída**: `execution.outputLayout` — `BY_DATE` (padrão: `saida/docs/doc-<alias>-MMDDAA/`, tudo o que for processado no dia para a org na mesma pasta, com manifesto e `_substituidos/`) ou `BY_RUN` (`saida/docs/doc-<alias>-MMDDAA/<runId>/`, cada execução isolada).
- **Uma pasta por org**: orgs diferentes nunca compartilham pasta. `.org.json` registra o `orgId` dono da pasta do dia; se o mesmo alias apontar para outra org no mesmo dia, os documentos vão para `doc-<alias>-<orgId>-MMDDAA/` e o log/`resumo.md` avisam.
- **Retomada em outro dia**: `execution.resumeOutput` — `ORIGINAL_FOLDER` (padrão: grava na pasta da coleta original, que fica completa) ou `TODAY` (grava na pasta do dia; os documentos herdados continuam na pasta original). `--resume-output` sobrepõe o `config.json` na execução. A `regenerate` segue a mesma regra. O log e o `resumo.md` indicam a pasta usada, quantos componentes foram processados em cada dia (`processedOn` no run state) e, se a execução de origem tiver mais de `execution.resumeWarnAfterDays` dias (padrão 1), recomendam uma execução completa nova.
- **Git**: `.gitignore` não é tratado como controle suficiente. `validate-config` e `run` verificam se há arquivo sensível **rastreado** (raw de `org display`, XMLs, normalizados, erros, `.crt`) — o `run` para antes de qualquer chamada à org (`SENSITIVE_FILES_TRACKED`) — e se os caminhos sensíveis estão de fato ignorados (`git check-ignore`). Fora de repositório Git a verificação fica registrada como indisponível.
- **Erros**: respostas de erro da CLI são gravadas como envelope `*.sanitized.json` (stdout/stderr mascarados), nunca como raw intacto.
- **Barreira final**: um documento que contenha o token ou valor de elemento sensível visto no XML (mesmo por outro campo) não é gravado (`FAILED`).
- **Cobertura**: `coverage` no run state e linha "Cobertura: COMPLETE/INCOMPLETE" no log.
- **Retomada**: só reaproveita o que for compatível (org, API, política, escopo, contratos/modelos); motivos em `resume.reprocessed`.
- Inventário de artefatos, sensibilidade e retenção: [`documentation/protecao-de-dados.md`](documentation/protecao-de-dados.md).
- Primeiro teste do MVP numa org real (fases com critério de passagem, premissas a confirmar, revisão de proteção de dados e modelo de relato): [`documentation/piloto-org-real.md`](documentation/piloto-org-real.md).

## Refatoração 3 — riscos de segurança, cobertura e execução

- **Raw (R1)**: raws e XMLs ficam intactos; proteção por `0600`, verificação de Git e retenção — nunca por reescrita do raw.
- **Org**: identidade obrigatória (`ORG_IDENTITY_UNVERIFIABLE`); fora de `approvedOrgs`, só continua em terminal se o usuário digitar o `orgId` exato (vale só para a execução); sem terminal/`--non-interactive`, para.
- **Token**: pedido só depois da aprovação; `ACCESS_TOKEN_UNAVAILABLE` antes de qualquer inventário.
- **Resumo**: `runs/<runId>/resumo.md` em toda execução; `progress` (planejadas/concluídas/pendentes), `errorClass` por componente e `metrics` por metadata type.
- **Retomada/regeneração**: fingerprint inclui `metadata-types-mvp.json` e o sha256 do XML de origem; `latest` ignora regenerações e descontinuadas; `regenerate` registra `regenerate.differences` e recusa XML ausente/alterado.
- **Retenção**: `purge` marca como DESCONTINUADA (não apaga); `--apply --delete-sensitive` apaga só artefatos sensíveis usados exclusivamente por execuções descontinuadas.
- **Erros**: exceção inesperada → run state `FAILED`/`UNEXPECTED_ERROR` mascarado; documentos gravados de forma atômica; erro de escrita falha só a unidade.

## Apex — Onda 01 (processamento assíncrono)

Adaptação de `_sf_utilities/ajudAI/contexto-apex.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Documento por classe** (`modelo-doc-apex-class`): `apiVersion`/`status` do `.cls-meta.xml` (fonte `XML`); sharing, modificadores, `extends`, interfaces, assinaturas e anotações dos métodos, chamadas assíncronas com argumentos literais e descrição ApexDoc (fonte `Código Apex`); dados internos do objeto `ApexClass` (`validationPending`).
- **Subdocumento por papel**, escolhido pela **interface/anotação**, nunca pelo nome: `implements Database.Batchable` → `modelo-doc-apex-batch`; `System.Queueable` → `modelo-doc-apex-queueable`; `System.Schedulable` → `modelo-doc-apex-scheduler`; cada método `@future` → `modelo-doc-apex-future`. Classe com vários papéis (ex.: Batch + Schedulable) gera um subdocumento por papel (`subDocuments.when` com `contains` e `forEach` em caminho pontuado).
- **Parser estrutural** (`src/salesforce_docs/parsing/apex_parser.py`): o `.cls` é raw e não é alterado; comentários e strings são neutralizados antes da análise (texto em comentário não vira evidência); Apex é tratado sem diferenciar maiúsculas; **o corpo dos métodos nunca é renderizado**; SOQL montado em tempo de execução e classe guardada em variável sem declaração local ficam "Não informado" (nunca inferidos).
- **Convenção de nomes** é configuração do time (bloco `naming_convention` no contrato, com `pattern`): o documento informa se o nome segue a convenção, mas o papel nunca é deduzido do nome.
- **Conteúdo genérico** (limites de governança, exemplos de invocação, monitoramento, boas práticas) não entra nos documentos por classe: está em [`documentation/referencia-apex-assincrono.md`](documentation/referencia-apex-assincrono.md), com links oficiais e o que ainda está a confirmar.
- **Próximas entregas**: índice entre classes ("invocado por", tamanho de lote e cron usados por outras classes) e dados internos de execução/agendamento (`AsyncApexJob`, `CronTrigger`) após o piloto.

## Apex Trigger — Onda 02

Adaptação de `_sf_utilities/ajudAI/contexto-apex-trigger.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Documento por trigger** (`modelo-doc-apex-trigger`): `apiVersion`/`status` do `.trigger-meta.xml` (fonte `XML`); objeto, eventos, variáveis de contexto `Trigger.*` usadas, classes chamadas, leituras de configuração e controles de segurança (fonte `Código Apex`); coexistência no objeto (fonte `Derivado`); dados internos do objeto `ApexTrigger` (`validationPending`); acesso via objeto e classes chamadas (fonte `XML`).
- **Parser** (`src/salesforce_docs/parsing/apex_trigger_parser.py`): mesmas regras do parser de classes (raw não alterado, comentários e strings neutralizados, corpo nunca renderizado). Classe chamada = `new X(`, `X.metodo(` ou variável local `X v`; o nome só é mantido se estiver no inventário de ApexClass (descarta sObjects e classes de sistema). Sem inventário, a linha fica "Não verificado".
- **Leituras de configuração** (trigger e classes chamadas): `FeatureManagement.checkPermission` (Custom Permission), `X__c.getInstance/getOrgDefaults/getValues/getAll` (Custom Setting) e `X__mdt.getInstance/getAll` ou SOQL em `__mdt` (Custom Metadata Type). O documento mostra a leitura; **não infere** que ela é um bypass. O parser de classes passou a registrar o mesmo (`configReads`, `securityPatterns`).
- **Coexistência e ordem de execução** (`automationIndex` em `config/metadata-types-mvp.json`): fases na ordem oficial (*Triggers and Order of Execution*): flow before-save → trigger before → regras de validação → trigger after → flow after-save. Fases de exclusão ficam com ordem "Não confirmado". Fontes: Flow (`start.object`, `start.triggerType`, `start.recordTriggerType`, `triggerOrder`), ApexTrigger (objeto e eventos do código) e ValidationRule (`active`). Só entram componentes processados na execução (ou herdados na retomada); a regeneração monta o índice depois de normalizar todas as unidades.
- **Acesso**: trigger não tem acesso próprio por perfil/permission set. A seção lista quem tem acesso ao objeto (`objectPermissions`) e às classes chamadas (`classAccesses`), com a via.
- **Conteúdo genérico** (variáveis de contexto, boas práticas, modo de execução por API version): [`documentation/referencia-apex-trigger.md`](documentation/referencia-apex-trigger.md).

## Lightning Web Components — Onda 03

Adaptação de `_sf_utilities/ajudAI/contexto-lwc.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Documento por componente** (`modelo-doc-lwc`): `masterLabel`, `apiVersion`, `isExposed`, `description`, targets (com o uso de cada um, descrito no contrato), propriedades e restrições de `targetConfigs` (fonte `XML`); arquivos do bundle, membros `@api`, hooks de ciclo de vida, métodos Apex importados (`@wire` ou imperativo), dados usados (LDS, `@salesforce/schema`, componentes base de formulário), comunicação (eventos, message channels, componentes filhos) e permissões importadas (fonte `Código LWC`); verificação dos métodos Apex no código das classes (fonte `Código Apex`); dados internos do objeto `LightningComponentBundle` (Tooling, `validationPending`).
- **Subdocumentos por target**, escolhidos pelo `.js-meta.xml`, nunca pelo nome: `lightning__RecordAction` → `modelo-doc-lwc-quick-action` (`actionType`, `@api invoke()` exigido em ação headless); `lightning__FlowScreen` → `modelo-doc-lwc-flow-screen` (propriedades com `role`, `@api validate()`, eventos de `lightning/flowSupport`). Página, utilitário e demais targets ficam no documento principal.
- **Parser do bundle** (`src/salesforce_docs/parsing/lwc_parser.py`, `sourceParser.bundle: true`): recebe todos os arquivos do componente; testes Jest (`__tests__/`) são ignorados; comentários e strings do JS e comentários do HTML não contam como evidência; o código nunca é renderizado. Lê os **atributos** do `.js-meta.xml` (`targetConfig targets=`, `property name/type/role`), que o normalizador XML genérico não guarda.
- **Verificação nas classes Apex**: para cada método importado, confere no código da classe processada na execução se ele é `static`, `public`/`global`, tem `@AuraEnabled` e, com `@wire`, `cacheable=true`. Classe fora do escopo: "Classe não processada nesta execução".
- **Acesso**: LWC não tem acesso próprio por perfil/permission set. A seção lista quem acessa as classes Apex chamadas (`classAccesses`, exigido para métodos `@AuraEnabled`) e quem tem as Custom Permissions importadas no JS (`customPermissions`, nova concessão em `accessSources.grants`).
- **Conteúdo genérico** (ciclo de vida, comunicação, LDS, APIs de plataforma): [`documentation/referencia-lwc.md`](documentation/referencia-lwc.md). Onde o componente é colocado: seções "Onde é usado (páginas Lightning)", a partir das FlexiPages processadas (Onda 04), e "Onde é usado (Experience Cloud)", a partir dos ExperienceBundles processados (Onda 09).

## Páginas Lightning (FlexiPage) — Onda 04

Adaptação de `_sf_utilities/ajudAI/contexto-flexipage.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Documento por página** (`modelo-doc-flexipage`): tipo, objeto, template, regiões (inclusive facets), componentes (com tipo pelo prefixo: `c:` do projeto, `flowruntime:interview` = Flow, plataforma, outros namespaces), campos de Dynamic Forms, propriedades dos componentes, regras de visibilidade (contexto Record/User/Permission/Client lido do critério), Flows embarcados — tudo do XML; dados internos do objeto `FlexiPage` (Tooling, `validationPending`).
- **Parser** (`src/salesforce_docs/parsing/flexipage_parser.py`, `sourceParser` `flexipage`): lê o próprio `.flexipage-meta.xml` e achata regiões → `itemInstances` → `componentInstance`/`fieldInstance`; aceita também o formato antigo (`componentInstances` direto na região).
- **Ativação** (última seção): padrão da org (`actionOverrides` do CustomObject processado), padrão do app e app + perfil/record type (`actionOverrides`/`profileActionOverrides` do CustomApplication, novo tipo do retrieve de acesso — `accessSources.pageAssignments`), e quem tem as Custom Permissions usadas na visibilidade. Página sem ativação nos componentes processados aparece como tal.
- **Onde é usado**: o documento do LWC ganhou a seção "Onde é usado (páginas Lightning)" (`recordIndex.pages`).
- **Conteúdo genérico** (templates, hierarquia de ativação, regras de visibilidade): [`documentation/referencia-flexipage.md`](documentation/referencia-flexipage.md).

## OmniStudio — Onda 10

Adaptação de `_sf_utilities/ajudAI/contexto-doc-industries-omni.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Formato lido:** o XML da Metadata API do OmniStudio padrão (`OmniDataTransform`, `OmniIntegrationProcedure`, `OmniScript`, `OmniUiCard`), recuperado como os demais tipos. Os `.json` do Vlocity Build Tool descritos no `ajudAI` (datapacks do pacote gerenciado) **não** são lidos.
- **DataRaptor** (`modelo-doc-omni-data-transform`): tipo, entrada/saída, itens de mapeamento (objeto/campo de entrada e saída, filtro, se há fórmula), objetos lidos e gravados, quem usa o DataRaptor e, na seção de acesso, quem tem permissão nesses objetos.
- **Integration Procedure** (`modelo-doc-omni-integration-procedure`) e **OmniScript** (`modelo-doc-omni-script`): elementos na ordem do XML (com nível e elemento pai) e os componentes que cada um referencia (DataRaptor, Integration Procedure, classe Apex, Named Credential). O Integration Procedure mostra também quem o chama (OmniScripts, FlexCards). Na seção de acesso, quem executa as classes Apex chamadas.
- **FlexCard** (`modelo-doc-omni-ui-card`): fonte de dados, ações e referências.
- **Segurança:** o texto de `propertySetConfig`, `dataSourceConfig` e `sampleDataSourceResponse` nunca vai para o Markdown (pode ter cabeçalhos HTTP, valores fixos e dados de exemplo): só os nomes dos componentes referenciados. Fórmulas do DataRaptor também não são reproduzidas.
- **Novidades genéricas:** índice `omniRefs` (`recordIndex.omni`) e builder `omni_usage_rows`.
- **Conteúdo genérico e o que não foi confirmado:** [`documentation/referencia-omnistudio.md`](documentation/referencia-omnistudio.md).

## Experience Cloud — Onda 09

Adaptação de `_sf_utilities/ajudAI/contexto-doc-experience-cloud.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Site do Experience Cloud** (`modelo-doc-network`): status, URL, autorregistro e perfil de autorregistro, templates de e-mail, o CustomSite do site e, na seção de acesso, os **membros** (perfis e permission sets de `networkMemberGroups`). O remetente de e-mail nunca é documentado: só se está configurado.
- **Site** (`modelo-doc-custom-site`): URL, tipo, configurações de segurança como estão no XML, a Network que usa o site e a **segurança do convidado**: perfil de convidado, permissões de objeto desse perfil (acesso além de Ler/Criar marcado para revisão) e regras de compartilhamento para convidado (`sharingGuestRules`). Administrador e dono padrão dos registros de convidado são usuários: só aparece se estão configurados.
- **Experience Builder** (`modelo-doc-experience-bundle`): pastas do bundle, páginas (views, layout, componentes por região), rotas com o acesso de cada página (ex.: `Public`, `RequiresLogin`) e referências de público/visibilidade como estão no JSON (fonte nova `JSON do ExperienceBundle`). Na seção de acesso, quem executa as classes Apex chamadas pelos LWC das páginas.
- **Onde é usado:** o documento do LWC ganhou a seção "Onde é usado (Experience Cloud)" (`recordIndex.pages.experience`). O documento de regras de compartilhamento ganhou "Regras para convidado (sites)".
- **Novidades genéricas:** builder `origin_grants_rows` (o que um perfil referenciado concede); `byPath.through` no `access_rows` (nomes levados por uma chave do índice da execução, ex.: LWC → classes Apex); `page_usage_rows.indexKey`.
- **Fora do escopo:** `DigitalExperienceBundle` (sites LWR aprimorados), Audiences como metadata e os critérios das audiências.
- **Conteúdo genérico e o que não foi confirmado:** [`documentation/referencia-experience-cloud.md`](documentation/referencia-experience-cloud.md).

## Sales Cloud — Onda 08

Adaptação de `_sf_utilities/ajudAI/contexto-doc-sales-cloud.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Processo de negócio** (`modelo-doc-business-process`): valores (em Opportunity, as etapas) e valor padrão, **record types que usam o processo** e, na seção de acesso, os perfis e permission sets que enxergam esses record types — a cadeia Processo → Record Type → Perfil.
- **Conversão de Lead** (`modelo-doc-lead-convert-settings`, documento único da org): configurações gerais, mapeamentos de objeto e de campos (de-para), quem tem `ConvertLeads` e o FLS dos campos mapeados.
- **Modelo de territórios** (`modelo-doc-territory2-model`): territórios (tipo, pai, níveis de acesso, regras associadas) e regras de atribuição (objeto, critérios). Usuários dos territórios nunca são documentados.
- **Tipo de divisão de oportunidade** (`modelo-doc-opportunity-split-type`): configuração como está no XML.
- **Novidades genéricas:**
  - relações `FIELD_EQUALS_PRIMARY_NAME` (campo do relacionado = nome do principal sem o objeto) e `NAME_PREFIX` (relacionados `<principal>.*`);
  - builder `leaf_properties` (folhas do XML como estão, para tipos com elementos não confirmados);
  - placeholders `{shortName}`/`{objectName}` nas consultas de dados internos.
- **Conteúdo genérico e o que não foi confirmado:** [`documentation/referencia-sales-cloud.md`](documentation/referencia-sales-cloud.md).

## Service Cloud — Onda 07

Sem `contexto-*.md` no `ajudAI` para esta onda: referência nos prompts de `_sf_utilities/tools/templates/exemplos-prompts/` (detalhados para AssignmentRules e EscalationRules).

- **Regras de atribuição, resposta automática e escalonamento** (`modelo-doc-assignment-rules`, `-auto-response-rules`, `-escalation-rules`, um por objeto): situação (quantas regras ativas), regras, entradas na ordem de avaliação (critério, lógica, destino, demais configurações) e, no escalonamento, ações; registros na org (`AssignmentRule`/`AutoResponseRule`/`EscalationRule`, `validationPending`).
- **Fila** (`modelo-doc-queue`): objetos aceitos, roteamento (`queueRoutingConfig`), regras que direcionam para a fila e membros (papéis, grupos) na seção de acesso.
- **Parsers** (`src/salesforce_docs/parsing/service_rules_parser.py`): leitura genérica do XML (nomes internos não confirmados); **usuário de destino, usuários notificados, membros usuários e e-mails nunca são documentados** — aparecem como texto fixo ou contagem; os elementos também entraram em `sensitiveXmlElements` (redigidos no normalizado).
- **Conteúdo genérico e o que ficou fora** (Omni-Channel, Entitlements, CaseSettings): [`documentation/referencia-service-cloud.md`](documentation/referencia-service-cloud.md).

## Objetos de evento — Onda 06

Adaptação de `_sf_utilities/ajudAI/contexto-platform-objects.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

- **Platform event** (`modelo-doc-platform-event`, um por objeto `__e`): identificação (`eventType`, `publishBehavior`...), campos do evento, **publicadores e assinantes** (Apex com `EventBus.publish` e `new X__e(`, triggers no evento, Flows disparados pelo evento ou que criam o evento, LWC com `lightning/empApi`), configuração da trigger assinante (`PlatformEventSubscriberConfig`: lote e se há usuário configurado — **o usuário nunca é documentado**) e permissões de objeto do evento.
- **Change Data Capture** (`modelo-doc-change-data-capture`, um por `PlatformEventChannelMember`): canal (padrão `ChangeEvents` ou customizado), evento selecionado, filtro, campos de enriquecimento, objeto de origem (convenção de nomes), assinantes e quem tem as permissões exigidas para assinar (Ver todos no objeto, View All Data, View All Users).
- **Índice de eventos** (`recordIndex.events`): quem publica e quem assina, a partir dos componentes processados na execução. Os parsers de Apex, trigger e LWC passaram a registrar `platformEvents` e `streamingChannels`.
- **Retrieve de acesso** (passo 6b) inclui `PlatformEventSubscriberConfig`; o índice de acesso ganhou `userPermissions` (permissões de sistema) e `subscriberConfigs`.
- **Conteúdo genérico** (retenção, replay, tipos de campo, cabeçalho do change event): [`documentation/referencia-eventos.md`](documentation/referencia-eventos.md).

## Segurança, acesso e governança — Onda 05

Adaptação de `_sf_utilities/ajudAI/contexto-seg-controle-acesso-gov.md` (ver a matriz em `documentation/refatoracao-1-matriz-ajudai.md`).

| Documento | Conteúdo | Fontes |
|---|---|---|
| `modelo-doc-org-security` (um por org) | Sessão (`sessionSettings`), senhas (`passwordPolicies`), faixas de IP confiáveis (`networkAccess`), OWD por objeto (`sharingModel`, `externalSharingModel` dos CustomObject processados), `Organization` (edição, sandbox, padrões de acesso de objetos padrão) | XML, Objeto interno |
| `modelo-doc-profile` | Licença, objetos, campos, classes, flows, páginas Visualforce, Custom Permissions, record types, layouts, guias, permissões de sistema, horário e faixas de IP de login | XML (passo 6b), Objeto interno |
| `modelo-doc-permission-set` (ampliado) | + Custom Permissions, páginas Visualforce, guias | XML (passo 6b) |
| `modelo-doc-permission-set-group` | Permission sets incluídos, muting permission sets, status | XML (passo 6b), Objeto interno |
| `modelo-doc-sharing-rules` (um por objeto) | Regras por critério e por proprietário (acesso, compartilhado com, critérios, registros de), OWD do objeto | XML (passo 6b) |
| `modelo-doc-role` | Níveis de acesso, papéis acima (cadeia de `parentRole`) e subordinados diretos, regras que compartilham com o papel | XML, Derivado |
| `modelo-doc-public-group` | `doesIncludeBosses`, regras que compartilham com o grupo | XML, Objeto interno |

- **Sem inventar nomes de campo:** sessão, senhas, horário de login e faixas de IP são renderizados como estão no XML (propriedade/valor), porque os nomes exatos não puderam ser confirmados na documentação oficial nesta adaptação.
- **Componente fixo** (`fixedComponents` no grupo): o documento da org não depende de listagem; recupera `Settings:Security`. No modo `ALL`, o retrieve de acesso usa o nome, nunca o tipo `Settings` inteiro.
- **Índice de registros** (`recordIndex` no config): campos copiados do XML de outros componentes (OWD do CustomObject, `parentRole` do Role) para os documentos da org, das regras e dos papéis. Só entram componentes processados na execução.
- **Proteção de dados:** usuários atribuídos a perfis, permission sets e grupos, e membros de grupos, não são documentados.
- **Conteúdo genérico** (modelo de compartilhamento, hierarquia, muting): [`documentation/referencia-seguranca-governanca.md`](documentation/referencia-seguranca-governanca.md).

## Refatoração 1 — modelos adaptados das referências `ajudAI`

A matriz de rastreabilidade, as divergências entre `ajudAI`, o utilitário e a documentação Salesforce, as decisões aplicadas e as pendências estão em [`documentation/refatoracao-1-matriz-ajudai.md`](documentation/refatoracao-1-matriz-ajudai.md). Cada contrato registra `referenceDoc`, `evidence` e o que ficou `notSupported`/`pendingVerification`.

## Como adicionar um metadata type

1. Adicionar o grupo em `config/metadata-types-mvp.json` (e `metadataTypeSettings` se a pasta/slug fugir do padrão kebab-case).
2. Criar o contrato `documentation/contracts/<tipo-kebab>.schema.json`:
   - `template`: nome do modelo (`{apiMajor}` é substituído pela API version);
   - `properties`: `name`, `placeholder`, `path` (`@fullName`, `@parent.fullName`, `internal:records`, `internal:first.Campo` ou caminho pontuado no XML normalizado), `source`, `required`, `markdownSection`;
   - `tables` / `blocks`: seção, `builder` (`related_components`, `related_rows`, `path_rows` — com filtro `where` —, `list_values`, `child_properties` — com lista `allow` —, `internal_record_properties`, `internal_rows`, `related_folders`, `related_properties_table` — com arquivo/sha256 de origem —, `flow_trigger_conditions`, `naming_convention`) e `source`;
   - `referenceDoc`: referência documental (ex.: arquivo `ajudAI`) citada no aviso de `NO_TEMPLATE`;
   - `internalData`: consulta SOQL opcional (`{developerName}`, `{fullName}`).
3. Criar o modelo em `documentation/models/api-v<N>/` (somente quando solicitado).
4. Criar parser/builder em `src/salesforce_docs/parsing/` **apenas se** os builders genéricos não bastarem. Arquivo-fonte não XML recuperado junto do metadata (ex.: `.cls`) é lido por um parser registrado em `parsing/source_parsers.py` e ligado em `metadataTypeSettings.<Tipo>.sourceParser` (`name`, `suffix`, `key`): o resultado entra no normalizado em `data.<key>`, com caminho e sha256 do arquivo em `source.code`/`source.codeSha256`.
   - Subdocumentos (`subDocuments`): `when` aceita `present`, `equals`, `in` e `contains` (lista que contém o valor, sem diferenciar maiúsculas); `forEach` aceita caminho pontuado.
5. `bin/sf-docs.sh validate-config [--strict]` (confere cada placeholder de cada modelo contra propriedades, blocos, colunas e builders do contrato, a fonte declarada e elementos bloqueados; blocos ausentes do modelo ou em seção divergente; propriedades do contrato que não aparecem no modelo — aviso, ou `intentionallyNotRendered`; contratos sem modelo próprio e sem uso — aviso, ou `renderedVia`; placeholders malformados; nome de modelo que tente sair de `documentation/models/api-vN/`. `--strict` transforma avisos em erro) e `python3 -m unittest discover -s tests -t .`.

## Estados

`SUCCESS`, `NO_TEMPLATE`, `NO_COMPONENTS`, `NOT_ENABLED`, `SCHEMA_UNAVAILABLE`, `RETRIEVE_FAILED`, `INTERNAL_DATA_UNAVAILABLE`, `RETRY_REQUIRED`, `MISMATCH` (+ `FAILED` para erro inesperado ou documento inválido; `OUT_OF_SCOPE` para grupo configurado mas fora do escopo; `NOT_FOUND` para componente pedido em `selection.metadataTypes` e ausente).

Status final da execução: `SUCCESS` (sem falhas e sem lacunas bloqueantes), `COMPLETED_WITH_GAPS` (sem falhas de componente, mas com modelo/contrato ausente, subdocumento sem modelo ou componente pedido não encontrado — **nunca** representa cobertura completa), `PARTIAL_SUCCESS` (algum componente falhou), `FAILED`, `INTERRUPTED`. Códigos de saída: `0` (SUCCESS, PARTIAL_SUCCESS, COMPLETED_WITH_GAPS), `1` falha global, `2` sessão expirada, `3` COMPLETED_WITH_GAPS quando `execution.strictCoverage = true`.

`coverage` no run state: `status` (`COMPLETE`, `COMPLETE_WITH_WARNINGS` — só avisos como dado interno ou schema indisponível —, `INCOMPLETE`), lacunas bloqueantes e avisos, e `coverage.types` com os metadata types **descobertos** na org (contagem e `discoveredNotConfigured`), **configurados**, **excluídos** (`byConfig`, `outOfScope`, `notEnabledInOrg`), **processados**, **documentados** (`documented`, `documentedAsRelated`) e **sem modelo** (`withoutModel`).

`NO_TEMPLATE` (contrato ou modelo ausente) nunca interrompe a execução: o aviso informa metadata type, componente, referência (`referenceDoc`), contrato e modelo esperados, os dados extraídos são preservados e as demais unidades continuam.

## Testes

```bash
python3 -m unittest discover -s tests -t .
```

Os testes usam uma Salesforce CLI **simulada** (`tests/fixtures/bin/sf`) e respostas SOAP simuladas. Nenhuma credencial real é usada.

### Simulação de todas as documentações do MVP

```bash
python3 -m unittest tests.test_mvp_simulation        # verifica os 46 modelos e os 46 metadata types
python3 -m tests.simulate_mvp --out /tmp/sim-mvp     # executa e gera o relatório passo a passo
```

O cenário `mvp_complete` da CLI simulada sobrepõe `tests/fixtures/mvp-complete/` às fixtures base, de modo que todo metadata type do MVP tenha ao menos um componente. O relatório versionado em `documentation/simulacao/relatorio-simulacao-mvp.md` mostra, para essa simulação, a saída no terminal, os comandos por passo, a situação de cada tipo, a árvore de arquivos e o conteúdo dos 73 documentos gerados.

| Grupo | Documento(s) / modelo | Tipos que aparecem dentro do documento |
|---|---|---|
| Flow | `modelo-doc-flow` + subdocumentos `modelo-doc-flow-trigger`, `modelo-doc-flow-autolaunched` e `modelo-doc-flow-screen` | FlowDefinition |
| ExternalClientApp | `modelo-doc-cea` | ExtlClntAppOauthSettings, ExtlClntAppConfigurablePolicies, ExtlClntAppOauthConfigurablePolicies |
| ExternalCredential | `modelo-doc-external-credential` | — |
| ConnectedApp | `modelo-doc-connectedapp` | — |
| NamedCredential | `modelo-doc-named-credential` | ExternalCredential (quando referenciada no XML da NC) |
| RemoteSiteSetting | `modelo-doc-remote-site-setting` | — |
| Certificate | `modelo-doc-certificate` | — |
| CustomObject | `modelo-doc-custom-object` | CustomField, RecordType, ValidationRule, WebLink |
| CustomMetadata | `modelo-doc-custom-metadata` | campos e records do tipo `__mdt` |
| PermissionSet | `modelo-doc-permission-set` | grupos que incluem o permission set |
| Profile | `modelo-doc-profile` | — |
| PermissionSetGroup | `modelo-doc-permission-set-group` | — |
| SharingRules | `modelo-doc-sharing-rules` | OWD do objeto (CustomObject processado) |
| Role | `modelo-doc-role` | hierarquia (outros papéis processados) e regras que compartilham com o papel |
| PublicGroup | `modelo-doc-public-group` | regras que compartilham com o grupo |
| OrgSecurity | `modelo-doc-org-security` | OWD dos CustomObject processados |
| ApexClass | `modelo-doc-apex-class` + subdocumentos `modelo-doc-apex-batch`, `modelo-doc-apex-queueable`, `modelo-doc-apex-scheduler` e `modelo-doc-apex-future` (um por método) | — |
| ApexTrigger | `modelo-doc-apex-trigger` | Flows record-triggered, regras de validação e outras triggers do mesmo objeto (coexistência) |
| LightningComponentBundle | `modelo-doc-lwc` + subdocumentos `modelo-doc-lwc-quick-action` e `modelo-doc-lwc-flow-screen` | — (métodos Apex conferidos nas classes processadas) |
| FlexiPage | `modelo-doc-flexipage` | ativação (CustomObject processado, CustomApplication do passo 6b); o LWC mostra as páginas que o usam |
| PlatformEvent | `modelo-doc-platform-event` | CustomField do evento; publicadores e assinantes processados |
| ChangeDataCapture | `modelo-doc-change-data-capture` | assinantes processados |
| AssignmentRules / AutoResponseRules / EscalationRules | `modelo-doc-assignment-rules`, `-auto-response-rules`, `-escalation-rules` | — |
| Queue | `modelo-doc-queue` | regras que direcionam para a fila |
| BusinessProcess | `modelo-doc-business-process` | RecordType que usam o processo |
| LeadConvertSettings | `modelo-doc-lead-convert-settings` | — |
| Territory2Model | `modelo-doc-territory2-model` | Territory2, Territory2Rule |
| OpportunitySplitType | `modelo-doc-opportunity-split-type` | — |
| Network | `modelo-doc-network` | CustomSite do site |
| CustomSite | `modelo-doc-custom-site` | Network que usa o site |
| ExperienceBundle | `modelo-doc-experience-bundle` | — |
| OmniDataTransform | `modelo-doc-omni-data-transform` | componentes que usam o DataRaptor |
| OmniIntegrationProcedure | `modelo-doc-omni-integration-procedure` | componentes referenciados e quem chama |
| OmniScript | `modelo-doc-omni-script` | componentes referenciados |
| OmniUiCard | `modelo-doc-omni-ui-card` | componentes referenciados |

## Estrutura

- `/catalog`: listagens, schemas e respostas brutas da org.
- `/inventory`: XML, dados normalizados, dados internos e estado por componente.
- `/documentation/models`: modelos Markdown por metadata type e API version.
- `/documentation/contracts`: contratos de propriedades e fontes.
- `/runs`: estado de execução, falhas e reprocessamento.
- `/saida/docs`: documentos Markdown finais.
- `/src/salesforce_docs`: o utilitário (único motor).
- `/bin/sf-docs.sh`: invólucro shell.

## Claude

`CLAUDE.md` e `.claude/skills/salesforce-docs-generator/SKILL.md` ficam versionados neste repositório.

O prompt enviado ao Claude não é versionado: ele instrui o Claude a ler e completar este repositório.
