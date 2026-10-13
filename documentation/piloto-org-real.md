# Primeiro teste do MVP em org real (roteiro do piloto)

Os testes automatizados usam uma Salesforce CLI **simulada**: provam o pipeline, não a org. Este roteiro conduz o **primeiro teste numa org real**, em fases curtas. Cada fase tem um critério de passagem. Ele responde a três perguntas:

1. O utilitário roda de ponta a ponta na org e produz documentos utilizáveis?
2. As premissas marcadas *a confirmar* (nomes de elemento, consultas, formatos da CLI) valem na org?
3. Nada que não deveria (token, segredo, usuário, e-mail, dado de exemplo) aparece nos documentos?

> **Segurança:** use uma org de desenvolvimento ou sandbox com autorização do responsável. Nenhum comando abaixo imprime o access token. Ao relatar, **não cole** tokens, senhas, `consumerSecret`, o conteúdo de `inventory/**/components/`, usuários, e-mails, `propertySetConfig` nem dados de registros.

Convenções: troque `dev` pelo alias da org e `<Nome>` pelo nome de API de um componente real. Os comandos rodam na raiz do utilitário. Os caminhos de saída usam `inventory/org-<alias>/api-v<N>/`; ajuste e defina uma vez por sessão:

```bash
INV=inventory/org-dev/api-v67
```

## Escopo do MVP

O que está configurado em `config/metadata-types-mvp.json`: 37 grupos e 46 modelos. Os grupos de **Profile, PermissionSet, PermissionSetGroup, SharingRules e Queue** usam o XML do retrieve de acesso (passo 6b). **SecuritySettings** e **LeadConvertSettings** são componentes fixos, sem listagem.

| Fase do roteiro | Grupos | Origem |
|---|---|---|
| C0 — base | Flow, ExternalClientApp, ExternalCredential, ConnectedApp, CustomObject, CustomMetadata, NamedCredential, RemoteSiteSetting, Certificate | MVP original |
| C1 | ApexClass | Onda 01 |
| C2 | ApexTrigger | Onda 02 |
| C3 | LightningComponentBundle | Onda 03 |
| C4 | FlexiPage | Onda 04 |
| C5 | OrgSecurity, Profile, PermissionSet, PermissionSetGroup, SharingRules, Role, PublicGroup | Onda 05 |
| C6 | PlatformEvent, ChangeDataCapture | Onda 06 |
| C7 | AssignmentRules, AutoResponseRules, EscalationRules, Queue | Onda 07 |
| C8 | BusinessProcess, LeadConvertSettings, Territory2Model, OpportunitySplitType | Onda 08 |
| C9 | Network, CustomSite, ExperienceBundle | Onda 09 |
| C10 | OmniDataTransform, OmniIntegrationProcedure, OmniScript, OmniUiCard | Onda 10 |

Tipos da org sem grupo configurado **não** são documentados. O `resumo.md` lista esses tipos em "Descobertos e não configurados".

## 0. Antes de começar

- [ ] Autorização escrita do responsável pela org e pelos dados; org de desenvolvimento ou sandbox.
- [ ] Commit aprovado do utilitário (registre o hash: `git rev-parse --short HEAD`).
- [ ] Python ≥ 3.8 e Salesforce CLI ≥ 2.0.0 (registre `python3 --version` e `sf --version`).
- [ ] Usuário da org com *View Setup and Configuration* e permissão de retrieve (Modify Metadata ou equivalente aprovado). Registre o perfil usado.
- [ ] Pasta de trabalho em armazenamento aprovado e com acesso restrito. `catalog/`, `inventory/`, `runs/` e `saida/` nunca vão para o Git nem para artifacts (ver `protecao-de-dados.md`).
- [ ] Combinado quem revisa os documentos e quando os dados locais serão removidos (seção 10).

## 1. Validação sem org

```bash
bin/sf-docs.sh validate-config --strict
python3 -m unittest discover -s tests -t .
```

**Passa se:** "Configuração válida." e todos os testes `OK`. Qualquer falha aqui encerra o piloto: o problema é do utilitário, não da org.

## 2. Conectar e aprovar a org

```bash
sf org login web --alias dev
```

**2.1 `connectedStatus` (DA-10).** Repita para cada forma de login usada (web, JWT, scratch org):

