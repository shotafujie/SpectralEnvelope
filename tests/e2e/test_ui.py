"""UI の E2E テスト。実サーバー + Chromium の偽マイク（合成母音 wav をループ再生）で録音から再生まで通す。

UI 側の観測点（テストとの契約）:
  #rec 録音ボタン（録音中は data-state="recording"） / #elapsed 経過秒
  #graph SVG（data-ymax, data-ymin, data-plot-left, data-plot-right）
    #orig-line / #mod-line 包絡線、line.band-line[data-freq] 帯域の縦線
  #frame フレームスライダー / #unvoiced 無声表示
  input[name=formant|tilt|band0..band3|smooth|pitch] と #<name>-value
  #reset / button[data-preset] / #play-orig / #play-mod / audio#player[data-source] / #error
"""

import json
import math
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pytest
from playwright.sync_api import expect, sync_playwright

from tests import audio_fixtures as af

ROOT = Path(__file__).resolve().parents[2]
SLIDERS = {
    "formant": (0.6, 1.6, 0.01, 1.0),
    "tilt": (-12, 12, 0.1, 0.0),
    "band0": (-12, 12, 0.1, 0.0),
    "band1": (-12, 12, 0.1, 0.0),
    "band2": (-12, 12, 0.1, 0.0),
    "band3": (-12, 12, 0.1, 0.0),
    "smooth": (0, 80, 1, 0),
    "pitch": (0.5, 2.0, 0.01, 1.0),
}
DEFAULTS = {k: v[3] for k, v in SLIDERS.items()}


# ---------------------------------------------------------------- フィクスチャ


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


# ---------------------------------------------------------------- 操作ヘルパ


def record(page, seconds=2.5):
    """録音して分解完了まで待ち、/api/analyze の応答 JSON を返す。"""
    with page.expect_response("**/api/analyze") as resp:
        page.click("#rec")
        page.wait_for_timeout(int(seconds * 1000))
        page.click("#rec")
    info = resp.value.json()
    expect(page.locator("#frame")).to_be_enabled()
    page.wait_for_function("id => document.querySelector('#graph').dataset.id === id", arg=info["id"])
    return info


def set_slider(page, name, value):
    page.eval_on_selector(
        f"input[name={name}]",
        "(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); }",
        str(value),
    )


def slider_values(page):
    return page.evaluate(
        "names => Object.fromEntries(names.map(n => [n, Number(document.querySelector(`input[name=${n}]`).value)]))",
        list(SLIDERS),
    )


def wait_playing(page, source):
    page.wait_for_function(
        "src => { const a = document.querySelector('#player');"
        " return a.dataset.source === src && !a.paused && a.currentTime > 0; }",
        arg=source,
    )


def rgb(css):
    return [int(float(v)) for v in css[css.index("(") + 1 : css.index(")")].split(",")[:3]]


def wait_envelope_count(page, n, timeout=2.0):
    deadline = time.monotonic() + timeout
    while len(page.reqs.of("/api/envelope")) < n and time.monotonic() < deadline:
        page.wait_for_timeout(50)
    return len(page.reqs.of("/api/envelope"))


# ---------------------------------------------------------------- 録音


def test_TC_200_1_録音中は経過秒が増える(page):
    page.click("#rec")
    expect(page.locator("#rec")).to_have_attribute("data-state", "recording")
    page.wait_for_timeout(1000)
    elapsed = float(page.inner_text("#elapsed").split()[0])
    assert elapsed >= 0.5
    page.click("#rec")


def test_TC_201_1_停止で自動送信される(page):
    record(page, 1.5)
    assert len(page.reqs.of("/api/analyze")) == 1


def test_TC_202_1_送信中は録音ボタンが無効(page):
    def slow(route):
        time.sleep(1.0)
        route.continue_()

    page.route("**/api/analyze", slow)
    page.click("#rec")
    page.wait_for_timeout(1500)
    page.click("#rec")
    expect(page.locator("#rec")).to_be_disabled()
    expect(page.locator("#rec")).to_be_enabled(timeout=10000)


