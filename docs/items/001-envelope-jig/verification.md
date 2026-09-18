# 検証レポート: スペクトル包絡いじり治具

- 検証日: 2026-09-18
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `ce54387`（`git rev-parse --short HEAD` の出力。作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple Silicon (arm64)、Python 3.13.12、pytest 9.1.1、ffmpeg 8.1.2
- 検証の観点: `ce54387` で 005 の SPEC-614 / SPEC-615 の文言が厳しくなり（非表示の要素の文言と大文字小文字を
  問わない検査、表示の並びの検査）、対応するテストも変わった。その追加・変更分の判定と、
  既存の保証が壊れていないかの判定。レポートは今回の実行結果で全体を書き直している。

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 86 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 86 |

判定の根拠は、5 アイテム分をまとめた 1 回のフル実行（`.venv/bin/pytest -v`、
`238 passed, 2 warnings in 264.81s (0:04:24)`、終了コード 0）。
出力に FAILED / ERROR / SKIPPED / XFAIL / XPASS の行は 0 件（結果行 238 行の内訳が `{'PASSED': 238}`）。

判定は仕様単位で、次の手順で機械的に決めた。

1. `test-design.md` からその仕様に属する TC をすべて取り出す。
2. その TC が `pytest -v` の結果行に 1 件以上現れ、現れたすべての行が PASSED であれば PASS。
   1 つのテスト名が 2 つ以上の TC を持つ場合（`test_TC_234_1_TC_234_2_…`）と、
   1 つの TC が複数のパラメータ化行に分かれる場合の両方を、この規則で扱う。
3. 1 件も現れない TC がある、または PASSED 以外の行がある場合は PASS にしない。

設計にあって実行結果に現れない TC は全アイテムで 0 件、実行結果に現れて設計に無い TC も 0 件
（238 行の結果行から取り出した TC ID 239 種類 = 5 アイテムの設計 TC 239 件と完全一致）。

## 仕様別の判定

記法は `docs/TRACEABILITY.md` に従う。判定は `PASS` / `FAIL` / `BLOCKED` の3値のみ。

