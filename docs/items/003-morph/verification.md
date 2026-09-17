# 検証レポート: 2 つの録音の包絡モーフィング

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `c5cb26d`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --short` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple M4 Max、Python 3.13.12、pytest 9.1.1、Playwright Chromium

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 22 |
| FAIL | 1 |
| BLOCKED | 0 |
| **仕様の総数** | 23 |

判定の根拠は、全アイテム分をまとめたフル実行の結果（`214 passed, 2 warnings in 249.20s`、終了コード 0）。出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件。

**FAIL の 1 件（SPEC-422）は、テストが落ちたことによるものではない。** 仕様が保証すると宣言した項目の一部（無声表示の切り替え）を観測するテストが存在しないことによる（verifier の判定基準「仕様を検証するテストが存在しない」に該当）。テスト出力を見ても、赤い行は無い。

- このアイテムのテストファイル（`tests/test_morph.py` / `tests/e2e/test_morph_ui.py`）で成功したテストは 42 件。
- 1 つのテスト名に 2 つの TC ID を持つパラメータ化テストが 2 つある（`test_TC_407_1_TC_407_2_...` と `test_TC_428_1_TC_428_2_...`）。どちらも 2 ケースずつで、各ケースが 1 つの TC に当たる。
- test-design.md に定義された TC は 42 件で、成功したテスト名から取り出したこのアイテムの TC ID も 42 種類。両方向の差は空。
- spec.md の 23 件の仕様には、どれも 1 件以上の TC がある。

## 仕様別の判定

判定行は機械的に決めた。仕様ごとに、test-design.md でその仕様に属する TC がすべて、成功したテスト名に含まれていれば PASS とした。この基準では 23 件すべてが PASS になる。ただし SPEC-422 は、テストを読んだ結果、仕様が挙げる保証の一部を検証するテストが存在しないことが分かったので、FAIL とした（詳細は所見 1）。

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
- **SPEC-422**: FAIL (TC-422-1, TC-422-2) — 「現在の録音」の切り替えで無声表示が切り替わることを観測するテストが無い（TC-422-1 が観測するのはフレームスライダーの `max` と値、`#graph` の `data-id` のみ。TC-422-2 は API と元音の `id` のみ）
- **SPEC-423**: PASS (TC-423-1)
- **SPEC-424**: PASS (TC-424-1)
- **SPEC-425**: PASS (TC-425-1)
- **SPEC-426**: PASS (TC-426-1, TC-426-2)
- **SPEC-427**: PASS (TC-427-1, TC-427-2)
- **SPEC-428**: PASS (TC-428-1, TC-428-2)
- **SPEC-429**: PASS (TC-429-1)
- **SPEC-430**: PASS (TC-430-1)

## 実行したコマンドと出力

```
$ git rev-parse --short HEAD
c5cb26d
$ git status --short
（出力なし）
```

フル実行（全アイテム分を 1 回）。下は、実行ヘッダ、このアイテムのテストファイルの行（省略なし）、警告と集計行。ほかのアイテムのテストの行は、それぞれのレポートに貼った。

