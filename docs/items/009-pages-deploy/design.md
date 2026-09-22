# 設計: GitHub Pages への配信と CI

- アイテムID: `009-pages-deploy`
- 入力: `spec.md`（SPEC-1100〜1150）、`test-design.md`（TC-1100-1〜TC-1150-1）
- 作成日: 2026-09-22

## ファイル構成

| パス | 役割 | 新規 / 変更 |
|---|---|---|
| `engine/world/build.sh` | 成果物と一緒にスタンプ（`stamp.mjs`）を書き出すようにする | 変更 |
| `engine/world/stamp.mjs` | 成果物の SHA-256。build.sh が生成する。手で編集しない | 新規（生成物） |
| `engine/world-engine.mjs` | スタンプを読み、ブラウザでは glue と wasm を同じ印を付けた URL で読み込む | 変更 |
| `app/index.html` | WORLD のライセンスへの参照を足す | 変更 |
| `tools/verify_wasm.sh` | 照合。再ビルドしてコミット済みと比べる。ワークフローも手元もこれを呼ぶ | 新規 |
| `tools/build_site.py` | 配信物の組み立て。ワークフローも手元もこれを呼ぶ | 新規 |
| `.github/workflows/ci.yml` | 照合ジョブ・テストジョブ・デプロイジョブ | 新規 |
| `tests/test_deploy.py` | 照合と組み立てのテスト | 新規 |
| `tests/test_workflow.py` | ワークフローの YAML のテスト | 新規 |
| `tests/e2e/test_deploy_ui.py` | 成果物の対・ライセンス表示・配信物の画面 | 新規 |
| `tests/test_pages_live.py` | Pages の設定と配信 URL（配信後にしか通らない） | 新規 |
| `requirements.txt` | テストで YAML を読むため pyyaml を足す | 変更 |

## 決めたこと

- **スタンプは `.mjs` にする。** ブラウザから追加の取得なしに読めるのが要点。JSON にすると fetch が要る
- **印（URL に付ける値）は wasm の SHA-256 の先頭 12 桁。** glue と wasm の両方に同じ印を付けるので、
  スタンプが古ければ「古い対」が、新しければ「新しい対」が読み込まれる。新旧が混ざらない
- **Node では印を付けない。** Node の glue は wasm をファイルとして読むので、URL にクエリが付くと開けない。
  ブラウザ（と Worker）でだけ印を付ける。console への出力も同じ条件にする（Node のテスト出力を汚さないため）
- **配信物の `app/` と `engine/` はコピーだけで、書き換えない**（SPEC-1125）。
  そのためルートの `index.html` は「`app/` へ送るだけ」の別ファイルにする。
  アプリ本体を配信物のルートへ動かすと、`app.js` の `../engine/` の解決先が site の外になる
- **ライセンスは `third_party/world/LICENSE.txt` の位置のまま配信する。**
  画面からのリンクは `../third_party/world/LICENSE.txt` で、リポジトリでも配信物でも同じ相対位置になる
- **照合は 3 ファイル（wasm・glue・スタンプ）のバイト比較 + スタンプと成果物の突き合わせ**。
  これで「再ビルド忘れ」「成果物だけの差し替え」「スタンプの手書き換え」のどれも失敗にできる
- **CI で E2E は回さない。** Playwright の用意で 10 分を超えるため。手元で回す運用を続ける（SPEC-1150）

## ワークフローの形

```
on: [push, pull_request]        permissions: contents: read（既定）

  verify-wasm (ubuntu-24.04-arm)      test-js (ubuntu-24.04)
    tools/verify_wasm.sh                npm run test:js
            └──────────┬──────────────────────┘
                       ▼
            deploy（main への push のときだけ / pages: write, id-token: write）
              tools/build_site.py _site → upload-pages-artifact → deploy-pages
```

## タスクの順番（1 タスク = 1 回の Red → Green）

| # | タスク | 緑にする TC |
|---|---|---|
| 1 | スタンプの生成と照合スクリプト | TC-1100-1（一部）、1101-1〜2、1102-1、1103-1〜2、1104-1、1143-1 |
| 2 | 成果物の対（印付き URL・console） | TC-1140-1、1141-1、1142-1 |
| 3 | 配信物の組み立てとライセンス表示 | TC-1123-1（一部）、1124-1〜2、1125-1、1126-1、1127-1、1130-1、1131-1 |
| 4 | ワークフロー | TC-1100-1、1110-1、1111-1、1112-1〜2、1113-1、1114-1、1115-1、1120-1、1121-1、1122-1、1123-1 |
| 5 | Pages の有効化と配信（main へマージした後） | TC-1128-1、1129-1〜2、1150-1 |

タスク 5 は main へマージして配信が走るまで緑にならない。
それまで TC-1128-1 / 1129-1〜2 / 1150-1 は落ちる。**落ちたまま先へ進み、マージ後に再検証する。**

## 検証の方法

- 実装中は `npm run test:js` と `.venv/bin/pytest` を回す（照合のテストは Docker が要る）
- 完了の判断は独立検証（`agents/verifier`）が行う。タスク 5 の分は、配信後にもう一度かける