- **SPEC-001**: PASS (TC-001-1, TC-001-2)
- **SPEC-002**: PASS (TC-002-1, TC-002-2)
- **SPEC-003**: PASS (TC-003-1, TC-003-2)
- **SPEC-004**: PASS (TC-004-1, TC-004-2)
- **SPEC-005**: PASS (TC-005-1, TC-005-2)
- **SPEC-006**: PASS (TC-006-1, TC-006-2)
- **SPEC-007**: PASS (TC-007-1, TC-007-2, TC-007-3)
- **SPEC-008**: PASS (TC-008-1, TC-008-2)
- **SPEC-009**: PASS (TC-009-1, TC-009-2)
- **SPEC-010**: PASS (TC-010-1, TC-010-2)
- **SPEC-011**: PASS (TC-011-1, TC-011-2)
- **SPEC-012**: PASS (TC-012-1)
- **SPEC-013**: PASS (TC-013-1, TC-013-2)
- **SPEC-014**: PASS (TC-014-1)
- **SPEC-020**: PASS (TC-020-1)
- **SPEC-021**: PASS (TC-021-1)
- **SPEC-022**: PASS (TC-022-1)
- **SPEC-030**: PASS (TC-030-1, TC-030-2)
- **SPEC-031**: PASS (TC-031-1, TC-031-2)
- **SPEC-032**: PASS (TC-032-1, TC-032-2)
- **SPEC-033**: PASS (TC-033-1)
- **SPEC-034**: PASS (TC-034-1, TC-034-2, TC-034-3)
- **SPEC-035**: PASS (TC-035-1)
- **SPEC-036**: PASS (TC-036-1)
- **SPEC-037**: PASS (TC-037-1)
- **SPEC-040**: PASS (TC-040-1)
- **SPEC-041**: PASS (TC-041-1)
- **SPEC-042**: PASS (TC-042-1, TC-042-2)
- **SPEC-043**: PASS (TC-043-1, TC-043-2, TC-043-3)
- **SPEC-044**: PASS (TC-044-1)
- **SPEC-045**: PASS (TC-045-1)
- **SPEC-050**: PASS (TC-050-1, TC-050-2)
- **SPEC-051**: PASS (TC-051-1, TC-051-2, TC-051-3)
- **SPEC-052**: PASS (TC-052-1, TC-052-2)
- **SPEC-053**: PASS (TC-053-1)
- **SPEC-054**: PASS (TC-054-1, TC-054-2)
- **SPEC-055**: PASS (TC-055-1, TC-055-2)
- **SPEC-056**: PASS (TC-056-1, TC-056-2, TC-056-3)
- **SPEC-060**: PASS (TC-060-1, TC-060-2, TC-060-3)
- **SPEC-061**: PASS (TC-061-1)
- **SPEC-062**: PASS (TC-062-1, TC-062-2)
- **SPEC-063**: PASS (TC-063-1)
- **SPEC-070**: PASS (TC-070-1, TC-070-2)
- **SPEC-071**: PASS (TC-071-1)
- **SPEC-080**: PASS (TC-080-1, TC-080-2)
- **SPEC-090**: PASS (TC-090-1)
- **SPEC-091**: PASS (TC-091-1, TC-091-2)
- **SPEC-092**: PASS (TC-092-1, TC-092-2)
- **SPEC-100**: PASS (TC-100-1, TC-100-2)
- **SPEC-101**: PASS (TC-101-1)
- **SPEC-102**: PASS (TC-102-1)
- **SPEC-110**: PASS (TC-110-1, TC-110-2)
- **SPEC-120**: PASS (TC-120-1)
- **SPEC-121**: PASS (TC-121-1)
- **SPEC-122**: PASS (TC-122-1)
- **SPEC-123**: PASS (TC-123-1)
- **SPEC-200**: PASS (TC-200-1)
- **SPEC-201**: PASS (TC-201-1)
- **SPEC-202**: PASS (TC-202-1)
- **SPEC-203**: PASS (TC-203-1)
- **SPEC-204**: PASS (TC-204-1)
- **SPEC-205**: PASS (TC-205-1, TC-205-2)
- **SPEC-210**: PASS (TC-210-1)
- **SPEC-211**: PASS (TC-211-1)
- **SPEC-212**: PASS (TC-212-1)
- **SPEC-213**: PASS (TC-213-1)
- **SPEC-220**: PASS (TC-220-1)
- **SPEC-221**: PASS (TC-221-1)
- **SPEC-222**: PASS (TC-222-1)
- **SPEC-223**: PASS (TC-223-1)
- **SPEC-230**: PASS (TC-230-1)
- **SPEC-231**: PASS (TC-231-1)
- **SPEC-232**: PASS (TC-232-1)
- **SPEC-233**: PASS (TC-233-1)
- **SPEC-234**: PASS (TC-234-1, TC-234-2)
- **SPEC-235**: PASS (TC-235-1)
- **SPEC-236**: PASS (TC-236-1)
- **SPEC-240**: PASS (TC-240-1, TC-240-2)
- **SPEC-241**: PASS (TC-241-1)
- **SPEC-242**: PASS (TC-242-1, TC-242-2)
- **SPEC-243**: PASS (TC-243-1, TC-243-2)
- **SPEC-244**: PASS (TC-244-1, TC-244-2)
- **SPEC-245**: PASS (TC-245-1)
- **SPEC-250**: PASS (TC-250-1, TC-250-2)
- **SPEC-260**: PASS (TC-260-1, TC-260-2)
- **SPEC-261**: PASS (TC-261-1)

## 実行したコマンドと出力

判定の根拠。**要約せず、実際の出力を貼る。**

全体の集計行（5 アイテム分を 1 回で実行）:

```
$ .venv/bin/pytest -v > pytest.log 2>&1; echo "EXIT=$?" >> pytest.log
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 238 items

（中略: 238 行の結果行のうち、このアイテムに属するものを下に抜き出す）
================= 238 passed, 2 warnings in 264.81s (0:04:24) ==================
EXIT=0
```

このアイテムに属する TC を名前に持つ結果行（上の出力からの抜粋、加工なし）:

