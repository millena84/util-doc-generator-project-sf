# Roteiro de piloto com org real

Os testes automatizados usam uma Salesforce CLI **simulada**. Este roteiro confirma, numa org real, as premissas que o código ainda não pôde validar. Cada item indica o que rodar, o que se espera e o que muda no utilitário conforme o resultado.

> **Segurança:** nenhum comando abaixo imprime o access token. Não cole tokens, senhas ou o conteúdo de `inventory/**/components/` ao relatar resultados. Use uma org de desenvolvimento ou sandbox aprovada em `approvedOrgs`.

Substitua `dev` pelo alias da org e `<Nome>` pelo nome de API de um componente real.

## 1. Token pelo comando novo da CLI (DA-14)

Confirma o formato de `sf org auth show-access-token --json` mostrando só a **estrutura** da resposta:

```bash
sf org auth show-access-token --target-org dev --json | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('result'); print('status:', d.get('status'), '| result:', type(r).__name__, sorted(r) if isinstance(r, dict) else '(texto)')"
```

- **Esperado:** `status: 0 | result: dict ['accessToken', ...]` ou `result: str (texto)`. O utilitário aceita os dois.
- **Se for diferente:** a execução para com `ACCESS_TOKEN_UNAVAILABLE`. Relate a lista de chaves para ajustar `_acquire_token`.

## 2. `connectedStatus` por tipo de autenticação (DA-10)

```bash
sf org display --target-org dev --json | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; print(r.get('connectedStatus'), '| chaves:', sorted(r))"
```

- **Esperado:** `Connected`. Repita para cada forma de login usada (web, JWT, scratch org).
- **Se vier outro valor ou nada:** o passo 3 para com `ORG_DISPLAY_INCOMPLETE`/`ORG_NOT_CONNECTED`. Relate o valor para ampliar a regra.

## 3. Dados internos (`validationPending` nos contratos)

Para cada consulta, rode com um componente real e anote: funcionou? quantos registros? Execute só as consultas dos tipos existentes na org.

| Contrato | Comando |
|---|---|
| Flow (versões) | `sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = '<Nome>' ORDER BY VersionNumber"` |
| Custom Object / Custom Metadata | `sf data query --use-tooling-api --target-org dev --json --query "SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = '<Objeto__c>'"` |
| Connected App | `sf data query --target-org dev --json --query "SELECT Id, Name, OptionsAllowAdminApprovedUsersOnly FROM ConnectedApplication WHERE Name = '<Nome>'"` |
| Named Credential | `sf data query --target-org dev --json --query "SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = '<Nome>'"` |
| Certificate | `sf data query --use-tooling-api --target-org dev --json --query "SELECT DeveloperName, ExpirationDate, KeySize FROM Certificate WHERE DeveloperName = '<Nome>'"` |
| External Credential | `sf data query --target-org dev --json --query "SELECT Id, DeveloperName, MasterLabel, CreatedDate, LastModifiedDate FROM ExternalCredential WHERE DeveloperName = '<Nome>'"` |

- **Esperado:** `status: 0` e `totalSize` = 1 (ou o número de versões, no Flow).
- **Erro `INVALID_FIELD` ou `INVALID_TYPE`:** o objeto ou campo não existe na org/API. Relate a mensagem; o contrato será ajustado (a execução não para: a seção fica "Não informado").
- **Erro de permissão:** relate o perfil usado; a seção depende de acesso à configuração (ex.: *View Setup and Configuration*).

### Connected App: `Name` é o nome de API? (DA-13)

```bash
sf sobject describe --sobject ConnectedApplication --target-org dev --json | python3 -c "import json,sys; f={x['name']: x['label'] for x in json.load(sys.stdin)['result']['fields']}; print({k: f[k] for k in f if 'Name' in k})"
```

E compare o valor de `Name` (consulta acima, sem filtro, com `LIMIT 5`) com o nome do arquivo `*.connectedApp-meta.xml` recuperado:

```bash
sf data query --target-org dev --json --query "SELECT Name FROM ConnectedApplication LIMIT 5"
```

