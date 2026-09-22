"""ワークフローの形（009-pages-deploy）。実行結果ではなく、YAML の構造を確かめる。"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".github/workflows/ci.yml"

VERIFY_JOB = "verify-wasm"
TEST_JOB = "test-js"
DEPLOY_JOB = "deploy"


@pytest.fixture(scope="module")
def wf():
    # YAML の on: は真偽値の True として読まれるので、キーを文字列に寄せておく
    data = yaml.safe_load(PATH.read_text())
    if True in data:
        data["on"] = data.pop(True)
    return data


@pytest.fixture(scope="module")
def raw():
    return PATH.read_text()


def steps_of(wf, job):
    return wf["jobs"][job]["steps"]


def test_TC_1110_1_pushとpull_requestで起動する(wf):
    assert set(wf["on"]) >= {"push", "pull_request"}


def test_TC_1111_1_照合ジョブはarm64ランナー(wf):
    assert wf["jobs"][VERIFY_JOB]["runs-on"] == "ubuntu-24.04-arm"


def test_TC_1100_1_ワークフローが照合スクリプトを呼ぶ(raw):
    assert "tools/verify_wasm.sh" in raw


def test_TC_1112_1_テストジョブがNodeテストを実行する(wf):
    assert any("npm run test:js" in (s.get("run") or "") for s in steps_of(wf, TEST_JOB))


def test_TC_1112_2_Nodeテストは失敗すると0以外で終わる(tmp_path):
    import subprocess

    bad = ROOT / "tests/js/zz-temporary-failing.test.mjs"
    bad.write_text('import { test } from "node:test";\n'
                   'import assert from "node:assert/strict";\n'
                   'test("わざと落とす", () => assert.equal(1, 2));\n')
    try:
        r = subprocess.run(["npm", "run", "test:js"], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode != 0
    finally:
        bad.unlink()


def test_TC_1113_1_外部actionはSHAで固定されている(raw):
    uses = re.findall(r"uses:\s*(\S+)", raw)
    assert uses
    for u in uses:
        assert re.search(r"@[0-9a-f]{40}$", u), u


def test_TC_1114_1_pull_request_targetを使わない(raw):
    assert "pull_request_target" not in raw


def test_TC_1115_1_既定の権限はcontents_readだけ(wf):
    assert wf["permissions"] == {"contents": "read"}


def test_TC_1120_1_デプロイはmainへのpushのときだけ(wf):
    cond = wf["jobs"][DEPLOY_JOB]["if"]
    assert "refs/heads/main" in cond
    assert "push" in cond


def test_TC_1121_1_デプロイは照合とテストの成功が条件(wf):
    assert set(wf["jobs"][DEPLOY_JOB]["needs"]) == {VERIFY_JOB, TEST_JOB}


def test_TC_1122_1_書き込み権限はデプロイジョブだけ(wf):
    for name, job in wf["jobs"].items():
        perms = job.get("permissions", {})
        writable = {k for k, v in perms.items() if v == "write"}
        if name == DEPLOY_JOB:
            assert writable == {"pages", "id-token"}, perms
        else:
            assert writable == set(), (name, perms)


def test_TC_1123_1_ワークフローが組み立てスクリプトを呼ぶ(raw):
    assert "tools/build_site.py" in raw
