"""HTTP wrapper and the live demo.

Routes:
  GET  /            the demo page (web/index.html)
  POST /api/check   one caller sentence -> decision card (used by the page)
  POST /book        one caller sentence -> raw guard decision (API)
  GET  /bookings    the demo register

Run locally (from the repo root):  uvicorn api:app --port 8000
Model: GUARD_MODEL env var. Default: groq:qwen/qwen3.8-27b if GROQ_API_KEY is set, else qwen3:4b via Ollama.
GUARD_MODEL=mock uses the labelled MockModel (intent=book, nothing else), so the deterministic layer runs alone.

The register is SQLite: in memory locally, /tmp on Vercel, deleted at start, so it resets on every cold start.
It is a non-persistent demo register seeded with the synthetic clinic in data/clinic.json.
"""
from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from guard.guard import Guard
from guard.model import model_from_spec
from guard.register import Register
from guard.schema import Decision

IST = timezone(timedelta(hours=5, minutes=30))
ROOT = Path(__file__).resolve().parent
MAX_CHARS = 300
NOTICE = ("Demo with synthetic data only. Do not enter real patient information. Not a medical device. "
          "In an emergency call 108.")
LIMITATION = ("Emergency detection caught 15 of 22 on the latest blind test and misses some phrasings.")
DEFAULT_GROQ_MODEL = "groq:qwen/qwen3.8-27b"


class BookRequest(BaseModel):
    utterance: str
    reference_datetime: Optional[datetime] = None  # when the call happens; default: now (IST)


class BookResponse(BaseModel):
    decision: Decision
    model: str
    model_error: Optional[str] = None
    mock: bool
    notice: str = NOTICE
    limitation: str = LIMITATION


def default_model_spec() -> str:
    if os.environ.get("GUARD_MODEL"):
        return os.environ["GUARD_MODEL"]
    return DEFAULT_GROQ_MODEL if os.environ.get("GROQ_API_KEY") else "qwen3:4b"


def demo_register() -> Register:
    path = os.environ.get("GUARD_DB") or ("/tmp/indic_guard_demo.sqlite" if os.environ.get("VERCEL") else ":memory:")
    if path != ":memory:":
        try:
            os.remove(path)  # reset on every cold start: a non-persistent demo register
        except FileNotFoundError:
            pass
    return Register(db_path=path)


class RateLimiter:
    """Per-IP sliding windows plus a per-instance daily cap, to protect the free Groq quota.
    In memory, so per server instance: best effort, not a security boundary."""

    def __init__(self, per_minute: int = 6, per_day: int = 60, instance_per_day: int = 600, clock=time.time):
        self.per_minute, self.per_day, self.instance_per_day = per_minute, per_day, instance_per_day
        self.clock = clock
        self.hits: dict[str, deque] = defaultdict(deque)
        self.all: deque = deque()
        self.lock = threading.Lock()

    def allow(self, ip: str) -> Optional[str]:
        now = self.clock()
        with self.lock:
            q = self.hits[ip]
            while q and now - q[0] > 86400:
                q.popleft()
            while self.all and now - self.all[0] > 86400:
                self.all.popleft()
            if len(self.all) >= self.instance_per_day:
                return "The demo has used today's free model quota. Please try again tomorrow."
            if len(q) >= self.per_day:
                return "You have reached today's limit for this demo. Please try again tomorrow."
            if sum(1 for t in q if now - t < 60) >= self.per_minute:
                return "Too many tries in a minute. Please wait a few seconds and try again."
            q.append(now)
            self.all.append(now)
        return None


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")


KIND = {"book": "Booked", "ask_again": "Ask again", "handoff": "Handoff to staff", "write_failed": "Not saved"}


