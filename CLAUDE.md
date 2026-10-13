# CLAUDE.md

## Propósito

Este repositório contém **um único utilitário** para gerar documentação Markdown de componentes Salesforce.

O utilitário deve ser genérico e configurável. Novos metadata types entram por configuração, contrato, extrator e modelo — não por criação de um novo utilitário.

## Regras obrigatórias

1. Não invente propriedades, objetos, tabelas, campos, relacionamentos ou valores Salesforce.
2. Toda resposta bruta da org deve ser salva antes de qualquer transformação.
3. Nunca altere arquivos `.raw.json`.
4. Todo derivado deve poder ser regenerado a partir do raw.
5. Toda propriedade em Markdown deve identificar sua fonte.
6. Não gere Markdown se o modelo não existir.
7. Não versione access token, refresh token, senha, chave privada ou segredo.
8. Use um único utilitário; desvios por metadata type devem ser configurados em JSON.
9. Valide informações Salesforce em documentação oficial ou dados reais da org.

## Desvios configuráveis

Alguns metadata types não seguem o padrão de um componente por documento.

Exemplos:

- `Flow` pode envolver `FlowDefinition`.
- `ExternalClientApp` pode envolver múltiplos metadata types e pastas relacionadas.
- `CustomObject` pode envolver `CustomField`, `RecordType`, `ValidationRule` e outros componentes.

Esses desvios devem ser declarados em `config/metadata-types-mvp.json`.

## Fontes prioritárias

1. https://developer.salesforce.com/docs/
2. https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/
3. https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/
4. https://developer.salesforce.com/docs/platform/salesforce-cli-reference/
5. https://help.salesforce.com/
6. https://developer.salesforce.com/docs/platform/api-rest/

## Restrição atual: produção sem login

- Por ora não é permitido login em org produtiva. O MVP exige login (`run`): use só em org de desenvolvimento ou sandbox autorizada.
- Cenário produtivo previsto: metadata do diretório de clone do repositório **Flosum** e dados de objetos internos exportados pelo **Salesforce Inspector** para um diretório. O plano de ação ainda está em definição pela responsável.
- **Não implemente esse modo** (nem altere o pipeline para ele) sem aprovação explícita. Referência: `documentation/como-testar-o-mvp.md`, seção 3.

## AWS

Não introduza serviços AWS sem solicitação explícita.
