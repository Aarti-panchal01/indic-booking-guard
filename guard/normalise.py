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
    "ayidu": 5, "aydu": 5,
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
WORD_DATE_MARKERS = {"tareekh", "tarikh", "taareekh", "tareek", "tarik", "tareeku", "tareekhu", *MONTHS}
NEXT_WORDS = {"agle", "agli", "agla", "next", "mundina", "mundhina", "coming", "aane"}
PAST_WORDS = {"last", "previous", "pichhle", "pichle", "pichhla", "pichla", "pichhli", "pichli", "kaleda", "hoda", "hodha"}
WEEK_WORDS = {"hafte", "haftey", "hafta", "hafton", "week", "weeks", "vaara", "vara", "waara", "vaarada", "vaaradha", "varada"}

# Added after the blind OOV probe (eval/OOV_RESULTS_blind.md). Not in TAXONOMY.md: these extend coverage,
# they do not change any TAXONOMY rule.
# day of month as a word ("pandrah tareekh", "hadinaidu tareeku"); 1-12 come from NUM_WORDS
DAY_WORDS = {
    "terah": 13, "chaudah": 14, "pandrah": 15, "solah": 16, "satrah": 17, "atharah": 18, "athara": 18,
    "unnees": 19, "unnis": 19, "bees": 20, "ikkees": 21, "ikkis": 21, "baees": 22, "bais": 22, "teis": 23,
    "tees": 30, "chaubees": 24, "pachchees": 25, "pachees": 25, "chhabbees": 26, "sattaees": 27, "atthaees": 28,
    "untees": 29, "ikattees": 31, "iktees": 31,
    "hadimooru": 13, "hadinaalku": 14, "hadinaidu": 15, "hadinaaru": 16, "hadinelu": 17, "hadinentu": 18,
    "hattombattu": 19, "ippattu": 20, "ippattondu": 21, "ippattheradu": 22, "ippattmooru": 23,
    "ippattnaalku": 24, "ippattaidu": 25, "ippattaaru": 26, "ippattelu": 27, "ippattentu": 28,
    "ippattombattu": 29, "moovattu": 30, "moovattondu": 31,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30,
}
# English ordinals are dates without a marker ("fifteenth of this month")
ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
    "twentieth": 20, "thirtieth": 30,
}
DAY_UNIT = {"din", "dino", "dina", "dinagalu", "dinada", "day", "days"}
AFTER_WORDS = {"baad", "bad", "nantara", "nanthara", "later", "after"}
COUNT_WORDS = {"a": 1, "one": 1, "ek": 1, "ondu": 1, "do": 2, "two": 2, "eradu": 2}
# words that modify a time but that the parser did not consume: a partial parse, never trust it
HEDGES = {"half", "quarter", "minute", "minutes", "min", "mins", "around", "about", "approx", "approximately", "aas",
          "roughly", "lagbhag", "takriban", "hattira", "aaspaas", "ish"}
MINUTE_WORDS = {"pandrah": 15, "tees": 30, "paintalis": 45, "paitalis": 45}
# Added after the blind OOV v2 probe (5 wrong writes, all partial parses whose dropped neighbour was not a
# hedge word: "nalku moovattu", "ten forty-five", "after 5 pm", "saade paanch ke thoda baad",
# "sawa paanch... nahi nahi, usse aadha ghanta pehle"). Structural, not a phrase list:
#  - an unconsumed number right after a time is unparsed minutes;
#  - an offset/qualifier word right before or after a time changes it;
#  - an offset word after a correction marker means the caller moved the time relative to itself.
TENS_WORDS = {"twenty", "thirty", "forty", "fifty", "nalavattu", "naalavattu", "aivattu", "chaalis", "pachaas"}
PRE_QUALIFIERS = {"after", "before", "by", "till", "until", "around", "about", "approx", "approximately", "lagbhag", "takriban"}
POST_QUALIFIERS = {"baad", "pehle", "tak", "se", "nantara", "mele", "olage", "modalu", "munche", "later", "earlier",
                   "onwards", "ish", "plus", "minus", "thoda", "swalpa"}
OFFSET_WORDS = {"pehle", "baad", "earlier", "later", "before", "after", "munche", "modalu", "nantara", "mele"}
NOT_MINUTES = {"ek", "do", "sat", "aru", "ent", "che", "rat", "ath", "mur", "a", "one"}

