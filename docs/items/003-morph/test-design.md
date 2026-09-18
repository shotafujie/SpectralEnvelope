# テスト設計書: 2 つの録音の包絡モーフィング

- アイテムID: `003-morph`
- 仕様書: `docs/items/003-morph/spec.md`
- 作成日: 2026-09-18

## テスト方針

| レベル | 対象 | 置き場所 |
|---|---|---|
| ユニット | 伸縮・混合の関数、加工順序 | `tests/test_morph.py`（テストダブルなし） |
| 統合 | `/api/envelope`・`/api/synthesize` の `morph` | `tests/test_morph.py`（TestClient + 本物の pyworld） |
| E2E | 選択欄・mix・相手の包絡線 | `tests/e2e/test_morph_ui.py` |

- 伸縮後の B の期待値は、テスト側で B の `original_db`（envelope API）を位置 p の前後フレームで線形補間して独立に求める。dB 表示値は log_sp の定数倍なので、log 領域の線形補間・線形混合は dB 領域でも同じ式になる
- 合成に渡る fo / ap は 001 と同じ `pyworld.synthesize` のスパイで観測する
- E2E の観測点: `#current` / `#partner`（`select`、`option` の value は id、「なし」は空文字）、`input[name=mix]` / `#mix-value`、`#partner-line`（path）
- E2E の 2 つ目以降の録音はファイル読み込み（002）で作る

## テストケース

### SPEC-400 morph 省略時は従来どおり

- **TC-400-1** `morph` 省略の envelope → `modified_db` == `original_db`（1e-6）、`partner_db` 以外のキーと値が 001 と同じ形
- **TC-400-2** `"morph": null` → `morph` 省略時と同じ `modified_db`

### SPEC-401 ratio のクランプ

- **TC-401-1** ratio 1.5 → ratio 1.0 と同じ `modified_db`
- **TC-401-2** ratio −0.5 → `morph` 省略時と同じ `modified_db`

### SPEC-402 ratio 0 は混合なし

- **TC-402-1** A=/a/、B=/i/、ratio 0 → envelope の `modified_db` が `morph` 省略時と一致（1e-6）
- **TC-402-2** 同条件で synthesize → WAV バイト列が `morph` 省略時と同一

### SPEC-403 伸縮と混合の式

- **TC-403-1** 関数に A = 0 の 5 フレーム、B = 各行が定数 [0, 10, 20] の 3 フレーム、α = 0.5 → 各フレームの値が [0, 2.5, 5, 7.5, 10]
- **TC-403-2** 関数に N_A = 1、B = 定数 [4, 8] の 2 フレーム、α = 1 → 値 4（p = 0）
- **TC-403-3** API: A=/a/ 3 秒、B=/i/ 2 秒、ratio 0.3、フレーム 100 と 400 → `modified_db` == 0.7·A の `original_db` + 0.3·（B の `original_db` を p で補間した値）（1e-6）

### SPEC-404 ratio 1 は伸縮後の B

- **TC-404-1** A=/a/ 3 秒、B=/i/ 2 秒、ratio 1、フレーム 250 → `modified_db` == 伸縮後の B（1e-6）
- **TC-404-2** B が A より長い（5 秒）場合も同様（フレーム 0 と最終フレームを含む 3 フレーム）

### SPEC-405 加工順序

- **TC-405-1** 関数で morph（α 0.6）+ formant 1.3 + smooth 20 + tilt 4 + bands [3,−2,5,−6] の一括適用 == morph → formant → smooth → tilt → bands の逐次適用
- **TC-405-2** 同条件で formant を morph より先にした結果とは一致しない

### SPEC-406 fo と ap は A のもの

- **TC-406-1** A=/a/（fo 120）、B=/i/（fo 200）、morph ratio 0.8・pitch 1.2 で synthesize → 合成に渡る fo == A の fo × 1.2、ap == `morph` 省略時に渡る ap（要素単位で一致）
- **TC-406-2** 同条件で合成音を再分解 → 有声フレームの fo 中央値が 144 ±5%（B の fo に引っ張られない）

### SPEC-407 合成の長さは A

- **TC-407-1** B が 5 秒 → 合成のサンプル数 == A の元音のサンプル数
- **TC-407-2** B が 1 秒 → 同上

### SPEC-408 相手の未知 id

- **TC-408-1** `morph.id` が未発行で envelope → 404
- **TC-408-2** `morph.id` が未発行で synthesize → 404

