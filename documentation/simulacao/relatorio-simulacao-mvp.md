# Relatório de simulação — todas as documentações do MVP

> **SIMULADO.** CLI `sf` simulada (`tests/fixtures/bin/sf`, cenário `mvp_complete`) e Metadata API simulada. Nenhum dado veio de uma org real. Gerado por `python3 -m tests.simulate_mvp`.

- Execução: `run-20261013-203232` — status **SUCCESS** — código de saída `0`
- Org: `dev` — API `67.0`
- Cobertura: **COMPLETE** — 60 documentada(s) de 60 no escopo; lacunas: 0 (nenhuma)

## 1. Saída no terminal

```
[20:32:32] INFO  Seleção ALL: {'ApexClass': ['ALL'], 'ApexTrigger': ['ALL'], 'AssignmentRules': ['ALL'], 'AutoResponseRules': ['ALL'], 'BusinessProcess': ['ALL'], 'Certificate': ['ALL'], 'ChangeDataCapture': ['ALL'], 'ConnectedApp': ['ALL'], 'CustomMetadata': ['ALL'], 'CustomObject': ['ALL'], 'CustomSite': ['ALL'], 'EscalationRules': ['ALL'], 'ExperienceBundle': ['ALL'], 'ExternalClientApp': ['ALL'], 'ExternalCredential': ['ALL'], 'FlexiPage': ['ALL'], 'Flow': ['ALL'], 'LeadConvertSettings': ['ALL'], 'LightningComponentBundle': ['ALL'], 'NamedCredential': ['ALL'], 'Network': ['ALL'], 'OmniDataTransform': ['ALL'], 'OmniIntegrationProcedure': ['ALL'], 'OmniScript': ['ALL'], 'OmniUiCard': ['ALL'], 'OpportunitySplitType': ['ALL'], 'OrgSecurity': ['ALL'], 'PermissionSet': ['ALL'], 'PermissionSetGroup': ['ALL'], 'PlatformEvent': ['ALL'], 'Profile': ['ALL'], 'PublicGroup': ['ALL'], 'Queue': ['ALL'], 'RemoteSiteSetting': ['ALL'], 'Role': ['ALL'], 'SharingRules': ['ALL'], 'Territory2Model': ['ALL']}
[20:32:32] WARN  Verificação de Git indisponível (fora de repositório Git): proteção de versionamento não verificada
[20:32:32] INFO  Passo 1: Salesforce CLI 2.60.0 (mínima 2.0.0)
[20:32:32] INFO  Passo 2: alias 'dev' autenticado
[20:32:32] INFO  Passo 3: `sf org display` exibiu credenciais; gravado só o envelope sanitizado
[20:32:32] INFO  Passo 3: usuario.simulado@example.com conectado; API 67.0 (detectada 67.0, fonte: sf org display)
[20:32:32] INFO  Passo 3b: org 00D000000000000AAA aprovada (approvedOrgs)
[20:32:32] INFO  Passo 3c: token de acesso obtido via `sf org display` (não persistido)
[20:32:32] INFO  Passo 4: grupos habilitados: Flow, ExternalClientApp, ExternalCredential, ConnectedApp, CustomObject, CustomMetadata, NamedCredential, RemoteSiteSetting, Certificate, ApexClass, ApexTrigger, LightningComponentBundle, FlexiPage, PlatformEvent, ChangeDataCapture, AssignmentRules, AutoResponseRules, EscalationRules, Queue, BusinessProcess, LeadConvertSettings, Territory2Model, OpportunitySplitType, Network, CustomSite, ExperienceBundle, OmniDataTransform, OmniIntegrationProcedure, OmniScript, OmniUiCard, PermissionSet, Profile, PermissionSetGroup, SharingRules, Role, PublicGroup, OrgSecurity
[20:32:32] INFO  Passo 6: Flow -> 4 componente(s)
[20:32:32] INFO  Passo 6: FlowDefinition -> 1 componente(s)
[20:32:32] INFO  Passo 6: ExternalClientApplication -> 1 componente(s)
[20:32:32] INFO  Passo 6: ExtlClntAppOauthSettings -> 2 componente(s)
[20:32:32] INFO  Passo 6: ExtlClntAppConfigurablePolicies -> 1 componente(s)
[20:32:32] INFO  Passo 6: ExtlClntAppOauthConfigurablePolicies -> 1 componente(s)
[20:32:32] INFO  Passo 6: ExternalCredential -> 1 componente(s)
[20:32:32] INFO  Passo 6: ConnectedApp -> 1 componente(s)
[20:32:32] INFO  Passo 6: CustomObject -> 4 componente(s)
[20:32:32] INFO  Passo 6: CustomMetadata -> 2 componente(s)
[20:32:32] INFO  Passo 6: NamedCredential -> 2 componente(s)
[20:32:32] INFO  Passo 6: RemoteSiteSetting -> 1 componente(s)
[20:32:33] INFO  Passo 6: Certificate -> 1 componente(s)
[20:32:33] INFO  Passo 6: ApexClass -> 9 componente(s)
[20:32:33] INFO  Passo 6: ApexTrigger -> 4 componente(s)
[20:32:33] INFO  Passo 6: LightningComponentBundle -> 4 componente(s)
[20:32:33] INFO  Passo 6: FlexiPage -> 2 componente(s)
[20:32:33] INFO  Passo 6: PlatformEventChannelMember -> 2 componente(s)
[20:32:33] INFO  Passo 6: AssignmentRules -> 1 componente(s)
[20:32:33] INFO  Passo 6: AutoResponseRules -> 1 componente(s)
[20:32:33] INFO  Passo 6: EscalationRules -> 1 componente(s)
[20:32:33] INFO  Passo 6: Queue -> 1 componente(s)
[20:32:33] INFO  Passo 6: BusinessProcess -> 1 componente(s)
[20:32:33] INFO  Passo 6: Territory2Model -> 1 componente(s)
[20:32:33] INFO  Passo 6: Territory2 -> 2 componente(s)
[20:32:33] INFO  Passo 6: Territory2Rule -> 1 componente(s)
[20:32:33] INFO  Passo 6: OpportunitySplitType -> 1 componente(s)
[20:32:33] INFO  Passo 6: Network -> 1 componente(s)
[20:32:33] INFO  Passo 6: CustomSite -> 1 componente(s)
[20:32:33] INFO  Passo 6: ExperienceBundle -> 1 componente(s)
[20:32:33] INFO  Passo 6: OmniDataTransform -> 1 componente(s)
[20:32:33] INFO  Passo 6: OmniIntegrationProcedure -> 1 componente(s)
[20:32:33] INFO  Passo 6: OmniScript -> 1 componente(s)
[20:32:33] INFO  Passo 6: OmniUiCard -> 1 componente(s)
[20:32:33] INFO  Passo 6: PermissionSet -> 2 componente(s)
[20:32:33] INFO  Passo 6: Profile -> 3 componente(s)
[20:32:33] INFO  Passo 6: PermissionSetGroup -> 1 componente(s)
[20:32:33] INFO  Passo 6: SharingRules -> 1 componente(s)
[20:32:34] INFO  Passo 6: Role -> 3 componente(s)
[20:32:34] INFO  Passo 6: Group -> 1 componente(s)
[20:32:34] INFO  Passo 6: RecordType (conferência) -> 3 componente(s)
[20:32:34] INFO  Passo 6b: 10 fonte(s) de acesso; índice em inventory/org-dev/api-v67/access/access-index.json
[20:32:34] INFO  [1/60] Flow:Flow:Meu_Flow
[20:32:34] INFO  Flow:Flow:Meu_Flow: processando
[20:32:34] INFO  Flow:Flow:Meu_Flow: SUCCESS -> saida/docs/doc-dev-101326/doc-meu-flow-flow.md
[20:32:34] INFO  [2/60] Flow:Flow:Pedido_Evento_Flow
[20:32:34] INFO  Flow:Flow:Pedido_Evento_Flow: processando
[20:32:34] INFO  Flow:Flow:Pedido_Evento_Flow: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-evento-flow-flow.md
[20:32:34] INFO  [3/60] Flow:Flow:Processa_Pedido
[20:32:34] INFO  Flow:Flow:Processa_Pedido: processando
[20:32:34] INFO  Flow:Flow:Processa_Pedido: SUCCESS -> saida/docs/doc-dev-101326/doc-processa-pedido-flow.md
[20:32:34] INFO  [4/60] Flow:Flow:Tela_Cadastro
[20:32:34] INFO  Flow:Flow:Tela_Cadastro: processando
[20:32:34] INFO  Flow:Flow:Tela_Cadastro: SUCCESS -> saida/docs/doc-dev-101326/doc-tela-cadastro-flow.md
[20:32:34] INFO  [5/60] ExternalClientApp:ExternalClientApplication:Minha_ECA
[20:32:34] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: processando
[20:32:34] INFO  ExternalClientApp:ExternalClientApplication:Minha_ECA: SUCCESS -> saida/docs/doc-dev-101326/doc-minha-eca-external-client-app.md
[20:32:34] INFO  [6/60] ExternalCredential:ExternalCredential:Minha_EC
[20:32:34] INFO  ExternalCredential:ExternalCredential:Minha_EC: processando
[20:32:35] INFO  ExternalCredential:ExternalCredential:Minha_EC: SUCCESS -> saida/docs/doc-dev-101326/doc-minha-ec-external-credential.md
[20:32:35] INFO  [7/60] ConnectedApp:ConnectedApp:Meu_App
[20:32:35] INFO  ConnectedApp:ConnectedApp:Meu_App: processando
[20:32:35] INFO  ConnectedApp:ConnectedApp:Meu_App: SUCCESS -> saida/docs/doc-dev-101326/doc-meu-app-connected-app.md
[20:32:35] INFO  [8/60] CustomObject:CustomObject:Pedido__c
[20:32:35] INFO  CustomObject:CustomObject:Pedido__c: processando
[20:32:35] INFO  CustomObject:CustomObject:Pedido__c: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-c-custom-object.md
[20:32:35] INFO  [9/60] CustomMetadata:CustomMetadata:Config__mdt
[20:32:35] INFO  CustomMetadata:CustomMetadata:Config__mdt: processando
[20:32:35] INFO  CustomMetadata:CustomMetadata:Config__mdt: SUCCESS -> saida/docs/doc-dev-101326/doc-config-mdt-custom-metadata.md
[20:32:35] INFO  [10/60] NamedCredential:NamedCredential:Minha_NC
[20:32:35] INFO  NamedCredential:NamedCredential:Minha_NC: processando
[20:32:35] INFO  NamedCredential:NamedCredential:Minha_NC: SUCCESS -> saida/docs/doc-dev-101326/doc-minha-nc-named-credential.md
[20:32:35] INFO  [11/60] NamedCredential:NamedCredential:NC_Legada
[20:32:35] INFO  NamedCredential:NamedCredential:NC_Legada: processando
[20:32:35] INFO  NamedCredential:NamedCredential:NC_Legada: SUCCESS -> saida/docs/doc-dev-101326/doc-nc-legada-named-credential.md
[20:32:35] INFO  [12/60] RemoteSiteSetting:RemoteSiteSetting:Meu_Site
[20:32:35] INFO  RemoteSiteSetting:RemoteSiteSetting:Meu_Site: processando
[20:32:35] INFO  RemoteSiteSetting:RemoteSiteSetting:Meu_Site: SUCCESS -> saida/docs/doc-dev-101326/doc-meu-site-remote-site-setting.md
[20:32:35] INFO  [13/60] Certificate:Certificate:Meu_Certificado
[20:32:35] INFO  Certificate:Certificate:Meu_Certificado: processando
[20:32:35] INFO  Certificate:Certificate:Meu_Certificado: SUCCESS -> saida/docs/doc-dev-101326/doc-meu-certificado-certificate.md
[20:32:35] INFO  [14/60] ApexClass:ApexClass:AccountSyncQueueable
[20:32:35] INFO  ApexClass:ApexClass:AccountSyncQueueable: processando
[20:32:35] INFO  ApexClass:ApexClass:AccountSyncQueueable: SUCCESS -> saida/docs/doc-dev-101326/doc-accountsyncqueueable-apex-class.md
[20:32:35] INFO  [15/60] ApexClass:ApexClass:DailyOrderCleanupScheduler
[20:32:35] INFO  ApexClass:ApexClass:DailyOrderCleanupScheduler: processando
[20:32:36] INFO  ApexClass:ApexClass:DailyOrderCleanupScheduler: SUCCESS -> saida/docs/doc-dev-101326/doc-dailyordercleanupscheduler-apex-class.md
[20:32:36] INFO  [16/60] ApexClass:ApexClass:IntegrationAsyncHelper
[20:32:36] INFO  ApexClass:ApexClass:IntegrationAsyncHelper: processando
[20:32:36] INFO  ApexClass:ApexClass:IntegrationAsyncHelper: SUCCESS -> saida/docs/doc-dev-101326/doc-integrationasynchelper-apex-class.md
[20:32:36] INFO  [17/60] ApexClass:ApexClass:MultiRoleJob
[20:32:36] INFO  ApexClass:ApexClass:MultiRoleJob: processando
[20:32:36] INFO  ApexClass:ApexClass:MultiRoleJob: SUCCESS -> saida/docs/doc-dev-101326/doc-multirolejob-apex-class.md
[20:32:36] INFO  [18/60] ApexClass:ApexClass:OrderCleanupBatch
[20:32:36] INFO  ApexClass:ApexClass:OrderCleanupBatch: processando
[20:32:36] INFO  ApexClass:ApexClass:OrderCleanupBatch: SUCCESS -> saida/docs/doc-dev-101326/doc-ordercleanupbatch-apex-class.md
[20:32:36] INFO  [19/60] ApexClass:ApexClass:PedidoController
[20:32:36] INFO  ApexClass:ApexClass:PedidoController: processando
[20:32:36] INFO  ApexClass:ApexClass:PedidoController: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidocontroller-apex-class.md
[20:32:36] INFO  [20/60] ApexClass:ApexClass:PedidoService
[20:32:36] INFO  ApexClass:ApexClass:PedidoService: processando
[20:32:36] INFO  ApexClass:ApexClass:PedidoService: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidoservice-apex-class.md
[20:32:36] INFO  [21/60] ApexClass:ApexClass:PedidoTriggerHandler
[20:32:36] INFO  ApexClass:ApexClass:PedidoTriggerHandler: processando
[20:32:36] INFO  ApexClass:ApexClass:PedidoTriggerHandler: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidotriggerhandler-apex-class.md
[20:32:36] INFO  [22/60] AssignmentRules:AssignmentRules:Case
[20:32:36] INFO  AssignmentRules:AssignmentRules:Case: processando
[20:32:36] INFO  AssignmentRules:AssignmentRules:Case: SUCCESS -> saida/docs/doc-dev-101326/doc-case-assignment-rules.md
[20:32:36] INFO  [23/60] AutoResponseRules:AutoResponseRules:Case
[20:32:36] INFO  AutoResponseRules:AutoResponseRules:Case: processando
[20:32:36] INFO  AutoResponseRules:AutoResponseRules:Case: SUCCESS -> saida/docs/doc-dev-101326/doc-case-auto-response-rules.md
[20:32:36] INFO  [24/60] EscalationRules:EscalationRules:Case
[20:32:36] INFO  EscalationRules:EscalationRules:Case: processando
[20:32:36] INFO  EscalationRules:EscalationRules:Case: SUCCESS -> saida/docs/doc-dev-101326/doc-case-escalation-rules.md
[20:32:37] INFO  [25/60] BusinessProcess:BusinessProcess:Opportunity.Venda_Enterprise
[20:32:37] INFO  BusinessProcess:BusinessProcess:Opportunity.Venda_Enterprise: processando
[20:32:37] INFO  BusinessProcess:BusinessProcess:Opportunity.Venda_Enterprise: SUCCESS -> saida/docs/doc-dev-101326/doc-opportunity-venda-enterprise-business-process.md
[20:32:37] INFO  [26/60] LeadConvertSettings:LeadConvertSettings:LeadConvertSettings
[20:32:37] INFO  LeadConvertSettings:LeadConvertSettings:LeadConvertSettings: processando
[20:32:37] INFO  LeadConvertSettings:LeadConvertSettings:LeadConvertSettings: SUCCESS -> saida/docs/doc-dev-101326/doc-leadconvertsettings-lead-convert.md
[20:32:37] INFO  [27/60] Territory2Model:Territory2Model:Modelo_Vendas
[20:32:37] INFO  Territory2Model:Territory2Model:Modelo_Vendas: processando
[20:32:37] INFO  Territory2Model:Territory2Model:Modelo_Vendas: SUCCESS -> saida/docs/doc-dev-101326/doc-modelo-vendas-territory-model.md
[20:32:37] INFO  [28/60] OpportunitySplitType:OpportunitySplitType:Receita_Principal
[20:32:37] INFO  OpportunitySplitType:OpportunitySplitType:Receita_Principal: processando
[20:32:37] INFO  OpportunitySplitType:OpportunitySplitType:Receita_Principal: SUCCESS -> saida/docs/doc-dev-101326/doc-receita-principal-opportunity-split-type.md
[20:32:37] INFO  [29/60] Network:Network:Portal_Clientes
[20:32:37] INFO  Network:Network:Portal_Clientes: processando
[20:32:37] INFO  Network:Network:Portal_Clientes: SUCCESS -> saida/docs/doc-dev-101326/doc-portal-clientes-network.md
[20:32:37] INFO  [30/60] CustomSite:CustomSite:Portal_Clientes
[20:32:37] INFO  CustomSite:CustomSite:Portal_Clientes: processando
[20:32:37] INFO  CustomSite:CustomSite:Portal_Clientes: SUCCESS -> saida/docs/doc-dev-101326/doc-portal-clientes-site.md
[20:32:37] INFO  [31/60] PermissionSet:PermissionSet:Integracao_API
[20:32:37] INFO  PermissionSet:PermissionSet:Integracao_API: processando
[20:32:37] INFO  PermissionSet:PermissionSet:Integracao_API: SUCCESS -> saida/docs/doc-dev-101326/doc-integracao-api-permission-set.md
[20:32:37] INFO  [32/60] PermissionSet:PermissionSet:Leitura_Pedidos
[20:32:37] INFO  PermissionSet:PermissionSet:Leitura_Pedidos: processando
[20:32:37] INFO  PermissionSet:PermissionSet:Leitura_Pedidos: SUCCESS -> saida/docs/doc-dev-101326/doc-leitura-pedidos-permission-set.md
[20:32:37] INFO  [33/60] Profile:Profile:Admin
[20:32:37] INFO  Profile:Profile:Admin: processando
[20:32:38] INFO  Profile:Profile:Admin: SUCCESS -> saida/docs/doc-dev-101326/doc-admin-profile.md
[20:32:38] INFO  [34/60] Profile:Profile:Portal Clientes Profile
[20:32:38] INFO  Profile:Profile:Portal Clientes Profile: processando
[20:32:38] INFO  Profile:Profile:Portal Clientes Profile: SUCCESS -> saida/docs/doc-dev-101326/doc-portal-clientes-profile-profile.md
[20:32:38] INFO  [35/60] Profile:Profile:Vendas
[20:32:38] INFO  Profile:Profile:Vendas: processando
[20:32:38] INFO  Profile:Profile:Vendas: SUCCESS -> saida/docs/doc-dev-101326/doc-vendas-profile.md
[20:32:38] INFO  [36/60] PermissionSetGroup:PermissionSetGroup:PSG_Integracao
[20:32:38] INFO  PermissionSetGroup:PermissionSetGroup:PSG_Integracao: processando
[20:32:38] INFO  PermissionSetGroup:PermissionSetGroup:PSG_Integracao: SUCCESS -> saida/docs/doc-dev-101326/doc-psg-integracao-permission-set-group.md
[20:32:38] INFO  [37/60] PublicGroup:Group:Grupo_Suporte
[20:32:38] INFO  PublicGroup:Group:Grupo_Suporte: processando
[20:32:38] INFO  PublicGroup:Group:Grupo_Suporte: SUCCESS -> saida/docs/doc-dev-101326/doc-grupo-suporte-public-group.md
[20:32:39] INFO  [38/60] ApexTrigger:ApexTrigger:PedidoAuditoriaTrigger
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoAuditoriaTrigger: processando
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoAuditoriaTrigger: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidoauditoriatrigger-apex-trigger.md
[20:32:39] INFO  [39/60] ApexTrigger:ApexTrigger:PedidoChangeTrigger
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoChangeTrigger: processando
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoChangeTrigger: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidochangetrigger-apex-trigger.md
[20:32:39] INFO  [40/60] ApexTrigger:ApexTrigger:PedidoEventoTrigger
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoEventoTrigger: processando
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoEventoTrigger: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidoeventotrigger-apex-trigger.md
[20:32:39] INFO  [41/60] ApexTrigger:ApexTrigger:PedidoTrigger
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoTrigger: processando
[20:32:39] INFO  ApexTrigger:ApexTrigger:PedidoTrigger: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidotrigger-apex-trigger.md
[20:32:39] INFO  [42/60] LightningComponentBundle:LightningComponentBundle:pedidoAcaoRapida
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoAcaoRapida: processando
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoAcaoRapida: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidoacaorapida-lwc.md
[20:32:39] INFO  [43/60] LightningComponentBundle:LightningComponentBundle:pedidoPainel
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoPainel: processando
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoPainel: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidopainel-lwc.md
[20:32:39] INFO  [44/60] LightningComponentBundle:LightningComponentBundle:pedidoTelaFlow
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoTelaFlow: processando
[20:32:39] INFO  LightningComponentBundle:LightningComponentBundle:pedidoTelaFlow: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidotelaflow-lwc.md
[20:32:39] INFO  [45/60] FlexiPage:FlexiPage:Pedido_Record_Page
[20:32:39] INFO  FlexiPage:FlexiPage:Pedido_Record_Page: processando
[20:32:39] INFO  FlexiPage:FlexiPage:Pedido_Record_Page: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-record-page-flexipage.md
[20:32:39] INFO  [46/60] FlexiPage:FlexiPage:Pedidos_App_Page
[20:32:39] INFO  FlexiPage:FlexiPage:Pedidos_App_Page: processando
[20:32:39] INFO  FlexiPage:FlexiPage:Pedidos_App_Page: SUCCESS -> saida/docs/doc-dev-101326/doc-pedidos-app-page-flexipage.md
[20:32:39] INFO  [47/60] PlatformEvent:CustomObject:Pedido_Evento__e
[20:32:39] INFO  PlatformEvent:CustomObject:Pedido_Evento__e: processando
[20:32:39] INFO  PlatformEvent:CustomObject:Pedido_Evento__e: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-evento-e-platform-event.md
[20:32:39] INFO  [48/60] ChangeDataCapture:PlatformEventChannelMember:Canal_Pedido_Pedido_ChangeEvent
[20:32:39] INFO  ChangeDataCapture:PlatformEventChannelMember:Canal_Pedido_Pedido_ChangeEvent: processando
[20:32:40] INFO  ChangeDataCapture:PlatformEventChannelMember:Canal_Pedido_Pedido_ChangeEvent: SUCCESS -> saida/docs/doc-dev-101326/doc-canal-pedido-pedido-changeevent-change-data-capture.md
[20:32:40] INFO  [49/60] ChangeDataCapture:PlatformEventChannelMember:ChangeEvents_Pedido_ChangeEvent
[20:32:40] INFO  ChangeDataCapture:PlatformEventChannelMember:ChangeEvents_Pedido_ChangeEvent: processando
[20:32:40] INFO  ChangeDataCapture:PlatformEventChannelMember:ChangeEvents_Pedido_ChangeEvent: SUCCESS -> saida/docs/doc-dev-101326/doc-changeevents-pedido-changeevent-change-data-capture.md
[20:32:40] INFO  [50/60] Queue:Queue:Fila_Pedidos
[20:32:40] INFO  Queue:Queue:Fila_Pedidos: processando
[20:32:40] INFO  Queue:Queue:Fila_Pedidos: SUCCESS -> saida/docs/doc-dev-101326/doc-fila-pedidos-queue.md
[20:32:40] INFO  [51/60] ExperienceBundle:ExperienceBundle:Portal_Clientes1
[20:32:40] INFO  ExperienceBundle:ExperienceBundle:Portal_Clientes1: processando
[20:32:40] INFO  ExperienceBundle:ExperienceBundle:Portal_Clientes1: SUCCESS -> saida/docs/doc-dev-101326/doc-portal-clientes1-experience.md
[20:32:40] INFO  [52/60] OmniDataTransform:OmniDataTransform:ExtrairPedido
[20:32:40] INFO  OmniDataTransform:OmniDataTransform:ExtrairPedido: processando
[20:32:40] INFO  OmniDataTransform:OmniDataTransform:ExtrairPedido: SUCCESS -> saida/docs/doc-dev-101326/doc-extrairpedido-dataraptor.md
[20:32:40] INFO  [53/60] OmniIntegrationProcedure:OmniIntegrationProcedure:Pedido_EnviarERP_Procedure_1
[20:32:40] INFO  OmniIntegrationProcedure:OmniIntegrationProcedure:Pedido_EnviarERP_Procedure_1: processando
[20:32:40] INFO  OmniIntegrationProcedure:OmniIntegrationProcedure:Pedido_EnviarERP_Procedure_1: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-enviarerp-procedure-1-integration-procedure.md
[20:32:40] INFO  [54/60] OmniScript:OmniScript:Vendas_CriarPedido_Portuguese_1
[20:32:40] INFO  OmniScript:OmniScript:Vendas_CriarPedido_Portuguese_1: processando
[20:32:40] INFO  OmniScript:OmniScript:Vendas_CriarPedido_Portuguese_1: SUCCESS -> saida/docs/doc-dev-101326/doc-vendas-criarpedido-portuguese-1-omniscript.md
[20:32:40] INFO  [55/60] OmniUiCard:OmniUiCard:CartaoPedido_1
[20:32:40] INFO  OmniUiCard:OmniUiCard:CartaoPedido_1: processando
[20:32:40] INFO  OmniUiCard:OmniUiCard:CartaoPedido_1: SUCCESS -> saida/docs/doc-dev-101326/doc-cartaopedido-1-flexcard.md
[20:32:40] INFO  [56/60] SharingRules:SharingRules:Pedido__c
[20:32:40] INFO  SharingRules:SharingRules:Pedido__c: processando
[20:32:40] INFO  SharingRules:SharingRules:Pedido__c: SUCCESS -> saida/docs/doc-dev-101326/doc-pedido-c-sharing-rules.md
[20:32:40] INFO  [57/60] Role:Role:Diretoria
[20:32:40] INFO  Role:Role:Diretoria: processando
[20:32:40] INFO  Role:Role:Diretoria: SUCCESS -> saida/docs/doc-dev-101326/doc-diretoria-role.md
[20:32:40] INFO  [58/60] Role:Role:Gerente_Vendas
[20:32:40] INFO  Role:Role:Gerente_Vendas: processando
[20:32:40] INFO  Role:Role:Gerente_Vendas: SUCCESS -> saida/docs/doc-dev-101326/doc-gerente-vendas-role.md
[20:32:40] INFO  [59/60] Role:Role:Vendas
[20:32:40] INFO  Role:Role:Vendas: processando
[20:32:40] INFO  Role:Role:Vendas: SUCCESS -> saida/docs/doc-dev-101326/doc-vendas-role.md
[20:32:40] INFO  [60/60] OrgSecurity:SecuritySettings:Security
[20:32:40] INFO  OrgSecurity:SecuritySettings:Security: processando
[20:32:40] INFO  OrgSecurity:SecuritySettings:Security: SUCCESS -> saida/docs/doc-dev-101326/doc-security-org-security.md
[20:32:40] INFO  Execução run-20261013-203232 finalizada: SUCCESS {'SUCCESS': 60}
[20:32:40] INFO  Cobertura: COMPLETE — 60 documentada(s) de 60 no escopo; lacunas bloqueantes: 0; avisos: 0
[20:32:40] INFO  Tipos: configurados 46, processados 46, documentados 36, sem modelo 0, fora do escopo 0, não habilitados 0, descobertos e não configurados 5
[20:32:40] INFO  Log: runs/run-20261013-203232.json
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
| 18 | 6 | `sf org list metadata --metadata-type ApexClass --target-org dev --api-version 67.0 --json` |
| 19 | 6 | `sf org list metadata --metadata-type ApexTrigger --target-org dev --api-version 67.0 --json` |
| 20 | 6 | `sf org list metadata --metadata-type LightningComponentBundle --target-org dev --api-version 67.0 --json` |
| 21 | 6 | `sf org list metadata --metadata-type FlexiPage --target-org dev --api-version 67.0 --json` |
| 22 | 6 | `sf org list metadata --metadata-type PlatformEventChannelMember --target-org dev --api-version 67.0 --json` |
| 23 | 6 | `sf org list metadata --metadata-type AssignmentRules --target-org dev --api-version 67.0 --json` |
| 24 | 6 | `sf org list metadata --metadata-type AutoResponseRules --target-org dev --api-version 67.0 --json` |
| 25 | 6 | `sf org list metadata --metadata-type EscalationRules --target-org dev --api-version 67.0 --json` |
| 26 | 6 | `sf org list metadata --metadata-type Queue --target-org dev --api-version 67.0 --json` |
| 27 | 6 | `sf org list metadata --metadata-type BusinessProcess --target-org dev --api-version 67.0 --json` |
| 28 | 6 | `sf org list metadata --metadata-type Territory2Model --target-org dev --api-version 67.0 --json` |
| 29 | 6 | `sf org list metadata --metadata-type Territory2 --target-org dev --api-version 67.0 --json` |
| 30 | 6 | `sf org list metadata --metadata-type Territory2Rule --target-org dev --api-version 67.0 --json` |
| 31 | 6 | `sf org list metadata --metadata-type OpportunitySplitType --target-org dev --api-version 67.0 --json` |
| 32 | 6 | `sf org list metadata --metadata-type Network --target-org dev --api-version 67.0 --json` |
| 33 | 6 | `sf org list metadata --metadata-type CustomSite --target-org dev --api-version 67.0 --json` |
| 34 | 6 | `sf org list metadata --metadata-type ExperienceBundle --target-org dev --api-version 67.0 --json` |
| 35 | 6 | `sf org list metadata --metadata-type OmniDataTransform --target-org dev --api-version 67.0 --json` |
| 36 | 6 | `sf org list metadata --metadata-type OmniIntegrationProcedure --target-org dev --api-version 67.0 --json` |
| 37 | 6 | `sf org list metadata --metadata-type OmniScript --target-org dev --api-version 67.0 --json` |
| 38 | 6 | `sf org list metadata --metadata-type OmniUiCard --target-org dev --api-version 67.0 --json` |
| 39 | 6 | `sf org list metadata --metadata-type PermissionSet --target-org dev --api-version 67.0 --json` |
| 40 | 6 | `sf org list metadata --metadata-type Profile --target-org dev --api-version 67.0 --json` |
| 41 | 6 | `sf org list metadata --metadata-type PermissionSetGroup --target-org dev --api-version 67.0 --json` |
| 42 | 6 | `sf org list metadata --metadata-type SharingRules --target-org dev --api-version 67.0 --json` |
| 43 | 6 | `sf org list metadata --metadata-type Role --target-org dev --api-version 67.0 --json` |
| 44 | 6 | `sf org list metadata --metadata-type Group --target-org dev --api-version 67.0 --json` |
| 45 | 6 | `sf org list metadata --metadata-type RecordType --target-org dev --api-version 67.0 --json` |
| 46 | 7 | `sf project retrieve start --metadata Profile --metadata PermissionSet --metadata PermissionSetGroup --metadata Queue --metadata SharingRules --metadata CustomApplication --metadata PlatformEventSubscriberConfig --metadata ApexClass --metadata ApexTrigger --metadata AssignmentRules --metadata AutoResponseRules --metadata BusinessProcess --metadata Certificate --metadata ConnectedApp --metadata CustomObject --metadata CustomSite --metadata EscalationRules --metadata ExperienceBundle --metadata ExternalClientApplication --metadata ExternalCredential --metadata FlexiPage --metadata Flow --metadata Group --metadata LeadConvertSettings:LeadConvertSettings --metadata LightningComponentBundle --metadata NamedCredential --metadata Network --metadata OmniDataTransform --metadata OmniIntegrationProcedure --metadata OmniScript --metadata OmniUiCard --metadata OpportunitySplitType --metadata PlatformEventChannelMember --metadata RemoteSiteSetting --metadata Role --metadata Settings:Security --metadata Territory2Model --target-org dev --api-version 67.0 --json` |
| 47 | 7 | `sf project retrieve start --metadata Flow:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 48 | 7 | `sf project retrieve start --metadata FlowDefinition:Meu_Flow --target-org dev --api-version 67.0 --json` |
| 49 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Meu_Flow' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 50 | 7 | `sf project retrieve start --metadata Flow:Pedido_Evento_Flow --target-org dev --api-version 67.0 --json` |
| 51 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Pedido_Evento_Flow' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 52 | 7 | `sf project retrieve start --metadata Flow:Processa_Pedido --target-org dev --api-version 67.0 --json` |
| 53 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Processa_Pedido' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 54 | 7 | `sf project retrieve start --metadata Flow:Tela_Cadastro --target-org dev --api-version 67.0 --json` |
| 55 | 9 | `sf data query --query SELECT Id, VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = 'Tela_Cadastro' ORDER BY VersionNumber --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 56 | 7 | `sf project retrieve start --metadata ExternalClientApplication:Minha_ECA --target-org dev --api-version 67.0 --json` |
| 57 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Minha_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 58 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthSettings:Outra_ECA_oauth --target-org dev --api-version 67.0 --json` |
| 59 | 7 | `sf project retrieve start --metadata ExtlClntAppConfigurablePolicies:Minha_ECA_plcy --target-org dev --api-version 67.0 --json` |
| 60 | 7 | `sf project retrieve start --metadata ExtlClntAppOauthConfigurablePolicies:Minha_ECA_oauthPlcy --target-org dev --api-version 67.0 --json` |
| 61 | 7 | `sf project retrieve start --metadata ExternalCredential:Minha_EC --target-org dev --api-version 67.0 --json` |
| 62 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, CreatedDate, LastModifiedDate FROM ExternalCredential WHERE DeveloperName = 'Minha_EC' --target-org dev --api-version 67.0 --json` |
| 63 | 7 | `sf project retrieve start --metadata ConnectedApp:Meu_App --target-org dev --api-version 67.0 --json` |
| 64 | 9 | `sf data query --query SELECT Id, Name, OptionsAllowAdminApprovedUsersOnly FROM ConnectedApplication WHERE Name = 'Meu_App' --target-org dev --api-version 67.0 --json` |
| 65 | 7 | `sf project retrieve start --metadata CustomObject:Pedido__c --target-org dev --api-version 67.0 --json` |
| 66 | 9 | `sf data query --query SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = 'Pedido__c' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 67 | 7 | `sf project retrieve start --metadata CustomObject:Config__mdt --target-org dev --api-version 67.0 --json` |
| 68 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Padrao --target-org dev --api-version 67.0 --json` |
| 69 | 7 | `sf project retrieve start --metadata CustomMetadata:Config.Secundario --target-org dev --api-version 67.0 --json` |
| 70 | 9 | `sf data query --query SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = 'Config__mdt' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 71 | 7 | `sf project retrieve start --metadata NamedCredential:Minha_NC --target-org dev --api-version 67.0 --json` |
| 72 | 9 | `sf data query --query SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = 'Minha_NC' --target-org dev --api-version 67.0 --json` |
| 73 | 7 | `sf project retrieve start --metadata NamedCredential:NC_Legada --target-org dev --api-version 67.0 --json` |
| 74 | 9 | `sf data query --query SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = 'NC_Legada' --target-org dev --api-version 67.0 --json` |
| 75 | 7 | `sf project retrieve start --metadata RemoteSiteSetting:Meu_Site --target-org dev --api-version 67.0 --json` |
| 76 | 7 | `sf project retrieve start --metadata Certificate:Meu_Certificado --target-org dev --api-version 67.0 --json` |
| 77 | 9 | `sf data query --query SELECT DeveloperName, ExpirationDate, KeySize FROM Certificate WHERE DeveloperName = 'Meu_Certificado' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 78 | 7 | `sf project retrieve start --metadata ApexClass:AccountSyncQueueable --target-org dev --api-version 67.0 --json` |
| 79 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'AccountSyncQueueable' --target-org dev --api-version 67.0 --json` |
| 80 | 7 | `sf project retrieve start --metadata ApexClass:DailyOrderCleanupScheduler --target-org dev --api-version 67.0 --json` |
| 81 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'DailyOrderCleanupScheduler' --target-org dev --api-version 67.0 --json` |
| 82 | 7 | `sf project retrieve start --metadata ApexClass:IntegrationAsyncHelper --target-org dev --api-version 67.0 --json` |
| 83 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'IntegrationAsyncHelper' --target-org dev --api-version 67.0 --json` |
| 84 | 7 | `sf project retrieve start --metadata ApexClass:MultiRoleJob --target-org dev --api-version 67.0 --json` |
| 85 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'MultiRoleJob' --target-org dev --api-version 67.0 --json` |
| 86 | 7 | `sf project retrieve start --metadata ApexClass:OrderCleanupBatch --target-org dev --api-version 67.0 --json` |
| 87 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'OrderCleanupBatch' --target-org dev --api-version 67.0 --json` |
| 88 | 7 | `sf project retrieve start --metadata ApexClass:PedidoController --target-org dev --api-version 67.0 --json` |
| 89 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'PedidoController' --target-org dev --api-version 67.0 --json` |
| 90 | 7 | `sf project retrieve start --metadata ApexClass:PedidoService --target-org dev --api-version 67.0 --json` |
| 91 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'PedidoService' --target-org dev --api-version 67.0 --json` |
| 92 | 7 | `sf project retrieve start --metadata ApexClass:PedidoTriggerHandler --target-org dev --api-version 67.0 --json` |
| 93 | 9 | `sf data query --query SELECT Id, Name, ApiVersion, Status, IsValid, LengthWithoutComments, CreatedDate, LastModifiedDate FROM ApexClass WHERE Name = 'PedidoTriggerHandler' --target-org dev --api-version 67.0 --json` |
| 94 | 7 | `sf project retrieve start --metadata AssignmentRules:Case --target-org dev --api-version 67.0 --json` |
| 95 | 9 | `sf data query --query SELECT Id, Name, Active FROM AssignmentRule WHERE SobjectType = 'Case' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 96 | 7 | `sf project retrieve start --metadata AutoResponseRules:Case --target-org dev --api-version 67.0 --json` |
| 97 | 9 | `sf data query --query SELECT Id, Name, Active FROM AutoResponseRule WHERE SobjectType = 'Case' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 98 | 7 | `sf project retrieve start --metadata EscalationRules:Case --target-org dev --api-version 67.0 --json` |
| 99 | 9 | `sf data query --query SELECT Id, Name, Active FROM EscalationRule WHERE SobjectType = 'Case' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 100 | 7 | `sf project retrieve start --metadata BusinessProcess:Opportunity.Venda_Enterprise --target-org dev --api-version 67.0 --json` |
| 101 | 7 | `sf project retrieve start --metadata RecordType:Opportunity.Enterprise --target-org dev --api-version 67.0 --json` |
| 102 | 7 | `sf project retrieve start --metadata RecordType:Opportunity.Varejo --target-org dev --api-version 67.0 --json` |
| 103 | 9 | `sf data query --query SELECT Id, Name, TableEnumOrId, IsActive, Description FROM BusinessProcess WHERE Name = 'Venda_Enterprise' AND TableEnumOrId = 'Opportunity' --target-org dev --api-version 67.0 --json` |
| 104 | 7 | `sf project retrieve start --metadata LeadConvertSettings:LeadConvertSettings --target-org dev --api-version 67.0 --json` |
| 105 | 7 | `sf project retrieve start --metadata Territory2Model:Modelo_Vendas --target-org dev --api-version 67.0 --json` |
| 106 | 7 | `sf project retrieve start --metadata Territory2:Modelo_Vendas.Sudeste --target-org dev --api-version 67.0 --json` |
| 107 | 7 | `sf project retrieve start --metadata Territory2Rule:Modelo_Vendas.Regra_SP --target-org dev --api-version 67.0 --json` |
| 108 | 9 | `sf data query --query SELECT Id, DeveloperName, Name, State, ActivatedDate FROM Territory2Model WHERE DeveloperName = 'Modelo_Vendas' --target-org dev --api-version 67.0 --json` |
| 109 | 7 | `sf project retrieve start --metadata OpportunitySplitType:Receita_Principal --target-org dev --api-version 67.0 --json` |
| 110 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel FROM OpportunitySplitType WHERE DeveloperName = 'Receita_Principal' --target-org dev --api-version 67.0 --json` |
| 111 | 7 | `sf project retrieve start --metadata Network:Portal_Clientes --target-org dev --api-version 67.0 --json` |
| 112 | 7 | `sf project retrieve start --metadata CustomSite:Portal_Clientes --target-org dev --api-version 67.0 --json` |
| 113 | 9 | `sf data query --query SELECT Id, Name, Status, UrlPathPrefix FROM Network WHERE Name = 'Portal_Clientes' --target-org dev --api-version 67.0 --json` |
| 114 | 9 | `sf data query --query SELECT Id, Name, MasterLabel, Status, SiteType, UrlPathPrefix FROM Site WHERE Name = 'Portal_Clientes' --target-org dev --api-version 67.0 --json` |
| 115 | 9 | `sf data query --query SELECT Id, Name, Label, IsOwnedByProfile, CreatedDate, LastModifiedDate FROM PermissionSet WHERE Name = 'Integracao_API' --target-org dev --api-version 67.0 --json` |
| 116 | 9 | `sf data query --query SELECT Id, Name, Label, IsOwnedByProfile, CreatedDate, LastModifiedDate FROM PermissionSet WHERE Name = 'Leitura_Pedidos' --target-org dev --api-version 67.0 --json` |
| 117 | 9 | `sf data query --query SELECT Id, Name, UserType, UserLicense.Name, Description, CreatedDate, LastModifiedDate FROM Profile WHERE Name = 'Admin' --target-org dev --api-version 67.0 --json` |
| 118 | 9 | `sf data query --query SELECT Id, Name, UserType, UserLicense.Name, Description, CreatedDate, LastModifiedDate FROM Profile WHERE Name = 'Portal Clientes Profile' --target-org dev --api-version 67.0 --json` |
| 119 | 9 | `sf data query --query SELECT Id, Name, UserType, UserLicense.Name, Description, CreatedDate, LastModifiedDate FROM Profile WHERE Name = 'Vendas' --target-org dev --api-version 67.0 --json` |
| 120 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, Status, HasActivationRequired, CreatedDate, LastModifiedDate FROM PermissionSetGroup WHERE DeveloperName = 'PSG_Integracao' --target-org dev --api-version 67.0 --json` |
| 121 | 7 | `sf project retrieve start --metadata Group:Grupo_Suporte --target-org dev --api-version 67.0 --json` |
| 122 | 9 | `sf data query --query SELECT Id, Name, DeveloperName, Type, DoesIncludeBosses, CreatedDate, LastModifiedDate FROM Group WHERE DeveloperName = 'Grupo_Suporte' --target-org dev --api-version 67.0 --json` |
| 123 | 7 | `sf project retrieve start --metadata ApexTrigger:PedidoAuditoriaTrigger --target-org dev --api-version 67.0 --json` |
| 124 | 7 | `sf project retrieve start --metadata ApexTrigger:PedidoChangeTrigger --target-org dev --api-version 67.0 --json` |
| 125 | 7 | `sf project retrieve start --metadata ApexTrigger:PedidoEventoTrigger --target-org dev --api-version 67.0 --json` |
| 126 | 7 | `sf project retrieve start --metadata ApexTrigger:PedidoTrigger --target-org dev --api-version 67.0 --json` |
| 127 | 7 | `sf project retrieve start --metadata LightningComponentBundle:pedidoAcaoRapida --target-org dev --api-version 67.0 --json` |
| 128 | 7 | `sf project retrieve start --metadata LightningComponentBundle:pedidoPainel --target-org dev --api-version 67.0 --json` |
| 129 | 7 | `sf project retrieve start --metadata LightningComponentBundle:pedidoTelaFlow --target-org dev --api-version 67.0 --json` |
| 130 | 7 | `sf project retrieve start --metadata FlexiPage:Pedido_Record_Page --target-org dev --api-version 67.0 --json` |
| 131 | 7 | `sf project retrieve start --metadata FlexiPage:Pedidos_App_Page --target-org dev --api-version 67.0 --json` |
| 132 | 7 | `sf project retrieve start --metadata CustomObject:Pedido_Evento__e --target-org dev --api-version 67.0 --json` |
| 133 | 7 | `sf project retrieve start --metadata PlatformEventChannelMember:Canal_Pedido_Pedido_ChangeEvent --target-org dev --api-version 67.0 --json` |
| 134 | 7 | `sf project retrieve start --metadata PlatformEventChannelMember:ChangeEvents_Pedido_ChangeEvent --target-org dev --api-version 67.0 --json` |
| 135 | 7 | `sf project retrieve start --metadata ExperienceBundle:Portal_Clientes1 --target-org dev --api-version 67.0 --json` |
| 136 | 7 | `sf project retrieve start --metadata OmniDataTransform:ExtrairPedido --target-org dev --api-version 67.0 --json` |
| 137 | 7 | `sf project retrieve start --metadata OmniIntegrationProcedure:Pedido_EnviarERP_Procedure_1 --target-org dev --api-version 67.0 --json` |
| 138 | 7 | `sf project retrieve start --metadata OmniScript:Vendas_CriarPedido_Portuguese_1 --target-org dev --api-version 67.0 --json` |
| 139 | 7 | `sf project retrieve start --metadata OmniUiCard:CartaoPedido_1 --target-org dev --api-version 67.0 --json` |
| 140 | 7 | `sf project retrieve start --metadata Role:Diretoria --target-org dev --api-version 67.0 --json` |
| 141 | 7 | `sf project retrieve start --metadata Role:Gerente_Vendas --target-org dev --api-version 67.0 --json` |
| 142 | 7 | `sf project retrieve start --metadata Role:Vendas --target-org dev --api-version 67.0 --json` |
| 143 | 7 | `sf project retrieve start --metadata Settings:Security --target-org dev --api-version 67.0 --json` |
| 144 | 9 | `sf data query --query SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete, CreatedDate, LastModifiedDate FROM ApexTrigger WHERE Name = 'PedidoAuditoriaTrigger' --target-org dev --api-version 67.0 --json` |
| 145 | 9 | `sf data query --query SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete, CreatedDate, LastModifiedDate FROM ApexTrigger WHERE Name = 'PedidoChangeTrigger' --target-org dev --api-version 67.0 --json` |
| 146 | 9 | `sf data query --query SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete, CreatedDate, LastModifiedDate FROM ApexTrigger WHERE Name = 'PedidoEventoTrigger' --target-org dev --api-version 67.0 --json` |
| 147 | 9 | `sf data query --query SELECT Id, Name, TableEnumOrId, ApiVersion, Status, IsValid, UsageBeforeInsert, UsageAfterInsert, UsageBeforeUpdate, UsageAfterUpdate, UsageBeforeDelete, UsageAfterDelete, UsageAfterUndelete, CreatedDate, LastModifiedDate FROM ApexTrigger WHERE Name = 'PedidoTrigger' --target-org dev --api-version 67.0 --json` |
| 148 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, ApiVersion, IsExposed, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM LightningComponentBundle WHERE DeveloperName = 'pedidoAcaoRapida' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 149 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, ApiVersion, IsExposed, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM LightningComponentBundle WHERE DeveloperName = 'pedidoPainel' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 150 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, ApiVersion, IsExposed, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM LightningComponentBundle WHERE DeveloperName = 'pedidoTelaFlow' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 151 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, Type, EntityDefinitionId, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM FlexiPage WHERE DeveloperName = 'Pedido_Record_Page' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 152 | 9 | `sf data query --query SELECT Id, DeveloperName, MasterLabel, Type, EntityDefinitionId, Description, NamespacePrefix, CreatedDate, LastModifiedDate FROM FlexiPage WHERE DeveloperName = 'Pedidos_App_Page' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 153 | 9 | `sf data query --query SELECT QualifiedApiName, Label, PluralLabel, KeyPrefix, LastModifiedDate FROM EntityDefinition WHERE QualifiedApiName = 'Pedido_Evento__e' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 154 | 9 | `sf data query --query SELECT Id, DeveloperName, EventChannel, SelectedEntity FROM PlatformEventChannelMember WHERE DeveloperName = 'Canal_Pedido_Pedido_ChangeEvent' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 155 | 9 | `sf data query --query SELECT Id, DeveloperName, EventChannel, SelectedEntity FROM PlatformEventChannelMember WHERE DeveloperName = 'ChangeEvents_Pedido_ChangeEvent' --use-tooling-api --target-org dev --api-version 67.0 --json` |
| 156 | 9 | `sf data query --query SELECT Id, Name, DeveloperName, Type, DoesSendEmailToMembers FROM Group WHERE DeveloperName = 'Fila_Pedidos' --target-org dev --api-version 67.0 --json` |
| 157 | 9 | `sf data query --query SELECT Id, Name, Type, IsActive, VersionNumber FROM OmniDataTransform WHERE Name = 'ExtrairPedido' --target-org dev --api-version 67.0 --json` |
| 158 | 9 | `sf data query --query SELECT Id, UniqueName, Type, SubType, Language, VersionNumber, IsActive, IsIntegrationProcedure FROM OmniProcess WHERE UniqueName = 'Pedido_EnviarERP_Procedure_1' --target-org dev --api-version 67.0 --json` |
| 159 | 9 | `sf data query --query SELECT Id, UniqueName, Type, SubType, Language, VersionNumber, IsActive, IsIntegrationProcedure FROM OmniProcess WHERE UniqueName = 'Vendas_CriarPedido_Portuguese_1' --target-org dev --api-version 67.0 --json` |
| 160 | 9 | `sf data query --query SELECT Id, UniqueName, Name, VersionNumber, IsActive FROM OmniUiCard WHERE UniqueName = 'CartaoPedido_1' --target-org dev --api-version 67.0 --json` |
| 161 | 9 | `sf data query --query SELECT Id, Name, DeveloperName, ParentRoleId, RollupDescription, CaseAccessForAccountOwner, ContactAccessForAccountOwner, OpportunityAccessForAccountOwner FROM UserRole WHERE DeveloperName = 'Diretoria' --target-org dev --api-version 67.0 --json` |
| 162 | 9 | `sf data query --query SELECT Id, Name, DeveloperName, ParentRoleId, RollupDescription, CaseAccessForAccountOwner, ContactAccessForAccountOwner, OpportunityAccessForAccountOwner FROM UserRole WHERE DeveloperName = 'Gerente_Vendas' --target-org dev --api-version 67.0 --json` |
| 163 | 9 | `sf data query --query SELECT Id, Name, DeveloperName, ParentRoleId, RollupDescription, CaseAccessForAccountOwner, ContactAccessForAccountOwner, OpportunityAccessForAccountOwner FROM UserRole WHERE DeveloperName = 'Vendas' --target-org dev --api-version 67.0 --json` |
| 164 | 9 | `sf data query --query SELECT Id, Name, OrganizationType, IsSandbox, InstanceName, DefaultAccountAccess, DefaultContactAccess, DefaultOpportunityAccess, DefaultCaseAccess, DefaultLeadAccess, DefaultCalendarAccess, DefaultPricebookAccess, DefaultCampaignAccess FROM Organization --target-org dev --api-version 67.0 --json` |

