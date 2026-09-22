// DSP（007-engine-dsp）
import { test } from "node:test";
import assert from "node:assert/strict";
import { normalizeParams } from "../../engine/dsp/params.mjs";

const zeros = n => Array.from({ length: n }, () => 0);

// ---------------------------------------------------------------- パラメータの解釈

// TC-800-1
test("未指定のキーは初期値になる", () => {
  const p = normalizeParams({});
  assert.equal(p.formant, 1.0);
  assert.equal(p.tilt, 0.0);
  assert.deepEqual(p.bands, [0, 0, 0, 0]);
  assert.equal(p.smooth, 0);
  assert.equal(p.pitch, 1.0);
  assert.deepEqual(p.curve, zeros(20));
  assert.equal(p.morph, null);
});

// TC-800-2
test("指定したキーだけが反映される", () => {
  const p = normalizeParams({ formant: 1.2 });
  assert.equal(p.formant, 1.2);
  assert.equal(p.tilt, 0.0);
  assert.equal(p.smooth, 0);
});

// TC-801-1
test("formant は 0.60〜1.60 にクランプされる", () => {
  assert.equal(normalizeParams({ formant: 0.1 }).formant, 0.6);
  assert.equal(normalizeParams({ formant: 2.0 }).formant, 1.6);
  assert.equal(normalizeParams({ formant: 1.2 }).formant, 1.2);
});

// TC-802-1
test("tilt は ±12 にクランプされる", () => {
  assert.equal(normalizeParams({ tilt: -20 }).tilt, -12);
  assert.equal(normalizeParams({ tilt: 20 }).tilt, 12);
  assert.equal(normalizeParams({ tilt: 3.5 }).tilt, 3.5);
});

// TC-803-1
test("bands の各要素は ±12 にクランプされる", () => {
  assert.deepEqual(normalizeParams({ bands: [20, -20, 4, -4] }).bands, [12, -12, 4, -4]);
});

// TC-804-1
test("pitch は 0.50〜2.00 にクランプされる", () => {
  assert.equal(normalizeParams({ pitch: 0.1 }).pitch, 0.5);
  assert.equal(normalizeParams({ pitch: 3.0 }).pitch, 2.0);
  assert.equal(normalizeParams({ pitch: 1.5 }).pitch, 1.5);
});

// TC-805-1
test("smooth は整数に丸め、0 以下は 0、1〜9 は 10、81 以上は 80", () => {
  const s = v => normalizeParams({ smooth: v }).smooth;
  assert.deepEqual([s(-5), s(0), s(5), s(9), s(10), s(30.4), s(80), s(81), s(200)],
    [0, 0, 10, 10, 10, 30, 80, 80, 80]);
});

// TC-806-1
test("curve の各要素は ±12 にクランプされる", () => {
  const curve = zeros(20);
  curve[0] = 20; curve[1] = -20; curve[5] = 3;
  const p = normalizeParams({ curve });
  assert.equal(p.curve[0], 12);
  assert.equal(p.curve[1], -12);
  assert.equal(p.curve[5], 3);
});

// TC-807-1
test("morph.ratio は 0〜1 にクランプされる", () => {
  assert.equal(normalizeParams({ morph: { ratio: -1 } }).morph.ratio, 0);
  assert.equal(normalizeParams({ morph: { ratio: 2 } }).morph.ratio, 1);
  assert.equal(normalizeParams({ morph: { ratio: 0.3 } }).morph.ratio, 0.3);
});

// TC-808-1
test("bands の要素数が 4 でないと TypeError", () => {
  assert.throws(() => normalizeParams({ bands: [0, 0, 0] }), TypeError);
});

// TC-808-2
test("bands に数値でない値があると TypeError", () => {
  assert.throws(() => normalizeParams({ bands: [0, "1", 0, 0] }), TypeError);
});

// TC-808-3
test("bands が配列でないと TypeError", () => {
  assert.throws(() => normalizeParams({ bands: 3 }), TypeError);
});

// TC-809-1
test("curve の要素数が 20 でないと TypeError", () => {
  assert.throws(() => normalizeParams({ curve: zeros(19) }), TypeError);
});

// TC-809-2
test("curve に null があると TypeError", () => {
  const curve = zeros(20);
  curve[3] = null;
  assert.throws(() => normalizeParams({ curve }), TypeError);
});

// TC-810-1
test("formant が文字列だと TypeError", () => {
  assert.throws(() => normalizeParams({ formant: "1.2" }), TypeError);
});