# ---------------------------------------------------------------- allowlist window (after blind OOV v3)
# Three blind probes beat every blocklist of "dangerous modifier" words. The polarity is flipped here:
# before a write, every token within WINDOW of the chosen day and time must be consumed by the parser,
# part of the patient's name, or in KNOWN (words that cannot change a day or a time). Anything else
# means we may have understood only part of what was said -> ask again. Numbers are never KNOWN.
WINDOW = 2
KNOWN = {
    # read by the parser through lookaround (not marked consumed)
    # (NEXT_WORDS / WEEK_WORDS are NOT here: they are harmless only when the parser consumed them)
    *DAYPARTS, *TIME_UNITS, *AMPM, *DATE_MARKERS, *MONTHS, "din", "dina",
    # body parts and symptoms (red flags are handled before this point; here they cannot change a slot)
    "dard", "novu", "pain", "kamar", "sonta", "mandi", "ghutne", "ghutna", "kandha", "kandhe", "gardan", "kutthige",
    "haath", "hath", "kai", "bhuja", "back", "knee", "neck", "shoulder", "ankle", "wrist", "hip", "seene", "chest",
    "jhunjhuni", "tingling", "sore", "stiff", "bandide", "jam", "gaya", "gayi", "sirf", "bas", "kooda", "bhi",
    "waise", "andre", "bandre", "which", "do", "le", "lena", "wait", "no", "sorry", "also", "only", "bahut",
    "ee", "month", "inda", "from", "ye", "yeh", "woh", "wo",
    # grammar: postpositions, particles, articles, pronouns, copulas
    "ko", "ke", "ka", "ki", "ge", "ige", "kke", "ke liye", "liye", "alli", "mein", "me", "mai", "par", "pe", "se",
    "at", "on", "in", "for", "the", "an", "to", "of", "is", "am", "are", "be", "this", "that", "it", "i", "me", "my",
    "we", "you", "your", "mera", "meri", "mere", "mujhe", "hum", "humko", "unka", "unki", "unke", "uska", "nanna",
    "nange", "naanu", "avaru", "avara", "amma", "appa", "papa", "mummy", "maa", "and", "aur", "mattu", "toh", "to",
    "hai", "hain", "hoon", "hu", "ho", "tha", "thi", "ide", "idhe", "agide", "alva", "na", "naa", "ri",
    # booking verbs and nouns
    "appointment", "slot", "time", "book", "booking", "session", "physio", "visit", "chahiye", "chaiye", "beku",
    "bekittu", "bartini", "barthini", "bartivi", "barthivi", "barteeni", "baruve", "barbeku", "baralaa", "baralla",
    "aana", "aaunga", "aaungi", "aa", "aayenge", "jaunga", "jaungi", "sakta", "sakti", "sakte", "milega", "milegi",
    "mil", "jayega", "jaayega", "dedo", "de", "dijiye", "dena", "karo", "kar", "karna", "kariye", "maadi", "kodi",
    "sigatta", "sigutta", "can", "could", "would", "like", "want", "need", "come", "get", "have", "take", "fix",
    "please", "pls", "kindly", "dayavittu", "swalpa", "thank", "thanks", "confirm",
    # name introductions
    "naam", "name", "hesaru", "bol", "raha", "rahi", "here", "speaking", "patient", "this", "is",
    # politeness and fillers
    "haan", "ha", "ji", "accha", "acha", "ok", "okay", "theek", "thik", "sir", "madam", "maam", "bhaiya", "hello",
    "hi", "namaste", "namaskara", "um", "umm", "uh", "hmm", "matlab", "arre", "yes", "yeah", "haudu", "sari",
    "doctor", "dr", "<damaged>",
}
# correction markers are handled by "last value wins"; what follows them is checked separately
CORRECTION_TAIL = 8
COUNTED_UNITS = DAY_UNIT | WEEK_WORDS | {"saal", "mahine", "mahina", "month", "months", "year", "years", "varsha",
                                         "log", "people", "baar", "times", "sessions", "session"}
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
    # military / 24h without colon: "1730 hours", "0930 hrs"
    s = re.sub(r"\b([01]\d|2[0-3])([0-5]\d)\s*(?:hours|hrs|hr)\b", r" \1:\2 ", s)
    s = re.sub(r"\ba\.m\.?", " am ", s)
    s = re.sub(r"\bp\.m\.?", " pm ", s)
    # 4:30 / 4.30 -> keep as one token "4:30"
    s = re.sub(r"\b(\d{1,2})[:.](\d{2})\b", r" \1:\2 ", s)
    # "4 30 baje", "shaam 4 30" -> 4:30 (space-separated hour and minute, TAXONOMY 3.3)
    dp_alt = "|".join(sorted(map(re.escape, DAYPARTS), key=len, reverse=True))
    s = re.sub(r"\b(\d{1,2}) ([0-5]\d)\b(?=\s*(?:baje|bajey|gante\w*|ganteg|am|pm|oclock|ko\b))", r"\1:\2", s)
    s = re.sub(rf"\b({dp_alt}) (?:ko |ke |)(\d{{1,2}}) ([0-5]\d)\b", r"\1 \2:\3", s)
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
    hedges: list[str] = field(default_factory=list)       # unconsumed time modifiers next to a time
    alternatives: bool = False                              # "Thursday ya Friday"
    used: set[int] = field(default_factory=set)            # token indices consumed by a day or time expression
    clause_starts: list[int] = field(default_factory=list)  # token index where each , . ? ! ; clause starts


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
        # "next to next day"
        if t == "next" and at(k + 1) == "to" and at(k + 2) == "next" and at(k + 3) == "day":
            p.days.append(DayExpr(k, "relative", 2, words="next to next day")); used.update(range(k, k + 4)); continue
        # spans: "ek hafte baad", "aidu vaara nantara", "3 din baad", "one week from today", "in a week", "after 2 days"
        span = _span(toks, k)
        if span:
            days, end = span
            p.days.append(DayExpr(k, "relative", days, words=" ".join(toks[k:end]))); used.update(range(k, end)); continue
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
            # "last Monday gir gaye", "pichhle hafte somvar": a past event, not the booking day (G130, V034)
            if prev in PAST_WORDS or (prev in WEEK_WORDS and prev2 in PAST_WORDS):
                used.add(k); continue
            if (prev in WEEK_WORDS and prev2 in NEXT_WORDS) or (prev in WEEK_WORDS and prev2 in ("ke", "ka", "ki", "")) and prev2 in NEXT_WORDS:
                kind = "nextweek_weekday"
            elif prev in WEEK_WORDS and at(k - 2) in NEXT_WORDS:
                kind = "nextweek_weekday"
            elif (prev in ("ke", "ka", "ki", "da", "de") and prev2 in WEEK_WORDS and at(k - 3) in NEXT_WORDS):
                kind = "nextweek_weekday"
            elif nxt in NEXT_WORDS and nxt2 in WEEK_WORDS:
                kind = "nextweek_weekday"
            elif prev in NEXT_WORDS or (prev in ("wala", "vala", "waala", "wale", "waale") and prev2 in NEXT_WORDS):
                kind = "next_weekday"
            if kind != "weekday":
                # mark the "agle hafte" / "next week" words this weekday used, so the allowlist window
                # can tell them apart from an unused "agle" ("kal ke agle din" must not pass as "kal")
                used.update(i for i in range(max(0, k - 3), min(n, k + 3)) if toks[i] in NEXT_WORDS | WEEK_WORDS | {"ke", "ka", "ki", "da", "de", "wala", "vala", "waala"})
            p.days.append(DayExpr(k, kind, wd, words=t)); used.add(k); continue
    # explicit dates: "10 tareekh", "9th", "october 9", "9 october", "9 ne tareeku"
    # A month already claimed by an ordinal ("the 2nd of November") cannot also claim the next number, and a
    # number after a comma does not attach to a month before it: "2nd of November, five in the evening" is a
    # date and a time, not two dates (OOV v4 S042).
    month_used: set[int] = set()
    cstarts = set(_clause_starts(text, toks))
    for k, t in enumerate(toks):
        if k in used:
            continue
        nxt = at(k + 1)
        nxt2 = at(k + 2)
        # "second Monday of November", "pehla shanivar": an ordinal before a weekday is not a day of the month
        if t in ORDINALS and (nxt in WEEKDAY_OF or nxt2 in WEEKDAY_OF):
            p.alternatives = True  # reported as ambiguous_date
            used.add(k)
            continue
        if t in ORDINALS or (t in ("twenty", "thirty") and nxt in ORDINALS and ORDINALS[nxt] < 10):
            val, end = (ORDINALS[t], k + 1) if t in ORDINALS else (DAY_WORDS[t] + ORDINALS[nxt], k + 2)
            month = MONTHS.get(at(end)) or (MONTHS.get(at(end + 1)) if at(end) == "of" else None) or MONTHS.get(at(k - 1))
            for mi in (end, end + 1, k - 1):
                if at(mi) in MONTHS:
                    month_used.add(mi)
                    break
            p.days.append(DayExpr(k, "date", val, month=month, words=" ".join(toks[k:end]))); used.update(range(k, end))
            continue
        markers = DATE_MARKERS
        if t.isdigit():
            val = int(t)
        elif t in DAY_WORDS or t in NUM_WORDS:
            # a number word is a date only before "tareekh"/a month, or after a month ("do date" is not a date)
            val = DAY_WORDS.get(t) or NUM_WORDS[t]
            markers = WORD_DATE_MARKERS
        else:
            continue
        if not (1 <= val <= 31):
            continue
        t = str(val)
        month = None
        is_date = False
        if nxt in markers or (nxt == "ne" and nxt2 in markers):
            is_date = True
            # "3rd november", "2nd of november", "november 3rd": the month may sit after "of" or before the number
            # (before Oct 8 the month was dropped here, so "november 10th" resolved to October 10)
            for mi in (k + 1, k + 2, k + 3 if nxt2 == "of" else -1, k - 1):
                if mi >= 0 and at(mi) in MONTHS and mi not in month_used:
                    month = MONTHS[at(mi)]
                    month_used.add(mi)
                    break
        elif at(k - 1) in MONTHS and (k - 1) not in month_used and k not in cstarts:
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
        # English fractions: "half past five", "quarter past 10", "quarter to five"
        elif not hm and (at(k - 2), at(k - 1)) in (("half", "past"), ("quarter", "past"), ("quarter", "to")):
            frac = {"half": 30, "past": 15, "to": -15}[at(k - 2) if at(k - 2) == "half" else at(k - 1)]
            start = k - 2
        if at(j) in FRAC_POST and not hm:
            frac = FRAC_POST[at(j)]; j += 1
        unit = False
        if at(j) in TIME_UNITS:
            unit = True; j += 1
            # "paanch baj ke tees minute", "5 baje ke 15 minute"
            mw = at(j + 1)
            mval = int(mw) if mw.isdigit() else MINUTE_WORDS.get(mw)
            if not hm and frac is None and at(j) == "ke" and mval is not None and 0 <= mval <= 59 and at(j + 2) in ("minute", "minutes", "min", "mins"):
                minute = mval; j += 3
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
        # "11 in the morning", "at 6 in the evening"
        if not marked and at(k + 1) == "in" and at(k + 2) == "the" and at(k + 3) in DAYPARTS:
            marked = True; dp = DAYPARTS[at(k + 3)]
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

    # Partial-parse guard (blind OOV probe: "half past five baje" was read as 17:00, "5 gante hattira" as 17:00):
    # a time modifier the parser did not consume, within 3 tokens of a time, means we did not understand it.
    for te in p.times:
        end = te.pos + len(te.words.split())
        for i in range(max(0, te.pos - 3), min(n, end + 3)):
            if i not in used and toks[i] in HEDGES:
                p.hedges.append(toks[i])
        if te.pos - 1 >= 0 and te.pos - 1 not in used and toks[te.pos - 1] in PRE_QUALIFIERS:
            p.hedges.append(toks[te.pos - 1])
        for i in range(end, min(n, end + 3)):
            w = toks[i]
            if i in used or w in NOT_MINUTES:
                continue
            is_num = ((w.isdigit() and int(w) < 60) or w in NUM_WORDS or w in DAY_WORDS or w in TENS_WORDS) \
                and not (i + 1 < n and toks[i + 1] in COUNTED_UNITS)   # "6 baje, 2 hafte se dard" is a duration
            # "5 baje ke baad" / "4 baje tak": a qualifier right after the time (allow one "ke"/"ka"/"ge" between)
            near_qual = w in POST_QUALIFIERS and (i <= end + 1 or toks[i - 1] in ("ke", "ka", "ki", "ge", "thoda", "swalpa"))
            if is_num or near_qual:
                p.hedges.append(w)
    if p.times:
        last_end = p.times[-1].pos + len(p.times[-1].words.split())
        cuts = [c for c in p.corrections if c >= last_end]
        if cuts:
            for i in range(cuts[0] + 1, min(n, cuts[0] + 8)):
                if toks[i] in OFFSET_WORDS and toks[i - 1] not in DAY_UNIT and toks[i - 1] not in WEEK_WORDS \
                        and toks[i - 1] not in ("saal", "mahine", "month", "year", "years", "months"):
                    p.hedges.append(f"correction+{toks[i]}")
                    break
    # "Thursday ya Friday", "naale athava naadidu": the caller offers alternatives
    for a, b in zip(p.days, p.days[1:]):
        between = toks[a.pos + len(a.words.split()): b.pos]
        if len(between) <= 2 and any(w in ("ya", "or", "athava", "illandre", "leda") for w in between):
            p.alternatives = True
    p.used = used
    p.clause_starts = _clause_starts(text, toks)
    return p


