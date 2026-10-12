# Queueable Apex: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| ClassName | {{ class_name }} | XML |
| ApiVersion | {{ api_version }} | XML |
| Status | {{ status }} | XML |
| Descrição (ApexDoc) | {{ description }} | Código Apex |

## Capacidades do Queueable

| Propriedade | Valor | Fonte |
|---|---|---|
| Database.AllowsCallouts | {{ allows_callouts }} | Código Apex |
| Encadeia outro job no execute() | {{ supports_chaining }} | Código Apex |
| Finalizer anexado no execute() | {{ has_finalizer }} | Código Apex |
| Classe do Finalizer | {{ finalizer_class }} | Código Apex |
| Implementa System.Finalizer | {{ implements_finalizer }} | Código Apex |

## Parâmetros de entrada (construtores)

| Parâmetro | Tipo | Fonte |
|---|---|---|
| {{ param_name }} | {{ param_type }} | Código Apex |

## Encadeamento no execute()

| Classe alvo | Atraso (min) | Fonte |
|---|---|---|
| {{ target_class }} | {{ delay_minutes }} | Código Apex |

## Convenção de nomes

{{ naming_convention }}

## Referência

Limites de governança, formas de invocação e monitoramento: ver `documentation/referencia-apex-assincrono.md` (documentação oficial). Não são propriedades desta classe.

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |
