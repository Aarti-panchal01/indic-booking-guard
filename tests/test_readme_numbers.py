"""The README's blind ledger must match what eval/ledger.py recomputes from the committed blind-run files.

Added after a hand-typed ledger cell was found wrong (OOV v2 wrong bookings 5 vs 6).
"""
import re
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent


def _rows(text: str, start: str) -> list[list[str]]:
    block = text[text.index(start):]
    out = []
    for line in block.splitlines()[2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip().replace("*", "") for c in line.strip("|").split("|")]
        out.append([re.sub(r"\s*\[.*\]$", "", c) for c in cells])
    return out


def test_readme_blind_ledger_matches_recomputed():
    subprocess.run([sys.executable, "-I", str(BUILD / "eval" / "ledger.py")], check=True, capture_output=True)
    header = "| Blind run | Guard at |"
    computed = _rows((BUILD / "eval" / "BLIND_LEDGER.md").read_text(encoding="utf-8"), header)
    readme = _rows((BUILD / "README.md").read_text(encoding="utf-8"), header)
    assert len(computed) == len(readme) == 7
    for c, r in zip(computed, readme):
        assert c[1:] == r[1:], (c, r)   # every cell except the label