```bash
sf org display --target-org dev --json | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; print(r.get('connectedStatus'), '| chaves:', sorted(r))"
```

- **Esperado:** `Connected`. Outro valor ou ausência faz a execução parar com `ORG_DISPLAY_INCOMPLETE`/`ORG_NOT_CONNECTED`. Relate o valor.

**2.2 Formato do comando de token (DA-14).** Mostra só a **estrutura** da resposta:

```bash
sf org auth show-access-token --target-org dev --json | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('result'); print('status:', d.get('status'), '| result:', type(r).__name__, sorted(r) if isinstance(r, dict) else '(texto)')"
```

- **Esperado:** `status: 0 | result: dict ['accessToken', ...]` ou `result: str (texto)`; o utilitário aceita os dois. Outra estrutura: relate a lista de chaves.

**2.3 Aprovar a org.** A primeira execução para em `ORG_NOT_APPROVED` antes de qualquer inventário ou retrieve, e mostra `orgId`, alias, usuário e instance URL:

```bash
bin/sf-docs.sh run --group RemoteSiteSetting --non-interactive
```

Confira se é a org pretendida e registre-a em `config/config.json`:

```json
"approvedOrgs": [ { "orgId": "00D...", "alias": "dev", "note": "piloto MVP - sandbox X" } ]
```

**Passa se:** a org aparece corretamente e, depois do registro, a execução segue.

## 3. Fase A — execução mínima

Um grupo pequeno, sem relacionados nem dados internos, para provar o caminho principal (inventário, retrieve, normalização, retrieve de acesso, Markdown):

```bash
bin/sf-docs.sh run --group RemoteSiteSetting --non-interactive
```

Abra `runs/<runId>/resumo.md` (o `runId` aparece no fim do log) e confira:

- [ ] **Status** `SUCCESS` ou `PARTIAL_SUCCESS` com motivo claro; **Cobertura** e "Com falha (0)".
- [ ] **Org-alvo** e **Aprovação** corretas; "Token obtido via" diz que o token nunca é persistido.
- [ ] Documento em `saida/docs/doc-dev-MMDDAA/` com toda linha de tabela terminando numa fonte (`XML`, `Objeto interno`...).
- [ ] Raws gravados: `$INV/remote-site-settings/inventory.raw.json` e `retrieve/*.raw.json`.
- [ ] Revisão de proteção de dados da seção 7 sem achados.

Para ver o que o retrieve trouxe sem abrir os XMLs (vale para qualquer fase; troque a pasta e o arquivo):

```bash
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(sorted((f['type'], f['fullName'], f['filePath'].split('/main/default/',1)[-1]) for f in d['result'].get('files', [])))" $INV/remote-site-settings/retrieve/<nome>.raw.json
```

**Passa se:** todos os itens acima estão OK. Sem a Fase A, não siga.

## 4. Fase B — acesso e configuração (passo 6b)

É a premissa de maior impacto: toda seção "Acesso e configuração" depende de o XML de Profile e PermissionSet trazer as permissões **dos componentes recuperados no mesmo pedido**.

```bash
bin/sf-docs.sh run --group ApexClass --component <Classe> --non-interactive
```

- [ ] `$INV/access/components/profiles/*.profile-meta.xml` contém `<classAccesses>` da classe.
- [ ] O documento da classe termina com "Acesso e configuração" listando os perfis e permission sets que liberam a classe no Setup. **Compare com o Setup** (perfil → Acesso a classes Apex). Perfil que libera e não aparece = falha. Relate o perfil e só o trecho `<classAccesses>`.
- [ ] Elementos não vazios quando deveriam ter valor: `objectPermissions`, `fieldPermissions`, `recordTypeVisibilities`, `customPermissions` (`name`/`enabled`), `userPermissions`, `PermissionSetGroup.permissionSets`, `SharingRules.sharedTo` e o formato de `externalCredentialPrincipal` (`<ExternalCredential>-<Principal>`).
- [ ] **Volume:** anote o tempo do passo 6b no log e o tamanho de `$INV/access/` (`du -sh`). O retrieve de acesso traz **todos** os Profile, PermissionSet, PermissionSetGroup, Queue, SharingRules, CustomApplication e PlatformEventSubscriberConfig da org a cada execução.

**Passa se:** as concessões batem com o Setup para a classe escolhida.

