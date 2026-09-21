# 検証レポート: 008-browser-app（ブラウザだけで動くアプリ）

- 検証日: 2026-09-21
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `9700fb2`（ブランチ `feature/wasm-engine`、作業ツリーは clean）
- 対象仕様: `docs/items/008-browser-app/spec.md` / 対象テスト設計: `docs/items/008-browser-app/test-design.md`

前回の検証（コミット `a3a880d`）の所見を受けてテスト設計とテストコードが広がったため、
Step 1 から通して検証し直したもの。`spec.md` と実装コード（`app/` `engine/`）は
`a3a880d` から変わっていない（`git diff a3a880d 9700fb2 --stat` の対象は
`test-design.md` とテストコード 5 ファイルのみ）。

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 109 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 109 |

受け入れ試聴（M1〜M3）は仕様IDを持たず、人が耳で判定する項目のため実行していない（末尾の「受け入れ試聴」節）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

### アダプタ（画面とエンジンの境界）

- **SPEC-900**: PASS (TC-900-1)
- **SPEC-901**: PASS (TC-901-1)
- **SPEC-902**: PASS (TC-902-1, TC-902-2)
- **SPEC-903**: PASS (TC-903-1)
- **SPEC-904**: PASS (TC-904-1, TC-904-2)
- **SPEC-905**: PASS (TC-905-1)
- **SPEC-906**: PASS (TC-906-1)
- **SPEC-907**: PASS (TC-907-1, TC-907-2)
- **SPEC-908**: PASS (TC-908-1, TC-908-2)
- **SPEC-909**: PASS (TC-909-1)

### 保持

- **SPEC-910**: PASS (TC-910-1)
- **SPEC-911**: PASS (TC-911-1)
- **SPEC-912**: PASS (TC-912-1)
- **SPEC-913**: PASS (TC-913-1, TC-913-2)
- **SPEC-914**: PASS (TC-914-1, TC-914-2)
- **SPEC-915**: PASS (TC-915-1)
- **SPEC-916**: PASS (TC-916-1)
- **SPEC-917**: PASS (TC-917-1)
- **SPEC-918**: PASS (TC-918-1)

### 音声のデコード

- **SPEC-920**: PASS (TC-920-1)
- **SPEC-921**: PASS (TC-921-1)
- **SPEC-922**: PASS (TC-922-1)
- **SPEC-923**: PASS (TC-923-1)
- **SPEC-924**: PASS (TC-924-1)
- **SPEC-925**: PASS (TC-925-1)
- **SPEC-926**: PASS (TC-926-1)
- **SPEC-927**: PASS (TC-927-1, TC-927-2)
- **SPEC-928**: PASS (TC-928-1, TC-928-2, TC-928-3)
- **SPEC-929**: PASS (TC-929-1, TC-929-2)

### 画面: 録音

- **SPEC-930**: PASS (TC-930-1)
- **SPEC-931**: PASS (TC-931-1)
- **SPEC-932**: PASS (TC-932-1)
- **SPEC-933**: PASS (TC-933-1)
- **SPEC-934**: PASS (TC-934-1)
- **SPEC-935**: PASS (TC-935-1)
- **SPEC-936**: PASS (TC-936-1)
- **SPEC-937**: PASS (TC-937-1)

### 画面: ファイルの読み込み

- **SPEC-940**: PASS (TC-940-1)
- **SPEC-941**: PASS (TC-941-1)
- **SPEC-942**: PASS (TC-942-1)
- **SPEC-943**: PASS (TC-943-1)
- **SPEC-944**: PASS (TC-944-1)
- **SPEC-945**: PASS (TC-945-1, TC-945-2)
- **SPEC-946**: PASS (TC-946-1)

### 画面: 包絡グラフ

- **SPEC-950**: PASS (TC-950-1)
- **SPEC-951**: PASS (TC-951-1)
- **SPEC-952**: PASS (TC-952-1)
- **SPEC-953**: PASS (TC-953-1)
- **SPEC-954**: PASS (TC-954-1, TC-954-2)

### 画面: フレーム選択

