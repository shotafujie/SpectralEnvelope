# 検証レポート: スペクトル包絡いじり治具

- 検証日: 2026-09-16
- 検証者: verifier サブエージェント（独立検証）
- 対象コミット: `0ddee3b`（作業ツリーはクリーン: `git status --porcelain` の出力なし）
- 対象仕様: `spec.md` / 対象テスト設計: `test-design.md`
- 実行環境: Apple M4 Max (arm64)、Python 3.13.12、pytest 9.1.1

## 判定サマリ

| 判定 | 件数 |
|------|------|
| PASS | 86 |
| FAIL | 0 |
| BLOCKED | 0 |
| **仕様の総数** | 86 |

判定の根拠は、次のフル実行の結果（129 passed、終了コード 0）。
test-design.md で定義された TC は 127 件あり、成功したテスト名から抽出した TC ID（127 種類）と完全に一致した。

## 仕様別の判定

判定行は、test-design.md の各 SPEC に属する TC がすべて、成功したテスト名に含まれているかで機械的に決めた。

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
- **SPEC-034**: PASS (TC-034-1, TC-034-2)
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
- **SPEC-056**: PASS (TC-056-1, TC-056-2)
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
- **SPEC-205**: PASS (TC-205-1)
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
- **SPEC-240**: PASS (TC-240-1)
- **SPEC-241**: PASS (TC-241-1)
- **SPEC-242**: PASS (TC-242-1)
- **SPEC-243**: PASS (TC-243-1, TC-243-2)
- **SPEC-244**: PASS (TC-244-1, TC-244-2)
- **SPEC-245**: PASS (TC-245-1)
- **SPEC-250**: PASS (TC-250-1, TC-250-2)
- **SPEC-260**: PASS (TC-260-1, TC-260-2)
- **SPEC-261**: PASS (TC-261-1)

## 実行したコマンドと出力

