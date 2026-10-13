# Próximos passos e evolução operacional

> Este documento é um roadmap, não uma declaração de que as funcionalidades abaixo já existem. Execute as refatorações na ordem aprovada e valide cada etapa com testes simulados antes de usar uma org real.

## Estado e princípio de segurança

O utilitário atual consulta/retrieve metadata Salesforce e grava dados locais em `catalog/`, `inventory/`, `runs/` e `saida/docs/`. A configuração de grupos e tipos está em `config/metadata-types-mvp.json`; a execução atual não deve ser considerada uma descoberta/documentação automática de todos os tipos da org.

Dados brutos, XMLs, respostas de API, logs e documentos podem expor informação interna ou sensível. Não os envie ao GitHub Actions como artifacts nem os publique em logs sem política aprovada. A CLI e o runner não substituem aprovação, classificação de dados, gestão de credenciais ou validação do alvo.

## Sequência aprovada de refatorações

### Prioridade 1 — modelos de documentação e tratamento

**Objetivo:** revisar os modelos/contratos existentes, validar placeholders e fontes, aperfeiçoar apresentação e garantir comportamento previsível para valores ausentes, listas vazias, tabelas, caracteres especiais e subdocumentos.

Atividades:

- auditar cada modelo Markdown junto ao contrato e aos builders usados;
- testar documentos preenchidos com fixtures sanitizadas;
- melhorar `validate-config` para detectar placeholders, builders, fontes e modelos ausentes/inválidos;
- manter a falta de modelo como aviso/status da unidade, sem parar as demais;
- investigar Named Credential, Certificate e Remote Site Settings por evidência oficial e fixtures autorizadas antes de criar configuração, contrato ou modelo;
- não inventar campos nem exibir credenciais, segredos ou material criptográfico.

**Aceite:** modelos e contratos validados; testes demonstram que nenhum placeholder fica sem diagnóstico; falta de modelo não aborta as demais unidades e fica visível no relatório.

### Prioridade 2 — selecionar tudo ou somente metadata/componentes no `config.json`

> **Implementada** (`config.json` → `selection`, `src/salesforce_docs/config/scope.py`, `tests/test_scope.py`, `tests/test_selection.py`). Ver README, seção "Seleção da execução".

**Objetivo:** permitir modo `ALL` e modo de seleção explícita, preservando o comportamento de CLI de forma previsível.

Atividades:

- definir schema/versionamento e semântica para todos os grupos, metadata types e `fullName`s;
- decidir como tipos relacionados/filhos são selecionados ou rejeitados;
- definir precedência entre configuração JSON e `--group`/`--component`;
- rejeitar configuração ambígua ou inválida antes de retrieve;
- registrar no estado do run o escopo solicitado e o efetivo;
- comprovar com a CLI simulada que itens fora do escopo nunca são recuperados.

**Aceite:** modo `ALL` preserva comportamento documentado; modo selecionado executa estritamente o escopo configurado; nomes não encontrados e dependências têm resultado explícito.

### Prioridade 3 — mitigação dos riscos de segurança e execução

> **Implementada** (`approvedOrgs`, `dataProtection`, `execution.outputLayout`, `coverage`, fingerprint de retomada; `tests/test_prioridade3.py`). Ver `documentation/protecao-de-dados.md`.

**Objetivo:** melhorar validação da org-alvo, proteção de dados, cobertura, resumabilidade, saídas e operação em org grande.

Atividades:

- exigir identidade/aprovação da org-alvo antes de inventário/retrieve;
- inventariar raws, XMLs, dados internos, run state, logs e Markdown e definir proteção/retention;
- testar mascaramento de segredos em arquivos, estruturas aninhadas, stdout/stderr e exceções;
- distinguir término de execução de cobertura completa; `NO_TEMPLATE` e lacunas devem aparecer no resultado geral;
- evitar colisão/sobrescrita silenciosa e isolar saída por run;
- verificar compatibilidade de org, API, escopo, contratos/modelos e fontes antes de reutilizar unidades `SUCCESS` em retomada;
- testar interrupções, timeouts, falhas por componente, regeneração offline e escala com fixtures.

**Aceite:** nenhum segredo sentinela vaza; nenhuma coleta ocorre antes de validar org e escopo; o resultado informa cobertura; retomada/saída não mistura nem reutiliza estado incompatível silenciosamente.

### Refatoração 3 — mitigação de riscos de segurança, cobertura e execução

> **Implementada** (política de raw R1, confirmação interativa da org, token via `sf org auth show-access-token` após aprovação, `resumo.md`, `progress`/`metrics`/`errorClass`, fingerprint com configuração e XML, `regenerate.differences`, `purge` por descontinuação; `tests/test_refatoracao3.py`). Ver `documentation/protecao-de-dados.md`.

