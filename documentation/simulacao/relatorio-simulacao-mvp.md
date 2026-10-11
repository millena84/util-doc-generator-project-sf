# Relatório de simulação — todas as documentações do MVP

> **SIMULADO.** CLI `sf` simulada (`tests/fixtures/bin/sf`, cenário `mvp_complete`) e Metadata API simulada. Nenhum dado veio de uma org real. Gerado por `python3 -m tests.simulate_mvp`.

- Execução: `run-20261011-015037` — status **SUCCESS** — código de saída `0`
- Org: `dev` — API `67.0`

## 1. Saída no terminal

```
[01:50:37] INFO  Passo 1: Salesforce CLI 2.60.0 (mínima 2.0.0)
[01:50:37] INFO  Passo 2: alias 'dev' autenticado
[01:50:37] INFO  Passo 3: usuario.simulado@example.com conectado; API 67.0 (detectada 67.0, fonte: sf org display)
[01:50:37] INFO  Passo 4: grupos habilitados: Flow, ExternalClientApp, ExternalCredential, ConnectedApp, CustomObject, CustomMetadata
[01:50:37] INFO  Passo 6: Flow -> 2 componente(s)
[01:50:37] INFO  Passo 6: FlowDefinition -> 1 componente(s)
[01:50:37] INFO  Passo 6: ExternalClientApplication -> 1 componente(s)
[01:50:37] INFO  Passo 6: ExtlClntAppOauthSettings -> 2 componente(s)
[01:50:37] INFO  Passo 6: ExtlClntAppConfigurablePolicies -> 1 componente(s)
[01:50:37] INFO  Passo 6: ExtlClntAppOauthConfigurablePolicies -> 1 componente(s)
[01:50:38] INFO  Passo 6: ExternalCredential -> 1 componente(s)
[01:50:38] INFO  Passo 6: NamedCredential -> 1 componente(s)
[01:50:38] INFO  Passo 6: ConnectedApp -> 1 componente(s)
[01:50:38] INFO  Passo 6: RemoteSiteSetting -> 1 componente(s)
[01:50:38] INFO  Passo 6: CorsWhitelistOrigin -> 1 componente(s)
[01:50:38] INFO  Passo 6: CspTrustedSite -> 1 componente(s)
[01:50:38] INFO  Passo 6: CustomObject -> 3 componente(s)
[01:50:38] INFO  Passo 6: CustomMetadata -> 2 componente(s)
[01:50:38] INFO  Flow:Flow:Meu_Flow: processando
[01:50:38] INFO  Flow:Flow:Meu_Flow: SUCCESS -> saida/docs/doc-org-101126/doc-meu-flow-flow.md
[01:50:38] INFO  Flow:Flow:Tela_Cadastro: processando
[01:50:38] INFO  Flow:Flow:Tela_Cadastro: SUCCESS -> saida/docs/doc-org-101126/doc-tela-cadastro-flow.md
[01:50:38] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: processando
[01:50:38] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: SUCCESS -> saida/docs/doc-org-101126/doc-minha-eca-external-client-app.md
[01:50:38] INFO  ExternalCredential:ExternalCredential:Minha_EC: processando
[01:50:38] INFO  ExternalCredential:ExternalCredential:Minha_EC: SUCCESS -> saida/docs/doc-org-101126/doc-minha-ec-external-credential.md
[01:50:38] INFO  ConnectedApp:ConnectedApp:Meu_App: processando
[01:50:38] INFO  ConnectedApp:ConnectedApp:Meu_App: SUCCESS -> saida/docs/doc-org-101126/doc-meu-app-connected-app.md
[01:50:38] INFO  CustomObject:CustomObject:Pedido__c: processando
[01:50:38] INFO  CustomObject:CustomObject:Pedido__c: SUCCESS -> saida/docs/doc-org-101126/doc-pedido-c-custom-object.md
[01:50:38] INFO  CustomMetadata:CustomMetadata:Config__mdt: processando
[01:50:39] INFO  CustomMetadata:CustomMetadata:Config__mdt: SUCCESS -> saida/docs/doc-org-101126/doc-config-mdt-custom-metadata.md
[01:50:39] INFO  Execução run-20261011-015037 finalizada: SUCCESS {'SUCCESS': 7}
[01:50:39] INFO  Log: runs/run-20261011-015037.json
```

