"""Evaluate raw model vs dateparser vs guard on the golden set and the held-out slice.

Usage (from build/):
  python -I eval/run.py                      # qwen3:4b from cache (calls Ollama on a miss), writes eval/RESULTS.md
  python -I eval/run.py --offline            # cache only, no Ollama (regenerates RESULTS.md anywhere)
  python -I eval/run.py --model mock         # MOCK model (intent=book, nothing else): deterministic layer alone
  python -I eval/run.py --split main --dev   # dev loop: main set only, print guard failures, no RESULTS.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from guard.baselines import dateparser_system, raw_model_system  # noqa: E402
from guard.guard import Guard  # noqa: E402
from guard.model import CachedModel, MockModel, OllamaModel  # noqa: E402
from guard.register import Register  # noqa: E402

FILES = {"main": "data/golden.jsonl", "held_out": "data/held_out.jsonl", "held_out_v2": "data/held_out_v2.jsonl"}
SPLIT_TITLE = {
    "main": "Main golden set",
    "held_out": "Held-out v1 (separate author; blind result was 23/24 with 1 wrong write, see RESULTS_v1_frozen_b721436.md; numbers below are AFTER the H024 fix, so not blind)",
    "held_out_v2": "Held-out v2, adversarial (separate author, written after the guard was frozen; the guard's author never read it before this run)",
}
WRITE_ACTIONS = {"book", "write_failed"}


def load(split: str) -> list[dict]:
    rows = [json.loads(l) for l in (ROOT / FILES[split]).read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        r["split"] = split
    return rows


def correct(case: dict, dec) -> bool:
    exp = case["expected"]
    if dec.action != exp["action"]:
        return False
    if exp["action"] == "ask_again":
        return dec.reason == exp["reason"]
    if exp["action"] in WRITE_ACTIONS:
        return dec.date == exp["date"] and dec.time == exp["time"]
    return True


def wrong_write(case: dict, dec) -> bool:
    """The system wrote (or tried to write) a booking the label does not allow, or the wrong slot."""
    exp = case["expected"]
    if dec.action not in WRITE_ACTIONS:
        return False
    if exp["action"] not in WRITE_ACTIONS:
        return True
    return (dec.date, dec.time) != (exp["date"], exp["time"])


def run_systems(cases: list[dict], model) -> list[dict]:
    out = []
    for c in cases:
        ref = datetime.fromisoformat(c["reference_datetime"])
        mr = model.extract(c["utterance"], ref)
        row = {"case": c, "model": mr}
        for sysname, fn in (("raw", raw_model_system), ("dateparser", dateparser_system)):
            reg = Register(fail_writes=c["tool_failure"])
            row[sysname] = fn(c["utterance"], ref, mr, reg)
        g = Guard(Register(fail_writes=c["tool_failure"]))
        t0 = time.perf_counter()
        row["guard"] = g.decide(c["utterance"], ref, mr)
        row["guard_ms"] = (time.perf_counter() - t0) * 1000
        out.append(row)
    return out


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "n/a"


def metrics(rows: list[dict], sysname: str) -> dict:
    m: dict = {}
    n = len(rows)
    m["fully_correct"] = (sum(correct(r["case"], r[sysname]) for r in rows), n)
    m["wrong_write"] = (sum(wrong_write(r["case"], r[sysname]) for r in rows), n)
    book = [r for r in rows if r["case"]["expected"]["action"] in WRITE_ACTIONS]
    m["datetime_exact_on_book"] = (sum(r[sysname].action in WRITE_ACTIONS and (r[sysname].date, r[sysname].time) ==
                                       (r["case"]["expected"]["date"], r["case"]["expected"]["time"]) for r in book), len(book))
    m["false_block"] = (sum(r[sysname].action not in WRITE_ACTIONS for r in book), len(book))
    m["ask_again_on_book"] = (sum(r[sysname].action == "ask_again" for r in book), len(book))
    neg = [r for r in rows if r["case"]["expected"]["action"] not in WRITE_ACTIONS]
    m["wrong_write_on_nonbook"] = (sum(wrong_write(r["case"], r[sysname]) for r in neg), len(neg))
    esc_true = [r for r in rows if r["case"]["expected"]["action"] == "escalate"]
    esc_pred = [r for r in rows if r[sysname].action == "escalate"]
    tp = sum(r["case"]["expected"]["action"] == "escalate" for r in esc_pred)
    m["esc_recall"] = (tp, len(esc_true))
    m["esc_precision"] = (tp, len(esc_pred))
    tf = [r for r in rows if r["case"]["expected"]["action"] == "write_failed"]
    m["confirmed_on_write_failure"] = (sum(r[sysname].confirmed for r in tf), len(tf))
    return m


METRIC_LABELS = [
    ("fully_correct", "Fully correct (action + reason / date+time)", "higher"),
    ("wrong_write", "Wrong booking written or attempted (all cases)", "lower"),
    ("wrong_write_on_nonbook", "Wrong booking written on cases that must NOT book", "lower"),
    ("datetime_exact_on_book", "Date+time exact on cases that should book", "higher"),
    ("false_block", "False block (should book, did not)", "lower"),
    ("ask_again_on_book", "  of which asked again", "info"),
    ("esc_recall", "Escalation recall", "higher"),
    ("esc_precision", "Escalation precision", "higher"),
]


def table(rows: list[dict], systems: list[str]) -> str:
    ms = {s: metrics(rows, s) for s in systems}
    head = "| Metric | " + " | ".join(SYS_TITLE[s] for s in systems) + " |\n|---|" + "---|" * len(systems) + "\n"
    body = ""
    for key, label, _ in METRIC_LABELS:
        body += f"| {label} | " + " | ".join(pct(*ms[s][key]) for s in systems) + " |\n"
    return head + body


SYS_TITLE = {"raw": "Raw model + register", "dateparser": "Model words + dateparser + register", "guard": "Model + guard"}


def by_lang(rows: list[dict], systems: list[str]) -> str:
    groups = defaultdict(list)
    for r in rows:
        groups[r["case"]["lang_mix"]].append(r)
    out = "| lang_mix | n | " + " | ".join(f"{SYS_TITLE[s]}: correct / wrong writes" for s in systems) + " |\n|---|---|" + "---|" * len(systems) + "\n"
    for lang in sorted(groups):
        g = groups[lang]
        cells = []
        for s in systems:
            m = metrics(g, s)
            cells.append(f"{m['fully_correct'][0]} / {m['wrong_write'][0]}")
        out += f"| {lang} | {len(g)} | " + " | ".join(cells) + " |\n"
    return out


def fmt_dec(d) -> str:
    s = d.action
    if d.reason:
        s += f"/{d.reason}"
    if d.date or d.time:
        s += f" {d.date} {d.time}"
    return s


def fmt_exp(e: dict) -> str:
    s = e["action"]
    if e.get("reason"):
        s += f"/{e['reason']}"
    if e["action"] in WRITE_ACTIONS:
        s += f" {e['date']} {e['time']}"
    return s


def failures(rows: list[dict], sysname: str) -> list[dict]:
    return [r for r in rows if not correct(r["case"], r[sysname])]


def model_stats(rows: list[dict]) -> str:
    lat = sorted(r["model"].latency_s for r in rows if r["model"].latency_s)
    errs = Counter((r["model"].error or "ok").split(":")[0] for r in rows)
    if not lat:
        return f"model errors: {dict(errs)}"
    p50 = lat[len(lat) // 2]
    p90 = lat[int(len(lat) * 0.9) - 1]
    g = sorted(r["guard_ms"] for r in rows)
    return (f"model calls: {len(rows)}, model latency p50 {p50:.1f} s, p90 {p90:.1f} s (recorded when the cache was filled); "
            f"parse status: {dict(errs)}. Guard decide() incl. SQLite checks and write: p50 {g[len(g) // 2]:.2f} ms, max {g[-1]:.2f} ms (this run).")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--split", choices=["main", "held_out", "held_out_v2", "both", "all"], default="all")
    ap.add_argument("--dev", action="store_true", help="print guard failures on the chosen split; do not write RESULTS.md")
    ap.add_argument("--out", default="eval/RESULTS.md")
    a = ap.parse_args()

    if a.model == "mock":
        model = MockModel()
    else:
        model = CachedModel(OllamaModel(a.model), ROOT / "eval" / "cache" / f"{a.model.replace(':', '_')}.jsonl", offline=a.offline)
    if a.split == "all":
        splits = [s for s in FILES if (ROOT / FILES[s]).exists()]
    else:
        splits = ["main", "held_out"] if a.split == "both" else [a.split]
    rows = {s: run_systems(load(s), model) for s in splits}
    systems = ["raw", "dateparser", "guard"]

    if a.dev:
        for s in splits:
            print(f"== {s} ({len(rows[s])} cases), model={model.name}")
            print(table(rows[s], systems))
            for r in failures(rows[s], "guard"):
                c = r["case"]
                print(f"- {c['id']} [{c['lang_mix']}/{c['category']}] {c['utterance']!r}\n    expected {fmt_exp(c['expected'])} | guard {fmt_dec(r['guard'])}"
                      f" | model {r['model'].extraction.model_dump(exclude={'date_words', 'time_words'}) if r['model'].extraction else r['model'].error}\n    trace {r['guard'].trace}")
        return
    write_results(rows, systems, model, a)


def write_results(rows: dict, systems: list[str], model, a) -> None:
    label = "vs qwen3:4b (4B, Q4)" if a.model == "qwen3:4b" else f"vs {a.model}"
    if a.model == "mock":
        label = "MOCK model (intent=book, no name/date/time): deterministic layer alone"
    L = [f"# Eval results ({label})", "",
         f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} IST by `python -I eval/run.py{' --offline' if a.offline else ''}{'' if a.model == 'qwen3:4b' else ' --model ' + a.model}`.",
         "All cases are synthetic, AI-written, not native-speaker-audited. Every number is "
         f"{label}; nothing here is a claim about production error rates.", "",
         "Systems (all three share the same SQLite register tool, which rejects closed days, out-of-hours and taken slots):",
         "- **Raw model + register**: book whatever date/time the model returns.",
         "- **Model words + dateparser + register**: the community fix (LiveKit thread): the model's verbatim day/time words resolved by dateparser 1.4.3.",
         "- **Model + guard**: red-flag list, Hinglish/Kannada-English normaliser on the caller's own words, weekday-vs-date check, past/far checks, confirmation gate. The model is used for intent and name only.", ""]
    for s, rs in rows.items():
        title = SPLIT_TITLE[s]
        L += [f"## {title}: {len(rs)} cases", "", model_stats(rs), "", table(rs, systems), "", "### By language mix", "", by_lang(rs, systems), ""]
    L += ["## Guard failures (every case the guard got wrong)", ""]
    for s, rs in rows.items():
        for r in failures(rs, "guard"):
            c = r["case"]
            L.append(f"- **{c['id']}** ({s}, {c['lang_mix']}, {c['category']}): `{c['utterance']}`  \n  expected `{fmt_exp(c['expected'])}`, guard `{fmt_dec(r['guard'])}`. Trace: {'; '.join(r['guard'].trace)}")
    L.append("")
    out = ROOT / a.out
    out.write_text("\n".join(L), encoding="utf-8")
    dump = ROOT / "eval" / (Path(a.out).stem + "_cases.jsonl")
    with dump.open("w", encoding="utf-8") as f:
        for s, rs in rows.items():
            for r in rs:
                f.write(json.dumps({"id": r["case"]["id"], "split": s, "expected": r["case"]["expected"],
                                    **{k: r[k].model_dump(exclude={"say"}) for k in systems}}, ensure_ascii=False) + "\n")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
