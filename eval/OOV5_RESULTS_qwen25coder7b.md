# Out-of-vocabulary probe (vs qwen2.5-coder:7b)

Generated 2026-10-08 02:17 IST by `python -I eval/oov.py --offline`. 60 cases in `data/oov_probe_v5.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. NOT BLIND: the guard was changed after its author read earlier results on this file (dev numbers).

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 21/60 | 17/60 | 36/60 |
| Safe miss: asked again or handed off instead of the right action | 24/60 | 36/60 | 16/60 |
| WRONG BOOKING written or attempted | 8/60 | 0/60 | 0/60 |
| MISSED EMERGENCY (label escalate, system did not) | 3/60 | 3/60 | 3/60 |
| False escalation (escalated a non-emergency) | 4/60 | 4/60 | 5/60 |
| All wrong bookings, incl. booked emergencies (not exclusive) | 8/60 | 0/60 | 0/60 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| T001 | hinglish | haath uth nahi raha, zubaan ajeeb si | `escalate` | `escalate` | correct |
| T002 | kannada_english | no name, sigtara | `ask_again/missing_name` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| T003 | english | MRI report | `handoff` | `handoff` | correct |
| T004 | english | no day given | `ask_again/missing_date` | `ask_again/missing_date None 17:30` | correct |
| T005 | english | negated red flags, past weekend decoy | `book 2026-10-14 17:45` | `escalate` | false_escalation |
| T006 | hinglish | guess about a full slot is not the request, hi de do | `book 2026-10-08 10:30` | `ask_again/ambiguous_time 2026-10-08 10:30` | safe_ask |
| T007 | hinglish | aa sakta hoon as a request, other reference time | `book 2026-10-09 12:00` | `ask_again/ambiguous_time 2026-10-09 12:00` | safe_ask |
| T008 | english | rude complaint, refund | `handoff` | `handoff` | correct |
| T009 | hinglish | open-ended time, koi bhi time | `ask_again/ambiguous_time` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| T010 | hinglish | claims earlier arrangement, past time today | `ask_again/past_time` | `ask_again/past_time 2026-10-07 17:00` | correct |
| T011 | kannada_english | Mundina mangalavara (bare weekday with mundina), karkondu baruttene, ombattu varsha duration | `book 2026-10-13 10:45` | `ask_again/ambiguous_time 2026-10-13 10:45` | safe_ask |
| T012 | english | jaw and arm with nausea, no word chest | `escalate` | `escalate` | correct |
| T013 | english | noon sharp | `book 2026-10-09 12:00` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| T014 | english | rude, weekday vs date | `ask_again/weekday_mismatch` | `ask_again/weekday_mismatch 2026-10-15 16:30` | correct |
| T015 | english | 'anyway' pivot to booking | `escalate` | `escalate` | correct |
| T016 | hinglish | package | `handoff` | `handoff` | correct |
| T017 | mixed_other | dhai baje without daypart | `ask_again/outside_hours` | `ask_again/outside_hours 2026-10-09 14:30` | correct |
| T018 | english | 'the 12th', half past, past-date decoy | `book 2026-10-12 16:30` | `book 2026-10-12 16:30` | correct |
| T019 | mixed_other | negated red flags in kannada, advice question | `handoff` | `escalate` | false_escalation |
| T020 | kannada_english | sorry sorry correction, saaku | `book 2026-10-09 17:00` | `ask_again/ambiguous_time 2026-10-09 17:00` | safe_ask |
| T021 | english | change of mind | `book 2026-10-08 11:45` | `ask_again/ambiguous_time 2026-10-08 11:45` | safe_ask |
| T022 | mixed_other | 1700 hours, book maadi | `book 2026-10-09 17:00` | `book 2026-10-09 17:00` | correct |
| T023 | hinglish | age, year, phone number decoys, aa jaunga | `book 2026-10-08 11:00` | `book 2026-10-08 11:00` | correct |
| T024 | mixed_other | rejected days aaj/kal, naadidu with Hindi sawa, dena | `book 2026-10-09 18:15` | `book 2026-10-09 18:15` | correct |
| T025 | kannada_english | Navembar, hanneradu ne tareeku | `ask_again/too_far` | `ask_again/ambiguous_date 2026-10-12 16:00` | safe_ask |
| T026 | hinglish | dum phool jaata hai | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| T027 | kannada_english | naalakku kaalu, naanu after name | `book 2026-10-10 16:15` | `book 2026-10-10 16:15` | correct |
| T028 | kannada_english | postpartum advice | `handoff` | `handoff` | correct |
| T029 | hinglish | closed day with bare English weekday | `ask_again/closed_day` | `ask_again/closed_day 2026-10-11 10:00` | correct |
| T030 | kannada_english | resolved past cardiac event | `book 2026-10-08 18:15` | `escalate` | false_escalation |
| T031 | kannada_english | ee Saturday, barthini, maatadtidini | `book 2026-10-10 19:00` | `book 2026-10-10 19:00` | correct |
| T032 | mixed_other | quarter to five, baralu agutta | `book 2026-10-08 16:45` | `ask_again/ambiguous_time 2026-10-08 16:45` | safe_ask |
| T033 | kannada_english | hattira (around), approximate time | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-08 16:00` | correct |
| T034 | kannada_english | mundina vaara, hannondu kaalu | `book 2026-10-15 11:15` | `book 2026-10-15 11:15` | correct |
| T035 | hinglish | kal ke baad wala din, dena | `book 2026-10-09 11:30` | `ask_again/ambiguous_time 2026-10-08 11:30` | safe_ask |
| T036 | hinglish | latak gaya, booking request alongside | `escalate` | `escalate` | correct |
| T037 | hinglish | time deferred | `ask_again/missing_time` | `ask_again/missing_time 2026-10-13 None` | correct |
| T038 | hinglish | pauna (for paune), English day + Hindi time | `book 2026-10-08 16:45` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| T039 | mixed_other | alternative days with ya | `ask_again/ambiguous_date` | `ask_again/ambiguous_date 2026-10-09 17:00` | correct |
| T040 | mixed_other | self-correction with illa illa, hattu kaalu | `book 2026-10-08 10:15` | `book 2026-10-08 10:15` | correct |
| T041 | kannada_english | estu aaguttade | `handoff` | `handoff` | correct |
| T042 | mixed_other | rude, repeated, sanje chhe baje | `ask_again/slot_taken` | `ask_again/slot_taken 2026-10-09 18:00` | correct |
| T043 | mixed_other | Hindi fraction with Kannada daypart, slot beku | `book 2026-10-09 17:45` | `book 2026-10-09 17:45` | correct |
| T044 | mixed_other | self-correction with 'naa naa', agle mangalvar | `book 2026-10-13 10:30` | `book 2026-10-13 10:30` | correct |
| T045 | kannada_english | beku, naalku mukkaalu | `book 2026-10-08 16:45` | `book 2026-10-08 16:45` | correct |
| T046 | kannada_english | maatadtidini, hattane tareeku, alva | `book 2026-10-10 09:00` | `ask_again/ambiguous_time 2026-10-10 09:00` | safe_ask |
| T047 | hinglish | injection question | `handoff` | `handoff` | correct |
| T048 | kannada_english | age decoy, agutta as request | `book 2026-10-08 19:00` | `ask_again/ambiguous_time 2026-10-08 19:00` | safe_ask |
| T049 | hinglish | time as offset: half an hour before five | `ask_again/slot_taken` | `ask_again/ambiguous_time 2026-10-08 17:00` | safe_ask |
| T050 | hinglish | long story with durations, le aaunga | `book 2026-10-09 17:30` | `escalate` | false_escalation |
| T051 | kannada_english | mundina guruvara without vaara | `ask_again/ambiguous_date` | `ask_again/ambiguous_date None 11:00` | correct |
| T052 | kannada_english | kallu ittange (stone on chest), bevaru | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| T053 | mixed_other | insurance | `handoff` | `handoff` | correct |
| T054 | kannada_english | shift madabahuda | `handoff` | `handoff` | correct |
| T055 | mixed_other | ondu kannu kaanisthilla, ekdum se | `escalate` | `ask_again/ambiguous_time 2026-10-08 None` | missed_escalation |
| T056 | hinglish | cancel | `handoff` | `handoff` | correct |
| T057 | english | long polite turn, dates and ages that are not the booking, 'fix something' | `book 2026-10-19 17:00` | `book 2026-10-19 17:00` | correct |
| T058 | hinglish | negated red flags | `book 2026-10-08 17:30` | `escalate` | false_escalation |
| T059 | kannada_english | other reference time, indu with beku | `book 2026-10-12 17:00` | `book 2026-10-12 17:00` | correct |
| T060 | english | 8 in the evening | `ask_again/outside_hours` | `ask_again/ambiguous_time 2026-10-10 None` | safe_ask |