## 5. Fase C — confirmação por grupo

Rode uma fase por vez, com **poucos componentes** (`--component`), e só avance quando a anterior passar. Em cada fase:

- **Rodar:** o comando indicado.
- **Conferir:** o documento contra o Setup e o `resumo.md`: "Com falha", "Dados internos indisponíveis" e "Relacionados não verificados".
- **Confirmar premissas:** os itens *a confirmar*. Se uma consulta de dados interno falhar, o Apêndice A tem a consulta para repetir à mão.
- **Classificar:** OK, falha do utilitário (relatar) ou premissa errada (relatar o nome/formato real).

### C0 — Tipos da base do MVP

```bash
bin/sf-docs.sh run --group Flow --group CustomObject --group CustomMetadata --component <Flow> --component <Objeto__c> --component <Tipo__mdt> --non-interactive
bin/sf-docs.sh run --group ExternalClientApp --group ExternalCredential --group NamedCredential --group ConnectedApp --group RemoteSiteSetting --group Certificate --non-interactive
```

- **Flow:** versões e status batem com o Setup; o `FlowDefinition` relacionado aparece.
- **Objeto e CMDT:** campos, record types e regras de validação do objeto. Componentes de pacote (`ns__`) são excluídos por `componentFilter`; confira o "Ignorados por componentFilter" no resumo.
- **Integrações:** nenhum segredo (`consumerSecret`, chave privada, certificado, `parameterValue`) aparece; os avisos "elementos sensíveis... omitidos do Markdown" no log são esperados.
- **Connected App (DA-13):** veja o Apêndice C.
- **Namespace (DA-05):** veja o Apêndice B.

### C1 — Apex (Onda 01)

```bash
bin/sf-docs.sh run --group ApexClass --component <Classe> --component <ClasseBatch> --non-interactive
```

- `$INV/apex-classes/components/classes/` tem `<Classe>.cls` e `.cls-meta.xml`; o documento traz interfaces e métodos.
- **Papéis assíncronos:** o subdocumento esperado foi gerado (`-apex-batch`, `-apex-queueable`, `-apex-scheduler`, `-apex-future`). Papel não detectado: relate só a linha `class ... implements ...`.
- **Consulta:** `IsValid` e `LengthWithoutComments` existem em `ApexClass`? (`INVALID_FIELD` = o campo sai do contrato.)

### C2 — Apex Trigger (Onda 02)

```bash
bin/sf-docs.sh run --group ApexTrigger --group Flow --group CustomObject --group ApexClass --non-interactive
```

- **Coexistência:** compare "Coexistência no objeto e ordem de execução" com o Object Manager (Triggers) e o Flow Trigger Explorer. Flow record-triggered ausente = falha (relate `start.triggerType` e `start.object`). `triggerOrder` vem no XML do Flow?
- **Classes chamadas:** classe ausente, ou nome que não é classe e aparece = falha; relate só a linha da chamada.
- **Consulta:** `TableEnumOrId`, `IsValid` e `Usage*` existem em `ApexTrigger`?
- **Modo de acesso:** confirme na página *Apex Versioned Behavior Changes* se o user mode padrão da API 67.0 vale para triggers.

### C3 — Lightning Web Components (Onda 03)

```bash
bin/sf-docs.sh run --group LightningComponentBundle --group ApexClass --component <componente> --non-interactive
```

- `$INV/lwc/components/lwc/<componente>/` tem `.js`, `.html` e `.js-meta.xml`; todos os arquivos do bundle vêm com o `fullName` do componente no raw do retrieve?
- Targets e `targetConfigs` iguais ao `.js-meta.xml`; métodos Apex chamados e a verificação `@AuraEnabled`.
- A permissão importada aparece em perfil/permission set no formato `<customPermissions><enabled>`/`<name>`?

### C4 — Páginas Lightning (Onda 04)

```bash
bin/sf-docs.sh run --group FlexiPage --group CustomObject --group LightningComponentBundle --non-interactive
```

- Regiões e componentes iguais ao Lightning App Builder.
- **Ativação:** compare "Acesso e configuração" com o botão *Activation*. Confira no XML do app (`$INV/access/components/applications/`) o formato de `profileActionOverrides` (`profile`, `recordType`, `formFactor`) e, no objeto, `actionOverrides` de View com `type` Flexipage.
- **Visibilidade:** relate o formato real de `leftValue` (ex.: `{!Record.Campo__c}`).