- **SPEC-955**: PASS (TC-955-1)
- **SPEC-956**: PASS (TC-956-1)
- **SPEC-957**: PASS (TC-957-1, TC-957-2)
- **SPEC-958**: PASS (TC-958-1)

### 画面: パラメータ操作

- **SPEC-960**: PASS (TC-960-1)
- **SPEC-961**: PASS (TC-961-1)
- **SPEC-962**: PASS (TC-962-1)
- **SPEC-963**: PASS (TC-963-1)
- **SPEC-964**: PASS (TC-964-1)
- **SPEC-965**: PASS (TC-965-1)
- **SPEC-966**: PASS (TC-966-1)
- **SPEC-967**: PASS (TC-967-1, TC-967-2, TC-967-3, TC-967-4, TC-967-5)

### 画面: ゲインカーブ

- **SPEC-970**: PASS (TC-970-1)
- **SPEC-971**: PASS (TC-971-1)
- **SPEC-972**: PASS (TC-972-1, TC-972-2, TC-972-3)
- **SPEC-973**: PASS (TC-973-1)
- **SPEC-974**: PASS (TC-974-1)
- **SPEC-975**: PASS (TC-975-1)
- **SPEC-976**: PASS (TC-976-1)
- **SPEC-977**: PASS (TC-977-1)
- **SPEC-978**: PASS (TC-978-1)
- **SPEC-979**: PASS (TC-979-1, TC-979-2)
- **SPEC-980**: PASS (TC-980-1)

### 画面: モーフィング

- **SPEC-985**: PASS (TC-985-1)
- **SPEC-986**: PASS (TC-986-1)
- **SPEC-987**: PASS (TC-987-1)
- **SPEC-988**: PASS (TC-988-1)
- **SPEC-989**: PASS (TC-989-1)
- **SPEC-990**: PASS (TC-990-1)
- **SPEC-991**: PASS (TC-991-1)
- **SPEC-992**: PASS (TC-992-1, TC-992-2)
- **SPEC-993**: PASS (TC-993-1)
- **SPEC-994**: PASS (TC-994-1, TC-994-2)

### 画面: 再生・比較

- **SPEC-1000**: PASS (TC-1000-1)
- **SPEC-1001**: PASS (TC-1001-1)
- **SPEC-1002**: PASS (TC-1002-1)
- **SPEC-1003**: PASS (TC-1003-1, TC-1003-2)
- **SPEC-1004**: PASS (TC-1004-1)
- **SPEC-1005**: PASS (TC-1005-1)
- **SPEC-1006**: PASS (TC-1006-1)

### 画面: エラー表示とツールチップ

- **SPEC-1010**: PASS (TC-1010-1)
- **SPEC-1011**: PASS (TC-1011-1)
- **SPEC-1012**: PASS (TC-1012-1)
- **SPEC-1013**: PASS (TC-1013-1)
- **SPEC-1014**: PASS (TC-1014-1)
- **SPEC-1015**: PASS (TC-1015-1)
- **SPEC-1016**: PASS (TC-1016-1)
- **SPEC-1017**: PASS (TC-1017-1)
- **SPEC-1018**: PASS (TC-1018-1)
- **SPEC-1019**: PASS (TC-1019-1)
- **SPEC-1020**: PASS (TC-1020-1)
- **SPEC-1021**: PASS (TC-1021-1)
- **SPEC-1022**: PASS (TC-1022-1)
- **SPEC-1023**: PASS (TC-1023-1)

### 静的配信で動くこと

- **SPEC-1030**: PASS (TC-1030-1)
- **SPEC-1031**: PASS (TC-1031-1)

### 非機能要件

- **SPEC-1040**: PASS (TC-1040-1)
- **SPEC-1041**: PASS (TC-1041-1)
- **SPEC-1042**: PASS (TC-1042-1)
- **SPEC-1043**: PASS (TC-1043-1, TC-1043-2)


## 実行したコマンドと出力

判定の根拠。要約せず、実際の出力を貼る。

### Node テスト（保持・Float32 化の影響・情報の値）

```
$ npm run test:js

> test:js
> node --test 'tests/js/*.test.mjs'

TAP version 13
...
  ...
1..140
# tests 140
# suites 0
# pass 140
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 54259.683125

（終了コード 0。`not ok` は 0 行）
```

