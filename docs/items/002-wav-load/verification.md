# 検証レポート: 音声ファイルの読み込み

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `c5cb26d`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --short` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple M4 Max、Python 3.13.12、pytest 9.1.1、Playwright Chromium

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 7 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 7 |

判定の根拠は、全アイテム分をまとめたフル実行の結果（`214 passed, 2 warnings in 249.20s`、終了コード 0）。出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件。

- このアイテムのテストファイル（`tests/e2e/test_load.py`）で成功したテストは 9 件。
- test-design.md に定義された TC は 9 件で、成功したテスト名から取り出したこのアイテムの TC ID も 9 種類。両方向の差は空。
- spec.md の 7 件の仕様には、どれも 1 件以上の TC がある。

## 仕様別の判定

判定行は機械的に決めた。仕様ごとに、test-design.md でその仕様に属する TC がすべて、成功したテスト名に含まれていれば PASS とした。

- **SPEC-300**: PASS (TC-300-1)
- **SPEC-301**: PASS (TC-301-1)
- **SPEC-302**: PASS (TC-302-1, TC-302-2)
- **SPEC-303**: PASS (TC-303-1)
- **SPEC-304**: PASS (TC-304-1)
- **SPEC-305**: PASS (TC-305-1, TC-305-2)
- **SPEC-306**: PASS (TC-306-1)

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
tests/e2e/test_load.py::test_TC_300_1_ファイルを開くボタンと受け付け種別 PASSED [  7%]
tests/e2e/test_load.py::test_TC_301_1_ファイル名付きで送信される PASSED  [  8%]
tests/e2e/test_load.py::test_TC_302_1_分解完了後は録音と同じ状態になる PASSED [  8%]
tests/e2e/test_load.py::test_TC_302_2_録音の後にファイルを読むとファイル側を使う PASSED [  9%]
tests/e2e/test_load.py::test_TC_303_1_送信中はボタンが無効 PASSED        [  9%]
tests/e2e/test_load.py::test_TC_304_1_録音中はファイルを開けない PASSED  [ 10%]
tests/e2e/test_load.py::test_TC_305_1_エラー時は前の録音を使い続ける PASSED [ 10%]
tests/e2e/test_load.py::test_TC_305_2_分解前のエラーでは再生ボタンは無効のまま PASSED [ 11%]
tests/e2e/test_load.py::test_TC_306_1_同じファイルを2回選べる PASSED     [ 11%]
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
$ ~/dev/.claude/hooks/trace-check.sh docs/items/002-wav-load
=== traceability check ===
スコープ: docs/items/002-wav-load （このアイテムに属するIDのみ検査）

[002-wav-load] 仕様 7件 / テストケース 9件

[テストコード] 検出したテストケースID: 9件 (探索起点: .)

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

1. **SPEC-306（同じファイルを続けて 2 回選ぶ）**: TC-306-1 はファイル選択を Playwright の `set_input_files` で行っている。
   - テストのコメントにあるとおり、実際のブラウザでは、`input[type=file]` の `value` が残っていると、同じファイルを選び直しても `change` が発火しない。
   - `set_input_files` はこの条件に関係なくイベントを発火させる。そのため、実際のファイル選択ダイアログで同じファイルを選び直す操作は再現できていない。
   - その代わりに、TC-306-1 は読み込み後に `#file` の `value` が空に戻っていることを確かめている（`assert page.eval_on_selector("#file", "el => el.value") == ""`）。これは、実ブラウザで再選択が効くための前提条件にあたる。
2. **SPEC-301（ファイルの内容の送信）**: 送信された multipart の本文は直接は観測していない。Chromium は、ファイルを含む multipart の本文を Playwright に渡さないため。代わりに次の 2 つで確かめている。
   - ページ内で `fetch` をラップし、渡された `FormData` のエントリ（キー名・ファイル名・サイズ）を記録する。
   - 分解結果の元音 WAV のサンプルが、元ファイルと一致することを確かめる。
3. **SPEC-302（グラフが有効になる）**: TC-302-1 / TC-302-2 がグラフについて確かめているのは、`#graph` の `data-id` が応答の `id` になることだけ（ヘルパ `load_file` が、この条件を満たすまで待つ）。包絡線の path が描き直されたことは直接は観測していない。
4. **SPEC-305（エラー時のメッセージ）**: 確かめたのは、分解が 400 を返す 2 つのケースで、エラー表示領域が空でないこと。
   - 0.5 秒の wav（録音で分解した後）
   - ランダムバイトの `.wav`（分解する前）

   メッセージの文言は確かめていない。
5. **SPEC-300（受け付け種別）**: TC-300-1 は、`accept` 属性に `audio/*` と `.wav` が「含まれる」ことを確かめている。仕様の「受け付け種別は `audio/*` と `.wav` である」は、ほかの種別が無いこととも読める。しかしテストは、ほかの種別が無いことまでは確かめていない。

   所見を書くために `jig/index.html` を読んだところ、実際の値は `accept="audio/*,.wav"` で、この 2 つだけだった。ただし、これはテストの結果ではない。
6. 実行時の警告 2 件（Starlette/httpx と anyio の DeprecationWarning）は、このアイテムのテストとは関係ない。
