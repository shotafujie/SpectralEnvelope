// ブラウザ版の画面（008-browser-app）。v0.1.0 の jig/index.html を写し、
// fetch("/api/...") をアダプタ（window.engine）の呼び出しに置き換えたもの。
// 呼び出しは毎回 window.engine から引く（テストがここを包んで観測するため）。
import { createAdapter } from "../engine/adapter.mjs";

window.engine = createAdapter();
"use strict";

const TIP_SUFFIX = "（ダブルクリックで初期値に戻る）";

const PARAMS = [
  { name: "formant", label: "formant", min: 0.6, max: 1.6, step: 0.01, init: 1.0, digits: 2,
    tip: "包絡の周波数軸を伸縮する。上げると声道が短くなる方向＝子供っぽく、下げると太く大人っぽくなる" },
  { name: "tilt", label: "tilt dB/oct", min: -12, max: 12, step: 0.1, init: 0, digits: 1,
    tip: "1kHz を支点にした傾き。正で明るく硬い声、負でこもった声になる" },
  { name: "band0", label: "〜500Hz", min: -12, max: 12, step: 0.1, init: 0, digits: 1, group: "バンドゲイン dB",
    tip: "500Hz 以下を上下させる。上げると低い響きが増えて太くなる" },
  { name: "band1", label: "〜1.5kHz", min: -12, max: 12, step: 0.1, init: 0, digits: 1,
    tip: "500〜1500Hz を上下させる。母音の骨格（第1・第2フォルマント）が変わる" },
  { name: "band2", label: "〜4kHz", min: -12, max: 12, step: 0.1, init: 0, digits: 1,
    tip: "1500〜4000Hz を上下させる。下げるとこもり、上げると子音がはっきりする" },
  { name: "band3", label: "4kHz〜", min: -12, max: 12, step: 0.1, init: 0, digits: 1,
    tip: "4kHz 以上を上下させる。息や擦れの成分が増減する" },
  { name: "smooth", label: "smooth", min: 0, max: 80, step: 1, init: 0, digits: 0, group: "平滑化・ピッチ",
    tip: "包絡をケプストラムの低次だけ残して平滑化する。小さいほどのっぺりして声色が失われる（0 で無効）" },
  { name: "pitch", label: "pitch ×", min: 0.5, max: 2.0, step: 0.01, init: 1.0, digits: 2,
    tip: "再合成に使う fo（基本周波数＝声の高さ）の倍率。包絡はそのままで高さだけ変える" },
];

const PRESETS = [
  ["素通し", {}, "すべて初期値に戻す"],
  ["子供っぽく", { formant: 1.25, pitch: 1.15 }, "formant 1.25 / pitch 1.15"],
  ["太く", { formant: 0.85, tilt: -3.0 }, "formant 0.85 / tilt −3.0"],
  ["こもる", { band0: 4, band1: 0, band2: -6, band3: -10 }, "バンドゲイン +4 / 0 / −6 / −10"],
  ["のっぺり", { smooth: 16 }, "smooth 16 で包絡を平坦にする"],
];

const MAX_RECORD_MS = 10000;
const DEBOUNCE_MS = 300;
const NYQUIST = 22050;
const F_MIN = 50;
const Y_RANGE = 70;
const BAND_FREQS = [500, 1500, 4000];
const PLOT = { left: 56, right: 784, top: 12, bottom: 348 };
const SVG_NS = "http://www.w3.org/2000/svg";
const MAX_HISTORY = 10;
const CURVE_FREQS = Array.from({ length: 20 }, (_, j) => 50 * 400 ** (j / 19));
const CURVE_LIMIT = 12;

const $ = (sel) => document.querySelector(sel);
const recBtn = $("#rec");
const elapsedEl = $("#elapsed");
const metaEl = $("#meta");
const errorEl = $("#error");
const graph = $("#graph");
const frameInput = $("#frame");
const frameValue = $("#frame-value");
const unvoicedEl = $("#unvoiced");
const playOrigBtn = $("#play-orig");
const playModBtn = $("#play-mod");
const openFileBtn = $("#open-file");
const fileInput = $("#file");
const currentSel = $("#current");
const partnerSel = $("#partner");
const mixInput = $("#p-mix");
const mixValue = $("#mix-value");
const curveReadout = $("#curve-readout");

