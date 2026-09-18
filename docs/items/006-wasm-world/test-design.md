# テスト設計書: WORLD の WASM エンジン（分解と再合成）

- アイテムID: `006-wasm-world`
- 仕様書: `docs/items/006-wasm-world/spec.md`
- 作成日: 2026-09-18

## テスト方針

| レベル | 対象 | 置き場所 | 実行コマンド |
|---|---|---|---|
| ユニット（エンジン） | 生成、分解、再合成、異常系、メモリ | `tests/js/world-engine.test.mjs` | `node --test 'tests/js/*.test.mjs'` |
| 統合（ビルド） | ソースの取り込み、ビルドスクリプト、成果物の再現 | `tests/js/world-build.test.mjs` | `node --test 'tests/js/*.test.mjs'` |
| 統合（照合用データ） | 生成スクリプトの再現性、バージョンの記録 | `tests/test_golden_world.py` | `.venv/bin/pytest tests/test_golden_world.py` |
| ブラウザ | Chromium のモジュール Worker からの読み込み | `tests/e2e/test_world_worker.py` | `.venv/bin/pytest tests/e2e/test_world_worker.py` |
| 性能 | 分解と再合成の時間、基準値のファイル | `tests/js/world-perf.test.mjs` | `node --test tests/js/world-perf.test.mjs` |

- **テストダブルは使わない。** エンジンは本物の WASM を読み込んで動かす。照合の基準は、コミット済みの照合用データ（pyworld 0.3.5 の出力）
- **照合用データの読み込み**は、テスト側の小さな読み込み関数で行う。エンジンの実装は使わない
- **包絡差**（SPEC-734）は、テスト側で独立に計算する。計算方法は 001 の `envelope_diff()` と同じ
- **入力の音声**:
  - 1 秒の入力は、照合用データの x を使う
  - 3 秒と 10 秒の入力は、`vowel("a", dur=3.0)` と `vowel("a", dur=10.0)` を Float64 のバイナリにしたもの。照合用データと同じ場所に、同じスクリプトで生成する
  - 3 秒と 10 秒の分解結果は pyworld と照合しない（データが大きくなるため）。長さと形だけを見る
- **Docker が要るテスト**（SPEC-704、705）: Docker が無い環境では失敗させ、スキップしない。独立検証では、その SPEC を BLOCKED として扱う
- **SPEC-704 の前提**: 判定できるのは linux/arm64 のマシン（Apple Silicon の Mac）だけ。それ以外のマシンでは失敗させる

## テストケース

### SPEC-700 `third_party/world/` に、WORLD の `src/` 以下のファイルと、WORLD のライセンス文（`LICENSE.txt`）がある

- **TC-700-1** `third_party/world/src/` に `harvest.cpp`、`cheaptrick.cpp`、`d4c.cpp`、`synthesis.cpp`、`common.cpp`、`fft.cpp`、`matlabfunctions.cpp` と、`world/` の下のヘッダがある
- **TC-700-2** `third_party/world/LICENSE.txt` があり、中身に著作権表示 "Copyright (c) 2010  M. Morise" と、再配布の条件（"Redistribution and use in source and binary forms"）を含む

### SPEC-701 `third_party/world/COMMIT` の内容は、40 桁のコミットハッシュ `d625e7608ca23a870018f01e7c562ac683d9847f` の 1 行である

- **TC-701-1** ファイルを読み、末尾の改行を除いた内容が `d625e7608ca23a870018f01e7c562ac683d9847f` と一致し、行数が 1 である

### SPEC-702 ビルドスクリプトが使う Docker イメージは、linux/arm64 のダイジェストで指定されている

- **TC-702-1** ビルドスクリプトの中に `emscripten/emsdk@sha256:41039722671531506a7d081828721e9ccde93125d91f88351e0fe4301606c7d4` が現れる

### SPEC-703 ビルドスクリプトには、タグだけで Docker イメージを指定している箇所が無い

