"""Servidor HTTP local sin servicios ni conexiones reales."""

from __future__ import annotations

import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .core import INITIAL_CUTOFF, UPDATE_CUTOFF, connect, get_case, list_cases, recent_runs, run_import, summary

WEB = Path(__file__).resolve().parent / "web"
ROOT = WEB.parent.parent
UPDATE_LOCK = threading.Lock()
DATASET_LOCK = threading.Lock()


def handler_factory(db: Path, dataset: str, orders: Path, update_mail: Path):
    configs = {}
    for name, suffix in (("sample", "muestra"), ("full", "full")):
        configs[name] = (ROOT / "data" / f"{name}.sqlite", ROOT / f"Pedidos_{suffix}.xlsx",
                         ROOT / f"Correos_{suffix}.xlsx", update_mail)
    configs[dataset] = (db, orders, ROOT / f"Correos_{'muestra' if dataset == 'sample' else 'full'}.xlsx", update_mail)
    ready: set[str] = set()

    def selected(query: dict[str, list[str]]) -> tuple[str, Path, Path, Path]:
        name = query.get("dataset", [dataset])[0]
        if name not in configs:
            raise ValueError("Conjunto de datos desconocido")
        target_db, target_orders, initial_mail, target_update = configs[name]
        if name not in ready:
            with DATASET_LOCK:
                if name not in ready:
                    version = 0
                    if target_db.exists():
                        connection = connect(target_db)
                        try:
                            version = connection.execute("PRAGMA user_version").fetchone()[0]
                        finally:
                            connection.close()
                    if not target_db.exists() or not recent_runs(target_db, 1):
                        run_import(target_db, name, target_orders, initial_mail, INITIAL_CUTOFF)
                        run_import(target_db, name, target_orders, target_update, UPDATE_CUTOFF)
                    elif version < 2:
                        run_import(target_db, name, target_orders, target_update, UPDATE_CUTOFF)
                    ready.add(name)
        return name, target_db, target_orders, target_update

    class Handler(BaseHTTPRequestHandler):
        server_version = "BacciLocal/0.1"

        def _send(self, status: int, payload: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(payload)

        def _json(self, status: int, data: object) -> None:
            self._send(status, json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            try:
                if parsed.path.startswith("/api/") and parsed.path != "/api/health":
                    _, target_db, _, _ = selected(query)
                if parsed.path == "/api/summary":
                    self._json(200, summary(target_db))
                elif parsed.path == "/api/runs":
                    self._json(200, recent_runs(target_db))
                elif parsed.path == "/api/cases":
                    page = max(1, int(query.get("page", ["1"])[0]))
                    self._json(200, list_cases(target_db, client=query.get("client", [""])[0] or None,
                                               priority=query.get("priority", [""])[0] or None,
                                               view=query.get("view", ["all"])[0],
                                               search=query.get("search", [""])[0], page=page))
                elif parsed.path.startswith("/api/cases/"):
                    case = get_case(target_db, unquote(parsed.path.removeprefix("/api/cases/")))
                    self._json(200 if case else 404, case if case else {"error": "Caso no encontrado"})
                elif parsed.path == "/api/health":
                    self._json(200, {"ok": True, "dataset": dataset})
                else:
                    route = {"/": ("index.html", "text/html; charset=utf-8"),
                             "/styles.css": ("styles.css", "text/css; charset=utf-8"),
                             "/app.js": ("app.js", "text/javascript; charset=utf-8")}.get(parsed.path)
                    if route:
                        self._send(200, (WEB / route[0]).read_bytes(), route[1])
                    else:
                        self._json(404, {"error": "Ruta no encontrada"})
            except ValueError as error:
                self._json(400, {"error": str(error)})
            except Exception as error:
                self._json(500, {"error": f"Error local: {error}"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/update":
                self._json(404, {"error": "Ruta no encontrada"})
                return
            origin = self.headers.get("Origin")
            expected = f"http://{self.headers.get('Host')}"
            if origin and origin != expected:
                self._json(403, {"error": "Origen no permitido"})
                return
            with UPDATE_LOCK:
                try:
                    selected_dataset, target_db, target_orders, target_update = selected(parse_qs(parsed.query))
                    result = run_import(target_db, selected_dataset, target_orders, target_update, UPDATE_CUTOFF)
                    self._json(200, result.__dict__)
                except ValueError as error:
                    self._json(400, {"error": str(error)})
                except Exception as error:
                    self._json(500, {"error": f"Actualización fallida: {error}"})

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def serve(db: Path, dataset: str, orders: Path, update_mail: Path, port: int) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler_factory(db, dataset, orders, update_mail))
    print(f"Bacci Operaciones · http://127.0.0.1:{port} · {dataset}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
