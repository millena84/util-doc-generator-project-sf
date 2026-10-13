# DataRaptor (OmniDataTransform): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ dr_name }} | XML |
| Tipo | {{ dr_type }} | XML |
| Entrada | {{ input_type }} | XML |
| Saída | {{ output_type }} | XML |
| IsActive | {{ is_active }} | XML |
| VersionNumber | {{ version_number }} | XML |
| Description | {{ description }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Itens de mapeamento

Itens na ordem do XML. A fórmula não é reproduzida, só se existe.

| Ordem | Objeto de entrada | Campo de entrada | Objeto de saída | Campo/caminho de saída | Filtro | Fórmula | Fonte |
|---|---|---|---|---|---|---|---|
| {{ item_order }} | {{ item_in_obj }} | {{ item_in_field }} | {{ item_out_obj }} | {{ item_out_field }} | {{ item_filter }} | {{ item_formula }} | XML |

## Objetos lidos

| Objeto | Fonte |
|---|---|
| {{ object_read }} | Derivado |

## Objetos gravados

| Objeto | Fonte |
|---|---|
| {{ object_written }} | Derivado |

## Quem usa

| Componente | Tipo | Elemento | Fonte |
|---|---|---|---|
| {{ caller_component }} | {{ caller_type }} | {{ caller_element }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Quem tem permissão nos objetos que o DataRaptor lê ou grava. Se o DataRaptor aplica ou não a segurança do usuário aparece nas configurações, como está no XML.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
