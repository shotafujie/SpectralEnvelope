# スペクトル包絡いじり治具

その場で録音した声を WORLD（pyworld）で分解し、スペクトル包絡（sp）だけを加工して再合成し、元音と聴き比べるローカルツール。

## 必要なもの

- Python 3.13 / [uv](https://github.com/astral-sh/uv)
- ffmpeg（ブラウザの webm/opus 録音をデコードするため。`brew install ffmpeg`）
- Chromium 系ブラウザ（マイク録音に MediaRecorder を使う）

## 起動

```bash
uv venv --python 3.13 .venv
VIRTUAL_ENV=$PWD/.venv uv pip install -r requirements.txt
.venv/bin/python jig/server.py            # --port で変更可（既定 8000）
```

`http://localhost:8000/` を開く（マイク権限のため `localhost` で開く）。サーバーは 127.0.0.1 だけで待ち受ける。

## 使い方

1. 「● 録音」で録音開始、もう一度押すと停止して分解（10 秒で自動停止）
2. スライダーを動かすと 300ms 後に包絡グラフが更新される（ダブルクリックで初期値）
3. 「元音」「加工音」、または **Space** で交互に再生して聴き比べる

加工は formant → smooth → tilt → bands の順に適用される。pitch は再合成時に f0 に掛けるだけで、ap は変更しない。

## テスト

```bash
.venv/bin/python -m playwright install chromium   # E2E 用（初回のみ）
.venv/bin/pytest                                  # 全件（約 2 分）
.venv/bin/pytest tests/test_dsp.py tests/test_api.py   # UI 以外
```

E2E は Chromium の偽マイクに合成母音を流して、録音から再生までを確かめる。

## 文書

- 仕様: `docs/items/001-envelope-jig/spec.md`（元の要件からの修正点は「要件からの修正・補完」節）
- テスト設計: `docs/items/001-envelope-jig/test-design.md`
- 検証レポート: `docs/items/001-envelope-jig/verification.md`
