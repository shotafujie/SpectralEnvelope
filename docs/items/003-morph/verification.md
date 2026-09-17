# 検証レポート: 2 つの録音の包絡モーフィング

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `3e94891`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple M4 Max、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 23 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 23 |

判定の根拠は、全アイテム分をまとめた 1 回のフル実行（`213 passed, 2 warnings in 251.01s (0:04:11)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件。

- このアイテムに属する TC を含む結果行は 42 行で、すべて PASSED（`tests/test_morph.py` / `tests/e2e/test_morph_ui.py`）。内訳はテスト関数 41 個で、うち 1 個がパラメータ化されているため 1 行多い。
- その 41 個のテスト名から取り出した TC ID は 43 種類（2 個のテストが名前に 2 つの TC ID を持つ）。`test-design.md` に定義された TC も 43 件で、両方向の差はどちらも空。
- `spec.md` の 23 件の仕様には、どれも 1 件以上の TC がある。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

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

```
$ git rev-parse --short HEAD
3e94891
$ git status --porcelain
（出力なし）
```

フル実行（全アイテム分を 1 回）。下は実行ヘッダ、このアイテムに属する TC を含むテストの行（42 行、省略なし）、警告と集計行。ほかのアイテムのテストの行は各アイテムのレポートに貼った。

```
$ .venv/bin/pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 213 items

tests/e2e/test_morph_ui.py::test_TC_420_1_選択欄のラベル PASSED          [ 11%]
tests/e2e/test_morph_ui.py::test_TC_420_2_分解前の選択欄 PASSED          [ 12%]
tests/e2e/test_morph_ui.py::test_TC_421_1_新しい録音に切り替わる PASSED  [ 12%]
tests/e2e/test_morph_ui.py::test_TC_422_1_現在の録音を切り替えるとグラフとフレームが切り替わる PASSED [ 13%]
tests/e2e/test_morph_ui.py::test_TC_422_3_切り替えると無声表示も切り替わる PASSED [ 13%]
tests/e2e/test_morph_ui.py::test_TC_422_2_切り替え後のAPIと元音は選んだ録音 PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_423_1_相手なしではmorphを送らない PASSED [ 14%]
tests/e2e/test_morph_ui.py::test_TC_424_1_mixスライダー PASSED           [ 15%]
tests/e2e/test_morph_ui.py::test_TC_425_1_morphパラメータの送信 PASSED   [ 15%]
tests/e2e/test_morph_ui.py::test_TC_426_1_相手の選択でデバウンス後に1回 PASSED [ 15%]
tests/e2e/test_morph_ui.py::test_TC_426_2_mixの連続変更は最後だけ送る PASSED [ 16%]
tests/e2e/test_morph_ui.py::test_TC_427_1_相手の包絡線が描かれる PASSED  [ 16%]
tests/e2e/test_morph_ui.py::test_TC_427_2_相手なしに戻すと消える PASSED  [ 17%]
tests/e2e/test_morph_ui.py::test_TC_428_1_TC_428_2_リセットとプリセットはmixだけ戻す PASSED [ 17%]
tests/e2e/test_morph_ui.py::test_TC_429_1_mixのダブルクリックで0 PASSED  [ 18%]
tests/e2e/test_morph_ui.py::test_TC_430_1_一覧は最新10件 PASSED          [ 18%]
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

対象のテストファイル: `tests/test_morph.py` / `tests/e2e/test_morph_ui.py`

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/003-morph
=== traceability check ===
スコープ: docs/items/003-morph （このアイテムに属するIDのみ検査）

[003-morph] 仕様 23件 / テストケース 43件

[テストコード] 検出したテストケースID: 43件 (探索起点: .)

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

## 前回の検証（`c5cb26d`、SPEC-422 が FAIL）からの差分

前回の FAIL は、テストが落ちたためではなく、SPEC-422 が挙げる保証のうち「無声表示の切り替え」を観測するテストが
1 件も存在しなかったことによる（verifier の判定基準「仕様を検証するテストが存在しない」）。

`git show 3e94891` で、このアイテムについて変わったのは次の 3 点だけだと確認した。**いずれもテストと테スト設計の側の変更で、実装（`jig/`）は 1 行も変わっていない。**

- `test-design.md` に TC-422-3 を追加（現在の録音 A で無声フレームを選んで無声表示を出し、全フレーム有声の B に切り替えると無声表示が消え、フレーム表示が B の中央フレームになる）。
- `tests/e2e/test_morph_ui.py` に `test_TC_422_3_切り替えると無声表示も切り替わる` を追加。テスト本体は `#unvoiced` の可視 → 不可視の遷移と `#frame-value` を観測しており、設計どおり。
- TC-420-1 のラベル確認を「秒」という文字列の有無から `f"{a['duration']:.2f} 秒"` / `"3.00 秒"` に、TC-428-2 のプリセット確認を「太く」1 種からプリセット 5 種すべてに広げた（前回の所見 2 / 9 に対応）。

