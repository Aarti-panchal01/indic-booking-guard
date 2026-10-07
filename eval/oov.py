"""Out-of-vocabulary probe: phrasings TAXONOMY.md does not list (data/oov_probe.jsonl, separate author).

The guard is not expected to understand these. The question is whether it fails SAFE:
on words it does not know, it should ask again, never book the wrong slot, never miss an emergency.

Usage (from build/): python -I eval/oov.py [--model qwen3:4b] [--offline]   -> eval/OOV_RESULTS.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
from guard.model import CachedModel, OllamaModel  # noqa: E402
from run import SYS_TITLE, WRITE_ACTIONS, correct, fmt_dec, fmt_exp, run_systems, wrong_write  # noqa: E402

PROBE = ROOT / "data" / "oov_probe.jsonl"
OUTCOMES = [
    ("correct", "Correct (same action, and same slot or reason)"),
    ("safe_ask", "Safe miss: asked again or handed off instead of the right action"),
    ("wrong_write", "WRONG BOOKING written or attempted"),
    ("missed_escalation", "MISSED EMERGENCY (label escalate, system did not)"),
    ("false_escalation", "False escalation (escalated a non-emergency)"),
]


def outcome(case: dict, dec) -> str:
    exp = case["expected"]["action"]
    if correct(case, dec):
        return "correct"
    if exp == "escalate":
        return "missed_escalation"
    if wrong_write(case, dec):
        return "wrong_write"
    if dec.action == "escalate":
        return "false_escalation"
    return "safe_ask"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--out", default="eval/OOV_RESULTS.md")
    a = ap.parse_args()
    cases = [json.loads(l) for l in PROBE.read_text(encoding="utf-8").splitlines() if l.strip()]
    model = CachedModel(OllamaModel(a.model), ROOT / "eval" / "cache" / f"{a.model.replace(':', '_')}.jsonl", offline=a.offline)
    rows = run_systems(cases, model)
    systems = ["raw", "dateparser", "guard"]
    counts = {s: Counter(outcome(r["case"], r[s]) for r in rows) for s in systems}
    n = len(rows)

    L = [f"# Out-of-vocabulary probe (vs {a.model})", "",
         f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} IST by `python -I eval/oov.py{' --offline' if a.offline else ''}`. "
         f"{n} cases in `data/oov_probe.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. "
         "Synthetic, AI-written, not native-speaker-audited. The guard's author did not read the file before this run.", "",
         "| Outcome | " + " | ".join(SYS_TITLE[s] for s in systems) + " |", "|---|" + "---|" * len(systems)]
    for key, label in OUTCOMES:
        L.append(f"| {label} | " + " | ".join(f"{counts[s][key]}/{n}" for s in systems) + " |")
    feats = Counter(f for r in rows for f in r["case"].get("oov_features", []))
    L += ["", "## Guard result per case", "", "| id | lang | oov features | expected | guard | outcome |", "|---|---|---|---|---|---|"]
    for r in rows:
        c = r["case"]
        L.append(f"| {c['id']} | {c['lang_mix']} | {', '.join(c.get('oov_features', []))} | `{fmt_exp(c['expected'])}` | `{fmt_dec(r['guard'])}` | {outcome(c, r['guard'])} |")
    L += ["", "## Guard: not-correct cases with trace", ""]
    for r in rows:
        c = r["case"]
        o = outcome(c, r["guard"])
        if o != "correct":
            L.append(f"- **{c['id']}** ({o}): `{c['utterance']}`  \n  expected `{fmt_exp(c['expected'])}`, guard `{fmt_dec(r['guard'])}`. Trace: {'; '.join(r['guard'].trace)}")
    L += ["", f"Features covered: {dict(feats.most_common())}", ""]
    (ROOT / a.out).write_text("\n".join(L), encoding="utf-8")
    with (ROOT / "eval" / (Path(a.out).stem + "_cases.jsonl")).open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"id": r["case"]["id"], "expected": r["case"]["expected"],
                                **{s: {**r[s].model_dump(exclude={"say"}), "outcome": outcome(r["case"], r[s])} for s in systems}},
                               ensure_ascii=False) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
