"""ブラウザ版の録音の選択欄・mix・相手の包絡（008-browser-app）。"""

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    app_load_file,
    app_record,
    calls,
    clear_calls,
    set_slider,
    wait_calls,
)


def options(page, sel):
    return page.eval_on_selector_all(f"{sel} option", "os => os.map(o => ({value: o.value, label: o.textContent}))")


def last_params(page):
    return calls(page, "envelope")[-1]["args"][-1]


@pytest.fixture
def two(ui_page, wav_files):
    """録音 1 件 + voice.wav 1 件を分解した状態にする。"""
    a = app_record(ui_page)
    b = app_load_file(ui_page, wav_files["voice"])
    ui_page.wait_for_timeout(400)
    return a, b


def test_TC_985_1_選択欄のラベル(ui_page, two):
    a, b = two
    cur = options(ui_page, "#current")
    par = options(ui_page, "#partner")
    assert [o["value"] for o in cur] == [a["id"], b["id"]]
    assert [o["value"] for o in par] == ["", a["id"], b["id"]]
    for text in ("#1", "録音", f"{a['duration']:.2f} 秒"):
        assert text in cur[0]["label"]
    for text in ("#2", "voice.wav", "3.00 秒"):
        assert text in cur[1]["label"]
    assert par[1]["label"] == cur[0]["label"]


def test_TC_986_1_新しい分解に切り替わる(ui_page, two):
    _, b = two
    assert ui_page.input_value("#current") == b["id"]
    assert options(ui_page, "#current")[-1]["value"] == b["id"]


def test_TC_987_1_現在の録音を切り替える(ui_page, two):
    a, _ = two
    ui_page.select_option("#current", a["id"])
    ui_page.wait_for_function("id => document.querySelector('#graph').dataset.id === id", arg=a["id"])
    voiced = a["voicedFrames"]
    assert ui_page.get_attribute("#frame", "max") == str(a["frames"] - 1)
    assert ui_page.input_value("#frame") == str(voiced[len(voiced) // 2])
    clear_calls(ui_page)
    set_slider(ui_page, "tilt", 2)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert calls(ui_page, "envelope")[-1]["args"][0] == a["id"]


def test_TC_988_1_相手の初期値はなし(ui_page):
    app_record(ui_page)
    assert ui_page.input_value("#partner") == ""
    clear_calls(ui_page)
    set_slider(ui_page, "tilt", 2)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert "morph" not in last_params(ui_page)


def test_TC_989_1_mixスライダー(ui_page):
    attrs = ui_page.eval_on_selector("#p-mix", "el => [el.min, el.max, el.step, el.value].map(Number)")
    assert attrs == pytest.approx([0, 1, 0.01, 0])
    set_slider(ui_page, "mix", 0.4)
    expect(ui_page.locator("#mix-value")).to_have_text("0.40")


def test_TC_990_1_paramsのmorph(ui_page, two):
    a, _ = two
    ui_page.select_option("#partner", a["id"])
    clear_calls(ui_page)
    set_slider(ui_page, "mix", 0.4)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert last_params(ui_page)["morph"] == {"id": a["id"], "ratio": pytest.approx(0.4)}


def test_TC_991_1_mixの変更でenvelopeが1回(ui_page, two):
    a, _ = two
    ui_page.select_option("#partner", a["id"])
    ui_page.wait_for_timeout(600)
    clear_calls(ui_page)
    set_slider(ui_page, "mix", 0.6)
    assert wait_calls(ui_page, "envelope", 1) == 1
    ui_page.wait_for_timeout(500)
    assert len(calls(ui_page, "envelope")) == 1


def test_TC_992_1_リセットはmixだけ戻す(ui_page, two):
    a, _ = two
    ui_page.select_option("#partner", a["id"])
    set_slider(ui_page, "mix", 0.7)
    ui_page.click("#reset")
    assert float(ui_page.input_value("#p-mix")) == 0.0
    assert ui_page.input_value("#partner") == a["id"]


def test_TC_992_2_プリセットもmixだけ戻す(ui_page, two):
    a, _ = two
    ui_page.select_option("#partner", a["id"])
    set_slider(ui_page, "mix", 0.7)
    ui_page.click("button[data-preset='こもる']")
    assert float(ui_page.input_value("#p-mix")) == 0.0
    assert ui_page.input_value("#partner") == a["id"]


def test_TC_993_1_mixのダブルクリックで0に戻る(ui_page):
    set_slider(ui_page, "mix", 0.5)
    ui_page.dblclick("#p-mix")
    assert float(ui_page.input_value("#p-mix")) == 0.0
    expect(ui_page.locator("#mix-value")).to_have_text("0.00")


def test_TC_994_1_選択欄は最新10件(ui_page, wav_files):
    ids = [app_load_file(ui_page, wav_files["one_sec"])["id"] for _ in range(11)]
    values = [o["value"] for o in options(ui_page, "#current")]
    assert len(values) == 10
    assert values == ids[1:]


def test_TC_994_2_消えた相手はなしに戻る(ui_page, wav_files):
    first = app_load_file(ui_page, wav_files["one_sec"])["id"]
    ui_page.select_option("#partner", first)
    for _ in range(10):
        app_load_file(ui_page, wav_files["one_sec"])
    assert ui_page.input_value("#partner") == ""
