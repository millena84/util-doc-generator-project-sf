# Fixtures de teste (SIMULADAS)

Todos os arquivos desta pasta são **simulados** para testes automatizados.
Nenhum dado aqui veio de uma org real e nenhum deve ser usado como documentação.

- `bin/sf`: Salesforce CLI simulada (Python) usada pelos testes de pipeline.
- `org/`: respostas simuladas de `sf org list`, `sf org display` e `sf org list metadata-types`.
- `inventory/<Tipo>.json`: respostas simuladas de `sf org list metadata`.
- `source/`: XMLs em formato source usados pelo retrieve simulado.
- `query/<Objeto>.json`: respostas simuladas de `sf data query`.
- `source/triggers/` e `source/classes/PedidoTriggerHandler.cls`: triggers e handler simulados da Onda 02 (duas triggers em `Pedido__c`, para a seção de coexistência).
- `source/lwc/` e `source/classes/PedidoController.cls`: bundles LWC simulados da Onda 03 (página, Quick Action headless e tela de Flow) e o controller Apex que eles chamam. `pedidoPainel/__tests__/` existe só para provar que testes Jest são ignorados.
- `source/roles/`, `source/groups/` e `source/settings/Security.settings-meta.xml`: papéis (Diretoria → Vendas → Gerente_Vendas), grupo público e configurações de segurança simulados da Onda 05. O perfil `Admin` ganhou layouts, guia, horário e faixa de IP de login; `Integracao_API`, página Visualforce e guia; `PSG_Integracao`, um muting permission set.
- `source/flexipages/` e `source/applications/Vendas.app-meta.xml`: páginas Lightning simuladas da Onda 04 (página de registro com facet, Dynamic Forms, LWC com visibilidade, Flow e componente de namespace; página de app no formato antigo) e o app que ativa a página de registro (padrão do app e app + perfil). `Pedido__c` ganhou `actionOverrides` (padrão da org).
- Onda 06: `objects/Pedido_Evento__e/` (platform event e campos), `triggers/PedidoEventoTrigger` (assina o evento) e `PedidoChangeTrigger` (assina `Pedido__ChangeEvent`), `flows/Pedido_Evento_Flow` (Flow disparado pelo evento), `platformEventChannelMembers/` (canal padrão e canal customizado com enriquecimento e filtro) e `platformEventSubscriberConfigs/` (usuário sentinela que nunca pode aparecer nos documentos). `PedidoController.enviar` publica o evento; `pedidoTelaFlow` assina por `lightning/empApi`.
- `mvp-complete/`: camada usada no cenário `mvp_complete` (`FAKE_SF_SCENARIO=mvp_complete`). Tem prioridade sobre as fixtures base e acrescenta componentes para os tipos do MVP que, na base, ficam sem componentes: ExtlClntAppConfigurablePolicies, ExtlClntAppOauthConfigurablePolicies, WebLink e dados internos de ExternalCredential.

### Origem dos campos dos XMLs simulados novos

O acesso direto a developer.salesforce.com não estava disponível no ambiente da verificação (2026-10-11). Por isso os campos foram conferidos em trechos da Metadata API Developer Guide retornados pela busca e em arquivos reais recuperados de orgs, publicados no GitHub:

| Arquivo | Campos | Referência |
|---|---|---|
| `extlClntAppPolicies/Minha_ECA_plcy.ecaPlcy-meta.xml` | `externalClientApplication` e `isEnabled` (obrigatórios), `isOauthPluginEnabled`, `label`, `startPage` | Metadata API: [ExtlClntAppConfigurablePolicies](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_extlclntappconfigurablepolicies.htm); arquivo real em [lorranmonteiro/my-salesforce-playground#9](https://github.com/lorranmonteiro/my-salesforce-playground/pull/9) |
| `extlClntAppOauthPolicies/Minha_ECA_oauthPlcy.ecaOauthPlcy-meta.xml` | `permittedUsersPolicyType` (`AllSelfAuthorized` / `AdminApprovedPreAuthorized`); demais campos iguais ao exemplo `default` do guia | Metadata API: [ExtlClntAppOauthConfigurablePolicies](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_extlclntappoauthconfigurablepolicies.htm); exemplo em [flxbl-io/external-client-apps-guide](https://github.com/flxbl-io/external-client-apps-guide) (fonte não oficial) |
| `objects/Pedido__c/webLinks/Imprimir_Pedido.webLink-meta.xml` | `availability`, `openType` e `protected` (obrigatórios), `displayType`, `linkType`, `masterLabel`, `url`. `openType=replace`, porque `newWindow` exige `height`. | Metadata API: [WebLink](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_weblink.htm) |

Os XMLs base `Minha_ECA.eca-meta.xml` e `Minha_ECA_oauth.ecaOauth-meta.xml` usam campos que também aparecem em um arquivo real ([onyx-dot-app/onyx#14953](https://github.com/onyx-dot-app/onyx/pull/14953)).

**Pendente:** abrir as três páginas da Metadata API linkadas acima e conferir a tabela completa de campos da API 67.0, principalmente os campos de `ExtlClntAppOauthConfigurablePolicies` que vieram só da fonte não oficial.

O token em `org/org-display.json` é um valor fictício.