O passo 5 (`describeValueType`) é SOAP direto na Metadata API, fora da CLI; o passo 8 (XML → JSON) e o passo 10 (Markdown) são locais.

## 3. Situação por metadata type

| Metadata type | Habilitado (4) | Schema (5) | Inventário (6) | Componentes |
|---|---|---|---|---|
| ApexClass | ENABLED | SUCCESS | SUCCESS | 9 |
| ApexTrigger | ENABLED | SUCCESS | SUCCESS | 4 |
| AssignmentRules | ENABLED | SUCCESS | SUCCESS | 1 |
| AutoResponseRules | ENABLED | SUCCESS | SUCCESS | 1 |
| BusinessProcess | ENABLED | SUCCESS | SUCCESS | 1 |
| Certificate | ENABLED | SUCCESS | SUCCESS | 1 |
| ConnectedApp | ENABLED | SUCCESS | SUCCESS | 1 |
| CustomField | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| CustomMetadata | ENABLED | SUCCESS | SUCCESS | 2 |
| CustomObject | ENABLED | SUCCESS | SUCCESS | 4 |
| CustomSite | ENABLED | SUCCESS | SUCCESS | 1 |
| EscalationRules | ENABLED | SUCCESS | SUCCESS | 1 |
| ExperienceBundle | ENABLED | SUCCESS | SUCCESS | 1 |
| ExternalClientApplication | ENABLED | SUCCESS | SUCCESS | 1 |
| ExternalCredential | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthConfigurablePolicies | ENABLED | SUCCESS | SUCCESS | 1 |
| ExtlClntAppOauthSettings | ENABLED | SUCCESS | SUCCESS | 2 |
| FlexiPage | ENABLED | SUCCESS | SUCCESS | 2 |
| Flow | ENABLED | SUCCESS | SUCCESS | 4 |
| FlowDefinition | ENABLED | SUCCESS | SUCCESS | 1 |
| Group | ENABLED | SUCCESS | SUCCESS | 1 |
| LeadConvertSettings | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| LightningComponentBundle | ENABLED | SUCCESS | SUCCESS | 4 |
| NamedCredential | ENABLED | SUCCESS | SUCCESS | 2 |
| Network | ENABLED | SUCCESS | SUCCESS | 1 |
| OmniDataTransform | ENABLED | SUCCESS | SUCCESS | 1 |
| OmniIntegrationProcedure | ENABLED | SUCCESS | SUCCESS | 1 |
| OmniScript | ENABLED | SUCCESS | SUCCESS | 1 |
| OmniUiCard | ENABLED | SUCCESS | SUCCESS | 1 |
| OpportunitySplitType | ENABLED | SUCCESS | SUCCESS | 1 |
| PermissionSet | ENABLED | SUCCESS | SUCCESS | 2 |
| PermissionSetGroup | ENABLED | SUCCESS | SUCCESS | 1 |
| PlatformEventChannelMember | ENABLED | SUCCESS | SUCCESS | 2 |
| Profile | ENABLED | SUCCESS | SUCCESS | 3 |
| Queue | ENABLED | SUCCESS | SUCCESS | 1 |
| RecordType | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| RemoteSiteSetting | ENABLED | SUCCESS | SUCCESS | 1 |
| Role | ENABLED | SUCCESS | SUCCESS | 3 |
| SecuritySettings | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| SharingRules | ENABLED | SUCCESS | SUCCESS | 1 |
| Territory2 | ENABLED | SUCCESS | SUCCESS | 2 |
| Territory2Model | ENABLED | SUCCESS | SUCCESS | 1 |
| Territory2Rule | ENABLED | SUCCESS | SUCCESS | 1 |
| ValidationRule | ENABLED | SUCCESS | via retrieve do CustomObject | — |
| WebLink | ENABLED | SUCCESS | via retrieve do CustomObject | — |