const state = {
  info: null,          // 今の分解結果の情報
  voiced: new Set(),
  lastPlayed: null,    // "original" | "processed" | null
  playToken: 0,
  debounceTimer: null,
  recorder: null,
  history: [],         // {info, label}（分解順、最大 MAX_HISTORY 件）
  analyzedCount: 0,
  curve: new Array(20).fill(0),
  dragging: null,      // ドラッグ中の制御点番号
};

// ---------------------------------------------------------------- エラー表示

function showError(message) { errorEl.textContent = message; }
function clearError() { errorEl.textContent = ""; }


// ---------------------------------------------------------------- パラメータ

const sliders = {};

function formatValue(p, v) { return Number(v).toFixed(p.digits); }

function buildParams() {
  const box = $("#params");
  for (const p of PARAMS) {
    if (p.group) {
      const g = document.createElement("div");
      g.className = "sub";
      g.textContent = p.group;
      box.append(g);
    }
    const row = document.createElement("div");
    row.className = "param";
    row.innerHTML =
      `<label for="p-${p.name}">${p.label}</label>` +
      `<input id="p-${p.name}" name="${p.name}" type="range" min="${p.min}" max="${p.max}" step="${p.step}"` +
      ` value="${p.init}" data-tip="${p.tip}${TIP_SUFFIX}">` +
      `<output id="${p.name}-value">${formatValue(p, p.init)}</output>`;
    box.append(row);
    const input = row.querySelector("input");
    const out = row.querySelector("output");
    sliders[p.name] = { p, input, out };
    input.addEventListener("input", () => {
      out.textContent = formatValue(p, input.value);
      markChanged(input, p.init);
      scheduleEnvelope();
    });
    input.addEventListener("dblclick", () => setParam(p.name, p.init));
  }
}

function markChanged(input, init) {
  input.classList.toggle("changed", Number(input.value) !== Number(init));
}

function setParam(name, value) {
  const s = sliders[name];
  s.input.value = value;
  s.out.textContent = formatValue(s.p, s.input.value);
  markChanged(s.input, s.p.init);
  scheduleEnvelope();
}

function setAllParams(values) {
  for (const p of PARAMS) setParam(p.name, values[p.name] ?? p.init);
  setMix(0);
  for (let j = 0; j < state.curve.length; j++) setCurvePoint(j, 0);
}

function setMix(value) {
  mixInput.value = value;
  mixValue.textContent = Number(mixInput.value).toFixed(2);
  markChanged(mixInput, 0);
  scheduleEnvelope();
}

mixInput.addEventListener("input", () => setMix(mixInput.value));
mixInput.addEventListener("dblclick", () => setMix(0));
partnerSel.addEventListener("change", scheduleEnvelope);

function currentParams() {
  const v = (n) => Number(sliders[n].input.value);
  return {
    formant: v("formant"),
    tilt: v("tilt"),
    bands: [v("band0"), v("band1"), v("band2"), v("band3")],
    smooth: v("smooth"),
    pitch: v("pitch"),
    curve: [...state.curve],
    ...(partnerSel.value ? { morph: { id: partnerSel.value, ratio: Number(mixInput.value) } } : {}),
  };
}

function buildPresets() {
  const box = $("#presets");
  for (const [name, values, tip] of PRESETS) {
    const b = document.createElement("button");
    b.type = "button";
    b.dataset.preset = name;
    b.dataset.tip = tip;
    b.textContent = name;
    b.addEventListener("click", () => setAllParams(values));
    box.append(b);
  }
  $("#reset").addEventListener("click", () => setAllParams({}));
}

// ---------------------------------------------------------------- 包絡グラフ

const xOf = (f) => PLOT.left + (PLOT.right - PLOT.left) * Math.log(f / F_MIN) / Math.log(NYQUIST / F_MIN);

function svg(tag, attrs, parent) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (parent) parent.append(el);
  return el;
}

const MID_Y = (PLOT.top + PLOT.bottom) / 2;
const PX_PER_DB = (PLOT.bottom - PLOT.top) / Y_RANGE;
const curveY = (g) => (MID_Y - g * PX_PER_DB).toFixed(2);

