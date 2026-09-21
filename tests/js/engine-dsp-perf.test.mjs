// DSP の性能（007-engine-dsp）。測定条件は spec.md の非機能要件を参照
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { createEngine } from "../../engine/world-engine.mjs";
import { applyEnvelope, envelopeAt } from "../../engine/dsp/envelope.mjs";
import { ROOT, vowel3s, vowel10s } from "./golden.mjs";

const ALL = { formant: 1.2, smooth: 30, tilt: 3, bands: [2, -2, 4, -4],
  curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j), pitch: 1.3 };

function median5(fn) {
  fn();
  const t = [];
  for (let i = 0; i < 5; i++) {
    const t0 = performance.now();
    fn();
    t.push((performance.now() - t0) / 1000);
  }
  return t.sort((a, b) => a - b)[2];
}

const engine = await createEngine();
const sp3 = engine.analyze(vowel3s()).sp;
const sp10 = engine.analyze(vowel10s()).sp;

// TC-880-1
test("3 秒（601 フレーム）の全パラメータ適用は 0.3 秒未満", () => {
  const s = median5(() => applyEnvelope(sp3, ALL));
  assert.ok(s < 0.3, `${s} 秒`);
});

// TC-881-1
test("10 秒（2001 フレーム）の全パラメータ適用は 1.0 秒未満", () => {
  const s = median5(() => applyEnvelope(sp10, ALL));
  assert.ok(s < 1.0, `${s} 秒`);
});

// TC-882-1
test("10 秒の分解結果に対する 1 フレーム分の dB 列は 0.02 秒未満", () => {
  const s = median5(() => envelopeAt(sp10, 1000, ALL));
  assert.ok(s < 0.02, `${s} 秒`);
});

const BENCH = path.join(ROOT, "benchmarks/engine-dsp");

// TC-883-1
test("基準値のファイルに 3 つの中央値がある", () => {
  const b = JSON.parse(readFileSync(path.join(BENCH, "baseline.json"), "utf8"));
  assert.ok(b.median_seconds.apply_3s > 0);
  assert.ok(b.median_seconds.apply_10s > 0);
  assert.ok(b.median_seconds.envelope_frame_10s > 0);
});

// TC-883-2
test("計測に使ったコマンドが書かれている", () => {
  const readme = path.join(BENCH, "README.md");
  assert.ok(existsSync(readme));
  assert.ok(readFileSync(readme, "utf8").includes("node benchmarks/engine-dsp/run.mjs"));
});
