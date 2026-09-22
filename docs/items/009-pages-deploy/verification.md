# 検証レポート: 009-pages-deploy（GitHub Pages への配信と CI）

- 検証日: 2026-09-22
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `03c8de9`（ブランチ `fix/pages-live-test`、作業ツリーは clean）
- 対象仕様: `docs/items/009-pages-deploy/spec.md` / 対象テスト設計: `docs/items/009-pages-deploy/test-design.md`

`main` との差分はテストコード 2 ファイルの各 1 行のみ（`git diff --stat main...HEAD` は
`tests/e2e/test_deploy_ui.py | 1 +` と `tests/e2e/test_pages_live.py | 1 +`）。
実装・ワークフロー・配信物の組み立ては `main` と同一である。

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 28 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 28 |

環境はすべて利用できた（Docker 29.6.1 aarch64、`gh` は shotafujie で認証済み、
配信 URL へのインターネット接続あり）。BLOCKED とした仕様は無い。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

### 照合

- **SPEC-1100**: PASS (TC-1100-1)
- **SPEC-1101**: PASS (TC-1101-1, TC-1101-2)
- **SPEC-1102**: PASS (TC-1102-1)
- **SPEC-1103**: PASS (TC-1103-1, TC-1103-2)
- **SPEC-1104**: PASS (TC-1104-1)

### ワークフロー

- **SPEC-1110**: PASS (TC-1110-1)
- **SPEC-1111**: PASS (TC-1111-1)
- **SPEC-1112**: PASS (TC-1112-1, TC-1112-2, TC-1112-3)
- **SPEC-1113**: PASS (TC-1113-1)
- **SPEC-1114**: PASS (TC-1114-1)
- **SPEC-1115**: PASS (TC-1115-1)

### 配信

- **SPEC-1120**: PASS (TC-1120-1)
- **SPEC-1121**: PASS (TC-1121-1)
- **SPEC-1122**: PASS (TC-1122-1)
- **SPEC-1123**: PASS (TC-1123-1)
- **SPEC-1124**: PASS (TC-1124-1, TC-1124-2)
- **SPEC-1125**: PASS (TC-1125-1)
- **SPEC-1126**: PASS (TC-1126-1)
- **SPEC-1127**: PASS (TC-1127-1)
- **SPEC-1128**: PASS (TC-1128-1)
- **SPEC-1129**: PASS (TC-1129-1, TC-1129-2)

### ライセンス

- **SPEC-1130**: PASS (TC-1130-1)
- **SPEC-1131**: PASS (TC-1131-1)

### 成果物の対

- **SPEC-1140**: PASS (TC-1140-1)
- **SPEC-1141**: PASS (TC-1141-1)
- **SPEC-1142**: PASS (TC-1142-1)
- **SPEC-1143**: PASS (TC-1143-1)

### 非機能要件

- **SPEC-1150**: PASS (TC-1150-1)

## 実行したコマンドと出力

判定の根拠。テストは対象を選ばず、プロジェクトのテストコマンドをフルで実行した。

### Node テスト（全件）

```
$ npm run test:js
（140 件すべて ok。TAP の各行は省略せず実行し、末尾の集計は以下）
1..140
# tests 140
# suites 0
# pass 140
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 55553.657625

$ npm run test:js >/dev/null 2>&1; echo "test:js exit=$?"
test:js exit=0
```

### pytest（全件）

```
$ .venv/bin/pytest -q
........................................................................ [ 17%]
........................................................................ [ 35%]
........................................................................ [ 52%]
........................................................................ [ 70%]
........................................................................ [ 88%]
................................................                         [100%]
=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
408 passed, 2 warnings in 591.71s (0:09:51)
pytest exit=0
```

skipped / xfail は 0 件。全 408 件が実行され成功した。

### このアイテムのテストの内訳（仕様単位の判定の根拠）

