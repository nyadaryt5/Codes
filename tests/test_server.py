import logging
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen

from titanfuse.server import Handler, serve


def test_serve_emits_info_log(caplog, monkeypatch):
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", lambda self: None)
    with caplog.at_level(logging.INFO, logger="titanfuse.server"):
        serve("127.0.0.1", 0)
    assert "titanfuse listening" in caplog.text


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
