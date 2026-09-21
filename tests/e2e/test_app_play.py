"""ブラウザ版の再生・比較（008-browser-app）。WAV を作らず AudioBuffer で鳴らす。"""

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    app_playing_count,
    app_record,
    app_wait_playing,
    calls,
    clear_calls,
    curve_gains,
    drag_handle,
    hold,
    release,
    set_slider,
    wait_held,
)


def last_params(page, name):
    return calls(page, name)[-1]["args"][-1]


def test_TC_1000_1_加工音ボタンはその時点の値で合成して再生する(ui_page):
    app_record(ui_page)
    set_slider(ui_page, "formant", 1.3)
    ui_page.click("#play-mod")
    app_wait_playing(ui_page, "processed")
    assert last_params(ui_page, "synthesize")["formant"] == pytest.approx(1.3)


def test_TC_977_1_加工音のcurveは画面のゲインと一致する(ui_page):
    app_record(ui_page)
    drag_handle(ui_page, 11, gain=4.0)
    clear_calls(ui_page)
    ui_page.click("#play-mod")
    app_wait_playing(ui_page, "processed")
    assert last_params(ui_page, "synthesize")["curve"] == pytest.approx(curve_gains(ui_page))


def test_TC_1001_1_合成待ちはローディング表示(ui_page):
    app_record(ui_page)
    hold(ui_page, "synthesize")
    ui_page.click("#play-mod")
    wait_held(ui_page)
    expect(ui_page.locator("#play-mod")).to_have_attribute("aria-busy", "true")
    release(ui_page)
    expect(ui_page.locator("#play-mod")).not_to_have_attribute("aria-busy", "true")


def test_TC_1002_1_元音ボタンで元音を再生する(ui_page):
    info = app_record(ui_page)
    clear_calls(ui_page)
    ui_page.click("#play-orig")
    app_wait_playing(ui_page, "original")
    assert calls(ui_page, "original")[-1]["args"][0] == info["id"]


def test_TC_1003_1_未再生のスペースは元音(ui_page):
    app_record(ui_page)
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "original")


def test_TC_1003_2_続けてスペースを押すと加工音(ui_page):
    app_record(ui_page)
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "original")
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "processed")
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "original")


def test_TC_1004_1_スライダーにフォーカスがあってもスペースは再生だけ(ui_page):
    ui_page.set_viewport_size({"width": 800, "height": 300})
    app_record(ui_page)
    ui_page.focus("input[name=formant]")
    before = (ui_page.input_value("input[name=formant]"), ui_page.evaluate("scrollY"))
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "original")
    assert (ui_page.input_value("input[name=formant]"), ui_page.evaluate("scrollY")) == before

    # 加工音ボタンにフォーカスしていても、スペースは A/B 切り替えとしてだけ働く
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "processed")
    ui_page.focus("#play-mod")
    clear_calls(ui_page)
    ui_page.keyboard.press("Space")
    app_wait_playing(ui_page, "original")
    ui_page.wait_for_timeout(300)
    assert calls(ui_page, "synthesize") == []  # ボタンは押されていない


def test_TC_1005_1_新しい再生で前の音は止まる(ui_page):
    app_record(ui_page)
    ui_page.click("#play-orig")
    app_wait_playing(ui_page, "original")
    ui_page.wait_for_timeout(500)
    ui_page.click("#play-mod")
    app_wait_playing(ui_page, "processed")
    assert app_playing_count(ui_page) == 1


def test_TC_1006_1_WAVのBlobURLを作らない(ui_page):
    app_record(ui_page)
    ui_page.click("#play-orig")
    app_wait_playing(ui_page, "original")
    ui_page.click("#play-mod")
    app_wait_playing(ui_page, "processed")
    types = ui_page.evaluate("() => window.__objectUrls")
    assert [t for t in types if str(t).startswith("audio/")] == []
