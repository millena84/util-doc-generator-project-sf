# Change Data Capture: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Membro do canal | {{ member_name }} | XML |
| EventChannel | {{ event_channel }} | XML |
| SelectedEntity | {{ selected_entity }} | XML |
| FilterExpression | {{ filter_expression }} | XML |
| Objeto de origem | {{ base_object }} | Derivado |
| Tipo de canal | {{ channel_kind }} | Derivado |

## Campos de enriquecimento

Campos enviados mesmo sem alteração. Aparecem só em eventos de update e delete; recomenda-se configurar em canal customizado.

| Campo | Fonte |
|---|---|
| {{ enriched_field }} | XML |

## Assinantes

| Papel | Tipo | Componente | Detalhe | Configuração do assinante | Fonte |
|---|---|---|---|---|---|
| {{ event_role }} | {{ event_kind }} | {{ event_component }} | {{ event_detail }} | {{ event_subscriber_config }} | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Assinar change events exige View All Data, View All Users ou "Ver todos" (View All Records) no objeto, conforme o canal. As linhas mostram essas concessões nos XMLs recuperados.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
