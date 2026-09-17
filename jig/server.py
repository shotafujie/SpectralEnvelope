"""スペクトル包絡いじり治具のサーバー。API とすべての DSP 処理をこのファイルに置く。

仕様: docs/items/001-envelope-jig/spec.md
"""

import argparse
import io
import secrets
import subprocess
import threading
import warnings
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field, field_validator
from scipy.fft import dct, idct

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
import pyworld  # noqa: E402  (上の警告抑止を先に効かせる)

HOST = "127.0.0.1"
INDEX_HTML = Path(__file__).with_name("index.html")
MIN_SAMPLES = 44100  # 1.0 秒
MAX_SAMPLES = 441000  # 10.0 秒
MAX_ENTRIES = 10

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


class AudioDecodeError(Exception):
    pass


def decode_audio(data):
    """任意の音声バイト列を 44100Hz・モノラル・16bit にして [-1, 1) の float で返す。"""
    if not data:
        raise AudioDecodeError("音声データが空です")
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
         "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", str(FS), "pipe:1"],
        input=data, capture_output=True,
    )
    if proc.returncode != 0 or not proc.stdout:
        raise AudioDecodeError("音声としてデコードできませんでした")
    pcm = np.frombuffer(proc.stdout, dtype="<i2")
    return pcm.astype(np.float64) / 32768.0


# ---------------------------------------------------------------- 分解結果の保持


@dataclass
class Analysis:
    f0: np.ndarray
    sp: np.ndarray
    ap: np.ndarray
    original_wav: bytes
    n_samples: int


class Store:
    def __init__(self, limit=MAX_ENTRIES):
        self._limit = limit
        self._items: OrderedDict[str, Analysis] = OrderedDict()
        self._lock = threading.Lock()

    def add(self, item):
        with self._lock:
            id_ = secrets.token_hex(4)
            while id_ in self._items:
                id_ = secrets.token_hex(4)
            self._items[id_] = item
            while len(self._items) > self._limit:
                self._items.popitem(last=False)
            return id_

    def get(self, id_):
        with self._lock:
            item = self._items.get(id_)
        if item is None:
            raise HTTPException(404, f"id {id_} は保持されていません。録音し直してください")
        return item


def analyze_signal(x):
    f0, t = pyworld.harvest(x, FS, frame_period=FRAME_PERIOD)
    sp = pyworld.cheaptrick(x, f0, t, FS, fft_size=FFT_SIZE)
    ap = pyworld.d4c(x, f0, t, FS, fft_size=FFT_SIZE)
    return f0, sp, ap


def synthesize(item, params):
    sp = apply_params(item.sp, params)
    f0 = item.f0 * params.pitch
    y = pyworld.synthesize(f0, sp, item.ap, FS, FRAME_PERIOD)[: item.n_samples]
    if len(y) < item.n_samples:
        y = np.pad(y, (0, item.n_samples - len(y)))
    return y


# ---------------------------------------------------------------- API


class SynthesizeRequest(BaseModel):
    id: str
    params: Params | None = None


class EnvelopeRequest(BaseModel):
    id: str
    frame: int
    params: Params | None = None


def wav_response(data):
    return Response(content=data, media_type="audio/wav")


def create_app():
    app = FastAPI(title="spectral envelope jig")
    store = Store()

    @app.get("/")
    def index():
        return FileResponse(INDEX_HTML, media_type="text/html")

    @app.post("/api/analyze")
    def analyze(audio: UploadFile = File(...)):
        try:
            x = decode_audio(audio.file.read())
        except AudioDecodeError as e:
            raise HTTPException(400, str(e)) from e
        if len(x) < MIN_SAMPLES:
            raise HTTPException(400, f"録音が短すぎます（{len(x) / FS:.2f} 秒）。1 秒以上録音してください")
        x = x[:MAX_SAMPLES]
        f0, sp, ap = analyze_signal(x)
        item = Analysis(f0=f0, sp=sp, ap=ap, original_wav=to_wav_bytes(x), n_samples=len(x))
        id_ = store.add(item)
        voiced = np.flatnonzero(f0 > 0)
        return {
            "id": id_,
            "fs": FS,
            "duration": len(x) / FS,
            "frames": int(len(f0)),
            "fft_size": FFT_SIZE,
            "f0_mean": float(f0[voiced].mean()) if len(voiced) else 0.0,
            "voiced_frames": voiced.tolist(),
        }

    @app.post("/api/synthesize")
    def synthesize_endpoint(req: SynthesizeRequest):
        item = store.get(req.id)
        return wav_response(to_wav_bytes(synthesize(item, req.params or Params())))

    @app.post("/api/envelope")
    def envelope(req: EnvelopeRequest):
        item = store.get(req.id)
        if not 0 <= req.frame < len(item.f0):
            raise HTTPException(400, f"frame は 0〜{len(item.f0) - 1} の範囲で指定してください")
        row = item.sp[req.frame : req.frame + 1]
        modified = apply_params(row, req.params or Params())
        return {
            "freq": freq_axis().tolist(),
            "original_db": to_db(row[0]).tolist(),
            "modified_db": (10 * np.log10(modified[0])).tolist(),
        }

    @app.get("/api/original/{id_}")
    def original(id_: str):
        return wav_response(store.get(id_).original_wav)

    return app


app = create_app()


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="スペクトル包絡いじり治具")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    print(f"http://localhost:{args.port}/ を開いてください")
    uvicorn.run(app, host=HOST, port=args.port)


if __name__ == "__main__":
    main()
