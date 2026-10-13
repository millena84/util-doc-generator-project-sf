# Scheduled Apex: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | {{ class_name }} | XML |
| ApiVersion | {{ api_version }} | XML |
| Status | {{ status }} | XML |
| Descrição (ApexDoc) | {{ description }} | Código Apex |

## Capacidades do Schedulable

| Propriedade | Valor | Fonte |
|---|---|---|
| Delega para Batch/Queueable | {{ delegates }} | Código Apex |
| Classes delegadas | {{ delegated_classes }} | Código Apex |

## Jobs disparados no execute()

| Chamada | Classe alvo | Tamanho do lote | Fonte |
|---|---|---|---|
| {{ call_kind }} | {{ target_class }} | {{ batch_size }} | Código Apex |

## Agendamentos feitos pela própria classe

| Nome do job | Expressão cron | Classe alvo | Fonte |
|---|---|---|---|
| {{ job_name }} | {{ cron_expression }} | {{ target_class }} | Código Apex |

## Convenção de nomes

{{ naming_convention }}

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |
