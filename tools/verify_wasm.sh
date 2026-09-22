#!/bin/sh
# 成果物の照合（009-pages-deploy / ADR-0002 の決定 4）。
# コミット済みの world.wasm / world.mjs / stamp.mjs が、ソースから作られたものかを確かめる。
#
# 使い方:
#   tools/verify_wasm.sh                # 再ビルドしてから比べる（Docker が要る）
#   tools/verify_wasm.sh --built DIR    # DIR を再ビルドの出力として比べる（Docker は要らない）
#
# 検査は 2 つ。
#   1. 再ビルドの出力 3 ファイルが、コミット済みのものとバイト単位で一致する
#   2. コミット済みのスタンプの SHA-256 が、コミット済みの成果物の SHA-256 と一致する
# 終了コード: 一致すれば 0 / 1 つでも違えば 1
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
COMMITTED="$ROOT/engine/world"
FILES="world.wasm world.mjs stamp.mjs"
BUILT=""
TMP=""

if [ "${1:-}" = "--built" ]; then
    [ $# -ge 2 ] || { echo "verify_wasm: --built には出力先ディレクトリが要ります" >&2; exit 2; }
    BUILT=$(cd "$2" && pwd)
elif [ $# -gt 0 ]; then
    echo "usage: verify_wasm.sh [--built DIR]" >&2
    exit 2
else
    TMP=$(mktemp -d)
    trap 'rm -rf "$TMP"' EXIT
    "$ROOT/engine/world/build.sh" "$TMP" >/dev/null
    BUILT="$TMP"
fi

sha() { shasum -a 256 "$1" | cut -d' ' -f1; }

failed=0

# 1. 再ビルドの出力とコミット済みの比較
for name in $FILES; do
    if [ ! -f "$BUILT/$name" ]; then
        echo "verify_wasm: 再ビルドの出力に $name がありません" >&2
        failed=1
    elif ! cmp -s "$BUILT/$name" "$COMMITTED/$name"; then
        echo "verify_wasm: $name がコミット済みのものと一致しません" >&2
        echo "  再ビルド: $(sha "$BUILT/$name")" >&2
        echo "  コミット: $(sha "$COMMITTED/$name")" >&2
        failed=1
    fi
done

# 2. コミット済みのスタンプと成果物の突き合わせ
for name in world.wasm world.mjs; do
    actual=$(sha "$COMMITTED/$name")
    if ! grep -q "\"$actual\"" "$COMMITTED/stamp.mjs"; then
        echo "verify_wasm: stamp.mjs に $name の SHA-256（$actual）がありません" >&2
        failed=1
    fi
done

if [ "$failed" -ne 0 ]; then
    echo "verify_wasm: 照合に失敗しました。engine/world/build.sh で再ビルドし、成果物を同じコミットに含めてください" >&2
    exit 1
fi

echo "verify_wasm: 照合に成功しました（world.wasm $(sha "$COMMITTED/world.wasm" | cut -c1-12)…）"
