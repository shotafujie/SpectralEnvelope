# 検証レポート: 007-engine-dsp（DSP の JS 移植）

- 検証日: 2026-09-21
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `5da4a0f`（ブランチ `feature/wasm-engine`、作業ツリーは clean）
- 対象仕様: `docs/items/007-engine-dsp/spec.md` / 対象テスト設計: `docs/items/007-engine-dsp/test-design.md`

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 55 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 55 |

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

### パラメータの解釈

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

### 包絡の加工

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

### モーフ相手の伸縮

- **SPEC-835**: PASS (TC-835-1)
- **SPEC-836**: PASS (TC-836-1, TC-836-2)
- **SPEC-837**: PASS (TC-837-1)
- **SPEC-838**: PASS (TC-838-1)

### 1 フレーム分の dB 列

- **SPEC-840**: PASS (TC-840-1)
- **SPEC-841**: PASS (TC-841-1)
- **SPEC-842**: PASS (TC-842-1)
- **SPEC-843**: PASS (TC-843-1)
- **SPEC-844**: PASS (TC-844-1)
- **SPEC-845**: PASS (TC-845-1)
- **SPEC-846**: PASS (TC-846-1)
- **SPEC-847**: PASS (TC-847-1, TC-847-2, TC-847-3)

### 再合成の経路

- **SPEC-850**: PASS (TC-850-1)
- **SPEC-851**: PASS (TC-851-1, TC-851-2)
- **SPEC-852**: PASS (TC-852-1)
- **SPEC-853**: PASS (TC-853-1)
- **SPEC-854**: PASS (TC-854-1)
- **SPEC-855**: PASS (TC-855-1)

### Python 版との照合

- **SPEC-860**: PASS (TC-860-1)
- **SPEC-861**: PASS (TC-861-1)
- **SPEC-862**: PASS (TC-862-1)
- **SPEC-863**: PASS (TC-863-1)
- **SPEC-864**: PASS (TC-864-1, TC-864-2)

### 異常系・境界

- **SPEC-870**: PASS (TC-870-1)
- **SPEC-871**: PASS (TC-871-1)
- **SPEC-872**: PASS (TC-872-1)
- **SPEC-873**: PASS (TC-873-1, TC-873-2)

### 非機能要件

- **SPEC-880**: PASS (TC-880-1)
- **SPEC-881**: PASS (TC-881-1)
- **SPEC-882**: PASS (TC-882-1)
- **SPEC-883**: PASS (TC-883-1, TC-883-2)

## 実行したコマンドと出力

判定の根拠。実際の出力を貼る。

### JS テスト（ユニット・統合・性能）

`tests/js/*.test.mjs` 全ファイルを実行した（006 のテストも含むフル実行）。

```
$ npm run test:js

> test:js
> node --test 'tests/js/*.test.mjs'

TAP version 13
...
1..127
# tests 127
# suites 0
# pass 127
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 55520.529791

（終了コード 0。`not ok` は 0 行）
```

内訳（`grep -cE '^\s*test\(' tests/js/*.test.mjs`）:

```
tests/js/engine-dsp-golden.test.mjs: 10
tests/js/engine-dsp-perf.test.mjs: 5
tests/js/engine-dsp.test.mjs: 57
tests/js/world-build.test.mjs: 8
tests/js/world-engine.test.mjs: 42
tests/js/world-perf.test.mjs: 5
TOTAL=127
```

007 のテストは `ok 1` 〜 `ok 72`（= 57 + 10 + 5）で、いずれも `ok`。
性能テスト（TC-880-1 / 881-1 / 882-1）の実測:

```
ok 11 - 3 秒（601 フレーム）の全パラメータ適用は 0.3 秒未満
  duration_ms: 283.464208
ok 12 - 10 秒（2001 フレーム）の全パラメータ適用は 1.0 秒未満
  duration_ms: 793.213
ok 13 - 10 秒の分解結果に対する 1 フレーム分の dB 列は 0.02 秒未満
  duration_ms: 2.415375
ok 14 - 基準値のファイルに 3 つの中央値がある
  duration_ms: 0.198916
ok 15 - 計測に使ったコマンドが書かれている
  duration_ms: 0.162375
```

