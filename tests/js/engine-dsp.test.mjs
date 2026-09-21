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
