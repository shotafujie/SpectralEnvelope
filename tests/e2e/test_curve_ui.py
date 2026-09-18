"""004-gain-curve: 制御点のドラッグ操作の E2E テスト。"""

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    CURVE_FREQS,
    curve_gains,
    drag_handle,
    handle,
    log_x_ratio,
    plot_box,
    record,
    svg_to_client,
    wait_envelope_count,
)


def center(page):
    b = plot_box(page)
    return (b["top"] + b["bottom"]) / 2


def test_TC_510_1_ハンドルのx位置は対数軸(page):
    b = plot_box(page)
    assert page.locator("circle.curve-point").count() == 20
    for j, f in enumerate(CURVE_FREQS):
        cx = float(handle(page, j).get_attribute("cx"))
        assert cx == pytest.approx(b["left"] + (b["right"] - b["left"]) * log_x_ratio(f), abs=0.01)


def test_TC_511_1_初期状態は中央(page):
    c = center(page)
    for j in range(20):
        assert float(handle(page, j).get_attribute("cy")) == pytest.approx(c, abs=0.01)


def test_TC_511_2_ゲインに応じたy位置(page):
    drag_handle(page, 7, gain=5.0)
    g = float(handle(page, 7).get_attribute("data-gain"))
    b = plot_box(page)
    expected = center(page) - g * (b["bottom"] - b["top"]) / 70
    assert float(handle(page, 7).get_attribute("cy")) == pytest.approx(expected, abs=0.01)


def test_TC_512_1_ドラッグでゲインが変わる(page):
    drag_handle(page, 7, gain=6.0)
    gains = curve_gains(page)
    assert gains[7] == pytest.approx(6.0, abs=0.1)
    assert all(g == 0 for i, g in enumerate(gains) if i != 7)


def test_TC_512_2_上下端でクランプ(page):
    b = plot_box(page)
    drag_handle(page, 3, svg_y=b["top"] - 40)
    drag_handle(page, 15, svg_y=b["bottom"] + 40)
    gains = curve_gains(page)
    assert gains[3] == 12.0
    assert gains[15] == -12.0


def test_TC_512_3_ゲインは0_1dB単位(page):
    drag_handle(page, 9, gain=3.37)
    g = curve_gains(page)[9]
    assert g != 0
    assert abs(g * 10 - round(g * 10)) < 1e-9


def test_TC_513_1_横に動かしても周波数は変わらない(page):
    cx = handle(page, 10).get_attribute("cx")
    drag_handle(page, 10, gain=4.0, dx=120)
    gains = curve_gains(page)
    assert handle(page, 10).get_attribute("cx") == cx
    assert gains[10] > 0
    assert all(g == 0 for g in gains[11:])


def test_TC_514_1_ゲイン線がハンドルに追従する(page):
    drag_handle(page, 6, gain=-5.0, release=False)
    h = handle(page, 6)
    d = page.get_attribute("#curve-line", "d")
    assert f"{h.get_attribute('cx')},{h.get_attribute('cy')}" in d
    page.mouse.up()
    d = page.get_attribute("#curve-line", "d")
    assert f"{h.get_attribute('cx')},{h.get_attribute('cy')}" in d


def test_TC_515_1_ドラッグ中は周波数とゲインを表示する(page):
    drag_handle(page, 7, gain=6.0, release=False)
    g = curve_gains(page)[7]
    readout = page.locator("#curve-readout")
    expect(readout).to_be_visible()
    text = readout.inner_text()
    assert f"{round(CURVE_FREQS[7])} Hz" in text
    assert f"{g:+.1f}" in text
    page.mouse.up()


def test_TC_516_1_離してから300ms後に1回送る(page):
    record(page)
    page.wait_for_timeout(600)
    page.reqs.clear()
    last = drag_handle(page, 8, gain=7.0, steps=5)
    page.wait_for_timeout(150)
    assert page.reqs.of("/api/envelope") == []
    assert wait_envelope_count(page, 1) == 1
    sent = page.reqs.of("/api/envelope")[0]
    assert sent["t"] - last >= 0.29
    assert sent["body"]["params"]["curve"] == pytest.approx(curve_gains(page))
    page.wait_for_timeout(400)
    assert len(page.reqs.of("/api/envelope")) == 1


def test_TC_516_2_2点を動かした後の送信内容(page):
    record(page)
    drag_handle(page, 4, gain=5.0)
    drag_handle(page, 12, gain=-3.0)
    page.wait_for_timeout(700)
    curve = page.reqs.of("/api/envelope")[-1]["body"]["params"]["curve"]
    gains = curve_gains(page)
    assert curve == pytest.approx(gains)
    assert [i for i, g in enumerate(curve) if g != 0] == [4, 12]


def test_TC_517_1_合成要求のcurve(page):
    record(page)
    drag_handle(page, 5, gain=-6.0)
    with page.expect_response("**/api/synthesize"):
        page.click("#play-mod")
    assert page.reqs.of("/api/synthesize")[-1]["body"]["params"]["curve"] == pytest.approx(curve_gains(page))


def test_TC_518_1_ダブルクリックで0(page):
    drag_handle(page, 7, gain=6.0)
    h = handle(page, 7)
    x, y = svg_to_client(page, float(h.get_attribute("cx")), float(h.get_attribute("cy")))
    page.mouse.dblclick(x, y)
    assert curve_gains(page)[7] == 0
    assert float(h.get_attribute("cy")) == pytest.approx(center(page), abs=0.01)


PRESETS = ("素通し", "子供っぽく", "太く", "こもる", "のっぺり")


def test_TC_519_1_TC_519_2_リセットとプリセットで全点0(page):
    for action in ["#reset", *(f"button[data-preset='{n}']" for n in PRESETS)]:
        for j, g in [(2, 4.0), (9, -6.0), (17, 8.0)]:
            drag_handle(page, j, gain=g)
        assert sum(1 for g in curve_gains(page) if g != 0) == 3
        page.click(action)
        assert curve_gains(page) == [0] * 20, action


def test_TC_520_1_分解前でも操作できる(page):
    assert page.locator("circle.curve-point").count() == 20
    drag_handle(page, 7, gain=6.0)
    page.wait_for_timeout(600)
    assert curve_gains(page)[7] != 0
    assert page.reqs.of("/api/envelope") == []
