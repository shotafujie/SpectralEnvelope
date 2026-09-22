// 再合成の経路（007-engine-dsp）。加工した sp と f0 × pitch で 006 のエンジンを呼ぶ。
// ap は分解時のものをそのまま使う。戻り値には、その再合成に渡した配列も含める（008 の描画で使う）。
import { normalizeParams } from "./dsp/params.mjs";
import { applyEnvelope } from "./dsp/envelope.mjs";

export function render(engine, analysis, params, nSamples, partnerLogSp = null) {
  const p = normalizeParams(params);
  const sp = applyEnvelope(analysis.sp, p, partnerLogSp);
  const f0 = Float64Array.from(analysis.f0, v => v * p.pitch); // 0（無声）は 0 のまま
  const ap = analysis.ap;
  return { y: engine.synthesize(f0, sp, ap, nSamples), f0, sp, ap };
}