// TC-810-2
test("smooth が NaN だと TypeError", () => {
  assert.throws(() => normalizeParams({ smooth: NaN }), TypeError);
});

// TC-810-3
test("morph.ratio が文字列だと TypeError", () => {
  assert.throws(() => normalizeParams({ morph: { ratio: "0.5" } }), TypeError);
});

// ---------------------------------------------------------------- 周波数軸のゲイン

import { applyEnvelope, applyEnvelopeLog } from "../../engine/dsp/envelope.mjs";
import { golden1s, maxAbsDiff as maxAbsDiffArr } from "./golden.mjs";
import * as ref from "./dsp-ref.mjs";

const G = golden1s();
const N1 = G.f0.length;
const FRAME = 100;

// 指定フレームの、加工前後の log_sp の差（長さ 1025）。ゲインは log_sp 上で加算される
function gainAt(sp, params, frame = FRAME) {
  const out = applyEnvelope(sp, params);
  return Array.from({ length: ref.F }, (_, k) =>
    Math.log(out[frame * ref.F + k]) - ref.logSp(sp[frame * ref.F + k]));
}
const lnGain = dbList => dbList.map(v => v * ref.DB_TO_LN);

const maxDiff = (a, b) => a.reduce((m, v, i) => Math.max(m, Math.abs(v - b[i])), 0);

// TC-825-1
test("tilt = 6 の dB 差は T·log2(max(freq,20)/1000)", () => {
  assert.ok(maxDiff(gainAt(G.sp, { tilt: 6 }), lnGain(ref.tiltGainDb(6))) <= 1e-9);
});

// TC-825-2
test("tilt = −6 の dB 差", () => {
  assert.ok(maxDiff(gainAt(G.sp, { tilt: -6 }), lnGain(ref.tiltGainDb(-6))) <= 1e-9);
});

// TC-826-1
test("bands = [6,0,0,0] は低域だけ 6dB 上がる", () => {
  const d = gainAt(G.sp, { bands: [6, 0, 0, 0] }).map(v => v / ref.DB_TO_LN);
  for (let k = 0; k < ref.F; k++) {
    const f = ref.freq(k);
    if (f <= 500 * 2 ** (-1 / 3)) assert.ok(Math.abs(d[k] - 6) <= 1e-9, `${f}Hz`);
    if (f >= 1500 * 2 ** (1 / 3)) assert.ok(Math.abs(d[k]) <= 1e-9, `${f}Hz`);
  }
});

// TC-826-2
test("bands = [3,−3,6,−6] の dB 差は G(f) と一致（クロスフェードを含む）", () => {
  assert.ok(maxDiff(gainAt(G.sp, { bands: [3, -3, 6, -6] }), lnGain(ref.bandGainDb([3, -3, 6, -6]))) <= 1e-9);
});

// 固定の種の疑似乱数（テストの再現性のため）
function randomCurve() {
  let s = 12345;
  return Array.from({ length: 20 }, () => {
    s = (s * 1103515245 + 12345) % 2147483648;
    return (s / 2147483648) * 24 - 12;
  });
}

// TC-827-1
test("curve の dB 差は C(f) と一致", () => {
  const curve = randomCurve();
  assert.ok(maxDiff(gainAt(G.sp, { curve }), lnGain(ref.curveGainDb(curve))) <= 1e-9);
});

// TC-827-2
test("500Hz 以上の制御点では、近いビンにその制御点の値が出る", () => {
  // 隣り合う制御点の差が 0.5dB のなだらかなカーブ。急なカーブだと、ビンの位置のずれがそのまま誤差になる
  const curve = Array.from({ length: 20 }, (_, j) => -5 + 0.5 * j);
  const d = gainAt(G.sp, { curve }).map(v => v / ref.DB_TO_LN);
  for (let j = 0; j < 20; j++) {
    const f = ref.CURVE_FREQS[j];
    if (f < 500 || f > ref.FS / 2) continue;
    const k = Math.round((f * ref.FFT_SIZE) / ref.FS);
    assert.ok(Math.abs(d[k] - curve[j]) <= 0.05, `点 ${j}（${f.toFixed(0)}Hz）: ${d[k]} と ${curve[j]}`);
  }
});

// ---------------------------------------------------------------- formant

