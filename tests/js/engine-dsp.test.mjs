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

import { applyEnvelope } from "../../engine/dsp/envelope.mjs";
import { golden1s } from "./golden.mjs";
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
