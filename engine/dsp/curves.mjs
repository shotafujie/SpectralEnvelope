// 周波数軸のゲイン（007-engine-dsp）。tilt / bands / curve は、フレームに依らない 1025 要素のゲイン列になる。
export const FS = 44100;
export const FFT_SIZE = 2048;
export const F = FFT_SIZE / 2 + 1;
export const EPS = 1e-12;
export const DB_TO_LN = Math.log(10) / 10; // dB 表示値（10·log10 sp）を log_sp の単位へ
const BAND_EDGES = [500, 1500, 4000];
const CROSSFADE_OCT = 1 / 3;
export const CURVE_FREQS = Array.from({ length: 20 }, (_, j) => 50 * 400 ** (j / 19));

export const freqAxis = () => Float64Array.from({ length: F }, (_, k) => (k * FS) / FFT_SIZE);

function tiltGainDb(freq, tilt) {
  return freq.map(f => tilt * Math.log2(Math.max(f, 20) / 1000));
}

function bandGainDb(freq, bands) {
  return freq.map(raw => {
    const f = Math.max(raw, 1e-9);
    for (let i = 0; i < BAND_EDGES.length; i++) {
      const x = Math.log2(f / BAND_EDGES[i]);
      if (Math.abs(x) < CROSSFADE_OCT) {
        const w = (1 - Math.cos((Math.PI * (x + CROSSFADE_OCT)) / (2 * CROSSFADE_OCT))) / 2;
        return bands[i] + (bands[i + 1] - bands[i]) * w;
      }
    }
    let idx = 0;
    while (idx < BAND_EDGES.length && f > BAND_EDGES[idx]) idx++;
    return bands[idx];
  });
}

function curveGainDb(freq, curve) {
  const xs = CURVE_FREQS.map(Math.log2);
  return freq.map(raw => {
    const x = Math.log2(Math.max(raw, 1e-9));
    if (x <= xs[0]) return curve[0];
    if (x >= xs[xs.length - 1]) return curve[curve.length - 1];
    let j = 0;
    while (x > xs[j + 1]) j++;
    return curve[j] + (curve[j + 1] - curve[j]) * ((x - xs[j]) / (xs[j + 1] - xs[j]));
  });
}

// tilt + bands + curve をまとめた、log_sp に加算する 1 本のゲイン列
export function gainLn(params) {
  const freq = freqAxis();
  const tilt = tiltGainDb(freq, params.tilt);
  const bands = bandGainDb(freq, params.bands);
  const curve = curveGainDb(freq, params.curve);
  return Float64Array.from({ length: F }, (_, k) => (tilt[k] + bands[k] + curve[k]) * DB_TO_LN);
}
