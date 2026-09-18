# 検証レポート: 説明のツールチップ化とスライダーの変更表示

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `ce54387`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple Silicon (arm64)、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2
- 検証の観点: `ce54387` で SPEC-614 / SPEC-615 の文言が厳しくなり（SPEC-614 は「そのとき非表示の要素の文言」と
  「大文字小文字を問わず」を明示、SPEC-615 は「この並びで」を明示）、対応するテスト
  （`tests/e2e/test_tooltip.py`）も変わった。その追加・変更分の判定と、既存の保証が壊れていないかの判定。
  レポートは今回の実行結果で全体を書き直している。

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 15 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 15 |

判定の根拠は、5 アイテム分をまとめた 1 回のフル実行（`.venv/bin/pytest -v`、
`238 passed, 2 warnings in 264.81s (0:04:24)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件（結果行 238 行の内訳が `{'PASSED': 238}`）。

判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
   1 つのテスト名が 2 つ以上の TC を持つ場合（`test_TC_234_1_TC_234_2_…`）と、
   1 つの TC が複数のパラメータ化行に分かれる場合の両方を、この規則で扱う。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

設計にあって実行結果に現れない TC は全アイテムで 0 件、実行結果に現れて設計に無い TC も 0 件
（238 行の結果行から取り出した TC ID 239 種類 = 5 アイテムの設計 TC 239 件と完全一致）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。
並びは `spec.md` の記載順。**今回変わったのは SPEC-614 / SPEC-615 の 2 件**（SPEC-614 に TC-614-3 が新設された）。

- **SPEC-600**: PASS (TC-600-1)
- **SPEC-601**: PASS (TC-601-1, TC-601-2)
- **SPEC-602**: PASS (TC-602-1)
- **SPEC-603**: PASS (TC-603-1, TC-603-2)
- **SPEC-604**: PASS (TC-604-1)
- **SPEC-605**: PASS (TC-605-1, TC-605-2)
- **SPEC-606**: PASS (TC-606-1, TC-606-2)
- **SPEC-607**: PASS (TC-607-1)
- **SPEC-608**: PASS (TC-608-1, TC-608-2)
- **SPEC-614**: PASS (TC-614-1, TC-614-2, TC-614-3)
- **SPEC-615**: PASS (TC-615-1)
- **SPEC-610**: PASS (TC-610-1)
- **SPEC-611**: PASS (TC-611-1, TC-611-2)
- **SPEC-612**: PASS (TC-612-1, TC-612-2, TC-612-3)
- **SPEC-613**: PASS (TC-613-1)

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
collecting ... collected 238 items

（中略: 238 行の結果行のうち、このアイテムに属するものを下に抜き出す）
================= 238 passed, 2 warnings in 264.81s (0:04:24) ==================
EXIT=0
```

このアイテムに属する TC を名前に持つ結果行（上の出力からの抜粋、加工なし）:

