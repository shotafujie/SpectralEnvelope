"""Pages の設定と配信 URL（009-pages-deploy）。

配信が一度も走っていない間は落ちる。それは実装漏れではなく「まだ配信されていない」という事実。
"""

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPO = "shotafujie/SpectralEnvelope"
SITE = "https://shotafujie.github.io/SpectralEnvelope/"


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def test_TC_1128_1_Pagesの配信元はActions():
    assert gh("api", f"repos/{REPO}/pages")["build_type"] == "workflow"


def test_TC_1129_1_配信URLが200を返す():
    import urllib.request

    with urllib.request.urlopen(SITE, timeout=30) as res:
        assert res.status == 200
        body = res.read().decode()
    assert "app/" in body


def test_TC_1129_2_配信URLでファイルを読み込んで再生できる(browser, wav_files):
    ctx = browser.new_context()
    page = ctx.new_page()
    page.set_default_timeout(60000)
    try:
        page.goto(SITE)
        page.wait_for_selector("#rec")
        page.set_input_files("#file", str(wav_files["voice"]))
        page.wait_for_function("() => document.querySelector('#graph').dataset.id")
        assert page.get_attribute("#mod-line", "d")
        page.click("#play-mod")
        page.wait_for_function(
            "() => { const p = document.querySelector('#player');"
            " return p.dataset.source === 'processed' && p.dataset.playing !== '0'; }")
    finally:
        ctx.close()


def test_TC_1150_1_CIは10分未満():
    runs = gh("api", f"repos/{REPO}/actions/workflows/ci.yml/runs?branch=main&status=success&per_page=1")
    assert runs["total_count"] > 0, "main で成功した実行がまだない"
    run = runs["workflow_runs"][0]
    usage = gh("api", f"repos/{REPO}/actions/runs/{run['id']}/timing")
    minutes = usage["run_duration_ms"] / 60000
    assert minutes < 10, f"{minutes:.1f} 分"
