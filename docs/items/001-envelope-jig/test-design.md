# テスト設計書: スペクトル包絡いじり治具

- アイテムID: `001-envelope-jig`
- 仕様書: `docs/items/001-envelope-jig/spec.md`
- 作成日: 2026-09-16

## テスト方針

| レベル | 対象 | 置き場所 | 協調者 |
|---|---|---|---|
| ユニット | sp 加工関数・パラメータ解釈・WAV 化 | `tests/test_dsp.py` | 本物の numpy / scipy。テストダブルなし |
| 統合 | HTTP API（分解・合成・包絡・保持） | `tests/test_api.py` | FastAPI TestClient + 本物の pyworld / ffmpeg |
| 性能 | SPEC-120/121 | `tests/test_perf.py` | TestClient。3 回計測の中央値 |
| 起動 | SPEC-122 | `tests/test_serve.py` | サブプロセスで起動して `lsof` で待ち受けアドレスを見る |
| E2E | UI | `tests/e2e/test_ui.py` | Playwright Chromium + 実サーバー（サブプロセス）+ 偽マイク（合成母音 wav） |

- **テスト入力**: マイク録音は使わない。`tests/audio_fixtures.py` が合成母音（倍音加算、既知フォルマント）を生成する。webm は ffmpeg（libopus）でその wav から作る。
- **観測点**:
  - 合成に使った f0 / sp / ap は `pyworld.synthesize` をスパイして観測する。記録したうえで本物に委譲する。
  - UI の再生状態は、単一の `<audio>` 要素の `data-source`（`original` / `processed`）と `paused` / `currentTime` で観測する。
  - グラフは SVG の要素と属性で観測する。
- **E2E の Chromium フラグ**:
  - `--use-fake-ui-for-media-stream`
  - `--use-fake-device-for-media-stream`
  - `--use-file-for-fake-audio-capture=<合成母音wav>`
  - `--autoplay-policy=no-user-gesture-required`
- **API 呼び出しの観測**: `page.on("request")` で記録する。応答待ちの状態は `page.route` で応答を遅らせて作る。

## テストケース

### SPEC-001 webm/opus を分解して必要なキーを返す

- **TC-001-1** 合成母音 3 秒を webm/opus 化して送る → 200、JSON に `id, fs, duration, frames, fft_size, f0_mean, voiced_frames` が全て含まれる
- **TC-001-2** 同 webm の `duration` → 3.0 ±0.1 秒

### SPEC-002 wav を 44100Hz モノラルに変換して分解する

- **TC-002-1** 22050Hz ステレオ 2 秒の wav → 200、`duration` 2.0 ±0.01、元音 WAV が 44100Hz・1ch
- **TC-002-2** 44100Hz モノラル 16bit の wav → 200、元音 WAV のサンプルが入力と一致

### SPEC-003 fs と fft_size

- **TC-003-1** 任意の分解応答 → `fs` == 44100、`fft_size` == 2048
- **TC-003-2** 48000Hz 入力でも `fs` == 44100

### SPEC-004 duration の定義

- **TC-004-1** 44100Hz・132300 サンプルの wav → `duration` == 3.0
- **TC-004-2** 44100Hz・66150 サンプルの wav → `duration` == 1.5

### SPEC-005 frames の定義

- **TC-005-1** 3 秒 wav → `frames` == `pyworld.harvest` を同じ信号にかけた f0 の要素数（601）
- **TC-005-2** 包絡 API で `frame = frames − 1` → 200（最終フレームが存在する）

### SPEC-006 voiced_frames の定義

- **TC-006-1** 合成母音の前後 0.5 秒を無音にした wav → `voiced_frames` が昇順、先頭 0 付近と末尾付近のフレームを含まない、各要素のフレームで f0 > 0（合成に渡る f0 で確認）
- **TC-006-2** 同入力 → `voiced_frames` の要素数 == 合成に渡る f0 の f0 > 0 の数

### SPEC-007 f0_mean の定義

- **TC-007-1** f0 ≈120Hz の合成母音 → `f0_mean` が 120 ±6
- **TC-007-2** デジタル無音 2 秒（有声フレームなし）→ `f0_mean` == 0 かつ `voiced_frames` == []
- **TC-007-3** 前後無音付き合成母音 → `f0_mean` == 合成に渡る f0 のうち f0 > 0 の要素の平均（1e-6 以内）

### SPEC-008 id の形式と一意性

