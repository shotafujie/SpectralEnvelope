# 検証レポート: 006-wasm-world（WORLD の WASM エンジン）

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `102008d`（ブランチ feature/wasm-engine）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: Apple M4 Max（arm64）、macOS（Darwin 25.5.0）、Node v22.22.3、Python 3.13.12、Docker 利用可

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 40 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 40 |

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

### WORLD のソースとビルド

- **SPEC-700**: PASS (TC-700-1, TC-700-2)
- **SPEC-701**: PASS (TC-701-1)
- **SPEC-702**: PASS (TC-702-1)
- **SPEC-703**: PASS (TC-703-1)
- **SPEC-704**: PASS (TC-704-1) — arm64 のマシンで Docker を使って実際にビルドし、SHA-256 が一致
- **SPEC-705**: PASS (TC-705-1)

### エンジンの生成

- **SPEC-710**: PASS (TC-710-1)
- **SPEC-711**: PASS (TC-711-1)
- **SPEC-712**: PASS (TC-712-1)
- **SPEC-713**: PASS (TC-713-1)
- **SPEC-714**: PASS (TC-714-1)

### 分解

- **SPEC-720**: PASS (TC-720-1)
- **SPEC-721**: PASS (TC-721-1, TC-721-2, TC-721-3)
- **SPEC-722**: PASS (TC-722-1, TC-722-2)
- **SPEC-723**: PASS (TC-723-1, TC-723-2)
- **SPEC-724**: PASS (TC-724-1)
- **SPEC-725**: PASS (TC-725-1)
- **SPEC-726**: PASS (TC-726-1)
- **SPEC-727**: PASS (TC-727-1)

### 再合成

- **SPEC-730**: PASS (TC-730-1, TC-730-2, TC-730-3)
- **SPEC-731**: PASS (TC-731-1)
- **SPEC-732**: PASS (TC-732-1, TC-732-2)
- **SPEC-733**: PASS (TC-733-1)
- **SPEC-734**: PASS (TC-734-1)

### 異常系・境界

- **SPEC-740**: PASS (TC-740-1, TC-740-2, TC-740-3)
- **SPEC-741**: PASS (TC-741-1, TC-741-2)
- **SPEC-742**: PASS (TC-742-1)
- **SPEC-743**: PASS (TC-743-1, TC-743-2)
- **SPEC-744**: PASS (TC-744-1, TC-744-2)
- **SPEC-745**: PASS (TC-745-1, TC-745-2, TC-745-3)
- **SPEC-746**: PASS (TC-746-1, TC-746-2)
- **SPEC-747**: PASS (TC-747-1)
- **SPEC-748**: PASS (TC-748-1, TC-748-2)

### 照合用データ

- **SPEC-750**: PASS (TC-750-1)
- **SPEC-751**: PASS (TC-751-1, TC-751-2)

### 非機能要件

- **SPEC-760**: PASS (TC-760-1)
- **SPEC-761**: PASS (TC-761-1)
- **SPEC-762**: PASS (TC-762-1)
- **SPEC-763**: PASS (TC-763-1, TC-763-2)
- **SPEC-764**: PASS (TC-764-1)

## 実行したコマンドと出力

### JS（エンジン・ビルド・性能）

TAP の出力が長いため、各テストの結果行と集計行を `grep -E '^(not )?ok |^# (tests|...)'` で抜き出したもの（行の中身は編集していない）。

