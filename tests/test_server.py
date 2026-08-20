from threading import Thread
from urllib.request import urlopen

from titanfuse.server import Handler
from http.server import ThreadingHTTPServer


def test_health_and_recommend():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        health = urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        assert b'"ok"' in health.read()
        rec = urlopen(
            f"http://127.0.0.1:{port}/api/recommend?gpus=1&vram=16&workload=sft&model=Llama-1B",
            timeout=5,
        )
        body = rec.read().decode()
        assert "unsloth" in body
        page = urlopen(f"http://127.0.0.1:{port}/", timeout=5)
        assert b"TitanFuse" in page.read()
    finally:
        httpd.shutdown()
