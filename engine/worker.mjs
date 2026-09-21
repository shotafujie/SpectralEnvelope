// Worker の入口（008-browser-app）。006 のエンジンと 007 の DSP、保持をここに置く。
// sp / ap はここから出さない（ADR-0001 の決定 1）。
import { createEngine } from "./world-engine.mjs";
import { createStore } from "./store.mjs";

const store = createStore();
const ready = createEngine();

const handlers = {
  // samples は転送で受け取った 44100Hz モノラルの Float64Array
  analyze(engine, { samples, source }) {
    const a = engine.analyze(samples);
    const id = store.put({ ...a, samples, source });
    return store.list().find(info => info.id === id);
  },

  list() {
    return store.list();
  },
};

self.onmessage = async ({ data: { seq, name, args } }) => {
  const engine = await ready; // 読み込み前に届いた呼び出しは、ここで待つ（SPEC-909）
  try {
    const handler = handlers[name];
    if (!handler) throw new Error(`未知の呼び出しです（${name}）`);
    self.postMessage({ seq, ok: true, value: handler(engine, args) });
  } catch (e) {
    self.postMessage({ seq, ok: false, code: e.code || "failed", message: String(e && e.message) });
  }
};
