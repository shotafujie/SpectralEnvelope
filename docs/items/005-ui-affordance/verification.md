# 検証レポート: 説明のツールチップ化とスライダーの変更表示

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
| PASS | 15 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 15 |

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
並びは `spec.md` の記載順。**今回追加された 2 件は SPEC-614 / SPEC-615**（SPEC-608 の次に置かれている）。

- **SPEC-600**: PASS (TC-600-1)
- **SPEC-601**: PASS (TC-601-1, TC-601-2)
- **SPEC-602**: PASS (TC-602-1)
- **SPEC-603**: PASS (TC-603-1, TC-603-2)
- **SPEC-604**: PASS (TC-604-1)
- **SPEC-605**: PASS (TC-605-1, TC-605-2)
- **SPEC-606**: PASS (TC-606-1, TC-606-2)
- **SPEC-607**: PASS (TC-607-1)
- **SPEC-608**: PASS (TC-608-1, TC-608-2)
- **SPEC-614**: PASS (TC-614-1, TC-614-2)
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
collecting ... collected 237 items

（中略: 237 行の結果行のうち、このアイテムに属するものを下に抜き出す）
================= 237 passed, 2 warnings in 263.25s (0:04:23) ==================
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
tests/e2e/test_tooltip.py::test_TC_611_2_mixも色が付く PASSED            [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_1_ダブルクリックでグレーに戻る PASSED [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_2_リセットで全てグレーに戻る PASSED [ 24%]
tests/e2e/test_tooltip.py::test_TC_612_3_プリセットは設定したものだけ色が付く PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_613_1_フレームスライダーは常にグレー PASSED [ 25%]
tests/e2e/test_tooltip.py::test_TC_614_2_分解前の画面にf0が無い PASSED   [ 26%]
tests/e2e/test_tooltip.py::test_TC_614_1_分解後の画面にf0が無い PASSED   [ 26%]
tests/e2e/test_tooltip.py::test_TC_615_1_分解結果の表示 PASSED           [ 27%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/005-ui-affordance
=== traceability check ===
スコープ: docs/items/005-ui-affordance （このアイテムに属するIDのみ検査）

[005-ui-affordance] 仕様 15件 / テストケース 24件

[テストコード] 検出したテストケースID: 24件 (探索起点: .)

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

### 追加された 2 仕様について

- **SPEC-614 / SPEC-615 は `91c7b18` で追加され、TC-614-1 / TC-614-2 / TC-615-1 の 3 件が新設された。
  3 件とも PASSED。** これにより 005 は 13 仕様 / 21 TC から 15 仕様 / 24 TC になった。
  `jig/index.html` は `91c7b18` では変更されていない（画面の表記は親側の `904147e` ですでに `fo` になっていた）。
  つまり今回のコミットは、すでに満たしていた状態をテストで固定したもの。
- **検証前の時点で SPEC-614 / SPEC-615 は孤児（分類 1: 検証されていない仕様）だった。**
  レポート更新前の `trace-check.sh docs/items/005-ui-affordance` は
  「孤児: 合計 2件 — 鎖が切れています」（SPEC-614 / SPEC-615）を出力し、終了コード 1 を返していた。
  本レポートで両者に判定を書いたことで 0 件になっている（上の出力は更新後のもの）。

### SPEC-614 のテストは本当にその保証を守れるか（実測）

TC-614-1 / TC-614-2 が使う `visible_f0` は、`document.body.innerText` に `f0` が含まれるか、
および `[data-tip]` 属性のいずれかに `f0` が含まれるかの 2 つだけを見る。
**この検査が「画面文言が `f0` に戻ったとき」に実際に落ちるかを、実サーバー + Chromium 上で
ページを人工的に変異させて確かめた**（検査は `visible_f0` と同一の JS。リポジトリのファイルは変更していない）。

| 変異 | 検出 |
|---|---|
| `#meta` を「3.00 秒 / 601 フレーム / 平均 f0 120.0 Hz」にする | 検出（`['text']`） |
| 先頭の説明文を「元の f0・ap で再合成」に戻す | 検出（`['text']`） |
| pitch の `data-tip` を「再合成に使う f0 の倍率」に戻す | 検出（`['tip:p-pitch']`） |
| 選択欄 `#current` の option ラベルに `f0` を入れる | 検出（`['text']`） |
| `#error`（エラー表示領域）に `f0` を入れる | 検出（`['text']`） |
| `#unvoiced` を「無声フレームです（f0 = 0）」にする（hidden のまま） | **未検出**（`[]`） |
| 同上を可視にしてから検査 | 検出（`['text']`） |
| `#curve-readout`（既定で非表示）に `f0` を入れる | **未検出**（`[]`） |
| `#meta` を大文字の「平均 F0 120.0 Hz」にする | **未検出**（`[]`） |

**結論: テストは空回りしていない。** 最も起きやすい回帰（`#meta` の「平均 fo」を `f0` に戻す、
先頭の説明文を戻す、`data-tip` を戻す）はいずれも検出される。SPEC-614 の判定は PASS で問題ない。

そのうえで、保証が届いていない範囲が 3 つある。

- **`hidden` の要素は `innerText` に現れないため検査されない。** 該当するのは
  `#unvoiced`（現在「無声フレームです（fo = 0）」）と `#curve-readout`。TC-614-1 は録音して分解し
  pitch にポインタを合わせるだけで、**無声フレームを選ぶ操作もドラッグもしない**ので、
  これらが可視になる状態を一度も作らない。`#unvoiced` は `data-tip` も持たないため、
  この文言が `f0` に戻っても TC-614-1 / TC-614-2 は通ってしまう。
  SPEC-614 は「画面に見える文言」としか書いておらず、操作の結果として見える文言を含むかは読み取れない。
- **大文字の `F0` は検出されない。** SPEC-614 は「`f0` という綴りが現れない」と書いており、
  大小を区別するかが明示されていない。テストは区別する側（小文字だけを見る）実装になっている。
- **`data-tip` 以外の属性（`title` / `aria-label` / `placeholder`）は検査されない。**
  現状これらに `f0` は無いが、SPEC-614 の「ラベル」がどこまでを指すかは仕様からは決まらない。

また、SPEC-614 は「選択欄」を明示的に対象に含めているが、`<option>` のテキストが
`document.body.innerText` に含まれるかは Chromium の実装依存である。上の実測では含まれた（検出された）ため
現状は保証できているが、テスト設計書はこの依存を書いていない。

### SPEC-615 のテストは仕様より狭い

- TC-615-1 は `#meta` のテキストに対して `"平均 fo" in meta`、`f"{f0_mean:.1f}" in meta`、`"Hz" in meta` の
  **3 つの部分文字列を独立に**検査している。SPEC-615 が求める「『平均 fo <数値> Hz』を含む」という**並び**は検査していない。
  `#meta` には「<秒> 秒 / <フレーム> フレーム」も同時に入るため、たとえば「平均 fo」と数値と「Hz」が
  ばらばらの位置に出る表示でも TC-615-1 は通る。判定は PASS だが、保証はこの分だけ弱い。
- TC-614-2（分解前のページ）は SPEC-614 の「分解の完了後」より広い範囲を検査している。
  仕様より強い方向なので害は無いが、仕様と TC の範囲は一致していない。

### 既存の 13 仕様について

- 既存の SPEC-600〜613 は 13 件すべて PASS のまま。`spec.md` の既存部分・`test-design.md` の既存部分は
  `91c7b18` で変更されておらず、追加のみ（`+6` 行 / `+9` 行）。
- TC-601-1 / TC-601-2 / TC-603-1 / TC-603-2 は、ツールチップの文言をその要素自身の `data-tip` と比較している。
  つまり「表示された文言が正しいか」ではなく「`data-tip` がそのまま出ているか」の検査であり、
  `data-tip` の内容がどう変わっても常に自己整合する。文言そのものの妥当性を保証するテストは無い
  （SPEC-601 も「`data-tip` の文言が表示される」としか要求していないので、仕様とテストは一致している）。
  ただし SPEC-614 の追加により、`data-tip` の中身に `f0` が入らないことだけは縛られるようになった。
- SPEC-610〜613 は `accent-color` の R = G = B でグレーを判定する。強調色がたまたま無彩色に設定された場合、
  TC-611-1 は落ちるが TC-610-1 は通る。今回の変更とは無関係だが、色の指定を変えるときは注意が要る。
- 前回のレポートは pytest の終了コードを記録できていなかった（zsh の `${PIPESTATUS[0]}` が空になったため）。
  今回は `echo "EXIT=$?"` をログに追記しており、`EXIT=0` を記録している。
