"""WORLD エンジンの照合用データを生成する（006-wasm-world）。

pyworld 0.3.5（v0.1.0 が使っているもの）で、合成母音 /a/ 1 秒を分解・再合成した結果を書き出す。
JS のエンジンのテストはこのファイルだけを読み、Python は使わない（ADR-0001 決定 4）。

使い方: .venv/bin/python tools/make_golden_world.py [出力先ディレクトリ（省略時は tests/golden）]
"""

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

import numpy as np  # noqa: E402
import pyworld  # noqa: E402
import scipy  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests import audio_fixtures as af  # noqa: E402

FS = 44100
FFT_SIZE = 2048
FRAME_PERIOD = 5.0


def write(path, a):
    np.ascontiguousarray(a, dtype="<f8").tofile(path)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    x = af.vowel("a", dur=1.0)
    f0, t = pyworld.harvest(x, FS, frame_period=FRAME_PERIOD)
    sp = pyworld.cheaptrick(x, f0, t, FS, fft_size=FFT_SIZE)
    ap = pyworld.d4c(x, f0, t, FS, fft_size=FFT_SIZE)
    y = pyworld.synthesize(f0, sp, ap, FS, FRAME_PERIOD)[: len(x)]
    arrays = {"x": x, "f0": f0, "t": t, "sp": sp, "ap": ap, "y": y}
    for name, a in arrays.items():
        write(out / f"world-a-1s.{name}.f64", a)
    # 3 秒と 10 秒はテスト入力だけ（分解結果は照合しない。データが大きくなるため）
    write(out / "vowel-a-3s.f64", af.vowel("a", dur=3.0))
    write(out / "vowel-a-10s.f64", af.vowel("a", dur=10.0))
    meta = {
        "source": 'tests/audio_fixtures.py の vowel("a", dur=...)',
        "analysis": {"fs": FS, "fft_size": FFT_SIZE, "frame_period": FRAME_PERIOD,
                     "harvest": "pyworld.harvest(x, fs, frame_period)",
                     "y": "pyworld.synthesize(f0, sp, ap, fs, frame_period)[: len(x)]"},
        "format": "リトルエンディアンの Float64。2 次元は行優先",
        "shapes": {f"world-a-1s.{k}.f64": list(a.shape) for k, a in arrays.items()}
        | {"vowel-a-3s.f64": [3 * FS], "vowel-a-10s.f64": [10 * FS]},
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__, "pyworld": pyworld.__version__},
    }
    (out / "world-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tests" / "golden")