- **TC-008-1** 分解応答の `id` → 正規表現 `^[0-9a-f]{8}$` に一致
- **TC-008-2** 同じ音声を 5 回分解 → `id` が 5 つとも異なる

### SPEC-009 1.0 秒未満は 400

- **TC-009-1** 0.5 秒の wav → 400、`detail` が空でない文字列
- **TC-009-2** ちょうど 1.0 秒（44100 サンプル）の wav → 200

### SPEC-010 10.0 秒超は切り詰め

- **TC-010-1** 12 秒の wav → 200、`duration` == 10.0、元音 WAV が 441000 サンプル
- **TC-010-2** ちょうど 10.0 秒の wav → `duration` == 10.0

### SPEC-011 デコード不能は 400

- **TC-011-1** ランダムバイト 1KB → 400、`detail` が空でない文字列
- **TC-011-2** 空ファイル → 400

### SPEC-012 audio フィールド欠落は 422

- **TC-012-1** multipart で別名フィールド `file` のみ送る → 422

### SPEC-013 11 件目で最古を破棄

- **TC-013-1** 11 回分解 → 1 件目の `id` で original / synthesize / envelope がいずれも 404
- **TC-013-2** 11 回分解 → 2 件目の `id` で original が 200

### SPEC-014 10 件目までは保持

- **TC-014-1** 10 回分解 → 1 件目〜10 件目すべての `id` で original が 200

### SPEC-020 元音 WAV の形式

- **TC-020-1** original → 200、`content-type` が `audio/wav`、soundfile で読むと subtype PCM_16・1ch・44100Hz

### SPEC-021 元音 WAV の長さ

- **TC-021-1** 3 秒 webm の分解 → original のサンプル数 == round(`duration` × 44100)

### SPEC-022 元音の未知 id

- **TC-022-1** `/api/original/deadbeef`（未発行）→ 404

### SPEC-030 合成 WAV の形式

- **TC-030-1** synthesize（params 省略）→ 200、`content-type` が `audio/wav`、PCM_16・1ch・44100Hz
- **TC-030-2** synthesize（formant 1.3, pitch 0.8）→ 同じ形式

### SPEC-031 合成 WAV の長さ

- **TC-031-1** 3 秒入力、params 省略 → 合成のサンプル数 == 元音のサンプル数
- **TC-031-2** pitch 2.0 → 合成のサンプル数 == 元音のサンプル数

### SPEC-032 無加工往復の包絡差

- **TC-032-1** 合成母音 /a/、params 省略 → 合成音を harvest+cheaptrick で再分解した sp と元の sp の包絡差 ≤ 1.0dB
- **TC-032-2** 合成母音 /i/、params = {} → 包絡差 ≤ 1.0dB

### SPEC-033 無加工の 3 通りが同一

- **TC-033-1** params 省略 / `{}` / 全キー初期値 → 3 つの WAV バイト列が同一

### SPEC-034 16bit 化の飽和

- **TC-034-1** WAV 化関数に [1.5, −1.5, 0.5] → 読み戻した int16 が [32767, −32767, 16384 ±1]
- **TC-034-2** WAV 化関数に [1.0, −1.0] → [32767, −32767]（符号が反転しない）

### SPEC-035 合成の未知 id

- **TC-035-1** 未発行の id で synthesize → 404

### SPEC-036 ap は不変

- **TC-036-1** 全パラメータ非初期値で synthesize → 合成に渡る ap が、params 省略時に渡る ap と要素単位で一致

### SPEC-037 合成と包絡の sp が一致

- **TC-037-1** params = {formant 1.2, tilt 3, bands [2,−2,4,−4], smooth 30} → 合成に渡る sp のフレーム 50 と 200 の dB 値が、同 params の envelope の `modified_db` と差 1e-6 以内

### SPEC-040 包絡応答の形

- **TC-040-1** envelope → 3 配列とも長さ 1025、`freq[0]` == 0、`freq[1024]` == 22050、`freq[k]` == k·44100/2048

### SPEC-041 original_db の定義

- **TC-041-1** frame = 100 → `original_db` == 10·log10(合成に渡る無加工 sp[100] + 1e-12)（差 1e-6 以内）

### SPEC-042 無加工なら modified == original

- **TC-042-1** params 省略 → `modified_db` == `original_db`（差 1e-6 以内）
- **TC-042-2** params = {} → 同上

### SPEC-043 frame 範囲外は 400

- **TC-043-1** frame = −1 → 400
- **TC-043-2** frame = `frames` → 400
- **TC-043-3** frame = 0 → 200