- **TC-703-1** ビルドスクリプトに現れるすべての `emscripten/emsdk` について、直後の文字列が `@sha256:` で始まる（`:latest` や `:6.0.9` のようなタグ指定が 0 件）

### SPEC-704 linux/arm64 のマシンでビルドスクリプトを実行すると、コミット済みの成果物とバイト単位で同一のファイルが出力される

- **TC-704-1** 一時ディレクトリを出力先にしてビルドスクリプトを実行 → 出力された `world.wasm` と `world.mjs` の SHA-256 が、コミット済みのものと一致する

### SPEC-705 ビルドスクリプトを同じマシンで 2 回実行すると、2 回の出力はバイト単位で同一である

- **TC-705-1** 別々の一時ディレクトリに 2 回ビルド → 2 組の `world.wasm` と `world.mjs` の SHA-256 がそれぞれ一致する

### SPEC-710 `createEngine()` は Promise を返し、それはエンジンに解決される

- **TC-710-1** `createEngine()` の戻り値が Promise（`then` を持つ）で、解決値が `analyze` と `synthesize` の関数を持つ

### SPEC-711 エンジンの `fs` は 44100、`fftSize` は 2048、`framePeriod` は 5、`bins` は 1025 である

- **TC-711-1** 4 つのプロパティがそれぞれ 44100、2048、5、1025

### SPEC-712 エンジンの `minSamples` は 44100、`maxSamples` は 441000 である

- **TC-712-1** 2 つのプロパティがそれぞれ 44100、441000

### SPEC-713 エンジンのモジュールは Node 22 から import でき、`createEngine()` が解決される

- **TC-713-1** Node のテストからモジュールを動的 import し、`createEngine()` が 5 秒以内に解決される

### SPEC-714 エンジンのモジュールは、Chromium のモジュール Worker の中から import でき、`createEngine()` が解決される

- **TC-714-1** リポジトリを静的に配信し、Chromium でテスト用のページを開く。ページがモジュール Worker を起動し、Worker 内で import → `createEngine()` → 照合用データの x で `analyze` を実行する → Worker から返ってきた f0 が、照合用データの f0 と絶対差 1e-6 以内で一致する

### SPEC-720 `analyze(x)` は、Float64Array の x を受け取り、`{ f0, t, sp, ap }` を返す

- **TC-720-1** 照合用データの x で `analyze` → 戻り値が `f0`、`t`、`sp`、`ap` の 4 つのキーを持ち、どれも Float64Array

### SPEC-721 `f0` と `t` は長さ N の Float64Array である

- **TC-721-1** 照合用データの x（1 秒）→ `f0` と `t` の長さが、照合用データの f0 の長さ（201）と等しい
- **TC-721-2** 3 秒の入力 → `f0` と `t` の長さが 601
- **TC-721-3** 10 秒の入力 → `f0` と `t` の長さが 2001

### SPEC-722 `sp` と `ap` は、行優先の N×F の Float64Array である

- **TC-722-1** 照合用データの x → `sp` と `ap` の長さが 201 × 1025
- **TC-722-2** 照合用データの x → `sp` の添字 `i·1025 + k` の値の dB 値が、照合用データの sp の (i, k) の dB 値と一致する。i と k は、(0, 0)、(100, 512)、(200, 1024) の 3 点で確かめる（行と列の並びの確認）

### SPEC-723 照合用データの x を分解した `f0` は、照合用データの f0 と、全要素で絶対差 1e-6 以内で一致する

- **TC-723-1** 全要素の絶対差の最大値が 1e-6 以下
- **TC-723-2** f0 が 0（無声）の要素の位置が、照合用データと完全に一致する

### SPEC-724 照合用データの x を分解した `t` は、照合用データの t と、全要素で絶対差 1e-9 以内で一致する

- **TC-724-1** 全要素の絶対差の最大値が 1e-9 以下

### SPEC-725 照合用データの x を分解した `sp` の dB 値は、照合用データの sp の dB 値と、全要素で差 1e-6 dB 以内で一致する

- **TC-725-1** 全要素（201 × 1025）の dB 値の差の最大値が 1e-6 以下

