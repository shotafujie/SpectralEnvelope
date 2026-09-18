# 設計: WORLD の WASM エンジン（分解と再合成）

- アイテムID: `006-wasm-world`
- 入力: `spec.md`（SPEC-700〜764）、`test-design.md`（TC-700-1〜TC-764-1）
- 作成日: 2026-09-18

## ファイル構成

| パス | 役割 | 新規 / 変更 |
|---|---|---|
| `third_party/world/src/`、`LICENSE.txt`、`COMMIT` | WORLD のソース（`d625e76` の `src/` をそのまま複製）とライセンス、取り込んだコミット | 新規 |
| `engine/world/wrapper.cpp` | C ラッパー。スパイクの約 40 行を元に、合成の長さ L で再合成してから n に切り詰める処理を加える | 新規 |
| `engine/world/build.sh` | ビルドスクリプト。イメージのダイジェスト、emcc のオプション、コンテナ内のマウント先（`/src`）を 1 か所に固定する。引数は出力先ディレクトリ（省略時は `engine/world/`） | 新規 |
| `engine/world/world.wasm`、`world.mjs` | 成果物（コミットする） | 新規 |
| `engine/world-engine.mjs` | JS のエンジン。`createEngine()` を公開し、引数の検査、WASM メモリの確保と解放、Float64Array への詰め替えを受け持つ | 新規 |
| `tools/make_golden_world.py` | 照合用データの生成スクリプト。引数は出力先ディレクトリ（省略時は `tests/golden/`） | 新規 |
| `tests/golden/world-a-1s.*`、`vowel-a-3s.f64`、`vowel-a-10s.f64`、`world-meta.json` | 照合用データと、テスト入力、メタデータ | 新規 |
| `tests/js/golden.mjs` | テスト用の照合用データ読み込み関数と、包絡差の計算（エンジンの実装を使わない） | 新規 |
| `tests/js/world-engine.test.mjs`、`world-build.test.mjs`、`world-perf.test.mjs` | Node のテスト（`node:test`） | 新規 |
| `tests/test_golden_world.py` | 照合用データの再現性とメタデータ | 新規 |
| `tests/e2e/test_world_worker.py`、`tests/e2e/world_worker.html`、`world_worker.mjs` | Chromium のモジュール Worker からの読み込み | 新規 |
| `benchmarks/wasm-world/baseline.json`、`README.md` | 速度の基準値と計測コマンド | 新規 |
| `benchmarks/wasm-world/run.mjs` | 計測スクリプト（基準値を出力する） | 新規 |
| `package.json` | `"type": "module"` と `test:js` スクリプトだけ。外部依存は入れない | 新規 |

### 照合用データの形式

- 配列は、リトルエンディアンの Float64 をそのまま並べたバイナリ（`.f64`）。2 次元配列は行優先
- 1 秒の照合用データのファイル: `world-a-1s.x.f64`、`.f0.f64`、`.t.f64`、`.sp.f64`、`.ap.f64`、`.y.f64`
- `world-meta.json` に、各ファイルの形、生成に使った numpy / scipy / pyworld のバージョン、入力の作り方を書く
- JSON はキーを整列して書き出す（SPEC-750 のバイト単位の再現のため）

### エンジンの内部

- WASM のモジュールは、`createEngine()` のたびに 1 つ作る。エンジンどうしで状態を共有しない
- 呼び出しごとに必要な領域を `_malloc` で確保し、戻る前に（例外のときも `finally` で）すべて `_free` する。これで SPEC-746 と SPEC-747 を満たす
- 結果は WASM のメモリから `slice()` で複製して返す。WASM のメモリを直接参照する配列は返さない（メモリが広がると、参照していた配列が無効になるため）
- `memoryBytes` は `HEAPU8.buffer.byteLength` を返す（`-sEXPORTED_RUNTIME_METHODS` に `HEAPU8` を加える）

## タスクの順番（1 タスク = 1 回の Red → Green）

| # | タスク | 緑にする TC |
|---|---|---|
| 1 | WORLD のソースを取り込み、`LICENSE.txt` と `COMMIT` を置く | TC-700-1、TC-700-2、TC-701-1 |
| 2 | 照合用データの生成スクリプトを書き、データをコミットする | TC-750-1、TC-751-1、TC-751-2 |
| 3 | テスト用の読み込み関数（`tests/js/golden.mjs`）を書く（テストの道具なので TC は無い。タスク 4 以降のテストの中で使われることで確かめる） | — |
| 4 | ビルドスクリプトと C ラッパーを書き、成果物をコミットする | TC-702-1、TC-703-1、TC-704-1、TC-705-1、TC-764-1 |
| 5 | エンジンの生成とプロパティ | TC-710-1、TC-711-1、TC-712-1、TC-713-1、TC-748-1 |
| 6 | `analyze` の形と照合 | TC-720-1、TC-721-1〜3、TC-722-1〜2、TC-723-1〜2、TC-724-1、TC-725-1、TC-726-1、TC-727-1、TC-743-1〜2、TC-748-2 |
| 7 | `analyze` の異常系 | TC-740-1〜3、TC-741-1〜2、TC-742-1、TC-746-1 |
| 8 | `synthesize` の形と照合、長さ L を超える部分 | TC-730-1〜3、TC-731-1、TC-732-1〜2、TC-733-1、TC-734-1 |
| 9 | `synthesize` の異常系 | TC-744-1〜2、TC-745-1〜3、TC-746-2 |
| 10 | メモリが増えないこと | TC-747-1 |
| 11 | Chromium のモジュール Worker | TC-714-1 |
| 12 | 性能と基準値 | TC-760-1、TC-761-1、TC-762-1、TC-763-1、TC-763-2 |

C ラッパーを変えたら（タスク 8 で長さ L の処理を加えるとき）、成果物を再ビルドして同じコミットに含める（ADR-0002）。

## 検証の方法

- 実装中は各タスクで `node --test 'tests/js/*.test.mjs'` と、該当する pytest を回す
- 完了の判断は `agents/verifier`（独立検証）が行い、`verification.md` を書く
- 検証の前に `~/dev/.claude/hooks/trace-check.sh docs/items/006-wasm-world` の孤児が、[1]（verification.md 未作成）を除いて 0 件であることを確かめる