function drawFrame() {
  graph.replaceChildren();
  graph.dataset.plotLeft = PLOT.left;
  graph.dataset.plotRight = PLOT.right;
  graph.dataset.plotTop = PLOT.top;
  graph.dataset.plotBottom = PLOT.bottom;
  for (const f of [100, 200, 500, 1000, 2000, 5000, 10000, 20000]) {
    svg("line", { class: "grid", "data-freq": f, x1: xOf(f), x2: xOf(f), y1: PLOT.top, y2: PLOT.bottom }, graph);
    svg("text", { x: xOf(f), y: PLOT.bottom + 16, "text-anchor": "middle" }, graph)
      .textContent = f >= 1000 ? `${f / 1000}k` : String(f);
  }
  for (const f of BAND_FREQS) {
    svg("line", { class: "band-line", "data-freq": f, x1: xOf(f), x2: xOf(f), y1: PLOT.top, y2: PLOT.bottom }, graph);
  }
  svg("g", { id: "y-grid" }, graph);
  svg("path", { id: "orig-line", d: "" }, graph);
  svg("path", { id: "partner-line", d: "", style: "display: none" }, graph);
  svg("path", { id: "mod-line", d: "" }, graph);
  svg("line", { id: "curve-zero", x1: PLOT.left, x2: PLOT.right, y1: MID_Y, y2: MID_Y }, graph);
  svg("path", { id: "curve-line", d: "" }, graph);
  CURVE_FREQS.forEach((f, j) => {
    const c = svg("circle", {
      class: "curve-point", r: 6, cx: xOf(f).toFixed(2), cy: curveY(0), "data-index": j, "data-gain": 0,
      "data-tip": `${Math.round(f)} Hz 付近のゲイン。上下にドラッグして調整、ダブルクリックで 0 に戻る`,
    }, graph);
    c.addEventListener("pointerdown", (e) => startCurveDrag(e, j));
    c.addEventListener("dblclick", () => setCurvePoint(j, 0));
  });
  drawCurveLine();
}

// ---------------------------------------------------------------- ゲインカーブ

const curvePoint = (j) => graph.querySelector(`.curve-point[data-index="${j}"]`);

function drawCurveLine() {
  const pts = CURVE_FREQS.map((_, j) => {
    const c = curvePoint(j);
    return `${c.getAttribute("cx")},${c.getAttribute("cy")}`;
  });
  graph.querySelector("#curve-line").setAttribute("d", "M" + pts.join("L"));
}

function setCurvePoint(j, gain) {
  const g = Math.min(Math.max(Math.round(gain * 10) / 10, -CURVE_LIMIT), CURVE_LIMIT) || 0;
  const changed = state.curve[j] !== g;
  state.curve[j] = g;
  const c = curvePoint(j);
  c.setAttribute("cy", curveY(g));
  c.dataset.gain = g;
  drawCurveLine();
  if (changed) scheduleEnvelope();
}

function showCurveReadout(j) {
  const g = state.curve[j];
  curveReadout.textContent =
    `制御点 ${j + 1}: ${Math.round(CURVE_FREQS[j])} Hz / ${g >= 0 ? "+" : ""}${g.toFixed(1)} dB`;
  curveReadout.hidden = false;
}

function svgY(clientX, clientY) {
  const p = graph.createSVGPoint();
  p.x = clientX;
  p.y = clientY;
  return p.matrixTransform(graph.getScreenCTM().inverse()).y;
}

function startCurveDrag(e, j) {
  e.preventDefault();
  state.dragging = j;
  curvePoint(j).classList.add("active");
  showCurveReadout(j);
}

window.addEventListener("pointermove", (e) => {
  if (state.dragging === null) return;
  const j = state.dragging;
  setCurvePoint(j, (MID_Y - svgY(e.clientX, e.clientY)) / PX_PER_DB);
  showCurveReadout(j);
});

function endCurveDrag() {
  if (state.dragging === null) return;
  curvePoint(state.dragging).classList.remove("active");
  state.dragging = null;
  curveReadout.hidden = true;
}

