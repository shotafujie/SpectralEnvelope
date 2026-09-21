# 設計: ブラウザだけで動くアプリ

- アイテムID: `008-browser-app`
- 入力: `spec.md`（SPEC-900〜1043）、`test-design.md`（TC-900-1〜TC-1043-2）
- 作成日: 2026-09-21

## ファイル構成

| パス | 役割 | 新規 / 変更 |
|---|---|---|
| `engine/store.mjs` | 分解結果の保持。id の発行、入れた順に古いものから捨てる保持（10 件）、sp / ap の Float32 化。ブラウザ API を使わない純粋な JS なので Node でテストできる | 新規 |
| `engine/worker.mjs` | Worker の入口。006 のエンジンと 007 の DSP、`store.mjs` を持ち、メッセージを処理する | 新規 |
| `engine/adapter.mjs` | メインスレッド側の窓口。Worker を起動し、5 つの関数を Promise で提供する。`envelope` の取り消し（superseded）もここ | 新規 |
| `engine/decode.mjs` | 音声のバイト列を 44100Hz モノラルの Float64Array にする。`decodeAudioData` と `OfflineAudioContext` を使い、10 秒で切り詰める | 新規 |
| `app/index.html` | 画面。`jig/index.html` を写して、`fetch("/api/...")` をアダプタ呼び出しに置き換える | 新規 |
| `app/app.js` | 画面のスクリプト（`index.html` から分ける） | 新規 |
| `tests/js/store.test.mjs` | 保持と Float32 化のテスト（Node） | 新規 |
| `tests/e2e/test_adapter.py` | アダプタ・Worker・デコード・静的配信・性能（Chromium） | 新規 |
| `tests/e2e/conftest.py` ほか既存 E2E | 観測点をネットワーク要求からアダプタへ移す | 変更 |
| `benchmarks/browser-app/` | 速さの基準値 | 新規 |

`jig/index.html` と `jig/server.py` は触らない（v0.1.0 の参照実装として凍結）。新しい画面は `app/` に置く。

## 決めたこと

- **デコードはメインスレッドで行う。** `decodeAudioData` は Worker から確実には使えない。デコード後の Float64Array を Worker へ転送する（転送なのでコピーしない）
- **分解・DSP・再合成・保持は Worker の中だけ。** sp / ap はメインスレッドへ渡さない（ADR-0001 の決定 1）
- **メッセージの形**: `{ seq, name, args }` を送り、`{ seq, ok, value }` か `{ seq, ok: false, code, message }` が返る。`seq` で呼び出しと応答を対応づける
- **`envelope` の取り消し**: アダプタが最新の `seq` だけを覚え、古い応答は捨てる。古い呼び出しの Promise は `superseded` で拒否する。Worker 側では取り消さない（計算は最後まで走るが、結果は使わない）
- **保持の中身**: `{ f0, t, spF32, apF32, samples, source, duration }`。再合成のとき Float32 を Float64 に戻してから 007 の経路に渡す
- **`morph` の解決**: 相手の id から log_sp を作るのは Worker の仕事。画面は id を渡すだけ

## タスクの順番（1 タスク = 1 回の Red → Green）

| # | タスク | 緑にする TC |
|---|---|---|
| 1 | 保持（id・件数の上限・Float32 化） | TC-910-1、911-1、912-1、913-1〜2、915-1、916-1、917-1、918-1 |
| 2 | Worker とアダプタの骨組み（`analyze` / `list` / 情報の値） | TC-900-1、901-1、905-1、906-1、909-1、924-1〜929-2 |
| 3 | デコード | TC-920-1、921-1、922-1、923-1 |
| 4 | `envelope` / `synthesize` / `original` と morph の解決 | TC-902-1〜2、903-1、904-1、914-1〜2 |
| 5 | 取り消しと順序 | TC-907-1〜2、908-1〜2 |
| 6 | 画面の骨格（録音・ファイル・進行中の表示・エラー） | TC-930-1〜937-1、940-1〜946-1、1010-1 |
| 7 | グラフとフレーム選択 | TC-950-1〜958-1 |
| 8 | パラメータ操作とプリセット | TC-960-1〜967-2 |
| 9 | ゲインカーブ | TC-970-1〜980-1 |
| 10 | モーフィング | TC-985-1〜994-2 |
| 11 | 再生・比較 | TC-1000-1〜1006-1 |
| 12 | ツールチップ・色・表記 | TC-1011-1〜1023-1 |
| 13 | 静的配信と性能 | TC-1030-1、1031-1、1040-1〜1043-2 |

タスク 6 以降は、v0.1.0 の `jig/index.html` と E2E テストを土台にして移す。
**移す前に、v0.1.0 の該当テストが何を観測していたかを確認し、観測点だけを置き換える。** 判定の中身は変えない。

## 検証の方法

- 実装中は `npm run test:js` と `.venv/bin/pytest tests/e2e` を回す
- 完了の判断は独立検証（`agents/verifier`）が行う。受け入れ試聴（M1〜M3）は人が行い、結果を `verification.md` に記録する
