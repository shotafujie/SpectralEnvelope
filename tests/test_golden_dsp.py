"""DSP の照合用データ（tests/golden/dsp-*）の再現性とメタデータ（007-engine-dsp）。"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"
SCRIPT = ROOT / "tools" / "make_golden_dsp.py"


def digests(d):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir())
            if p.is_file() and p.name.startswith("dsp-")}


def test_TC_863_1_生成スクリプトの出力はコミット済みの照合用データと同一(tmp_path):
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, cwd=ROOT)
    committed = digests(GOLDEN)
    assert committed, "tests/golden に dsp-* が無い"
    assert digests(tmp_path) == committed


def meta():
    return json.loads((GOLDEN / "dsp-meta.json").read_text())


def test_TC_864_1_生成に使ったライブラリのバージョンが記録されている():
    versions = meta()["versions"]
    for k in ("numpy", "scipy", "pyworld"):
        assert isinstance(versions[k], str) and versions[k]
    assert versions["pyworld"] == "0.3.5"


def test_TC_864_2_7つのパラメータの組が記録されている():
    cases = meta()["cases"]
    assert len(cases) == 7
    assert set(cases) == {"default", "formant", "smooth", "tilt", "bands", "curve", "all"}
    assert cases["formant"]["formant"] != 1.0
    assert "morph" in cases["all"]
