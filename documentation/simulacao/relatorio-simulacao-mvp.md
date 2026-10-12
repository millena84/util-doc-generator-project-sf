# Relatório de simulação — todas as documentações do MVP

> **SIMULADO.** CLI `sf` simulada (`tests/fixtures/bin/sf`, cenário `mvp_complete`) e Metadata API simulada. Nenhum dado veio de uma org real. Gerado por `python3 -m tests.simulate_mvp`.

- Execução: `run-20261012-031718` — status **SUCCESS** — código de saída `0`
- Org: `dev` — API `67.0`
- Cobertura: **COMPLETE** — 12 documentada(s) de 12 no escopo; lacunas: 0 (nenhuma)

## 1. Saída no terminal

```
[03:17:18] INFO  Escopo ALL: {'Certificate': ['*'], 'ConnectedApp': ['*'], 'CustomMetadata': ['*'], 'CustomObject': ['*'], 'ExternalClientApp': ['*'], 'ExternalCredential': ['*'], 'Flow': ['*'], 'NamedCredential': ['*'], 'RemoteSiteSetting': ['*']}
[03:17:18] INFO  Passo 1: Salesforce CLI 2.60.0 (mínima 2.0.0)
[03:17:18] INFO  Passo 2: alias 'dev' autenticado
[03:17:18] INFO  Passo 3: usuario.simulado@example.com conectado; API 67.0 (detectada 67.0, fonte: sf org display)
[03:17:18] INFO  Passo 3b: org 00D000000000000AAA aprovada (approvedOrgs)
[03:17:18] INFO  Passo 4: grupos habilitados: Flow, ExternalClientApp, ExternalCredential, ConnectedApp, CustomObject, CustomMetadata, NamedCredential, RemoteSiteSetting, Certificate
[03:17:18] INFO  Passo 6: Flow -> 3 componente(s)
[03:17:18] INFO  Passo 6: FlowDefinition -> 1 componente(s)
[03:17:19] INFO  Passo 6: ExternalClientApplication -> 1 componente(s)
[03:17:19] INFO  Passo 6: ExtlClntAppOauthSettings -> 2 componente(s)
[03:17:19] INFO  Passo 6: ExtlClntAppConfigurablePolicies -> 1 componente(s)
[03:17:19] INFO  Passo 6: ExtlClntAppOauthConfigurablePolicies -> 1 componente(s)
[03:17:19] INFO  Passo 6: ExternalCredential -> 1 componente(s)
[03:17:19] INFO  Passo 6: ConnectedApp -> 1 componente(s)
[03:17:19] INFO  Passo 6: CustomObject -> 3 componente(s)
[03:17:19] INFO  Passo 6: CustomMetadata -> 2 componente(s)
[03:17:19] INFO  Passo 6: NamedCredential -> 2 componente(s)
[03:17:19] INFO  Passo 6: RemoteSiteSetting -> 1 componente(s)
[03:17:19] INFO  Passo 6: Certificate -> 1 componente(s)
[03:17:19] INFO  Flow:Flow:Meu_Flow: processando
[03:17:19] INFO  Flow:Flow:Meu_Flow: SUCCESS -> saida/docs/doc-org-101226/doc-meu-flow-flow.md
[03:17:19] INFO  Flow:Flow:Processa_Pedido: processando
[03:17:19] INFO  Flow:Flow:Processa_Pedido: SUCCESS -> saida/docs/doc-org-101226/doc-processa-pedido-flow.md
[03:17:19] INFO  Flow:Flow:Tela_Cadastro: processando
[03:17:19] INFO  Flow:Flow:Tela_Cadastro: SUCCESS -> saida/docs/doc-org-101226/doc-tela-cadastro-flow.md
[03:17:19] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: processando
[03:17:19] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: SUCCESS -> saida/docs/doc-org-101226/doc-minha-eca-external-client-app.md
[03:17:19] INFO  ExternalCredential:ExternalCredential:Minha_EC: processando
[03:17:20] INFO  ExternalCredential:ExternalCredential:Minha_EC: SUCCESS -> saida/docs/doc-org-101226/doc-minha-ec-external-credential.md
[03:17:20] INFO  ConnectedApp:ConnectedApp:Meu_App: processando
[03:17:20] INFO  ConnectedApp:ConnectedApp:Meu_App: SUCCESS -> saida/docs/doc-org-101226/doc-meu-app-connected-app.md
[03:17:20] INFO  CustomObject:CustomObject:Pedido__c: processando
[03:17:20] INFO  CustomObject:CustomObject:Pedido__c: SUCCESS -> saida/docs/doc-org-101226/doc-pedido-c-custom-object.md
[03:17:20] INFO  CustomMetadata:CustomMetadata:Config__mdt: processando
[03:17:20] INFO  CustomMetadata:CustomMetadata:Config__mdt: SUCCESS -> saida/docs/doc-org-101226/doc-config-mdt-custom-metadata.md
[03:17:20] INFO  NamedCredential:NamedCredential:Minha_NC: processando
[03:17:20] INFO  NamedCredential:NamedCredential:Minha_NC: SUCCESS -> saida/docs/doc-org-101226/doc-minha-nc-named-credential.md
[03:17:20] INFO  NamedCredential:NamedCredential:NC_Legada: processando
[03:17:20] INFO  NamedCredential:NamedCredential:NC_Legada: SUCCESS -> saida/docs/doc-org-101226/doc-nc-legada-named-credential.md
[03:17:20] INFO  RemoteSiteSetting:RemoteSiteSetting:Meu_Site: processando
[03:17:20] INFO  RemoteSiteSetting:RemoteSiteSetting:Meu_Site: SUCCESS -> saida/docs/doc-org-101226/doc-meu-site-remote-site-setting.md
[03:17:20] INFO  Certificate:Certificate:Meu_Certificado: processando
[03:17:20] INFO  Certificate:Certificate:Meu_Certificado: SUCCESS -> saida/docs/doc-org-101226/doc-meu-certificado-certificate.md
[03:17:20] INFO  Execução run-20261012-031718 finalizada: SUCCESS {'SUCCESS': 12}
[03:17:20] INFO  Cobertura: COMPLETE — 12 documentada(s) de 12 no escopo; lacunas: 0
[03:17:20] INFO  Log: runs/run-20261012-031718.json
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
| 12 | 6 | `sf org list metadata --metadata-type ConnectedApp --target-org dev --api-version 67.0 --json` |
| 13 | 6 | `sf org list metadata --metadata-type CustomObject --target-org dev --api-version 67.0 --json` |
| 14 | 6 | `sf org list metadata --metadata-type CustomMetadata --target-org dev --api-version 67.0 --json` |
| 15 | 6 | `sf org list metadata --metadata-type NamedCredential --target-org dev --api-version 67.0 --json` |
| 16 | 6 | `sf org list metadata --metadata-type RemoteSiteSetting --target-org dev --api-version 67.0 --json` |
| 17 | 6 | `sf org list metadata --metadata-type Certificate --target-org dev --api-version 67.0 --json` |
| 18 | 7 | `sf project retrieve start --metadata Flow:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 19 | 7 | `sf project retrieve start --metadata FlowDefinition:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 20 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Meu_Flow' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 21 | 7 | `sf project retrieve start --metadata Flow:Processa_Pedido --target-org dev --api-version 67.0 --json` |
| 22 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Processa_Pedido' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 23 | 7 | `sf project retrieve start --metadata Flow:Tela_Cadastro --target-org dev --api-version 67.0 --json` |
| 24 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Tela_Cadastro' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 25 | 7 | `sf project retrieve start --metadata ExternalClientApplication:Minha_ECA --target-org dev --api-version 67.0 --json` |
| 26 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Minha_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 27 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Outra_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 28 | 7 | `sf project retrieve start --metadata ExtlClntAppConfigurablePolicies:Minha_ECA_plcy --target-org dev --api-version 67.0 --json` |
| 29 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthConfigurablePolicies:Minha_ECA_oauthPlcy --target-org dev --api-version 67.0 --json` |
| 30 | 7 | `sf project retrieve start --metadata ExternalCredential:Minha_EC --target-org dev --api-version 67.0 --json` |
| 31 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, CreatedDate, LastModifiedDate FROM ExternalCredential WHERE DeveloperName = 'Minha_EC' --target-org dev --api-version 67.0 --json` |
| 32 | 7 | `sf project retrieve start --metadata ConnectedApp:Meu_App --target-org dev --api-version 67.0 --json` |
| 33 | 7 | `sf project retrieve start --metadata CustomObject:Pedido__c --target-org dev --api-version 67.0 --json` |
| 34 | 7 | `sf project retrieve start --metadata CustomObject:Config__mdt --target-org dev --api-version 67.0 --json` |
| 35 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Padrao --target-org dev --api-version 67.0 --json` |
| 36 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Secundario --target-org dev --api-version 67.0 --json` |
| 37 | 7 | `sf project retrieve start --metadata NamedCredential:Minha_NC --target-org dev --api-version 67.0 --json` |
| 38 | 7 | `sf project retrieve start --metadata NamedCredential:NC_Legada --target-org dev --api-version 67.0 --json` |
| 39 | 7 | `sf project retrieve start --metadata RemoteSiteSetting:Meu_Site --target-org dev --api-version 67.0 --json` |
| 40 | 7 | `sf project retrieve start --metadata Certificate:Meu_Certificado --target-org dev --api-version 67.0 --json` |

O passo 5 (`describeValueType`) é SOAP direto na Metadata API, fora da CLI; o passo 8 (XML → JSON) e o passo 10 (Markdown) são locais.

## 3. Situação por metadata type

| Metadata type | Habilitado (4) | Schema (5) | Inventário (6) | Componentes |
|---|---|---|---|---|
| Certificate | ENABLED | SUCCESS | SUCCESS | 1 |
| ConnectedApp | ENABLED | SUCCESS | SUCCESS | 1 |
| CustomField | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| CustomMetadata | ENABLED | SUCCESS | SUCCESS | 2 |
| CustomObject | ENABLED | SUCCESS | SUCCESS | 3 |
| ExternalClientApplication | ENABLED | SUCCESS | SUCCESS | 1 |
| ExternalCredential | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthSettings | ENABLED | SUCCESS | SUCCESS | 2 |
| Flow | ENABLED | SUCCESS | SUCCESS | 3 |
| FlowDefinition | ENABLED | SUCCESS | SUCCESS | 1 |
| NamedCredential | ENABLED | SUCCESS | SUCCESS | 2 |
| RecordType | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| RemoteSiteSetting | ENABLED | SUCCESS | SUCCESS | 1 |
| ValidationRule | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| WebLink | ENABLED | SUCCESS | via retrieve do CustomObject | — |

## 4. Documentos gerados (passo 10)

| Documento | Modelo | Principal | Relacionados no documento | Status |
|---|---|---|---|---|
| `doc-meu-flow-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Meu_Flow | Meu_Flow (FlowDefinition) | SUCCESS |
| `doc-meu-flow-flow-trigger.md` | `modelo-doc-flow-trigger-vapi-67.md` | Flow:Meu_Flow | (subdocumento) | SUCCESS |
| `doc-processa-pedido-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Processa_Pedido | — | SUCCESS |
| `doc-processa-pedido-flow-autolaunched.md` | `modelo-doc-flow-autolaunched-vapi-67.md` | Flow:Processa_Pedido | (subdocumento) | SUCCESS |
| `doc-tela-cadastro-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Tela_Cadastro | — | SUCCESS |
| `doc-tela-cadastro-dados-cliente-flow-screen.md` | `modelo-doc-flow-screen-vapi-67.md` | Flow:Tela_Cadastro | (subdocumento) | SUCCESS |
| `doc-minha-eca-external-client-app.md` | `modelo-doc-cea-vapi-67.md` | ExternalClientApplication:Minha_ECA | Minha_ECA_oauth (ExtlClntAppOauthSettings), Minha_ECA_plcy (ExtlClntAppConfigurablePolicies), Minha_ECA_oauthPlcy (ExtlClntAppOauthConfigurablePolicies) | SUCCESS |
| `doc-minha-ec-external-credential.md` | `modelo-doc-external-credential-vapi-67.md` | ExternalCredential:Minha_EC | — | SUCCESS |
| `doc-meu-app-connected-app.md` | `modelo-doc-connectedapp-vapi-67.md` | ConnectedApp:Meu_App | — | SUCCESS |
| `doc-pedido-c-custom-object.md` | `modelo-doc-custom-object-vapi-67.md` | CustomObject:Pedido__c | Pedido__c.Status__c (CustomField), Pedido__c.Valor__c (CustomField), Pedido__c.Padrao (RecordType), Pedido__c.Valor_Positivo (ValidationRule), Pedido__c.Imprimir_Pedido (WebLink) | SUCCESS |
| `doc-config-mdt-custom-metadata.md` | `modelo-doc-custom-metadata-vapi-67.md` | CustomMetadata:Config__mdt | Config.Padrao (CustomMetadata), Config.Secundario (CustomMetadata), Config__mdt.Ativo__c (CustomField), Config__mdt.Chave_API__c (CustomField) | SUCCESS |
| `doc-minha-nc-named-credential.md` | `modelo-doc-named-credential-vapi-67.md` | NamedCredential:Minha_NC | Minha_EC (ExternalCredential) | SUCCESS |
| `doc-nc-legada-named-credential.md` | `modelo-doc-named-credential-vapi-67.md` | NamedCredential:NC_Legada | — | SUCCESS |
| `doc-meu-site-remote-site-setting.md` | `modelo-doc-remote-site-setting-vapi-67.md` | RemoteSiteSetting:Meu_Site | — | SUCCESS |
| `doc-meu-certificado-certificate.md` | `modelo-doc-certificate-vapi-67.md` | Certificate:Meu_Certificado | — | SUCCESS |

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
    "Certificate": {
      "directoryName": "certs",
      "suffix": "crt",
      "inFolder": false,
      "metaFile": true,
      "childXmlNames": []
    },
    "ConnectedApp": {
      "directoryName": "connectedApps",
      "suffix": "connectedApp",
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
  "count": 3,
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
      "fullName": "Processa_Pedido",
      "type": "Flow",
      "fileName": "x/Processa_Pedido",
      "id": "000000000000000AAA",
      "namespacePrefix": "",
... (14 linhas omitidas)
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
        "filePath": "/tmp/sfdocs-retrieve-6ojx2unr/force-app/main/default/flows/Meu_Flow.flow-meta.xml"
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
    ],
    "redacted": []
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
catalog/org-dev/api-v67/schemas/certificate.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/certificate.schema.json
catalog/org-dev/api-v67/schemas/connected-app.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/connected-app.schema.json
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
inventory/org-dev/api-v67/certificates/components/certs/Meu_Certificado.crt
inventory/org-dev/api-v67/certificates/components/certs/Meu_Certificado.crt-meta.xml
inventory/org-dev/api-v67/certificates/inventory.index.json
inventory/org-dev/api-v67/certificates/inventory.raw.json
inventory/org-dev/api-v67/certificates/normalized/meu-certificado.json
inventory/org-dev/api-v67/certificates/retrieve/meu-certificado.raw.json
inventory/org-dev/api-v67/connected-apps/components/connectedApps/Meu_App.connectedApp-meta.xml
inventory/org-dev/api-v67/connected-apps/inventory.index.json
inventory/org-dev/api-v67/connected-apps/inventory.raw.json
inventory/org-dev/api-v67/connected-apps/normalized/meu-app.json
inventory/org-dev/api-v67/connected-apps/retrieve/meu-app.raw.json
inventory/org-dev/api-v67/custom-metadata/components/customMetadata/Config.Padrao.md-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/customMetadata/Config.Secundario.md-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/objects/Config__mdt/Config__mdt.object-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/objects/Config__mdt/fields/Ativo__c.field-meta.xml
inventory/org-dev/api-v67/custom-metadata/components/objects/Config__mdt/fields/Chave_API__c.field-meta.xml
inventory/org-dev/api-v67/custom-metadata/inventory.index.json
inventory/org-dev/api-v67/custom-metadata/inventory.raw.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-mdt-ativo-c.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-mdt-chave-api-c.json
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
inventory/org-dev/api-v67/flows/components/flows/Processa_Pedido.flow-meta.xml
inventory/org-dev/api-v67/flows/components/flows/Tela_Cadastro.flow-meta.xml
inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json
inventory/org-dev/api-v67/flows/internal-data/processa-pedido.raw.json
inventory/org-dev/api-v67/flows/internal-data/tela-cadastro.raw.json
inventory/org-dev/api-v67/flows/inventory.index.json
inventory/org-dev/api-v67/flows/inventory.raw.json
inventory/org-dev/api-v67/flows/normalized/meu-flow.json
inventory/org-dev/api-v67/flows/normalized/processa-pedido.json
inventory/org-dev/api-v67/flows/normalized/tela-cadastro.json
inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json
inventory/org-dev/api-v67/flows/retrieve/processa-pedido.raw.json
inventory/org-dev/api-v67/flows/retrieve/tela-cadastro.raw.json
inventory/org-dev/api-v67/named-credentials/components/namedCredentials/Minha_NC.namedCredential-meta.xml
inventory/org-dev/api-v67/named-credentials/components/namedCredentials/NC_Legada.namedCredential-meta.xml
inventory/org-dev/api-v67/named-credentials/inventory.index.json
inventory/org-dev/api-v67/named-credentials/inventory.raw.json
inventory/org-dev/api-v67/named-credentials/normalized/minha-nc.json
inventory/org-dev/api-v67/named-credentials/normalized/nc-legada.json
inventory/org-dev/api-v67/named-credentials/retrieve/minha-nc.raw.json
inventory/org-dev/api-v67/named-credentials/retrieve/nc-legada.raw.json
inventory/org-dev/api-v67/remote-site-settings/components/remoteSiteSettings/Meu_Site.remoteSite-meta.xml
inventory/org-dev/api-v67/remote-site-settings/inventory.index.json
inventory/org-dev/api-v67/remote-site-settings/inventory.raw.json
inventory/org-dev/api-v67/remote-site-settings/normalized/meu-site.json
inventory/org-dev/api-v67/remote-site-settings/retrieve/meu-site.raw.json
runs/run-20261012-031718.json
saida/docs/doc-org-101226/.manifest.json
saida/docs/doc-org-101226/doc-config-mdt-custom-metadata.md
saida/docs/doc-org-101226/doc-meu-app-connected-app.md
saida/docs/doc-org-101226/doc-meu-certificado-certificate.md
saida/docs/doc-org-101226/doc-meu-flow-flow-trigger.md
saida/docs/doc-org-101226/doc-meu-flow-flow.md
saida/docs/doc-org-101226/doc-meu-site-remote-site-setting.md
saida/docs/doc-org-101226/doc-minha-ec-external-credential.md
saida/docs/doc-org-101226/doc-minha-eca-external-client-app.md
saida/docs/doc-org-101226/doc-minha-nc-named-credential.md
saida/docs/doc-org-101226/doc-nc-legada-named-credential.md
saida/docs/doc-org-101226/doc-pedido-c-custom-object.md
saida/docs/doc-org-101226/doc-processa-pedido-flow-autolaunched.md
saida/docs/doc-org-101226/doc-processa-pedido-flow.md
saida/docs/doc-org-101226/doc-tela-cadastro-dados-cliente-flow-screen.md
saida/docs/doc-org-101226/doc-tela-cadastro-flow.md
```

## 7. Conteúdo dos documentos finais

### `saida/docs/doc-org-101226/doc-meu-flow-flow.md`

```markdown
# Flow: Meu_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Flow | XML |
| MasterLabel | Meu Flow | XML |
| ProcessType | AutoLaunchedFlow | XML |
| ApiVersion | 67.0 | XML |
| Description | Não informado | XML |
| Status (versão recuperada) | Active | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

