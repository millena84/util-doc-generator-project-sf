# Checklist: documentar a estrutura de acessos a partir dos repositórios clonados

Para documentar **roles, profiles, permission sets, permission set groups e OWD** de duas orgs a partir das pastas `Org01Repo` e `Org02Repo` (clones do Flosum já feitos). Sem login e sem Salesforce CLI: o utilitário só lê as pastas e nunca as altera.

Marque cada item ao concluir. Se algum passo falhar, anote o passo, a mensagem e o `runId`, e **não cole conteúdo dos documentos** no relato.

## A. Preparar a máquina (uma vez)

- [ ] `python3 --version` mostra 3.8 ou mais (Windows: `python --version`)
- [ ] Utilitário atualizado: `cd util-doc-generator-project-sf && git checkout main && git pull`
- [ ] `bin/sf-docs.sh validate-config --strict` termina com "Configuração válida."

## B. Cadastrar as duas pastas (de-para pasta → org)

- [ ] Anotar o caminho completo de cada pasta:
  - Org01Repo: `________________________________`
  - Org02Repo: `________________________________`
- [ ] Em `config/config.json`, preencher `sourceRepositories` com o nome de cada org:

  ```json
  "sourceRepositories": [
    { "folder": "Org01Repo", "orgName": "<nome da org 01>" },
    { "folder": "Org02Repo", "orgName": "<nome da org 02>" }
  ]
  ```

- [ ] `bin/sf-docs.sh validate-config` mostra as duas linhas "Repositório (modo pasta): ... -> org ..."
- [ ] Conferir que cada pasta tem as subpastas `roles`, `profiles`, `permissionsets`, `permissionsetgroups`, `sharingRules`, `objects` e `settings` (direto na pasta, em `src/` ou em `force-app/main/default/`). Se estiverem em outro lugar, informar `"metadataPath": "<subpasta>"` no de-para.

## C. Gerar a documentação da Org01

- [ ] Rodar:

  ```bash
  bin/sf-docs.sh run --source-dir /caminho/Org01Repo \
    --group Role --group Profile --group PermissionSet --group PermissionSetGroup \
    --group OrgSecurity --group SharingRules --group CustomObject --group PublicGroup
  ```

  Sem Bash (Windows): `set PYTHONPATH=src` e `python -m salesforce_docs run --source-dir C:\caminho\Org01Repo --group Role ...` (mesmos `--group`).
- [ ] O terminal mostra "Modo pasta: repositório Org01Repo (org: ...)" logo no início
- [ ] A última linha não tem "ERRO"; a linha "Execução ... finalizada" mostra `SUCCESS`
- [ ] Abrir `runs/<runId>/resumo.md`:
  - [ ] **Status** `SUCCESS` e "Com falha (0)"
  - [ ] Seção "Origem (modo pasta, sem login)" com a pasta e o nome da org corretos
  - [ ] Cobertura `COMPLETE_WITH_WARNINGS` é esperada: os avisos são "Dados internos indisponíveis" (não há consulta à org)

## D. Conferir os documentos da Org01 (`saida/docs/doc-org01repo-<MMDDAA>/`)

- [ ] Todo documento começa com "**Origem:** repositório `Org01Repo` (org: ...)"
- [ ] **Roles:** um `doc-<papel>-role.md` por arquivo da pasta `roles`; a seção "Hierarquia" mostra os papéis acima e os subordinados
- [ ] **Profiles:** um `doc-<perfil>-profile.md` por arquivo da pasta `profiles`; no do Admin, as tabelas de objetos, campos e permissões de sistema estão preenchidas
- [ ] **Permission sets:** um `doc-<ps>-permission-set.md` por arquivo da pasta `permissionsets`
- [ ] **Permission set groups:** um `doc-<psg>-permission-set-group.md` por arquivo; a lista de permission sets incluídos está preenchida
- [ ] **OWD:** em `doc-security-org-security.md`, a tabela "Padrão de compartilhamento por objeto (OWD)" lista os objetos (padrão e customizados) que estão na pasta `objects`
- [ ] **Regras de compartilhamento:** um `doc-<objeto>-sharing-rules.md` por arquivo da pasta `sharingRules`, com o OWD do objeto
- [ ] Toda linha de tabela tem a coluna "Fonte" preenchida
- [ ] Linhas "Não informado" na seção "Dados internos" são esperadas

## E. Gerar e conferir a Org02

- [ ] Repetir o C com `--source-dir /caminho/Org02Repo`
- [ ] Repetir o D em `saida/docs/doc-org02repo-<MMDDAA>/`

## F. Proteção dos dados

- [ ] As pastas `Org01Repo` e `Org02Repo` não foram alteradas (`git status` dentro de cada uma, se forem repositórios Git: nada modificado)
- [ ] **Não fazer commit** de `saida/`, `inventory/`, `catalog/` nem `runs/` (descrevem orgs reais). Conferir com `git status` antes de qualquer commit no utilitário
- [ ] Revisar antes de versionar a alteração do `config/config.json` (ela contém os nomes das orgs)
- [ ] Não enviar os documentos para fora do ambiente aprovado

## O que este modo não traz

- **Dados internos** (IDs, datas, padrões da `Organization`): só existem na org e ficam "Não informado".
- **Usuários atribuídos** a perfis, permission sets e grupos, e membros de grupos: nunca são documentados (proteção de dados).
- O repositório mostra o que foi versionado. Se um perfil estiver parcial no repositório, o documento também estará.