```
$ .venv/bin/pytest -v; echo "exit=$?"
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /Users/fujiemon/dev/speech/analyze/SpectralEnvelope/.venv/bin/python3
rootdir: /Users/fujiemon/dev/speech/analyze/SpectralEnvelope
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 129 items

tests/e2e/test_ui.py::test_TC_200_1_録音中は経過秒が増える PASSED        [  0%]
tests/e2e/test_ui.py::test_TC_201_1_停止で自動送信される PASSED          [  1%]
tests/e2e/test_ui.py::test_TC_202_1_送信中は録音ボタンが無効 PASSED      [  2%]
tests/e2e/test_ui.py::test_TC_203_1_10秒で自動停止する PASSED            [  3%]
tests/e2e/test_ui.py::test_TC_204_1_再録音でidが差し替わる PASSED        [  3%]
tests/e2e/test_ui.py::test_TC_205_1_未分解では再生ボタンが無効 PASSED    [  4%]
tests/e2e/test_ui.py::test_TC_210_1_元包絡と加工後包絡の2本 PASSED       [  5%]
tests/e2e/test_ui.py::test_TC_211_1_横軸は対数スケール PASSED            [  6%]
tests/e2e/test_ui.py::test_TC_212_1_縦軸は最大値プラス5から70dB幅 PASSED [  6%]
tests/e2e/test_ui.py::test_TC_213_1_帯域の縦線が3本 PASSED               [  7%]
tests/e2e/test_ui.py::test_TC_220_1_フレームスライダーの範囲 PASSED      [  8%]
tests/e2e/test_ui.py::test_TC_221_1_初期フレームは有声フレームの中央 PASSED [  9%]
tests/e2e/test_ui.py::test_TC_222_1_無声フレームで表示が出る PASSED      [ 10%]
tests/e2e/test_ui.py::test_TC_223_1_フレーム変更で包絡を取り直す PASSED  [ 10%]
tests/e2e/test_ui.py::test_TC_230_1_スライダーの範囲と初期値 PASSED      [ 11%]
tests/e2e/test_ui.py::test_TC_231_1_数値表示が追従する PASSED            [ 12%]
tests/e2e/test_ui.py::test_TC_232_1_ダブルクリックで初期値に戻る PASSED  [ 13%]
tests/e2e/test_ui.py::test_TC_233_1_すべてリセット PASSED                [ 13%]
tests/e2e/test_ui.py::test_TC_234_1_TC_234_2_300msデバウンス PASSED      [ 14%]
tests/e2e/test_ui.py::test_TC_235_1_パラメータ変更で合成しない PASSED    [ 15%]
tests/e2e/test_ui.py::test_TC_236_1_smooth5は10として描画される PASSED   [ 16%]
tests/e2e/test_ui.py::test_TC_240_1_加工音ボタンでその時点の値で合成して再生 PASSED [ 17%]
tests/e2e/test_ui.py::test_TC_241_1_合成待ちはローディング表示 PASSED    [ 17%]
tests/e2e/test_ui.py::test_TC_242_1_元音ボタンで元音を再生 PASSED        [ 18%]
tests/e2e/test_ui.py::test_TC_243_1_スペースで元音と加工音が交互に再生される PASSED [ 19%]
tests/e2e/test_ui.py::test_TC_243_2_加工音の後のスペースは元音 PASSED    [ 20%]
tests/e2e/test_ui.py::test_TC_244_1_ボタンにフォーカスがあってもスペースはAB切替 PASSED [ 20%]
tests/e2e/test_ui.py::test_TC_244_2_スライダーにフォーカスがあってもスクロールしない PASSED [ 21%]
tests/e2e/test_ui.py::test_TC_245_1_新しい再生で前の音は止まる PASSED    [ 22%]
tests/e2e/test_ui.py::test_TC_250_1_プリセットで表の値になる PASSED      [ 23%]
tests/e2e/test_ui.py::test_TC_250_2_プリセットを続けて押すと前の値が消える PASSED [ 24%]
tests/e2e/test_ui.py::test_TC_260_1_分解エラーを表示する PASSED          [ 24%]
tests/e2e/test_ui.py::test_TC_260_2_合成エラーを表示する PASSED          [ 25%]
tests/e2e/test_ui.py::test_TC_261_1_マイク取得失敗を表示する PASSED      [ 26%]
tests/test_api.py::test_TC_001_1_webmを分解して必要なキーを返す PASSED   [ 27%]
tests/test_api.py::test_TC_001_2_webmのdurationは元の長さ PASSED         [ 27%]
tests/test_api.py::test_TC_002_1_22050Hzステレオwavは44100Hzモノラルになる PASSED [ 28%]
tests/test_api.py::test_TC_002_2_44100Hzモノラルwavはサンプルが保たれる PASSED [ 29%]
tests/test_api.py::test_TC_003_1_fsとfft_size PASSED                     [ 30%]
tests/test_api.py::test_TC_003_2_48000Hz入力でもfsは44100 PASSED         [ 31%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[132300-3.0] PASSED [ 31%]
tests/test_api.py::test_TC_004_1_TC_004_2_durationはサンプル数割る44100[66150-1.5] PASSED [ 32%]
tests/test_api.py::test_TC_005_1_framesはf0の要素数 PASSED               [ 33%]
tests/test_api.py::test_TC_005_2_最終フレームが存在する PASSED           [ 34%]
tests/test_api.py::test_TC_006_1_voiced_framesは有声フレームの昇順 PASSED [ 34%]
tests/test_api.py::test_TC_006_2_voiced_framesの個数 PASSED              [ 35%]
tests/test_api.py::test_TC_007_1_f0_meanは約120Hz PASSED                 [ 36%]
tests/test_api.py::test_TC_007_2_無音ではf0_meanが0 PASSED               [ 37%]
tests/test_api.py::test_TC_007_3_f0_meanは有声フレームの平均 PASSED      [ 37%]
tests/test_api.py::test_TC_008_1_idは8桁の16進 PASSED                    [ 38%]
tests/test_api.py::test_TC_008_2_idは毎回異なる PASSED                   [ 39%]
tests/test_api.py::test_TC_009_1_1秒未満は400 PASSED                     [ 40%]
tests/test_api.py::test_TC_009_2_ちょうど1秒は受け付ける PASSED          [ 41%]
tests/test_api.py::test_TC_010_1_10秒超は切り詰める PASSED               [ 41%]
tests/test_api.py::test_TC_010_2_ちょうど10秒 PASSED                     [ 42%]
tests/test_api.py::test_TC_011_1_ランダムバイトは400 PASSED              [ 43%]
tests/test_api.py::test_TC_011_2_空ファイルは400 PASSED                  [ 44%]
tests/test_api.py::test_TC_012_1_audioフィールドが無いと422 PASSED       [ 44%]
tests/test_api.py::test_TC_013_1_11件目で最古が破棄される PASSED         [ 45%]
tests/test_api.py::test_TC_013_2_11件目で2件目は残る PASSED              [ 46%]
tests/test_api.py::test_TC_014_1_10件までは全て残る PASSED               [ 47%]
tests/test_api.py::test_TC_020_1_元音WAVの形式 PASSED                    [ 48%]
tests/test_api.py::test_TC_021_1_元音WAVの長さ PASSED                    [ 48%]
tests/test_api.py::test_TC_022_1_元音の未知id PASSED                     [ 49%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[None] PASSED     [ 50%]
tests/test_api.py::test_TC_030_1_TC_030_2_合成WAVの形式[params1] PASSED  [ 51%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[None] PASSED [ 51%]
tests/test_api.py::test_TC_031_1_TC_031_2_合成WAVの長さは元音と一致[params1] PASSED [ 52%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[a-True] PASSED [ 53%]
tests/test_api.py::test_TC_032_1_TC_032_2_無加工往復の包絡差は1dB以下[i-False] PASSED [ 54%]
tests/test_api.py::test_TC_033_1_無加工の3通りは同一 PASSED              [ 55%]
tests/test_api.py::test_TC_035_1_合成の未知id PASSED                     [ 55%]
tests/test_api.py::test_TC_036_1_apは加工されない PASSED                 [ 56%]
tests/test_api.py::test_TC_037_1_合成のspと包絡APIのmodified_dbが一致する PASSED [ 57%]
tests/test_api.py::test_TC_040_1_包絡応答の形 PASSED                     [ 58%]
tests/test_api.py::test_TC_041_1_original_dbは元spのdB値 PASSED          [ 58%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[None] PASSED [ 59%]
tests/test_api.py::test_TC_042_1_TC_042_2_無加工ならmodifiedはoriginalと一致[params1] PASSED [ 60%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[-1-400] PASSED [ 61%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[frames-400] PASSED [ 62%]
tests/test_api.py::test_TC_043_1_TC_043_2_TC_043_3_frame範囲[0-200] PASSED [ 62%]
tests/test_api.py::test_TC_044_1_包絡の未知id PASSED                     [ 63%]
tests/test_api.py::test_TC_045_1_母音でピーク位置が変わる PASSED         [ 64%]
tests/test_api.py::test_TC_050_1_未指定キーは初期値 PASSED               [ 65%]
tests/test_api.py::test_TC_051_1_formant範囲外はクランプされて包絡に効く PASSED [ 65%]
tests/test_api.py::test_TC_055_2_smooth5はsmooth10と同じ PASSED          [ 66%]
tests/test_api.py::test_TC_056_1_bands要素数3は422 PASSED                [ 67%]
tests/test_api.py::test_TC_056_2_bandsに文字列は422 PASSED               [ 68%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[1.25-1.1875-1.3125] PASSED [ 68%]
tests/test_api.py::test_TC_062_1_TC_062_2_formantでグラフのピークが移る[0.8-0.76-0.84] PASSED [ 69%]
tests/test_api.py::test_TC_063_1_formantで合成音のピークが移る PASSED    [ 70%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のf0が変わる[1.5-1.455-1.545] PASSED [ 71%]
tests/test_api.py::test_TC_100_1_TC_100_2_pitchで合成音のf0が変わる[0.5-0.485-0.515] PASSED [ 72%]
tests/test_api.py::test_TC_101_1_無声フレームは0のまま PASSED            [ 72%]
tests/test_api.py::test_TC_102_1_pitchは包絡に影響しない PASSED          [ 73%]
tests/test_api.py::test_TC_123_1_ルートでUIページを返す PASSED           [ 74%]
tests/test_dsp.py::test_TC_050_2_空のパラメータは初期値になる PASSED     [ 75%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[5.0-1.6] PASSED [ 75%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[0.1-0.6] PASSED [ 76%]
tests/test_dsp.py::test_TC_051_1_TC_051_2_TC_051_3_formantのクランプ[1.6-1.6] PASSED [ 77%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[100-12.0] PASSED [ 78%]
tests/test_dsp.py::test_TC_052_1_TC_052_2_tiltのクランプ[-13--12.0] PASSED [ 79%]
tests/test_dsp.py::test_TC_053_1_bandsの各要素がクランプされる PASSED    [ 79%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[3.0-2.0] PASSED [ 80%]
tests/test_dsp.py::test_TC_054_1_TC_054_2_pitchのクランプ[0.1-0.5] PASSED [ 81%]
tests/test_dsp.py::test_TC_055_1_smoothの丸め PASSED                     [ 82%]
tests/test_dsp.py::test_bands形式不正はバリデーションエラー[bands0] PASSED [ 82%]
tests/test_dsp.py::test_bands形式不正はバリデーションエラー[bands1] PASSED [ 83%]
tests/test_dsp.py::test_TC_060_1_r2でビンkはk半分の位置の値になる PASSED [ 84%]
tests/test_dsp.py::test_TC_060_2_r1_25で線形補間される PASSED            [ 85%]
tests/test_dsp.py::test_TC_060_3_r1は恒等 PASSED                         [ 86%]
tests/test_dsp.py::test_TC_061_1_範囲外は最終ビンの値 PASSED             [ 86%]
tests/test_dsp.py::test_TC_070_1_DCTの低次だけ残す PASSED                [ 87%]
tests/test_dsp.py::test_TC_070_2_低次成分だけの行は変化しない PASSED     [ 88%]
tests/test_dsp.py::test_TC_071_1_smooth0は恒等 PASSED                    [ 89%]
tests/test_dsp.py::test_TC_080_1_tilt6の加算量 PASSED                    [ 89%]
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
================= 129 passed, 2 warnings in 134.10s (0:02:14) ==================
exit=0
```

