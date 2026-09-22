# ブラウザ版の速さの基準値

分解（`analyze`）・つまみからグラフ更新まで・再合成（`synthesize`）の速さ。
仕様は `docs/items/008-browser-app/spec.md` の SPEC-1040〜1043。

計測はブラウザの中で行う（Worker と WASM を通した実際の経路を測るため）。

## 計測コマンド

```bash
.venv/bin/python benchmarks/browser-app/run.py          # 計測して表示するだけ
.venv/bin/python benchmarks/browser-app/run.py --write  # 基準値（baseline.json）を上書きする
```

## 基準値

`baseline.json` を見る。計測条件（CPU、Chromium のバージョン、入力、方法）も同じファイルにある。
上書きするのは、意図して速度が変わる変更をしたときだけにする。

`envelope_after_slider` には 300ms のデバウンスが含まれる（体感の待ち時間を測るため）。
