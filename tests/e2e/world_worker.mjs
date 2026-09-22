// TC-714-1: モジュール Worker の中でエンジンを import し、照合用データの x を分解して f0 を返す
import { createEngine } from "../../engine/world-engine.mjs";

try {
  const x = new Float64Array(await (await fetch("../golden/world-a-1s.x.f64")).arrayBuffer());
  const engine = await createEngine();
  self.postMessage({ f0: Array.from(engine.analyze(x).f0) });
} catch (e) {
  self.postMessage({ error: String(e && e.stack || e) });
}
