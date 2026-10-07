"""Deterministic date/time normaliser for Hinglish and Kannada-English (Latin script).

Implements TAXONOMY.md section 3. No model calls. Pure functions of (text, reference).
Written after held_out.jsonl was committed (sha256 in STATE.md) and without reading it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional

# ---------------------------------------------------------------- vocab
HI_NUM = {
    "ek": 1, "do": 2, "teen": 3, "tin": 3, "chaar": 4, "char": 4, "chār": 4, "paanch": 5, "panch": 5,
    "paach": 5, "chhe": 6, "chhah": 6, "chhey": 6, "che": 6, "chheh": 6, "saat": 7, "aath": 8, "ath": 8,
    "nau": 9, "das": 10, "dus": 10, "gyarah": 11, "gyara": 11, "gyaarah": 11, "barah": 12, "bara": 12, "baarah": 12,
}
KN_NUM = {
    "ondu": 1, "ond": 1, "eradu": 2, "erdu": 2, "yeradu": 2, "mooru": 3, "muru": 3, "mur": 3,
    "naalku": 4, "nalku": 4, "naalakku": 4, "nalakku": 4, "naalk": 4, "nalk": 4, "aidu": 5, "aidhu": 5, "aid": 5,
    "aaru": 6, "aru": 6, "elu": 7, "yelu": 7, "entu": 8, "yentu": 8, "ent": 8, "ombattu": 9, "ombhattu": 9,
    "hattu": 10, "hatthu": 10, "hannondu": 11, "hanneradu": 12, "hanerdu": 12,
}
EN_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
NUM_WORDS = {**EN_NUM, **HI_NUM, **KN_NUM}

FRAC_PRE = {"saade": 30, "sade": 30, "saadhe": 30, "sadhe": 30, "saarhe": 30,
            "sawa": 15, "sava": 15, "savva": 15, "paune": -15, "pone": -15, "paunay": -15}
FRAC_POST = {"vare": 30, "uvare": 30, "kaalu": 15, "kaal": 15, "mukkaalu": 45, "mukkal": 45, "mukaalu": 45}
FRAC_WHOLE = {"dedh": (1, 30), "derh": (1, 30), "dhai": (2, 30), "dhaai": (2, 30), "adhai": (2, 30)}
TIME_UNITS = {"baje", "bajey", "bajay", "bje", "baj", "gante", "gantege", "ganteg", "gantige", "ghante",
              "ganteh", "gantey", "oclock", "o'clock", "hrs"}
AMPM = {"am": "am", "a.m.": "am", "pm": "pm", "p.m.": "pm"}

# day-part -> allowed 24h range [start, end] in minutes; raat wraps midnight
DAYPARTS = {
    "subah": "morning", "subha": "morning", "savere": "morning", "sawere": "morning", "morning": "morning",
    "beligge": "morning", "bellige": "morning", "belagge": "morning", "beligy": "morning",
    "dopahar": "afternoon", "dopaher": "afternoon", "dophar": "afternoon", "afternoon": "afternoon",
    "madhyahna": "afternoon", "madhyana": "afternoon", "madhyaahna": "afternoon",
    "shaam": "evening", "sham": "evening", "shyam": "evening", "evening": "evening",
    "sanje": "evening", "saayankaala": "evening", "sayankala": "evening", "saayankala": "evening",
    "raat": "night", "rat": "night", "night": "night", "raatri": "night", "ratri": "night", "rathri": "night",
}
DAYPART_RANGE = {"morning": (5 * 60, 11 * 60 + 59), "afternoon": (12 * 60, 15 * 60 + 59),
                 "evening": (16 * 60, 19 * 60 + 59), "night": (20 * 60, 4 * 60 + 59)}

WEEKDAY_WORDS = {
    0: ["somvar", "somwar", "somvaar", "somavara", "somavaara", "monday", "mon"],
    1: ["mangalvar", "mangalwar", "mangalvaar", "mangalavara", "mangalavaara", "tuesday", "tue"],
    2: ["budhvar", "budhwar", "budhvaar", "budhavara", "budhavaara", "budhvara", "wednesday", "wed"],
    3: ["guruvar", "guruwar", "guruvaar", "guruvara", "guruvaara", "brihaspativar", "brihaspatiwar", "thursday", "thu", "thurs"],
    4: ["shukravar", "shukrawar", "shukravaar", "shukravara", "shukravaara", "sukravara", "friday", "fri"],
    5: ["shanivar", "shaniwar", "shanivaar", "shanivara", "shanivaara", "saturday", "sat"],
    6: ["ravivar", "raviwar", "ravivaar", "ravivara", "bhanuvara", "bhanuvaara", "itvaar", "itwar", "sunday", "sun"],
}
WEEKDAY_OF = {w: i for i, ws in WEEKDAY_WORDS.items() for w in ws}
RELATIVE = {
    "aaj": 0, "aj": 0, "today": 0, "indu": 0, "ivattu": 0, "ivatthu": 0, "ivathu": 0,
    "kal": 1, "kall": 1, "tomorrow": 1, "tmrw": 1, "naale": 1, "nale": 1, "naaley": 1, "naali": 1,
    "parso": 2, "parson": 2, "parsoon": 2, "parsho": 2, "naadidu": 2, "nadidu": 2, "naadiddu": 2,
}
DATE_MARKERS = {"tareekh", "tarikh", "taareekh", "tareek", "tarik", "tareeku", "tareekhu", "date",
                "th", "st", "nd", "rd", "october", "oct", "november", "nov"}
MONTHS = {"october": 10, "oct": 10, "november": 11, "nov": 11}
NEXT_WORDS = {"agle", "agli", "agla", "next", "mundina", "mundhina", "coming", "aane"}
WEEK_WORDS = {"hafte", "haftey", "week", "vaara", "vara", "waara"}
CORRECTION_MARKERS = {"nahi", "nahin", "nai", "alla", "illa", "beda", "sorry", "matlab", "actually", "balki", "rather"}
DAMAGE = re.compile(r"\[(?:inaudible|noise|unclear|crosstalk|silence|static|unintelligible)[^\]]*\]|\?\?\?|<unk>", re.I)


# ---------------------------------------------------------------- tokens
@dataclass
class Tok:
    text: str
    i: int


def tokenize(text: str) -> list[str]:
    s = text.lower()
    s = DAMAGE.sub(" <damaged> ", s)
    s = s.replace("’", "'").replace("o' clock", "oclock").replace("o'clock", "oclock").replace("o clock", "oclock")
    s = re.sub(r"\ba\.m\.?", " am ", s)
    s = re.sub(r"\bp\.m\.?", " pm ", s)
    # 4:30 / 4.30 -> keep as one token "4:30"
    s = re.sub(r"\b(\d{1,2})[:.](\d{2})\b", r" \1:\2 ", s)
    # glued units: 4baje, 4pm, 9th, 10tareekh
    s = re.sub(r"\b(\d{1,2}(?::\d{2})?)(am|pm|baje|gante\w*|ganteg|th|st|nd|rd|tareekh\w*|tarikh)\b", r"\1 \2", s)
    # Kannada glued fractions: naalkuvare, naalku-vare, naalakkuvare, 4-vare
    num_alt = "|".join(sorted(map(re.escape, KN_NUM), key=len, reverse=True))
    s = re.sub(rf"\b({num_alt}|\d{{1,2}})-?u?vare\b", r"\1 vare", s)
    s = re.sub(r"\b(\d{1,2})-?(ne|ne)\b", r"\1 ne", s)
    s = re.sub(r"[^\w:<>'\s]", " ", s)
    return s.split()


# ---------------------------------------------------------------- results
@dataclass
class TimeExpr:
    pos: int
    hour: int            # as spoken: 1..12, or 0..23 if a 24h digit form
    minute: int
    daypart: Optional[str] = None
    ampm: Optional[str] = None
    is24: bool = False
    words: str = ""


@dataclass
class DayExpr:
    pos: int
    kind: str            # relative | weekday | next_weekday | nextweek_weekday | date
    value: int           # offset, weekday index, or day-of-month
    month: Optional[int] = None
    words: str = ""


@dataclass
class Parse:
    days: list[DayExpr] = field(default_factory=list)
    times: list[TimeExpr] = field(default_factory=list)
    corrections: list[int] = field(default_factory=list)
    damaged: bool = False
    tokens: list[str] = field(default_factory=list)


def _num(tok: str) -> Optional[int]:
    if tok.isdigit() and 0 <= int(tok) <= 24:
        return int(tok)
    return NUM_WORDS.get(tok)


def parse(text: str) -> Parse:
    toks = tokenize(text)
    p = Parse(tokens=toks, damaged="<damaged>" in toks)
    n = len(toks)
    used: set[int] = set()

    def at(k: int) -> str:
        return toks[k] if 0 <= k < n else ""

    # corrections ("nahi nahi", "alla alla", "sorry", "i mean")
    for k, t in enumerate(toks):
        if t in CORRECTION_MARKERS or (t == "mean" and at(k - 1) == "i") or (t == "no" and at(k + 1) == "no"):
            p.corrections.append(k)

    # ---- days
    for k, t in enumerate(toks):
        if k in used:
            continue
        # "day after tomorrow"
        if t == "day" and at(k + 1) == "after" and at(k + 2) == "tomorrow":
            p.days.append(DayExpr(k, "relative", 2, words="day after tomorrow")); used.update({k, k + 1, k + 2}); continue
        if t in RELATIVE:
            # "kal se" / "kal raat se" = since yesterday (symptom history), not a booking day
            if t in ("kal", "kall") and (at(k + 1) == "se" or (at(k + 1) in DAYPARTS and at(k + 2) == "se")):
                continue
            # "aane wala kal" is still tomorrow; "ek" or a number before kal is not a day
            p.days.append(DayExpr(k, "relative", RELATIVE[t], words=t)); used.add(k); continue
        if t in WEEKDAY_OF:
            if t in ("sat", "sun", "wed", "mon", "fri", "thu", "tue") and not _looks_like_english_day_abbrev(toks, k):
                continue
            wd = WEEKDAY_OF[t]
            prev, prev2 = at(k - 1), at(k - 2)
            nxt, nxt2 = at(k + 1), at(k + 2)
            kind = "weekday"
            if (prev in WEEK_WORDS and prev2 in NEXT_WORDS) or (prev in WEEK_WORDS and prev2 in ("ke", "ka", "ki", "")) and prev2 in NEXT_WORDS:
                kind = "nextweek_weekday"
            elif prev in WEEK_WORDS and at(k - 2) in NEXT_WORDS:
                kind = "nextweek_weekday"
            elif (prev in ("ke", "ka", "ki", "da", "de") and prev2 in WEEK_WORDS and at(k - 3) in NEXT_WORDS):
                kind = "nextweek_weekday"
            elif nxt in NEXT_WORDS and nxt2 in WEEK_WORDS:
                kind = "nextweek_weekday"
            elif prev in NEXT_WORDS or (prev in ("wala", "vala", "waala") and prev2 in NEXT_WORDS):
                kind = "next_weekday"
            p.days.append(DayExpr(k, kind, wd, words=t)); used.add(k); continue
    # explicit dates: "10 tareekh", "9th", "october 9", "9 october", "9 ne tareeku"
    for k, t in enumerate(toks):
        if not t.isdigit() or not (1 <= int(t) <= 31):
            continue
        nxt = at(k + 1)
        nxt2 = at(k + 2)
        month = None
        is_date = False
        if nxt in DATE_MARKERS or (nxt == "ne" and nxt2 in DATE_MARKERS):
            is_date = True
            month = MONTHS.get(nxt) or MONTHS.get(nxt2)
        elif at(k - 1) in MONTHS:
            is_date = True
            month = MONTHS[at(k - 1)]
        if is_date and nxt not in TIME_UNITS:
            p.days.append(DayExpr(k, "date", int(t), month=month, words=f"{t} {nxt}")); used.add(k)

    # ---- times
    def nearest_daypart(k: int) -> Optional[str]:
        for d in (1, 2, 3, 4):
            if at(k - d) in DAYPARTS:
                return DAYPARTS[at(k - d)]
        for d in (1, 2, 3):
            if at(k + d) in DAYPARTS:
                return DAYPARTS[at(k + d)]
        return None

    k = 0
    while k < n:
        t = toks[k]
        if k in used:
            k += 1; continue
        if t in FRAC_WHOLE:
            h, m = FRAC_WHOLE[t]
            j = k + 1
            ampm = None
            if at(j) in TIME_UNITS:
                j += 1
            if at(j) in AMPM:
                ampm = AMPM[at(j)]; j += 1
            p.times.append(TimeExpr(k, h, m, nearest_daypart(k), ampm, words=" ".join(toks[k:j])))
            used.update(range(k, j)); k = j; continue
        hm = re.fullmatch(r"(\d{1,2}):(\d{2})", t)
        h = int(hm.group(1)) if hm else _num(t)
        if h is None:
            k += 1; continue
        minute = int(hm.group(2)) if hm else 0
        start, j = k, k + 1
        frac = None
        if at(k - 1) in FRAC_PRE and not hm:
            frac = FRAC_PRE[at(k - 1)]; start = k - 1
        if at(j) in FRAC_POST and not hm:
            frac = FRAC_POST[at(j)]; j += 1
        unit = False
        if at(j) in TIME_UNITS:
            unit = True; j += 1
        ampm = None
        if at(j) in AMPM:
            ampm = AMPM[at(j)]; j += 1
        elif at(j) == "ko" and at(j + 1) in AMPM:
            ampm = AMPM[at(j + 1)]; j += 2
        dp = nearest_daypart(k)
        is_word = t in NUM_WORDS
        # Only accept a number as a time when something marks it as one.
        marked = hm is not None or frac is not None or unit or ampm is not None
        if not marked and dp is not None and (at(k - 1) in DAYPARTS or at(k - 2) in DAYPARTS or at(k + 1) in DAYPARTS):
            marked = True
        if not marked or (is_word and t in ("do", "ek", "sat", "aru", "ent", "che", "rat", "ath", "mur") and not (unit or frac or ampm)):
            k += 1; continue
        if h > 24 or minute > 59:
            k += 1; continue
        if frac is not None:
            if frac < 0:  # paune X = (X-1):45
                h = h - 1 if h > 1 else 12
                minute = 45
            else:
                minute = frac
        is24 = hm is not None and h >= 13 or h == 0
        p.times.append(TimeExpr(start, h, minute, dp, ampm, is24, words=" ".join(toks[start:j])))
        used.update(range(start, j))
        k = j
    p.days.sort(key=lambda d: d.pos)
    p.times.sort(key=lambda t: t.pos)
    return p


def _looks_like_english_day_abbrev(toks: list[str], k: int) -> bool:
    """'sat'/'sun' etc. are common words in Hinglish/Kannada; only accept with an English-ish neighbour."""
    near = set(toks[max(0, k - 2): k + 3])
    return bool(near & {"on", "this", "next", "coming", "morning", "evening", "at", "pm", "am"})


# ---------------------------------------------------------------- resolution
@dataclass
class Resolved:
    date: Optional[date] = None
    hm: Optional[tuple[int, int]] = None
    problem: Optional[str] = None   # TAXONOMY reason code found while resolving
    notes: list[str] = field(default_factory=list)


def _next_weekday_strict(ref: date, wd: int) -> date:
    delta = (wd - ref.weekday()) % 7
    return ref + timedelta(days=delta or 7)


def _weekday_next_week(ref: date, wd: int) -> date:
    monday_next = ref + timedelta(days=7 - ref.weekday())
    return monday_next + timedelta(days=wd)


def resolve_day(e: DayExpr, ref: date) -> tuple[Optional[date], Optional[str]]:
    if e.kind == "relative":
        return ref + timedelta(days=e.value), None
    if e.kind == "weekday":
        return _next_weekday_strict(ref, e.value), None
    if e.kind == "nextweek_weekday":
        return _weekday_next_week(ref, e.value), None
    if e.kind == "next_weekday":
        a, b = _next_weekday_strict(ref, e.value), _weekday_next_week(ref, e.value)
        return (a, None) if a == b else (None, "ambiguous_date")
    if e.kind == "date":
        y, m = ref.year, e.month or ref.month
        if e.month is None and e.value < ref.day:
            m += 1
            if m == 13:
                y, m = y + 1, 1
        try:
            return date(y, m, e.value), None
        except ValueError:
            return None, "ambiguous_date"
    return None, None


def _in_range(minutes: int, part: str) -> bool:
    lo, hi = DAYPART_RANGE[part]
    return lo <= minutes <= hi if lo <= hi else (minutes >= lo or minutes <= hi)


def resolve_time(t: TimeExpr, in_session) -> tuple[Optional[tuple[int, int]], Optional[str]]:
    """Return ((h, m), None) or (None/partial, reason). `in_session(h, m)` is the clinic-hours check."""
    if t.is24:
        hm = (t.hour, t.minute)
        if t.daypart and not _in_range(hm[0] * 60 + hm[1], t.daypart):
            return None, "ambiguous_time"
        return hm, None
    h12 = t.hour % 12
    if t.ampm:
        h = h12 + (12 if t.ampm == "pm" else 0)
        return (h, t.minute), None
    cands = [(h12, t.minute), (h12 + 12, t.minute)]
    if t.daypart:
        fit = [c for c in cands if _in_range(c[0] * 60 + c[1], t.daypart)]
        if not fit:
            return None, "ambiguous_time"
        return fit[0], None
    ok = [c for c in cands if in_session(*c)]
    if len(ok) == 1:
        return ok[0], None
    if not ok:
        return cands[1] if 1 <= t.hour <= 7 else cands[0], "outside_hours"
    return None, "ambiguous_time"


def weekday_conflict(p: Parse, anchor: DayExpr, resolved: date) -> Optional[DayExpr]:
    """A stated weekday that disagrees with the resolved date, with no correction marker between them."""
    for e in p.days:
        if e is anchor or e.kind not in ("weekday", "next_weekday", "nextweek_weekday"):
            continue
        lo, hi = sorted((e.pos, anchor.pos))
        if any(lo < c < hi for c in p.corrections):
            continue
        if e.value != resolved.weekday():
            return e
    return None
