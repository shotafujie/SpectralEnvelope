# 検証レポート: ドラッグで描くゲインカーブ

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
| PASS | 18 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 18 |

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
tests/test_curve.py::test_TC_500_2_curve省略は全0と同じ PASSED           [ 70%]
tests/test_curve.py::test_TC_501_1_要素数19は422 PASSED                  [ 70%]
tests/test_curve.py::test_TC_501_2_文字列を含むと422 PASSED              [ 70%]
tests/test_curve.py::test_TC_501_3_要素数21はバリデーションエラー PASSED [ 71%]
tests/test_curve.py::test_TC_502_1_curveのクランプ PASSED                [ 71%]
tests/test_curve.py::test_TC_503_1_ゲインはカーブどおり加算される PASSED [ 72%]
tests/test_curve.py::test_TC_503_2_API全6dBは全ビン6dB上がる PASSED      [ 72%]
tests/test_curve.py::test_TC_504_1_制御点での値と区間の線形性 PASSED     [ 72%]
tests/test_curve.py::test_TC_504_2_範囲外は端の値 PASSED                 [ 73%]
tests/test_curve.py::test_TC_505_1_curveは最後に適用される PASSED        [ 73%]
tests/test_curve.py::test_TC_505_2_curveをformantより先にすると結果が変わる PASSED [ 74%]
tests/test_curve.py::test_TC_506_1_全フレームに同じゲイン PASSED         [ 74%]
tests/test_curve.py::test_TC_506_2_foとapは変わらない PASSED             [ 75%]
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

- **004 に関わる `91c7b18` の変更はテスト名 1 件の改名だけ。**
  `tests/test_curve.py` の `test_TC_506_2_f0とapは変わらない` → `…foとapは変わらない`。
  TC ID（`TC_506_2`）は変わらず、`spec.md` / `test-design.md` は変更されていない。
  仕様 18 件 / TC 30 件は前回検証（`802aa71`）と同数で、判定も 18 件すべて PASS のまま。
- **SPEC-506 とテストの対応は保たれている。** 仕様は「`curve` はすべてのフレームに同じゲインを加え、fo と ap は変えない」、
  テストは `pyworld.synthesize` に渡る f0 / ap 配列を `curve` 省略時と要素単位で比較している。
  文書の `fo` とコードの `f0` は同じ対象を指す（001 の「表記」の除外規定）。
- 004 の E2E が描画テキストを文字列で読むのは `#curve-readout`（TC-515-1、ドラッグ中の周波数とゲインの表示）だけ。
  005 の TC-614-1 / TC-614-2 はドラッグしない状態で検査するため `#curve-readout` は非表示であり、
  **この表示の文言が `f0` を含むようになっても、005 側では検出されない**（実測は 005 のレポートの所見に記載）。
  004 側の TC-515-1 は「`round(f_7)` Hz と現在のゲイン」を含むことしか要求しないので、こちらでも検出されない。
- 005 の SPEC-608 / TC-608-2 は 20 個の制御点が空でない `data-tip` を持つことを要求しており、
  004 の SPEC-510〜520 とは観測点（`data-gain` / `cx` / `cy`）が重ならない。今回の変更の影響は無い。
- SPEC-520（分解前でもハンドルを操作できる）の TC-520-1 は、ハンドルが 20 個あること・ドラッグでゲインが 0 でなくなること・
  envelope 要求が出ないことを確認している。設定したゲインが分解後の要求に反映されるかまでは、この TC では追っていない
  （SPEC-516 / SPEC-517 が分解後の経路を押さえている）。
