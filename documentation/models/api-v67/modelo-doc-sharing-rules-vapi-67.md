# Regras de compartilhamento: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Objeto | {{ sharing_object }} | XML |

## Regras por critério

| Regra | Rótulo | Acesso | Compartilhado com | Critérios | Lógica | Fonte |
|---|---|---|---|---|---|---|
| {{ rule_name }} | {{ rule_label }} | {{ rule_access }} | {{ rule_shared_to }} | {{ rule_criteria }} | {{ rule_logic }} | XML |

## Regras por proprietário

| Regra | Rótulo | Acesso | Compartilhado com | Registros de | Fonte |
|---|---|---|---|---|---|
| {{ rule_name }} | {{ rule_label }} | {{ rule_access }} | {{ rule_shared_to }} | {{ rule_shared_from }} | XML |

## Padrão de compartilhamento do objeto (OWD)

As regras só ampliam acesso a partir do padrão do objeto.

| Objeto | Interno (sharingModel) | Externo (externalSharingModel) | Fonte |
|---|---|---|---|
| {{ owd_object }} | {{ owd_internal }} | {{ owd_external }} | XML |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