### C5 — Segurança e governança (Onda 05)

```bash
bin/sf-docs.sh run --group OrgSecurity --group CustomObject --group Profile --group Role --group PublicGroup --group SharingRules --group PermissionSetGroup --non-interactive
```

- **Settings:** o raw `$INV/org-security/retrieve/*.raw.json` traz `type: Settings` e `fullName: Security`? Se vier outro tipo, ajuste `fixedComponents.retrieveType`. Se `SecuritySettings` não aparecer em `sf org list metadata-types` (só `Settings`), o grupo fica `NOT_ENABLED`: relate.
- **Perfis padrão:** o filtro de dados internos usa o fullName do metadata (`Admin`), mas o `Name` é "System Administrator". Relate o par fullName/Name.
- **Confira** `sessionSettings`, `passwordPolicies` e `networkAccess` contra o Setup; `parentRole` e níveis de acesso do Role; `doesIncludeBosses` do Group; `mutingPermissionSets` do PSG.

### C6 — Objetos de evento (Onda 06)

```bash
bin/sf-docs.sh run --group PlatformEvent --group ChangeDataCapture --group ApexTrigger --group ApexClass --group Flow --non-interactive
```

- **Platform event:** o retrieve de `CustomObject:<Evento>__e` traz os campos? `eventType` e `publishBehavior` batem com o Setup?
- **CDC:** a seleção do Setup aparece como `PlatformEventChannelMember` no canal `ChangeEvents`? Relate o formato do fullName dos membros e o nome do change event de objeto customizado (`X__ChangeEvent`).
- **PlatformEventSubscriberConfig:** `platformEventConsumer`, `batchSize` e `user` no XML. O valor de `user` nunca vai para o documento; **não cole**.
- **Permissões:** nomes de API `ViewAllData` e `ViewAllUsers` no XML de perfil.

### C7 — Service Cloud (Onda 07)

```bash
bin/sf-docs.sh run --group AssignmentRules --group AutoResponseRules --group EscalationRules --group Queue --non-interactive
```

- Ordem das entradas, critérios e destinos iguais ao Setup. Elemento que só aparece em "Outras configurações" = nome real diferente do esperado; relate.
- **Tooling:** `AutoResponseRule`/`EscalationRule` existem como objetos? O filtro `SobjectType` funciona?
- **Fila:** contêineres de `queueMembers` (papéis, grupos) e se `queueRoutingConfig` vem no XML.

### C8 — Sales Cloud (Onda 08)

```bash
bin/sf-docs.sh run --group BusinessProcess --group LeadConvertSettings --group Territory2Model --group OpportunitySplitType --non-interactive
```

- **Processo de vendas:** o `<businessProcess>` do RecordType traz só o nome do processo (sem o objeto)? Os record types listados batem com o Setup?
- **LeadConvertSettings:** o raw `$INV/lead-convert-settings/retrieve/*.raw.json` traz o componente com `fullName` `LeadConvertSettings`? Nomes de `objectMapping`/`mappingFields`; relate se os pares não aparecerem na tabela de-para.
- **Territórios:** fullName `Modelo.Territorio` e `Modelo.Regra`? Elementos de nível de acesso e `ruleAssociations`.
- **Permissões:** nomes de API `ConvertLeads`, `ManageTerritories`, `ManageOpportunitySplits` nos XMLs de perfil.
- **Split type:** elemento real do "total deve somar 100%" (`isTotalValidated`?).

### C9 — Experience Cloud (Onda 09)

```bash
bin/sf-docs.sh run --group Network --group CustomSite --group ExperienceBundle --group LightningComponentBundle --group SharingRules --non-interactive
```

- **Network:** membros em `networkMemberGroups/profile` e `permissionSet`? O site é o elemento `<site>`? Existe `<label>`? Nome dos elementos de remetente (`emailSenderAddress`?).
- **CustomSite:** existe `<guestProfile>`? O nome do perfil de convidado bate com o Setup?
- **Regras para convidado:** `sharingGuestRules` com `sharedTo/guestUser`: qual é o valor (nome do site)? O documento do site lista a regra?
- **ExperienceBundle:** liste as pastas do bundle pelo raw `$INV/experiences/retrieve/*.raw.json` (comando da Fase A). Campos `pageAccess`, `urlPrefix` e `activeViewId` das rotas; como a audiência aparece nos componentes das views. Site LWR aprimorado (`DigitalExperienceBundle`) não é coberto: relate se for o caso.

