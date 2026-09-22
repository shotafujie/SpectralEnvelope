// パラメータの解釈（007-engine-dsp）。初期値の補完・クランプ・丸め・形式の検査を行う。
// 値の範囲と丸め方は v0.1.0 の仕様（SPEC-050〜055、401、502）と同じ。

export const CURVE_POINTS = 20;
export const BANDS = 4;

const num = (v, name) => {
  if (typeof v !== "number" || !Number.isFinite(v)) throw new TypeError(`${name} は数値で指定してください`);
  return v;
};

const clamp = (v, lo, hi, name) => Math.min(Math.max(num(v, name), lo), hi);

function clampList(v, length, name) {
  if (!Array.isArray(v) || v.length !== length)
    throw new TypeError(`${name} は ${length} 要素の配列で指定してください`);
  return v.map((e, i) => clamp(e, -12, 12, `${name}[${i}]`));
}

// 0 以下は 0（無効）、1〜9 は 10、81 以上は 80
function normalizeSmooth(v) {
  const n = Math.round(num(v, "smooth"));
  return n <= 0 ? 0 : Math.min(Math.max(n, 10), 80);
}

export function normalizeParams(params = {}) {
  const p = params ?? {};
  return {
    formant: p.formant === undefined ? 1.0 : clamp(p.formant, 0.6, 1.6, "formant"),
    tilt: p.tilt === undefined ? 0.0 : clamp(p.tilt, -12, 12, "tilt"),
    bands: p.bands === undefined ? [0, 0, 0, 0] : clampList(p.bands, BANDS, "bands"),
    smooth: p.smooth === undefined ? 0 : normalizeSmooth(p.smooth),
    pitch: p.pitch === undefined ? 1.0 : clamp(p.pitch, 0.5, 2.0, "pitch"),
    curve: p.curve === undefined ? new Array(CURVE_POINTS).fill(0) : clampList(p.curve, CURVE_POINTS, "curve"),
    morph: p.morph == null ? null : { ratio: p.morph.ratio === undefined ? 0 : clamp(p.morph.ratio, 0, 1, "morph.ratio") },
  };
}
