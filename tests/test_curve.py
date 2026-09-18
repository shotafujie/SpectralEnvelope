"""004-gain-curve: ゲインカーブ関数（ユニット）と API の curve パラメータ（統合）。"""

import numpy as np
import pytest
from pydantic import ValidationError

from jig.server import (
    EPS,
    Params,
    apply_bands,
    apply_curve,
    apply_params,
    apply_tilt,
    curve_gain_db,
    freq_axis,
    morph_log_sp,
    shift_formant,
    smooth_envelope,
    stretch_partner,
)
from tests.test_api import envelope, synth

FREQ = freq_axis()
LN10_10 = np.log(10) / 10
F_J = 50 * 400 ** (np.arange(20) / 19)


def reference_curve(f, c):
    return np.interp(np.log2(np.maximum(f, 1e-9)), np.log2(F_J), c)


def random_curve(seed=5):
    return np.round(np.random.default_rng(seed).uniform(-12, 12, 20), 1).tolist()


# ---------------------------------------------------------------- パラメータ


def test_TC_500_1_curveの既定値は全0():
    assert Params.model_validate({}).curve == [0.0] * 20


def test_TC_500_2_curve省略は全0と同じ(client, analyze):
    id_ = analyze().json()["id"]
    x = envelope(client, id_, 100, {"tilt": 1}).json()["modified_db"]
    y = envelope(client, id_, 100, {"tilt": 1, "curve": [0] * 20}).json()["modified_db"]
    assert x == y


def test_TC_501_1_要素数19は422(client, analyze):
    assert envelope(client, analyze().json()["id"], 100, {"curve": [0] * 19}).status_code == 422


def test_TC_501_2_文字列を含むと422(client, analyze):
    assert synth(client, analyze().json()["id"], {"curve": ["a"] + [0] * 19}).status_code == 422


def test_TC_501_3_要素数21はバリデーションエラー():
    with pytest.raises(ValidationError):
        Params(curve=[0] * 21)


def test_TC_502_1_curveのクランプ():
    c = [20, -20] + [5.5] * 18
    assert Params(curve=c).curve == [12, -12] + [5.5] * 18


# ---------------------------------------------------------------- ゲインカーブ


def test_TC_503_1_ゲインはカーブどおり加算される():
    c = random_curve()
    x = np.random.default_rng(1).normal(-5, 2, (3, 1025))
    d = (apply_curve(x, FREQ, c) - x) / LN10_10
    np.testing.assert_allclose(d, np.broadcast_to(reference_curve(FREQ, c), d.shape), atol=1e-9)


def test_TC_503_2_API全6dBは全ビン6dB上がる(client, analyze):
    j = envelope(client, analyze().json()["id"], 100, {"curve": [6] * 20}).json()
    np.testing.assert_allclose(np.array(j["modified_db"]) - j["original_db"], 6.0, atol=1e-6)


def test_TC_504_1_制御点での値と区間の線形性():
    c = random_curve(7)
    np.testing.assert_allclose(curve_gain_db(F_J, c), c, atol=1e-9)
    mids = np.sqrt(F_J[:-1] * F_J[1:])
    np.testing.assert_allclose(curve_gain_db(mids, c), (np.array(c[:-1]) + np.array(c[1:])) / 2, atol=1e-9)


def test_TC_504_2_範囲外は端の値():
    c = random_curve(9)
    g = curve_gain_db(np.array([0.0, 30.0, 21000.0, 22050.0]), c)
    np.testing.assert_allclose(g, [c[0], c[0], c[19], c[19]], atol=1e-9)


def _sps():
    rng = np.random.default_rng(4)
    return np.exp(rng.normal(-5, 2, (5, 1025))), np.exp(rng.normal(-5, 2, (3, 1025)))


def test_TC_505_1_curveは最後に適用される():
    sp_a, sp_b = _sps()
    c = random_curve()
    p = Params(formant=1.3, smooth=20, tilt=4, bands=[3, -2, 5, -6], curve=c,
               morph={"id": "x", "ratio": 0.4})
    step = morph_log_sp(np.log(sp_a + EPS), np.log(sp_b + EPS), 0.4)
    step = shift_formant(step, 1.3)
    step = smooth_envelope(step, 20)
    step = apply_tilt(step, FREQ, 4)
    step = apply_bands(step, FREQ, [3, -2, 5, -6])
    step = apply_curve(step, FREQ, c)
    partner = stretch_partner(np.log(sp_b + EPS), 5)
    np.testing.assert_allclose(apply_params(sp_a, p, partner=partner), np.exp(step), rtol=1e-9)


def test_TC_505_2_curveをformantより先にすると結果が変わる():
    sp_a, _ = _sps()
    c = random_curve()
    p = Params(formant=1.3, curve=c)
    step = apply_curve(np.log(sp_a + EPS), FREQ, c)
    step = shift_formant(step, 1.3)
    assert not np.allclose(apply_params(sp_a, p), np.exp(step), rtol=1e-6)


def test_TC_506_1_全フレームに同じゲイン(client, analyze, synth_spy):
    id_ = analyze().json()["id"]
    c = random_curve()
    synth(client, id_, omit=True)
    synth(client, id_, {"curve": c})
    base, curved = synth_spy
    d = 10 * np.log10(curved["sp"]) - 10 * np.log10(base["sp"])
    np.testing.assert_allclose(d, np.broadcast_to(reference_curve(FREQ, c), d.shape), atol=1e-6)


def test_TC_506_2_foとapは変わらない(client, analyze, synth_spy):
    id_ = analyze().json()["id"]
    synth(client, id_, omit=True)
    synth(client, id_, {"curve": random_curve()})
    base, curved = synth_spy
    np.testing.assert_array_equal(curved["f0"], base["f0"])
    np.testing.assert_array_equal(curved["ap"], base["ap"])
