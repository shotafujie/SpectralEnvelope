"""DSP の照合用データを生成する（007-engine-dsp）。

v0.1.0 の `jig/server.py` の関数（apply_params / stretch_partner / synthesize）を使い、
7 つのパラメータの組について、加工後の dB 列・再合成音・（"all" のみ）加工後の sp 全体を書き出す。
JS 側の移植は、このデータと 1e-6 以内で一致することをもって正しいとする（ADR-0001 決定 4）。

使い方: .venv/bin/python tools/make_golden_dsp.py [出力先ディレクトリ（省略時は tests/golden/dsp）]
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
from jig.server import DB_TO_LN, FS, Params, apply_params, stretch_partner  # noqa: E402

FRAMES = [0, 50, 100, 150, 200]  # dB 列を記録するフレーム
CURVE = [-3 + 0.3 * j for j in range(20)]
CASES = {
    "default": {},
    "formant": {"formant": 1.2},
    "smooth": {"smooth": 30},
    "tilt": {"tilt": 3.0},
    "bands": {"bands": [2.0, -2.0, 4.0, -4.0]},
    "curve": {"curve": CURVE},
    "all": {"formant": 1.2, "smooth": 30, "tilt": 3.0, "bands": [2.0, -2.0, 4.0, -4.0],
            "curve": CURVE, "pitch": 1.3, "morph": {"id": "partner", "ratio": 0.4}},
}


def write(path, a):
    np.ascontiguousarray(a, dtype="<f8").tofile(path)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    g = ROOT / "tests" / "golden"  # 入力は 006 の照合用データ
    read = lambda name, shape: np.fromfile(g / name, "<f8").reshape(shape)  # noqa: E731
    x = read("world-a-1s.x.f64", -1)
    f0 = read("world-a-1s.f0.f64", -1)
    sp = read("world-a-1s.sp.f64", (-1, 1025))
    ap = read("world-a-1s.ap.f64", (-1, 1025))
    partner_log = read("partner-i-1.5s.logsp.f64", (-1, 1025))

    for name, raw in CASES.items():
        params = Params(**raw)
        partner = None
        if params.morph is not None:
            partner = stretch_partner(partner_log, len(f0))
        modified = apply_params(sp, params, partner=partner)
        # 加工後の dB 列（modified_db と同じ換算: 1e-12 を足さない）
        write(out / f"dsp-{name}.db.f64", 10 * np.log10(modified[FRAMES]))
        y = pyworld.synthesize(f0 * params.pitch, modified, ap, FS, 5.0)[: len(x)]
        if len(y) < len(x):
            y = np.pad(y, (0, len(x) - len(y)))
        write(out / f"dsp-{name}.y.f64", y)
        if name == "all":
            write(out / "dsp-all.sp.f64", modified)

    meta = {
        "cases": CASES,
        "frames": FRAMES,
        "input": "world-a-1s.*（合成母音 /a/ 1 秒）。morph の相手は partner-i-1.5s.logsp.f64",
        "db": "10 · log10(sp)（1e-12 を足さない。/api/envelope の modified_db と同じ）",
        "source": "jig/server.py の apply_params / stretch_partner と pyworld.synthesize",
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__, "pyworld": pyworld.__version__},
    }
    (out / "dsp-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tests" / "golden" / "dsp")
