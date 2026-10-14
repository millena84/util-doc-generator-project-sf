# Fase 2 — descoberta de integrações (`integration_discovery`)

Segundo módulo do repositório. Ele **não altera** o Utilitário 1 (`salesforce_docs`): só **lê** os JSONs normalizados que o Utilitário 1 já gerou e propõe quais componentes formam uma integração.

```text
CSV curado ──► JSON normalizado ──► referências ──► grafo ──► clusters CANDIDATE ──► propostas de nome ──► relatório
(usuária)      (inventory/**/normalized)  (data/codeBody)                          (revisão humana)
```

- Não acessa a org, não lê XML bruto, não lê Markdown.
- Toda relação tem evidência: arquivo, campo, caminho JSON e o texto casado.
- Todo cluster é `CANDIDATE` e todo nome é **proposta** até a revisão humana. Nenhum dossiê é gerado nesta fase.

## 1. Pré-requisito

Os componentes do CSV precisam ter sido processados pelo Utilitário 1 na mesma org e versão de API, por exemplo:

```bash
bin/sf-docs.sh run --group ApexClass --group ApexTrigger --group CustomObject --component IntegracaoRHService --component ColaboradorTrigger --component Colaborador__c --non-interactive
```

Assim existem os arquivos `inventory/org-<alias>/api-v<N>/<pasta>/normalized/<slug>.json`. O `<slug>` é o nome em minúsculas com separadores trocados por `-`: `IntegracaoRHService` vira `integracaorhservice.json` e `Colaborador__c` vira `colaborador-c.json`.

## 2. Preparar o CSV

Copie o exemplo e edite:

```bash
cp discovery/input/componentes-squad.example.csv discovery/input/componentes-squad.csv
```

| Coluna | Obrigatória | Conteúdo |
|---|---|---|
| `component_type` | sim | um de: `ConnectedApp`, `ExternalClientApp`, `NamedCredential`, `ExternalCredential`, `ApexClass`, `ApexTrigger`, `CustomObject`, `CustomMetadata`, `PermissionSet`, `RemoteSiteSetting`, `Certificate`, `SelfSignedCertificate`, `Flow`, `FlowDefinition` (maiúsculas não importam) |
| `component_name` | sim | `fullName` / nome de API (ex.: `Colaborador__c`, `Endpoint_Config__mdt`) |
| `squad_suspect` | sim | `true` ou `false` |
| `notes` | não | texto livre; use aspas se tiver vírgula |

```csv
component_type,component_name,squad_suspect,notes
ApexClass,IntegracaoRHService,true,Serviço de integração
ApexTrigger,ColaboradorTrigger,true,Trigger do objeto Colaborador
CustomObject,Colaborador__c,true,Objeto de colaborador
NamedCredential,RH_Endpoint,true,Endpoint do RH
```

Validação:
- O cabeçalho deve ter exatamente as 4 colunas, nesta ordem. Sem isso a execução para **sem alterar nenhuma saída anterior**.
- Uma linha inválida (tipo fora da lista, nome vazio, `squad_suspect` diferente de true/false) é ignorada e listada no relatório, com o número da linha e o motivo. O número é a linha física do arquivo, contando linhas em branco; para uma nota entre aspas em várias linhas, vale a linha onde o registro começa.
- Uma linha duplicada (mesmo tipo e nome) é ignorada com aviso.

## 3. Executar

```bash
bin/integration-discovery.sh --csv discovery/input/componentes-squad.csv --target-org dev --api-version 67.0
# equivalente:
PYTHONPATH=src python3 -m integration_discovery --csv discovery/input/componentes-squad.csv --target-org dev --api-version 67.0
```

- `--csv` relativo é resolvido a partir da **pasta atual**. Sem `--csv`, o padrão é `discovery/input/componentes-squad.csv` dentro da raiz do projeto.
- `--target-org` e `--api-version` só escolhem a pasta do inventário (`inventory/org-<alias>/api-v<N>`). Padrões: `orgAlias` e `defaultApiVersion` do `config.json`.
- **Retomada:** um componente cujo JSON normalizado (sha256), lista de componentes do CSV e regras não mudaram não é reprocessado; o cache fica em `discovery/state/`. `--no-cache` força tudo de novo.
- Componente sem JSON vira `NORMALIZED_JSON_NOT_FOUND` e a execução continua. Outros status: `NORMALIZED_JSON_INVALID` (JSON malformado) e `NORMALIZED_JSON_MISMATCH` (o arquivo é de outro componente ou tipo).

## 4. Ver o resultado