- **Se `Name` for o rótulo (com espaços, por exemplo):** a consulta por `DeveloperName` do metadata não encontra o app. Relate quais campos existem para trocar o filtro.

## 4. Campos de namespace (DA-05)

O filtro de namespace só entra nos contratos depois de confirmar que o campo existe em cada objeto. Rode uma vez por objeto:

```bash
sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, Definition.NamespacePrefix FROM Flow LIMIT 1"
sf data query --target-org dev --json --query "SELECT Id, NamespacePrefix FROM NamedCredential LIMIT 1"
sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, NamespacePrefix FROM Certificate LIMIT 1"
sf data query --target-org dev --json --query "SELECT Id, NamespacePrefix FROM ExternalCredential LIMIT 1"
```

- **Sucesso:** o campo existe; o contrato passa a filtrar `NamespacePrefix` e o aviso "pode incluir componente homônimo de outro namespace" deixa de aparecer.
- **`INVALID_FIELD`:** o objeto não tem o campo; o aviso continua para componentes de pacote.

## 5. Apex (Onda 01)

Confirma que o retrieve traz o código e que a consulta de dados internos funciona:

```bash
sf data query --target-org dev --json --query "SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = '<Classe>'"
bin/sf-docs.sh run --group ApexClass --component <Classe> --non-interactive
```

- **Esperado:** `status: 0` na consulta; no run, `inventory/org-<alias>/api-v<N>/apex-classes/components/classes/` com `<Classe>.cls` e `<Classe>.cls-meta.xml`, e o documento `doc-<classe>-apex-class.md` com interfaces e métodos preenchidos.
- **`INVALID_FIELD` em `IsValid` ou `LengthWithoutComments`:** relate; o campo sai do contrato `apex-class.schema.json`.
- **Classe com papel assíncrono:** confira se o subdocumento esperado (`-apex-batch`, `-apex-queueable`, `-apex-scheduler`, `-apex-future`) foi gerado. Classe com papel não detectado: relate a declaração da classe (só a linha `class ... implements ...`, sem o corpo).

## 5b. Apex Trigger (Onda 02)

```bash
sf data query --target-org dev --json --query "SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete FROM ApexTrigger WHERE Name = '<Trigger>'"
bin/sf-docs.sh run --group ApexTrigger --group Flow --group CustomObject --group ApexClass --non-interactive
```

- **Esperado:** `status: 0` na consulta; no run, `apex-triggers/components/triggers/<Trigger>.trigger` e o documento `doc-<trigger>-apex-trigger.md`.
- **`INVALID_FIELD` em `TableEnumOrId`, `IsValid` ou `Usage*`:** relate; o campo sai do contrato `apex-trigger.schema.json`.
- **Coexistência:** compare a seção "Coexistência no objeto e ordem de execução" com o Setup (Object Manager → objeto → Triggers e Flow Trigger Explorer). Flow record-triggered do objeto que não aparece = falha (relate `start.triggerType` e `start.object` do XML). Confirme se `triggerOrder` vem no XML do Flow.
- **Classes chamadas:** classe chamada que não aparece, ou nome que não é classe e aparece, = falha; relate só a linha da chamada (sem o corpo).
- **Modo de acesso:** confirme na página *Apex Versioned Behavior Changes* se o user mode padrão da API 67.0 vale para triggers.

## 5c. Lightning Web Components (Onda 03)

```bash
sf data query --use-tooling-api --target-org dev --json --query "SELECT Id, DeveloperName, MasterLabel, ApiVersion, IsExposed, Description, NamespacePrefix FROM LightningComponentBundle WHERE DeveloperName = '<componente>'"
bin/sf-docs.sh run --group LightningComponentBundle --group ApexClass --component <componente> --non-interactive
```