### SPEC-726 照合用データの x を分解した `ap` は、照合用データの ap と、全要素で絶対差 1e-6 以内で一致する

- **TC-726-1** 全要素の絶対差の最大値が 1e-6 以下

### SPEC-727 `analyze` は、引数の x を書き換えない

- **TC-727-1** 照合用データの x を複製してから `analyze` に渡す → 呼び出し後の x が、複製と全要素で同一

### SPEC-730 `synthesize(f0, sp, ap, n)` は、長さ n の Float64Array を返す

- **TC-730-1** 照合用データの f0、sp、ap と n = 44100 → 長さ 44100 の Float64Array
- **TC-730-2** 同じ入力で n = 1 → 長さ 1
- **TC-730-3** 同じ入力で n = 50000（L = 44320 より長い）→ 長さ 50000

### SPEC-731 照合用データの f0、sp、ap と n = 44100 で再合成した結果は、照合用データの y と、全サンプルで絶対差 1e-6 以内で一致する

- **TC-731-1** 全サンプルの絶対差の最大値が 1e-6 以下

### SPEC-732 n が再合成の長さ L より長いとき、L を超えた部分のサンプルはすべて 0 である

- **TC-732-1** 照合用データの f0、sp、ap（N = 201、L = 44320）と n = 50000 → 添字 44320〜49999 がすべて 0
- **TC-732-2** 同じ入力で n = 50000 → 先頭 44100 サンプルが、照合用データの y と絶対差 1e-6 以内で一致する（長くしても前半は変わらない）

### SPEC-733 `synthesize` は、引数の f0、sp、ap を書き換えない

- **TC-733-1** 照合用データの f0、sp、ap を複製してから `synthesize` に渡す → 呼び出し後の 3 つが、それぞれの複製と全要素で同一

### SPEC-734 合成母音 /a/ 3 秒を分解して、加工せずに再合成した音をエンジンで再分解すると、元の sp との包絡差は 1.0dB 以下である

- **TC-734-1** 3 秒の入力を `analyze` → `synthesize`（n = 132300）→ `analyze` → 1 回目と 2 回目の sp の包絡差が 1.0dB 以下

### SPEC-740 x が Float64Array でないとき、`analyze` は TypeError を投げる

- **TC-740-1** 長さ 44100 の Float32Array → TypeError
- **TC-740-2** 長さ 44100 の通常の配列（`Array`）→ TypeError
- **TC-740-3** `undefined` → TypeError

### SPEC-741 x の長さが `minSamples` 未満のとき、`analyze` は RangeError を投げる

- **TC-741-1** 長さ 44099 → RangeError
- **TC-741-2** 長さ 0 → RangeError

### SPEC-742 x の長さが `maxSamples` を超えるとき、`analyze` は RangeError を投げる

- **TC-742-1** 長さ 441001 → RangeError

### SPEC-743 長さがちょうど `minSamples` の x と、ちょうど `maxSamples` の x は、どちらも `analyze` が例外を投げずに結果を返す

- **TC-743-1** 長さ 44100（照合用データの x）→ 例外なし、`f0` の長さ 201
- **TC-743-2** 長さ 441000（10 秒の入力）→ 例外なし、`f0` の長さ 2001

### SPEC-744 f0 の長さを N としたとき、sp か ap の長さが N·F でない場合、`synthesize` は RangeError を投げる

- **TC-744-1** 照合用データの sp の末尾 1 要素を削った配列を渡す → RangeError
- **TC-744-2** 照合用データの ap に 1 要素足した配列を渡す → RangeError

### SPEC-745 n が 1 未満の場合、または `maxSamples` を超える場合、`synthesize` は RangeError を投げる

- **TC-745-1** n = 0 → RangeError
- **TC-745-2** n = 441001 → RangeError
- **TC-745-3** n = 441000 → 例外なし、長さ 441000

### SPEC-746 例外を投げた後も、同じエンジンで `analyze` と `synthesize` を続けて呼ぶと、正常な結果を返す

