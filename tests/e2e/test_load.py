"""002-wav-load: ファイル読み込みの E2E テスト。"""

import numpy as np
from playwright.sync_api import expect

from tests import audio_fixtures as af
from tests.e2e.helpers import hold_requests, load_file, record, set_slider, wait_envelope_count, wait_held


def test_TC_300_1_ファイルを開くボタンと受け付け種別(page):
    expect(page.locator("#open-file")).to_be_visible()
    expect(page.locator("#open-file")).to_be_enabled()
    accept = page.get_attribute("#file", "accept").split(",")
    assert {"audio/*", ".wav"} <= {a.strip() for a in accept}


def test_TC_301_1_ファイル名付きで送信される(page, wav_files):
    # Chromium はファイルを含む multipart 本文を Playwright に渡さないので、
    # ファイル名は fetch に渡された FormData をページ内で記録して見る。内容は元音の一致で見る
    page.evaluate(
        "() => { window.__sent = []; const orig = window.fetch;"
        " window.fetch = (url, opts = {}) => {"
        "   if (opts.body instanceof FormData) {"
        "     for (const [k, v] of opts.body.entries()) window.__sent.push({key: k, name: v.name, size: v.size});"
        "   }"
        "   return orig(url, opts); }; }"
    )
    with page.expect_response("**/api/analyze") as resp:
        page.set_input_files("#file", str(wav_files["voice"]))
    sent = page.evaluate("window.__sent")
    assert sent == [{"key": "audio", "name": "voice.wav", "size": wav_files["voice"].stat().st_size}]
    info = resp.value.json()
    original = page.request.get(f"/api/original/{info['id']}").body()
    x, _, _ = af.read_wav(wav_files["voice"].read_bytes())
    y, _, _ = af.read_wav(original)
    np.testing.assert_array_equal(y, x)
    page.wait_for_timeout(300)
    assert len(page.reqs.of("/api/analyze")) == 1


def test_TC_302_1_分解完了後は録音と同じ状態になる(page, wav_files):
    info = load_file(page, wav_files["voice"])
    expect(page.locator("#frame")).to_be_enabled()
    expect(page.locator("#play-orig")).to_be_enabled()
    expect(page.locator("#play-mod")).to_be_enabled()
    page.reqs.clear()
    set_slider(page, "tilt", 3)
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["body"]["id"] == info["id"]


def test_TC_302_2_録音の後にファイルを読むとファイル側を使う(page, wav_files):
    record(page)
    info = load_file(page, wav_files["voice"])
    page.reqs.clear()
    set_slider(page, "tilt", 3)
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["body"]["id"] == info["id"]
    page.click("#play-orig")
    page.wait_for_function("() => document.querySelector('#player').dataset.source === 'original'")
    assert page.get_attribute("#player", "src").endswith(f"/api/original/{info['id']}")


def test_TC_303_1_送信中はボタンが無効(page, wav_files):
    held = hold_requests(page, "**/api/analyze")
    page.set_input_files("#file", str(wav_files["voice"]))
    wait_held(page, held)
    page.wait_for_timeout(300)
    expect(page.locator("#open-file")).to_be_disabled()
    expect(page.locator("#rec")).to_be_disabled()
    with page.expect_response("**/api/analyze"):
        held[0].continue_()
    expect(page.locator("#open-file")).to_be_enabled()
    expect(page.locator("#rec")).to_be_enabled()


def test_TC_304_1_録音中はファイルを開けない(page):
    page.click("#rec")
    expect(page.locator("#rec")).to_have_attribute("data-state", "recording")
    expect(page.locator("#open-file")).to_be_disabled()
    page.wait_for_timeout(1500)
    with page.expect_response("**/api/analyze"):
        page.click("#rec")
    expect(page.locator("#open-file")).to_be_enabled()


def test_TC_305_1_エラー時は前の録音を使い続ける(page, wav_files):
    rec = record(page)
    with page.expect_response("**/api/analyze") as resp:
        page.set_input_files("#file", str(wav_files["short"]))
    assert resp.value.status == 400
    expect(page.locator("#error")).not_to_be_empty()
    page.reqs.clear()
    set_slider(page, "tilt", 3)
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["body"]["id"] == rec["id"]


def test_TC_305_2_分解前のエラーでは再生ボタンは無効のまま(page, wav_files):
    with page.expect_response("**/api/analyze") as resp:
        page.set_input_files("#file", str(wav_files["broken"]))
    assert resp.value.status == 400
    expect(page.locator("#error")).not_to_be_empty()
    expect(page.locator("#play-orig")).to_be_disabled()
    expect(page.locator("#play-mod")).to_be_disabled()


def test_TC_306_1_同じファイルを2回選べる(page, wav_files):
    first = load_file(page, wav_files["one_sec"])
    # 実ブラウザでは value が残っていると同じファイルの再選択で change が発火しない。
    # 読み込み後に value が空へ戻されていることもあわせて見る
    assert page.eval_on_selector("#file", "el => el.value") == ""
    second = load_file(page, wav_files["one_sec"])
    assert first["id"] != second["id"]
    assert len(page.reqs.of("/api/analyze")) == 2