```
$ npm run test:js
ok 1 - WORLD の src と world/ のヘッダが取り込まれている
ok 2 - WORLD のライセンス文がある
ok 3 - COMMIT は取り込んだ 40 桁のコミットハッシュの 1 行である
ok 4 - ビルドスクリプトは linux/arm64 のダイジェストでイメージを指定している
ok 5 - ビルドスクリプトはタグだけでイメージを指定していない
ok 6 - linux/arm64 でビルドすると、コミット済みの成果物と同一のファイルが出る
ok 7 - 同じマシンで 2 回ビルドすると、出力は同一である
ok 8 - world.wasm と world.mjs のサイズの合計が 200KB 未満
ok 9 - createEngine は Promise を返し、analyze と synthesize を持つエンジンに解決される
ok 10 - 分析条件のプロパティ
ok 11 - 録音の下限と上限のプロパティ
ok 12 - Node から import して 5 秒以内に createEngine が解決される
ok 13 - 生成直後の memoryBytes は 65536 の正の倍数
ok 14 - analyze は f0 / t / sp / ap の Float64Array を返す
ok 15 - 1 秒の入力で f0 と t の長さは 201
ok 16 - 3 秒の入力で f0 と t の長さは 601
ok 17 - 10 秒の入力で f0 と t の長さは 2001
ok 18 - sp と ap の長さは 201 × 1025
ok 19 - sp は行優先に並んでいる
ok 20 - f0 は照合用データと 1e-6 以内で一致する
ok 21 - 無声（f0 = 0）の位置は照合用データと完全に一致する
ok 22 - t は照合用データと 1e-9 以内で一致する
ok 23 - sp の dB 値は照合用データと 1e-6 dB 以内で一致する
ok 24 - ap は照合用データと 1e-6 以内で一致する
ok 25 - analyze は引数の x を書き換えない
ok 26 - 長さちょうど minSamples の x は分解できる
ok 27 - 長さちょうど maxSamples の x は分解できる
ok 28 - 10 秒を分解すると memoryBytes が広がり、65536 の倍数のまま
ok 29 - Float32Array は TypeError
ok 30 - 通常の配列は TypeError
ok 31 - undefined は TypeError
ok 32 - 長さ 44099 は RangeError
ok 33 - 長さ 0 は RangeError
ok 34 - 長さ 441001 は RangeError
ok 35 - analyze が例外を投げた後も、同じエンジンで正しく分解できる
ok 36 - n = 44100 で長さ 44100 の Float64Array を返す
ok 37 - n = 1 で長さ 1
ok 38 - n = 50000（L より長い）で長さ 50000
ok 39 - 再合成は照合用データの y と 1e-6 以内で一致する
ok 40 - L を超えた部分はすべて 0
ok 41 - n を長くしても先頭 44100 サンプルは照合用データと一致する
ok 42 - synthesize は引数の f0 / sp / ap を書き換えない
ok 43 - 3 秒の無加工往復で包絡差は 1.0dB 以下
ok 44 - sp の長さが N·F でないと RangeError
ok 45 - ap の長さが N·F でないと RangeError
ok 46 - n = 0 は RangeError
ok 47 - n = 441001 は RangeError
ok 48 - n = 441000 は長さ 441000 を返す
ok 49 - synthesize が例外を投げた後も、同じエンジンで正しく再合成できる
ok 50 - 10 秒の分解と再合成を 20 回繰り返しても memoryBytes は 1 回目の後から増えない
ok 51 - 3 秒の analyze は 1.0 秒未満
ok 52 - 10 秒の analyze は 3.0 秒未満
ok 53 - 3 秒の synthesize は 0.1 秒未満
ok 54 - 基準値のファイルに 3 秒と 10 秒の analyze / synthesize の中央値がある
ok 55 - 計測に使ったコマンドが書かれている
# tests 55
# suites 0
# pass 55
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 54798.590084
exit=0
```

補足: TC-704-1 は 1769ms、TC-705-1 は 3654ms で終わった。`engine/world/build.sh` は `docker run --platform linux/arm64 <ダイジェスト指定のイメージ> em++ ...` を実行しており、イメージはローカルにキャッシュ済みだった。

### Python（照合用データ・Chromium の Worker）

```
$ .venv/bin/pytest tests/test_golden_world.py tests/e2e/test_world_worker.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
plugins: anyio-4.15.1
collecting ... collected 4 items

tests/test_golden_world.py::test_TC_750_1_生成スクリプトの出力はコミット済みの照合用データと同一 PASSED [ 25%]
tests/test_golden_world.py::test_TC_751_1_生成に使ったライブラリのバージョンが記録されている PASSED [ 50%]
tests/test_golden_world.py::test_TC_751_2_pyworld_のバージョンは_0_3_5 PASSED [ 75%]
tests/e2e/test_world_worker.py::test_TC_714_1_モジュールWorkerの中でエンジンを読み込み分解できる PASSED [100%]

=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 4 passed, 2 warnings in 2.36s =========================
exit=0
```

### Python 全体（他を壊していないことの確認）

```
$ .venv/bin/pytest -q
（進捗の行は省略）

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
242 passed, 2 warnings in 269.41s (0:04:29)
exit=0
```

### 参考: 速度の実測（表示のみ。基準値は書き換えていない）

```
$ node benchmarks/wasm-world/run.mjs
{
 "median_seconds": {
  "3s": {
   "analyze": 0.616,
   "synthesize": 0.0353
  },
  "10s": {
   "analyze": 2.0912,
   "synthesize": 0.1199
  }
 },
 "conditions": {
  "cpu": "Apple M4 Max",
  "node": "v22.22.3",
  "input": "tests/golden/vowel-a-{3s,10s}.f64（合成母音 /a/）",
  "method": "初回を除く 5 回の中央値"
 }
}
```

### トレーサビリティ（このレポートを書く前）

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/006-wasm-world
=== traceability check ===
スコープ: docs/items/006-wasm-world （このアイテムに属するIDのみ検査）

