// WORLD の WASM エンジン（006-wasm-world）
import { test } from "node:test";
import assert from "node:assert/strict";
import { createEngine } from "../../engine/world-engine.mjs";
import { golden1s, vowel3s, vowel10s, maxAbsDiff, db, envelopeDiff, F } from "./golden.mjs";

const isPage = v => Number.isInteger(v) && v > 0 && v % 65536 === 0;

// ---------------------------------------------------------------- 生成

// TC-710-1
test("createEngine は Promise を返し、analyze と synthesize を持つエンジンに解決される", async () => {
  const p = createEngine();
  assert.equal(typeof p.then, "function");
  const e = await p;
  assert.equal(typeof e.analyze, "function");
  assert.equal(typeof e.synthesize, "function");
});

// TC-711-1
test("分析条件のプロパティ", async () => {
  const e = await createEngine();
  assert.deepEqual([e.fs, e.fftSize, e.framePeriod, e.bins], [44100, 2048, 5, 1025]);
});

// TC-712-1
test("録音の下限と上限のプロパティ", async () => {
  const e = await createEngine();
  assert.deepEqual([e.minSamples, e.maxSamples], [44100, 441000]);
});

// TC-713-1
test("Node から import して 5 秒以内に createEngine が解決される", async () => {
  const mod = await import("../../engine/world-engine.mjs");
  const timeout = new Promise((_, reject) => setTimeout(() => reject(new Error("5 秒を超えた")), 5000).unref());
  const e = await Promise.race([mod.createEngine(), timeout]);
  assert.equal(typeof e.analyze, "function");
});

// TC-748-1
test("生成直後の memoryBytes は 65536 の正の倍数", async () => {
  const e = await createEngine();
  assert.ok(isPage(e.memoryBytes), String(e.memoryBytes));
});

// ---------------------------------------------------------------- 分解

const G = golden1s();
const N1 = G.f0.length; // 201
let shared; // 分解結果を使い回すテスト用（照合用データの x を 1 回だけ分解する）
async function analyzed() {
  if (!shared) {
    const e = await createEngine();
    shared = { e, r: e.analyze(G.x.slice()) };
  }
  return shared;
}

// TC-720-1
test("analyze は f0 / t / sp / ap の Float64Array を返す", async () => {
  const { r } = await analyzed();
  assert.deepEqual(Object.keys(r).sort(), ["ap", "f0", "sp", "t"]);
  for (const k of ["f0", "t", "sp", "ap"]) assert.ok(r[k] instanceof Float64Array, k);
});

// TC-721-1
test("1 秒の入力で f0 と t の長さは 201", async () => {
  const { r } = await analyzed();
  assert.equal(N1, 201);
  assert.equal(r.f0.length, N1);
  assert.equal(r.t.length, N1);
});

// TC-721-2
test("3 秒の入力で f0 と t の長さは 601", async () => {
  const r = (await createEngine()).analyze(vowel3s());
  assert.equal(r.f0.length, 601);
  assert.equal(r.t.length, 601);
});

// TC-721-3
test("10 秒の入力で f0 と t の長さは 2001", async () => {
  const r = (await createEngine()).analyze(vowel10s());
  assert.equal(r.f0.length, 2001);
  assert.equal(r.t.length, 2001);
});

// TC-722-1
test("sp と ap の長さは 201 × 1025", async () => {
  const { r } = await analyzed();
  assert.equal(r.sp.length, N1 * F);
  assert.equal(r.ap.length, N1 * F);
});

// TC-722-2
test("sp は行優先に並んでいる", async () => {
  const { r } = await analyzed();
  for (const [i, k] of [[0, 0], [100, 512], [200, 1024]])
    assert.ok(Math.abs(db(r.sp[i * F + k]) - db(G.sp[i * F + k])) <= 1e-6, `(${i}, ${k})`);
});

// TC-723-1
test("f0 は照合用データと 1e-6 以内で一致する", async () => {
  const { r } = await analyzed();
  assert.ok(maxAbsDiff(r.f0, G.f0) <= 1e-6);
});

// TC-723-2
test("無声（f0 = 0）の位置は照合用データと完全に一致する", async () => {
  const { r } = await analyzed();
  const unvoiced = f0 => Array.from(f0, (v, i) => (v === 0 ? i : -1)).filter(i => i >= 0);
  assert.deepEqual(unvoiced(r.f0), unvoiced(G.f0));
});

// TC-724-1
test("t は照合用データと 1e-9 以内で一致する", async () => {
  const { r } = await analyzed();
  assert.ok(maxAbsDiff(r.t, G.t) <= 1e-9);
});

// TC-725-1
test("sp の dB 値は照合用データと 1e-6 dB 以内で一致する", async () => {
  const { r } = await analyzed();
  assert.ok(maxAbsDiff(r.sp, G.sp, db) <= 1e-6);
});

