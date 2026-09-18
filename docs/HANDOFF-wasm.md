# 引き継ぎ: ブラウザ単体で動かす（WASM 化）作業

作成日: 2026-09-18 / 対象: `feature/wasm-engine` ブランチでこれから進める作業

この文書だけ読めば作業を再開できるようにしてある。すでに完了した v0.1.0 の内容は `CHANGELOG.md` と `docs/items/*/` を見る。

## 1. なぜやるか

GitHub Pages で誰でも試せるようにするため、分解と再合成をブラウザ内で完結させる。
現状はサーバー（Python + pyworld）と ffmpeg が必要なので、Pages に置いても動かない。

検討した 3 案のうち **C 案（全部ブラウザで動かす）** を採る。
A 案（Python が動くホストに置く）、B 案（Pages + 手元のサーバー）は見送り。

## 2. いまの状態

- `main` は **v0.1.0** をリリース済み。https://github.com/shotafujie/SpectralEnvelope
  - 5 アイテム 149 仕様すべて PASS、テスト 238 件、受け入れ試聴 M1〜M3 合格（リビジョン `ce54387` で独立検証）
- `feature/wasm-engine` ブランチを作成済み。**まだ 1 行も実装していない**
- **Phase 0 スパイク完了（2026-09-18）**: 3 指標とも合格したので C 案で進める。結果は `docs/research/wasm-spike.md`。次は Phase 1（ADR）
- この作業のための仕様アイテム（`docs/items/006-*`）は未作成

## 3. 調べがついていること

| 項目 | 結果 |
|---|---|
| `emcc`（ローカル） | 未導入 |
| Docker | あり。`emscripten/emsdk:latest`（3.35GB）を **取得済み** |
| Node.js | v22.22.3（npm 10.9.8） |
| cmake | 4.4.3 |
| WORLD 本家 | https://github.com/mmorise/World 。修正 BSD。最新コミット `d625e76`（2025-02-21）。C++ 約 7300 行、依存なし |
| World.JS | https://github.com/YuzukiTsuru/World.JS 。MIT。Emscripten 製ラッパーで Dio / Harvest / CheapTrick / D4C / Synthesis を公開。ただし 2019 年から更新が止まり、README も「obsolete かもしれない」と断っている。関数シグネチャ・メモリの扱い・Float32/64 は未文書 |
| pyworld の Pyodide ビルド | 見つからなかった（Pyodide 経由の案は無し） |

現在の性能（ネイティブ、3 秒音声、Apple Silicon Mac の中央値）:

| 処理 | 実測 |
|---|---|
| 分解（harvest + cheaptrick + d4c） | 0.47 秒 |
| 再合成 | 0.04 秒 |

## 4. 進め方（この順で）

### Phase 0: スパイク（まずこれ。半日）

**目的**: 速度・メモリ・音質の 3 つの数字を出して、C 案が成立するか判断する。だめなら A 案に戻る。

1. WORLD を `emscripten/emsdk` でビルドし、最小の C ラッパーを通して Node から呼ぶ
2. 合成母音 3 秒（`tests/audio_fixtures.py` の `vowel()` で作った wav）で無加工往復（harvest → cheaptrick → d4c → synthesis）
3. 測る:
   - **速度**: 分解と再合成の時間。ネイティブの 1.5〜3 倍を見込む。分解が 2 秒を超えたら体験が変わるので要検討
   - **音質**: 往復後の sp と元の sp の包絡差（50〜8000Hz、有声フレーム平均）が **1.0dB 以下**か。判定コードは `tests/test_api.py` の `envelope_diff()` がそのまま使える
   - **メモリ**: sp と ap は 1 録音あたり約 10MB（601 × 1025 × 8B × 2）。10 件保持で 100MB。Float32 化の要否を決める

スパイクのコードは捨ててよい。数字だけ残す。

### Phase 1: ADR（`skills/adr`）

決めること:

1. **World.JS を使うか、本家 WORLD を自前で emcc ビルドするか**
   - 自前ビルド案: 必要な関数だけを薄い C ラッパーで公開でき、最適化フラグもこちらで決められる。更新が止まっている依存を抱えずに済む
   - World.JS 案: ビルド作業が省ける。ただし API が不明瞭で、更新が止まっている
2. **ビルド成果物（`.wasm` / glue の `.js`）をリポジトリにコミットするか、GitHub Actions で焼くか**
   - Pages で配信する以上、どこかに成果物が要る
3. **Python 版（`jig/server.py`）をどうするか**
   - 残すことを推奨。理由は 5 節
4. **数値の精度**: sp / ap を Float64 のまま扱うか Float32 に落とすか（Phase 0 のメモリと音質の数字で決める）
5. **Web Worker に載せるか**（分解中に UI を固めないため。ほぼ必須）

### Phase 2: 仕様とテスト設計の張り替え（ここが一番重い）

