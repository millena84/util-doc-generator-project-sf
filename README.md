# util-doc-generator-project-sf

Utilitário único para gerar documentação Markdown de componentes Salesforce, combinando dados da org, XMLs recuperados, objetos internos e modelos por metadata type.

## Requisitos

- Python **3.8+** — somente biblioteca padrão. **Nenhum `pip install`** é necessário.
- Salesforce CLI (`sf`) **2.0.0+** (mínima configurada em `config/config.json`).
- Bash (para o invólucro `bin/sf-docs.sh`; opcional — o módulo Python roda direto).
- Org autenticada: `sf org login web --alias dev`.

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

# Regerar derivados (index/schema/normalized) e Markdown SOMENTE a partir dos raws/XMLs
bin/sf-docs.sh regenerate --run latest

# Validar config, contratos e modelos (sem acessar a org)
bin/sf-docs.sh validate-config
```

Sem Bash (ex.: Windows): `PYTHONPATH=src python -m salesforce_docs run`.

Códigos de saída: `0` sucesso (inclui `PARTIAL_SUCCESS`), `1` falha global, `2` sessão expirada (estado salvo para retomada).

## Ordem de execução

| Passo | Ação | Raw | Derivado |
|---|---|---|---|
| 1 | `sf --version` ≥ mínima | — | — |
| 2 | `sf org list --json` contém o alias | não persistido (dado local da CLI, pode conter tokens) | — |
| 3 | `sf org display --target-org <alias> --json` | `catalog/org-<alias>/api-v<N>/org-display.raw.json` | — |
| 4 | `sf org list metadata-types` | `catalog/.../metadata-types.raw.json` | `metadata-types.index.json` |
| 5 | `describeValueType()` via Metadata API (SOAP, `urllib`) | `catalog/.../schemas/<tipo>.describevaluetype.raw.json` | `<tipo>.schema.json` |
| 6 | `sf org list metadata --metadata-type <tipo>` | `inventory/.../<pasta>/inventory.raw.json` | `inventory.index.json` |
| 7 | `sf project retrieve start --metadata <tipo>:<nome>` | `inventory/.../<pasta>/retrieve/<comp>.raw.json` + XML original em `components/` | — |
| 8 | XML → JSON | — | `inventory/.../<pasta>/normalized/<comp>.json` |
| 9 | `sf data query` (se o contrato prever) | `inventory/.../<pasta>/internal-data/<comp>.raw.json` | — |
| 10 | Modelo + contrato → Markdown | — | `saida/docs/doc-org-<MMDDAA>/doc-<comp>-<tipo>.md` |

Estado da execução: `runs/run-<AAAAMMDD-HHMMSS>.json`. Respostas de erro ficam em `runs/<runId>/errors/` (não sobrescrevem raws válidos).

## Decisões de implementação

- **Raw do `describeValueType`**: a Metadata API responde em XML (SOAP). O raw é um envelope JSON (`rawFormat: metadata-api-soap-capture/v1`) com `request` (endpoint, tipo, data — **sem token**) e `response.body` contendo o **XML exatamente como recebido**. O `.schema.json` é derivado desse corpo e pode ser regenerado.
- **Token**: lido em tempo de execução de `sf org display`, mantido só em memória, mascarado em logs/`repr`/`str`, não serializável (pickle/deepcopy) e descartado (`OrgSession.clear()`) ao fim de cada execução. O `org-display.raw.json` é salvo inalterado (regra do raw), com permissão `0600` e no `.gitignore`.
- **Retrieve**: roda em um projeto SFDX temporário; o XML é copiado byte a byte, preservando as pastas do formato source (ex.: `objects/Obj__c/fields/...`).
- **Valores ausentes**: `Não aplicável` quando o `describeValueType` comprova que o campo não existe no tipo; `Não informado` quando existe mas não veio no XML/dado interno.
- **Dados sensíveis**: elementos listados em `sensitiveXmlElements` (ex.: `consumerSecret`) nunca são renderizados e são substituídos por `[REDACTED]` no JSON normalizado (o XML original fica intacto); o run log avisa quando um XML recuperado os contém. `ExtlClntAppGlobalOauthSettings` é tipo excluído (contém consumer secret).
- **Valores sujeitos a decisão de segurança** (`omitFromDocumentation`: `consumerKey`, `callbackUrl`, `contactEmail/Phone`, `certificate`, `parameterValue`, permission sets/perfis, usuários de execução): nunca entram no Markdown. A linha é **omitida** (sem criar valor além de `Não informado`/`Não aplicável`) e o nome da propriedade fica em `omittedProperties` no run state. Valores (`<values>`) de records de Custom Metadata também não são renderizados.
- **`inventory/**/components/` e `inventory/**/normalized/` estão no `.gitignore`**: o raw é preservado em disco, mas pode conter valores sensíveis.
- **External Client App**: o nome correto do metadata type é `ExternalClientApplication` (Metadata API). O grupo continua chamado `ExternalClientApp`.

## Riscos conhecidos (tratar futuramente, se necessário)

Registro da auditoria de segurança de 2026-10-11 (10 riscos: 1 crítico, 2 altos, 5 médios, 2 baixos). Só o risco crítico foi detalhado e tratado até agora; os demais ainda precisam ser descritos aqui quando o relatório completo estiver disponível.

| # | Risco | Situação | Possível tratamento futuro |
|---|---|---|---|
| 1 | 🔴 `accessToken` mantido em memória durante a execução | **Mitigado**: mascarado em `repr`/`str`, serialização bloqueada, descartado em `finally` ao fim da execução; `MetadataApiClient` obtém o token da sessão a cada chamada (sem cópia própria). | Risco residual: Python não permite zerar uma `str` na memória; um dump do processo durante a execução ainda expõe o token. Aceitável para uso local. |
| 1a | 🔴 `accessToken` gravado em disco em `catalog/.../org-display.raw.json` (e em `runs/*/errors/`) | **Mitigado e configurável**: `.gitignore` + `0600`; `dataProtection.orgDisplayRaw = DELETE_AFTER_RUN` apaga o raw ao fim da execução (padrão `KEEP_PRIVATE` preserva a regra do raw). | Decisão registrada em `documentation/protecao-de-dados.md`. |
| P3 | Coleta em org errada; segredos em mensagens; sobrescrita silenciosa; retomada incompatível; cobertura não informada | **Tratados na Prioridade 3**: `approvedOrgs` (nada é coletado sem aprovação), máscara de valores secretos do XML e run state mascarado recursivamente, arquivos `0600`, manifesto/`_substituidos`/`BY_RUN`, fingerprint de retomada, `coverage`. | Ver `documentation/protecao-de-dados.md`. |
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

Cada componente (principal ou relacionado) é extraído e normalizado de forma independente; a agregação acontece apenas no documento.

## Escopo da execução (`config.json` → `scope`)

| Item | Onde | Precedência |
|---|---|---|
| Alias da org | `orgAlias` | `--target-org` > `config.json` (o `orgAlias` de `metadata-types-mvp.json` é só informativo; divergência gera aviso) |
| Diretórios | `paths` (`catalog`, `inventory`, `models`, `contracts`, `runs`, `outputDocs`, `metadataTypesConfig`) | `config.json` |
| O que documentar | `scope.mode` = `ALL` ou `SELECTED` | `config.json`; `--group`/`--component` só **restringem** |

- **`ALL`** (padrão): todos os grupos configurados em `metadataTypesConfig`, com todos os componentes que a org tiver. Não usa automaticamente a lista inteira de `sf org list metadata-types` (tipos sem grupo/contrato não são processados).
- **`SELECTED`**: somente os tipos principais e componentes listados:

```json
"scope": {
  "mode": "SELECTED",
  "selection": [
    { "metadataType": "Flow", "components": ["Meu_Flow", "Outro_Flow"] },
    { "metadataType": "CustomMetadata", "components": ["Config__mdt"] },
    { "metadataType": "RemoteSiteSetting", "components": ["*"] }
  ]
}
```

Regras:

- `metadataType` é o tipo **principal** de um grupo. Tipos relacionados/filhos (`FlowDefinition`, `CustomField`, `ExtlClntApp*`…) são rejeitados com a indicação do principal — eles entram como dependência do principal selecionado.
- `components` é obrigatório; `["*"]` = todos do tipo. Para Custom Metadata o componente é o tipo (`Config__mdt`).
- Configuração inválida ou ambígua (modo desconhecido, `selection` vazia ou com `ALL`, tipo repetido, componente vazio/repetido, `*` misturado com nomes, tipo desconhecido) é rejeitada **antes de qualquer chamada à org**.
- `--group`/`--component` fora do escopo do `config.json` é erro (antes de chamar a org).
- Componente pedido e não encontrado (ou excluído pelo `componentFilter` do grupo) vira `NOT_FOUND` explícito no run state (`scope.notFound`) e a execução termina como `PARTIAL_SUCCESS`.
- Componentes fora do escopo **não são recuperados**. Dependências do principal selecionado são: `FlowDefinition` de mesmo nome, filhos do objeto, records do `__mdt`, EC referenciada pela NC. Exceção documentada: para ligar `ExtlClntApp*` a uma ECA (`FIELD_EQUALS_PRIMARY`), os candidatos do tipo relacionado são recuperados para ler `externalClientApplication`; só os que apontam para a ECA selecionada entram no documento.
- O run state registra o escopo pedido (`scope.requested`, `scope.cli`), o efetivo (`scope.effective`), o alias e sua origem; grupos fora do escopo aparecem como `OUT_OF_SCOPE`.
- `bin/sf-docs.sh validate-config` mostra alias e escopo efetivo.

## Segurança e execução (Prioridade 3)

- **Org aprovada**: preencha `approvedOrgs` no `config.json` (o `run` informa o `orgId` detectado). Sem aprovação, nada é coletado (`ORG_NOT_APPROVED`).
- **Proteção de dados**: `dataProtection.privateFiles` (padrão `true`, arquivos `0600`), `dataProtection.orgDisplayRaw` (`KEEP_PRIVATE` | `DELETE_AFTER_RUN`).
- **Saída**: `execution.outputLayout` (`BY_DATE` com manifesto e `_substituidos/`, ou `BY_RUN`).
- **Cobertura**: `coverage` no run state e linha "Cobertura: COMPLETE/INCOMPLETE" no log.
- **Retomada**: só reaproveita o que for compatível (org, API, política, escopo, contratos/modelos); motivos em `resume.reprocessed`.
- Inventário de artefatos, sensibilidade e retenção: [`documentation/protecao-de-dados.md`](documentation/protecao-de-dados.md).

## Refatoração 1 — modelos adaptados das referências `ajudAI`

A matriz de rastreabilidade, as divergências entre `ajudAI`, o utilitário e a documentação Salesforce, as decisões aplicadas e as pendências estão em [`documentation/refatoracao-1-matriz-ajudai.md`](documentation/refatoracao-1-matriz-ajudai.md). Cada contrato registra `referenceDoc`, `evidence` e o que ficou `notSupported`/`pendingVerification`.

## Como adicionar um metadata type

1. Adicionar o grupo em `config/metadata-types-mvp.json` (e `metadataTypeSettings` se a pasta/slug fugir do padrão kebab-case).
2. Criar o contrato `documentation/contracts/<tipo-kebab>.schema.json`:
   - `template`: nome do modelo (`{apiMajor}` é substituído pela API version);
   - `properties`: `name`, `placeholder`, `path` (`@fullName`, `@parent.fullName`, `internal:records`, `internal:first.Campo` ou caminho pontuado no XML normalizado), `source`, `required`, `markdownSection`;
   - `tables` / `blocks`: seção, `builder` (`related_components`, `related_rows`, `path_rows` — com filtro `where` —, `child_properties` — com lista `allow` —, `internal_record_properties`, `related_folders`, `related_properties_table` — com arquivo/sha256 de origem —, `flow_trigger_conditions`) e `source`;
   - `referenceDoc`: referência documental (ex.: arquivo `ajudAI`) citada no aviso de `NO_TEMPLATE`;
   - `internalData`: consulta SOQL opcional (`{developerName}`, `{fullName}`).
3. Criar o modelo em `documentation/models/api-v<N>/` (somente quando solicitado).
4. Criar parser/builder em `src/salesforce_docs/parsing/` **apenas se** os builders genéricos não bastarem.
5. `bin/sf-docs.sh validate-config` (confere cada placeholder de cada modelo contra propriedades, blocos, colunas e builders do contrato, a fonte declarada e elementos bloqueados) e `python3 -m unittest discover -s tests -t .`.

## Estados

`SUCCESS`, `NO_TEMPLATE`, `NO_COMPONENTS`, `NOT_ENABLED`, `SCHEMA_UNAVAILABLE`, `RETRIEVE_FAILED`, `INTERNAL_DATA_UNAVAILABLE`, `RETRY_REQUIRED`, `MISMATCH` (+ `FAILED` para erro inesperado ou documento inválido; `OUT_OF_SCOPE` para grupo configurado mas fora do escopo; `NOT_FOUND` para componente pedido em `scope.selection` e ausente).

`NO_TEMPLATE` (contrato ou modelo ausente) nunca interrompe a execução: o aviso informa metadata type, componente, referência (`referenceDoc`), contrato e modelo esperados, os dados extraídos são preservados e as demais unidades continuam.

## Testes

```bash
python3 -m unittest discover -s tests -t .
```

Os testes usam uma Salesforce CLI **simulada** (`tests/fixtures/bin/sf`) e respostas SOAP simuladas. Nenhuma credencial real é usada.

### Simulação de todas as documentações do MVP

```bash
python3 -m unittest tests.test_mvp_simulation        # verifica os 12 modelos e os 17 metadata types
python3 -m tests.simulate_mvp --out /tmp/sim-mvp     # executa e gera o relatório passo a passo
```

O cenário `mvp_complete` da CLI simulada sobrepõe `tests/fixtures/mvp-complete/` às fixtures base, de modo que todo metadata type do MVP tenha ao menos um componente. O relatório versionado em `documentation/simulacao/relatorio-simulacao-mvp.md` mostra, para essa simulação, a saída no terminal, os comandos por passo, a situação de cada tipo, a árvore de arquivos e o conteúdo dos 15 documentos gerados.

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
