"""Pydantic types shared by the model layer, the guard and the eval.

The model (probabilistic) fills `Extraction`. The guard (deterministic) turns
an utterance + an Extraction into a `Decision`. Nothing in this file calls a model.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Intent = Literal["book", "cancel", "reschedule", "question", "other"]
Action = Literal["book", "ask_again", "escalate", "handoff", "write_failed"]
Reason = Literal[
    "unintelligible",
    "missing_date",
    "ambiguous_date",
    "weekday_mismatch",
    "past_time",
    "too_far",
    "closed_day",
    "missing_time",
    "ambiguous_time",
    "outside_hours",
    "slot_taken",
    "missing_name",
]

# Priority order from TAXONOMY.md section 2: when several reasons apply, the first wins.
REASON_PRIORITY: list[str] = list(Reason.__args__)  # type: ignore[attr-defined]


class Extraction(BaseModel):
    """What the LLM is asked to return for one caller utterance."""

    intent: Intent = Field(description="book = new appointment; cancel/reschedule/question/other otherwise")
    patient_name: Optional[str] = Field(default=None, description="patient's name as said, no titles")
    date: Optional[str] = Field(default=None, description="appointment date YYYY-MM-DD, resolved against the reference date")
    time: Optional[str] = Field(default=None, description="appointment time HH:MM 24h")
    date_words: Optional[str] = Field(default=None, description="the caller's exact words for the day, verbatim")
    time_words: Optional[str] = Field(default=None, description="the caller's exact words for the time, verbatim")
    red_flag: bool = Field(default=False, description="true if the caller reports an emergency symptom (chest pain, breathlessness, stroke signs)")


class ModelResult(BaseModel):
    """One model call, kept whole so the eval can be regenerated from the cache."""

    model: str
    extraction: Optional[Extraction] = None
    raw: str = ""
    latency_s: float = 0.0
    error: Optional[str] = None
    mock: bool = False


class Decision(BaseModel):
    """What the system does with one call."""

    action: Action
    reason: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    confirmed: bool = False  # True only if the agent told the caller "confirmed"
    say: str = ""            # what the agent says back (for the README examples)
    trace: list[str] = Field(default_factory=list)  # which deterministic checks fired
