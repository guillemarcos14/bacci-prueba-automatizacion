import tempfile
import unittest
import sqlite3
from datetime import datetime
from pathlib import Path

from bacci.core import (INITIAL_CUTOFF, UPDATE_CUTOFF, build_lines, classify_email,
                        extract_references, get_case, list_cases, load_sheet, run_import)

ROOT = Path(__file__).resolve().parent.parent


class SourceAndCalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        orders = load_sheet(ROOT / "Pedidos_muestra.xlsx", "Pedidos")
        clients = load_sheet(ROOT / "Pedidos_muestra.xlsx", "Clientes")
        cls.lines, _, cls.by_order = build_lines(orders, clients)

    def test_duplicate_conflict_is_not_resolved_by_row_order(self):
        conflict = self.lines["P-26009:10000"]
        self.assertIsNone(conflict["pendientes"])
        self.assertIn("filas contradictorias en el ERP", conflict["issues"])
        exact = self.lines["P-26003:10000"]
        self.assertEqual(exact["pendientes"], 300)
        self.assertIn("duplicado idéntico consolidado", exact["issues"])

    def test_over_shipment_is_exception_not_negative_backlog(self):
        line = self.lines["P-26008:10000"]
        self.assertIsNone(line["pendientes"])
        self.assertIn("unidades enviadas mayores que pedidas", line["issues"])

    def test_multiline_mail_and_date_slash_are_distinct(self):
        refs, issues = extract_references("Estado de dos entregas",
            "Estado de P-32353, línea 30000, y P-30353, línea 50000.", self.by_order)
        self.assertFalse(issues)
        self.assertEqual({r["case_id"] for r in refs}, {"line:P-32353:30000", "line:P-30353:50000"})
        refs, issues = extract_references("Solicitud de entrega P-33853",
            "Podemos recibir el 12/09/2026. Ajustad la línea 50000 del pedido P-33853.", self.by_order)
        self.assertFalse(issues)
        self.assertEqual(refs[0]["case_id"], "line:P-33853:50000")
        refs, issues = extract_references("Solicitud de entrega P-31868",
            "Mover P-31868 / 20000 al 21/09/2026.", self.by_order)
        self.assertFalse(issues)
        self.assertEqual(refs[0]["case_id"], "line:P-31868:20000")

    def test_negation_and_correction(self):
        self.assertEqual(classify_email("Estado", "No solicitamos cambiar la fecha; decidnos el estado.")[0], "seguimiento")
        self.assertEqual(classify_email("Rectificación", "Rectifico mi correo msg-002. Solicitamos el 13/09/2026 en lugar del 12/09/2026."),
                         ("cambio_fecha", "2026-09-13", "msg-002"))


class UpdateSequenceTests(unittest.TestCase):
    def test_initial_update_repeat_and_human_review_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "sample.sqlite"
            orders = ROOT / "Pedidos_muestra.xlsx"
            initial = run_import(db, "sample", orders, ROOT / "Correos_muestra.xlsx", INITIAL_CUTOFF)
            before = get_case(db, "line:P-26002:10000")
            self.assertEqual(initial.added_messages, 24)
            self.assertEqual(initial.repeated_messages, 1)
            self.assertEqual(before["requested_date"], "2026-09-12")
            self.assertEqual(get_case(db, "line:P-26004:10000")["pendientes"], 250)
            self.assertTrue(get_case(db, "line:P-26004:10000")["overdue"])
            self.assertEqual(get_case(db, "line:P-26001:20000")["reason"], "Solicitud de cancelación")
            self.assertIsNotNone(get_case(db, "email:msg-007"))

            updated = run_import(db, "sample", orders, ROOT / "Correos_actualizacion.xlsx", UPDATE_CUTOFF)
            after = get_case(db, "line:P-26002:10000")
            self.assertEqual(updated.added_messages, 3)
            self.assertEqual(updated.repeated_messages, 2)
            self.assertEqual(after["requested_date"], "2026-09-13")
            self.assertEqual(len(after["emails"]), 4)
            self.assertNotEqual(initial.output_sha256, updated.output_sha256)

            repeated = run_import(db, "sample", orders, ROOT / "Correos_actualizacion.xlsx", UPDATE_CUTOFF)
            self.assertEqual(repeated.added_messages, 0)
            self.assertEqual(repeated.repeated_messages, 5)
            self.assertEqual(repeated.output_sha256, updated.output_sha256)
            self.assertEqual(list_cases(db, view="unresolved")["total"], updated.unresolved_cases)

            # La cola mantiene solo trabajo pendiente, pero la consulta incluye líneas ya servidas.
            self.assertEqual(list_cases(db)["total"], 90)
            self.assertEqual(list_cases(db, view="records")["total"], 100)
            low_priority = list_cases(db, view="records", priority="Baja", page_size=100)
            self.assertTrue(low_priority["items"])
            self.assertTrue(all(item["attention"] == 1 for item in low_priority["items"]))
            connection = sqlite3.connect(db)
            try:
                served_id, served_order = connection.execute(
                    "SELECT case_id,order_id FROM cases WHERE attention=0 LIMIT 1").fetchone()
            finally:
                connection.close()
            self.assertEqual(get_case(db, served_id)["reason"], "Línea servida sin incidencia")
            matches = list_cases(db, view="records", search=served_order, page_size=100)
            self.assertIn(served_id, {item["case_id"] for item in matches["items"]})

            # La búsqueda abarca SKU, cuerpo de correo y maestro de clientes, no solo pedido y nombre.
            self.assertIn("line:P-26002:10000", {item["case_id"] for item in
                list_cases(db, search="rectifico mi correo", page_size=100)["items"]})
            sku = after["sku"]
            self.assertIn("line:P-26002:10000", {item["case_id"] for item in
                list_cases(db, search=sku, page_size=100)["items"]})
            customer_email = next(row["email"] for row in load_sheet(orders, "Clientes")
                                  if str(row["cliente_id"]) == after["cliente_id"])
            self.assertIn("line:P-26002:10000", {item["case_id"] for item in
                list_cases(db, search=customer_email, page_size=100)["items"]})


if __name__ == "__main__":
    unittest.main()
