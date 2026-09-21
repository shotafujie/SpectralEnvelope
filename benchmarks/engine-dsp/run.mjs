// DSP の速さを測り、基準値（baseline.json）を書き出す（007-engine-dsp）。
// 使い方: node benchmarks/engine-dsp/run.mjs [--write]
import { readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createEngine } from "../../engine/world-engine.mjs";
import { applyEnvelope, envelopeAt, stretchPartner } from "../../engine/dsp/envelope.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const GOLDEN = path.join(HERE, "../../tests/golden");
const read = name => {
  const b = readFileSync(path.join(GOLDEN, name));
  return new Float64Array(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
};
// 全パラメータ（morph を含む）。相手は伸縮済みの log_sp を渡す
const ALL = { formant: 1.2, smooth: 30, tilt: 3, bands: [2, -2, 4, -4],
  curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j), pitch: 1.3, morph: { ratio: 0.4 } };

function median(fn, reps = 5) {
  fn();
  const t = [];
  for (let i = 0; i < reps; i++) {
    const t0 = performance.now();
    fn();
    t.push((performance.now() - t0) / 1000);
  }
  return +t.sort((a, b) => a - b)[reps >> 1].toFixed(4);
}

const engine = await createEngine();
const sp3 = engine.analyze(read("vowel-a-3s.f64")).sp;
const sp10 = engine.analyze(read("vowel-a-10s.f64")).sp;
const B = read("partner-i-1.5s.logsp.f64");
const partner3 = stretchPartner(B, sp3.length / 1025);
const partner10 = stretchPartner(B, sp10.length / 1025);
const result = {
  median_seconds: {
    apply_3s: median(() => applyEnvelope(sp3, ALL, partner3)),
    apply_10s: median(() => applyEnvelope(sp10, ALL, partner10)),
    envelope_frame_10s: median(() => envelopeAt(sp10, 1000, ALL, partner10)),
  },
  conditions: { cpu: os.cpus()[0].model, node: process.version,
    input: "tests/golden/vowel-a-{3s,10s}.f64（合成母音 /a/）を 006 のエンジンで分解した sp",
    params: ALL, method: "初回を除く 5 回の中央値" },
};
console.log(JSON.stringify(result, null, 1));
if (process.argv.includes("--write"))
  writeFileSync(path.join(HERE, "baseline.json"), JSON.stringify(result, null, 1) + "\n");
