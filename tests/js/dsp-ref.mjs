// テスト用の独立計算（007-engine-dsp）。実装とは別の道筋で期待値を作るためのもの。
// 実装のモジュールは import しない。
export const F = 1025;
export const FS = 44100;
export const FFT_SIZE = 2048;
export const EPS = 1e-12;
export const DB_TO_LN = Math.log(10) / 10;
export const BAND_EDGES = [500, 1500, 4000];
export const CROSSFADE_OCT = 1 / 3;
export const CURVE_FREQS = Array.from({ length: 20 }, (_, j) => 50 * 400 ** (j / 19));

export const freq = k => (k * FS) / FFT_SIZE;
export const logSp = v => Math.log(v + EPS);
export const db = v => 10 * Math.log10(v + EPS);

export function tiltGainDb(tilt) {
  return Array.from({ length: F }, (_, k) => tilt * Math.log2(Math.max(freq(k), 20) / 1000));
}

export function bandGainDb(bands) {
  return Array.from({ length: F }, (_, k) => {
    const f = Math.max(freq(k), 1e-9);
    for (let i = 0; i < BAND_EDGES.length; i++) {
      const x = Math.log2(f / BAND_EDGES[i]);
      if (Math.abs(x) < CROSSFADE_OCT) {
        const w = (1 - Math.cos((Math.PI * (x + CROSSFADE_OCT)) / (2 * CROSSFADE_OCT))) / 2;
        return bands[i] + (bands[i + 1] - bands[i]) * w;
      }
    }
    // クロスフェードの外: 境界で区切られた 4 つの帯のどれか
    let idx = 0;
    while (idx < BAND_EDGES.length && f > BAND_EDGES[idx]) idx++;
    return bands[idx];
  });
}

export function curveGainDb(curve) {
  return Array.from({ length: F }, (_, k) => {
    const x = Math.log2(Math.max(freq(k), 1e-9));
    const xs = CURVE_FREQS.map(Math.log2);
    if (x <= xs[0]) return curve[0];
    if (x >= xs[19]) return curve[19];
    let j = 0;
    while (x > xs[j + 1]) j++;
    const w = (x - xs[j]) / (xs[j + 1] - xs[j]);
    return curve[j] + (curve[j + 1] - curve[j]) * w;
  });
}

// 定義どおりの正規直交 DCT-II / IDCT（O(N²)）。実装側は次数を絞って計算するので別の道筋になる
export function smoothRowRef(row, M) {
  const N = row.length;
  const a = m => (m === 0 ? Math.sqrt(1 / N) : Math.sqrt(2 / N)); // 正規直交 DCT-II の係数
  const c = new Float64Array(M);
  for (let m = 0; m < M; m++) {
    let acc = 0;
    for (let k = 0; k < N; k++) acc += row[k] * Math.cos((Math.PI * (2 * k + 1) * m) / (2 * N));
    c[m] = a(m) * acc;
  }
  const out = new Float64Array(N);
  for (let k = 0; k < N; k++) {
    let acc = 0;
    for (let m = 0; m < M; m++) acc += a(m) * c[m] * Math.cos((Math.PI * (2 * k + 1) * m) / (2 * N));
    out[k] = acc;
  }
  return out;
}

export function interpRow(row, positions) {
  const N = row.length;
  return positions.map(p => {
    if (p <= 0) return row[0];
    if (p >= N - 1) return row[N - 1];
    const lo = Math.floor(p), w = p - lo;
    return row[lo] * (1 - w) + row[lo + 1] * w;
  });
}

export function stretchRef(logB, nB, nA) {
  const out = new Float64Array(nA * F);
  for (let i = 0; i < nA; i++) {
    const p = nA > 1 ? (i * (nB - 1)) / (nA - 1) : 0;
    const lo = Math.floor(p), hi = Math.min(lo + 1, nB - 1), w = p - lo;
    for (let k = 0; k < F; k++) out[i * F + k] = (1 - w) * logB[lo * F + k] + w * logB[hi * F + k];
  }
  return out;
}
