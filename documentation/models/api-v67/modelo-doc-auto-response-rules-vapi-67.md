# Regras de resposta automática: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | {{ rules_object }} | XML |
| Situação | {{ active_check }} | Derivado |

## Regras

| Regra | Ativa | Outras configurações | Fonte |
|---|---|---|---|
| {{ rule_name }} | {{ rule_active }} | {{ rule_details }} | XML |

## Entradas (ordem de avaliação)

A plataforma avalia as entradas em ordem e para na primeira que casa; recomenda-se uma última entrada sem critério. Só uma regra de cada tipo fica ativa por objeto.

| Regra | Ordem | Critério | Lógica | Destino | Outras configurações | Fonte |
|---|---|---|---|---|---|---|
| {{ entry_rule }} | {{ entry_order }} | {{ entry_criteria }} | {{ entry_logic }} | {{ entry_destination }} | {{ entry_details }} | XML |

## Registros na org

| Id | Nome | Ativa | Fonte |
|---|---|---|---|
| {{ internal_rule_id }} | {{ internal_rule_name }} | {{ internal_rule_active }} | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
