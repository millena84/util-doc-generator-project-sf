# Processo de negócio: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ process_name }} | XML |
| MasterLabel | {{ master_label }} | XML |
| Description | {{ description }} | XML |
| IsActive | {{ is_active }} | XML |
| Valor padrão | {{ default_value }} | XML |

## Valores do processo

Valores da picklist do processo (em Opportunity, as etapas de StageName), na ordem do XML.

| Ordem | Valor | Padrão | Fonte |
|---|---|---|---|
| {{ value_order }} | {{ process_value }} | {{ value_default }} | XML |

## Record types que usam o processo

O processo não é atribuído a perfis: ele é vinculado a record types, que são liberados em perfis e permission sets.

| Record type | Rótulo | Ativo | Fonte |
|---|---|---|---|
| {{ record_type }} | {{ rt_label }} | {{ rt_active }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Perfis e permission sets que enxergam os record types que usam este processo.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
