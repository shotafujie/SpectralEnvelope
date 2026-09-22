// 音声のバイト列を 44100Hz モノラルの Float64Array にする（008-browser-app / SPEC-920〜922）。
// ブラウザの decodeAudioData に任せるので、メインスレッドで呼ぶ。
import { engineError } from "./errors.mjs";

export const FS = 44100;
export const MIN_SAMPLES = FS; // 1.0 秒
export const MAX_SAMPLES = 10 * FS; // 10.0 秒

const toArrayBuffer = data => {
  if (data instanceof ArrayBuffer) return data;
  if (ArrayBuffer.isView(data)) return data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
  throw engineError("decode_failed", "音声として読み取れませんでした");
};

export async function decodeAudio(data) {
  let buf;
  try {
    // 出力先が 44100Hz なので、decodeAudioData がその周波数へ直して返す
    buf = await new OfflineAudioContext(1, 1, FS).decodeAudioData(toArrayBuffer(data));
  } catch {
    throw engineError("decode_failed", "音声として読み取れませんでした");
  }

  const n = Math.min(buf.length, MAX_SAMPLES); // 10 秒を超えた分は捨てる
  const x = new Float64Array(n);
  for (let ch = 0; ch < buf.numberOfChannels; ch++) {
    const c = buf.getChannelData(ch);
    for (let i = 0; i < n; i++) x[i] += c[i];
  }
  if (buf.numberOfChannels > 1) for (let i = 0; i < n; i++) x[i] /= buf.numberOfChannels;

  if (n < MIN_SAMPLES) throw engineError("too_short", "1 秒以上の音が要ります");
  return x;
}
