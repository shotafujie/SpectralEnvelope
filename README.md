# スペクトル包絡いじり治具

その場で録音した声を WORLD で分解し、スペクトル包絡（sp）だけを加工して再合成し、元音と聴き比べる道具。
分解も再合成もブラウザの中で完結する（WORLD を WebAssembly にしてある）。

**→ https://shotafujie.github.io/SpectralEnvelope/**

![画面](docs/images/screenshot.png)

## 必要なもの

Chromium 系ブラウザだけ。上の URL を開けば動く（録音に MediaRecorder、分解に WebAssembly と Web Worker を使う）。

Safari と iOS は動作を保証しない（`docs/adr/ADR-0001-browser-world-engine.md` の追記）。

録音した音の送り先は無い。アプリが外へ出す要求は、自分自身のファイルの取得だけである（SPEC-1031）。

## 使い方

1. 「● 録音」で録音開始、もう一度押すと停止して分解（10 秒で自動停止）。「ファイルを開く」で手元の音声ファイルも読める
2. スライダーを動かすと 300ms 後に包絡グラフが更新される（ダブルクリックで初期値）
3. グラフ上の緑の点を上下にドラッグすると、任意の dB ゲインカーブを全フレームに加えられる
4. 「混ぜる相手」に別の録音を選び mix を上げると、相手の包絡が混ざる（モーフィング）
5. 「元音」「加工音」、または **Space** で交互に再生して聴き比べる

![モーフィングとゲインカーブ](docs/images/morph-and-curve.png)

加工は morph → formant → smooth → tilt → bands → ゲインカーブ の順に適用される。
pitch は再合成時に fo（基本周波数）に掛けるだけで、fo と ap は常に「現在の録音」のものを使う。
表記は Titze らの合意（下付きは oscillation の o）に従って fo とする。ただし pyworld の識別子と v0.1.0 の API の `f0_mean` は元の綴りのまま。

モーフィングでは、相手の包絡を現在の録音のフレーム数に線形に伸縮してから、mix の比率で対数領域で混ぜる。

分解結果はブラウザの中に最大 10 件まで保持し、選択欄から切り替えられる。10 秒を超える入力は先頭 10 秒だけを使う。ページを閉じると消える。

## 手元で動かす

サーバー側の処理を持たないので、静的に配信するだけでよい。

```bash
python3 -m http.server 8000     # リポジトリ直下で
```

`http://localhost:8000/app/` を開く（マイク権限のため `localhost` で開く）。

## 構成

| 場所 | 内容 |
|---|---|
| `app/` | 画面。エンジンはアダプタ（`window.engine`）越しに呼ぶ |
| `engine/` | Worker 上のエンジン。`worker.mjs` が窓口、`dsp/` が包絡の加工、`decode.mjs` が音声のデコード、`store.mjs` が分解結果の保持 |
| `engine/world/` | WORLD の WASM 成果物（`world.mjs` / `world.wasm`）とビルドスクリプト。ビルドは Docker の `emscripten/emsdk` で行う |
| `third_party/world/` | WORLD の原典（`src/` / `LICENSE.txt` / `COMMIT`） |
| `jig/` | v0.1.0 の Python サーバー版。**凍結**。照合用のゴールデンデータを作るために残してある |
| `tools/` | 配信物の組み立て（`build_site.py`）、成果物の照合（`verify_wasm.sh`）、ゴールデンデータの生成 |
| `tests/` | Python 側のテストと Playwright の E2E |
| `tests/js/` | JS 側のテスト（エンジン・DSP・保持・ビルド） |
| `benchmarks/` | 速さの基準値 |

## 速さ

3 秒の合成母音・Apple M4 Max・Chromium 153 での実測（中央値、`benchmarks/browser-app/baseline.json`）。

| 処理 | 実測 | 目標 |
|---|---|---|
| 分解（`analyze`、デコードを含む） | 0.61 秒 | < 3.0 秒（SPEC-1040） |
| つまみ → グラフ更新 | 0.35 秒 | < 1.0 秒（SPEC-1041） |
| 再合成（`synthesize`） | 0.08 秒 | < 1.0 秒（SPEC-1042） |

つまみからグラフ更新までには 300ms のデバウンスを含む（体感の待ち時間を測るため）。

## テスト

JS 側は Node 22 で回す。

```bash
npm run test:js         # 140 件（エンジン・DSP・保持・ビルド）
```

うち 2 件（`tests/js/world-build.test.mjs`）は成果物をソースから再現ビルドして突き合わせるもので、
**Docker が動いていないと落ちる**（CI では動かしている）。
`npm run test:js:ci` は CI が使うもので、性能テストだけを外す（再現ビルドは外さない）。

Python 側と E2E には v0.1.0 のセットアップが要る。

```bash
uv venv --python 3.13 .venv
VIRTUAL_ENV=$PWD/.venv uv pip install -r requirements.txt
.venv/bin/python -m playwright install chromium   # E2E 用（初回のみ）
.venv/bin/pytest                                  # 408 件
```

E2E は Chromium の偽マイクに合成母音を流して、録音から再生までを確かめる。

## 配信

`main` への push で GitHub Actions が動く（`.github/workflows/ci.yml`）。

1. **照合** — `world.wasm` と `world.mjs` をソースから再ビルドし、コミット済みのものとバイト単位で一致するか確かめる
2. **テスト** — `npm run test:js:ci`（性能テストは共有ランナーの速さに左右されるので門にしない）
3. **配信** — 両方が通ったときだけ `tools/build_site.py` で組み立てて GitHub Pages へ

配信されている `world.wasm` が、リポジトリにあるソースから作られたものだと言える状態を保つため
（`docs/adr/ADR-0002-wasm-artifact-delivery.md` の決定 4）。

## 次にやること

`docs/roadmap.md` は未作成。未実装と分かっているのは、加工結果の書き出し、時間変化する加工、DTW による時間対応付け。

## 文書

開発アイテムごとに `docs/items/<アイテム>/` に spec.md（仕様）/ test-design.md（テスト設計）/ verification.md（独立検証レポート）を置く。
006 以降は design.md（設計）も置く。

| アイテム | 内容 | 仕様ID |
|---|---|---|
| `001-envelope-jig` | 録音・分解・sp 加工・再合成・A/B 比較・包絡グラフ | SPEC-001〜261 |
| `002-wav-load` | 音声ファイルの読み込み | SPEC-300〜306 |
| `003-morph` | 2 つの録音の包絡モーフィング | SPEC-400〜430 |
| `004-gain-curve` | ドラッグで描くゲインカーブ | SPEC-500〜520 |
| `005-ui-affordance` | ツールチップと、動かしたスライダーの色付け | SPEC-600〜615 |
| `006-wasm-world` | WORLD の WASM エンジン | SPEC-700〜764 |
| `007-engine-dsp` | DSP の JS 移植 | SPEC-800〜883 |
| `008-browser-app` | Worker・保持・デコード・画面 | SPEC-900〜1043 |
| `009-pages-deploy` | GitHub Pages への配信と CI | SPEC-1100〜1150 |

技術判断は `docs/adr/` に置く（ADR-0001 ブラウザ内 WASM エンジン / ADR-0002 成果物の配布）。

元の要件からの修正点は `001-envelope-jig/spec.md` の「要件からの修正・補完」節にまとめてある。
ID の対応が切れていないかは `~/dev/.claude/hooks/trace-check.sh` で検査する。