- **Esperado:** `status: 0`; no run, `lwc/components/lwc/<componente>/` com `.js`, `.html` e `.js-meta.xml`, e o documento `doc-<componente>-lwc.md` (mais `-lwc-quick-action`/`-lwc-flow-screen` conforme os targets).
- **`INVALID_FIELD`:** relate; o campo sai do contrato `lwc.schema.json`.
- **Confira:** `fullName` dos arquivos no retrieve do bundle (todos com o nome do componente?); targets e propriedades de `targetConfigs` iguais ao `.js-meta.xml`; métodos Apex chamados e a verificação `@AuraEnabled`; perfil/permission set com `customPermissions` da permissão importada (formato `<customPermissions><enabled>`/`<name>`).

## 5d. Segurança e governança (Onda 04)

```bash
sf project retrieve start --metadata Settings:Security --target-org dev --json | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; print([(f['type'], f['fullName']) for f in r.get('files', [])])"
sf org list metadata-types --target-org dev --json | python3 -c "import json,sys; print(sorted(t['xmlName'] for t in json.load(sys.stdin)['result']['metadataObjects'] if 'Settings' in t['xmlName'])[:20])"
sf data query --target-org dev --json --query "SELECT Id, Name, OrganizationType, IsSandbox, DefaultAccountAccess FROM Organization"
bin/sf-docs.sh run --group OrgSecurity --group CustomObject --group Profile --group Role --group PublicGroup --group SharingRules --group PermissionSetGroup --non-interactive
```

- **Retrieve de Settings:** o arquivo vem como `type: Settings` e `fullName: Security`? Se vier outro tipo, ajuste `fixedComponents.retrieveType` em `config/metadata-types-mvp.json`.
- **`SecuritySettings` na lista de metadata types:** se não aparecer (e aparecer só `Settings`), troque `primaryMetadataType` do grupo `OrgSecurity`; o grupo fica `NOT_ENABLED` até isso.
- **Perfis padrão:** a consulta de dados internos filtra `Profile.Name` pelo fullName do metadata (`Admin`), mas o Name é "System Administrator": relate o par fullName/Name para ajustar o filtro.
- **Confira** os elementos de `sessionSettings`, `passwordPolicies` e `networkAccess` contra o Setup; `parentRole` e níveis de acesso do Role; `doesIncludeBosses` do Group; `mutingPermissionSets` do PSG.

## 6. Acesso e configuração

O ponto mais importante: confirmar se o XML de Profile/PermissionSet traz as permissões **só** dos componentes recuperados no mesmo pedido. O utilitário já recupera tudo junto (passo 6b), mas o resultado precisa ser conferido:

```bash
bin/sf-docs.sh run --group ApexClass --component <Classe> --non-interactive
```

- **Esperado:** `inventory/org-<alias>/api-v<N>/access/components/profiles/*.profile-meta.xml` com `<classAccesses>` da classe; o documento da classe termina com "Acesso e configuração" listando os perfis/permission sets que a liberam no Setup.
- **Compare com o Setup** (perfil → Acesso a classes Apex): perfil que libera a classe e não aparece no documento = falha; relate o perfil e o trecho `<classAccesses>` do XML.
- **Confirmar elementos** (relate se algum vier vazio quando deveria ter valor): `objectPermissions` (objeto), `recordTypeVisibilities`, `PermissionSetGroup.permissionSets`, `SharingRules` (`sharedTo`) e o formato de `externalCredentialPrincipal` (`<ExternalCredential>-<Principal>`).
- **Volume:** anote o tempo do passo 6b e o tamanho de `access/` numa org grande; se ficar inviável, o retrieve pode ser dividido por tipo.

## 7. Execução completa

Depois dos itens acima:

```bash
bin/sf-docs.sh validate-config
bin/sf-docs.sh run --group Flow --non-interactive
```

Confira em `runs/<runId>/resumo.md`: cobertura, `tokenSource`, avisos de dados internos e a pasta `saida/docs/doc-<alias>-MMDDAA/`.

## Como relatar

Para cada item: comando, resultado (`status`, `totalSize`, mensagem de erro) e a forma de login. Não inclua token, senha, `consumerSecret` nem conteúdo dos XMLs recuperados.
