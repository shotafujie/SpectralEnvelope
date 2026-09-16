"""sp 加工・パラメータ解釈・WAV 化のユニットテスト（テストダブルなし）。"""

import io

import numpy as np
import pytest
import soundfile as sf
from pydantic import ValidationError
from scipy.fft import dct, idct

from jig.server import (
    Params,
    apply_bands,
    apply_params,
    apply_tilt,
    band_gain_db,
    freq_axis,
    shift_formant,
    smooth_envelope,
    to_wav_bytes,
)

F = 1025
FREQ = freq_axis()
LN10_10 = np.log(10) / 10


def ramp():
    return np.arange(F, dtype=float)[None, :]


def rand_log_sp(rows=3, seed=1):
    return np.random.default_rng(seed).normal(-5, 2, size=(rows, F))


def db_delta(before, after):
    return (after - before) / LN10_10


# ---------------------------------------------------------------- パラメータ


def test_TC_050_2_空のパラメータは初期値になる():
    p = Params.model_validate({})
    assert (p.formant, p.tilt, p.bands, p.smooth, p.pitch) == (1.0, 0.0, [0.0] * 4, 0, 1.0)


@pytest.mark.parametrize(("given", "expected"), [(5.0, 1.6), (0.1, 0.6), (1.6, 1.6)])
def test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ(given, expected):
    assert Params(formant=given).formant == pytest.approx(expected)


@pytest.mark.parametrize(("given", "expected"), [(100, 12.0), (-13, -12.0)])
def test_TC_052_1_TC_052_2_tiltのクランプ(given, expected):
    assert Params(tilt=given).tilt == expected


def test_TC_053_1_bandsの各要素がクランプされる():
    assert Params(bands=[20, -20, 12, -12]).bands == [12, -12, 12, -12]


@pytest.mark.parametrize(("given", "expected"), [(3.0, 2.0), (0.1, 0.5)])
def test_TC_054_1_TC_054_2_pitchのクランプ(given, expected):
    assert Params(pitch=given).pitch == expected


def test_TC_055_1_smoothの丸め():
    cases = {-5: 0, 0: 0, 1: 10, 9: 10, 10: 10, 16.4: 16, 80: 80, 81: 80, 200: 80}
    assert {k: Params(smooth=k).smooth for k in cases} == cases


@pytest.mark.parametrize("bands", [[0, 0, 0], ["a", 0, 0, 0]])
def test_TC_056_3_bands形式不正はバリデーションエラー(bands):
    with pytest.raises(ValidationError):
        Params(bands=bands)


# ---------------------------------------------------------------- formant


def test_TC_060_1_r2でビンkはk半分の位置の値になる():
    out = shift_formant(ramp(), 2.0)
    np.testing.assert_allclose(out[0], np.arange(F) / 2)


def test_TC_060_2_r1_25で線形補間される():
    x = rand_log_sp(1)
    out = shift_formant(x, 1.25)
    assert out[0, 10] == pytest.approx(x[0, 8])
    # 11 / 1.25 = 8.8 → ビン8 と ビン9 を 0.2 : 0.8 で混ぜる（ビン8側の重みが 0.2）
    assert out[0, 11] == pytest.approx(0.2 * x[0, 8] + 0.8 * x[0, 9])


def test_TC_060_3_r1は恒等():
    x = rand_log_sp()
    np.testing.assert_array_equal(shift_formant(x, 1.0), x)


def test_TC_061_1_範囲外は最終ビンの値():
    out = shift_formant(ramp(), 0.6)
    assert np.all(out[0, 615:] == 1024)
    assert out[0, 614] < 1024


# ---------------------------------------------------------------- smooth


def test_TC_070_1_DCTの低次だけ残す():
    x = rand_log_sp()
    c = dct(x, type=2, norm="ortho", axis=1)
    c[:, 20:] = 0
    expected = idct(c, type=2, norm="ortho", axis=1)
    np.testing.assert_allclose(smooth_envelope(x, 20), expected, atol=1e-9)


def test_TC_070_2_低次成分だけの行は変化しない():
    c = np.zeros((1, F))
    c[0, :10] = np.arange(1, 11)
    x = idct(c, type=2, norm="ortho", axis=1)
    np.testing.assert_allclose(smooth_envelope(x, 10), x, atol=1e-9)


def test_TC_071_1_smooth0は恒等():
    x = rand_log_sp()
    np.testing.assert_array_equal(smooth_envelope(x, 0), x)


# ---------------------------------------------------------------- tilt


def test_TC_080_1_tilt6の加算量():
    x = rand_log_sp(1)
    d = db_delta(x, apply_tilt(x, FREQ, 6.0))[0]
    np.testing.assert_allclose(d, 6.0 * np.log2(np.maximum(FREQ, 20) / 1000), atol=1e-6)
    for f, g in [(1000, 0.0), (2000, 6.0), (500, -6.0)]:
        k = int(np.argmin(np.abs(FREQ - f)))
        assert d[k] == pytest.approx(g, abs=0.1)


