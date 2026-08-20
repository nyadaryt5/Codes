from threading import Thread
from urllib.request import urlopen

from veridian.server import _handler
from veridian.lattice import Lattice
from http.server import ThreadingHTTPServer


def test_health_page():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _handler(Lattice(), None))
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        health = urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        assert b'"ok"' in health.read()
        page = urlopen(f"http://127.0.0.1:{port}/", timeout=5)
        assert b"Veridian" in page.read()
    finally:
        httpd.shutdown()