// 指定フレームの加工後 log_sp
function logRowAt(sp, params, frame = FRAME) {
  const out = applyEnvelope(sp, params);
  return Array.from({ length: ref.F }, (_, k) => Math.log(out[frame * ref.F + k]));
}
const logRowOf = (sp, frame = FRAME) =>
  Array.from({ length: ref.F }, (_, k) => ref.logSp(sp[frame * ref.F + k]));

// TC-821-1
test("formant r = 1.25 は k / r の線形補間", () => {
  const r = 1.25;
  const expected = ref.interpRow(logRowOf(G.sp), Array.from({ length: ref.F }, (_, k) => k / r));
  assert.ok(maxDiff(logRowAt(G.sp, { formant: r }), expected) <= 1e-9);
});

// TC-821-2
test("formant r = 0.8（縮小方向）も k / r の線形補間", () => {
  const r = 0.8;
  const expected = ref.interpRow(logRowOf(G.sp), Array.from({ length: ref.F }, (_, k) => k / r));
  assert.ok(maxDiff(logRowAt(G.sp, { formant: r }), expected) <= 1e-9);
});

// TC-822-1
test("k / r が F − 1 を超えるビンは、加工前の最終ビンの値", () => {
  const r = 0.8;
  const out = logRowAt(G.sp, { formant: r });
  const last = ref.logSp(G.sp[FRAME * ref.F + (ref.F - 1)]);
  let checked = 0;
  for (let k = 0; k < ref.F; k++) {
    if (k / r <= ref.F - 1) continue;
    assert.ok(Math.abs(out[k] - last) <= 1e-12, `k=${k}`);
    checked++;
  }
  assert.ok(checked > 0, "対象のビンが無い");
});

// ---------------------------------------------------------------- 平滑化

// TC-823-1
test("smooth = 30 は、次数 30 以上の DCT 係数を落とした結果と一致", () => {
  const expected = ref.smoothRowRef(logRowOf(G.sp), 30);
  assert.ok(maxDiff(logRowAt(G.sp, { smooth: 30 }), Array.from(expected)) <= 1e-9);
});

// TC-823-2
test("smooth = 80 も一致し、30 のときより元の log_sp に近い", () => {
  const original = logRowOf(G.sp);
  const at80 = logRowAt(G.sp, { smooth: 80 });
  assert.ok(maxDiff(at80, Array.from(ref.smoothRowRef(original, 80))) <= 1e-9);
  const dist = a => a.reduce((s, v, i) => s + (v - original[i]) ** 2, 0);
  assert.ok(dist(at80) < dist(logRowAt(G.sp, { smooth: 30 })));
});

// TC-824-1
test("smooth = 0 は log_sp を変えない", () => {
  const log = Float64Array.from(G.sp, ref.logSp);
  assert.equal(maxAbsDiffArr(applyEnvelopeLog(log, { smooth: 0 }), log), 0);
});

// ---------------------------------------------------------------- 伸縮と morph

import { stretchPartner } from "../../engine/dsp/envelope.mjs";
import { partnerLogSp } from "./golden.mjs";

const B = partnerLogSp();
const NB = B.length / ref.F; // 301

// TC-835-1
test("伸縮は N_A×F の Float64Array を返す", () => {
  const s = stretchPartner(B, N1);
  assert.ok(s instanceof Float64Array);
  assert.equal(s.length, N1 * ref.F);
});

// TC-836-1
test("伸縮はフレーム方向の線形補間", () => {
  const s = stretchPartner(B, N1);
  const expected = ref.stretchRef(B, NB, N1);
  assert.ok(maxAbsDiffArr(s, expected) <= 1e-9);
});

// TC-836-2
test("N_A = 1 のとき B のフレーム 0", () => {
  const s = stretchPartner(B, 1);
  assert.equal(s.length, ref.F);
  for (let k = 0; k < ref.F; k++) assert.equal(s[k], B[k]);
});

// TC-837-1
test("N_A = N_B なら伸縮後は B と同一", () => {
  assert.equal(maxAbsDiffArr(stretchPartner(B, NB), B), 0);
});

// TC-828-1
test("morph の混合は (1−α)·A + α·(伸縮後の B)", () => {
  const alpha = 0.4;
  const stretched = ref.stretchRef(B, NB, N1);
  const out = applyEnvelope(G.sp, { morph: { ratio: alpha } }, stretchPartner(B, N1));
  let m = 0;
  for (let i = 0; i < G.sp.length; i++) {
    const expected = (1 - alpha) * ref.logSp(G.sp[i]) + alpha * stretched[i];
    m = Math.max(m, Math.abs(Math.log(out[i]) - expected));
  }
  assert.ok(m <= 1e-9, String(m));
});

