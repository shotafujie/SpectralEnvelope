"""SPEC-120/121 の応答時間。ウォームアップ 1 回の後、3 回の中央値を見る。"""

import statistics
import time

from tests.conftest import vowel_wav


def median_seconds(fn, runs=3):
    fn()
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def test_TC_120_1_3秒wavの分解は1秒未満(analyze):
    data = vowel_wav()
    t = median_seconds(lambda: analyze(data).raise_for_status())
    print(f"analyze median {t:.3f}s")
    assert t < 1.0


def test_TC_121_1_3秒音声の合成は0_3秒未満(client, analyze):
    id_ = analyze().json()["id"]
    body = {"id": id_, "params": {"formant": 1.2, "tilt": 3, "bands": [2, -2, 4, -4], "smooth": 30, "pitch": 1.3}}
    t = median_seconds(lambda: client.post("/api/synthesize", json=body).raise_for_status())
    print(f"synthesize median {t:.3f}s")
    assert t < 0.3
