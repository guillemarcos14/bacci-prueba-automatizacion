import tempfile
import unittest
import sqlite3
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from bacci.core import (INITIAL_CUTOFF, UPDATE_CUTOFF, build_cases, build_lines, case_label, classify_email,
                        extract_references, get_case, get_run_changes, list_cases, load_sheet, run_import, summary)

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

    def test_source_rows_keep_physical_provenance_without_creating_conflicts(self):
        exact = self.lines["P-26003:10000"]
        self.assertEqual([row["__source_row"] for row in exact["source_rows"]], [88, 95])
        self.assertEqual({row["__source_file"] for row in exact["source_rows"]}, {"Pedidos_muestra.xlsx"})
        self.assertEqual({row["__source_sheet"] for row in exact["source_rows"]}, {"Pedidos"})
        self.assertEqual([(row["uds_pedidas"], row["uds_enviadas"]) for row in exact["source_rows"]],
                         [(400, 100), (400, 100)])
        conflict = self.lines["P-26009:10000"]
        self.assertEqual([row["__source_row"] for row in conflict["source_rows"]], [49, 96])
        self.assertEqual([row["uds_pedidas"] for row in conflict["source_rows"]], [500, 450])
        self.assertIsNone(conflict["pendientes"])

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

    def test_detail_label_precedence(self):
        case = {"attention": True, "unresolved": False, "issues": [], "request_count": 0,
                "priority": "Alta"}
        self.assertEqual(case_label(case), "Atención prioritaria")
        case["request_count"] = 1
        self.assertEqual(case_label(case), "Solicitud sin confirmar")
        case["issues"] = ["cliente no encontrado en el maestro"]
        self.assertEqual(case_label(case), "Revisión humana")
        case["unresolved"] = True
        self.assertEqual(case_label(case), "Sin correspondencia")
        case["attention"] = False
        self.assertEqual(case_label(case), "Servido")
        case.update(attention=True, unresolved=False, issues=["duplicado idéntico consolidado"],
                    request_count=0, priority="Media")
        self.assertEqual(case_label(case), "Pendiente")

    def test_multiple_active_requested_dates_remain_ambiguous(self):
        orders = load_sheet(ROOT / "Pedidos_muestra.xlsx", "Pedidos")
        clients = load_sheet(ROOT / "Pedidos_muestra.xlsx", "Clientes")
        def message(mid, received, requested, body=""):
            return {"message_id": mid, "received_at": received, "sender": "prueba@example.com",
                    "recipient": "operaciones@bacci.test", "subject": "Solicitud P-26002, línea 10000",
                    "body": body or f"Solicitamos {requested} para P-26002, línea 10000.",
                    "source_file": "prueba.xlsx", "source_sheet": "Correos", "source_row": 2}
        messages = [message("msg-90001", "2026-09-10T09:00", "09/09/2026"),
                    message("msg-90002", "2026-09-10T09:30", "13/09/2026")]
        case = next(c for c in build_cases(orders, clients, messages, INITIAL_CUTOFF)
                    if c["case_id"] == "line:P-26002:10000")
        self.assertIsNone(case["requested_date"])
        self.assertEqual(case["requested_dates"], ["2026-09-09", "2026-09-13"])
        self.assertTrue(case["request_conflict"])
        self.assertEqual(case["priority"], "Alta")
        self.assertIn("varias peticiones sin rectificación explícita", case["issues"])
        self.assertIn("Aclarar las fechas solicitadas", case["action"])