**FlowDefinition: Meu_Flow**

_Arquivo: `inventory/org-dev/api-v67/flow-definitions/components/flowDefinitions/Meu_Flow.flowDefinition-meta.xml` · sha256 `b5580d18adf4bdb1…`_

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

### `saida/docs/doc-org-101226/doc-meu-flow-flow-trigger.md`

```markdown
# Flow Trigger: Meu_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Flow | XML |
| TriggerType | RecordAfterSave | XML |
| RecordTriggerType | Update | XML |
| Object | Pedido__c | XML |

## Condições

- `Status__c` EqualTo stringValue=Aprovado
- filterLogic: and

_Fonte: XML_
```

### `saida/docs/doc-org-101226/doc-processa-pedido-flow.md`

```markdown
# Flow: Processa_Pedido

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Processa_Pedido | XML |
| MasterLabel | Processa Pedido | XML |
| ProcessType | AutoLaunchedFlow | XML |
| ApiVersion | 67.0 | XML |
| Description | Processa pedidos \| lote<br>linha 2 – ação ✓ çãõ; Texto longo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx | XML |
| Status (versão recuperada) | Active | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

Não aplicável

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |
```

### `saida/docs/doc-org-101226/doc-processa-pedido-flow-autolaunched.md`

```markdown
# Autolaunched Flow: Processa_Pedido

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Processa_Pedido | XML |
| Label | Processa Pedido | XML |
| ProcessType | AutoLaunchedFlow | XML |
| ApiVersion | 67.0 | XML |
| Description | Processa pedidos \| lote<br>linha 2 – ação ✓ çãõ; Texto longo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx | XML |
| Status (versão recuperada) | Active | XML |

## Variáveis de entrada

| Variável | Tipo de dado | Objeto | Coleção | Fonte |
|---|---|---|---|---|
| recordId | String | Não informado | false | XML |
| pedidos | SObject | Pedido__c | true | XML |

## Variáveis de saída

| Variável | Tipo de dado | Objeto | Coleção | Fonte |
|---|---|---|---|---|
| sucesso | Boolean | Não informado | false | XML |
```

