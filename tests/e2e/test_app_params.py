"""ブラウザ版のパラメータ操作・プリセット・ゲインカーブ（008-browser-app）。"""

import time

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    CURVE_FREQS,
    DEFAULTS,
    SLIDERS,
    app_record,
    calls,
    clear_calls,
    curve_gains,
    drag_handle,
    handle,
    log_x_ratio,
    plot_box,
    set_slider,
    slider_values,
    wait_calls,
)


def center(page):
    b = plot_box(page)
    return (b["top"] + b["bottom"]) / 2


def last_params(page, name="envelope"):
    return calls(page, name)[-1]["args"][-1]


# ---------------------------------------------------------------- スライダー

def test_TC_960_1_スライダーの範囲と初期値(ui_page):
    for name, (lo, hi, step, init) in SLIDERS.items():
        attrs = ui_page.eval_on_selector(
            f"input[name={name}]", "el => [el.min, el.max, el.step, el.value].map(Number)")
        assert attrs == pytest.approx([lo, hi, step, init]), name


def test_TC_961_1_数値表示が追従する(ui_page):
    set_slider(ui_page, "formant", 1.3)
    expect(ui_page.locator("#formant-value")).to_have_text("1.30")


def test_TC_962_1_ダブルクリックで初期値に戻る(ui_page):
    set_slider(ui_page, "tilt", 5)
    expect(ui_page.locator("#tilt-value")).to_have_text("5.0")
    ui_page.dblclick("input[name=tilt]")
    assert float(ui_page.input_value("input[name=tilt]")) == 0.0
    expect(ui_page.locator("#tilt-value")).to_have_text("0.0")


def test_TC_963_1_すべてリセット(ui_page):
    for name, v in {"formant": 1.3, "tilt": 4, "band0": 3, "band1": -3, "band2": 5,
                    "band3": -5, "smooth": 20, "pitch": 1.5}.items():
        set_slider(ui_page, name, v)
    ui_page.click("#reset")
    assert slider_values(ui_page) == pytest.approx(DEFAULTS)


def test_TC_964_1_300msデバウンス(ui_page):
    app_record(ui_page)
    ui_page.wait_for_timeout(600)
    clear_calls(ui_page)
    for v in [1.1, 1.2, 1.3, 1.4, 1.45]:
        set_slider(ui_page, "formant", v)
        ui_page.wait_for_timeout(100)
    t_last = time.monotonic() - 0.1
    ui_page.wait_for_timeout(150)  # 最後の変更から約 250ms
    assert calls(ui_page, "envelope") == []
    assert wait_calls(ui_page, "envelope", 1, timeout=0.6) == 1
    ui_page.wait_for_timeout(500)
    sent = calls(ui_page, "envelope")
    assert len(sent) == 1
    assert sent[0]["args"][2]["formant"] == pytest.approx(1.45)
    assert time.monotonic() - t_last >= 0.29


def test_TC_965_1_パラメータ変更で合成しない(ui_page):
    app_record(ui_page)
    clear_calls(ui_page)
    for name, v in (("formant", 1.3), ("tilt", -4), ("pitch", 1.2)):
        set_slider(ui_page, name, v)
    ui_page.wait_for_timeout(1000)
    assert calls(ui_page, "synthesize") == []


def test_TC_966_1_smooth5は10として送られる(ui_page):
    app_record(ui_page)
    clear_calls(ui_page)
    set_slider(ui_page, "smooth", 5)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert last_params(ui_page)["smooth"] == 10


# ---------------------------------------------------------------- プリセット

def test_TC_967_1_子供っぽく(ui_page):
    set_slider(ui_page, "tilt", 5)
    ui_page.click("button[data-preset='子供っぽく']")
    values = slider_values(ui_page)
    assert values["formant"] == pytest.approx(1.25)
    assert values["pitch"] == pytest.approx(1.15)
    for name in ("tilt", "band0", "band1", "band2", "band3", "smooth"):
        assert values[name] == pytest.approx(DEFAULTS[name]), name


def test_TC_967_2_こもる(ui_page):
    ui_page.click("button[data-preset='こもる']")
    values = slider_values(ui_page)
    assert [values[f"band{i}"] for i in range(4)] == pytest.approx([4, 0, -6, -10])
    for name in ("formant", "tilt", "smooth", "pitch"):
        assert values[name] == pytest.approx(DEFAULTS[name]), name