## 4. Documentos gerados (passo 10)

| Documento | Modelo | Principal | Relacionados no documento | Status |
|---|---|---|---|---|
| `doc-meu-flow-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Meu_Flow | Meu_Flow (FlowDefinition) | SUCCESS |
| `doc-meu-flow-flow-trigger.md` | `modelo-doc-flow-trigger-vapi-67.md` | Flow:Meu_Flow | (subdocumento) | SUCCESS |
| `doc-pedido-evento-flow-flow.md` | `modelo-doc-flow-vapi-67.md` | Flow:Pedido_Evento_Flow | — | SUCCESS |
| `doc-pedido-evento-flow-flow-trigger.md` | `modelo-doc-flow-trigger-vapi-67.md` | Flow:Pedido_Evento_Flow | (subdocumento) | SUCCESS |
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
| `doc-accountsyncqueueable-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:AccountSyncQueueable | — | SUCCESS |
| `doc-accountsyncqueueable-apex-queueable.md` | `modelo-doc-apex-queueable-vapi-67.md` | ApexClass:AccountSyncQueueable | (subdocumento) | SUCCESS |
| `doc-dailyordercleanupscheduler-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:DailyOrderCleanupScheduler | — | SUCCESS |
| `doc-dailyordercleanupscheduler-apex-scheduler.md` | `modelo-doc-apex-scheduler-vapi-67.md` | ApexClass:DailyOrderCleanupScheduler | (subdocumento) | SUCCESS |
| `doc-integrationasynchelper-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:IntegrationAsyncHelper | — | SUCCESS |
| `doc-integrationasynchelper-processordersasync-apex-future.md` | `modelo-doc-apex-future-vapi-67.md` | ApexClass:IntegrationAsyncHelper | (subdocumento) | SUCCESS |
| `doc-integrationasynchelper-recalc-apex-future.md` | `modelo-doc-apex-future-vapi-67.md` | ApexClass:IntegrationAsyncHelper | (subdocumento) | SUCCESS |
| `doc-multirolejob-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:MultiRoleJob | — | SUCCESS |
| `doc-multirolejob-apex-batch.md` | `modelo-doc-apex-batch-vapi-67.md` | ApexClass:MultiRoleJob | (subdocumento) | SUCCESS |
| `doc-multirolejob-apex-scheduler.md` | `modelo-doc-apex-scheduler-vapi-67.md` | ApexClass:MultiRoleJob | (subdocumento) | SUCCESS |
| `doc-ordercleanupbatch-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:OrderCleanupBatch | — | SUCCESS |
| `doc-ordercleanupbatch-apex-batch.md` | `modelo-doc-apex-batch-vapi-67.md` | ApexClass:OrderCleanupBatch | (subdocumento) | SUCCESS |
| `doc-pedidocontroller-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:PedidoController | — | SUCCESS |
| `doc-pedidoservice-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:PedidoService | — | SUCCESS |
| `doc-pedidotriggerhandler-apex-class.md` | `modelo-doc-apex-class-vapi-67.md` | ApexClass:PedidoTriggerHandler | — | SUCCESS |
| `doc-case-assignment-rules.md` | `modelo-doc-assignment-rules-vapi-67.md` | AssignmentRules:Case | — | SUCCESS |
| `doc-case-auto-response-rules.md` | `modelo-doc-auto-response-rules-vapi-67.md` | AutoResponseRules:Case | — | SUCCESS |
| `doc-case-escalation-rules.md` | `modelo-doc-escalation-rules-vapi-67.md` | EscalationRules:Case | — | SUCCESS |
| `doc-opportunity-venda-enterprise-business-process.md` | `modelo-doc-business-process-vapi-67.md` | BusinessProcess:Opportunity.Venda_Enterprise | Opportunity.Enterprise (RecordType) | SUCCESS |
| `doc-leadconvertsettings-lead-convert.md` | `modelo-doc-lead-convert-settings-vapi-67.md` | LeadConvertSettings:LeadConvertSettings | — | SUCCESS |
| `doc-modelo-vendas-territory-model.md` | `modelo-doc-territory2-model-vapi-67.md` | Territory2Model:Modelo_Vendas | Modelo_Vendas.Sudeste (Territory2), Modelo_Vendas.Regra_SP (Territory2Rule) | SUCCESS |
| `doc-receita-principal-opportunity-split-type.md` | `modelo-doc-opportunity-split-type-vapi-67.md` | OpportunitySplitType:Receita_Principal | — | SUCCESS |
| `doc-portal-clientes-network.md` | `modelo-doc-network-vapi-67.md` | Network:Portal_Clientes | Portal_Clientes (CustomSite) | SUCCESS |
| `doc-portal-clientes-site.md` | `modelo-doc-custom-site-vapi-67.md` | CustomSite:Portal_Clientes | Portal_Clientes (Network) | SUCCESS |
| `doc-integracao-api-permission-set.md` | `modelo-doc-permission-set-vapi-67.md` | PermissionSet:Integracao_API | — | SUCCESS |
| `doc-leitura-pedidos-permission-set.md` | `modelo-doc-permission-set-vapi-67.md` | PermissionSet:Leitura_Pedidos | — | SUCCESS |
| `doc-admin-profile.md` | `modelo-doc-profile-vapi-67.md` | Profile:Admin | — | SUCCESS |
| `doc-portal-clientes-profile-profile.md` | `modelo-doc-profile-vapi-67.md` | Profile:Portal Clientes Profile | — | SUCCESS |
| `doc-vendas-profile.md` | `modelo-doc-profile-vapi-67.md` | Profile:Vendas | — | SUCCESS |
| `doc-psg-integracao-permission-set-group.md` | `modelo-doc-permission-set-group-vapi-67.md` | PermissionSetGroup:PSG_Integracao | — | SUCCESS |
| `doc-grupo-suporte-public-group.md` | `modelo-doc-public-group-vapi-67.md` | Group:Grupo_Suporte | — | SUCCESS |
| `doc-pedidoauditoriatrigger-apex-trigger.md` | `modelo-doc-apex-trigger-vapi-67.md` | ApexTrigger:PedidoAuditoriaTrigger | — | SUCCESS |
| `doc-pedidochangetrigger-apex-trigger.md` | `modelo-doc-apex-trigger-vapi-67.md` | ApexTrigger:PedidoChangeTrigger | — | SUCCESS |
| `doc-pedidoeventotrigger-apex-trigger.md` | `modelo-doc-apex-trigger-vapi-67.md` | ApexTrigger:PedidoEventoTrigger | — | SUCCESS |
| `doc-pedidotrigger-apex-trigger.md` | `modelo-doc-apex-trigger-vapi-67.md` | ApexTrigger:PedidoTrigger | — | SUCCESS |
| `doc-pedidoacaorapida-lwc.md` | `modelo-doc-lwc-vapi-67.md` | LightningComponentBundle:pedidoAcaoRapida | — | SUCCESS |
| `doc-pedidoacaorapida-lwc-quick-action.md` | `modelo-doc-lwc-quick-action-vapi-67.md` | LightningComponentBundle:pedidoAcaoRapida | (subdocumento) | SUCCESS |
| `doc-pedidopainel-lwc.md` | `modelo-doc-lwc-vapi-67.md` | LightningComponentBundle:pedidoPainel | — | SUCCESS |
| `doc-pedidotelaflow-lwc.md` | `modelo-doc-lwc-vapi-67.md` | LightningComponentBundle:pedidoTelaFlow | — | SUCCESS |
| `doc-pedidotelaflow-lwc-flow-screen.md` | `modelo-doc-lwc-flow-screen-vapi-67.md` | LightningComponentBundle:pedidoTelaFlow | (subdocumento) | SUCCESS |
| `doc-pedido-record-page-flexipage.md` | `modelo-doc-flexipage-vapi-67.md` | FlexiPage:Pedido_Record_Page | — | SUCCESS |
| `doc-pedidos-app-page-flexipage.md` | `modelo-doc-flexipage-vapi-67.md` | FlexiPage:Pedidos_App_Page | — | SUCCESS |
| `doc-pedido-evento-e-platform-event.md` | `modelo-doc-platform-event-vapi-67.md` | CustomObject:Pedido_Evento__e | Pedido_Evento__e.Numero_Pedido__c (CustomField), Pedido_Evento__e.Payload__c (CustomField) | SUCCESS |
| `doc-canal-pedido-pedido-changeevent-change-data-capture.md` | `modelo-doc-change-data-capture-vapi-67.md` | PlatformEventChannelMember:Canal_Pedido_Pedido_ChangeEvent | — | SUCCESS |
| `doc-changeevents-pedido-changeevent-change-data-capture.md` | `modelo-doc-change-data-capture-vapi-67.md` | PlatformEventChannelMember:ChangeEvents_Pedido_ChangeEvent | — | SUCCESS |
| `doc-fila-pedidos-queue.md` | `modelo-doc-queue-vapi-67.md` | Queue:Fila_Pedidos | — | SUCCESS |
| `doc-portal-clientes1-experience.md` | `modelo-doc-experience-bundle-vapi-67.md` | ExperienceBundle:Portal_Clientes1 | — | SUCCESS |
| `doc-extrairpedido-dataraptor.md` | `modelo-doc-omni-data-transform-vapi-67.md` | OmniDataTransform:ExtrairPedido | — | SUCCESS |
| `doc-pedido-enviarerp-procedure-1-integration-procedure.md` | `modelo-doc-omni-integration-procedure-vapi-67.md` | OmniIntegrationProcedure:Pedido_EnviarERP_Procedure_1 | — | SUCCESS |
| `doc-vendas-criarpedido-portuguese-1-omniscript.md` | `modelo-doc-omni-script-vapi-67.md` | OmniScript:Vendas_CriarPedido_Portuguese_1 | — | SUCCESS |
| `doc-cartaopedido-1-flexcard.md` | `modelo-doc-omni-ui-card-vapi-67.md` | OmniUiCard:CartaoPedido_1 | — | SUCCESS |
| `doc-pedido-c-sharing-rules.md` | `modelo-doc-sharing-rules-vapi-67.md` | SharingRules:Pedido__c | — | SUCCESS |
| `doc-diretoria-role.md` | `modelo-doc-role-vapi-67.md` | Role:Diretoria | — | SUCCESS |
| `doc-gerente-vendas-role.md` | `modelo-doc-role-vapi-67.md` | Role:Gerente_Vendas | — | SUCCESS |
| `doc-vendas-role.md` | `modelo-doc-role-vapi-67.md` | Role:Vendas | — | SUCCESS |
| `doc-security-org-security.md` | `modelo-doc-org-security-vapi-67.md` | SecuritySettings:Security | — | SUCCESS |

## 5. Rastreamento de um componente: `Flow:Meu_Flow`

**Passo 3** — `catalog/org-dev/api-v67/org-display.sanitized.json`

```json
{
  "sanitized": true,
  "note": "Resposta de `sf org display` com credenciais; não é raw intacto.",
  "redacted": [
    "result.accessToken"
  ],
  "response": {
    "status": 0,
    "result": {
      "id": "00D000000000000AAA",
      "apiVersion": "67.0",
      "accessToken": "[REDACTED]",
      "instanceUrl": "https://simulado.my.salesforce.com",
      "username": "usuario.simulado@example.com",
      "clientId": "PlatformCLI",
      "connectedStatus": "Connected",
      "alias": "dev"
    }
  }
}
```

**Passo 4** — `catalog/org-dev/api-v67/metadata-types.index.json`