class UpdateSequenceTests(unittest.TestCase):
    def test_initial_update_repeat_and_human_review_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "sample.sqlite"
            orders = ROOT / "Pedidos_muestra.xlsx"
            initial = run_import(db, "sample", orders, ROOT / "Correos_muestra.xlsx", INITIAL_CUTOFF)
            before = get_case(db, "line:P-26002:10000")
            self.assertEqual(initial.added_messages, 24)
            self.assertEqual(initial.repeated_messages, 1)
            self.assertIsNone(initial.changed_cases)
            self.assertFalse(get_run_changes(db, initial.run_id)["available"])
            self.assertEqual(before["requested_date"], "2026-09-12")
            self.assertEqual(get_case(db, "line:P-26004:10000")["pendientes"], 250)
            self.assertTrue(get_case(db, "line:P-26004:10000")["overdue"])
            self.assertEqual(get_case(db, "line:P-26001:20000")["reason"], "Solicitud de cancelación")
            self.assertIsNotNone(get_case(db, "email:msg-007"))

            updated = run_import(db, "sample", orders, ROOT / "Correos_actualizacion.xlsx", UPDATE_CUTOFF)
            after = get_case(db, "line:P-26002:10000")
            self.assertEqual(updated.added_messages, 3)
            self.assertEqual(updated.repeated_messages, 2)
            self.assertEqual(updated.changed_cases, 2)
            changes = get_run_changes(db, updated.run_id)
            self.assertEqual({item["case_id"] for item in changes["items"]},
                             {"line:P-26002:10000", "line:P-26004:10000"})
            correction = next(item for item in changes["items"] if item["case_id"] == "line:P-26002:10000")
            self.assertEqual((correction["before"]["requested_date"], correction["after"]["requested_date"]),
                             ("2026-09-12", "2026-09-13"))
            self.assertEqual(correction["changed_fields"], ["requested_date", "requested_dates", "email_ids"])
            self.assertEqual(after["requested_date"], "2026-09-13")
            self.assertEqual(len(after["emails"]), 4)
            email_sources = {mail["message_id"]: (mail["source_file"], mail["source_sheet"], mail["source_row"])
                             for mail in after["emails"]}
            self.assertEqual(email_sources["msg-001"], ("Correos_muestra.xlsx", "Correos", 6))
            self.assertEqual(email_sources["msg-20001"], ("Correos_actualizacion.xlsx", "Correos", 5))
            self.assertEqual(after["source_rows"][0]["__source_row"], 84)
            self.assertEqual((after["uds_pedidas"], after["uds_enviadas"], after["pendientes"]),
                             (800, 0, 800))
            self.assertNotEqual(initial.output_sha256, updated.output_sha256)

            repeated = run_import(db, "sample", orders, ROOT / "Correos_actualizacion.xlsx", UPDATE_CUTOFF)
            self.assertEqual(repeated.added_messages, 0)
            self.assertEqual(repeated.repeated_messages, 5)
            self.assertEqual(repeated.changed_cases, 0)
            self.assertEqual(get_run_changes(db, repeated.run_id)["items"], [])
            self.assertEqual(repeated.output_sha256, updated.output_sha256)
            self.assertEqual(list_cases(db, view="unresolved")["total"], updated.unresolved_cases)
            self.assertEqual(summary(db)["review_cases"], 7)
            review = list_cases(db, review=True, page_size=100)
            self.assertEqual(review["total"], 7)
            self.assertTrue(all(item["label"] == "Revisión humana" for item in review["items"]))
            self.assertEqual(list_cases(db, review=True, client="C002", priority="Alta",
                                        search="P-26009")["items"][0]["case_id"], "line:P-26009:10000")

            # Una base anterior sin procedencia recupera el primer origen real,
            # también si el mensaje reaparece en el lote de actualización.
            connection = sqlite3.connect(db)
            try:
                connection.execute("""UPDATE messages SET source_file=NULL,source_sheet=NULL,source_row=NULL
                  WHERE message_id IN ('msg-001','msg-20001')""")
                connection.commit()
            finally:
                connection.close()
            migrated = run_import(db, "sample", orders, ROOT / "Correos_actualizacion.xlsx", UPDATE_CUTOFF)
            self.assertEqual(migrated.output_sha256, updated.output_sha256)
            migrated_emails = {mail["message_id"]: (mail["source_file"], mail["source_row"])
                               for mail in get_case(db, "line:P-26002:10000")["emails"]}
            self.assertEqual(migrated_emails["msg-001"], ("Correos_muestra.xlsx", 6))
            self.assertEqual(migrated_emails["msg-20001"], ("Correos_actualizacion.xlsx", 5))

            changed_batch = Path(folder) / "Correos_cambiados.xlsx"
            workbook = load_workbook(ROOT / "Correos_actualizacion.xlsx")
            workbook["Correos"]["F5"] = "Contenido distinto con el mismo message_id"
            workbook["Correos"]["F6"] = "Contenido distinto con el mismo message_id"
            workbook.save(changed_batch)
            workbook.close()
            conflicted = run_import(db, "sample", orders, changed_batch, UPDATE_CUTOFF)
            self.assertEqual((conflicted.added_messages, conflicted.conflicting_messages), (0, 2))
            self.assertEqual(conflicted.output_sha256, updated.output_sha256)
            retained = next(mail for mail in get_case(db, "line:P-26002:10000")["emails"]
                            if mail["message_id"] == "msg-20001")
            self.assertEqual((retained["source_file"], retained["source_row"]),
                             ("Correos_actualizacion.xlsx", 5))

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

            # Los términos de estado y prioridad se interpretan según lo visible.
            low = list_cases(db, view="records", search="  BAJA  ", page_size=100)
            self.assertGreater(low["total"], 0)
            self.assertTrue(all(item["attention"] and item["priority"] == "Baja" for item in low["items"]))
            served = list_cases(db, view="records", search="servido", page_size=100)
            self.assertEqual(served["total"], 10)
            self.assertTrue(all(not item["attention"] for item in served["items"]))
            self.assertEqual(list_cases(db, view="records", search="servido", priority="Baja")["total"], 0)
            self.assertEqual(list_cases(db, view="records", search="baja", priority="Alta")["total"], 0)
            self.assertIn(served_id, {item["case_id"] for item in
                list_cases(db, view="records", search=f"servido {served_order}", page_size=100)["items"]})
            self.assertEqual(get_case(db, served_id)["label"], "Servido")
            self.assertEqual(get_case(db, "email:msg-007")["label"], "Sin correspondencia")
            self.assertEqual(get_case(db, "line:P-26009:10000")["label"], "Revisión humana")
            self.assertEqual(after["label"], "Solicitud sin confirmar")

            # Consulta libre sobre las columnas importadas y fechas en ambos formatos.
            source = after["source_rows"][0]
            for term in (after["order_id"].lower(), str(after["line_id"]), source["sku"].lower(),
                         source["color"], source["talla"], str(source["uds_pedidas"]),
                         after["fecha_compromiso"],
                         datetime.fromisoformat(after["fecha_compromiso"]).strftime("%d/%m/%Y"),
                         customer_email.upper(), "RECTIFICO MI CORREO"):
                with self.subTest(term=term):
                    self.assertIn(after["case_id"], {item["case_id"] for item in
                        list_cases(db, view="records", search=term, page_size=100)["items"]})
            self.assertIn(after["case_id"], {item["case_id"] for item in
                list_cases(db, view="records", search=f"{after['order_id']} {source['sku']}", page_size=100)["items"]})
            self.assertIn(after["case_id"], {item["case_id"] for item in
                list_cases(db, view="records", search=after["order_id"], client=after["cliente_id"],
                           priority=after["priority"], page_size=100)["items"]})
            self.assertIn("line:P-26006:10000", {item["case_id"] for item in
                list_cases(db, view="records", search="ÁLAMEDA p-26006", page_size=100)["items"]})
            self.assertEqual(list_cases(db, view="records", search="%_")["total"], 0)


if __name__ == "__main__":
    unittest.main()
