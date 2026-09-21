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

// 相手 B の log_sp（N_B×F）を、A のフレーム数 nA に線形伸縮する
export function stretchPartner(logB, nA) {
  const framesB = logB.length / F;
  if (!Number.isInteger(framesB) || framesB < 1)
    throw new RangeError(`相手の log_sp の長さは ${F} の倍数です（${logB.length}）`);
  const out = new Float64Array(nA * F);
  for (let i = 0; i < nA; i++) {
    const pos = nA > 1 ? (i * (framesB - 1)) / (nA - 1) : 0;
    const lo = Math.floor(pos), hi = Math.min(lo + 1, framesB - 1), w = pos - lo;
    for (let k = 0; k < F; k++) out[i * F + k] = (1 - w) * logB[lo * F + k] + w * logB[hi * F + k];
  }
  return out;
}

// 加工の本体（log 形式）。段を分けて逐次適用するときもこちらを使う。
// sp 形式を繰り返すと、1e-12 を足す操作が段ごとに入り、平滑化がその差を全ビンに広げる（SPEC-819）
export function applyEnvelopeLog(logSp, params, partnerLogSp = null) {
  const p = normalizeParams(params);
  const frames = logSp.length / F;
  if (!Number.isInteger(frames)) throw new RangeError(`log_sp の長さは ${F} の倍数です（${logSp.length}）`);

  const log = logSp.slice();
  // morph: 伸縮済みの相手の log_sp と混ぜる
  if (p.morph && partnerLogSp) {
    if (partnerLogSp.length !== log.length)
      throw new RangeError(`伸縮済みの相手の長さは ${log.length} です（${partnerLogSp.length}）`);
    const a = p.morph.ratio;
    for (let i = 0; i < log.length; i++) log[i] = (1 - a) * log[i] + a * partnerLogSp[i];
  }

  const shifted = smoothLog(shiftFormant(log, frames, p.formant), frames, p.smooth);

  const gain = gainLn(p);
  const out = new Float64Array(logSp.length);
  for (let i = 0; i < frames; i++)
    for (let k = 0; k < F; k++) out[i * F + k] = shifted[i * F + k] + gain[k];
  return out;
}

// sp 形式: exp(log 形式(ln(sp + EPS)))
export function applyEnvelope(sp, params, partnerLogSp = null) {
  if (!Number.isInteger(sp.length / F)) throw new RangeError(`sp の長さは ${F} の倍数です（${sp.length}）`);
  const log = new Float64Array(sp.length);
  for (let i = 0; i < sp.length; i++) log[i] = Math.log(sp[i] + EPS);
  const out = applyEnvelopeLog(log, params, partnerLogSp);
  for (let i = 0; i < out.length; i++) out[i] = Math.exp(out[i]);
  return out;
}
