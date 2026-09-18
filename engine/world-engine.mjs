// WORLD の WASM エンジン（006-wasm-world）。
// 分解（harvest → cheaptrick → d4c）と再合成を、Float64Array の入出力で提供する。状態は持たない。
import createWorld from "./world/world.mjs";

const FS = 44100;
const FFT_SIZE = 2048;
const FRAME_PERIOD = 5;
const BINS = FFT_SIZE / 2 + 1;

export async function createEngine() {
  const M = await createWorld();
  return {
    fs: FS,
    fftSize: FFT_SIZE,
    framePeriod: FRAME_PERIOD,
    bins: BINS,
    minSamples: FS,
    maxSamples: 10 * FS,
    get memoryBytes() {
      return M.HEAPU8.buffer.byteLength;
    },
    analyze() {
      throw new Error("未実装");
    },
    synthesize() {
      throw new Error("未実装");
    },
  };
}
