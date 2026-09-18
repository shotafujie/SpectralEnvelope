# 検証レポート: 説明のツールチップ化とスライダーの変更表示

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `802aa71`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple Silicon (arm64)、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2
- 検証の観点: `904147e`（画面の表記）と `802aa71`（仕様書・テスト設計書の表記）で基本周波数の綴りを
  `f0` から `fo` に変えたことにより、保証の内容が変わっていないか・既存の保証が壊れていないか

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 13 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 13 |

判定の根拠は、5 アイテム分をまとめた 1 回のフル実行（`.venv/bin/pytest -v`、
`234 passed, 2 warnings in 257.25s (0:04:17)`）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件
（`grep -cE 'FAILED|ERROR|SKIPPED|XFAIL|XPASS'` の出力が 0）。

判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
   1 つのテスト名が 2 つの TC を持つ場合（`test_TC_234_1_TC_234_2_…`）と、
   1 つの TC が複数のパラメータ化行に分かれる場合の両方を、この規則で扱う。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

設計にあって実行結果に現れない TC は全アイテムで 0 件、実行結果に現れて設計に無い TC も 0 件
（234 行の結果行から取り出した TC ID 235 種類 = 5 アイテムの設計 TC 235 件と完全一致）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

- **SPEC-600**: PASS (TC-600-1)
- **SPEC-601**: PASS (TC-601-1, TC-601-2)
- **SPEC-602**: PASS (TC-602-1)
- **SPEC-603**: PASS (TC-603-1, TC-603-2)
- **SPEC-604**: PASS (TC-604-1)
- **SPEC-605**: PASS (TC-605-1, TC-605-2)
- **SPEC-606**: PASS (TC-606-1, TC-606-2)
- **SPEC-607**: PASS (TC-607-1)
- **SPEC-608**: PASS (TC-608-1, TC-608-2)
- **SPEC-610**: PASS (TC-610-1)
- **SPEC-611**: PASS (TC-611-1, TC-611-2)
- **SPEC-612**: PASS (TC-612-1, TC-612-2, TC-612-3)
- **SPEC-613**: PASS (TC-613-1)

## 実行したコマンドと出力

判定の根拠。**要約せず、実際の出力を貼る。**

全体の集計行（5 アイテム分を 1 回で実行）:

```
$ .venv/bin/pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 234 items

（中略: 234 行の結果行のうち、このアイテムに属するものを下に抜き出す）
================= 234 passed, 2 warnings in 257.25s (0:04:17) ==================
```

pytest の終了コードは記録できなかった。実行時に `${PIPESTATUS[0]}` で拾おうとしたが、
このシェルは zsh（`pipestatus`）のため空に展開され、ログ末尾は `EXITCODE=` のままになっている。
観測できたのは上の集計行と、`collected 234 items` に対して 234 行の結果行がすべて PASSED であること、
`grep -cE 'FAILED|ERROR|SKIPPED|XFAIL|XPASS'` の出力が 0 であること。
（前回検証 `8840cd2` のレポートは pytest の終了コードを記録しているが、今回は取れていない。
以下の trace-check の「終了コード: 0」は、実行時に表示された値をそのまま書いている。）

このアイテムに属する TC を名前に持つ結果行（上の出力からの抜粋、加工なし）:

