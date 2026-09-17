# 検証レポート: ドラッグで描くゲインカーブ

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `3e94891`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple M4 Max、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 18 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 18 |

判定の根拠は、全アイテム分をまとめた 1 回のフル実行（`213 passed, 2 warnings in 251.01s (0:04:11)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件。

- このアイテムに属する TC を含む結果行は 29 行で、すべて PASSED（`tests/test_curve.py` / `tests/e2e/test_curve_ui.py`）。パラメータ化されたテストは無く、テスト関数も 29 個。
- その 29 個のテスト名から取り出した TC ID は 30 種類（`test_TC_519_1_TC_519_2_リセットとプリセットで全点0` が名前に 2 つの TC ID を持つ）。`test-design.md` に定義された TC も 30 件で、両方向の差はどちらも空。
- `spec.md` の 18 件の仕様には、どれも 1 件以上の TC がある。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

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

```
$ git rev-parse --short HEAD
3e94891
$ git status --porcelain
（出力なし）
```

フル実行（全アイテム分を 1 回）。下は実行ヘッダ、このアイテムに属する TC を含むテストの行（29 行、省略なし）、警告と集計行。ほかのアイテムのテストの行は各アイテムのレポートに貼った。

```
$ .venv/bin/pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 213 items

tests/e2e/test_curve_ui.py::test_TC_510_1_ハンドルのx位置は対数軸 PASSED [  0%]
tests/e2e/test_curve_ui.py::test_TC_511_1_初期状態は中央 PASSED          [  0%]
tests/e2e/test_curve_ui.py::test_TC_511_2_ゲインに応じたy位置 PASSED     [  1%]
tests/e2e/test_curve_ui.py::test_TC_512_1_ドラッグでゲインが変わる PASSED [  1%]
tests/e2e/test_curve_ui.py::test_TC_512_2_上下端でクランプ PASSED        [  2%]
tests/e2e/test_curve_ui.py::test_TC_512_3_ゲインは0_1dB単位 PASSED       [  2%]
tests/e2e/test_curve_ui.py::test_TC_513_1_横に動かしても周波数は変わらない PASSED [  3%]
tests/e2e/test_curve_ui.py::test_TC_514_1_ゲイン線がハンドルに追従する PASSED [  3%]
tests/e2e/test_curve_ui.py::test_TC_515_1_ドラッグ中は周波数とゲインを表示する PASSED [  4%]
tests/e2e/test_curve_ui.py::test_TC_516_1_離してから300ms後に1回送る PASSED [  4%]
tests/e2e/test_curve_ui.py::test_TC_516_2_2点を動かした後の送信内容 PASSED [  5%]
tests/e2e/test_curve_ui.py::test_TC_517_1_合成要求のcurve PASSED         [  5%]
tests/e2e/test_curve_ui.py::test_TC_518_1_ダブルクリックで0 PASSED       [  6%]
tests/e2e/test_curve_ui.py::test_TC_519_1_TC_519_2_リセットとプリセットで全点0 PASSED [  6%]
tests/e2e/test_curve_ui.py::test_TC_520_1_分解前でも操作できる PASSED    [  7%]
tests/test_curve.py::test_TC_500_1_curveの既定値は全0 PASSED             [ 66%]
tests/test_curve.py::test_TC_500_2_curve省略は全0と同じ PASSED           [ 66%]
tests/test_curve.py::test_TC_501_1_要素数19は422 PASSED                  [ 67%]
tests/test_curve.py::test_TC_501_2_文字列を含むと422 PASSED              [ 67%]
tests/test_curve.py::test_TC_501_3_要素数21はバリデーションエラー PASSED [ 68%]
tests/test_curve.py::test_TC_502_1_curveのクランプ PASSED                [ 68%]
tests/test_curve.py::test_TC_503_1_ゲインはカーブどおり加算される PASSED [ 69%]
tests/test_curve.py::test_TC_503_2_API全6dBは全ビン6dB上がる PASSED      [ 69%]
tests/test_curve.py::test_TC_504_1_制御点での値と区間の線形性 PASSED     [ 69%]
tests/test_curve.py::test_TC_504_2_範囲外は端の値 PASSED                 [ 70%]
tests/test_curve.py::test_TC_505_1_curveは最後に適用される PASSED        [ 70%]
tests/test_curve.py::test_TC_505_2_curveをformantより先にすると結果が変わる PASSED [ 71%]
tests/test_curve.py::test_TC_506_1_全フレームに同じゲイン PASSED         [ 71%]
tests/test_curve.py::test_TC_506_2_f0とapは変わらない PASSED             [ 72%]