### SPEC-044 包絡の未知 id

- **TC-044-1** 未発行の id で envelope → 404

### SPEC-045 母音でピークが変わる

- **TC-045-1** 合成母音 /a/ と /i/ を分解し、有声中央フレームの `original_db`（50〜8000Hz）のピーク周波数 → 差 ≥ 200Hz

### SPEC-050 未指定キーは初期値

- **TC-050-1** params = {"tilt": 3.0} の envelope == params = {全キー初期値, tilt 3.0} の envelope
- **TC-050-2** パラメータ解釈関数に {} → formant 1.0, tilt 0.0, bands [0,0,0,0], smooth 0, pitch 1.0

### SPEC-051 formant のクランプ

- **TC-051-1** formant 5.0 → 解釈結果 1.60、envelope が formant 1.60 と一致
- **TC-051-2** formant 0.1 → 0.60
- **TC-051-3** formant 1.6 → 1.6（境界値はそのまま）

### SPEC-052 tilt のクランプ

- **TC-052-1** tilt 100 → 12.0
- **TC-052-2** tilt −13 → −12.0

### SPEC-053 bands のクランプ

- **TC-053-1** bands [20, −20, 12, −12] → [12, −12, 12, −12]

### SPEC-054 pitch のクランプ

- **TC-054-1** pitch 3.0 → 2.0
- **TC-054-2** pitch 0.1 → 0.5

### SPEC-055 smooth の丸め

- **TC-055-1** smooth の入力 → 解釈結果: −5→0, 0→0, 1→10, 9→10, 10→10, 16.4→16, 80→80, 81→80, 200→80
- **TC-055-2** envelope で smooth 5 → smooth 10 と同じ `modified_db`

### SPEC-056 bands 形式不正は 422

- **TC-056-1** bands 要素数 3 で envelope → 422
- **TC-056-2** bands に文字列 "a" を含めて synthesize → 422

### SPEC-060 formant の線形補間

- **TC-060-1** log_sp = ビン番号そのもの（0,1,…,1024 の 1 行）、r = 2.0 → 出力ビン k == k/2
- **TC-060-2** ランダム行、r = 1.25 → 出力ビン 10 == 入力ビン 8、出力ビン 11 == 入力ビン 8 と 9 の 0.8:0.2 内分
- **TC-060-3** r = 1.0 → 出力 == 入力

### SPEC-061 範囲外は最終ビン

- **TC-061-1** log_sp = ビン番号、r = 0.6 → k/0.6 > 1024 となるビン（k ≥ 615）の値がすべて 1024

### SPEC-062 formant でグラフのピークが移る

- **TC-062-1** 合成母音 /a/、formant 1.25、有声中央フレーム → `modified_db` ピーク周波数 / `original_db` ピーク周波数 が 1.1875〜1.3125
- **TC-062-2** 同、formant 0.8 → 比が 0.76〜0.84

### SPEC-063 formant で合成音のピークが移る

- **TC-063-1** 合成母音 /a/、formant 1.25 で合成 → 再分解の有声フレーム平均包絡のピーク周波数比が 1.1875〜1.3125

### SPEC-070 DCT 平滑化の定義

- **TC-070-1** ランダム 3 行、smooth 20 → 出力 == idct(dct(x, norm=ortho) の 20 次以降を 0, norm=ortho)（差 1e-9 以内）
- **TC-070-2** 次数 10 未満の余弦のみで作った行、smooth 10 → 出力 == 入力（差 1e-9 以内）

### SPEC-071 smooth 0 は恒等

- **TC-071-1** ランダム行、smooth 0 → 出力 == 入力

### SPEC-080 tilt の加算量

- **TC-080-1** tilt 6 → 加工前後の dB 差が 1000Hz 付近のビンで ≈0、2000Hz で +6、500Hz で −6（各 ±0.1、ビン周波数での厳密値とは 1e-6 以内）
- **TC-080-2** tilt −12 → ビン 0（0Hz）の dB 差 == −12·log2(20/1000)

### SPEC-090 bands の加算

- **TC-090-1** bands [3, −3, 6, −6] → 加工前後の dB 差が全ビンでゲインカーブ G(freq) と一致（1e-6 以内。G は SPEC-091/092 の式でテスト側が独立に計算）

### SPEC-091 bands の平坦区間

