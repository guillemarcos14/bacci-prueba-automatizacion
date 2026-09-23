"""Arnés reproducible: oráculos explícitos, actualización y tiempo completo."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bacci.core import INITIAL_CUTOFF, UPDATE_CUTOFF, build_lines, get_case, load_sheet, run_import  # noqa: E402


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
        check(checks, "Corte inicial", INITIAL_CUTOFF.isoformat(timespec="minutes"), initial.as_of)
        check(checks, "Corte actualizado", UPDATE_CUTOFF.isoformat(timespec="minutes"), updated.as_of)
        check(checks, "P-26002 solicitud inicial", "2026-09-12", before["requested_date"])
        check(checks, "P-26002 rectificación vigente", "2026-09-13", after["requested_date"])
        check(checks, "Acuse no cambia la solicitud", 4, len(after["emails"]))
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