## 2. Comandos executados na CLI (por passo)

| # | Passo | Comando |
|---|---|---|
| 1 | 1 | `sf --version` |
| 2 | 2 | `sf org list --json` |
| 3 | 3 | `sf org display --target-org dev --json` |
| 4 | 4 | `sf org list metadata-types --target-org dev --api-version 67.0 --json` |
| 5 | 6 | `sf org list metadata --metadata-type Flow --target-org dev --api-version 67.0 --json` |
| 6 | 6 | `sf org list metadata --metadata-type FlowDefinition --target-org dev --api-version 67.0 --json` |
| 7 | 6 | `sf org list metadata --metadata-type ExternalClientApplication --target-org dev --api-version 67.0 --json` |
| 8 | 6 | `sf org list metadata --metadata-type ExtlClntAppOauthSettings --target-org dev --api-version 67.0 --json` |
| 9 | 6 | `sf org list metadata --metadata-type ExtlClntAppConfigurablePolicies --target-org dev --api-version 67.0 --json` |
| 10 | 6 | `sf org list metadata --metadata-type ExtlClntAppOauthConfigurablePolicies --target-org dev --api-version 67.0 --json` |
| 11 | 6 | `sf org list metadata --metadata-type ExternalCredential --target-org dev --api-version 67.0 --json` |
| 12 | 6 | `sf org list metadata --metadata-type NamedCredential --target-org dev --api-version 67.0 --json` |
| 13 | 6 | `sf org list metadata --metadata-type ConnectedApp --target-org dev --api-version 67.0 --json` |
| 14 | 6 | `sf org list metadata --metadata-type RemoteSiteSetting --target-org dev --api-version 67.0 --json` |
| 15 | 6 | `sf org list metadata --metadata-type CorsWhitelistOrigin --target-org dev --api-version 67.0 --json` |
| 16 | 6 | `sf org list metadata --metadata-type CspTrustedSite --target-org dev --api-version 67.0 --json` |
| 17 | 6 | `sf org list metadata --metadata-type CustomObject --target-org dev --api-version 67.0 --json` |
| 18 | 6 | `sf org list metadata --metadata-type CustomMetadata --target-org dev --api-version 67.0 --json` |
| 19 | 7 | `sf project retrieve start --metadata Flow:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 20 | 7 | `sf project retrieve start --metadata FlowDefinition:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 21 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Meu_Flow' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 22 | 7 | `sf project retrieve start --metadata Flow:Tela_Cadastro --target-org dev --api-version 67.0 --json` |
| 23 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Tela_Cadastro' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 24 | 7 | `sf project retrieve start --metadata ExternalClientApplication:Minha_ECA --target-org dev --api-version 67.0 --json` |
| 25 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Minha_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 26 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Outra_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 27 | 7 | `sf project retrieve start --metadata ExtlClntAppConfigurablePolicies:Minha_ECA_plcy --target-org dev --api-version 67.0 --json` |
| 28 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthConfigurablePolicies:Minha_ECA_oauthPlcy --target-org dev --api-version 67.0 --json` |
| 29 | 7 | `sf project retrieve start --metadata ExternalCredential:Minha_EC --target-org dev --api-version 67.0 --json` |
| 30 | 7 | `sf project retrieve start --metadata NamedCredential:Minha_NC --target-org dev --api-version 67.0 --json` |
| 31 | 7 | `sf project retrieve start --metadata ConnectedApp:Meu_App --target-org dev --api-version 67.0 --json` |
| 32 | 7 | `sf project retrieve start --metadata RemoteSiteSetting:Parceiro_API --target-org dev --api-version 67.0 --json` |
| 33 | 7 | `sf project retrieve start --metadata CorsWhitelistOrigin:Parceiro_Portal --target-org dev --api-version 67.0 --json` |
| 34 | 7 | `sf project retrieve start --metadata CspTrustedSite:Parceiro_CDN --target-org dev --api-version 67.0 --json` |
| 35 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, CreatedDate, LastModifiedDate FROM ExternalCredential WHERE DeveloperName = 'Minha_EC' --target-org dev --api-version 67.0 --json` |
| 36 | 7 | `sf project retrieve start --metadata CustomObject:Pedido__c --target-org dev --api-version 67.0 --json` |
| 37 | 7 | `sf project retrieve start --metadata CustomObject:Config__mdt --target-org dev --api-version 67.0 --json` |
| 38 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Padrao --target-org dev --api-version 67.0 --json` |
| 39 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Secundario --target-org dev --api-version 67.0 --json` |