```json
{
  "metadataTypes": {
    "ApexClass": {
      "directoryName": "classes",
      "suffix": "cls",
      "inFolder": false,
      "metaFile": true,
      "childXmlNames": []
    },
    "ApexTrigger": {
      "directoryName": "triggers",
      "suffix": "trigger",
      "inFolder": false,
      "metaFile": true,
      "childXmlNames": []
    },
    "AssignmentRules": {
      "directoryName": "assignmentRules",
      "suffix": "assignmentRules",
      "inFolder": false,
... (327 linhas omitidas)
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
  "count": 4,
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
      "fullName": "Pedido_Evento_Flow",
      "type": "Flow",
      "fileName": "x/Pedido_Evento_Flow",
      "id": "0PS000000000000AAA",
      "namespacePrefix": "",
... (23 linhas omitidas)
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
        "filePath": "/tmp/sfdocs-retrieve-acq8ekri/force-app/main/default/flows/Meu_Flow.flow-meta.xml"
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
catalog/org-dev/api-v67/org-display.sanitized.json
catalog/org-dev/api-v67/schemas/apex-class.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/apex-class.schema.json
catalog/org-dev/api-v67/schemas/apex-trigger.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/apex-trigger.schema.json
catalog/org-dev/api-v67/schemas/assignment-rules.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/assignment-rules.schema.json
catalog/org-dev/api-v67/schemas/auto-response-rules.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/auto-response-rules.schema.json
catalog/org-dev/api-v67/schemas/business-process.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/business-process.schema.json
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
catalog/org-dev/api-v67/schemas/custom-site.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/custom-site.schema.json
catalog/org-dev/api-v67/schemas/escalation-rules.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/escalation-rules.schema.json
catalog/org-dev/api-v67/schemas/experience-bundle.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/experience-bundle.schema.json
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
catalog/org-dev/api-v67/schemas/flexi-page.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/flexi-page.schema.json
catalog/org-dev/api-v67/schemas/flow-definition.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/flow-definition.schema.json
catalog/org-dev/api-v67/schemas/flow.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/flow.schema.json
catalog/org-dev/api-v67/schemas/group.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/group.schema.json
catalog/org-dev/api-v67/schemas/lead-convert-settings.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/lead-convert-settings.schema.json
catalog/org-dev/api-v67/schemas/lightning-component-bundle.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/lightning-component-bundle.schema.json
catalog/org-dev/api-v67/schemas/named-credential.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/named-credential.schema.json
catalog/org-dev/api-v67/schemas/network.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/network.schema.json
catalog/org-dev/api-v67/schemas/omni-data-transform.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/omni-data-transform.schema.json
catalog/org-dev/api-v67/schemas/omni-integration-procedure.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/omni-integration-procedure.schema.json
catalog/org-dev/api-v67/schemas/omni-script.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/omni-script.schema.json
catalog/org-dev/api-v67/schemas/omni-ui-card.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/omni-ui-card.schema.json
catalog/org-dev/api-v67/schemas/opportunity-split-type.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/opportunity-split-type.schema.json
catalog/org-dev/api-v67/schemas/permission-set-group.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/permission-set-group.schema.json
catalog/org-dev/api-v67/schemas/permission-set.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/permission-set.schema.json
catalog/org-dev/api-v67/schemas/platform-event-channel-member.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/platform-event-channel-member.schema.json
catalog/org-dev/api-v67/schemas/profile.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/profile.schema.json
catalog/org-dev/api-v67/schemas/queue.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/queue.schema.json
catalog/org-dev/api-v67/schemas/record-type.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/record-type.schema.json
catalog/org-dev/api-v67/schemas/remote-site-setting.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/remote-site-setting.schema.json
catalog/org-dev/api-v67/schemas/role.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/role.schema.json
catalog/org-dev/api-v67/schemas/security-settings.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/security-settings.schema.json
catalog/org-dev/api-v67/schemas/sharing-rules.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/sharing-rules.schema.json
catalog/org-dev/api-v67/schemas/territory2-model.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/territory2-model.schema.json
catalog/org-dev/api-v67/schemas/territory2-rule.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/territory2-rule.schema.json
catalog/org-dev/api-v67/schemas/territory2.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/territory2.schema.json
catalog/org-dev/api-v67/schemas/validation-rule.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/validation-rule.schema.json
catalog/org-dev/api-v67/schemas/web-link.describevaluetype.raw.json
catalog/org-dev/api-v67/schemas/web-link.schema.json
inventory/org-dev/api-v67/access/access-index.json
inventory/org-dev/api-v67/access/components/applications/Vendas.app-meta.xml
inventory/org-dev/api-v67/access/components/assignmentRules/Case.assignmentRules-meta.xml
inventory/org-dev/api-v67/access/components/autoResponseRules/Case.autoResponseRules-meta.xml
inventory/org-dev/api-v67/access/components/certs/Meu_Certificado.crt
inventory/org-dev/api-v67/access/components/certs/Meu_Certificado.crt-meta.xml
inventory/org-dev/api-v67/access/components/classes/AccountSyncQueueable.cls
inventory/org-dev/api-v67/access/components/classes/AccountSyncQueueable.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/DailyOrderCleanupScheduler.cls
inventory/org-dev/api-v67/access/components/classes/DailyOrderCleanupScheduler.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/IntegrationAsyncHelper.cls
inventory/org-dev/api-v67/access/components/classes/IntegrationAsyncHelper.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/MultiRoleJob.cls
inventory/org-dev/api-v67/access/components/classes/MultiRoleJob.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/OrderCleanupBatch.cls
inventory/org-dev/api-v67/access/components/classes/OrderCleanupBatch.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/PedidoController.cls
inventory/org-dev/api-v67/access/components/classes/PedidoController.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/PedidoService.cls
inventory/org-dev/api-v67/access/components/classes/PedidoService.cls-meta.xml
inventory/org-dev/api-v67/access/components/classes/PedidoTriggerHandler.cls
inventory/org-dev/api-v67/access/components/classes/PedidoTriggerHandler.cls-meta.xml
inventory/org-dev/api-v67/access/components/connectedApps/Meu_App.connectedApp-meta.xml
inventory/org-dev/api-v67/access/components/escalationRules/Case.escalationRules-meta.xml
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/config/portal_clientes1.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/routes/home.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/routes/login.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/themes/tema.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/views/home.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1/views/login.json
inventory/org-dev/api-v67/access/components/experiences/Portal_Clientes1.site-meta.xml
inventory/org-dev/api-v67/access/components/externalClientApps/Minha_ECA.eca-meta.xml
inventory/org-dev/api-v67/access/components/externalCredentials/Minha_EC.externalCredential-meta.xml
inventory/org-dev/api-v67/access/components/flexipages/Pedido_Record_Page.flexipage-meta.xml
inventory/org-dev/api-v67/access/components/flexipages/Pedidos_App_Page.flexipage-meta.xml
inventory/org-dev/api-v67/access/components/flows/Meu_Flow.flow-meta.xml
inventory/org-dev/api-v67/access/components/flows/Pedido_Evento_Flow.flow-meta.xml
inventory/org-dev/api-v67/access/components/flows/Processa_Pedido.flow-meta.xml
inventory/org-dev/api-v67/access/components/flows/Tela_Cadastro.flow-meta.xml
inventory/org-dev/api-v67/access/components/groups/Grupo_Suporte.group-meta.xml
inventory/org-dev/api-v67/access/components/leadConvertSettings/LeadConvertSettings.LeadConvertSetting-meta.xml
inventory/org-dev/api-v67/access/components/lwc/pedidoAcaoRapida/pedidoAcaoRapida.js
inventory/org-dev/api-v67/access/components/lwc/pedidoAcaoRapida/pedidoAcaoRapida.js-meta.xml
inventory/org-dev/api-v67/access/components/lwc/pedidoPainel/__tests__/pedidoPainel.test.js
inventory/org-dev/api-v67/access/components/lwc/pedidoPainel/pedidoPainel.css
inventory/org-dev/api-v67/access/components/lwc/pedidoPainel/pedidoPainel.html
inventory/org-dev/api-v67/access/components/lwc/pedidoPainel/pedidoPainel.js
inventory/org-dev/api-v67/access/components/lwc/pedidoPainel/pedidoPainel.js-meta.xml
inventory/org-dev/api-v67/access/components/lwc/pedidoTelaFlow/pedidoTelaFlow.html
inventory/org-dev/api-v67/access/components/lwc/pedidoTelaFlow/pedidoTelaFlow.js
inventory/org-dev/api-v67/access/components/lwc/pedidoTelaFlow/pedidoTelaFlow.js-meta.xml
inventory/org-dev/api-v67/access/components/namedCredentials/Minha_NC.namedCredential-meta.xml
inventory/org-dev/api-v67/access/components/namedCredentials/NC_Legada.namedCredential-meta.xml
inventory/org-dev/api-v67/access/components/networks/Portal_Clientes.network-meta.xml
inventory/org-dev/api-v67/access/components/objects/Config__mdt/Config__mdt.object-meta.xml
inventory/org-dev/api-v67/access/components/objects/Config__mdt/fields/Ativo__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Config__mdt/fields/Chave_API__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Opportunity/businessProcesses/Venda_Enterprise.businessProcess-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido_Evento__e/Pedido_Evento__e.object-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido_Evento__e/fields/Numero_Pedido__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido_Evento__e/fields/Payload__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/Pedido__c.object-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/fields/Status__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/fields/Valor__c.field-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/recordTypes/Padrao.recordType-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/validationRules/Valor_Positivo.validationRule-meta.xml
inventory/org-dev/api-v67/access/components/objects/Pedido__c/webLinks/Imprimir_Pedido.webLink-meta.xml
inventory/org-dev/api-v67/access/components/omniDataTransforms/ExtrairPedido.rpt-meta.xml
inventory/org-dev/api-v67/access/components/omniIntegrationProcedures/Pedido_EnviarERP_Procedure_1.oip-meta.xml
inventory/org-dev/api-v67/access/components/omniScripts/Vendas_CriarPedido_Portuguese_1.os-meta.xml
inventory/org-dev/api-v67/access/components/omniUiCards/CartaoPedido_1.ouc-meta.xml
inventory/org-dev/api-v67/access/components/opportunitySplitTypes/Receita_Principal.opportunitySplitType-meta.xml
inventory/org-dev/api-v67/access/components/permissionsetgroups/PSG_Integracao.permissionsetgroup-meta.xml
inventory/org-dev/api-v67/access/components/permissionsets/Integracao_API.permissionset-meta.xml
inventory/org-dev/api-v67/access/components/permissionsets/Leitura_Pedidos.permissionset-meta.xml
inventory/org-dev/api-v67/access/components/platformEventChannelMembers/Canal_Pedido_Pedido_ChangeEvent.platformEventChannelMember-meta.xml
inventory/org-dev/api-v67/access/components/platformEventChannelMembers/ChangeEvents_Pedido_ChangeEvent.platformEventChannelMember-meta.xml
inventory/org-dev/api-v67/access/components/platformEventSubscriberConfigs/PedidoEventoTriggerConfig.platformEventSubscriberConfig-meta.xml
inventory/org-dev/api-v67/access/components/profiles/Admin.profile-meta.xml
inventory/org-dev/api-v67/access/components/profiles/Portal Clientes Profile.profile-meta.xml
inventory/org-dev/api-v67/access/components/profiles/Vendas.profile-meta.xml
inventory/org-dev/api-v67/access/components/queues/Fila_Pedidos.queue-meta.xml
inventory/org-dev/api-v67/access/components/remoteSiteSettings/Meu_Site.remoteSite-meta.xml
inventory/org-dev/api-v67/access/components/roles/Diretoria.role-meta.xml
inventory/org-dev/api-v67/access/components/roles/Gerente_Vendas.role-meta.xml
inventory/org-dev/api-v67/access/components/roles/Vendas.role-meta.xml
inventory/org-dev/api-v67/access/components/settings/Security.settings-meta.xml
inventory/org-dev/api-v67/access/components/sharingRules/Pedido__c.sharingRules-meta.xml
inventory/org-dev/api-v67/access/components/sites/Portal_Clientes.site-meta.xml
inventory/org-dev/api-v67/access/components/territory2Models/Modelo_Vendas/Modelo_Vendas.territory2Model-meta.xml
inventory/org-dev/api-v67/access/components/triggers/PedidoAuditoriaTrigger.trigger
inventory/org-dev/api-v67/access/components/triggers/PedidoAuditoriaTrigger.trigger-meta.xml
inventory/org-dev/api-v67/access/components/triggers/PedidoChangeTrigger.trigger
inventory/org-dev/api-v67/access/components/triggers/PedidoChangeTrigger.trigger-meta.xml
inventory/org-dev/api-v67/access/components/triggers/PedidoEventoTrigger.trigger
inventory/org-dev/api-v67/access/components/triggers/PedidoEventoTrigger.trigger-meta.xml
inventory/org-dev/api-v67/access/components/triggers/PedidoTrigger.trigger
inventory/org-dev/api-v67/access/components/triggers/PedidoTrigger.trigger-meta.xml
inventory/org-dev/api-v67/access/retrieve.raw.json
inventory/org-dev/api-v67/apex-classes/components/classes/AccountSyncQueueable.cls
inventory/org-dev/api-v67/apex-classes/components/classes/AccountSyncQueueable.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/DailyOrderCleanupScheduler.cls
inventory/org-dev/api-v67/apex-classes/components/classes/DailyOrderCleanupScheduler.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/IntegrationAsyncHelper.cls
inventory/org-dev/api-v67/apex-classes/components/classes/IntegrationAsyncHelper.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/MultiRoleJob.cls
inventory/org-dev/api-v67/apex-classes/components/classes/MultiRoleJob.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/OrderCleanupBatch.cls
inventory/org-dev/api-v67/apex-classes/components/classes/OrderCleanupBatch.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoController.cls
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoController.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoService.cls
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoService.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoTriggerHandler.cls
inventory/org-dev/api-v67/apex-classes/components/classes/PedidoTriggerHandler.cls-meta.xml
inventory/org-dev/api-v67/apex-classes/internal-data/accountsyncqueueable.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/dailyordercleanupscheduler.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/integrationasynchelper.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/multirolejob.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/ordercleanupbatch.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/pedidocontroller.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/pedidoservice.raw.json
inventory/org-dev/api-v67/apex-classes/internal-data/pedidotriggerhandler.raw.json
inventory/org-dev/api-v67/apex-classes/inventory.index.json
inventory/org-dev/api-v67/apex-classes/inventory.raw.json
inventory/org-dev/api-v67/apex-classes/normalized/accountsyncqueueable.json
inventory/org-dev/api-v67/apex-classes/normalized/dailyordercleanupscheduler.json
inventory/org-dev/api-v67/apex-classes/normalized/integrationasynchelper.json
inventory/org-dev/api-v67/apex-classes/normalized/multirolejob.json
inventory/org-dev/api-v67/apex-classes/normalized/ordercleanupbatch.json
inventory/org-dev/api-v67/apex-classes/normalized/pedidocontroller.json
inventory/org-dev/api-v67/apex-classes/normalized/pedidoservice.json
inventory/org-dev/api-v67/apex-classes/normalized/pedidotriggerhandler.json
inventory/org-dev/api-v67/apex-classes/retrieve/accountsyncqueueable.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/dailyordercleanupscheduler.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/integrationasynchelper.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/multirolejob.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/ordercleanupbatch.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/pedidocontroller.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/pedidoservice.raw.json
inventory/org-dev/api-v67/apex-classes/retrieve/pedidotriggerhandler.raw.json
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoAuditoriaTrigger.trigger
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoAuditoriaTrigger.trigger-meta.xml
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoChangeTrigger.trigger
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoChangeTrigger.trigger-meta.xml
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoEventoTrigger.trigger
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoEventoTrigger.trigger-meta.xml
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoTrigger.trigger
inventory/org-dev/api-v67/apex-triggers/components/triggers/PedidoTrigger.trigger-meta.xml
inventory/org-dev/api-v67/apex-triggers/internal-data/pedidoauditoriatrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/internal-data/pedidochangetrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/internal-data/pedidoeventotrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/internal-data/pedidotrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/inventory.index.json
inventory/org-dev/api-v67/apex-triggers/inventory.raw.json
inventory/org-dev/api-v67/apex-triggers/normalized/pedidoauditoriatrigger.json
inventory/org-dev/api-v67/apex-triggers/normalized/pedidochangetrigger.json
inventory/org-dev/api-v67/apex-triggers/normalized/pedidoeventotrigger.json
inventory/org-dev/api-v67/apex-triggers/normalized/pedidotrigger.json
inventory/org-dev/api-v67/apex-triggers/retrieve/pedidoauditoriatrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/retrieve/pedidochangetrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/retrieve/pedidoeventotrigger.raw.json
inventory/org-dev/api-v67/apex-triggers/retrieve/pedidotrigger.raw.json
inventory/org-dev/api-v67/assignment-rules/components/assignmentRules/Case.assignmentRules-meta.xml
inventory/org-dev/api-v67/assignment-rules/internal-data/case.raw.json
inventory/org-dev/api-v67/assignment-rules/inventory.index.json
inventory/org-dev/api-v67/assignment-rules/inventory.raw.json
inventory/org-dev/api-v67/assignment-rules/normalized/case.json
inventory/org-dev/api-v67/assignment-rules/retrieve/case.raw.json
inventory/org-dev/api-v67/auto-response-rules/components/autoResponseRules/Case.autoResponseRules-meta.xml
inventory/org-dev/api-v67/auto-response-rules/internal-data/case.raw.json
inventory/org-dev/api-v67/auto-response-rules/inventory.index.json
inventory/org-dev/api-v67/auto-response-rules/inventory.raw.json
inventory/org-dev/api-v67/auto-response-rules/normalized/case.json
inventory/org-dev/api-v67/auto-response-rules/retrieve/case.raw.json
inventory/org-dev/api-v67/business-processes/components/objects/Opportunity/businessProcesses/Venda_Enterprise.businessProcess-meta.xml
inventory/org-dev/api-v67/business-processes/internal-data/opportunity-venda-enterprise.raw.json
inventory/org-dev/api-v67/business-processes/inventory.index.json
inventory/org-dev/api-v67/business-processes/inventory.raw.json
inventory/org-dev/api-v67/business-processes/normalized/opportunity-venda-enterprise.json
inventory/org-dev/api-v67/business-processes/retrieve/opportunity-venda-enterprise.raw.json
inventory/org-dev/api-v67/certificates/components/certs/Meu_Certificado.crt
inventory/org-dev/api-v67/certificates/components/certs/Meu_Certificado.crt-meta.xml
inventory/org-dev/api-v67/certificates/internal-data/meu-certificado.raw.json
inventory/org-dev/api-v67/certificates/inventory.index.json
inventory/org-dev/api-v67/certificates/inventory.raw.json
inventory/org-dev/api-v67/certificates/normalized/meu-certificado.json
inventory/org-dev/api-v67/certificates/retrieve/meu-certificado.raw.json
inventory/org-dev/api-v67/connected-apps/components/connectedApps/Meu_App.connectedApp-meta.xml
inventory/org-dev/api-v67/connected-apps/internal-data/meu-app.raw.json
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
inventory/org-dev/api-v67/custom-metadata/normalized/config-mdt.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-padrao.json
inventory/org-dev/api-v67/custom-metadata/normalized/config-secundario.json
inventory/org-dev/api-v67/custom-metadata/normalized/custom-field--config-mdt-ativo-c.json
inventory/org-dev/api-v67/custom-metadata/normalized/custom-field--config-mdt-chave-api-c.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-mdt.raw.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-padrao.raw.json
inventory/org-dev/api-v67/custom-metadata/retrieve/config-secundario.raw.json
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido_Evento__e/Pedido_Evento__e.object-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido_Evento__e/fields/Numero_Pedido__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido_Evento__e/fields/Payload__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/Pedido__c.object-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/fields/Status__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/fields/Valor__c.field-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/recordTypes/Padrao.recordType-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/validationRules/Valor_Positivo.validationRule-meta.xml
inventory/org-dev/api-v67/custom-objects/components/objects/Pedido__c/webLinks/Imprimir_Pedido.webLink-meta.xml
inventory/org-dev/api-v67/custom-objects/internal-data/config-mdt.raw.json
inventory/org-dev/api-v67/custom-objects/internal-data/pedido-c.raw.json
inventory/org-dev/api-v67/custom-objects/internal-data/pedido-evento-e.raw.json
inventory/org-dev/api-v67/custom-objects/inventory.index.json
inventory/org-dev/api-v67/custom-objects/inventory.raw.json
inventory/org-dev/api-v67/custom-objects/normalized/custom-field--pedido-c-status-c.json
inventory/org-dev/api-v67/custom-objects/normalized/custom-field--pedido-c-valor-c.json
inventory/org-dev/api-v67/custom-objects/normalized/custom-field--pedido-evento-e-numero-pedido-c.json
inventory/org-dev/api-v67/custom-objects/normalized/custom-field--pedido-evento-e-payload-c.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-c.json
inventory/org-dev/api-v67/custom-objects/normalized/pedido-evento-e.json
inventory/org-dev/api-v67/custom-objects/normalized/record-type--pedido-c-padrao.json
inventory/org-dev/api-v67/custom-objects/normalized/validation-rule--pedido-c-valor-positivo.json
inventory/org-dev/api-v67/custom-objects/normalized/web-link--pedido-c-imprimir-pedido.json
inventory/org-dev/api-v67/custom-objects/retrieve/pedido-c.raw.json
inventory/org-dev/api-v67/custom-objects/retrieve/pedido-evento-e.raw.json
inventory/org-dev/api-v67/escalation-rules/components/escalationRules/Case.escalationRules-meta.xml
inventory/org-dev/api-v67/escalation-rules/internal-data/case.raw.json
inventory/org-dev/api-v67/escalation-rules/inventory.index.json
inventory/org-dev/api-v67/escalation-rules/inventory.raw.json
inventory/org-dev/api-v67/escalation-rules/normalized/case.json
inventory/org-dev/api-v67/escalation-rules/retrieve/case.raw.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/config/portal_clientes1.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/routes/home.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/routes/login.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/themes/tema.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/views/home.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1/views/login.json
inventory/org-dev/api-v67/experiences/components/experiences/Portal_Clientes1.site-meta.xml
inventory/org-dev/api-v67/experiences/inventory.index.json
inventory/org-dev/api-v67/experiences/inventory.raw.json
inventory/org-dev/api-v67/experiences/normalized/portal-clientes1.json
inventory/org-dev/api-v67/experiences/retrieve/portal-clientes1.raw.json
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
inventory/org-dev/api-v67/flexipages/components/flexipages/Pedido_Record_Page.flexipage-meta.xml
inventory/org-dev/api-v67/flexipages/components/flexipages/Pedidos_App_Page.flexipage-meta.xml
inventory/org-dev/api-v67/flexipages/internal-data/pedido-record-page.raw.json
inventory/org-dev/api-v67/flexipages/internal-data/pedidos-app-page.raw.json
inventory/org-dev/api-v67/flexipages/inventory.index.json
inventory/org-dev/api-v67/flexipages/inventory.raw.json
inventory/org-dev/api-v67/flexipages/normalized/pedido-record-page.json
inventory/org-dev/api-v67/flexipages/normalized/pedidos-app-page.json
inventory/org-dev/api-v67/flexipages/retrieve/pedido-record-page.raw.json
inventory/org-dev/api-v67/flexipages/retrieve/pedidos-app-page.raw.json
inventory/org-dev/api-v67/flow-definitions/components/flowDefinitions/Meu_Flow.flowDefinition-meta.xml
inventory/org-dev/api-v67/flow-definitions/inventory.index.json
inventory/org-dev/api-v67/flow-definitions/inventory.raw.json
inventory/org-dev/api-v67/flow-definitions/normalized/meu-flow.json
inventory/org-dev/api-v67/flow-definitions/retrieve/meu-flow.raw.json
inventory/org-dev/api-v67/flows/components/flows/Meu_Flow.flow-meta.xml
inventory/org-dev/api-v67/flows/components/flows/Pedido_Evento_Flow.flow-meta.xml
inventory/org-dev/api-v67/flows/components/flows/Processa_Pedido.flow-meta.xml
inventory/org-dev/api-v67/flows/components/flows/Tela_Cadastro.flow-meta.xml
inventory/org-dev/api-v67/flows/internal-data/meu-flow.raw.json
inventory/org-dev/api-v67/flows/internal-data/pedido-evento-flow.raw.json
inventory/org-dev/api-v67/flows/internal-data/processa-pedido.raw.json
inventory/org-dev/api-v67/flows/internal-data/tela-cadastro.raw.json
inventory/org-dev/api-v67/flows/inventory.index.json
inventory/org-dev/api-v67/flows/inventory.raw.json
inventory/org-dev/api-v67/flows/normalized/meu-flow.json
inventory/org-dev/api-v67/flows/normalized/pedido-evento-flow.json
inventory/org-dev/api-v67/flows/normalized/processa-pedido.json
inventory/org-dev/api-v67/flows/normalized/tela-cadastro.json
inventory/org-dev/api-v67/flows/retrieve/meu-flow.raw.json
inventory/org-dev/api-v67/flows/retrieve/pedido-evento-flow.raw.json
inventory/org-dev/api-v67/flows/retrieve/processa-pedido.raw.json
inventory/org-dev/api-v67/flows/retrieve/tela-cadastro.raw.json
inventory/org-dev/api-v67/lead-convert-settings/components/leadConvertSettings/LeadConvertSettings.LeadConvertSetting-meta.xml
inventory/org-dev/api-v67/lead-convert-settings/normalized/leadconvertsettings.json
inventory/org-dev/api-v67/lead-convert-settings/retrieve/leadconvertsettings.raw.json
inventory/org-dev/api-v67/lwc/components/lwc/pedidoAcaoRapida/pedidoAcaoRapida.js
inventory/org-dev/api-v67/lwc/components/lwc/pedidoAcaoRapida/pedidoAcaoRapida.js-meta.xml
inventory/org-dev/api-v67/lwc/components/lwc/pedidoPainel/__tests__/pedidoPainel.test.js
inventory/org-dev/api-v67/lwc/components/lwc/pedidoPainel/pedidoPainel.css
inventory/org-dev/api-v67/lwc/components/lwc/pedidoPainel/pedidoPainel.html
inventory/org-dev/api-v67/lwc/components/lwc/pedidoPainel/pedidoPainel.js
inventory/org-dev/api-v67/lwc/components/lwc/pedidoPainel/pedidoPainel.js-meta.xml
inventory/org-dev/api-v67/lwc/components/lwc/pedidoTelaFlow/pedidoTelaFlow.html
inventory/org-dev/api-v67/lwc/components/lwc/pedidoTelaFlow/pedidoTelaFlow.js
inventory/org-dev/api-v67/lwc/components/lwc/pedidoTelaFlow/pedidoTelaFlow.js-meta.xml
inventory/org-dev/api-v67/lwc/internal-data/pedidoacaorapida.raw.json
inventory/org-dev/api-v67/lwc/internal-data/pedidopainel.raw.json
inventory/org-dev/api-v67/lwc/internal-data/pedidotelaflow.raw.json
inventory/org-dev/api-v67/lwc/inventory.index.json
inventory/org-dev/api-v67/lwc/inventory.raw.json
inventory/org-dev/api-v67/lwc/normalized/pedidoacaorapida.json
inventory/org-dev/api-v67/lwc/normalized/pedidopainel.json
inventory/org-dev/api-v67/lwc/normalized/pedidotelaflow.json
inventory/org-dev/api-v67/lwc/retrieve/pedidoacaorapida.raw.json
inventory/org-dev/api-v67/lwc/retrieve/pedidopainel.raw.json
inventory/org-dev/api-v67/lwc/retrieve/pedidotelaflow.raw.json
inventory/org-dev/api-v67/named-credentials/components/namedCredentials/Minha_NC.namedCredential-meta.xml
inventory/org-dev/api-v67/named-credentials/components/namedCredentials/NC_Legada.namedCredential-meta.xml
inventory/org-dev/api-v67/named-credentials/internal-data/minha-nc.raw.json
inventory/org-dev/api-v67/named-credentials/internal-data/nc-legada.raw.json
inventory/org-dev/api-v67/named-credentials/inventory.index.json
inventory/org-dev/api-v67/named-credentials/inventory.raw.json
inventory/org-dev/api-v67/named-credentials/normalized/minha-nc.json
inventory/org-dev/api-v67/named-credentials/normalized/nc-legada.json
inventory/org-dev/api-v67/named-credentials/retrieve/minha-nc.raw.json
inventory/org-dev/api-v67/named-credentials/retrieve/nc-legada.raw.json
inventory/org-dev/api-v67/networks/components/networks/Portal_Clientes.network-meta.xml
inventory/org-dev/api-v67/networks/internal-data/portal-clientes.raw.json
inventory/org-dev/api-v67/networks/inventory.index.json
inventory/org-dev/api-v67/networks/inventory.raw.json
inventory/org-dev/api-v67/networks/normalized/portal-clientes.json
inventory/org-dev/api-v67/networks/retrieve/portal-clientes.raw.json
inventory/org-dev/api-v67/omni-data-transforms/components/omniDataTransforms/ExtrairPedido.rpt-meta.xml
inventory/org-dev/api-v67/omni-data-transforms/internal-data/extrairpedido.raw.json
inventory/org-dev/api-v67/omni-data-transforms/inventory.index.json
inventory/org-dev/api-v67/omni-data-transforms/inventory.raw.json
inventory/org-dev/api-v67/omni-data-transforms/normalized/extrairpedido.json
inventory/org-dev/api-v67/omni-data-transforms/retrieve/extrairpedido.raw.json
inventory/org-dev/api-v67/omni-integration-procedures/components/omniIntegrationProcedures/Pedido_EnviarERP_Procedure_1.oip-meta.xml
inventory/org-dev/api-v67/omni-integration-procedures/internal-data/pedido-enviarerp-procedure-1.raw.json
inventory/org-dev/api-v67/omni-integration-procedures/inventory.index.json
inventory/org-dev/api-v67/omni-integration-procedures/inventory.raw.json
inventory/org-dev/api-v67/omni-integration-procedures/normalized/pedido-enviarerp-procedure-1.json
inventory/org-dev/api-v67/omni-integration-procedures/retrieve/pedido-enviarerp-procedure-1.raw.json
inventory/org-dev/api-v67/omni-scripts/components/omniScripts/Vendas_CriarPedido_Portuguese_1.os-meta.xml
inventory/org-dev/api-v67/omni-scripts/internal-data/vendas-criarpedido-portuguese-1.raw.json
inventory/org-dev/api-v67/omni-scripts/inventory.index.json
inventory/org-dev/api-v67/omni-scripts/inventory.raw.json
inventory/org-dev/api-v67/omni-scripts/normalized/vendas-criarpedido-portuguese-1.json
inventory/org-dev/api-v67/omni-scripts/retrieve/vendas-criarpedido-portuguese-1.raw.json
inventory/org-dev/api-v67/omni-ui-cards/components/omniUiCards/CartaoPedido_1.ouc-meta.xml
inventory/org-dev/api-v67/omni-ui-cards/internal-data/cartaopedido-1.raw.json
inventory/org-dev/api-v67/omni-ui-cards/inventory.index.json
inventory/org-dev/api-v67/omni-ui-cards/inventory.raw.json
inventory/org-dev/api-v67/omni-ui-cards/normalized/cartaopedido-1.json
inventory/org-dev/api-v67/omni-ui-cards/retrieve/cartaopedido-1.raw.json
inventory/org-dev/api-v67/opportunity-split-types/components/opportunitySplitTypes/Receita_Principal.opportunitySplitType-meta.xml
inventory/org-dev/api-v67/opportunity-split-types/internal-data/receita-principal.raw.json
inventory/org-dev/api-v67/opportunity-split-types/inventory.index.json
inventory/org-dev/api-v67/opportunity-split-types/inventory.raw.json
inventory/org-dev/api-v67/opportunity-split-types/normalized/receita-principal.json
inventory/org-dev/api-v67/opportunity-split-types/retrieve/receita-principal.raw.json
inventory/org-dev/api-v67/org-security/components/settings/Security.settings-meta.xml
inventory/org-dev/api-v67/org-security/normalized/security.json
inventory/org-dev/api-v67/org-security/retrieve/security.raw.json
inventory/org-dev/api-v67/permission-set-groups/internal-data/psg-integracao.raw.json
inventory/org-dev/api-v67/permission-set-groups/inventory.index.json
inventory/org-dev/api-v67/permission-set-groups/inventory.raw.json
inventory/org-dev/api-v67/permission-set-groups/normalized/psg-integracao.json
inventory/org-dev/api-v67/permission-sets/internal-data/integracao-api.raw.json
inventory/org-dev/api-v67/permission-sets/internal-data/leitura-pedidos.raw.json
inventory/org-dev/api-v67/permission-sets/inventory.index.json
inventory/org-dev/api-v67/permission-sets/inventory.raw.json
inventory/org-dev/api-v67/permission-sets/normalized/integracao-api.json
inventory/org-dev/api-v67/permission-sets/normalized/leitura-pedidos.json
inventory/org-dev/api-v67/platform-event-channel-members/components/platformEventChannelMembers/Canal_Pedido_Pedido_ChangeEvent.platformEventChannelMember-meta.xml
inventory/org-dev/api-v67/platform-event-channel-members/components/platformEventChannelMembers/ChangeEvents_Pedido_ChangeEvent.platformEventChannelMember-meta.xml
inventory/org-dev/api-v67/platform-event-channel-members/internal-data/canal-pedido-pedido-changeevent.raw.json
inventory/org-dev/api-v67/platform-event-channel-members/internal-data/changeevents-pedido-changeevent.raw.json
inventory/org-dev/api-v67/platform-event-channel-members/inventory.index.json
inventory/org-dev/api-v67/platform-event-channel-members/inventory.raw.json
inventory/org-dev/api-v67/platform-event-channel-members/normalized/canal-pedido-pedido-changeevent.json
inventory/org-dev/api-v67/platform-event-channel-members/normalized/changeevents-pedido-changeevent.json
inventory/org-dev/api-v67/platform-event-channel-members/retrieve/canal-pedido-pedido-changeevent.raw.json
inventory/org-dev/api-v67/platform-event-channel-members/retrieve/changeevents-pedido-changeevent.raw.json
inventory/org-dev/api-v67/profiles/internal-data/admin.raw.json
inventory/org-dev/api-v67/profiles/internal-data/portal-clientes-profile.raw.json
inventory/org-dev/api-v67/profiles/internal-data/vendas.raw.json
inventory/org-dev/api-v67/profiles/inventory.index.json
inventory/org-dev/api-v67/profiles/inventory.raw.json
inventory/org-dev/api-v67/profiles/normalized/admin.json
inventory/org-dev/api-v67/profiles/normalized/portal-clientes-profile.json
inventory/org-dev/api-v67/profiles/normalized/vendas.json
inventory/org-dev/api-v67/public-groups/components/groups/Grupo_Suporte.group-meta.xml
inventory/org-dev/api-v67/public-groups/internal-data/grupo-suporte.raw.json
inventory/org-dev/api-v67/public-groups/inventory.index.json
inventory/org-dev/api-v67/public-groups/inventory.raw.json
inventory/org-dev/api-v67/public-groups/normalized/grupo-suporte.json
inventory/org-dev/api-v67/public-groups/retrieve/grupo-suporte.raw.json
inventory/org-dev/api-v67/queues/internal-data/fila-pedidos.raw.json
inventory/org-dev/api-v67/queues/inventory.index.json
inventory/org-dev/api-v67/queues/inventory.raw.json
inventory/org-dev/api-v67/queues/normalized/fila-pedidos.json
inventory/org-dev/api-v67/record-type/components/objects/Opportunity/recordTypes/Enterprise.recordType-meta.xml
inventory/org-dev/api-v67/record-type/components/objects/Opportunity/recordTypes/Varejo.recordType-meta.xml
inventory/org-dev/api-v67/record-type/inventory.index.json
inventory/org-dev/api-v67/record-type/inventory.raw.json
inventory/org-dev/api-v67/record-type/normalized/opportunity-enterprise.json
inventory/org-dev/api-v67/record-type/normalized/opportunity-varejo.json
inventory/org-dev/api-v67/record-type/retrieve/opportunity-enterprise.raw.json
inventory/org-dev/api-v67/record-type/retrieve/opportunity-varejo.raw.json
inventory/org-dev/api-v67/remote-site-settings/components/remoteSiteSettings/Meu_Site.remoteSite-meta.xml
inventory/org-dev/api-v67/remote-site-settings/inventory.index.json
inventory/org-dev/api-v67/remote-site-settings/inventory.raw.json
inventory/org-dev/api-v67/remote-site-settings/normalized/meu-site.json
inventory/org-dev/api-v67/remote-site-settings/retrieve/meu-site.raw.json
inventory/org-dev/api-v67/roles/components/roles/Diretoria.role-meta.xml
inventory/org-dev/api-v67/roles/components/roles/Gerente_Vendas.role-meta.xml
inventory/org-dev/api-v67/roles/components/roles/Vendas.role-meta.xml
inventory/org-dev/api-v67/roles/internal-data/diretoria.raw.json
inventory/org-dev/api-v67/roles/internal-data/gerente-vendas.raw.json
inventory/org-dev/api-v67/roles/internal-data/vendas.raw.json
inventory/org-dev/api-v67/roles/inventory.index.json
inventory/org-dev/api-v67/roles/inventory.raw.json
inventory/org-dev/api-v67/roles/normalized/diretoria.json
inventory/org-dev/api-v67/roles/normalized/gerente-vendas.json
inventory/org-dev/api-v67/roles/normalized/vendas.json
inventory/org-dev/api-v67/roles/retrieve/diretoria.raw.json
inventory/org-dev/api-v67/roles/retrieve/gerente-vendas.raw.json
inventory/org-dev/api-v67/roles/retrieve/vendas.raw.json
inventory/org-dev/api-v67/settings/internal-data/security.raw.json
inventory/org-dev/api-v67/sharing-rules/inventory.index.json
inventory/org-dev/api-v67/sharing-rules/inventory.raw.json
inventory/org-dev/api-v67/sharing-rules/normalized/pedido-c.json
inventory/org-dev/api-v67/sites/components/sites/Portal_Clientes.site-meta.xml
inventory/org-dev/api-v67/sites/internal-data/portal-clientes.raw.json
inventory/org-dev/api-v67/sites/inventory.index.json
inventory/org-dev/api-v67/sites/inventory.raw.json
inventory/org-dev/api-v67/sites/normalized/portal-clientes.json
inventory/org-dev/api-v67/sites/retrieve/portal-clientes.raw.json
inventory/org-dev/api-v67/territory2-models/components/territory2Models/Modelo_Vendas/Modelo_Vendas.territory2Model-meta.xml
inventory/org-dev/api-v67/territory2-models/components/territory2Models/Modelo_Vendas/rules/Regra_SP.territory2Rule-meta.xml
inventory/org-dev/api-v67/territory2-models/components/territory2Models/Modelo_Vendas/territories/Sudeste.territory2-meta.xml
inventory/org-dev/api-v67/territory2-models/internal-data/modelo-vendas.raw.json
inventory/org-dev/api-v67/territory2-models/inventory.index.json
inventory/org-dev/api-v67/territory2-models/inventory.raw.json
inventory/org-dev/api-v67/territory2-models/normalized/modelo-vendas-regra-sp.json
inventory/org-dev/api-v67/territory2-models/normalized/modelo-vendas-sudeste.json
inventory/org-dev/api-v67/territory2-models/normalized/modelo-vendas.json
inventory/org-dev/api-v67/territory2-models/retrieve/modelo-vendas-regra-sp.raw.json
inventory/org-dev/api-v67/territory2-models/retrieve/modelo-vendas-sudeste.raw.json
inventory/org-dev/api-v67/territory2-models/retrieve/modelo-vendas.raw.json
runs/run-20261013-203232/resumo.md
runs/run-20261013-203232.json
saida/docs/doc-dev-101326/.manifest.json
saida/docs/doc-dev-101326/.org.json
saida/docs/doc-dev-101326/doc-accountsyncqueueable-apex-class.md
saida/docs/doc-dev-101326/doc-accountsyncqueueable-apex-queueable.md
saida/docs/doc-dev-101326/doc-admin-profile.md
saida/docs/doc-dev-101326/doc-canal-pedido-pedido-changeevent-change-data-capture.md
saida/docs/doc-dev-101326/doc-cartaopedido-1-flexcard.md
saida/docs/doc-dev-101326/doc-case-assignment-rules.md
saida/docs/doc-dev-101326/doc-case-auto-response-rules.md
saida/docs/doc-dev-101326/doc-case-escalation-rules.md
saida/docs/doc-dev-101326/doc-changeevents-pedido-changeevent-change-data-capture.md
saida/docs/doc-dev-101326/doc-config-mdt-custom-metadata.md
saida/docs/doc-dev-101326/doc-dailyordercleanupscheduler-apex-class.md
saida/docs/doc-dev-101326/doc-dailyordercleanupscheduler-apex-scheduler.md
saida/docs/doc-dev-101326/doc-diretoria-role.md
saida/docs/doc-dev-101326/doc-extrairpedido-dataraptor.md
saida/docs/doc-dev-101326/doc-fila-pedidos-queue.md
saida/docs/doc-dev-101326/doc-gerente-vendas-role.md
saida/docs/doc-dev-101326/doc-grupo-suporte-public-group.md
saida/docs/doc-dev-101326/doc-integracao-api-permission-set.md
saida/docs/doc-dev-101326/doc-integrationasynchelper-apex-class.md
saida/docs/doc-dev-101326/doc-integrationasynchelper-processordersasync-apex-future.md
saida/docs/doc-dev-101326/doc-integrationasynchelper-recalc-apex-future.md
saida/docs/doc-dev-101326/doc-leadconvertsettings-lead-convert.md
saida/docs/doc-dev-101326/doc-leitura-pedidos-permission-set.md
saida/docs/doc-dev-101326/doc-meu-app-connected-app.md
saida/docs/doc-dev-101326/doc-meu-certificado-certificate.md
saida/docs/doc-dev-101326/doc-meu-flow-flow-trigger.md
saida/docs/doc-dev-101326/doc-meu-flow-flow.md
saida/docs/doc-dev-101326/doc-meu-site-remote-site-setting.md
saida/docs/doc-dev-101326/doc-minha-ec-external-credential.md
saida/docs/doc-dev-101326/doc-minha-eca-external-client-app.md
saida/docs/doc-dev-101326/doc-minha-nc-named-credential.md
saida/docs/doc-dev-101326/doc-modelo-vendas-territory-model.md
saida/docs/doc-dev-101326/doc-multirolejob-apex-batch.md
saida/docs/doc-dev-101326/doc-multirolejob-apex-class.md
saida/docs/doc-dev-101326/doc-multirolejob-apex-scheduler.md
saida/docs/doc-dev-101326/doc-nc-legada-named-credential.md
saida/docs/doc-dev-101326/doc-opportunity-venda-enterprise-business-process.md
saida/docs/doc-dev-101326/doc-ordercleanupbatch-apex-batch.md
saida/docs/doc-dev-101326/doc-ordercleanupbatch-apex-class.md
saida/docs/doc-dev-101326/doc-pedido-c-custom-object.md
saida/docs/doc-dev-101326/doc-pedido-c-sharing-rules.md
saida/docs/doc-dev-101326/doc-pedido-enviarerp-procedure-1-integration-procedure.md
saida/docs/doc-dev-101326/doc-pedido-evento-e-platform-event.md
saida/docs/doc-dev-101326/doc-pedido-evento-flow-flow-trigger.md
saida/docs/doc-dev-101326/doc-pedido-evento-flow-flow.md
saida/docs/doc-dev-101326/doc-pedido-record-page-flexipage.md
saida/docs/doc-dev-101326/doc-pedidoacaorapida-lwc-quick-action.md
saida/docs/doc-dev-101326/doc-pedidoacaorapida-lwc.md
saida/docs/doc-dev-101326/doc-pedidoauditoriatrigger-apex-trigger.md
saida/docs/doc-dev-101326/doc-pedidochangetrigger-apex-trigger.md
saida/docs/doc-dev-101326/doc-pedidocontroller-apex-class.md
saida/docs/doc-dev-101326/doc-pedidoeventotrigger-apex-trigger.md
saida/docs/doc-dev-101326/doc-pedidopainel-lwc.md
saida/docs/doc-dev-101326/doc-pedidos-app-page-flexipage.md
saida/docs/doc-dev-101326/doc-pedidoservice-apex-class.md
saida/docs/doc-dev-101326/doc-pedidotelaflow-lwc-flow-screen.md
saida/docs/doc-dev-101326/doc-pedidotelaflow-lwc.md
saida/docs/doc-dev-101326/doc-pedidotrigger-apex-trigger.md
saida/docs/doc-dev-101326/doc-pedidotriggerhandler-apex-class.md
saida/docs/doc-dev-101326/doc-portal-clientes-network.md
saida/docs/doc-dev-101326/doc-portal-clientes-profile-profile.md
saida/docs/doc-dev-101326/doc-portal-clientes-site.md
saida/docs/doc-dev-101326/doc-portal-clientes1-experience.md
saida/docs/doc-dev-101326/doc-processa-pedido-flow-autolaunched.md
saida/docs/doc-dev-101326/doc-processa-pedido-flow.md
saida/docs/doc-dev-101326/doc-psg-integracao-permission-set-group.md
saida/docs/doc-dev-101326/doc-receita-principal-opportunity-split-type.md
saida/docs/doc-dev-101326/doc-security-org-security.md
saida/docs/doc-dev-101326/doc-tela-cadastro-dados-cliente-flow-screen.md
saida/docs/doc-dev-101326/doc-tela-cadastro-flow.md
saida/docs/doc-dev-101326/doc-vendas-criarpedido-portuguese-1-omniscript.md
saida/docs/doc-dev-101326/doc-vendas-profile.md
saida/docs/doc-dev-101326/doc-vendas-role.md
```

