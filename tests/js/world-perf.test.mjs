// WORLD エンジンの性能（006-wasm-world）。測定条件は spec.md の非機能要件を参照
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { createEngine } from "../../engine/world-engine.mjs";
import { ROOT, vowel3s, vowel10s } from "./golden.mjs";

// 初回を除く 5 回の中央値（秒）
function median5(fn) {
  fn();
  const times = [];
  for (let i = 0; i < 5; i++) {
    const t0 = performance.now();
    fn();
    times.push((performance.now() - t0) / 1000);
  }
  return times.sort((a, b) => a - b)[2];
}

// TC-760-1
test("3 秒の analyze は 1.0 秒未満", async () => {
  const e = await createEngine(), x = vowel3s();
  const s = median5(() => e.analyze(x));
  assert.ok(s < 1.0, `${s} 秒`);
});

// TC-761-1
test("10 秒の analyze は 3.0 秒未満", async () => {
  const e = await createEngine(), x = vowel10s();
  const s = median5(() => e.analyze(x));
  assert.ok(s < 3.0, `${s} 秒`);
});

// TC-762-1
test("3 秒の synthesize は 0.1 秒未満", async () => {
  const e = await createEngine(), x = vowel3s();
  const r = e.analyze(x);
  const s = median5(() => e.synthesize(r.f0, r.sp, r.ap, x.length));
  assert.ok(s < 0.1, `${s} 秒`);
});

const BENCH = path.join(ROOT, "benchmarks/wasm-world");

// TC-763-1
test("基準値のファイルに 3 秒と 10 秒の analyze / synthesize の中央値がある", () => {
  const b = JSON.parse(readFileSync(path.join(BENCH, "baseline.json"), "utf8"));
  for (const d of ["3s", "10s"])
    for (const k of ["analyze", "synthesize"]) assert.ok(b.median_seconds[d][k] > 0, `${d} ${k}`);
});

// TC-763-2
test("計測に使ったコマンドが書かれている", () => {
  const readme = path.join(BENCH, "README.md");
  assert.ok(existsSync(readme));
  assert.ok(readFileSync(readme, "utf8").includes("node benchmarks/wasm-world/run.mjs"));
});
