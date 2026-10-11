# util-doc-generator-project-sf

Utilitário único para gerar documentação Markdown de componentes Salesforce, combinando dados da org, XMLs recuperados, objetos internos e modelos por metadata type.

## Estrutura

- `/catalog`: listagens, schemas e respostas brutas da org.
- `/inventory`: XML, dados normalizados, dados internos e estado por componente.
- `/documentation/models`: modelos Markdown por metadata type e API version.
- `/documentation/contracts`: contratos de propriedades e fontes.
- `/runs`: estado de execução, falhas e reprocessamento.
- `/saida/docs`: documentos Markdown finais.

## Premissas

- Org autenticada via `sf org login web`.
- Alias da org definido em `config/config.json`.
- API version detectada por `sf org display --target-org <alias> --json`.
- Lista de metadata types do MVP fixa em `config/metadata-types-mvp.json`.
- Respostas brutas da org são preservadas antes de qualquer transformação.

## Utilitário único

O projeto deve ter **um único utilitário**, capaz de documentar diferentes metadata types por configuração.

Desvios são declarados no JSON, por exemplo:

- `Flow` pode envolver `FlowDefinition`.
- `ExternalClientApp` pode envolver vários metadata types e pastas relacionadas.
- `CustomObject` pode envolver campos, record types e componentes relacionados.

## Claude

`CLAUDE.md` e `.claude/skills/salesforce-docs-generator/SKILL.md` ficam versionados neste repositório.

O prompt enviado ao Claude não é versionado: ele instrui o Claude a ler e completar este repositório.