```
$ .venv/bin/pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 214 items
...
tests/e2e/test_morph_ui.py::test_TC_420_1_選択欄のラベル PASSED          [ 12%]
tests/e2e/test_morph_ui.py::test_TC_420_2_分解前の選択欄 PASSED          [ 12%]
tests/e2e/test_morph_ui.py::test_TC_421_1_新しい録音に切り替わる PASSED  [ 13%]
tests/e2e/test_morph_ui.py::test_TC_422_1_現在の録音を切り替えるとグラフとフレームが切り替わる PASSED [ 13%]
tests/e2e/test_morph_ui.py::test_TC_422_2_切り替え後のAPIと元音は選んだ録音 PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_423_1_相手なしではmorphを送らない PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_424_1_mixスライダー PASSED           [ 14%]
tests/e2e/test_morph_ui.py::test_TC_425_1_morphパラメータの送信 PASSED   [ 15%]
tests/e2e/test_morph_ui.py::test_TC_426_1_相手の選択でデバウンス後に1回 PASSED [ 15%]
tests/e2e/test_morph_ui.py::test_TC_426_2_mixの連続変更は最後だけ送る PASSED [ 16%]
tests/e2e/test_morph_ui.py::test_TC_427_1_相手の包絡線が描かれる PASSED  [ 16%]
tests/e2e/test_morph_ui.py::test_TC_427_2_相手なしに戻すと消える PASSED  [ 17%]
tests/e2e/test_morph_ui.py::test_TC_428_1_TC_428_2_リセットとプリセットはmixだけ戻す[#reset] PASSED [ 17%]
tests/e2e/test_morph_ui.py::test_TC_428_1_TC_428_2_リセットとプリセットはmixだけ戻す[button[data-preset='\u592a\u304f']] PASSED [ 18%]
tests/e2e/test_morph_ui.py::test_TC_429_1_mixのダブルクリックで0 PASSED  [ 18%]
tests/e2e/test_morph_ui.py::test_TC_430_1_一覧は最新10件 PASSED          [ 19%]
tests/test_morph.py::test_TC_403_1_伸縮して混ぜる PASSED                 [ 86%]
tests/test_morph.py::test_TC_403_2_Aが1フレームなら相手の先頭 PASSED     [ 87%]
tests/test_morph.py::test_TC_405_1_morphは最初に適用される PASSED        [ 87%]
tests/test_morph.py::test_TC_405_2_formantを先にすると結果が変わる PASSED [ 88%]
tests/test_morph.py::test_TC_400_1_morph省略時は従来どおり PASSED        [ 88%]
tests/test_morph.py::test_TC_400_2_morph_nullは省略と同じ PASSED         [ 89%]
tests/test_morph.py::test_TC_401_1_ratio1_5は1と同じ PASSED              [ 89%]
tests/test_morph.py::test_TC_401_2_負のratioは混合なし PASSED            [ 90%]
tests/test_morph.py::test_TC_402_1_ratio0の包絡は混合なし PASSED         [ 90%]
tests/test_morph.py::test_TC_402_2_ratio0の合成は混合なしと同一 PASSED   [ 91%]
tests/test_morph.py::test_TC_403_3_APIの混合は式どおり PASSED            [ 91%]
tests/test_morph.py::test_TC_404_1_ratio1は伸縮後のB PASSED              [ 92%]
tests/test_morph.py::test_TC_404_2_Bが長くても伸縮後のB PASSED           [ 92%]
tests/test_morph.py::test_TC_406_1_f0とapはAのもの PASSED                [ 92%]
tests/test_morph.py::test_TC_406_2_合成音のf0はBに引っ張られない PASSED  [ 93%]
tests/test_morph.py::test_TC_407_1_TC_407_2_合成の長さはA[5.0] PASSED    [ 93%]
tests/test_morph.py::test_TC_407_1_TC_407_2_合成の長さはA[1.0] PASSED    [ 94%]
tests/test_morph.py::test_TC_408_1_包絡の相手が未知なら404 PASSED        [ 94%]
tests/test_morph.py::test_TC_408_2_合成の相手が未知なら404 PASSED        [ 95%]
tests/test_morph.py::test_TC_409_1_partner_dbは伸縮後のB PASSED          [ 95%]
tests/test_morph.py::test_TC_409_2_両端のフレームはBの両端 PASSED        [ 96%]
tests/test_morph.py::test_TC_409_3_ratio0でもpartner_dbを返す PASSED     [ 96%]
tests/test_morph.py::test_TC_410_1_params省略ならpartner_dbはnull PASSED [ 97%]
tests/test_morph.py::test_TC_410_2_morph以外だけならpartner_dbはnull PASSED [ 97%]
tests/test_morph.py::test_TC_411_1_自分自身との混合は混合なしと同じ PASSED [ 98%]
tests/test_morph.py::test_TC_411_2_自分自身との混合とformant PASSED      [ 98%]
...
=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 214 passed, 2 warnings in 249.20s (0:04:09) ==================
EXIT=0
```

（`EXIT=0` は、実行時に `echo "EXIT=$?"` で追記した終了コード）

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/003-morph
=== traceability check ===
スコープ: docs/items/003-morph （このアイテムに属するIDのみ検査）

[003-morph] 仕様 23件 / テストケース 42件

[テストコード] 検出したテストケースID: 42件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

注: 上の出力は、4 アイテムすべての verification.md を書き出した後に取ったもの。全体検査（引数なし）の出力は `docs/items/001-envelope-jig/verification.md` に貼った。

## トレーサビリティ

