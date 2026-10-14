# Fixtures da Fase 2 (integration_discovery) — SIMULADAS

JSONs normalizados no **mesmo formato** que o Utilitário 1 grava em `inventory/org-<alias>/api-v<N>/<pasta>/normalized/`
(chaves `metadataType`, `fullName`, `role`, `source`, `schema`, `fields`, `data`; estrutura de `data.apex` igual à do parser
Apex/trigger). Nada aqui veio de uma org real.

Cenário (integração com o RH):
- `ColaboradorTrigger` dispara em `Colaborador__c`, invoca `IntegracaoRHService` e lê `Endpoint_Config__mdt`;
- o record `Endpoint_Config.Producao` aponta para a Named Credential `RH_Endpoint`;
- o permission set `IntegracaoRH_User` libera `IntegracaoRHService` **e** `SAPOrderSync` (ponte: não funde clusters);
- a Connected App `IntegracaoRH` usa o certificado `IntegracaoRH_Cert` e cita o permission set;
- `RH_Remote_Site` não é referenciado (órfão com dica de nome);
- `IntegracaoRH_ECA` está no CSV sem JSON (`NORMALIZED_JSON_NOT_FOUND`).

Como no Utilitário 1, o normalizado **não** guarda o corpo do código: a chamada `callout:RH_Endpoint` não aparece. A Named
Credential só se liga ao cluster pelo record de Custom Metadata. A menção em `data.apex.description` vira menção não verificada.

Valores `SENTINELA*` / `sentinela*` (URLs, cabeçalhos, valores de Custom Metadata, consumerKey) nunca podem aparecer nas saídas.
