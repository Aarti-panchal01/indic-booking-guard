"""The demo page and /api/check: examples, input limits, rate limit, notices. MockModel only, no network."""
import re
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

import api
from api import MAX_CHARS, NOTICE, RateLimiter, create_app
from guard.model import MockModel
from guard.schema import Extraction, ModelResult


def client(limiter=None, model=None) -> TestClient:
    return TestClient(create_app(model=model or MockModel(fn=lambda u, r: Extraction(intent="book")), limiter=limiter))


def examples() -> list[str]:
    html = open(api.ROOT / "web" / "index.html", encoding="utf-8").read()
    return re.findall(r'data-u="([^"]+)"', html)


def test_page_has_notice_limitation_and_four_examples():
    c = client()
    html = c.get("/").text
    assert NOTICE in html and "15 of 22" in html
    assert len(examples()) == 4


def test_every_example_gives_a_card(monkeypatch):
    # fixed "now" on a Wednesday evening so the slots are deterministic
    fixed = datetime(2026, 10, 7, 20, 40, tzinfo=timezone(timedelta(hours=5, minutes=30)))

    class FixedDT(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(api, "datetime", FixedDT)
    c = client()
    labels = []
    for u in examples():
        r = c.post("/api/check", json={"utterance": u})
        assert r.status_code == 200, u
        d = r.json()
        assert d["notice"] == NOTICE and d["card"]["checks"]
        labels.append((d["card"]["action"], d["card"]["tier"], d["card"]["reason"], d["card"]["time"]))
    hinglish, kannada, emergency, stacked = labels
    assert hinglish[0] == "book" and hinglish[3] == "17:15"
    assert kannada[0] == "book" and kannada[3] == "10:30"
    assert emergency[:2] == ("escalate", "urgent")
    assert stacked[0] == "ask_again" and stacked[2] == "ambiguous_date"


def test_input_limits():
    c = client()
    assert c.post("/api/check", json={"utterance": "x" * MAX_CHARS}).status_code == 200
    r = c.post("/api/check", json={"utterance": "x" * (MAX_CHARS + 1)})
    assert r.status_code == 400 and "300" in r.json()["error"] and r.json()["notice"] == NOTICE
    assert c.post("/api/check", json={"utterance": "   "}).status_code == 400
    assert c.post("/book", json={"utterance": "y" * (MAX_CHARS + 1)}).status_code == 400


def test_junk_input_is_handled():
    c = client()
    for junk in ["asdf qwer zxcv", "<script>alert(1)</script>", "1234567890", "!!!???"]:
        r = c.post("/api/check", json={"utterance": junk})
        assert r.status_code == 200 and r.json()["card"]["action"] != "book", junk


def test_rate_limit_per_ip():
    t = [1000.0]
    c = client(limiter=RateLimiter(per_minute=2, per_day=3, clock=lambda: t[0]))
    h = {"x-forwarded-for": "203.0.113.5"}
    assert c.post("/api/check", json={"utterance": "kal 5 baje"}, headers=h).status_code == 200
    assert c.post("/api/check", json={"utterance": "kal 5 baje"}, headers=h).status_code == 200
    r = c.post("/api/check", json={"utterance": "kal 5 baje"}, headers=h)
    assert r.status_code == 429 and "minute" in r.json()["error"]
    assert c.post("/api/check", json={"utterance": "kal 5 baje"}, headers={"x-forwarded-for": "198.51.100.7"}).status_code == 200
    t[0] += 120
    assert c.post("/api/check", json={"utterance": "kal 5 baje"}, headers=h).status_code == 200
    t[0] += 120
    assert "today" in c.post("/api/check", json={"utterance": "kal 5 baje"}, headers=h).json()["error"]


def test_model_rate_limit_is_a_friendly_note_and_the_guard_still_runs():
    class Busy:
        name = "groq:test"

        def extract(self, u, r):
            return ModelResult(model=self.name, error="call_error: rate_limited")

    d = client(model=Busy()).post("/api/check", json={"utterance": "seene mein dard ho raha hai"}).json()
    assert "free-tier limit" in d["card"]["model_note"] and d["card"]["action"] == "escalate"


def test_bookings_are_labelled_non_persistent():
    d = client().get("/bookings").json()
    assert "non-persistent" in d["register"] and d["notice"] == NOTICE
