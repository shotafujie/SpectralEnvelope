// WORLD の WASM エンジン（006-wasm-world）。
// 分解（harvest → cheaptrick → d4c）と再合成を、Float64Array の入出力で提供する。状態は持たない。
import { WORLD_WASM_SHA256, WORLD_MJS_SHA256 } from "./world/stamp.mjs";

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

// ブラウザでは glue と wasm に同じ印を付けて読み込む（009-pages-deploy / SPEC-1140〜1142）。
// 印はスタンプの wasm の SHA-256 の先頭 12 桁で、両方に同じ値を付けるので新旧の対が混ざらない。
// Node の glue は wasm をファイルとして読むため、印を付けない。
const IN_NODE = typeof process !== "undefined" && !!process.versions?.node;
const MARK = IN_NODE ? "" : `?v=${WORLD_WASM_SHA256.slice(0, 12)}`;

export async function createEngine() {
  const { default: createWorld } = await import(`./world/world.mjs${MARK}`);
  const M = await createWorld(
    IN_NODE ? undefined : { locateFile: name => new URL(`./world/${name}${MARK}`, import.meta.url).href },
  );
  if (!IN_NODE) console.log(`WORLD 成果物 wasm=${WORLD_WASM_SHA256} glue=${WORLD_MJS_SHA256}`);

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
