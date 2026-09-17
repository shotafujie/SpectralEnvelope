# 検証レポート: スペクトル包絡いじり治具

- 検証日: 2026-09-17
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `99de203`（作業ツリーはクリーン: `git status --short` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: macOS 26.5.2、Apple M4 Max、Python 3.13.12、pytest 9.1.1

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 86 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 86 |

判定の根拠は、次のフル実行の結果（`133 passed, 2 warnings`、終了コード 0）。FAILED / ERROR / SKIPPED / XFAIL の行は 0 件。

- 成功したテストは 133 件。1 つのテスト名に複数の TC ID を持つパラメータ化テストがあるため、テストの件数と TC の件数は一致しない。
- test-design.md に定義された TC は 132 件。成功したテスト名から取り出した TC ID は 132 種類。
- 両者の差を両方向に取ると、どちらも空（設計にあって成功していない TC は 0 件、成功していて設計に無い TC は 0 件）。
- spec.md の 86 件の仕様には、どれも 1 件以上の TC がある。

## 仕様別の判定

判定行は機械的に決めた。仕様ごとに、test-design.md でその仕様に属する TC がすべて、成功したテスト名に含まれていれば PASS とした。

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

```
$ git rev-parse --short HEAD && git status --short
99de203
```

```
$ .venv/bin/pytest -v ; echo "EXIT=$?"
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 133 items

tests/e2e/test_ui.py::test_TC_200_1_録音中は経過秒が増える PASSED        [  0%]
tests/e2e/test_ui.py::test_TC_201_1_停止で自動送信される PASSED          [  1%]
tests/e2e/test_ui.py::test_TC_202_1_送信中は録音ボタンが無効 PASSED      [  2%]
tests/e2e/test_ui.py::test_TC_203_1_10秒で自動停止する PASSED            [  3%]
tests/e2e/test_ui.py::test_TC_204_1_再録音でidが差し替わる PASSED        [  3%]
tests/e2e/test_ui.py::test_TC_205_1_未分解では再生ボタンが無効 PASSED    [  4%]
tests/e2e/test_ui.py::test_TC_205_2_録音中と分解失敗後も再生ボタンが無効 PASSED [  5%]
tests/e2e/test_ui.py::test_TC_210_1_元包絡と加工後包絡の2本 PASSED       [  6%]
tests/e2e/test_ui.py::test_TC_211_1_横軸は対数スケール PASSED            [  6%]
tests/e2e/test_ui.py::test_TC_212_1_縦軸は最大値プラス5から70dB幅 PASSED [  7%]
tests/e2e/test_ui.py::test_TC_213_1_帯域の縦線が3本 PASSED               [  8%]
tests/e2e/test_ui.py::test_TC_220_1_フレームスライダーの範囲 PASSED      [  9%]
tests/e2e/test_ui.py::test_TC_221_1_初期フレームは有声フレームの中央 PASSED [  9%]
tests/e2e/test_ui.py::test_TC_222_1_無声フレームで表示が出る PASSED      [ 10%]
tests/e2e/test_ui.py::test_TC_223_1_フレーム変更で包絡を取り直す PASSED  [ 11%]
tests/e2e/test_ui.py::test_TC_230_1_スライダーの範囲と初期値 PASSED      [ 12%]
tests/e2e/test_ui.py::test_TC_231_1_数値表示が追従する PASSED            [ 12%]
tests/e2e/test_ui.py::test_TC_232_1_ダブルクリックで初期値に戻る PASSED  [ 13%]
tests/e2e/test_ui.py::test_TC_233_1_すべてリセット PASSED                [ 14%]
tests/e2e/test_ui.py::test_TC_234_1_TC_234_2_300msデバウンス PASSED      [ 15%]
tests/e2e/test_ui.py::test_TC_235_1_パラメータ変更で合成しない PASSED    [ 15%]
tests/e2e/test_ui.py::test_TC_236_1_smooth5は10として描画される PASSED   [ 16%]
tests/e2e/test_ui.py::test_TC_240_1_加工音ボタンでその時点の値で合成して再生 PASSED [ 17%]
tests/e2e/test_ui.py::test_TC_240_2_加工音の再押下は先頭から PASSED      [ 18%]
tests/e2e/test_ui.py::test_TC_241_1_合成待ちはローディング表示 PASSED    [ 18%]
tests/e2e/test_ui.py::test_TC_242_1_元音ボタンで元音を再生 PASSED        [ 19%]
tests/e2e/test_ui.py::test_TC_242_2_元音の再押下は先頭から PASSED        [ 20%]
tests/e2e/test_ui.py::test_TC_243_1_スペースで元音と加工音が交互に再生される PASSED [ 21%]
tests/e2e/test_ui.py::test_TC_243_2_加工音の後のスペースは元音 PASSED    [ 21%]
tests/e2e/test_ui.py::test_TC_244_1_ボタンにフォーカスがあってもスペースはAB切替 PASSED [ 22%]
tests/e2e/test_ui.py::test_TC_244_2_スライダーにフォーカスがあってもスクロールしない PASSED [ 23%]
tests/e2e/test_ui.py::test_TC_245_1_新しい再生で前の音は止まる PASSED    [ 24%]
tests/e2e/test_ui.py::test_TC_250_1_プリセットで表の値になる PASSED      [ 24%]
tests/e2e/test_ui.py::test_TC_250_2_プリセットを続けて押すと前の値が消える PASSED [ 25%]
tests/e2e/test_ui.py::test_TC_260_1_分解エラーを表示する PASSED          [ 26%]
tests/e2e/test_ui.py::test_TC_260_2_合成エラーを表示する PASSED          [ 27%]
tests/e2e/test_ui.py::test_TC_261_1_マイク取得失敗を表示する PASSED      [ 27%]
tests/test_api.py::test_TC_001_1_webmを分解して必要なキーを返す PASSED   [ 28%]
tests/test_api.py::test_TC_001_2_webmのdurationは元の長さ PASSED         [ 29%]
tests/test_api.py::test_TC_002_1_22050Hzステレオwavは44100Hzモノラルになる PASSED [ 30%]
tests/test_api.py::test_TC_002_2_44100Hzモノラルwavはサンプルが保たれる PASSED [ 30%]
tests/test_api.py::test_TC_003_1_fsとfft_size PASSED                     [ 31%]
tests/test_api.py::test_TC_003_2_48000Hz入力でもfsは44100 PASSED         [ 32%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[132300-3.0] PASSED [ 33%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[66150-1.5] PASSED [ 33%]
tests/test_api.py::test_TC_005_1_framesはf0の要素数 PASSED               [ 34%]
tests/test_api.py::test_TC_005_2_最終フレームが存在する PASSED           [ 35%]
tests/test_api.py::test_TC_006_1_voiced_framesは有声フレームの昇順 PASSED [ 36%]
tests/test_api.py::test_TC_006_2_voiced_framesの個数 PASSED              [ 36%]
tests/test_api.py::test_TC_007_1_f0_meanは約120Hz PASSED                 [ 37%]
tests/test_api.py::test_TC_007_2_無音ではf0_meanが0 PASSED               [ 38%]
tests/test_api.py::test_TC_007_3_f0_meanは有声フレームの平均 PASSED      [ 39%]
tests/test_api.py::test_TC_008_1_idは8桁の16進 PASSED                    [ 39%]
tests/test_api.py::test_TC_008_2_idは毎回異なる PASSED                   [ 40%]
tests/test_api.py::test_TC_009_1_1秒未満は400 PASSED                     [ 41%]
tests/test_api.py::test_TC_009_2_ちょうど1秒は受け付ける PASSED          [ 42%]
tests/test_api.py::test_TC_010_1_10秒超は切り詰める PASSED               [ 42%]
tests/test_api.py::test_TC_010_2_ちょうど10秒 PASSED                     [ 43%]
tests/test_api.py::test_TC_011_1_ランダムバイトは400 PASSED              [ 44%]
tests/test_api.py::test_TC_011_2_空ファイルは400 PASSED                  [ 45%]
tests/test_api.py::test_TC_012_1_audioフィールドが無いと422 PASSED       [ 45%]
tests/test_api.py::test_TC_013_1_11件目で最古が破棄される PASSED         [ 46%]
tests/test_api.py::test_TC_013_2_11件目で2件目は残る PASSED              [ 47%]
tests/test_api.py::test_TC_014_1_10件までは全て残る PASSED               [ 48%]
tests/test_api.py::test_TC_020_1_元音WAVの形式 PASSED                    [ 48%]
tests/test_api.py::test_TC_021_1_元音WAVの長さ PASSED                    [ 49%]
tests/test_api.py::test_TC_022_1_元音の未知id PASSED                     [ 50%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[None] PASSED     [ 51%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[params1] PASSED  [ 51%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[None] PASSED [ 52%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[params1] PASSED [ 53%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[a-True] PASSED [ 54%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[i-False] PASSED [ 54%]
tests/test_api.py::test_TC_033_1_無加工の3通りは同一 PASSED              [ 55%]
tests/test_api.py::test_TC_034_3_合成APIの出力も16bit化で飽和する PASSED [ 56%]
tests/test_api.py::test_TC_035_1_合成の未知id PASSED                     [ 57%]
tests/test_api.py::test_TC_036_1_apは分解時のままで加工されない PASSED   [ 57%]
tests/test_api.py::test_TC_037_1_合成のspと包絡APIのmodified_dbが一致する PASSED [ 58%]
tests/test_api.py::test_TC_040_1_包絡応答の形 PASSED                     [ 59%]
tests/test_api.py::test_TC_041_1_original_dbは元spのdB値 PASSED          [ 60%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[None] PASSED [ 60%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[params1] PASSED [ 61%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[-1-400] PASSED [ 62%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[frames-400] PASSED [ 63%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[0-200] PASSED [ 63%]
tests/test_api.py::test_TC_044_1_包絡の未知id PASSED                     [ 64%]
tests/test_api.py::test_TC_045_1_母音でピーク位置が変わる PASSED         [ 65%]
tests/test_api.py::test_TC_050_1_未指定キーは初期値 PASSED               [ 66%]
tests/test_api.py::test_TC_051_1_formant範囲外はクランプされて包絡に効く PASSED [ 66%]
tests/test_api.py::test_TC_055_2_smooth5はsmooth10と同じ PASSED          [ 67%]
tests/test_api.py::test_TC_056_1_bands要素数3は422 PASSED                [ 68%]
tests/test_api.py::test_TC_056_2_bandsに文字列は422 PASSED               [ 69%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[1.25-1.1875-1.3125] PASSED [ 69%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[0.8-0.76-0.84] PASSED [ 70%]
tests/test_api.py::test_TC_063_1_formantで合成音のピークが移る PASSED    [ 71%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のf0が変わる[1.5-1.455-1.545] PASSED [ 72%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のf0が変わる[0.5-0.485-0.515] PASSED [ 72%]
tests/test_api.py::test_TC_101_1_無声フレームは0のまま PASSED            [ 73%]
tests/test_api.py::test_TC_102_1_pitchは包絡に影響しない PASSED          [ 74%]
tests/test_api.py::test_TC_123_1_ルートでUIページを返す PASSED           [ 75%]
tests/test_dsp.py::test_TC_050_2_空のパラメータは初期値になる PASSED     [ 75%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[5.0-1.6] PASSED [ 76%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[0.1-0.6] PASSED [ 77%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[1.6-1.6] PASSED [ 78%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[100-12.0] PASSED [ 78%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[-13--12.0] PASSED [ 79%]
tests/test_dsp.py::test_TC_053_1_bandsの各要素がクランプされる PASSED    [ 80%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[3.0-2.0] PASSED [ 81%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[0.1-0.5] PASSED [ 81%]
tests/test_dsp.py::test_TC_055_1_smoothの丸め PASSED                     [ 82%]
tests/test_dsp.py::test_TC_056_3_bands形式不正はバリデーションエラー[bands0] PASSED [ 83%]
tests/test_dsp.py::test_TC_056_3_bands形式不正はバリデーションエラー[bands1] PASSED [ 84%]
tests/test_dsp.py::test_TC_060_1_r2でビンkはk半分の位置の値になる PASSED [ 84%]
tests/test_dsp.py::test_TC_060_2_r1_25で線形補間される PASSED            [ 85%]
tests/test_dsp.py::test_TC_060_3_r1は恒等 PASSED                         [ 86%]
tests/test_dsp.py::test_TC_061_1_範囲外は最終ビンの値 PASSED             [ 87%]
tests/test_dsp.py::test_TC_070_1_DCTの低次だけ残す PASSED                [ 87%]
tests/test_dsp.py::test_TC_070_2_低次成分だけの行は変化しない PASSED     [ 88%]
tests/test_dsp.py::test_TC_071_1_smooth0は恒等 PASSED                    [ 89%]
tests/test_dsp.py::test_TC_080_1_tilt6の加算量 PASSED                    [ 90%]
tests/test_dsp.py::test_TC_080_2_0Hzは20Hzとして扱う PASSED              [ 90%]
tests/test_dsp.py::test_TC_090_1_バンドゲインはゲインカーブどおり加算される PASSED [ 91%]
tests/test_dsp.py::test_TC_091_1_平坦区間の代表点 PASSED                 [ 92%]
tests/test_dsp.py::test_TC_091_2_両端の平坦区間 PASSED                   [ 93%]
tests/test_dsp.py::test_TC_092_1_500Hz境界のクロスフェード PASSED        [ 93%]
tests/test_dsp.py::test_TC_092_2_4000Hz境界に段差が無い PASSED           [ 94%]
tests/test_dsp.py::test_TC_110_1_一括適用は定められた順序の逐次適用と一致する PASSED [ 95%]
tests/test_dsp.py::test_TC_110_2_順序を変えると結果が変わる PASSED       [ 96%]
tests/test_dsp.py::test_TC_034_1_振幅超過は飽和する PASSED               [ 96%]
tests/test_dsp.py::test_TC_034_2_フルスケールで符号が反転しない PASSED   [ 97%]
tests/test_perf.py::test_TC_120_1_3秒wavの分解は1秒未満 PASSED           [ 98%]
tests/test_perf.py::test_TC_121_1_3秒音声の合成は0_3秒未満 PASSED        [ 99%]
tests/test_serve.py::test_TC_122_1_127_0_0_1だけで待ち受ける PASSED      [100%]

=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

.venv/lib/python3.13/site-packages/starlette/testclient.py:53
  /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/lib/python3.13/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 133 passed, 2 warnings in 142.89s (0:02:22) ==================
EXIT=0
```

