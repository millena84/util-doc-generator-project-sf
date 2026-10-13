# Modelo de territórios: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ model_name }} | XML |

## Configurações do modelo

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Territórios

Territórios do modelo. Usuários atribuídos aos territórios não são documentados.

| Território | Rótulo | Tipo | Território pai | Acesso a contas | Acesso a oportunidades | Acesso a casos | Regras associadas | Fonte |
|---|---|---|---|---|---|---|---|---|
| {{ territory }} | {{ territory_label }} | {{ territory_type }} | {{ parent_territory }} | {{ account_access }} | {{ opportunity_access }} | {{ case_access }} | {{ rule_associations }} | XML |

## Regras de atribuição

| Regra | Ativa | Objeto | Lógica | Critérios | Fonte |
|---|---|---|---|---|---|
| {{ rule }} | {{ rule_active }} | {{ rule_object }} | {{ rule_logic }} | {{ rule_items }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Quem pode gerenciar territórios. O acesso aos registros vem dos níveis de acesso de cada território.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
