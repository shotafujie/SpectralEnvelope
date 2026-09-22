"""照合と配信物の組み立て（009-pages-deploy）。"""

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools/verify_wasm.sh"
BUILD = ROOT / "engine/world/build.sh"
WORLD = ROOT / "engine/world"


def run(args, **kw):
    return subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True, text=True, **kw)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture
def built_copy(tmp_path):
    """再ビルドの出力に見立てたコピー（コミット済みの成果物は触らない）。"""
    dst = tmp_path / "built"
    dst.mkdir()
    for name in ("world.wasm", "world.mjs", "stamp.mjs"):
        shutil.copy2(WORLD / name, dst / name)
    return dst


# ---------------------------------------------------------------- 照合

def test_TC_1100_1_照合スクリプトがあり実行できる():
    assert VERIFY.exists()
    assert os.access(VERIFY, os.X_OK)


def test_TC_1101_2_照合とビルドが同じイメージを指している():
    digests = {p: set(re.findall(r"emscripten/emsdk@sha256:[0-9a-f]{64}", p.read_text()))
               for p in (VERIFY, BUILD)}
    assert digests[BUILD], "build.sh にイメージのダイジェストが無い"
    # 照合スクリプトは build.sh を呼ぶか、同じダイジェストを自分で持つ
    assert digests[VERIFY] <= digests[BUILD]
    assert digests[VERIFY] or "build.sh" in VERIFY.read_text()


def test_TC_1101_1_再ビルドしてコミット済みと一致する():
    r = run([VERIFY])
    assert r.returncode == 0, r.stdout + r.stderr


def test_TC_1102_1_一致すれば成功する(built_copy):
    r = run([VERIFY, "--built", built_copy])
    assert r.returncode == 0, r.stdout + r.stderr


def test_TC_1103_1_wasmが違えば失敗する(built_copy):
    data = bytearray((built_copy / "world.wasm").read_bytes())
    data[-1] ^= 0xFF
    (built_copy / "world.wasm").write_bytes(bytes(data))
    r = run([VERIFY, "--built", built_copy])
    assert r.returncode != 0
    assert "world.wasm" in r.stdout + r.stderr


def test_TC_1103_2_glueが違えば失敗する(built_copy):
    (built_copy / "world.mjs").write_text((built_copy / "world.mjs").read_text() + "\n// 余計な行\n")
    r = run([VERIFY, "--built", built_copy])
    assert r.returncode != 0
    assert "world.mjs" in r.stdout + r.stderr


def test_TC_1104_1_スタンプが食い違えば失敗する(built_copy):
    text = (built_copy / "stamp.mjs").read_text()
    (built_copy / "stamp.mjs").write_text(re.sub(r'"[0-9a-f]{64}"', '"' + "0" * 64 + '"', text, count=1))
    r = run([VERIFY, "--built", built_copy])
    assert r.returncode != 0


# ---------------------------------------------------------------- スタンプ

def test_TC_1143_1_buildがスタンプを書き出す(tmp_path):
    out = tmp_path / "out"
    r = run([BUILD, out])
    assert r.returncode == 0, r.stdout + r.stderr
    stamp = (out / "stamp.mjs").read_text()
    assert sha256(out / "world.wasm") in stamp
    assert sha256(out / "world.mjs") in stamp