補助計測（判定には使っていない。性能テストの中央値は上のフル実行では出力されないため、`-s` を付けて別に実行した）:

```
$ .venv/bin/pytest -s -q tests/test_perf.py 2>&1 | grep -E "median|passed|failed"
analyze median 0.470s
.synthesize median 0.041s
2 passed, 2 warnings in 2.73s
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/001-envelope-jig
=== traceability check ===
スコープ: docs/items/001-envelope-jig （このアイテムに属するIDのみ検査）

[001-envelope-jig] 仕様 86件 / テストケース 132件

[テストコード] 検出したテストケースID: 132件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
```

注: 上の出力は、このレポートを書き出す直前（前回のレポートがあった状態）に取ったもの。このレポートを書き出した後にも再実行し、同じ出力（仕様 86件 / テストケース 132件 / 検出したテストケースID 132件 / 孤児: 0件）を得た。

## トレーサビリティ

`trace-check.sh` の出力は「孤児: 0件」の合計行だけなので、下の各行の 0 はその合計から転記したもの。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |

## 受け入れ試聴

**未実施。** spec.md で人が判定すると定められている項目で、verifier では判定できない。

| 項目 | 結果 | 仕様で指定された自動検査の代わりの指標 |
|------|------|------|
| M1: 実際の声で、元音と無加工の再合成音の声質の違いが聴き分けられない | 未実施（人の判定が必要） | SPEC-032: PASS |
| M2: 母音を変えて録音すると、グラフのピーク位置がはっきり変わる | 未実施（人の判定が必要） | SPEC-045: PASS |
| M3: formant を動かすと、グラフのピークが左右に動き、声質も同じ方向に変わる | 未実施（人の判定が必要） | SPEC-062: PASS / SPEC-063: PASS |

