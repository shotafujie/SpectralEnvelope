"""003-morph: 録音の選択欄・mix・相手の包絡線の E2E テスト。"""

import time

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import load_file, record, rgb, set_slider, set_slider_frame, wait_envelope_count


def options(page, sel):
    return page.eval_on_selector_all(f"{sel} option", "os => os.map(o => ({value: o.value, label: o.textContent}))")


@pytest.fixture
def two(page, wav_files):
    """録音 1 件 + voice.wav 1 件を分解した状態にする。"""
    a = record(page)
    b = load_file(page, wav_files["voice"])
    page.wait_for_timeout(400)
    return a, b


def select_partner(page, id_):
    page.select_option("#partner", id_)


def test_TC_420_1_選択欄のラベル(page, two):
    a, b = two
    cur = options(page, "#current")
    par = options(page, "#partner")
    assert [o["value"] for o in cur] == [a["id"], b["id"]]
    assert [o["value"] for o in par] == ["", a["id"], b["id"]]
    for text in ("#1", "録音", "秒"):
        assert text in cur[0]["label"]
    for text in ("#2", "voice.wav", "秒"):
        assert text in cur[1]["label"]
    assert par[1]["label"] == cur[0]["label"]


def test_TC_420_2_分解前の選択欄(page):
    assert options(page, "#current") == []
    assert [o["value"] for o in options(page, "#partner")] == [""]


def test_TC_421_1_新しい録音に切り替わる(page, two):
    _, b = two
    assert page.input_value("#current") == b["id"]
    assert options(page, "#current")[-1]["value"] == b["id"]
    assert options(page, "#partner")[-1]["value"] == b["id"]


