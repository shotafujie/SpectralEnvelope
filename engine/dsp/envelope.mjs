// 包絡の加工（007-engine-dsp）。morph → formant → smooth → tilt → bands → curve の順に適用する。
// 計算はすべて log_sp = ln(sp + 1e-12) の上で行い、最後に exp で戻す。
import { normalizeParams } from "./params.mjs";
import { EPS, F, gainLn } from "./curves.mjs";
import { smoothLog } from "./smooth.mjs";

export { F };

// formant 比 r: 加工後のビン k は、加工前をビン位置 k / r で線形補間した値。
// k / r が F − 1 を超えるビンは最終ビンの値
function shiftFormant(log, frames, r) {
  if (r === 1) return log;
  const out = new Float64Array(log.length);
  for (let i = 0; i < frames; i++) {
    const base = i * F;
    for (let k = 0; k < F; k++) {
      const p = k / r;
      if (p >= F - 1) {
        out[base + k] = log[base + F - 1];
      } else {
        const lo = Math.floor(p), w = p - lo;
        out[base + k] = log[base + lo] * (1 - w) + log[base + lo + 1] * w;
      }
    }
  }
  return out;
}

export function applyEnvelope(sp, params, partnerLogSp = null) {
  const p = normalizeParams(params);
  const frames = sp.length / F;
  if (!Number.isInteger(frames)) throw new RangeError(`sp の長さは ${F} の倍数です（${sp.length}）`);

  const log = new Float64Array(sp.length);
  for (let i = 0; i < sp.length; i++) log[i] = Math.log(sp[i] + EPS);

  const shifted = smoothLog(shiftFormant(log, frames, p.formant), frames, p.smooth);

  const gain = gainLn(p);
  const out = new Float64Array(sp.length);
  for (let i = 0; i < frames; i++)
    for (let k = 0; k < F; k++) out[i * F + k] = Math.exp(shifted[i * F + k] + gain[k]);
  return out;
}
