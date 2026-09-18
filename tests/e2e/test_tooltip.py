"""005-ui-affordance: ツールチップとスライダーの変更表示の E2E テスト。"""

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import curve_gains, drag_handle, handle, record, rgb, set_slider, set_slider_frame

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


def test_TC_600_1_初期状態では出ていない(page):
    expect(page.locator("#tooltip")).to_be_hidden()


def test_TC_601_1_ポインタを合わせると出る(page):
    page.hover(slider("formant"))
    expect(page.locator("#tooltip")).to_be_visible()
    assert page.inner_text("#tooltip") == tip_of(page, slider("formant"))


def test_TC_601_2_別の要素に移ると文言が変わる(page):
    page.hover(slider("formant"))
    expect(page.locator("#tooltip")).to_have_text(tip_of(page, slider("formant")))
    page.hover(slider("pitch"))
    expect(page.locator("#tooltip")).to_have_text(tip_of(page, slider("pitch")))


def test_TC_602_1_ポインタを外すと消える(page):
    page.hover(slider("formant"))
    expect(page.locator("#tooltip")).to_be_visible()
    page.hover("h1")
    expect(page.locator("#tooltip")).to_be_hidden()


def test_TC_603_1_フォーカスでも出る(page):
    page.focus("#rec")
    expect(page.locator("#tooltip")).to_be_visible()
    assert page.inner_text("#tooltip") == tip_of(page, "#rec")


def test_TC_603_2_フォーカスが外れると消える(page):
    page.focus("#rec")
    expect(page.locator("#tooltip")).to_be_visible()
    page.focus(slider("formant"))
    expect(page.locator("#tooltip")).to_have_text(tip_of(page, slider("formant")))
    page.eval_on_selector(slider("formant"), "el => el.blur()")
    expect(page.locator("#tooltip")).to_be_hidden()


def test_TC_604_1_Escapeで消える(page):
    page.hover(slider("formant"))
    expect(page.locator("#tooltip")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#tooltip")).to_be_hidden()


def test_TC_605_1_ポインタを受け取らない(page):
    page.hover(slider("formant"))
    expect(page.locator("#tooltip")).to_be_visible()
    assert page.eval_on_selector("#tooltip", "el => getComputedStyle(el).pointerEvents") == "none"


def test_TC_605_2_ツールチップが出ていてもドラッグできる(page):
    handle(page, 7).hover()
    expect(page.locator("#tooltip")).to_be_visible()
    drag_handle(page, 7, gain=6.0)
    assert curve_gains(page)[7] == pytest.approx(6.0, abs=0.1)


def visible_with_text(page, text):
    loc = page.get_by_text(text, exact=False)
    return [loc.nth(i) for i in range(loc.count()) if loc.nth(i).is_visible()]


def test_TC_606_1_旧ヒントは常時表示されない(page):
    for text in ("交互に再生", "ダブルクリックで初期値", "比率で混ぜる"):
        assert visible_with_text(page, text) == [], text


def test_TC_606_2_旧ヒントはツールチップになっている(page):
    assert "交互に再生" in tip_of(page, "#play-mod")
    assert "ダブルクリックで初期値" in tip_of(page, slider("formant"))
    assert "比率で混ぜる" in tip_of(page, slider("mix"))


def test_TC_607_1_パラメータの説明(page):
    tips = {name: tip_of(page, slider(name)) for name in SLIDER_NAMES}
    assert all(t and len(t) >= 5 for t in tips.values()), tips
    assert len(set(tips.values())) == len(SLIDER_NAMES)


def test_TC_608_1_主要な操作の説明(page):
    for sel in ["#rec", "#open-file", "#play-orig", "#play-mod", "#current", "#partner", "#frame", "#reset"]:
        assert tip_of(page, sel), sel


def test_TC_608_2_プリセットと制御点の説明(page):
    for name in PRESETS:
        assert tip_of(page, f"button[data-preset='{name}']"), name
    tips = page.eval_on_selector_all("circle.curve-point", "cs => cs.map(c => c.dataset.tip)")
    assert len(tips) == 20
    assert all(tips)


# ---------------------------------------------------------------- スライダーの色


def test_TC_610_1_初期値はグレー(page):
    assert gray_flags(page) == dict.fromkeys(SLIDER_NAMES, True)


def test_TC_611_1_変更したものだけ色が付く(page):
    set_slider(page, "formant", 1.3)
    flags = gray_flags(page)
    assert flags["formant"] is False
    assert all(v for k, v in flags.items() if k != "formant")


def test_TC_611_2_mixも色が付く(page):
    set_slider(page, "mix", 0.5)
    assert gray_flags(page)["mix"] is False


def test_TC_612_1_ダブルクリックでグレーに戻る(page):
    set_slider(page, "tilt", 5)
    assert gray_flags(page)["tilt"] is False
    page.dblclick(slider("tilt"))
    assert gray_flags(page)["tilt"] is True


def test_TC_612_2_リセットで全てグレーに戻る(page):
    for name, v in [("formant", 1.4), ("tilt", -5), ("band2", 6), ("smooth", 20), ("pitch", 1.5), ("mix", 0.3)]:
        set_slider(page, name, v)
    page.click("#reset")
    assert gray_flags(page) == dict.fromkeys(SLIDER_NAMES, True)


def test_TC_612_3_プリセットは設定したものだけ色が付く(page):
    set_slider(page, "tilt", 7)
    page.click("button[data-preset='子供っぽく']")
    flags = gray_flags(page)
    assert flags["formant"] is False and flags["pitch"] is False
    assert all(v for k, v in flags.items() if k not in ("formant", "pitch"))


def test_TC_613_1_フレームスライダーは常にグレー(page):
    info = record(page)
    assert is_gray(accent(page, "#frame"))
    set_slider_frame(page, info["voiced_frames"][0])
    assert is_gray(accent(page, "#frame"))


# ---------------------------------------------------------------- 基本周波数の表記


def visible_f0(page):
    """画面に見える文言と data-tip の中の "f0" を集める。"""
    return page.evaluate(
        "() => { const hits = [];"
        " const text = document.body.innerText || '';"
        " if (text.includes('f0')) hits.push('text');"
        " for (const el of document.querySelectorAll('[data-tip]'))"
        "   if (el.dataset.tip.includes('f0')) hits.push(`tip:${el.id || el.className}`);"
        " return hits; }"
    )


def test_TC_614_2_分解前の画面にf0が無い(page):
    assert visible_f0(page) == []


def test_TC_614_1_分解後の画面にf0が無い(page):
    record(page)
    page.hover(slider("pitch"))
    expect(page.locator("#tooltip")).to_be_visible()
    assert visible_f0(page) == []


def test_TC_615_1_分解結果の表示(page):
    info = record(page)
    meta = page.inner_text("#meta")
    assert "平均 fo" in meta
    assert f"{info['f0_mean']:.1f}" in meta
    assert "Hz" in meta