## 7. Conteúdo dos documentos finais

### `saida/docs/doc-dev-101326/doc-meu-flow-flow.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-meu-flow-flow-trigger.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-evento-flow-flow.md`

```markdown
# Flow: Pedido_Evento_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Pedido_Evento_Flow | XML |
| MasterLabel | Pedido Evento Flow | XML |
| ProcessType | AutoLaunchedFlow | XML |
| ApiVersion | 67.0 | XML |
| Description | Não informado | XML |
| Status (versão recuperada) | Active | XML |
| Status | v1: Obsolete; v2: Active | Objeto interno |

## Definição

Não aplicável

_Fonte: XML_

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-evento-flow-flow-trigger.md`

```markdown
# Flow Trigger: Pedido_Evento_Flow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Pedido_Evento_Flow | XML |
| TriggerType | PlatformEvent | XML |
| RecordTriggerType | Não informado | XML |
| Object | Pedido_Evento__e | XML |

## Condições

Não informado

_Fonte: XML_

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-processa-pedido-flow.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-processa-pedido-flow-autolaunched.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-tela-cadastro-flow.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Executar | — | XML |
| Permission Set Group | PSG_Integracao | Executar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-tela-cadastro-dados-cliente-flow-screen.md`

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

## Dados internos

| Versão | Status | Id | Fonte |
|---|---|---|---|
| 1 | Obsolete | 301000000000001AAA | Tooling API |
| 2 | Active | 301000000000002AAA | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Executar | — | XML |
| Permission Set Group | PSG_Integracao | Executar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-minha-eca-external-client-app.md`

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

_Arquivo: `inventory/org-dev/api-v67/extl-clnt-app-oauth-configurable-policies/components/extlClntAppOauthPolicies/Minha_ECA_oauthPlcy.ecaOauthPlcy-meta.xml` · sha256 `03b6ce1846607417…`_

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Vendas | Autorizado no componente | ExtlClntAppOauthConfigurablePolicies Minha_ECA_oauthPlcy | XML |
| Permission Set | Integracao_API | Autorizado no componente | ExtlClntAppOauthConfigurablePolicies Minha_ECA_oauthPlcy | XML |
| Permission Set | Leitura_Pedidos | Autorizado no componente | ExtlClntAppOauthConfigurablePolicies Minha_ECA_oauthPlcy | XML |
```

### `saida/docs/doc-dev-101326/doc-minha-ec-external-credential.md`

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

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Usar principal | Principal Principal_Integracao | XML |
| Permission Set Group | PSG_Integracao | Usar principal | Principal Principal_Integracao; Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-meu-app-connected-app.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0H4000000000001AAA | Objeto interno |
| Name | Meu_App | Objeto interno |
| OptionsAllowAdminApprovedUsersOnly | True | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Vendas | Autorizado no componente | — | XML |
| Permission Set | Integracao_API | Autorizado no componente | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-c-custom-object.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| QualifiedApiName | Pedido__c | Tooling API |
| Label | Pedido | Tooling API |
| PluralLabel | Pedidos | Tooling API |
| KeyPrefix | a01 | Tooling API |
| LastModifiedDate | 2026-01-10T12:00:00.000+0000 | Tooling API |

## Compartilhamento e filas

| Tipo | Nome | Compartilhado com | Nível de acesso | Fonte |
|---|---|---|---|---|
| Fila | Fila_Pedidos | — | — | XML |
| Regra de compartilhamento por critério | Pedidos_Altos | role: Gerente_Vendas | Read | XML |
| Regra de compartilhamento por proprietário | Pedidos_Suporte | group: Grupo_Suporte | Edit | XML |
| Regra de compartilhamento para convidado | Pedidos_Portal | guestUser: Portal_Clientes | Read | XML |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | — | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | — | XML |
| Perfil | Vendas | Ler | — | XML |
| Permission Set | Integracao_API | Ler, Editar | — | XML |
| Permission Set | Leitura_Pedidos | Ler | — | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-config-mdt-custom-metadata.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| QualifiedApiName | Config__mdt | Tooling API |
| Label | Config | Tooling API |
| PluralLabel | Configs | Tooling API |
| KeyPrefix | m00 | Tooling API |
| LastModifiedDate | 2026-01-11T12:00:00.000+0000 | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler | — | XML |
| Permission Set | Leitura_Pedidos | Ler | — | XML |
```

### `saida/docs/doc-dev-101326/doc-minha-nc-named-credential.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0XA000000000001AAA | Objeto interno |
| DeveloperName | Minha_NC | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Usar principal | ExternalCredential Minha_EC (principal Principal_Integracao) | XML |
| Permission Set Group | PSG_Integracao | Usar principal | ExternalCredential Minha_EC (principal Principal_Integracao); Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-nc-legada-named-credential.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não informado | Não informado | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-meu-site-remote-site-setting.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Remote Site Setting vale para a org inteira; não há atribuição por perfil ou permission set. | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-meu-certificado-certificate.md`

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

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | Meu_Certificado | Tooling API |
| ExpirationDate | 2027-10-01 | Tooling API |
| KeySize | 2048 | Tooling API |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Certificate não é atribuído a perfil ou permission set; o uso é configurado no componente consumidor. | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-accountsyncqueueable-apex-class.md`

```markdown
# Classe Apex: AccountSyncQueueable

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | AccountSyncQueueable | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | Não informado | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Queueable | Código Apex |
| Database.AllowsCallouts | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| execute(QueueableContext context) | void | public | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| execute | enqueueJob | AccountSyncQueueable | Não informado | 5 | Não informado | Não informado | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000000AAA | Objeto interno |
| Name | AccountSyncQueueable | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 400 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Executar | — | XML |
| Permission Set Group | PSG_Integracao | Executar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-accountsyncqueueable-apex-queueable.md`

```markdown
# Queueable Apex: AccountSyncQueueable

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | AccountSyncQueueable | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Capacidades do Queueable

| Propriedade | Valor | Fonte |
|---|---|---|
| Database.AllowsCallouts | True | Código Apex |
| Encadeia outro job no execute() | True | Código Apex |
| Finalizer anexado no execute() | True | Código Apex |
| Classe do Finalizer | IntegrationFinalizerHandler | Código Apex |
| Implementa System.Finalizer | False | Código Apex |

## Parâmetros de entrada (construtores)

| Parâmetro | Tipo | Fonte |
|---|---|---|
| accounts | List<Account> | Código Apex |
| retry | Boolean | Código Apex |

## Encadeamento no execute()

| Classe alvo | Atraso (min) | Fonte |
|---|---|---|
| AccountSyncQueueable | 5 | Código Apex |

## Convenção de nomes

- Nome: `AccountSyncQueueable`
- Convenção do projeto: sufixo `Queueable` (ex.: `AccountSyncQueueable`)
- Segue a convenção: Sim

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000000AAA | Objeto interno |
| Name | AccountSyncQueueable | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 400 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Executar | — | XML |
| Permission Set Group | PSG_Integracao | Executar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-dailyordercleanupscheduler-apex-class.md`

```markdown
# Classe Apex: DailyOrderCleanupScheduler

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | DailyOrderCleanupScheduler | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | Não informado | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| System.Schedulable | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| execute(SchedulableContext sc) | void | public | Não informado | Código Apex |
| agendar() | String | public, static | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| execute | executeBatch | OrderCleanupBatch | 200 | Não informado | Não informado | Não informado | Código Apex |
| agendar | schedule | DailyOrderCleanupScheduler | Não informado | Não informado | Limpeza Diaria de Pedidos | 0 0 1 * * ? | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000001AAA | Objeto interno |
| Name | DailyOrderCleanupScheduler | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 401 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-dailyordercleanupscheduler-apex-scheduler.md`

```markdown
# Scheduled Apex: DailyOrderCleanupScheduler

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | DailyOrderCleanupScheduler | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Capacidades do Schedulable

| Propriedade | Valor | Fonte |
|---|---|---|
| Delega para Batch/Queueable | True | Código Apex |
| Classes delegadas | OrderCleanupBatch | Código Apex |

## Jobs disparados no execute()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| executeBatch | OrderCleanupBatch | 200 | Código Apex |

## Agendamentos feitos pela própria classe

| Nome do job | Expressão cron | Classe alvo | Fonte |
|---|---|---|---|
| Limpeza Diaria de Pedidos | 0 0 1 * * ? | DailyOrderCleanupScheduler | Código Apex |

## Convenção de nomes

- Nome: `DailyOrderCleanupScheduler`
- Convenção do projeto: sufixo `Scheduler` (ex.: `DailyOrderCleanupScheduler`)
- Segue a convenção: Sim

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000001AAA | Objeto interno |
| Name | DailyOrderCleanupScheduler | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 401 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-integrationasynchelper-apex-class.md`

```markdown
# Classe Apex: IntegrationAsyncHelper

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | IntegrationAsyncHelper | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | without sharing | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Não aplicável | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| processOrdersAsync(List<Id> orderIds) | void | public, static | @future | Código Apex |
| recalc(Set<String> keys) | void | public, static | @Future | Código Apex |
| helper() | Integer | public, static | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000002AAA | Objeto interno |
| Name | IntegrationAsyncHelper | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 402 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-integrationasynchelper-processordersasync-apex-future.md`

```markdown
# Método @future: processOrdersAsync

## Identificação do método

| Propriedade | Valor | Fonte |
|---|---|---|
| Classe | IntegrationAsyncHelper | XML |
| Método | processOrdersAsync | Código Apex |
| Assinatura | processOrdersAsync(List<Id> orderIds) | Código Apex |
| Modificadores | public, static | Código Apex |
| Retorno | void | Código Apex |
| callout=true | True | Código Apex |

## Parâmetros

| Parâmetro | Tipo | Fonte |
|---|---|---|
| orderIds | List<Id> | Código Apex |

## Convenção de nomes

- Nome: `IntegrationAsyncHelper`
- Convenção do projeto: sufixo `AsyncHelper` ou `Service` na classe
- Segue a convenção: Sim

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000002AAA | Objeto interno |
| Name | IntegrationAsyncHelper | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 402 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-integrationasynchelper-recalc-apex-future.md`

```markdown
# Método @future: recalc

## Identificação do método

| Propriedade | Valor | Fonte |
|---|---|---|
| Classe | IntegrationAsyncHelper | XML |
| Método | recalc | Código Apex |
| Assinatura | recalc(Set<String> keys) | Código Apex |
| Modificadores | public, static | Código Apex |
| Retorno | void | Código Apex |
| callout=true | False | Código Apex |

## Parâmetros

| Parâmetro | Tipo | Fonte |
|---|---|---|
| keys | Set<String> | Código Apex |

## Convenção de nomes

- Nome: `IntegrationAsyncHelper`
- Convenção do projeto: sufixo `AsyncHelper` ou `Service` na classe
- Segue a convenção: Sim

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000002AAA | Objeto interno |
| Name | IntegrationAsyncHelper | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 402 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-multirolejob-apex-class.md`

```markdown
# Classe Apex: MultiRoleJob

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | MultiRoleJob | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | inherited sharing | Código Apex |
| Modificadores | global | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| database.batchable<SObject> | Código Apex |
| schedulable | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| start(Database.BatchableContext bc) | Database.QueryLocator | global | Não informado | Código Apex |
| execute(Database.BatchableContext bc, List<SObject> scope) | void | global | Não informado | Código Apex |
| finish(Database.BatchableContext bc) | void | global | Não informado | Código Apex |
| execute(SchedulableContext sc) | void | global | Não informado | Código Apex |
| montarConsulta() | String | private | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| execute | executeBatch | MultiRoleJob | 100 | Não informado | Não informado | Não informado | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000003AAA | Objeto interno |
| Name | MultiRoleJob | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 403 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-multirolejob-apex-batch.md`

```markdown
# Batch Apex: MultiRoleJob

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | MultiRoleJob | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Capacidades do Batch

| Propriedade | Valor | Fonte |
|---|---|---|
| Tipo de escopo | QueryLocator | Código Apex |
| Retorno do start() | Database.QueryLocator | Código Apex |
| Database.Stateful | False | Código Apex |
| Database.AllowsCallouts | False | Código Apex |
| Database.RaisesPlatformEvents | False | Código Apex |
| Métodos do ciclo de vida | start, execute, finish | Código Apex |

## Consulta

| Propriedade | Valor | Fonte |
|---|---|---|
| Consulta do start() | Não informado | Código Apex |
| Consulta dinâmica | True | Código Apex |
| Objeto da consulta | Não informado | Código Apex |

## Encadeamento no finish()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Convenção de nomes

- Nome: `MultiRoleJob`
- Convenção do projeto: sufixo `Batch` (ex.: `OrderCleanupBatch`)
- Segue a convenção: Não

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000003AAA | Objeto interno |
| Name | MultiRoleJob | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 403 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-multirolejob-apex-scheduler.md`

```markdown
# Scheduled Apex: MultiRoleJob

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | MultiRoleJob | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Capacidades do Schedulable

| Propriedade | Valor | Fonte |
|---|---|---|
| Delega para Batch/Queueable | True | Código Apex |
| Classes delegadas | MultiRoleJob | Código Apex |

## Jobs disparados no execute()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| executeBatch | MultiRoleJob | 100 | Código Apex |

## Agendamentos feitos pela própria classe

| Nome do job | Expressão cron | Classe alvo | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Convenção de nomes

- Nome: `MultiRoleJob`
- Convenção do projeto: sufixo `Scheduler` (ex.: `DailyOrderCleanupScheduler`)
- Segue a convenção: Não

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000003AAA | Objeto interno |
| Name | MultiRoleJob | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 403 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-ordercleanupbatch-apex-class.md`

```markdown
# Classe Apex: OrderCleanupBatch

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | OrderCleanupBatch | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Limpa pedidos cancelados (classe SIMULADA para testes). | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | with sharing | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Database.Batchable<sObject> | Código Apex |
| Database.Stateful | Código Apex |
| Database.AllowsCallouts | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| start(Database.BatchableContext bc) | Database.QueryLocator | public | Não informado | Código Apex |
| execute(Database.BatchableContext bc, List<sObject> scope) | void | public | Não informado | Código Apex |
| finish(Database.BatchableContext bc) | void | public | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| finish | executeBatch | InvoiceSyncBatch | 50 | Não informado | Não informado | Não informado | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000004AAA | Objeto interno |
| Name | OrderCleanupBatch | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 404 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-ordercleanupbatch-apex-batch.md`

```markdown
# Batch Apex: OrderCleanupBatch

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | OrderCleanupBatch | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Limpa pedidos cancelados (classe SIMULADA para testes). | Código Apex |

## Capacidades do Batch

| Propriedade | Valor | Fonte |
|---|---|---|
| Tipo de escopo | QueryLocator | Código Apex |
| Retorno do start() | Database.QueryLocator | Código Apex |
| Database.Stateful | True | Código Apex |
| Database.AllowsCallouts | True | Código Apex |
| Database.RaisesPlatformEvents | False | Código Apex |
| Métodos do ciclo de vida | start, execute, finish | Código Apex |

## Consulta

| Propriedade | Valor | Fonte |
|---|---|---|
| Consulta do start() | SELECT Id, Status__c FROM Order__c WHERE Status__c = 'Cancelled' | Código Apex |
| Consulta dinâmica | False | Código Apex |
| Objeto da consulta | Order__c | Código Apex |

## Encadeamento no finish()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| executeBatch | InvoiceSyncBatch | 50 | Código Apex |

## Convenção de nomes

- Nome: `OrderCleanupBatch`
- Convenção do projeto: sufixo `Batch` (ex.: `OrderCleanupBatch`)
- Segue a convenção: Sim

_Fonte: Derivado_

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000004AAA | Objeto interno |
| Name | OrderCleanupBatch | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 404 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidocontroller-apex-class.md`

```markdown
# Classe Apex: PedidoController

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | PedidoController | XML |
| ApiVersion | 67.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Controller Apex dos LWCs de pedido (simulado). | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | with sharing | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Não aplicável | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| buscarPedidos(Id recordId) | List<Pedido__c> | public, static | @AuraEnabled | Código Apex |
| contarPedidos() | Integer | public, static | @AuraEnabled | Código Apex |
| enviar(Id pedidoId) | void | public, static | @AuraEnabled | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000007AAA | Objeto interno |
| Name | PedidoController | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 407 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidoservice-apex-class.md`

```markdown
# Classe Apex: PedidoService

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | PedidoService | XML |
| ApiVersion | 62.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | with sharing | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Não aplicável | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| buscar(Set<Id> ids) | List<Order__c> | public, static | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000005AAA | Objeto interno |
| Name | PedidoService | Objeto interno |
| ApiVersion | 62.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 405 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | — | XML |
| Perfil | Vendas | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidotriggerhandler-apex-class.md`

```markdown
# Classe Apex: PedidoTriggerHandler

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | PedidoTriggerHandler | XML |
| ApiVersion | 67.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Handler da PedidoTrigger. | Código Apex |
| Tipo de declaração | class | Código Apex |
| Sharing | with sharing | Código Apex |
| Modificadores | public | Código Apex |
| Extends | Não informado | Código Apex |
| Anotações da classe | Não informado | Código Apex |

## Interfaces implementadas

| Interface | Fonte |
|---|---|
| Não aplicável | Código Apex |

## Métodos

| Assinatura | Retorno | Modificadores | Anotações | Fonte |
|---|---|---|---|---|
| run(System.TriggerOperation operacao) | void | public | Não informado | Código Apex |

## Chamadas assíncronas feitas pela classe

| Método | Chamada | Classe alvo | Tamanho do lote | Atraso (min) | Nome do job | Expressão cron | Fonte |
|---|---|---|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01p000000000006AAA | Objeto interno |
| Name | PedidoTriggerHandler | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| LengthWithoutComments | 406 | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Vendas | Executar | — | XML |
```

### `saida/docs/doc-dev-101326/doc-case-assignment-rules.md`

