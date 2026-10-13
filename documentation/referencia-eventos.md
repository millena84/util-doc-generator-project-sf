# Referência: objetos de evento (platform events e Change Data Capture)

Conteúdo **genérico da plataforma** (publicação, assinatura, retenção, replay, tipos de campo), que vale para qualquer evento. Por isso ele não aparece como propriedade nos documentos gerados (`modelo-doc-platform-event`, `modelo-doc-change-data-capture`), que só mostram o que está no XML, no código dos componentes processados e nos dados internos.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-platform-objects.md` (material de referência, não normativo; Onda 06). O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13): os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Decoupled Publishing and Subscription (Publish Immediately): <https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_considerations_decoupled_processes.htm>
- Configure the User and Batch Size for Your Platform Event Trigger (PlatformEventSubscriberConfig): <https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_trigger_config.htm>
- Subscribe to Platform Event Messages with Flows: <https://developer.salesforce.com/docs/platform/platform-events/guide/platform-events-subscribe-flow.html>
- `EventBus` class: <https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_System_eventbus.htm>
- CDC — Channels and Channel Members: <https://developer.salesforce.com/docs/platform/change-data-capture/guide/cdc-channel-examples.html>
- CDC — Enrich Change Events: <https://developer.salesforce.com/docs/platform/change-data-capture/guide/cdc-enrich-intro.html>
- CDC — Add Enrichment with Metadata API: <https://developer.salesforce.com/docs/platform/change-data-capture/guide/cdc-enrich-metadata-api.html>
- CDC — Change Event Storage and Delivery: <https://developer.salesforce.com/docs/platform/change-data-capture/guide/cdc-subscribe-delivery.html>
- CDC — Change Event Triggers: <https://developer.salesforce.com/docs/platform/change-data-capture/guide/cdc-trigger-intro.html>

## Platform events (`__e`)

| Tema | Situação |
|---|---|
| `PublishImmediately`: publicado fora da transação; não é desfeito em rollback | confirmado |
| `PublishAfterCommit`: só publica após o commit | *a confirmar* (o `ajudAI` afirma) |
| Trigger de evento roda como **Automated Process** com lote de até **2.000** mensagens; `PlatformEventSubscriberConfig` (API 51+) muda usuário e lote | confirmado |
| Com o usuário padrão, não é possível enviar e-mail (`Messaging.SingleEmailMessage`) da trigger | confirmado |
| Flow disparado por evento: até 200 mensagens por lote; cada entrevista roda no contexto de quem publicou | confirmado |
| Trigger de evento só aceita `after insert` | *a confirmar* |
| Tipos de campo permitidos (Text, LongTextArea, Number, Date/DateTime, Checkbox; sem Lookup/Fórmula) | *a confirmar*; o documento mostra o tipo do XML |
| Retenção de 24 h / 72 h para eventos de alto volume e opções de replay `-1`/`-2` | *a confirmar* |
| Permissão Criar = publicar, Ler = assinar | *a confirmar*; o documento mostra as permissões de objeto do evento |

- **Correção do `ajudAI`:** o exemplo de `PlatformEventSubscriberConfig` sugere 200 como referência; o padrão da plataforma sem configuração é **2.000**.
- O usuário configurado em `PlatformEventSubscriberConfig` é um nome de usuário: o utilitário registra só que existe um usuário configurado, nunca o valor (proteção de dados).

## Change Data Capture

| Tema | Situação |
|---|---|
| Seleção de objetos: `PlatformEventChannelMember` (`selectedEntity`, ex.: `AccountChangeEvent`), no canal padrão `ChangeEvents` ou em canal customizado (`PlatformEventChannel`) | confirmado |
| Membro: zero ou mais campos de enriquecimento (até 10) e no máximo um filtro | confirmado |
| Campos de enriquecimento aparecem só em eventos de update e delete; recomenda-se canal customizado | confirmado |
| Retenção de change events: 3 dias; entrega na ordem do ReplayId | confirmado |
| Assinante precisa de View All Data, View All Users ou View All Records do objeto, conforme o canal | confirmado |
| `PlatformEventSubscriberConfig` também configura triggers de change event | confirmado |
| Nome do change event de objeto customizado: `X__ChangeEvent` | convenção usada pelo utilitário; *a confirmar* |
| `ChangeEventHeader` (`changeType`, `changedFields`, `recordIds`, `commitUser`...) | *a confirmar*; não é propriedade do documento |

- **Correções do `ajudAI`:**
  - a seleção de objetos não fica em `ChangeDataCapture.settings` (`selectedEntities`): fica em `PlatformEventChannelMember`;
  - o tipo de enriquecimento é `PlatformEventChannelMember`, não `EventChannelMember`;
  - a permissão citada `ViewChangeDataCapture` não foi encontrada; a documentação cita View All Data, View All Users ou View All Records;
  - "CDC respeita FLS e remove o campo do payload" não foi confirmado nesta adaptação.

## O que os documentos mostram

| Documento | Mostra | Fonte |
|---|---|---|
| Platform event | Identificação do `.object-meta.xml`, campos, publicadores e assinantes, configuração das triggers assinantes (sem usuário), permissões de objeto | XML, Derivado, Objeto interno |
| Change Data Capture (por membro de canal) | Canal, evento selecionado, filtro, enriquecimento, objeto de origem, assinantes, permissões exigidas | XML, Derivado, Objeto interno |

Publicadores e assinantes vêm dos componentes processados na mesma execução: Apex com `EventBus.publish` e `new X__e(` no mesmo arquivo, triggers no evento, Flows disparados pelo evento (`start.triggerType` PlatformEvent) ou que criam o evento (`recordCreates`), e LWC com `lightning/empApi` e canal literal (`/event/...`, `/data/...`).