=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 213 passed, 2 warnings in 251.01s (0:04:11) ==================
```
（終了コード 0）

対象のテストファイル: `tests/test_curve.py` / `tests/e2e/test_curve_ui.py`

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/004-gain-curve
=== traceability check ===
スコープ: docs/items/004-gain-curve （このアイテムに属するIDのみ検査）

[004-gain-curve] 仕様 18件 / テストケース 30件

[テストコード] 検出したテストケースID: 30件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```
（終了コード 0）

```
$ ~/dev/.claude/hooks/trace-check.sh
=== traceability check ===

[001-envelope-jig] 仕様 86件 / テストケース 132件

[002-wav-load] 仕様 7件 / テストケース 9件

[003-morph] 仕様 23件 / テストケース 43件

[004-gain-curve] 仕様 18件 / テストケース 30件

[テストコード] 検出したテストケースID: 214件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```
（終了コード 0）

## トレーサビリティ

`trace-check.sh` の出力から転記する。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

スクリプトの出力は「孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。」の 1 行で、
5 種類の孤児はいずれも 1 件も報告されていない。

## 前回の検証（`c5cb26d`）からの差分

`git show 3e94891` で確認した。このアイテムについて変わったのはテスト側の 1 箇所だけで、実装（`jig/`）と `spec.md` は変わっていない。

- TC-519-2 の確認対象を、プリセット「こもる」1 種からプリセット 5 種（素通し・子供っぽく・太く・こもる・のっぺり）すべてに広げた（前回の所見 7 に対応）。`test_TC_519_1_TC_519_2_リセットとプリセットで全点0` は、リセットと 5 つのプリセットのそれぞれについて、3 点を動かしてから全点が 0 に戻ることを確かめている。

## 所見

判定は変えないが、記録しておくべきこと。

1. **SPEC-510 / SPEC-511 / SPEC-512（ハンドルの座標とドラッグの逆算）**: 期待値の計算は、UI が自分で `#graph` に書き出した属性（`data-plot-left` / `data-plot-right` / `data-plot-top` / `data-plot-bottom`）を基準にしている（TC-510-1 の cx、TC-511-1 / TC-511-2 の cy、TC-512-1 などのドラッグ先 y 座標を作るヘルパ `gain_to_svg_y`）。

   次の 2 点は、テストでは確かめていない。
   - これらの属性が、実際に描かれているプロット領域（001 の包絡線・縦線の座標系）と一致しているか
   - SPEC-512 の「ポインタの y 位置に対応する値」を、UI の自己申告とは別の基準で確かめること

   001 の所見 3（SPEC-211 / SPEC-212）と同じ種類の限界。
2. **SPEC-512（逆算した値）**: TC-512-1 は、+6 dB に相当する y までドラッグした結果が 6.0 ±0.1 になることを確かめている。0.1 dB への丸め方（四捨五入か切り捨てか）は、この許容幅では区別できない。TC-512-3 が確かめているのは、値が 0.1 刻みであることだけ。
3. **SPEC-520（分解前でも操作できる）**: TC-520-1 は、分解前のドラッグで envelope 要求が出ないことも確かめている。仕様にない確認で、仕様より広い。
4. **SPEC-506（f0 と ap は変えない）**: TC-506-2 の比較相手は、同じ API を `curve` なしで呼んだときに合成へ渡った f0 / ap。独立に求めた ap とは比べていない。`curve` なしのときの ap が分解時の ap と一致することは、001 の SPEC-036 が保証している。
5. **SPEC-505（加工順序）**: TC-505-1 は、morph を含む 6 段の一括適用と逐次適用を比べている。伸縮後の B は実装の関数 `stretch_partner` で作っている（003 の所見 5 と同じ）。
   - TC-505-2 は、curve を formant より前に適用した場合と結果が違うことを確かめている。
   - curve を tilt / bands より前に置いた場合は、どれも対数領域の加算で交換可能なので結果は区別できない。したがって「curve が bands より後」という順序は、テストでは観測できない。
6. **SPEC-513（横方向の移動）**: TC-513-1 は、右へ 120px 動かした場合だけを確かめている。
   - 左への移動や、隣のハンドルと重なる位置まで動かす場合は確かめていない。
   - ハンドル 11 以降のゲインが 0 であることは確かめているが、ハンドル 9 以前は確かめていない（右に動かしたので影響するとすれば右側、という前提による）。
7. **前回の所見 7 は解消された**: SPEC-519 のプリセットは 5 種すべてが確かめられている。
8. 実行時の警告 2 件（Starlette/httpx と anyio の DeprecationWarning）は、判定には影響しない。

