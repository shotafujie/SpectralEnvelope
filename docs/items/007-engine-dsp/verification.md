# 検証レポート: DSP の JS 移植（包絡の加工と再合成の経路）

- 検証日: 2026-09-21
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `63db6a0`（ブランチ `feature/wasm-engine`、作業ツリーは clean）
- 対象仕様: `docs/items/007-engine-dsp/spec.md` / 対象テスト設計: `docs/items/007-engine-dsp/test-design.md`
- 実行環境: Node v22.22.3、Python 3.13.12（`.venv`）、darwin 25.5.0

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 55 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 55 |

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

- **SPEC-800**: PASS (TC-800-1, TC-800-2)
- **SPEC-801**: PASS (TC-801-1)
- **SPEC-802**: PASS (TC-802-1)
- **SPEC-803**: PASS (TC-803-1)
- **SPEC-804**: PASS (TC-804-1)
- **SPEC-805**: PASS (TC-805-1)
- **SPEC-806**: PASS (TC-806-1)
- **SPEC-807**: PASS (TC-807-1)
- **SPEC-808**: PASS (TC-808-1, TC-808-2, TC-808-3)
- **SPEC-809**: PASS (TC-809-1, TC-809-2)
- **SPEC-810**: PASS (TC-810-1, TC-810-2, TC-810-3)
- **SPEC-819**: PASS (TC-819-1)
- **SPEC-820**: PASS (TC-820-1, TC-820-2)
- **SPEC-821**: PASS (TC-821-1, TC-821-2)
- **SPEC-822**: PASS (TC-822-1)
- **SPEC-823**: PASS (TC-823-1, TC-823-2)
- **SPEC-824**: PASS (TC-824-1)
- **SPEC-825**: PASS (TC-825-1, TC-825-2)
- **SPEC-826**: PASS (TC-826-1, TC-826-2)
- **SPEC-827**: PASS (TC-827-1, TC-827-2)
- **SPEC-828**: PASS (TC-828-1)
- **SPEC-829**: PASS (TC-829-1, TC-829-2)
- **SPEC-830**: PASS (TC-830-1)
- **SPEC-831**: PASS (TC-831-1)
- **SPEC-835**: PASS (TC-835-1)
- **SPEC-836**: PASS (TC-836-1, TC-836-2)
- **SPEC-837**: PASS (TC-837-1)
- **SPEC-838**: PASS (TC-838-1)
- **SPEC-840**: PASS (TC-840-1)
- **SPEC-841**: PASS (TC-841-1)
- **SPEC-842**: PASS (TC-842-1)
- **SPEC-843**: PASS (TC-843-1)
- **SPEC-844**: PASS (TC-844-1)
- **SPEC-845**: PASS (TC-845-1)
- **SPEC-846**: PASS (TC-846-1)
- **SPEC-847**: PASS (TC-847-1, TC-847-2, TC-847-3)
- **SPEC-850**: PASS (TC-850-1)
- **SPEC-851**: PASS (TC-851-1)
- **SPEC-852**: PASS (TC-852-1)
- **SPEC-853**: PASS (TC-853-1)
- **SPEC-854**: PASS (TC-854-1)
- **SPEC-855**: PASS (TC-855-1)
- **SPEC-860**: PASS (TC-860-1)
- **SPEC-861**: PASS (TC-861-1)
- **SPEC-862**: PASS (TC-862-1)
- **SPEC-863**: PASS (TC-863-1)
- **SPEC-864**: PASS (TC-864-1, TC-864-2)
- **SPEC-870**: PASS (TC-870-1)
- **SPEC-871**: PASS (TC-871-1)
- **SPEC-872**: PASS (TC-872-1)
- **SPEC-873**: PASS (TC-873-1, TC-873-2)
- **SPEC-880**: PASS (TC-880-1)
- **SPEC-881**: PASS (TC-881-1)
- **SPEC-882**: PASS (TC-882-1)
- **SPEC-883**: PASS (TC-883-1, TC-883-2)

## 実行したコマンドと出力

判定の根拠。**要約せず、実際の出力を貼る。**

JS は対象アイテムだけでなく `tests/js/*.test.mjs` 全体（006 を含む）を実行した。
TAP の各テスト行は長いため、集計行をそのまま貼る（`not ok` 行は 0 件、`ok` 行は 126 件）。

```
$ npm run test:js
（終了コード 0）
# tests 126
# suites 0
# pass 126
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 55683.835334
```

```
$ .venv/bin/pytest tests/test_golden_dsp.py
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
plugins: anyio-4.15.1
collected 3 items

tests/test_golden_dsp.py ...                                             [100%]

=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 3 passed, 2 warnings in 0.46s =========================
（終了コード 0）
```

トレーサビリティ検査は、このレポートを書く前と後の 2 回実行した。

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/007-engine-dsp   # レポート作成前
=== traceability check ===
スコープ: docs/items/007-engine-dsp （このアイテムに属するIDのみ検査）