```
tests/e2e/test_tooltip.py::test_TC_600_1_初期状態では出ていない PASSED   [ 17%]
tests/e2e/test_tooltip.py::test_TC_601_1_ポインタを合わせると出る PASSED [ 17%]
tests/e2e/test_tooltip.py::test_TC_601_2_別の要素に移ると文言が変わる PASSED [ 18%]
tests/e2e/test_tooltip.py::test_TC_602_1_ポインタを外すと消える PASSED   [ 18%]
tests/e2e/test_tooltip.py::test_TC_603_1_フォーカスでも出る PASSED       [ 19%]
tests/e2e/test_tooltip.py::test_TC_603_2_フォーカスが外れると消える PASSED [ 19%]
tests/e2e/test_tooltip.py::test_TC_604_1_Escapeで消える PASSED           [ 20%]
tests/e2e/test_tooltip.py::test_TC_605_1_ポインタを受け取らない PASSED   [ 20%]
tests/e2e/test_tooltip.py::test_TC_605_2_ツールチップが出ていてもドラッグできる PASSED [ 20%]
tests/e2e/test_tooltip.py::test_TC_606_1_旧ヒントは常時表示されない PASSED [ 21%]
tests/e2e/test_tooltip.py::test_TC_606_2_旧ヒントはツールチップになっている PASSED [ 21%]
tests/e2e/test_tooltip.py::test_TC_607_1_パラメータの説明 PASSED         [ 22%]
tests/e2e/test_tooltip.py::test_TC_608_1_主要な操作の説明 PASSED         [ 22%]
tests/e2e/test_tooltip.py::test_TC_608_2_プリセットと制御点の説明 PASSED [ 23%]
tests/e2e/test_tooltip.py::test_TC_610_1_初期値はグレー PASSED           [ 23%]
tests/e2e/test_tooltip.py::test_TC_611_1_変更したものだけ色が付く PASSED [ 23%]
tests/e2e/test_tooltip.py::test_TC_611_2_mixも色が付く PASSED            [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_1_ダブルクリックでグレーに戻る PASSED [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_2_リセットで全てグレーに戻る PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_612_3_プリセットは設定したものだけ色が付く PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_613_1_フレームスライダーは常にグレー PASSED [ 26%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/005-ui-affordance
=== traceability check ===
スコープ: docs/items/005-ui-affordance （このアイテムに属するIDのみ検査）

[005-ui-affordance] 仕様 13件 / テストケース 21件

[テストコード] 検出したテストケースID: 21件 (探索起点: .)

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

[005-ui-affordance] 仕様 13件 / テストケース 21件

[テストコード] 検出したテストケースID: 235件 (探索起点: .)

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

- **005 の `spec.md` と `test-design.md` は今回の 2 コミットで変更されていない。** 変更されたのは
  `jig/index.html` の表示文言（`904147e`）で、005 の仕様のうち文言に触れるのは SPEC-606 / SPEC-607 / SPEC-608。
  13 仕様 / 21 TC は前回検証（`8840cd2`）と同数で、判定も 13 件すべて PASS のまま。
- **文言が実際に書き換わった TC は TC-606-2 と TC-607-1 の 2 件で、どちらも PASSED。**
  mix の `data-tip` は「相手の包絡をこの比率で混ぜる。f0 と ap は…」から「…fo（基本周波数）と ap は…」に、
  pitch は「再合成に使う f0 の倍率」から「再合成に使う fo（基本周波数＝声の高さ）の倍率」に変わった。
  TC-606-2 が要求する「比率で混ぜる」は mix の `data-tip` に残っており、TC-607-1 が要求する
  「9 つとも 5 文字以上・互いに異なる」も維持されている。
- frame スライダーの `data-tip` にも「（無声＝fo が 0 のフレームもある）」が加わったが、
  SPEC-608 / TC-608-1 は空でないことしか要求しておらず、判定には影響しない。PASSED。
- TC-606-1（旧ヒントが可視要素として現れない）は `get_by_text` で描画テキストを見るため、
  `data-tip` 属性に何を書いても引っかからない。今回追加された文言も属性の中にあり、影響しない。PASSED。
- **TC-601-1 / TC-601-2 / TC-603-1 / TC-603-2 は、ツールチップの文言をその要素自身の `data-tip` と比較している。**
  つまり「表示された文言が正しいか」ではなく「`data-tip` がそのまま出ているか」の検査であり、
  `data-tip` の内容がどう変わっても常に自己整合する。文言そのものの妥当性を保証するテストは無い
  （SPEC-601 も「`data-tip` の文言が表示される」としか要求していないので、仕様とテストは一致している）。
- SPEC-610〜613 は `accent-color` の R = G = B でグレーを判定する。強調色がたまたま無彩色に設定された場合、
  TC-611-1 は落ちるが TC-610-1 は通る。今回の変更とは無関係だが、色の指定を変えるときは注意が要る。