### `saida/docs/doc-org-101226/doc-tela-cadastro-flow.md`

```markdown
# Flow: Tela_Cadastro

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Tela_Cadastro | XML |
| MasterLabel | Tela Cadastro | XML |
| ProcessType | Flow | XML |
| ApiVersion | 67.0 | XML |
| Description | Não informado | XML |
| Status (versão recuperada) | Draft | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

Não aplicável

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |
```

### `saida/docs/doc-org-101226/doc-tela-cadastro-dados-cliente-flow-screen.md`

```markdown
# Flow Screen: Dados_Cliente

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Dados_Cliente | XML |
| Label | Dados do Cliente | XML |
| Flow | Tela_Cadastro | XML |
| AllowBack | Não informado | XML |
| AllowFinish | Não informado | XML |
| AllowPause | Não informado | XML |
| ShowHeader | Não informado | XML |
| ShowFooter | Não informado | XML |

## Campos da tela

| Campo | Tipo | Obrigatório | Fonte |
|---|---|---|---|
| Nome | InputField | true | XML |
| Observacao | LargeTextArea | Não informado | XML |
```

### `saida/docs/doc-org-101226/doc-minha-eca-external-client-app.md`

```markdown
# External Client App: Minha_ECA

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_ECA | XML |
| Label | Minha ECA | XML |
| ApiVersion | Não aplicável | XML |
| Description | Não informado | XML |
| DistributionState | Local | XML |
| IsProtected | false | XML |

## Configuração OAuth

**ExtlClntAppOauthSettings: Minha_ECA_oauth**

_Arquivo: `inventory/org-dev/api-v67/extl-clnt-app-oauth-settings/components/extlClntAppOauthSettings/Minha_ECA_oauth.ecaOauth-meta.xml` · sha256 `0876b78309cb2972…`_

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_ECA_oauth | XML |
| Label | Minha ECA oauth | XML |
| ExternalClientApplication | Minha_ECA | XML |
| CommaSeparatedOauthScopes | Api, RefreshToken | XML |

_Fonte: XML_

## Políticas OAuth

**ExtlClntAppOauthConfigurablePolicies: Minha_ECA_oauthPlcy**

_Arquivo: `inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/components/extlClntAppOauthPolicies/Minha_ECA_oauthPlcy.ecaOauthPlcy-meta.xml` · sha256 `4686e2b22fdc507c…`_

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_ECA_oauthPlcy | XML |
| Label | Minha_ECA_oauthPlcy | XML |
| ExternalClientApplication | Minha_ECA | XML |

_Fonte: XML_

## Políticas do app

**ExtlClntAppConfigurablePolicies: Minha_ECA_plcy**

_Arquivo: `inventory/org-dev/api-v67/extl-clnt-app-configurable-policies/components/extlClntAppPolicies/Minha_ECA_plcy.ecaPlcy-meta.xml` · sha256 `4036b9fb899849a2…`_

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_ECA_plcy | XML |
| Label | Minha_ECA_plcy | XML |
| ExternalClientApplication | Minha_ECA | XML |
| IsEnabled | true | XML |
| IsOauthPluginEnabled | true | XML |
| StartPage | None | XML |
| StartUrl | Não informado | XML |

_Fonte: XML_

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

### `saida/docs/doc-org-101226/doc-minha-ec-external-credential.md`

```markdown
# External Credential: Minha_EC

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_EC | XML |
| Label | Minha EC | XML |
| AuthenticationProtocol | Custom | XML |