| Arquivo | Conteúdo |
|---|---|
| `discovery/report/discovery-report.md` | resumo, componentes sem JSON, clusters por número de evidências, relações com evidência, justificativa dos nomes, órfãos, menções não verificadas, erros do CSV, pendências |
| `discovery/clusters/cluster-NNN.json` | membros, relações, confiança, nome proposto, revisão humana, `signature` (composição) |
| `discovery/proposals/cluster-NNN.proposal.json` | 1 a 3 nomes, confiança e justificativa |
| `discovery/graphs/graph.json` | nós, arestas confirmadas, menções não verificadas e referências a componentes sem JSON |
| `discovery/orphans/orphans.json` | componentes sem relação confirmada (`ORPHAN`) |
| `discovery/report/component-status.json` | status de cada linha do CSV |

Essas saídas são derivadas da org e ficam no `.gitignore`.

### Como as relações são encontradas

- Para cada componente, todas as folhas de texto de `data` (e `codeBody`, se existir) são comparadas com os nomes do CSV:
  - nome exato, com fronteira de identificador e sensível a maiúsculas;
  - aceita `'Nome'`, `"Nome"`, `callout:Nome`, `Nome__c` e `Nome__mdt`;
  - nunca casa partes do nome.
- O tipo de relação vem de `config/integration-discovery-rules.json`: tipo de origem × tipo de destino, refinado pelo caminho JSON sem índices (`pathEndsWith` ou `pathRegex`). Vale a primeira regra que casar; combinação sem regra vira `REFERENCES`. Exemplos:
  - `ApexTrigger` → `CustomObject` em `data.apex.sObject`: `TRIGGERS_ON_OBJECT`;
  - `ApexClass` → `ApexClass` depende do campo: `apex.extends` é `EXTENDS_CLASS`; `apex.implements` é `IMPLEMENTS_INTERFACE`; tipos em `apex.methods`/`constructors` (assinatura, parâmetro, retorno) são `USES_TYPE`; `asyncInvocations`/`chainedJobs.targetClass` é `INVOKES_CLASS`; o resto é `REFERENCES_CLASS`;
  - `CustomObject` → `CustomObject` em `referenceTo` (campo lookup): `LOOKUP_TO_OBJECT`;
  - `Flow` → `CustomObject` em `start.object`: `TRIGGERS_ON_OBJECT`; `Flow` → `ApexClass` em `actionCalls.actionName`: `INVOKES_CLASS`.
- Evidência:
  - `CODE_REFERENCE`: fatos de código lidos pelo Utilitário 1 (`data.apex.*`) ou `codeBody`;
  - `CONFIGURATION_REFERENCE`: demais campos do XML;
  - `MANIFEST_REFERENCE`: vínculo pela estrutura do metadata (ver abaixo);
  - `UNVERIFIED`: texto livre (`description`, `errorMessage`, `inlineHelpText`), ou o mesmo nome em dois tipos do CSV sem dica no caminho. `UNVERIFIED` **não entra no grafo**: aparece só no relatório.
- **Relacionados lidos junto** (`discovery.relatedSources`, padrões em `settings.py`): JSONs que o Utilitário 1 grava ao lado do componente são lidos como parte dele. As referências achadas neles contam como do componente do CSV, com `relatedSource` indicando o arquivo de origem. Eles não viram nós do grafo e são listados no relatório ("Relacionados lidos junto") e em `component-status.json`.
  - **External Client App:** as políticas (`ExtlClntAppOauthSettings`, `ExtlClntAppConfigurablePolicies`, `ExtlClntAppOauthConfigurablePolicies`) cujo `externalClientApplication` é a ECA. Exemplo: `commaSeparatedPermissionSet` liga a ECA aos permission sets.
  - **CustomObject:** os filhos `<Objeto>.*` (CustomField, RecordType, ValidationRule, WebLink). Um lookup (`referenceTo`) liga a outro objeto do CSV.
  - **Custom Metadata:** o tipo (`X__mdt`), os seus records (`X.Registro`) e campos, para que um record que aponta para uma Named Credential gere `DEFINES_ENDPOINT`.
  - O `fullName` do relacionado (a identidade dele, ex.: campo `Empresa__c`) não é varrido, para não confundir com um objeto de mesmo nome.
- **Mesmo componente em dois tipos** (`discovery.sameNamePairs`): `Flow` e `FlowDefinition` com o mesmo nome no CSV são ligados por `HAS_DEFINITION` (evidência `MANIFEST_REFERENCE`, como o `SAME_FULL_NAME` do Utilitário 1). Uma menção ambígua entre os dois vai para o `Flow`, sem rebaixar a evidência (`ambiguityPreference` nas regras).
- `matchedText` guarda **só o nome casado**: o normalizado pode ter valores sensíveis (cabeçalhos de Named Credential, valores de Custom Metadata, `consumerKey`) e nenhum deles é copiado.

