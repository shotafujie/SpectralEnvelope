"""HTTP API の統合テスト。pyworld / ffmpeg は本物を使う。"""

import re

import numpy as np
import pytest
import pyworld

from tests import audio_fixtures as af
from tests.conftest import vowel_wav

FS = 44100
FREQ = np.arange(1025) * FS / 2048
ALL_PARAMS = {"formant": 1.2, "tilt": 3.0, "bands": [2, -2, 4, -4], "smooth": 30, "pitch": 1.3}


def reanalyze(y, f0_floor=71.0):
    f0, t = pyworld.harvest(y, FS, frame_period=5.0, f0_floor=f0_floor)
    sp = pyworld.cheaptrick(y, f0, t, FS)
    return f0, sp


def envelope_diff(sp_a, f0_a, sp_b, f0_b):
    n = min(len(f0_a), len(f0_b))
    v = (f0_a[:n] > 0) & (f0_b[:n] > 0)
    band = (FREQ >= 50) & (FREQ <= 8000)
    da = 10 * np.log10(sp_a[:n][v] + 1e-12)
    db = 10 * np.log10(sp_b[:n][v] + 1e-12)
    return float(np.abs(da - db)[:, band].mean())


def synth(client, id_, params=None, omit=False):
    body = {"id": id_} if omit else {"id": id_, "params": params}
    return client.post("/api/synthesize", json=body)


def envelope(client, id_, frame, params=None):
    body = {"id": id_, "frame": frame}
    if params is not None:
        body["params"] = params
    return client.post("/api/envelope", json=body)


