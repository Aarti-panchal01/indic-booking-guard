"""Call the real local model once per case and cache the result (eval/cache/<model>.jsonl).

Usage: python -I eval/collect.py [model] [file ...]   (run from build/)
Re-running only calls the model for cases not in the cache.
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from guard.model import CachedModel, cache_path, model_from_spec  # noqa: E402

model = sys.argv[1] if len(sys.argv) > 1 else "qwen3:4b"
files = sys.argv[2:] or ["data/golden.jsonl", "data/held_out.jsonl"]
cm = CachedModel(model_from_spec(model), cache_path(ROOT, model))
for f in files:
    cases = [json.loads(l) for l in (ROOT / f).read_text(encoding="utf-8").splitlines() if l.strip()]
    for i, c in enumerate(cases):
        t0 = time.perf_counter()
        r = cm.extract(c["utterance"], datetime.fromisoformat(c["reference_datetime"]))
        print(f"{f} {i + 1}/{len(cases)} {c['id']} {time.perf_counter() - t0:.1f}s err={r.error}", flush=True)