- **TC-091-1** bands [1, 2, 3, 4] → 100Hz のビンで 1、1000Hz で 2、2500Hz で 3、10000Hz で 4
- **TC-091-2** 同 → 500·2^(−1/3) 以下の全ビンが 1、4000·2^(1/3) 以上の全ビンが 4

### SPEC-092 bands のクロスフェード

- **TC-092-1** bands [0, 12, 0, 0] → 500Hz 相当のビンでゲインが式の値（≈6）と一致、区間内で単調増加
- **TC-092-2** bands [0, 0, 0, 12] → 4000Hz 付近のビンで式の値と一致、隣接ビン間の差の最大が 12 未満（段差が無い）

### SPEC-100 pitch で f0 が変わる

- **TC-100-1** 合成母音、pitch 1.5 で合成 → 再分解 f0 中央値 / 元の f0 中央値 が 1.455〜1.545
- **TC-100-2** pitch 0.5 → 比が 0.485〜0.515

### SPEC-101 無声フレームは 0 のまま

- **TC-101-1** 前後無音付き合成母音、pitch 2.0 → 合成に渡る f0 で、元 f0 == 0 のフレームがすべて 0、有声フレームは元の 2 倍

### SPEC-102 pitch は包絡に影響しない

- **TC-102-1** params = {pitch 1.7} の `modified_db` == `original_db`

### SPEC-110 加工順序

- **TC-110-1** 全パラメータ非初期値（formant 1.3, smooth 20, tilt 4, bands [3,−2,5,−6]）→ 一括適用 == bands(tilt(smooth(formant(x)))) を個別関数で順に適用した結果
- **TC-110-2** 同 → formant を最後にした順序の結果とは一致しない（順序が効いていることの確認）

### SPEC-120 分解の応答時間

- **TC-120-1** 合成母音 3 秒 wav で analyze 3 回 → 中央値 < 1.0 秒

### SPEC-121 合成の応答時間

- **TC-121-1** 3 秒入力、全パラメータ非初期値で synthesize 3 回 → 中央値 < 0.3 秒

### SPEC-122 127.0.0.1 のみで待ち受ける

- **TC-122-1** `python jig/server.py` を空きポートで起動 → `lsof` の LISTEN アドレスが 127.0.0.1 のみ（`*` や `0.0.0.0` を含まない）

### SPEC-123 UI ページの配信

- **TC-123-1** GET / → 200、content-type が text/html、本文に `<html` を含む

### SPEC-200 録音開始と経過秒表示

- **TC-200-1** 録音ボタン押下 → ボタンが録音中表示、経過秒表示が 1 秒後に 0.5 以上へ増える

### SPEC-201 停止で自動送信

- **TC-201-1** 録音開始 → 1.5 秒後に再押下 → `/api/analyze` の POST が 1 回発生し、分解完了表示（フレームスライダー有効化）になる

### SPEC-202 送信中は録音ボタン無効

- **TC-202-1** `/api/analyze` の応答を 1 秒遅らせる → 停止直後に録音ボタンが disabled、応答後に enabled

### SPEC-203 10 秒で自動停止

- **TC-203-1** 録音開始して何もしない → 10 秒後〜11.5 秒以内に `/api/analyze` の POST が発生し、録音中表示が消える

### SPEC-204 再録音で id が差し替わる

- **TC-204-1** 1 回目の分解後、2 回目を録音 → 以降の envelope 要求の `id` が 2 回目の応答の `id`

### SPEC-205 未分解時は再生ボタン無効

- **TC-205-1** ページ読み込み直後 → 元音・加工音ボタンが disabled

### SPEC-210 2 本の包絡線

- **TC-210-1** 分解完了後 → SVG に元包絡線と加工後包絡線の path があり、元包絡の stroke がグレー（R=G=B）、加工後の stroke がグレーでなく、stroke-width が元包絡より大きい

### SPEC-211 横軸の対数スケール

- **TC-211-1** 縦線 500 / 1500 / 4000Hz の x 座標 → (x − x50) / (x22050 − x50) が log(f/50)/log(441) と 0.005 以内で一致

### SPEC-212 縦軸の範囲

- **TC-212-1** グラフの `data-ymax` / `data-ymin` → ymax == 表示フレームの `original_db`（freq ≥ 50）の最大 + 5（0.01 以内）、ymin == ymax − 70

### SPEC-213 帯域の縦線

- **TC-213-1** SVG に 500 / 1500 / 4000Hz の縦線が 3 本ある

### SPEC-220 フレームスライダーの範囲

