# Como testar o MVP

Este guia diz **o que testar, onde e com qual roteiro**, conforme o ambiente. Comece pelo nível 1 e só suba de nível quando o anterior passar.

> ⚠️ **Restrição atual — ambientes produtivos:** por ora **não é permitido login** (`sf org login ...`) em org produtiva. O MVP atual **precisa** de login: todos os passos de coleta chamam a org pela Salesforce CLI. Portanto, **o MVP não deve ser executado contra produção**. O cenário produtivo previsto (nível 3) usa o projeto Salesforce de um **clone do repositório Flosum** e dados de objetos internos **exportados pelo Salesforce Inspector**. Esse modo **ainda não existe**: está descrito abaixo só como plano, para decisão. Nada no código foi alterado para ele.

| Nível | Ambiente | Login na org | Roteiro | Situação |
|---|---|---|---|---|
| 1 | Máquina local, sem org | Não | Seção 1 deste guia | Pronto |
| 2 | Org de desenvolvimento ou sandbox autorizada | Sim (não produtiva) | [`piloto-org-real.md`](piloto-org-real.md) | Pronto para o primeiro teste |
| 3 | Produção | **Não permitido** | Seção 3 deste guia (plano) | **Não implementado** |

## 0. Escolher os metadados a documentar

O utilitário documenta **só o que está configurado** em `config/metadata-types-mvp.json`: 37 grupos, um documento por componente (alguns por objeto ou por org). Tipos da org fora dessa lista não são documentados; o `resumo.md` os mostra em "Descobertos e não configurados".

### Como indicar o que documentar

| Forma | Onde | Quando usar |
|---|---|---|
| `--group <Grupo>` (repetível) | linha de comando | restringe a execução aos grupos informados |
| `--component <nome>` (repetível) | linha de comando | restringe aos componentes informados (vale para todos os `--group` do comando). **Use sempre no piloto:** sem ele, o modo `ALL` recupera os tipos inteiros |
| `selection.mode = "ALL"` | `config/config.json` | padrão: todos os grupos e todos os componentes encontrados na org |
| `selection.mode = "SELECTED"` + `metadataTypes` | `config/config.json` | lista fixa de tipos principais e componentes, revisável. **Não use no piloto:** o grupo PlatformEvent não é selecionável (achado ADD-09) |

Exemplo para um piloto de uma classe e um Flow:

```bash
bin/sf-docs.sh run --group ApexClass --group Flow --component PedidoService --component Meu_Flow --non-interactive
```

Depois da execução, confira na lista "Documentados" do `runs/<runId>/resumo.md` se todos os nomes pedidos aparecem. No modo `ALL`, nome digitado errado não gera aviso.

### Catálogo do MVP

Os exemplos de `--component` são os componentes das fixtures simuladas: troque pelos nomes de API da sua org. Formatos marcados *a confirmar* serão conferidos no piloto.

