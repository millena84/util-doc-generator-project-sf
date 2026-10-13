# Lightning Web Component: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ComponentName | {{ component_api_name }} | XML |
| MasterLabel | {{ master_label }} | XML |
| ApiVersion | {{ api_version }} | XML |
| IsExposed | {{ is_exposed }} | XML |
| Description | {{ description }} | XML |

## Arquivos do bundle

| Arquivo | Tipo | Fonte |
|---|---|---|
| {{ bundle_file }} | {{ bundle_file_kind }} | Código LWC |

## Targets (onde o componente pode ser usado)

| Target | Uso | Fonte |
|---|---|---|
| {{ lwc_target }} | {{ lwc_target_label }} | XML |

## Propriedades configuráveis (targetConfigs)

| Targets | Propriedade | Tipo | Rótulo | Role | Obrigatória | Padrão | @api no JS | Fonte |
|---|---|---|---|---|---|---|---|---|
| {{ config_targets }} | {{ config_property }} | {{ config_type }} | {{ config_label }} | {{ config_role }} | {{ config_required }} | {{ config_default }} | {{ config_has_api }} | XML |

## Restrições por target

| Targets | Restrição | Valor | Fonte |
|---|---|---|---|
| {{ restriction_targets }} | {{ restriction_kind }} | {{ restriction_value }} | XML |

## Propriedades e métodos públicos (@api)

| Membro | Tipo | Fonte |
|---|---|---|
| {{ api_member }} | {{ api_kind }} | Código LWC |

## Ciclo de vida implementado

| Hook | Fonte |
|---|---|
| {{ lifecycle_hook }} | Código LWC |

## Métodos Apex chamados

| Classe | Método | Nome importado | Uso | Fonte |
|---|---|---|---|---|
| {{ called_class }} | {{ called_method }} | {{ called_import }} | {{ called_usage }} | Código LWC |

## Verificação nas classes Apex

Para ser chamado pelo LWC, o método precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, também `cacheable=true`. A verificação usa o código das classes processadas nesta execução.

| Classe | Método | @AuraEnabled | Modificadores | Verificação | Fonte |
|---|---|---|---|---|---|
| {{ apex_class }} | {{ apex_method }} | {{ aura_enabled }} | {{ method_modifiers }} | {{ apex_check }} | Código Apex |

## Dados do Salesforce usados

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| {{ data_kind }} | {{ data_name }} | {{ data_detail }} | Código LWC |

## Comunicação

| Tipo | Nome | Detalhe | Fonte |
|---|---|---|---|
| {{ comm_kind }} | {{ comm_name }} | {{ comm_detail }} | Código LWC |

## Permissões verificadas no código

| Tipo | Nome | Fonte |
|---|---|---|
| {{ perm_kind }} | {{ perm_name }} | Código LWC |

## Onde é usado (páginas Lightning)

Páginas Lightning (FlexiPage) processadas nesta execução que incluem o componente.

| Página | Tipo da página | Região | Identificador | Visibilidade condicional | Fonte |
|---|---|---|---|---|---|
| {{ usage_page }} | {{ usage_page_type }} | {{ usage_region }} | {{ usage_identifier }} | {{ usage_visibility }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

O LWC não tem acesso próprio por perfil ou permission set: aparece onde é colocado (páginas, ações, flows). As linhas mostram quem acessa as classes Apex chamadas e quem tem as Custom Permissions verificadas no código.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
