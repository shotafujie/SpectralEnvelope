// 分解結果の保持（008-browser-app）
import { test } from "node:test";
import assert from "node:assert/strict";
import { createStore } from "../../engine/store.mjs";
import { createEngine } from "../../engine/world-engine.mjs";
import { envelopeAt } from "../../engine/dsp/envelope.mjs";
import { golden1s, maxAbsDiff, F } from "./golden.mjs";

const FS = 44100;

// frames×F の分解結果を作る。値は保持の検査に使うだけなので中身は問わない
function fakeAnalysis(frames, { source = "録音", seconds = frames * 0.005 } = {}) {
  const n = frames * F;
  const sp = new Float64Array(n);
  const ap = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    sp[i] = (i % 97) * 1e-4 + 1e-6;
    ap[i] = ((i % 31) / 31) * 0.9;
  }
  return {
    f0: Float64Array.from({ length: frames }, (_, i) => (i % 5 === 0 ? 0 : 100 + (i % 20))),
    t: Float64Array.from({ length: frames }, (_, i) => i * 0.005),
    sp,
    ap,
    samples: new Float64Array(Math.round(seconds * FS)),
    source,
  };
}

// ---------------------------------------------------------------- id の発行

// TC-910-1
test("id は 8 文字の小文字 16 進で、分解のたびに異なる", () => {
  const s = createStore();
  const ids = [s.put(fakeAnalysis(3)), s.put(fakeAnalysis(3)), s.put(fakeAnalysis(3))];
  for (const id of ids) assert.match(id, /^[0-9a-f]{8}$/);
  assert.equal(new Set(ids).size, 3);
});

// ---------------------------------------------------------------- 保持の件数

test("10 件目までは取り出せる", () => {
  const s = createStore();
  const ids = Array.from({ length: 10 }, () => s.put(fakeAnalysis(3)));
  for (const id of ids) assert.ok(s.get(id), `${id} が取り出せない`);
  assert.equal(s.size, 10);
});

test("11 件目を入れると最も古い 1 件が消える", () => {
  const s = createStore();
  const ids = Array.from({ length: 11 }, () => s.put(fakeAnalysis(3)));
  assert.equal(s.get(ids[0]), null);
  for (const id of ids.slice(1)) assert.ok(s.get(id), `${id} が取り出せない`);
  assert.equal(s.size, 10);
});

test("途中で取り出しても、消えるのは入れた順に古いものである", () => {
  const s = createStore();
  const ids = Array.from({ length: 10 }, () => s.put(fakeAnalysis(3)));
  s.get(ids[0]); // 取り出しても古さは変わらない
  s.put(fakeAnalysis(3));
  assert.equal(s.get(ids[0]), null);
  assert.ok(s.get(ids[1]));
});

test("保持していない id は null になる", () => {
  const s = createStore();
  assert.equal(s.get("deadbeef"), null);
  assert.equal(s.analysis("deadbeef"), null);
});

test("list は分解した順の情報を返す", () => {
  const s = createStore();
  const a = s.put(fakeAnalysis(3, { source: "録音" }));
  const b = s.put(fakeAnalysis(3, { source: "a.wav" }));
  assert.deepEqual(s.list().map(i => i.id), [a, b]);
  assert.deepEqual(s.list().map(i => i.source), ["録音", "a.wav"]);
});

test("情報は fs・fftSize・frames・duration・f0Mean・voicedFrames を持つ", () => {
  const s = createStore();
  const a = fakeAnalysis(20, { seconds: 1.5 });
  const id = s.put(a);
  const info = s.list()[0];
  const voiced = [...a.f0.keys()].filter(i => a.f0[i] > 0);
  const mean = voiced.reduce((t, i) => t + a.f0[i], 0) / voiced.length;
  assert.equal(info.id, id);
  assert.equal(info.fs, 44100);
  assert.equal(info.fftSize, 2048);
  assert.equal(info.frames, 20);
  assert.ok(Math.abs(info.duration - 1.5) < 1e-9, `duration=${info.duration}`);
  assert.ok(Math.abs(info.f0Mean - mean) < 1e-9, `f0Mean=${info.f0Mean}`);
  assert.deepEqual([...info.voicedFrames], voiced);
});