```
tests/e2e/test_tooltip.py::test_TC_600_1_初期状態では出ていない PASSED   [ 17%]
tests/e2e/test_tooltip.py::test_TC_601_1_ポインタを合わせると出る PASSED [ 17%]
tests/e2e/test_tooltip.py::test_TC_601_2_別の要素に移ると文言が変わる PASSED [ 18%]
tests/e2e/test_tooltip.py::test_TC_602_1_ポインタを外すと消える PASSED   [ 18%]
tests/e2e/test_tooltip.py::test_TC_603_1_フォーカスでも出る PASSED       [ 18%]
tests/e2e/test_tooltip.py::test_TC_603_2_フォーカスが外れると消える PASSED [ 19%]
tests/e2e/test_tooltip.py::test_TC_604_1_Escapeで消える PASSED           [ 19%]
tests/e2e/test_tooltip.py::test_TC_605_1_ポインタを受け取らない PASSED   [ 20%]
tests/e2e/test_tooltip.py::test_TC_605_2_ツールチップが出ていてもドラッグできる PASSED [ 20%]
tests/e2e/test_tooltip.py::test_TC_606_1_旧ヒントは常時表示されない PASSED [ 21%]
tests/e2e/test_tooltip.py::test_TC_606_2_旧ヒントはツールチップになっている PASSED [ 21%]
tests/e2e/test_tooltip.py::test_TC_607_1_パラメータの説明 PASSED         [ 21%]
tests/e2e/test_tooltip.py::test_TC_608_1_主要な操作の説明 PASSED         [ 22%]
tests/e2e/test_tooltip.py::test_TC_608_2_プリセットと制御点の説明 PASSED [ 22%]
tests/e2e/test_tooltip.py::test_TC_610_1_初期値はグレー PASSED           [ 23%]
tests/e2e/test_tooltip.py::test_TC_611_1_変更したものだけ色が付く PASSED [ 23%]
tests/e2e/test_tooltip.py::test_TC_611_2_mixも色が付く PASSED            [ 23%]
tests/e2e/test_tooltip.py::test_TC_612_1_ダブルクリックでグレーに戻る PASSED [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_2_リセットで全てグレーに戻る PASSED [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_3_プリセットは設定したものだけ色が付く PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_613_1_フレームスライダーは常にグレー PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_614_2_分解前の画面にf0が無い PASSED   [ 26%]
tests/e2e/test_tooltip.py::test_TC_614_1_分解後の画面にf0が無い PASSED   [ 26%]
tests/e2e/test_tooltip.py::test_TC_614_3_無声表示とドラッグ中とエラー表示にもf0が無い PASSED [ 26%]
tests/e2e/test_tooltip.py::test_TC_615_1_分解結果の表示 PASSED           [ 27%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/005-ui-affordance
=== traceability check ===
スコープ: docs/items/005-ui-affordance （このアイテムに属するIDのみ検査）

[005-ui-affordance] 仕様 15件 / テストケース 25件

[テストコード] 検出したテストケースID: 25件 (探索起点: .)

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

[005-ui-affordance] 仕様 15件 / テストケース 25件

[テストコード] 検出したテストケースID: 239件 (探索起点: .)

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

（`trace-check.sh` は孤児が 0 件の分類を個別に出力しないため、合計「孤児: 0件」からの転記。
上の出力はレポート書き直し後のもの。書き直し前の同じコマンドの出力も「孤児: 0件」・終了コード 0 だった。）

## 所見

仕様とテスト設計を読んだうえで気づいたこと。判定を左右しないが記録すべきもの。

### 今回変わった範囲

`ce54387` が変えたのは 3 ファイルだけ（`git show --stat ce54387`）。

- `docs/items/005-ui-affordance/spec.md`（±2 行）— SPEC-614 は「分解の完了後、画面に見える文言（本文・ラベル・
  選択欄・ツールチップ）に `f0` という綴りが現れない」から「画面に出うる文言（… そのとき非表示の要素の文言を含み、
  スクリプトとスタイルの中身は除く）に、大文字小文字を問わず …」へ。SPEC-615 は「「平均 fo <数値> Hz」を含む」から
  「「平均 fo <`f0_mean` を小数 1 桁にした数値> Hz」を**この並びで**含む」へ。
- `docs/items/005-ui-affordance/test-design.md`（+3 / −2 行）— TC-614-1 の文言を新しい仕様に合わせ、TC-614-3 を新設、
  TC-615-1 を正規表現一致に書き換え。
- `tests/e2e/test_tooltip.py`（+30 / −15 行）— `visible_f0` を `f0_hits` に置き換え、TC-614-3 を追加、TC-615-1 を
  `re.search` に変更。

**実装（`jig/index.html` / `jig/server.py`）は `ce54387` では 1 行も変わっていない。**
`jig/index.html` に残る `f0` は 1 箇所だけで、`<script>` の中のテンプレート文字列
（`info.f0_mean` — API の応答フィールド名）。これは新しい SPEC-614 が明示的に除外している範囲で、
001 の「共通の定義」の「表記」とも整合している。つまり今回のコミットは、すでに満たしていた状態を
より厳しい検査で固定し直したもの。

### 新しい検査は前回見つかった穴を塞いだか（実測）

前回（`91c7b18`）の本レポートは、旧 `visible_f0` が **3 つの回帰を検出できない**ことを実測で記録していた
（hidden の `#unvoiced`、hidden の `#curve-readout`、大文字の `F0`）。新しい仕様の文言はこの 3 つを名指しで
検査範囲に入れている。**そこで今回も、`f0_hits` と同一の JS を実サーバー + Chromium 上のページに対して
実行し、ページを人工的に変異させて検出されるかを確かめた**（リポジトリのファイルは変更していない）。

| 変異 | `f0_hits` の結果 | 検出 |
|---|---|---|
| `#meta` を「… 平均 f0 120.0 Hz」に戻す（小文字） | `['text:meta']` | 検出 |
| `#meta` を「… 平均 F0 120.0 Hz」にする（大文字） | `['text:meta']` | **検出（前回は未検出）** |
| `#unvoiced` を「無声フレームです（f0 = 0）」にする（hidden のまま） | `['text:unvoiced']` | **検出（前回は未検出）** |
| `#curve-readout`（既定で非表示）に `f0` を入れる | `['text:curve-readout']` | **検出（前回は未検出）** |
| `#error`（エラー表示領域、空）に `f0` を入れる | `['text:error']` | 検出 |
| pitch の `data-tip` を「再合成に使う f0 の倍率」に戻す | `['tip:p-pitch']` | 検出 |
| `#current` の option ラベルに `f0` を入れる | `['text:OPTION']` | 検出 |
| 見出し `h1` の文言に `F0` を入れる | `['text:H1']` | 検出 |
| `body` の直下の子テキストノードに `f0` を入れる | `[]` | **未検出** |
| `#rec` の `title` 属性に `f0` を入れる | `[]` | **未検出** |
| `#graph` の `aria-label` に `f0` を入れる | `[]` | **未検出** |
| `script` の中身に `f0` を入れる（仕様が除外する範囲） | `[]` | 未検出（仕様どおり） |
| `style` の中身に `f0` を入れる（仕様が除外する範囲） | `[]` | 未検出（仕様どおり） |
| （対照）何も変異させない | `[]` | — |

