# Referência: páginas Lightning (FlexiPage)

Conteúdo **genérico da plataforma** (tipos de página, templates, ativação e regras de visibilidade), que vale para qualquer página. Por isso ele não aparece como propriedade no documento gerado (`modelo-doc-flexipage`), que só mostra o que está no XML da página, nos dados internos e nos componentes que a ativam.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-flexipage.md` (material de referência, não normativo; Onda 04). O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13): os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Metadata API `FlexiPage`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_flexipage.htm>
- Tooling API `FlexiPage`: <https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/tooling_api_objects_flexipage.htm>
- Activate Lightning Record or Home Pages: <https://help.salesforce.com/s/articleView?id=lightning_app_builder_customize_lex_pages_activate.htm&language=en_US>
- Visibility Rules on Lightning Pages: <https://help.salesforce.com/s/articleView?id=platform.lightning_page_components_visibility.htm&language=en_US&type=5>
- `sf template generate flexipage` (tipos RecordPage, AppPage, HomePage): <https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_template_generate_flexipage.html>
- Ativação e `actionOverrides` em pacotes (blog Salesforce Developers): <https://developer.salesforce.com/blogs/2018/06/working-with-modular-development-and-unlocked-packages-part-2>

## Tipos de página

| Tipo | Uso | Situação |
|---|---|---|
| `RecordPage` | sobrescreve a página de registro de um objeto (exige objeto) | confirmado |
| `AppPage` | página inicial de um app ou página avulsa de app | confirmado |
| `HomePage` | sobrescreve a página inicial no Lightning Experience | confirmado |
| `UtilityBar`, `CommAppPage` e demais | *a confirmar* | o documento mostra o `type` do XML |

Templates "recomendados" do `ajudAI` (ex.: `flexipage:defaultRecordHomeTemplate`) não foram confirmados; o documento mostra o template do XML.

## Ativação

| Nível | Onde fica no metadata | Situação |
|---|---|---|
| Padrão da org | `actionOverrides` (ação View) no `.object-meta.xml` | confirmado |
| Padrão do app | `actionOverrides` no `.app-meta.xml`; tem precedência sobre o override da org naquele app | confirmado |
| App + record type + perfil | no app (`profileActionOverrides`); record type só em página de registro | nível confirmado; elemento *a confirmar* |

- **Correção do `ajudAI`:** "Profile guarda a atribuição da Flexipage em ativadores de página" não foi confirmado. O utilitário lê a atribuição por perfil do XML do app.
- Ao implantar objetos com esse `actionOverrides`, a FlexiPage referenciada precisa ir junto (confirmado).
- Uma página que não está ativada em nenhum nível não aparece para o usuário.

## Regras de visibilidade

- Em páginas de registro, filtros podem usar campos do registro (inclusive de objetos relacionados) ou do usuário. Em páginas de app e home, só contextos como User, User Permission e Device (confirmado).
- Operadores: contém, igual, diferente e comparações (confirmado). Campos e seções do Dynamic Forms também aceitam visibilidade (confirmado).
- Custom Permission de pacote gerenciado pode não funcionar na visibilidade; o contorno documentado é criar a permissão na org (confirmado, *known issue*).
- A sintaxe exata de `leftValue` no XML (`{!Record.Campo}`, `{!$User...}`, `{!$Permission.CustomPermission.X}`) está *a confirmar*; o parser aceita com ou sem `{!`/`$`.
- **Esclarecimento ao `ajudAI`:** o que o arquivo chama de "bypass" por visibilidade (por perfil, Custom Permission ou dispositivo) só mostra ou esconde o componente na página. Não é controle de acesso: dados e ações continuam protegidos pelas permissões de objeto, campo e classe.

## O que o documento mostra

| Informação | Fonte |
|---|---|
| Tipo, objeto, template, regiões, componentes, propriedades, campos, visibilidade, Flows | `XML` (`.flexipage-meta.xml`) |
| Ativação: padrão da org, padrão do app, app + perfil | `XML` do CustomObject processado e do CustomApplication (passo 6b) |
| Quem tem as Custom Permissions da visibilidade | `XML` (passo 6b) |
| Registro `FlexiPage` | `Objeto interno` (Tooling, `validationPending`) |
| Páginas que usam um LWC | documento do LWC, seção "Onde é usado (páginas Lightning)" |