O passo 5 (`describeValueType`) é SOAP direto na Metadata API, fora da CLI; o passo 8 (XML → JSON) e o passo 10 (Markdown) são locais.

## 3. Situação por metadata type

| Metadata type | Habilitado (4) | Schema (5) | Inventário (6) | Componentes |
|---|---|---|---|---|
| ConnectedApp | ENABLED | SUCCESS | SUCCESS | 1 |
| CorsWhitelistOrigin | ENABLED | SUCCESS | SUCCESS | 1 |
| CspTrustedSite | ENABLED | SUCCESS | SUCCESS | 1 |
| CustomField | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| CustomMetadata | ENABLED | SUCCESS | SUCCESS | 2 |
| CustomObject | ENABLED | SUCCESS | SUCCESS | 3 |
| ExternalClientApplication | ENABLED | SUCCESS | SUCCESS | 1 |
| ExternalCredential | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthSettings | ENABLED | SUCCESS | SUCCESS | 2 |
| Flow | ENABLED | SUCCESS | SUCCESS | 2 |
| FlowDefinition | ENABLED | SUCCESS | SUCCESS | 1 |
| NamedCredential | ENABLED | SUCCESS | SUCCESS | 1 |
| RecordType | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| RemoteSiteSetting | ENABLED | SUCCESS | SUCCESS | 1 |
| ValidationRule | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| WebLink | ENABLED | SUCCESS | via retrieve do CustomObject | — |

## 4. Documentos gerados (passo 10)

| Documento | Modelo | Principal | Relacionados no documento | Status |
|---|---|---|---|---|
| `doc-meu-flow-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Meu_Flow | Meu_Flow (FlowDefinition) | SUCCESS |
| `doc-meu-flow-flow-trigger.md` | `modelo-doc-flow-trigger-vapi-67.md` | Flow:Meu_Flow | (subdocumento) | SUCCESS |
| `doc-tela-cadastro-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Tela_Cadastro | — | SUCCESS |
| `doc-tela-cadastro-dados-cliente-flow-screen.md` | `modelo-doc-flow-screen-vapi-67.md` | Flow:Tela_Cadastro | (subdocumento) | SUCCESS |
| `doc-minha-eca-external-client-app.md` | `modelo-doc-cea-vapi-67.md` | ExternalClientApplication:Minha_ECA | Minha_ECA_oauth (ExtlClntAppOauthSettings), Minha_ECA_plcy (ExtlClntAppConfigurablePolicies), Minha_ECA_oauthPlcy (ExtlClntAppOauthConfigurablePolicies) | SUCCESS |
| `doc-minha-ec-external-credential.md` | `modelo-doc-external-credential-vapi-67.md` | ExternalCredential:Minha_EC | — | SUCCESS |
| `doc-meu-app-connected-app.md` | `modelo-doc-connectedapp-vapi-67.md` | ConnectedApp:Meu_App | — | SUCCESS |
| `doc-pedido-c-custom-object.md` | `modelo-doc-custom-object-vapi-67.md` | CustomObject:Pedido__c | Pedido__c.Status__c (CustomField), Pedido__c.Valor__c (CustomField), Pedido__c.Padrao (RecordType), Pedido__c.Valor_Positivo (ValidationRule), Pedido__c.Imprimir_Pedido (WebLink) | SUCCESS |
| `doc-config-mdt-custom-metadata.md` | `modelo-doc-custom-metadata-vapi-67.md` | CustomMetadata:Config__mdt | Config.Padrao (CustomMetadata), Config.Secundario (CustomMetadata) | SUCCESS |

