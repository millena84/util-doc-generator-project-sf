# Site do Experience Cloud (Network): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ network_name }} | XML |
| Label | {{ network_label }} | XML |
| Description | {{ description }} | XML |
| Status | {{ network_status }} | XML |
| Site (CustomSite) | {{ network_site }} | XML |
| URL path prefix | {{ url_path_prefix }} | XML |
| Autorregistro | {{ self_registration }} | XML |
| Perfil de autorregistro | {{ self_reg_profile }} | XML |
| Remetente de e-mail | {{ email_sender }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Templates de e-mail

| Elemento | Template | Fonte |
|---|---|---|
| {{ template_element }} | {{ template_name }} | XML |

## Site (CustomSite)

Infraestrutura web do site. O perfil de convidado define o que visitantes não autenticados acessam.

| Site | Ativo | URL path prefix | Perfil de convidado | Tipo | Fonte |
|---|---|---|---|---|---|
| {{ site_name }} | {{ site_active }} | {{ site_prefix }} | {{ site_guest_profile }} | {{ site_type }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

Perfis e permission sets cujos usuários podem entrar no site, e o perfil dado a quem se autorregistra.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
