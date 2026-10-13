# Batch Apex: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | {{ class_name }} | XML |
| ApiVersion | {{ api_version }} | XML |
| Status | {{ status }} | XML |
| Descrição (ApexDoc) | {{ description }} | Código Apex |

## Capacidades do Batch

| Propriedade | Valor | Fonte |
|---|---|---|
| Tipo de escopo | {{ scope_type }} | Código Apex |
| Retorno do start() | {{ start_return_type }} | Código Apex |
| Database.Stateful | {{ is_stateful }} | Código Apex |
| Database.AllowsCallouts | {{ allows_callouts }} | Código Apex |
| Database.RaisesPlatformEvents | {{ raises_platform_events }} | Código Apex |
| Métodos do ciclo de vida | {{ lifecycle_methods }} | Código Apex |

## Consulta

| Propriedade | Valor | Fonte |
|---|---|---|
| Consulta do start() | {{ soql_query }} | Código Apex |
| Consulta dinâmica | {{ soql_dynamic }} | Código Apex |
| Objeto da consulta | {{ target_sobject }} | Código Apex |

## Encadeamento no finish()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| {{ call_kind }} | {{ target_class }} | {{ batch_size }} | Código Apex |

## Convenção de nomes

{{ naming_convention }}

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
