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
