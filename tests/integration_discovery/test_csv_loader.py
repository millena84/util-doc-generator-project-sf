from tests.integration_discovery.base import CSV, DiscoveryBase
from integration_discovery.csv_loader import load_csv

HEADER = "component_type,component_name,squad_suspect,notes\n"


class CsvLoaderTest(DiscoveryBase):
    def test_valid_csv(self):
        r = load_csv(CSV)
        self.assertIsNone(r.fatal)
        self.assertEqual((r.total_rows, len(r.components), r.errors), (11, 11, []))
        first = r.components[0]
        self.assertEqual((first["componentType"], first["componentName"], first["squadSuspect"], first["line"]),
                         ("ConnectedApp", "IntegracaoRH", True, 2))
        self.assertEqual(r.components[-1]["notes"], "Outra squad? liberada pelo mesmo permission set")

    def test_missing_column_is_fatal(self):
        r = load_csv(self.write_csv("component_type,component_name,squad_suspect\nApexClass,X,true\n"))
        self.assertIn("cabeçalho inválido", r.fatal)
        self.assertEqual(r.components, [])

    def test_wrong_column_order_is_fatal(self):
        r = load_csv(self.write_csv("component_name,component_type,squad_suspect,notes\n"))
        self.assertIn("nesta ordem", r.fatal)

    def test_invalid_type_and_values_skip_only_bad_lines(self):
        r = load_csv(self.write_csv(HEADER + "ApexPage,Pagina,true,\napexclass,Boa,TRUE,\nApexClass,,talvez,\n"))
        self.assertEqual([c["componentName"] for c in r.components], ["Boa"])
        self.assertEqual(r.components[0]["componentType"], "ApexClass")  # tipo sem diferenciar maiúsculas
        self.assertEqual([e["line"] for e in r.errors], [2, 4])
        self.assertIn("component_type inválido", r.errors[0]["reason"])
        self.assertIn("component_name vazio", r.errors[1]["reason"])
        self.assertIn("squad_suspect", r.errors[1]["reason"])

    def test_duplicate_line_deduplicated_with_warning(self):
        r = load_csv(self.write_csv(HEADER + "ApexClass,X,true,\nAPEXCLASS,X,false,de novo\n"))
        self.assertEqual(len(r.components), 1)
        self.assertEqual(r.warnings[0]["line"], 3)
        self.assertIn("duplicada da linha 2", r.warnings[0]["reason"])

    def test_empty_csv(self):
        self.assertEqual(load_csv(self.write_csv("")).fatal, "CSV vazio (sem cabeçalho)")
        r = load_csv(self.write_csv(HEADER))
        self.assertIsNone(r.fatal)
        self.assertEqual((r.total_rows, r.components), (0, []))

    def test_line_numbers_are_physical_lines(self):
        # linhas em branco e notes entre aspas em duas linhas não deslocam a numeração
        text = HEADER + "\n\nApexClass,A,true,\"nota\nem duas linhas\"\n\nApexPage,X,true,\n"
        r = load_csv(self.write_csv(text))
        self.assertEqual([c["line"] for c in r.components], [4])
        self.assertEqual(r.errors[0]["line"], 7)

    def test_missing_file(self):
        self.assertIn("não encontrado", load_csv(self.root / "nao-existe.csv").fatal)
