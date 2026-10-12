# Guia de instalação e uso

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

Na versão atual, o alias padrão configurado é `dev`. Confirme que esse alias corresponde à org pretendida antes de executar. O escopo (tudo o que está configurado ou só os tipos/componentes listados) também fica no `config.json`; os argumentos `--group` e `--component` apenas restringem esse escopo. Nada disso substitui uma política de allowlist de org nem uma revisão de segurança.

### Escopo da execução (`config.json` → `scope`)

| Item | Onde | Precedência |
|---|---|---|
| Alias da org | `orgAlias` | `--target-org` > `config.json` (o `orgAlias` de `metadata-types-mvp.json` é só informativo; divergência gera aviso) |
| Diretórios | `paths` (`catalog`, `inventory`, `models`, `contracts`, `runs`, `outputDocs`, `metadataTypesConfig`) | `config.json` |
| O que documentar | `scope.mode` = `ALL` ou `SELECTED` | `config.json`; `--group`/`--component` só **restringem** |

- **`ALL`** (padrão): todos os grupos configurados em `metadataTypesConfig`, com todos os componentes que a org tiver. Não usa automaticamente a lista inteira de `sf org list metadata-types` (tipos sem grupo/contrato não são processados).
- **`SELECTED`**: somente os tipos principais e componentes listados:

```json
"scope": {
  "mode": "SELECTED",
  "selection": [
    { "metadataType": "Flow", "components": ["Meu_Flow", "Outro_Flow"] },
    { "metadataType": "CustomMetadata", "components": ["Config__mdt"] },
    { "metadataType": "RemoteSiteSetting", "components": ["*"] }
  ]
}
```

Regras:

- `metadataType` é o tipo **principal** de um grupo. Tipos relacionados/filhos (`FlowDefinition`, `CustomField`, `ExtlClntApp*`…) são rejeitados com a indicação do principal — eles entram como dependência do principal selecionado.
- `components` é obrigatório; `["*"]` = todos do tipo. Para Custom Metadata o componente é o tipo (`Config__mdt`).
- Configuração inválida ou ambígua (modo desconhecido, `selection` vazia ou com `ALL`, tipo repetido, componente vazio/repetido, `*` misturado com nomes, tipo desconhecido) é rejeitada **antes de qualquer chamada à org**.
- `--group`/`--component` fora do escopo do `config.json` é erro (antes de chamar a org).
- Componente pedido e não encontrado (ou excluído pelo `componentFilter` do grupo) vira `NOT_FOUND` explícito no run state (`scope.notFound`) e a execução termina como `PARTIAL_SUCCESS`.
- Componentes fora do escopo **não são recuperados**. Dependências do principal selecionado são: `FlowDefinition` de mesmo nome, filhos do objeto, records do `__mdt`, EC referenciada pela NC. Exceção documentada: para ligar `ExtlClntApp*` a uma ECA (`FIELD_EQUALS_PRIMARY`), os candidatos do tipo relacionado são recuperados para ler `externalClientApplication`; só os que apontam para a ECA selecionada entram no documento.
- O run state registra o escopo pedido (`scope.requested`, `scope.cli`), o efetivo (`scope.effective`), o alias e sua origem; grupos fora do escopo aparecem como `OUT_OF_SCOPE`.
- `bin/sf-docs.sh validate-config` mostra alias e escopo efetivo.

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

A versão atual ainda precisa das refatorações de seleção explícita e das proteções descritas em `proximos-passos.md`. Portanto, não trate um alias como proteção suficiente contra executar na org errada.

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

Os argumentos repetíveis `--group` e `--component` podem ser informados mais de uma vez. Eles só restringem o escopo do `config.json`: em `SELECTED`, pedir algo fora da seleção é erro antes de qualquer chamada à org. Para um piloto, prefira declarar a seleção em `scope.selection`.

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

Ou informe o identificador exato do run. Antes de retomar, confirme que org, versão da API, configuração, contratos e modelos continuam compatíveis. A validação reforçada dessa compatibilidade está listada como evolução; não presuma que uma execução antiga é automaticamente apropriada para o estado atual.

### Regenerar documentos offline

Quando os XMLs e raws de origem necessários já existem localmente:

```bash
bin/sf-docs.sh regenerate --run latest
```

A regeneração foi projetada para reconstruir derivados e Markdown sem nova chamada à org. Ela ainda usa os arquivos locais da execução; isso não torna esses dados seguros para compartilhar.

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

O layout de saída atual usa diretório de data. A evolução para isolamento por `runId` e proteção contra sobrescrita está descrita em `proximos-passos.md`.

## 8. Interpretar o resultado

Consulte o sumário do terminal e `runs/<runId>.json`. Alguns estados existentes incluem `SUCCESS`, `NO_TEMPLATE`, `NO_COMPONENTS`, `NOT_ENABLED`, `SCHEMA_UNAVAILABLE`, `RETRIEVE_FAILED`, `INTERNAL_DATA_UNAVAILABLE`, `RETRY_REQUIRED`, `MISMATCH` e `FAILED`.

- **Modelo ausente:** o comportamento esperado é avisar, não gerar aquele documento e continuar as outras unidades. Isso não significa que o tipo ausente tenha sido descoberto/processado.
- **`PARTIAL_SUCCESS`:** houve resultado parcial; revise unidades, avisos e falhas antes de considerar a saída utilizável.
- **`SUCCESS`:** não conclua cobertura completa apenas pelo nome do status. Confira tipos descobertos, selecionados e documentados; a semântica de cobertura global será reforçada na terceira refatoração.
- **Simulação:** resultados com CLI/Metadata API simuladas são exemplos de teste, não documentação obtida da org real.

## 9. Procedimento mínimo para o primeiro piloto controlado

1. Use checkout/commit aprovado.
2. Rode `validate-config` e toda a suíte de testes.
3. Confirme autorização, alias, org-alvo e usuário.
4. Restrinja o escopo ao necessário; não suponha que `run` documentará toda a org.
5. Execute em armazenamento aprovado e com acesso restrito.
6. Revise estado do run, tipos não cobertos, erros, raws/XMLs e documentos gerados.
7. Procure segredos e informação que não deveria ser divulgada.
8. Registre cobertura, limitações e aprovação do responsável.
9. Remova os dados locais conforme a política de retenção definida.

## Referências

- README e instruções da versão do utilitário: `README.md`, `CLAUDE.md` e `.claude/skills/salesforce-docs-generator/SKILL.md`.
- [Salesforce CLI: instalar a CLI](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html)
- [Salesforce CLI: autenticação web de uma org](https://developer.salesforce.com/docs/platform/sfdx-dev/guide/sfdx-dev-auth-web-flow.html)
- [Salesforce Metadata Coverage Report](https://developer.salesforce.com/docs/success/metadata-coverage-report/references/coverage-report/metadata-coverage-report.html)
- [Salesforce CLI: `project retrieve start`](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_retrieve_start.html)
