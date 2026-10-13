# Perfil: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ profile_name }} | XML |
| UserLicense | {{ user_license }} | XML |
| Custom | {{ custom }} | XML |
| Description | {{ description }} | XML |

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

## Páginas Visualforce

| Página | Fonte |
|---|---|
| {{ apex_page }} | XML |

## Custom Permissions

| Custom Permission | Fonte |
|---|---|
| {{ custom_permission }} | XML |

## Record types

| Record type | Visível | Padrão | Fonte |
|---|---|---|---|
| {{ record_type }} | {{ visible }} | {{ rt_default }} | XML |

## Layouts de página

| Layout | Record type | Fonte |
|---|---|---|
| {{ layout }} | {{ layout_record_type }} | XML |

## Guias

| Guia | Visibilidade | Fonte |
|---|---|---|
| {{ tab }} | {{ tab_visibility }} | XML |

## Permissões de sistema

| Permissão | Fonte |
|---|---|
| {{ user_permission }} | XML |

## Horário de login

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ login_hours_key }} | {{ login_hours_value }} | XML |

## Faixas de IP de login

| Faixa (como no XML) | Fonte |
|---|---|
| {{ login_ip_range }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