補助計測（判定には使わない。SPEC-120/121 の実測値を残すため、`-s` 付きで性能テストだけを再実行した）

```
$ .venv/bin/pytest tests/test_perf.py -v -s | grep -E "median|PASSED|FAILED"
tests/test_perf.py::test_TC_120_1_3秒wavの分解は1秒未満 analyze median 0.466s
PASSED
tests/test_perf.py::test_TC_121_1_3秒音声の合成は0_3秒未満 synthesize median 0.040s
PASSED
```

```
$ ~/dev/.claude/hooks/trace-check.sh docs/items/001-envelope-jig
=== traceability check ===
スコープ: docs/items/001-envelope-jig （このアイテムに属するIDのみ検査）

[001-envelope-jig] 仕様 86件 / テストケース 127件

[テストコード] 検出したテストケースID: 127件 (探索起点: .)

孤児: 0件 — 仕様・テスト設計・テストコード・検証はすべて対応が取れています。
exit=0
```

（参考: このレポートを書く前に実行したときは、verification.md が無いため「検証されていない仕様: 86件」、終了コード 1 だった。上の出力はレポートを書いた後に再実行したもの）

## トレーサビリティ

`trace-check.sh` の出力（レポート作成後の再実行）から転記する。

| # | 孤児 | 件数 |
|---|------|------|
| 1 | 検証されていない仕様 | 0 |
| 2 | テストケースの無い仕様 | 0 |
| 3 | 設計にあるがコードに無いTC | 0 |
| 4 | コードにあるが設計に無いTC | 0 |
| 5 | 親仕様が存在しないTC | 0 |
| | **合計** | **0** |