window.addEventListener("pointerup", endCurveDrag);
window.addEventListener("pointercancel", endCurveDrag);

function drawEnvelope(env) {
  const { freq, originalDb: orig, modifiedDb: mod } = env;
  let top = -Infinity;
  for (let k = 0; k < freq.length; k++) if (freq[k] >= F_MIN) top = Math.max(top, orig[k]);
  top += 5;
  const bottom = top - Y_RANGE;
  graph.dataset.ymax = top;
  graph.dataset.ymin = bottom;

  const yOf = (db) => {
    const c = Math.min(Math.max(db, bottom), top);
    return PLOT.top + (PLOT.bottom - PLOT.top) * (top - c) / Y_RANGE;
  };
  const path = (values) => {
    const parts = [];
    for (let k = 0; k < freq.length; k++) {
      if (freq[k] < F_MIN) continue;
      parts.push(`${parts.length ? "L" : "M"}${xOf(freq[k]).toFixed(1)},${yOf(values[k]).toFixed(1)}`);
    }
    return parts.join("");
  };

  const yGrid = graph.querySelector("#y-grid");
  yGrid.replaceChildren();
  for (let db = Math.ceil(bottom / 10) * 10; db <= top; db += 10) {
    svg("line", { class: "grid", x1: PLOT.left, x2: PLOT.right, y1: yOf(db), y2: yOf(db) }, yGrid);
    svg("text", { x: PLOT.left - 6, y: yOf(db) + 3, "text-anchor": "end" }, yGrid).textContent = `${db}`;
  }
  graph.querySelector("#orig-line").setAttribute("d", path(orig));
  const partnerLine = graph.querySelector("#partner-line");
  if (env.partnerDb) {
    partnerLine.setAttribute("d", path(env.partnerDb));
    partnerLine.style.display = "";
  } else {
    partnerLine.setAttribute("d", "");
    partnerLine.style.display = "none";
  }
  graph.querySelector("#mod-line").setAttribute("d", path(mod));
}

async function refreshEnvelope() {
  if (!state.info) return;
  const id = state.info.id;
  try {
    const env = await window.engine.envelope(id, Number(frameInput.value), currentParams());
    drawEnvelope(env);
    graph.dataset.id = id;
  } catch (e) {
    if (e.code === "superseded") return;  // 新しい要求に置き換わっただけ
    showError(e.message);
  }
}

function scheduleEnvelope() {
  if (!state.info) return;
  clearTimeout(state.debounceTimer);
  state.debounceTimer = setTimeout(refreshEnvelope, DEBOUNCE_MS);
}

// ---------------------------------------------------------------- フレーム選択

function updateFrameLabel() {
  const f = Number(frameInput.value);
  frameValue.textContent = `${f}（${(f * 5 / 1000).toFixed(3)} 秒）`;
  unvoicedEl.hidden = state.voiced.has(f);
}

frameInput.addEventListener("input", () => { updateFrameLabel(); scheduleEnvelope(); });

// ---------------------------------------------------------------- 録音・分解

function setRecording(on) {
  recBtn.dataset.state = on ? "recording" : "idle";
  recBtn.textContent = on ? "■ 停止" : "● 録音";
}

async function startRecording() {
  clearError();
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    showError(`マイクを使えませんでした: ${e.message || e.name}`);
    return;
  }
  const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "";
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  const chunks = [];
  const started = performance.now();
  const ticker = setInterval(() => {
    elapsedEl.textContent = `${((performance.now() - started) / 1000).toFixed(1)} 秒`;
  }, 100);
  const limit = setTimeout(() => stopRecording(), MAX_RECORD_MS);

  recorder.addEventListener("dataavailable", (e) => { if (e.data.size) chunks.push(e.data); });
  recorder.addEventListener("stop", () => {
    clearInterval(ticker);
    clearTimeout(limit);
    stream.getTracks().forEach((t) => t.stop());
    setRecording(false);
    analyze(new Blob(chunks, { type: recorder.mimeType || "audio/webm" }), "録音");
  });
  state.recorder = recorder;
  openFileBtn.disabled = true;
  recorder.start();
  elapsedEl.textContent = "0.0 秒";
  setRecording(true);
}