## 5. Rastreamento de um componente: `Flow:Meu_Flow`

**Passo 3** — `catalog/org-dev/api-v67/org-display.raw.json`

```json
{
  "status": 0,
  "result": {
    "id": "00D000000000000AAA",
    "apiVersion": "67.0",
    "accessToken": "********",
    "instanceUrl": "https://simulado.my.salesforce.com",
    "username": "usuario.simulado@example.com",
    "clientId": "PlatformCLI",
    "connectedStatus": "Connected",
    "alias": "dev"
  }
}
```

**Passo 4** — `catalog/org-dev/api-v67/metadata-types.index.json`

```json
{
  "metadataTypes": {
    "ConnectedApp": {
      "directoryName": "connectedApps",
      "suffix": "connectedApp",
      "inFolder": false,
      "metaFile": false,
      "childXmlNames": []
    },
    "CorsWhitelistOrigin": {
      "directoryName": "corsWhitelistOrigins",
      "suffix": "corsWhitelistOrigin",
      "inFolder": false,
      "metaFile": false,
      "childXmlNames": []
    },
    "CspTrustedSite": {
      "directoryName": "cspTrustedSites",
      "suffix": "cspTrustedSite",
      "inFolder": false,
... (113 linhas omitidas)
```

**Passo 5** — `catalog/org-dev/api-v67/schemas/flow.schema.json`

```json
{
  "metadataType": "Flow",
  "apiVersion": "67.0",
  "sourceRaw": "flow.describevaluetype.raw.json",
  "sourceRawSha256": "4cdc660b89abe08e1dd9b34d7613ba65d4db0fd3ed2c8cc0096501f593f3484f",
  "apiCreatable": "true",
  "apiDeletable": "true",
  "apiReadable": "true",
  "apiUpdatable": "true",
  "parentField": null,
  "fieldNames": [
    "apiVersion",
    "description",
    "label",
    "processType",
    "screens",
    "start",
    "status"
  ],
  "valueTypeFields": [
... (58 linhas omitidas)
```

**Passo 6** — `inventory/org-dev/api-v67/flows/inventory.index.json`

```json
{
  "metadataType": "Flow",
  "sourceRaw": "inventory.raw.json",
  "count": 2,
  "components": [
    {
      "fullName": "Meu_Flow",
      "type": "Flow",
      "fileName": "x/Meu_Flow",
      "id": "000000000000000AAA",
      "namespacePrefix": "",
      "manageableState": "unmanaged",
      "lastModifiedDate": "2026-10-01T00:00:00.000Z"
    },
    {
      "fullName": "Tela_Cadastro",
      "type": "Flow",
      "fileName": "x/Tela_Cadastro",
      "id": "000000000000000AAA",
      "namespacePrefix": "",
... (5 linhas omitidas)
```

**Passo 7** — `inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json`

```json
{
  "status": 0,
  "result": {
    "done": true,
    "status": "Succeeded",
    "success": true,
    "files": [
      {
        "fullName": "Meu_Flow",
        "type": "Flow",
        "state": "Created",
        "filePath": "/tmp/sfdocs-retrieve-f6x38qr0/force-app/main/default/flows/Meu_Flow.flow-meta.xml"
      }
    ]
  }
}
```

**Passo 7** — `inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>67.0</apiVersion>
    <label>Meu Flow</label>
    <processType>AutoLaunchedFlow</processType>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Status__c</field>
            <operator>EqualTo</operator>
            <value>
                <stringValue>Aprovado</stringValue>
            </value>
        </filters>
        <object>Pedido__c</object>
        <recordTriggerType>Update</recordTriggerType>
        <triggerType>RecordAfterSave</triggerType>
    </start>
    <status>Active</status>
</Flow>
```

