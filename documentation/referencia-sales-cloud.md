# Referência: Sales Cloud

Conteúdo **genérico da plataforma** sobre processo de vendas, conversão de Lead, territórios e divisão de oportunidade. Ele vale para qualquer org, por isso não aparece como propriedade nos documentos gerados (`modelo-doc-business-process`, `-lead-convert-settings`, `-territory2-model`, `-opportunity-split-type`). Esses documentos só mostram o que está no XML, nos dados internos e nos componentes recuperados.

> **Origem:** adaptado de `_sf_utilities/ajudAI/contexto-doc-sales-cloud.md` (Onda 08), na versão `ca067b0` do repositório `millena84/_sf_utilities`. É material de referência, não normativo.
>
> O acesso direto a developer.salesforce.com não estava disponível no ambiente da adaptação (2026-10-13). Os itens "confirmado" vieram de trechos das páginas oficiais retornados pela busca. Itens *a confirmar* não foram verificados.

## Fontes oficiais

- Metadata API `BusinessProcess`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_businessprocess.htm>
- Business Process (Object Reference): <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_businessprocess.htm>
- Metadata API `RecordType`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_recordtype.htm>
- Metadata API `LeadConvertSettings`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_leadconvertsettings.htm>
- Metadata API `Territory2Model`, `Territory2`, `Territory2Rule`, `Territory2Settings`: <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_territory2model.htm>, <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_territory2.htm>, <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_territory2rule.htm>, <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_territory2settings.htm>
- `Territory2Type` (Object Reference): <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_territory2type.htm>
- `OpportunitySplitType` (Tooling API): <https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/tooling_api_objects_opportunitysplittype.htm>
- `OpportunitySplit` (Object Reference): <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunitysplit.htm>

## 8.1 Processo de vendas (`BusinessProcess`)

| Tema | Situação |
|---|---|
| Processo de negócio acompanha ciclos de vendas, lead, suporte e solução, mostrando valores de picklist diferentes | confirmado |
| Record type oferece processos de negócio, valores de picklist e layouts diferentes (é o vínculo entre o processo e o usuário) | confirmado |
| Cadeia Processo → Record Type → Perfil/Permission Set (o processo não é atribuído direto ao perfil) | confirmado pelo vínculo acima |
| Elementos `isActive`, `description` e `values` (`fullName`, `default`) | *a confirmar*; são os do exemplo do `ajudAI` e da fixture |
| `masterLabel` no XML do processo | *a confirmar*; o documento mostra só se estiver no XML |

O utilitário recupera os record types do mesmo objeto cujo `<businessProcess>` é o processo (relação `FIELD_EQUALS_PRIMARY_NAME`). Também lista os perfis e permission sets que enxergam esses record types (`recordTypeVisibilities`).

## 8.2 Conversão de Lead

| Tema | Situação |
|---|---|
| `LeadConvertSettings`: mapeamento de campos customizados do Lead para Account, Contact e Opportunity, e opções de criação de oportunidade | confirmado |
| Elementos (`objectMapping`, `inputObject`/`outputObject`, `mappingFields` com `inputField`/`outputField`, `opportunityCreationOptions`, `allowOwnerChange`) | *a confirmar*; o parser lê pares `input*`/`output*` de forma genérica |
| `Lead.settings` com `LeadSettings` (`enableLeadConvert`, `createOpportunityOnConvert`, `selectDefaultOpportunityStageUponConvert`) | **não usado**: tipo e elementos não confirmados; o prompt de exemplos cita outro tipo (`LeadConfigSettings`) |
| Caminho `objects/Lead/leadConvertSettings/...` do `ajudAI` | *a confirmar*; o utilitário recupera `LeadConvertSettings:LeadConvertSettings` |
| Permissão `ConvertLeads` e FLS nos campos mapeados | permissão *a confirmar* (nome de API); FLS lida de `fieldPermissions` |

## 8.3 Territórios 2.0

| Tema | Situação |
|---|---|
| `Territory2Model`, `Territory2`, `Territory2Rule` e `Territory2Type` exigem Sales Territories habilitado; todo `Territory2` tem um `Territory2Type` | confirmado |
| `Territory2Settings` controla o acesso padrão a registros (contas e oportunidades) | confirmado |
| Nomes `Modelo.Territorio` / `Modelo.Regra` e elementos (`accountAccessLevel`, `opportunityAccessLevel`, `parentTerritory`, `territory2Type`, `ruleAssociations`, `ruleItems`...) | *a confirmar*; ausentes ficam "Não informado" |
| **"Membros do território (usuários) no `.territory2-meta.xml`"** | **não usado**: não confirmado. Usuários nunca são documentados (proteção de dados) |
| Permissão `ManageTerritories` | *a confirmar* (nome de API) |

## 8.4 Divisão de oportunidade (`OpportunitySplitType`)

| Tema | Situação |
|---|---|
| `OpportunitySplitType` define rótulos e comportamento de cada tipo de divisão (Tooling API 37+) | confirmado |
| `OpportunitySplit` credita membros da equipe da oportunidade com parte do valor | confirmado |
| **`isTotalPercentageEnforced`** do `ajudAI` | **não confirmado**; a fixture usa `isTotalValidated`, também *a confirmar*. O documento mostra as folhas do XML como estão |
| Permissão `ManageOpportunitySplits` | *a confirmar* (nome de API) |

## O que os documentos mostram

| Documento | Mostra | Fonte |
|---|---|---|
| Processo de negócio | Valores e valor padrão, record types que usam o processo, perfis que enxergam esses record types | XML, Objeto interno |
| Conversão de Lead (documento único da org) | Configurações gerais, mapeamentos de objeto e de campos, quem converte e FLS dos campos | XML |
| Modelo de territórios | Configuração do modelo, territórios (tipo, pai, níveis de acesso, regras associadas), regras (objeto, critérios), quem gerencia territórios | XML, Objeto interno |
| Tipo de divisão | Configuração como está no XML, quem gerencia divisões | XML, Objeto interno |
