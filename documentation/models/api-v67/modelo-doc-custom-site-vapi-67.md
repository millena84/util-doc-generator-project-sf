# Site (CustomSite): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ site_name }} | XML |
| MasterLabel | {{ master_label }} | XML |
| Active | {{ site_active }} | XML |
| Tipo do site | {{ site_type }} | XML |
| URL path prefix | {{ url_path_prefix }} | XML |
| Subdomínio | {{ subdomain }} | XML |
| Perfil de convidado | {{ guest_profile }} | XML |

## Usuários do site

Usuários nunca são documentados: o documento mostra só se cada papel está configurado.

| Papel | Situação | Fonte |
|---|---|---|
| {{ site_user_role }} | {{ site_user_state }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Sites do Experience Cloud (Network)

| Network | Status | Autorregistro | Fonte |
|---|---|---|---|
| {{ network }} | {{ network_status }} | {{ network_self_reg }} | XML |

## Permissões de objeto do perfil de convidado

Visitantes não autenticados usam o perfil de convidado. Acesso além de Ler/Criar é marcado para revisão.

| Objeto | Acesso | Revisar (acima de Ler/Criar) | Fonte |
|---|---|---|---|
| {{ grant_name }} | {{ grant_access }} | {{ grant_review }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Perfil de convidado e regras de compartilhamento que expõem registros a visitantes do site.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