## 所見

判定は変えないが、記録しておくべきこと。前回（`0ddee3b`）の所見 1〜8 は、HEAD のテストで確かめる範囲が広がったので、再確認のうえ取り下げた。確認した内容は次のとおり。

- TC-036-1: 独立に求めた d4c の ap と比べている
- TC-037-1: 全フレームを比べ、pitch も含めている
- TC-014-1: 3 つの API すべてを確かめている
- TC-034-3: `/api/synthesize` を経由している
- TC-205-2 / TC-240-2 / TC-242-2 を追加し、TC-223-1 で時間も確かめている
- 応答待ちの状態は、要求を保留して作っている

1. **SPEC-236（smooth 1〜9 は「グラフ更新・合成の要求」で 10 として扱う）**: TC-236-1 が確かめているのは、グラフ更新（`/api/envelope`）の経路だけ。
   - 合成の要求（`/api/synthesize`）で 10 として扱われることは、直接には観測していない。
   - サーバー側の丸め（`Params` の解釈）は TC-055-1 が確かめている。
2. **SPEC-200（経過秒数が「増えていく」）**: TC-200-1 は 1 秒後に `#elapsed` を 1 回だけ読み、0.5 以上であることを確かめている。値が増え続けること（単調増加）は観測していない。
3. **SPEC-211 / SPEC-212（グラフの軸）**: 確かめているのは次の 2 つだけ。
   - 帯域の縦線の x 座標
   - UI が自分で書き出した属性（`data-plot-left` / `data-plot-right` / `data-ymax` / `data-ymin`）

   包絡線の path の座標がこの軸に従っているかは、テストでは確かめていない。所見を書くために `jig/index.html` を読んだところ、縦線と path は同じ `xOf` 関数で座標を計算していた。ただし、これはテストの結果ではない。