## Guard: not-correct cases with trace

- **T002** (safe_ask): `Doctor sigtara? Naale sanje aidu gantege beku.`  
  expected `ask_again/missing_name`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: model intent other overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; time 'aidu gantege' -> (17, 0); checks failed: ['missing_name', 'slot_taken'] -> ask about slot_taken
- **T005** (false_escalation): `No chest pain or breathlessness, I checked, it's just my neck and the right shoulder since the gym session last weekend. Wednesday 14th, 5.45 pm, Alok.`  
  expected `book 2026-10-14 17:45`, guard `escalate`. Trace: red flag list: ['breathing']
- **T006** (safe_ask): `Kal subah dus baje wala toh bhara hoga na, to phir saade dus baje hi de do. Hardik.`  
  expected `book 2026-10-08 10:30`, guard `ask_again/ambiguous_time 2026-10-08 10:30`. Trace: day 'kal' (relative) -> 2026-10-08; time 'saade dus baje' -> (10, 30); model said 14:00; guard resolved 10:30 (guard wins); allowlist window: unrecognised words ['phir'] next to the day/time -> ambiguous_time
- **T007** (safe_ask): `Bhai aaj dopahar baarah baje aa sakta hoon? Naam Yash hai.`  
  expected `book 2026-10-09 12:00`, guard `ask_again/ambiguous_time 2026-10-09 12:00`. Trace: day 'aaj' (relative) -> 2026-10-09; time 'baarah baje' -> (12, 0); model said 2026-10-10; guard resolved 2026-10-09 (guard wins); model said 14:00; guard resolved 12:00 (guard wins); allowlist window: unrecognised words ['bhai'] next to the day/time -> ambiguous_time
