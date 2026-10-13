# Custom Object: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| DeveloperName | {{ developer_name }} | XML |
| Label | {{ label }} | XML |
| PluralLabel | {{ plural_label }} | XML |
| SharingModel | {{ sharing_model }} | XML |
| DeploymentStatus | {{ deployment_status }} | XML |

## Custom Fields

| Field | Label | Type | Fonte |
|---|---|---|---|
| {{ field }} | {{ label }} | {{ type }} | XML |

## Validation Rules

| Regra | Ativa | Condição de erro | Mensagem de erro | Fonte |
|---|---|---|---|---|
| {{ rule }} | {{ active }} | {{ condition }} | {{ error_message }} | XML |

## Record Types

| Record Type | Label | Ativo | Fonte |
|---|---|---|---|
| {{ record_type }} | {{ label }} | {{ active }} | XML |

## Componentes relacionados

| Componente | Tipo | Fonte |
|---|---|---|
| {{ related_component }} | {{ related_type }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Tooling API |

## Compartilhamento e filas

| Tipo | Nome | Compartilhado com | Nível de acesso | Fonte |
|---|---|---|---|---|
| {{ sharing_kind }} | {{ sharing_name }} | {{ shared_to }} | {{ sharing_access_level }} | XML |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