出力は種別ごとの行を出さず、「孤児: 0件」とだけ表示した。上の表の各行は、この合計 0 件から転記したもの。
出力の件数: 仕様 86件 / テストケース 127件 / テストコードで検出した TC ID 127件。

補足（trace-check の検査対象外で、別に観測したこと）

- ID を持たないテストが 2 件ある: `tests/test_dsp.py::test_bands形式不正はバリデーションエラー[bands0]` / `[bands1]`（test_dsp.py:73）。ID が無いため、孤児 #4 としては検出されない。コード内のコメントでは、API レベルの 422 は TC-056-1/2 で確認すると書かれている。
- テストコード中に同じ TC ID が 2 か所に出てくる。
  - `TC-051-1`: `tests/test_dsp.py:49`（Params のクランプ）と `tests/test_api.py:348`（envelope の一致）。TC-051-1 の 2 つの観点を 2 つのテストに分けたもの。
  - `TC-056-1`: `tests/test_api.py:362` のテスト名と、`tests/test_dsp.py:74` のコメント（ID の付いていない上記テストの中）。テストコードで ID の出現を数える検査の場合、このコメントもカウントされうる。

## 受け入れ試聴（仕様外・人が判定）

spec.md の指示に従い、この節を設ける。verifier には人の聴覚による判定ができないため、**すべて未実施**。人による判定が必要。