### C10 — OmniStudio (Onda 10)

```bash
sf org list metadata-types --target-org dev --json | python3 -c "import json,sys; print(sorted(t['xmlName'] for t in json.load(sys.stdin)['result']['metadataObjects'] if t['xmlName'].startswith('Omni')))"
bin/sf-docs.sh run --group OmniDataTransform --group OmniIntegrationProcedure --group OmniScript --group OmniUiCard --non-interactive
```

- **Formato:** a org usa o OmniStudio padrão (os quatro tipos `Omni*` aparecem no primeiro comando) ou o pacote gerenciado Vlocity (datapacks, fora do escopo)? Sem os tipos, os grupos ficam `NOT_ENABLED`.
- **Nomes:** formato do fullName (`Type_SubType_Language_Version`?); sufixos `.rpt`, `.oip`, `.os`, `.ouc` no raw do retrieve; elementos `omniProcessElements`/`childElements` e `omniDataTransformItem` (`inputObjectName`, `outputFieldName`...).
- **Referências:** as chaves `bundle`, `integrationProcedureKey`, `ipMethod`, `remoteClass`, `namedCredential` existem no `propertySetConfig`? Como um FlexCard lança um OmniScript?
- **Segurança do DataRaptor:** qual elemento corresponde a "verificar FLS" / "ignorar segurança"?

**Passa se** (para cada fase C): nenhum componente em "Com falha" sem causa entendida, e os documentos batem com o Setup nos pontos conferidos. Premissa errada não reprova a fase: vira ajuste de contrato, que é o objetivo do piloto.

## 6. Execução completa

Só depois das fases A, B e C. Use `selection.mode = "ALL"` ou uma `SELECTED` aprovada (ver `guia-instalacao-e-uso.md`, seção 4):

```bash
bin/sf-docs.sh run --non-interactive
```

- [ ] Anote o tempo total, o número de chamadas e os segundos por tipo (tabela "Chamadas à CLI" do resumo) e o tamanho de `inventory/` e `saida/`.
- [ ] Interrupção (sessão expirada, timeout): retome com `bin/sf-docs.sh run --resume latest` e confira se nenhum componente `SUCCESS` foi reprocessado.
- [ ] Rode `bin/sf-docs.sh regenerate --run latest`: os documentos devem ser regenerados sem nenhuma chamada à org.

## 7. Revisão de proteção de dados (obrigatória em toda fase)

Os comandos abaixo só **contam** ocorrências por arquivo; não imprimem o conteúdo.

```bash
# e-mails nos documentos
grep -rIlE "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" saida/docs | head
# marcadores de credencial nos documentos e no estado da execução
grep -rIicE "bearer |access_token|refresh_token|client_secret|BEGIN [A-Z ]*PRIVATE KEY" saida/docs runs | grep -v ":0$" | head
# texto de configuração do OmniStudio nunca deve chegar ao Markdown
grep -rIlE "propertySetConfig|dataSourceConfig|sampleDataSourceResponse" saida/docs | head
```

- **Esperado:** nenhuma saída nos três comandos. Não procure por `password`: o documento de segurança da org mostra a política de senhas (`passwordPolicies`) de propósito. O `runs/` guarda o **usuário da execução** (seção "Org-alvo" do resumo), por isso fica fora da busca de e-mails.
- Qualquer outro achado **para o piloto**: não compartilhe os arquivos, relate só o caminho e o tipo do achado.
- Nunca documentados, por desenho: usuários (filas, regras, territórios, site, subscriber config), e-mails e remetentes, segredos de integração, corpo de código, configuração interna do OmniStudio e dados de exemplo do FlexCard.

## 8. Critérios de aprovação e de parada

| Situação | Decisão |
|---|---|
| Seção 1, 2 ou Fase A falha | **Parar.** Corrigir o utilitário ou o ambiente antes de continuar |
| Achado na revisão de proteção de dados (seção 7) | **Parar** e tratar como incidente de dados conforme a política local |
| Fase B: concessões diferentes do Setup | **Parar** as fases C; todas as seções de acesso dependem dela |
| Fase C: premissa *a confirmar* diferente na org | Seguir; registrar para ajuste de contrato/parser |
| Fase C: componente `FAILED` sem causa entendida | Seguir com as outras fases; relatar com o erro do `resumo.md` |
| Execução completa inviável em tempo/volume | Aprovar com escopo `SELECTED`; registrar a limitação |

