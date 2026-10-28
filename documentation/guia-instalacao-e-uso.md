# Guia de instalação e uso

> ⚠️ **Produção:** por ora não é permitido login em org produtiva. Com login, use só org de desenvolvimento ou sandbox autorizada. Para produção, use o **modo pasta** (`run --source-dir`), que lê o repositório já clonado (ex.: Flosum) sem login: ver [`como-testar-o-mvp.md`](como-testar-o-mvp.md), seção 3, e o checklist [`checklist-acessos-modo-pasta.md`](checklist-acessos-modo-pasta.md).

> **Status:** guia operacional da versão atual do repositório. Leia as ressalvas de segurança antes de conectar uma org real. A simulação com fixtures não valida o comportamento nem as permissões de uma org Salesforce real.

## 1. O que é necessário

- Python **3.8 ou superior**.
- Salesforce CLI (`sf`) **2.0.0 ou superior**, conforme `config/config.json`.
- Bash para usar `bin/sf-docs.sh`. Em Windows, execute o módulo Python diretamente no PowerShell.
- Uma org Salesforce autenticada somente quando for executar o comando `run`.
- Nenhum `pip install` é necessário na configuração atual; o utilitário usa a biblioteca padrão do Python.

Instale Python e Salesforce CLI por canais aprovados para seu ambiente. Registre as versões usadas no teste. Não coloque tokens, senhas, certificados ou chaves privadas nos arquivos do repositório.

