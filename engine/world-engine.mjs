// WORLD の WASM エンジン（006-wasm-world）。
// 分解（harvest → cheaptrick → d4c）と再合成を、Float64Array の入出力で提供する。状態は持たない。
import createWorld from "./world/world.mjs";

const FS = 44100;
const FFT_SIZE = 2048;
const FRAME_PERIOD = 5;
const BINS = FFT_SIZE / 2 + 1;
const MIN_SAMPLES = FS; // 1.0 秒
const MAX_SAMPLES = 10 * FS; // 10.0 秒

function checkSignal(x) {
  if (!(x instanceof Float64Array)) throw new TypeError("x は Float64Array で渡してください");
  if (x.length < MIN_SAMPLES || x.length > MAX_SAMPLES)
    throw new RangeError(`x の長さは ${MIN_SAMPLES}〜${MAX_SAMPLES} サンプルです（${x.length}）`);
}

export async function createEngine() {
  const M = await createWorld();

  // 呼び出しの間だけ WASM のメモリを借り、戻る前に必ず返す
  function withBuffers(lengths, fn) {
    const ptrs = [];
    try {
      for (const n of lengths) ptrs.push(M._malloc(n * 8));
      return fn(ptrs);
    } finally {
      for (const p of ptrs) M._free(p);
    }
  }
  const view = (ptr, n) => new Float64Array(M.HEAPF64.buffer, ptr, n);
  const copyOut = (ptr, n) => view(ptr, n).slice();

  return {
    fs: FS,
    fftSize: FFT_SIZE,
    framePeriod: FRAME_PERIOD,
    bins: BINS,
    minSamples: MIN_SAMPLES,
    maxSamples: MAX_SAMPLES,
    get memoryBytes() {
      return M.HEAPU8.buffer.byteLength;
    },
    analyze(x) {
      checkSignal(x);
      const len = x.length;
      const n = M._world_n_frames(len, FS, FRAME_PERIOD);
      return withBuffers([len, n, n, n * BINS, n * BINS], ([px, pf0, pt, psp, pap]) => {
        view(px, len).set(x);
        M._world_harvest(px, len, FS, FRAME_PERIOD, pf0, pt);
        M._world_cheaptrick(px, len, FS, pf0, pt, n, FFT_SIZE, psp);
        M._world_d4c(px, len, FS, pf0, pt, n, FFT_SIZE, pap);
        return { f0: copyOut(pf0, n), t: copyOut(pt, n), sp: copyOut(psp, n * BINS), ap: copyOut(pap, n * BINS) };
      });
    },
    // 再合成の長さ L = floor(N · framePeriod / 1000 · fs)（pyworld と同じ）で合成し、先頭 n サンプルを返す。
    // n が L より長いとき、残りは 0
    synthesize(f0, sp, ap, n) {
      const frames = f0.length;
      if (sp.length !== frames * BINS || ap.length !== frames * BINS)
        throw new RangeError(`sp と ap の長さは f0 の長さ × ${BINS}（${frames * BINS}）です`);
      if (!(n >= 1 && n <= MAX_SAMPLES)) throw new RangeError(`n は 1〜${MAX_SAMPLES} です（${n}）`);
      const synthLength = Math.floor(((frames * FRAME_PERIOD) / 1000) * FS);
      return withBuffers([frames, frames * BINS, frames * BINS, synthLength], ([pf0, psp, pap, py]) => {
        view(pf0, frames).set(f0);
        view(psp, frames * BINS).set(sp);
        view(pap, frames * BINS).set(ap);
        M._world_synthesize(pf0, psp, pap, frames, FFT_SIZE, FS, FRAME_PERIOD, py, synthLength);
        const y = new Float64Array(n);
        y.set(view(py, Math.min(n, synthLength)));
        return y;
      });
    },
  };
}
