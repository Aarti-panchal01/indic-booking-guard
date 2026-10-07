"""The two comparison systems. Both use the same register tool as the guard.

- `raw_model_system`: trust the model's date and time (what a naive tool-calling agent does).
- `dateparser_system`: the community fix from the LiveKit thread: take the caller's words
  verbatim (here: the model's date_words/time_words) and resolve them with dateparser.
"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

import dateparser

from .register import Register, RegisterWriteError
from .schema import Decision, ModelResult


def _parse_date(s: Optional[str]) -> Optional[date]:
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def _parse_time(s: Optional[str]) -> Optional[time]:
    try:
        return time.fromisoformat(s) if s else None
    except ValueError:
        return None


def _book_with_tool(d: date, t: time, name: str, register: Register, trace: list[str]) -> Decision:
    """Shared booking tool: rejects closed/outside/taken slots, then writes."""
    problem = register.slot_problem(d, t)
    if problem:
        trace.append(f"tool rejected: {problem}")
        return Decision(action="ask_again", reason=problem, name=name, date=d.isoformat(),
                        time=t.strftime("%H:%M"), trace=trace)
    try:
        register.book(d, t, name)
    except RegisterWriteError as e:
        trace.append(f"tool error: {e}")
        return Decision(action="write_failed", name=name, date=d.isoformat(), time=t.strftime("%H:%M"), trace=trace)
    return Decision(action="book", name=name, date=d.isoformat(), time=t.strftime("%H:%M"), confirmed=True, trace=trace)


def _common_front(mr: ModelResult, trace: list[str]) -> Optional[Decision]:
    if mr.extraction is None:
        trace.append(f"model output unusable: {mr.error}")
        return Decision(action="ask_again", reason="unintelligible", trace=trace)
    ex = mr.extraction
    if ex.red_flag:
        return Decision(action="escalate", trace=trace + ["model red_flag"])
    if ex.intent != "book":
        return Decision(action="handoff", trace=trace + [f"model intent {ex.intent}"])
    return None


def raw_model_system(utterance: str, reference: datetime, mr: ModelResult, register: Register) -> Decision:
    trace: list[str] = ["raw model"]
    early = _common_front(mr, trace)
    if early:
        return early
    ex = mr.extraction
    d, t = _parse_date(ex.date), _parse_time(ex.time)
    if d is None:
        return Decision(action="ask_again", reason="missing_date", trace=trace)
    if t is None:
        return Decision(action="ask_again", reason="missing_time", date=d.isoformat(), trace=trace)
    if not ex.patient_name:
        return Decision(action="ask_again", reason="missing_name", date=d.isoformat(), time=t.strftime("%H:%M"), trace=trace)
    return _book_with_tool(d, t, ex.patient_name, register, trace)


def dateparse_words(words: str, reference: datetime) -> Optional[datetime]:
    return dateparser.parse(
        words,
        settings={
            "RELATIVE_BASE": reference.replace(tzinfo=None),
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False,
        },
    )


def dateparser_system(utterance: str, reference: datetime, mr: ModelResult, register: Register) -> Decision:
    trace: list[str] = ["dateparser on model's verbatim words"]
    early = _common_front(mr, trace)
    if early:
        return early
    ex = mr.extraction
    d: Optional[date] = None
    t: Optional[time] = None
    if ex.date_words or ex.time_words:
        both = dateparse_words(" ".join(w for w in (ex.date_words, ex.time_words) if w), reference)
        if both is not None:
            d = both.date() if ex.date_words else None
            t = both.time().replace(second=0, microsecond=0) if ex.time_words else None
    if d is None and ex.date_words:
        p = dateparse_words(ex.date_words, reference)
        d = p.date() if p else None
    if t is None and ex.time_words:
        p = dateparse_words(ex.time_words, reference)
        t = p.time().replace(second=0, microsecond=0) if p else None
    trace.append(f"dateparser -> {d} {t}")
    if d is None:
        return Decision(action="ask_again", reason="missing_date", trace=trace)
    if t is None:
        return Decision(action="ask_again", reason="missing_time", date=d.isoformat(), trace=trace)
    if not ex.patient_name:
        return Decision(action="ask_again", reason="missing_name", date=d.isoformat(), time=t.strftime("%H:%M"), trace=trace)
    return _book_with_tool(d, t, ex.patient_name, register, trace)