**Passo 8** — `inventory/org-dev/api-v67/flows/normalized/meu-flow.json`

```json
{
  "metadataType": "Flow",
  "fullName": "Meu_Flow",
  "role": "primary",
  "source": {
    "xml": "inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml",
    "xmlSha256": "9da16627f54c49d441102a1bb44e0c5e8f584469af7d31e36ef57ca9c3f2dc3e",
    "rootElement": "Flow",
    "retrieveRaw": "inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json"
  },
  "schema": {
    "available": true,
    "fieldNames": [
      "apiVersion",
      "description",
      "label",
      "processType",
      "screens",
      "start",
      "status"
    ]
  },
  "fields": {
    "present": [
      "apiVersion",
      "label",
      "processType",
      "start",
      "status"
    ],
    "absent": [
      "description",
      "screens"
    ]
  },
  "data": {
    "apiVersion": "67.0",
    "label": "Meu Flow",
    "processType": "AutoLaunchedFlow",
    "start": {
      "locationX": "50",
      "locationY": "0",
      "filterLogic": "and",
      "filters": {
        "field": "Status__c",
        "operator": "EqualTo",
        "value": {
          "stringValue": "Aprovado"
        }
      },
      "object": "Pedido__c",
      "recordTriggerType": "Update",
      "triggerType": "RecordAfterSave"
    },
    "status": "Active",
    "description": null,
    "screens": null
  }
}
```

**Passo 9** — `inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json`

```json
{
  "status": 0,
  "result": {
    "done": true,
    "totalSize": 2,
    "records": [
      {
        "attributes": {
          "type": "Flow"
        },
        "Id": "301000000000001AAA",
        "VersionNumber": 1,
        "Status": "Obsolete"
      },
      {
        "attributes": {
          "type": "Flow"
        },
        "Id": "301000000000002AAA",
        "VersionNumber": 2,
        "Status": "Active"
      }
    ]
  }
}
```

## 6. Árvore de arquivos gerados

