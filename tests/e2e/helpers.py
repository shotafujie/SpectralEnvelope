"""E2E の操作ヘルパ。

UI 側の観測点（テストとの契約）:
  #rec 録音ボタン（録音中は data-state="recording"） / #elapsed 経過秒
  #open-file / #file ファイル読み込み
  #graph SVG（data-id, data-ymax, data-ymin, data-plot-left/right/top/bottom）
    #orig-line / #mod-line / #partner-line 包絡線、line.band-line[data-freq] 帯域の縦線
    circle.curve-point[data-index][data-gain] ゲインカーブの制御点、#curve-line、#curve-readout
  #frame フレームスライダー / #unvoiced 無声表示
  input[name=formant|tilt|band0..band3|smooth|pitch|mix] と #<name>-value
  #current / #partner 録音の選択欄
  #reset / button[data-preset] / #play-orig / #play-mod / audio#player[data-source] / #error
"""

import math
import time

from playwright.sync_api import expect

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
CURVE_FREQS = [50 * 400 ** (j / 19) for j in range(20)]


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
    """指定の音が再生中になるまで待ち、そのときの currentTime を返す。"""
    handle = page.wait_for_function(
        "src => { const a = document.querySelector('#player');"
        " return a.dataset.source === src && !a.paused && a.currentTime > 0 && a.currentTime; }",
        arg=source,
        polling=20,
    )
    return handle.json_value()


def hold_requests(page, pattern):
    """pattern に一致する要求を保留する。戻り値のリストに route が溜まるので、テスト側で continue_ する。"""
    held = []

    def handler(route):
        held.append(route)

    page.route(pattern, handler)
    return held


def wait_held(page, held, timeout=10.0):
    deadline = time.monotonic() + timeout
    while not held:
        assert time.monotonic() < deadline, "request was not issued"
        page.wait_for_timeout(50)


def rgb(css):
    return [int(float(v)) for v in css[css.index("(") + 1 : css.index(")")].split(",")[:3]]


def wait_envelope_count(page, n, timeout=2.0):
    deadline = time.monotonic() + timeout
    while len(page.reqs.of("/api/envelope")) < n and time.monotonic() < deadline:
        page.wait_for_timeout(50)
    return len(page.reqs.of("/api/envelope"))



def set_slider_frame(page, value):
    page.eval_on_selector(
        "#frame",
        "(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); }",
        str(value),
    )


def load_file(page, path):
    """ファイルを読み込んで分解完了まで待ち、/api/analyze の応答 JSON を返す。"""
    with page.expect_response("**/api/analyze") as resp:
        page.set_input_files("#file", str(path))
    info = resp.value.json()
    page.wait_for_function("id => document.querySelector('#graph').dataset.id === id", arg=info["id"])
    return info


def plot_box(page):
    g = page.locator("#graph")
    return {k: float(g.get_attribute(f"data-plot-{k}")) for k in ("left", "right", "top", "bottom")}


def curve_gains(page):
    return page.eval_on_selector_all(
        "circle.curve-point",
        "cs => cs.sort((a, b) => a.dataset.index - b.dataset.index).map(c => Number(c.dataset.gain))",
    )


def handle(page, j):
    return page.locator(f"circle.curve-point[data-index='{j}']")


def svg_to_client(page, x, y):
    return page.evaluate(
        "([x, y]) => { const s = document.querySelector('#graph'); const p = s.createSVGPoint();"
        " p.x = x; p.y = y; const q = p.matrixTransform(s.getScreenCTM()); return [q.x, q.y]; }",
        [x, y],
    )


def gain_to_svg_y(page, gain):
    b = plot_box(page)
    return (b["top"] + b["bottom"]) / 2 - gain * (b["bottom"] - b["top"]) / 70


def drag_handle(page, j, gain=None, svg_y=None, dx=0, steps=5, release=True):
    """ハンドル j を、ゲイン gain（または SVG 座標 svg_y）の高さまでドラッグする。"""
    h = handle(page, j)
    cx, cy = float(h.get_attribute("cx")), float(h.get_attribute("cy"))
    x0, y0 = svg_to_client(page, cx, cy)
    target = gain_to_svg_y(page, gain) if svg_y is None else svg_y
    _, y1 = svg_to_client(page, cx, target)
    page.mouse.move(x0, y0)
    page.mouse.down()
    page.mouse.move(x0 + dx, y1, steps=steps)
    last_move = time.monotonic()
    if release:
        page.mouse.up()
    return last_move


def log_x_ratio(f):
    return math.log(f / 50) / math.log(441)


# ---------------------------------------------------------------- ブラウザ版（008-browser-app）
#
# 観測点はネットワーク要求ではなくアダプタの呼び出し（window.__calls）。
# 画面側の観測点は v0.1.0 と同じだが、再生は audio 要素ではなく
# #player の data-source / data-playing（AudioBuffer で鳴らすため）。

def calls(page, name=None):
    items = page.evaluate("() => window.__calls")
    return [c for c in items if name is None or c["name"] == name]


def clear_calls(page):
    page.evaluate("() => { window.__calls.length = 0; }")


def wait_calls(page, name, n, timeout=3.0):
    """name の呼び出しが n 件以上になるまで待ち、件数を返す（増えなくても落とさない）。"""
    deadline = time.monotonic() + timeout
    while len(calls(page, name)) < n and time.monotonic() < deadline:
        page.wait_for_timeout(50)
    return len(calls(page, name))


def hold(page, name):
    """name の呼び出しの解決を保留する（release で解く）。"""
    page.evaluate("n => { window.__hold = n; }", name)


def wait_held(page, timeout=10.0):
    deadline = time.monotonic() + timeout
    while not page.evaluate("() => window.__held.length"):
        assert time.monotonic() < deadline, "保留された呼び出しがありません"
        page.wait_for_timeout(50)


def release(page):
    page.evaluate("() => window.__release()")


def app_record(page, seconds=2.5):
    """録音して分解完了まで待ち、その分解結果の情報を返す。"""
    prev = graph_id(page)
    page.click("#rec")
    page.wait_for_timeout(int(seconds * 1000))
    page.click("#rec")
    expect(page.locator("#frame")).to_be_enabled()
    wait_new_graph_id(page, prev)
    return app_info(page)


def app_load_file(page, path):
    """ファイルを読み込んで分解完了まで待ち、その分解結果の情報を返す。"""
    prev = graph_id(page)
    page.set_input_files("#file", str(path))
    wait_new_graph_id(page, prev)
    return app_info(page)


def graph_id(page):
    return page.evaluate("() => document.querySelector('#graph').dataset.id || ''")


def wait_new_graph_id(page, prev):
    page.wait_for_function(
        "prev => { const id = document.querySelector('#graph').dataset.id; return id && id !== prev; }", arg=prev)


def app_info(page):
    """今グラフに出ている分解結果の情報。"""
    return page.evaluate("""async () => {
        const id = document.querySelector('#graph').dataset.id;
        return (await window.engine.list()).find(i => i.id === id) || null;
    }""")


def app_wait_playing(page, source, timeout=10000):
    """指定の音が鳴り始めるまで待つ。"""
    page.wait_for_function(
        "src => { const p = document.querySelector('#player');"
        " return p.dataset.source === src && p.dataset.playing !== '0'; }",
        arg=source, polling=20, timeout=timeout,
    )


def app_playing_count(page):
    return int(page.get_attribute("#player", "data-playing"))