```
tests/e2e/test_ui.py::test_TC_200_1_録音中は経過秒が増える PASSED        [ 27%]
tests/e2e/test_ui.py::test_TC_201_1_停止で自動送信される PASSED          [ 28%]
tests/e2e/test_ui.py::test_TC_202_1_送信中は録音ボタンが無効 PASSED      [ 28%]
tests/e2e/test_ui.py::test_TC_203_1_10秒で自動停止する PASSED            [ 28%]
tests/e2e/test_ui.py::test_TC_204_1_再録音でidが差し替わる PASSED        [ 29%]
tests/e2e/test_ui.py::test_TC_205_1_未分解では再生ボタンが無効 PASSED    [ 29%]
tests/e2e/test_ui.py::test_TC_205_2_録音中と分解失敗後も再生ボタンが無効 PASSED [ 30%]
tests/e2e/test_ui.py::test_TC_210_1_元包絡と加工後包絡の2本 PASSED       [ 30%]
tests/e2e/test_ui.py::test_TC_211_1_横軸は対数スケール PASSED            [ 31%]
tests/e2e/test_ui.py::test_TC_212_1_縦軸は最大値プラス5から70dB幅 PASSED [ 31%]
tests/e2e/test_ui.py::test_TC_213_1_帯域の縦線が3本 PASSED               [ 31%]
tests/e2e/test_ui.py::test_TC_220_1_フレームスライダーの範囲 PASSED      [ 32%]
tests/e2e/test_ui.py::test_TC_221_1_初期フレームは有声フレームの中央 PASSED [ 32%]
tests/e2e/test_ui.py::test_TC_222_1_無声フレームで表示が出る PASSED      [ 33%]
tests/e2e/test_ui.py::test_TC_223_1_フレーム変更で包絡を取り直す PASSED  [ 33%]
tests/e2e/test_ui.py::test_TC_230_1_スライダーの範囲と初期値 PASSED      [ 34%]
tests/e2e/test_ui.py::test_TC_231_1_数値表示が追従する PASSED            [ 34%]
tests/e2e/test_ui.py::test_TC_232_1_ダブルクリックで初期値に戻る PASSED  [ 34%]
tests/e2e/test_ui.py::test_TC_233_1_すべてリセット PASSED                [ 35%]
tests/e2e/test_ui.py::test_TC_234_1_TC_234_2_300msデバウンス PASSED      [ 35%]
tests/e2e/test_ui.py::test_TC_235_1_パラメータ変更で合成しない PASSED    [ 36%]
tests/e2e/test_ui.py::test_TC_236_1_smooth5は10として描画される PASSED   [ 36%]
tests/e2e/test_ui.py::test_TC_240_1_加工音ボタンでその時点の値で合成して再生 PASSED [ 36%]
tests/e2e/test_ui.py::test_TC_240_2_加工音の再押下は先頭から PASSED      [ 37%]
tests/e2e/test_ui.py::test_TC_241_1_合成待ちはローディング表示 PASSED    [ 37%]
tests/e2e/test_ui.py::test_TC_242_1_元音ボタンで元音を再生 PASSED        [ 38%]
tests/e2e/test_ui.py::test_TC_242_2_元音の再押下は先頭から PASSED        [ 38%]
tests/e2e/test_ui.py::test_TC_243_1_スペースで元音と加工音が交互に再生される PASSED [ 39%]
tests/e2e/test_ui.py::test_TC_243_2_加工音の後のスペースは元音 PASSED    [ 39%]
tests/e2e/test_ui.py::test_TC_244_1_ボタンにフォーカスがあってもスペースはAB切替 PASSED [ 39%]
tests/e2e/test_ui.py::test_TC_244_2_スライダーにフォーカスがあってもスクロールしない PASSED [ 40%]
tests/e2e/test_ui.py::test_TC_245_1_新しい再生で前の音は止まる PASSED    [ 40%]
tests/e2e/test_ui.py::test_TC_250_1_プリセットで表の値になる PASSED      [ 41%]
tests/e2e/test_ui.py::test_TC_250_2_プリセットを続けて押すと前の値が消える PASSED [ 41%]
tests/e2e/test_ui.py::test_TC_260_1_分解エラーを表示する PASSED          [ 42%]
tests/e2e/test_ui.py::test_TC_260_2_合成エラーを表示する PASSED          [ 42%]
tests/e2e/test_ui.py::test_TC_261_1_マイク取得失敗を表示する PASSED      [ 42%]
tests/test_api.py::test_TC_001_1_webmを分解して必要なキーを返す PASSED   [ 43%]
tests/test_api.py::test_TC_001_2_webmのdurationは元の長さ PASSED         [ 43%]
tests/test_api.py::test_TC_002_1_22050Hzステレオwavは44100Hzモノラルになる PASSED [ 44%]
tests/test_api.py::test_TC_002_2_44100Hzモノラルwavはサンプルが保たれる PASSED [ 44%]
tests/test_api.py::test_TC_003_1_fsとfft_size PASSED                     [ 44%]
tests/test_api.py::test_TC_003_2_48000Hz入力でもfsは44100 PASSED         [ 45%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[132300-3.0] PASSED [ 45%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[66150-1.5] PASSED [ 46%]
tests/test_api.py::test_TC_005_1_framesはfoの要素数 PASSED               [ 46%]
tests/test_api.py::test_TC_005_2_最終フレームが存在する PASSED           [ 47%]
tests/test_api.py::test_TC_006_1_voiced_framesは有声フレームの昇順 PASSED [ 47%]
tests/test_api.py::test_TC_006_2_voiced_framesの個数 PASSED              [ 47%]
tests/test_api.py::test_TC_007_1_f0_meanは約120Hz PASSED                 [ 48%]
tests/test_api.py::test_TC_007_2_無音ではf0_meanが0 PASSED               [ 48%]
tests/test_api.py::test_TC_007_3_f0_meanは有声フレームの平均 PASSED      [ 49%]
tests/test_api.py::test_TC_008_1_idは8桁の16進 PASSED                    [ 49%]
tests/test_api.py::test_TC_008_2_idは毎回異なる PASSED                   [ 50%]
tests/test_api.py::test_TC_009_1_1秒未満は400 PASSED                     [ 50%]
tests/test_api.py::test_TC_009_2_ちょうど1秒は受け付ける PASSED          [ 50%]
tests/test_api.py::test_TC_010_1_10秒超は切り詰める PASSED               [ 51%]
tests/test_api.py::test_TC_010_2_ちょうど10秒 PASSED                     [ 51%]
tests/test_api.py::test_TC_011_1_ランダムバイトは400 PASSED              [ 52%]
tests/test_api.py::test_TC_011_2_空ファイルは400 PASSED                  [ 52%]
tests/test_api.py::test_TC_012_1_audioフィールドが無いと422 PASSED       [ 52%]
tests/test_api.py::test_TC_013_1_11件目で最古が破棄される PASSED         [ 53%]
tests/test_api.py::test_TC_013_2_11件目で2件目は残る PASSED              [ 53%]
tests/test_api.py::test_TC_014_1_10件までは全て残る PASSED               [ 54%]
tests/test_api.py::test_TC_020_1_元音WAVの形式 PASSED                    [ 54%]
tests/test_api.py::test_TC_021_1_元音WAVの長さ PASSED                    [ 55%]
tests/test_api.py::test_TC_022_1_元音の未知id PASSED                     [ 55%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[None] PASSED     [ 55%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[params1] PASSED  [ 56%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[None] PASSED [ 56%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[params1] PASSED [ 57%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[a-True] PASSED [ 57%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[i-False] PASSED [ 57%]
tests/test_api.py::test_TC_033_1_無加工の3通りは同一 PASSED              [ 58%]
tests/test_api.py::test_TC_034_3_合成APIの出力も16bit化で飽和する PASSED [ 58%]
tests/test_api.py::test_TC_035_1_合成の未知id PASSED                     [ 59%]
tests/test_api.py::test_TC_036_1_apは分解時のままで加工されない PASSED   [ 59%]
tests/test_api.py::test_TC_037_1_合成のspと包絡APIのmodified_dbが一致する PASSED [ 60%]
tests/test_api.py::test_TC_040_1_包絡応答の形 PASSED                     [ 60%]
tests/test_api.py::test_TC_041_1_original_dbは元spのdB値 PASSED          [ 60%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[None] PASSED [ 61%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[params1] PASSED [ 61%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[-1-400] PASSED [ 62%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[frames-400] PASSED [ 62%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[0-200] PASSED [ 63%]
tests/test_api.py::test_TC_044_1_包絡の未知id PASSED                     [ 63%]
tests/test_api.py::test_TC_045_1_母音でピーク位置が変わる PASSED         [ 63%]
tests/test_api.py::test_TC_050_1_未指定キーは初期値 PASSED               [ 64%]
tests/test_api.py::test_TC_051_1_formant範囲外はクランプされて包絡に効く PASSED [ 64%]
tests/test_api.py::test_TC_055_2_smooth5はsmooth10と同じ PASSED          [ 65%]
tests/test_api.py::test_TC_056_1_bands要素数3は422 PASSED                [ 65%]
tests/test_api.py::test_TC_056_2_bandsに文字列は422 PASSED               [ 65%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[1.25-1.1875-1.3125] PASSED [ 66%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[0.8-0.76-0.84] PASSED [ 66%]
tests/test_api.py::test_TC_063_1_formantで合成音のピークが移る PASSED    [ 67%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のfoが変わる[1.5-1.455-1.545] PASSED [ 67%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のfoが変わる[0.5-0.485-0.515] PASSED [ 68%]
tests/test_api.py::test_TC_101_1_無声フレームは0のまま PASSED            [ 68%]
tests/test_api.py::test_TC_102_1_pitchは包絡に影響しない PASSED          [ 68%]
tests/test_api.py::test_TC_123_1_ルートでUIページを返す PASSED           [ 69%]
tests/test_dsp.py::test_TC_050_2_空のパラメータは初期値になる PASSED     [ 75%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[5.0-1.6] PASSED [ 76%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[0.1-0.6] PASSED [ 76%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[1.6-1.6] PASSED [ 76%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[100-12.0] PASSED [ 77%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[-13--12.0] PASSED [ 77%]
tests/test_dsp.py::test_TC_053_1_bandsの各要素がクランプされる PASSED    [ 78%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[3.0-2.0] PASSED [ 78%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[0.1-0.5] PASSED [ 78%]
tests/test_dsp.py::test_TC_055_1_smoothの丸め PASSED                     [ 79%]
tests/test_dsp.py::test_TC_056_3_bands形式不正はバリデーションエラー[bands0] PASSED [ 79%]
tests/test_dsp.py::test_TC_056_3_bands形式不正はバリデーションエラー[bands1] PASSED [ 80%]
tests/test_dsp.py::test_TC_060_1_r2でビンkはk半分の位置の値になる PASSED [ 80%]
tests/test_dsp.py::test_TC_060_2_r1_25で線形補間される PASSED            [ 81%]
tests/test_dsp.py::test_TC_060_3_r1は恒等 PASSED                         [ 81%]
tests/test_dsp.py::test_TC_061_1_範囲外は最終ビンの値 PASSED             [ 81%]
tests/test_dsp.py::test_TC_070_1_DCTの低次だけ残す PASSED                [ 82%]
tests/test_dsp.py::test_TC_070_2_低次成分だけの行は変化しない PASSED     [ 82%]
tests/test_dsp.py::test_TC_071_1_smooth0は恒等 PASSED                    [ 83%]
tests/test_dsp.py::test_TC_080_1_tilt6の加算量 PASSED                    [ 83%]
tests/test_dsp.py::test_TC_080_2_0Hzは20Hzとして扱う PASSED              [ 84%]
tests/test_dsp.py::test_TC_090_1_バンドゲインはゲインカーブどおり加算される PASSED [ 84%]
tests/test_dsp.py::test_TC_091_1_平坦区間の代表点 PASSED                 [ 84%]
tests/test_dsp.py::test_TC_091_2_両端の平坦区間 PASSED                   [ 85%]
tests/test_dsp.py::test_TC_092_1_500Hz境界のクロスフェード PASSED        [ 85%]
tests/test_dsp.py::test_TC_092_2_4000Hz境界に段差が無い PASSED           [ 86%]
tests/test_dsp.py::test_TC_110_1_一括適用は定められた順序の逐次適用と一致する PASSED [ 86%]
tests/test_dsp.py::test_TC_110_2_順序を変えると結果が変わる PASSED       [ 86%]
tests/test_dsp.py::test_TC_034_1_振幅超過は飽和する PASSED               [ 87%]
tests/test_dsp.py::test_TC_034_2_フルスケールで符号が反転しない PASSED   [ 87%]
tests/test_perf.py::test_TC_120_1_3秒wavの分解は1秒未満 PASSED           [ 99%]
tests/test_perf.py::test_TC_121_1_3秒音声の合成は0_3秒未満 PASSED        [ 99%]
tests/test_serve.py::test_TC_122_1_127_0_0_1だけで待ち受ける PASSED      [100%]
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/001-envelope-jig
=== traceability check ===
スコープ: docs/items/001-envelope-jig （このアイテムに属するIDのみ検査）

[001-envelope-jig] 仕様 86件 / テストケース 132件

[テストコード] 検出したテストケースID: 132件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

終了コード: 0。

```
$ ~/dev/.claude/hooks/trace-check.sh
=== traceability check ===

