# Eval results (vs qwen3:4b (4B, Q4))

Generated 2026-10-07 23:10 IST by `python -I eval/run.py --offline`.
All cases are synthetic, AI-written, not native-speaker-audited. Every number is vs qwen3:4b (4B, Q4); nothing here is a claim about production error rates.

Systems (all three share the same SQLite register tool, which rejects closed days, out-of-hours and taken slots):
- **Raw model + register**: book whatever date/time the model returns.
- **Model words + dateparser + register**: the community fix (LiveKit thread): the model's verbatim day/time words resolved by dateparser 1.4.3.
- **Model + guard**: red-flag list, Hinglish/Kannada-English normaliser on the caller's own words, weekday-vs-date check, past/far checks, confirmation gate. The model is used for intent and name only.

## Main golden set: 156 cases

model calls: 156, model latency p50 9.9 s, p90 10.8 s (recorded when the cache was filled); parse status: {'ok': 156}. Guard decide() incl. SQLite checks and write: p50 0.60 ms, max 32.91 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 31/156 (20%) | 28/156 (18%) | 152/156 (97%) |
| Wrong booking written or attempted (all cases) | 40/156 (26%) | 4/156 (3%) | 1/156 (1%) |
| Wrong booking written on cases that must NOT book | 19/86 (22%) | 3/86 (3%) | 1/86 (1%) |
| Date+time exact on cases that should book | 8/70 (11%) | 8/70 (11%) | 69/70 (99%) |
| False block (should book, did not) | 41/70 (59%) | 61/70 (87%) | 1/70 (1%) |
|   of which asked again | 27/70 (39%) | 47/70 (67%) | 1/70 (1%) |
| Escalation recall | 7/18 (39%) | 7/18 (39%) | 17/18 (94%) |
| Escalation precision | 7/7 (100%) | 7/7 (100%) | 17/17 (100%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| devanagari_hindi | 3 | 2 / 0 | 1 / 0 | 2 / 0 |
| english | 21 | 10 / 9 | 14 / 4 | 21 / 0 |
| hinglish | 65 | 12 / 18 | 7 / 0 | 63 / 0 |
| kannada_english | 51 | 5 / 10 | 4 / 0 | 51 / 0 |
| mixed_other | 16 | 2 / 3 | 2 / 0 | 15 / 1 |


## Guard failures (every case the guard got wrong)

- **G058** (main, devanagari_hindi, devanagari): `कल शाम साढ़े पांच बजे अपॉइंटमेंट चाहिए, मेरा नाम सुनील है`  
  expected `book 2026-10-08 17:30`, guard `ask_again/missing_time 2026-10-08 None`. Trace: dateparser fallback on 'कल' -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **G112** (main, mixed_other, missing_field): `namaste, hesaru Padma, sanje aaru baje chahiye, 2 hafte se dard ide`  
  expected `ask_again/missing_date`, guard `book 2026-10-14 18:00`. Trace: time 'aaru baje' -> (18, 0); dateparser fallback on 'Wednesday' -> 2026-10-14; model said 2026-10-07; guard resolved 2026-10-14 (guard wins); model said 08:00; guard resolved 18:00 (guard wins); register write ok -> confirmed
- **G130** (main, hinglish, slot_taken): `last Monday seedhiyon se gir gaye, tab se kandha dukh raha hai, budhvar ko shaam saade chaar baje chahiye, naam Ayesha`  
  expected `ask_again/slot_taken`, guard `ask_again/weekday_mismatch 2026-10-14 16:30`. Trace: day 'budhvar' (weekday) -> 2026-10-14; time 'saade chaar baje' -> (16, 30); model said 2026-10-07; guard resolved 2026-10-14 (guard wins); model said 16:00; guard resolved 16:30 (guard wins); checks failed: ['slot_taken', 'weekday_mismatch'] -> ask about weekday_mismatch
- **G140** (main, hinglish, red_flag): `doctor sahab subah se left kandhe mein dard hai aur nausea ho raha hai, aaj hi dikha sakte hain kya`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-07 None`. Trace: model intent question overridden: transcript names a day/time; day 'aaj' (relative) -> 2026-10-07; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
