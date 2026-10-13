"""Páginas Lightning — FlexiPage (Onda 04): parser, documento, ativação e uso no LWC.

Usa a CLI simulada e as páginas SIMULADAS de tests/fixtures/source/flexipages.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.flexipage_parser import component_kind, parse_flexipage
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexiPage xmlns="http://soap.sforce.com/2006/04/metadata">
  <flexiPageRegions>
    <itemInstances><componentInstance>
      <componentInstanceProperties><name>flowName</name><value>Meu_Flow</value></componentInstanceProperties>
      <componentName>flowruntime:interview</componentName><identifier>f1</identifier>
      <visibilityRule><criteria><leftValue>$Permission.CustomPermission.Ver_Flow</leftValue>
        <operator>EQUAL</operator><rightValue>true</rightValue></criteria></visibilityRule>
    </componentInstance></itemInstances>
    <name>main</name><type>Region</type>
  </flexiPageRegions>
  <flexiPageRegions>
    <componentInstances><componentName>c:velho</componentName><identifier>c1</identifier></componentInstances>
    <name>side</name><type>Region</type>
  </flexiPageRegions>
  <template><name>flexipage:t</name></template>
  <type>AppPage</type>
</FlexiPage>"""


class FlexiPageParserTest(unittest.TestCase):
    def test_flattens_both_formats_and_references(self):
        r = parse_flexipage(XML)
        self.assertTrue(r["parsed"])
        self.assertEqual(r["template"], "flexipage:t")
        self.assertEqual([(c["region"], c["componentName"]) for c in r["components"]],
                         [("main", "flowruntime:interview"), ("side", "c:velho")])
        self.assertEqual(r["flows"], ["Meu_Flow"])
        self.assertEqual(r["projectComponents"], ["velho"])
        self.assertEqual(r["customPermissions"], ["Ver_Flow"])  # sem {! }
        self.assertEqual(r["visibility"][0]["context"], "Permission")

    def test_component_kinds_and_invalid_xml(self):
        self.assertEqual(component_kind("force:highlightsPanel"), "Componente da plataforma")
        self.assertEqual(component_kind("acme:painel"), "Componente de namespace (acme)")
        self.assertFalse(parse_flexipage("<FlexiPage>")["parsed"])


class FlexiPageDocumentTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=["FlexiPage", "LightningComponentBundle", "CustomObject"])

    def doc(self, name):
        e = self.primary(self.state, name)
        self.assertEqual(e["status"], st.SUCCESS, name)
        return self.read(e["document"])

    def test_record_page_document(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        doc = self.doc("Pedido_Record_Page")
        self.assertIn("| Type | RecordPage | XML |", doc)
        self.assertIn("| Template | flexipage:recordHomeTemplateDesktop | XML |", doc)
        self.assertIn("| Facet-detalhes | Facet |", doc)
        self.assertIn("| sidebar | c:pedidoPainel | c_pedidoPainel | Componente do projeto (c:) | Sim | XML |", doc)
        self.assertIn("| sidebar | pkg:painelExterno | pkg_painelExterno | Componente de namespace (pkg) |", doc)
        self.assertIn("| Facet-detalhes | Record.Valor__c | RecordValor_cField | Sim | XML |", doc)
        self.assertIn("| c_pedidoPainel | c:pedidoPainel | titulo | Pedidos do cliente | XML |", doc)
        self.assertIn("| c_pedidoPainel | Permission | {!$Permission.CustomPermission.Aprova_Pedido} | EQUAL | true | "
                      "1 AND 2 | XML |", doc)
        self.assertIn("| Tela_Cadastro | XML |", doc)
        self.assertIn("| Type | RecordPage | Objeto interno |", doc)
        self.assertNotIn("{{", doc)

    def test_activation_levels_first(self):
        access = self.doc("Pedido_Record_Page").split("## Acesso e configuração", 1)[1]
        rows = [ln for ln in access.splitlines() if ln.startswith("| ") and ln.endswith("| XML |")]
        self.assertEqual(rows[:3], [
            "| Padrão da org | Pedido__c | Ativada (View, Large) | Objeto Pedido__c | XML |",
            "| Padrão do app | Vendas | Ativada (View, Large) | Objeto Pedido__c | XML |",
            "| App + perfil | Vendas | Ativada (View, Large) | Objeto Pedido__c; Perfil Vendas; "
            "Record type Pedido__c.Padrao | XML |"])
        self.assertIn("| Permission Set | Integracao_API | Habilitada | Custom Permission Aprova_Pedido (visibilidade) |",
                      access)

    def test_app_page_old_format_not_activated(self):
        doc = self.doc("Pedidos_App_Page")
        self.assertIn("| main | c:pedidoPainel | c_pedidoPainel_app | Componente do projeto (c:) | Sim | XML |", doc)
        self.assertIn("| c_pedidoPainel_app | Client | {!$Client.formFactor} | EQUAL | Large |", doc)
        self.assertIn("| Página não ativada nos componentes processados |", doc.split("## Acesso e configuração", 1)[1])

    def test_lwc_document_lists_pages(self):
        usage = self.doc("pedidoPainel").split("## Onde é usado (páginas Lightning)", 1)[1].split("## ", 1)[0]
        self.assertIn("| Pedido_Record_Page | RecordPage | sidebar | c_pedidoPainel | Sim | XML |", usage)
        self.assertIn("| Pedidos_App_Page | AppPage | main | c_pedidoPainel_app | Sim | XML |", usage)
        other = self.doc("pedidoAcaoRapida").split("## Onde é usado (páginas Lightning)", 1)[1].split("## ", 1)[0]
        self.assertIn("Nenhuma página processada nesta execução usa o componente", other)
        self.assertIn("--metadata CustomApplication", self.calls())

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "Pedido_Record_Page")["document"])
        self.assertIn("| Padrão da org | Pedido__c | Ativada (View, Large) |", doc)
        self.assertIn("| App + perfil | Vendas |", doc)
        lwc = self.read(self.primary(state, "pedidoPainel")["document"])
        self.assertIn("| Pedido_Record_Page | RecordPage | sidebar |", lwc)


class FlexiPageWithoutObjectTest(P3Base):
    def test_org_default_needs_custom_object(self):
        code, state = self.run_pipeline(groups=["FlexiPage"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        access = self.read(self.primary(state, "Pedido_Record_Page")["document"]).split("## Acesso e configuração", 1)[1]
        self.assertNotIn("Padrão da org", access)   # CustomObject fora do escopo
        self.assertIn("| Padrão do app | Vendas |", access)


if __name__ == "__main__":
    unittest.main()
