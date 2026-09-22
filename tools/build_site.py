"""配信物を組み立てる（009-pages-deploy / SPEC-1123〜1127、1130）。

使い方:
    .venv/bin/python tools/build_site.py [出力先（省略時は _site）]

ワークフローも手元もこのスクリプトを呼ぶ。`app/` と `engine/` は書き換えずにコピーする
（配信されているものが、リポジトリのものと同じだと言えるようにするため）。
そのためルートの index.html は「app/ へ送るだけ」の別ファイルにする。
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 配信するファイル。engine/ のビルド用ファイル（build.sh、wrapper.cpp）は含めない
COPY = [
    "app/index.html",
    "app/app.js",
    "engine/adapter.mjs",
    "engine/decode.mjs",
    "engine/errors.mjs",
    "engine/render.mjs",
    "engine/store.mjs",
    "engine/worker.mjs",
    "engine/world-engine.mjs",
    "engine/dsp/curves.mjs",
    "engine/dsp/envelope.mjs",
    "engine/dsp/params.mjs",
    "engine/dsp/smooth.mjs",
    "engine/world/stamp.mjs",
    "engine/world/world.mjs",
    "engine/world/world.wasm",
    "third_party/world/LICENSE.txt",
]

INDEX = """<!doctype html>
<html lang="ja">
<meta charset="utf-8">
<title>包絡いじり</title>
<meta http-equiv="refresh" content="0; url=app/">
<link rel="canonical" href="app/">
<p><a href="app/">包絡いじりを開く</a></p>
"""


def build(out: Path) -> Path:
    if out.exists():
        shutil.rmtree(out)
    for rel in COPY:
        src = ROOT / rel
        if not src.is_file():
            raise SystemExit(f"build_site: {rel} がありません")
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (out / "index.html").write_text(INDEX, encoding="utf-8")
    return out


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    build(out.resolve())
    print(f"build_site: {out} に {len(COPY) + 1} ファイルを置きました")


if __name__ == "__main__":
    main()