**前回記録した 3 つの穴は 3 つとも塞がった。** あわせて、前回「Chromium の `innerText` が `<option>` の
テキストを含むかに依存している」と書いた点も解消している。新しい `f0_hits` は要素を直接走査して
テキストノードを見るため、`innerText` の挙動に依存しない（上表の `text:OPTION` が実測）。

残っている範囲外は 3 つで、いずれも仕様の文言からは是非が決まらない。

- **`body` の直下の子テキストノードは検査されない。** `f0_hits` は `document.body.querySelectorAll('*')` で
  得た各要素の `childNodes` しか見ないため、`body` 自身の子テキストノードを一度も訪れない。
  現状の `jig/index.html` に該当する文字列は無い。
- **`data-tip` 以外の属性（`title` / `aria-label` / `placeholder` / `alt`）は検査されない。**
  SPEC-614 の「ラベル」がどこまでを指すかは仕様から決まらない。現時点で該当する文字列は無い
  （`grep -inE '(title|aria-label|placeholder|alt)="[^"]*f0' jig/index.html` は一致なし、終了コード 1）ので、
  現に守られていない箇所があるという話ではなく、検査範囲が仕様の文言より狭い可能性があるという話。
  `#graph` は `aria-label="元の包絡と加工後の包絡"` を実際に持っており、画面読み上げに出る文言ではある。
- **スクリプトが後から挿入する文言は、その状態を作ったときしか検査されない。**
  TC-614-3 が無声表示・ドラッグ中の表示・API エラー表示の 3 状態を明示的に作るようになったのは前進だが、
  網羅の根拠は「代表的な状態を列挙した」ことであって、全状態ではない。

### SPEC-615 の検査

- TC-615-1 は `re.search(rf"平均 fo {info['f0_mean']:.1f} Hz", page.inner_text("#meta"))` になり、
  SPEC-615 が今回明示した「**この並びで**」は実際に検査されるようになった。
  「平均 fo」「数値」「Hz」がばらばらの位置にあっても通っていた前回の弱さは解消している
  （実測: `'平均 fo 120.5Hz'` と `'Hz 120.5 平均 fo'` はいずれも不一致）。
- ただし **パターン中の小数点がエスケープされていない**ため、`.` は任意の 1 文字に一致する。
  実測で `'平均 fo 120x5 Hz'` がこのパターンに一致する。値の一致がこの分だけ緩い。
  今回のコミットで加わった「並び」の保証そのものは効いている。
- TC-614-2（分解前のページ）は、SPEC-614 が「分解の完了後」の限定を外したことで、仕様と範囲が一致した
  （前回は仕様より広い検査だった）。

### 既存の 13 仕様について

- SPEC-600〜613 は 13 件すべて PASS のまま。`spec.md` / `test-design.md` の該当部分は `ce54387` で
  変更されておらず、`tests/e2e/test_tooltip.py` の変更もファイル末尾の「基本周波数の表記」節に閉じている。
- TC-601-1 / TC-601-2 / TC-603-1 / TC-603-2 は、ツールチップの文言をその要素自身の `data-tip` と比較しており、
  「`data-tip` がそのまま出ているか」の検査である。`data-tip` の内容そのものの妥当性を保証するテストは無い
  （SPEC-601 も「`data-tip` の文言が表示される」としか要求していないので、仕様とテストは一致している）。
  SPEC-614 の強化により、`data-tip` の中身に `f0` / `F0` が入らないことは縛られる。
- SPEC-610〜613 は `accent-color` の R = G = B でグレーを判定する。強調色がたまたま無彩色に設定された場合、
  TC-611-1 は落ちるが TC-610-1 は通る。今回の変更とは無関係だが、色の指定を変えるときは注意が要る。
- TC-614-3 は 1 つのテスト関数の中で 3 つの状態（無声表示・ドラッグ中・API エラー）を順に作って
  同じ検査を 3 回行う。どれか 1 つで落ちた場合、pytest の結果行からはどの状態で落ちたかは分からない。