```
catalog/org-dev/api-v67/metadata-types.index.json
catalog/org-dev/api-v67/metadata-types.raw.json
catalog/org-dev/api-v67/org-display.raw.json
catalog/org-dev/api-v67/schemas/connected-app.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/connected-app.schema.json
catalog/org-dev/api-v67/schemas/cors-whitelist-origin.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/cors-whitelist-origin.schema.json
catalog/org-dev/api-v67/schemas/csp-trusted-site.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/csp-trusted-site.schema.json
catalog/org-dev/api-v67/schemas/custom-field.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/custom-field.schema.json
catalog/org-dev/api-v67/schemas/custom-metadata.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/custom-metadata.schema.json
catalog/org-dev/api-v67/schemas/custom-object.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/custom-object.schema.json
catalog/org-dev/api-v67/schemas/external-client-application.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/external-client-application.schema.json
catalog/org-dev/api-v67/schemas/external-credential.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/external-credential.schema.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-configurable-policies.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-configurable-policies.schema.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-oauth-configurable-policies.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-oauth-configurable-policies.schema.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-oauth-settings.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/extl-clnt-app-oauth-settings.schema.json
catalog/org-dev/api-v67/schemas/flow-definition.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/flow-definition.schema.json
catalog/org-dev/api-v67/schemas/flow.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/flow.schema.json
catalog/org-dev/api-v67/schemas/named-credential.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/named-credential.schema.json
catalog/org-dev/api-v67/schemas/record-type.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/record-type.schema.json
catalog/org-dev/api-v67/schemas/remote-site-setting.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/remote-site-setting.schema.json
catalog/org-dev/api-v67/schemas/validation-rule.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/validation-rule.schema.json
catalog/org-dev/api-v67/schemas/web-link.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/web-link.schema.json
inventory/org-dev/api-v67/connected-apps/components/connectedApps/Meu_App.connectedApp-meta.xml
inventory/org-dev/api-v67/connected-apps/inventory.index.json
inventory/org-dev/api-v67/connected-apps/inventory.raw.json
inventory/org-dev/api-v67/connected-apps/normalized/meu-app.json
inventory/org-dev/api-v67/connected-apps/retrieve/meu-app.raw.json
inventory/org-dev/api-v67/cors-whitelist-origins/components/corsWhitelistOrigins/Parceiro_Portal.corsWhitelistOrigin-meta.xml
inventory/org-dev/api-v67/cors-whitelist-origins/inventory.index.json
inventory/org-dev/api-v67/cors-whitelist-origins/inventory.raw.json
inventory/org-dev/api-v67/cors-whitelist-origins/normalized/parceiro-portal.json
inventory/org-dev/api-v67/cors-whitelist-origins/retrieve/parceiro-portal.raw.json
inventory/org-dev/api-v67/csp-trusted-sites/components/cspTrustedSites/Parceiro_CDN.cspTrustedSite-meta.xml
inventory/org-dev/api-v67/csp-trusted-sites/inventory.index.json
inventory/org-dev/api-v67/csp-trusted-sites/inventory.raw.json
inventory/org-dev/api-v67/csp-trusted-sites/normalized/parceiro-cdn.json
inventory/org-dev/api-v67/csp-trusted-sites/retrieve/parceiro-cdn.raw.json
inventory/org-dev/api-v67/custom-metadata/components/customMetadata/Config.Padrao.md-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/customMetadata/Config.Secundario.md-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/objects/Config__mdt/Config__mdt.object-meta.xml
inventory/org-dev/api-v67/custom-metadata/inventory.index.json
inventory/org-dev/api-v67/custom-metadata/inventory.raw.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-mdt.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-padrao.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-secundario.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-mdt.raw.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-padrao.raw.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-secundario.raw.json
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/Pedido__c.object-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/fields/Status__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/fields/Valor__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/recordTypes/Padrao.recordType-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/validationRules/Valor_Positivo.validationRule-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/webLinks/Imprimir_Pedido.webLink-meta.xml
inventory/org-dev/api-v67/custom-objects/inventory.index.json
inventory/org-dev/api-v67/custom-objects/inventory.raw.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c-imprimir-pedido.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c-padrao.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c-status-c.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c-valor-c.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c-valor-positivo.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c.json
inventory/org-dev/api-v67/custom-objects/retrieve/pedido-c.raw.json
inventory/org-dev/api-v67/external-client-apps/components/externalClientApps/Minha_ECA.eca-meta.xml
inventory/org-dev/api-v67/external-client-apps/inventory.index.json
inventory/org-dev/api-v67/external-client-apps/inventory.raw.json
inventory/org-dev/api-v67/external-client-apps/normalized/minha-eca.json
inventory/org-dev/api-v67/external-client-apps/retrieve/minha-eca.raw.json
inventory/org-dev/api-v67/external-credentials/components/externalCredentials/Minha_EC.externalCredential-meta.xml
inventory/org-dev/api-v67/external-credentials/internal-data/minha-ec.raw.json
inventory/org-dev/api-v67/external-credentials/inventory.index.json
inventory/org-dev/api-v67/external-credentials/inventory.raw.json
inventory/org-dev/api-v67/external-credentials/normalized/minha-ec.json
inventory/org-dev/api-v67/external-credentials/retrieve/minha-ec.raw.json
inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/components/extlClntAppPolicies/Minha_ECA_plcy.ecaPlcy-meta.xml
inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/inventory.index.json
inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/inventory.raw.json
inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/normalized/minha-eca-plcy.json
inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/retrieve/minha-eca-plcy.raw.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/components/extlClntAppOauthPolicies/Minha_ECA_oauthPlcy.ecaOauthPlcy-meta.xml
inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/inventory.index.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/inventory.raw.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/normalized/minha-eca-oauthplcy.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/retrieve/minha-eca-oauthplcy.raw.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/components/extlClntAppOauthSettings/Minha_ECA_oauth.ecaOauth-meta.xml
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/components/extlClntAppOauthSettings/Outra_ECA_oauth.ecaOauth-meta.xml
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/inventory.index.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/inventory.raw.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/normalized/minha-eca-oauth.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/normalized/outra-eca-oauth.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/retrieve/minha-eca-oauth.raw.json
inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/retrieve/outra-eca-oauth.raw.json
inventory/org-dev/api-v67/flow-definitions/components/flowDefinitions/Meu_Flow.flowDefinition-meta.xml
inventory/org-dev/api-v67/flow-definitions/inventory.index.json
inventory/org-dev/api-v67/flow-definitions/inventory.raw.json
inventory/org-dev/api-v67/flow-definitions/normalized/meu-flow.json
inventory/org-dev/api-v67/flow-definitions/retrieve/meu-flow.raw.json
inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml
inventory/org-dev/api-v67/flows/components/flows/Tela_Cadastro.flow-meta.xml
inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json
inventory/org-dev/api-v67/flows/internal-data/tela-cadastro.raw.json
inventory/org-dev/api-v67/flows/inventory.index.json
inventory/org-dev/api-v67/flows/inventory.raw.json
inventory/org-dev/api-v67/flows/normalized/meu-flow.json
inventory/org-dev/api-v67/flows/normalized/tela-cadastro.json
inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json
inventory/org-dev/api-v67/flows/retrieve/tela-cadastro.raw.json
inventory/org-dev/api-v67/named-credentials/components/namedCredentials/Minha_NC.namedCredential-meta.xml
inventory/org-dev/api-v67/named-credentials/inventory.index.json
inventory/org-dev/api-v67/named-credentials/inventory.raw.json
inventory/org-dev/api-v67/named-credentials/normalized/minha-nc.json
inventory/org-dev/api-v67/named-credentials/retrieve/minha-nc.raw.json
inventory/org-dev/api-v67/remote-site-settings/components/remoteSiteSettings/Parceiro_API.remoteSite-meta.xml
inventory/org-dev/api-v67/remote-site-settings/inventory.index.json
inventory/org-dev/api-v67/remote-site-settings/inventory.raw.json
inventory/org-dev/api-v67/remote-site-settings/normalized/parceiro-api.json
inventory/org-dev/api-v67/remote-site-settings/retrieve/parceiro-api.raw.json
runs/run-20261011-015037.json
saida/docs/doc-org-101126/doc-config-mdt-custom-metadata.md
saida/docs/doc-org-101126/doc-meu-app-connected-app.md
saida/docs/doc-org-101126/doc-meu-flow-flow-trigger.md
saida/docs/doc-org-101126/doc-meu-flow-flow.md
saida/docs/doc-org-101126/doc-minha-ec-external-credential.md
saida/docs/doc-org-101126/doc-minha-eca-external-client-app.md
saida/docs/doc-org-101126/doc-pedido-c-custom-object.md
saida/docs/doc-org-101126/doc-tela-cadastro-dados-cliente-flow-screen.md
saida/docs/doc-org-101126/doc-tela-cadastro-flow.md
```

