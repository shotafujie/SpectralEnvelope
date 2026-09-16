"""テスト用の音声を生成する。マイク録音の代わりに、包絡が既知の合成母音を使う。"""

import io
import subprocess
import warnings

import numpy as np
import soundfile as sf

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

FS = 44100

VOWELS = {
    "a": [(800, 80), (1200, 90), (2500, 120)],
    "i": [(300, 60), (2300, 100), (3000, 120)],
}


def _envelope_db(f, formants):
    g = np.zeros_like(f)
    for fc, bw in formants:
        g += 1.0 / np.sqrt(1 + ((f - fc) / (bw / 2)) ** 2)
    return 20 * np.log10(g + 0.02) - 3 * np.log2(np.maximum(f, 50) / 500)


def vowel(name="a", dur=3.0, f0=120.0, fs=FS, seed=0):
    """倍音加算で作る母音。f0 は ±3% でゆっくり揺らす。"""
    rng = np.random.default_rng(seed)
    n = int(round(dur * fs))
    t = np.arange(n) / fs
    f0t = f0 * (1 + 0.03 * np.sin(2 * np.pi * 2 * t))
    phase = 2 * np.pi * np.cumsum(f0t) / fs
    y = np.zeros(n)
    for k in range(1, int(10000 / f0)):
        fk = k * f0t
        amp = 10 ** (_envelope_db(fk, VOWELS[name]) / 20) * (fk < fs / 2 - 500)
        y += amp * np.sin(k * phase + rng.uniform(0, 2 * np.pi))
    y += 1e-4 * rng.standard_normal(n)
    return 0.5 * y / np.max(np.abs(y))


def with_silence(x, pad=0.5, fs=FS):
    z = np.zeros(int(pad * fs))
    return np.concatenate([z, x, z])


def wav_bytes(x, fs=FS, subtype="PCM_16"):
    buf = io.BytesIO()
    sf.write(buf, x, fs, format="WAV", subtype=subtype)
    return buf.getvalue()


def webm_bytes(x, fs=FS):
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "wav", "-i", "pipe:0",
         "-c:a", "libopus", "-b:a", "128k", "-f", "webm", "pipe:1"],
        input=wav_bytes(x, fs), capture_output=True, check=True,
    )
    return proc.stdout


def read_wav(data):
    info = sf.info(io.BytesIO(data))
    y, fs = sf.read(io.BytesIO(data), dtype="float64")
    return y, fs, info


def peak_freq(db, freq, lo=50.0, hi=8000.0):
    band = (freq >= lo) & (freq <= hi)
    return float(freq[band][np.argmax(np.asarray(db)[band])])
