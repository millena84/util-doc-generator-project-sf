# Experience Builder (ExperienceBundle): {{ component_name }}

## Identificação

| Propriedade | Valor | Fonte |
|---|---|---|
| Name | {{ experience_name }} | XML |
| Label | {{ experience_label }} | XML |
| Tipo | {{ experience_type }} | XML |

## Configurações

| Propriedade | Valor | Fonte |
|---|---|---|
| {{ leaf_key }} | {{ leaf_value }} | XML |

## Pastas do bundle

| Pasta | Arquivos JSON | Fonte |
|---|---|---|
| {{ bundle_folder }} | {{ bundle_files }} | JSON do ExperienceBundle |

## Páginas (views)

| View | Rótulo | Layout | Componentes | Arquivo | Fonte |
|---|---|---|---|---|---|
| {{ view_id }} | {{ view_label }} | {{ view_layout }} | {{ view_components }} | {{ view_file }} | JSON do ExperienceBundle |

## Rotas e acesso às páginas

Acesso à página como está na rota (ex.: público ou exige login); valor ausente fica "Não informado".

| Rota | URL | Acesso à página | View ativa | Tipo | Arquivo | Fonte |
|---|---|---|---|---|---|---|
| {{ route_id }} | {{ route_prefix }} | {{ route_access }} | {{ route_view }} | {{ route_type }} | {{ route_file }} | JSON do ExperienceBundle |

## Componentes por página

| View | Região | Componente | Identificador | Fonte |
|---|---|---|---|---|
| {{ cmp_view }} | {{ cmp_region }} | {{ cmp_name }} | {{ cmp_id }} | JSON do ExperienceBundle |

## Público-alvo e visibilidade

Referências de público (audience) e visibilidade como estão no JSON. Os critérios não são interpretados.

| View | Componente | Chave | Valor | Fonte |
|---|---|---|---|---|
| {{ tg_view }} | {{ tg_component }} | {{ tg_key }} | {{ tg_value }} | JSON do ExperienceBundle |

## Acesso e configuração

Quem pode executar as classes Apex chamadas pelos LWC das páginas. Quem entra no site está no documento da Network; o acesso a cada página, na tabela de rotas.

| Origem | Nome | Acesso | Via | Fonte |
|---|---|---|---|---|
| {{ origin_type }} | {{ origin_name }} | {{ access_granted }} | {{ access_via }} | XML |
