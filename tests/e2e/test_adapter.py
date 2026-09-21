"""アダプタ・Worker・デコード（008-browser-app）。観測点は window.engine。"""

import base64
import io

import numpy as np
import pytest
import soundfile as sf

from tests import audio_fixtures as af

INFO_KEYS = {"id", "fs", "fftSize", "duration", "frames", "f0Mean", "voicedFrames", "source"}


def b64(data):
    return base64.b64encode(data).decode()


@pytest.fixture(scope="session")
def wavs():
    """アダプタに渡すバイト列（base64）。"""
    buf = io.BytesIO()
    x = af.vowel("a", 1.5, fs=22050)
    sf.write(buf, np.stack([x, x], axis=1), 22050, format="WAV", subtype="PCM_16")
    return {
        "1s": b64(af.wav_bytes(af.vowel("a", 1.0))),
        "3s": b64(af.wav_bytes(af.vowel("a", 3.0))),
        "10s": b64(af.wav_bytes(af.vowel("a", 10.0))),
        "12s": b64(af.wav_bytes(af.vowel("a", 12.0))),
        "short": b64(af.wav_bytes(af.vowel("a", 0.5))),
        "gap": b64(af.wav_bytes(af.with_silence(af.vowel("a", 1.5)))),
        "silence": b64(af.wav_bytes(np.zeros(int(1.5 * af.FS)))),
        "stereo_22k": b64(buf.getvalue()),  # 22050Hz ステレオ 1.5 秒
        "broken": b64(bytes(range(256)) * 4),
    }


def analyze(page, data_b64, source="録音"):
    """analyze を呼び、解決なら情報を返す。拒否なら AssertionError。"""
    r = settle(page, "(b) => window.engine.analyze(window.__bytes(b), '録音')", data_b64)
    assert r["ok"], r
    return r["value"]


def settle(page, fn, *args):
    return page.evaluate("([fn, ...args]) => window.__settle((0, eval(fn))(...args))", [fn, *args])


# ---------------------------------------------------------------- アダプタの形

def test_TC_900_1_アダプタは5つの関数を持ちPromiseを返す(app_page):
    r = app_page.evaluate("""() => {
        const names = ['analyze', 'envelope', 'synthesize', 'original', 'list'];
        return {
            types: names.map(n => typeof window.engine[n]),
            thenable: typeof window.engine.list().then === 'function',
        };
    }""")
    assert r["types"] == ["function"] * 5
    assert r["thenable"]


