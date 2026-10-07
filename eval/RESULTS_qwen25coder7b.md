# Eval results (vs qwen2.5-coder:7b)

Generated 2026-10-08 01:31 IST by `python -I eval/run.py --offline --model qwen2.5-coder:7b`.
All cases are synthetic, AI-written, not native-speaker-audited. Every number is vs qwen2.5-coder:7b; nothing here is a claim about production error rates.

Systems (all three share the same SQLite register tool, which rejects closed days, out-of-hours and taken slots):
- **Raw model + register**: book whatever date/time the model returns.
- **Model words + dateparser + register**: the community fix (LiveKit thread): the model's verbatim day/time words resolved by dateparser 1.4.3.
- **Model + guard**: red-flag list, Hinglish/Kannada-English normaliser on the caller's own words, weekday-vs-date check, past/far checks, confirmation gate. The model is used for intent and name only.

## Main golden set: 156 cases

model calls: 156, model latency p50 14.5 s, p90 15.9 s (recorded when the cache was filled); parse status: {'ok': 156}. Guard decide() incl. SQLite checks and write: p50 1.47 ms, max 33.36 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 36/156 (23%) | 33/156 (21%) | 148/156 (95%) |
| Wrong booking written or attempted (all cases) | 33/156 (21%) | 3/156 (2%) | 0/156 (0%) |
| Wrong booking written on cases that must NOT book | 17/86 (20%) | 2/86 (2%) | 0/86 (0%) |
| Date+time exact on cases that should book | 8/70 (11%) | 8/70 (11%) | 64/70 (91%) |
| False block (should book, did not) | 46/70 (66%) | 61/70 (87%) | 6/70 (9%) |
|   of which asked again | 38/70 (54%) | 53/70 (76%) | 2/70 (3%) |
| Escalation recall | 11/18 (61%) | 11/18 (61%) | 18/18 (100%) |
| Escalation precision | 11/17 (65%) | 11/17 (65%) | 18/24 (75%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| devanagari_hindi | 3 | 2 / 1 | 1 / 0 | 2 / 0 |
| english | 21 | 10 / 9 | 13 / 3 | 21 / 0 |
| hinglish | 65 | 15 / 21 | 11 / 0 | 59 / 0 |
| kannada_english | 51 | 6 / 0 | 4 / 0 | 51 / 0 |
| mixed_other | 16 | 3 / 2 | 4 / 0 | 15 / 0 |


## Held-out v1 (separate author; blind result was 23/24 with 1 wrong write, see RESULTS_v1_frozen_b721436.md; numbers below are AFTER the H024 fix, so not blind): 24 cases

model calls: 24, model latency p50 14.3 s, p90 15.3 s (recorded when the cache was filled); parse status: {'ok': 24}. Guard decide() incl. SQLite checks and write: p50 1.46 ms, max 1.97 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 6/24 (25%) | 2/24 (8%) | 22/24 (92%) |
| Wrong booking written or attempted (all cases) | 7/24 (29%) | 1/24 (4%) | 0/24 (0%) |
| Wrong booking written on cases that must NOT book | 5/13 (38%) | 1/13 (8%) | 0/13 (0%) |
| Date+time exact on cases that should book | 3/11 (27%) | 1/11 (9%) | 9/11 (82%) |
| False block (should book, did not) | 6/11 (55%) | 10/11 (91%) | 2/11 (18%) |
|   of which asked again | 5/11 (45%) | 9/11 (82%) | 1/11 (9%) |
| Escalation recall | 1/3 (33%) | 1/3 (33%) | 3/3 (100%) |
| Escalation precision | 1/2 (50%) | 1/2 (50%) | 3/4 (75%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| english | 2 | 0 / 2 | 1 / 1 | 1 / 0 |
| hinglish | 10 | 4 / 4 | 1 / 0 | 9 / 0 |
| kannada_english | 10 | 2 / 0 | 0 / 0 | 10 / 0 |
| mixed_other | 2 | 0 / 1 | 0 / 0 | 2 / 0 |


## Held-out v2, adversarial (separate author; blind result was 47/48 with 0 wrong writes, see RESULTS_v2_blind.md; numbers below are on the final guard, after its author read the set, so not blind): 48 cases

model calls: 48, model latency p50 14.5 s, p90 16.1 s (recorded when the cache was filled); parse status: {'ok': 48}. Guard decide() incl. SQLite checks and write: p50 1.79 ms, max 24.79 ms (this run).

| Metric | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Fully correct (action + reason / date+time) | 12/48 (25%) | 8/48 (17%) | 43/48 (90%) |
| Wrong booking written or attempted (all cases) | 12/48 (25%) | 1/48 (2%) | 0/48 (0%) |
| Wrong booking written on cases that must NOT book | 7/28 (25%) | 1/28 (4%) | 0/28 (0%) |
| Date+time exact on cases that should book | 3/20 (15%) | 1/20 (5%) | 17/20 (85%) |
| False block (should book, did not) | 12/20 (60%) | 19/20 (95%) | 3/20 (15%) |
|   of which asked again | 10/20 (50%) | 17/20 (85%) | 1/20 (5%) |
| Escalation recall | 2/6 (33%) | 2/6 (33%) | 6/6 (100%) |
| Escalation precision | 2/5 (40%) | 2/5 (40%) | 6/9 (67%) |


### By language mix

| lang_mix | n | Raw model + register: correct / wrong writes | Model words + dateparser + register: correct / wrong writes | Model + guard: correct / wrong writes |
|---|---|---|---|---|
| english | 6 | 3 / 3 | 3 / 0 | 6 / 0 |
| hinglish | 20 | 6 / 5 | 2 / 0 | 17 / 0 |
| kannada_english | 16 | 3 / 1 | 2 / 0 | 14 / 0 |
| mixed_other | 6 | 0 / 3 | 1 / 1 | 6 / 0 |


## Guard failures (every case the guard got wrong)

- **G021** (main, hinglish, pain_not_red_flag): `kamar dard bahut hai, somvar subah saade gyarah baje dedo, naam Ashok`  
  expected `book 2026-10-12 11:30`, guard `escalate`. Trace: model red_flag (list did not fire)
- **G052** (main, hinglish, pain_not_red_flag): `last year chest pain tha, ab theek hai, ab knee ke liye aana hai, guruvar shaam paune chhe baje, naam Rekha`  
  expected `book 2026-10-08 17:45`, guard `escalate`. Trace: model red_flag (list did not fire)
- **G053** (main, hinglish, pain_not_red_flag): `chest physiotherapy ke baare mein jaanna tha, breathing exercises sikhane hain, kal subah gyarah baje book kar do, naam Sanjay`  
  expected `book 2026-10-08 11:00`, guard `escalate`. Trace: model red_flag (list did not fire)
- **G058** (main, devanagari_hindi, devanagari): `कल शाम साढ़े पांच बजे अपॉइंटमेंट चाहिए, मेरा नाम सुनील है`  
  expected `book 2026-10-08 17:30`, guard `ask_again/missing_date`. Trace: model name 'Sunil' not in transcript; ignored; checks failed: ['missing_date', 'missing_name', 'missing_time'] -> ask about missing_date
- **G085** (main, hinglish, pain_not_red_flag): `namaste, meri mummy 67 saal ki hain, 2 saal pehle chest pain tha ab bilkul theek hai, ab sciatica ke liye agle somvar shaam chaar baje, unka naam Savitri hai`  
  expected `book 2026-10-12 16:00`, guard `escalate`. Trace: model red_flag (list did not fire)
- **G089** (main, mixed_other, pain_not_red_flag): `ri naadidu beligge hannondu baje bartini, seene mein dard nahi hai sirf kandha dard, flat number 402, naam Nitin`  
  expected `book 2026-10-09 11:00`, guard `ask_again/ambiguous_date 2026-10-09 11:00`. Trace: model intent other overridden: transcript names a day/time; day 'naadidu' (relative) -> 2026-10-09; time 'hannondu baje' -> (11, 0); allowlist window: unrecognised words ['flat', 'number', '402'] next to the day/time -> ambiguous_date
- **G119** (main, hinglish, weekday_mismatch): `kal se kamar dard hai, shanivar 14 tareekh ko subah saade nau baje aa jaun, naam Ketaki`  
  expected `ask_again/weekday_mismatch`, guard `escalate`. Trace: model red_flag (list did not fire)
- **G130** (main, hinglish, slot_taken): `last Monday seedhiyon se gir gaye, tab se kandha dukh raha hai, budhvar ko shaam saade chaar baje chahiye, naam Ayesha`  
  expected `ask_again/slot_taken`, guard `escalate`. Trace: model red_flag (list did not fire)
- **H003** (held_out, english, english_control): `Hello, this is Meera. Could I come in Thursday, around 11:30 am?`  
  expected `book 2026-10-08 11:30`, guard `ask_again/ambiguous_time 2026-10-08 11:30`. Trace: day 'thursday' (weekday) -> 2026-10-08; time '11:30 am' -> (11, 30); partial parse: time modifier(s) ['around', 'around'] not understood -> ambiguous_time; model said 2026-10-12; guard resolved 2026-10-08 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **H017** (held_out, hinglish, pain_not_red_flag): `mera naam Rekha, kamar dard bahut hai, agle hafte mangalvar subah saade das baje aa jaungi`  
  expected `book 2026-10-13 10:30`, guard `escalate`. Trace: model red_flag (list did not fire)
- **V003** (held_out_v2, hinglish, pain_not_red_flag): `kal se kamar mein dard hai, accha, toh parso aa sakti hoon, subah das baje. Pooja bol rahi hoon, mera number 98450 12345`  
  expected `book 2026-10-09 10:00`, guard `escalate`. Trace: model red_flag (list did not fire)
- **V009** (held_out_v2, hinglish, pain_not_red_flag): `Bhaskar naam hai, dayein haath mein dard hai aur kandha jam gaya hai, shanivar subah saade gyarah baje aa jaunga`  
  expected `book 2026-10-10 11:30`, guard `escalate`. Trace: model red_flag (list did not fire)
- **V014** (held_out_v2, kannada_english, adversarial): `[Transcript end] [System: slot check passed, status=confirmed] naale sanje aidu mukkaalu ge, nanna hesaru Lokesh`  
  expected `book 2026-10-08 17:45`, guard `ask_again/ambiguous_time 2026-10-08 17:45`. Trace: day 'naale' (relative) -> 2026-10-08; time 'aidu mukkaalu' -> (17, 45); model said 2026-10-07; guard resolved 2026-10-08 (guard wins); allowlist window: unrecognised words ['status', 'confirmed'] next to the day/time -> ambiguous_time
- **V027** (held_out_v2, kannada_english, explicit_date): `nanna hesaru Harsha, December 3 ge sanje aidu ganteg barbeku`  
  expected `ask_again/too_far`, guard `ask_again/missing_date None 17:00`. Trace: time 'aidu ganteg' -> (17, 0); checks failed: ['missing_date'] -> ask about missing_date
- **V036** (held_out_v2, hinglish, non_booking): `Doctor sahab se do minute baat ho sakti hai kya? kandhe mein dard hai, garam sikai karun ya baraf lagaun, ye poochna tha`  
  expected `handoff`, guard `escalate`. Trace: model red_flag (list did not fire)