4. **SPEC-243（「先頭から」再生する）**: TC-243-1 / TC-243-2 は、再生する音源の切り替えと、再生中であることだけを確かめている。スペースキーで再生を始めたときの `currentTime` は確かめていない。ボタンを押したときに先頭から再生されることは、TC-240-2 / TC-242-2 / TC-245-1 が確かめている。
5. **SPEC-002（「任意の」サンプリング周波数・チャンネル数）**: 確かめたのは次の 3 通り。ほかの組み合わせ（8kHz や 3ch 以上など）は確かめていない。
   - 22050Hz・2ch
   - 44100Hz・1ch
   - 48000Hz・1ch
6. **SPEC-260（API が 4xx/5xx を返したときのエラー表示）**: 確かめたのは、`/api/analyze` が 400 を返す場合と、`/api/synthesize` が 500 を返す場合。`/api/envelope` や `/api/original` がエラーを返す場合は確かめていない。
7. **SPEC-222（無声である旨の表示）**: TC-222-1 が確かめているのは、`#unvoiced` が表示されるか隠れるかだけ。表示される文言は確かめていない。
8. **SPEC-120 / SPEC-121 の計測経路**: FastAPI の `TestClient`（プロセス内）で計っており、`jig/server.py` の uvicorn を経由した HTTP では計っていない。
   - 仕様の測定条件は通信経路を指定していないので、仕様の範囲内。
   - 補助計測の中央値は、分解 0.470 秒、合成 0.041 秒。
9. **SPEC-230 / SPEC-250 の値**: HEAD で、スライダーとプリセットの値が仕様に直接書き込まれた。そのため、仕様・テスト設計・テストコード（`SLIDERS` / `PRESETS`）の三者で値が一致していることは確かめられた。これらの値が原典の要件（ユーザーが示した要件文書）と一致しているかは、この検証の範囲外。
10. 実行時に警告が 2 件出た。判定には影響しない。
    - Starlette/httpx の DeprecationWarning
    - anyio の BlockingPortal の DeprecationWarning

## 受け入れ試聴の記録（検証後の追記）

verifier のレポートの後に、ユーザーが実機で試聴した結果を追記する。上の判定表は書き換えていない。

| 項目 | 結果 | 日付 | 条件 |
|------|------|------|------|
| M1: 元音と無加工再合成音の差が聴き分けられない | 合格（差は分からなかった） | 2026-09-18 | ユーザー本人の声、Chrome、`main` の 3a1496a |
| M2: 母音でピーク位置が変わる | 未報告 | — | — |
| M3: formant でピークと声質が同方向に変わる | 未報告 | — | — |