[001-envelope-jig] 仕様 86件 / テストケース 132件

[002-wav-load] 仕様 7件 / テストケース 9件

[003-morph] 仕様 23件 / テストケース 43件

[004-gain-curve] 仕様 18件 / テストケース 30件

[005-ui-affordance] 仕様 15件 / テストケース 25件

[テストコード] 検出したテストケースID: 239件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

終了コード: 0。

## トレーサビリティ

`trace-check.sh` の出力から転記する（目視で「0件」と書かない）。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

（`trace-check.sh` は孤児が 0 件の分類を個別に出力しないため、合計「孤児: 0件」からの転記。
上の出力はレポート書き直し後のもの。書き直し前の同じコマンドの出力も「孤児: 0件」・終了コード 0 だった。）

## 所見

仕様とテスト設計を読んだうえで気づいたこと。判定を左右しないが記録すべきもの。

- **`ce54387` は 001 に一切触れていない。** `git show --stat ce54387` が挙げるのは 3 ファイル
  （`docs/items/005-ui-affordance/spec.md`、同 `test-design.md`、`tests/e2e/test_tooltip.py`）で、
  001 の `spec.md` / `test-design.md`、001 が観測する `jig/server.py` / `jig/index.html`、
  001 のテスト（`tests/e2e/test_ui.py` / `tests/test_api.py` / `tests/test_dsp.py` / `tests/test_perf.py` /
  `tests/test_serve.py`）はいずれも含まれない。仕様 86 件 / TC 132 件は前回検証（`91c7b18`）と同数で、
  判定も 86 件すべて PASS のまま。ただしこの判定は差分ではなく、今回のフル実行の結果に基づく。