```markdown
# Regras de atribuição: Case

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | Case | XML |
| Situação | Uma regra ativa | Derivado |

## Regras

| Regra | Ativa | Outras configurações | Fonte |
|---|---|---|---|
| Atribuicao_Case | true | Não informado | XML |
| Atribuicao_Antiga | false | Não informado | XML |

## Entradas (ordem de avaliação)

A plataforma avalia as entradas em ordem e para na primeira que casa; recomenda-se uma última entrada sem critério. Só uma regra de cada tipo fica ativa por objeto.

| Regra | Ordem | Critério | Lógica | Destino | Outras configurações | Fonte |
|---|---|---|---|---|---|---|
| Atribuicao_Case | 1 | Case.Origin equals Email; Case.Priority equals High | Não informado | Queue: Fila_Pedidos | template=unfiled$public/Caso_Atribuido | XML |
| Atribuicao_Case | 2 | (sem critério: pega tudo) | Não informado | User: usuário (não documentado) | Não informado | XML |

## Registros na org

| Id | Nome | Ativa | Fonte |
|---|---|---|---|
| 01Q000000000000AAA | Atribuicao_Case | True | Objeto interno |
| 01Q000000000001AAA | Atribuicao_Antiga | False | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Regras de automação do objeto; não são concedidas por perfil ou permission set | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-case-auto-response-rules.md`

```markdown
# Regras de resposta automática: Case

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | Case | XML |
| Situação | Uma regra ativa | Derivado |

## Regras

| Regra | Ativa | Outras configurações | Fonte |
|---|---|---|---|
| Resposta_Case | true | Não informado | XML |

## Entradas (ordem de avaliação)

A plataforma avalia as entradas em ordem e para na primeira que casa; recomenda-se uma última entrada sem critério. Só uma regra de cada tipo fica ativa por objeto.

| Regra | Ordem | Critério | Lógica | Destino | Outras configurações | Fonte |
|---|---|---|---|---|---|---|
| Resposta_Case | 1 | Case.Origin equals Web | Não informado | Não informado | template=unfiled$public/Caso_Recebido; 1 e-mail de resposta (não documentado); 1 e-mail do remetente (não documentado); 1 nome do remetente (não documentado) | XML |

## Registros na org

| Id | Nome | Ativa | Fonte |
|---|---|---|---|
| 03o000000000000AAA | Resposta_Case | True | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Regras de automação do objeto; não são concedidas por perfil ou permission set | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-case-escalation-rules.md`

```markdown
# Regras de escalonamento: Case

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | Case | XML |
| Situação | Uma regra ativa | Derivado |

## Regras

| Regra | Ativa | Outras configurações | Fonte |
|---|---|---|---|
| Escalonamento_Case | true | Não informado | XML |

## Entradas (ordem de avaliação)

A plataforma avalia as entradas em ordem e para na primeira que casa; recomenda-se uma última entrada sem critério. Só uma regra de cada tipo fica ativa por objeto.

| Regra | Ordem | Critério | Lógica | Destino | Outras configurações | Fonte |
|---|---|---|---|---|---|---|
| Escalonamento_Case | 1 | Case.Priority equals High | Não informado | Não informado | businessHoursSource=None | XML |

## Ações de escalonamento

| Regra | Entrada | Ação | Destino | Configuração | Fonte |
|---|---|---|---|---|---|
| Escalonamento_Case | 1 | escalationAction 1 | Queue: Fila_Pedidos | minutesToEscalation=240; notifyCaseOwner=true; notifyToTemplate=unfiled$public/Caso_Escalonado; 1 e-mail(s) de notificação (não documentados); 1 usuário(s) notificado(s) (não documentados) | XML |

## Registros na org

| Id | Nome | Ativa | Fonte |
|---|---|---|---|
| 01S000000000000AAA | Escalonamento_Case | True | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Regras de automação do objeto; não são concedidas por perfil ou permission set | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-opportunity-venda-enterprise-business-process.md`

```markdown
# Processo de negócio: Opportunity.Venda_Enterprise

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Opportunity.Venda_Enterprise | XML |
| MasterLabel | Não aplicável | XML |
| Description | Ciclo de vendas para contas corporativas (simulado) | XML |
| IsActive | true | XML |
| Valor padrão | Prospecting | XML |

## Valores do processo

Valores da picklist do processo (em Opportunity, as etapas de StageName), na ordem do XML.

| Ordem | Valor | Padrão | Fonte |
|---|---|---|---|
| 1 | Prospecting | true | XML |
| 2 | Qualification | false | XML |
| 3 | Closed Won | false | XML |
| 4 | Closed Lost | false | XML |

## Record types que usam o processo

O processo não é atribuído a perfis: ele é vinculado a record types, que são liberados em perfis e permission sets.

| Record type | Rótulo | Ativo | Fonte |
|---|---|---|---|
| Opportunity.Enterprise | Enterprise | true | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 019000000000000AAA | Objeto interno |
| Name | Venda_Enterprise | Objeto interno |
| TableEnumOrId | Opportunity | Objeto interno |
| IsActive | True | Objeto interno |
| Description | Ciclo de vendas para contas corporativas (simulado) | Objeto interno |

## Acesso e configuração

Perfis e permission sets que enxergam os record types que usam este processo.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Visível | RecordType Opportunity.Enterprise | XML |
```

### `saida/docs/doc-dev-101326/doc-leadconvertsettings-lead-convert.md`

```markdown
# Conversão de Lead: LeadConvertSettings

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Componente | LeadConvertSettings | XML |

## Configurações gerais

| Propriedade | Valor | Fonte |
|---|---|---|
| allowOwnerChange | true | XML |
| opportunityCreationOptions | VisibleOptional | XML |

## Mapeamentos de objeto

| Elemento | Objeto de origem | Objeto de destino | Outras configurações | Fonte |
|---|---|---|---|---|
| objectMapping | Lead | Account | Não informado | XML |
| objectMapping | Lead | Opportunity | Não informado | XML |

## Mapeamento de campos (de-para)

Campos do Lead copiados para Account, Contact e Opportunity na conversão.

| Objeto de origem | Campo de origem | Objeto de destino | Campo de destino | Fonte |
|---|---|---|---|---|
| Lead | CNPJ__c | Account | CNPJ__c | XML |
| Lead | Orcamento__c | Opportunity | Amount | XML |

## Acesso e configuração

Quem pode converter leads (permissão de sistema) e quem tem acesso aos campos mapeados (FLS).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Vendas | Habilitada | Permissão de sistema ConvertLeads | XML |
| Perfil | Admin | Ler, Editar | Campo de destino Account.CNPJ__c | XML |
```

### `saida/docs/doc-dev-101326/doc-modelo-vendas-territory-model.md`

```markdown
# Modelo de territórios: Modelo_Vendas

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Modelo_Vendas | XML |

## Configurações do modelo

| Propriedade | Valor | Fonte |
|---|---|---|
| description | Modelo de vendas 2026 (simulado) | XML |
| name | Modelo de Vendas 2026 | XML |

## Territórios

Territórios do modelo. Usuários atribuídos aos territórios não são documentados.

| Território | Rótulo | Tipo | Território pai | Acesso a contas | Acesso a oportunidades | Acesso a casos | Regras associadas | Fonte |
|---|---|---|---|---|---|---|---|---|
| Modelo_Vendas.Sudeste | Brasil Sudeste | Regional | Não aplicável | Edit | Read | Read | inherited=false, ruleName=Regra_SP | XML |

## Regras de atribuição

| Regra | Ativa | Objeto | Lógica | Critérios | Fonte |
|---|---|---|---|---|---|
| Modelo_Vendas.Regra_SP | true | Account | 1 | field=Account.BillingState, operation=equals, value=SP | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0MA000000000000AAA | Objeto interno |
| DeveloperName | Modelo_Vendas | Objeto interno |
| Name | Modelo de Vendas 2026 | Objeto interno |
| State | Active | Objeto interno |
| ActivatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

Quem pode gerenciar territórios. O acesso aos registros vem dos níveis de acesso de cada território.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Habilitada | Permissão de sistema ManageTerritories | XML |
```

### `saida/docs/doc-dev-101326/doc-receita-principal-opportunity-split-type.md`

```markdown
# Tipo de divisão de oportunidade: Receita_Principal

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Receita_Principal | XML |

## Configuração

| Propriedade | Valor | Fonte |
|---|---|---|
| description | Divisão do valor total (simulado) | XML |
| isActive | true | XML |
| isTotalValidated | true | XML |
| masterLabel | Divisão de Receita | XML |
| splitDataStatus | Completed | XML |
| splitEntity | Opportunity | XML |
| splitField | Amount | XML |
| splitLabel | Receita | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 149000000000000AAA | Objeto interno |
| DeveloperName | Receita_Principal | Objeto interno |
| MasterLabel | Divisão de Receita | Objeto interno |

## Acesso e configuração

Quem pode gerenciar divisões de oportunidade. Divisões dependem da equipe da oportunidade (Opportunity Team).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-portal-clientes-network.md`

```markdown
# Site do Experience Cloud (Network): Portal_Clientes

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Portal_Clientes | XML |
| Label | Não informado | XML |
| Description | Portal de autoatendimento de clientes | XML |
| Status | Live | XML |
| Site (CustomSite) | Portal_Clientes | XML |
| URL path prefix | clientes | XML |
| Autorregistro | true | XML |
| Perfil de autorregistro | Customer Community User | XML |
| Remetente de e-mail | Configurado (não documentado) | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| enableGuestChatter | false | XML |
| enableKnowledgeable | true | XML |
| enableNicknameDisplay | true | XML |

## Templates de e-mail

| Elemento | Template | Fonte |
|---|---|---|
| forgotPasswordTemplate | unfiled$public/CommunityForgotPasswordEmail | XML |
| welcomeTemplate | unfiled$public/CommunityWelcomeEmail | XML |

## Site (CustomSite)

Infraestrutura web do site. O perfil de convidado define o que visitantes não autenticados acessam.

| Site | Ativo | URL path prefix | Perfil de convidado | Tipo | Fonte |
|---|---|---|---|---|---|
| Portal_Clientes | true | clientes | Portal Clientes Profile | ChatterNetwork | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0DB000000000001AAA | Objeto interno |
| Name | Portal_Clientes | Objeto interno |
| Status | Live | Objeto interno |
| UrlPathPrefix | clientes | Objeto interno |

## Acesso e configuração

Perfis e permission sets cujos usuários podem entrar no site, e o perfil dado a quem se autorregistra.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Leitura_Pedidos | Membro do site | — | XML |
| Perfil | Vendas | Membro do site | — | XML |
| Perfil de autorregistro | Customer Community User | Membro do site | — | XML |
```

### `saida/docs/doc-dev-101326/doc-portal-clientes-site.md`

```markdown
# Site (CustomSite): Portal_Clientes

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Portal_Clientes | XML |
| MasterLabel | Portal de Clientes | XML |
| Active | true | XML |
| Tipo do site | ChatterNetwork | XML |
| URL path prefix | clientes | XML |
| Subdomínio | Não aplicável | XML |
| Perfil de convidado | Portal Clientes Profile | XML |

## Usuários do site

Usuários nunca são documentados: o documento mostra só se cada papel está configurado.

| Papel | Situação | Fonte |
|---|---|---|
| Administrador do site (siteAdmin) | Configurado (usuário não documentado) | XML |
| Dono padrão dos registros de convidado (siteGuestRecordDefaultOwner) | Configurado (usuário não documentado) | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| allowHomePage | false | XML |
| browserXssProtection | true | XML |
| clickjackProtectionLevel | SameOriginOnly | XML |

## Sites do Experience Cloud (Network)

| Network | Status | Autorregistro | Fonte |
|---|---|---|---|
| Portal_Clientes | Live | true | XML |

## Permissões de objeto do perfil de convidado

Visitantes não autenticados usam o perfil de convidado. Acesso além de Ler/Criar é marcado para revisão.

| Objeto | Acesso | Revisar (acima de Ler/Criar) | Fonte |
|---|---|---|---|
| Account | Ler, Editar | Sim | XML |
| Pedido__c | Ler, Criar | Não | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0DM000000000001AAA | Objeto interno |
| Name | Portal_Clientes | Objeto interno |
| MasterLabel | Portal de Clientes | Objeto interno |
| Status | Active | Objeto interno |
| SiteType | ChatterNetwork | Objeto interno |
| UrlPathPrefix | clientes | Objeto interno |

## Acesso e configuração

Perfil de convidado e regras de compartilhamento que expõem registros a visitantes do site.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil de convidado | Portal Clientes Profile | Autorizado no componente | — | XML |
| Regra de compartilhamento | Pedidos_Portal | Read | Objeto Pedido__c; Regra de compartilhamento para convidado | XML |
```

### `saida/docs/doc-dev-101326/doc-integracao-api-permission-set.md`

```markdown
# Permission Set: Integracao_API

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Integracao_API | XML |
| Label | Integração API | XML |
| Description | Acesso da integração (SIMULADO) | XML |
| License | Não aplicável | XML |
| HasActivationRequired | false | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| Pedido_Evento__e | true | true | false | false | false | false | XML |
| Pedido__c | true | false | true | false | false | false | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| Pedido__c.Status__c | true | false | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| AccountSyncQueueable | XML |

## Flows

| Flow | Fonte |
|---|---|
| Tela_Cadastro | XML |

## Custom Metadata Types

| Tipo | Fonte |
|---|---|
| Não aplicável | XML |

## Record types

| Record type | Visível | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Principals de External Credential

| Principal | Fonte |
|---|---|
| Minha_EC-Principal_Integracao | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| ApiEnabled | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| Aprova_Pedido | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| PedidoResumo | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| Pedido__c | Visible | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0PS000000000000AAA | Objeto interno |
| Name | Integracao_API | Objeto interno |
| Label | Integração API | Objeto interno |
| IsOwnedByProfile | False | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set Group | PSG_Integracao | Inclui o permission set | — | XML |
```

### `saida/docs/doc-dev-101326/doc-leitura-pedidos-permission-set.md`

```markdown
# Permission Set: Leitura_Pedidos

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Leitura_Pedidos | XML |
| Label | Leitura de Pedidos | XML |
| Description | Não aplicável | XML |
| License | Não aplicável | XML |
| HasActivationRequired | false | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| Pedido__c | true | false | false | false | false | false | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| Não aplicável | XML |

## Flows

| Flow | Fonte |
|---|---|
| Não aplicável | XML |

## Custom Metadata Types

| Tipo | Fonte |
|---|---|
| Config__mdt | XML |

## Record types

| Record type | Visível | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Principals de External Credential

| Principal | Fonte |
|---|---|
| Não aplicável | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| Não aplicável | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| Não aplicável | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| Não aplicável | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0PS000000000001AAA | Objeto interno |
| Name | Leitura_Pedidos | Objeto interno |
| Label | Leitura de Pedidos | Objeto interno |
| IsOwnedByProfile | False | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-admin-profile.md`

```markdown
# Perfil: Admin

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Admin | XML |
| UserLicense | Salesforce | XML |
| Custom | false | XML |
| Description | Não aplicável | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| Pedido__c | true | true | true | true | true | true | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| Account.CNPJ__c | true | true | XML |
| Pedido__c.Valor__c | true | true | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| OrderCleanupBatch | XML |
| PedidoController | XML |
| PedidoService | XML |

## Flows

| Flow | Fonte |
|---|---|
| Meu_Flow | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| Não aplicável | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| Não aplicável | XML |

## Record types

| Record type | Visível | Padrão | Fonte |
|---|---|---|---|
| Opportunity.Enterprise | true | true | XML |
| Pedido__c.Padrao | true | true | XML |

## Layouts de página

| Layout | Record type | Fonte |
|---|---|---|
| Pedido__c-Pedido Layout | Não informado | XML |
| Pedido__c-Pedido Layout Venda | Pedido__c.Padrao | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| Pedido__c | DefaultOn | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| ModifyAllData | XML |
| ViewAllData | XML |
| ManageTerritories | XML |

## Horário de login

| Propriedade | Valor | Fonte |
|---|---|---|
| mondayEnd | 1080 | XML |
| mondayStart | 480 | XML |

## Faixas de IP de login

| Faixa (como no XML) | Fonte |
|---|---|
| description=Rede corporativa (simulada), endAddress=10.0.0.254, startAddress=10.0.0.1 | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não informado | Não informado | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Perfil é atribuído a usuários; usuários não são documentados (proteção de dados) | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-portal-clientes-profile-profile.md`

```markdown
# Perfil: Portal Clientes Profile

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Portal Clientes Profile | XML |
| UserLicense | Guest User License | XML |
| Custom | false | XML |
| Description | Não aplicável | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| Pedido__c | true | true | false | false | false | false | XML |
| Account | true | false | true | false | false | false | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| Não aplicável | XML |

## Flows

| Flow | Fonte |
|---|---|
| Não aplicável | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| Não aplicável | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| Não aplicável | XML |

## Record types

| Record type | Visível | Padrão | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Layouts de página

| Layout | Record type | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| Não aplicável | XML |

## Horário de login

| Propriedade | Valor | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Faixas de IP de login

| Faixa (como no XML) | Fonte |
|---|---|
| Não aplicável | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não informado | Não informado | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Perfil é atribuído a usuários; usuários não são documentados (proteção de dados) | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-vendas-profile.md`

```markdown
# Perfil: Vendas

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Vendas | XML |
| UserLicense | Salesforce | XML |
| Custom | true | XML |
| Description | Não aplicável | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| Pedido__c | true | false | false | false | false | false | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| PedidoService | XML |
| PedidoTriggerHandler | XML |

## Flows

| Flow | Fonte |
|---|---|
| Não aplicável | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| Não aplicável | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| Não aplicável | XML |

## Record types

| Record type | Visível | Padrão | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Layouts de página

| Layout | Record type | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| ConvertLeads | XML |

## Horário de login

| Propriedade | Valor | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Faixas de IP de login

| Faixa (como no XML) | Fonte |
|---|---|
| Não aplicável | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00e000000000001AAA | Objeto interno |
| Name | Vendas | Objeto interno |
| UserType | Standard | Objeto interno |
| UserLicense | Name=Salesforce | Objeto interno |
| Description | Perfil de vendas (simulado) | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Perfil é atribuído a usuários; usuários não são documentados (proteção de dados) | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-psg-integracao-permission-set-group.md`

```markdown
# Permission Set Group: PSG_Integracao

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | PSG_Integracao | XML |
| Label | PSG Integração | XML |
| Description | Grupo de integração (SIMULADO) | XML |
| HasActivationRequired | Não aplicável | XML |
| Status | Updated | XML |

## Permission sets incluídos

| Permission set | Fonte |
|---|---|
| Integracao_API | XML |

## Muting permission sets

| Muting permission set | Fonte |
|---|---|
| PSG_Integracao_Muting | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0PG000000000000AAA | Objeto interno |
| DeveloperName | PSG_Integracao | Objeto interno |
| MasterLabel | PSG Integração | Objeto interno |
| Status | Updated | Objeto interno |
| HasActivationRequired | False | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Permission set group é atribuído a usuários; usuários não são documentados (proteção de dados) | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-grupo-suporte-public-group.md`

```markdown
# Grupo público: Grupo_Suporte

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Grupo_Suporte | XML |
| Label | Grupo Suporte | XML |
| Description | Não aplicável | XML |
| DoesIncludeBosses | true | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00G000000000000AAA | Objeto interno |
| Name | Grupo Suporte | Objeto interno |
| DeveloperName | Grupo_Suporte | Objeto interno |
| Type | Regular | Objeto interno |
| DoesIncludeBosses | True | Objeto interno |

## Acesso e configuração

Grupo não é concedido por perfil/permission set. As linhas mostram as regras de compartilhamento que dão acesso a este grupo. Membros não são documentados (proteção de dados).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Regra de compartilhamento | Pedidos_Suporte | Edit | Objeto Pedido__c; Regra de compartilhamento por proprietário | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidoauditoriatrigger-apex-trigger.md`

```markdown
# Trigger Apex: PedidoAuditoriaTrigger

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| TriggerName | PedidoAuditoriaTrigger | XML |
| Objeto | Pedido__c | Código Apex |
| ApiVersion | 66.0 | XML |
| Status | Inactive | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Eventos

| Evento | Momento | Operação | Fonte |
|---|---|---|---|
| before update | before | update | Código Apex |
| after delete | after | delete | Código Apex |

## Variáveis de contexto usadas

| Variável | Fonte |
|---|---|
| Trigger.size | Código Apex |

## Classes chamadas pela trigger

| Classe | Referência | Membros chamados | Classe da org | Fonte |
|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Leituras de configuração

Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código. A leitura pode ser um mecanismo de desativação (bypass), mas isso não é inferido: confira o uso no código.

| Onde | Mecanismo | Componente | Chamada | Registro | Fonte |
|---|---|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | — | — | Código Apex |

## Controles de segurança

Controles explícitos de modo de acesso e de CRUD/FLS no código. Sem controle explícito, vale o modo padrão da `apiVersion` de cada arquivo (mudou na API 67.0; ver `documentation/referencia-apex-trigger.md`).

| Onde | Controle | Ocorrências | Fonte |
|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | Código Apex |

## Coexistência no objeto e ordem de execução

Automações do mesmo objeto processadas nesta execução, na ordem oficial de execução (Apex Developer Guide, *Triggers and Order of Execution*). Componentes fora do escopo da execução não aparecem.

| Ordem | Fase | Tipo | Componente | Eventos | Status/Ativo | Observação | Fonte |
|---|---|---|---|---|---|---|---|
| 2 | Trigger before (insert/update) | Apex Trigger | PedidoAuditoriaTrigger (este documento) | before update | Inactive | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 2 | Trigger before (insert/update) | Apex Trigger | PedidoTrigger | before insert, before update | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 3 | Regras de validação | Regra de validação | Pedido__c.Valor_Positivo | — | true | Após as triggers before; só em insert/update | Derivado |
| 4 | Trigger after (insert/update) | Apex Trigger | PedidoTrigger | after insert, after update | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 5 | Flow after-save (após salvar) | Record-Triggered Flow | Meu_Flow | Update | Active | Entre flows do objeto: triggerOrder 1–1000, depois sem valor, depois 1001–2000; empate pelo nome de API | Derivado |
| Não confirmado | Trigger after delete | Apex Trigger | PedidoAuditoriaTrigger (este documento) | after delete | Inactive | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01q000000000000AAA | Objeto interno |
| Name | PedidoAuditoriaTrigger | Objeto interno |
| TableEnumOrId | 01I000000000000AAA | Objeto interno |
| ApiVersion | 66.0 | Objeto interno |
| Status | Inactive | Objeto interno |
| IsValid | True | Objeto interno |
| UsageBeforeInsert | False | Objeto interno |
| UsageAfterInsert | False | Objeto interno |
| UsageBeforeUpdate | True | Objeto interno |
| UsageAfterUpdate | False | Objeto interno |
| UsageBeforeDelete | False | Objeto interno |
| UsageAfterDelete | True | Objeto interno |
| UsageAfterUndelete | False | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

A trigger não tem acesso próprio por perfil ou permission set: dispara na operação DML do objeto. As linhas mostram quem tem acesso ao objeto e às classes chamadas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto Pedido__c | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | Objeto Pedido__c | XML |
| Perfil | Vendas | Ler | Objeto Pedido__c | XML |
| Permission Set | Integracao_API | Ler, Editar | Objeto Pedido__c | XML |
| Permission Set | Leitura_Pedidos | Ler | Objeto Pedido__c | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Objeto Pedido__c; Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidochangetrigger-apex-trigger.md`

```markdown
# Trigger Apex: PedidoChangeTrigger

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| TriggerName | PedidoChangeTrigger | XML |
| Objeto | Pedido__ChangeEvent | Código Apex |
| ApiVersion | 67.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Eventos

| Evento | Momento | Operação | Fonte |
|---|---|---|---|
| after insert | after | insert | Código Apex |

## Variáveis de contexto usadas

| Variável | Fonte |
|---|---|
| Trigger.new | Código Apex |

## Classes chamadas pela trigger

| Classe | Referência | Membros chamados | Classe da org | Fonte |
|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código Apex |

## Leituras de configuração

Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código. A leitura pode ser um mecanismo de desativação (bypass), mas isso não é inferido: confira o uso no código.

| Onde | Mecanismo | Componente | Chamada | Registro | Fonte |
|---|---|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | — | — | Código Apex |

## Controles de segurança

Controles explícitos de modo de acesso e de CRUD/FLS no código. Sem controle explícito, vale o modo padrão da `apiVersion` de cada arquivo (mudou na API 67.0; ver `documentation/referencia-apex-trigger.md`).

| Onde | Controle | Ocorrências | Fonte |
|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | Código Apex |

## Coexistência no objeto e ordem de execução

Automações do mesmo objeto processadas nesta execução, na ordem oficial de execução (Apex Developer Guide, *Triggers and Order of Execution*). Componentes fora do escopo da execução não aparecem.

| Ordem | Fase | Tipo | Componente | Eventos | Status/Ativo | Observação | Fonte |
|---|---|---|---|---|---|---|---|
| 4 | Trigger after (insert/update) | Apex Trigger | PedidoChangeTrigger (este documento) | after insert | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não informado | Não informado | Objeto interno |

## Acesso e configuração

A trigger não tem acesso próprio por perfil ou permission set: dispara na operação DML do objeto. As linhas mostram quem tem acesso ao objeto e às classes chamadas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidoeventotrigger-apex-trigger.md`

```markdown
# Trigger Apex: PedidoEventoTrigger

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| TriggerName | PedidoEventoTrigger | XML |
| Objeto | Pedido_Evento__e | Código Apex |
| ApiVersion | 67.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Não informado | Código Apex |

## Eventos

| Evento | Momento | Operação | Fonte |
|---|---|---|---|
| after insert | after | insert | Código Apex |

## Variáveis de contexto usadas

| Variável | Fonte |
|---|---|
| Não aplicável | Código Apex |

## Classes chamadas pela trigger

| Classe | Referência | Membros chamados | Classe da org | Fonte |
|---|---|---|---|---|
| PedidoService | chamada estática | buscar | Sim (inventário ApexClass) | Código Apex |

## Leituras de configuração

Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código. A leitura pode ser um mecanismo de desativação (bypass), mas isso não é inferido: confira o uso no código.

| Onde | Mecanismo | Componente | Chamada | Registro | Fonte |
|---|---|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | — | — | Código Apex |

## Controles de segurança

Controles explícitos de modo de acesso e de CRUD/FLS no código. Sem controle explícito, vale o modo padrão da `apiVersion` de cada arquivo (mudou na API 67.0; ver `documentation/referencia-apex-trigger.md`).

| Onde | Controle | Ocorrências | Fonte |
|---|---|---|---|
| Nenhuma ocorrência no código lido | — | — | Código Apex |

## Coexistência no objeto e ordem de execução

Automações do mesmo objeto processadas nesta execução, na ordem oficial de execução (Apex Developer Guide, *Triggers and Order of Execution*). Componentes fora do escopo da execução não aparecem.

| Ordem | Fase | Tipo | Componente | Eventos | Status/Ativo | Observação | Fonte |
|---|---|---|---|---|---|---|---|
| 4 | Trigger after (insert/update) | Apex Trigger | PedidoEventoTrigger (este documento) | after insert | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Não informado | Não informado | Objeto interno |

## Acesso e configuração

A trigger não tem acesso próprio por perfil ou permission set: dispara na operação DML do objeto. As linhas mostram quem tem acesso ao objeto e às classes chamadas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Ler, Criar | Objeto Pedido_Evento__e | XML |
| Permission Set Group | PSG_Integracao | Ler, Criar | Objeto Pedido_Evento__e; Permission Set Integracao_API | XML |
| Perfil | Admin | Executar | Classe chamada PedidoService | XML |
| Perfil | Vendas | Executar | Classe chamada PedidoService | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidotrigger-apex-trigger.md`

