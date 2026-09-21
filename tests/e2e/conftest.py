"""E2E 共通のフィクスチャ: 実サーバー + 偽マイク付き Chromium + 要求の記録。"""

import functools
import http.server
import json
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from tests import audio_fixtures as af

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def fake_mic_wav(tmp_path_factory):
    # 0.5 秒無音 + 1.5 秒母音 + 0.5 秒無音。2.5 秒録れば必ず無声区間を含む
    path = tmp_path_factory.mktemp("mic") / "vowel.wav"
    path.write_bytes(af.wav_bytes(af.with_silence(af.vowel("a", 1.5))))
    return path


@pytest.fixture(scope="session")
def base_url():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    proc = subprocess.Popen([sys.executable, "jig/server.py", "--port", str(port)], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://localhost:{port}"
    deadline = time.time() + 20
    while True:
        try:
            urllib.request.urlopen(url + "/", timeout=1)
            break
        except OSError:
            if time.time() > deadline:
                proc.kill()
                raise
            time.sleep(0.2)
    yield url
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def browser(fake_mic_wav):
    with sync_playwright() as p:
        b = p.chromium.launch(args=[
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-audio-capture={fake_mic_wav}",
            "--autoplay-policy=no-user-gesture-required",
        ])
        yield b
        b.close()


class Requests:
    def __init__(self):
        self.items = []

    def of(self, path):
        return [r for r in self.items if r["path"] == path]

    def clear(self):
        self.items.clear()


@pytest.fixture
def page(browser, base_url):
    ctx = browser.new_context(base_url=base_url, permissions=["microphone"])
    pg = ctx.new_page()
    pg.set_default_timeout(8000)
    reqs = Requests()

    def on_request(req):
        path = req.url.split(base_url, 1)[-1]
        body = None
        if req.method == "POST" and path != "/api/analyze":
            body = json.loads(req.post_data or "null")
        reqs.items.append({"path": path, "body": body, "t": time.monotonic()})

    pg.on("request", on_request)
    pg.reqs = reqs
    pg.goto("/")
    yield pg
    ctx.close()



@pytest.fixture(scope="session")
def wav_files(tmp_path_factory):
    """読み込みテスト用のファイル一式。"""
    d = tmp_path_factory.mktemp("files")
    files = {
        "voice": ("voice.wav", af.wav_bytes(af.vowel("i", 3.0))),
        "one_sec": ("one_sec.wav", af.wav_bytes(af.vowel("a", 1.0))),
        "short": ("short.wav", af.wav_bytes(af.vowel("a", 0.5))),
        "broken": ("broken.wav", bytes(range(256)) * 4),
    }
    paths = {}
    for key, (name, data) in files.items():
        paths[key] = d / name
        paths[key].write_bytes(data)
    return paths

# ---------------------------------------------------------------- ブラウザ版（008-browser-app）

class _Static(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".wasm": "application/wasm"}

    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def static_url():
    """リポジトリ直下を静的に返すだけのサーバー（サーバー側の処理を持たない）。"""
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Static, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture
def app_page(browser, static_url):
    """ブラウザ版のページ。window.engine（アダプタ）が使える。"""
    ctx = browser.new_context(base_url=static_url, permissions=["microphone"])
    pg = ctx.new_page()
    pg.set_default_timeout(20000)
    pg.add_init_script(ADAPTER_HELPERS)
    pg.goto("/app/index.html")
    yield pg
    ctx.close()


# テストからアダプタを呼ぶための道具。拒否は { ok: false, code } に畳んで受け取る
ADAPTER_HELPERS = """
window.__bytes = b64 => Uint8Array.from(atob(b64), c => c.charCodeAt(0));
window.__settle = p => p.then(
  value => ({ ok: true, value }),
  e => ({ ok: false, code: e && e.code, message: String(e && e.message) }),
);
"""