### Como os clusters são formados

- Componentes ligados direta ou indiretamente por arestas confirmadas, em qualquer sentido, formam um cluster.
- **Tipos ponte** (`discovery.bridgeTypes`, padrão `PermissionSet`) não unem clusters: cada ponte entra em todo cluster com que se liga. Um permission set que libera classes de duas integrações aparece nos dois clusters sem fundi-los. Por isso um componente pode estar em mais de um cluster.
- Confiança, contando relações distintas e sem as inversas:
  - `HIGH`: ≥ 3 relações, alguma `CODE_REFERENCE` e um componente de endpoint ou app;
  - `MEDIUM`: ≥ 2 relações, ou 1 relação com endpoint ou app;
  - `LOW`: os demais casos.
- `orphanComponents` de um cluster: órfãos cujo nome contém o termo dominante do cluster. É só dica de convenção de nome, nunca relação.

## 5. Aprovar ou rejeitar um cluster

```bash
bin/integration-discovery.sh review --cluster cluster-001 --decision APPROVED --by "Millena" --name "Integração RH - Admissões" --notes "confirmado com o time do RH"
bin/integration-discovery.sh review --cluster cluster-003 --decision REJECTED --by "Millena" --notes "permission set compartilhado"
bin/integration-discovery.sh review --cluster cluster-002 --decision PENDING          # volta para CANDIDATE
```

Números estáveis e histórico (`discovery/state/cluster-registry.json`):
- **O número segue a composição, não a ordem.** Cada composição de cluster (os seus membros, resumidos na `signature`) recebe um número uma única vez. Uma execução nova que reordena os clusters por evidência não muda os números: `cluster-002` continua sendo o mesmo conjunto de componentes.
- **Composição nova recebe o próximo número livre.** Quando um cluster muda de membros, o número antigo é **aposentado** e nunca é reutilizado por outra composição. Se a mesma composição voltar, o número volta a valer.
- **O `review` confere o número no registro antes de gravar.** Número aposentado é recusado com a indicação de onde os componentes estão agora (ex.: *"cluster-001 não existe mais (a composição mudou); os componentes dele agora estão em: cluster-004"*). Número inexistente também é recusado. `--signature <assinatura do relatório>` é uma confirmação opcional: se o cluster mudou desde o relatório lido, nada é gravado.
- **As decisões ficam num histórico que só cresce.** A decisão vigente de uma composição é a última revisão dela, e é copiada para `cluster-NNN.json` e para a proposta em toda execução.
- **Decisão de cluster aposentado continua no relatório** ("Revisões que não se aplicam mais"), com quem decidiu e a nota, até os clusters que receberam os componentes serem revisados.
- **Saídas de antes deste registro:** na primeira execução, os arquivos de cluster existentes são migrados com o mesmo número e a mesma decisão.

## 6. Próxima fase (não implementada)

Um cluster **aprovado** vira entrada para o mapa de integração (Fase 3). A proposta, a ser desenhada:
- ler só os clusters com `status = APPROVED`;
- usar as relações já com evidência para montar o fluxo (origem → objeto → trigger → classe → endpoint/credencial);
- reaproveitar os documentos Markdown do Utilitário 1 de cada membro como anexos;
- gerar o dossiê.

Nada disso é feito agora.

## 7. Limitações conhecidas

- **O normalizado do Utilitário 1 não guarda o corpo do código Apex.** Uma chamada `callout:RH_Endpoint` dentro de um método não aparece. A Named Credential só se liga ao cluster por outro caminho (Custom Metadata, ExternalCredential...) ou por um `codeBody` que o Utilitário 1 hoje não grava. Relação ausente não prova ausência.
- Só são vistas referências entre componentes **do CSV**. Um componente intermediário fora do CSV quebra a ligação e gera órfãos.
- A busca é sensível a maiúsculas. Em campos de XML, o Salesforce às vezes não diferencia maiúsculas; um nome escrito com outra caixa não casa.
- Nome de componente que é palavra comum (ex.: classe `Status`) pode casar em valores de configuração. A busca exige o nome inteiro, mas não sabe se o campo é uma referência.
- `SelfSignedCertificate` não é um metadata type separado no Utilitário 1 (certificados ficam em `Certificate`): essa linha do CSV sempre resulta em `NORMALIZED_JSON_NOT_FOUND`.
- `line` só é preenchida para `codeBody`; os campos de `data` não têm número de linha.
- As pastas dos relacionados (`extl-clnt-app-*`, `custom-objects`, `custom-metadata`) e o campo `externalClientApplication` seguem a saída atual do Utilitário 1 (conferida com a CLI simulada). Confirme com dados reais; se mudarem, ajuste `discovery.relatedSources` no `config.json`.
