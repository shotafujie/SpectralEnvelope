import functools

import pytest
from fastapi.testclient import TestClient

from jig import server
from tests import audio_fixtures as af


@pytest.fixture
def client():
    return TestClient(server.create_app())


@functools.cache
def vowel_wav(name="a", dur=3.0, silence=False):
    x = af.vowel(name, dur)
    if silence:
        x = af.with_silence(x)
    return af.wav_bytes(x)


@pytest.fixture
def analyze(client):
    def _analyze(data=None, filename="a.wav", content_type="audio/wav"):
        data = vowel_wav() if data is None else data
        return client.post("/api/analyze", files={"audio": (filename, data, content_type)})

    return _analyze


@pytest.fixture
def synth_spy(monkeypatch):
    """pyworld.synthesize に渡った f0 / sp / ap を記録し、本物に委譲する。"""
    calls = []
    real = server.pyworld.synthesize

    def spy(f0, sp, ap, fs, frame_period=5.0):
        calls.append({"f0": f0.copy(), "sp": sp.copy(), "ap": ap.copy()})
        return real(f0, sp, ap, fs, frame_period)

    monkeypatch.setattr(server.pyworld, "synthesize", spy)
    return calls
