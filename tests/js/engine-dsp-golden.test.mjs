// 再合成の経路と、Python 版との照合（007-engine-dsp）
import { test } from "node:test";
import assert from "node:assert/strict";
import { createEngine } from "../../engine/world-engine.mjs";
import { render } from "../../engine/render.mjs";
import { envelopeAt, stretchPartner } from "../../engine/dsp/envelope.mjs";
import { golden1s, partnerLogSp, vowelWithGap, maxAbsDiff, F } from "./golden.mjs";

const dbNoEps = v => 10 * Math.log10(v); // modifiedDb と同じ換算（1e-12 を足さない）

const G = golden1s();
const B = partnerLogSp();
const N1 = G.f0.length;
const N_SAMPLES = 44100;
const ALL = { formant: 1.2, smooth: 30, tilt: 3, bands: [2, -2, 4, -4],
  curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j), pitch: 1.3, morph: { ratio: 0.4 } };
const analysis = () => ({ f0: G.f0, sp: G.sp, ap: G.ap });
const engine = await createEngine();

// TC-850-1
test("再合成の経路は y と、使った f0 / sp / ap を返す", () => {
  const r = render(engine, analysis(), ALL, N_SAMPLES, stretchPartner(B, N1));
  assert.ok(r.y instanceof Float64Array);
  assert.equal(r.y.length, N_SAMPLES);
  assert.equal(r.f0.length, N1);
  assert.equal(r.sp.length, N1 * F);
  assert.equal(r.ap.length, N1 * F);
});

// TC-851-1
test("再合成に使う f0 は、分解時の f0 を pitch 倍したもの", () => {
  const r = render(engine, analysis(), { pitch: 1.5 }, N_SAMPLES);
  assert.equal(r.f0.length, N1);
  for (let i = 0; i < N1; i++) assert.equal(r.f0[i], G.f0[i] * 1.5, `frame ${i}`);
});

// TC-851-2
test("pitch 1.5 で再合成した音を再分解すると fo の中央値が 1.5 倍", () => {
  const r = render(engine, analysis(), { pitch: 1.5 }, N_SAMPLES);
  const again = engine.analyze(r.y);
  const pairs = [];
  for (let i = 0; i < Math.min(G.f0.length, again.f0.length); i++)
    if (G.f0[i] > 0 && again.f0[i] > 0) pairs.push(again.f0[i] / G.f0[i]);
  pairs.sort((a, b) => a - b);
  const ratio = pairs[pairs.length >> 1];
  assert.ok(Math.abs(ratio - 1.5) / 1.5 <= 0.03, String(ratio));
});

// TC-852-1
test("f0 = 0 のフレームは pitch を掛けても 0 のまま", () => {
  const x = vowelWithGap(); // 前後 0.5 秒が無音
  const a = engine.analyze(x);
  assert.ok(Array.from(a.f0).some(v => v === 0), "無声フレームが無い");
  const r = render(engine, a, { pitch: 1.5 }, x.length);
  for (let i = 0; i < a.f0.length; i++) if (a.f0[i] === 0) assert.equal(r.f0[i], 0, `frame ${i}`);
});

// TC-853-1
test("ap は分解時のものと同一", () => {
  const r = render(engine, analysis(), ALL, N_SAMPLES, stretchPartner(B, N1));
  assert.equal(maxAbsDiff(r.ap, G.ap), 0);
});

// TC-854-1
test("再合成に使う sp は、同じ params の modifiedDb と 1e-6 dB 以内で一致", () => {
  const partner = stretchPartner(B, N1);
  const r = render(engine, analysis(), ALL, N_SAMPLES, partner);
  for (const frame of [0, 50, 100, 150, 200]) {
    const { modifiedDb } = envelopeAt(G.sp, frame, ALL, partner);
    const rowDb = Float64Array.from(r.sp.subarray(frame * F, (frame + 1) * F), dbNoEps);
    assert.ok(maxAbsDiff(rowDb, modifiedDb) <= 1e-6, `frame ${frame}`);
  }
});

// TC-855-1
test("相手を指定しても出力の長さは元音と同じ", () => {
  const r = render(engine, analysis(), ALL, N_SAMPLES, stretchPartner(B, N1));
  assert.equal(r.y.length, N_SAMPLES);
});

// ---------------------------------------------------------------- Python 版との照合

import { goldenDsp, goldenDspSpAll, dspMeta } from "./golden.mjs";

const META = dspMeta();
const CASES = Object.keys(META.cases);
const partnerFor = raw => (raw.morph ? stretchPartner(B, N1) : null);

// TC-860-1
test("7 つのパラメータの組の dB 列が Python 版と 1e-6 dB 以内で一致", () => {
  for (const name of CASES) {
    const raw = META.cases[name];
    const partner = partnerFor(raw);
    const sp = render(engine, analysis(), raw, N_SAMPLES, partner).sp;
    const expected = goldenDsp(name).db;
    for (const [row, frame] of META.frames.entries()) {
      const got = Float64Array.from(sp.subarray(frame * F, (frame + 1) * F), dbNoEps);
      const want = expected.subarray(row * F, (row + 1) * F);
      assert.ok(maxAbsDiff(got, want) <= 1e-6, `${name} / frame ${frame}: ${maxAbsDiff(got, want)}`);
    }
  }
});

// TC-861-1
test("7 つのパラメータの組の再合成音が Python 版と 1e-6 以内で一致", () => {
  for (const name of CASES) {
    const raw = META.cases[name];
    const r = render(engine, analysis(), raw, N_SAMPLES, partnerFor(raw));
    const d = maxAbsDiff(r.y, goldenDsp(name).y);
    assert.ok(d <= 1e-6, `${name}: ${d}`);
  }
});

// TC-862-1
test("全パラメータの組で、加工後の sp 全体が Python 版と 1e-6 dB 以内で一致", () => {
  const raw = META.cases.all;
  const sp = render(engine, analysis(), raw, N_SAMPLES, partnerFor(raw)).sp;
  const got = Float64Array.from(sp, dbNoEps);
  const want = Float64Array.from(goldenDspSpAll(), dbNoEps);
  const d = maxAbsDiff(got, want);
  assert.ok(d <= 1e-6, String(d));
});
