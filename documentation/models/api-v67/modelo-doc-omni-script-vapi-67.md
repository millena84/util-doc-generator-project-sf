# OmniScript: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ os_name }} | XML |
| Type | {{ proc_type }} | XML |
| SubType | {{ proc_subtype }} | XML |
| Type_SubType | {{ proc_key }} | Derivado |
| Language | {{ proc_language }} | XML |
| IsActive | {{ is_active }} | XML |
| VersionNumber | {{ version_number }} | XML |
| Description | {{ description }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Elementos

Elementos na ordem do XML. A configuração de cada elemento não é reproduzida: só os componentes que ela referencia.

| Ordem | Elemento | Tipo | Nível | Elemento pai | Ativo | Referências | Fonte |
|---|---|---|---|---|---|---|---|
| {{ el_order }} | {{ el_name }} | {{ el_type }} | {{ el_level }} | {{ el_parent }} | {{ el_active }} | {{ el_refs }} | XML |

## Componentes referenciados

| Tipo | Componente | Elemento | Fonte |
|---|---|---|---|
| {{ ref_kind }} | {{ ref_name }} | {{ ref_element }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Quem pode executar as classes Apex chamadas (Remote Action). O acesso ao formulário vem de onde ele é colocado (página, site, FlexCard).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
