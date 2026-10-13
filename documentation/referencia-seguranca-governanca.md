# Referência: segurança, acesso e governança

Conteúdo **genérico da plataforma** (modelo de compartilhamento, hierarquia de papéis, permission sets e muting, políticas da org), que vale para qualquer org. Por isso ele não aparece como propriedade nos documentos gerados (`modelo-doc-org-security`, `-profile`, `-permission-set`, `-permission-set-group`, `-sharing-rules`, `-role`, `-public-group`), que só mostram o que está no XML recuperado, nos dados internos ou nos componentes processados na execução.

> Origem: adaptado de `_sf_utilities/ajudAI/contexto-seg-controle-acesso-gov.md` (material de referência, não normativo; Onda 05). O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13): os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Metadata API `SecuritySettings`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_securitysettings.htm>
- Metadata API `Settings`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_settings.htm>
- Metadata API `Profile`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_profile.htm>
- Metadata API `ProfileSessionSetting`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_profilesessionsetting.htm>
- Metadata API `PermissionSet`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_permissionset.htm>
- Metadata API `PermissionSetGroup`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_permissionsetgroup.htm>
- Metadata API `MutingPermissionSet`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_mutingpermissionset.htm>
- Metadata API `Group`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_group.htm>
- Metadata API `SharingSettings`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_sharingsettings.htm>
- Objeto `Organization`: <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_organization.htm>
- External OWD: <https://developer.salesforce.com/docs/atlas.en-us.securityImplGuide.meta/securityImplGuide/security_owd_external_setting.htm>

## Situação de cada afirmação do `ajudAI`

| Tema | Situação |
|---|---|
| `SecuritySettings` reúne faixas de IP confiáveis, regras de senha e login, expiração de sessão e SSO | confirmado |
| Configuração de sessão por perfil existe em tipo próprio (`ProfileSessionSetting`) | confirmado (não documentado por perfil nesta entrega) |
| Permission set só concede acesso, não nega; para retirar permissão dentro de um grupo usa-se `MutingPermissionSet` (API 46+) | confirmado |
| Grupo público reúne usuários, papéis e outros grupos | confirmado |
| OWD externo permite um nível de acesso padrão diferente para usuários externos | confirmado |
| Nomes dos elementos de `sessionSettings`, `passwordPolicies`, `networkAccess` | *a confirmar*: o documento mostra os elementos como estão no XML |
| `<lockSessionsToDomain>` "força a sessão ao IP de login" | **incorreto no `ajudAI`**: o nome indica bloqueio por domínio; o bloqueio por IP aparece como elemento separado nos XMLs (`lockSessionsToIp`). *A confirmar* na página oficial |
| `<forceLogoutOnSessionTimeout>` descrito como "aviso de expiração" | **descrição inconsistente no `ajudAI`** (o próprio texto diz que desconecta o usuário). *A confirmar* |
| `<enableMfaDirectUILogin>` | não encontrado; não usado |
| "Grant Access Using Hierarchies" como coluna do OWD | não encontrado no metadata de `CustomObject`; **não usado**. O documento mostra só `sharingModel` e `externalSharingModel` |
| Edição da org ("Org Edition") | vem do objeto `Organization` (`OrganizationType`, dados internos, *a confirmar*), não de `Organization.settings` |
| Campos de `Role` (`parentRole`, `caseAccessLevel`, `contactAccessLevel`, `opportunityAccessLevel`, `mayForecastManagerShare`) | *a confirmar* (renderizados só se presentes no XML) |
| `Group.doesIncludeBosses` | *a confirmar* |
| `loginIpRanges` com `startIp`/`endIp` | **não usado**: o documento mostra os elementos como estão no XML |

## Modelo de compartilhamento (genérico)

- O OWD define o acesso mínimo aos registros de cada objeto; hierarquia de papéis, regras de compartilhamento, filas, compartilhamento manual e Apex ampliam esse acesso.
- Regras de compartilhamento: por proprietário (`sharingOwnerRules`, registros de um papel/grupo) ou por critério (`sharingCriteriaRules`, filtro de campo); destinatário em `sharedTo` (papel, papel e subordinados, grupo...).
- Superiores na hierarquia herdam acesso aos registros dos subordinados quando o objeto concede acesso pela hierarquia (objetos padrão sempre; objetos customizados conforme configuração, *a confirmar* no metadata).

## O que os documentos mostram

| Documento | Mostra | Não mostra (proteção de dados ou não verificável) |
|---|---|---|
| Segurança da org | Sessão, senhas, IPs confiáveis, OWD dos objetos processados, `Organization` | Usuários, SSO (fora do escopo desta entrega) |
| Perfil | Permissões, layouts, guias, record types, horário e IP de login | Usuários atribuídos |
| Permission set / PSG | Permissões, grupos, muting | Usuários atribuídos |
| Regras de compartilhamento | Regras e OWD do objeto | — |
| Papel | Níveis de acesso, hierarquia, regras que compartilham com ele | Usuários do papel |
| Grupo público | `doesIncludeBosses`, regras que compartilham com ele | Membros |
