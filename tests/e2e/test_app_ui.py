"""ブラウザ版の画面（008-browser-app）。観測点は window.__calls（アダプタの呼び出し）。"""

import math
import time

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import (
    app_info,
    app_load_file,
    app_record,
    calls,
    clear_calls,
    hold,
    release,
    rgb,
    set_slider,
    set_slider_frame,
    wait_calls,
    wait_held,
)


# ---------------------------------------------------------------- 録音

def test_TC_930_1_録音中は経過秒が増える(ui_page):
    ui_page.click("#rec")
    expect(ui_page.locator("#rec")).to_have_attribute("data-state", "recording")
    ui_page.wait_for_timeout(1000)
    assert float(ui_page.inner_text("#elapsed").split()[0]) >= 0.5
    ui_page.click("#rec")


def test_TC_931_1_停止で分解が始まる(ui_page):
    app_record(ui_page, 1.5)
    assert len(calls(ui_page, "analyze")) == 1


def test_TC_932_1_分解中は録音ボタンが無効(ui_page):
    hold(ui_page, "analyze")
    ui_page.click("#rec")
    ui_page.wait_for_timeout(1500)
    ui_page.click("#rec")
    wait_held(ui_page)
    expect(ui_page.locator("#rec")).to_be_disabled()
    release(ui_page)
    expect(ui_page.locator("#rec")).to_be_enabled()


def test_TC_933_1_10秒で自動停止する(ui_page):
    ui_page.click("#rec")
    start = time.monotonic()
    assert wait_calls(ui_page, "analyze", 1, timeout=12.0) == 1
    elapsed = time.monotonic() - start
    assert 10.0 <= elapsed <= 11.5
    expect(ui_page.locator("#rec")).not_to_have_attribute("data-state", "recording")


def test_TC_934_1_再録音でidが差し替わる(ui_page):
    first = app_record(ui_page)
    second = app_record(ui_page)
    assert first["id"] != second["id"]
    clear_calls(ui_page)
    set_slider(ui_page, "tilt", 2)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert calls(ui_page, "envelope")[-1]["args"][0] == second["id"]


def test_TC_935_1_分解前は再生ボタンが無効(ui_page):
    expect(ui_page.locator("#play-orig")).to_be_disabled()
    expect(ui_page.locator("#play-mod")).to_be_disabled()


def test_TC_936_1_分解中は進行中の表示が出る(ui_page):
    hold(ui_page, "analyze")
    ui_page.click("#rec")
    ui_page.wait_for_timeout(1500)
    ui_page.click("#rec")
    wait_held(ui_page)
    expect(ui_page.locator("#meta")).to_have_text("分解中…")
    release(ui_page)
    expect(ui_page.locator("#meta")).not_to_have_text("分解中…")


def test_TC_937_1_マイクが取れないときエラーが出る(ui_page):
    ui_page.evaluate(
        "() => { navigator.mediaDevices.getUserMedia = () => Promise.reject(new Error('だめでした')); }")
    ui_page.click("#rec")
    expect(ui_page.locator("#error")).to_contain_text("マイク")
    expect(ui_page.locator("#rec")).not_to_have_attribute("data-state", "recording")


# ---------------------------------------------------------------- ファイルの読み込み

def test_TC_940_1_ファイルを開くボタンと受け付け種別(ui_page):
    expect(ui_page.locator("#open-file")).to_be_visible()
    assert ui_page.get_attribute("#file", "accept") == "audio/*,.wav"


def test_TC_941_1_ファイルを選ぶとファイル名で分解される(ui_page, wav_files):
    app_load_file(ui_page, wav_files["voice"])
    analyzed = calls(ui_page, "analyze")
    assert len(analyzed) == 1
    assert analyzed[0]["args"][1] == "voice.wav"