## 2. Obter o utilitário

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/millena84/util-doc-generator-project-sf.git
cd util-doc-generator-project-sf
```

Antes de editar configuração ou conectar uma org, confira o branch/commit aprovado pela equipe responsável.

## 3. Validar sem acessar a org

Valide configuração, contratos e modelos:

```bash
bin/sf-docs.sh validate-config
```

Execute os testes simulados:

```bash
python3 -m unittest discover -s tests -t .
```

Para testar a simulação completa do MVP:

```bash
python3 -m unittest tests.test_mvp_simulation
python3 -m tests.simulate_mvp --out /tmp/sim-mvp
```

Os testes usam uma Salesforce CLI simulada e fixtures. Não usam credenciais reais nem provam que uma consulta/retrieve terá sucesso na org-alvo.

## 4. Configurar o alvo e o escopo

A configuração geral está em `config/config.json`; os grupos e tipos de metadata do MVP estão em `config/metadata-types-mvp.json`.

Na versão atual, o alias padrão configurado é `dev`. Confirme que esse alias corresponde à org pretendida antes de executar. A seleção (tudo o que está configurado ou só os tipos/componentes listados) também fica no `config.json`; os argumentos `--group` e `--component` apenas restringem esse escopo. Nada disso substitui uma política de allowlist de org nem uma revisão de segurança.

### Seleção da execução (`config.json` → `selection`)

| Item | Onde | Precedência |
|---|---|---|
| Alias da org | `orgAlias` | `--target-org` > `config.json` (o `orgAlias` de `metadata-types-mvp.json` é só informativo; divergência gera aviso) |
| Diretórios | `paths` (`catalog`, `inventory`, `models`, `contracts`, `runs`, `outputDocs`, `metadataTypesConfig`) | `config.json` |
| O que documentar | `selection.mode` = `ALL` ou `SELECTED` | `config.json`; `--group`/`--component` só **restringem** |

- **`ALL`** (padrão; também quando `selection` está ausente): todos os grupos documentáveis configurados em `metadataTypesConfig`, com todos os componentes encontrados na org. Não usa automaticamente a lista inteira de `sf org list metadata-types` (tipos sem grupo/contrato não são processados).
- **`SELECTED`**: somente os tipos principais listados em `metadataTypes`:

```json
"selection": {
  "mode": "SELECTED",
  "metadataTypes": {
    "Flow":                      { "components": "ALL" },
    "CustomObject":              { "components": ["Pedido__c"] },
    "CustomMetadata":            { "components": ["Config__mdt"] },
    "ExternalClientApplication": { "components": ["Minha_ECA"] }
  }
}
```

Regras (validadas **antes de qualquer chamada à org**):

- `selection` aceita só `mode` e `metadataTypes`; cada tipo aceita só `components`. Chave desconhecida é erro.
- `mode` é exatamente `"ALL"` ou `"SELECTED"`; em `ALL`, `metadataTypes` deve estar ausente ou vazio.
- Em `SELECTED`, `metadataTypes` é obrigatório e não vazio; tipo ausente não é processado.
- `components`: `"ALL"` (todos do tipo) ou lista não vazia de fullNames únicos. Lista vazia é erro (nunca significa "todos"); `"ALL"`/`"*"` dentro da lista é erro.
- Nomes com espaço no início/fim são rejeitados (não corrigidos). Chave JSON repetida (ex.: `"Flow"` duas vezes) é erro — o leitor JSON padrão manteria só a última.
- A chave é o **tipo principal** (`ExternalClientApplication`), não o nome do grupo (`ExternalClientApp`) — usar o nome do grupo gera erro indicando o tipo correto. Para Custom Metadata o componente é o tipo (`Config__mdt`).
- Tipos relacionados/filhos (`FlowDefinition`, `CustomField`, `RecordType`, `ValidationRule`, `WebLink`, `ExtlClntApp*`…) são **rejeitados** com o principal a selecionar; entram como dependência do principal.
- `--group`/`--component` fora da seleção é erro (antes de chamar a org). A chave antiga `scope` é rejeitada com instrução de migração.

Comportamento:

- Componentes fora da seleção **não são recuperados**. Dependências comprovadas do principal selecionado continuam: `FlowDefinition` de mesmo nome, filhos do objeto, records do `__mdt`, EC referenciada no XML da NC.
- **Limitação conhecida (ADD-09):** a seleção é por tipo principal; quando dois grupos têm o mesmo tipo principal (`CustomObject` nos grupos CustomObject e PlatformEvent), só o primeiro grupo é selecionável.
- Em `SELECTED`, relações que só se comprovam lendo o XML de **cada candidato** (`FIELD_EQUALS_PRIMARY`, `REFERENCE_SCAN` — ex.: `ExtlClntApp*` de uma ECA) **não recuperam candidatos**: as seções correspondentes mostram `Não informado`, a lacuna fica em `selection.relatedNotResolved` e a cobertura é `COMPLETE_WITH_WARNINGS`. Em `ALL` os candidatos são recuperados e o vínculo é verificado normalmente.
- Componente pedido e não encontrado (ou excluído pelo `componentFilter` do grupo) vira `NOT_FOUND` (`selection.notFound`) e a execução termina como `COMPLETED_WITH_GAPS` — nunca vira "todos os componentes".
- O run state registra `selection.requested` (formato do config.json), `selection.cli`, `selection.effective`, o alias e sua origem; grupos fora da seleção aparecem como `OUT_OF_SCOPE`. `bin/sf-docs.sh validate-config` mostra alias e seleção.

**Não assuma que a configuração atual cobre todos os metadata types da org.** Mesmo em `ALL`, o utilitário processa só os grupos configurados. Tipos sem grupo/contrato não passam automaticamente a ser processados só por aparecerem na org.

## 5. Autenticar uma org autorizada

Para login interativo com alias `dev`:

```bash
sf org login web --alias dev
```

A Salesforce CLI guarda a autorização no ambiente local da CLI. Não copie arquivos de autorização para o Git, não os inclua em artefatos compartilhados e não os envie em tickets ou mensagens.

Antes de qualquer piloto real:

1. obtenha autorização do responsável pela org e pelos dados;
2. confirme o alias e a identidade da org/usuário usando a CLI;
3. valide que as permissões concedidas são as aprovadas;
4. combine onde os dados coletados serão armazenados, quem poderá acessá-los e quando serão removidos;
5. comece com um escopo reduzido e revise as saídas antes de ampliar.

O alias sozinho não protege contra executar na org errada: a proteção é a aprovação explícita do `orgId` em `approvedOrgs` (abaixo).

### Aprovar a org-alvo (obrigatório)

Na primeira execução sem `approvedOrgs`, o utilitário para depois de `sf org display` com `ORG_NOT_APPROVED` e mostra `orgId`, `alias`, `username` e `instanceUrl` detectados — **nenhum inventário ou retrieve é feito**. Em terminal interativo, você pode digitar o `orgId` exato para aprovar a org **só nessa execução**; sem terminal (CI ou `--non-interactive`) a execução sempre para. Confira se é a org pretendida e registre-a no `config.json`:

```json
"approvedOrgs": [ { "orgId": "00D...", "alias": "dev", "note": "motivo/ambiente" } ]
```

Detalhes de proteção e retenção dos arquivos gerados: `documentation/protecao-de-dados.md`.

## 6. Executar

### Todos os grupos atualmente configurados

```bash
bin/sf-docs.sh run
```

### Um grupo

```bash
bin/sf-docs.sh run --group Flow
```

### Um componente de um grupo

```bash
bin/sf-docs.sh run --group Flow --component Meu_Flow
```

### Mais de um grupo ou componente

Os argumentos repetíveis `--group` e `--component` podem ser informados mais de uma vez. Eles só restringem o escopo do `config.json`: em `SELECTED`, pedir algo fora da seleção é erro antes de qualquer chamada à org. Para o piloto, use `--component` em todo `run` (modo `ALL`): o retrieve de acesso pede só `Tipo:Nome` dos componentes informados. Não use `SELECTED` por enquanto: o tipo `CustomObject` é principal de dois grupos (CustomObject e PlatformEvent) e o grupo PlatformEvent não é selecionável (achado ADD-09, ver `piloto-org-real.md`, seção 0).

### Informar a versão da API

```bash
bin/sf-docs.sh run --api-version 67.0
```

Sem essa opção, o pipeline usa a versão detectada na sessão da org. A versão efetivamente usada deve ser registrada e considerada ao avaliar cobertura de metadata.

### Retomar uma execução interrompida

Após resolver a causa da interrupção — por exemplo, renovar uma sessão expirada — a versão atual documenta:

```bash
bin/sf-docs.sh run --resume latest
```

Ou informe o identificador exato do run.

Onde os documentos ficam:

- Por padrão, a retomada grava na **pasta da coleta original** (`saida/docs/doc-<alias>-MMDDAA/` do dia em que a execução começou), mesmo que seja retomada em outro dia. Assim a coleta fica completa numa pasta só.
- Para gravar na pasta do dia atual, use `--resume-output TODAY` (ou `execution.resumeOutput = "TODAY"` no `config.json`). Nesse caso, os documentos herdados continuam na pasta original.
- O log e o `runs/<runId>/resumo.md` informam a pasta usada e quantos componentes foram processados em cada dia. Se a execução de origem tiver mais de `execution.resumeWarnAfterDays` dias (padrão 1), há um aviso: a org pode ter mudado, e uma execução completa nova pode ser mais adequada.

Antes de retomar, confirme que org, versão da API, configuração, contratos e modelos continuam compatíveis. A validação reforçada dessa compatibilidade está listada como evolução; não presuma que uma execução antiga é automaticamente apropriada para o estado atual.

### Regenerar documentos offline

Quando os XMLs e raws de origem necessários já existem localmente:

```bash
bin/sf-docs.sh regenerate --run latest
```

A regeneração foi projetada para reconstruir derivados e Markdown sem nova chamada à org. Os documentos são gravados na pasta da execução de origem (mesma regra da retomada; `--resume-output TODAY` grava na pasta do dia). Ela ainda usa os arquivos locais da execução; isso não torna esses dados seguros para compartilhar.

### Windows sem Bash

No PowerShell, a forma direta equivalente é:

```powershell
$env:PYTHONPATH = "src"
python -m salesforce_docs run --group Flow
```

Use `python -m salesforce_docs validate-config` ou `python -m salesforce_docs regenerate --run latest` para os demais subcomandos. Confirme `python --version` e a disponibilidade de `sf` no `PATH`.

## 7. Onde ficam os arquivos

Os caminhos configurados atualmente incluem:

| Caminho | Conteúdo |
|---|---|
| `catalog/` | Descoberta da org, schemas e respostas brutas. |
| `inventory/` | Inventários, XMLs recuperados, dados normalizados e dados internos. |
| `runs/` | Estado, resumo, eventos e falhas da execução. |
| `saida/docs/` | Documentação Markdown gerada. |

Trate todo conteúdo proveniente da org como dado interno potencialmente sensível. O `.gitignore` não deve ser usado como único controle de segurança. Não faça commit, upload de artifact ou compartilhamento desses diretórios sem revisão e autorização explícitas.

O layout padrão (`execution.outputLayout = BY_DATE`) junta o que foi processado no dia em `saida/docs/doc-<alias>-MMDDAA/`; versões anteriores com conteúdo diferente vão para `_substituidos/`. `BY_RUN` isola cada execução numa subpasta `<runId>/`. Detalhes em `protecao-de-dados.md`.

## 8. Interpretar o resultado

Consulte o sumário do terminal e `runs/<runId>.json`. Alguns estados existentes incluem `SUCCESS`, `NO_TEMPLATE`, `NO_COMPONENTS`, `NOT_ENABLED`, `SCHEMA_UNAVAILABLE`, `RETRIEVE_FAILED`, `INTERNAL_DATA_UNAVAILABLE`, `RETRY_REQUIRED`, `MISMATCH` e `FAILED`.

- **Modelo ausente:** o comportamento esperado é avisar, não gerar aquele documento e continuar as outras unidades. Isso não significa que o tipo ausente tenha sido descoberto/processado.
- **`PARTIAL_SUCCESS`:** houve resultado parcial; revise unidades, avisos e falhas antes de considerar a saída utilizável.
- **`SUCCESS`:** não conclua cobertura completa apenas pelo nome do status. Confira a linha **Cobertura** e as tabelas de tipos (descobertos, configurados, selecionados, documentados) em `runs/<runId>/resumo.md`.
- **Simulação:** resultados com CLI/Metadata API simuladas são exemplos de teste, não documentação obtida da org real.

## 9. Primeiro teste em org real

Visão geral dos níveis de teste (sem org, org não produtiva, produção): [`como-testar-o-mvp.md`](como-testar-o-mvp.md). O roteiro completo do primeiro teste em org está em [`piloto-org-real.md`](piloto-org-real.md): validação sem org, aprovação da org, execução mínima, conferência do acesso (passo 6b), confirmação por grupo (C0–C10), execução completa, revisão de proteção de dados, critérios de aprovação e de parada, modelo de relato e limpeza. Em resumo:

1. Use um commit aprovado e rode `validate-config --strict` e toda a suíte de testes.
2. Confirme autorização, alias, org-alvo e usuário; registre a org em `approvedOrgs`.
3. Comece com um grupo pequeno e use `--component` em todo `run` (sem ele, o modo `ALL` recupera tipos inteiros); amplie fase a fase.
4. Execute em armazenamento aprovado e com acesso restrito.
5. Revise o `resumo.md`, os documentos e a busca por dados sensíveis antes de compartilhar qualquer coisa.
6. Registre cobertura, limitações e aprovação do responsável; remova os dados locais conforme a retenção combinada.

## Referências

- README e instruções da versão do utilitário: `README.md`, `CLAUDE.md` e `.claude/skills/salesforce-docs-generator/SKILL.md`.
- [Salesforce CLI: instalar a CLI](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html)
- [Salesforce CLI: autenticação web de uma org](https://developer.salesforce.com/docs/platform/sfdx-dev/guide/sfdx-dev-auth-web-flow.html)
- [Salesforce Metadata Coverage Report](https://developer.salesforce.com/docs/success/metadata-coverage-report/references/coverage-report/metadata-coverage-report.html)
- [Salesforce CLI: `project retrieve start`](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_retrieve_start.html)
