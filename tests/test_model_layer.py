"""Model layer: parse_extraction, CachedModel, MockModel. No network, no Ollama."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from guard.model import CachedModel, MockModel, parse_extraction
from guard.schema import Extraction, ModelResult

REF = datetime(2026, 10, 7, 20, 40, tzinfo=timezone(timedelta(hours=5, minutes=30)))


class CountingModel:
    name = "counting"

    def __init__(self, error=None):
        self.calls = 0
        self.error = error

    def extract(self, utterance, reference):
        self.calls += 1
        if self.error:
            return ModelResult(model=self.name, error=self.error)
        return ModelResult(model=self.name, extraction=Extraction(intent="book", patient_name="Ravi"), raw="{}")


# ---- parse_extraction never raises
def test_parse_good_json():
    ex, err = parse_extraction('{"intent": "book", "patient_name": "Ravi", "date": "2026-10-08", "time": "16:00"}')
    assert err is None and ex.patient_name == "Ravi" and ex.red_flag is False


@pytest.mark.parametrize("raw", ["", "not json", "{", "{'intent': 'book'}", "nan"])
def test_parse_bad_json(raw):
    ex, err = parse_extraction(raw)
    assert ex is None and err.startswith("json_error")


@pytest.mark.parametrize("raw", ["[]", "3", '"book"', "null"])
def test_parse_non_object(raw):
    ex, err = parse_extraction(raw)
    assert ex is None and err.startswith("json_error")


@pytest.mark.parametrize("raw", [
    '{"intent": "dance"}',            # not in the enum
    '{"patient_name": "Ravi"}',       # intent missing
    '{"intent": "book", "red_flag": "maybe"}',
    '{"intent": "book", "date": 5}',
])
def test_parse_wrong_schema(raw):
    ex, err = parse_extraction(raw)
    assert ex is None and err.startswith("schema_error")


# ---- CachedModel
def test_cache_round_trip_second_call_hits_cache(tmp_path):
    inner = CountingModel()
    path = tmp_path / "sub" / "cache.jsonl"
    m = CachedModel(inner, path)
    first = m.extract("kal 4 baje", REF)
    second = m.extract("kal 4 baje", REF)
    assert inner.calls == 1
    assert first.extraction == second.extraction
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1


def test_cache_persists_across_instances(tmp_path):
    path = tmp_path / "cache.jsonl"
    CachedModel(CountingModel(), path).extract("kal 4 baje", REF)
    inner = CountingModel()
    res = CachedModel(inner, path).extract("kal 4 baje", REF)
    assert inner.calls == 0
    assert res.extraction.patient_name == "Ravi"


def test_cache_key_depends_on_utterance_and_reference(tmp_path):
    inner = CountingModel()
    m = CachedModel(inner, tmp_path / "c.jsonl")
    m.extract("a", REF)
    m.extract("b", REF)
    m.extract("a", REF + timedelta(days=1))
    assert inner.calls == 3


def test_offline_miss_returns_error_result_not_raise(tmp_path):
    inner = CountingModel()
    m = CachedModel(inner, tmp_path / "c.jsonl", offline=True)
    res = m.extract("never seen", REF)
    assert res.error == "cache_miss_offline"
    assert res.extraction is None
    assert inner.calls == 0


def test_offline_hit_after_online_fill(tmp_path):
    path = tmp_path / "c.jsonl"
    CachedModel(CountingModel(), path).extract("x", REF)
    res = CachedModel(CountingModel(), path, offline=True).extract("x", REF)
    assert res.error is None and res.extraction is not None


def test_transport_errors_are_not_cached(tmp_path):
    inner = CountingModel(error="call_error: boom")
    path = tmp_path / "c.jsonl"
    m = CachedModel(inner, path)
    m.extract("x", REF)
    m.extract("x", REF)
    assert inner.calls == 2
    assert not path.exists() or path.read_text(encoding="utf-8").strip() == ""


def test_parse_errors_are_cached(tmp_path):
    inner = CountingModel(error="json_error: bad")
    m = CachedModel(inner, tmp_path / "c.jsonl")
    m.extract("x", REF)
    m.extract("x", REF)
    assert inner.calls == 1


def test_cache_file_is_valid_jsonl(tmp_path):
    path = tmp_path / "c.jsonl"
    CachedModel(CountingModel(), path).extract("kal शाम 4 baje", REF)
    row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert {"key", "utterance", "reference", "prompt_version", "result"} <= set(row)


# ---- MockModel
def test_mock_is_flagged_mock():
    res = MockModel().extract("anything", REF)
    assert res.mock is True
    assert MockModel().name == "MOCK"


def test_mock_default_is_book_intent_only():
    ex = MockModel().extract("anything", REF).extraction
    assert ex == Extraction(intent="book")


def test_mock_returns_configured_response_and_fn():
    canned = Extraction(intent="cancel")
    m = MockModel(responses={"hi": canned}, fn=lambda u, r: Extraction(intent="question"))
    assert m.extract("hi", REF).extraction == canned
    assert m.extract("other", REF).extraction.intent == "question"
    assert json.loads(m.extract("hi", REF).raw)["intent"] == "cancel"
