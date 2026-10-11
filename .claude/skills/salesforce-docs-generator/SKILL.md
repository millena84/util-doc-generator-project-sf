---
name: salesforce-docs-generator
description: Implementa, executa e valida o utilitário único de documentação Salesforce, usando Salesforce CLI, Metadata API, Tooling API, XML recuperado e modelos Markdown por metadata type.
---

# Skill: Salesforce Docs Generator

## Regra central

Existe **um único utilitário**. Novos metadata types entram por:

1. Configuração em JSON.
2. Contrato em `documentation/contracts/`.
3. Modelo em `documentation/models/`.
4. Extrator/configuração de desvio, se necessário.

## Premissas do MVP

1. Org autenticada via `sf org login web`.
2. Alias em `config/config.json`.
3. Lista mockada em `config/metadata-types-mvp.json`.
4. API version detectada por `sf org display --target-org <alias> --json`.
5. Respostas brutas são sempre preservadas.

## Ordem de execução

1. `sf --version`
2. `sf org list --json`
3. `sf org display --target-org <alias> --json`
4. `sf org list metadata-types --target-org <alias> --api-version <versao> --json`
5. Validar tipos mockados contra a listagem raw.
6. Para cada tipo habilitado, executar `describeValueType()` via `mdapi.<Type>.describe()`.
7. `sf org list metadata --metadata-type <tipo> --json`.
8. `sf project retrieve start --metadata <tipo>:<componente>`.
9. Normalizar XML.
10. Consultar dados internos, se previsto.
11. Renderizar Markdown, se modelo existir.
12. Registrar estado em `/runs`.

## Regras de arquivos

- Raw em `/catalog` para listagens e schemas.
- Componentes, XML, dados normalizados e internal data em `/inventory`.
- Modelos em `/documentation/models`.
- Documentos finais em `/saida/docs`.
- Estado em `/runs`.

## Desvios

Desvios são configurados no JSON. Exemplos:

- `Flow` + `FlowDefinition`.
- `ExternalClientApp` + metadata types relacionados.
- `CustomObject` + campos e componentes relacionados.

## Estados

`SUCCESS`, `NO_TEMPLATE`, `NO_COMPONENTS`, `NOT_ENABLED`, `SCHEMA_UNAVAILABLE`, `RETRIEVE_FAILED`, `INTERNAL_DATA_UNAVAILABLE`, `RETRY_REQUIRED`, `MISMATCH`.

## Execução e validação

- Executar: `bin/sf-docs.sh run [--group <Grupo>] [--component <fullName>] [--api-version <N.0>] [--resume latest]`.
- Regerar derivados e Markdown a partir dos raws (sem org): `bin/sf-docs.sh regenerate --run latest`.
- Validar configuração/contratos: `bin/sf-docs.sh validate-config`.
- Testes (somente biblioteca padrão): `python3 -m unittest discover -s tests -t .`.
- Contratos ficam em `documentation/contracts/<tipo-kebab>.schema.json`; ver README para a sintaxe de `path`, `tables` e `blocks`.

## Segurança

Nunca versionar ou expor access token, refresh token, senha, chave privada ou segredo.
