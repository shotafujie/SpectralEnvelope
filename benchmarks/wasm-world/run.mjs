// WORLD エンジンの速度を測り、基準値（baseline.json）を書き出す（ADR-0001 決定 5）。
// 使い方: node benchmarks/wasm-world/run.mjs [--write]
//   --write を付けると baseline.json を上書きする。付けなければ結果を表示するだけ
import { readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createEngine } from "../../engine/world-engine.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const GOLDEN = path.join(HERE, "../../tests/golden");
const read = name => {
  const b = readFileSync(path.join(GOLDEN, name));
  return new Float64Array(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
};

function median(fn, reps) {
  fn(); // 初回は除く
  const t = [];
  for (let i = 0; i < reps; i++) {
    const t0 = performance.now();
    fn();
    t.push((performance.now() - t0) / 1000);
  }
  return t.sort((a, b) => a - b)[reps >> 1];
}

const engine = await createEngine();
const result = { median_seconds: {} };
for (const [label, file] of [["3s", "vowel-a-3s.f64"], ["10s", "vowel-a-10s.f64"]]) {
  const x = read(file);
  const r = engine.analyze(x);
  result.median_seconds[label] = {
    analyze: +median(() => engine.analyze(x), 5).toFixed(4),
    synthesize: +median(() => engine.synthesize(r.f0, r.sp, r.ap, x.length), 5).toFixed(4),
  };
}
result.conditions = {
  cpu: os.cpus()[0].model,
  node: process.version,
  input: 'tests/golden/vowel-a-{3s,10s}.f64（合成母音 /a/）',
  method: "初回を除く 5 回の中央値",
};
console.log(JSON.stringify(result, null, 1));
if (process.argv.includes("--write")) writeFileSync(path.join(HERE, "baseline.json"), JSON.stringify(result, null, 1) + "\n");
