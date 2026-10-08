# Eval results (vs groq:qwen/qwen3.8-27b)

Generated 2026-10-08 14:32 IST by `python -I eval/run.py --offline --model groq:qwen/qwen3.8-27b`.
All cases are synthetic, AI-written, not native-speaker-audited. Every number is vs groq:qwen/qwen3.8-27b; nothing here is a claim about production error rates.

Systems (all three share the same SQLite register tool, which rejects closed days, out-of-hours and taken slots):
- **Raw model + register**: book whatever date/time the model returns.
- **Model words + dateparser + register**: the community fix (LiveKit thread): the model's verbatim day/time words resolved by dateparser 1.4.3.
- **Model + guard**: red-flag list, Hinglish/Kannada-English normaliser on the caller's own words, weekday-vs-date check, past/far checks, confirmation gate. The model is used for intent and name only.

## Held-out v1 (separate author; blind result was 23/24 with 1 wrong write, see RESULTS_v1_frozen_563f11e.md; numbers below are AFTER the H024 fix, so not blind): 24 cases

model calls: 24, model latency p50 4.3 s, p90 5.4 s (recorded when the cache was filled); parse status: {'ok': 24}. Guard decide() incl. SQLite checks and write: p50 2.00 ms, max 17.55 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 12/24 (50%) | 2/24 (8%) | 23/24 (96%) |
| Wrong booking written or attempted (all cases) | 8/24 (33%) | 1/24 (4%) | 0/24 (0%) |
| Wrong booking written on cases that must NOT book | 5/13 (38%) | 1/13 (8%) | 0/13 (0%) |
| Date+time exact on cases that should book | 6/11 (55%) | 0/11 (0%) | 10/11 (91%) |
| False block (should book, did not) | 2/11 (18%) | 11/11 (100%) | 1/11 (9%) |
|   of which asked again | 2/11 (18%) | 11/11 (100%) | 1/11 (9%) |
| Escalation recall | 2/3 (67%) | 2/3 (67%) | 3/3 (100%) |
| Escalation precision | 2/2 (100%) | 2/2 (100%) | 3/3 (100%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| english | 2 | 1 / 1 | 0 / 1 | 1 / 0 |
| hinglish | 10 | 6 / 4 | 1 / 0 | 10 / 0 |
| kannada_english | 10 | 3 / 3 | 0 / 0 | 10 / 0 |
| mixed_other | 2 | 2 / 0 | 1 / 0 | 2 / 0 |


## Guard failures (every case the guard got wrong)

- **H003** (held_out, english, english_control): `Hello, this is Meera. Could I come in Thursday, around 11:30 am?`  
  expected `book 2026-10-08 11:30`, guard `ask_again/ambiguous_time 2026-10-08 11:30`. Trace: day 'thursday' (weekday) -> 2026-10-08; time '11:30 am' -> (11, 30); partial parse: time modifier(s) ['around', 'around'] not understood -> ambiguous_time; checks failed: ['ambiguous_time'] -> ask about ambiguous_time