def card(dec: Decision, model_error: Optional[str]) -> dict:
    """What the page shows: a label, the resolved slot, and which checks passed or failed and why."""
    if dec.action == "escalate":
        label = "Urgent escalation: call 108" if dec.tier != "human_check" else "Human check: staff call back now"
    else:
        label = KIND.get(dec.action, dec.action)
        if dec.action == "ask_again" and dec.reason:
            label += f" ({dec.reason.replace('_', ' ')})"
    checks = []
    for t in dec.trace:
        failed = any(w in t for w in ("failed", "red flag", "human check", "not in transcript", "ignored", "unrecognised",
                                      "stacked", "ambiguous", "model red_flag", "unusable", "NOT confirming"))
        checks.append({"text": t, "status": "fail" if failed else "ok"})
    why = {
        "book": "Every day and time word was understood, the slot is open and free, and the register write succeeded.",
        "ask_again": "The guard will not book until the caller clears this up.",
        "escalate": "A red-flag sign was found, so booking stops and a person takes over." if dec.tier != "human_check"
        else "A body complaint that started today, with no known sign word, so staff call back before any booking.",
        "handoff": "Not a new booking (cancel, reschedule, fees or advice), so it goes to the staff list.",
        "write_failed": "The register write failed, so the caller is told it is NOT confirmed.",
    }.get(dec.action, "")
    out = {"label": label, "action": dec.action, "tier": dec.tier, "reason": dec.reason, "date": dec.date,
           "time": dec.time, "name": dec.name, "confirmed": dec.confirmed, "say": dec.say, "why": why, "checks": checks}
    if model_error:
        out["model_note"] = ("The language model was busy (free-tier limit), so the guard ran on your words alone."
                             if "rate_limited" in model_error else "The language model did not answer, so the guard ran on your words alone.")
    return out


class CheckRequest(BaseModel):
    utterance: str


def create_app(model=None, register: Optional[Register] = None, limiter: Optional[RateLimiter] = None) -> FastAPI:
    app = FastAPI(title="Indic booking guard (demo)")
    app.state.model = model or model_from_spec(default_model_spec())
    app.state.register = register or demo_register()
    app.state.limiter = limiter or RateLimiter()
    lock = threading.Lock()  # one guard decision (check + write) at a time on the shared register

    def decide(utterance: str, ref: datetime):
        mr = app.state.model.extract(utterance, ref)
        with lock:
            dec = Guard(app.state.register).decide(utterance, ref, mr)
        return dec, mr

    def too_long(u: str) -> Optional[JSONResponse]:
        if not u.strip():
            return JSONResponse({"error": "Type what the caller said.", "notice": NOTICE}, status_code=400)
        if len(u) > MAX_CHARS:
            return JSONResponse({"error": f"Please keep it under {MAX_CHARS} characters (yours is {len(u)}).", "notice": NOTICE},
                                status_code=400)
        return None

    @app.get("/", response_class=HTMLResponse)
    def page() -> HTMLResponse:
        return HTMLResponse((ROOT / "web" / "index.html").read_text(encoding="utf-8"))

    @app.post("/api/check")
    def check(req: CheckRequest, request: Request):
        bad = too_long(req.utterance)
        if bad:
            return bad
        msg = app.state.limiter.allow(client_ip(request))
        if msg:
            return JSONResponse({"error": msg, "notice": NOTICE}, status_code=429)
        ref = datetime.now(IST)
        dec, mr = decide(req.utterance, ref)
        return {"card": card(dec, mr.error), "reference": ref.strftime("%A %d %B %Y, %H:%M IST"), "model": mr.model,
                "notice": NOTICE, "limitation": LIMITATION}

    @app.post("/book", response_model=BookResponse)
    def book(req: BookRequest, request: Request):
        bad = too_long(req.utterance)
        if bad:
            return bad
        msg = app.state.limiter.allow(client_ip(request))
        if msg:
            return JSONResponse({"error": msg, "notice": NOTICE}, status_code=429)
        dec, mr = decide(req.utterance, req.reference_datetime or datetime.now(IST))
        return BookResponse(decision=dec, model=mr.model, model_error=mr.error, mock=mr.mock)

    @app.get("/bookings")
    def bookings() -> dict:
        with lock:
            rows = app.state.register.bookings()
        return {"notice": NOTICE, "register": "non-persistent demo register, reset on every cold start",
                "bookings": [{"slot": s, "name": n, "source": src} for s, n, src in rows]}

    return app


app = create_app()