| Onda | `--group` | Tipo principal (`selection`) | Relacionados no mesmo documento | Exemplo de `--component` |
|---|---|---|---|---|
| MVP | `Certificate` | `Certificate` | — | `Meu_Certificado` |
| MVP | `ConnectedApp` | `ConnectedApp` | — | `Meu_App` |
| MVP | `CustomMetadata` | `CustomMetadata` | CustomField | `Config__mdt` (o tipo; os records vêm junto) |
| MVP | `CustomObject` | `CustomObject` | CustomField, RecordType, ValidationRule, WebLink | `Pedido__c` (só objetos `__c`; objetos padrão como `Account` ficam fora pelo `componentFilter`) |
| MVP | `ExternalClientApp` | `ExternalClientApplication` | ExtlClntAppOauthSettings, ExtlClntAppConfigurablePolicies, ExtlClntAppOauthConfigurablePolicies | `Minha_ECA` |
| MVP | `ExternalCredential` | `ExternalCredential` | — | `Minha_EC` |
| MVP | `Flow` | `Flow` | FlowDefinition | `Meu_Flow` (nome de API do Flow) |
| MVP | `NamedCredential` | `NamedCredential` | ExternalCredential | `Minha_NC` |
| MVP | `RemoteSiteSetting` | `RemoteSiteSetting` | — | `Meu_Site` |
| 01 | `ApexClass` | `ApexClass` | — | `PedidoService` (classes de pacote `ns__` ficam fora) |
| 02 | `ApexTrigger` | `ApexTrigger` | — | `PedidoTrigger` (`ns__` fica fora) |
| 03 | `LightningComponentBundle` | `LightningComponentBundle` | — | `pedidoPainel` (`ns__` fica fora) |
| 04 | `FlexiPage` | `FlexiPage` | — | `Pedido_Record_Page` (`ns__` fica fora) |
| 05 | `OrgSecurity` | `SecuritySettings` | — | `Security` (fixo) |
| 05 | `PermissionSet` | `PermissionSet` | — | `Leitura_Pedidos` |
| 05 | `PermissionSetGroup` | `PermissionSetGroup` | — | `PSG_Integracao` |
| 05 | `Profile` | `Profile` | — | `Admin` (nome do metadata, não o rótulo) |
| 05 | `PublicGroup` | `Group` | — | `Grupo_Suporte` |
| 05 | `Role` | `Role` | — | `Gerente_Vendas` |
| 05 | `SharingRules` | `SharingRules` | — | objeto: `Pedido__c` |
| 06 | `ChangeDataCapture` | `PlatformEventChannelMember` | — | nome do membro do canal (formato *a confirmar*) |
| 06 | `PlatformEvent` | `CustomObject` | CustomField | `Pedido_Evento__e` (só `__e`) |
| 07 | `AssignmentRules` | `AssignmentRules` | — | objeto: `Case` ou `Lead` |
| 07 | `AutoResponseRules` | `AutoResponseRules` | — | objeto: `Case` ou `Lead` |
| 07 | `EscalationRules` | `EscalationRules` | — | objeto: `Case` |
| 07 | `Queue` | `Queue` | — | `Fila_Pedidos` (DeveloperName) |
| 08 | `BusinessProcess` | `BusinessProcess` | RecordType | `Opportunity.Venda_Enterprise` (Objeto.Processo) |
| 08 | `LeadConvertSettings` | `LeadConvertSettings` | — | `LeadConvertSettings` (fixo) |
| 08 | `OpportunitySplitType` | `OpportunitySplitType` | — | `Receita_Principal` |
| 08 | `Territory2Model` | `Territory2Model` | Territory2, Territory2Rule | `Modelo_Vendas` |
| 09 | `CustomSite` | `CustomSite` | Network | `Portal_Clientes` |
| 09 | `ExperienceBundle` | `ExperienceBundle` | — | `Portal_Clientes1` |
| 09 | `Network` | `Network` | CustomSite | `Portal_Clientes` |
| 10 | `OmniDataTransform` | `OmniDataTransform` | — | `ExtrairPedido` (formato *a confirmar*) |
| 10 | `OmniIntegrationProcedure` | `OmniIntegrationProcedure` | — | `Pedido_EnviarERP_Procedure_1` (formato *a confirmar*) |
| 10 | `OmniScript` | `OmniScript` | — | `Vendas_CriarPedido_Portuguese_1` (formato *a confirmar*) |
| 10 | `OmniUiCard` | `OmniUiCard` | — | `CartaoPedido_1` (formato *a confirmar*) |

Componentes fixos (OrgSecurity e LeadConvertSettings) não são listados na org: informe o nome indicado. Os relacionados (coluna 4) não precisam de `--component`: vêm junto com o principal.

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

### 2.1 E se não puder rodar `sf data query`?

O `sf data query` é usado **só** no passo 9 (dados internos): uma consulta por componente, definida no contrato (lista no Apêndice A do piloto). Os passos de inventário, retrieve, acesso e Markdown não dependem dele.

Se a consulta falhar (sem permissão, objeto ou campo inexistente, comando bloqueado por política), **a execução continua**. Foi simulado com todas as consultas falhando nos 37 grupos (fixtures sem respostas de consulta):

| O que acontece | Resultado da simulação |
|---|---|
| Status da execução | `SUCCESS`, com cobertura `COMPLETE_WITH_WARNINGS` |
| Documentos | todos gerados (60 de 60) |
| Seção "Dados internos" (e "Registros na org" das regras de atendimento) | linha "Não informado", com fonte `Objeto interno` |
| Avisos | um `INTERNAL_DATA_UNAVAILABLE` por componente (55), no log, no run state e na lista "Dados internos indisponíveis" do `resumo.md` |
| Resposta de erro | gravada em `runs/<runId>/errors/internal-<pasta>-<componente>.sanitized.json` (com segredos mascarados) |

O que se **perde**, porque só existe na consulta:
- datas de criação e alteração, `Id`, versões e status das versões do Flow (a linha "Status" com fonte `Objeto interno` fica "Não informado"; o "Status (versão recuperada)" continua vindo do XML);
- `IsValid` e `LengthWithoutComments` do Apex e o uso por evento das triggers;
- padrões de acesso da org (`Organization.Default*Access`) no documento de segurança;
- registros das regras de atendimento (`AssignmentRule`, `AutoResponseRule`, `EscalationRule`);
- `State` e `ActivatedDate` do modelo de territórios, `Status` da Network e do Site, e os demais campos do Apêndice A.

Todo o resto vem do XML e não muda: propriedades, relacionados, código lido, acesso e configuração, índice entre componentes.

Exceções:
- **Sessão expirada** (`INVALID_SESSION_ID`) numa consulta **interrompe** a execução com `SESSION_EXPIRED`, como em qualquer outro passo. Retome com `run --resume latest` depois de novo login.
- Hoje não há opção global para pular o passo 9. As consultas são tentadas, falham e ficam registradas, e cada uma custa uma chamada à CLI. Desligar por contrato (`internalData.enabled = false`) é possível, mas muda os contratos: só com aprovação.

No cenário produtivo sem login (seção 3), essas consultas seriam substituídas por exportações do Salesforce Inspector. Até lá, a perda acima é o comportamento esperado.

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