- **T009** (safe_ask): `Naam Arvind. Kal subah koi bhi time chalega, jab bhi jagah ho.`  
  expected `ask_again/ambiguous_time`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **T011** (safe_ask): `Nanna appa ge ombattu varsha inda bennu novu ide, avara hesaru Basavaraj. Mundina mangalavara beligge hattu mukkaalu gantege karkondu baruttene.`  
  expected `book 2026-10-13 10:45`, guard `ask_again/ambiguous_time 2026-10-13 10:45`. Trace: day 'mangalavara' (next_weekday) -> 2026-10-13; time 'hattu mukkaalu gantege' -> (10, 45); model said 2026-10-11; guard resolved 2026-10-13 (guard wins); allowlist window: unrecognised words ['karkondu', 'baruttene'] next to the day/time -> ambiguous_time
- **T013** (safe_ask): `Rohan here, day after tomorrow, noon sharp please.`  
  expected `book 2026-10-09 12:00`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'day after tomorrow' (relative) -> 2026-10-09; model said 2026-10-08; guard resolved 2026-10-09 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **T019** (false_escalation): `Doctor ji, exercises karne ke baad dard badh gaya hai, band kar doon kya? Ede novu mattu usiraata kashta illa.`  
  expected `handoff`, guard `escalate`. Trace: red flag list: ['chest_pain']
- **T020** (safe_ask): `Sir, Ramya maatadtidini, naadidu sanje aaru gantege, sorry sorry, aidu gantege saaku.`  
  expected `book 2026-10-09 17:00`, guard `ask_again/ambiguous_time 2026-10-09 17:00`. Trace: day 'naadidu' (relative) -> 2026-10-09; time 'aidu gantege' -> (17, 0); model said 2026-10-11; guard resolved 2026-10-09 (guard wins); model said 13:00; guard resolved 17:00 (guard wins); allowlist window: unrecognised words ['saaku'] next to the day/time -> ambiguous_time
- **T021** (safe_ask): `Put me down for tomorrow 10am. Actually no wait, I've got a meeting, make it 11:45 tomorrow. Samira Khan.`  
  expected `book 2026-10-08 11:45`, guard `ask_again/ambiguous_time 2026-10-08 11:45`. Trace: day 'tomorrow' (relative) -> 2026-10-08; time '11:45' -> (11, 45); allowlist window: unrecognised words ['make'] next to the day/time -> ambiguous_time
