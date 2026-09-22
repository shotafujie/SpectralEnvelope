"""成果物の対・ライセンス表示・配信物の画面（009-pages-deploy）。"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def stamp_hashes():
    text = (ROOT / "engine/world/stamp.mjs").read_text()
    wasm = re.search(r'WORLD_WASM_SHA256 = "([0-9a-f]{64})"', text).group(1)
    mjs = re.search(r'WORLD_MJS_SHA256 = "([0-9a-f]{64})"', text).group(1)
    return wasm, mjs


@pytest.fixture
def engine_page(browser, static_url):
    """アプリを開き、ネットワーク要求と console を記録する。"""
    from tests.e2e.conftest import ADAPTER_HELPERS

    ctx = browser.new_context(base_url=static_url)
    page = ctx.new_page()
    page.set_default_timeout(20000)
    page.add_init_script(ADAPTER_HELPERS)
    urls, logs = [], []
    page.on("request", lambda r: urls.append(r.url))
    page.on("console", lambda m: logs.append(m.text))
    page.goto("/app/index.html")
    page.wait_for_function("() => window.engine !== undefined")
    # エンジンの読み込みが終わるまで待つ（list() はエンジンの準備後に解決する）
    page.evaluate("async () => { await window.engine.list(); }")
    yield page, urls, logs
    ctx.close()


def test_TC_1140_1_wasmのURLに印が入る(engine_page):
    _, urls, _ = engine_page
    wasm, _ = stamp_hashes()
    got = [u for u in urls if "world.wasm" in u]
    assert got, urls
    assert all(wasm[:12] in u for u in got), got


def test_TC_1141_1_glueのURLにも同じ印が入る(engine_page):
    _, urls, _ = engine_page
    wasm, _ = stamp_hashes()
    got = [u for u in urls if "world.mjs" in u]
    assert got, urls
    assert all(wasm[:12] in u for u in got), got


def test_TC_1142_1_スタンプの値がconsoleに出る(engine_page):
    _, _, logs = engine_page
    wasm, mjs = stamp_hashes()
    hits = [m for m in logs if wasm in m]
    assert len(hits) == 1, logs
    assert mjs in hits[0]
