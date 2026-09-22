// メインスレッド側の窓口（008-browser-app）。画面はここだけを見る。
// 実体は Worker 越しの呼び出しで、すべて Promise を返す。
import { decodeAudio } from "./decode.mjs";
import { engineError } from "./errors.mjs";

export function createAdapter({ workerUrl = new URL("./worker.mjs", import.meta.url), decode = decodeAudio } = {}) {
  const worker = new Worker(workerUrl, { type: "module" });
  const pending = new Map(); // seq → { resolve, reject }
  let seq = 0;
  let envelopeSeq = 0; // 最新の envelope の seq。これ以外の応答は捨てる

  worker.onmessage = ({ data }) => {
    const p = pending.get(data.seq);
    if (!p) return; // 取り消した呼び出しの応答
    pending.delete(data.seq);
    if (data.ok) p.resolve(data.value);
    else p.reject(engineError(data.code, data.message));
  };

  const call = (name, args, transfer = []) =>
    new Promise((resolve, reject) => {
      const s = ++seq;
      pending.set(s, { resolve, reject });
      worker.postMessage({ seq: s, name, args }, transfer);
      if (name === "envelope") envelopeSeq = s;
    });

  return {
    async analyze(data, source) {
      const samples = await decode(data); // デコードだけはメインスレッドで行う
      return call("analyze", { samples, source }, [samples.buffer]);
    },

    // 新しい呼び出しが来たら、前の呼び出しは superseded で拒否する（SPEC-907）
    envelope(id, frame, params) {
      const prev = envelopeSeq;
      const p = call("envelope", { id, frame, params });
      const old = pending.get(prev);
      if (old) {
        pending.delete(prev);
        old.reject(engineError("superseded", "新しい要求に置き換わりました"));
      }
      return p;
    },

    synthesize(id, params) {
      return call("synthesize", { id, params });
    },

    original(id) {
      return call("original", { id });
    },

    list() {
      return call("list", {});
    },
  };
}