O MVP é **aprovado no piloto** quando: seções 1–4 passam, toda fase C executada tem os pontos conferidos OK ou com ajuste registrado, a seção 7 não tem achados e o responsável pela org aceita o resultado.

## 9. Como relatar

Um registro por item, sem dados da org:

| Campo | Exemplo |
|---|---|
| Item | `C8 — LeadConvertSettings` |
| Commit / versões | `44475ba`, `sf 2.x`, Python 3.x, login web |
| Comando | `bin/sf-docs.sh run --group LeadConvertSettings --non-interactive` |
| Resultado | `SUCCESS`; 1 documento; tabela de-para vazia |
| Premissa | `objectMapping` → nome real `<...>` (só o nome do elemento) |
| Decisão | ajustar parser `lead-convert` |

Não inclua token, senha, `consumerSecret`, usuários, e-mails, conteúdo de XML/JSON recuperado ou dados de registros.

## 10. Limpeza

Ao fim do piloto, conforme a retenção combinada (seção 0):

```bash
bin/sf-docs.sh purge --older-than-days 0                              # lista o que seria marcado
bin/sf-docs.sh purge --older-than-days 0 --apply --delete-sensitive   # marca e apaga os artefatos sensíveis
```

Remova também, se combinado, `saida/` e a autorização da CLI (`sf org logout --target-org dev`).

## Apêndice A — consultas de dados internos

O utilitário roda estas consultas sozinho no `run`; falha não para a execução (a seção fica "Não informado" e o componente aparece em "Dados internos indisponíveis"). Para investigar uma falha, repita a consulta à mão com um componente real (Tooling: acrescente `--use-tooling-api`):

```bash
sf data query --target-org dev --json --query "<consulta com os placeholders preenchidos>" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), (d.get('result') or {}).get('totalSize'), d.get('name'), d.get('message'))"
```

- **Esperado:** `0 1` (no Flow, o número de versões).
- **`INVALID_FIELD`/`INVALID_TYPE`:** campo ou objeto não existe na org/API. Relate a mensagem; o contrato é ajustado.
- **Erro de permissão:** relate o perfil usado (ex.: falta *View Setup and Configuration*).

Placeholders: `{fullName}` = nome do metadata; `{developerName}` = nome sem namespace; `{objectName}`/`{shortName}` = partes antes/depois do ponto (`Objeto.Nome`).

