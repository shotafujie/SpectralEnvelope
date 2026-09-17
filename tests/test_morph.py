"""003-morph: 伸縮・混合（ユニット）と API の morph パラメータ（統合）。"""

import numpy as np
import pytest

from jig.server import (
    EPS,
    Params,
    apply_bands,
    apply_params,
    apply_tilt,
    freq_axis,
    morph_log_sp,
    shift_formant,
    smooth_envelope,
    stretch_partner,
)
from tests import audio_fixtures as af
from tests.conftest import vowel_wav
from tests.test_api import envelope, reanalyze, synth

FREQ = freq_axis()


@pytest.fixture
def pair(analyze):
    """A = /a/ 3 秒、B = /i/ 2 秒 を分解して (A の応答, B の応答) を返す。"""
    a = analyze(vowel_wav("a", 3.0)).json()
    b = analyze(vowel_wav("i", 2.0)).json()
    return a, b


def stretched_db(client, b, n_a, frame):
    """B の original_db を位置 p で線形補間した値（テスト側で独立に計算）。"""
    p = frame * (b["frames"] - 1) / (n_a - 1)
    lo, hi = int(np.floor(p)), int(np.ceil(p))
    w = p - lo
    db_lo = np.array(envelope(client, b["id"], lo).json()["original_db"])
    db_hi = np.array(envelope(client, b["id"], hi).json()["original_db"])
    return (1 - w) * db_lo + w * db_hi


def morph(b, ratio):
    return {"morph": {"id": b["id"], "ratio": ratio}}


# ---------------------------------------------------------------- ユニット


def test_TC_403_1_伸縮して混ぜる():
    a = np.zeros((5, 4))
    b = np.array([[0.0] * 4, [10.0] * 4, [20.0] * 4])
    out = morph_log_sp(a, b, 0.5)
    np.testing.assert_allclose(out[:, 0], [0, 2.5, 5, 7.5, 10])
    assert np.all(out == out[:, :1])


def test_TC_403_2_Aが1フレームなら相手の先頭():
    a = np.zeros((1, 3))
    b = np.array([[4.0] * 3, [8.0] * 3])
    np.testing.assert_allclose(morph_log_sp(a, b, 1.0), [[4.0] * 3])


def _full_params():
    return dict(formant=1.3, smooth=20, tilt=4, bands=[3, -2, 5, -6])


def test_TC_405_1_morphは最初に適用される():
    rng = np.random.default_rng(3)
    sp_a = np.exp(rng.normal(-5, 2, (6, 1025)))
    sp_b = np.exp(rng.normal(-5, 2, (4, 1025)))
    p = Params(**_full_params(), morph={"id": "x", "ratio": 0.6})
    partner = stretch_partner(np.log(sp_b + EPS), 6)
    step = morph_log_sp(np.log(sp_a + EPS), np.log(sp_b + EPS), 0.6)
    step = shift_formant(step, 1.3)
    step = smooth_envelope(step, 20)
    step = apply_tilt(step, FREQ, 4)
    step = apply_bands(step, FREQ, [3, -2, 5, -6])
    np.testing.assert_allclose(apply_params(sp_a, p, partner=partner), np.exp(step), rtol=1e-9)


def test_TC_405_2_formantを先にすると結果が変わる():
    rng = np.random.default_rng(3)
    sp_a = np.exp(rng.normal(-5, 2, (6, 1025)))
    sp_b = np.exp(rng.normal(-5, 2, (4, 1025)))
    p = Params(**_full_params(), morph={"id": "x", "ratio": 0.6})
    partner = stretch_partner(np.log(sp_b + EPS), 6)
    step = shift_formant(np.log(sp_a + EPS), 1.3)
    step = morph_log_sp(step, np.log(sp_b + EPS), 0.6)
    step = smooth_envelope(step, 20)
    step = apply_tilt(step, FREQ, 4)
    step = apply_bands(step, FREQ, [3, -2, 5, -6])
    assert not np.allclose(apply_params(sp_a, p, partner=partner), np.exp(step), rtol=1e-6)


# ---------------------------------------------------------------- API


def test_TC_400_1_morph省略時は従来どおり(client, pair):
    a, _ = pair
    j = envelope(client, a["id"], 100).json()
    assert set(j) == {"freq", "original_db", "modified_db", "partner_db"}
    np.testing.assert_allclose(j["modified_db"], j["original_db"], atol=1e-6)


def test_TC_400_2_morph_nullは省略と同じ(client, pair):
    a, _ = pair
    x = envelope(client, a["id"], 100, {"tilt": 2, "morph": None}).json()["modified_db"]
    y = envelope(client, a["id"], 100, {"tilt": 2}).json()["modified_db"]
    assert x == y


def test_TC_401_1_ratio1_5は1と同じ(client, pair):
    a, b = pair
    x = envelope(client, a["id"], 100, morph(b, 1.5)).json()["modified_db"]
    y = envelope(client, a["id"], 100, morph(b, 1.0)).json()["modified_db"]
    assert x == y


def test_TC_401_2_負のratioは混合なし(client, pair):
    a, b = pair
    x = envelope(client, a["id"], 100, morph(b, -0.5)).json()["modified_db"]
    y = envelope(client, a["id"], 100).json()["modified_db"]
    np.testing.assert_allclose(x, y, atol=1e-6)


def test_TC_402_1_ratio0の包絡は混合なし(client, pair):
    a, b = pair
    x = envelope(client, a["id"], 100, morph(b, 0.0)).json()["modified_db"]
    y = envelope(client, a["id"], 100).json()["modified_db"]
    np.testing.assert_allclose(x, y, atol=1e-6)


