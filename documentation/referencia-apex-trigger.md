# Referência: Apex Trigger

Conteúdo **genérico da plataforma** (variáveis de contexto, ordem de execução, modo de acesso e boas práticas), que vale para qualquer trigger. Por isso ele não aparece como propriedade no documento gerado por trigger (`modelo-doc-apex-trigger`), que só mostra fatos extraídos do código, do metadata e dos componentes recuperados.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-apex-trigger.md` (material de referência, não normativo). O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13): os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Triggers and Order of Execution: <https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_triggers_order_of_execution.htm>
- Trigger Context Variables / classe `Trigger`: <https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_System_Trigger.htm>
- Metadata API `ApexTrigger`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_triggers.htm>
- Objeto `ApexTrigger` (Object Reference): <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apextrigger.htm>
- Ordem de triggers e regras de automação: <https://help.salesforce.com/s/articleView?id=000005694&language=en_US&type=1>
- Ordem entre record-triggered flows: <https://help.salesforce.com/s/articleView?id=sf.flow_task_trigger_run_order.htm&language=en_US>
- Before-save flows: <https://help.salesforce.com/s/articleView?id=platform.flow_concepts_trigger_record.htm&language=en_US&type=5>
- Mudanças de comportamento por versão do Apex: <https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/versioned_behavior_changes.htm>

## Ordem de execução (insert/update)

| Ordem | Automação | Situação |
|---|---|---|
| 1 | Record-triggered flows before-save | confirmado: rodam imediatamente antes das triggers before |
| 2 | Triggers Apex before | confirmado |
| 3 | Regras de validação customizadas (e a maior parte das validações de sistema de novo) | confirmado (Apex Developer Guide) |
| 4 | Triggers Apex after | confirmado |
| 5 | Record-triggered flows after-save | confirmado (depois das triggers after) |

- **Correção do `ajudAI`:** a matriz da seção 4 coloca a trigger before em 1º e o flow before-save em 2º. A ordem oficial é a inversa.
- Entre triggers do **mesmo objeto e evento**, a ordem **não é garantida** e não pode ser controlada.
- Entre record-triggered flows do mesmo objeto: `triggerOrder` de 1 a 1000 em ordem crescente, depois os sem valor, depois 1001 a 2000; empate pelo nome de API. Um flow não passa à frente de um before-save flow nem de uma trigger.
- Etapas intermediárias (regras de duplicidade, atribuição, auto-resposta, workflow, escalonamento, roll-up) *a confirmar* na página oficial; não entram no documento por trigger.
- Exclusão e restauração (`before/after delete`, `after undelete`, flow before-delete): posição relativa *a confirmar*. O documento mostra essas fases com ordem "Não confirmado".

## Variáveis de contexto

| Variável | Uso |
|---|---|
| `Trigger.isExecuting`, `isInsert`, `isUpdate`, `isDelete`, `isUndelete`, `isBefore`, `isAfter` | Boolean do contexto atual |
| `Trigger.new` / `Trigger.newMap` | registros novos (insert, update, undelete); `new` só é alterável em `before` |
| `Trigger.old` / `Trigger.oldMap` | valores anteriores (update, delete) |
| `Trigger.operationType` | enum `System.TriggerOperation` (ex.: `BEFORE_INSERT`) |
| `Trigger.size` | quantidade de registros no lote |

*A confirmar*: disponibilidade exata de `newMap` por evento e o tamanho máximo de lote citado no `ajudAI` (200).

## Modo de acesso e segurança

- **Correção do `ajudAI`:** "a trigger executa em System Mode, ignorando CRUD e FLS" não vale para todas as versões. A página *Apex Versioned Behavior Changes* indica que, **a partir da API 67.0, o Apex roda em user mode por padrão** (permissões e FLS do usuário aplicados); na API 66.0 e anteriores, system mode é o padrão. Como isso se aplica a triggers e classes chamadas com `apiVersion` diferentes está *a confirmar*. O documento mostra a `apiVersion` da trigger e os controles explícitos encontrados no código (`WITH USER_MODE`, `WITH SYSTEM_MODE`, `AccessLevel`, `Security.stripInaccessible`, describe).
- **Triggers não têm acesso próprio por perfil/permission set**: a segurança de classe Apex vale para classes, não para triggers. O documento lista quem tem acesso ao objeto e às classes chamadas, mas acesso a classe não impede a trigger de chamar a classe (a verificação é no ponto de entrada).

## Boas práticas citadas no `ajudAI` (não verificadas pelo utilitário)

| Prática | Por que não é propriedade do documento |
|---|---|
| Uma linha na trigger, lógica no handler | convenção de arquitetura; o documento mostra as classes chamadas, não julga |
| Bulkificação (sem SOQL/DML em laço) | não comprovável por leitura estática confiável |
| Controle de recursão (variável estática, conjunto de Ids) | idem |
| Mecanismos de bypass (Custom Permission, Custom Setting hierárquico, Custom Metadata) | o documento mostra as **leituras** desses componentes; se desativam a lógica depende do código |

## O que o documento por trigger mostra

| Informação | Fonte |
|---|---|
| `apiVersion`, `status` | `XML` (`.trigger-meta.xml`) |
| Objeto, eventos, variáveis de contexto, classes chamadas, leituras de configuração, controles de segurança | `Código Apex` (`.trigger` e `.cls` das classes chamadas processadas) |
| Coexistência no objeto e ordem | `Derivado` (Flows, regras de validação e triggers processados na execução) |
| `TableEnumOrId`, `Usage*`, `IsValid` | `Objeto interno` (`validationPending`) |
| Perfis/permission sets do objeto e das classes chamadas | `XML` (passo 6b) |
