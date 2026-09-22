# DSP の速さの基準値

包絡の加工（`applyEnvelope`）と 1 フレーム分の dB 列（`envelopeAt`）の速さ。
仕様は `docs/items/007-engine-dsp/spec.md` の SPEC-880〜883。

## 計測コマンド

```bash
node benchmarks/engine-dsp/run.mjs          # 計測して表示するだけ
node benchmarks/engine-dsp/run.mjs --write  # 基準値（baseline.json）を上書きする
```

## 基準値

`baseline.json` を見る。計測条件（CPU、Node のバージョン、入力、パラメータ、方法）も同じファイルにある。
上書きするのは、意図して速度が変わる変更をしたときだけにする。