## 7. Conteúdo dos documentos finais

### `saida/docs/doc-org-101126/doc-meu-flow-flow.md`

```markdown
# Flow: Meu_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Flow | XML |
| MasterLabel | Meu Flow | XML |
| ApiVersion | 67.0 | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

**FlowDefinition: Meu_Flow**

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Flow | XML |
| MasterLabel | Meu Flow | XML |
| ActiveVersionNumber | 2 | XML |
| Description | Não informado | XML |

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Meu_Flow | FlowDefinition | XML |
```

### `saida/docs/doc-org-101126/doc-meu-flow-flow-trigger.md`

```markdown
# Flow Trigger: Meu_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Flow | XML |
| TriggerType | RecordAfterSave | XML |
| Object | Pedido__c | XML |

## Condições

- `Status__c` EqualTo stringValue=Aprovado
- filterLogic: and

_Fonte: XML_
```

### `saida/docs/doc-org-101126/doc-tela-cadastro-flow.md`

```markdown
# Flow: Tela_Cadastro

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Tela_Cadastro | XML |
| MasterLabel | Tela Cadastro | XML |
| ApiVersion | 67.0 | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

Não aplicável

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |
```

### `saida/docs/doc-org-101126/doc-tela-cadastro-dados-cliente-flow-screen.md`

