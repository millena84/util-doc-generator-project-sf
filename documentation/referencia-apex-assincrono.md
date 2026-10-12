# Referência: Apex assíncrono

Conteúdo **genérico da plataforma** (limites, formas de invocação, monitoramento e boas práticas) que vale para qualquer classe do mesmo tipo. Por isso ele não aparece como propriedade nos documentos gerados por classe (`modelo-doc-apex-*`), que só mostram fatos extraídos do código e do metadata daquela classe.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-apex.md` (material de referência, não normativo). Limites mudam entre releases: **confira sempre a página oficial da versão em uso** antes de decidir com base neles. Itens marcados *a confirmar* não foram verificados na documentação oficial nesta adaptação.

## Fontes oficiais

- Batch Apex: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_batch_interface.htm>
- Eventos de plataforma em Batch (`Database.RaisesPlatformEvents`, `BatchApexErrorEvent`): <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_batch_platformevents.htm>
- Queueable Apex: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_queueing_jobs.htm>
- Transaction Finalizers: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_transaction_finalizers.htm>
- Future Methods: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_invoking_future_methods.htm>
- Scheduled Apex: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_scheduler.htm>
- Limites de execução (Execution Governors and Limits): <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm>
- Metadata API `ApexClass`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_classes.htm>

## Batch Apex (`Database.Batchable`)

| Tema | Referência | Situação |
|---|---|---|
| Métodos | `start`, `execute`, `finish` | Apex Developer Guide |
| Escopo do `start()` | `Database.QueryLocator` (até 50 milhões de registros) ou `Iterable` | a confirmar (limite) |
| Tamanho do lote | padrão 200; até 2.000 com `QueryLocator` (`Database.executeBatch(job, n)`) | a confirmar |
| `Database.Stateful` | mantém variáveis de instância entre lotes (serializa o estado a cada lote) | Apex Developer Guide |
| `Database.AllowsCallouts` | libera callouts | a confirmar (página própria) |
| `Database.RaisesPlatformEvents` | publica `BatchApexErrorEvent` em exceção não tratada (API 44+) | confirmado |
| Fila e concorrência | até 100 jobs em *Holding* na Flex Queue; até 5 em processamento simultâneo | a confirmar |
| Monitoramento | `AsyncApexJob` (`Status`, `NumberOfErrors`, `JobItemsProcessed`, `TotalJobItems`) | a confirmar |

## Queueable Apex (`System.Queueable`)

| Tema | Referência | Situação |
|---|---|---|
| Método | `execute(QueueableContext context)` | Apex Developer Guide |
| Atraso | `System.enqueueJob(job, delayInMinutes)` (0 a 10 minutos) | a confirmar |
| Enfileiramentos | até 50 `System.enqueueJob` por transação síncrona; 1 a partir de um job assíncrono | a confirmar |
| Profundidade de encadeamento | sem limite padrão em produção; contexto de teste limita o encadeamento | a confirmar (o `ajudAI` cita "1 nível em Developer Org", **não confirmado**) |
| Finalizer | `System.attachFinalizer(finalizer)` é chamado **dentro do `execute()`** do Queueable; um finalizer por job; pode re-enfileirar até 5 vezes em falha | confirmado (o exemplo do `ajudAI`, que anexa antes do `enqueueJob`, está **incorreto**) |

## Future Method (`@future`)

| Tema | Referência | Situação |
|---|---|---|
| Assinatura | `static void`; parâmetros só primitivos ou coleções de primitivos (sem sObjects) | Apex Developer Guide |
| Callout | `@future(callout=true)` | Apex Developer Guide |
| Restrições | sem ordem garantida de execução; um `@future` não chama outro `@future` | a confirmar |
| Limite | até 50 chamadas `@future` por transação | a confirmar |

## Scheduled Apex (`System.Schedulable`)

| Tema | Referência | Situação |
|---|---|---|
| Método | `execute(SchedulableContext sc)` | Apex Developer Guide |
| Agendamento | `System.schedule(nomeDoJob, expressãoCron, instância)` | Apex Developer Guide |
| Expressão cron | `Segundos Minutos Horas Dia_do_mês Mês Dia_da_semana [Ano]` (ex.: `0 0 1 * * ?`, diário à 01:00) | Apex Developer Guide |
| Boa prática | o `execute()` delega o trabalho pesado a um Batch ou Queueable | recomendação, não regra da plataforma |
| Monitoramento | `CronTrigger` (`CronExpression`, `State`, `NextFireTime`) e `CronJobDetail.Name` | a confirmar |

## O que os documentos por classe mostram

| Informação | Onde aparece |
|---|---|
| Interfaces, sharing, assinaturas, anotações, SOQL literal do `start()`, finalizer, encadeamento e delegação | documento da classe e subdocumentos por papel (fonte `Código Apex`) |
| `apiVersion` e `status` | documento da classe (fonte `XML`, `.cls-meta.xml`) |
| Tamanho de lote, cron e nome do job usados por **outras** classes | próxima entrega (índice entre classes) |
| Agendamentos e execuções reais na org (`CronTrigger`, `AsyncApexJob`) | entrega de dados internos, após o piloto |
