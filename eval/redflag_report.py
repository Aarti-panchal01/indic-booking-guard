"""Per-set guard numbers for the red-flag work: emergencies caught, false escalations, wrong bookings, correct.

Prints a table only; writes no result files. Uses the cached qwen3:4b outputs (offline), so it needs no Ollama.
Refuses the v7 blind probe: that file is run once, by eval/oov.py --blind, after the fix is frozen.

Usage (from build/): python -I eval/redflag_report.py [--model qwen3:4b]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
from guard.model import CachedModel, cache_path, model_from_spec  # noqa: E402
from run import correct, run_systems, wrong_write  # noqa: E402

SETS = [
    ("golden (156)", "data/golden.jsonl"),
    ("held-out v1", "data/held_out.jsonl"),
    ("held-out v2", "data/held_out_v2.jsonl"),
    ("OOV v1", "data/oov_probe.jsonl"),
    ("OOV v2", "data/oov_probe_v2.jsonl"),
    ("OOV v3", "data/oov_probe_v3.jsonl"),
    ("OOV v4", "data/oov_probe_v4.jsonl"),
    ("OOV v5", "data/oov_probe_v5.jsonl"),
    ("OOV v6", "data/oov_probe_v6.jsonl"),
]
BLIND_UNTIL_FROZEN = {"data/oov_probe_v7.jsonl"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:4b")
    a = ap.parse_args()
    assert not BLIND_UNTIL_FROZEN & {p for _, p in SETS}
    model = CachedModel(model_from_spec(a.model), cache_path(ROOT, a.model), offline=True)
    print("| Set | Cases | Emergencies caught (urgent + human check) | False escalations (urgent + human check) | Wrong bookings | Guard correct |")
    print("|---|---|---|---|---|---|")
    tot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for name, path in SETS:
        cases = [json.loads(l) for l in (ROOT / path).read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = run_systems(cases, model)
        n = len(rows)
        emerg = [r for r in rows if r["case"]["expected"]["action"] == "escalate"]
        hc = lambda d: getattr(d, "tier", None) == "human_check"  # noqa: E731
        caught = sum(r["guard"].action == "escalate" for r in emerg)
        caught_hc = sum(r["guard"].action == "escalate" and hc(r["guard"]) for r in emerg)
        fa = [r for r in rows if r["guard"].action == "escalate" and r["case"]["expected"]["action"] != "escalate"]
        fa_hc = sum(hc(r["guard"]) for r in fa)
        wrong = sum(wrong_write(r["case"], r["guard"]) for r in rows)
        ok = sum(correct(r["case"], r["guard"]) for r in rows)
        print(f"| {name} | {n} | {caught}/{len(emerg)} ({caught - caught_hc} + {caught_hc}) | {len(fa)} ({len(fa) - fa_hc} + {fa_hc}) | {wrong} | {ok}/{n} |")
        for i, v in enumerate((n, caught, len(emerg), len(fa), wrong, ok, caught_hc, fa_hc)):
            tot[i] += v
    print(f"| **all** | {tot[0]} | {tot[1]}/{tot[2]} ({tot[1] - tot[6]} + {tot[6]}) | {tot[3]} ({tot[3] - tot[7]} + {tot[7]}) | {tot[4]} | {tot[5]}/{tot[0]} |")


if __name__ == "__main__":
    main()