| 項目 | 結果 | 自動検査での代用指標 | 代用指標の判定 |
|---|---|---|---|
| M1: 実際の声で、元音と無加工再合成音の違いが聴き分けられない | 未実施（人による判定が必要） | SPEC-032 | PASS（合成母音での測定。実際の声ではない） |
| M2: 母音を変えて録音すると、グラフのピーク位置が明らかに変わる | 未実施（人による判定が必要） | SPEC-045 | PASS |
| M3: formant を動かすと、グラフのピークと再生音の声質が同じ方向に変わる | 未実施（人による判定が必要） | SPEC-062 / SPEC-063 | PASS / PASS（声質の聴感は検査対象外） |

## 所見

判定は変えないが、記録しておくべきこと。テストは成功しているものの、仕様の文言より狭い範囲しか確かめていない箇所を、影響が大きい順に並べる。

1. **SPEC-036（ap は分解時の ap と同一）**: TC-036-1（`tests/test_api.py:276`）は、params 省略時と全パラメータ指定時の 2 回の synthesize で `pyworld.synthesize` に渡った ap どうしを比べている。「分解時の ap」との比較ではない。確かめているのは「ap が params によって変わらない」ことだけで、両方の経路で同じ変換がかかっていた場合は検出できない。
2. **SPEC-037（全フレームで一致）**: TC-037-1 はフレーム 50 と 200 の 2 つしか比べていない。また、params から pitch を除いている（test-design の params と同じ）。
3. **SPEC-014（10 件目までは各 API が 200）**: TC-014-1 は 10 個の id について `/api/original` しか確かめていない。synthesize / envelope は確かめていない（TC-013-1 は 3 つの API すべてを確かめているのと対照的）。
4. **SPEC-034（16bit 化の飽和）**: `to_wav_bytes` を単体で確かめている。`/api/synthesize` の出力がこの経路を通ることは確かめていない（test-design に書かれているとおりの範囲）。
5. **SPEC-240 / SPEC-242（先頭から再生）**: `wait_playing` は `data-source`、`!paused`、`currentTime > 0` だけを見ていて、「先頭から」は確かめていない。再生開始位置を確かめているのは TC-245-1 の `currentTime < 0.5` だけ。
6. **SPEC-205（分解が一度も完了していない間は再生ボタンが無効）**: TC-205-1 はページを読み込んだ直後しか確かめていない。録音中や、分解がエラーで終わった後の状態は確かめていない。
7. **SPEC-223 / TC-223-1**: test-design には「300ms 後以降に」とあるが、テストは要求の件数と `frame` だけを確かめていて、タイミングは確かめていない（300ms デバウンスのタイミングは TC-234-1 が params の変更で確かめている）。
8. **TC-202-1 / TC-241-1 の遅延の入れ方**: 応答の遅延を、同期 API の route ハンドラ内の `time.sleep(1.0)` で作っている。この sleep は、`expect` のポーリングと同じ Python スレッドを止める。そのため「応答待ちの間の状態」を観測する時間を、この遅延が本当に確保しているかどうかは、このレポートでは確かめていない。テスト自体は成功している。
9. **SPEC-230 / SPEC-250（要件6章・要件7.6 の値）**: 仕様は原典の要件の表を参照しているが、原典は検証対象の文書に含まれていない。テスト（test-design.md と `tests/e2e/test_ui.py` の `SLIDERS` / `PRESETS`）の値が原典と一致しているかは、この検証では確かめられていない。
10. **SPEC-120 / SPEC-121 の計測経路**: FastAPI の `TestClient`（プロセス内）で計っていて、`jig/server.py` の uvicorn を経由した HTTP では計っていない。仕様の測定条件は通信経路を指定していないので、仕様の範囲内。実測の中央値は、分解 0.466 秒、合成 0.040 秒（補助計測）。
11. **TC-212-1 のコメントと実際の処理の食い違い**: コメントには「分解直後の描画に使われた最後の包絡」とあるが、`page.expect_response` が捕まえるのは最初の `/api/envelope` の応答。
12. 実行時に警告が 2 件出た（Starlette/httpx の DeprecationWarning、anyio の BlockingPortal の DeprecationWarning）。判定には影響しない。