def test_TC_422_1_現在の録音を切り替えるとグラフとフレームが切り替わる(page, two):
    a, _ = two
    page.select_option("#current", a["id"])
    page.wait_for_function("id => document.querySelector('#graph').dataset.id === id", arg=a["id"])
    v = a["voiced_frames"]
    assert page.get_attribute("#frame", "max") == str(a["frames"] - 1)
    assert page.input_value("#frame") == str(v[len(v) // 2])


def test_TC_422_2_切り替え後のAPIと元音は選んだ録音(page, two):
    a, _ = two
    page.select_option("#current", a["id"])
    page.wait_for_function("id => document.querySelector('#graph').dataset.id === id", arg=a["id"])
    page.reqs.clear()
    set_slider(page, "tilt", 2)
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["body"]["id"] == a["id"]
    page.click("#play-orig")
    page.wait_for_function("() => document.querySelector('#player').dataset.source === 'original'")
    assert page.get_attribute("#player", "src").endswith(f"/api/original/{a['id']}")


def test_TC_423_1_相手なしではmorphを送らない(page, two):
    page.reqs.clear()
    set_slider(page, "tilt", 2)
    assert wait_envelope_count(page, 1) == 1
    assert "morph" not in page.reqs.of("/api/envelope")[0]["body"]["params"]
    with page.expect_response("**/api/synthesize"):
        page.click("#play-mod")
    assert "morph" not in page.reqs.of("/api/synthesize")[-1]["body"]["params"]


def test_TC_424_1_mixスライダー(page):
    attrs = page.eval_on_selector("input[name=mix]", "el => [el.min, el.max, el.step, el.value].map(Number)")
    assert attrs == [0, 1, 0.01, 0]
    set_slider(page, "mix", 0.35)
    expect(page.locator("#mix-value")).to_have_text("0.35")


def test_TC_425_1_morphパラメータの送信(page, two):
    a, _ = two
    select_partner(page, a["id"])
    set_slider(page, "mix", 0.4)
    page.wait_for_timeout(600)
    env = page.reqs.of("/api/envelope")[-1]["body"]["params"]
    assert env["morph"] == {"id": a["id"], "ratio": 0.4}
    with page.expect_response("**/api/synthesize"):
        page.click("#play-mod")
    assert page.reqs.of("/api/synthesize")[-1]["body"]["params"]["morph"] == {"id": a["id"], "ratio": 0.4}


def test_TC_426_1_相手の選択でデバウンス後に1回(page, two):
    a, _ = two
    page.reqs.clear()
    changed = time.monotonic()
    select_partner(page, a["id"])
    assert wait_envelope_count(page, 1) == 1
    assert page.reqs.of("/api/envelope")[0]["t"] - changed >= 0.29
    page.wait_for_timeout(400)
    assert len(page.reqs.of("/api/envelope")) == 1


def test_TC_426_2_mixの連続変更は最後だけ送る(page, two):
    a, _ = two
    select_partner(page, a["id"])
    page.wait_for_timeout(600)
    page.reqs.clear()
    for v in (0.2, 0.4, 0.6, 0.8):
        set_slider(page, "mix", v)
        page.wait_for_timeout(100)
    last = time.monotonic() - 0.1
    assert wait_envelope_count(page, 1) == 1
    sent = page.reqs.of("/api/envelope")[0]
    assert sent["t"] - last >= 0.29
    assert sent["body"]["params"]["morph"]["ratio"] == 0.8
    page.wait_for_timeout(400)
    assert len(page.reqs.of("/api/envelope")) == 1


def partner_line_style(page):
    return page.evaluate(
        "() => ['#orig-line', '#mod-line', '#partner-line'].map(s => {"
        " const c = getComputedStyle(document.querySelector(s)); return {stroke: c.stroke, dash: c.strokeDasharray}; })"
    )


def test_TC_427_1_相手の包絡線が描かれる(page, two):
    a, _ = two
    with page.expect_response("**/api/envelope"):
        select_partner(page, a["id"])
    page.wait_for_function("() => document.querySelector('#partner-line').getAttribute('d')")
    expect(page.locator("#partner-line")).to_be_visible()
    orig, mod, partner = partner_line_style(page)
    assert rgb(partner["stroke"]) not in (rgb(orig["stroke"]), rgb(mod["stroke"]))
    assert partner["dash"] not in ("none", "")


def test_TC_427_2_相手なしに戻すと消える(page, two):
    a, _ = two
    with page.expect_response("**/api/envelope"):
        select_partner(page, a["id"])
    expect(page.locator("#partner-line")).to_be_visible()
    with page.expect_response("**/api/envelope"):
        select_partner(page, "")
    expect(page.locator("#partner-line")).to_be_hidden()


@pytest.mark.parametrize("action", ["#reset", "button[data-preset='太く']"])
def test_TC_428_1_TC_428_2_リセットとプリセットはmixだけ戻す(page, two, action):
    a, _ = two
    select_partner(page, a["id"])
    set_slider(page, "mix", 0.5)
    page.click(action)
    assert page.input_value("input[name=mix]") == "0"
    assert page.input_value("#partner") == a["id"]


def test_TC_429_1_mixのダブルクリックで0(page):
    set_slider(page, "mix", 0.6)
    page.dblclick("input[name=mix]")
    assert page.input_value("input[name=mix]") == "0"
    expect(page.locator("#mix-value")).to_have_text("0.00")


def test_TC_430_1_一覧は最新10件(page, wav_files):
    ids = [load_file(page, wav_files["one_sec"])["id"]]
    ids.append(load_file(page, wav_files["one_sec"])["id"])
    select_partner(page, ids[0])
    for _ in range(9):
        ids.append(load_file(page, wav_files["one_sec"])["id"])
    cur = [o["value"] for o in options(page, "#current")]
    par = [o["value"] for o in options(page, "#partner")]
    assert cur == ids[1:]
    assert par == [""] + ids[1:]
    assert page.input_value("#partner") == ""
    # 消えた相手を参照し続けていないこと（その後の要求が 404 にならない）
    set_slider_frame(page, 5)
    page.wait_for_timeout(600)
    expect(page.locator("#error")).to_be_empty()
