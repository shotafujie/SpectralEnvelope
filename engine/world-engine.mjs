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
    synthesize() {
      throw new Error("未実装");
    },
  };
}