Pendências: validar o fluxo do token com CLI real (versões suportadas) em org autorizada; confirmar em documentação oficial os demais elementos sensíveis candidatos antes de incluí-los.

## Pendente de plano: produção sem login (clone Flosum + Salesforce Inspector)

> **Não implementado; não iniciar sem aprovação.** Registro da restrição e do cenário em 2026-10-13.

- **Restrição:** por ora não é permitido login em org produtiva. O MVP atual depende de login em todos os passos de coleta (1–7 e 9) e não deve ser usado em produção.
- **Fonte de metadata em produção:** o projeto Salesforce num diretório de clone do repositório Flosum.
- **Dados de objetos internos:** plano em elaboração para consultá-los pelo Salesforce Inspector e salvar os resultados num diretório.
- **Impacto esperado, quando aprovado:** um modo de execução sem org. O clone substitui inventário e retrieve (passos 4, 6, 6b e 7) e as exportações substituem as consultas (passo 9). Normalização, contratos, modelos e Markdown (passos 8 e 10) continuam os mesmos. O modo precisará de novas fontes na coluna "Fonte", de raw preservado (clone e exportações com sha256) e de identificação da org sem `sf org display`.
- **Perguntas em aberto** (formato do clone, perfis completos no repositório, formato e nomes das exportações, aprovação de exportar da produção, armazenamento): `documentation/como-testar-o-mvp.md`, seção 3.

## Testes antes de cada piloto

```bash
bin/sf-docs.sh validate-config
python3 -m unittest discover -s tests -t .
python3 -m unittest tests.test_mvp_simulation
```

A execução de `tests/` deve permanecer sem credenciais e org reais. Uma aprovação para teste real é um passo operacional distinto da aprovação de um PR.

## Evolução futura: GitHub Actions após implantação Salesforce

### Decisão de arquitetura antes de criar workflow

Primeiro determine onde ocorre o deploy Salesforce e quem pode disparar a documentação:

| Origem do evento de implantação | Opção a avaliar | Observações |
|---|---|---|
| Deploy e documentação no mesmo workflow | Job posterior no mesmo workflow | É a opção mais simples para controlar dependências e transferir apenas um identificador de implantação/run. Separar o job de documentação e restringir suas permissões. |
| Workflow de deploy em outro workflow do mesmo repositório | `workflow_run` após o workflow autorizado | Filtrar pelo nome/branch/conclusão e verificar cuidadosamente a fronteira de confiança: o workflow acionado pode ter acesso a secrets/tokens. Não executar código não confiável nesse contexto. |
| Deploy realizado por sistema/repositório externo | `repository_dispatch` com `event_type` dedicado | Requer autenticação para chamar a API do repositório. Enviar apenas metadados não secretos, como ambiente e deployment ID; não enviar token Salesforce ou payload de metadata. |
| Execução manual aprovada | `workflow_dispatch` | Útil para piloto/reprocessamento com inputs validados e environment protegido. Não deve aceitar alias/arbitrário sem allowlist. |

**Recomendação:** no primeiro piloto, usar acionamento manual (`workflow_dispatch`) com aprovação e escopo restrito. Para automação após deploy externo, adotar evento dedicado (`repository_dispatch`) apenas depois de validar a integração e os controles. Se o deploy já ocorre em workflow confiável no mesmo repositório, preferir encadear o job no próprio workflow; avaliar `workflow_run` com cautela.

### Pré-requisitos antes de automatizar

- As três prioridades de refatoração aprovadas e testes passando.
- Org-alvo identificável e allowlist/política de autorização definida.
- Modo não interativo seguro: não depender de confirmação via terminal.
- Método de autenticação de automação aprovado por administradores Salesforce e segurança; preferir credencial de integração de privilégio mínimo, com expiração/rotação e segredos fora do Git.
- Decisão sobre executor. GitHub-hosted runner pode não atender requisitos de conectividade/rede corporativa; se avaliar self-hosted runner, considerar que ele é uma máquina persistente e exige hardening, isolamento e limpeza.
- Ambiente GitHub Actions, por exemplo `controlled-salesforce-readonly`, com branch restrictions, secrets de environment e required reviewers conforme disponibilidade do plano e política da organização.
- Concorrência configurada para impedir runs simultâneos conflitantes para o mesmo ambiente/org.
- `GITHUB_TOKEN` com `permissions` mínimas; ações externas revisadas e, quando exigido pela política, fixadas a SHA completo.
- Política aprovada para outputs. Por padrão, não fazer upload de `catalog/`, `inventory/`, XMLs, raws, `runs/` completos ou documentos de org como workflow artifacts. Preferir um sumário sanitizado de status/cobertura. Se artifacts forem autorizados, limitar conteúdo, acesso e retenção.
- Identificador do deployment correlacionado ao run de documentação para auditoria; evitar incluir dados/segredos no payload do evento.

