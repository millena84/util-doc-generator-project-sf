# Página Lightning (FlexiPage): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ page_name }} | XML |
| MasterLabel | {{ master_label }} | XML |
| Type | {{ page_type }} | XML |
| SobjectType | {{ sobject_type }} | XML |
| Template | {{ template }} | XML |
| Description | {{ description }} | XML |
| ParentFlexiPage | {{ parent_page }} | XML |

## Regiões

| Região | Tipo | Modo | Itens | Fonte |
|---|---|---|---|---|
| {{ region_name }} | {{ region_type }} | {{ region_mode }} | {{ region_items }} | XML |

## Componentes

| Região | Componente | Identificador | Tipo | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| {{ comp_region }} | {{ comp_name }} | {{ comp_identifier }} | {{ comp_kind }} | {{ comp_visibility }} | XML |

## Campos (Dynamic Forms)

| Região | Campo | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|
| {{ field_region }} | {{ field_item }} | {{ field_identifier }} | {{ field_visibility }} | XML |

## Propriedades dos componentes

| Identificador | Componente | Propriedade | Valor | Fonte |
|---|---|---|---|---|
| {{ prop_identifier }} | {{ prop_component }} | {{ prop_name }} | {{ prop_value }} | XML |

## Visibilidade condicional

Regra de visibilidade só esconde o componente na página; não substitui permissão de objeto, campo ou classe.

| Identificador | Contexto | Campo/variável | Operador | Valor | Lógica | Fonte |
|---|---|---|---|---|---|---|
| {{ vis_identifier }} | {{ vis_context }} | {{ vis_left }} | {{ vis_operator }} | {{ vis_right }} | {{ vis_logic }} | XML |

## Flows embarcados

| Flow | Fonte |
|---|---|
| {{ page_flow }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Onde a página está ativada (padrão da org, padrão do app, app + perfil/record type) e quem tem as Custom Permissions usadas nas regras de visibilidade. Página não ativada não aparece para o usuário.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
