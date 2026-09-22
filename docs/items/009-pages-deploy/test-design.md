# テスト設計書: GitHub Pages への配信と CI

- アイテムID: `009-pages-deploy`
- 仕様書: `docs/items/009-pages-deploy/spec.md`
- 作成日: 2026-09-22

## テスト方針

| レベル | 対象 | 置き場所 | 実行コマンド |
|---|---|---|---|
| スクリプト | 照合・配信物の組み立て | `tests/test_deploy.py` | `.venv/bin/pytest tests/test_deploy.py` |
| 静的解析 | ワークフローの YAML | `tests/test_workflow.py` | `.venv/bin/pytest tests/test_workflow.py` |
| ブラウザ | 成果物の対・ライセンス表示・配信物の画面 | `tests/e2e/test_deploy_ui.py` | `.venv/bin/pytest tests/e2e/test_deploy_ui.py` |
| 実配信 | Pages の設定と配信 URL | `tests/e2e/test_pages_live.py` | `.venv/bin/pytest tests/e2e/test_pages_live.py` |

### 観測点

- 照合と組み立ては**スクリプトの終了コードと出力**で観測する。ワークフローからも手元からも同じスクリプトを呼ぶので、
  スクリプトを直接叩けば CI を待たずに確かめられる
- ワークフローの仕様（権限・トリガ・SHA 固定）は、YAML を読んで構造として確かめる。
  「CI が実際に緑だったか」は別の問いで、GitHub 側の実行結果で見る
- 成果物の対（ハッシュ付き URL）は、ブラウザが出したネットワーク要求の URL と console の出力で観測する
- 配信 URL の仕様（SPEC-1128、1129）は、**main へマージして配信が走るまで確かめられない**。
  それまでは落ちる。これは実装漏れではなく、配信がまだ起きていないという事実を表す

### 入力

- 照合の失敗系は、`engine/world` のコピーを作って 1 バイト書き換えたものを渡す（コミット済みの成果物は触らない）
- ブラウザのテストは 008 と同じ静的配信のサーバーと `ui_page` / `app_page` を使う

## テストケース

### SPEC-1100 照合は 1 つのスクリプトで実行できる

- **TC-1100-1** `tools/verify_wasm.sh` が存在して実行可能であり、ワークフローの YAML がそのパスを呼んでいる

### SPEC-1101 照合は固定したイメージで再ビルドする

- **TC-1101-1** `tools/verify_wasm.sh` を引数なしで実行 → 終了コード 0（Docker で再ビルドし、コミット済みと一致する）
- **TC-1101-2** `tools/verify_wasm.sh` と `engine/world/build.sh` が参照するイメージのダイジェストが同一である

### SPEC-1102 一致すれば成功する

- **TC-1102-1** `engine/world` をコピーしたディレクトリを `--built` で渡す → 終了コード 0

### SPEC-1103 一致しなければ失敗する

- **TC-1103-1** コピーの `world.wasm` を 1 バイト変えて渡す → 終了コード 0 以外で、出力に `world.wasm` が現れる
- **TC-1103-2** コピーの `world.mjs` を 1 バイト変えて渡す → 終了コード 0 以外で、出力に `world.mjs` が現れる

### SPEC-1104 スタンプと成果物が食い違えば失敗する

- **TC-1104-1** コピーのスタンプの SHA-256 を書き換えて渡す → 終了コード 0 以外

### SPEC-1110 push と pull_request で起動する

- **TC-1110-1** ワークフローの `on` に `push` と `pull_request` の両方がある

### SPEC-1111 照合ジョブは arm64 ランナー

- **TC-1111-1** 照合ジョブの `runs-on` が `ubuntu-24.04-arm`

### SPEC-1112 テストジョブは性能テストを除く Node テストを実行する

- **TC-1112-1** テストジョブのいずれかのステップが `npm run test:js:ci` を実行している
- **TC-1112-2** `npm run test:js:ci` が、1 件でも失敗したとき 0 以外で終わる（失敗するテストを一時ファイルで足して確かめる）
- **TC-1112-3** `npm run test:js:ci` の対象に `tests/js/*-perf.test.mjs` が含まれず、それ以外の `tests/js/*.test.mjs` はすべて含まれる

### SPEC-1113 外部の action は SHA で固定されている