def test_TC_080_2_0Hzは20Hzとして扱う():
    x = rand_log_sp(1)
    d = db_delta(x, apply_tilt(x, FREQ, -12.0))[0]
    assert d[0] == pytest.approx(-12.0 * np.log2(20 / 1000))


# ---------------------------------------------------------------- bands


def reference_gain(f, bands):
    """SPEC-091/092 の式をテスト側で独立に書いたもの。"""
    g = np.empty_like(f)
    edges = [500.0, 1500.0, 4000.0]
    for i, fv in enumerate(f):
        idx = sum(fv >= e for e in edges)
        val = bands[idx]
        for j, fb in enumerate(edges):
            lo, hi = fb * 2 ** (-1 / 3), fb * 2 ** (1 / 3)
            if lo < fv < hi:
                w = (1 - np.cos(np.pi * (np.log2(fv / fb) + 1 / 3) / (2 / 3))) / 2
                val = bands[j] + (bands[j + 1] - bands[j]) * w
        g[i] = val
    return g


def test_TC_090_1_バンドゲインはゲインカーブどおり加算される():
    x = rand_log_sp(2)
    bands = [3, -3, 6, -6]
    d = db_delta(x, apply_bands(x, FREQ, bands))
    ref = reference_gain(FREQ, bands)
    np.testing.assert_allclose(d, np.broadcast_to(ref, d.shape), atol=1e-6)


def test_TC_091_1_平坦区間の代表点():
    g = band_gain_db(FREQ, [1, 2, 3, 4])
    for f, v in [(100, 1), (1000, 2), (2500, 3), (10000, 4)]:
        assert g[np.argmin(np.abs(FREQ - f))] == pytest.approx(v)


def test_TC_091_2_両端の平坦区間():
    g = band_gain_db(FREQ, [1, 2, 3, 4])
    assert np.all(g[FREQ <= 500 * 2 ** (-1 / 3)] == 1)
    assert np.all(g[FREQ >= 4000 * 2 ** (1 / 3)] == 4)


def test_TC_092_1_500Hz境界のクロスフェード():
    bands = [0, 12, 0, 0]
    g = band_gain_db(FREQ, bands)
    region = (FREQ > 500 * 2 ** (-1 / 3)) & (FREQ < 500 * 2 ** (1 / 3))
    np.testing.assert_allclose(g[region], reference_gain(FREQ[region], bands), atol=1e-9)
    assert np.all(np.diff(g[region]) > 0)
    k = int(np.argmin(np.abs(FREQ - 500)))
    assert g[k] == pytest.approx(6.0, abs=0.6)


def test_TC_092_2_4000Hz境界に段差が無い():
    bands = [0, 0, 0, 12]
    g = band_gain_db(FREQ, bands)
    k = int(np.argmin(np.abs(FREQ - 4000)))
    assert g[k] == pytest.approx(reference_gain(FREQ[k : k + 1], bands)[0], abs=1e-9)
    assert np.max(np.abs(np.diff(g))) < 12


# ---------------------------------------------------------------- 順序


def test_TC_110_1_一括適用は定められた順序の逐次適用と一致する():
    x = rand_log_sp()
    sp = np.exp(x)
    p = Params(formant=1.3, smooth=20, tilt=4, bands=[3, -2, 5, -6])
    step = shift_formant(np.log(sp + 1e-12), 1.3)
    step = smooth_envelope(step, 20)
    step = apply_tilt(step, FREQ, 4)
    step = apply_bands(step, FREQ, [3, -2, 5, -6])
    np.testing.assert_allclose(apply_params(sp, p), np.exp(step), rtol=1e-9)


def test_TC_110_2_順序を変えると結果が変わる():
    x = rand_log_sp()
    sp = np.exp(x)
    p = Params(formant=1.3, smooth=20, tilt=4, bands=[3, -2, 5, -6])
    step = smooth_envelope(np.log(sp + 1e-12), 20)
    step = apply_tilt(step, FREQ, 4)
    step = apply_bands(step, FREQ, [3, -2, 5, -6])
    step = shift_formant(step, 1.3)
    assert not np.allclose(apply_params(sp, p), np.exp(step), rtol=1e-6)


# ---------------------------------------------------------------- WAV 化


def read_int16(data):
    y, fs = sf.read(io.BytesIO(data), dtype="int16")
    return y, fs


def test_TC_034_1_振幅超過は飽和する():
    y, fs = read_int16(to_wav_bytes(np.array([1.5, -1.5, 0.5])))
    assert fs == 44100
    assert y[0] == 32767 and y[1] == -32767
    assert abs(int(y[2]) - 16384) <= 1


def test_TC_034_2_フルスケールで符号が反転しない():
    y, _ = read_int16(to_wav_bytes(np.array([1.0, -1.0])))
    assert list(y) == [32767, -32767]
