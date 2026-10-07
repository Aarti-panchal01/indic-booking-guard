"""Thin HTTP wrapper: POST /book runs one caller utterance through model + guard.

Run (from build/):  uvicorn api:app --port 8000
Model: GUARD_MODEL env var (default qwen3:4b via Ollama at OLLAMA_URL). GUARD_MODEL=mock uses the
labelled MockModel (intent=book, nothing else), so the deterministic layer runs alone.

One register per process (SQLite, in memory unless GUARD_DB is set), so a slot booked by one
request is taken for the next. No auth: local demo only, never deploy as is.
"""
from __future__ import annotations

import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from guard.guard import Guard
from guard.model import MockModel, OllamaModel
from guard.register import Register
from guard.schema import Decision

IST = timezone(timedelta(hours=5, minutes=30))


class BookRequest(BaseModel):
    utterance: str
    reference_datetime: Optional[datetime] = None  # when the call happens; default: now (IST)


class BookResponse(BaseModel):
    decision: Decision
    model: str
    model_error: Optional[str] = None
    mock: bool


def make_model(name: str):
    return MockModel() if name == "mock" else OllamaModel(name, base_url=os.environ.get("OLLAMA_URL"))


def create_app(model=None, register: Optional[Register] = None) -> FastAPI:
    app = FastAPI(title="Indic booking guard")
    app.state.model = model or make_model(os.environ.get("GUARD_MODEL", "qwen3:4b"))
    app.state.register = register or Register(db_path=os.environ.get("GUARD_DB", ":memory:"))
    lock = threading.Lock()  # one guard decision (check + write) at a time on the shared register

    @app.post("/book", response_model=BookResponse)
    def book(req: BookRequest) -> BookResponse:
        ref = req.reference_datetime or datetime.now(IST)
        mr = app.state.model.extract(req.utterance, ref)
        with lock:
            dec = Guard(app.state.register).decide(req.utterance, ref, mr)
        return BookResponse(decision=dec, model=mr.model, model_error=mr.error, mock=mr.mock)

    @app.get("/bookings")
    def bookings() -> list[dict]:
        with lock:
            rows = app.state.register.bookings()
        return [{"slot": s, "name": n, "source": src} for s, n, src in rows]

    return app


app = create_app()
