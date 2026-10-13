# FlexCard (OmniUiCard): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ card_name }} | XML |
| IsActive | {{ is_active }} | XML |
| VersionNumber | {{ version_number }} | XML |
| Description | {{ description }} | XML |
| Tipo da fonte de dados | {{ data_source_type }} | XML |
| Fonte de dados | {{ data_source }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Ações

Ações do card como estão no JSON de configuração (o texto não é reproduzido).

| Ação | Tipo | Referências | Fonte |
|---|---|---|---|
| {{ action_label }} | {{ action_type }} | {{ action_refs }} | XML |

## Componentes referenciados

| Tipo | Componente | Elemento | Fonte |
|---|---|---|---|
| {{ ref_kind }} | {{ ref_name }} | {{ ref_element }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Quem pode executar as classes Apex referenciadas. O acesso aos dados vem da fonte de dados (DataRaptor ou Integration Procedure).

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
