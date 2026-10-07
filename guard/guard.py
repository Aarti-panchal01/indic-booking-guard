"""The guard: deterministic checks between the model's extraction and the register write.

Probabilistic part (input): ModelResult from any ExtractionModel. Used for intent,
the patient's name, and (as a fallback for English only) the verbatim date/time words.
Deterministic part (this file): red flags, date/time resolution from the caller's own
words, weekday-vs-date check, past/far/closed/hours/taken checks, the write, and the
confirmation gate. The model's own date and time are never used for the booking.
"""
from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Optional

from .baselines import dateparse_words
from .normalise import (DAYPARTS, FRAC_POST, FRAC_PRE, FRAC_WHOLE, HEDGES, NUM_WORDS, RELATIVE, TIME_UNITS, WEEKDAY_OF,
                        WINDOW, DayExpr, Parse, parse, resolve_day, resolve_time, tokenize, unknown_near, weekday_conflict)
from .redflags import red_flag_hits
from .register import Register, RegisterWriteError
from .schema import REASON_PRIORITY, Decision, ModelResult

NON_BOOKING = re.compile(
    r"\b(?:cancel|radd|reschedule|postpone|prepone|change (?:my|the) (?:appointment|time|slot)|"
    r"fee|fees|kitna (?:charge|lagega|paisa)|kitne paise|charges|price|"
    r"doctor se baat|talk to (?:the )?doctor|speak to (?:the )?doctor|"
    r"ice (?:lagau|lagaun|lagana|put)|put ice|kya (?:karu|karun|karna chahiye)|which (?:medicine|tablet)|"
    r"report (?:ready|aaya)|eshtu (?:fees|charge|duddu))\b",
    re.I,
)
NAME_PATTERNS = [
    r"\bmera naam (?:hai )?([a-z]+)", r"\bmeri? (?:mummy|mother|maa|papa|father|wife|husband|beti|beta|daughter|son)(?: ka| ki)? naam ([a-z]+)",
    r"\bnaam ([a-z]+)", r"\bname (?:is )?([a-z]+)", r"\bmy name is ([a-z]+)", r"\bthis is ([a-z]+)",
    r"\bnanna hesaru ([a-z]+)", r"\bhesaru ([a-z]+)", r"\bnaanu ([a-z]+)", r"\b([a-z]+) bol (?:raha|rahi) (?:hoon|hu|hun)",
    r"\b([a-z]+) (?:here|speaking)\b",
]
NAME_STOP = {"hai", "he", "is", "the", "my", "mera", "meri", "a", "ji", "sir", "madam", "aunty", "uncle",
             "appointment", "doctor", "physio", "clinic", "kal", "naale", "booking", "patient", "calling", "nanna"}
TITLES = {"ji", "sir", "madam", "aunty", "uncle", "mr", "mrs", "ms", "dr", "shri", "smt", "avaru", "avru", "garu"}

SAY = {
    "escalate": "This sounds urgent. Please call 108 now. I am also alerting the clinic staff.",
    "handoff": "I will pass this to the clinic staff; they will call you back in the morning.",
    "write_failed": "I could not save the booking just now. The clinic will call you back to confirm. It is NOT confirmed yet.",
}


def _clean_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    parts = [w for w in re.split(r"\s+", name.strip()) if w.lower().strip(".,") not in TITLES]
    return " ".join(w.capitalize() for w in parts) or None


def _name_from_text(text: str) -> Optional[str]:
    s = text.lower()
    for pat in NAME_PATTERNS:
        m = re.search(pat, s)
        if m and m.group(1) not in NAME_STOP:
            return m.group(1).capitalize()
    return None


NOT_NAME_WORDS = (set(RELATIVE) | set(DAYPARTS) | set(NUM_WORDS) | set(WEEKDAY_OF) | TIME_UNITS | set(FRAC_PRE)
                  | set(FRAC_POST) | set(FRAC_WHOLE) | NAME_STOP | {
                      "ge", "ke", "ko", "maadi", "please", "chahiye", "book", "slot", "baje", "bekittu", "beku",
                      "sigatta", "aagutta", "tomorrow", "today", "morning", "evening", "pm", "am", "null", "none"})


def _plausible_name(name: str) -> bool:
    """Held-out H024: qwen3:4b returned the time words 'parso sanje paune aaru ge' as the name.
    Those words are in the transcript, so the in-transcript check alone let them through."""
    words = [w.lower() for w in name.split()]
    return 1 <= len(words) <= 3 and not any(w in NOT_NAME_WORDS or w.isdigit() for w in words)


