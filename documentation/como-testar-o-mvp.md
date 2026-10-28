# Como testar o MVP

Este guia diz **o que testar, onde e com qual roteiro**, conforme o ambiente. Comece pelo nível 1 e só suba de nível quando o anterior passar.

> ⚠️ **Restrição atual — ambientes produtivos:** por ora **não é permitido login** (`sf org login ...`) em org produtiva. Para produção, use o **modo pasta** (nível 3): o utilitário lê o repositório já clonado (ex.: Flosum), sem login e sem Salesforce CLI. Dados internos exportados pelo Salesforce Inspector ainda não são lidos.

| Nível | Ambiente | Login na org | Roteiro | Situação |
|---|---|---|---|---|
| 1 | Máquina local, sem org | Não | Seção 1 deste guia | Pronto |
| 2 | Org de desenvolvimento ou sandbox autorizada | Sim (não produtiva) | [`piloto-org-real.md`](piloto-org-real.md) | Pronto para o primeiro teste |
| 3 | Produção (repositório clonado) | **Não** | Seção 3 deste guia e [`checklist-acessos-modo-pasta.md`](checklist-acessos-modo-pasta.md) | Pronto (sem dados internos) |

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

No modo pasta (seção 3) as consultas não são feitas e a perda acima é o comportamento esperado. Exportações do Salesforce Inspector poderão substituí-las no futuro (pendente de aprovação).

## 3. Nível 3 — produção sem login: modo pasta

Implementado em 2026-10-28. O utilitário lê os metadados de um **repositório já clonado** (ex.: Flosum), sem login e sem Salesforce CLI. O clone é feito antes, fora do utilitário. Checklist passo a passo para documentar acessos: [`checklist-acessos-modo-pasta.md`](checklist-acessos-modo-pasta.md).

### Como funciona

| Passo do `run` | Modo com login | Modo pasta (`--source-dir`) |
|---|---|---|
| 1–3c (CLI, org, aprovação, token) | Salesforce CLI | Não feitos. A pasta só é lida se estiver no de-para `sourceRepositories` (pasta → nome da org) |
| 4 (tipos) | `sf org list metadata-types` | Tipos com pasta configurada em `sourceDirectory` |
| 5 (`describeValueType`) | Metadata API | Não feito: sem ele, valor ausente fica "Não informado" (nunca "Não aplicável") |
| 6 (inventário) | `sf org list metadata` | Arquivos do repositório |
| 6b e 7 (retrieve) | `sf project retrieve start` | Cópia byte a byte dos arquivos do repositório para `inventory/.../components/` |
| 8 e 10 (normalização e Markdown) | Local | **Iguais** (mesmos contratos, modelos e parsers) |
| 9 (dados internos) | `sf data query` | Não feito: "Não informado" |

Regras do `CLAUDE.md` mantidas:

- **Raw preservado (regras 2–4):** o repositório nunca é alterado. `catalog/org-<alias>/api-v<N>/source-manifest.json` registra caminho e sha256 de cada arquivo lido. No formato metadata, o `.object` é copiado intacto em `components/_repositorio/` e separado em objeto + filhos (campos, record types...) como arquivos derivados (`derived: true`).
- **Fonte identificada (regra 5):** a coluna "Fonte" continua `XML` (o dado é o XML do componente); a origem fica no topo de cada documento, logo abaixo do título ("**Origem:** repositório `Org01Repo` (org: **Nome da org**)..."). A retomada reprocessa tudo se o conteúdo do repositório mudou.
- **Nada inventado (regra 1):** pasta e sufixo de cada tipo vêm do Metadata API Developer Guide (seção *File Suffix and Directory Location*) e estão em `config/metadata-types-mvp.json` → `sourceDirectory`.

Formatos aceitos (detectados sozinhos): **source** do SFDX (`profiles/Admin.profile-meta.xml`, `objects/Conta/fields/...`) e **metadata** da Metadata API (`profiles/Admin.profile`, campos dentro de `objects/Conta.object`). Não precisa de `sfdx-project.json` nem de `package.xml`. A pasta de metadados é procurada em `.`, `src` e `force-app/main/default`; em outro lugar, informe `metadataPath` no de-para.

Só no modo pasta, o grupo CustomObject inclui **objetos padrão** (ex.: Account), para o OWD deles (`sharingModel` do XML) aparecer nos documentos de segurança da org e de regras de compartilhamento (`sourceDirectoryComponentFilter`). No modo com login continua só `__c`.

### Limites

- O repositório reflete o que foi versionado, não necessariamente a org: perfis parciais no repositório geram documentos parciais.
- Dados internos (versões de Flow, datas, `IsValid` do Apex, padrões da `Organization`...) ficam "Não informado". Ver a lista do que se perde na seção 2.1.

### Pendente (não implementar sem aprovação)

Dados internos a partir de exportações do **Salesforce Inspector** num diretório (substituiriam o passo 9). Perguntas em aberto:

- [ ] Quais consultas (Apêndice A do piloto), em que formato (CSV ou JSON) e com que nome de arquivo por consulta?
- [ ] Quem exporta e com qual perfil? Exportar a partir da produção é permitido?
- [ ] Onde guardar as exportações (armazenamento aprovado, retenção, acesso)?