`trace-check.sh` は、孤児が 0 件の種類については行を出さず、合計行だけを出す。下の各行の値は、上の出力の「孤児: 0件」の合計行から転記したもの。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

## 所見

判定は変えないが、記録しておくべきこと。

1. **SPEC-422 の FAIL の中身（「現在の録音」を切り替えると無声表示が切り替わる）**: SPEC-422 は、切り替わるものとして次の 4 つを挙げている。
   - フレームスライダーの範囲
   - フレームスライダーの値
   - 無声表示
   - グラフ

   テストが観測しているのは次のものだけ。
   - TC-422-1: スライダーの `max` と値、`#graph` の `data-id`
   - TC-422-2: 切り替え後の envelope 要求の `id` と、元音の src

   テストコード全体を `grep -rn 'unvoiced' tests/ --include='*.py'` で調べた。無声表示（`#unvoiced`）を見ているのは、001 の TC-222-1（フレームスライダーの操作による切り替え）だけだった。「現在の録音」の切り替えによる無声表示の変化は、どのテストも観測していない。

   さらに、TC-422-1 の手順では、この遷移を観測できない。切り替え後のスライダー値は `voiced_frames` の中央（有声フレーム）なので、切り替え後の無声表示は常に隠れた状態になるからである。この遷移を観測するには、切り替え前に無声フレームを選んでおき、表示されている状態から隠れる状態に変わることを見る必要がある。

   **テストは実行されて成功しているが、仕様より狭い。** テスト設計（TC-422-1 に無声表示の確認を加える）か仕様の、どちらかを直して再検証する必要がある。
2. **SPEC-420（ラベルに長さ（秒）を含む）**: TC-420-1 は、ラベルに文字列「秒」が含まれることだけを確かめている。表示された秒数が、その録音の `duration` と一致するかは確かめていない。
3. **SPEC-403（API の混合式）**: TC-403-3 の期待値の作り方は、A 側と B 側で異なる。
   - A 側: 検査対象と同じ応答の `original_db` を使っている。
   - B 側: B の `original_db` をテスト側で補間して、独立に求めている。

   `original_db` そのものの正しさは、001 の TC-041-1 が独立に求めた sp と比べて確かめている。
4. **SPEC-406（f0 と ap は A のもの）**: TC-406-1 の比較相手は、同じ API を `morph` なしで呼んだときに合成へ渡った f0 / ap。001 の TC-036-1 のように、元音から harvest + d4c で独立に求めた ap とは比べていない。
   - `morph` なしのときの ap が分解時の ap と一致することは、001 の SPEC-036 が保証している。
   - したがって、2 つを合わせれば A の ap であることまで言える。
5. **SPEC-405（加工順序）**: TC-405-1 / TC-405-2 では、伸縮後の B を実装の関数 `stretch_partner` で作り、`apply_params` に渡している。つまり、伸縮そのものは実装の関数に頼っている。伸縮の式が正しいことは、別のテストが確かめている。
   - TC-403-1 / TC-403-2: 関数に既知の値を与えて確かめている。
   - TC-403-3 / TC-404-1 / TC-404-2 / TC-409-1 / TC-409-2: API の結果を、テスト側で独立に補間した値と比べている。
6. **SPEC-427（異なる色の破線）**: TC-427-1 は、computed style の stroke 色の RGB が、元包絡・加工後包絡のどちらとも違うこと、`stroke-dasharray` が `none` でないことを確かめている。色の違いは、RGB が完全に一致しないことだけで判定している。見た目で区別できるほど違うかは確かめていない。
7. **SPEC-430（一覧は最新 10 件）**: TC-430-1 は、相手に選んだ 1 件目が一覧から消えた後に、フレームを変えてエラー表示が空のままであることも確かめている。仕様にない確認（消えた相手の `id` を送り続けて 404 にならないこと）で、仕様より広い。
8. **SPEC-401（ratio のクランプ）**: 確かめ方は、ratio 1.5 が 1.0 と同じ結果になること、−0.5 が `morph` 省略時と同じ結果になること。クランプ後の値そのもの（パラメータ解釈の結果）は確かめていない。
9. **SPEC-428（プリセットは mix を 0 に戻す）**: 確かめたプリセットは「太く」だけ。ほかの 4 つのプリセットは確かめていない。
10. 実行時の警告 2 件（Starlette/httpx と anyio の DeprecationWarning）は、判定には影響しない。