| Contrato | API | Consulta (placeholders preenchidos pelo utilitário) | Pendência (`validationPending`) |
|---|---|---|---|
| `apex-class` | Dados | `SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = '{developerName}'` | Objeto ApexClass (SOAP/REST API): confirmar no piloto os campos IsValid e LengthWithoutComments. |
| `apex-trigger` | Dados | `SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete, CreatedDate, LastModifiedDate FROM ApexTrigger WHERE Name = '{developerName}'` | Objeto ApexTrigger (Object Reference): campos TableEnumOrId, IsValid e Usage* não confirmados na documentação oficial nesta adaptação; confirmar no piloto. |
| `assignment-rules` | Tooling | `SELECT Id, Name, Active FROM AssignmentRule WHERE SobjectType = '{fullName}'` | Objeto AssignmentRule (Tooling API): confirmar nome do objeto e o filtro SobjectType no piloto. |
| `auto-response-rules` | Tooling | `SELECT Id, Name, Active FROM AutoResponseRule WHERE SobjectType = '{fullName}'` | Objeto AutoResponseRule (Tooling API): confirmar nome do objeto e o filtro SobjectType no piloto. |
| `business-process` | Dados | `SELECT Id, Name, TableEnumOrId, IsActive, Description FROM BusinessProcess WHERE Name = '{shortName}' AND TableEnumOrId = '{objectName}'` | Objeto BusinessProcess: confirmar campos e o filtro por objeto (TableEnumOrId) no piloto. |
| `certificate` | Tooling | `SELECT DeveloperName, ExpirationDate, KeySize FROM Certificate WHERE DeveloperName = '{developerName}'` | Tooling API (Certificate, API 37.0+). Confirmar no piloto. |
| `change-data-capture` | Tooling | `SELECT Id, DeveloperName, EventChannel, SelectedEntity FROM PlatformEventChannelMember WHERE DeveloperName = '{developerName}'` | PlatformEventChannelMember (Tooling API): confirmar campos no piloto. |
| `connected-app` | Dados | `SELECT Id, Name, OptionsAllowAdminApprovedUsersOnly FROM ConnectedApplication WHERE Name = '{developerName}'` | Object Reference (ConnectedApplication, query()). Confirmar no piloto se Name corresponde ao fullName do metadata ConnectedApp. |
| `custom-metadata` | Tooling | `SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = '{fullName}'` | Campos conforme Tooling API e Field Reference (EntityDefinition); confirmar no piloto que a consulta é aceita pela org. |
| `custom-object` | Tooling | `SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = '{fullName}'` | Campos conforme Tooling API e Field Reference (EntityDefinition); confirmar no piloto que a consulta é aceita pela org. |
| `custom-site` | Dados | `SELECT Id, Name, MasterLabel, Status, SiteType, UrlPathPrefix FROM Site WHERE Name = '{fullName}'` | Objeto Site: confirmar campos no piloto. |
| `escalation-rules` | Tooling | `SELECT Id, Name, Active FROM EscalationRule WHERE SobjectType = '{fullName}'` | Objeto EscalationRule (Tooling API): confirmar nome do objeto e o filtro SobjectType no piloto. |
| `external-credential` | Dados | `SELECT Id, DeveloperName, MasterLabel, CreatedDate, LastModifiedDate FROM ExternalCredential WHERE DeveloperName = '{developerName}'` | Confirmar no piloto que o objeto ExternalCredential é consultável via SOQL na org. |
| `flexipage` | Tooling | `SELECT Id, DeveloperName, MasterLabel, Type, EntityDefinitionId, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM FlexiPage WHERE DeveloperName = '{developerName}'` | Objeto FlexiPage (Tooling API): confirmar campos no piloto. |
| `flow` | Tooling | `SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = '{developerName}' ORDER BY VersionNumber` | Confirmar no piloto que o filtro Definition.DeveloperName é aceito pela Tooling API da org. |
| `lwc` | Tooling | `SELECT Id, DeveloperName, MasterLabel, ApiVersion, IsExposed, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM LightningComponentBundle WHERE DeveloperName = '{developerName}'` | Objeto LightningComponentBundle (Tooling API): campos não confirmados na documentação oficial nesta adaptação; confirmar no piloto. |
| `named-credential` | Dados | `SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = '{developerName}'` | Object Reference (NamedCredential, query(); exige View Setup and Configuration). Confirmar no piloto. |
| `network` | Dados | `SELECT Id, Name, Status, UrlPathPrefix FROM Network WHERE Name = '{fullName}'` | Objeto Network: confirmar campos e se Name é o nome de API (fullName) no piloto. |
| `omni-data-transform` | Dados | `SELECT Id, Name, Type, IsActive, VersionNumber FROM OmniDataTransform WHERE Name = '{fullName}'` | Objeto OmniDataTransform: confirmar campos e se Name é o fullName no piloto. |
| `omni-integration-procedure` | Dados | `SELECT Id, UniqueName, Type, SubType, Language, VersionNumber, IsActive, IsIntegrationProcedure FROM OmniProcess WHERE UniqueName = '{fullName}'` | Objeto OmniProcess: confirmar campos e o filtro UniqueName = fullName no piloto. |
| `omni-script` | Dados | `SELECT Id, UniqueName, Type, SubType, Language, VersionNumber, IsActive, IsIntegrationProcedure FROM OmniProcess WHERE UniqueName = '{fullName}'` | Objeto OmniProcess: confirmar campos e o filtro UniqueName = fullName no piloto. |
| `omni-ui-card` | Dados | `SELECT Id, UniqueName, Name, VersionNumber, IsActive FROM OmniUiCard WHERE UniqueName = '{fullName}'` | Objeto OmniUiCard: confirmar campos e o filtro UniqueName = fullName no piloto. |
| `opportunity-split-type` | Dados | `SELECT Id, DeveloperName, MasterLabel FROM OpportunitySplitType WHERE DeveloperName = '{developerName}'` | Objeto OpportunitySplitType (API 37+): confirmar campos no piloto. |
| `org-security` | Dados | `SELECT Id, Name, OrganizationType, IsSandbox, InstanceName, DefaultAccountAccess, DefaultContactAccess, DefaultOpportunityAccess, DefaultCaseAccess, DefaultLeadAccess, DefaultCalendarAccess, DefaultPricebookAccess, DefaultCampaignAccess FROM Organization` | Objeto Organization: confirmar campos no piloto. |
| `permission-set-group` | Dados | `SELECT Id, DeveloperName, MasterLabel, Status, HasActivationRequired, CreatedDate, LastModifiedDate FROM PermissionSetGroup WHERE DeveloperName = '{developerName}'` | Objeto PermissionSetGroup: confirmar campos no piloto. |
| `permission-set` | Dados | `SELECT Id, Name, Label, IsOwnedByProfile, CreatedDate, LastModifiedDate FROM PermissionSet WHERE Name = '{developerName}'` | Objeto PermissionSet (SOAP/REST API): confirmar campos no piloto. |
| `platform-event` | Tooling | `SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = '{fullName}'` | EntityDefinition para objeto __e: confirmar no piloto. |
| `profile` | Dados | `SELECT Id, Name, UserType, UserLicense.Name, Description, CreatedDate, LastModifiedDate FROM Profile WHERE Name = '{fullName}'` | Objeto Profile: perfis padrão têm Name (ex.: System Administrator) diferente do fullName do metadata (ex.: Admin); confirmar filtro e campos no piloto. |
| `public-group` | Dados | `SELECT Id, Name, DeveloperName, Type, DoesIncludeBosses, CreatedDate, LastModifiedDate FROM Group WHERE DeveloperName = '{developerName}'` | Objeto Group: confirmar campos no piloto. Membros (GroupMember) não são consultados. |
| `queue` | Dados | `SELECT Id, Name, DeveloperName, Type, DoesSendEmailToMembers FROM Group WHERE DeveloperName = '{developerName}'` | Fila é um Group com Type Queue: confirmar no piloto. E-mail e membros não são consultados. |
| `role` | Dados | `SELECT Id, Name, DeveloperName, ParentRoleId, RollupDescription, CaseAccessForAccountOwner, ContactAccessForAccountOwner, OpportunityAccessForAccountOwner FROM UserRole WHERE DeveloperName = '{developerName}'` | Objeto UserRole: confirmar campos no piloto. |
| `territory2-model` | Dados | `SELECT Id, DeveloperName, Name, State, ActivatedDate FROM Territory2Model WHERE DeveloperName = '{developerName}'` | Objeto Territory2Model: confirmar campos (State, ActivatedDate) no piloto. |

