# Permission Set: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ ps_name }} | XML |
| Label | {{ label }} | XML |
| Description | {{ description }} | XML |
| License | {{ license }} | XML |
| HasActivationRequired | {{ has_activation_required }} | XML |

## Objetos

| Objeto | Ler | Criar | Editar | Excluir | Ver todos | Modificar todos | Fonte |
|---|---|---|---|---|---|---|---|
| {{ object }} | {{ allow_read }} | {{ allow_create }} | {{ allow_edit }} | {{ allow_delete }} | {{ view_all }} | {{ modify_all }} | XML |

## Campos

| Campo | Ler | Editar | Fonte |
|---|---|---|---|
| {{ field }} | {{ readable }} | {{ editable }} | XML |

## Classes Apex

| Classe | Fonte |
|---|---|
| {{ apex_class }} | XML |

## Flows

| Flow | Fonte |
|---|---|
| {{ flow }} | XML |

## Custom Metadata Types

| Tipo | Fonte |
|---|---|
| {{ cmdt }} | XML |

## Record types

| Record type | Visível | Fonte |
|---|---|---|
| {{ record_type }} | {{ visible }} | XML |

## Principals de External Credential

| Principal | Fonte |
|---|---|
| {{ principal_name }} | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| {{ user_permission }} | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| {{ custom_permission }} | XML |

## Páginas Visualforce

| Página | Fonte |
|---|---|
| {{ apex_page }} | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| {{ tab }} | {{ tab_visibility }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
