# Trigger Apex: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| TriggerName | {{ trigger_name }} | XML |
| Objeto | {{ trigger_sobject }} | Código Apex |
| ApiVersion | {{ api_version }} | XML |
| Status | {{ status }} | XML |
| Descrição (ApexDoc) | {{ description }} | Código Apex |

## Eventos

| Evento | Momento | Operação | Fonte |
|---|---|---|---|
| {{ trigger_event }} | {{ event_timing }} | {{ event_operation }} | Código Apex |

## Variáveis de contexto usadas

| Variável | Fonte |
|---|---|
| {{ context_variable }} | Código Apex |

## Classes chamadas pela trigger

| Classe | Referência | Membros chamados | Classe da org | Fonte |
|---|---|---|---|---|
| {{ class_name }} | {{ class_reference }} | {{ class_members }} | {{ class_in_org }} | Código Apex |

## Leituras de configuração

Leituras de Custom Permission, Custom Setting e Custom Metadata Type no código. A leitura pode ser um mecanismo de desativação (bypass), mas isso não é inferido: confira o uso no código.

| Onde | Mecanismo | Componente | Chamada | Registro | Fonte |
|---|---|---|---|---|---|
| {{ read_location }} | {{ read_mechanism }} | {{ read_component }} | {{ read_call }} | {{ read_record }} | Código Apex |

## Controles de segurança

Controles explícitos de modo de acesso e de CRUD/FLS no código. Sem controle explícito, vale o modo padrão da `apiVersion` de cada arquivo (mudou na API 67.0; ver `documentation/referencia-apex-trigger.md`).

| Onde | Controle | Ocorrências | Fonte |
|---|---|---|---|
| {{ security_location }} | {{ security_pattern }} | {{ security_occurrences }} | Código Apex |

## Coexistência no objeto e ordem de execução

Automações do mesmo objeto processadas nesta execução, na ordem oficial de execução (Apex Developer Guide, *Triggers and Order of Execution*). Componentes fora do escopo da execução não aparecem.

| Ordem | Fase | Tipo | Componente | Eventos | Status/Ativo | Observação | Fonte |
|---|---|---|---|---|---|---|---|
| {{ exec_order }} | {{ exec_phase }} | {{ automation_type }} | {{ automation_name }} | {{ automation_events }} | {{ automation_status }} | {{ automation_order_detail }} | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

A trigger não tem acesso próprio por perfil ou permission set: dispara na operação DML do objeto. As linhas mostram quem tem acesso ao objeto e às classes chamadas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