```markdown
# Flow Screen: Dados_Cliente

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Dados_Cliente | XML |
| Label | Dados do Cliente | XML |
| Flow | Tela_Cadastro | XML |

## Campos da tela

| Campo | Tipo | Obrigatório | Fonte |
|---|---|---|---|
| Nome | InputField | true | XML |
| Observacao | LargeTextArea | Não informado | XML |
```

### `saida/docs/doc-org-101126/doc-minha-eca-external-client-app.md`

```markdown
# External Client App: Minha_ECA

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_ECA | XML |
| Label | Minha ECA | XML |
| ApiVersion | Não aplicável | XML |

## Componentes relacionados

| Componente | Metadata Type | Fonte |
|---|---|---|
| Minha_ECA_plcy | ExtlClntAppConfigurablePolicies | XML |
| Minha_ECA_oauthPlcy | ExtlClntAppOauthConfigurablePolicies | XML |
| Minha_ECA_oauth | ExtlClntAppOauthSettings | XML |

## Pastas relacionadas

| Pasta | Finalidade | Fonte |
|---|---|---|
| externalClientApps | ExternalClientApplication | XML |
| extlClntAppOauthPolicies | ExtlClntAppOauthConfigurablePolicies | XML |
| extlClntAppOauthSettings | ExtlClntAppOauthSettings | XML |
| extlClntAppPolicies | ExtlClntAppConfigurablePolicies | XML |
```

### `saida/docs/doc-org-101126/doc-minha-ec-external-credential.md`

```markdown
# External Credential: Minha_EC

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_EC | XML |
| Label | Minha EC | XML |
| AuthenticationProtocol | Custom | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0pt000000000001AAA | Objeto interno |
| DeveloperName | Minha_EC | Objeto interno |
| MasterLabel | Minha EC | Objeto interno |
| CreatedDate | 2026-09-01T12:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T12:00:00.000+0000 | Objeto interno |
```

### `saida/docs/doc-org-101126/doc-meu-app-connected-app.md`

```markdown
# Connected App: Meu_App

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_App | XML |
| Label | Meu App | XML |
| ApiVersion | Não aplicável | XML |

## OAuth

| Propriedade | Valor | Fonte |
|---|---|---|
| callbackUrl | https://example.com/callback | XML |
| consumerKey | CHAVE_SIMULADA | XML |
| scopes | Api, RefreshToken | XML |
```

### `saida/docs/doc-org-101126/doc-pedido-c-custom-object.md`

```markdown
# Custom Object: Pedido__c

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Pedido__c | XML |
| Label | Pedido | XML |
| PluralLabel | Pedidos | XML |

## Custom Fields

| Field | Label | Type | Fonte |
|---|---|---|---|
| Status__c | Status | Picklist | XML |
| Valor__c | Valor | Currency | XML |

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Pedido__c.Padrao | RecordType | XML |
| Pedido__c.Valor_Positivo | ValidationRule | XML |
| Pedido__c.Imprimir_Pedido | WebLink | XML |
```

### `saida/docs/doc-org-101126/doc-config-mdt-custom-metadata.md`

```markdown
# Custom Metadata: Config__mdt

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Config__mdt | XML |
| Label | Config | XML |
| Visibility | Public | XML |

## Records

| Record | Label | Fonte |
|---|---|---|
| Config.Padrao | Config Padrao | XML |
| Config.Secundario | Config Secundario | XML |
```

