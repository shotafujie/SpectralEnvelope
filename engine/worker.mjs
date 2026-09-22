// Worker の入口（008-browser-app）。006 のエンジンと 007 の DSP、保持をここに置く。
// sp / ap はここから出さない（ADR-0001 の決定 1）。
import { createEngine } from "./world-engine.mjs";
import { createStore } from "./store.mjs";
import { render } from "./render.mjs";
import { envelopeAt, stretchPartner, F } from "./dsp/envelope.mjs";
import { EPS } from "./dsp/curves.mjs";
import { engineError } from "./errors.mjs";

const store = createStore();
const ready = createEngine();

const held = id => {
  const a = store.analysis(id);
  if (!a) throw engineError("not_found", "その録音は残っていません");
  return a;
};

// morph の相手を id から引き、A のフレーム数に伸縮した log_sp にする
function partnerLogSp(params, framesA) {
  const id = params?.morph?.id;
  if (!id) return null;
  const b = held(id);
  const logB = Float64Array.from(b.sp, v => Math.log(v + EPS));
  return stretchPartner(logB, framesA);
}

const handlers = {
  // samples は転送で受け取った 44100Hz モノラルの Float64Array
  analyze(engine, { samples, source }) {
    const a = engine.analyze(samples);
    const id = store.put({ ...a, samples, source });
    return store.list().find(info => info.id === id);
  },

  envelope(engine, { id, frame, params }) {
    const a = held(id);
    return envelopeAt(a.sp, frame, params, partnerLogSp(params, a.sp.length / F));
  },

  synthesize(engine, { id, params }) {
    const a = held(id);
    const n = store.get(id).samples.length;
    const { y } = render(engine, a, params, n, partnerLogSp(params, a.sp.length / F));
    return Float32Array.from(y);
  },

  original(engine, { id }) {
    const e = store.get(id);
    if (!e) throw engineError("not_found", "その録音は残っていません");
    return Float32Array.from(e.samples);
  },

  list() {
    return store.list();
  },
};

// 大きい配列はコピーせずに渡す
const transfersOf = value => {
  const vals = ArrayBuffer.isView(value) ? [value] : value && typeof value === "object" ? Object.values(value) : [];
  return vals.filter(ArrayBuffer.isView).map(v => v.buffer);
};

self.onmessage = async ({ data: { seq, name, args } }) => {
  const engine = await ready; // 読み込み前に届いた呼び出しは、ここで待つ（SPEC-909）
  try {
    const handler = handlers[name];
    if (!handler) throw new Error(`未知の呼び出しです（${name}）`);
    const value = handler(engine, args);
    self.postMessage({ seq, ok: true, value }, transfersOf(value));
  } catch (e) {
    self.postMessage({ seq, ok: false, code: e.code || "failed", message: String(e && e.message) });
  }
};
