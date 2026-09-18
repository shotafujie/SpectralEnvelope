"""WORLD の照合用データ（tests/golden/）の再現性とメタデータ（006-wasm-world）。"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"
SCRIPT = ROOT / "tools" / "make_golden_world.py"


def digests(d):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir()) if p.is_file()}


def test_TC_750_1_生成スクリプトの出力はコミット済みの照合用データと同一(tmp_path):
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, cwd=ROOT)
    committed = {k: v for k, v in digests(GOLDEN).items()}
    assert committed, "tests/golden が空"
    assert digests(tmp_path) == committed


def meta():
    return json.loads((GOLDEN / "world-meta.json").read_text())


def test_TC_751_1_生成に使ったライブラリのバージョンが記録されている():
    versions = meta()["versions"]
    for k in ("numpy", "scipy", "pyworld"):
        assert isinstance(versions[k], str) and versions[k]


def test_TC_751_2_pyworld_のバージョンは_0_3_5():
    assert meta()["versions"]["pyworld"] == "0.3.5"