def _clause_starts(text: str, toks: list[str]) -> list[int]:
    """Token index of each clause start, by tokenizing each punctuation-separated piece on its own.
    If the pieces do not add up to the same tokens (a rewrite crossed a boundary), return [0]."""
    pieces = [s for s in re.split(r"[,.?!;]+(?:\s|$)", text) if s.strip()]
    starts, out = 0, []
    for piece in pieces:
        out.append(starts)
        starts += len(tokenize(piece))
    joined = [t for piece in pieces for t in tokenize(piece)]
    return out if joined == toks else [0]


def unknown_near(p: Parse, spans: list[tuple[int, int]], name_tokens: set[str]) -> list[str]:
    """Tokens within WINDOW of the chosen day/time spans, or after a correction that follows the last
    time, that are not consumed, not the name, and not KNOWN. Empty list = the write may go ahead."""
    toks, n = p.tokens, len(p.tokens)
    inside = set(p.used) | {i for s, e in spans for i in range(s, e)}
    # look back only within the clause ("neck pain from desk work, kal shaam 4 baje": 'work' is narrative);
    # look ahead across clauses ("naale nahi, uske agle din" must still be seen)
    starts = [c for c in p.clause_starts if c <= min((s for s, _ in spans), default=0)]
    floor = max(starts, default=0)
    near = {i for s, e in spans for i in range(max(floor, s - WINDOW), min(n, e + WINDOW))}
    if spans:
        last_end = max(e for _, e in spans)
        for c in p.corrections:
            if c >= last_end - 1:
                near |= set(range(c + 1, min(n, c + 1 + CORRECTION_TAIL)))
    out = []
    for i in sorted(near):
        w = toks[i]
        if i in inside or w in name_tokens or w in KNOWN or w in CORRECTION_MARKERS:
            continue
        out.append(w)
    return out


def _count(tok: str) -> Optional[int]:
    if tok.isdigit():
        return int(tok)
    return COUNT_WORDS.get(tok) or NUM_WORDS.get(tok)


def _span(toks: list[str], k: int) -> Optional[tuple[int, int]]:
    """'ek hafte baad', 'aidu vaara nantara', '3 din baad', 'one week from today', 'in a week', 'after 2 days'
    -> (days, end index). None if not a span. 'do hafte se dard' (since) is not a span."""
    at = lambda i: toks[i] if 0 <= i < len(toks) else ""  # noqa: E731
    lead = 1 if toks[k] in ("in", "after") else 0
    num = _count(at(k + lead))
    unit = at(k + lead + 1)
    if num is None or not (unit in WEEK_WORDS or unit in DAY_UNIT):
        return None
    days = num * (7 if unit in WEEK_WORDS else 1)
    end = k + lead + 2
    if lead:
        return days, end
    if at(end) in AFTER_WORDS:
        return days, end + 1
    if at(end) == "from" and at(end + 1) in ("today", "now"):
        return days, end + 2
    return None


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