def mid_voiced(info):
    v = info["voiced_frames"]
    return v[len(v) // 2]


# ---------------------------------------------------------------- analyze


def test_TC_001_1_webmを分解して必要なキーを返す(analyze):
    r = analyze(af.webm_bytes(af.vowel("a")), "rec.webm", "audio/webm")
    assert r.status_code == 200
    assert set(r.json()) >= {"id", "fs", "duration", "frames", "fft_size", "f0_mean", "voiced_frames"}


def test_TC_001_2_webmのdurationは元の長さ(analyze):
    r = analyze(af.webm_bytes(af.vowel("a")), "rec.webm", "audio/webm")
    assert r.json()["duration"] == pytest.approx(3.0, abs=0.1)


def test_TC_002_1_22050Hzステレオwavは44100Hzモノラルになる(client, analyze):
    x = af.vowel("a", 2.0, fs=22050)
    r = analyze(af.wav_bytes(np.stack([x, x], axis=1), fs=22050))
    assert r.status_code == 200
    assert r.json()["duration"] == pytest.approx(2.0, abs=0.01)
    _, fs, info = af.read_wav(client.get(f"/api/original/{r.json()['id']}").content)
    assert (fs, info.channels) == (44100, 1)


def test_TC_002_2_44100Hzモノラルwavはサンプルが保たれる(client, analyze):
    data = vowel_wav()
    r = analyze(data)
    assert r.status_code == 200
    y, _, _ = af.read_wav(client.get(f"/api/original/{r.json()['id']}").content)
    x, _, _ = af.read_wav(data)
    np.testing.assert_array_equal(y, x)


def test_TC_003_1_fsとfft_size(analyze):
    j = analyze().json()
    assert (j["fs"], j["fft_size"]) == (44100, 2048)


def test_TC_003_2_48000Hz入力でもfsは44100(analyze):
    j = analyze(af.wav_bytes(af.vowel("a", 1.5, fs=48000), fs=48000)).json()
    assert j["fs"] == 44100


@pytest.mark.parametrize(("n", "dur"), [(132300, 3.0), (66150, 1.5)])
def test_TC_004_1_TC_004_2_durationはサンプル数割る44100(analyze, n, dur):
    x = af.vowel("a", 3.0)[:n]
    assert analyze(af.wav_bytes(x)).json()["duration"] == dur


def test_TC_005_1_framesはf0の要素数(analyze):
    x, _, _ = af.read_wav(vowel_wav())
    f0, _ = pyworld.harvest(x, FS, frame_period=5.0)
    assert analyze().json()["frames"] == len(f0) == 601


def test_TC_005_2_最終フレームが存在する(client, analyze):
    j = analyze().json()
    assert envelope(client, j["id"], j["frames"] - 1).status_code == 200


def test_TC_006_1_voiced_framesは有声フレームの昇順(client, analyze, synth_spy):
    j = analyze(vowel_wav(silence=True)).json()
    v = j["voiced_frames"]
    assert v == sorted(v)
    assert v[0] > 20 and v[-1] < j["frames"] - 20
    synth(client, j["id"], omit=True)
    f0 = synth_spy[-1]["f0"]
    assert np.all(f0[v] > 0)


def test_TC_006_2_voiced_framesの個数(client, analyze, synth_spy):
    j = analyze(vowel_wav(silence=True)).json()
    synth(client, j["id"], omit=True)
    assert len(j["voiced_frames"]) == int(np.sum(synth_spy[-1]["f0"] > 0))


def test_TC_007_1_f0_meanは約120Hz(analyze):
    assert analyze().json()["f0_mean"] == pytest.approx(120, abs=6)


def test_TC_007_2_無音ではf0_meanが0(analyze):
    j = analyze(af.wav_bytes(np.zeros(2 * FS))).json()
    assert j["f0_mean"] == 0
    assert j["voiced_frames"] == []


def test_TC_007_3_f0_meanは有声フレームの平均(client, analyze, synth_spy):
    j = analyze(vowel_wav(silence=True)).json()
    synth(client, j["id"], omit=True)
    f0 = synth_spy[-1]["f0"]
    assert j["f0_mean"] == pytest.approx(float(f0[f0 > 0].mean()), abs=1e-6)


def test_TC_008_1_idは8桁の16進(analyze):
    assert re.fullmatch(r"[0-9a-f]{8}", analyze().json()["id"])


def test_TC_008_2_idは毎回異なる(analyze):
    data = af.wav_bytes(af.vowel("a", 1.0))
    ids = {analyze(data).json()["id"] for _ in range(5)}
    assert len(ids) == 5


def test_TC_009_1_1秒未満は400(analyze):
    r = analyze(af.wav_bytes(af.vowel("a", 0.5)))
    assert r.status_code == 400
    assert isinstance(r.json()["detail"], str) and r.json()["detail"]


def test_TC_009_2_ちょうど1秒は受け付ける(analyze):
    x = af.vowel("a", 1.0)
    assert len(x) == 44100
    assert analyze(af.wav_bytes(x)).status_code == 200


def test_TC_010_1_10秒超は切り詰める(client, analyze):
    r = analyze(af.wav_bytes(af.vowel("a", 12.0)))
    assert r.status_code == 200
    assert r.json()["duration"] == 10.0
    y, _, _ = af.read_wav(client.get(f"/api/original/{r.json()['id']}").content)
    assert len(y) == 441000


def test_TC_010_2_ちょうど10秒(analyze):
    assert analyze(af.wav_bytes(af.vowel("a", 10.0))).json()["duration"] == 10.0


def test_TC_011_1_ランダムバイトは400(analyze):
    r = analyze(np.random.default_rng(0).bytes(1024), "x.webm", "audio/webm")
    assert r.status_code == 400
    assert r.json()["detail"]


def test_TC_011_2_空ファイルは400(analyze):
    assert analyze(b"", "x.webm", "audio/webm").status_code == 400


def test_TC_012_1_audioフィールドが無いと422(client):
    r = client.post("/api/analyze", files={"file": ("a.wav", vowel_wav(), "audio/wav")})
    assert r.status_code == 422


def _analyze_n(analyze, n):
    data = af.wav_bytes(af.vowel("a", 1.0))
    return [analyze(data).json()["id"] for _ in range(n)]


def test_TC_013_1_11件目で最古が破棄される(client, analyze):
    ids = _analyze_n(analyze, 11)
    assert client.get(f"/api/original/{ids[0]}").status_code == 404
    assert synth(client, ids[0], omit=True).status_code == 404
    assert envelope(client, ids[0], 0).status_code == 404


def test_TC_013_2_11件目で2件目は残る(client, analyze):
    ids = _analyze_n(analyze, 11)
    assert client.get(f"/api/original/{ids[1]}").status_code == 200


def test_TC_014_1_10件までは全て残る(client, analyze):
    ids = _analyze_n(analyze, 10)
    assert [client.get(f"/api/original/{i}").status_code for i in ids] == [200] * 10


# ---------------------------------------------------------------- original


def test_TC_020_1_元音WAVの形式(client, analyze):
    r = client.get(f"/api/original/{analyze().json()['id']}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"
    _, fs, info = af.read_wav(r.content)
    assert (info.subtype, info.channels, fs) == ("PCM_16", 1, 44100)


def test_TC_021_1_元音WAVの長さ(client, analyze):
    j = analyze(af.webm_bytes(af.vowel("a")), "rec.webm", "audio/webm").json()
    y, _, _ = af.read_wav(client.get(f"/api/original/{j['id']}").content)
    assert len(y) == round(j["duration"] * 44100)


def test_TC_022_1_元音の未知id(client):
    assert client.get("/api/original/deadbeef").status_code == 404


# ---------------------------------------------------------------- synthesize


@pytest.mark.parametrize("params", [None, {"formant": 1.3, "pitch": 0.8}])
def test_TC_030_1_TC_030_2_合成WAVの形式(client, analyze, params):
    r = synth(client, analyze().json()["id"], params, omit=params is None)
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"
    _, fs, info = af.read_wav(r.content)
    assert (info.subtype, info.channels, fs) == ("PCM_16", 1, 44100)


@pytest.mark.parametrize("params", [None, {"pitch": 2.0}])
def test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致(client, analyze, params):
    id_ = analyze().json()["id"]
    y, _, _ = af.read_wav(synth(client, id_, params, omit=params is None).content)
    x, _, _ = af.read_wav(client.get(f"/api/original/{id_}").content)
    assert len(y) == len(x)


@pytest.mark.parametrize(("vowel_name", "omit"), [("a", True), ("i", False)])
def test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下(client, analyze, vowel_name, omit):
    id_ = analyze(vowel_wav(vowel_name)).json()["id"]
    x, _, _ = af.read_wav(client.get(f"/api/original/{id_}").content)
    y, _, _ = af.read_wav(synth(client, id_, {}, omit=omit).content)
    f0_x, sp_x = reanalyze(x)
    f0_y, sp_y = reanalyze(y)
    assert envelope_diff(sp_x, f0_x, sp_y, f0_y) <= 1.0


def test_TC_033_1_無加工の3通りは同一(client, analyze):
    id_ = analyze().json()["id"]
    defaults = {"formant": 1.0, "tilt": 0.0, "bands": [0, 0, 0, 0], "smooth": 0, "pitch": 1.0}
    a = synth(client, id_, omit=True).content
    b = synth(client, id_, {}).content
    c = synth(client, id_, defaults).content
    assert a == b == c


def test_TC_035_1_合成の未知id(client):
    assert synth(client, "deadbeef", omit=True).status_code == 404


def test_TC_036_1_apは加工されない(client, analyze, synth_spy):
    id_ = analyze().json()["id"]
    synth(client, id_, omit=True)
    synth(client, id_, ALL_PARAMS)
    np.testing.assert_array_equal(synth_spy[0]["ap"], synth_spy[1]["ap"])


def test_TC_037_1_合成のspと包絡APIのmodified_dbが一致する(client, analyze, synth_spy):
    id_ = analyze().json()["id"]
    params = {k: v for k, v in ALL_PARAMS.items() if k != "pitch"}
    synth(client, id_, params)
    sp = synth_spy[-1]["sp"]
    for frame in (50, 200):
        m = envelope(client, id_, frame, params).json()["modified_db"]
        np.testing.assert_allclose(10 * np.log10(sp[frame]), m, atol=1e-6)


# ---------------------------------------------------------------- envelope


def test_TC_040_1_包絡応答の形(client, analyze):
    j = envelope(client, analyze().json()["id"], 100).json()
    assert [len(j[k]) for k in ("freq", "original_db", "modified_db")] == [1025] * 3
    assert j["freq"][0] == 0 and j["freq"][1024] == 22050
    np.testing.assert_allclose(j["freq"], FREQ)


def test_TC_041_1_original_dbは元spのdB値(client, analyze):
    id_ = analyze().json()["id"]
    x, _, _ = af.read_wav(client.get(f"/api/original/{id_}").content)
    _, sp = reanalyze(x)
    j = envelope(client, id_, 100).json()
    np.testing.assert_allclose(j["original_db"], 10 * np.log10(sp[100] + 1e-12), atol=1e-6)


@pytest.mark.parametrize("params", [None, {}])
def test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致(client, analyze, params):
    j = envelope(client, analyze().json()["id"], 100, params).json()
    np.testing.assert_allclose(j["modified_db"], j["original_db"], atol=1e-6)


@pytest.mark.parametrize(("frame", "status"), [(-1, 400), ("frames", 400), (0, 200)])
def test_TC_043_1_TC_043_2_TC_043_3_frame範囲(client, analyze, frame, status):
    j = analyze().json()
    frame = j["frames"] if frame == "frames" else frame
    assert envelope(client, j["id"], frame).status_code == status


def test_TC_044_1_包絡の未知id(client):
    assert envelope(client, "deadbeef", 0).status_code == 404


def test_TC_045_1_母音でピーク位置が変わる(client, analyze):
    peaks = []
    for name in ("a", "i"):
        info = analyze(vowel_wav(name)).json()
        j = envelope(client, info["id"], mid_voiced(info)).json()
        peaks.append(af.peak_freq(j["original_db"], FREQ))
    assert abs(peaks[0] - peaks[1]) >= 200


# ---------------------------------------------------------------- params（API 経由）


def test_TC_050_1_未指定キーは初期値(client, analyze):
    id_ = analyze().json()["id"]
    full = {"formant": 1.0, "tilt": 3.0, "bands": [0, 0, 0, 0], "smooth": 0, "pitch": 1.0}
    a = envelope(client, id_, 100, {"tilt": 3.0}).json()["modified_db"]
    b = envelope(client, id_, 100, full).json()["modified_db"]
    assert a == b


def test_TC_051_1_formant範囲外はクランプされて包絡に効く(client, analyze):
    id_ = analyze().json()["id"]
    a = envelope(client, id_, 100, {"formant": 5.0}).json()["modified_db"]
    b = envelope(client, id_, 100, {"formant": 1.6}).json()["modified_db"]
    assert a == b


def test_TC_055_2_smooth5はsmooth10と同じ(client, analyze):
    id_ = analyze().json()["id"]
    a = envelope(client, id_, 100, {"smooth": 5}).json()["modified_db"]
    b = envelope(client, id_, 100, {"smooth": 10}).json()["modified_db"]
    assert a == b


def test_TC_056_1_bands要素数3は422(client, analyze):
    r = envelope(client, analyze().json()["id"], 100, {"bands": [0, 0, 0]})
    assert r.status_code == 422


def test_TC_056_2_bandsに文字列は422(client, analyze):
    r = synth(client, analyze().json()["id"], {"bands": ["a", 0, 0, 0]})
    assert r.status_code == 422


# ---------------------------------------------------------------- formant / pitch の効果


@pytest.mark.parametrize(("r", "lo", "hi"), [(1.25, 1.1875, 1.3125), (0.8, 0.76, 0.84)])
def test_TC_062_1_TC_062_2_formantでグラフのピークが移る(client, analyze, r, lo, hi):
    info = analyze().json()
    j = envelope(client, info["id"], mid_voiced(info), {"formant": r}).json()
    ratio = af.peak_freq(j["modified_db"], FREQ) / af.peak_freq(j["original_db"], FREQ)
    assert lo <= ratio <= hi


def test_TC_063_1_formantで合成音のピークが移る(client, analyze):
    id_ = analyze().json()["id"]
    x, _, _ = af.read_wav(client.get(f"/api/original/{id_}").content)
    y, _, _ = af.read_wav(synth(client, id_, {"formant": 1.25}).content)

    def mean_peak(sig):
        f0, sp = reanalyze(sig)
        return af.peak_freq(10 * np.log10(sp[f0 > 0] + 1e-12).mean(axis=0), FREQ)

    assert 1.1875 <= mean_peak(y) / mean_peak(x) <= 1.3125


@pytest.mark.parametrize(("pitch", "lo", "hi"), [(1.5, 1.455, 1.545), (0.5, 0.485, 0.515)])
def test_TC_100_1_TC_100_2_pitchで合成音のf0が変わる(client, analyze, pitch, lo, hi):
    id_ = analyze().json()["id"]
    x, _, _ = af.read_wav(client.get(f"/api/original/{id_}").content)
    y, _, _ = af.read_wav(synth(client, id_, {"pitch": pitch}).content)
    # pitch 0.5 で f0 ≈60Hz になり、harvest 既定の下限 71Hz ではオクターブ上を拾うため下限を下げる
    f0_x, _ = reanalyze(x, f0_floor=40.0)
    f0_y, _ = reanalyze(y, f0_floor=40.0)
    v = (f0_x > 0) & (f0_y > 0)
    assert lo <= np.median(f0_y[v]) / np.median(f0_x[v]) <= hi


def test_TC_101_1_無声フレームは0のまま(client, analyze, synth_spy):
    id_ = analyze(vowel_wav(silence=True)).json()["id"]
    synth(client, id_, omit=True)
    synth(client, id_, {"pitch": 2.0})
    base, scaled = synth_spy[0]["f0"], synth_spy[1]["f0"]
    assert np.any(base == 0)
    assert np.all(scaled[base == 0] == 0)
    np.testing.assert_allclose(scaled[base > 0], base[base > 0] * 2)


def test_TC_102_1_pitchは包絡に影響しない(client, analyze):
    j = envelope(client, analyze().json()["id"], 100, {"pitch": 1.7}).json()
    np.testing.assert_allclose(j["modified_db"], j["original_db"], atol=1e-6)


# ---------------------------------------------------------------- UI 配信


def test_TC_123_1_ルートでUIページを返す(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "<html" in r.text