（`duration_ms` は暖機 1 回 + 計測 5 回の合計。`benchmarks/engine-dsp/baseline.json`
の中央値 apply_3s 0.038 / apply_10s 0.129 / envelope_frame_10s 0.0004 秒と矛盾しない）

### Python テスト（照合用データの再現性とメタデータ）

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
======================== 3 passed, 2 warnings in 0.45s =========================

（終了コード 0）
```

### トレーサビリティ検査

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/007-engine-dsp
=== traceability check ===
スコープ: docs/items/007-engine-dsp （このアイテムに属するIDのみ検査）

[007-engine-dsp] 仕様 55件 / テストケース 75件

[テストコード] 検出したテストケースID: 75件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。

（終了コード 0）
```

## トレーサビリティ

`trace-check.sh` の出力から転記。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |
| **合計** | | **0** |

テスト設計書の 75 件の TC はすべてテストコードに ID が埋まっており、かつ 3 ファイルの
`test(` の数（57 + 10 + 5 = 72）と Python の 3 件を合わせた 75 件と一致する。
設計にあるだけで実行されていない TC は無い。

## 所見

判定を左右しないが記録すべきもの。

1. **SPEC-854 の検査範囲が仕様文より狭い。** 仕様は「全フレーム・全ビンで 1e-6 dB 以内」と
   書いているが、TC-854-1 はフレーム 0・50・100・150・200 の 5 行だけを見る（テスト設計書に
   そう書いてあり、設計どおりではある）。ただし SPEC-862 の TC-862-1 が同じ「全部」の params で
   `render()` の返す sp 全体（201×1025）を Python 版と 1e-6 dB 以内で照合しているため、
   全フレームの sp そのものは別経路で押さえられている。

2. **SPEC-860 / SPEC-862 の照合対象は `render()` の返す sp である。** 仕様文の「加工後の dB 列」は
   包絡の加工（SPEC-820）の出力を指すが、テストは `render(engine, analysis(), raw, …).sp` から
   dB に直して照合している。両者が同じであることは SPEC-854（5 フレーム）でしか結ばれていない。
   実質は 1 の項と同じ穴で、「加工の出力そのもの」と「再合成に渡した sp」が
   全フレームで同一であることを直接見るテストは存在しない。

3. **SPEC-880 / 881 の計測に伸縮が含まれない。** TC-880-1 / 881-1 は `stretchPartner()` を
   事前に呼んで伸縮済みの相手を用意し、`applyEnvelope()` だけを計測している。仕様が加工
   （SPEC-820）を「伸縮後の B を受け取るもの」と定義しているので設計と整合しているが、
   008 でつまみ操作の応答を見るときは伸縮（SPEC-835）のコストが別途載る点に注意がいる。

4. **TC-851-2 の統計量が設計の記述と厳密には異なる。** 設計は「双方で有声のフレームの fo の
   中央値が、元の 1.5 倍 ±3%」だが、実装は「フレームごとの比 `again.f0[i] / G.f0[i]` の中央値」を
   取っている（中央値の比 ではなく 比の中央値）。実測は通っており、この入力では実害はない。

5. **`tests/js/dsp-ref.mjs` は実装を import しない独立計算だが、定数は書き写しである。**
   バンド境界（500 / 1500 / 4000Hz）、クロスフェード幅（1/3 oct）、制御点 `50·400^(j/19)`、
   `k·44100/2048` などは実装と同じ値をテスト側に置いている。式の取り違えは検出できるが、
   定数そのものの誤りは検出できない。この部分は SPEC-860〜862 の Python 版照合が担保している。

6. **TC-826-1 はクロスフェード区間を見ない。** 500·2^(−1/3) 以下と 1500·2^(1/3) 以上だけを
   確認しているが、クロスフェード区間は TC-826-2 が全ビンで独立計算と照合しているため穴は無い。

7. **`spec.md` の記載順が ID の昇順ではない。** SPEC-820 が SPEC-819 より前に書かれている。
   `trace-check.sh` の判定には影響しない。

8. 本レポートは、コミット `5da4a0f` の作業ツリーで上記 3 コマンドを実際に実行した結果に基づく。
   前リビジョンの検証レポートの内容は参照していない。
