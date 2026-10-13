# Platform Event: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ event_name }} | XML |
| Label | {{ label }} | XML |
| PluralLabel | {{ plural_label }} | XML |
| Description | {{ description }} | XML |
| EventType | {{ event_type }} | XML |
| PublishBehavior | {{ publish_behavior }} | XML |
| DeploymentStatus | {{ deployment_status }} | XML |

## Campos do evento

| Campo | Rótulo | Tipo | Tamanho | Obrigatório | Fonte |
|---|---|---|---|---|---|
| {{ field }} | {{ label }} | {{ type }} | {{ length }} | {{ required }} | XML |

## Publicadores e assinantes

Entre os componentes processados nesta execução. Trigger de evento roda, por padrão, como Automated Process com lote de até 2.000 mensagens; PlatformEventSubscriberConfig muda usuário e lote.

| Papel | Tipo | Componente | Detalhe | Configuração do assinante | Fonte |
|---|---|---|---|---|---|
| {{ event_role }} | {{ event_kind }} | {{ event_component }} | {{ event_detail }} | {{ event_subscriber_config }} | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Permissões de objeto do evento em perfis e permission sets.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