```
$ .venv/bin/pytest -v tests/test_deploy.py tests/test_workflow.py tests/e2e/test_deploy_ui.py tests/e2e/test_pages_live.py
tests/test_deploy.py::test_TC_1100_1_照合スクリプトがあり実行できる PASSED [  2%]
tests/test_deploy.py::test_TC_1101_2_照合とビルドが同じイメージを指している PASSED [  5%]
tests/test_deploy.py::test_TC_1101_1_再ビルドしてコミット済みと一致する PASSED [  8%]
tests/test_deploy.py::test_TC_1102_1_一致すれば成功する PASSED           [ 11%]
tests/test_deploy.py::test_TC_1103_1_wasmが違えば失敗する PASSED         [ 13%]
tests/test_deploy.py::test_TC_1103_2_glueが違えば失敗する PASSED         [ 16%]
tests/test_deploy.py::test_TC_1104_1_スタンプが食い違えば失敗する PASSED [ 19%]
tests/test_deploy.py::test_TC_1143_1_buildがスタンプを書き出す PASSED    [ 22%]
tests/test_deploy.py::test_TC_1123_1_組み立てスクリプトが出力先を作る PASSED [ 25%]
tests/test_deploy.py::test_TC_1124_1_配信物の中身 PASSED                 [ 27%]
tests/test_deploy.py::test_TC_1124_2_ビルド用のファイルは入らない PASSED [ 30%]
tests/test_deploy.py::test_TC_1125_1_appとengineはリポジトリと同一 PASSED [ 33%]
tests/test_deploy.py::test_TC_1126_1_余計なものが入らない PASSED         [ 36%]
tests/test_deploy.py::test_TC_1130_1_ライセンス文が入る PASSED           [ 38%]
tests/test_workflow.py::test_TC_1110_1_pushとpull_requestで起動する PASSED [ 41%]
tests/test_workflow.py::test_TC_1111_1_照合ジョブはarm64ランナー PASSED  [ 44%]
tests/test_workflow.py::test_TC_1100_1_ワークフローが照合スクリプトを呼ぶ PASSED [ 47%]
tests/test_workflow.py::test_TC_1112_1_テストジョブがNodeテストを実行する PASSED [ 50%]
tests/test_workflow.py::test_TC_1112_2_Nodeテストは失敗すると0以外で終わる PASSED [ 52%]
tests/test_workflow.py::test_TC_1113_1_外部actionはSHAで固定されている PASSED [ 55%]
tests/test_workflow.py::test_TC_1114_1_pull_request_targetを使わない PASSED [ 58%]
tests/test_workflow.py::test_TC_1115_1_既定の権限はcontents_readだけ PASSED [ 61%]
tests/test_workflow.py::test_TC_1120_1_デプロイはmainへのpushのときだけ PASSED [ 63%]
tests/test_workflow.py::test_TC_1121_1_デプロイは照合とテストの成功が条件 PASSED [ 66%]
tests/test_workflow.py::test_TC_1122_1_書き込み権限はデプロイジョブだけ PASSED [ 69%]
tests/test_workflow.py::test_TC_1123_1_ワークフローが組み立てスクリプトを呼ぶ PASSED [ 72%]
tests/test_workflow.py::test_TC_1112_3_性能テストは対象から外れている PASSED [ 75%]
tests/e2e/test_deploy_ui.py::test_TC_1140_1_wasmのURLに印が入る PASSED   [ 77%]
tests/e2e/test_deploy_ui.py::test_TC_1141_1_glueのURLにも同じ印が入る PASSED [ 80%]
tests/e2e/test_deploy_ui.py::test_TC_1142_1_スタンプの値がconsoleに出る PASSED [ 83%]
tests/e2e/test_deploy_ui.py::test_TC_1127_1_ルートを開くとアプリになる PASSED [ 86%]
tests/e2e/test_deploy_ui.py::test_TC_1131_1_画面からライセンスをたどれる PASSED [ 88%]
tests/e2e/test_pages_live.py::test_TC_1128_1_Pagesの配信元はActions PASSED [ 91%]
tests/e2e/test_pages_live.py::test_TC_1129_1_配信URLが200を返す PASSED   [ 94%]
tests/e2e/test_pages_live.py::test_TC_1129_2_配信URLでファイルを読み込んで再生できる PASSED [ 97%]
tests/e2e/test_pages_live.py::test_TC_1150_1_CIは10分未満 PASSED         [100%]
================== 36 passed, 2 warnings in 62.97s (0:01:02) ===================
exit=0
```

設計された TC は 34 件、テスト関数は 36 件。差の 2 件は TC-1100-1 と TC-1123-1 が
「スクリプトが存在する」側（`test_deploy.py`）と「ワークフローが呼んでいる」側（`test_workflow.py`）に
分かれているためで、どちらも同じ TC-ID を指している。

### 実配信の状態（読み取りのみ）

