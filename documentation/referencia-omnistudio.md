# Referência: OmniStudio

Conteúdo **genérico da plataforma** sobre OmniStudio (DataRaptor, Integration Procedure, OmniScript e FlexCard). Ele vale para qualquer org, por isso não aparece como propriedade nos documentos gerados (`modelo-doc-omni-data-transform`, `-omni-integration-procedure`, `-omni-script`, `-omni-ui-card`). Esses documentos só mostram o que está no XML, nos dados internos e nos componentes processados.

> **Origem:** adaptado de `_sf_utilities/ajudAI/contexto-doc-industries-omni.md` (Onda 10), na versão `ca067b0` do repositório `millena84/_sf_utilities`. É material de referência, não normativo.
>
> O acesso direto à documentação oficial não estava disponível no ambiente da adaptação (2026-10-13). Nenhum item abaixo foi conferido na página oficial: os itens *a confirmar* ficam para o piloto (`piloto-org-real.md`, fase C10).

## Fontes oficiais

- Lista de tipos da Metadata API (tipos `Omni*`): <https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_types_list.htm>
- OmniStudio (Help): <https://help.salesforce.com/s/articleView?id=sf.os_omnistudio.htm>

## Formato: Metadata API x Vlocity Build Tool

| Tema | Situação |
|---|---|
| O `ajudAI` descreve arquivos `.json` (`ExtractOrderData_1.json`, `Order_SendToAWS_Procedure_1.json`...) | **não usado**: é o formato de datapack do Vlocity Build Tool (pacote gerenciado). O utilitário usa `sf project retrieve` |
| OmniStudio padrão (sem pacote) na Metadata API: `OmniDataTransform`, `OmniIntegrationProcedure`, `OmniScript`, `OmniUiCard`, em XML | *a confirmar* (tipos, pastas e sufixos `.rpt`, `.oip`, `.os`, `.ouc`) |
| Configuração de cada elemento em `propertySetConfig` (texto JSON dentro do XML); fonte do card em `dataSourceConfig` | *a confirmar*. O utilitário lê esses JSON **só** para extrair nomes de componentes referenciados; o texto nunca é documentado |

## 10.1 DataRaptor (`OmniDataTransform`)

| Tema | Situação |
|---|---|
| Tipos `Extract`, `Turbo Extract`, `Transform`, `Load` (Extract/Turbo leem, Load grava, Transform não usa o banco) | *a confirmar*; o documento mostra o `type` como está e só deduz objetos lidos/gravados quando o tipo contém extract/turbo/load |
| Itens `omniDataTransformItem` (`inputObjectName`, `inputFieldName`, `outputObjectName`, `outputFieldName`, `filterOperator`, `filterValue`, `formulaExpression`, `lookupObjectName`) | *a confirmar*; ausentes ficam "Não informado" |
| `Check Link Access Rights` e `Ignore Security` (modo sistema) | **não usados**: nomes do exemplo não confirmados. O elemento real de segurança aparece em "Configurações", como está no XML |
| Permission sets "OmniStudio Admin" / "OmniStudio User" | **não usados**: nomes não confirmados (podem ser licenças de permission set) |

## 10.2 Integration Procedure e 10.3 OmniScript

| Tema | Situação |
|---|---|
| Os dois são `OmniProcess` (`type`, `subType`, `language`, `versionNumber`, `isActive`); quem chama usa `Type_SubType` | *a confirmar*; `Type_SubType` aparece como `Derivado` |
| Elementos em `omniProcessElements`, filhos em `childElements` (`name`, `type`, `level`, `isActive`) | *a confirmar* |
| Chaves de referência: `bundle` (DataRaptor), `integrationProcedureKey`/`ipMethod` (Integration Procedure), `remoteClass` (Apex), `namedCredential` | *a confirmar* |
| `chainOnStep`, `queueableChainable`, `chainableCpuLimit` | *a confirmar*; aparecem só se forem folhas do XML |
| Execução via LWC/REST exige acesso à classe `OmniStudioIntegrationProcedureService` | **não usado**: classe não confirmada. O acesso documentado é o das classes Apex referenciadas (Remote Action) |
| OmniScript compilado em LWC (`typeToLwcComponent`, `webComponentKey`) | **não ligado**: nomes não confirmados; o uso do LWC compilado em páginas não aparece |

## 10.4 FlexCard (`OmniUiCard`)

| Tema | Situação |
|---|---|
| Fonte de dados (`IntegrationProcedure`, `DataRaptor`, `SOQL`, `REST`...) | *a confirmar*; o documento mostra o `type` do `dataSourceConfig` e o componente referenciado |
| Ações (`actionList`, `stateAction.type`: IntegrationProcedure, OmniScript, Flyout, Navigate...) | *a confirmar* |
| Lançamento de OmniScript e flyout de outro card | **não ligados** (chaves não confirmadas) |
| `sampleDataSourceResponse` (dados de exemplo) | **nunca documentado**: pode ter dados reais |
| Visibilidade condicional (`State Conditions`) | **não interpretada** |

## O que os documentos mostram

| Documento | Mostra | Fonte |
|---|---|---|
| DataRaptor | Tipo, entrada/saída, itens de mapeamento, objetos lidos/gravados, quem usa, permissões nos objetos | XML, Derivado, Objeto interno |
| Integration Procedure | Elementos, componentes referenciados, quem chama, quem executa as classes Apex | XML, Derivado, Objeto interno |
| OmniScript | Elementos, componentes referenciados, quem executa as classes Apex | XML, Derivado, Objeto interno |
| FlexCard | Fonte de dados, ações, componentes referenciados, quem executa as classes Apex | XML, Objeto interno |
