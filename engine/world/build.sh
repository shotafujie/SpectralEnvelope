#!/bin/sh
# WORLD を WASM にビルドする（ADR-0002）。
# 使い方: engine/world/build.sh [出力先ディレクトリ（省略時は engine/world）]
#
# ビルドの入力（イメージ、オプション、コンテナ内のパス）はすべてこのファイルで固定する。
# イメージは linux/arm64 のダイジェストで指定し、タグでは指定しない。
set -eu

IMAGE="emscripten/emsdk@sha256:41039722671531506a7d081828721e9ccde93125d91f88351e0fe4301606c7d4"

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$(mkdir -p "${1:-$ROOT/engine/world}" && cd "${1:-$ROOT/engine/world}" && pwd)

SOURCES="third_party/world/src/cheaptrick.cpp third_party/world/src/common.cpp
  third_party/world/src/d4c.cpp third_party/world/src/fft.cpp third_party/world/src/harvest.cpp
  third_party/world/src/matlabfunctions.cpp third_party/world/src/synthesis.cpp
  engine/world/wrapper.cpp"

EXPORTS="_malloc,_free,_world_n_frames,_world_harvest,_world_cheaptrick,_world_d4c,_world_synthesize"

# shellcheck disable=SC2086
docker run --rm --platform linux/arm64 \
  -v "$ROOT":/src:ro -v "$OUT":/out -w /src -u "$(id -u):$(id -g)" \
  "$IMAGE" \
  em++ -O3 -I third_party/world/src $SOURCES -o /out/world.mjs \
    -sMODULARIZE -sEXPORT_ES6 -sALLOW_MEMORY_GROWTH -sENVIRONMENT=web,worker,node \
    -sEXPORTED_RUNTIME_METHODS=HEAPF64,HEAPU8 \
    -sEXPORTED_FUNCTIONS="$EXPORTS"
