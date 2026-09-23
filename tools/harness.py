"""Arnés reproducible: oráculos explícitos, actualización y tiempo completo."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bacci.core import INITIAL_CUTOFF, UPDATE_CUTOFF, build_lines, case_label, get_case, get_run_changes, load_sheet, list_cases, run_import, summary  # noqa: E402


def check(checks: list[dict], name: str, expected: object, actual: object) -> None:
    checks.append({"check": name, "expected": expected, "actual": actual, "pass": expected == actual})


def evaluate(dataset: str) -> dict:
    suffix = "muestra" if dataset == "sample" else "full"
    orders_path = ROOT / f"Pedidos_{suffix}.xlsx"
    emails_path = ROOT / f"Correos_{suffix}.xlsx"
    update_path = ROOT / "Correos_actualizacion.xlsx"
    checks: list[dict] = []
    with tempfile.TemporaryDirectory() as folder:
        db = Path(folder) / f"{dataset}.sqlite"
        initial = run_import(db, dataset, orders_path, emails_path, INITIAL_CUTOFF)
        before = get_case(db, "line:P-26002:10000")
        updated = run_import(db, dataset, orders_path, update_path, UPDATE_CUTOFF)
        after = get_case(db, "line:P-26002:10000")
        repeated = run_import(db, dataset, orders_path, update_path, UPDATE_CUTOFF)
        expected_initial = 24 if dataset == "sample" else 3800
        expected_initial_repeat = 1 if dataset == "sample" else 200
        check(checks, "Correos iniciales únicos", expected_initial, initial.added_messages)
        check(checks, "Duplicados iniciales ignorados", expected_initial_repeat, initial.repeated_messages)
        check(checks, "Mensajes nuevos del lote", 3, updated.added_messages)
        check(checks, "Reentregas del lote", 2, updated.repeated_messages)
        check(checks, "Mensajes nuevos al repetir", 0, repeated.added_messages)
        check(checks, "Reentregas al repetir", 5, repeated.repeated_messages)
        check(checks, "Digest estable tras repetición", updated.output_sha256, repeated.output_sha256)
        check(checks, "Casos afectados por la actualización", 2, updated.changed_cases)
        check(checks, "Casos afectados al repetir", 0, repeated.changed_cases)
        changed = get_run_changes(db, updated.run_id)
        check(checks, "Identidad de casos afectados", ["line:P-26002:10000", "line:P-26004:10000"],
              [item["case_id"] for item in changed["items"]])
        correction = next(item for item in changed["items"] if item["case_id"] == "line:P-26002:10000")
        check(checks, "Fecha antes/después explicada", ("2026-09-12", "2026-09-13"),
              (correction["before"]["requested_date"], correction["after"]["requested_date"]))
        check(checks, "Filtro revisión humana", 7 if dataset == "sample" else 767,
              list_cases(db, review=True)["total"])
        check(checks, "Conteo visible de revisión humana", 7 if dataset == "sample" else 767,
              summary(db)["review_cases"])
        date_case = get_case(db, "line:P-26002:10000" if dataset == "sample" else "line:P-30168:40000")
        check(checks, "No escoger una fecha entre peticiones incompatibles",
              "2026-09-13" if dataset == "sample" else None, date_case["requested_date"])
        check(checks, "Conservar todas las fechas solicitadas activas",
              ["2026-09-13"] if dataset == "sample" else ["2026-09-21", "2026-09-24"],
              date_case["requested_dates"])
        check(checks, "Acción pide aclarar fechas incompatibles", dataset == "full",
              "Aclarar las fechas solicitadas" in date_case["action"])
        check(checks, "Corte inicial", INITIAL_CUTOFF.isoformat(timespec="minutes"), initial.as_of)
        check(checks, "Corte actualizado", UPDATE_CUTOFF.isoformat(timespec="minutes"), updated.as_of)
        check(checks, "P-26002 solicitud inicial", "2026-09-12", before["requested_date"])
        check(checks, "P-26002 rectificación vigente", "2026-09-13", after["requested_date"])
        check(checks, "Acuse no cambia la solicitud", 4, len(after["emails"]))
        email_sources = {mail["message_id"]: (mail["source_file"], mail["source_sheet"], mail["source_row"])
                         for mail in after["emails"]}
        check(checks, "Correo inicial conserva primera fila", (f"Correos_{suffix}.xlsx", "Correos", 6 if dataset == "sample" else 1970),
              email_sources["msg-001"])
        check(checks, "Correo nuevo conserva primera fila", ("Correos_actualizacion.xlsx", "Correos", 5),
              email_sources["msg-20001"])
        check(checks, "Pedido inexistente visible", True, get_case(db, "email:msg-007") is not None)
        check(checks, "P-26004 pendiente", 250, get_case(db, "line:P-26004:10000")["pendientes"])
        check(checks, "P-26004 vencido", True, get_case(db, "line:P-26004:10000")["overdue"])
        check(checks, "Cancelación en línea expedida", "Solicitud de cancelación", get_case(db, "line:P-26001:20000")["reason"])
        rows = load_sheet(orders_path, "Pedidos")
        clients = load_sheet(orders_path, "Clientes")
        lines, _, _ = build_lines(rows, clients)
        check(checks, "Líneas únicas del ERP", 98 if dataset == "sample" else 19400, len(lines))
        check(checks, "Conflictos sin elegir fila", None, lines["P-26009:10000"]["pendientes"])
        check(checks, "Duplicado idéntico consolidado", 300, lines["P-26003:10000"]["pendientes"])
        check(checks, "Sobreexpedición no negativa", None, lines["P-26008:10000"]["pendientes"])
        check(checks, "Filas ERP duplicadas localizables", [88, 95] if dataset == "sample" else [7248, 12350],
              [row["__source_row"] for row in lines["P-26003:10000"]["source_rows"]])
        check(checks, "Filas ERP contradictorias localizables", [49, 96] if dataset == "sample" else [11164, 18936],
              [row["__source_row"] for row in lines["P-26009:10000"]["source_rows"]])
        check(checks, "Cálculo visible y fuente conservada", (800, 0, 800, 84 if dataset == "sample" else 1865),
              (after["uds_pedidas"], after["uds_enviadas"], after["pendientes"],
               after["source_rows"][0]["__source_row"]))
        with closing(sqlite3.connect(db)) as connection:
            all_cases = [json.loads(row[0]) for row in connection.execute("SELECT detail_json FROM cases")]
            message_ids = {row[0] for row in connection.execute("SELECT message_id FROM messages")}
        check(checks, "Casos con varias fechas activas incompatibles", 0 if dataset == "sample" else 43,
              sum(len(case.get("requested_dates", [])) > 1 for case in all_cases))
        arithmetic_errors = []
        provenance_errors = []
        label_errors = []
        for case in all_cases:
            if case_label(case) != case["label"]:
                label_errors.append(case["case_id"])
            for source in case.get("source_rows", []):
                if not all(source.get(key) for key in ("__source_file", "__source_sheet", "__source_row")):
                    provenance_errors.append(case["case_id"])
            for mail in case.get("emails", []):
                if mail["message_id"] not in message_ids or not all(mail.get(key) for key in
                    ("source_file", "source_sheet", "source_row")):
                    provenance_errors.append(case["case_id"])
            source_rows = case.get("source_rows", [])
            if len(source_rows) == 1:
                ordered, shipped = source_rows[0].get("uds_pedidas"), source_rows[0].get("uds_enviadas")
                if all(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0
                       for value in (ordered, shipped)):
                    expected_pending = ordered - shipped if shipped <= ordered else None
                    if case["pendientes"] != expected_pending:
                        arithmetic_errors.append(case["case_id"])
        check(checks, "Aritmética de todas las líneas sin duplicados", [], arithmetic_errors)
        check(checks, "Procedencia e integridad de todas las evidencias", [], provenance_errors)
        check(checks, "Etiquetas coherentes en todos los registros", [], label_errors)
        return {"dataset": dataset, "passed": sum(c["pass"] for c in checks), "total": len(checks),
                "checks": checks, "runs": [initial.__dict__, updated.__dict__, repeated.__dict__],
                "changes": {"new_messages": updated.added_messages, "p26002_requested_date_before": before["requested_date"],
                            "p26002_requested_date_after": after["requested_date"],
                            "stable_after_repeat": updated.output_sha256 == repeated.output_sha256}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("sample", "full", "both"), default="both")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "validation.json")
    args = parser.parse_args()
    datasets = ("sample", "full") if args.dataset == "both" else (args.dataset,)
    result = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "results": [evaluate(item) for item in datasets]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in result["results"]:
        times = "/".join(str(round(run["elapsed_ms"] / 1000, 2)) for run in item["runs"])
        print(f"{item['dataset']}: {item['passed']}/{item['total']} checks · segundos inicial/actualización/repetición: {times}")
        for failed in (x for x in item["checks"] if not x["pass"]):
            print(f"  FALLA {failed['check']}: esperado={failed['expected']!r}, obtenido={failed['actual']!r}")
    print(args.output)
    if any(item["passed"] != item["total"] for item in result["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
