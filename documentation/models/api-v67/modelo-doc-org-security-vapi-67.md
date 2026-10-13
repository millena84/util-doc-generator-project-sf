# Segurança da org: {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Componente | {{ settings_name }} | XML |

## Sessão

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ session_key }} | {{ session_value }} | XML |

## Senhas

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ password_key }} | {{ password_value }} | XML |

## Faixas de IP confiáveis

| Faixa (como no XML) | Fonte |
|---|---|
| {{ ip_range }} | XML |

## Padrão de compartilhamento por objeto (OWD)

Objetos processados nesta execução (grupo CustomObject). Padrões de objetos padrão também aparecem nos dados internos (Organization).

| Objeto | Rótulo | Interno (sharingModel) | Externo (externalSharingModel) | Fonte |
|---|---|---|---|---|
| {{ owd_object }} | {{ owd_label }} | {{ owd_internal }} | {{ owd_external }} | XML |

## Dados internos

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ internal_property }} | {{ internal_value }} | Objeto interno |

## Acesso e configuração

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
