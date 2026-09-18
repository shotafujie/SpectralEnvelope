# Phase 0 スパイク: WORLD の WASM ビルドで C 案（全部ブラウザで動かす）が成立するか

実施日: 2026-09-18 / ブランチ: `feature/wasm-engine` / 前提: `docs/HANDOFF-wasm.md` の Phase 0

**結論: 3 指標とも合格の目安に収まった。C 案で進める。**

スパイクのコードは捨てた（スクラッチ領域に置いたのみ）。再現に必要な条件は下に残す。

## 条件

| 項目 | 値 |
|---|---|
| WORLD | 本家 `mmorise/World` `d625e76` を自前ビルド（World.JS は不使用） |
| ビルド | `emscripten/emsdk:latest`（emcc 6.0.9）を Docker 越しに実行。`em++ -O3`、`-sMODULARIZE -sEXPORT_ES6 -sALLOW_MEMORY_GROWTH -sENVIRONMENT=web,worker,node` |
| ビルド対象 | `cheaptrick` `common` `d4c` `fft` `harvest` `matlabfunctions` `synthesis` の .cpp と、HANDOFF 6 節の案どおりの薄い C ラッパー（`extern "C"`、sp / ap は平坦な Float64 配列で受け、行ポインタはラッパー内で組む） |
| 成果物サイズ | `world.wasm` 100KB、`world.mjs`（glue）8KB |
| 実行環境 | Node v22.22.3、Apple M4 Max |
| 入力 | `tests/audio_fixtures.py` の `vowel("a")`（3 秒、44.1kHz、132300 サンプル、601 フレーム） |
| 分析条件 | `jig/server.py` と同じ（frame_period 5.0ms、fft_size 2048、harvest の f0_floor 71） |
| 比較対象 | pyworld 0.3.5（ネイティブ）に同じ入力を与えた出力 |
| 計時 | 5 回実行した中央値 |

注意: 包絡差を測るときの再分解は `tests/test_api.py` の `reanalyze()` を使ったので pyworld で行っている。
WASM で分解した結果と pyworld で分解した結果が一致することは別途確かめている（下の表 2）。

## 結果

### 1. 速度

| 処理 | ネイティブ（pyworld） | WASM（Node） | 倍率 |
|---|---|---|---|
| 分解（合計） | 0.468 秒 | 0.725 秒 | 1.55 倍 |
| └ harvest | — | 0.350 秒 | |
| └ cheaptrick | — | 0.050 秒 | |
| └ d4c | — | 0.327 秒 | |
| 再合成 | 0.025 秒 | 0.041 秒 | 1.7 倍 |
| 初回呼び出しの分解（コールドスタート） | — | 0.70 秒 | |
| モジュールの初期化 | — | 1.2ms | |

目安（分解 2 秒未満）に対して **0.73 秒で合格**。ただし 0.7 秒ほど UI が止まるので、Worker に載せる方針は変えない。

### 2. WASM とネイティブの一致

| 出力 | 最大絶対誤差 | 最大相対誤差 |
|---|---|---|
| f0 | 5.7e-13 | 4.7e-15 |
| t | 0 | 0 |
| sp | 5.0e-14 | 1.1e-11（dB では 4.6e-11） |
| ap | 1.7e-12 | 1.1e-11 |
| y（再合成） | 1.2e-11 | — |

同じ WORLD のソースから作ったビルドなので、浮動小数点の丸め以外の差は出なかった。
**HANDOFF 5 節の「1e-6 以内で一致」というゴールデンテストは、WORLD 部分については余裕で成り立つ。**

### 3. 音質（無加工往復の包絡差。50〜8000Hz、有声フレームの平均）

| 経路 | 包絡差 |
|---|---|
| WASM（Float64） | 0.2499 dB |
| ネイティブ（Float64） | 0.2499 dB |
| WASM の sp / ap を Float32 に落として合成 | 0.2499 dB（y の差は最大 9.8e-9） |

目安（1.0dB 以下）に対して **0.25dB で合格**。Float32 に落としても、この指標では違いが出なかった。

### 4. メモリ（3 秒の録音 10 件の sp / ap を JS 側で保持した場合）

| 精度 | 10 件保持に使った ArrayBuffer | 保持後のプロセス RSS |
|---|---|---|
| Float64 | 94MB | 174MB |
| Float32 | 47MB | 127MB |

WASM のヒープは 1 件を作業中のとき 23MB。
目安（200MB 未満）に対して **Float64 のままでも合格**。

## Phase 1（ADR）への材料

| 決めること | スパイクで分かったこと |
|---|---|
| World.JS か自前ビルドか | 自前ビルドは C ラッパー約 40 行とビルドコマンド 1 本で動いた（詰まったのは `emcc` ではなく `em++` でリンクする必要があった点だけ）。ビルドの手間は小さい |
| 成果物のコミットか CI ビルドか | 成果物は合計約 108KB と小さい。Docker イメージ（3.35GB）が無いとビルドできない点をどう扱うかが論点になる |
| Float64 か Float32 か | 音質・メモリのどちらからも Float32 化は必須ではない。10 件保持で 94MB → 47MB に減る利点はある。ゴールデンデータとの 1e-6 一致を考えると、エンジン内部は Float64 のままにしておくほうが扱いやすい |
| Web Worker | 分解で 0.7 秒ブロックするので必要 |

## 未確認（このスパイクの範囲外）

- ブラウザ（Chrome / Safari / Firefox）での速度。Node と同じ V8 を使う Chrome は近い値になると予想するが、Safari（JavaScriptCore）は測っていない
- 長い録音（10 秒以上）での時間とメモリ。どちらもフレーム数にほぼ比例するはず
- 合成母音 `a` 以外の入力（実際の録音音声）
- DSP（formant / smooth / tilt / bands / curve / morph）の JS 移植の速度。WORLD の外側の処理なので、このスパイクでは扱っていない
