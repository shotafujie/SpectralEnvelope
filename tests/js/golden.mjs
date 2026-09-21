// テスト用: 照合用データ（tests/golden/）の読み込みと、包絡差の計算。
// エンジンの実装には依存しない。
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
export const GOLDEN = path.join(ROOT, "tests/golden");
export const F = 1025;

export function readF64(name) {
  const b = readFileSync(path.join(GOLDEN, name));
  return new Float64Array(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
}

export function golden1s() {
  const g = {};
  for (const k of ["x", "f0", "t", "sp", "ap", "y"]) g[k] = readF64(`world-a-1s.${k}.f64`);
  return g;
}

export const vowel3s = () => readF64("vowel-a-3s.f64");
export const partnerLogSp = () => readF64("partner-i-1.5s.logsp.f64"); // /i/ 1.5 秒（301×1025）
export const vowel10s = () => readF64("vowel-a-10s.f64");
export const vowelWithGap = () => readF64("vowel-a-gap-2.5s.f64"); // 前後 0.5 秒が無音（無声フレームを含む）

export const db = v => 10 * Math.log10(v + 1e-12);

export function maxAbsDiff(a, b, map = v => v) {
  if (a.length !== b.length) throw new Error(`長さが違う: ${a.length} と ${b.length}`);
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(map(a[i]) - map(b[i])));
  return m;
}

// 001 の envelope_diff() と同じ: 双方で f0 > 0 のフレーム、50〜8000Hz のビンで dB の差の絶対値の平均
export function envelopeDiff(spA, f0A, spB, f0B) {
  const n = Math.min(f0A.length, f0B.length);
  let sum = 0, count = 0;
  for (let i = 0; i < n; i++) {
    if (!(f0A[i] > 0 && f0B[i] > 0)) continue;
    for (let k = 0; k < F; k++) {
      const f = (k * 44100) / 2048;
      if (f < 50 || f > 8000) continue;
      sum += Math.abs(db(spA[i * F + k]) - db(spB[i * F + k]));
      count++;
    }
  }
  return sum / count;
}

// DSP の照合用データ（007-engine-dsp）
export const goldenDsp = name => ({
  db: readF64(`dsp/dsp-${name}.db.f64`),   // 5 フレーム × 1025（10·log10(sp)、1e-12 を足さない）
  y: readF64(`dsp/dsp-${name}.y.f64`),
});
export const goldenDspSpAll = () => readF64("dsp/dsp-all.sp.f64");
export const dspMeta = () => JSON.parse(readFileSync(path.join(GOLDEN, "dsp/dsp-meta.json"), "utf8"));