def test_TC_402_2_ratio0の合成は混合なしと同一(client, pair):
    a, b = pair
    assert synth(client, a["id"], morph(b, 0.0)).content == synth(client, a["id"], omit=True).content


def test_TC_403_3_APIの混合は式どおり(client, pair):
    a, b = pair
    for frame in (100, 400):
        j = envelope(client, a["id"], frame, morph(b, 0.3)).json()
        expected = 0.7 * np.array(j["original_db"]) + 0.3 * stretched_db(client, b, a["frames"], frame)
        np.testing.assert_allclose(j["modified_db"], expected, atol=1e-6)


def test_TC_404_1_ratio1は伸縮後のB(client, pair):
    a, b = pair
    j = envelope(client, a["id"], 250, morph(b, 1.0)).json()
    np.testing.assert_allclose(j["modified_db"], stretched_db(client, b, a["frames"], 250), atol=1e-6)


def test_TC_404_2_Bが長くても伸縮後のB(client, analyze):
    a = analyze(vowel_wav("a", 3.0)).json()
    b = analyze(vowel_wav("i", 5.0)).json()
    for frame in (0, 300, a["frames"] - 1):
        j = envelope(client, a["id"], frame, morph(b, 1.0)).json()
        np.testing.assert_allclose(j["modified_db"], stretched_db(client, b, a["frames"], frame), atol=1e-6)


def test_TC_406_1_f0とapはAのもの(client, analyze, synth_spy):
    a = analyze(vowel_wav("a", 3.0)).json()
    b = analyze(af.wav_bytes(af.vowel("i", 3.0, f0=200.0))).json()
    synth(client, a["id"], omit=True)
    synth(client, a["id"], {**morph(b, 0.8), "pitch": 1.2})
    base, mixed = synth_spy
    np.testing.assert_allclose(mixed["f0"], base["f0"] * 1.2)
    np.testing.assert_array_equal(mixed["ap"], base["ap"])


def test_TC_406_2_合成音のf0はBに引っ張られない(client, analyze):
    a = analyze(vowel_wav("a", 3.0)).json()
    b = analyze(af.wav_bytes(af.vowel("i", 3.0, f0=200.0))).json()
    y, _, _ = af.read_wav(synth(client, a["id"], {**morph(b, 0.8), "pitch": 1.2}).content)
    f0, _ = reanalyze(y)
    assert np.median(f0[f0 > 0]) == pytest.approx(144, rel=0.05)


@pytest.mark.parametrize("b_dur", [5.0, 1.0])
def test_TC_407_1_TC_407_2_合成の長さはA(client, analyze, b_dur):
    a = analyze(vowel_wav("a", 3.0)).json()
    b = analyze(vowel_wav("i", b_dur)).json()
    y, _, _ = af.read_wav(synth(client, a["id"], morph(b, 0.5)).content)
    x, _, _ = af.read_wav(client.get(f"/api/original/{a['id']}").content)
    assert len(y) == len(x)


def test_TC_408_1_包絡の相手が未知なら404(client, pair):
    a, _ = pair
    r = envelope(client, a["id"], 100, {"morph": {"id": "deadbeef", "ratio": 0.5}})
    assert r.status_code == 404


def test_TC_408_2_合成の相手が未知なら404(client, pair):
    a, _ = pair
    assert synth(client, a["id"], {"morph": {"id": "deadbeef", "ratio": 0.5}}).status_code == 404


def test_TC_409_1_partner_dbは伸縮後のB(client, pair):
    a, b = pair
    j = envelope(client, a["id"], 100, morph(b, 0.5)).json()
    assert len(j["partner_db"]) == 1025
    np.testing.assert_allclose(j["partner_db"], stretched_db(client, b, a["frames"], 100), atol=1e-6)


def test_TC_409_2_両端のフレームはBの両端(client, pair):
    a, b = pair
    first = envelope(client, a["id"], 0, morph(b, 0.5)).json()["partner_db"]
    last = envelope(client, a["id"], a["frames"] - 1, morph(b, 0.5)).json()["partner_db"]
    np.testing.assert_allclose(first, envelope(client, b["id"], 0).json()["original_db"], atol=1e-6)
    np.testing.assert_allclose(last, envelope(client, b["id"], b["frames"] - 1).json()["original_db"], atol=1e-6)


def test_TC_409_3_ratio0でもpartner_dbを返す(client, pair):
    a, b = pair
    assert len(envelope(client, a["id"], 100, morph(b, 0.0)).json()["partner_db"]) == 1025


def test_TC_410_1_params省略ならpartner_dbはnull(client, pair):
    a, _ = pair
    assert envelope(client, a["id"], 100).json()["partner_db"] is None


def test_TC_410_2_morph以外だけならpartner_dbはnull(client, pair):
    a, _ = pair
    assert envelope(client, a["id"], 100, {"formant": 1.2}).json()["partner_db"] is None


def test_TC_411_1_自分自身との混合は混合なしと同じ(client, pair):
    a, _ = pair
    x = envelope(client, a["id"], 100, morph(a, 0.7)).json()["modified_db"]
    y = envelope(client, a["id"], 100).json()["modified_db"]
    np.testing.assert_allclose(x, y, atol=1e-6)


def test_TC_411_2_自分自身との混合とformant(client, pair):
    a, _ = pair
    x = envelope(client, a["id"], 100, {**morph(a, 0.7), "formant": 1.2}).json()["modified_db"]
    y = envelope(client, a["id"], 100, {"formant": 1.2}).json()["modified_db"]
    np.testing.assert_allclose(x, y, atol=1e-6)