def test_TC_203_1_10秒で自動停止する(page):
    page.click("#rec")
    start = time.monotonic()
    with page.expect_request("**/api/analyze", timeout=12000):
        pass
    elapsed = time.monotonic() - start
    assert 10.0 <= elapsed <= 11.5
    expect(page.locator("#rec")).not_to_have_attribute("data-state", "recording")


def test_TC_204_1_再録音でidが差し替わる(page):
    first = record(page)
    second = record(page)
    assert first["id"] != second["id"]
    page.reqs.clear()
    set_slider(page, "tilt", 2)
    assert wait_envelope_count(page, 1) >= 1
    assert page.reqs.of("/api/envelope")[-1]["body"]["id"] == second["id"]


def test_TC_205_1_未分解では再生ボタンが無効(page):
    expect(page.locator("#play-orig")).to_be_disabled()
    expect(page.locator("#play-mod")).to_be_disabled()


# ---------------------------------------------------------------- グラフ


def test_TC_210_1_元包絡と加工後包絡の2本(page):
    record(page)
    style = page.evaluate(
        "() => ['#orig-line', '#mod-line'].map(s => { const c = getComputedStyle(document.querySelector(s));"
        " return {stroke: c.stroke, width: parseFloat(c.strokeWidth)}; })"
    )
    orig, mod = style
    r, g, b = rgb(orig["stroke"])
    assert r == g == b
    assert len(set(rgb(mod["stroke"]))) > 1
    assert mod["width"] > orig["width"]
    assert page.get_attribute("#orig-line", "d") and page.get_attribute("#mod-line", "d")


def test_TC_211_1_横軸は対数スケール(page):
    record(page)
    left = float(page.get_attribute("#graph", "data-plot-left"))
    right = float(page.get_attribute("#graph", "data-plot-right"))
    for f in (500, 1500, 4000):
        x = float(page.get_attribute(f"line.band-line[data-freq='{f}']", "x1"))
        assert (x - left) / (right - left) == pytest.approx(math.log(f / 50) / math.log(441), abs=0.005)


def test_TC_212_1_縦軸は最大値プラス5から70dB幅(page):
    with page.expect_response("**/api/envelope") as resp:
        record(page)
    # 分解直後の描画に使われた最後の包絡
    page.wait_for_timeout(500)
    env = resp.value.json()
    freq = np.array(env["freq"])
    top = float(np.max(np.array(env["original_db"])[freq >= 50])) + 5
    ymax = float(page.get_attribute("#graph", "data-ymax"))
    ymin = float(page.get_attribute("#graph", "data-ymin"))
    assert ymax == pytest.approx(top, abs=0.01)
    assert ymin == pytest.approx(ymax - 70, abs=0.01)


def test_TC_213_1_帯域の縦線が3本(page):
    record(page)
    freqs = page.eval_on_selector_all("line.band-line", "ls => ls.map(l => Number(l.dataset.freq))")
    assert sorted(freqs) == [500, 1500, 4000]


# ---------------------------------------------------------------- フレーム選択


def test_TC_220_1_フレームスライダーの範囲(page):
    info = record(page)
    assert page.get_attribute("#frame", "min") == "0"
    assert page.get_attribute("#frame", "max") == str(info["frames"] - 1)