// TC-871-1
test("相手の log_sp の長さが F の倍数でないと RangeError", () => {
  assert.throws(() => stretchPartner(B.slice(0, -1), N1), RangeError);
});

// TC-872-1
test("ratio 0 は相手なしと同一", () => {
  const log = Float64Array.from(G.sp, ref.logSp);
  const withPartner = applyEnvelopeLog(log, { morph: { ratio: 0 } }, stretchPartner(B, N1));
  assert.equal(maxAbsDiffArr(withPartner, applyEnvelopeLog(log, {})), 0);
});

// TC-873-1
test("相手に自分自身を与えた α = 0.5 は相手なしと一致", () => {
  const selfLog = Float64Array.from(G.sp, ref.logSp);
  const out = applyEnvelope(G.sp, { morph: { ratio: 0.5 } }, stretchPartner(selfLog, N1));
  assert.ok(maxAbsDiffArr(out, applyEnvelope(G.sp, {}), ref.db) <= 1e-6);
});

// TC-873-2
test("相手に自分自身を与えた α = 1.0 も相手なしと一致", () => {
  const selfLog = Float64Array.from(G.sp, ref.logSp);
  const out = applyEnvelope(G.sp, { morph: { ratio: 1.0 } }, stretchPartner(selfLog, N1));
  assert.ok(maxAbsDiffArr(out, applyEnvelope(G.sp, {}), ref.db) <= 1e-6);
});

// ---------------------------------------------------------------- 加工の組み立て

const ALL = { formant: 1.2, smooth: 30, tilt: 3, bands: [2, -2, 4, -4], curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j), pitch: 1.3, morph: { ratio: 0.4 } };

// TC-819-1
test("sp 形式は exp(log 形式(ln(sp + 1e-12))) と同一", () => {
  const partner = stretchPartner(B, N1);
  const viaLog = applyEnvelopeLog(Float64Array.from(G.sp, ref.logSp), ALL, partner).map(Math.exp);
  assert.equal(maxAbsDiffArr(applyEnvelope(G.sp, ALL, partner), viaLog), 0);
});

// TC-820-1
test("sp 形式は同じ形の Float64Array を返し、値は有限で正", () => {
  const out = applyEnvelope(G.sp, ALL, stretchPartner(B, N1));
  assert.ok(out instanceof Float64Array);
  assert.equal(out.length, N1 * ref.F);
  assert.ok(out.every(v => Number.isFinite(v) && v > 0));
});

// TC-820-2
test("log 形式も同じ形の Float64Array を返し、値は有限", () => {
  const out = applyEnvelopeLog(Float64Array.from(G.sp, ref.logSp), ALL, stretchPartner(B, N1));
  assert.ok(out instanceof Float64Array);
  assert.equal(out.length, N1 * ref.F);
  assert.ok(out.every(Number.isFinite));
});

// TC-829-1
test("全パラメータ同時指定は、morph → formant → smooth → tilt → bands → curve の順の逐次適用と一致", () => {
  const partner = stretchPartner(B, N1);
  const log = Float64Array.from(G.sp, ref.logSp);
  const step = [
    l => applyEnvelopeLog(l, { morph: ALL.morph }, partner),
    l => applyEnvelopeLog(l, { formant: ALL.formant }),
    l => applyEnvelopeLog(l, { smooth: ALL.smooth }),
    l => applyEnvelopeLog(l, { tilt: ALL.tilt }),
    l => applyEnvelopeLog(l, { bands: ALL.bands }),
    l => applyEnvelopeLog(l, { curve: ALL.curve }),
  ].reduce((l, f) => f(l), log);
  assert.ok(maxAbsDiffArr(applyEnvelopeLog(log, ALL, partner), step) <= 1e-9);
});

// TC-829-2
test("順序を入れ替えると結果が変わる（tilt を formant の前に適用）", () => {
  const log = Float64Array.from(G.sp, ref.logSp);
  const swapped = applyEnvelopeLog(applyEnvelopeLog(log, { tilt: ALL.tilt }), { formant: ALL.formant });
  const inOrder = applyEnvelopeLog(applyEnvelopeLog(log, { formant: ALL.formant }), { tilt: ALL.tilt });
  assert.ok(maxAbsDiffArr(swapped, inOrder) > 0.01);
});