これで SPEC-422 が挙げる保証は、次のようにすべていずれかの TC が観測している。今回は PASS とした。

| SPEC-422 が挙げる保証 | 観測する TC |
|---|---|
| フレームスライダーの範囲 | TC-422-1（`max` == A の `frames` − 1） |
| フレームスライダーの値 | TC-422-1（`voiced_frames` の中央） / TC-422-3（`#frame-value`） |
| 無声表示 | TC-422-3（可視 → 不可視） |
| グラフ | TC-422-1 / TC-422-3（`#graph` の `data-id`） |
| 以降の API 呼び出しの `id` | TC-422-2（envelope 要求の `id`） |
| 元音再生の `id` | TC-422-2（`#player` の `src`） |

## 所見

判定は変えないが、記録しておくべきこと。

1. **SPEC-422 の是正はテスト側だけで行われた**: 前回 FAIL の原因は観測の欠落であり、実装は変わっていない（上の差分節を参照）。実装の振る舞いが前回から変わったことを示す観測はない。
2. **SPEC-422 の「グラフ」の観測範囲**: TC-422-1 / TC-422-3 がグラフについて見ているのは `#graph` の `data-id` だけで、包絡線の path が描き直されたことは見ていない（002 の所見 3 と同じ種類の限界）。
3. **TC-422-3 のフレーム表示の確かめ方**: 切り替え後のフレーム表示は `page.inner_text("#frame-value").startswith(str(mid))` で確かめている。前方一致なので、期待値が `25` のときに表示が `250` でも通る。フレームスライダーの値そのもの（`page.input_value("#frame")`）で確かめているのは TC-422-1 のほう。
4. **SPEC-403（API の混合式）**: TC-403-3 の期待値の作り方は、A 側と B 側で異なる。
   - A 側: 検査対象と同じ応答の `original_db` を使っている。
   - B 側: B の `original_db` をテスト側で補間して、独立に求めている。

   `original_db` そのものの正しさは、001 の TC-041-1 が独立に求めた sp と比べて確かめている。
5. **SPEC-406（f0 と ap は A のもの）**: TC-406-1 の比較相手は、同じ API を `morph` なしで呼んだときに合成へ渡った f0 / ap。001 の TC-036-1 のように、元音から harvest + d4c で独立に求めた ap とは比べていない。`morph` なしのときの ap が分解時の ap と一致することは 001 の SPEC-036 が保証しているので、2 つを合わせれば A の ap であることまで言える。
6. **SPEC-405（加工順序）**: TC-405-1 / TC-405-2 では、伸縮後の B を実装の関数 `stretch_partner` で作り、`apply_params` に渡している。つまり伸縮そのものは実装の関数に頼っている。伸縮の式が正しいことは別のテストが確かめている（TC-403-1 / TC-403-2 は関数に既知の値を与える。TC-403-3 / TC-404-1 / TC-404-2 / TC-409-1 / TC-409-2 は API の結果をテスト側で独立に補間した値と比べる）。
7. **SPEC-427（異なる色の破線）**: TC-427-1 は、computed style の stroke 色の RGB が元包絡・加工後包絡のどちらとも違うこと、`stroke-dasharray` が `none` でないことを確かめている。色の違いは RGB が完全に一致しないことだけで判定しており、見た目で区別できるほど違うかは確かめていない。
8. **SPEC-430（一覧は最新 10 件）**: TC-430-1 は、相手に選んだ 1 件目が一覧から消えた後にフレームを変えてエラー表示が空のままであることも確かめている。仕様にない確認（消えた相手の `id` を送り続けて 404 にならないこと）で、仕様より広い。
9. **SPEC-401（ratio のクランプ）**: 確かめ方は、ratio 1.5 が 1.0 と同じ結果になること、−0.5 が `morph` 省略時と同じ結果になること。クランプ後の値そのもの（パラメータ解釈の結果）は確かめていない。
10. **前回の所見 2 / 9 は解消された**: SPEC-420 のラベルの秒数（TC-420-1）と、SPEC-428 のプリセット 5 種すべて（TC-428-2）が、今回は確かめられている。
11. 実行時の警告 2 件（Starlette/httpx と anyio の DeprecationWarning）は、判定には影響しない。

