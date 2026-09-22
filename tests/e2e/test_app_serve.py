"""ブラウザ版の静的配信と速さ（008-browser-app）。"""

import base64
import json
import statistics
from pathlib import Path

import pytest

from tests import audio_fixtures as af
from tests.e2e.helpers import app_record, app_wait_playing, set_slider

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmarks/browser-app"


@pytest.fixture(scope="module")
def wav3_b64():
    return base64.b64encode(af.wav_bytes(af.vowel("a", 3.0))).decode()


# ---------------------------------------------------------------- 静的配信

def test_TC_1030_1_静的配信だけで一通り動く(ui_page):
    """ui_page は静的ファイルを返すだけのサーバー（SimpleHTTPRequestHandler）で配信されている。"""
    info = app_record(ui_page)
    assert info["frames"] > 0
    assert ui_page.get_attribute("#mod-line", "d")
    ui_page.click("#play-mod")
    app_wait_playing(ui_page, "processed")


def test_TC_1031_1_外へ出る要求はアプリ自身のファイルだけ(browser, static_url):
    from tests.e2e.conftest import ADAPTER_HELPERS, RECORDER

    ctx = browser.new_context(base_url=static_url, permissions=["microphone"])
    page = ctx.new_page()
    page.set_default_timeout(20000)
    page.add_init_script(ADAPTER_HELPERS + RECORDER)
    seen = []
    page.on("request", lambda r: seen.append(r.url))
    try:
        page.goto("/app/index.html")
        page.wait_for_function("() => window.engine !== undefined")
        app_record(page)
        page.click("#play-mod")
        app_wait_playing(page, "processed")
    finally:
        ctx.close()

    paths = [u.split(static_url, 1)[-1] for u in seen]
    assert [p for p in paths if p.startswith("/api/")] == []
    allowed = (".html", ".js", ".mjs", ".wasm")
    assert [p for p in paths if not p.split("?")[0].endswith(allowed)] == []


# ---------------------------------------------------------------- 速さ

def median_of(values):
    return statistics.median(values)


def test_TC_1040_1_3秒の分解は3秒未満(ui_page, wav3_b64):
    times = ui_page.evaluate("""async (b) => {
        const t = [];
        for (let i = 0; i < 5; i++) {
            const t0 = performance.now();
            await window.engine.analyze(window.__bytes(b), '録音');
            t.push((performance.now() - t0) / 1000);
        }
        return t;
    }""", wav3_b64)
    assert median_of(times) < 3.0, times


def test_TC_1042_1_3秒の再合成は1秒未満(ui_page, wav3_b64):
    times = ui_page.evaluate("""async (b) => {
        const info = await window.engine.analyze(window.__bytes(b), '録音');
        const params = { formant: 1.2, tilt: 3, bands: [2, -2, 4, -4], smooth: 30, pitch: 1.2,
                         curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j) };
        const t = [];
        for (let i = 0; i < 5; i++) {
            const t0 = performance.now();
            await window.engine.synthesize(info.id, params);
            t.push((performance.now() - t0) / 1000);
        }
        return t;
    }""", wav3_b64)
    assert median_of(times) < 1.0, times


def test_TC_1041_1_つまみからグラフ更新まで1秒未満(ui_page, wav_files):
    from tests.e2e.helpers import app_load_file

    partner = app_load_file(ui_page, wav_files["voice"])["id"]
    app_record(ui_page)
    ui_page.select_option("#partner", partner)
    set_slider(ui_page, "mix", 0.5)
    ui_page.wait_for_timeout(1200)
    times = ui_page.evaluate("""async () => {
        const line = document.querySelector('#mod-line');
        const input = document.querySelector('input[name=formant]');
        const t = [];
        for (let i = 0; i < 5; i++) {
            const before = line.getAttribute('d');
            const t0 = performance.now();
            input.value = String(1.05 + 0.05 * i);
            input.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(resolve => {
                const check = () => (line.getAttribute('d') !== before ? resolve() : requestAnimationFrame(check));
                check();
            });
            t.push((performance.now() - t0) / 1000);
        }
        return t;
    }""")
    assert median_of(times) < 1.0, times


# ---------------------------------------------------------------- 基準値

def test_TC_1043_1_基準値がある():
    data = json.loads((BENCH / "baseline.json").read_text())
    medians = data["median_seconds"]
    for key in ("analyze_3s", "envelope_after_slider", "synthesize_3s"):
        assert isinstance(medians[key], (int, float)) and medians[key] > 0, key


def test_TC_1043_2_計測コマンドが書かれている():
    text = (BENCH / "README.md").read_text()
    assert "benchmarks/browser-app/run.py" in text