## Parâmetros

| Parâmetro | Tipo | Grupo | Fonte |
|---|---|---|---|
| x-api-key | AuthHeader | DefaultGroup | XML |

## Principais

| Principal | Tipo | Sequência | Fonte |
|---|---|---|---|
| Principal_Integracao | NamedPrincipal | 1 | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0pt000000000001AAA | Objeto interno |
| DeveloperName | Minha_EC | Objeto interno |
| MasterLabel | Minha EC | Objeto interno |
| CreatedDate | 2026-09-01T12:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T12:00:00.000+0000 | Objeto interno |
```

### `saida/docs/doc-org-101226/doc-meu-app-connected-app.md`

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
| scopes | Api, RefreshToken | XML |
```

### `saida/docs/doc-org-101226/doc-pedido-c-custom-object.md`

```markdown
# Custom Object: Pedido__c

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Pedido__c | XML |
| Label | Pedido | XML |
| PluralLabel | Pedidos | XML |
| SharingModel | ReadWrite | XML |
| DeploymentStatus | Deployed | XML |

## Custom Fields

| Field | Label | Type | Fonte |
|---|---|---|---|
| Status__c | Status | Picklist | XML |
| Valor__c | Valor | Currency | XML |

## Validation Rules

| Regra | Ativa | Condição de erro | Mensagem de erro | Fonte |
|---|---|---|---|---|
| Pedido__c.Valor_Positivo | true | Valor__c < 0 | Valor deve ser positivo | XML |

## Record Types

| Record Type | Label | Ativo | Fonte |
|---|---|---|---|
| Pedido__c.Padrao | Padrão | true | XML |

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Pedido__c.Imprimir_Pedido | WebLink | XML |
```

