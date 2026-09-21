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
