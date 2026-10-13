# Fila: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ queue_api_name }} | XML |
| Label | {{ queue_label }} | XML |
| DoesSendEmailToMembers | {{ send_email }} | XML |
| QueueRoutingConfig | {{ routing_config }} | XML |
| Usuários membros | {{ user_members }} | XML |

## Objetos aceitos

| Objeto | Fonte |
|---|---|
| {{ queue_object }} | XML |

## Regras que direcionam para a fila

Regras de atribuição e de escalonamento processadas nesta execução cujo destino é esta fila.

| Tipo | Objeto | Regra | Entrada | Regra ativa | Fonte |
|---|---|---|---|---|---|
| {{ target_rule_type }} | {{ target_object }} | {{ target_rule }} | {{ target_order }} | {{ target_active }} | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Quem trabalha os registros da fila: membros do XML (papéis, grupos e outros). Usuários aparecem só como contagem.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
