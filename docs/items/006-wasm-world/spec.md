# 仕様書: WORLD の WASM エンジン（分解と再合成）

- アイテムID: `006-wasm-world`
- 関連ロードマップ項目: なし（`docs/roadmap.md` は未作成）
- 関連ADR: `docs/adr/ADR-0001-browser-world-engine.md`、`docs/adr/ADR-0002-wasm-artifact-delivery.md`
- 作成日: 2026-09-18

## 目的

WORLD 本家を WASM にビルドし、JS から分解（harvest → cheaptrick → d4c）と再合成を呼べるエンジンを作る。
エンジンの出力が、v0.1.0 が使っている pyworld 0.3.5 の出力と一致することを、コミット済みの照合用データで保証する。

WASM 移行（ADR-0001）は 4 つのアイテムに分けて進める。これはその 1 つ目で、残りは次のとおり。

- 007-engine-dsp: DSP の JS 移植
- 008-worker-ui: Worker と UI の切り替え
- 009-pages-deploy: CI と Pages への配信

## スコープ

### やること

- WORLD のソース（`d625e7608ca23a870018f01e7c562ac683d9847f`）を、リポジトリ内に取り込む
- C ラッパーとビルドスクリプトを作り、成果物 `world.wasm` と `world.mjs` をコミットする（ADR-0002 の決定 1〜3）
- JS のエンジンモジュールを作る。WASM のメモリ管理を隠し、Float64Array で入出力する
- 照合用データ（ゴールデンデータ）を Python で生成するスクリプトと、そのデータ自体をコミットする
- 速度の基準値を `benchmarks/` に置く（ADR-0001 の決定 5）

### やらないこと

- **DSP**（formant / smooth / tilt / bands / curve / morph、パラメータの解釈、dB 列の出力）→ 007
- **分解結果の保持**（10 件の LRU）、**id の発行**、**Float32 での保持** → 008。このアイテムのエンジンは状態を持たない
- **Web Worker とのメッセージ**、**音声ファイルのデコード**（`decodeAudioData`）、**UI** → 008
- **有声フレームの一覧、fo の平均、秒数**など、分解結果から派生する値 → 008
- **GitHub Actions** での照合と Pages への配信 → 009
- **Pixel での計測** → 009
- **dio、stonemask** など、v0.1.0 が使っていない WORLD の関数を公開すること
- **44100Hz 以外のサンプリング周波数**、fft_size 2048 以外、frame_period 5ms 以外。分析条件は v0.1.0 と同じ値で固定する

## 共通の定義

- **F** = 1025（fft_size 2048 のビン数）
- **N** = 入力 x を分解して得られるフレーム数。pyworld 0.3.5 の `harvest(x, 44100, frame_period=5.0)` が返す f0 の要素数と同じ
- **行優先の N×F 配列** = 長さ N·F の Float64Array。フレーム i のビン k の値が、添字 `i·F + k` にある
- **照合用データ** = 次の手順で作り、`tests/golden/` にコミットしたファイル群
  - 入力は `tests/audio_fixtures.py` の `vowel("a", dur=1.0)`（44100 サンプル）
  - これを pyworld 0.3.5 で `harvest(x, 44100, frame_period=5.0)`、`cheaptrick(x, f0, t, 44100, fft_size=2048)`、`d4c(x, f0, t, 44100, fft_size=2048)` の順に処理する
  - さらに `synthesize(f0, sp, ap, 44100, 5.0)` の先頭 44100 サンプルを取る
  - 入力 x と、f0、t、sp、ap、y を記録する
- **再合成の長さ L** = `floor(N · 5 / 1000 · 44100)`。pyworld 0.3.5 の `synthesize` が出力する長さと同じ（実測: N = 201 で 44320、N = 601 で 132520）。エンジンはこの長さで再合成してから、先頭 n サンプルを返す
- **dB 値** = `10 · log10(sp + 1e-12)`（001 と同じ定義）
- **包絡差** = 001 と同じ定義。双方で fo > 0 のフレーム、かつ 50〜8000Hz のビンで取った dB 値の差の絶対値の平均
- **エンジン** = `createEngine()` が返すオブジェクト

