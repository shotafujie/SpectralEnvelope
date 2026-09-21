// アダプタが拒否に使う理由（code）。画面もテストも code で分岐する（008-browser-app）。
export function engineError(code, message) {
  const e = new Error(message || code);
  e.code = code;
  return e;
}
