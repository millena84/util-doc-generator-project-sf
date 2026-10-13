"""Objetos de evento (Onda 06): platform events (`__e`) e Change Data Capture.

Usa a CLI simulada e os XMLs SIMULADOS de tests/fixtures/source.
"""

import unittest

from tests.test_prioridade3 import P3Base
from salesforce_docs import status as st
from salesforce_docs.parsing.apex_parser import parse_apex_source
from salesforce_docs.parsing.event_channel_parser import base_object, parse_event_channel_member
from salesforce_docs.parsing.lwc_parser import parse_lwc_bundle
from salesforce_docs.pipeline.document_pipeline import EXIT_OK

GROUPS = ["PlatformEvent", "ChangeDataCapture", "ApexTrigger", "ApexClass", "Flow",
          "LightningComponentBundle", "CustomObject"]
META = ('<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">'
        '<apiVersion>67.0</apiVersion><isExposed>false</isExposed></LightningComponentBundle>')


class EventParsersTest(unittest.TestCase):
    def test_apex_publish_requires_eventbus_call(self):
        pub = parse_apex_source("public class A { void m() { X__e e = new X__e(); EventBus.publish(e); } }")
        self.assertEqual(pub["platformEvents"], {"publishCall": True, "eventTypes": ["X__e"]})
        only_new = parse_apex_source("public class A { void m() { X__e e = new X__e(); } }")
        self.assertFalse(only_new["platformEvents"]["publishCall"])
        commented = parse_apex_source("public class A { void m() { /* EventBus.publish(new Y__e()); */ } }")
        self.assertEqual(commented["platformEvents"], {"publishCall": False, "eventTypes": []})

    def test_lwc_streaming_channels_only_with_emp_api(self):
        js = "import { subscribe } from 'lightning/empApi';\nconst c = '/event/X__e';\nsubscribe(c, -1, f);"
        r = parse_lwc_bundle({"x.js": js, "x.js-meta.xml": META})
        self.assertEqual(r["streamingChannels"], ["/event/X__e"])
        r = parse_lwc_bundle({"x.js": "const c = '/event/X__e';", "x.js-meta.xml": META})
        self.assertEqual(r["streamingChannels"], [])

    def test_channel_member_and_base_object(self):
        self.assertEqual([base_object(n) for n in ("AccountChangeEvent", "Pedido__ChangeEvent", "Evento__e", None)],
                         ["Account", "Pedido__c", None, None])
        r = parse_event_channel_member(
            '<PlatformEventChannelMember xmlns="http://soap.sforce.com/2006/04/metadata">'
            '<enrichedFields><name>A__c</name></enrichedFields><eventChannel>ChangeEvents</eventChannel>'
            '<selectedEntity>AccountChangeEvent</selectedEntity></PlatformEventChannelMember>')
        self.assertEqual((r["baseObject"], r["enrichedFields"], r["channelKind"]),
                         ("Account", ["A__c"], "Canal padrão do CDC (ChangeEvents)"))


class EventDocumentsTest(P3Base):
    def setUp(self):
        super().setUp()
        self.code, self.state = self.run_pipeline(groups=GROUPS)

    def doc(self, name, suffix):
        e = next(c for c in self.state.data["components"]
                 if c.get("role") == "primary" and c["component"] == name and suffix in str(c.get("document")))
        self.assertEqual(e["status"], st.SUCCESS, name)
        return self.read(e["document"])

    def test_platform_event_document(self):
        self.assertEqual(self.code, EXIT_OK, self.log.getvalue())
        doc = self.doc("Pedido_Evento__e", "platform-event")
        self.assertIn("| PublishBehavior | PublishAfterCommit | XML |", doc)
        self.assertIn("| Numero_Pedido__c | Número do Pedido | Text | 18 | true | XML |", doc)
        self.assertIn("| Publica | Classe Apex | PedidoController |", doc)
        self.assertIn("| Assina | Apex Trigger | PedidoEventoTrigger | after insert; status Active | "
                      "PedidoEventoTriggerConfig: batchSize 200; usuário configurado (não documentado) | Derivado |", doc)
        self.assertIn("| Assina | Flow | Pedido_Evento_Flow |", doc)
        self.assertIn("| Assina | LWC (lightning/empApi) | pedidoTelaFlow | /event/Pedido_Evento__e |", doc)
        self.assertIn("| Permission Set | Integracao_API | Ler, Criar | — | XML |", doc)
        self.assertNotIn("sentinela", doc)  # usuário do PlatformEventSubscriberConfig nunca é documentado
        self.assertNotIn("{{", doc)

    def test_custom_object_group_keeps_only_c(self):
        names = {c["component"] for c in self.state.data["components"]
                 if c.get("role") == "primary" and c.get("group") == "CustomObject"}
        self.assertNotIn("Pedido_Evento__e", names)
        self.assertIn("Pedido__c", names)

    def test_change_data_capture_documents(self):
        custom = self.doc("Canal_Pedido_Pedido_ChangeEvent", "change-data-capture")
        self.assertIn("| Objeto de origem | Pedido__c | Derivado |", custom)
        self.assertIn("| Tipo de canal | Canal customizado | Derivado |", custom)
        self.assertIn("| FilterExpression | Valor__c > 1000 | XML |", custom)
        self.assertIn("| Status__c | XML |", custom)
        self.assertIn("| Assina | Apex Trigger | PedidoChangeTrigger |", custom)
        self.assertIn("Sem PlatformEventSubscriberConfig nos XMLs recuperados", custom)
        self.assertIn("| Perfil | Admin | Habilitada | Permissão de sistema ViewAllData | XML |", custom)
        self.assertIn("| Perfil | Admin | Ler, Criar, Editar, Excluir, Ver todos, Modificar todos | "
                      "Objeto de origem Pedido__c | XML |", custom)
        standard = self.doc("ChangeEvents_Pedido_ChangeEvent", "change-data-capture")
        self.assertIn("| Tipo de canal | Canal padrão do CDC (ChangeEvents) | Derivado |", standard)
        self.assertIn("| Não aplicável | XML |", standard.split("## Campos de enriquecimento", 1)[1].split("## ", 1)[0])

    def test_regenerate(self):
        code, state = self.pipeline().regenerate("latest")
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(next(c for c in state.data["components"]
                             if c.get("component") == "Pedido_Evento__e" and c.get("role") == "primary")["document"])
        self.assertIn("| Publica | Classe Apex | PedidoController |", doc)
        self.assertIn("PedidoEventoTriggerConfig: batchSize 200", doc)


class EventAloneTest(P3Base):
    def test_without_publishers_in_scope(self):
        code, state = self.run_pipeline(groups=["PlatformEvent"])
        self.assertEqual(code, EXIT_OK, self.log.getvalue())
        doc = self.read(self.primary(state, "Pedido_Evento__e")["document"])
        self.assertIn("| Nenhum publicador ou assinante entre os componentes processados |", doc)


if __name__ == "__main__":
    unittest.main()
