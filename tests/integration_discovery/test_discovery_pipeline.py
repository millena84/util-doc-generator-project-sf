import io
import json
import shutil

from tests.integration_discovery.base import CSV, DiscoveryBase, INV
from tests.test_prioridade3 import P3Base
from integration_discovery import reference_extractor
from integration_discovery.__main__ import main as cli_main
from integration_discovery.discovery_pipeline import review_cluster, run_discovery

SENTINELS = ("sentinela", "SENTINELA", "CONSUMER_KEY", "example.invalid")


class DiscoveryPipelineTest(DiscoveryBase):
    def run_it(self, csv=CSV, **kw):
        return run_discovery(self.root, csv, stream=io.StringIO(), **kw)

    def all_outputs(self):
        return "\n".join(p.read_text(encoding="utf-8") for p in self.out().rglob("*") if p.is_file())

    def test_full_flow_with_fixtures(self):
        code, summary = self.run_it()
        self.assertEqual(code, 0)
        self.assertEqual((summary["found"], summary["notFound"], summary["clusters"], summary["orphans"]), (10, 1, 3, 1))
        graph = self.read_json("graphs", "graph.json")
        self.assertEqual(set(graph), {"generatedAt", "nodes", "edges", "unverifiedMentions",
                                      "referencesToComponentsWithoutJson"})
        c1 = self.read_json("clusters", "cluster-001.json")
        self.assertEqual((c1["status"], c1["confidence"], c1["proposedName"]), ("CANDIDATE", "HIGH", "Integração RH - Colaborador"))
        self.assertIn("NamedCredential:RH_Endpoint", [x["id"] for x in c1["components"]])
        # o permission set (ponte) aparece em mais de um cluster, sem fundir as integrações
        with_ps = [p.name for p in sorted(self.out("clusters").glob("*.json"))
                   if "PermissionSet:IntegracaoRH_User" in p.read_text(encoding="utf-8")]
        self.assertEqual(len(with_ps), 3)
        proposal = self.read_json("proposals", "cluster-001.proposal.json")
        self.assertEqual((proposal["status"], proposal["clusterId"]), ("CANDIDATE", "cluster-001"))
        self.assertEqual(self.read_json("orphans", "orphans.json")["orphans"][0]["id"], "RemoteSiteSetting:RH_Remote_Site")
        report = self.out("report", "discovery-report.md").read_text(encoding="utf-8")
        for section in ("## 1. Resumo", "## 2. Componentes sem JSON", "## 3. Clusters", "## 4. Órfãos",
                        "## 7. Erros e avisos de validação do CSV", "## 8. Pendências e dúvidas"):
            self.assertIn(section, report)
        for s in SENTINELS:  # nenhum valor sensível do normalizado nas saídas
            self.assertNotIn(s, self.all_outputs(), s)

    def test_missing_json_does_not_break_pipeline(self):
        (self.root / INV / "apex-triggers" / "normalized" / "colaboradortrigger.json").unlink()
        code, summary = self.run_it()
        self.assertEqual((code, summary["notFound"]), (0, 2))
        status = {c["componentName"]: c for c in self.read_json("report", "component-status.json")["components"]}
        self.assertEqual(status["ColaboradorTrigger"]["status"], "NORMALIZED_JSON_NOT_FOUND")
        self.assertEqual(status["ColaboradorTrigger"]["expectedPath"], f"{INV}/apex-triggers/normalized/colaboradortrigger.json")
        self.assertGreaterEqual(summary["clusters"], 1)

    def test_resume_does_not_reprocess_unchanged_components(self):
        self.run_it()
        calls = []

        def spy(entry, targets, rules):
            calls.append(entry["key"])
            return reference_extractor.extract_references(entry, targets, rules)

        _, summary = self.run_it(extractor=spy)
        self.assertEqual((calls, summary["cacheHits"]), ([], 10))
        p = self.root / INV / "certificates" / "normalized" / "integracaorh-cert.json"
        p.write_text(p.read_text(encoding="utf-8").replace('"2048"', '"4096"'), encoding="utf-8")
        _, summary = self.run_it(extractor=spy)
        self.assertEqual((calls, summary["cacheHits"]), (["Certificate:IntegracaoRH_Cert"], 9))
        calls.clear()
        self.run_it(extractor=spy, use_cache=False)
        self.assertEqual(len(calls), 10)

    def members(self, cluster_id):
        return [x["id"] for x in self.read_json("clusters", f"{cluster_id}.json")["components"]]

    def test_review_is_kept_across_runs_while_composition_is_the_same(self):
        self.run_it()
        review_cluster(self.root, "cluster-001", "APPROVED", "Millena", "ok", "Integração RH - Admissões", stream=io.StringIO())
        c = self.read_json("clusters", "cluster-001.json")
        self.assertEqual((c["status"], c["approvedName"], c["humanReview"]["reviewedBy"]),
                         ("APPROVED", "Integração RH - Admissões", "Millena"))
        self.assertEqual(self.read_json("proposals", "cluster-001.proposal.json")["status"], "APPROVED")
        self.run_it()
        c = self.read_json("clusters", "cluster-001.json")
        self.assertEqual((c["status"], c["approvedName"]), ("APPROVED", "Integração RH - Admissões"))
        with self.assertRaises(ValueError):
            review_cluster(self.root, "cluster-001", "APPROVED", None, stream=io.StringIO())

    def test_cluster_numbers_are_stable_when_order_changes(self):
        # D22-01: nova evidência reordena os clusters; o número continua apontando para a mesma composição
        self.run_it()
        app = self.members("cluster-002")
        self.assertIn("ConnectedApp:IntegracaoRH", app)
        p = self.root / INV / "permission-sets" / "normalized" / "integracaorh-user.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["data"]["fieldPermissions"] = [{"field": "x", "note": "SAPOrderSync"}, {"field": "y", "note": "SAPOrderSync"}]
        p.write_text(json.dumps(d), encoding="utf-8")
        self.run_it()
        report = self.out("report", "discovery-report.md").read_text(encoding="utf-8")
        self.assertLess(report.index("| cluster-003 |"), report.index("| cluster-002 |"))  # SAP passou à frente
        review_cluster(self.root, "cluster-002", "APPROVED", "Millena", stream=io.StringIO())
        self.assertEqual(self.members("cluster-002"), app)
        self.assertEqual(self.read_json("clusters", "cluster-002.json")["status"], "APPROVED")

    def test_retired_number_is_refused_and_never_reused(self):
        self.run_it()
        review_cluster(self.root, "cluster-001", "REJECTED", "Millena", "não é integração", stream=io.StringIO())
        (self.root / INV / "custom-metadata" / "normalized" / "endpoint-config-producao.json").unlink()
        self.run_it()
        self.assertFalse(self.out("clusters", "cluster-001.json").exists())
        new_ids = sorted(p.stem for p in self.out("clusters").glob("*.json"))
        self.assertNotIn("cluster-001", new_ids)
        self.assertIn("cluster-004", new_ids)  # composição nova: próximo número livre
        with self.assertRaises(ValueError) as ctx:
            review_cluster(self.root, "cluster-001", "APPROVED", "Millena", stream=io.StringIO())
        self.assertIn("não existe mais", str(ctx.exception))
        self.assertIn("cluster-004", str(ctx.exception))
        with self.assertRaises(ValueError):
            review_cluster(self.root, "cluster-999", "APPROVED", "Millena", stream=io.StringIO())

    def test_decision_history_survives_several_runs(self):
        # D22-02: a decisão de um cluster aposentado continua no histórico e no relatório
        self.run_it()
        review_cluster(self.root, "cluster-001", "REJECTED", "Millena", "não é integração", stream=io.StringIO())
        (self.root / INV / "custom-metadata" / "normalized" / "endpoint-config-producao.json").unlink()
        for _ in range(2):
            self.run_it()
            report = self.out("report", "discovery-report.md").read_text(encoding="utf-8")
            self.assertIn("## 9. Revisões que não se aplicam mais", report)
            self.assertIn("cluster-001 (decisão anterior: REJECTED por Millena; nota: não é integração)", report)
        registry = self.read_json("state", "cluster-registry.json")
        self.assertEqual(registry["reviews"][0]["notes"], "não é integração")
        # revisar o sucessor encerra o aviso
        succ = [x for x in registry["clusters"].values() if x["clusterId"] == "cluster-001"][0]["successors"]
        for cid in succ:
            review_cluster(self.root, cid, "APPROVED", "Millena", stream=io.StringIO())
        self.run_it()
        self.assertNotIn("## 9.", self.out("report", "discovery-report.md").read_text(encoding="utf-8"))

    def test_signature_confirmation(self):
        self.run_it()
        sig = self.read_json("clusters", "cluster-001.json")["signature"]
        with self.assertRaises(ValueError):
            review_cluster(self.root, "cluster-001", "APPROVED", "Millena", signature="0" * 16, stream=io.StringIO())
        review_cluster(self.root, "cluster-001", "APPROVED", "Millena", signature=sig, stream=io.StringIO())
        self.assertEqual(self.read_json("clusters", "cluster-001.json")["status"], "APPROVED")

    def test_migration_from_outputs_without_registry(self):
        self.run_it()
        review_cluster(self.root, "cluster-002", "APPROVED", "Millena", stream=io.StringIO())
        app = self.members("cluster-002")
        self.out("state", "cluster-registry.json").unlink()  # como saídas geradas antes do registro
        self.run_it()
        self.assertEqual(self.members("cluster-002"), app)
        self.assertEqual(self.read_json("clusters", "cluster-002.json")["status"], "APPROVED")

    def test_fatal_csv_keeps_previous_outputs(self):
        self.run_it()
        before = self.out("clusters", "cluster-001.json").read_text(encoding="utf-8")
        code, summary = self.run_it(csv=self.write_csv("errado\n"))
        self.assertEqual(code, 2)
        self.assertIn("cabeçalho", summary["fatal"])
        self.assertEqual(self.out("clusters", "cluster-001.json").read_text(encoding="utf-8"), before)

    def test_invalid_csv_lines_are_reported_and_valid_ones_processed(self):
        text = CSV.read_text(encoding="utf-8") + "ApexPage,Pagina,true,\nApexClass,SAPOrderSync,false,duplicada\n"
        code, summary = self.run_it(csv=self.write_csv(text))
        self.assertEqual((code, summary["csvErrors"], summary["found"]), (0, 1, 10))
        report = self.out("report", "discovery-report.md").read_text(encoding="utf-8")
        self.assertIn("component_type inválido: 'ApexPage'", report)
        self.assertIn("duplicada da linha 12", report)

    def test_cli_relative_csv_is_resolved_from_current_directory(self):
        import os
        work = self.root / "minha-pasta"
        work.mkdir()
        shutil.copy(CSV, work / "squad.csv")
        cwd = os.getcwd()
        os.chdir(work)
        try:
            self.assertEqual(cli_main(["--project-root", str(self.root), "--csv", "squad.csv"]), 0)
        finally:
            os.chdir(cwd)
        self.assertTrue(self.out("clusters", "cluster-001.json").is_file())

    def test_cli_run_without_subcommand_and_review(self):
        csv_copy = self.root / "discovery" / "input" / "componentes-squad.csv"
        csv_copy.parent.mkdir(parents=True)
        shutil.copy(CSV, csv_copy)
        self.assertEqual(cli_main(["--project-root", str(self.root), "--target-org", "dev", "--api-version", "67.0"]), 0)
        self.assertTrue(self.out("clusters", "cluster-001.json").is_file())
        self.assertEqual(cli_main(["review", "--project-root", str(self.root), "--cluster", "cluster-002",
                                   "--decision", "rejected", "--by", "Millena"]), 0)
        self.assertEqual(self.read_json("clusters", "cluster-002.json")["status"], "REJECTED")