- **TC-746-1** 長さ 0 の x で `analyze`（RangeError）→ 同じエンジンで照合用データの x を `analyze` → f0 が照合用データと 1e-6 以内で一致する
- **TC-746-2** 長さが合わない sp で `synthesize`（RangeError）→ 同じエンジンで照合用データを `synthesize` → y が照合用データと 1e-6 以内で一致する

### SPEC-747 10 秒の入力で `analyze` と `synthesize` を続けて 20 回呼んだ後の `memoryBytes` は、1 回目を終えた直後の `memoryBytes` と同じである

- **TC-747-1** 10 秒の入力で `analyze` → `synthesize`（n = 441000）を 1 回 → `memoryBytes` を記録 → さらに 19 回繰り返す → `memoryBytes` が記録した値と等しい

### SPEC-748 エンジンの `memoryBytes` は、そのエンジンが使っている WASM 線形メモリのバイト数で、65536 の正の倍数である

- **TC-748-1** 生成直後の `memoryBytes` が 65536 の正の倍数
- **TC-748-2** 10 秒の入力で `analyze` した後の `memoryBytes` が、生成直後より大きく、65536 の倍数（10 秒の分解で線形メモリが広がったことが観測できる）

### SPEC-750 照合用データの生成スクリプトを実行すると、コミット済みの照合用データとバイト単位で同一のファイルが出力される

- **TC-750-1** 一時ディレクトリを出力先にして生成スクリプトを実行 → 出力されたすべてのファイルの SHA-256 が、`tests/golden/` のコミット済みのファイルと一致し、ファイルの集合も一致する

### SPEC-751 照合用データには、生成に使った numpy、scipy、pyworld のバージョン文字列が記録されている

- **TC-751-1** 照合用データのメタデータに `numpy`、`scipy`、`pyworld` のキーがあり、値が空でない文字列
- **TC-751-2** `pyworld` の値が `0.3.5`

### SPEC-760 3 秒の入力に対する `analyze` の時間が 1.0 秒未満である

- **TC-760-1** 3 秒の入力で `analyze` を初回 1 回と、その後 5 回実行 → 後の 5 回の中央値が 1.0 秒未満

### SPEC-761 10 秒の入力に対する `analyze` の時間が 3.0 秒未満である

- **TC-761-1** 10 秒の入力で同様に計測 → 中央値が 3.0 秒未満

### SPEC-762 3 秒の入力に対する `synthesize` の時間が 0.1 秒未満である

- **TC-762-1** 3 秒の入力の分解結果で `synthesize`（n = 132300）を同様に計測 → 中央値が 0.1 秒未満

### SPEC-763 `benchmarks/wasm-world/` に、基準値と計測コマンドがある

- **TC-763-1** `benchmarks/wasm-world/` の基準値ファイルに、3 秒と 10 秒それぞれの `analyze` と `synthesize` の中央値（正の数）がある
- **TC-763-2** 同じディレクトリに、計測に使ったコマンドが書かれている

### SPEC-764 `world.wasm` と `world.mjs` のサイズの合計が 200KB 未満である

- **TC-764-1** 2 つのファイルのバイト数の合計が 204800 未満

## 仕様への差し戻し（テスト設計中に見つけたもの）

- **SPEC-747 / 748**: SPEC-747 の「WASM メモリの大きさ」を、テストが外から観測する手段が仕様に無かった。エンジンの公開プロパティ `memoryBytes` を SPEC-748 として追加し、SPEC-747 をそれで言い直した
- **SPEC-744**: `synthesize(f0, sp, ap, n)` は t を取らないのに、「t の長さが N でない場合」を条件に含めていた。t の条件を外した。どの検証レポートからも参照される前なので、ID は変えていない

## 網羅性の確認

- [x] `spec.md` の全 SPEC-ID が、この文書に見出しとして現れている
- [x] 各ケースが「入力 → 期待する観測結果」の形で書けている
- [x] 異常系・境界値の仕様に、対応するケースがある
- [ ] `trace-check.sh` の [2] [5] が 0 件（テストコードを書いた後に確認する）
