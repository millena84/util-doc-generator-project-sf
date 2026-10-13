"""Documentos de Lightning Web Component (Onda 03): parser do bundle, subdocumentos e acesso.

Usa a CLI simulada e os bundles SIMULADOS de tests/fixtures/source/lwc.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.lwc_parser import neutralize_js, parse_lwc_bundle
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

META = """<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>67.0</apiVersion>
    <isExposed>true</isExposed>
    <targets><target>lightning__FlowScreen</target><target>lightning__RecordAction</target></targets>
    <targetConfigs>
        <targetConfig targets="lightning__FlowScreen">
            <property name="valor" type="Integer" role="inputOnly"/>
            <property name="semApi" type="String"/>
        </targetConfig>
        <targetConfig targets="lightning__RecordAction"><actionType>Action</actionType></targetConfig>
    </targetConfigs>
</LightningComponentBundle>"""


class LwcParserTest(unittest.TestCase):
    def parse(self, js, html="<template></template>", extra=None):
        files = {"x.js": js, "x.html": html, "x.js-meta.xml": META}
        files.update(extra or {})
        return parse_lwc_bundle(files)

    def test_comments_and_strings_are_not_evidence(self):
        code, literals = neutralize_js("a('x // y'); // import z from 'c/z';\n/* new CustomEvent('k') */ b(\"q\");")
        self.assertNotIn("import", code)
        self.assertNotIn("CustomEvent", code)
        self.assertEqual(literals, ["x // y", "q"])

    def test_apex_imports_usage_and_permissions(self):
        r = self.parse(
            "import { LightningElement, api, wire } from 'lwc';\n"
            "import buscar from '@salesforce/apex/ns.Ctrl.buscar';\n"
            "import salvar from '@salesforce/apex/Ctrl.salvar';\n"
            "import sobra from '@salesforce/apex/Ctrl.sobra';\n"
            "import PERM from '@salesforce/customPermission/Pode_Salvar';\n"
            "import VIEW from '@salesforce/userPermission/ViewSetup';\n"
            "export default class X extends LightningElement {\n"
            " @api valor; @api invoke() {} @api get rotulo() { return 1; }\n"
            " @wire(buscar) dados;\n connectedCallback() { super.connectedCallback(); salvar({}); }\n}")
        apex = {a["method"]: a for a in r["apexMethods"]}
        self.assertEqual(apex["buscar"]["className"], "ns.Ctrl")
        self.assertEqual(apex["buscar"]["usage"], "@wire")
        self.assertEqual(apex["salvar"]["usage"], "imperativo")
        self.assertEqual(apex["sobra"]["usage"], "importado, uso não detectado")
        self.assertEqual(r["customPermissions"], ["Pode_Salvar"])
        self.assertIn({"kind": "User Permission", "name": "ViewSetup"}, r["permissionChecks"])
        self.assertEqual({a["name"]: a["kind"] for a in r["apiMembers"]},
                         {"valor": "propriedade", "invoke": "método", "rotulo": "getter/setter"})
        self.assertEqual(r["lifecycleHooks"], ["connectedCallback"])

    def test_target_config_attributes_and_checks(self):
        r = self.parse("import { api } from 'lwc';\nexport default class X { @api valor; @api invoke() {} }")
        props = {p["name"]: p for p in r["flowScreen"]["properties"]}
        self.assertEqual(props["valor"]["roleText"], "inputOnly")
        self.assertEqual(props["semApi"]["roleText"], "entrada e saída (role ausente)")
        self.assertEqual((props["valor"]["hasApi"], props["semApi"]["hasApi"]), ("Sim", "Não"))
        self.assertEqual(r["quickAction"]["actionType"], "Action")
        self.assertEqual(r["quickAction"]["headlessCheck"], "Atende: @api invoke() declarado")
        r = self.parse("export default class X {}")
        self.assertEqual(r["quickAction"]["headlessCheck"], "Não atende: actionType Action sem @api invoke()")

    def test_html_children_and_lds(self):
        r = self.parse("", html="<template><!-- <c-falso></c-falso> --><c-meu-filho></c-meu-filho>"
                                "<lightning-record-form></lightning-record-form></template>")
        comm = [(c["kind"], c["name"]) for c in r["communication"]]
        self.assertEqual(comm, [("Componente filho (HTML)", "c/meuFilho")])
        self.assertIn("lightning-record-form", [d["name"] for d in r["dataAccess"]])

    def test_jest_tests_ignored_and_missing_meta(self):
        r = self.parse("", extra={"__tests__/x.test.js": "import a from '@salesforce/apex/T.m';"})
        self.assertEqual(r["apexMethods"], [])
        self.assertNotIn("__tests__/x.test.js", [f["path"] for f in r["files"]])
        self.assertFalse(parse_lwc_bundle({"x.js": ""})["parsed"])


class LwcDocumentTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=["LightningComponentBundle", "ApexClass"])

    def entry(self, name):
        return self.primary(self.state, name)

    def doc(self, name):
        return self.read(self.entry(name)["document"])

    def subdoc(self, name, suffix):
        return self.read(next(s["document"] for s in self.entry(name)["subDocuments"]
                              if s["document"].endswith(f"-{suffix}.md")))

    def test_documents_and_subdocuments(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        expected = {"pedidoPainel": [], "pedidoAcaoRapida": ["lwc-quick-action"],
                    "pedidoTelaFlow": ["lwc-flow-screen"]}
        for name, subs in expected.items():
            e = self.entry(name)
            self.assertEqual(e["status"], st.SUCCESS, name)
            self.assertTrue(e["document"].endswith(f"doc-{name.lower()}-lwc.md"))
            self.assertEqual([s["document"].rsplit(f"{name.lower()}-", 1)[1][:-3] for s in e["subDocuments"]],
                             subs)
        self.assertIn("pkg__componenteGerenciado", str(self.state.data.get("ignoredByFilter")))

    def test_main_document(self):
        doc = self.doc("pedidoPainel")
        self.assertIn("| MasterLabel | Painel de Pedidos | XML |", doc)
        self.assertIn("| pedidoPainel.css | CSS | Código LWC |", doc)
        self.assertNotIn("__tests__", doc)
        self.assertIn("| lightning__RecordPage | Página de registro (Lightning App Builder) | XML |", doc)
        self.assertIn("| lightning__RecordPage | titulo | String | Título | entrada e saída (role ausente) | "
                      "Não informado | Pedidos | Sim | XML |", doc)
        self.assertIn("| lightning__RecordPage | Objeto | Pedido__c | XML |", doc)
        self.assertIn("| recordId | propriedade | Código LWC |", doc)
        self.assertIn("| PedidoController | buscarPedidos | buscarPedidos | @wire | Código LWC |", doc)
        self.assertIn("| Adaptador @wire | getRecord | lightning/uiRecordApi | Código LWC |", doc)
        self.assertIn("| Message channel (LMS) | Pedido_Selecionado__c | chamadas no componente: publish |", doc)
        self.assertIn("| Evento customizado | pedidoselecionado | CustomEvent | Código LWC |", doc)
        self.assertNotIn("falso", doc)                # string no JS
        self.assertNotIn("LegadoController", doc)     # import comentado
        self.assertNotIn("componente-comentado", doc)  # comentário HTML
        self.assertIn("| Custom Permission | Aprova_Pedido | Código LWC |", doc)
        self.assertIn("| DeveloperName | pedidoPainel | Objeto interno |", doc)
        self.assertNotIn("{{", doc)

    def test_apex_methods_checked_in_processed_class(self):
        doc = self.doc("pedidoPainel")
        self.assertIn("| PedidoController | buscarPedidos | Sim (cacheable=true) | public, static | Atende |", doc)
        self.assertIn("| PedidoController | contarPedidos | Sim | public, static | "
                      "Não atende: @wire exige @AuraEnabled(cacheable=true) |", doc)
        self.assertIn("| PedidoController | enviar | Sim | public, static | Atende |", doc)

    def test_access_via_apex_class_and_custom_permission(self):
        access = self.doc("pedidoPainel").split("## Acesso e configuração", 1)[1]
        self.assertIn("| Perfil | Admin | Executar | Classe Apex chamada PedidoController | XML |", access)
        self.assertIn("| Permission Set | Integracao_API | Habilitada | Custom Permission Aprova_Pedido | XML |", access)
        # Três métodos da mesma classe: uma linha só por concessão.
        self.assertEqual(access.count("| Classe Apex chamada PedidoController | XML |"), 1)

    def test_quick_action_subdocument(self):
        doc = self.subdoc("pedidoAcaoRapida", "lwc-quick-action")
        self.assertIn("| ActionType | Action | XML |", doc)
        self.assertIn("| Verificação headless | Atende: @api invoke() declarado | Derivado |", doc)
        self.assertIn("| Propriedades no targetConfig da ação | 0 | XML |", doc)

    def test_flow_screen_subdocument(self):
        doc = self.subdoc("pedidoTelaFlow", "lwc-flow-screen")
        self.assertIn("| @api validate() declarado | True | Código LWC |", doc)
        self.assertIn("| valor | Integer | Valor do Pedido | inputOnly | Sim | XML |", doc)
        self.assertIn("| codigo | String | Código Cliente | entrada e saída (role ausente) | Sim | XML |", doc)
        self.assertIn("| fantasma | String | Sem @api | entrada e saída (role ausente) | Não | XML |", doc)
        self.assertIn("| FlowNavigationNextEvent | Código LWC |", doc)

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "pedidoPainel")["document"])
        self.assertIn("| PedidoController | contarPedidos | Sim | public, static | Não atende", doc)


class LwcWithoutApexClassTest(P3Base):
    def test_apex_check_not_informed_when_class_out_of_scope(self):
        code, state = self.run_pipeline(groups=["LightningComponentBundle"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "pedidoPainel")["document"])
        self.assertIn("| PedidoController | buscarPedidos | Classe não processada nesta execução |", doc)


if __name__ == "__main__":
    unittest.main()