# ---------------------------------------------------------------- ゲインカーブ

def test_TC_970_1_ハンドルは20個で対数軸に並ぶ(ui_page):
    b = plot_box(ui_page)
    assert ui_page.locator("circle.curve-point").count() == 20
    for j, f in enumerate(CURVE_FREQS):
        cx = float(handle(ui_page, j).get_attribute("cx"))
        assert cx == pytest.approx(b["left"] + (b["right"] - b["left"]) * log_x_ratio(f), abs=0.01)


def test_TC_971_1_ゲインに応じたy位置(ui_page):
    drag_handle(ui_page, 7, gain=6.0)
    g = float(handle(ui_page, 7).get_attribute("data-gain"))
    b = plot_box(ui_page)
    expected = center(ui_page) - g * (b["bottom"] - b["top"]) / 70
    assert float(handle(ui_page, 7).get_attribute("cy")) == pytest.approx(expected, abs=1.0)


def test_TC_972_1_ドラッグでゲインが変わる(ui_page):
    drag_handle(ui_page, 7, gain=6.0)
    gains = curve_gains(ui_page)
    assert gains[7] == pytest.approx(6.0, abs=0.1)
    assert abs(gains[7] * 10 - round(gains[7] * 10)) < 1e-9
    assert all(g == 0 for i, g in enumerate(gains) if i != 7)


def test_TC_972_2_上端を超えるとクランプ(ui_page):
    b = plot_box(ui_page)
    drag_handle(ui_page, 3, svg_y=b["top"] - 40)
    assert curve_gains(ui_page)[3] == 12.0


def test_TC_973_1_横に動かしても制御点は変わらない(ui_page):
    cx = handle(ui_page, 10).get_attribute("cx")
    drag_handle(ui_page, 10, gain=4.0, dx=120)
    assert handle(ui_page, 10).get_attribute("cx") == cx
    assert handle(ui_page, 10).get_attribute("data-index") == "10"
    assert curve_gains(ui_page)[10] > 0


def test_TC_974_1_ゲイン線がハンドルに追従する(ui_page):
    drag_handle(ui_page, 6, gain=-5.0)
    h = handle(ui_page, 6)
    d = ui_page.get_attribute("#curve-line", "d")
    assert f"{h.get_attribute('cx')},{h.get_attribute('cy')}" in d


def test_TC_975_1_ドラッグ中は周波数とゲインを表示する(ui_page):
    drag_handle(ui_page, 7, gain=6.0, release=False)
    g = curve_gains(ui_page)[7]
    readout = ui_page.inner_text("#curve-readout")
    ui_page.mouse.up()
    assert str(round(CURVE_FREQS[7])) in readout
    assert f"{g:+.1f}".replace("+", "+") in readout or f"{g:.1f}" in readout


def test_TC_976_1_ゲイン変更後にenvelopeが呼ばれる(ui_page):
    app_record(ui_page)
    ui_page.wait_for_timeout(600)
    clear_calls(ui_page)
    drag_handle(ui_page, 12, gain=5.0)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert last_params(ui_page)["curve"] == pytest.approx(curve_gains(ui_page))


def test_TC_978_1_ハンドルのダブルクリックで0に戻る(ui_page):
    drag_handle(ui_page, 5, gain=7.0)
    assert curve_gains(ui_page)[5] != 0
    handle(ui_page, 5).dblclick()
    assert curve_gains(ui_page)[5] == 0


def test_TC_979_1_すべてリセットでカーブも戻る(ui_page):
    drag_handle(ui_page, 4, gain=6.0)
    drag_handle(ui_page, 14, gain=-6.0)
    ui_page.click("#reset")
    assert curve_gains(ui_page) == [0] * 20


def test_TC_979_2_プリセットでカーブも戻る(ui_page):
    drag_handle(ui_page, 4, gain=6.0)
    ui_page.click("button[data-preset='太く']")
    assert curve_gains(ui_page) == [0] * 20


def test_TC_980_1_分解前でもハンドルを動かせる(ui_page):
    drag_handle(ui_page, 9, gain=3.0)
    assert curve_gains(ui_page)[9] == pytest.approx(3.0, abs=0.1)