test("有声フレームが無いとき f0Mean は 0 になる", () => {
  const s = createStore();
  const a = fakeAnalysis(10);
  a.f0.fill(0);
  s.put(a);
  assert.equal(s.list()[0].f0Mean, 0);
  assert.deepEqual([...s.list()[0].voicedFrames], []);
});

// ---------------------------------------------------------------- 保持の形と量

// TC-915-1
test("sp と ap は Float32、f0・時刻・元の音声サンプルは Float64 のまま保持する", () => {
  const s = createStore();
  const id = s.put(fakeAnalysis(5, { seconds: 1.0 }));
  const e = s.get(id);
  assert.ok(e.spF32 instanceof Float32Array);
  assert.ok(e.apF32 instanceof Float32Array);
  assert.ok(e.f0 instanceof Float64Array);
  assert.ok(e.t instanceof Float64Array);
  assert.ok(e.samples instanceof Float64Array);
  assert.equal(e.spF32.length, 5 * F);
  assert.equal(e.apF32.length, 5 * F);
});

// TC-916-1
test("10 秒 × 10 件の sp と ap の保持量は 170MB 未満", () => {
  const s = createStore();
  const a = fakeAnalysis(2001, { seconds: 10.0 });
  for (let i = 0; i < 10; i++) s.put(a);
  const bytes = s.list().reduce((t, info) => {
    const e = s.get(info.id);
    return t + e.spF32.byteLength + e.apF32.byteLength;
  }, 0);
  assert.ok(bytes < 170 * 2 ** 20, `${bytes} バイト`);
});

test("analysis は保持した Float32 を Float64 に戻して返す", () => {
  const s = createStore();
  const a = fakeAnalysis(4, { seconds: 1.0 });
  const id = s.put(a);
  const got = s.analysis(id);
  assert.ok(got.sp instanceof Float64Array);
  assert.ok(got.ap instanceof Float64Array);
  assert.equal(got.sp.length, a.sp.length);
  assert.equal(maxAbsDiff(got.sp, Float64Array.from(a.sp, v => Math.fround(v))), 0);
});

// ---------------------------------------------------------------- Float32 化の影響

// TC-917-1
test("Float32 で保持した sp からの再合成音は、Float64 のままと 1e-6 以内で一致する", async () => {
  const e = await createEngine();
  const g = golden1s();
  const s = createStore();
  const id = s.put({ f0: g.f0, t: g.t, sp: g.sp, ap: g.ap, samples: g.x, source: "照合" });
  const kept = s.analysis(id);
  const y64 = e.synthesize(g.f0, g.sp, g.ap, g.x.length);
  const y32 = e.synthesize(kept.f0, kept.sp, kept.ap, g.x.length);
  assert.ok(maxAbsDiff(y64, y32) <= 1e-6, `最大差 ${maxAbsDiff(y64, y32)}`);
});

// TC-918-1
test("Float32 で保持した sp からの modifiedDb は、Float64 のままと 1e-3 dB 以内で一致する", () => {
  const g = golden1s();
  const s = createStore();
  const id = s.put({ f0: g.f0, t: g.t, sp: g.sp, ap: g.ap, samples: g.x, source: "照合" });
  const kept = s.analysis(id);
  const params = { formant: 1.2, tilt: 6, smooth: 3, bands: [2, -3, 4, -1] };
  for (const frame of [0, 50, 100]) {
    const a = envelopeAt(g.sp, frame, params);
    const b = envelopeAt(kept.sp, frame, params);
    const d = maxAbsDiff(a.modifiedDb, b.modifiedDb);
    assert.ok(d <= 1e-3, `フレーム ${frame} の最大差 ${d} dB`);
  }
});
