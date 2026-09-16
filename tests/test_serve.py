"""SPEC-122: 起動エントリポイントの待ち受けアドレス。"""

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_ready(port, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError("server did not start")


def test_TC_122_1_127_0_0_1だけで待ち受ける():
    port = free_port()
    proc = subprocess.Popen([sys.executable, "jig/server.py", "--port", str(port)], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_ready(port)
        out = subprocess.run(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-a", "-p", str(proc.pid)],
                             capture_output=True, text=True).stdout
        addrs = {line.split()[8] for line in out.splitlines()[1:]}
        assert addrs == {f"127.0.0.1:{port}"}
    finally:
        proc.terminate()
        proc.wait(timeout=10)
