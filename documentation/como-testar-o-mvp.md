# Como testar o MVP

Este guia diz **o que testar, onde e com qual roteiro**, conforme o ambiente. Comece pelo nível 1 e só suba de nível quando o anterior passar.

> ⚠️ **Restrição atual — ambientes produtivos:** por ora **não é permitido login** (`sf org login ...`) em org produtiva. O MVP atual **precisa** de login: todos os passos de coleta chamam a org pela Salesforce CLI. Portanto, **o MVP não deve ser executado contra produção**. O cenário produtivo previsto (nível 3) usa o projeto Salesforce de um **clone do repositório Flosum** e dados de objetos internos **exportados pelo Salesforce Inspector**. Esse modo **ainda não existe**: está descrito abaixo só como plano, para decisão. Nada no código foi alterado para ele.

| Nível | Ambiente | Login na org | Roteiro | Situação |
|---|---|---|---|---|
| 1 | Máquina local, sem org | Não | Seção 1 deste guia | Pronto |
| 2 | Org de desenvolvimento ou sandbox autorizada | Sim (não produtiva) | [`piloto-org-real.md`](piloto-org-real.md) | Pronto para o primeiro teste |
| 3 | Produção | **Não permitido** | Seção 3 deste guia (plano) | **Não implementado** |

## 1. Nível 1 — sem org (fixtures simuladas)

Prova que o utilitário, a configuração, os contratos e os modelos estão coerentes. Não prova nada sobre uma org real: a CLI e as respostas são simuladas (`tests/fixtures/`).

```bash
bin/sf-docs.sh validate-config --strict                 # config, contratos, modelos e placeholders
python3 -m unittest discover -s tests -t .              # suíte completa (~10 min)
python3 -m unittest tests.test_mvp_simulation           # os 46 modelos e os 46 metadata types do MVP
python3 -m tests.simulate_mvp --out /tmp/sim-mvp        # execução completa simulada + relatório passo a passo
```

O que conferir:

- [ ] `validate-config --strict` termina com "Configuração válida."; a suíte, com `OK`.
- [ ] Em `/tmp/sim-mvp/runs/<runId>/resumo.md`: status `SUCCESS`, cobertura `COMPLETE`, 0 falhas.
- [ ] Em `/tmp/sim-mvp/saida/docs/`: os 73 documentos, cada linha de tabela com uma fonte (`XML`, `Objeto interno`, `Derivado`...).
- [ ] Nenhum valor sentinela das fixtures (`SEGREDO_SIMULADO`, `sentinela`, `@example.invalid`) nos documentos: os testes de proteção de dados verificam isso.
- [ ] Opcional: `PYTHONPATH=src python3 -m salesforce_docs --project-root /tmp/sim-mvp regenerate --run latest` regenera os documentos da simulação sem nenhuma chamada.

O relatório versionado da última simulação fica em `documentation/simulacao/relatorio-simulacao-mvp.md`.

**Limite do nível 1:** os nomes de elementos XML e de campos dos objetos internos marcados *a confirmar* foram usados nas fixtures do mesmo jeito que no código. Os testes passam por construção e só o nível 2 confirma essas premissas.

## 2. Nível 2 — org não produtiva (primeiro teste do MVP)

Siga [`piloto-org-real.md`](piloto-org-real.md). Em resumo:

1. Autorização, org de desenvolvimento ou sandbox, armazenamento aprovado.
2. Nível 1 completo no mesmo commit.
3. Login (`sf org login web`), conferência de `connectedStatus` e registro do `orgId` em `approvedOrgs`.
4. `--component` em todo `run`, com poucos componentes por fase. Sem ele, o modo `ALL` recupera tipos inteiros. Não use `SELECTED` no piloto (achado ADD-09).
5. Fase A (execução mínima), Fase B (acesso e configuração) e fases C0–C10, uma de cada vez.
6. Revisão de proteção de dados em toda fase; critérios de aprovação e de parada; relato sem dados da org; limpeza.

## 3. Nível 3 — produção sem login (PLANO, não implementado)

