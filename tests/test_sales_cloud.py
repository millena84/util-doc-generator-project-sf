"""Sales Cloud (Onda 08): processo de negócio, conversão de Lead, territórios e split type.

Usa a CLI simulada e os XMLs SIMULADOS de tests/fixtures/source.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.extraction.internal_data_extractor import build_query
from salesforce_docs.parsing.sales_parser import parse_business_process, parse_lead_convert
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

GROUPS = ["BusinessProcess", "LeadConvertSettings", "Territory2Model", "OpportunitySplitType"]


class SalesParsersTest(unittest.TestCase):
    def test_business_process_values_and_default(self):
        r = parse_business_process('<BusinessProcess xmlns="x"><values><fullName>A</fullName><default>false</default>'
                                   '</values><values><fullName>B</fullName><default>true</default></values></BusinessProcess>')
        self.assertEqual([(v["order"], v["value"]) for v in r["values"]], [(1, "A"), (2, "B")])
        self.assertEqual(r["defaultValue"], "B")

    def test_lead_convert_pairs_and_field_names(self):
        r = parse_lead_convert('<LeadConvertSettings xmlns="x"><objectMapping><inputObject>Lead</inputObject>'
                               '<mappingFields><inputField>F__c</inputField><outputField>G__c</outputField></mappingFields>'
                               '<outputObject>Contact</outputObject></objectMapping></LeadConvertSettings>')
        self.assertEqual(r["fieldMappings"][0], {"sourceObject": "Lead", "sourceField": "F__c", "targetObject": "Contact",
                                                 "targetField": "G__c", "element": "objectMapping/mappingFields"})
        self.assertEqual((r["sourceFieldNames"], r["targetFieldNames"]), (["Lead.F__c"], ["Contact.G__c"]))

    def test_query_placeholders_for_object_dot_name(self):
        q = build_query("WHERE Name = '{shortName}' AND TableEnumOrId = '{objectName}'", "Opportunity.Venda")
        self.assertEqual(q, "WHERE Name = 'Venda' AND TableEnumOrId = 'Opportunity'")
        self.assertEqual(build_query("'{shortName}' '{objectName}'", "Sem_Ponto"), "'Sem_Ponto' ''")


class SalesDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=GROUPS)

    def doc(self, name):
        e = self.primary(self.state, name)
        self.assertEqual(e["status"], st.SUCCESS, name)
        return self.read(e["document"])

    def test_business_process_record_types_and_access(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        doc = self.doc("Opportunity.Venda_Enterprise")
        self.assertIn("| Valor padrão | Prospecting | XML |", doc)
        self.assertIn("| 3 | Closed Won | false | XML |", doc)
        self.assertIn("| Opportunity.Enterprise | Enterprise | true | XML |", doc)
        self.assertNotIn("Opportunity.Varejo", doc)          # outro processo
        self.assertIn("| Perfil | Admin | Visível | RecordType Opportunity.Enterprise | XML |", doc)
        self.assertIn("| TableEnumOrId | Opportunity | Objeto interno |", doc)
        calls = self.calls()
        self.assertIn("org list metadata --metadata-type RecordType", calls)
        self.assertNotIn("RecordType:Pedido__c.Padrao", calls)  # outro objeto: nem é recuperado

    def test_lead_convert(self):
        doc = self.doc("LeadConvertSettings")
        self.assertIn("| opportunityCreationOptions | VisibleOptional | XML |", doc)
        self.assertIn("| Lead | Orcamento__c | Opportunity | Amount | XML |", doc)
        self.assertIn("| Perfil | Vendas | Habilitada | Permissão de sistema ConvertLeads | XML |", doc)
        self.assertIn("| Perfil | Admin | Ler, Editar | Campo de destino Account.CNPJ__c | XML |", doc)
        self.assertIn("--metadata LeadConvertSettings:LeadConvertSettings", self.calls())

    def test_territory_model(self):
        doc = self.doc("Modelo_Vendas")
        self.assertIn("| Modelo_Vendas.Sudeste | Brasil Sudeste | Regional |", doc)
        self.assertIn("| Edit | Read | Read | inherited=false, ruleName=Regra_SP | XML |", doc)
        self.assertIn("| Modelo_Vendas.Regra_SP | true | Account | 1 | field=Account.BillingState, operation=equals, "
                      "value=SP | XML |", doc)
        self.assertNotIn("Outro_Modelo", doc)                   # território de outro modelo
        self.assertIn("| Perfil | Admin | Habilitada | Permissão de sistema ManageTerritories | XML |", doc)

    def test_opportunity_split_type(self):
        doc = self.doc("Receita_Principal")
        self.assertIn("| splitField | Amount | XML |", doc)
        self.assertIn("| isTotalValidated | true | XML |", doc)
        self.assertNotIn("{{", doc)

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "Opportunity.Venda_Enterprise")["document"])
        self.assertIn("| Opportunity.Enterprise | Enterprise | true | XML |", doc)


if __name__ == "__main__":
    unittest.main()