- **TC-1113-1** `uses:` の値がすべて `@` の後ろに 40 桁の 16 進を持つ

### SPEC-1114 `pull_request_target` を使わない

- **TC-1114-1** ワークフローの YAML に `pull_request_target` が現れない

### SPEC-1115 既定の権限は contents: read だけ

- **TC-1115-1** トップレベルの `permissions` が `{contents: read}` と一致する

### SPEC-1120 デプロイは main への push のときだけ

- **TC-1120-1** デプロイジョブの `if` が、`refs/heads/main` への `push` に限っている

### SPEC-1121 デプロイは照合とテストの成功が条件

- **TC-1121-1** デプロイジョブの `needs` が、照合ジョブとテストジョブの両方を含む

### SPEC-1122 書き込み権限はデプロイジョブだけ

- **TC-1122-1** `pages: write` と `id-token: write` を持つジョブがデプロイジョブだけである

### SPEC-1123 組み立ては 1 つのスクリプトで実行できる

- **TC-1123-1** `tools/build_site.py` を実行すると出力先ディレクトリができ、ワークフローの YAML が同じパスを呼んでいる

### SPEC-1124 配信物の中身

- **TC-1124-1** 組み立てた結果のファイル一覧が、ルートの `index.html`・`app/` の 2 ファイル・`engine/` の JS と WASM・`third_party/world/LICENSE.txt` と完全に一致する
- **TC-1124-2** 配信物に `engine/world/build.sh` と `engine/world/wrapper.cpp` が含まれない

### SPEC-1125 app と engine はリポジトリと同一

- **TC-1125-1** 配信物の `app/` と `engine/` の各ファイルが、リポジトリの同じ位置のファイルとバイト単位で一致する

### SPEC-1126 余計なものが入らない

- **TC-1126-1** 配信物に `tests`・`docs`・`jig`・`benchmarks`・`third_party/world/src`・`.git` で始まるパスが 1 つも無い

### SPEC-1127 ルートの index.html はアプリへ送る

- **TC-1127-1** 配信物のルートを静的配信して `/` を開く → アプリの画面（`#rec` と `#graph`）が表示される

### SPEC-1128 Pages の配信元は Actions

- **TC-1128-1** `gh api repos/shotafujie/SpectralEnvelope/pages` の `build_type` が `workflow`

### SPEC-1129 配信 URL でアプリが動く

- **TC-1129-1** 配信 URL が 200 を返し、本文に `app/` への参照がある
- **TC-1129-2** 配信 URL をブラウザで開いてファイルを読み込む → 包絡が描かれ、加工音の再生が始まる

### SPEC-1130 ライセンス文が配信物に入る

- **TC-1130-1** 配信物の `third_party/world/LICENSE.txt` が、リポジトリのものとバイト単位で一致する

### SPEC-1131 画面にライセンスへの参照がある

- **TC-1131-1** 画面に WORLD の名前を含む文言があり、ライセンス文へのリンクの `href` が配信物の中で 200 になる

### SPEC-1140 wasm の URL にハッシュが入る

- **TC-1140-1** アプリを開いたときのネットワーク要求のうち `world.wasm` のものが、スタンプの SHA-256 の先頭 12 桁を URL に含む

### SPEC-1141 glue も同じ値で読み込まれる

- **TC-1141-1** `world.mjs` の要求も同じ 12 桁を URL に含む

### SPEC-1142 スタンプの値が console に出る

- **TC-1142-1** エンジンの読み込み後、console の出力にスタンプの値が 1 回現れる

### SPEC-1143 スタンプは build.sh が書き出す

- **TC-1143-1** 出力先を一時ディレクトリにして `engine/world/build.sh` を実行 → そこにスタンプができ、中の SHA-256 が出力された成果物のものと一致する

### SPEC-1150 CI は 10 分未満

- **TC-1150-1** 直近の main への push に対するワークフローの実行時間が 10 分未満である

## 網羅性の確認

- [x] `spec.md` の全 SPEC-ID が、この文書に見出しとして現れている
- [x] 各ケースが「入力 → 期待する観測結果」の形で書けている
- [x] 異常系（照合の失敗、スタンプの食い違い）に対応するケースがある
- [ ] `trace-check.sh` の [2] [5] が 0 件（テストコードを書いた後に確認する）
