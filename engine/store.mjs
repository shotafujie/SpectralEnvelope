// 分解結果の保持（008-browser-app）。id を発行し、古い順に最大 10 件だけ持つ。
// sp と ap は Float32 に落として持ち、取り出すときに Float64 へ戻す（SPEC-915〜918）。
// ブラウザ API に触れないので Node でもそのまま動く。
const FS = 44100;
const FFT_SIZE = 2048;
export const CAPACITY = 10;

const hex8 = () => [...crypto.getRandomValues(new Uint8Array(4))].map(b => b.toString(16).padStart(2, "0")).join("");

// 情報（画面へ渡す値の組）。SPEC-924〜929
function infoOf(e) {
  const voiced = [];
  let sum = 0;
  for (let i = 0; i < e.f0.length; i++) {
    if (e.f0[i] > 0) {
      voiced.push(i);
      sum += e.f0[i];
    }
  }
  return {
    id: e.id,
    fs: FS,
    fftSize: FFT_SIZE,
    duration: e.duration,
    frames: e.f0.length,
    f0Mean: voiced.length ? sum / voiced.length : 0,
    voicedFrames: voiced,
    source: e.source,
  };
}

export function createStore({ capacity = CAPACITY } = {}) {
  const entries = new Map(); // id → entry（Map は挿入順を保つので、これが分解した順になる）

  const newId = () => {
    let id = hex8();
    while (entries.has(id)) id = hex8();
    return id;
  };

  return {
    get size() {
      return entries.size;
    },

    // 分解結果を入れて id を返す。溢れた分は入れた順に古いものから捨てる（SPEC-911）
    put({ f0, t, sp, ap, samples, source }) {
      const id = newId();
      entries.set(id, {
        id,
        f0: Float64Array.from(f0),
        t: Float64Array.from(t),
        spF32: Float32Array.from(sp),
        apF32: Float32Array.from(ap),
        samples: Float64Array.from(samples),
        source,
        duration: samples.length / FS,
      });
      while (entries.size > capacity) entries.delete(entries.keys().next().value);
      return id;
    },

    // 保持しているものをそのまま返す（sp と ap は Float32 のまま）。無ければ null
    get(id) {
      return entries.get(id) ?? null;
    },

    // 再合成・包絡の経路（007）へ渡す形。sp と ap を Float64 に戻す
    analysis(id) {
      const e = entries.get(id);
      if (!e) return null;
      return { f0: e.f0, t: e.t, sp: Float64Array.from(e.spF32), ap: Float64Array.from(e.apF32) };
    },

    list() {
      return [...entries.values()].map(infoOf);
    },
  };
}
