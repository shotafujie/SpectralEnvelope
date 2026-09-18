# 検証レポート: 2 つの録音の包絡モーフィング

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
| PASS | 23 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 23 |

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

- **SPEC-400**: PASS (TC-400-1, TC-400-2)
- **SPEC-401**: PASS (TC-401-1, TC-401-2)
- **SPEC-402**: PASS (TC-402-1, TC-402-2)
- **SPEC-403**: PASS (TC-403-1, TC-403-2, TC-403-3)
- **SPEC-404**: PASS (TC-404-1, TC-404-2)
- **SPEC-405**: PASS (TC-405-1, TC-405-2)
- **SPEC-406**: PASS (TC-406-1, TC-406-2)
- **SPEC-407**: PASS (TC-407-1, TC-407-2)
- **SPEC-408**: PASS (TC-408-1, TC-408-2)
- **SPEC-409**: PASS (TC-409-1, TC-409-2, TC-409-3)
- **SPEC-410**: PASS (TC-410-1, TC-410-2)
- **SPEC-411**: PASS (TC-411-1, TC-411-2)
- **SPEC-420**: PASS (TC-420-1, TC-420-2)
- **SPEC-421**: PASS (TC-421-1)
- **SPEC-422**: PASS (TC-422-1, TC-422-3, TC-422-2)
- **SPEC-423**: PASS (TC-423-1)
- **SPEC-424**: PASS (TC-424-1)
- **SPEC-425**: PASS (TC-425-1)
- **SPEC-426**: PASS (TC-426-1, TC-426-2)
- **SPEC-427**: PASS (TC-427-1, TC-427-2)
- **SPEC-428**: PASS (TC-428-1, TC-428-2)
- **SPEC-429**: PASS (TC-429-1)
- **SPEC-430**: PASS (TC-430-1)

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
tests/e2e/test_morph_ui.py::test_TC_420_1_選択欄のラベル PASSED          [ 10%]
tests/e2e/test_morph_ui.py::test_TC_420_2_分解前の選択欄 PASSED          [ 11%]
tests/e2e/test_morph_ui.py::test_TC_421_1_新しい録音に切り替わる PASSED  [ 11%]
tests/e2e/test_morph_ui.py::test_TC_422_1_現在の録音を切り替えるとグラフとフレームが切り替わる PASSED [ 11%]
tests/e2e/test_morph_ui.py::test_TC_422_3_切り替えると無声表示も切り替わる PASSED [ 12%]
tests/e2e/test_morph_ui.py::test_TC_422_2_切り替え後のAPIと元音は選んだ録音 PASSED [ 12%]
tests/e2e/test_morph_ui.py::test_TC_423_1_相手なしではmorphを送らない PASSED [ 13%]
tests/e2e/test_morph_ui.py::test_TC_424_1_mixスライダー PASSED           [ 13%]
tests/e2e/test_morph_ui.py::test_TC_425_1_morphパラメータの送信 PASSED   [ 14%]
tests/e2e/test_morph_ui.py::test_TC_426_1_相手の選択でデバウンス後に1回 PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_426_2_mixの連続変更は最後だけ送る PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_427_1_相手の包絡線が描かれる PASSED  [ 15%]
tests/e2e/test_morph_ui.py::test_TC_427_2_相手なしに戻すと消える PASSED  [ 15%]
tests/e2e/test_morph_ui.py::test_TC_428_1_TC_428_2_リセットとプリセットはmixだけ戻す PASSED [ 16%]
tests/e2e/test_morph_ui.py::test_TC_429_1_mixのダブルクリックで0 PASSED  [ 16%]
tests/e2e/test_morph_ui.py::test_TC_430_1_一覧は最新10件 PASSED          [ 17%]
tests/test_morph.py::test_TC_403_1_伸縮して混ぜる PASSED                 [ 88%]
tests/test_morph.py::test_TC_403_2_Aが1フレームなら相手の先頭 PASSED     [ 88%]
tests/test_morph.py::test_TC_405_1_morphは最初に適用される PASSED        [ 88%]
tests/test_morph.py::test_TC_405_2_formantを先にすると結果が変わる PASSED [ 89%]
tests/test_morph.py::test_TC_400_1_morph省略時は従来どおり PASSED        [ 89%]
tests/test_morph.py::test_TC_400_2_morph_nullは省略と同じ PASSED         [ 90%]
tests/test_morph.py::test_TC_401_1_ratio1_5は1と同じ PASSED              [ 90%]
tests/test_morph.py::test_TC_401_2_負のratioは混合なし PASSED            [ 91%]
tests/test_morph.py::test_TC_402_1_ratio0の包絡は混合なし PASSED         [ 91%]
tests/test_morph.py::test_TC_402_2_ratio0の合成は混合なしと同一 PASSED   [ 91%]
tests/test_morph.py::test_TC_403_3_APIの混合は式どおり PASSED            [ 92%]
tests/test_morph.py::test_TC_404_1_ratio1は伸縮後のB PASSED              [ 92%]
tests/test_morph.py::test_TC_404_2_Bが長くても伸縮後のB PASSED           [ 93%]
tests/test_morph.py::test_TC_406_1_f0とapはAのもの PASSED                [ 93%]
tests/test_morph.py::test_TC_406_2_合成音のf0はBに引っ張られない PASSED  [ 94%]
tests/test_morph.py::test_TC_407_1_TC_407_2_合成の長さはA[5.0] PASSED    [ 94%]
tests/test_morph.py::test_TC_407_1_TC_407_2_合成の長さはA[1.0] PASSED    [ 94%]
tests/test_morph.py::test_TC_408_1_包絡の相手が未知なら404 PASSED        [ 95%]
tests/test_morph.py::test_TC_408_2_合成の相手が未知なら404 PASSED        [ 95%]
tests/test_morph.py::test_TC_409_1_partner_dbは伸縮後のB PASSED          [ 96%]
tests/test_morph.py::test_TC_409_2_両端のフレームはBの両端 PASSED        [ 96%]
tests/test_morph.py::test_TC_409_3_ratio0でもpartner_dbを返す PASSED     [ 97%]
tests/test_morph.py::test_TC_410_1_params省略ならpartner_dbはnull PASSED [ 97%]
tests/test_morph.py::test_TC_410_2_morph以外だけならpartner_dbはnull PASSED [ 97%]
tests/test_morph.py::test_TC_411_1_自分自身との混合は混合なしと同じ PASSED [ 98%]
tests/test_morph.py::test_TC_411_2_自分自身との混合とformant PASSED      [ 98%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/003-morph
=== traceability check ===
スコープ: docs/items/003-morph （このアイテムに属するIDのみ検査）

[003-morph] 仕様 23件 / テストケース 43件

[テストコード] 検出したテストケースID: 43件 (探索起点: .)

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

- **今回の変更は説明文の綴りだけ。** `spec.md` はスコープの「B の fo・ap の利用」と SPEC-406 の本文、
  `test-design.md` は方針の 1 行と SPEC-406 の見出し・TC-406-1 / TC-406-2 の説明文が `f0` → `fo` に変わった。
  混合の式・許容差（1e-6、±5%）・観測対象（`pyworld.synthesize` のスパイ）は変わっていない。
  仕様 23 件 / TC 43 件は前回検証（`8840cd2`）と同数で、判定も 23 件すべて PASS のまま。
- **SPEC-406 とテストの対応は保たれている。** 仕様は「再合成に使う fo と ap は A のもの（fo は A の fo × pitch）」、
  テストは `test_TC_406_1_f0とapはAのもの` / `test_TC_406_2_合成音のf0はBに引っ張られない` で、
  観測しているのは `pyworld.synthesize` に渡る f0 配列そのもの。`spec.md`（001）の「表記」が pyworld の識別子を
  除外しているため、`fo`（文書）と `f0`（コード）は同じ対象を指す。
- 画面文言の変更のうち 003 に関わるのは mix スライダーの `data-tip` だが、003 の仕様は mix について
  範囲・刻み・初期値・数値表示（SPEC-424）とダブルクリック（SPEC-429）を要求しているだけで、説明文には触れていない。
  TC-424-1 / TC-429-1 は値と `#mix-value` のテキストを観測しており、いずれも PASSED。
- TC-422-3（`tests/e2e/test_morph_ui.py:62`）は `#unvoiced` の可視・不可視だけを見ているため、
  「無声フレームです（fo = 0）」への文言変更では落ちない。PASSED。
- SPEC-420 は選択欄のラベルが「通し番号・入力元・長さ（秒）を含む」ことを求めており、
  TC-420-1 はこれを option のテキストで検査している。今回の文言変更はこのラベルには及んでいない。