def test_TC_942_1_ファイルの分解完了後の状態(ui_page, wav_files):
    info = app_load_file(ui_page, wav_files["voice"])
    for sel in ("#frame", "#play-orig", "#play-mod"):
        expect(ui_page.locator(sel)).to_be_enabled()
    clear_calls(ui_page)
    set_slider(ui_page, "tilt", 3)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert calls(ui_page, "envelope")[-1]["args"][0] == info["id"]


def test_TC_943_1_ファイルの分解中はボタンが無効(ui_page, wav_files):
    hold(ui_page, "analyze")
    ui_page.set_input_files("#file", str(wav_files["voice"]))
    wait_held(ui_page)
    expect(ui_page.locator("#open-file")).to_be_disabled()
    expect(ui_page.locator("#rec")).to_be_disabled()
    release(ui_page)
    expect(ui_page.locator("#open-file")).to_be_enabled()


def test_TC_944_1_録音中はファイルを開けない(ui_page):
    ui_page.click("#rec")
    expect(ui_page.locator("#rec")).to_have_attribute("data-state", "recording")
    expect(ui_page.locator("#open-file")).to_be_disabled()
    ui_page.click("#rec")


def test_TC_945_1_短すぎるファイルはエラーになる(ui_page, wav_files):
    ui_page.set_input_files("#file", str(wav_files["short"]))
    expect(ui_page.locator("#error")).not_to_be_empty()


def test_TC_945_2_分解に失敗しても前のidを使い続ける(ui_page, wav_files):
    info = app_load_file(ui_page, wav_files["voice"])
    ui_page.set_input_files("#file", str(wav_files["short"]))
    expect(ui_page.locator("#error")).not_to_be_empty()
    clear_calls(ui_page)
    set_slider(ui_page, "tilt", 4)
    assert wait_calls(ui_page, "envelope", 1) >= 1
    assert calls(ui_page, "envelope")[-1]["args"][0] == info["id"]


def test_TC_946_1_同じファイルを2回選んでも2回分解される(ui_page, wav_files):
    app_load_file(ui_page, wav_files["voice"])
    app_load_file(ui_page, wav_files["voice"])
    assert len(calls(ui_page, "analyze")) == 2


def test_TC_1010_1_拒否されたときエラー表示が出る(ui_page, wav_files):
    ui_page.set_input_files("#file", str(wav_files["short"]))
    expect(ui_page.locator("#error")).to_contain_text("秒")


# ---------------------------------------------------------------- 包絡グラフ

def test_TC_950_1_元包絡と加工後包絡の2本(ui_page):
    app_record(ui_page)
    orig, mod = ui_page.evaluate(
        "() => ['#orig-line', '#mod-line'].map(s => { const c = getComputedStyle(document.querySelector(s));"
        " return { stroke: c.stroke, width: parseFloat(c.strokeWidth) }; })"
    )
    r, g, b = rgb(orig["stroke"])
    assert r == g == b
    assert len(set(rgb(mod["stroke"]))) > 1
    assert mod["width"] > orig["width"]
    assert ui_page.get_attribute("#orig-line", "d") and ui_page.get_attribute("#mod-line", "d")


def test_TC_951_1_横軸は対数スケール(ui_page):
    app_record(ui_page)
    left = float(ui_page.get_attribute("#graph", "data-plot-left"))
    right = float(ui_page.get_attribute("#graph", "data-plot-right"))
    for f in (500, 5000):
        x = float(ui_page.get_attribute(f"#graph line[data-freq='{f}']", "x1"))
        assert (x - left) / (right - left) == pytest.approx(math.log(f / 50) / math.log(441), abs=0.01)


def test_TC_952_1_縦軸の範囲(ui_page):
    info = app_record(ui_page)
    frame = int(ui_page.input_value("#frame"))
    top = ui_page.evaluate("""async ([id, frame]) => {
        const env = await window.engine.envelope(id, frame, {});
        let m = -Infinity;
        for (let k = 0; k < env.freq.length; k++) if (env.freq[k] >= 50) m = Math.max(m, env.originalDb[k]);
        return m + 5;
    }""", [info["id"], frame])
    assert float(ui_page.get_attribute("#graph", "data-ymax")) == pytest.approx(top, abs=0.5)
    assert float(ui_page.get_attribute("#graph", "data-ymin")) == pytest.approx(top - 70, abs=0.5)


