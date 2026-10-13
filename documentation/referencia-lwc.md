# Referência: Lightning Web Components

Conteúdo **genérico da plataforma** (ciclo de vida, comunicação, Lightning Data Service e APIs de plataforma), que vale para qualquer componente. Por isso ele não aparece como propriedade nos documentos gerados por componente (`modelo-doc-lwc*`), que só mostram fatos extraídos do bundle, do metadata e das classes Apex processadas.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-lwc.md` (material de referência, não normativo). O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13): os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- XML Configuration File Elements: <https://developer.salesforce.com/docs/platform/lwc/guide/reference-configuration-tags.html>
- Configure a Component for Flow Screens: <https://developer.salesforce.com/docs/platform/lwc/guide/use-config-for-flow-screens.html>
- Configure a Component for Quick Actions: <https://developer.salesforce.com/docs/platform/lwc/guide/use-config-for-quick-actions.html>
- Create Headless Quick Actions: <https://developer.salesforce.com/docs/platform/lwc/guide/use-quick-actions-headless.html>
- lightning__RecordAction Target: <https://developer.salesforce.com/docs/platform/lwc/guide/targets-lightning-record-action.html>
- Wire Apex Methods to Components: <https://developer.salesforce.com/docs/platform/lwc/guide/apex-wire-method.html>
- Secure Apex Classes: <https://developer.salesforce.com/docs/platform/lwc/guide/apex-security.html>
- Permissions (`@salesforce/customPermission`): <https://developer.salesforce.com/docs/platform/lwc/guide/create-get-permissions.html>
- `@salesforce` Modules: <https://developer.salesforce.com/docs/platform/lwc/guide/reference-salesforce-modules.html>
- Metadata API `LightningComponentBundle`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_lightningcomponentbundle.htm>
- Metadata API `LightningMessageChannel`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_lightningmessagechannel.htm>

## Configuração (`.js-meta.xml`)

| Tema | Referência | Situação |
|---|---|---|
| `apiVersion` | 45.0 ou superior; LDS e componentes base usam sempre a versão mais recente | confirmado |
| `targets` | onde o componente pode ser usado (ex.: `lightning__RecordPage`, `lightning__AppPage`, `lightning__HomePage`, `lightningCommunity__Page`) | confirmado |
| `property role` (Flow Screen) | `inputOnly` ou `outputOnly`; sem `role`, entrada e saída | confirmado |
| `property name` | precisa corresponder a uma propriedade `@api` do JS | confirmado |
| `actionType` (Quick Action) | `ScreenAction` (modal) ou `Action` (headless); ausente = `ScreenAction`; não pode ser trocado depois | confirmado |
| Propriedades em `lightning__RecordAction` | não suportadas | confirmado |

- **Correção do `ajudAI`:** o exemplo usa `role="inputOutput"`, valor que não existe. O documento mostra "entrada e saída (role ausente)" quando o atributo não é declarado.

## Quick Action headless

- O JS precisa de um método público `@api invoke()`; a plataforma o chama a cada execução (confirmado).
- Não dependa de hooks de ciclo de vida para executar a ação; `recordId` não chega no `connectedCallback()` (confirmado).
- A ação não impede duplo clique: a documentação sugere um flag interno (confirmado). LWC Quick Actions não são suportadas no app móvel (confirmado).

## Apex chamado pelo componente

- O método precisa ser `static`, `public` ou `global` e ter `@AuraEnabled`; com `@wire`, `@AuraEnabled(cacheable=true)` (confirmado). Chamadas imperativas podem usar `cacheable=true` opcionalmente.
- O usuário só chama um método `@AuraEnabled` se o perfil ou um permission set dele der acesso à classe Apex (confirmado).
- Trate todo método `@AuraEnabled` como endpoint: valide entradas e aplique permissões de objeto e campo no Apex (confirmado; recomendação).

## Ciclo de vida

| Hook | Momento | Uso |
|---|---|---|
| `constructor()` | criação | inicializar estado; não acessar o DOM |
| `connectedCallback()` | inserido no DOM | carregar dados, assinar canais |
| `renderedCallback()` | após cada renderização | integração com bibliotecas que mexem no DOM |
| `disconnectedCallback()` | removido do DOM | limpar timers e assinaturas |
| `errorCallback(error, stack)` | erro em componente filho | tratamento de erro (*error boundary*) |

Conteúdo do `ajudAI`, *a confirmar* na página de ciclo de vida.

## Comunicação

- Pai → filho: propriedades e métodos `@api`.
- Filho → pai: `CustomEvent` (`bubbles`, `composed` controlam a propagação).
- Sem relação: Lightning Message Service (`lightning/messageService` + `LightningMessageChannel`). Por padrão a comunicação vale na guia/item de navegação ativo ou no item de utilitário; `APPLICATION_SCOPE` amplia para o app (confirmado).
- **Rejeitado do `ajudAI`:** "apenas perfis e permission sets com acesso liberado ao canal podem publicar/assinar". Não foi encontrada documentação de acesso a message channel por perfil/permission set; `isExposed` do canal controla o uso por outros namespaces (confirmado).

## Segurança e dados

- Lightning Data Service (`lightning/ui*Api`, `lightning-record-*-form`) respeita CRUD, FLS e compartilhamento; o comportamento exato quando falta acesso a um campo (ocultar ou erro) está *a confirmar*.
- `@salesforce/customPermission/<Nome>` retorna `true` se o usuário tem a permissão, senão `undefined`; permissão de pacote usa `ns__Nome` (confirmado).
- `lightning/platformWorkspaceApi` e `lightning/utilityBarApi`: *a confirmar*.

## O que o documento por componente mostra

| Informação | Fonte |
|---|---|
| `masterLabel`, `apiVersion`, `isExposed`, `description`, targets, `targetConfigs` | `XML` (`.js-meta.xml`) |
| Arquivos, `@api`, hooks, Apex importado, dados usados, comunicação, permissões importadas | `Código LWC` |
| `@AuraEnabled`, `cacheable`, `static`, `public/global` dos métodos chamados | `Código Apex` (classes processadas na execução) |
| Registro `LightningComponentBundle` | `Objeto interno` (Tooling, `validationPending`) |
| Perfis/permission sets das classes chamadas e das Custom Permissions | `XML` (passo 6b) |
| Páginas Lightning que usam o componente | `XML` das FlexiPages processadas (Onda 04) |
