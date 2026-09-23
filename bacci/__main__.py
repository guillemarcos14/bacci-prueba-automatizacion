"""Comandos locales de Bacci Operaciones."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import INITIAL_CUTOFF, UPDATE_CUTOFF, connect, recent_runs, run_import, summary

ROOT = Path(__file__).resolve().parent.parent


def paths(dataset: str) -> tuple[Path, Path, Path, Path]:
    suffix = "muestra" if dataset == "sample" else "full"
    return (ROOT / "data" / f"{dataset}.sqlite", ROOT / f"Pedidos_{suffix}.xlsx",
            ROOT / f"Correos_{suffix}.xlsx", ROOT / "Correos_actualizacion.xlsx")


def main() -> None:
    parser = argparse.ArgumentParser(description="Conciliación local de pedidos y correos de Bacci")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "update", "demo", "summary", "serve"):
        item = sub.add_parser(command)
        if command == "serve":
            item.add_argument("--port", type=int, default=8765)
        else:
            item.add_argument("--dataset", choices=("sample", "full"), default="sample")
    args = parser.parse_args()
    dataset = "full" if args.command == "serve" else args.dataset
    db, orders, initial_mail, update_mail = paths(dataset)
    if args.command == "serve":
        db = ROOT / "data" / "operations.sqlite"
    if args.command == "init":
        print(json.dumps(run_import(db, dataset, orders, initial_mail, INITIAL_CUTOFF).__dict__, ensure_ascii=False, indent=2))
    elif args.command == "update":
        if not db.exists() or not recent_runs(db, 1):
            parser.error("Primero ejecuta init para conservar los correos iniciales")
        print(json.dumps(run_import(db, dataset, orders, update_mail, UPDATE_CUTOFF).__dict__, ensure_ascii=False, indent=2))
    elif args.command == "demo":
        if db.exists():
            parser.error(f"{db} ya existe. Usa init/update o una base nueva para una demostración limpia")
        stages = [run_import(db, dataset, orders, initial_mail, INITIAL_CUTOFF),
                  run_import(db, dataset, orders, update_mail, UPDATE_CUTOFF),
                  run_import(db, dataset, orders, update_mail, UPDATE_CUTOFF)]
        print(json.dumps({"stages": [stage.__dict__ for stage in stages],
                          "idempotent": stages[1].output_sha256 == stages[2].output_sha256
                          and stages[2].added_messages == 0}, ensure_ascii=False, indent=2))
    elif args.command == "summary":
        print(json.dumps({"summary": summary(db), "runs": recent_runs(db)}, ensure_ascii=False, indent=2))
    elif args.command == "serve":
        if not db.exists() or not recent_runs(db, 1):
            run_import(db, dataset, orders, initial_mail, INITIAL_CUTOFF)
            run_import(db, dataset, orders, update_mail, UPDATE_CUTOFF)
        else:
            connection = connect(db)
            try:
                version = connection.execute("PRAGMA user_version").fetchone()[0]
            finally:
                connection.close()
            if version < 3:
                run_import(db, dataset, orders, update_mail, UPDATE_CUTOFF)
        from .server import serve
        serve(db, orders, update_mail, args.port)


if __name__ == "__main__":
    main()