## 仕様

### WORLD のソースとビルド

- **SPEC-700** `third_party/world/` に、WORLD の `src/` 以下のファイルと、WORLD のライセンス文（`LICENSE.txt`）がある
- **SPEC-701** `third_party/world/COMMIT` の内容は、40 桁のコミットハッシュ `d625e7608ca23a870018f01e7c562ac683d9847f` の 1 行である
- **SPEC-702** ビルドスクリプトが使う Docker イメージは、`emscripten/emsdk@sha256:41039722671531506a7d081828721e9ccde93125d91f88351e0fe4301606c7d4`（linux/arm64 のダイジェスト）で指定されている
- **SPEC-703** ビルドスクリプトには、タグだけで Docker イメージを指定している箇所が無い（`emscripten/emsdk` の後ろは必ず `@sha256:` で始まる）
- **SPEC-704** linux/arm64 のマシンでビルドスクリプトを実行すると、コミット済みの `world.wasm` と `world.mjs` とバイト単位で同一のファイルが出力される
- **SPEC-705** ビルドスクリプトを同じマシンで 2 回実行すると、2 回の出力はバイト単位で同一である

### エンジンの生成

- **SPEC-710** `createEngine()` は Promise を返し、それはエンジンに解決される
- **SPEC-711** エンジンの `fs` は 44100、`fftSize` は 2048、`framePeriod` は 5、`bins` は 1025 である
- **SPEC-712** エンジンの `minSamples` は 44100（1.0 秒）、`maxSamples` は 441000（10.0 秒）である。後続のアイテムは、録音の下限と上限をこの値から参照する
- **SPEC-713** エンジンのモジュールは Node 22 から import でき、`createEngine()` が解決される
- **SPEC-714** エンジンのモジュールは、Chromium のモジュール Worker（`new Worker(url, { type: "module" })`）の中から import でき、`createEngine()` が解決される

### 分解 `analyze(x)`

- **SPEC-720** `analyze(x)` は、Float64Array の x を受け取り、`{ f0, t, sp, ap }` を返す
- **SPEC-721** `f0` と `t` は長さ N の Float64Array である
- **SPEC-722** `sp` と `ap` は、行優先の N×F の Float64Array である
- **SPEC-723** 照合用データの x を分解した `f0` は、照合用データの f0 と、全要素で絶対差 1e-6 以内で一致する
- **SPEC-724** 照合用データの x を分解した `t` は、照合用データの t と、全要素で絶対差 1e-9 以内で一致する
- **SPEC-725** 照合用データの x を分解した `sp` の dB 値は、照合用データの sp の dB 値と、全要素で差 1e-6 dB 以内で一致する
- **SPEC-726** 照合用データの x を分解した `ap` は、照合用データの ap と、全要素で絶対差 1e-6 以内で一致する
- **SPEC-727** `analyze` は、引数の x を書き換えない

### 再合成 `synthesize(f0, sp, ap, n)`

- **SPEC-730** `synthesize(f0, sp, ap, n)` は、長さ n の Float64Array を返す
- **SPEC-731** 照合用データの f0、sp、ap と n = 44100 で再合成した結果は、照合用データの y と、全サンプルで絶対差 1e-6 以内で一致する
- **SPEC-732** n が再合成の長さ L より長いとき、L を超えた部分のサンプルはすべて 0 である
- **SPEC-733** `synthesize` は、引数の f0、sp、ap を書き換えない
- **SPEC-734** 合成母音 /a/ 3 秒を分解して、加工せずに再合成した音をエンジンで再分解すると、元の sp との包絡差は 1.0dB 以下である

### 異常系・境界

