# 検証レポート: ドラッグで描くゲインカーブ

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `8840cd2`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple Silicon (arm64)、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 18 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 18 |

判定の根拠は、5 アイテム分をまとめた 1 回のフル実行（`.venv/bin/pytest -v`、
`234 passed, 2 warnings in 264.65s (0:04:24)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件。

判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

設計にあって実行結果に現れない TC は全アイテムで 0 件、実行結果に現れて設計に無い TC も 0 件
（234 行の結果行から取り出した TC ID 235 種類 = 5 アイテムの設計 TC 235 件と完全一致）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

- **SPEC-500**: PASS (TC-500-1, TC-500-2)
- **SPEC-501**: PASS (TC-501-1, TC-501-2, TC-501-3)
- **SPEC-502**: PASS (TC-502-1)
- **SPEC-503**: PASS (TC-503-1, TC-503-2)
- **SPEC-504**: PASS (TC-504-1, TC-504-2)
- **SPEC-505**: PASS (TC-505-1, TC-505-2)
- **SPEC-506**: PASS (TC-506-1, TC-506-2)
- **SPEC-510**: PASS (TC-510-1)
- **SPEC-511**: PASS (TC-511-1, TC-511-2)
- **SPEC-512**: PASS (TC-512-1, TC-512-2, TC-512-3)
- **SPEC-513**: PASS (TC-513-1)
- **SPEC-514**: PASS (TC-514-1)
- **SPEC-515**: PASS (TC-515-1)
- **SPEC-516**: PASS (TC-516-1, TC-516-2)
- **SPEC-517**: PASS (TC-517-1)
- **SPEC-518**: PASS (TC-518-1)
- **SPEC-519**: PASS (TC-519-1, TC-519-2)
- **SPEC-520**: PASS (TC-520-1)

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
================= 234 passed, 2 warnings in 264.65s (0:04:24) ==================
```

終了コード: 0（実行時に `echo "EXIT=$?"` でログ末尾に記録した値）。

このアイテムに属する TC を名前に持つ結果行（上の出力からの抜粋、加工なし）:

```
tests/e2e/test_curve_ui.py::test_TC_510_1_ハンドルのx位置は対数軸 PASSED [  0%]
tests/e2e/test_curve_ui.py::test_TC_511_1_初期状態は中央 PASSED          [  0%]
tests/e2e/test_curve_ui.py::test_TC_511_2_ゲインに応じたy位置 PASSED     [  1%]
tests/e2e/test_curve_ui.py::test_TC_512_1_ドラッグでゲインが変わる PASSED [  1%]
tests/e2e/test_curve_ui.py::test_TC_512_2_上下端でクランプ PASSED        [  2%]
tests/e2e/test_curve_ui.py::test_TC_512_3_ゲインは0_1dB単位 PASSED       [  2%]
tests/e2e/test_curve_ui.py::test_TC_513_1_横に動かしても周波数は変わらない PASSED [  2%]
tests/e2e/test_curve_ui.py::test_TC_514_1_ゲイン線がハンドルに追従する PASSED [  3%]
tests/e2e/test_curve_ui.py::test_TC_515_1_ドラッグ中は周波数とゲインを表示する PASSED [  3%]
tests/e2e/test_curve_ui.py::test_TC_516_1_離してから300ms後に1回送る PASSED [  4%]
tests/e2e/test_curve_ui.py::test_TC_516_2_2点を動かした後の送信内容 PASSED [  4%]
tests/e2e/test_curve_ui.py::test_TC_517_1_合成要求のcurve PASSED         [  5%]
tests/e2e/test_curve_ui.py::test_TC_518_1_ダブルクリックで0 PASSED       [  5%]
tests/e2e/test_curve_ui.py::test_TC_519_1_TC_519_2_リセットとプリセットで全点0 PASSED [  5%]
tests/e2e/test_curve_ui.py::test_TC_520_1_分解前でも操作できる PASSED    [  6%]
tests/test_curve.py::test_TC_500_1_curveの既定値は全0 PASSED             [ 69%]
tests/test_curve.py::test_TC_500_2_curve省略は全0と同じ PASSED           [ 69%]
tests/test_curve.py::test_TC_501_1_要素数19は422 PASSED                  [ 70%]
tests/test_curve.py::test_TC_501_2_文字列を含むと422 PASSED              [ 70%]
tests/test_curve.py::test_TC_501_3_要素数21はバリデーションエラー PASSED [ 70%]
tests/test_curve.py::test_TC_502_1_curveのクランプ PASSED                [ 71%]
tests/test_curve.py::test_TC_503_1_ゲインはカーブどおり加算される PASSED [ 71%]
tests/test_curve.py::test_TC_503_2_API全6dBは全ビン6dB上がる PASSED      [ 72%]
tests/test_curve.py::test_TC_504_1_制御点での値と区間の線形性 PASSED     [ 72%]
tests/test_curve.py::test_TC_504_2_範囲外は端の値 PASSED                 [ 73%]
tests/test_curve.py::test_TC_505_1_curveは最後に適用される PASSED        [ 73%]
tests/test_curve.py::test_TC_505_2_curveをformantより先にすると結果が変わる PASSED [ 73%]
tests/test_curve.py::test_TC_506_1_全フレームに同じゲイン PASSED         [ 74%]
tests/test_curve.py::test_TC_506_2_f0とapは変わらない PASSED             [ 74%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/004-gain-curve
=== traceability check ===
スコープ: docs/items/004-gain-curve （このアイテムに属するIDのみ検査）

[004-gain-curve] 仕様 18件 / テストケース 30件

[テストコード] 検出したテストケースID: 30件 (探索起点: .)

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

- 005 による UI 変更後も、004 の 18 仕様はすべて PASS。004 に属する結果行は 29 行で全て PASSED
  （TC-519-1 と TC-519-2 が 1 つのテスト関数 `test_TC_519_1_TC_519_2_リセットとプリセットで全点0` に
  まとまっているため、行数 29 < TC 30）。
- 005 は 20 個の制御点（`circle.curve-point`）に `data-tip` を追加した。これがドラッグ操作を妨げていないことは、
  004 側の TC-512-1 / TC-512-2 / TC-513-1 / TC-518-1 の PASS と、005 側の TC-605-2
  （ツールチップを出した状態から制御点をドラッグしてゲインが変わる）の PASS の両方で確認された。
- SPEC-515 の「ドラッグ中の数値表示」（`#curve-readout`）は凡例の行に置かれている。005 は凡例を残す仕様
  （005 のスコープ「やらないこと」）なので、表示場所の衝突は起きていない。TC-515-1 は PASSED。
- SPEC-520（分解前でもハンドルを操作できる）は TC-520-1 の 1 ケースのみで、ドラッグ後に envelope 要求が
  出ないことまで含めて確認されている。