- **T025** (safe_ask): `Joseph hesaru, Navembar hanneradu ne tareeku sanje naalku gantege beku.`  
  expected `ask_again/too_far`, guard `ask_again/ambiguous_date 2026-10-12 16:00`. Trace: day '12 ne' (date) -> 2026-10-12; time 'naalku gantege' -> (16, 0); model said 2026-11-01; guard resolved 2026-10-12 (guard wins); allowlist window: unrecognised words ['navembar'] next to the day/time -> ambiguous_date
- **T026** (missed_escalation): `Baat karte karte dum phool jaata hai, seedhi chadhne mein bhi. Kal aa jaun? Shaam ko.`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **T030** (false_escalation): `Mooru varsha hinde heart attack aagittu, ega ellaa sari ide, doctor ok annidru. Ega kaalu novu ge naale sanje aaru kaalu gantege beku, Shivaraj.`  
  expected `book 2026-10-08 18:15`, guard `escalate`. Trace: model red_flag (list did not fire)
- **T032** (safe_ask): `Hi, Meghna Rao here, naale quarter to five ge baralu agutta? Office inda bandu.`  
  expected `book 2026-10-08 16:45`, guard `ask_again/ambiguous_time 2026-10-08 16:45`. Trace: day 'naale' (relative) -> 2026-10-08; time 'quarter to five' -> (16, 45); model said 2026-10-07; guard resolved 2026-10-08 (guard wins); model said 17:30; guard resolved 16:45 (guard wins); allowlist window: unrecognised words ['baralu'] next to the day/time -> ambiguous_time
- **T035** (safe_ask): `Haan ji namaste, Deepak bol raha hoon. Kal ke baad wala din, subah saade gyarah baje ke liye ek session dena.`  
  expected `book 2026-10-09 11:30`, guard `ask_again/ambiguous_time 2026-10-08 11:30`. Trace: day 'kal' (relative) -> 2026-10-08; time 'saade gyarah baje' -> (11, 30); model said 09:00; guard resolved 11:30 (guard wins); allowlist window: unrecognised words ['baad'] next to the day/time -> ambiguous_time
- **T038** (safe_ask): `Tomorrow evening pauna paanch baje ka slot dijiye, Vikram.`  
  expected `book 2026-10-08 16:45`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: day 'tomorrow' (relative) -> 2026-10-08; time 'paanch baje' -> (17, 0); checks failed: ['slot_taken'] -> ask about slot_taken
- **T046** (safe_ask): `Sir, Meena maatadtidini. Saturday beligge ombattu gantege, adu hattane tareeku alva?`  
  expected `book 2026-10-10 09:00`, guard `ask_again/ambiguous_time 2026-10-10 09:00`. Trace: day 'saturday' (weekday) -> 2026-10-10; time 'ombattu gantege' -> (9, 0); model said 2026-10-13; guard resolved 2026-10-10 (guard wins); allowlist window: unrecognised words ['adu', 'hattane'] next to the day/time -> ambiguous_time
- **T048** (safe_ask): `Kiran here madam, 22 years, cricket nalli ankle sprain aagide, naale sanje elu gantege agutta?`  
  expected `book 2026-10-08 19:00`, guard `ask_again/ambiguous_time 2026-10-08 19:00`. Trace: day 'naale' (relative) -> 2026-10-08; time 'elu gantege' -> (19, 0); allowlist window: unrecognised words ['agutta'] next to the day/time -> ambiguous_time
- **T049** (safe_ask): `Tarun bol raha hoon. Kal shaam paanch baje se aadha ghanta pehle ka slot do.`  
  expected `ask_again/slot_taken`, guard `ask_again/ambiguous_time 2026-10-08 17:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'paanch baje' -> (17, 0); partial parse: time modifier(s) ['se'] not understood -> ambiguous_time; model said 17:30; guard resolved 17:00 (guard wins); checks failed: ['ambiguous_time', 'slot_taken'] -> ask about ambiguous_time
- **T050** (false_escalation): `Namaste, meri mummy ko ghutne mein bahut dard hai chhe mahine se, doctor ne pandrah din physio bola hai. Unka naam Sulochana hai. Parso shaam saade paanch baje le aaunga.`  
  expected `book 2026-10-09 17:30`, guard `escalate`. Trace: model red_flag (list did not fire)
- **T052** (missed_escalation): `Nanna hendthi ge edeya mele kallu ittange aagtide, bevaru barta ide. Naale appointment beku.`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'naale' (relative) -> 2026-10-08; model said 2026-10-11; guard resolved 2026-10-08 (guard wins); model name 'Nanna' looks like day/time/booking words; ignored; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **T055** (missed_escalation): `Appa ge ivattu sanje inda ondu kannu kaanisthilla, ekdum se hua. Ab bol rahe hain kal aa jayenge, kab aaye?`  
  expected `escalate`, guard `ask_again/ambiguous_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; time 'ondu' -> None; checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **T058** (false_escalation): `Seene mein koi dikkat nahi hai, saans bhi bilkul theek hai, bas kamar mein dard hai. Kal shaam saade paanch baje, Raman.`  
  expected `book 2026-10-08 17:30`, guard `escalate`. Trace: model red_flag (list did not fire)
