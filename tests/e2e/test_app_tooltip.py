"""ブラウザ版のツールチップ・スライダーの色・表記（008-browser-app）。"""

import re

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    app_record,
    curve_gains,
    drag_handle,
    handle,
    rgb,
    set_slider,
    set_slider_frame,
)

SLIDER_NAMES = ["formant", "tilt", "band0", "band1", "band2", "band3", "smooth", "pitch", "mix"]
PRESETS = ("素通し", "子供っぽく", "太く", "こもる", "のっぺり")


def tip_of(page, selector):
    return page.get_attribute(selector, "data-tip")


def slider(name):
    return f"input[name={name}]"


def accent(page, selector):
    return rgb(page.eval_on_selector(selector, "el => getComputedStyle(el).accentColor"))


def is_gray(color):
    return color[0] == color[1] == color[2]


def gray_flags(page):
    return {name: is_gray(accent(page, slider(name))) for name in SLIDER_NAMES}


# ---------------------------------------------------------------- ツールチップ

def test_TC_1011_1_初期状態では出ていない(ui_page):
    expect(ui_page.locator("#tooltip")).to_be_hidden()


def test_TC_1012_1_ポインタを合わせると出る(ui_page):
    ui_page.hover(slider("formant"))
    expect(ui_page.locator("#tooltip")).to_be_visible()
    assert ui_page.inner_text("#tooltip") == tip_of(ui_page, slider("formant"))


def test_TC_1013_1_ポインタを外すと消える(ui_page):
    ui_page.hover(slider("formant"))
    expect(ui_page.locator("#tooltip")).to_be_visible()
    ui_page.hover("h1")
    expect(ui_page.locator("#tooltip")).to_be_hidden()


def test_TC_1014_1_フォーカスで出て外れると消える(ui_page):
    ui_page.focus("#rec")
    expect(ui_page.locator("#tooltip")).to_be_visible()
    assert ui_page.inner_text("#tooltip") == tip_of(ui_page, "#rec")
    ui_page.eval_on_selector("#rec", "el => el.blur()")
    expect(ui_page.locator("#tooltip")).to_be_hidden()


def test_TC_1015_1_Escapeで消える(ui_page):
    ui_page.hover(slider("formant"))
    expect(ui_page.locator("#tooltip")).to_be_visible()
    ui_page.keyboard.press("Escape")
    expect(ui_page.locator("#tooltip")).to_be_hidden()


def test_TC_1016_1_ツールチップの下の要素を操作できる(ui_page):
    handle(ui_page, 7).hover()
    expect(ui_page.locator("#tooltip")).to_be_visible()
    assert ui_page.eval_on_selector("#tooltip", "el => getComputedStyle(el).pointerEvents") == "none"
    drag_handle(ui_page, 7, gain=6.0)
    assert curve_gains(ui_page)[7] == pytest.approx(6.0, abs=0.1)


def test_TC_1017_1_スライダーの説明(ui_page):
    tips = {name: tip_of(ui_page, slider(name)) for name in SLIDER_NAMES}
    assert all(t and len(t) >= 5 for t in tips.values()), tips
    assert len(set(tips.values())) == len(SLIDER_NAMES)


def test_TC_1018_1_主要な操作の説明(ui_page):
    for sel in ["#rec", "#open-file", "#play-orig", "#play-mod", "#current", "#partner", "#frame", "#reset"]:
        assert tip_of(ui_page, sel), sel
    for name in PRESETS:
        assert tip_of(ui_page, f"button[data-preset='{name}']"), name
    tips = ui_page.eval_on_selector_all("circle.curve-point", "cs => cs.map(c => c.dataset.tip)")
    assert len(tips) == 20 and all(tips)


# ---------------------------------------------------------------- スライダーの色

def test_TC_1019_1_初期値はグレーで動かすと色が付く(ui_page):
    assert gray_flags(ui_page) == dict.fromkeys(SLIDER_NAMES, True)
    set_slider(ui_page, "formant", 1.3)
    set_slider(ui_page, "mix", 0.5)
    flags = gray_flags(ui_page)
    assert flags["formant"] is False and flags["mix"] is False
    assert all(v for k, v in flags.items() if k not in ("formant", "mix"))


def test_TC_1020_1_初期値に戻すとグレーに戻る(ui_page):
    set_slider(ui_page, "tilt", 5)
    assert gray_flags(ui_page)["tilt"] is False
    ui_page.dblclick(slider("tilt"))
    assert gray_flags(ui_page)["tilt"] is True

    for name, v in [("formant", 1.4), ("band2", 6), ("smooth", 20), ("pitch", 1.5), ("mix", 0.3)]:
        set_slider(ui_page, name, v)
    ui_page.click("#reset")
    assert gray_flags(ui_page) == dict.fromkeys(SLIDER_NAMES, True)

    set_slider(ui_page, "tilt", 7)
    ui_page.click("button[data-preset='子供っぽく']")
    flags = gray_flags(ui_page)
    assert flags["formant"] is False and flags["pitch"] is False
    assert all(v for k, v in flags.items() if k not in ("formant", "pitch"))


def test_TC_1021_1_フレームスライダーは常にグレー(ui_page):
    info = app_record(ui_page)
    assert is_gray(accent(ui_page, "#frame"))
    set_slider_frame(ui_page, info["voicedFrames"][0])
    assert is_gray(accent(ui_page, "#frame"))


# ---------------------------------------------------------------- 基本周波数の表記

def f0_hits(page):
    """画面に出うる文言（非表示の要素も含む。script / style は除く）と data-tip の中の "f0"。"""
    return page.evaluate(
        "() => { const hits = []; const bad = /f0/i;"
        " for (const el of document.body.querySelectorAll('*')) {"
        "   if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;"
        "   for (const n of el.childNodes)"
        "     if (n.nodeType === 3 && bad.test(n.textContent)) hits.push(`text:${el.id || el.tagName}`);"
        "   if (el.dataset.tip && bad.test(el.dataset.tip)) hits.push(`tip:${el.id || el.className}`);"
        " }"
        " return hits; }"
    )


def test_TC_1022_1_画面にf0の綴りが無い(ui_page, wav_files):
    assert f0_hits(ui_page) == []
    info = app_record(ui_page)
    ui_page.hover(slider("pitch"))
    expect(ui_page.locator("#tooltip")).to_be_visible()
    assert f0_hits(ui_page) == []

    unvoiced = next(i for i in range(info["frames"]) if i not in set(info["voicedFrames"]))
    set_slider_frame(ui_page, unvoiced)
    expect(ui_page.locator("#unvoiced")).to_be_visible()
    assert f0_hits(ui_page) == []

    drag_handle(ui_page, 7, gain=6.0, release=False)
    expect(ui_page.locator("#curve-readout")).to_be_visible()
    assert f0_hits(ui_page) == []
    ui_page.mouse.up()

    ui_page.set_input_files("#file", str(wav_files["short"]))
    expect(ui_page.locator("#error")).not_to_be_empty()
    assert f0_hits(ui_page) == []


def test_TC_1023_1_分解結果の表示(ui_page):
    info = app_record(ui_page)
    assert re.search(re.escape(f"平均 fo {info['f0Mean']:.1f} Hz"), ui_page.inner_text("#meta"))