## Apêndice B — campos de namespace (DA-05)

O filtro de namespace só entra nos contratos depois de confirmar que o campo existe em cada objeto:

```bash
sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, Definition.NamespacePrefix FROM Flow LIMIT 1"
sf data query --target-org dev --json --query "SELECT Id, NamespacePrefix FROM NamedCredential LIMIT 1"
sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, NamespacePrefix FROM Certificate LIMIT 1"
sf data query --target-org dev --json --query "SELECT Id, NamespacePrefix FROM ExternalCredential LIMIT 1"
```

- **Sucesso:** o campo existe; o contrato passa a filtrar `NamespacePrefix` e o aviso "pode incluir componente homônimo de outro namespace" deixa de aparecer.
- **`INVALID_FIELD`:** o objeto não tem o campo; o aviso continua para componentes de pacote.

## Apêndice C — Connected App: `Name` é o nome de API? (DA-13)

```bash
sf sobject describe --sobject ConnectedApplication --target-org dev --json | python3 -c "import json,sys; f={x['name']: x['label'] for x in json.load(sys.stdin)['result']['fields']}; print({k: f[k] for k in f if 'Name' in k})"
sf data query --target-org dev --json --query "SELECT Name FROM ConnectedApplication LIMIT 5"
```

Compare o `Name` com o nome dos arquivos `*.connectedApp-meta.xml` no raw do retrieve. Se `Name` for o rótulo (com espaços, por exemplo), a consulta por nome do metadata não encontra o app: relate quais campos existem para trocar o filtro.