- **前回 001 の所見で「005 側の検査が届いていない」と書いた 2 か所が、今回 005 側で塞がった。**
  SPEC-222 の `#unvoiced`（現在「無声フレームです（fo = 0）」）と、004 の `#curve-readout` は、
  いずれも既定で `hidden` であるため前回の 005 の検査では文言を見られなかった。
  `ce54387` の SPEC-614 は非表示の要素の文言を明示的に検査範囲に含め、TC-614-3 が
  実際に無声フレームを選びドラッグする状態を作るようになった。実測でも両方が検出される
  （005 のレポートの所見の表）。**ただし仕様IDは 005 側にあり、001 側には無い。**
  001 の「共通の定義」の「表記」の行は仕様行（`- **SPEC-NNN**`）ではないため、001 の trace-check はこれを見ていない。
- **`f0` の綴りがコード側に残っているのは仕様どおり。** 001 の共通の定義「表記」は、pyworld の識別子・
  コードの変数名・API 応答フィールド `f0_mean` を明示的に除外している。新しい SPEC-614 も
  「スクリプトとスタイルの中身は除く」と書いており、`jig/index.html` に残る唯一の `f0`
  （`<script>` 内の `info.f0_mean`）とは衝突しない。
- SPEC-222 の TC-222-1 は `#unvoiced` の可視・不可視だけを観測しており、その文言は見ていない。
  文言側の保証は 005 の SPEC-614 が持つという分担のままで、001 側には無い。
- SPEC-120 / SPEC-121（性能）は 3 回計測の中央値で、実行環境の負荷に依存する。今回は他の重い処理を
  並行させずに 1 回のフル実行の中で測定しており、`tests/test_perf.py` の 2 件とも PASSED。
  しきい値に対する余裕は pytest の出力からは読み取れない。
- 「受け入れ試聴」の M1〜M3 は仕様IDを持たず、自動検査の対象外。記録は末尾の節のとおりで、M2 / M3 は未報告のまま。

## 受け入れ試聴の記録（検証後の追記）

verifier のレポートの後に、ユーザーが実機で試聴した結果を追記する。上の判定表は書き換えていない。

| 項目 | 結果 | 日付 | 条件 |
|------|------|------|------|
| M1: 元音と無加工再合成音の差が聴き分けられない | 合格（差は分からなかった） | 2026-09-18 | ユーザー本人の声、Chrome、`main` の 3a1496a |
| M2: 母音でピーク位置が変わる | 未報告 | — | — |
| M3: formant でピークと声質が同方向に変わる | 未報告 | — | — |