function stopRecording() {
  const r = state.recorder;
  state.recorder = null;
  if (r && r.state !== "inactive") {
    recBtn.disabled = true;  // stop イベント → 送信完了まで押せない
    r.stop();
  }
}

async function analyze(blob, source) {
  recBtn.disabled = true;
  openFileBtn.disabled = true;
  const prevMeta = metaEl.textContent;
  metaEl.textContent = "分解中…";
  try {
    addToHistory(await window.engine.analyze(await blob.arrayBuffer(), source), source);
  } catch (e) {
    metaEl.textContent = state.info ? prevMeta : "";
    showError(e.message);
  } finally {
    recBtn.disabled = false;
    openFileBtn.disabled = false;
  }
}

openFileBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  fileInput.value = "";  // 同じファイルを続けて選んでも change が発火するように
  if (!file) return;
  clearError();
  analyze(file, file.name);
});

function option(value, label) {
  const o = document.createElement("option");
  o.value = value;
  o.textContent = label;
  return o;
}

function addToHistory(info, source) {
  state.analyzedCount += 1;
  const label = `#${state.analyzedCount} ${source} ${info.duration.toFixed(2)} 秒`;
  state.history.push({ info, label });
  while (state.history.length > MAX_HISTORY) state.history.shift();
  const partner = partnerSel.value;
  currentSel.replaceChildren(...state.history.map((h) => option(h.info.id, h.label)));
  partnerSel.replaceChildren(option("", "なし"), ...state.history.map((h) => option(h.info.id, h.label)));
  partnerSel.value = state.history.some((h) => h.info.id === partner) ? partner : "";
  currentSel.value = info.id;
  activate(info);
}

currentSel.addEventListener("change", () => {
  const entry = state.history.find((h) => h.info.id === currentSel.value);
  if (entry) activate(entry.info);
});

function activate(info) {
  state.info = info;
  state.voiced = new Set(info.voicedFrames);
  state.lastPlayed = null;
  stopPlayback();
  elapsedEl.textContent = "";
  metaEl.textContent =
    `${info.duration.toFixed(2)} 秒 / ${info.frames} フレーム / 平均 fo ${info.f0Mean.toFixed(1)} Hz`;
  const v = info.voicedFrames;
  frameInput.max = info.frames - 1;
  frameInput.value = v.length ? v[Math.floor(v.length / 2)] : 0;
  frameInput.disabled = false;
  playOrigBtn.disabled = false;
  playModBtn.disabled = false;
  updateFrameLabel();
  clearTimeout(state.debounceTimer);
  refreshEnvelope();
}

recBtn.addEventListener("click", () => {
  if (state.recorder) stopRecording();
  else startRecording();
});

// ---------------------------------------------------------------- 再生

// TODO(008 タスク 11): AudioBuffer での再生をここへ移す（SPEC-1000〜1006）
function stopPlayback() {
  state.playToken++;
}

// ---------------------------------------------------------------- ツールチップ

const tooltip = $("#tooltip");

function showTooltip(el) {
  tooltip.textContent = el.dataset.tip;
  tooltip.hidden = false;
  const r = el.getBoundingClientRect();
  const box = tooltip.getBoundingClientRect();
  const left = Math.min(Math.max(8, r.left + r.width / 2 - box.width / 2), window.innerWidth - box.width - 8);
  const below = r.bottom + 8;
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${below + box.height < window.innerHeight ? below : r.top - box.height - 8}px`;
}

function hideTooltip() {
  tooltip.hidden = true;
}

function tipTarget(e) {
  const el = e.target;
  return el instanceof Element ? el.closest("[data-tip]") : null;
}

document.addEventListener("pointerover", (e) => {
  const el = tipTarget(e);
  if (el) showTooltip(el);
  else hideTooltip();
});
document.addEventListener("pointerleave", hideTooltip);
document.addEventListener("focusin", (e) => {
  const el = tipTarget(e);
  if (el) showTooltip(el);
  else hideTooltip();
});
document.addEventListener("focusout", hideTooltip);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") hideTooltip(); });

// ---------------------------------------------------------------- 起動

buildParams();
buildPresets();
drawFrame();
