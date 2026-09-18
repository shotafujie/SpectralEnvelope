# 検証レポート: 音声ファイルの読み込み

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `91c7b18`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple Silicon (arm64)、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2
- 検証の観点: `91c7b18` で 005 に SPEC-614 / SPEC-615（画面に見える文言に `f0` の綴りが出ないこと、
  分解結果の表示）が追加された。その追加分の判定と、既存の保証が壊れていないかの判定。
  レポートは今回の実行結果で全体を書き直している。

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 7 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 7 |

判定の根拠は、5 アイテム分をまとめた 1 回のフル実行（`.venv/bin/pytest -v`、
`237 passed, 2 warnings in 263.25s (0:04:23)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件
（結果行 237 行を数えて、PASSED 以外の行が 0 行）。

判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
   1 つのテスト名が 2 つの TC を持つ場合（`test_TC_234_1_TC_234_2_…`）と、
   1 つの TC が複数のパラメータ化行に分かれる場合の両方を、この規則で扱う。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

設計にあって実行結果に現れない TC は全アイテムで 0 件、実行結果に現れて設計に無い TC も 0 件
（237 行の結果行から取り出した TC ID 238 種類 = 5 アイテムの設計 TC 238 件と完全一致）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

- **SPEC-300**: PASS (TC-300-1)
- **SPEC-301**: PASS (TC-301-1)
- **SPEC-302**: PASS (TC-302-1, TC-302-2)
- **SPEC-303**: PASS (TC-303-1)
- **SPEC-304**: PASS (TC-304-1)
- **SPEC-305**: PASS (TC-305-1, TC-305-2)
- **SPEC-306**: PASS (TC-306-1)

## 実行したコマンドと出力

判定の根拠。**要約せず、実際の出力を貼る。**

全体の集計行（5 アイテム分を 1 回で実行）:

```
$ .venv/bin/pytest -v > pytest.log 2>&1; echo "EXIT=$?" >> pytest.log
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 237 items

（中略: 237 行の結果行のうち、このアイテムに属するものを下に抜き出す）
================= 237 passed, 2 warnings in 263.25s (0:04:23) ==================
EXIT=0
```

このアイテムに属する TC を名前に持つ結果行（上の出力からの抜粋、加工なし）:

```
tests/e2e/test_load.py::test_TC_300_1_ファイルを開くボタンと受け付け種別 PASSED [  6%]
tests/e2e/test_load.py::test_TC_301_1_ファイル名付きで送信される PASSED  [  7%]
tests/e2e/test_load.py::test_TC_302_1_分解完了後は録音と同じ状態になる PASSED [  7%]
tests/e2e/test_load.py::test_TC_302_2_録音の後にファイルを読むとファイル側を使う PASSED [  8%]
tests/e2e/test_load.py::test_TC_303_1_送信中はボタンが無効 PASSED        [  8%]
tests/e2e/test_load.py::test_TC_304_1_録音中はファイルを開けない PASSED  [  8%]
tests/e2e/test_load.py::test_TC_305_1_エラー時は前の録音を使い続ける PASSED [  9%]
tests/e2e/test_load.py::test_TC_305_2_分解前のエラーでは再生ボタンは無効のまま PASSED [  9%]
tests/e2e/test_load.py::test_TC_306_1_同じファイルを2回選べる PASSED     [ 10%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/002-wav-load
=== traceability check ===
スコープ: docs/items/002-wav-load （このアイテムに属するIDのみ検査）

[002-wav-load] 仕様 7件 / テストケース 9件

[テストコード] 検出したテストケースID: 9件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

終了コード: 0。

```
$ ~/dev/.claude/hooks/trace-check.sh
=== traceability check ===

[001-envelope-jig] 仕様 86件 / テストケース 132件

[002-wav-load] 仕様 7件 / テストケース 9件

[003-morph] 仕様 23件 / テストケース 43件

[004-gain-curve] 仕様 18件 / テストケース 30件

[005-ui-affordance] 仕様 15件 / テストケース 24件

[テストコード] 検出したテストケースID: 238件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

終了コード: 0。

## トレーサビリティ

`trace-check.sh` の出力から転記する（目視で「0件」と書かない）。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

（`trace-check.sh` は孤児が 0 件の分類を個別に出力しないため、合計「孤児: 0件」からの転記。）

## 所見

仕様とテスト設計を読んだうえで気づいたこと。判定を左右しないが記録すべきもの。

- **002 の `spec.md` と `test-design.md` は `91c7b18` で変更されていない**
  （`git show --stat 91c7b18` に 002 のファイルも `tests/e2e/test_load.py` も現れない）。
  7 仕様 / 9 TC の対応は前回検証（`802aa71`）と同数で、判定も 7 件すべて PASS のまま。
- 005 に追加された SPEC-614（画面に `f0` の綴りが出ない）は、002 の観測点に触れていない。
  002 の E2E が見るのは `#open-file` / `#file` の `accept` と disabled 状態、`#graph` の `data-id`、
  要求の `id` であり、描画テキストの文字列比較は 1 件も無い。
- TC-301-1 は、Chromium がファイル込みの multipart 本文を Playwright に渡さない制約のため、
  ページ内で `fetch` をラップして FormData を記録している。送信内容の検査はこのラッパー越しの観測であり、
  ネットワーク上のバイト列そのものを見ているわけではない（テスト設計に明記済み）。
- SPEC-305 は「それ以前の分解結果があれば以降の API 呼び出しはその `id` を使い続ける」を求めるが、
  TC-305-1 が確認するのは envelope 要求の `id` のみで、元音再生の src までは見ていない。仕様よりわずかに狭い。
- SPEC-305 / TC-305-2 はエラー表示領域が空でないことを求めるが、その文言の綴りは検査していない。
  005 の TC-614-1 / TC-614-2 は**エラーが出ていない状態のページしか作らない**ため、
  エラー文言に `f0` が現れても、どのテストも落ちない。`#error` は可視要素であり、
  エラーが出た状態で検査すれば 005 の検査方法（`document.body.innerText`）で検出できることは実測で確認している
  （005 のレポートの所見の表を参照）。検出できないのは要素の性質ではなく、その状態を作るテストが無いこと。
