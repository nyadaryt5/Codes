"""Read-only local HTTP API. Does not execute training or load user models."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from titanfuse.config import TrainConfig
from titanfuse.errors import TitanFuseError
from titanfuse.stack import TitanFuse

INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>TitanFuse planner</title>
  <style>
    body { font-family: ui-sans-serif, system-ui; max-width: 42rem; margin: 2rem auto; color: #111; }
    code { background: #f3f3f3; padding: 0.1rem 0.3rem; }
    pre { background: #111; color: #eee; padding: 1rem; overflow: auto; }
    label { display: block; margin-top: 0.6rem; }
  </style>
</head>
<body>
  <h1>TitanFuse</h1>
  <p>Routes <strong>Unsloth</strong>, <strong>Liger-Kernel</strong>, and <strong>TorchTitan</strong>.</p>
  <form id="f">
    <label>Workload <select name="workload">
      <option>sft</option><option>pretrain</option><option>dpo</option><option>distill</option>
    </select></label>
    <label>GPUs <input name="gpus" type="number" value="1" min="1"/></label>
    <label>VRAM GB <input name="vram" type="number" value="16" min="1"/></label>
    <label>Model <input name="model" value="meta-llama/Llama-3.2-1B"/></label>
    <button type="submit">Plan</button>
  </form>
  <pre id="out"></pre>
  <script>
    document.getElementById('f').onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const q = new URLSearchParams(fd);
      const r = await fetch('/api/recommend?' + q.toString());
      document.getElementById('out').textContent = JSON.stringify(await r.json(), null, 2);
    };
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = INDEX.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/health":
            self._json(200, {"ok": True})
            return
        if parsed.path == "/api/recommend":
            qs = parse_qs(parsed.query)
            try:
                gpus = int((qs.get("gpus") or ["1"])[0])
                vram = float((qs.get("vram") or ["16"])[0])
                workload = (qs.get("workload") or ["sft"])[0]
                model = (qs.get("model") or ["meta-llama/Llama-3.2-1B"])[0]
                cfg = TrainConfig(backend="auto", workload=workload, model=model)  # type: ignore[arg-type]
                fuse = TitanFuse(cfg, gpu_count=gpus, vram_gb=vram)
                self._json(200, {"summary": fuse.summary(), "plan": fuse.plan()})
            except (TitanFuseError, ValueError) as exc:
                self._json(400, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})


def serve(host: str, port: int) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"TitanFuse planner at http://{host}:{port}/")
    httpd.serve_forever()
