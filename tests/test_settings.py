import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from opendevmate.settings import ConfigError, load_settings


class Nacos(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        raw = b'{"accessToken":"token-1"}'
        self.send_response(200)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        raw = b"port=9100\ndatabase=/data/from-nacos.sqlite3\nhost=10.1.2.3\n"
        self.send_response(200)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        return


def _serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Nacos)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_environment_is_used_when_nacos_is_not_configured():
    settings = load_settings({"APP_PORT": "8011", "APP_DATABASE": "/tmp/app.sqlite3", "APP_LOCALE": "en"})
    assert settings["config_source"] == "environment"
    assert settings["port"] == 8011
    assert settings["database"] == "/tmp/app.sqlite3"
    assert settings["default_locale"] == "en"


def test_nacos_overrides_concrete_values_and_keeps_placeholders():
    server = _serve()
    host, port = server.server_address
    try:
        settings = load_settings({
            "NACOS_SERVER": f"http://{host}:{port}",
            "NACOS_USERNAME": "reader",
            "NACOS_PASSWORD": "secret-pass",
            "APP_PORT": "8000",
        })
    finally:
        server.shutdown()
    assert settings["config_source"] == "nacos"
    assert settings["port"] == 9100
    assert settings["database"] == "/data/from-nacos.sqlite3"
    assert settings["host"] == "10.1.2.3"
    assert "secret-pass" not in str(settings)


def test_nacos_failure_does_not_reveal_the_password():
    with pytest.raises(ConfigError) as caught:
        load_settings({
            "NACOS_SERVER": "http://127.0.0.1:1",
            "NACOS_USERNAME": "reader",
            "NACOS_PASSWORD": "secret-pass",
        })
    assert "secret-pass" not in str(caught.value)