```
$ curl -s -o /dev/null -w "%{http_code}\n" https://shotafujie.github.io/SpectralEnvelope/
200

$ gh api repos/shotafujie/SpectralEnvelope/pages --jq '{build_type, status, html_url, source}'
{"build_type":"workflow","html_url":"https://shotafujie.github.io/SpectralEnvelope/","source":{"branch":"main","path":"/"},"status":null}

$ gh api "repos/shotafujie/SpectralEnvelope/actions/workflows/ci.yml/runs?branch=main&status=success&per_page=1" --jq '.workflow_runs[0] | {id, head_sha, created_at, conclusion}'
{"conclusion":"success","created_at":"2026-09-22T03:50:48Z","head_sha":"fb504c3a20970bc1d58db37ac12dcbf915df536c","id":35684646660}

$ gh api repos/shotafujie/SpectralEnvelope/actions/runs/35684646660/timing
{"billable":{"UBUNTU":{"total_ms":0,"jobs":3,"job_runs":[{"job_id":106608772497,"duration_ms":0},{"job_id":106608772707,"duration_ms":0},{"job_id":106609144502,"duration_ms":0}]}},"run_duration_ms":141000}
```

`run_duration_ms` は 141000 ミリ秒（2.35 分）。

### トレーサビリティ検査

```
$ bash ~/dev/.claude/hooks/trace-check.sh docs/items/009-pages-deploy
=== traceability check ===
スコープ: docs/items/009-pages-deploy （このアイテムに属するIDのみ検査）

[009-pages-deploy] 仕様 28件 / テストケース 34件

[テストコード] 検出したテストケースID: 34件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
trace exit=0
```

## トレーサビリティ

`trace-check.sh` の出力から転記した。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

（`trace-check.sh` は孤児 0 件のカテゴリを出力しない。上表の 0 は「合計 0 件」という
最終行と、どのカテゴリの見出しも出力されていないことから転記している。）

なお、この検証レポートを書き出す前に同じコマンドを実行したときは
`[1] 検証されていない仕様: 28件 (verification.md が未作成)` で合計 28 件だった。
これは検証前の状態であって、検証結果ではない。

## 所見

判定を左右しないが、記録しておくべきもの。

### 1. 実配信のテストが見ているのは HEAD ではなく `main` の配信物

TC-1128-1 / TC-1129-1 / TC-1129-2 / TC-1150-1 は GitHub と配信 URL の**現在の状態**を見る。
今そこにあるのは `main`（`fb504c3`）から配信されたもので、検証対象の `03c8de9` そのものではない。
`03c8de9` の差分はテストコード 2 行だけなので配信物は同一だが、
「テストが通った時点の配信物 = 対象コミットの配信物」が常に成り立つ構造ではない。
この 4 件は、コミットの性質ではなくクラウド側の現況を観測している。

### 2. SPEC-1150 のテストはジョブではなくワークフロー実行全体を測っている

仕様は「照合ジョブとテストジョブを合わせた」時間だが、TC-1150-1 が読む `run_duration_ms` は
デプロイジョブを含むワークフロー実行全体の時間である。仕様より広い範囲を測っているので、
通ったことは仕様の充足を含む（今回 2.35 分）。仕様どおりの範囲を測りたければ
ジョブ単位の時間を合算する必要がある。

### 3. TC-1112-2 は作業ツリーに一時ファイルを書いて消す

`tests/js/zz-temporary-failing.test.mjs` を `tests/js/` に書き出し、`finally` で消している。
実行が途中で中断されるとリポジトリに残る。今回の実行後は `git status --porcelain` が空で、
残留は無いことを確認した。

### 4. SPEC-1141 の「同じスタンプの値」は wasm 側のハッシュで確かめている

TC-1141-1 は `world.mjs` の URL に、`world.mjs` 自身の SHA-256 ではなく
`world.wasm` の SHA-256 の先頭 12 桁が入っていることを確かめている。
新旧の混在を防ぐという SPEC-1141 の目的（1 つの値で対を縛る）には合致しているが、
仕様の文面「同じスタンプの値」がどちらのハッシュを指すかは明示されていない。

### 5. 性能テストは CI の門から外れているが、手元では実行されている

SPEC-1112 / TC-1112-3 のとおり `npm run test:js:ci` は `*-perf.test.mjs` を除く。
一方この検証では `npm run test:js` をフルで実行しており、性能テスト
（`engine-dsp-perf` / `world-perf`）も含めて 140 件すべてが成功している。
つまり CI の門から外したことによる見落としは、この検証の時点では発生していない。

## 受け入れの目安について

`spec.md` の「受け入れの目安」（人が配信 URL を開いて耳で確かめる）は仕様 ID を持たず、
自動テストで代替できる項目ではないため、この検証では実行していない。
機械で確かめられる範囲は SPEC-1129（TC-1129-1 / TC-1129-2）が覆っており、
配信 URL 上でファイル読み込みから加工音の再生開始までが動くことは確認済みである。