def test_TC_953_1_境界の縦線がある(ui_page):
    app_record(ui_page)
    for f in (500, 1500, 4000):
        expect(ui_page.locator(f"#graph line.band-line[data-freq='{f}']")).to_have_count(1)


def test_TC_954_1_相手の包絡は破線で色が違う(ui_page, wav_files):
    app_load_file(ui_page, wav_files["voice"])
    partner = app_record(ui_page)["id"]
    ui_page.select_option("#partner", partner)
    ui_page.wait_for_function("() => document.querySelector('#partner-line').getAttribute('d')")
    style = ui_page.evaluate(
        "() => ['#orig-line', '#mod-line', '#partner-line'].map(s => {"
        " const c = getComputedStyle(document.querySelector(s));"
        " return { stroke: c.stroke, dash: c.strokeDasharray, display: c.display }; })"
    )
    o, m, p = style
    assert p["display"] != "none"
    assert p["dash"] not in ("none", "")
    assert p["stroke"] != o["stroke"] and p["stroke"] != m["stroke"]


def test_TC_954_2_相手をなしに戻すと破線が消える(ui_page, wav_files):
    app_load_file(ui_page, wav_files["voice"])
    partner = app_record(ui_page)["id"]
    ui_page.select_option("#partner", partner)
    ui_page.wait_for_function("() => document.querySelector('#partner-line').getAttribute('d')")
    ui_page.select_option("#partner", "")
    ui_page.wait_for_function("() => !document.querySelector('#partner-line').getAttribute('d')")
    assert ui_page.evaluate("() => getComputedStyle(document.querySelector('#partner-line')).display") == "none"


# ---------------------------------------------------------------- フレーム選択

def test_TC_955_1_フレームスライダーの範囲(ui_page, wav_files):
    app_load_file(ui_page, wav_files["voice"])  # 3.0 秒
    assert ui_page.get_attribute("#frame", "min") == "0"
    assert ui_page.get_attribute("#frame", "max") == "600"


def test_TC_956_1_初期のフレームは有声の真ん中(ui_page):
    info = app_record(ui_page)
    voiced = info["voicedFrames"]
    assert int(ui_page.input_value("#frame")) == voiced[len(voiced) // 2]


def test_TC_957_1_無声フレームの表示(ui_page):
    info = app_record(ui_page)
    unvoiced = next(i for i in range(info["frames"]) if i not in set(info["voicedFrames"]))
    set_slider_frame(ui_page, unvoiced)
    expect(ui_page.locator("#unvoiced")).to_be_visible()


def test_TC_957_2_有声に戻すと表示が消える(ui_page):
    info = app_record(ui_page)
    unvoiced = next(i for i in range(info["frames"]) if i not in set(info["voicedFrames"]))
    set_slider_frame(ui_page, unvoiced)
    expect(ui_page.locator("#unvoiced")).to_be_visible()
    set_slider_frame(ui_page, info["voicedFrames"][0])
    expect(ui_page.locator("#unvoiced")).to_be_hidden()


def test_TC_958_1_フレーム変更で包絡が引き直される(ui_page):
    info = app_record(ui_page)
    clear_calls(ui_page)
    target = info["voicedFrames"][-1]
    set_slider_frame(ui_page, target)
    assert wait_calls(ui_page, "envelope", 1) == 1
    assert calls(ui_page, "envelope")[-1]["args"][1] == target


def test_TC_929_2_ファイル読み込みのsourceはファイル名(ui_page, wav_files):
    info = app_load_file(ui_page, wav_files["voice"])
    assert info["source"] == "voice.wav"
