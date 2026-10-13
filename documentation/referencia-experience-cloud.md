# Referência: Experience Cloud

Conteúdo **genérico da plataforma** sobre sites do Experience Cloud (Network, CustomSite e ExperienceBundle). Ele vale para qualquer org, por isso não aparece como propriedade nos documentos gerados (`modelo-doc-network`, `-custom-site`, `-experience-bundle`). Esses documentos só mostram o que está no XML/JSON, nos dados internos e nos componentes recuperados.

> **Origem:** adaptado de `_sf_utilities/ajudAI/contexto-doc-experience-cloud.md` (Onda 09), na versão `ca067b0` do repositório `millena84/_sf_utilities`. É material de referência, não normativo.
>
> O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13). Nenhum item abaixo foi conferido na página oficial nesta adaptação: os itens *a confirmar* ficam para o piloto (`piloto-org-real.md`, fase C9).

## Fontes oficiais

- Metadata API `Network`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_network.htm>
- Metadata API `CustomSite`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_customsite.htm>
- Metadata API `ExperienceBundle`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_experiencebundle.htm>
- Metadata API `SharingRules` (regras para convidado): <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_sharingrules.htm>
- Object Reference `Network`: <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_network.htm>

## 9.1 Site do Experience Cloud (`Network`)

| Tema | Situação |
|---|---|
| Tríade Network + CustomSite + ExperienceBundle forma o site no formato source | *a confirmar* |
| `networkMemberGroups` com `profile` e `permissionSet` define quem entra no site | *a confirmar*; o utilitário lê os dois e mostra outros filhos pelo nome do elemento |
| `status` (`Live`, `UnderConstruction`, `Inactive`...), `selfRegistration`, `selfRegProfile`, `urlPathPrefix`, `site` | *a confirmar*; ausentes ficam "Não informado" |
| `<label>` na Network | *a confirmar* (presente só no exemplo do `ajudAI`) |
| `<emailSenderEmail>` | **não usado**: nome não confirmado (o utilitário também omite `emailSenderAddress`/`emailSenderName`). O remetente nunca é documentado, só se está configurado |
| Templates de e-mail (`welcomeTemplate`, `forgotPasswordTemplate`...) | lidos como folhas `*Template` do XML |

## 9.2 Site (`CustomSite`) e convidado

| Tema | Situação |
|---|---|
| `active`, `urlPathPrefix`, `subdomain`, `siteType`, `masterLabel` | *a confirmar*; folhas do XML como estão |
| `siteAdmin` e `siteGuestRecordDefaultOwner` são usuários | **nunca documentados**: o documento só diz se estão configurados |
| Perfil de convidado no XML (`guestProfile`) | *a confirmar*. O `ajudAI` cita o perfil `<site> Profile` criado automaticamente; o utilitário **não deduz** o nome: sem `guestProfile`, a tabela fica "Não informado" |
| "Convidado só pode ter Ler/Criar" (sem Editar/Excluir/Ver todos/Modificar todos) | *a confirmar*. O documento marca "Revisar = Sim" quando o perfil concede algo além de Ler/Criar; não afirma que a plataforma bloqueia |
| OWD externo obrigatoriamente privado para convidado | *a confirmar*; o OWD aparece no documento do objeto e no de regras de compartilhamento |
| Regras para convidado (`sharingGuestRules` com `sharedTo/guestUser`) | *a confirmar* (elemento e valor de `guestUser`). O documento do site lista as regras cujo `guestUser` é o nome do site |

## 9.3 Experience Builder (`ExperienceBundle`)

| Tema | Situação |
|---|---|
| Pasta `experiences/<site>/` com `config/`, `views/`, `routes/`, `themes/` (JSON) e `experiences/<site>.site-meta.xml` | *a confirmar*; o utilitário conta os JSON de cada subpasta e lê só `views` e `routes` |
| View: `id`, `label`, `componentName` (layout), `regions` → `components` (`componentName`, `id`, `type`) | *a confirmar*; regiões aninhadas são percorridas |
| Rota: `urlPrefix`, `pageAccess` (ex.: `Public`, `RequiresLogin`), `activeViewId`, `routeType` | *a confirmar*; ausentes ficam "Não informado"; `""` aparece como `(vazio)` |
| Audiências (*Audience Targeting*) e seus critérios (`User.Account.Rating = 'Hot'`...) | **não interpretados**: só as chaves com `audience`/`visibility` nos componentes aparecem, com o valor como está |
| `templateType` Aura/LWR | **não deduzido**: o documento mostra o `<type>` do `.site-meta.xml` como está |
| `DigitalExperienceBundle` (sites LWR aprimorados, `digitalExperiences/`) | **fora do escopo** desta onda |
| LWC das páginas dependem do acesso às classes Apex chamadas | adotado: a seção de acesso lista quem executa as classes importadas pelos LWC `c:*` processados |

## O que os documentos mostram

| Documento | Mostra | Fonte |
|---|---|---|
| Site do Experience Cloud (Network) | Status, URL, autorregistro, templates, CustomSite, membros | XML, Objeto interno |
| Site (CustomSite) | URL, tipo, configurações, Network, usuários (só se configurados), permissões de objeto do perfil de convidado, regras para convidado | XML, Objeto interno |
| Experience Builder (ExperienceBundle) | Pastas, views, rotas e acesso às páginas, componentes por página, público/visibilidade, quem executa as classes Apex dos LWC | XML, JSON do ExperienceBundle |
| LWC | Páginas do Experience Cloud que usam o componente | JSON do ExperienceBundle |