### Situação

- **Restrição:** não é permitido login em org produtiva por enquanto.
- **Fonte de metadata disponível:** o projeto Salesforce estará num diretório de **clone de repositório do Flosum**.
- **Dados de objetos internos** (as consultas do Apêndice A do piloto, como `Flow`, `ApexClass` e `EntityDefinition`): plano em elaboração para obtê-los pelo **Salesforce Inspector** e salvar os resultados num diretório.
- **Decisão:** documentar a restrição e o plano; **não modificar o MVP ainda**.

### O que o MVP atual faz e por que não serve para produção sem login

| Passo do `run` | Chamada | Funciona sem login? |
|---|---|---|
| 1–3 (`sf --version`, `org list`, `org display`, aprovação, token) | Salesforce CLI | Não (exige org autenticada) |
| 4 (`org list metadata-types`) | CLI | Não |
| 5 (describe dos tipos) | Metadata API (token) | Não |
| 6 (`org list metadata`, inventário) | CLI | Não |
| 6b (retrieve de acesso: Profile, PermissionSet...) | CLI | Não |
| 7 (retrieve por componente) | CLI | Não |
| 8 (normalização do XML) | Local | Sim |
| 9 (dados internos, `sf data query`) | CLI | Não |
| 10 (Markdown) | Local | Sim |
| `regenerate` | Local (raws de uma execução anterior) | Sim, mas só a partir de uma execução feita com login |

Não use `regenerate` como atalho para produção: ele exige os raws de uma execução `run` anterior na mesma org.

### Esboço do modo futuro (para decisão; nada implementado)

A ideia é um modo de execução **sem org**:

1. **Fonte de metadata:** o diretório do clone do Flosum, que substitui os passos 4, 6, 6b e 7. O inventário seria a lista de arquivos e o XML viria do clone.
2. **Dados internos:** os arquivos exportados do Salesforce Inspector num diretório combinado, que substituem o passo 9. Cada consulta do Apêndice A do piloto teria um arquivo correspondente.
3. **Passos 8 e 10:** inalterados. Contratos, modelos, parsers e builders continuam os mesmos.

Regras do `CLAUDE.md` que o modo terá de manter:

- **Raw preservado (regras 2–4):** o clone e as exportações seriam o raw. O utilitário nunca os altera e registra caminho e sha256, como faz hoje com o retrieve.
- **Fonte identificada (regra 5):** a coluna "Fonte" precisaria distinguir "XML do repositório (Flosum)" de "XML recuperado da org", e "Objeto interno (export Salesforce Inspector)" de "Objeto interno (consulta)". Hoje `ALLOWED_SOURCES` não tem essas fontes.
- **Validação (regra 9):** o clone reflete o repositório, não necessariamente a org. Os documentos teriam de dizer de qual commit ou branch vieram.

### Perguntas em aberto para o plano

- [ ] Formato do clone Flosum: formato source do SFDX (`force-app/main/default/...`) ou formato metadata (`package.xml` + `src/`)? Qual branch ou commit representa produção?
- [ ] O clone inclui Profile, PermissionSet, PermissionSetGroup, SharingRules, Queue e CustomApplication completos? Sem eles, as seções "Acesso e configuração" ficariam "Não informado". Hoje o XML de perfil vem de um retrieve feito junto com os componentes; no repositório, o perfil pode estar parcial.
- [ ] Salesforce Inspector: quais consultas, em que formato de exportação (CSV ou JSON) e com que nome de arquivo por consulta? Quem executa e com qual perfil? Exportar a partir da produção é permitido?
- [ ] Como identificar a org de origem sem `sf org display` (`orgId`), já que hoje a aprovação depende dele (`approvedOrgs`)?
- [ ] Onde guardar o clone e as exportações (armazenamento aprovado, retenção, acesso)?

Enquanto o plano não for aprovado, o comportamento do MVP não muda: **todo `run` exige uma org autenticada e aprovada, e só deve ser usado em ambientes não produtivos.**