現在の 149 仕様のうち **約 70 件が HTTP API を前提にしている**（SPEC-001〜045、400〜411、500〜506 など）。
これを「エンジン関数」の仕様に書き直す。TC 約 240 件のうち Python 側の約 140 件を JS 側へ移す。

- 新しいアイテム `docs/items/006-wasm-engine/` を切る想定。仕様IDは **SPEC-700 以降**（`SPEC-615` まで使用済み）
- 採番済みの最大値は `grep -rho 'SPEC-[0-9]\+' docs/items | sort -u | tail -1` で確認する
- ID 規約は `docs/TRACEABILITY.md`、検査は `~/dev/.claude/hooks/trace-check.sh`

### Phase 3: 実装

| 作業 | 内容 |
|---|---|
| DSP の移植 | `formant` / `smooth` / `tilt` / `bands` / `curve` / `morph` とパラメータ解釈を JS へ。**DCT-II は FFT ベースで書く**（1025 点 × 600 フレームを O(N²) で回すと 1 フレーム 100 万回で間に合わない） |
| 入出力 | ffmpeg が不要になる。録音 blob → `decodeAudioData` → `OfflineAudioContext` で 44.1kHz モノラル化。再生は AudioBuffer 直で、WAV 生成も不要 |
| UI 改修 | `fetch("/api/...")` をエンジン呼び出しに置換。非同期は Worker 越し |

### Phase 4: Pages 配信

GitHub Actions でビルドしてデプロイ。リポジトリは公開済みなので Pages はすぐ有効にできる。

## 5. 移植を安全にやるための要点

**現在の Python 実装をゴールデンデータの生成器として残す。**

合成母音に対する `apply_params()` の出力（および harvest / cheaptrick / d4c の結果）を Python 側で書き出しておき、
JS 実装がそれと **1e-6 以内で一致する**ことをテストにする。
移植の正しさを、すでに独立検証を通った実装に紐付けられるので、鎖を切らずに移せる。

この用途があるので `jig/server.py` と Python のテストは消さないこと。

## 6. 再開するときのコマンド

```bash
cd ~/dev/speech/analyze/SpectralEnvelope
git checkout feature/wasm-engine

# 既存（Python 版）の動作確認
.venv/bin/python jig/server.py          # http://localhost:8000/
.venv/bin/pytest -q                     # 238 件・約 4 分半
~/dev/.claude/hooks/trace-check.sh      # 孤児 0 件であること

# WORLD の取得（スパイク用。スクラッチ領域は消えるので都度取り直す）
git clone --depth 1 https://github.com/mmorise/World.git /tmp/world-src
cd /tmp/world-src && git checkout d625e76

# emcc をコンテナ越しに叩く
docker run --rm -v "$PWD":/src -u $(id -u):$(id -g) emscripten/emsdk emcc --version
```

ビルドの雛形（Phase 0 で試す形）:

```bash
docker run --rm -v "$PWD":/src -u $(id -u):$(id -g) emscripten/emsdk \
  emcc -O3 -I src src/*.cpp wrapper/world_wasm.cpp -o build/world.js \
  -sMODULARIZE -sEXPORT_ES6 -sALLOW_MEMORY_GROWTH -sENVIRONMENT=web,worker,node \
  -sEXPORTED_RUNTIME_METHODS=ccall,cwrap,HEAPF64 \
  -sEXPORTED_FUNCTIONS=_malloc,_free,_world_fft_size,_world_harvest,_world_cheaptrick,_world_d4c,_world_synthesize
```

C ラッパーで公開する関数（案）:

```c
int  world_fft_size(int fs);
int  world_n_frames(int len, int fs, double frame_period);
void world_harvest(const double* x, int len, int fs, double fp, double f0_floor, double* f0, double* t);
void world_cheaptrick(const double* x, int len, int fs, double fp, const double* f0, const double* t,
                      int n_frames, int fft_size, double* sp);
void world_d4c(const double* x, int len, int fs, double fp, const double* f0, const double* t,
               int n_frames, int fft_size, double* ap);
void world_synthesize(const double* f0, const double* sp, const double* ap, int n_frames,
                      int fft_size, int fs, double fp, double* y, int y_len);
```

## 7. 判断の基準（Phase 0 の結果で決める）

| 指標 | 合格の目安 | だめなら |
|---|---|---|
| 分解の時間（3 秒音声） | 2 秒未満 | Worker + 進捗表示で許容するか、dio に落とすか、A 案に戻る |
| 包絡差（無加工往復） | 1.0dB 以下 | Float64 を維持する。それでも外れるならビルドの最適化オプションを疑う |
| メモリ（10 件保持） | 200MB 未満 | Float32 化、または保持件数を減らす |

## 8. 未決・未報告

- Pages を公開したときの扱い（録音データはブラウザ内で完結するので送信は無いが、その旨を画面に書くか）
- Python 版を将来どうするか（当面は残す）
- `~/dev/.claude/hooks/trace-check.sh` の検査 [7]（アイテムをまたいだ仕様IDの重複）は構造上機能していない。共有設定リポジトリ側の不具合で、未修正
