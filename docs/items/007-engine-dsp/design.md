# 設計: DSP の JS 移植

- アイテムID: `007-engine-dsp`
- 入力: `spec.md`（SPEC-800〜883）、`test-design.md`（TC-800-1〜TC-883-2）
- 作成日: 2026-09-21

## ファイル構成

| パス | 役割 | 新規 / 変更 |
|---|---|---|
| `engine/dsp/params.mjs` | パラメータの解釈（初期値・クランプ・丸め・形式の検査） | 新規 |
| `engine/dsp/curves.mjs` | 周波数軸のゲイン: tilt、bands の G(f)、curve の C(f) | 新規 |
| `engine/dsp/smooth.mjs` | 正規直交 DCT-II による平滑化（次数 M 未満だけを計算する） | 新規 |
| `engine/dsp/envelope.mjs` | 包絡の加工（morph → formant → smooth → tilt → bands → curve）、伸縮、1 フレーム分の dB 列 | 新規 |
| `engine/render.mjs` | 再合成の経路（006 のエンジンを呼ぶ）。`{ y, f0, sp, ap }` を返す | 新規 |
| `tools/make_golden_dsp.py` | 照合用データの生成（`jig/server.py` の関数を使う） | 新規 |
| `tests/golden/dsp-*.f64`、`dsp-meta.json` | 照合用データ | 新規 |
| `tests/js/dsp-ref.mjs` | テスト側の独立計算（素朴な DCT-II / IDCT、補間、G(f)、C(f)、伸縮） | 新規 |
| `tests/js/engine-dsp.test.mjs`、`engine-dsp-golden.test.mjs`、`engine-dsp-perf.test.mjs` | テスト | 新規 |
| `tests/test_golden_dsp.py` | 生成スクリプトの再現性とメタデータ | 新規 |
| `benchmarks/engine-dsp/run.mjs`、`baseline.json`、`README.md` | 速さの基準値 | 新規 |

## 計算の方針

- **対数領域**: 加工はすべて `log_sp = ln(sp + 1e-12)` の上で行い、最後に `exp` で戻す（001 と同じ）。dB のゲインは `gain_db · ln(10) / 10` を加算する
- **平滑化**: `cos(π(2k+1)m / (2F))` の表を M × F だけ作り、係数 m < M を求めてから同じ表で戻す。M ≤ 80 なので 1 フレーム `2·M·F` 回の積和。表はエンジンの生成時ではなく、M ごとに遅延して作り、同じ M の間は使い回す
- **周波数軸のゲイン**: tilt / bands / curve は、フレームに依らず同じ 1025 要素のゲイン列になる（004 の SPEC-506 と同じ）。params ごとに 1 回だけ作り、全フレームに加算する
- **formant**: ビン位置 `k / r` の線形補間。`k / r > F − 1` のビンは最終ビンの値
- **伸縮**: フレーム方向の線形補間。相手の log_sp をそのまま受け取り、A のフレーム数に合わせる
- **引数は書き換えない**: 加工は新しい配列に書き出す（SPEC-831）

## タスクの順番（1 タスク = 1 回の Red → Green）

| # | タスク | 緑にする TC |
|---|---|---|
| 1 | パラメータの解釈 | TC-800-1〜TC-810-3 |
| 2 | 周波数軸のゲイン（tilt / bands / curve）と、テスト側の独立計算 | TC-825-1〜TC-827-2 |
| 3 | formant | TC-821-1〜TC-822-1 |
| 4 | 平滑化 | TC-823-1、TC-823-2、TC-824-1 |
| 5 | 伸縮と morph | TC-828-1、TC-835-1〜TC-838-1、TC-871-1、TC-872-1、TC-873-1〜2 |
| 6 | 加工の組み立て（順序・不変・異常系） | TC-820-1、TC-829-1〜2、TC-830-1、TC-831-1、TC-870-1 |
| 7 | 1 フレーム分の dB 列 | TC-840-1〜TC-847-3 |
| 8 | 再合成の経路 | TC-850-1〜TC-855-1 |
| 9 | 照合用データの生成スクリプトとデータ | TC-863-1、TC-864-1〜2 |
| 10 | Python 版との照合 | TC-860-1、TC-861-1、TC-862-1 |
| 11 | 性能と基準値 | TC-880-1〜TC-883-2 |

タスク 9 で Python 版と食い違いが出たら、原因が実装側か照合用データ側かを切り分ける。
**実装に合わせて仕様や照合用データを直さない。** v0.1.0 の仕様が正。

## 検証の方法

- 実装中は `npm run test:js` と該当の pytest を回す
- 完了の判断は独立検証（`agents/verifier`）が行い、`verification.md` を書く
