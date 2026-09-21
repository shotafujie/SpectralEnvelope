// 包絡の加工（007-engine-dsp）。morph → formant → smooth → tilt → bands → curve の順に適用する。
// 計算はすべて log_sp = ln(sp + 1e-12) の上で行い、最後に exp で戻す。
import { normalizeParams } from "./params.mjs";
import { EPS, F, gainLn } from "./curves.mjs";

export { F };

export function applyEnvelope(sp, params, partnerLogSp = null) {
  const p = normalizeParams(params);
  const frames = sp.length / F;
  if (!Number.isInteger(frames)) throw new RangeError(`sp の長さは ${F} の倍数です（${sp.length}）`);

  const log = new Float64Array(sp.length);
  for (let i = 0; i < sp.length; i++) log[i] = Math.log(sp[i] + EPS);

  const gain = gainLn(p);
  const out = new Float64Array(sp.length);
  for (let i = 0; i < frames; i++)
    for (let k = 0; k < F; k++) out[i * F + k] = Math.exp(log[i * F + k] + gain[k]);
  return out;
}