def test_TC_221_1_初期フレームは有声フレームの中央(page):
    info = record(page)
    v = info["voiced_frames"]
    assert page.input_value("#frame") == str(v[len(v) // 2])


def test_TC_222_1_無声フレームで表示が出る(page):
    info = record(page)
    voiced = set(info["voiced_frames"])
    unvoiced = next(i for i in range(info["frames"]) if i not in voiced)
    set_slider_frame(page, unvoiced)
    expect(page.locator("#unvoiced")).to_be_visible()
    set_slider_frame(page, info["voiced_frames"][0])
    expect(page.locator("#unvoiced")).to_be_hidden()


def set_slider_frame(page, value):
    page.eval_on_selector(
        "#frame",
        "(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); }",
        str(value),
    )


def test_TC_223_1_フレーム変更で包絡を取り直す(page):
    info = record(page)
    page.wait_for_timeout(500)
    page.reqs.clear()
    target = info["voiced_frames"][0]
    set_slider_frame(page, target)
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["body"]["frame"] == target


# ---------------------------------------------------------------- パラメータ


def test_TC_230_1_スライダーの範囲と初期値(page):
    for name, (lo, hi, step, init) in SLIDERS.items():
        attrs = page.eval_on_selector(
            f"input[name={name}]", "el => [el.min, el.max, el.step, el.value].map(Number)"
        )
        assert attrs == pytest.approx([lo, hi, step, init]), name


def test_TC_231_1_数値表示が追従する(page):
    set_slider(page, "formant", 1.25)
    expect(page.locator("#formant-value")).to_have_text("1.25")


def test_TC_232_1_ダブルクリックで初期値に戻る(page):
    set_slider(page, "tilt", 5)
    expect(page.locator("#tilt-value")).to_have_text("5.0")
    page.dblclick("input[name=tilt]")
    assert page.input_value("input[name=tilt]") == "0"
    expect(page.locator("#tilt-value")).to_have_text("0.0")


def test_TC_233_1_すべてリセット(page):
    for name, v in {"formant": 1.3, "tilt": 4, "band0": 3, "band1": -3, "band2": 5,
                    "band3": -5, "smooth": 20, "pitch": 1.5}.items():
        set_slider(page, name, v)
    page.click("#reset")
    assert slider_values(page) == pytest.approx(DEFAULTS)


def test_TC_234_1_TC_234_2_300msデバウンス(page):
    record(page)
    page.wait_for_timeout(600)
    page.reqs.clear()
    values = [1.1, 1.2, 1.3, 1.4, 1.45]
    for v in values:
        set_slider(page, "formant", v)
        page.wait_for_timeout(100)
    t_last = time.monotonic() - 0.1
    page.wait_for_timeout(150)  # 最後の変更から約 250ms
    assert page.reqs.of("/api/envelope") == []
    assert wait_envelope_count(page, 1, timeout=0.6) == 1
    sent = page.reqs.of("/api/envelope")[0]
    assert sent["t"] - t_last >= 0.29
    page.wait_for_timeout(500)
    assert len(page.reqs.of("/api/envelope")) == 1
    assert sent["body"]["params"]["formant"] == pytest.approx(1.45)


def test_TC_235_1_パラメータ変更で合成しない(page):
    record(page)
    set_slider(page, "formant", 1.3)
    set_slider(page, "tilt", -4)
    set_slider(page, "pitch", 1.2)
    page.wait_for_timeout(1000)
    assert page.reqs.of("/api/synthesize") == []


def test_TC_236_1_smooth5は10として描画される(page):
    info = record(page)
    page.wait_for_timeout(500)
    with page.expect_response("**/api/envelope") as resp:
        set_slider(page, "smooth", 5)
    shown = resp.value.json()["modified_db"]
    ref = page.request.post("/api/envelope", data={
        "id": info["id"], "frame": int(page.input_value("#frame")), "params": {"smooth": 10},
    }).json()["modified_db"]
    assert shown == ref


# ---------------------------------------------------------------- 再生


def test_TC_240_1_加工音ボタンでその時点の値で合成して再生(page):
    record(page)
    set_slider(page, "formant", 1.3)
    page.click("#play-mod")
    wait_playing(page, "processed")
    body = page.reqs.of("/api/synthesize")[-1]["body"]
    assert body["params"]["formant"] == pytest.approx(1.3)


def test_TC_241_1_合成待ちはローディング表示(page):
    record(page)

    def slow(route):
        time.sleep(1.0)
        route.continue_()

    page.route("**/api/synthesize", slow)
    page.click("#play-mod")
    expect(page.locator("#play-mod")).to_have_attribute("aria-busy", "true")
    expect(page.locator("#play-mod")).not_to_have_attribute("aria-busy", "true", timeout=10000)


def test_TC_242_1_元音ボタンで元音を再生(page):
    info = record(page)
    page.click("#play-orig")
    wait_playing(page, "original")
    assert page.get_attribute("#player", "src").endswith(f"/api/original/{info['id']}")


def test_TC_243_1_スペースで元音と加工音が交互に再生される(page):
    record(page)
    page.keyboard.press("Space")
    wait_playing(page, "original")
    page.keyboard.press("Space")
    wait_playing(page, "processed")
    page.keyboard.press("Space")
    wait_playing(page, "original")


def test_TC_243_2_加工音の後のスペースは元音(page):
    record(page)
    page.click("#play-mod")
    wait_playing(page, "processed")
    page.keyboard.press("Space")
    wait_playing(page, "original")


def test_TC_244_1_ボタンにフォーカスがあってもスペースはAB切替(page):
    record(page)
    page.focus("#play-mod")
    page.keyboard.press("Space")
    wait_playing(page, "original")
    page.wait_for_timeout(500)
    assert page.reqs.of("/api/synthesize") == []


def test_TC_244_2_スライダーにフォーカスがあってもスクロールしない(page):
    page.set_viewport_size({"width": 800, "height": 300})
    record(page)
    page.focus("input[name=formant]")
    before = (page.input_value("input[name=formant]"), page.evaluate("scrollY"))
    page.keyboard.press("Space")
    wait_playing(page, "original")
    assert (page.input_value("input[name=formant]"), page.evaluate("scrollY")) == before


def test_TC_245_1_新しい再生で前の音は止まる(page):
    record(page)
    page.click("#play-orig")
    wait_playing(page, "original")
    page.wait_for_timeout(700)
    page.click("#play-mod")
    page.wait_for_function(
        "() => { const a = document.querySelector('#player');"
        " return a.dataset.source === 'processed' && !a.paused; }"
    )
    assert page.evaluate("document.querySelector('#player').currentTime") < 0.5
    playing = page.evaluate("[...document.querySelectorAll('audio,video')].filter(m => !m.paused).length")
    assert playing == 1


# ---------------------------------------------------------------- プリセット


PRESETS = {
    "素通し": {},
    "子供っぽく": {"formant": 1.25, "pitch": 1.15},
    "太く": {"formant": 0.85, "tilt": -3.0},
    "こもる": {"band0": 4, "band1": 0, "band2": -6, "band3": -10},
    "のっぺり": {"smooth": 16},
}


def test_TC_250_1_プリセットで表の値になる(page):
    for name, values in PRESETS.items():
        set_slider(page, "tilt", 7)  # 直前の状態が残らないことも見る
        page.click(f"button[data-preset='{name}']")
        assert slider_values(page) == pytest.approx({**DEFAULTS, **values}), name


def test_TC_250_2_プリセットを続けて押すと前の値が消える(page):
    page.click("button[data-preset='太く']")
    page.click("button[data-preset='こもる']")
    assert slider_values(page) == pytest.approx({**DEFAULTS, **PRESETS["こもる"]})


# ---------------------------------------------------------------- エラー


def test_TC_260_1_分解エラーを表示する(page):
    page.route("**/api/analyze", lambda r: r.fulfill(
        status=400, content_type="application/json", body=json.dumps({"detail": "too short"})))
    page.click("#rec")
    page.wait_for_timeout(1200)
    page.click("#rec")
    expect(page.locator("#error")).to_contain_text("too short")
    expect(page.locator("#rec")).to_be_enabled()


def test_TC_260_2_合成エラーを表示する(page):
    record(page)
    page.route("**/api/synthesize", lambda r: r.fulfill(status=500, body="boom"))
    page.click("#play-mod")
    expect(page.locator("#error")).not_to_be_empty()
    expect(page.locator("#play-mod")).not_to_have_attribute("aria-busy", "true")


def test_TC_261_1_マイク取得失敗を表示する(browser, base_url):
    ctx = browser.new_context(base_url=base_url)
    pg = ctx.new_page()
    pg.add_init_script(
        "navigator.mediaDevices.getUserMedia = () =>"
        " Promise.reject(new DOMException('denied', 'NotAllowedError'));"
    )
    pg.goto("/")
    pg.click("#rec")
    expect(pg.locator("#error")).not_to_be_empty()
    ctx.close()
