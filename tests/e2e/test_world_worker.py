"""WORLD エンジンを Chromium のモジュール Worker から読み込む（006-wasm-world / SPEC-714）。"""

import functools
import http.server
import threading
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".wasm": "application/wasm"}

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def static_url():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_TC_714_1_モジュールWorkerの中でエンジンを読み込み分解できる(browser, static_url):
    ctx = browser.new_context()
    page = ctx.new_page()
    try:
        page.goto(f"{static_url}/tests/e2e/world_worker.html")
        page.wait_for_function("window.result !== undefined", timeout=20000)
        result = page.evaluate("window.result")
        assert "error" not in result, result.get("error")
        golden = np.fromfile(ROOT / "tests/golden/world-a-1s.f0.f64", "<f8")
        f0 = np.array(result["f0"])
        assert f0.shape == golden.shape
        assert np.max(np.abs(f0 - golden)) <= 1e-6
    finally:
        ctx.close()