008 の TC を持つ Node テスト（`tests/js/store.test.mjs`）の該当行:

```
ok 73 - id は 8 文字の小文字 16 進で、分解のたびに異なる
ok 79 - 情報は fs・fftSize・frames・duration・f0Mean・voicedFrames を持つ
ok 80 - 有声フレームが無いとき f0Mean は 0 になる
ok 81 - sp と ap は Float32、f0・時刻・元の音声サンプルは Float64 のまま保持する
ok 82 - 10 秒 × 10 件の sp と ap の保持量は 170MB 未満
ok 84 - Float32 で保持した sp からの再合成音は、Float64 のままと 1e-6 以内で一致する
ok 85 - Float32 で保持した sp からの modifiedDb は、Float64 のままと 1e-3 dB 以内で一致する
```

（`ok 79` が TC-927-2 / TC-928-3、`ok 80` が TC-928-3、`ok 73` が TC-910-1、
`ok 81` が TC-915-1、`ok 82` が TC-916-1、`ok 84` が TC-917-1、`ok 85` が TC-918-1）

内訳:

```
$ grep -cE '^\s*test\(' tests/js/*.test.mjs
tests/js/engine-dsp-golden.test.mjs:10
tests/js/store.test.mjs:13
tests/js/engine-dsp-perf.test.mjs:5
tests/js/engine-dsp.test.mjs:57
tests/js/world-build.test.mjs:8
tests/js/world-engine.test.mjs:42
tests/js/world-perf.test.mjs:5
TOTAL=140
```

### Python テスト（Playwright を含むフル実行）

```
$ .venv/bin/pytest -q
.........----------------------------------------
............................................................... [ 19%]
........................................................................ [ 38%]
........................................................................ [ 58%]
........................................................................ [ 77%]
........................................................................ [ 96%]
............                                                             [100%]
=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
（中略: warnings summary は既知の 2 件）
372 passed, 2 warnings in 501.51s (0:08:21)
EXIT=0
```

1 行目の先頭に混ざっている `----------------------------------------` は、静的配信用の
テストサーバー（`ThreadingHTTPServer`）のリクエストスレッドが標準エラーへ出した区切り行で、
pytest の集計には現れていない（`372 passed` / 終了コード 0、`FAILED` / `ERROR` 行は 0 件）。

収集件数と、今回増えたテストの収集:

```
$ .venv/bin/pytest --collect-only -q | tail -1
372 tests collected in 0.06s

$ .venv/bin/pytest --collect-only -q | grep -E "TC_904_2|TC_967_3|TC_967_4|TC_967_5|TC_972_3|TC_992_2"
tests/e2e/test_adapter.py::test_TC_904_2_originalはデコードした波形と一致する
tests/e2e/test_app_morph.py::test_TC_992_2_プリセットもmixだけ戻す
tests/e2e/test_app_params.py::test_TC_967_3_太く
tests/e2e/test_app_params.py::test_TC_967_4_のっぺり
tests/e2e/test_app_params.py::test_TC_967_5_素通し
tests/e2e/test_app_params.py::test_TC_972_3_下端を超えるとクランプ
```

### トレーサビリティ検査

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/008-browser-app
=== traceability check ===
スコープ: docs/items/008-browser-app （このアイテムに属するIDのみ検査）

[008-browser-app] 仕様 109件 / テストケース 133件

[テストコード] 検出したテストケースID: 133件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。

（終了コード 0）
```

## トレーサビリティ

`trace-check.sh` の出力から転記。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |
| **合計** | | **0** |

テスト設計書の 133 件の TC はすべてテストコードに ID が埋まっている。内訳は
Python 側が 126 件（`pytest --collect-only -q` の収集済みノードのうち `test_TC_<番号>_<連番>` を
持つもの）、Node 側が 7 件（`tests/js/store.test.mjs` の TC-910-1 / 915-1 / 916-1 / 917-1 /
918-1 / 927-2 / 928-3）。008 のテストファイル 7 本の収集件数は 127 件で、うち 1 件
（`test_morphは相手の包絡に近づける`）は TC を持たない補助テスト。
スキップ・xfail は 0 件（`372 passed` / `# skipped 0`）。