```markdown
# Trigger Apex: PedidoTrigger

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| TriggerName | PedidoTrigger | XML |
| Objeto | Pedido__c | Código Apex |
| ApiVersion | 67.0 | XML |
| Status | Active | XML |
| Descrição (ApexDoc) | Trigger do Pedido: delega a lógica ao PedidoTriggerHandler. | Código Apex |

## Eventos

| Evento | Momento | Operação | Fonte |
|---|---|---|---|
| before insert | before | insert | Código Apex |
| before update | before | update | Código Apex |
| after insert | after | insert | Código Apex |
| after update | after | update | Código Apex |

## Variáveis de contexto usadas

| Variável | Fonte |
|---|---|
| Trigger.isAfter | Código Apex |
| Trigger.new | Código Apex |
| Trigger.newMap | Código Apex |
| Trigger.oldMap | Código Apex |
| Trigger.operationType | Código Apex |

## Classes chamadas pela trigger

| Classe | Referência | Membros chamados | Classe da org | Fonte |
|---|---|---|---|---|
| PedidoService | chamada estática | buscar | Sim (inventário ApexClass) | Código Apex |
| PedidoTriggerHandler | instância (new), instância (variável) | run | Sim (inventário ApexClass) | Código Apex |

## Leituras de configuração

Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código. A leitura pode ser um mecanismo de desativação (bypass), mas isso não é inferido: confira o uso no código.

| Onde | Mecanismo | Componente | Chamada | Registro | Fonte |
|---|---|---|---|---|---|
| Trigger PedidoTrigger | Custom Permission | Bypass_Pedido_Trigger | FeatureManagement.checkPermission | — | Código Apex |
| Trigger PedidoTrigger | Custom Metadata Type | Trigger_Setting__mdt | Trigger_Setting__mdt.getInstance | PedidoTrigger | Código Apex |
| Classe PedidoTriggerHandler | Custom Setting | Automation_Settings__c | Automation_Settings__c.getInstance | — | Código Apex |

## Controles de segurança

Controles explícitos de modo de acesso e de CRUD/FLS no código. Sem controle explícito, vale o modo padrão da `apiVersion` de cada arquivo (mudou na API 67.0; ver `documentation/referencia-apex-trigger.md`).

| Onde | Controle | Ocorrências | Fonte |
|---|---|---|---|
| Classe PedidoTriggerHandler | WITH USER_MODE | 1 | Código Apex |
| Classe PedidoTriggerHandler | Security.stripInaccessible | 1 | Código Apex |

## Coexistência no objeto e ordem de execução

Automações do mesmo objeto processadas nesta execução, na ordem oficial de execução (Apex Developer Guide, *Triggers and Order of Execution*). Componentes fora do escopo da execução não aparecem.

| Ordem | Fase | Tipo | Componente | Eventos | Status/Ativo | Observação | Fonte |
|---|---|---|---|---|---|---|---|
| 2 | Trigger before (insert/update) | Apex Trigger | PedidoAuditoriaTrigger | before update | Inactive | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 2 | Trigger before (insert/update) | Apex Trigger | PedidoTrigger (este documento) | before insert, before update | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 3 | Regras de validação | Regra de validação | Pedido__c.Valor_Positivo | — | true | Após as triggers before; só em insert/update | Derivado |
| 4 | Trigger after (insert/update) | Apex Trigger | PedidoTrigger (este documento) | after insert, after update | Active | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |
| 5 | Flow after-save (após salvar) | Record-Triggered Flow | Meu_Flow | Update | Active | Entre flows do objeto: triggerOrder 1–1000, depois sem valor, depois 1001–2000; empate pelo nome de API | Derivado |
| Não confirmado | Trigger after delete | Apex Trigger | PedidoAuditoriaTrigger | after delete | Inactive | Sem ordem garantida entre triggers do mesmo objeto e evento | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 01q000000000001AAA | Objeto interno |
| Name | PedidoTrigger | Objeto interno |
| TableEnumOrId | 01I000000000000AAA | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| Status | Active | Objeto interno |
| IsValid | True | Objeto interno |
| UsageBeforeInsert | True | Objeto interno |
| UsageAfterInsert | True | Objeto interno |
| UsageBeforeUpdate | True | Objeto interno |
| UsageAfterUpdate | True | Objeto interno |
| UsageBeforeDelete | False | Objeto interno |
| UsageAfterDelete | False | Objeto interno |
| UsageAfterUndelete | False | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

A trigger não tem acesso próprio por perfil ou permission set: dispara na operação DML do objeto. As linhas mostram quem tem acesso ao objeto e às classes chamadas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto Pedido__c | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | Objeto Pedido__c | XML |
| Perfil | Vendas | Ler | Objeto Pedido__c | XML |
| Permission Set | Integracao_API | Ler, Editar | Objeto Pedido__c | XML |
| Permission Set | Leitura_Pedidos | Ler | Objeto Pedido__c | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Objeto Pedido__c; Permission Set Integracao_API | XML |
| Perfil | Admin | Executar | Classe chamada PedidoService | XML |
| Perfil | Vendas | Executar | Classe chamada PedidoService | XML |
| Perfil | Vendas | Executar | Classe chamada PedidoTriggerHandler | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidoacaorapida-lwc.md`

```markdown
# Lightning Web Component: pedidoAcaoRapida

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | pedidoAcaoRapida | XML |
| MasterLabel | Enviar Pedido | XML |
| ApiVersion | 67.0 | XML |
| IsExposed | true | XML |
| Description | Não aplicável | XML |

## Arquivos do bundle

| Arquivo | Tipo | Fonte |
|---|---|---|
| pedidoAcaoRapida.js | JavaScript | Código LWC |
| pedidoAcaoRapida.js-meta.xml | Configuração (.js-meta.xml) | Código LWC |

## Targets (onde o componente pode ser usado)

| Target | Uso | Fonte |
|---|---|---|
| lightning__RecordAction | Quick Action na página de registro | XML |

## Propriedades configuráveis (targetConfigs)

| Targets | Propriedade | Tipo | Rótulo | Role | Obrigatória | Padrão | @api no JS | Fonte |
|---|---|---|---|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | Não aplicável | XML |

## Restrições por target

| Targets | Restrição | Valor | Fonte |
|---|---|---|---|
| lightning__RecordAction | Tipo de ação (actionType) | Action | XML |

## Propriedades e métodos públicos (@api)

| Membro | Tipo | Fonte |
|---|---|---|
| recordId | propriedade | Código LWC |
| invoke | método | Código LWC |

## Ciclo de vida implementado

| Hook | Fonte |
|---|---|
| Não aplicável | Código LWC |

## Métodos Apex chamados

| Classe | Método | Nome importado | Uso | Fonte |
|---|---|---|---|---|
| PedidoController | enviar | enviar | imperativo | Código LWC |

## Verificação nas classes Apex

Para ser chamado pelo LWC, o método precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, também `cacheable=true`. A verificação usa o código das classes processadas nesta execução.

| Classe | Método | @AuraEnabled | Modificadores | Verificação | Fonte |
|---|---|---|---|---|---|
| PedidoController | enviar | Sim | public, static | Atende | Código Apex |

## Dados do Salesforce usados

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Código LWC |

## Comunicação

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Código LWC |

## Permissões verificadas no código

| Tipo | Nome | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | Código LWC |

## Onde é usado (páginas Lightning)

Páginas Lightning (FlexiPage) processadas nesta execução que incluem o componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Nenhuma página processada nesta execução usa o componente | — | — | — | — | XML |

## Onde é usado (Experience Cloud)

Páginas (views) de sites do Experience Cloud (ExperienceBundle) processadas nesta execução que incluem o componente. Página = `<bundle>/<view>`; visibilidade = há chave de público ou visibilidade no componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Nenhuma página de Experience Cloud processada nesta execução usa o componente | — | — | — | — | JSON do ExperienceBundle |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0Rb000000000000AAA | Objeto interno |
| DeveloperName | pedidoAcaoRapida | Objeto interno |
| MasterLabel | Enviar Pedido | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| IsExposed | True | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

O LWC não tem acesso próprio por perfil ou permission set: aparece onde é colocado (páginas, ações, flows). As linhas mostram quem acessa as classes Apex chamadas e quem tem as Custom Permissions verificadas no código.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | Classe Apex chamada PedidoController | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidoacaorapida-lwc-quick-action.md`

```markdown
# LWC Quick Action: pedidoAcaoRapida

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | pedidoAcaoRapida | XML |
| MasterLabel | Enviar Pedido | XML |
| ApiVersion | 67.0 | XML |
| ActionType | Action | XML |
| @api invoke() declarado | True | Código LWC |
| Verificação headless | Atende: @api invoke() declarado | Derivado |
| @api recordId declarado | True | Código LWC |
| Propriedades no targetConfig da ação | 0 | XML |

## Eventos de ação usados

| Evento | Fonte |
|---|---|
| Não aplicável | Código LWC |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0Rb000000000000AAA | Objeto interno |
| DeveloperName | pedidoAcaoRapida | Objeto interno |
| MasterLabel | Enviar Pedido | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| IsExposed | True | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | Classe Apex chamada PedidoController | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidopainel-lwc.md`

```markdown
# Lightning Web Component: pedidoPainel

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | pedidoPainel | XML |
| MasterLabel | Painel de Pedidos | XML |
| ApiVersion | 67.0 | XML |
| IsExposed | true | XML |
| Description | Painel de pedidos (simulado) | XML |

## Arquivos do bundle

| Arquivo | Tipo | Fonte |
|---|---|---|
| pedidoPainel.css | CSS | Código LWC |
| pedidoPainel.html | Template HTML | Código LWC |
| pedidoPainel.js | JavaScript | Código LWC |
| pedidoPainel.js-meta.xml | Configuração (.js-meta.xml) | Código LWC |

## Targets (onde o componente pode ser usado)

| Target | Uso | Fonte |
|---|---|---|
| lightning__RecordPage | Página de registro (Lightning App Builder) | XML |
| lightning__AppPage | Página de aplicativo (Lightning App Builder) | XML |
| lightning__HomePage | Página inicial (Lightning App Builder) | XML |

## Propriedades configuráveis (targetConfigs)

| Targets | Propriedade | Tipo | Rótulo | Role | Obrigatória | Padrão | @api no JS | Fonte |
|---|---|---|---|---|---|---|---|---|
| lightning__RecordPage | titulo | String | Título | entrada e saída (role ausente) | Não informado | Pedidos | Sim | XML |

## Restrições por target

| Targets | Restrição | Valor | Fonte |
|---|---|---|---|
| lightning__RecordPage | Objeto | Pedido__c | XML |
| lightning__RecordPage | Form factor | Large | XML |

## Propriedades e métodos públicos (@api)

| Membro | Tipo | Fonte |
|---|---|---|
| recordId | propriedade | Código LWC |
| objectApiName | propriedade | Código LWC |
| titulo | propriedade | Código LWC |

## Ciclo de vida implementado

| Hook | Fonte |
|---|---|
| connectedCallback | Código LWC |
| disconnectedCallback | Código LWC |

## Métodos Apex chamados

| Classe | Método | Nome importado | Uso | Fonte |
|---|---|---|---|---|
| PedidoController | buscarPedidos | buscarPedidos | @wire | Código LWC |
| PedidoController | contarPedidos | contarPedidos | @wire | Código LWC |
| PedidoController | enviar | enviar | imperativo | Código LWC |

## Verificação nas classes Apex

Para ser chamado pelo LWC, o método precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, também `cacheable=true`. A verificação usa o código das classes processadas nesta execução.

| Classe | Método | @AuraEnabled | Modificadores | Verificação | Fonte |
|---|---|---|---|---|---|
| PedidoController | buscarPedidos | Sim (cacheable=true) | public, static | Atende | Código Apex |
| PedidoController | contarPedidos | Sim | public, static | Não atende: @wire exige @AuraEnabled(cacheable=true) | Código Apex |
| PedidoController | enviar | Sim | public, static | Atende | Código Apex |

## Dados do Salesforce usados

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Módulo LDS (UI API) | lightning/uiRecordApi | — | Código LWC |
| Adaptador @wire | getRecord | lightning/uiRecordApi | Código LWC |
| Referência de schema | Pedido__c.Valor__c | campo | Código LWC |
| Componente base LDS (HTML) | lightning-output-field | — | Código LWC |
| Componente base LDS (HTML) | lightning-record-view-form | — | Código LWC |

## Comunicação

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Evento customizado | pedidoselecionado | CustomEvent | Código LWC |
| Message channel (LMS) | Pedido_Selecionado__c | chamadas no componente: publish | Código LWC |
| Componente filho (HTML) | c/pedidoItem | c-pedido-item | Código LWC |

## Permissões verificadas no código

| Tipo | Nome | Fonte |
|---|---|---|
| Custom Permission | Aprova_Pedido | Código LWC |

## Onde é usado (páginas Lightning)

Páginas Lightning (FlexiPage) processadas nesta execução que incluem o componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Pedido_Record_Page | RecordPage | sidebar | c_pedidoPainel | Sim | XML |
| Pedidos_App_Page | AppPage | main | c_pedidoPainel_app | Sim | XML |

## Onde é usado (Experience Cloud)

Páginas (views) de sites do Experience Cloud (ExperienceBundle) processadas nesta execução que incluem o componente. Página = `<bundle>/<view>`; visibilidade = há chave de público ou visibilidade no componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Portal_Clientes1/home | Experience Cloud | header | painel_cmp | Sim | JSON do ExperienceBundle |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0Rb000000000001AAA | Objeto interno |
| DeveloperName | pedidoPainel | Objeto interno |
| MasterLabel | Painel de Pedidos | Objeto interno |
| ApiVersion | 67.0 | Objeto interno |
| IsExposed | True | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

O LWC não tem acesso próprio por perfil ou permission set: aparece onde é colocado (páginas, ações, flows). As linhas mostram quem acessa as classes Apex chamadas e quem tem as Custom Permissions verificadas no código.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | Classe Apex chamada PedidoController | XML |
| Permission Set | Integracao_API | Habilitada | Custom Permission Aprova_Pedido | XML |
| Permission Set Group | PSG_Integracao | Habilitada | Custom Permission Aprova_Pedido; Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidotelaflow-lwc.md`

```markdown
# Lightning Web Component: pedidoTelaFlow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | pedidoTelaFlow | XML |
| MasterLabel | Tela de Pedido no Flow | XML |
| ApiVersion | 66.0 | XML |
| IsExposed | true | XML |
| Description | Não aplicável | XML |

## Arquivos do bundle

| Arquivo | Tipo | Fonte |
|---|---|---|
| pedidoTelaFlow.html | Template HTML | Código LWC |
| pedidoTelaFlow.js | JavaScript | Código LWC |
| pedidoTelaFlow.js-meta.xml | Configuração (.js-meta.xml) | Código LWC |

## Targets (onde o componente pode ser usado)

| Target | Uso | Fonte |
|---|---|---|
| lightning__FlowScreen | Componente de tela de Flow | XML |

## Propriedades configuráveis (targetConfigs)

| Targets | Propriedade | Tipo | Rótulo | Role | Obrigatória | Padrão | @api no JS | Fonte |
|---|---|---|---|---|---|---|---|---|
| lightning__FlowScreen | valor | Integer | Valor do Pedido | inputOnly | Não informado | Não informado | Sim | XML |
| lightning__FlowScreen | status | String | Status Selecionado | outputOnly | Não informado | Não informado | Sim | XML |
| lightning__FlowScreen | codigo | String | Código Cliente | entrada e saída (role ausente) | Não informado | Não informado | Sim | XML |
| lightning__FlowScreen | fantasma | String | Sem @api | entrada e saída (role ausente) | Não informado | Não informado | Não | XML |

## Restrições por target

| Targets | Restrição | Valor | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | XML |

## Propriedades e métodos públicos (@api)

| Membro | Tipo | Fonte |
|---|---|---|
| valor | propriedade | Código LWC |
| status | propriedade | Código LWC |
| codigo | propriedade | Código LWC |
| validate | método | Código LWC |

## Ciclo de vida implementado

| Hook | Fonte |
|---|---|
| connectedCallback | Código LWC |

## Métodos Apex chamados

| Classe | Método | Nome importado | Uso | Fonte |
|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | Código LWC |

## Verificação nas classes Apex

Para ser chamado pelo LWC, o método precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, também `cacheable=true`. A verificação usa o código das classes processadas nesta execução.

| Classe | Método | @AuraEnabled | Modificadores | Verificação | Fonte |
|---|---|---|---|---|---|
| Não informado | Não informado | Não informado | Não informado | Não informado | Código Apex |

## Dados do Salesforce usados

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Código LWC |

## Comunicação

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| Evento da plataforma | FlowAttributeChangeEvent | lightning/flowSupport | Código LWC |
| Evento da plataforma | FlowNavigationNextEvent | lightning/flowSupport | Código LWC |
| Canal de streaming (empApi) | /event/Pedido_Evento__e | lightning/empApi | Código LWC |

## Permissões verificadas no código

| Tipo | Nome | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | Código LWC |

## Onde é usado (páginas Lightning)

Páginas Lightning (FlexiPage) processadas nesta execução que incluem o componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Nenhuma página processada nesta execução usa o componente | — | — | — | — | XML |

## Onde é usado (Experience Cloud)

Páginas (views) de sites do Experience Cloud (ExperienceBundle) processadas nesta execução que incluem o componente. Página = `<bundle>/<view>`; visibilidade = há chave de público ou visibilidade no componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| Nenhuma página de Experience Cloud processada nesta execução usa o componente | — | — | — | — | JSON do ExperienceBundle |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0Rb000000000002AAA | Objeto interno |
| DeveloperName | pedidoTelaFlow | Objeto interno |
| MasterLabel | Tela de Pedido no Flow | Objeto interno |
| ApiVersion | 66.0 | Objeto interno |
| IsExposed | True | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

O LWC não tem acesso próprio por perfil ou permission set: aparece onde é colocado (páginas, ações, flows). As linhas mostram quem acessa as classes Apex chamadas e quem tem as Custom Permissions verificadas no código.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidotelaflow-lwc-flow-screen.md`

```markdown
# LWC em tela de Flow: pedidoTelaFlow

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | pedidoTelaFlow | XML |
| MasterLabel | Tela de Pedido no Flow | XML |
| ApiVersion | 66.0 | XML |
| @api validate() declarado | True | Código LWC |

## Propriedades expostas ao Flow

| Propriedade | Tipo | Rótulo | Role | @api no JS | Fonte |
|---|---|---|---|---|---|
| valor | Integer | Valor do Pedido | inputOnly | Sim | XML |
| status | String | Status Selecionado | outputOnly | Sim | XML |
| codigo | String | Código Cliente | entrada e saída (role ausente) | Sim | XML |
| fantasma | String | Sem @api | entrada e saída (role ausente) | Não | XML |

## Eventos de Flow disparados

| Evento | Fonte |
|---|---|
| FlowAttributeChangeEvent | Código LWC |
| FlowNavigationNextEvent | Código LWC |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0Rb000000000002AAA | Objeto interno |
| DeveloperName | pedidoTelaFlow | Objeto interno |
| MasterLabel | Tela de Pedido no Flow | Objeto interno |
| ApiVersion | 66.0 | Objeto interno |
| IsExposed | True | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |
| CreatedDate | 2026-01-01T00:00:00.000+0000 | Objeto interno |
| LastModifiedDate | 2026-10-01T00:00:00.000+0000 | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma concessão encontrada | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-record-page-flexipage.md`

```markdown
# Página Lightning (FlexiPage): Pedido_Record_Page

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Pedido_Record_Page | XML |
| MasterLabel | Pedido - Página de registro | XML |
| Type | RecordPage | XML |
| SobjectType | Pedido__c | XML |
| Template | flexipage:recordHomeTemplateDesktop | XML |
| Description | Página de registro do Pedido (simulada) | XML |
| ParentFlexiPage | Não aplicável | XML |

## Regiões

| Região | Tipo | Modo | Itens | Fonte |
|---|---|---|---|---|
| header | Region | Não informado | 1 | XML |
| Facet-detalhes | Facet | Não informado | 1 | XML |
| sidebar | Region | Não informado | 3 | XML |

## Componentes

| Região | Componente | Identificador | Tipo | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| header | force:highlightsPanel | force_highlightsPanel | Componente da plataforma | Não | XML |
| sidebar | c:pedidoPainel | c_pedidoPainel | Componente do projeto (c:) | Sim | XML |
| sidebar | flowruntime:interview | flowruntime_interview | Flow | Não | XML |
| sidebar | pkg:painelExterno | pkg_painelExterno | Componente de namespace (pkg) | Não | XML |

## Campos (Dynamic Forms)

| Região | Campo | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|
| Facet-detalhes | Record.Valor__c | RecordValor_cField | Sim | XML |

## Propriedades dos componentes

| Identificador | Componente | Propriedade | Valor | Fonte |
|---|---|---|---|---|
| c_pedidoPainel | c:pedidoPainel | titulo | Pedidos do cliente | XML |
| flowruntime_interview | flowruntime:interview | flowName | Tela_Cadastro | XML |

## Visibilidade condicional

Regra de visibilidade só esconde o componente na página; não substitui permissão de objeto, campo ou classe.

| Identificador | Contexto | Campo/variável | Operador | Valor | Lógica | Fonte |
|---|---|---|---|---|---|---|
| RecordValor_cField | User | {!$User.Profile.Name} | EQUAL | Vendas | Não informado | XML |
| c_pedidoPainel | Record | {!Record.Status__c} | EQUAL | Aprovado | 1 AND 2 | XML |
| c_pedidoPainel | Permission | {!$Permission.CustomPermission.Aprova_Pedido} | EQUAL | true | 1 AND 2 | XML |

## Flows embarcados

| Flow | Fonte |
|---|---|
| Tela_Cadastro | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0M0000000000000AAA | Objeto interno |
| DeveloperName | Pedido_Record_Page | Objeto interno |
| MasterLabel | Pedido - Página de registro | Objeto interno |
| Type | RecordPage | Objeto interno |
| EntityDefinitionId | 01I000000000000AAA | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |

## Acesso e configuração

Onde a página está ativada (padrão da org, padrão do app, app + perfil/record type) e quem tem as Custom Permissions usadas nas regras de visibilidade. Página não ativada não aparece para o usuário.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Padrão da org | Pedido__c | Ativada (View, Large) | Objeto Pedido__c | XML |
| Padrão do app | Vendas | Ativada (View, Large) | Objeto Pedido__c | XML |
| App + perfil | Vendas | Ativada (View, Large) | Objeto Pedido__c; Perfil Vendas; Record type Pedido__c.Padrao | XML |
| Permission Set | Integracao_API | Habilitada | Custom Permission Aprova_Pedido (visibilidade) | XML |
| Permission Set Group | PSG_Integracao | Habilitada | Custom Permission Aprova_Pedido (visibilidade); Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-pedidos-app-page-flexipage.md`

```markdown
# Página Lightning (FlexiPage): Pedidos_App_Page

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Pedidos_App_Page | XML |
| MasterLabel | Pedidos - Página de app | XML |
| Type | AppPage | XML |
| SobjectType | Não aplicável | XML |
| Template | flexipage:defaultAppHomeTemplate | XML |
| Description | Não aplicável | XML |
| ParentFlexiPage | Não aplicável | XML |

## Regiões

| Região | Tipo | Modo | Itens | Fonte |
|---|---|---|---|---|
| main | Region | Não informado | 1 | XML |

## Componentes

| Região | Componente | Identificador | Tipo | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| main | c:pedidoPainel | c_pedidoPainel_app | Componente do projeto (c:) | Sim | XML |

## Campos (Dynamic Forms)

| Região | Campo | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | XML |

## Propriedades dos componentes

| Identificador | Componente | Propriedade | Valor | Fonte |
|---|---|---|---|---|
| Não aplicável | Não aplicável | Não aplicável | Não aplicável | XML |

## Visibilidade condicional

Regra de visibilidade só esconde o componente na página; não substitui permissão de objeto, campo ou classe.

| Identificador | Contexto | Campo/variável | Operador | Valor | Lógica | Fonte |
|---|---|---|---|---|---|---|
| c_pedidoPainel_app | Client | {!$Client.formFactor} | EQUAL | Large | Não informado | XML |

## Flows embarcados

| Flow | Fonte |
|---|---|
| Não aplicável | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0M0000000000001AAA | Objeto interno |
| DeveloperName | Pedidos_App_Page | Objeto interno |
| MasterLabel | Pedidos - Página de app | Objeto interno |
| Type | AppPage | Objeto interno |
| EntityDefinitionId | Não informado | Objeto interno |
| Description | Não informado | Objeto interno |
| NamespacePrefix | Não informado | Objeto interno |

## Acesso e configuração

Onde a página está ativada (padrão da org, padrão do app, app + perfil/record type) e quem tem as Custom Permissions usadas nas regras de visibilidade. Página não ativada não aparece para o usuário.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Página não ativada nos componentes processados | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-evento-e-platform-event.md`