### SPEC-409 partner_db

- **TC-409-1** A 3 秒、B 2 秒、フレーム 100 → `partner_db` が 1025 要素で、B の `original_db` を p で補間した値と一致（1e-6）
- **TC-409-2** フレーム 0 → B のフレーム 0 の `original_db`、最終フレーム → B の最終フレームの `original_db`
- **TC-409-3** ratio 0 でも `morph` を指定していれば `partner_db` は配列

### SPEC-410 morph 省略時の partner_db

- **TC-410-1** `params` 省略 → `partner_db` が `null`
- **TC-410-2** `params` に `morph` 以外だけ指定 → `partner_db` が `null`

### SPEC-411 A 自身との混合

- **TC-411-1** `morph.id` = A、ratio 0.7 → `modified_db` が `morph` 省略時と一致（1e-6）
- **TC-411-2** 同条件で formant 1.2 も指定 → formant 1.2 のみの結果と一致（1e-6）

### SPEC-420 選択欄と項目のラベル

- **TC-420-1** 録音 1 回 + `voice.wav` 読み込み → `#current` の option が 2 件、`#partner` が 3 件（先頭が「なし」で value 空）。ラベルが順に「#1」「録音」「<録音の duration を小数 2 桁> 秒」、「#2」「voice.wav」「3.00 秒」を含む
- **TC-420-2** 分解前 → `#current` の option 0 件、`#partner` は「なし」の 1 件のみ

### SPEC-421 追加と切り替え

- **TC-421-1** 2 件目の分解完了 → `#current` の値が 2 件目の `id`、各選択欄の末尾が 2 件目

### SPEC-422 現在の録音の切り替え

- **TC-422-1** 録音（A、2.5 秒）→ 3 秒のファイル（B）→ `#current` を A に戻す → フレームスライダーの max が A の frames − 1、値が A の `voiced_frames` の中央、`#graph` の `data-id` が A
- **TC-422-3** 現在の録音 A（前後に無音を含む録音）で無声フレームを選んで無声表示を出す → `#current` を全フレーム有声の B に切り替える → 無声表示が消え、フレーム表示が B の中央フレームになる
- **TC-422-2** 同操作の後にスライダー変更 → envelope 要求の `id` が A、元音ボタン → src が A の `id` で終わる

### SPEC-423 相手「なし」

- **TC-423-1** 2 件分解後、相手が「なし」のままスライダー変更 → envelope 要求の `params` に `morph` キーが無い。加工音 → synthesize 要求にも無い

### SPEC-424 mix スライダー

- **TC-424-1** `input[name=mix]` の min / max / step / value → 0 / 1 / 0.01 / 0。値 0.35 に変更 → `#mix-value` が "0.35"

### SPEC-425 morph パラメータの送信

- **TC-425-1** 相手に 1 件目を選び mix 0.4 → envelope 要求の `params.morph` == {id: 1 件目, ratio: 0.4}、加工音 → synthesize 要求の `params.morph` も同じ

### SPEC-426 デバウンス

- **TC-426-1** 相手の選択を変える → 変更から 0.29 秒以上後に envelope 要求が 1 件、その後 0.4 秒間増えない
- **TC-426-2** mix を 100ms 間隔で 4 回変える → 最後の変更から 0.29 秒以上後に 1 件だけ、`ratio` は最後の値

### SPEC-427 相手の包絡線

- **TC-427-1** 相手を選ぶ → `#partner-line` が表示され `d` が空でない。stroke が `#orig-line`・`#mod-line` と異なり、`stroke-dasharray` が `none` でない
- **TC-427-2** 相手を「なし」に戻す → `#partner-line` が非表示

### SPEC-428 リセットとプリセット

- **TC-428-1** 相手選択 + mix 0.5 → すべてリセット → mix 0、相手の選択は変わらない
- **TC-428-2** 相手選択 + mix 0.5 → プリセット 5 種それぞれ → 毎回 mix 0、相手の選択は変わらない

### SPEC-429 mix のダブルクリック

- **TC-429-1** mix 0.6 → ダブルクリック → 0、`#mix-value` が "0.00"

### SPEC-430 一覧は最新 10 件

- **TC-430-1** 1 秒の wav を 11 回読み込み、2 回目の後で相手に 1 件目を選んでおく → 11 回目の後、`#current` が 10 件、`#partner` が 11 件（なし含む）、1 件目の `id` がどちらにも無く、`#partner` の値が空（なし）
