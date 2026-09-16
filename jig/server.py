"""スペクトル包絡いじり治具のサーバー。API とすべての DSP 処理をこのファイルに置く。

仕様: docs/items/001-envelope-jig/spec.md
"""

import io
import warnings

import numpy as np
import soundfile as sf
from pydantic import BaseModel, Field, field_validator
from scipy.fft import dct, idct

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

FS = 44100
FFT_SIZE = 2048
FRAME_PERIOD = 5.0
EPS = 1e-12
DB_TO_LN = np.log(10) / 10  # dB 表示値（10·log10 sp）を log_sp の単位へ
BAND_EDGES = (500.0, 1500.0, 4000.0)
CROSSFADE_OCT = 1 / 3


def _clamp(v, lo, hi):
    return float(min(max(v, lo), hi))


class Params(BaseModel):
    formant: float = 1.0
    tilt: float = 0.0
    bands: list[float] = Field(default_factory=lambda: [0.0] * 4, min_length=4, max_length=4)
    smooth: float = 0
    pitch: float = 1.0

    @field_validator("formant")
    @classmethod
    def _formant(cls, v):
        return _clamp(v, 0.6, 1.6)

    @field_validator("tilt")
    @classmethod
    def _tilt(cls, v):
        return _clamp(v, -12.0, 12.0)

    @field_validator("bands")
    @classmethod
    def _bands(cls, v):
        return [_clamp(b, -12.0, 12.0) for b in v]

    @field_validator("pitch")
    @classmethod
    def _pitch(cls, v):
        return _clamp(v, 0.5, 2.0)

    @field_validator("smooth")
    @classmethod
    def _smooth(cls, v):
        n = int(round(v))
        if n <= 0:
            return 0
        return min(max(n, 10), 80)


def freq_axis(fs=FS, fft_size=FFT_SIZE):
    return np.arange(fft_size // 2 + 1) * fs / fft_size


# ---------------------------------------------------------------- 包絡の加工（log_sp 上）


def shift_formant(log_sp, r):
    if r == 1.0:
        return log_sp
    bins = np.arange(log_sp.shape[1])
    src = bins / r
    return np.stack([np.interp(src, bins, row) for row in log_sp])


def smooth_envelope(log_sp, n):
    if n <= 0:
        return log_sp
    c = dct(log_sp, type=2, norm="ortho", axis=1)
    c[:, n:] = 0
    return idct(c, type=2, norm="ortho", axis=1)


def apply_tilt(log_sp, freq, tilt):
    gain_db = tilt * np.log2(np.maximum(freq, 20.0) / 1000.0)
    return log_sp + gain_db * DB_TO_LN


def band_gain_db(freq, bands):
    g = np.asarray(bands, dtype=float)[np.searchsorted(BAND_EDGES, freq, side="right")]
    for i, fb in enumerate(BAND_EDGES):
        x = np.log2(np.maximum(freq, 1e-9) / fb)
        inside = np.abs(x) < CROSSFADE_OCT
        w = (1 - np.cos(np.pi * (x[inside] + CROSSFADE_OCT) / (2 * CROSSFADE_OCT))) / 2
        g[inside] = bands[i] + (bands[i + 1] - bands[i]) * w
    return g


def apply_bands(log_sp, freq, bands):
    return log_sp + band_gain_db(freq, bands) * DB_TO_LN


def apply_params(sp, params, fs=FS):
    """SPEC-110: formant → smooth → tilt → bands の固定順で sp を加工する。"""
    freq = freq_axis(fs, (sp.shape[1] - 1) * 2)
    log_sp = np.log(sp + EPS)
    log_sp = shift_formant(log_sp, params.formant)
    log_sp = smooth_envelope(log_sp, params.smooth)
    log_sp = apply_tilt(log_sp, freq, params.tilt)
    log_sp = apply_bands(log_sp, freq, params.bands)
    return np.exp(log_sp)


def to_db(sp):
    return 10 * np.log10(sp + EPS)


# ---------------------------------------------------------------- 音声入出力


def to_wav_bytes(x, fs=FS):
    pcm = np.round(np.clip(x, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    sf.write(buf, pcm, fs, format="WAV", subtype="PCM_16")
    return buf.getvalue()