def pick_name(text: str, mr: ModelResult, trace: list[str]) -> Optional[str]:
    """Model's name, but only if those words appear in the transcript (no invented names)."""
    ex = mr.extraction
    if ex and ex.patient_name:
        cand = _clean_name(ex.patient_name)
        if cand and not _plausible_name(cand):
            trace.append(f"model name {ex.patient_name!r} looks like day/time/booking words; ignored")
        elif cand and all(w.lower() in text.lower() for w in cand.split()):
            return cand
        else:
            trace.append(f"model name {ex.patient_name!r} not in transcript; ignored")
    nm = _name_from_text(text)
    if nm:
        trace.append(f"name from pattern: {nm}")
    return nm


def _said(words: str, utterance: str) -> bool:
    """True if the model's 'verbatim' words really occur in the transcript (case and spacing ignored)."""
    norm = lambda s: " ".join(re.sub(r"[^\w:]", " ", s.lower()).split())  # noqa: E731
    w = norm(words)
    return bool(w) and w in norm(utterance)


def choose_anchor(p: Parse) -> Optional[DayExpr]:
    """The day the caller finally means: last date/relative expression, unless a weekday
    was said after a correction marker that follows it."""
    if not p.days:
        return None
    concrete = [d for d in p.days if d.kind in ("relative", "date")]
    weekdays = [d for d in p.days if d.kind not in ("relative", "date")]
    if not concrete:
        return weekdays[-1]
    last_c = concrete[-1]
    if weekdays and weekdays[-1].pos > last_c.pos and any(last_c.pos < c < weekdays[-1].pos for c in p.corrections):
        return weekdays[-1]
    return last_c