[007-engine-dsp] 仕様 55件 / テストケース 74件
  [1] 検証されていない仕様: 55件 (verification.md が未作成)
      SPEC-800
      SPEC-801
      SPEC-802
      SPEC-803
      SPEC-804
      SPEC-805
      SPEC-806
      SPEC-807
      SPEC-808
      SPEC-809
      SPEC-810
      SPEC-819
      SPEC-820
      SPEC-821
      SPEC-822
      SPEC-823
      SPEC-824
      SPEC-825
      SPEC-826
      SPEC-827
      SPEC-828
      SPEC-829
      SPEC-830
      SPEC-831
      SPEC-835
      SPEC-836
      SPEC-837
      SPEC-838
      SPEC-840
      SPEC-841
      SPEC-842
      SPEC-843
      SPEC-844
      SPEC-845
      SPEC-846
      SPEC-847
      SPEC-850
      SPEC-851
      SPEC-852
      SPEC-853
      SPEC-854
      SPEC-855
      SPEC-860
      SPEC-861
      SPEC-862
      SPEC-863
      SPEC-864
      SPEC-870
      SPEC-871
      SPEC-872
      SPEC-873
      SPEC-880
      SPEC-881
      SPEC-882
      SPEC-883

[テストコード] 検出したテストケースID: 74件 (探索起点: .)

孤児: 合計 55件 — 鎖が切れています。
孤児の意味と対処は docs/TRACEABILITY.md の「孤児（orphan）の定義」を参照。
（終了コード 1）
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/007-engine-dsp   # レポート作成後
=== traceability check ===
スコープ: docs/items/007-engine-dsp （このアイテムに属するIDのみ検査）

[007-engine-dsp] 仕様 55件 / テストケース 74件

[テストコード] 検出したテストケースID: 74件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
（終了コード 0）
```

## トレーサビリティ

`trace-check.sh` の出力（レポート作成後の実行）から転記する。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

全アイテムを対象にした `~/dev/.claude/hooks/trace-check.sh`（引数なし）でも、
同一IDの二重定義（[6]）と複数アイテムでの仕様ID重複（[7]）は報告されなかった。

## 所見

判定を左右しないが記録しておくこと。

- **SPEC-851 の検証は間接的である。** 仕様は「再合成に使う fo は f0 の各要素に pitch を掛けたもの」だが、
  TC-851-1 は再合成音を 006 のエンジンで再分解し、有声フレームの fo 比の中央値が 1.5 倍 ±3% であることを見ている。
  「観測点」として戻り値 `f0` が公開されている（TC-852-1 はそれを直接見ている）のに、
  TC-851-1 は `r.f0[i] === f0[i] * pitch` の要素ごとの一致を確かめていない。
  検出できるのは「おおむね 1.5 倍になっている」までで、一部フレームだけ別の係数が掛かる誤りは通り抜ける。
- **SPEC-880 / SPEC-881 の「全パラメータ」に morph が含まれていない。**
  `tests/js/engine-dsp-perf.test.mjs` の `ALL` は formant / smooth / tilt / bands / curve / pitch のみで、
  `morph` と相手の log_sp を渡していない（`engine-dsp-golden.test.mjs` の `ALL` には `morph: { ratio: 0.4 }` がある）。
  モーフ相手の伸縮と混合の時間は、この 2 つの性能仕様の測定に入っていない。
  `benchmarks/engine-dsp/baseline.json` の `conditions.params` にも morph は無く、基準値も同じ条件である。
- **TC-864-2 は仕様 SPEC-864 より狭い。** 仕様は「7 つのパラメータの組の中身が記録されている」だが、
  テストは組の名前の集合が 7 つであること、`formant` の組の `formant` が 1.0 でないこと、
  `all` に `morph` があることだけを見ており、各組の値そのものの妥当性は見ていない。
  ただし組の中身は TC-860-1 / TC-861-1 が `dsp-meta.json` の `cases` をそのまま params として使って
  Python 版の出力と照合しているため、実質的な保証はそちらにある。
- **TC-870-1 の名前と SPEC-870 の条件がずれている。** 仕様は「sp の長さが N·F でないとき」だが、
  テスト名は「sp の長さが F の倍数でないと RangeError」で、検査しているのは末尾 1 要素を削った場合
  （= F の倍数でない場合）だけである。N·F ではあるが想定した N と異なる長さ、という入力は検査されていない。
  もっとも、加工の関数は N を引数で受け取らず長さから決める設計なので、
  仕様側の「N·F」という書き方が実際に検査できる条件より強い、という指摘にとどまる。
- **期待値の独立性は保たれている。** `tests/js/dsp-ref.mjs` は冒頭に「実装のモジュールは import しない」と書かれており、
  実際に `engine/` からの import は無い。平滑化は O(N²) の素朴な DCT-II / IDCT で、
  実装（次数を絞った計算）とは別の道筋で期待値を作っている。
- **照合用データの再現性テストは本物である。** TC-863-1 は `tools/make_golden_dsp.py` を
  一時ディレクトリへ実際に実行し、`tests/golden/dsp/` の全ファイルの SHA-256 と集合を比較している。
- 006 のテストを含む `npm run test:js` 全体（126 件）が通っており、このアイテムの変更が
  006 のエンジンのテストを壊していないことも確認した。