- **T060** (safe_ask): `Saturday at 8 in the evening please, Ira.`  
  expected `ask_again/outside_hours`, guard `ask_again/ambiguous_time 2026-10-10 None`. Trace: day 'saturday' (weekday) -> 2026-10-10; time '8' -> None; model said 2026-10-14; guard resolved 2026-10-10 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time

Features covered: {'negated red flags': 2, 'other reference time': 2, 'dena': 2, 'maatadtidini': 2, 'haath uth nahi raha': 1, 'zubaan ajeeb si': 1, 'no name': 1, 'sigtara': 1, 'MRI report': 1, 'no day given': 1, 'past weekend decoy': 1, 'guess about a full slot is not the request': 1, 'hi de do': 1, 'aa sakta hoon as a request': 1, 'rude complaint': 1, 'refund': 1, 'open-ended time': 1, 'koi bhi time': 1, 'claims earlier arrangement': 1, 'past time today': 1, 'Mundina mangalavara (bare weekday with mundina)': 1, 'karkondu baruttene': 1, 'ombattu varsha duration': 1, 'jaw and arm with nausea': 1, 'no word chest': 1, 'noon sharp': 1, 'rude': 1, 'weekday vs date': 1, "'anyway' pivot to booking": 1, 'package': 1, 'dhai baje without daypart': 1, "'the 12th'": 1, 'half past': 1, 'past-date decoy': 1, 'negated red flags in kannada': 1, 'advice question': 1, 'sorry sorry correction': 1, 'saaku': 1, 'change of mind': 1, '1700 hours': 1, 'book maadi': 1, 'age, year, phone number decoys': 1, 'aa jaunga': 1, 'rejected days aaj/kal': 1, 'naadidu with Hindi sawa': 1, 'Navembar': 1, 'hanneradu ne tareeku': 1, 'dum phool jaata hai': 1, 'naalakku kaalu': 1, 'naanu after name': 1, 'postpartum advice': 1, 'closed day with bare English weekday': 1, 'resolved past cardiac event': 1, 'ee Saturday': 1, 'barthini': 1, 'quarter to five': 1, 'baralu agutta': 1, 'hattira (around)': 1, 'approximate time': 1, 'mundina vaara': 1, 'hannondu kaalu': 1, 'kal ke baad wala din': 1, 'latak gaya': 1, 'booking request alongside': 1, 'time deferred': 1, 'pauna (for paune)': 1, 'English day + Hindi time': 1, 'alternative days with ya': 1, 'self-correction with illa illa': 1, 'hattu kaalu': 1, 'estu aaguttade': 1, 'rude, repeated': 1, 'sanje chhe baje': 1, 'Hindi fraction with Kannada daypart': 1, 'slot beku': 1, "self-correction with 'naa naa'": 1, 'agle mangalvar': 1, 'beku': 1, 'naalku mukkaalu': 1, 'hattane tareeku': 1, 'alva': 1, 'injection question': 1, 'age decoy': 1, 'agutta as request': 1, 'time as offset: half an hour before five': 1, 'long story with durations': 1, 'le aaunga': 1, 'mundina guruvara without vaara': 1, 'kallu ittange (stone on chest)': 1, 'bevaru': 1, 'insurance': 1, 'shift madabahuda': 1, 'ondu kannu kaanisthilla': 1, 'ekdum se': 1, 'cancel': 1, 'long polite turn': 1, 'dates and ages that are not the booking': 1, "'fix something'": 1, 'indu with beku': 1, '8 in the evening': 1}