class Guard:
    def __init__(self, register: Register):
        self.register = register

    def _in_session(self, h: int, m: int) -> bool:
        return 0 <= h <= 23 and self.register.in_session(time(h, m))

    def decide(self, utterance: str, reference: datetime, mr: ModelResult) -> Decision:
        trace: list[str] = []
        ref_d = reference.date()
        ref_naive = reference.replace(tzinfo=None)

        # 1. red flags: deterministic list first; the model's flag also escalates (cheap to over-escalate)
        hits = red_flag_hits(utterance)
        if hits:
            return Decision(action="escalate", say=SAY["escalate"], trace=[f"red flag list: {hits}"])
        if mr.extraction and mr.extraction.red_flag:
            return Decision(action="escalate", say=SAY["escalate"], trace=["model red_flag (list did not fire)"])

        # 2. not a new booking -> staff
        #    cancel/reschedule from the model are trusted. "question"/"other" are not: in eval
        #    iteration 1 qwen3:4b called Kannada slot requests ("...gantege sigatta?") questions.
        #    A question that names a day or a time is treated as a booking request.
        p = parse(utterance)
        intent = mr.extraction.intent if mr.extraction else None
        if intent in ("cancel", "reschedule"):
            return Decision(action="handoff", say=SAY["handoff"], trace=[f"model intent {intent}"])
        if NON_BOOKING.search(utterance):
            return Decision(action="handoff", say=SAY["handoff"], trace=["non-booking keyword"])
        if intent in ("question", "other"):
            if not (p.days or p.times):
                return Decision(action="handoff", say=SAY["handoff"], trace=[f"model intent {intent}, no day/time in transcript"])
            trace.append(f"model intent {intent} overridden: transcript names a day/time")
        if intent is None:
            trace.append(f"model output unusable ({mr.error}); continuing on transcript only")

        # 3. resolve the caller's own words
        problems: dict[str, str] = {}
        d: Optional[date] = None
        hm: Optional[tuple[int, int]] = None

        anchor = choose_anchor(p)
        if anchor is not None:
            d, prob = resolve_day(anchor, ref_d)
            trace.append(f"day '{anchor.words}' ({anchor.kind}) -> {d}")
            if prob:
                problems[prob] = anchor.words
            if d is not None:
                bad = weekday_conflict(p, anchor, d)
                if bad:
                    problems["weekday_mismatch"] = f"'{bad.words}' vs {d.strftime('%A %Y-%m-%d')}"
        if p.times:
            te = p.times[-1]
            hm, prob = resolve_time(te, self._in_session)
            trace.append(f"time '{te.words}' -> {hm}")
            if prob:
                problems[prob] = te.words
        if p.hedges:
            problems["ambiguous_time"] = f"unparsed time words {p.hedges}"
            trace.append(f"partial parse: time modifier(s) {p.hedges} not understood -> ambiguous_time")
        if p.alternatives:
            problems["ambiguous_date"] = "caller offered alternative days"
            trace.append("alternative days offered -> ambiguous_date")

        # English fallback: dateparser on the model's verbatim words (never the model's own date),
        # and only if the caller actually said them: in G112 the model invented "Wednesday" for a
        # caller who gave no day, and the fallback booked it.
        ex = mr.extraction
        fallback_words: set[str] = set()  # verbatim words the fallback resolved (checked in the transcript)
        if ex and ex.date_words and not _said(ex.date_words, utterance):
            trace.append(f"model date words '{ex.date_words}' not in transcript: ignored")
        elif (d is None and anchor is None) and ex and ex.date_words:
            dp = dateparse_words(ex.date_words, ref_naive)
            if dp:
                d = dp.date(); trace.append(f"dateparser fallback on '{ex.date_words}' -> {d}")
                fallback_words |= set(tokenize(ex.date_words))
        if (hm is None and not p.times and ex and ex.time_words and _said(ex.time_words, utterance)
                and not HEDGES & set(ex.time_words.lower().split())):
            dp = dateparse_words(ex.time_words, ref_naive)
            if dp and (dp.hour or dp.minute):
                hm = (dp.hour, dp.minute); trace.append(f"dateparser fallback on '{ex.time_words}' -> {hm}")
                fallback_words |= set(tokenize(ex.time_words))

        if ex and ex.date and d and ex.date != d.isoformat():
            trace.append(f"model said {ex.date}; guard resolved {d} (guard wins)")
        if ex and ex.time and hm and ex.time != f"{hm[0]:02d}:{hm[1]:02d}":
            trace.append(f"model said {ex.time}; guard resolved {hm[0]:02d}:{hm[1]:02d} (guard wins)")

        # 4. deterministic checks
        if p.damaged and (d is None or hm is None):
            problems["unintelligible"] = "damaged transcript"
        if d is None and "ambiguous_date" not in problems:
            problems["missing_date"] = ""
        if hm is None and "ambiguous_time" not in problems and "outside_hours" not in problems:
            problems["missing_time"] = ""
        if d is not None:
            if hm is not None:
                when = datetime.combine(d, time(*hm)) if 0 <= hm[0] <= 23 else None
                if when and when < ref_naive:
                    problems["past_time"] = when.isoformat()
            elif d < ref_d:
                problems["past_time"] = d.isoformat()
            if d > ref_d + timedelta(days=int(self.register.clinic["booking_horizon_days"])):
                problems["too_far"] = d.isoformat()
            if self.register.is_closed_day(d):
                problems["closed_day"] = d.strftime("%A")
        if d is not None and hm is not None and 0 <= hm[0] <= 23:
            t = time(*hm)
            if not self.register.in_session(t):
                problems.setdefault("outside_hours", t.strftime("%H:%M"))
            elif self.register.is_taken(d, t):
                problems["slot_taken"] = f"{d} {t:%H:%M}"
        name = pick_name(utterance, mr, trace)
        if not name:
            problems["missing_name"] = ""

        ds = d.isoformat() if d else None
        ts = f"{hm[0]:02d}:{hm[1]:02d}" if hm and 0 <= hm[0] <= 23 else None
        if problems:
            reason = next(r for r in REASON_PRIORITY if r in problems)
            trace.append(f"checks failed: {sorted(problems)} -> ask about {reason}")
            return Decision(action="ask_again", reason=reason, name=name, date=ds, time=ts,
                            say=f"Sorry, I need to check that again ({reason.replace('_', ' ')}).", trace=trace)

        # 5. last gate before the write: did we understand every word around the day and the time?
        spans = [(e.pos, e.pos + len(e.words.split())) for e in ([anchor] if anchor else []) + p.times[-1:]]
        unknown = unknown_near(p, spans, set((name or "").lower().split()) | fallback_words)
        if unknown:
            time_side = bool(p.times) and any(
                abs(i - p.times[-1].pos) <= WINDOW + len(p.times[-1].words.split())
                for i, w in enumerate(p.tokens) if w in unknown)
            reason = "ambiguous_time" if time_side or not anchor else "ambiguous_date"
            trace.append(f"allowlist window: unrecognised words {unknown} next to the day/time -> {reason}")
            return Decision(action="ask_again", reason=reason, name=name, date=ds, time=ts,
                            say=f"Sorry, I need to check that again ({reason.replace('_', ' ')}).", trace=trace)

        # 6. the write, then the confirmation gate
        try:
            self.register.book(d, time(*hm), name, source="guard")
        except RegisterWriteError as e:
            trace.append(f"register write failed: {e}; NOT confirming")
            return Decision(action="write_failed", name=name, date=ds, time=ts, confirmed=False,
                            say=SAY["write_failed"], trace=trace)
        trace.append("register write ok -> confirmed")
        return Decision(action="book", name=name, date=ds, time=ts, confirmed=True,
                        say=f"Booked: {name}, {d.strftime('%A %d %B')} at {ts}. Confirmed.", trace=trace)