### `saida/docs/doc-org-101226/doc-config-mdt-custom-metadata.md`

```markdown
# Custom Metadata: Config__mdt

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Config__mdt | XML |
| Label | Config | XML |
| PluralLabel | Configs | XML |
| Description | Não informado | XML |
| Visibility | Public | XML |

## Campos do tipo

| Field | Label | Type | Fonte |
|---|---|---|---|
| Ativo__c | Ativo | Checkbox | XML |
| Chave_API__c | Chave API | Text | XML |

## Records

| Record | Label | Protected | Fonte |
|---|---|---|---|
| Config.Padrao | Config Padrao | false | XML |
| Config.Secundario | Config Secundario | false | XML |
```

### `saida/docs/doc-org-101226/doc-minha-nc-named-credential.md`

```markdown
# Named Credential: Minha_NC

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_NC | XML |
| Label | Minha NC | XML |
| NamedCredentialType | SecuredEndpoint | XML |
| Description | NC sintética \| testes<br>segunda linha – ç | XML |

## Opções de callout

| Propriedade | Valor | Fonte |
|---|---|---|
| GenerateAuthorizationHeader | true | XML |
| AllowMergeFieldsInHeader | true | XML |
| AllowMergeFieldsInBody | false | XML |

## Parâmetros

| Parâmetro | Tipo | Fonte |
|---|---|---|
| Url | Url | XML |
| ExternalCredential | Authentication | XML |
| x-api-key | HttpHeader | XML |

## Credencial externa

**ExternalCredential: Minha_EC**

_Arquivo: `inventory/org-dev/api-v67/external-credentials/components/externalCredentials/Minha_EC.externalCredential-meta.xml` · sha256 `84d013436503b07b…`_

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Minha_EC | XML |
| Label | Minha EC | XML |
| AuthenticationProtocol | Custom | XML |

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Minha_EC | ExternalCredential | XML |
```

