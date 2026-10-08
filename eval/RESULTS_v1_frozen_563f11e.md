# Eval results (vs qwen3:4b (4B, Q4))

Generated 2026-10-07 22:28 IST by `python -I eval/run.py --offline`.
All cases are synthetic, AI-written, not native-speaker-audited. Every number is vs qwen3:4b (4B, Q4); nothing here is a claim about production error rates.

Systems (all three share the same SQLite register tool, which rejects closed days, out-of-hours and taken slots):
- **Raw model + register**: book whatever date/time the model returns.
- **Model words + dateparser + register**: the community fix (LiveKit thread): the model's verbatim day/time words resolved by dateparser 1.4.3.
- **Model + guard**: red-flag list, Hinglish/Kannada-English normaliser on the caller's own words, weekday-vs-date check, past/far checks, confirmation gate. The model is used for intent and name only.

## Main golden set: 72 cases

model calls: 72, model latency p50 9.6 s, p90 10.4 s (recorded when the cache was filled); parse status: {'ok': 72}. Guard decide() incl. SQLite checks and write: p50 0.66 ms, max 28.16 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 15/72 (21%) | 13/72 (18%) | 71/72 (99%) |
| Wrong booking written or attempted (all cases) | 14/72 (19%) | 1/72 (1%) | 0/72 (0%) |
| Wrong booking written on cases that must NOT book | 6/38 (16%) | 1/38 (3%) | 0/38 (0%) |
| Date+time exact on cases that should book | 5/34 (15%) | 4/34 (12%) | 33/34 (97%) |
| False block (should book, did not) | 21/34 (62%) | 30/34 (88%) | 1/34 (3%) |
|   of which asked again | 16/34 (47%) | 25/34 (74%) | 1/34 (3%) |
| Escalation recall | 4/8 (50%) | 4/8 (50%) | 8/8 (100%) |
| Escalation precision | 4/4 (100%) | 4/4 (100%) | 8/8 (100%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| devanagari_hindi | 3 | 2 / 0 | 1 / 0 | 2 / 0 |
| english | 11 | 6 / 3 | 7 / 1 | 11 / 0 |
| hinglish | 32 | 4 / 8 | 3 / 0 | 32 / 0 |
| kannada_english | 23 | 3 / 3 | 2 / 0 | 23 / 0 |
| mixed_other | 3 | 0 / 0 | 0 / 0 | 3 / 0 |


## Held-out slice (separate author, never read by the guard's author before this run): 24 cases

model calls: 24, model latency p50 10.6 s, p90 11.2 s (recorded when the cache was filled); parse status: {'ok': 24}. Guard decide() incl. SQLite checks and write: p50 0.64 ms, max 0.84 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 4/24 (17%) | 1/24 (4%) | 23/24 (96%) |
| Wrong booking written or attempted (all cases) | 8/24 (33%) | 1/24 (4%) | 1/24 (4%) |
| Wrong booking written on cases that must NOT book | 5/13 (38%) | 1/13 (8%) | 1/13 (8%) |
| Date+time exact on cases that should book | 3/11 (27%) | 1/11 (9%) | 11/11 (100%) |
| False block (should book, did not) | 5/11 (45%) | 10/11 (91%) | 0/11 (0%) |
|   of which asked again | 5/11 (45%) | 10/11 (91%) | 0/11 (0%) |
| Escalation recall | 0/3 (0%) | 0/3 (0%) | 3/3 (100%) |
| Escalation precision | n/a | n/a | 3/3 (100%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| english | 2 | 1 / 1 | 1 / 1 | 2 / 0 |
| hinglish | 10 | 3 / 0 | 0 / 0 | 10 / 0 |
| kannada_english | 10 | 0 / 6 | 0 / 0 | 10 / 0 |
| mixed_other | 2 | 0 / 1 | 0 / 0 | 1 / 1 |


## Guard failures (every case the guard got wrong)

- **G058** (main, devanagari_hindi, devanagari): `कल शाम साढ़े पांच बजे अपॉइंटमेंट चाहिए, मेरा नाम सुनील है`  
  expected `book 2026-10-08 17:30`, guard `ask_again/missing_time 2026-10-08 None`. Trace: dateparser fallback on 'कल' -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **H024** (held_out, mixed_other, missing_field): `parso sanje paune aaru ge book maadi please, appointment chahiye`  
  expected `ask_again/missing_name`, guard `book 2026-10-09 17:45`. Trace: day 'parso' (relative) -> 2026-10-09; time 'paune aaru' -> (17, 45); model said 2026-10-07; guard resolved 2026-10-09 (guard wins); model said null; guard resolved 17:45 (guard wins); register write ok -> confirmed