- **TC-220-1** 分解後 → スライダー min == 0、max == `frames` − 1

### SPEC-221 フレームスライダーの初期値

- **TC-221-1** 分解後 → スライダー値 == `voiced_frames[len // 2]`

### SPEC-222 無声フレームの表示

- **TC-222-1** スライダーを 0（前無音区間）にする → 無声表示が見える、有声フレームに戻す → 見えない

### SPEC-223 フレーム変更で包絡取得

- **TC-223-1** フレームスライダーを別の値へ → 300ms 後以降に、その `frame` を持つ envelope 要求が発生する

### SPEC-230 スライダーの範囲・刻み・初期値

- **TC-230-1** 8 本のスライダーの min / max / step / value → formant 0.6/1.6/0.01/1、tilt −12/12/0.1/0、bands 各 −12/12/0.1/0、smooth 0/80/1/0、pitch 0.5/2/0.01/1

### SPEC-231 数値表示の追従

- **TC-231-1** formant を 1.25 に変更 → 隣の数値表示が "1.25"

### SPEC-232 ダブルクリックで初期値

- **TC-232-1** tilt を 5 にしてダブルクリック → 値 0、数値表示 "0.0"

### SPEC-233 すべてリセット

- **TC-233-1** 全スライダーを非初期値にしてリセット → 全スライダーが初期値

### SPEC-234 300ms デバウンス

- **TC-234-1** 分解後に要求記録を空にし、formant を 100ms 間隔で 5 回変更 → 変更中は envelope 要求 0 件、最後の変更から 250ms 時点でも 0 件、800ms 以内に 1 件、以後 1 件のまま
- **TC-234-2** その 1 件の `params.formant` == 最後に設定した値

### SPEC-235 パラメータ変更で合成しない

- **TC-235-1** 複数スライダーを変更して 1 秒待つ → synthesize 要求 0 件

### SPEC-236 smooth 1〜9 の扱い

- **TC-236-1** smooth を 5 にして待つ → 描画に使われた `modified_db`（envelope 応答）が smooth 10 の API 応答と一致

### SPEC-240 加工音ボタン

- **TC-240-1** formant 1.3 にして加工音ボタン → synthesize 要求の `params.formant` == 1.3、`<audio>` の `data-source` == processed、再生中（paused == false）

### SPEC-241 合成待ちのローディング表示

- **TC-241-1** synthesize 応答を 1 秒遅らせて加工音ボタン → 待ちの間ボタンが `aria-busy="true"`、応答後に消える

### SPEC-242 元音ボタン

- **TC-242-1** 元音ボタン → `data-source` == original、src が `/api/original/<id>` を指す、再生中

### SPEC-243 スペースキーで A/B

- **TC-243-1** 未再生でスペース → original 再生、再度スペース → processed 再生、再度 → original
- **TC-243-2** 加工音ボタンで再生後にスペース → original 再生

### SPEC-244 フォーカス中もスペースは A/B のみ

- **TC-244-1** 加工音ボタンにフォーカスしてスペース（未再生状態）→ original が再生される（加工音ボタンの押下にならない）
- **TC-244-2** formant スライダーにフォーカスしてスペース → スライダーの値が変わらず、`window.scrollY` が変わらず、original が再生される

### SPEC-245 再生の切り替えで前の音は止まる

- **TC-245-1** 元音再生中に加工音ボタン → 再生中の音声が 1 つだけ（ページ内の再生中メディアが 1 個）で source が processed、currentTime が 0.5 秒未満から始まる

### SPEC-250 プリセット

- **TC-250-1** 各プリセットを押す → スライダー値が表どおり（子供っぽく: formant 1.25, pitch 1.15, 他初期値。太く: formant 0.85, tilt −3。こもる: bands [4,0,−6,−10]。のっぺり: smooth 16。素通し: 全初期値）
- **TC-250-2** 「太く」の後に「こもる」→ formant 1.0, tilt 0 に戻り bands のみ設定

### SPEC-260 API エラーの表示

- **TC-260-1** `/api/analyze` を 400（detail "too short"）に差し替えて録音・停止 → エラー表示領域に "too short" を含む文言
- **TC-260-2** `/api/synthesize` を 500 に差し替えて加工音ボタン → エラー表示領域が空でない、ボタンのローディングが解除される

### SPEC-261 マイク取得失敗の表示

- **TC-261-1** `navigator.mediaDevices.getUserMedia` を失敗させる初期化スクリプトで録音ボタン → エラー表示領域が空でない