### `saida/docs/doc-org-101226/doc-nc-legada-named-credential.md`

```markdown
# Named Credential: NC_Legada

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | NC_Legada | XML |
| Label | NC Legada | XML |
| NamedCredentialType | Legacy | XML |
| Description | Não informado | XML |

## Opções de callout

| Propriedade | Valor | Fonte |
|---|---|---|
| GenerateAuthorizationHeader | true | XML |
| AllowMergeFieldsInHeader | false | XML |
| AllowMergeFieldsInBody | false | XML |

## Parâmetros

| Parâmetro | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Credencial externa

Não aplicável

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |
```

### `saida/docs/doc-org-101226/doc-meu-site-remote-site-setting.md`

```markdown
# Remote Site Setting: Meu_Site

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Site | XML |
| Url | https://api.example.com | XML |
| IsActive | true | XML |
| DisableProtocolSecurity | false | XML |
| Description | Site remoto sintético | XML |
```

### `saida/docs/doc-org-101226/doc-meu-certificado-certificate.md`

```markdown
# Certificate: Meu_Certificado

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Certificado | XML |
| MasterLabel | Meu Certificado | XML |
| CaSigned | false | XML |
| KeySize | 2048 | XML |
| ExpirationDate | 2027-10-12T00:00:00.000Z | XML |
| PrivateKeyExportable | true | XML |
| EncryptedWithPlatformEncryption | false | XML |
```