class DiscoveryOnRealUtility1OutputTest(P3Base):
    """Ponta a ponta sobre JSONs normalizados gerados DE VERDADE pelo Utilitário 1 (CLI simulada)."""

    def test_clusters_from_utility1_inventory(self):
        code, _ = self.run_pipeline(groups=["ApexTrigger", "ApexClass", "CustomObject", "PermissionSet",
                                            "NamedCredential", "ExternalCredential", "ConnectedApp"])
        self.assertEqual(code, 0, self.log.getvalue())
        csv = self.root / "squad.csv"
        csv.write_text("component_type,component_name,squad_suspect,notes\n"
                       "ApexTrigger,PedidoTrigger,true,\nApexClass,PedidoTriggerHandler,true,\nApexClass,PedidoService,true,\n"
                       "CustomObject,Pedido__c,true,\nNamedCredential,Minha_NC,true,\nExternalCredential,Minha_EC,true,\n"
                       "ConnectedApp,Meu_App,true,\nPermissionSet,Integracao_API,true,\n", encoding="utf-8")
        code, summary = run_discovery(self.root, csv, stream=io.StringIO())
        self.assertEqual((code, summary["notFound"]), (0, 0))
        graph = json.loads((self.root / "discovery" / "graphs" / "graph.json").read_text(encoding="utf-8"))
        edges = {(e["from"], e["to"], e["relationship"]) for e in graph["edges"]}
        self.assertIn(("ApexTrigger:PedidoTrigger", "CustomObject:Pedido__c", "TRIGGERS_ON_OBJECT"), edges)
        self.assertIn(("ApexTrigger:PedidoTrigger", "ApexClass:PedidoService", "INVOKES_CLASS"), edges)
        self.assertIn(("NamedCredential:Minha_NC", "ExternalCredential:Minha_EC", "USES_CREDENTIAL"), edges)
        self.assertIn(("ConnectedApp:Meu_App", "PermissionSet:Integracao_API", "REFERENCES"), edges)
        out = "\n".join(p.read_text(encoding="utf-8") for p in (self.root / "discovery").rglob("*.*") if p.is_file())
        for s in ("SENTINELA", "sentinela", "CHAVE_SIMULADA"):
            self.assertNotIn(s, out)
