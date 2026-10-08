"""GroqModel with mocked HTTP (httpx.MockTransport). No network, no real key."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from guard.model import GroqModel, MockModel, OllamaModel, cache_path, model_from_spec

REF = datetime(2026, 10, 7, 20, 40, tzinfo=timezone(timedelta(hours=5, minutes=30)))
FAKE_KEY = "test-key-not-real-123"
GOOD = {"intent": "book", "patient_name": "Ravi", "date": "2026-10-08", "time": "16:00",
        "date_words": "kal", "time_words": "4 baje", "red_flag": False}


def chat_reply(content: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def model_with(handler, **kw) -> tuple[GroqModel, list]:
    sleeps: list = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return GroqModel("qwen/qwen3-32b", api_key=FAKE_KEY, client=client, sleep=sleeps.append, **kw), sleeps


def test_no_key_is_an_error_not_a_crash():
    called = []
    m = GroqModel("qwen/qwen3-32b", api_key="", client=httpx.Client(transport=httpx.MockTransport(lambda r: called.append(r))))
    res = m.extract("kal 4 baje, naam Ravi", REF)
    assert res.error == "call_error: GROQ_API_KEY is not set" and res.extraction is None and called == []


def test_success_parses_and_sends_the_right_request():
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["auth"] = req.headers["authorization"]
        seen["body"] = json.loads(req.content)
        seen["url"] = str(req.url)
        return httpx.Response(200, json=chat_reply(json.dumps(GOOD)))

    m, _ = model_with(handler)
    res = m.extract("kal shaam 4 baje, naam Ravi", REF)
    assert res.error is None and res.extraction.patient_name == "Ravi" and res.model == "groq:qwen/qwen3-32b"
    assert seen["url"].endswith("/chat/completions") and seen["auth"] == f"Bearer {FAKE_KEY}"
    assert seen["body"]["model"] == "qwen/qwen3-32b" and seen["body"]["response_format"] == {"type": "json_object"}
    assert seen["body"]["temperature"] == 0 and seen["body"]["reasoning_effort"] == "none"
    assert FAKE_KEY not in res.model_dump_json()


def test_think_block_is_stripped():
    m, _ = model_with(lambda r: httpx.Response(200, json=chat_reply("<think>hmm</think>\n" + json.dumps(GOOD))))
    assert m.extract("x", REF).extraction.time == "16:00"


def test_rate_limit_then_success_waits_retry_after():
    calls = []

    def handler(req):
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(429, headers={"retry-after": "1.5"}, json={"error": {"message": "rate limit"}})
        return httpx.Response(200, json=chat_reply(json.dumps(GOOD)))

    m, sleeps = model_with(handler)
    res = m.extract("x", REF)
    assert res.error is None and len(calls) == 3 and sleeps == [1.5, 1.5]


def test_rate_limit_every_time_gives_a_clean_error():
    m, sleeps = model_with(lambda r: httpx.Response(429, json={"error": {"message": "rate limit"}}), max_retries=3)
    res = m.extract("x", REF)
    assert res.error == "call_error: rate_limited" and sleeps == [2.0, 4.0, 8.0]


def test_backoff_is_capped():
    m, sleeps = model_with(lambda r: httpx.Response(429, headers={"retry-after": "500"}), max_retries=1, max_wait_s=10)
    m.extract("x", REF)
    assert sleeps == [10]


def test_server_error_is_retried():
    calls = []

    def handler(req):
        calls.append(1)
        return httpx.Response(503) if len(calls) == 1 else httpx.Response(200, json=chat_reply(json.dumps(GOOD)))

    m, sleeps = model_with(handler)
    assert m.extract("x", REF).error is None and sleeps == [2.0]


def test_auth_error_does_not_leak_the_key():
    m, _ = model_with(lambda r: httpx.Response(401, json={"error": {"message": "invalid api key"}}))
    res = m.extract("x", REF)
    assert res.error.startswith("call_error: HTTPStatusError") and FAKE_KEY not in res.error


def test_bad_json_is_a_schema_error_not_a_crash():
    m, _ = model_with(lambda r: httpx.Response(200, json=chat_reply("not json")))
    res = m.extract("x", REF)
    assert res.extraction is None and res.error.startswith("json_error")


def test_list_models():
    m, _ = model_with(lambda r: httpx.Response(200, json={"data": [{"id": "b-model"}, {"id": "a-model"}]}))
    assert m.list_models() == ["a-model", "b-model"]


def test_model_from_spec_and_cache_path():
    assert isinstance(model_from_spec("mock"), MockModel)
    assert isinstance(model_from_spec("qwen3:4b"), OllamaModel) and model_from_spec("qwen3:4b").name == "ollama:qwen3:4b"
    assert isinstance(model_from_spec("ollama:qwen3:4b"), OllamaModel)
    g = model_from_spec("groq:qwen/qwen3-32b")
    assert isinstance(g, GroqModel) and g.model == "qwen/qwen3-32b"
    assert cache_path(Path("R"), "qwen3:4b") == Path("R/eval/cache/qwen3_4b.jsonl")
    assert cache_path(Path("R"), "qwen2.5-coder:7b") == Path("R/eval/cache/qwen2.5-coder_7b.jsonl")
    assert cache_path(Path("R"), "groq:qwen/qwen3-32b") == Path("R/eval/cache/groq_qwen_qwen3-32b.jsonl")
