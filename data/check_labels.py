"""Consistency checker for golden.jsonl / held_out.jsonl labels.

Usage: python -I check_labels.py <path-to-jsonl> [--clinic <clinic.json>] [--min-distribution]

Checks schema, enums and the arithmetic-checkable parts of the label spec
(TAXONOMY.md). It does NOT resolve utterances; it only verifies that the
labels are self-consistent with clinic.json and with any weekday word said.
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, date
from pathlib import Path

LANGS = {"hinglish", "kannada_english", "english", "devanagari_hindi", "mixed_other"}
ACTIONS = {"book", "ask_again", "escalate", "handoff", "write_failed"}
REASONS = {"missing_name", "missing_date", "missing_time", "ambiguous_date", "ambiguous_time",
           "weekday_mismatch", "past_time", "outside_hours", "closed_day", "slot_taken",
           "too_far", "unintelligible"}
CATEGORIES = {"clean_relative", "daypart_fraction", "bare_hour", "weekday_only", "explicit_date",
              "weekday_mismatch", "weekday_match", "ambiguous_next", "past_time", "outside_hours",
              "slot_taken", "missing_field", "self_correction", "spelling_variant", "asr_noise",
              "adversarial", "red_flag", "pain_not_red_flag", "non_booking", "tool_failure",
              "devanagari", "english_control"}
TOP_KEYS = {"id", "utterance", "lang_mix", "reference_datetime", "category", "tool_failure",
            "expected", "notes", "provenance"}
EXP_KEYS = {"action", "name", "date", "time", "reason"}
PROVENANCE = "synthetic, AI-written, not native-speaker-audited"

# weekday index: Monday = 0
WEEKDAYS = {}
for idx, names in enumerate([
    ["somvar", "somwar", "somavara", "monday"],
    ["mangalvar", "mangalwar", "mangalavara", "tuesday"],
    ["budhvar", "budhwar", "budhavara", "wednesday"],
    ["guruvar", "gurwar", "brihaspativar", "guruvara", "thursday"],
    ["shukravar", "shukrawar", "shukravara", "friday"],
    ["shanivar", "shaniwar", "shanivara", "saturday"],
    ["ravivar", "raviwar", "ravivara", "bhanuvara", "sunday"],
]):
    for n in names:
        WEEKDAYS[n] = idx

SESSIONS = [(9 * 60, 13 * 60), (16 * 60, 20 * 60)]  # start inclusive, end exclusive


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def in_session(hhmm):
    t = minutes(hhmm)
    return t % 15 == 0 and any(s <= t < e for s, e in SESSIONS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--clinic", default=str(Path(__file__).resolve().parent / "clinic.json"))
    ap.add_argument("--min-distribution", action="store_true",
                    help="also enforce the main golden-set distribution minimums")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    clinic = json.loads(Path(args.clinic).read_text(encoding="utf-8"))
    booked = set(clinic["booked"])  # "YYYY-MM-DDTHH:MM"
    horizon = clinic["booking_horizon_days"]

    viol = []
    cases = []
    for ln, line in enumerate(Path(args.path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as e:
            viol.append(f"line {ln}: invalid JSON: {e}")

    seen = set()
    c_lang, c_act, c_rea, c_cat = Counter(), Counter(), Counter(), Counter()
    refs = Counter()
    n_tf = n_adv = 0
    weird_neg = 0

    for c in cases:
        cid = c.get("id", "?")

        def v(msg):
            viol.append(f"{cid}: {msg}")

        # OOV probe files (T ids) may carry an extra "oov_features" list
        if set(c) - {"oov_features"} != TOP_KEYS:
            v(f"top-level keys differ: missing {TOP_KEYS - set(c)}, extra {set(c) - TOP_KEYS}")
            continue
        exp = c["expected"]
        if not isinstance(exp, dict) or set(exp) != EXP_KEYS:
            v("expected keys wrong")
            continue
        if not re.fullmatch(r"[GHVT]\d{3}", cid):
            v("id format")
        if cid in seen:
            v("duplicate id")
        seen.add(cid)
        if c["lang_mix"] not in LANGS:
            v(f"lang_mix {c['lang_mix']}")
        if c["category"] not in CATEGORIES:
            v(f"category {c['category']}")
        if not isinstance(c["tool_failure"], bool):
            v("tool_failure not bool")
        if not str(c["provenance"]).startswith(PROVENANCE):
            v("provenance string")
        if not c["utterance"].strip() or not c["notes"].strip():
            v("empty utterance/notes")
        try:
            ref = datetime.fromisoformat(c["reference_datetime"])
        except ValueError:
            v("bad reference_datetime")
            continue
        if not c["reference_datetime"].endswith("+05:30"):
            v("reference_datetime not +05:30")

        act, reason = exp["action"], exp["reason"]
        name, dstr, tstr = exp["name"], exp["date"], exp["time"]
        if act not in ACTIONS:
            v(f"action {act}")
            continue
        if reason is not None and reason not in REASONS:
            v(f"reason {reason}")
        if (act == "ask_again") != (reason is not None):
            v("reason must be set iff action is ask_again")
        if name is not None and not (isinstance(name, str) and name.strip() and name[0].isupper() or
                                     (isinstance(name, str) and name and not name[0].isascii())):
            v(f"name format {name!r}")
        if dstr is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dstr):
            v(f"date format {dstr!r}")
        if tstr is not None and not re.fullmatch(r"\d{2}:\d{2}", tstr):
            v(f"time format {tstr!r}")

        d = None
        if dstr:
            try:
                d = date.fromisoformat(dstr)
            except ValueError:
                v(f"date not a valid date {dstr}")

        # tool_failure / write_failed consistency
        if act == "write_failed" and not c["tool_failure"]:
            v("write_failed requires tool_failure true")
        if c["tool_failure"] and act == "book":
            v("tool_failure true with action book (should be write_failed)")
        if act in ("escalate", "handoff") and (name or dstr or tstr):
            v("escalate/handoff must have null name/date/time (file convention)")

        if act in ("book", "write_failed"):
            if not (name and d and tstr):
                v("book/write_failed needs name, date, time")
            else:
                if d.weekday() == 6:
                    v("booked on Sunday")
                if not in_session(tstr):
                    v(f"time {tstr} not a quarter hour inside a session")
                if f"{dstr}T{tstr}" in booked:
                    v(f"slot {dstr} {tstr} already booked")
                dt = datetime.fromisoformat(f"{dstr}T{tstr}:00+05:30")
                if dt <= ref:
                    v("datetime not after reference_datetime")
                if (d - ref.date()).days > horizon:
                    v(f"more than {horizon} days ahead")
            # weekday words must match
            toks = re.findall(r"[a-z]+", c["utterance"].lower())
            for tok in toks:
                if tok in WEEKDAYS and d and WEEKDAYS[tok] != d.weekday():
                    v(f"weekday word '{tok}' does not match date {dstr} ({d.strftime('%A')})")

        if act == "ask_again" and reason:
            if reason == "slot_taken":
                if not (d and tstr and f"{dstr}T{tstr}" in booked):
                    v("slot_taken but slot is not in booked list")
            if reason == "closed_day" and not (d and d.weekday() == 6):
                v("closed_day but date is not a Sunday")
            if reason == "past_time":
                if not (d and tstr):
                    v("past_time needs resolved date and time")
                else:
                    dt = datetime.fromisoformat(f"{dstr}T{tstr}:00+05:30")
                    if dt >= ref:
                        v("past_time but datetime is not before reference")
            if reason == "too_far":
                if not d or (d - ref.date()).days <= horizon:
                    v("too_far but date within horizon")
            if reason == "missing_name" and name is not None:
                v("missing_name but name filled")
            if reason == "missing_date" and dstr is not None:
                v("missing_date but date filled")
            if reason == "missing_time" and tstr is not None:
                v("missing_time but time filled")
            if reason == "weekday_mismatch":
                if dstr is not None:
                    v("weekday_mismatch must leave date null (file convention)")
                if not any(t in WEEKDAYS for t in re.findall(r"[a-z]+", c["utterance"].lower())) \
                        and c["lang_mix"] != "devanagari_hindi":
                    v("weekday_mismatch but no weekday word in utterance")
            if reason == "ambiguous_date" and dstr is not None:
                v("ambiguous_date must leave date null")
            if reason == "outside_hours" and d and d.weekday() == 6:
                v("outside_hours on a Sunday should be closed_day")
            if reason == "outside_hours" and tstr and in_session(tstr):
                v("outside_hours but time is a valid slot time")
            # ask_again that would otherwise be a clean valid slot
            if reason not in ("slot_taken", "past_time") and d and tstr and in_session(tstr) \
                    and reason in ("ambiguous_time", "outside_hours"):
                v(f"{reason} with an in-session resolved time")

        # counts
        c_lang[c["lang_mix"]] += 1
        c_act[act] += 1
        c_cat[c["category"]] += 1
        if reason:
            c_rea[reason] += 1
        if c["reference_datetime"] != clinic["default_reference_datetime"]:
            refs[c["reference_datetime"]] += 1
        n_tf += c["tool_failure"]
        n_adv += c["category"] == "adversarial"
        if c["category"] in ("weekday_match", "pain_not_red_flag", "spelling_variant",
                             "self_correction") or (c["category"] == "asr_noise" and act == "book"):
            weird_neg += 1

    print(f"file: {args.path}   cases: {len(cases)}")
    for title, cnt in (("lang_mix", c_lang), ("action", c_act), ("reason", c_rea), ("category", c_cat)):
        print(f"\n{title}:")
        for k, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {k:20s} {n}")
    print(f"\nnon-default reference_datetime cases: {sum(refs.values())}")
    print(f"tool_failure true: {n_tf}   adversarial: {n_adv}   valid-but-weird negatives: {weird_neg}")

    if args.min_distribution:
        need = [("lang hinglish", c_lang["hinglish"], 28), ("lang kannada_english", c_lang["kannada_english"], 22),
                ("lang english", c_lang["english"], 8), ("lang devanagari_hindi", c_lang["devanagari_hindi"], 3),
                ("lang mixed_other", c_lang["mixed_other"], 3), ("book", c_act["book"], 22),
                ("ask_again", c_act["ask_again"], 22), ("escalate", c_act["escalate"], 7),
                ("handoff", c_act["handoff"], 3), ("write_failed", c_act["write_failed"], 5),
                ("weekday_mismatch", c_rea["weekday_mismatch"], 4), ("ambiguous_date", c_rea["ambiguous_date"], 2),
                ("past_time", c_rea["past_time"], 2), ("outside_hours", c_rea["outside_hours"], 3),
                ("closed_day", c_rea["closed_day"], 2), ("slot_taken", c_rea["slot_taken"], 3),
                ("missing_*", sum(c_rea[k] for k in c_rea if k.startswith("missing_")), 3),
                ("unintelligible", c_rea["unintelligible"], 2),
                ("pain_not_red_flag", c_cat["pain_not_red_flag"], 6), ("adversarial", n_adv, 4),
                ("weird negatives", weird_neg, 15), ("non-default refs", sum(refs.values()), 8),
                ("total", len(cases), 72)]
        for label, got, want in need:
            if got < want:
                viol.append(f"distribution: {label} = {got} < {want}")

    print(f"\nviolations: {len(viol)}")
    for m in viol:
        print("  VIOLATION", m)
    return 1 if viol else 0


if __name__ == "__main__":
    sys.exit(main())