// TC-726-1
test("ap は照合用データと 1e-6 以内で一致する", async () => {
  const { r } = await analyzed();
  assert.ok(maxAbsDiff(r.ap, G.ap) <= 1e-6);
});

// TC-727-1
test("analyze は引数の x を書き換えない", async () => {
  const e = await createEngine();
  const x = G.x.slice(), copy = x.slice();
  e.analyze(x);
  assert.deepEqual(x, copy);
});

// TC-743-1
test("長さちょうど minSamples の x は分解できる", async () => {
  const r = (await createEngine()).analyze(G.x.slice());
  assert.equal(G.x.length, 44100);
  assert.equal(r.f0.length, 201);
});

// TC-743-2
test("長さちょうど maxSamples の x は分解できる", async () => {
  const x = vowel10s();
  assert.equal(x.length, 441000);
  assert.equal((await createEngine()).analyze(x).f0.length, 2001);
});

// TC-748-2
test("10 秒を分解すると memoryBytes が広がり、65536 の倍数のまま", async () => {
  const e = await createEngine();
  const before = e.memoryBytes;
  e.analyze(vowel10s());
  assert.ok(e.memoryBytes > before);
  assert.ok(isPage(e.memoryBytes));
});

// ---------------------------------------------------------------- analyze の異常系

// TC-740-1
test("Float32Array は TypeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(new Float32Array(44100)), TypeError);
});

// TC-740-2
test("通常の配列は TypeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(Array.from(G.x)), TypeError);
});

// TC-740-3
test("undefined は TypeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(undefined), TypeError);
});

// TC-741-1
test("長さ 44099 は RangeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(G.x.slice(0, 44099)), RangeError);
});

// TC-741-2
test("長さ 0 は RangeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(new Float64Array(0)), RangeError);
});

// TC-742-1
test("長さ 441001 は RangeError", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(new Float64Array(441001)), RangeError);
});

// TC-746-1
test("analyze が例外を投げた後も、同じエンジンで正しく分解できる", async () => {
  const e = await createEngine();
  assert.throws(() => e.analyze(new Float64Array(0)), RangeError);
  assert.ok(maxAbsDiff(e.analyze(G.x.slice()).f0, G.f0) <= 1e-6);
});

// ---------------------------------------------------------------- 再合成

const L1 = Math.floor(N1 * 220.5); // 44320

// TC-730-1
test("n = 44100 で長さ 44100 の Float64Array を返す", async () => {
  const y = (await createEngine()).synthesize(G.f0, G.sp, G.ap, 44100);
  assert.ok(y instanceof Float64Array);
  assert.equal(y.length, 44100);
});

// TC-730-2
test("n = 1 で長さ 1", async () => {
  assert.equal((await createEngine()).synthesize(G.f0, G.sp, G.ap, 1).length, 1);
});

// TC-730-3
test("n = 50000（L より長い）で長さ 50000", async () => {
  assert.equal((await createEngine()).synthesize(G.f0, G.sp, G.ap, 50000).length, 50000);
});

// TC-731-1
test("再合成は照合用データの y と 1e-6 以内で一致する", async () => {
  const y = (await createEngine()).synthesize(G.f0, G.sp, G.ap, 44100);
  assert.ok(maxAbsDiff(y, G.y) <= 1e-6);
});

// TC-732-1
test("L を超えた部分はすべて 0", async () => {
  assert.equal(L1, 44320);
  const y = (await createEngine()).synthesize(G.f0, G.sp, G.ap, 50000);
  assert.ok(y.subarray(L1).every(v => v === 0));
});

// TC-732-2
test("n を長くしても先頭 44100 サンプルは照合用データと一致する", async () => {
  const y = (await createEngine()).synthesize(G.f0, G.sp, G.ap, 50000);
  assert.ok(maxAbsDiff(y.subarray(0, 44100), G.y) <= 1e-6);
});

// TC-733-1
test("synthesize は引数の f0 / sp / ap を書き換えない", async () => {
  const [f0, sp, ap] = [G.f0.slice(), G.sp.slice(), G.ap.slice()];
  (await createEngine()).synthesize(f0, sp, ap, 44100);
  assert.deepEqual(f0, G.f0);
  assert.deepEqual(sp, G.sp);
  assert.deepEqual(ap, G.ap);
});

// TC-734-1
test("3 秒の無加工往復で包絡差は 1.0dB 以下", async () => {
  const e = await createEngine();
  const x = vowel3s();
  const a = e.analyze(x);
  const b = e.analyze(e.synthesize(a.f0, a.sp, a.ap, x.length));
  const d = envelopeDiff(a.sp, a.f0, b.sp, b.f0);
  assert.ok(d <= 1.0, `${d} dB`);
});