// TC-830-1
test("初期値のみなら log 形式は入力を変えない", () => {
  const log = Float64Array.from(G.sp, ref.logSp);
  assert.equal(maxAbsDiffArr(applyEnvelopeLog(log, {}), log), 0);
});

// TC-831-1
test("加工は引数を書き換えない", () => {
  const sp = G.sp.slice(), partner = stretchPartner(B, N1);
  const spCopy = sp.slice(), partnerCopy = partner.slice();
  applyEnvelope(sp, ALL, partner);
  assert.equal(maxAbsDiffArr(sp, spCopy), 0);
  assert.equal(maxAbsDiffArr(partner, partnerCopy), 0);
});

// TC-870-1
test("sp の長さが F の倍数でないと RangeError", () => {
  assert.throws(() => applyEnvelope(G.sp.slice(0, -1), {}), RangeError);
});

// ---------------------------------------------------------------- 1 フレーム分の dB 列

import { envelopeAt } from "../../engine/dsp/envelope.mjs";

const partner1 = () => stretchPartner(B, N1);

// TC-840-1
test("包絡の出力は freq / originalDb / modifiedDb / partnerDb を返す", () => {
  const e = envelopeAt(G.sp, FRAME, {});
  for (const k of ["freq", "originalDb", "modifiedDb"]) {
    assert.ok(e[k] instanceof Float64Array, k);
    assert.equal(e[k].length, ref.F, k);
  }
  assert.ok("partnerDb" in e);
});

// TC-841-1
test("freq[k] は k · 44100 / 2048", () => {
  const { freq } = envelopeAt(G.sp, FRAME, {});
  for (const k of [0, 512, 1024]) assert.equal(freq[k], (k * 44100) / 2048);
});

// TC-842-1
test("originalDb は加工前の dB 値", () => {
  const { originalDb } = envelopeAt(G.sp, FRAME, {});
  const expected = Array.from({ length: ref.F }, (_, k) => ref.db(G.sp[FRAME * ref.F + k]));
  assert.ok(maxDiff(Array.from(originalDb), expected) <= 1e-9);
});

// TC-843-1
test("初期値のみなら modifiedDb は originalDb と 1e-6 dB 以内で一致", () => {
  const e = envelopeAt(G.sp, FRAME, {});
  assert.ok(maxAbsDiffArr(e.modifiedDb, e.originalDb) <= 1e-6);
});

// TC-844-1
test("相手ありの partnerDb は、伸縮後の B のその行の dB 値", () => {
  const e = envelopeAt(G.sp, FRAME, { morph: { ratio: 0.4 } }, partner1());
  assert.ok(e.partnerDb instanceof Float64Array);
  assert.equal(e.partnerDb.length, ref.F);
  const stretched = ref.stretchRef(B, NB, N1);
  const expected = Array.from({ length: ref.F }, (_, k) => stretched[FRAME * ref.F + k] / ref.DB_TO_LN);
  assert.ok(maxDiff(Array.from(e.partnerDb), expected) <= 1e-9);
});

// TC-845-1
test("相手なしの partnerDb は null", () => {
  assert.equal(envelopeAt(G.sp, FRAME, {}).partnerDb, null);
});

// TC-846-1
test("pitch は modifiedDb を変えない", () => {
  const a = envelopeAt(G.sp, FRAME, { pitch: 1.0, formant: 1.2 });
  const b = envelopeAt(G.sp, FRAME, { pitch: 1.5, formant: 1.2 });
  assert.equal(maxAbsDiffArr(a.modifiedDb, b.modifiedDb), 0);
});

// TC-847-1
test("フレーム −1 は RangeError", () => {
  assert.throws(() => envelopeAt(G.sp, -1, {}), RangeError);
});

// TC-847-2
test("フレーム N は RangeError", () => {
  assert.throws(() => envelopeAt(G.sp, N1, {}), RangeError);
});

// TC-847-3
test("フレーム N − 1 は例外なし", () => {
  assert.equal(envelopeAt(G.sp, N1 - 1, {}).modifiedDb.length, ref.F);
});

// TC-838-1
test("ratio 1 のとき、加工後の dB 列は伸縮後の B の dB 値と一致", () => {
  const partner = stretchPartner(B, N1);
  const e = envelopeAt(G.sp, FRAME, { morph: { ratio: 1 } }, partner);
  const expected = Array.from({ length: ref.F }, (_, k) => partner[FRAME * ref.F + k] / ref.DB_TO_LN);
  assert.ok(maxDiff(Array.from(e.modifiedDb), expected) <= 1e-6);
});
