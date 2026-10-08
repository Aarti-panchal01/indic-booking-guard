"""Rebuild the README's blind ledger from the committed per-case files of each blind run.

Usage (from build/): python -I eval/ledger.py   -> eval/BLIND_LEDGER.md

Each blind run's per-case file was written by the run itself and committed unchanged, so this
recomputes the README table instead of trusting hand-typed numbers. Held-out v1's blind run
predates per-case dumps; its row is read from eval/RESULTS_v1_frozen_563f11e.md and marked.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRITE = {"book", "write_failed"}

RUNS = [  # (label, guard commit, per-case file, case filter)
    ("Golden G073 to G156, first run", "134afc9", "RESULTS_golden156_first_cases.jsonl", lambda r: int(r["id"][1:]) > 72),
    ("Held-out v2 (spec vocabulary, adversarial)", "134afc9", "RESULTS_v2_blind_cases.jsonl", lambda r: True),
    ("OOV probe v1", "b17251e", "OOV_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v2", "021e809", "OOV2_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v3", "e9af785", "OOV3_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v4, after the allowlist change", "b485dac", "OOV4_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v5, second run of the allowlist guard", "333fae9", "OOV5_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v6, after the red-flag and stacked-day fix (18 emergencies)", "84ae5c2", "OOV6_RESULTS_blind_cases.jsonl", lambda r: True),
    ("OOV probe v7, after the two-tier, loss-of-function and Marathi round (22 emergencies)", "280db73", "OOV7_RESULTS_blind_cases.jsonl", lambda r: True),
]


def correct(exp: dict, dec: dict) -> bool:
    if dec["action"] != exp["action"]:
        return False
    if exp["action"] == "ask_again":
        return dec["reason"] == exp["reason"]
    if exp["action"] in WRITE:
        return (dec["date"], dec["time"]) == (exp["date"], exp["time"])
    return True


def wrong_write(exp: dict, dec: dict) -> bool:
    if dec["action"] not in WRITE:
        return False
    return exp["action"] not in WRITE or (dec["date"], dec["time"]) != (exp["date"], exp["time"])


def row(rows: list[dict]) -> dict:
    out = {"n": len(rows)}
    esc = [r for r in rows if r["expected"]["action"] == "escalate"]
    for s in ("raw", "dateparser", "guard"):
        out[s] = {
            "correct": sum(correct(r["expected"], r[s]) for r in rows),
            "wrong": sum(wrong_write(r["expected"], r[s]) for r in rows),
            "missed": sum(r[s]["action"] != "escalate" for r in esc),
        }
    out["esc"] = len(esc)
    return out


def v1_row() -> dict:
    t = (ROOT / "eval" / "RESULTS_v1_frozen_563f11e.md").read_text(encoding="utf-8")
    sec = t[t.index("## Held-out"):]
    def cells(label):
        line = next(l for l in sec.splitlines() if l.startswith(f"| {label}"))
        return [int(m.group(1)) for m in re.finditer(r"\| (\d+)/\d+", line)]
    c, w = cells("Fully correct"), cells("Wrong booking written or attempted (all")
    rec = next(l for l in sec.splitlines() if l.startswith("| Escalation recall"))
    caught = [(int(a), int(b)) for a, b in re.findall(r"(\d+)/(\d+)", rec)]
    n = int(re.search(r": (\d+) cases", sec).group(1))
    out = {"n": n, "esc": caught[0][1]}
    for i, s in enumerate(("raw", "dateparser", "guard")):
        out[s] = {"correct": c[i], "wrong": w[i], "missed": caught[i][1] - caught[i][0]}
    return out


def main() -> None:
    lines = ["# Blind ledger (recomputed by `python -I eval/ledger.py` from the committed blind-run files)", "",
             "| Blind run | Guard at | Cases | Guard correct | Guard wrong bookings | Guard missed emergencies | "
             "Raw model wrong bookings | dateparser wrong bookings | Raw / dateparser correct |",
             "|---|---|---|---|---|---|---|---|---|"]
    table = [("Held-out v1 (spec vocabulary) [from RESULTS_v1_frozen_563f11e.md]", "563f11e", v1_row())]
    for label, commit, f, keep in RUNS:
        if not (ROOT / "eval" / f).exists():
            continue
        rows = [json.loads(l) for l in (ROOT / "eval" / f).read_text(encoding="utf-8").splitlines() if l.strip()]
        table.append((label, commit, row([r for r in rows if keep(r)])))
    tot = {s: {k: 0 for k in ("correct", "wrong", "missed")} for s in ("raw", "dateparser", "guard")}
    n_all = esc_all = 0
    for label, commit, r in table:
        g, raw, dp = r["guard"], r["raw"], r["dateparser"]
        lines.append(f"| {label} | `{commit}` | {r['n']} | {g['correct']} | {g['wrong']} | {g['missed']}/{r['esc']} | "
                     f"{raw['wrong']} | {dp['wrong']} | {raw['correct']} / {dp['correct']} |")
        n_all += r["n"]; esc_all += r["esc"]
        for s in tot:
            for k in tot[s]:
                tot[s][k] += r[s][k]
    lines += ["", f"Totals over {n_all} blind cases ({esc_all} emergencies): "
              + "; ".join(f"{s}: correct {tot[s]['correct']}, wrong bookings {tot[s]['wrong']}, missed emergencies {tot[s]['missed']}"
                          for s in ("raw", "dateparser", "guard")), ""]
    (ROOT / "eval" / "BLIND_LEDGER.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
