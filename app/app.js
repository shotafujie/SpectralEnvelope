// 画面のスクリプト（008-browser-app）。今はアダプタを窓口として公開するだけ。
import { createAdapter } from "../engine/adapter.mjs";

window.engine = createAdapter();
