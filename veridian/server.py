from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from veridian.errors import VeridianError
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.query import Query, QueryEngine
from veridian.store import load, save

INDEX = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


def _handler(lattice: Lattice, persist: Path | None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _json(self, code: int, payload) -> None:
            body = json.dumps(payload, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                raw = INDEX.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return
            if parsed.path == "/health":
                self._json(200, {"ok": True, "n": lattice.snapshot()["n"]})
                return
            if parsed.path == "/api/snapshot":
                self._json(200, lattice.snapshot())
                return
            if parsed.path == "/api/query":
                qs = parse_qs(parsed.query)
                q = Query(
                    subject=(qs.get("subject") or [None])[0],
                    predicate=(qs.get("predicate") or [None])[0],
                    min_confidence=float((qs.get("min_conf") or ["0"])[0]),
                )
                try:
                    self._json(200, QueryEngine(lattice).run(q))
                except VeridianError as exc:
                    self._json(400, {"error": str(exc)})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "invalid json"})
                return
            if parsed.path != "/api/claim":
                self._json(404, {"error": "not found"})
                return
            try:
                obs = claim(
                    lattice,
                    subject=str(data["subject"]),
                    predicate=str(data["predicate"]),
                    obj=str(data.get("object") or data.get("obj")),
                    value=data.get("value"),
                    agent_id=str(data.get("agent_id") or "web"),
                    sensor_id=str(data.get("sensor_id") or "ui"),
                    confidence=float(data.get("confidence", 0.8)),
                    gen_depth=int(data.get("gen_depth", 0)),
                )
                if persist:
                    save(lattice, persist)
                self._json(200, obs.to_dict())
            except (VeridianError, KeyError, TypeError, ValueError) as exc:
                self._json(400, {"error": str(exc)})

    return Handler


def serve(host: str, port: int, path: Path | None = None) -> None:
    lattice = load(path) if path and path.exists() else Lattice()
    httpd = ThreadingHTTPServer((host, port), _handler(lattice, path))
    print(f"Veridian at http://{host}:{port}/")
    httpd.serve_forever()
