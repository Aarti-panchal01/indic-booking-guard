"""golden.jsonl: label checker passes and every case is schema-valid."""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"
GOLDEN = DATA / "golden.jsonl"

ACTIONS = {"book", "ask_again", "escalate", "handoff", "write_failed"}
REASONS = {"missing_name", "missing_date", "missing_time", "ambiguous_date", "ambiguous_time",
           "weekday_mismatch", "past_time", "outside_hours", "closed_day", "slot_taken",
           "too_far", "unintelligible"}
LANGS = {"hinglish", "kannada_english", "english", "devanagari_hindi", "mixed_other"}


def cases():
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_check_labels_reports_zero_violations():
    r = subprocess.run([sys.executable, "-I", str(DATA / "check_labels.py"), str(GOLDEN)],
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-500:]
    assert "violations: 0" in r.stdout


def test_golden_size_and_unique_ids():
    cs = cases()
    assert len(cs) >= 50
    ids = [c["id"] for c in cs]
    assert len(set(ids)) == len(ids)


@pytest.mark.parametrize("case", cases(), ids=lambda c: c["id"])
def test_case_schema(case):
    assert set(case) == {"id", "utterance", "lang_mix", "reference_datetime", "category",
                         "tool_failure", "expected", "notes", "provenance"}
    assert case["lang_mix"] in LANGS
    assert isinstance(case["utterance"], str) and case["utterance"].strip()
    assert isinstance(case["tool_failure"], bool)
    assert datetime.fromisoformat(case["reference_datetime"]).tzinfo is not None
    exp = case["expected"]
    assert set(exp) == {"action", "name", "date", "time", "reason"}
    assert exp["action"] in ACTIONS
    if exp["date"] is not None:
        datetime.strptime(exp["date"], "%Y-%m-%d")
    if exp["time"] is not None:
        datetime.strptime(exp["time"], "%H:%M")
    if exp["action"] == "ask_again":
        assert exp["reason"] in REASONS
    else:
        assert exp["reason"] is None
    if exp["action"] in ("book", "write_failed"):
        assert exp["date"] and exp["time"]
    if exp["action"] in ("escalate", "handoff"):
        assert exp["name"] is None and exp["date"] is None and exp["time"] is None
    if exp["action"] == "write_failed":
        assert case["tool_failure"] is True