- **SPEC-740** x が Float64Array でないとき、`analyze` は TypeError を投げる
- **SPEC-741** x の長さが `minSamples` 未満のとき、`analyze` は RangeError を投げる
- **SPEC-742** x の長さが `maxSamples` を超えるとき、`analyze` は RangeError を投げる
- **SPEC-743** 長さがちょうど `minSamples` の x と、ちょうど `maxSamples` の x は、どちらも `analyze` が例外を投げずに結果を返す
- **SPEC-744** f0 の長さを N としたとき、t の長さが N でない場合、または sp か ap の長さが N·F でない場合、`synthesize` は RangeError を投げる
- **SPEC-745** n が 1 未満の場合、または `maxSamples` を超える場合、`synthesize` は RangeError を投げる
- **SPEC-746** 例外を投げた後も、同じエンジンで `analyze` と `synthesize` を続けて呼ぶと、正常な結果を返す
- **SPEC-747** 10 秒の入力で `analyze` と `synthesize` を続けて 20 回呼んだ後の WASM メモリの大きさは、1 回目を終えた直後の大きさと同じである（呼び出しのたびにメモリが増えていかない）

### 照合用データ

- **SPEC-750** 照合用データの生成スクリプトを実行すると、コミット済みの照合用データとバイト単位で同一のファイルが出力される
- **SPEC-751** 照合用データには、生成に使った numpy、scipy、pyworld のバージョン文字列が記録されている

## 非機能要件

測定条件: Apple M4 Max、Node 22、合成母音 /a/、初回を除く 5 回の中央値。

- **SPEC-760** 3 秒の入力に対する `analyze` の時間が 1.0 秒未満である
- **SPEC-761** 10 秒の入力に対する `analyze` の時間が 3.0 秒未満である
- **SPEC-762** 3 秒の入力に対する `synthesize` の時間が 0.1 秒未満である
- **SPEC-763** `benchmarks/wasm-world/` に、3 秒と 10 秒の入力に対する `analyze` と `synthesize` の中央値の基準値と、計測に使ったコマンドがある
- **SPEC-764** `world.wasm` と `world.mjs` のサイズの合計が 200KB 未満である

## 旧仕様との対応

v0.1.0 の仕様は凍結し、書き換えない（ADR-0001 の決定 6）。このアイテムが引き継ぐものは次のとおり。

| 旧 SPEC | 内容 | このアイテムでの扱い |
|---|---|---|
| SPEC-003 | `fs` は 44100、`fft_size` は 2048 | SPEC-711 |
| SPEC-005 | `frames` は f0 の要素数（= sp の行数） | SPEC-721、SPEC-722（`frames` の値そのものは 008） |
| SPEC-010 | 10.0 秒を超えたら先頭 10.0 秒を分解する | エンジンは上限を公開し（SPEC-712）、超えたら RangeError を投げる（SPEC-742）。切り詰めは 008 |
| SPEC-009 | 1.0 秒未満はエラー | エンジンは下限を公開し（SPEC-712）、下回ったら RangeError を投げる（SPEC-741）。画面へのエラー表示は 008 |
| SPEC-032 | 無加工の往復で包絡差 1.0dB 以下 | SPEC-734（エンジン単体での往復） |
| SPEC-036 | 再合成に使う ap は分解時の ap と同一 | SPEC-733（エンジンは ap を書き換えない）。経路全体は 007 |
| SPEC-120 | 3 秒の分解が 1.0 秒未満 | SPEC-760 |
| SPEC-121 | 3 秒の再合成が 0.3 秒未満 | SPEC-762 |

## 前提・依存

- ビルドには Docker と、SPEC-702 のイメージ（linux/arm64）が要る。SPEC-704 と SPEC-705 は、linux/arm64 のマシン（Apple Silicon の Mac）でだけ判定できる
- エンジンのテストは Node 22 で動かす。照合用データを読むだけで、Python も Docker も使わない（ADR-0001 の決定 4）
- 照合用データの生成には Python 3.13 と pyworld 0.3.5 を使う（v0.1.0 の `.venv`）
- SPEC-714 は Playwright の Chromium で判定する

## 未決事項

| # | 論点 | 決めないと何が書けないか |
|---|------|------------------------|
| — | なし | — |