def test_TC_901_1_analyzeは情報に解決される(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    assert set(info) == INFO_KEYS


def test_TC_905_1_listは分解した順の情報を返す(app_page, wavs):
    ids = [analyze(app_page, wavs["3s"])["id"] for _ in range(3)]
    r = settle(app_page, "() => window.engine.list()")
    assert r["ok"], r
    assert [i["id"] for i in r["value"]] == ids
    for info in r["value"]:
        assert set(info) == INFO_KEYS


def test_TC_906_1_分解中もメインスレッドは止まらない(app_page, wavs):
    ticks = app_page.evaluate("""async (b) => {
        let ticks = 0;
        const h = setInterval(() => ticks++, 100);
        await window.engine.analyze(window.__bytes(b), '録音');
        clearInterval(h);
        return ticks;
    }""", wavs["10s"])
    assert ticks >= 3


def test_TC_909_1_読み込み前に呼ばれても待ってから実行する(browser, static_url):
    """window.engine が作られたその場で analyze を呼ぶ（エンジンの読み込みは始まったばかり）。"""
    from tests.e2e.conftest import ADAPTER_HELPERS

    early = """
    window.__early = new Promise(resolve => {
      Object.defineProperty(window, 'engine', {
        configurable: true,
        set(v) {
          Object.defineProperty(window, 'engine', { value: v, writable: true, configurable: true });
          resolve(window.__settle(v.analyze(window.__bytes(B64), '録音')));
        },
        get() { return undefined; },
      });
    });
    """.replace("B64", repr(b64(af.wav_bytes(af.vowel("a", 1.0)))))

    ctx = browser.new_context(base_url=static_url)
    page = ctx.new_page()
    page.set_default_timeout(20000)
    page.add_init_script(ADAPTER_HELPERS + early)
    try:
        page.goto("/app/index.html")
        r = page.evaluate("() => window.__early")
        assert r["ok"], r
    finally:
        ctx.close()


# ---------------------------------------------------------------- デコード

def test_TC_920_1_任意の条件の音声を44100Hzモノラルにする(app_page, wavs):
    info = analyze(app_page, wavs["stereo_22k"])
    assert info["fs"] == 44100
    assert abs(info["duration"] - 1.5) <= 0.01


def test_TC_921_1_10秒を超えたら先頭10秒だけを分解する(app_page, wavs):
    info = analyze(app_page, wavs["12s"])
    assert info["duration"] == pytest.approx(10.0, abs=1e-6)
    assert info["frames"] == 2001


def test_TC_922_1_1秒未満はtoo_shortで拒否される(app_page, wavs):
    r = settle(app_page, "(b) => window.engine.analyze(window.__bytes(b), '録音')", wavs["short"])
    assert r == {"ok": False, "code": "too_short", "message": r["message"]}


def test_TC_923_1_デコードできないデータはdecode_failedで拒否される(app_page, wavs):
    r = settle(app_page, "(b) => window.engine.analyze(window.__bytes(b), '録音')", wavs["broken"])
    assert r["ok"] is False and r["code"] == "decode_failed"


# ---------------------------------------------------------------- 情報の値

def test_TC_924_1_durationはサンプル数を44100で割った秒数(app_page, wavs):
    assert analyze(app_page, wavs["3s"])["duration"] == pytest.approx(3.0, abs=1e-6)


def test_TC_925_1_fsとfftSize(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    assert (info["fs"], info["fftSize"]) == (44100, 2048)


def test_TC_926_1_framesはf0の要素数(app_page, wavs):
    assert analyze(app_page, wavs["3s"])["frames"] == 601


def test_TC_927_1_voicedFramesは昇順で無声フレームを含まない(app_page, wavs):
    info = analyze(app_page, wavs["gap"])
    voiced = info["voicedFrames"]
    assert voiced == sorted(voiced) and len(set(voiced)) == len(voiced)
    assert all(0 <= i < info["frames"] for i in voiced)
    assert not set(range(0, 50)) & set(voiced)  # 先頭 0.25 秒は無音


def test_TC_928_1_f0Meanは有声フレームの平均(app_page, wavs):
    assert 100 <= analyze(app_page, wavs["3s"])["f0Mean"] <= 140


def test_TC_928_2_有声フレームが無いときf0Meanは0(app_page, wavs):
    assert analyze(app_page, wavs["silence"])["f0Mean"] == 0


def test_TC_929_1_sourceは渡した表示名と一致する(app_page, wavs):
    assert analyze(app_page, wavs["3s"])["source"] == "録音"


# ---------------------------------------------------------------- 包絡・再合成・元音

def test_TC_902_1_envelopeの戻り値(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = settle(app_page, "(id) => window.engine.envelope(id, 100, {})", info["id"])
    assert r["ok"], r
    env = r["value"]
    assert [len(env[k]) for k in ("freq", "originalDb", "modifiedDb")] == [1025] * 3
    assert env["partnerDb"] is None


def test_TC_902_2_tiltは対数周波数に比例した差になる(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = settle(app_page, "(id) => window.engine.envelope(id, 100, { tilt: 6 })", info["id"])
    assert r["ok"], r
    env = r["value"]
    diff = np.array(env["modifiedDb"]) - np.array(env["originalDb"])
    freq = np.array(env["freq"])
    expected = 6 * np.log2(np.maximum(freq, 20.0) / 1000.0)
    assert np.max(np.abs(diff - expected)) <= 1e-6


def test_TC_903_1_synthesizeは元音と同じ長さのFloat32Arrayを返す(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = app_page.evaluate("""async (id) => {
        const y = await window.engine.synthesize(id, {});
        return { ctor: y.constructor.name, length: y.length, finite: y.every(Number.isFinite) };
    }""", info["id"])
    assert r["ctor"] == "Float32Array"
    assert r["length"] == round(info["duration"] * 44100)
    assert r["finite"]


def test_TC_904_1_originalは元の音声サンプルを返す(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = app_page.evaluate("""async (id) => {
        const y = await window.engine.original(id);
        return { ctor: y.constructor.name, length: y.length };
    }""", info["id"])
    assert r["ctor"] == "Float32Array"
    assert r["length"] == int(info["duration"] * 44100)


def test_TC_914_1_保持していないmorph先はenvelopeでnot_found(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = settle(app_page, "(id) => window.engine.envelope(id, 100, { morph: { id: 'deadbeef', ratio: 0.5 } })",
               info["id"])
    assert r["ok"] is False and r["code"] == "not_found"


def test_TC_914_2_保持していないmorph先はsynthesizeでnot_found(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = settle(app_page, "(id) => window.engine.synthesize(id, { morph: { id: 'deadbeef', ratio: 0.5 } })",
               info["id"])
    assert r["ok"] is False and r["code"] == "not_found"


def test_morphは相手の包絡に近づける(app_page, wavs):
    """morph の解決が Worker 側で効いていること（SPEC-914 の前提）。"""
    a = analyze(app_page, wavs["3s"])
    b = analyze(app_page, wavs["gap"])
    r = app_page.evaluate("""async ([a, b]) => {
        const plain = await window.engine.envelope(a, 100, {});
        const mixed = await window.engine.envelope(a, 100, { morph: { id: b, ratio: 1.0 } });
        return { plain: Array.from(plain.modifiedDb), mixed: Array.from(mixed.modifiedDb),
                 partner: mixed.partnerDb && Array.from(mixed.partnerDb) };
    }""", [a["id"], b["id"]])
    assert r["partner"] is not None
    assert np.max(np.abs(np.array(r["mixed"]) - np.array(r["partner"]))) <= 1e-6
    assert np.max(np.abs(np.array(r["mixed"]) - np.array(r["plain"]))) > 1e-3


# ---------------------------------------------------------------- 保持の件数（アダプタ越し）

def test_TC_913_1_保持していないidのenvelopeはnot_found(app_page):
    r = settle(app_page, "() => window.engine.envelope('deadbeef', 0, {})")
    assert r["ok"] is False and r["code"] == "not_found"


def test_TC_913_2_保持していないidのsynthesizeとoriginalはnot_found(app_page):
    for name in ("synthesize", "original"):
        r = settle(app_page, f"() => window.engine.{name}('deadbeef', {{}})")
        assert r["ok"] is False and r["code"] == "not_found", name


@pytest.fixture(scope="module")
def ten_ids(browser, static_url, wavs):
    """1 秒の音声を 11 件分解したページ（分解は重いので使い回す）。"""
    from tests.e2e.conftest import ADAPTER_HELPERS

    ctx = browser.new_context(base_url=static_url)
    page = ctx.new_page()
    page.set_default_timeout(60000)
    page.add_init_script(ADAPTER_HELPERS)
    page.goto("/app/index.html")
    ids = page.evaluate("""async (b) => {
        const ids = [];
        for (let i = 0; i < 11; i++) ids.push((await window.engine.analyze(window.__bytes(b), '録音')).id);
        return ids;
    }""", wavs["1s"])
    yield page, ids
    ctx.close()


def test_TC_912_1_10件目までは3つの呼び出しが成功する(ten_ids):
    page, ids = ten_ids
    # 11 件目の分解前の 10 件のうち、最も古い id（＝ 1 件目）を除いた 2 件目を見る
    r = page.evaluate("""async (id) => {
        const out = {};
        for (const name of ['envelope', 'synthesize', 'original']) {
            const p = name === 'envelope' ? window.engine.envelope(id, 0, {})
                : name === 'synthesize' ? window.engine.synthesize(id, {})
                : window.engine.original(id);
            out[name] = await window.__settle(p);
        }
        return out;
    }""", ids[1])
    assert all(v["ok"] for v in r.values()), r


def test_TC_911_1_11件目を分解すると1件目はnot_foundになる(ten_ids):
    page, ids = ten_ids
    r = page.evaluate("(id) => window.__settle(window.engine.envelope(id, 0, {}))", ids[0])
    assert r["ok"] is False and r["code"] == "not_found"
    listed = page.evaluate("() => window.engine.list()")
    assert [i["id"] for i in listed] == ids[1:]


# ---------------------------------------------------------------- 取り消しと順序

def test_TC_907_1_古いenvelopeはsupersededで拒否される(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    first, second = app_page.evaluate("""async (id) => {
        const a = window.__settle(window.engine.envelope(id, 100, { tilt: 3 }));
        const b = window.__settle(window.engine.envelope(id, 100, { tilt: 6 }));
        return [await a, await b];
    }""", info["id"])
    assert first["ok"] is False and first["code"] == "superseded"
    assert second["ok"] is True


def test_TC_907_2_後から呼んだenvelopeの結果は単独で呼んだときと同じ(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    r = app_page.evaluate("""async (id) => {
        const a = window.__settle(window.engine.envelope(id, 100, { tilt: 3 }));
        const b = window.engine.envelope(id, 100, { tilt: 6 });
        await a;
        const raced = Array.from((await b).modifiedDb);
        const alone = Array.from((await window.engine.envelope(id, 100, { tilt: 6 })).modifiedDb);
        return { raced, alone };
    }""", info["id"])
    assert np.array_equal(np.array(r["raced"]), np.array(r["alone"]))


def test_TC_908_1_synthesizeは取り消されず2つとも解決する(app_page, wavs):
    info = analyze(app_page, wavs["3s"])
    both = app_page.evaluate("""async (id) => {
        const a = window.__settle(window.engine.synthesize(id, { tilt: 3 }));
        const b = window.__settle(window.engine.synthesize(id, { tilt: 6 }));
        const [x, y] = [await a, await b];
        return [{ ok: x.ok, code: x.code, length: x.value && x.value.length },
                { ok: y.ok, code: y.code, length: y.value && y.value.length }];
    }""", info["id"])
    assert [r["ok"] for r in both] == [True, True], both
    assert [r["length"] for r in both] == [round(info["duration"] * 44100)] * 2


def test_TC_908_2_analyzeは取り消されず2つとも解決する(app_page, wavs):
    r = app_page.evaluate("""async (b) => {
        const a1 = window.__settle(window.engine.analyze(window.__bytes(b), '録音'));
        const a2 = window.__settle(window.engine.analyze(window.__bytes(b), '録音'));
        const both = [await a1, await a2];
        return { both, count: (await window.engine.list()).length };
    }""", wavs["1s"])
    assert [x["ok"] for x in r["both"]] == [True, True], r
    assert r["both"][0]["value"]["id"] != r["both"][1]["value"]["id"]
    assert r["count"] == 2
