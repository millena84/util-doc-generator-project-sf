# Referência: Service Cloud (regras de atendimento e filas)

Conteúdo **genérico da plataforma** sobre regras de atribuição, resposta automática e escalonamento e sobre filas. Ele vale para qualquer org, por isso não aparece como propriedade nos documentos gerados (`modelo-doc-assignment-rules`, `-auto-response-rules`, `-escalation-rules`, `-queue`). Esses documentos só mostram o que está no XML, nos dados internos e nos componentes processados.

> **Origem (Onda 07):** não há `contexto-*.md` desta onda no `ajudAI`. A referência usada foram os prompts de `_sf_utilities/tools/templates/exemplos-prompts/`:
> - detalhados: `prompt-assignment-rules.md` e `prompt-escalation-rules.md`;
> - só esboço: `prompt-auto-response-rules.md`, `prompt-queue.md` e `prompt-case-settings.md`.
>
> O acesso direto a developer.salesforce.com e a help.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13). Os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Metadata API `AssignmentRules`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_assignmentrule.htm>
- Metadata API `AutoResponseRules`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_autoresponserules.htm>
- Metadata API `EscalationRules`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_escalationrules.htm>
- Metadata API `Queue`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_queue.htm>
- `QueueSobject`: <https://developer.salesforce.com/docs/atlas.en-us.sfFieldRef.meta/sfFieldRef/salesforce_field_reference_QueueSobject.htm>
- `QueueRoutingConfig`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_queueroutingconfig.htm>
- Guidelines for Assignment Rules: <https://help.salesforce.com/s/articleView?id=customize_leadrules.htm&language=en_US&type=5>
- Escalation Rule Entries: <https://help.salesforce.com/s/articleView?language=en_US&id=service.rules_escalation_rule_entry.htm&type=5>
- Limits for Assignment, Auto-Response, and Escalation Rules: <https://help.salesforce.com/apex/HTViewHelpDoc?id=sf.rules_limits.htm>
- Assignment Rule Header (API): <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/headers_autoassign.htm>

## Regras de atendimento

| Tema | Situação |
|---|---|
| `AssignmentRules` direciona casos (e leads) automaticamente para usuários ou filas | confirmado |
| `AutoResponseRules` envia e-mail automático para lead ou caso conforme os atributos do registro | confirmado |
| `EscalationRules` escalona casos não resolvidos no prazo | confirmado |
| O metadata pode ser recuperado para todos os objetos, para um objeto ou para uma regra de um objeto | confirmado |
| Só uma regra de cada tipo fica ativa por vez (por objeto) | confirmado |
| As entradas são avaliadas em ordem; a avaliação para na primeira que casa | confirmado |
| Recomenda-se uma última entrada sem critério; no escalonamento, as entradas mais complexas vêm primeiro | confirmado |
| Até 3.000 entradas por regra; até 50 regras ativas por objeto, somando workflow, atribuição, resposta automática, escalonamento e processos | confirmado |
| Nomes dos elementos internos (`ruleEntry`, `criteriaItems`, `assignedTo`, `assignedToType`, `escalationAction`, `minutesToEscalation`, `notifyTo`...) | *a confirmar*. Vêm dos prompts; o parser os lê de forma genérica e mostra as demais folhas como `nome=valor` |
| Invocar regra de atribuição via Apex/API (`Database.DMLOptions`, Assignment Rule Header) | confirmado (cabeçalho da API); não é propriedade do documento |

## Filas

| Tema | Situação |
|---|---|
| Fila é uma área de espera de itens antes do processamento | confirmado |
| `QueueSobject` mapeia a fila para os objetos que ela aceita, inclusive customizados | confirmado |
| `QueueRoutingConfig` guarda o roteamento de trabalho para agentes (Omni-Channel) | confirmado |
| Elementos de membros (`queueMembers` com `users`, `roles`, `publicGroups`...) | *a confirmar*. O parser lê qualquer contêiner dentro de `queueMembers` |

## Proteção de dados

Os documentos desta onda **nunca** mostram:
- o usuário de destino (`assignedTo` quando o tipo é `User`); no lugar aparece "usuário (não documentado)";
- usuários notificados e e-mails de notificação, remetente, resposta e da fila; no lugar aparece só a contagem;
- usuários membros de fila; aparece só a contagem.

Os nomes desses elementos também estão em `omitFromDocumentation` (config) como barreira adicional. Filas, papéis e grupos (destinos e membros) aparecem, porque não são dados pessoais.

## Fora do escopo desta onda (sem referência)

Omni-Channel (`ServiceChannel`, `RoutingConfiguration`/`QueueRoutingConfig` como documento próprio, `PresenceUserConfig`), Entitlements e Milestones (`EntitlementProcess`, `MilestoneType`), `CaseSettings`/`EmailToCaseSettings` (podem conter usuários e e-mails), Knowledge e Embedded Service. Entram numa onda futura, se houver referência.
