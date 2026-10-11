# Fixtures de teste (SIMULADAS)

Todos os arquivos desta pasta são **simulados** para testes automatizados.
Nenhum dado aqui veio de uma org real e nenhum deve ser usado como documentação.

- `bin/sf`: Salesforce CLI simulada (Python) usada pelos testes de pipeline.
- `org/`: respostas simuladas de `sf org list`, `sf org display` e `sf org list metadata-types`.
- `inventory/<Tipo>.json`: respostas simuladas de `sf org list metadata`.
- `source/`: XMLs em formato source usados pelo retrieve simulado.
- `query/<Objeto>.json`: respostas simuladas de `sf data query`.
- `mvp-complete/`: camada usada no cenário `mvp_complete` (`FAKE_SF_SCENARIO=mvp_complete`). Tem prioridade sobre as fixtures base e acrescenta componentes para os tipos que, na base, ficam sem componentes ou desabilitados (CorsWhitelistOrigin, RemoteSiteSetting, CspTrustedSite, ExtlClntApp*Policies, WebLink e dados internos de ExternalCredential). Os campos dos XMLs novos foram escolhidos de forma mínima e **ainda precisam ser conferidos na documentação oficial da Metadata API**.

O token em `org/org-display.json` é um valor fictício.