[006-wasm-world] 仕様 40件 / テストケース 59件
  [1] 検証されていない仕様: 40件 (verification.md が未作成)
      SPEC-700
      SPEC-701
      SPEC-702
      SPEC-703
      SPEC-704
      SPEC-705
      SPEC-710
      SPEC-711
      SPEC-712
      SPEC-713
      SPEC-714
      SPEC-720
      SPEC-721
      SPEC-722
      SPEC-723
      SPEC-724
      SPEC-725
      SPEC-726
      SPEC-727
      SPEC-730
      SPEC-731
      SPEC-732
      SPEC-733
      SPEC-734
      SPEC-740
      SPEC-741
      SPEC-742
      SPEC-743
      SPEC-744
      SPEC-745
      SPEC-746
      SPEC-747
      SPEC-748
      SPEC-750
      SPEC-751
      SPEC-760
      SPEC-761
      SPEC-762
      SPEC-763
      SPEC-764

[テストコード] 検出したテストケースID: 59件 (探索起点: .)

孤児: 合計 40件 — 鎖が切れています。
孤児の意味と対処は docs/TRACEABILITY.md の「孤児（orphan）の定義」を参照。
exit=1
```

[1] の 40 件は、このレポートがまだ無かったことによるもの。[2]〜[5] は 0 件（出力に現れていない）。
このレポートを書いた後の出力は、末尾の「トレーサビリティ（このレポートを書いた後）」に貼る。

## 所見

判定は左右しないが、記録すべきこと。

1. **SPEC-746 はテストが仕様より狭い。** 仕様は「例外を投げた後も、同じエンジンで `analyze` と `synthesize` を続けて呼ぶと、正常な結果を返す」。TC-746-1 は `analyze` の例外の後に `analyze` だけ、TC-746-2 は `synthesize` の例外の後に `synthesize` だけを確かめている。`analyze` の例外の後の `synthesize`（逆も）は確かめていない。
2. **SPEC-748 の前半はテストで直接確かめていない。** 仕様は `memoryBytes` を「そのエンジンが使っている WASM 線形メモリのバイト数」と定義する。TC-748-1、TC-748-2 が見ているのは「65536 の正の倍数」と「10 秒の分解の後に増える」ことだけで、実際の線形メモリの大きさと等しいことは確かめていない。実装は `M.HEAPU8.buffer.byteLength` を返している（コードを読んで分かったことで、テストの結果ではない）。SPEC-747 はこの値に頼って判定しているので、その前提もテストでは保証されていない。
3. **性能テストの測り方。** `npm run test:js` は `node --test 'tests/js/*.test.mjs'` で、Node のテストランナーは既定でファイルを並列に動かす。TC-760〜762 は、ほかのテストファイル（Docker ビルドや 20 回の繰り返しなど）と同時に測られた。仕様の測定条件は負荷について何も書いていない。この条件でも基準を満たした。単体で測った中央値（上の参考）は、10 秒の analyze が 2.09 秒で上限 3.0 秒の約 70%、3 秒の synthesize が 0.035 秒で上限 0.1 秒の約 35%。
4. **仕様に無い振る舞い（コードを読んで分かったこと。テストはしていない）。**
   - `synthesize` は f0、sp、ap の型を確かめていない（`analyze` は x に TypeError を投げる）
   - `synthesize` の n の検査は `n >= 1 && n <= maxSamples` だけで、整数でない n（例 1.5）は検査を通り、その後の `new Float64Array(n)` の振る舞いに任される
   - f0 の長さが 0 のとき（sp と ap も長さ 0）の `synthesize` の振る舞いは、仕様に無い
5. **SPEC-732 は N = 201 の 1 通りだけで確かめている。** L の式（`floor(N·5/1000·44100)`）は、N·220.5 が小数になる奇数の N でしか床関数が効かない。N = 201 は奇数なので床関数の側は確かめられているが、偶数の N では確かめていない。
6. **TC-704-1 と TC-705-1 は、Docker のイメージがローカルに無いと取得のためにネットワークが要る。** 今回はキャッシュ済みで、2 秒前後で終わった。
7. `test-design.md` の網羅性の確認の最後の項目（「trace-check.sh の [2] [5] が 0 件」）はチェックが付いていない。今回の trace-check.sh の出力では [2] と [5] は 0 件だった。

## トレーサビリティ（このレポートを書いた後）

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/006-wasm-world
=== traceability check ===
スコープ: docs/items/006-wasm-world （このアイテムに属するIDのみ検査）

[006-wasm-world] 仕様 40件 / テストケース 59件

[テストコード] 検出したテストケースID: 59件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
exit=0
```

`trace-check.sh` の出力から転記する（目視で「0件」と書かない）。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |
| — | 合計 | 0（「孤児: 0件」） |