```markdown
# Platform Event: Pedido_Evento__e

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Pedido_Evento__e | XML |
| Label | Pedido Evento | XML |
| PluralLabel | Pedido Eventos | XML |
| Description | Evento de pedido enviado (simulado) | XML |
| EventType | HighVolume | XML |
| PublishBehavior | PublishAfterCommit | XML |
| DeploymentStatus | Deployed | XML |

## Campos do evento

| Campo | Rótulo | Tipo | Tamanho | Obrigatório | Fonte |
|---|---|---|---|---|---|
| Numero_Pedido__c | Número do Pedido | Text | 18 | true | XML |
| Payload__c | Payload | LongTextArea | 131072 | false | XML |

## Publicadores e assinantes

Entre os componentes processados nesta execução. Trigger de evento roda, por padrão, como Automated Process com lote de até 2.000 mensagens; PlatformEventSubscriberConfig muda usuário e lote.

| Papel | Tipo | Componente | Detalhe | Configuração do assinante | Fonte |
|---|---|---|---|---|---|
| Publica | Classe Apex | PedidoController | EventBus.publish (tipo instanciado no mesmo arquivo) | — | Derivado |
| Assina | Apex Trigger | PedidoEventoTrigger | after insert; status Active | PedidoEventoTriggerConfig: batchSize 200; usuário configurado (não documentado) | Derivado |
| Assina | Flow | Pedido_Evento_Flow | start.triggerType PlatformEvent; status Active | — | Derivado |
| Assina | LWC (lightning/empApi) | pedidoTelaFlow | /event/Pedido_Evento__e | — | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| QualifiedApiName | Pedido_Evento__e | Objeto interno |
| Label | Pedido Evento | Objeto interno |
| PluralLabel | Pedido Eventos | Objeto interno |
| KeyPrefix | e00 | Objeto interno |
| LastModifiedDate | 2026-01-10T12:00:00.000+0000 | Objeto interno |

## Acesso e configuração

Permissões de objeto do evento em perfis e permission sets.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Permission Set | Integracao_API | Ler, Criar | — | XML |
| Permission Set Group | PSG_Integracao | Ler, Criar | Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-canal-pedido-pedido-changeevent-change-data-capture.md`

```markdown
# Change Data Capture: Canal_Pedido_Pedido_ChangeEvent

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Membro do canal | Canal_Pedido_Pedido_ChangeEvent | XML |
| EventChannel | Canal_Pedido__chn | XML |
| SelectedEntity | Pedido__ChangeEvent | XML |
| FilterExpression | Valor__c > 1000 | XML |
| Objeto de origem | Pedido__c | Derivado |
| Tipo de canal | Canal customizado | Derivado |

## Campos de enriquecimento

Campos enviados mesmo sem alteração. Aparecem só em eventos de update e delete; recomenda-se configurar em canal customizado.

| Campo | Fonte |
|---|---|
| Status__c | XML |
| Valor__c | XML |

## Assinantes

| Papel | Tipo | Componente | Detalhe | Configuração do assinante | Fonte |
|---|---|---|---|---|---|
| Assina | Apex Trigger | PedidoChangeTrigger | after insert; status Active | Sem PlatformEventSubscriberConfig nos XMLs recuperados | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0v8000000000001AAA | Objeto interno |
| DeveloperName | Canal_Pedido_Pedido_ChangeEvent | Objeto interno |
| EventChannel | Canal_Pedido__chn | Objeto interno |
| SelectedEntity | Pedido__ChangeEvent | Objeto interno |

## Acesso e configuração

Assinar change events exige View All Data, View All Users ou "Ver todos" (View All Records) no objeto, conforme o canal. As linhas mostram essas concessões nos XMLs recuperados.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto de origem Pedido__c | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | Objeto de origem Pedido__c | XML |
| Perfil | Vendas | Ler | Objeto de origem Pedido__c | XML |
| Permission Set | Integracao_API | Ler, Editar | Objeto de origem Pedido__c | XML |
| Permission Set | Leitura_Pedidos | Ler | Objeto de origem Pedido__c | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Objeto de origem Pedido__c; Permission Set Integracao_API | XML |
| Perfil | Admin | Habilitada | Permissão de sistema ViewAllData | XML |
```

### `saida/docs/doc-dev-101326/doc-changeevents-pedido-changeevent-change-data-capture.md`

```markdown
# Change Data Capture: ChangeEvents_Pedido_ChangeEvent

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Membro do canal | ChangeEvents_Pedido_ChangeEvent | XML |
| EventChannel | ChangeEvents | XML |
| SelectedEntity | Pedido__ChangeEvent | XML |
| FilterExpression | Não informado | XML |
| Objeto de origem | Pedido__c | Derivado |
| Tipo de canal | Canal padrão do CDC (ChangeEvents) | Derivado |

## Campos de enriquecimento

Campos enviados mesmo sem alteração. Aparecem só em eventos de update e delete; recomenda-se configurar em canal customizado.

| Campo | Fonte |
|---|---|
| Não aplicável | XML |

## Assinantes

| Papel | Tipo | Componente | Detalhe | Configuração do assinante | Fonte |
|---|---|---|---|---|---|
| Assina | Apex Trigger | PedidoChangeTrigger | after insert; status Active | Sem PlatformEventSubscriberConfig nos XMLs recuperados | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0v8000000000000AAA | Objeto interno |
| DeveloperName | ChangeEvents_Pedido_ChangeEvent | Objeto interno |
| EventChannel | ChangeEvents | Objeto interno |
| SelectedEntity | Pedido__ChangeEvent | Objeto interno |

## Acesso e configuração

Assinar change events exige View All Data, View All Users ou "Ver todos" (View All Records) no objeto, conforme o canal. As linhas mostram essas concessões nos XMLs recuperados.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto de origem Pedido__c | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | Objeto de origem Pedido__c | XML |
| Perfil | Vendas | Ler | Objeto de origem Pedido__c | XML |
| Permission Set | Integracao_API | Ler, Editar | Objeto de origem Pedido__c | XML |
| Permission Set | Leitura_Pedidos | Ler | Objeto de origem Pedido__c | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Objeto de origem Pedido__c; Permission Set Integracao_API | XML |
| Perfil | Admin | Habilitada | Permissão de sistema ViewAllData | XML |
```

### `saida/docs/doc-dev-101326/doc-fila-pedidos-queue.md`

```markdown
# Fila: Fila_Pedidos

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Fila_Pedidos | XML |
| Label | Fila de Pedidos | XML |
| DoesSendEmailToMembers | false | XML |
| QueueRoutingConfig | Não informado | XML |
| Usuários membros | 1 usuário(s) (não documentados) | XML |

## Objetos aceitos

| Objeto | Fonte |
|---|---|
| Pedido__c | XML |
| Case | XML |

## Regras que direcionam para a fila

Regras de atribuição e de escalonamento processadas nesta execução cujo destino é esta fila.

| Tipo | Objeto | Regra | Entrada | Regra ativa | Fonte |
|---|---|---|---|---|---|
| AssignmentRules | Case | Atribuicao_Case | 1 | true | Derivado |
| EscalationRules | Case | Escalonamento_Case | 1 | true | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00G000000000001AAA | Objeto interno |
| Name | Fila de Pedidos | Objeto interno |
| DeveloperName | Fila_Pedidos | Objeto interno |
| Type | Queue | Objeto interno |
| DoesSendEmailToMembers | False | Objeto interno |

## Acesso e configuração

Quem trabalha os registros da fila: membros do XML (papéis, grupos e outros). Usuários aparecem só como contagem.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| publicGroups | Grupo_Suporte | Membro da fila | — | XML |
| roles | Vendas | Membro da fila | — | XML |
| Usuários | 1 (não documentados) | Membro da fila | — | XML |
```

### `saida/docs/doc-dev-101326/doc-portal-clientes1-experience.md`

```markdown
# Experience Builder (ExperienceBundle): Portal_Clientes1

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Portal_Clientes1 | XML |
| Label | Portal_Clientes1 | XML |
| Tipo | ChatterNetworkPicasso | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| Não aplicável | Não aplicável | XML |

## Pastas do bundle

| Pasta | Arquivos JSON | Fonte |
|---|---|---|
| config | 1 | JSON do ExperienceBundle |
| routes | 2 | JSON do ExperienceBundle |
| themes | 1 | JSON do ExperienceBundle |
| views | 2 | JSON do ExperienceBundle |

## Páginas (views)

| View | Rótulo | Layout | Componentes | Arquivo | Fonte |
|---|---|---|---|---|---|
| home | Home | siteforce:sldsTwoFrameEightFourLayout | 3 | views/home.json | JSON do ExperienceBundle |
| login | Login | siteforce:sldsOneColLayout | 1 | views/login.json | JSON do ExperienceBundle |

## Rotas e acesso às páginas

Acesso à página como está na rota (ex.: público ou exige login); valor ausente fica "Não informado".

| Rota | URL | Acesso à página | View ativa | Tipo | Arquivo | Fonte |
|---|---|---|---|---|---|---|
| home | (vazio) | RequiresLogin | home | home | routes/home.json | JSON do ExperienceBundle |
| login | login | Public | login | login-main | routes/login.json | JSON do ExperienceBundle |

## Componentes por página

| View | Região | Componente | Identificador | Fonte |
|---|---|---|---|---|
| home | header | c:portalBanner | banner_cmp | JSON do ExperienceBundle |
| home | header | c:pedidoPainel | painel_cmp | JSON do ExperienceBundle |
| home | content | forceCommunity:richText | texto_cmp | JSON do ExperienceBundle |
| login | content | salesforceIdentity:loginForm2 | login_cmp | JSON do ExperienceBundle |

## Público-alvo e visibilidade

Referências de público (audience) e visibilidade como estão no JSON. Os critérios não são interpretados.

| View | Componente | Chave | Valor | Fonte |
|---|---|---|---|---|
| home | c:pedidoPainel | targetAudience | Audiencia_Clientes_VIP | JSON do ExperienceBundle |

## Acesso e configuração

Quem pode executar as classes Apex chamadas pelos LWC das páginas. Quem entra no site está no documento da Network; o acesso a cada página, na tabela de rotas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não verificado | portalBanner não processado nesta execução | — | — | XML |
| Perfil | Admin | Executar | Classe Apex PedidoController (LWC pedidoPainel) | XML |
```

### `saida/docs/doc-dev-101326/doc-extrairpedido-dataraptor.md`

```markdown
# DataRaptor (OmniDataTransform): ExtrairPedido

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | ExtrairPedido | XML |
| Tipo | Extract | XML |
| Entrada | JSON | XML |
| Saída | JSON | XML |
| IsActive | true | XML |
| VersionNumber | 1 | XML |
| Description | Lê o pedido e a conta | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| isFieldLevelSecurityEnabled | true | XML |

## Itens de mapeamento

Itens na ordem do XML. A fórmula não é reproduzida, só se existe.

| Ordem | Objeto de entrada | Campo de entrada | Objeto de saída | Campo/caminho de saída | Filtro | Fórmula | Fonte |
|---|---|---|---|---|---|---|---|
| 1 | Pedido__c | Id | Não informado | Pedido | = PedidoId | Não informado | XML |
| 2 | Pedido__c | Valor__c | Não informado | Pedido:Valor | Não informado | Não informado | XML |
| 3 | Account | Name | Não informado | Conta:Nome | Não informado | Sim | XML |

## Objetos lidos

| Objeto | Fonte |
|---|---|
| Account | Derivado |
| Pedido__c | Derivado |

## Objetos gravados

| Objeto | Fonte |
|---|---|
| Não aplicável | Derivado |

## Quem usa

| Componente | Tipo | Elemento | Fonte |
|---|---|---|---|
| Pedido_EnviarERP_Procedure_1 | Integration Procedure | DR_ExtrairPedido | XML |
| Vendas_CriarPedido_Portuguese_1 | OmniScript | DR_Carregar | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0jI000000000001AAA | Objeto interno |
| Name | ExtrairPedido | Objeto interno |
| Type | Extract | Objeto interno |
| IsActive | True | Objeto interno |
| VersionNumber | 1 | Objeto interno |

## Acesso e configuração

Quem tem permissão nos objetos que o DataRaptor lê ou grava. Se o DataRaptor aplica ou não a segurança do usuário aparece nas configurações, como está no XML.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Portal Clientes Profile | Ler, Editar | Objeto lido Account | XML |
| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | Objeto lido Pedido__c | XML |
| Perfil | Portal Clientes Profile | Ler, Criar | Objeto lido Pedido__c | XML |
| Perfil | Vendas | Ler | Objeto lido Pedido__c | XML |
| Permission Set | Integracao_API | Ler, Editar | Objeto lido Pedido__c | XML |
| Permission Set | Leitura_Pedidos | Ler | Objeto lido Pedido__c | XML |
| Permission Set Group | PSG_Integracao | Ler, Editar | Objeto lido Pedido__c; Permission Set Integracao_API | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-enviarerp-procedure-1-integration-procedure.md`

```markdown
# Integration Procedure: Pedido_EnviarERP_Procedure_1

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Pedido_EnviarERP_Procedure_1 | XML |
| Type | Pedido | XML |
| SubType | EnviarERP | XML |
| Type_SubType | Pedido_EnviarERP | Derivado |
| Language | Procedure | XML |
| IsActive | true | XML |
| VersionNumber | 1 | XML |
| Description | Envia o pedido ao ERP | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| isIntegrationProcedure | true | XML |

## Elementos

Elementos na ordem do XML. A configuração de cada elemento não é reproduzida: só os componentes que ela referencia.

| Ordem | Elemento | Tipo | Nível | Elemento pai | Ativo | Referências | Fonte |
|---|---|---|---|---|---|---|---|
| 1 | DR_ExtrairPedido | DataRaptor Extract Action | 0 | Não informado | true | DataRaptor ExtrairPedido | XML |
| 2 | HTTP_EnviarERP | Rest Action | 0 | Não informado | true | Named Credential Minha_NC | XML |
| 3 | Remote_Registrar | Remote Action | 0 | Não informado | true | Classe Apex PedidoService | XML |
| 4 | Resposta | Response Action | 0 | Não informado | true | Não informado | XML |

## Componentes referenciados

| Tipo | Componente | Elemento | Fonte |
|---|---|---|---|
| DataRaptor | ExtrairPedido | DR_ExtrairPedido | XML |
| Named Credential | Minha_NC | HTTP_EnviarERP | XML |
| Classe Apex | PedidoService | Remote_Registrar | XML |

## Quem chama

| Componente | Tipo | Elemento | Fonte |
|---|---|---|---|
| Vendas_CriarPedido_Portuguese_1 | OmniScript | IP_Enviar | XML |
| CartaoPedido_1 | FlexCard | Fonte de dados | XML |
| CartaoPedido_1 | FlexCard | Reenviar | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0jN000000000001AAA | Objeto interno |
| UniqueName | Pedido_EnviarERP_Procedure_1 | Objeto interno |
| Type | Pedido | Objeto interno |
| SubType | EnviarERP | Objeto interno |
| Language | Procedure | Objeto interno |
| VersionNumber | 1 | Objeto interno |
| IsActive | True | Objeto interno |
| IsIntegrationProcedure | True | Objeto interno |

## Acesso e configuração

Quem pode executar as classes Apex chamadas (Remote Action). Named Credentials usadas aparecem nos componentes referenciados.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Perfil | Admin | Executar | Classe Apex PedidoService | XML |
| Perfil | Vendas | Executar | Classe Apex PedidoService | XML |
```

### `saida/docs/doc-dev-101326/doc-vendas-criarpedido-portuguese-1-omniscript.md`

```markdown
# OmniScript: Vendas_CriarPedido_Portuguese_1

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Vendas_CriarPedido_Portuguese_1 | XML |
| Type | Vendas | XML |
| SubType | CriarPedido | XML |
| Type_SubType | Vendas_CriarPedido | Derivado |
| Language | Portuguese | XML |
| IsActive | true | XML |
| VersionNumber | 1 | XML |
| Description | Não aplicável | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| isIntegrationProcedure | false | XML |

## Elementos

Elementos na ordem do XML. A configuração de cada elemento não é reproduzida: só os componentes que ela referencia.

| Ordem | Elemento | Tipo | Nível | Elemento pai | Ativo | Referências | Fonte |
|---|---|---|---|---|---|---|---|
| 1 | Passo_Cliente | Step | 0 | Não informado | true | Não informado | XML |
| 2 | Texto_Ajuda | Text Block | 1 | Passo_Cliente | true | Não informado | XML |
| 3 | DR_Carregar | DataRaptor Extract Action | 0 | Não informado | true | DataRaptor ExtrairPedido | XML |
| 4 | IP_Enviar | Integration Procedure Action | 0 | Não informado | true | Integration Procedure Pedido_EnviarERP | XML |
| 5 | Navegar | Navigate Action | 0 | Não informado | true | Não informado | XML |

## Componentes referenciados

| Tipo | Componente | Elemento | Fonte |
|---|---|---|---|
| DataRaptor | ExtrairPedido | DR_Carregar | XML |
| Integration Procedure | Pedido_EnviarERP | IP_Enviar | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0jN000000000002AAA | Objeto interno |
| UniqueName | Vendas_CriarPedido_Portuguese_1 | Objeto interno |
| Type | Vendas | Objeto interno |
| SubType | CriarPedido | Objeto interno |
| Language | Portuguese | Objeto interno |
| VersionNumber | 1 | Objeto interno |
| IsActive | True | Objeto interno |
| IsIntegrationProcedure | False | Objeto interno |

## Acesso e configuração

Quem pode executar as classes Apex chamadas (Remote Action). O acesso ao formulário vem de onde ele é colocado (página, site, FlexCard).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma classe Apex referenciada com acesso concedido | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-cartaopedido-1-flexcard.md`

```markdown
# FlexCard (OmniUiCard): CartaoPedido_1

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | CartaoPedido_1 | XML |
| IsActive | true | XML |
| VersionNumber | 1 | XML |
| Description | Resumo do pedido | XML |
| Tipo da fonte de dados | IntegrationProcedures | XML |
| Fonte de dados | Integration Procedure Pedido_EnviarERP | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| omniUiCardType | Parent | XML |

## Ações

Ações do card como estão no JSON de configuração (o texto não é reproduzido).

| Ação | Tipo | Referências | Fonte |
|---|---|---|---|
| Reenviar | IntegrationProcedure | Integration Procedure Pedido_EnviarERP | XML |
| Detalhes | Flyout | Não informado | XML |

## Componentes referenciados

| Tipo | Componente | Elemento | Fonte |
|---|---|---|---|
| Integration Procedure | Pedido_EnviarERP | Fonte de dados | XML |
| Integration Procedure | Pedido_EnviarERP | Reenviar | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 0kc000000000001AAA | Objeto interno |
| UniqueName | CartaoPedido_1 | Objeto interno |
| Name | CartaoPedido | Objeto interno |
| VersionNumber | 1 | Objeto interno |
| IsActive | True | Objeto interno |

## Acesso e configuração

Quem pode executar as classes Apex referenciadas. O acesso aos dados vem da fonte de dados (DataRaptor ou Integration Procedure).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma classe Apex referenciada com acesso concedido | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-pedido-c-sharing-rules.md`

```markdown
# Regras de compartilhamento: Pedido__c

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | Pedido__c | XML |

## Regras por critério

| Regra | Rótulo | Acesso | Compartilhado com | Critérios | Lógica | Fonte |
|---|---|---|---|---|---|---|
| Pedidos_Altos | Pedidos Altos | Read | role=Gerente_Vendas | field=Valor__c, operation=greaterThan, value=1000 | Não informado | XML |

## Regras por proprietário

| Regra | Rótulo | Acesso | Compartilhado com | Registros de | Fonte |
|---|---|---|---|---|---|
| Pedidos_Suporte | Pedidos Suporte | Edit | group=Grupo_Suporte | roleAndSubordinates=Vendas | XML |

## Regras para convidado (sites)

Regras que expõem registros a visitantes não autenticados de um site (usuário convidado).

| Regra | Rótulo | Acesso | Compartilhado com | Critérios | Lógica | Fonte |
|---|---|---|---|---|---|---|
| Pedidos_Portal | Pedidos do Portal | Read | guestUser=Portal_Clientes | field=Publico__c, operation=equals, value=True | Não informado | XML |

## Padrão de compartilhamento do objeto (OWD)

As regras só ampliam acesso a partir do padrão do objeto.

| Objeto | Interno (sharingModel) | Externo (externalSharingModel) | Fonte |
|---|---|---|---|
| Pedido__c | ReadWrite | Não informado | XML |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Regras de compartilhamento não são concedidas por perfil ou permission set | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-diretoria-role.md`

```markdown
# Papel (Role): Diretoria

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Diretoria | XML |
| Label | Diretoria | XML |
| ParentRole | Não aplicável | XML |
| Description | Não aplicável | XML |
| CaseAccessLevel | Edit | XML |
| ContactAccessLevel | Edit | XML |
| OpportunityAccessLevel | Edit | XML |
| MayForecastManagerShare | false | XML |

## Hierarquia

Papéis acima herdam acesso aos registros deste papel quando o objeto concede acesso pela hierarquia.

| Relação | Papel | Nível | Fonte |
|---|---|---|---|
| Topo da hierarquia (sem parentRole) | Diretoria | 0 | Derivado |
| Subordinado direto | Vendas | 1 abaixo | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00E000000000000AAA | Objeto interno |
| Name | Diretoria | Objeto interno |
| DeveloperName | Diretoria | Objeto interno |
| ParentRoleId | Não informado | Objeto interno |
| RollupDescription | Diretoria | Objeto interno |

## Acesso e configuração

Papel não é concedido por perfil/permission set. As linhas mostram as regras de compartilhamento que dão acesso a este papel.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma regra de compartilhamento compartilha com este componente | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-gerente-vendas-role.md`

```markdown
# Papel (Role): Gerente_Vendas

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Gerente_Vendas | XML |
| Label | Gerente de Vendas | XML |
| ParentRole | Vendas | XML |
| Description | Não aplicável | XML |
| CaseAccessLevel | Read | XML |
| ContactAccessLevel | Read | XML |
| OpportunityAccessLevel | Read | XML |
| MayForecastManagerShare | false | XML |

## Hierarquia

Papéis acima herdam acesso aos registros deste papel quando o objeto concede acesso pela hierarquia.

| Relação | Papel | Nível | Fonte |
|---|---|---|---|
| Acima | Vendas | 1 acima | Derivado |
| Acima | Diretoria | 2 acima | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00E000000000002AAA | Objeto interno |
| Name | Gerente de Vendas | Objeto interno |
| DeveloperName | Gerente_Vendas | Objeto interno |
| ParentRoleId | 00E000000000001AAA | Objeto interno |
| RollupDescription | Gerente de Vendas | Objeto interno |

## Acesso e configuração

Papel não é concedido por perfil/permission set. As linhas mostram as regras de compartilhamento que dão acesso a este papel.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Regra de compartilhamento | Pedidos_Altos | Read | Objeto Pedido__c; Regra de compartilhamento por critério | XML |
```

### `saida/docs/doc-dev-101326/doc-vendas-role.md`

```markdown
# Papel (Role): Vendas

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | Vendas | XML |
| Label | Vendas | XML |
| ParentRole | Diretoria | XML |
| Description | Equipe de vendas (simulado) | XML |
| CaseAccessLevel | Read | XML |
| ContactAccessLevel | Edit | XML |
| OpportunityAccessLevel | Read | XML |
| MayForecastManagerShare | false | XML |

## Hierarquia

Papéis acima herdam acesso aos registros deste papel quando o objeto concede acesso pela hierarquia.

| Relação | Papel | Nível | Fonte |
|---|---|---|---|
| Acima | Diretoria | 1 acima | Derivado |
| Subordinado direto | Gerente_Vendas | 1 abaixo | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00E000000000001AAA | Objeto interno |
| Name | Vendas | Objeto interno |
| DeveloperName | Vendas | Objeto interno |
| ParentRoleId | 00E000000000000AAA | Objeto interno |
| RollupDescription | Vendas | Objeto interno |

## Acesso e configuração

Papel não é concedido por perfil/permission set. As linhas mostram as regras de compartilhamento que dão acesso a este papel.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Nenhuma regra de compartilhamento compartilha com este componente | — | — | — | XML |
```

### `saida/docs/doc-dev-101326/doc-security-org-security.md`

```markdown
# Segurança da org: Security

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Componente | Security | XML |

## Sessão

| Propriedade | Valor | Fonte |
|---|---|---|
| forceLogoutOnSessionTimeout | true | XML |
| lockSessionsToDomain | true | XML |
| lockSessionsToIp | false | XML |
| sessionTimeout | TwoHours | XML |

## Senhas

| Propriedade | Valor | Fonte |
|---|---|---|
| complexity | AlphaNumeric | XML |
| expiration | NinetyDays | XML |
| historyRestriction | 3 | XML |
| maxLoginAttempts | TenAttempts | XML |
| minimumPasswordLength | 8 | XML |

## Faixas de IP confiáveis

| Faixa (como no XML) | Fonte |
|---|---|
| description=Rede corporativa (simulada), end=10.0.0.254, start=10.0.0.1 | XML |

## Padrão de compartilhamento por objeto (OWD)

Objetos processados nesta execução (grupo CustomObject). Padrões de objetos padrão também aparecem nos dados internos (Organization).

| Objeto | Rótulo | Interno (sharingModel) | Externo (externalSharingModel) | Fonte |
|---|---|---|---|---|
| Config__mdt | Config | Não informado | Não informado | XML |
| Pedido__c | Pedido | ReadWrite | Não informado | XML |
| Pedido_Evento__e | Pedido Evento | Não informado | Não informado | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| Id | 00D000000000000AAA | Objeto interno |
| Name | Org Simulada | Objeto interno |
| OrganizationType | Developer Edition | Objeto interno |
| IsSandbox | False | Objeto interno |
| InstanceName | NA000 | Objeto interno |
| DefaultAccountAccess | Edit | Objeto interno |
| DefaultContactAccess | ControlledByParent | Objeto interno |
| DefaultOpportunityAccess | None | Objeto interno |
| DefaultCaseAccess | Read | Objeto interno |
| DefaultLeadAccess | ReadEditTransfer | Objeto interno |
| DefaultCalendarAccess | HideDetailsInsert | Objeto interno |
| DefaultPricebookAccess | ReadSelect | Objeto interno |
| DefaultCampaignAccess | All | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| Não aplicável | Configuração global da org; não é concedida por perfil ou permission set | — | — | XML |
```

