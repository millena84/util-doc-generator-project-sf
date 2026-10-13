"""OmniStudio (Onda 10): DataRaptor, Integration Procedure, OmniScript e FlexCard.

Usa a CLI simulada e os XMLs SIMULADOS de tests/fixtures/source. O cabeçalho HTTP do Integration
Procedure tem um segredo SIMULADO e o FlexCard tem dado pessoal sentinela nos dados de exemplo:
nenhum dos dois pode aparecer nos documentos.
"""

import json
import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.omnistudio_parser import parse_data_transform, parse_omni_process, parse_ui_card
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

GROUPS = ["OmniDataTransform", "OmniIntegrationProcedure", "OmniScript", "OmniUiCard"]
PROCESS = """<OmniIntegrationProcedure xmlns="x"><type>T</type><subType>S</subType>
  <omniProcessElements><name>Bloco</name><type>Conditional Block</type><propertySetConfig>{}</propertySetConfig>
    <childElements><name>Chamada</name><type>Remote Action</type>
      <propertySetConfig>{"remoteClass": "MinhaClasse", "headers": {"token": "SEGREDO"}}</propertySetConfig></childElements>
  </omniProcessElements>
  <omniProcessElements><name>Ruim</name><type>Set Values</type><propertySetConfig>{nao json</propertySetConfig></omniProcessElements>
</OmniIntegrationProcedure>"""


class OmniParsersTest(unittest.TestCase):
    def test_process_elements_nested_references_and_no_config_text(self):
        r = parse_omni_process(PROCESS)
        self.assertNotIn("SEGREDO", json.dumps(r))
        self.assertEqual(r["procedureKey"], "T_S")
        self.assertEqual([(e["order"], e["name"], e["parent"]) for e in r["elements"]],
                         [(1, "Bloco", None), (2, "Chamada", "Bloco"), (3, "Ruim", None)])
        self.assertEqual(r["apexClasses"], ["MinhaClasse"])
        self.assertEqual(r["elements"][2]["config"], "não lida (JSON inválido)")

    def test_data_transform_read_and_written_objects(self):
        item = "<omniDataTransformItem><inputObjectName>A</inputObjectName><outputObjectName>B</outputObjectName></omniDataTransformItem>"
        extract = parse_data_transform(f'<OmniDataTransform xmlns="x"><type>Extract</type>{item}</OmniDataTransform>')
        load = parse_data_transform(f'<OmniDataTransform xmlns="x"><type>Load</type>{item}</OmniDataTransform>')
        self.assertEqual((extract["objectsRead"], extract["objectsWritten"]), (["A"], []))
        self.assertEqual((load["objectsRead"], load["objectsWritten"]), ([], ["B"]))

    def test_ui_card_source_actions_and_no_sample_data(self):
        ds = json.dumps({"type": "DataRaptor", "value": {"bundle": "DR"}})
        props = json.dumps({"x": [{"actionList": [{"label": "Rodar", "stateAction": {"type": "IntegrationProcedure",
                                                                                      "ipMethod": "T_S"}}]}]})
        r = parse_ui_card(f'<OmniUiCard xmlns="x"><dataSourceConfig>{ds}</dataSourceConfig>'
                          f'<propertySetConfig>{props}</propertySetConfig>'
                          '<sampleDataSourceResponse>[{"Email": "p@example.invalid"}]</sampleDataSourceResponse></OmniUiCard>')
        self.assertNotIn("@", json.dumps(r))
        self.assertEqual((r["dataSourceType"], r["dataSource"]), ("DataRaptor", "DataRaptor DR"))
        self.assertEqual(r["actions"], [{"label": "Rodar", "type": "IntegrationProcedure",
                                         "references": "Integration Procedure T_S"}])
        self.assertEqual([(x["name"], x["element"]) for x in r["references"]], [("DR", "Fonte de dados"), ("T_S", "Rodar")])

    def test_invalid_xml(self):
        for fn in (parse_omni_process, parse_data_transform, parse_ui_card):
            self.assertFalse(fn("<x>")["parsed"])


class OmniDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=GROUPS)

    def doc(self, name):
        e = self.primary(self.state, name)
        self.assertEqual(e["status"], st.SUCCESS, name)
        return self.read(e["document"])

    def test_no_secret_config_or_personal_data(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        for c in self.state.data["components"]:
            if c.get("role") == "primary" and c.get("document"):
                text = self.read(c["document"])
                for forbidden in ("SEGREDO_SIMULADO", "Sentinela", "@example.invalid", "propertySetConfig",
                                  "sampleDataSourceResponse", "Bearer"):
                    self.assertNotIn(forbidden, text, c["unitId"])

    def test_data_raptor(self):
        doc = self.doc("ExtrairPedido")
        self.assertIn("| 1 | Pedido__c | Id | Não informado | Pedido | = PedidoId | Não informado | XML |", doc)
        self.assertIn("| 3 | Account | Name | Não informado | Conta:Nome | Não informado | Sim | XML |", doc)
        self.assertNotIn("ROUND(", doc)                         # fórmula não é reproduzida
        self.assertIn("| Pedido_EnviarERP_Procedure_1 | Integration Procedure | DR_ExtrairPedido | XML |", doc)
        self.assertIn("| Perfil | Vendas | Ler | Objeto lido Pedido__c | XML |", doc)

    def test_integration_procedure(self):
        doc = self.doc("Pedido_EnviarERP_Procedure_1")
        self.assertIn("| Type_SubType | Pedido_EnviarERP | Derivado |", doc)
        self.assertIn("| 2 | HTTP_EnviarERP | Rest Action | 0 | Não informado | true | Named Credential Minha_NC | XML |", doc)
        self.assertIn("| Vendas_CriarPedido_Portuguese_1 | OmniScript | IP_Enviar | XML |", doc)
        self.assertIn("| CartaoPedido_1 | FlexCard | Reenviar | XML |", doc)
        self.assertIn("| Perfil | Vendas | Executar | Classe Apex PedidoService | XML |", doc)
        self.assertIn("| UniqueName | Pedido_EnviarERP_Procedure_1 | Objeto interno |", doc)

    def test_omniscript_and_flexcard(self):
        doc = self.doc("Vendas_CriarPedido_Portuguese_1")
        self.assertIn("| 2 | Texto_Ajuda | Text Block | 1 | Passo_Cliente | true |", doc)
        self.assertIn("| Integration Procedure | Pedido_EnviarERP | IP_Enviar | XML |", doc)
        card = self.doc("CartaoPedido_1")
        self.assertIn("| Fonte de dados | Integration Procedure Pedido_EnviarERP | XML |", card)
        self.assertIn("| Detalhes | Flyout | Não informado | XML |", card)

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "ExtrairPedido")["document"])
        self.assertIn("| Vendas_CriarPedido_Portuguese_1 | OmniScript | DR_Carregar | XML |", doc)


if __name__ == "__main__":
    unittest.main()