### Esqueleto conceitual — não pronto para produção

Este exemplo demonstra somente um gatilho externo. **Não autentica Salesforce, não instala a Salesforce CLI, não implementa allowlist nem escolhe uma configuração local segura. Não o habilite em produção sem completar e revisar esses controles.** Substitua versões de actions por referências aprovadas/pinadas conforme política interna.

```yaml
name: Salesforce post-deploy documentation

on:
  repository_dispatch:
    types: [salesforce_post_deploy]

permissions:
  contents: read

env:
  PYTHONUNBUFFERED: "1"

concurrency:
  group: salesforce-docs-controlled-org
  cancel-in-progress: false

jobs:
  document:
    if: github.event.client_payload.environment == 'controlled'
    runs-on: ubuntu-latest # validar rede; considerar executor controlado se necessário
    environment: controlled-salesforce-readonly
    timeout-minutes: 60
    steps:
      - name: Checkout do código aprovado
        uses: actions/checkout@<SHA-completo-aprovado>

      - name: Configurar Python
        uses: actions/setup-python@<SHA-completo-aprovado>
        with:
          python-version: "3.8"

      - name: Validar configuração e testes simulados
        run: |
          bin/sf-docs.sh validate-config
          python3 -m unittest discover -s tests -t .

      # TODO: instalar uma versão aprovada da Salesforce CLI.
      # TODO: autenticar com mecanismo não interativo aprovado, sem gravar segredo no repo.
      # TODO: validar org ID/ambiente e escopo antes de qualquer inventário/retrieve.
      # TODO: executar seleção explícita do config.json após a Prioridade 2.
      # TODO: publicar somente sumário sanitizado, se permitido pela política.
```

### Escolha do gatilho

- A documentação oficial do GitHub descreve workflows em `.github/workflows/` e eventos de repositório, externos, agendados e manuais.
- `repository_dispatch` é destinado a evento externo e exige payload autenticado; o workflow deve filtrar um `event_type` específico.
- `workflow_run` permite reagir à conclusão de outro workflow, mas o workflow subsequente pode acessar secrets/tokens mesmo quando o workflow anterior não podia. Não usar como ponte de confiança para código não confiável.
- `workflow_dispatch` é adequado para início manual controlado; valide branch, inputs, org e escopo no workflow e no utilitário.

### Regras para artifacts e logs do Actions

Artifacts ficam associados à execução do workflow e podem ser baixados por pessoas com acesso de leitura ao repositório. O GitHub informa retenção padrão de 90 dias para logs/artifacts, configurável conforme o tipo de repositório. Portanto, não envie dados de org automaticamente: defina allowlist de arquivos e retenção mínima aprovada. Redação automática de secrets nos logs não é um controle suficiente para proteger conteúdo intencionalmente impresso ou transformado.

### Sequência para implementar a automação

1. Concluir e aprovar as prioridades 1–3.
2. Demonstrar execução manual autorizada em ambiente controlado, com escopo restrito e revisão de dados.
3. Documentar identidade da org, CLI/API version, método de autenticação e outputs aprovados.
4. Criar workflow inicialmente manual e sem upload de metadata; validar permissões, rede, logs e limpeza do runner.
5. Pedir aprovação do environment e testar falha/timeout/execução duplicada.
6. Integrar ao evento pós-deploy aprovado; rejeitar evento com ambiente/deployment inválido.
7. Executar piloto acompanhado, revisar cobertura e só então avaliar agendamento/execução recorrente.
8. Reavaliar periodicamente acesso, secrets, versões da CLI/actions, retenção e política de metadata.

## Referências

### Salesforce

- [Salesforce CLI: instalação](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html)
- [Salesforce CLI: autenticação web](https://developer.salesforce.com/docs/platform/sfdx-dev/guide/sfdx-dev-auth-web-flow.html)
- [Salesforce CLI: `project retrieve start`](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_retrieve_start.html)
- [Salesforce Metadata Coverage Report](https://developer.salesforce.com/docs/success/metadata-coverage-report/references/coverage-report/metadata-coverage-report.html)

### GitHub Actions

- [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Deployment environments](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments)
- [Deployments and environments: protection rules and environment secrets](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)
- [Store and share data with workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data)
