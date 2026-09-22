"""ブラウザ版の速さを測り、基準値（baseline.json）を書き出す（008-browser-app）。

使い方:
    .venv/bin/python benchmarks/browser-app/run.py           # 計測して表示するだけ
    .venv/bin/python benchmarks/browser-app/run.py --write   # baseline.json を上書きする

仕様は docs/items/008-browser-app/spec.md の SPEC-1040〜1043。
"""

import argparse
import base64
import functools
import http.server
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests import audio_fixtures as af  # noqa: E402

HERE = Path(__file__).resolve().parent
REPS = 5


class Static(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".wasm": "application/wasm"}

    def log_message(self, *args):
        pass


def serve():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Static, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


ANALYZE = """async (b) => {
    const bytes = () => Uint8Array.from(atob(b), c => c.charCodeAt(0));
    const t = [];
    for (let i = 0; i < REPS; i++) {
        const t0 = performance.now();
        await window.engine.analyze(bytes(), '録音');
        t.push((performance.now() - t0) / 1000);
    }
    return t;
}"""

SYNTHESIZE = """async (b) => {
    const bytes = () => Uint8Array.from(atob(b), c => c.charCodeAt(0));
    const info = await window.engine.analyze(bytes(), '録音');
    const params = { formant: 1.2, tilt: 3, bands: [2, -2, 4, -4], smooth: 30, pitch: 1.2,
                     curve: Array.from({ length: 20 }, (_, j) => -3 + 0.3 * j) };
    const t = [];
    for (let i = 0; i < REPS; i++) {
        const t0 = performance.now();
        await window.engine.synthesize(info.id, params);
        t.push((performance.now() - t0) / 1000);
    }
    return t;
}"""

SLIDER_TO_GRAPH = """async () => {
    const line = document.querySelector('#mod-line');
    const input = document.querySelector('input[name=formant]');
    const t = [];
    for (let i = 0; i < REPS; i++) {
        const before = line.getAttribute('d');
        const t0 = performance.now();
        input.value = String(1.05 + 0.05 * i);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        await new Promise(resolve => {
            const check = () => (line.getAttribute('d') !== before ? resolve() : requestAnimationFrame(check));
            check();
        });
        t.push((performance.now() - t0) / 1000);
    }
    return t;
}"""


def measure():
    wav3 = af.wav_bytes(af.vowel("a", 3.0))
    b64 = base64.b64encode(wav3).decode()
    server, url = serve()
    with tempfile.TemporaryDirectory() as tmp:
        files = {name: Path(tmp) / f"{name}.wav" for name in ("a", "i")}
        files["a"].write_bytes(wav3)
        files["i"].write_bytes(af.wav_bytes(af.vowel("i", 3.0)))
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
                page = browser.new_page(base_url=url)
                page.set_default_timeout(60000)
                page.goto("/app/index.html")
                page.wait_for_function("() => window.engine !== undefined")
                version = browser.version

                analyze = page.evaluate(ANALYZE.replace("REPS", str(REPS)), b64)
                synthesize = page.evaluate(SYNTHESIZE.replace("REPS", str(REPS)), b64)

                # つまみ → グラフ: 相手を選んだ状態で測る（相手の伸縮を含める）
                for key in ("i", "a"):
                    prev = page.evaluate("() => document.querySelector('#graph').dataset.id || ''")
                    page.set_input_files("#file", str(files[key]))
                    page.wait_for_function(
                        "prev => { const id = document.querySelector('#graph').dataset.id;"
                        " return id && id !== prev; }", arg=prev)
                partner = page.eval_on_selector("#partner option:nth-child(2)", "o => o.value")
                page.select_option("#partner", partner)
                page.eval_on_selector("#p-mix", "el => { el.value = '0.5';"
                                                " el.dispatchEvent(new Event('input', { bubbles: true })); }")
                page.wait_for_timeout(1500)
                slider = page.evaluate(SLIDER_TO_GRAPH.replace("REPS", str(REPS)))
                browser.close()
        finally:
            server.shutdown()

    return {
        "median_seconds": {
            "analyze_3s": round(statistics.median(analyze), 3),
            "envelope_after_slider": round(statistics.median(slider), 3),
            "synthesize_3s": round(statistics.median(synthesize), 3),
        },
        "samples": {"analyze_3s": analyze, "envelope_after_slider": slider, "synthesize_3s": synthesize},
        "conditions": {
            "cpu": cpu_name(),
            "chromium": version,
            "input": "合成母音 /a/ 3.0 秒の wav（tests/audio_fixtures.vowel）",
            "method": f"ブラウザ内で {REPS} 回測った中央値。analyze はデコードを含み、"
                      "envelope_after_slider は 300ms のデバウンスと相手の伸縮（mix 0.5）を含む",
        },
    }


def cpu_name():
    if platform.system() == "Darwin":
        return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                              capture_output=True, text=True).stdout.strip()
    return platform.processor() or platform.machine()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="baseline.json を上書きする")
    args = ap.parse_args()

    result = measure()
    for key, value in result["median_seconds"].items():
        print(f"{key:24s} {value:7.3f} 秒")
    if args.write:
        (HERE / "baseline.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
        print(f"\n書き出しました: {HERE / 'baseline.json'}")


if __name__ == "__main__":
    main()
