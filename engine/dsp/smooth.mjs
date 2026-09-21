// 平滑化（007-engine-dsp）: 正規直交 DCT-II をかけ、次数 M 以上の係数を 0 にして戻す。
// M ≤ 80 なので、必要な次数の係数だけを計算する（1 フレームあたり 2·M·F 回の積和）。
import { F } from "./curves.mjs";

const tables = new Map(); // M ごとの cos 表（同じ M の間は使い回す）

function cosTable(M) {
  let table = tables.get(M);
  if (!table) {
    table = new Float64Array(M * F);
    for (let m = 0; m < M; m++)
      for (let k = 0; k < F; k++) table[m * F + k] = Math.cos((Math.PI * (2 * k + 1) * m) / (2 * F));
    tables.set(M, table);
  }
  return table;
}

// log: 行優先の frames×F。M ≤ 0 のときは何もしない（新しい配列も作らない）
export function smoothLog(log, frames, M) {
  if (M <= 0) return log;
  const table = cosTable(M);
  const a0 = Math.sqrt(1 / F), a = Math.sqrt(2 / F);
  const out = new Float64Array(log.length);
  const c = new Float64Array(M);
  for (let i = 0; i < frames; i++) {
    const base = i * F;
    for (let m = 0; m < M; m++) {
      const row = m * F;
      let acc = 0;
      for (let k = 0; k < F; k++) acc += log[base + k] * table[row + k];
      c[m] = (m === 0 ? a0 : a) * acc;
    }
    for (let m = 0; m < M; m++) c[m] *= m === 0 ? a0 : a;
    for (let k = 0; k < F; k++) {
      let acc = 0;
      for (let m = 0; m < M; m++) acc += c[m] * table[m * F + k];
      out[base + k] = acc;
    }
  }
  return out;
}
