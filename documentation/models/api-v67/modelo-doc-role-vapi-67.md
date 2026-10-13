# Papel (Role): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ role_api_name }} | XML |
| Label | {{ role_label }} | XML |
| ParentRole | {{ parent_role }} | XML |
| Description | {{ description }} | XML |
| CaseAccessLevel | {{ case_access }} | XML |
| ContactAccessLevel | {{ contact_access }} | XML |
| OpportunityAccessLevel | {{ opportunity_access }} | XML |
| MayForecastManagerShare | {{ forecast_share }} | XML |

## Hierarquia

Papéis acima herdam acesso aos registros deste papel quando o objeto concede acesso pela hierarquia.

| Relação | Papel | Nível | Fonte |
|---|---|---|---|
| {{ hierarchy_relation }} | {{ hierarchy_role }} | {{ hierarchy_level }} | Derivado |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Papel não é concedido por perfil/permission set. As linhas mostram as regras de compartilhamento que dão acesso a este papel.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