## 所見

判定を左右しないが記録すべきもの。

### 前回（`a3a880d`）の所見のうち、今回のテストで塞がれたもの

いずれも追加された TC が実行され成功していることを確認した。仕様（`spec.md`）は変わっていないので、
「仕様を実装に合わせて緩めた」形跡は無い。

- **SPEC-904**: TC-904-2 が追加され、`original` の中身が「同じバイト列をその場で `decodeAudioData`
  し直した波形」と全サンプルで 1e-6 以内に一致すること、かつ /a/ と /i/ の `original` が
  互いに 1e-3 を超えて異なることを確かめている。型と長さだけの検証ではなくなった。
- **SPEC-927 / SPEC-928**: 厳密に昇順と算術平均を確かめていた `store.test.mjs` の 2 つのテストに
  TC-927-2 / TC-928-3 の ID が振られ、鎖の中に入った（テスト内容自体は前回も実行され成功していた）。
- **SPEC-967**: TC-967-3（太く）/ 967-4（のっぺり）/ 967-5（素通し）が加わり、仕様が挙げる
  5 つのプリセットすべてが検証されるようになった。
- **SPEC-972**: TC-972-3 で下端側（−12）のクランプが検証されるようになった。
- **SPEC-992**: TC-992-2 でプリセット側（mix が 0 に戻り、相手の選択は変わらない）が
  検証されるようになった。
- **SPEC-1031**: 許可する拡張子から `.f64`（`tests/golden/` の照合用データ）が外れ、
  仕様どおり HTML / JS / WASM（`.html` `.js` `.mjs` `.wasm`）のみになった。外した状態で通っている。

### 残っている、テストが仕様より狭い箇所

対応する TC は実行され成功しているが、仕様の文の一部が、実行されたどのテストでも触れられていない。

- **SPEC-964**（パラメータを連続して変えている間は 300ms のデバウンスで 1 回だけ）:
  TC-964-1 は formant のスライダーだけで確かめている。他の 7 つのスライダーは未確認
  （mix については SPEC-991 が別途確かめている）。

### 観測点についての注意（前回から変わらず）

- 再生の判定（SPEC-1000〜1005）は、アプリ自身が更新する `#player` の `data-source` /
  `data-playing` 属性を観測している。実際に音が出ているかどうかは観測していない。
- TC-904-2 の基準は `OfflineAudioContext.decodeAudioData` の出力である。つまりこのテストが
  保証するのは「保持している元音がブラウザのデコード結果と一致すること」であって、
  wav のバイト列を独立にデコードした値との一致ではない（仕様 SPEC-904 は「その分解結果の
  元の音声サンプル」としか言っていないので、仕様の範囲内ではある）。
- Python 側のフル実行の標準エラーに、静的配信用テストサーバー由来の区切り行が 1 件混ざる。
  pytest の集計には現れず、`372 passed` / 終了コード 0。

### 仕様の外で気づいたこと

- v0.1.0 の HTTP 版のテスト（`tests/test_api.py` `tests/e2e/test_ui.py` ほか）は残っており、
  今回のフル実行でも `jig/server.py` を起動して通っている。ADR-0001 の「凍結して残す」と整合する。
- `benchmarks/browser-app/baseline.json` の `synthesize_3s` の 5 サンプルのうち 1 件が 0.364 秒で、
  他の 4 件（0.072〜0.084 秒）から外れている。中央値 0.076 秒は SPEC-1042 の 1.0 秒に対して
  十分小さいので判定には影響しない（今回の TC-1042-1 も成功している）。

## 受け入れ試聴（M1〜M3）

- **未実施。** 実際の声を聴いて判定する項目であり、verifier は実行できない。
- M1（元音と無加工再合成音の声質差が聴き分けられない）、M2（母音を変えるとグラフのピーク位置が変わる）、
  M3（formant を動かすとピークが動き、再生音の声質も同じ方向に変わる）は、人が判定して
  この節に結果を追記すること。
- これらは仕様IDを持たないため、判定サマリ（109 件）には含めていない。
