# WORLD エンジンの速度の基準値

ADR-0001 の決定 5: WORLD やビルドの入力を変えて再ビルドしたら、ここの基準値の 1.5 倍以内であることを確かめる。

## 計測コマンド

```bash
node benchmarks/wasm-world/run.mjs          # 計測して表示するだけ
node benchmarks/wasm-world/run.mjs --write  # 基準値（baseline.json）を上書きする
```

## 基準値

`baseline.json` を見る。計測条件（CPU、Node のバージョン、入力、方法）も同じファイルに記録してある。
基準値を上書きするのは、意図して速度が変わる変更をしたときだけにする。
