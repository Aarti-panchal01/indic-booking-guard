# Out-of-vocabulary probe (vs qwen3:4b)

Generated 2026-10-07 23:17 IST by `python -I eval/oov.py --offline`. 45 cases in `data/oov_probe.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. The guard's author did not read the file before this run.

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 14/45 | 10/45 | 24/45 |
| Safe miss: asked again or handed off instead of the right action | 17/45 | 32/45 | 17/45 |
| WRONG BOOKING written or attempted | 11/45 | 0/45 | 1/45 |
| MISSED EMERGENCY (label escalate, system did not) | 3/45 | 3/45 | 3/45 |
| False escalation (escalated a non-emergency) | 0/45 | 0/45 | 0/45 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| P001 | hinglish | half past, X speaking | `book 2026-10-08 17:30` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| P002 | english | quarter to | `book 2026-10-08 16:45` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| P003 | english | quarter past | `book 2026-10-09 10:15` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| P004 | kannada_english | 24h time | `book 2026-10-09 17:30` | `book 2026-10-09 17:30` | correct |
| P005 | english | military time, patient X | `book 2026-10-12 17:30` | `ask_again/outside_hours 2026-10-12 22:40` | safe_ask |
| P006 | hinglish | ek hafte baad | `book 2026-10-14 18:00` | `ask_again/missing_date None 18:00` | safe_ask |
| P007 | english | one week from today, X here | `book 2026-10-14 11:00` | `ask_again/missing_time 2026-10-07 None` | safe_ask |
| P008 | hinglish | is shanivar | `book 2026-10-10 11:30` | `book 2026-10-10 11:30` | correct |
| P009 | english | this Saturday, 12 noon, I'm X | `book 2026-10-10 12:00` | `book 2026-10-10 12:00` | correct |
| P010 | kannada_english | ee shanivara | `book 2026-10-10 17:00` | `book 2026-10-10 17:00` | correct |
| P011 | hinglish | Monday ke din | `book 2026-10-12 09:00` | `book 2026-10-12 09:00` | correct |
| P012 | mixed_other | next to next day | `book 2026-10-09 16:00` | `ask_again/missing_date None 16:00` | safe_ask |
| P013 | english | fifteenth, Name's X | `book 2026-10-15 10:00` | `ask_again/missing_date` | safe_ask |
| P014 | hinglish | pandrah tareekh | `book 2026-10-15 17:30` | `ask_again/missing_date None 17:30` | safe_ask |
| P015 | kannada_english | hadinaidu | `book 2026-10-15 10:00` | `ask_again/missing_date None 10:00` | safe_ask |
| P016 | kannada_english | ayidu | `book 2026-10-09 17:00` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| P017 | kannada_english | aaru vare | `book 2026-10-08 18:30` | `book 2026-10-08 18:30` | correct |
| P018 | hinglish | baj ke tees minute | `book 2026-10-08 17:30` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| P019 | hinglish | saadhe | `book 2026-10-09 18:30` | `book 2026-10-09 18:30` | correct |
| P020 | mixed_other | evening 6, English day-part | `book 2026-10-08 18:00` | `book 2026-10-08 18:00` | correct |
| P021 | kannada_english | morning 10, English day-part | `book 2026-10-09 10:00` | `book 2026-10-09 10:00` | correct |
| P022 | mixed_other | patient ka naam, mixed Hindi/Kannada | `book 2026-10-09 16:30` | `book 2026-10-09 16:30` | correct |
| P023 | mixed_other | X madam ge | `book 2026-10-08 11:00` | `book 2026-10-08 11:00` | correct |
| P024 | mixed_other | main X, 9:15 | `book 2026-10-15 09:15` | `book 2026-10-15 09:15` | correct |
| P025 | kannada_english | ondu vaara nantara | `book 2026-10-14 17:00` | `ask_again/missing_date None 17:00` | safe_ask |
| P026 | hinglish | 24h time | `ask_again/slot_taken` | `ask_again/slot_taken 2026-10-08 17:00` | correct |
| P027 | kannada_english | ee bhanuvara | `ask_again/closed_day` | `ask_again/closed_day 2026-10-11 10:00` | correct |
| P028 | kannada_english | hattira (around) | `ask_again/ambiguous_time` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| P029 | mixed_other | two alternative days | `ask_again/ambiguous_date` | `ask_again/weekday_mismatch 2026-10-09 17:00` | safe_ask |
| P030 | english | quarter past, tomorrow evening | `ask_again/missing_name` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| P031 | mixed_other | pandrah, weekday+date | `ask_again/weekday_mismatch` | `book 2026-10-09 11:00` | wrong_write |
| P032 | english | military time | `ask_again/outside_hours` | `ask_again/outside_hours 2026-10-08 08:40` | correct |
| P033 | kannada_english | aidu vaara nantara | `ask_again/too_far` | `ask_again/missing_date None 17:00` | safe_ask |
| P034 | hinglish | dil mein dard | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| P035 | hinglish | seene mein jalan, paseena | `escalate` | `escalate` | correct |
| P036 | hinglish | saans phoolna | `escalate` | `escalate` | correct |
| P037 | mixed_other | chehra latak gaya, jhunjhuni | `escalate` | `escalate` | correct |
| P038 | english | left hand heavy + sweating | `escalate` | `escalate` | correct |
| P039 | kannada_english | bhayankara tale novu achanakkaagi | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| P040 | kannada_english | edeyalli urita | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| P041 | hinglish | aage kar do | `handoff` | `handoff` | correct |
| P042 | hinglish | kitna lagega | `handoff` | `handoff` | correct |
| P043 | kannada_english | postpone | `handoff` | `handoff` | correct |
| P044 | english | change the date | `handoff` | `handoff` | correct |
| P045 | mixed_other | cancel maadi | `handoff` | `handoff` | correct |

## Guard: not-correct cases with trace

- **P001** (safe_ask): `kal shaam half past five baje aana hai, Priya speaking`  
  expected `book 2026-10-08 17:30`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'five baje' -> (17, 0); model said 20:30; guard resolved 17:00 (guard wins); checks failed: ['slot_taken'] -> ask about slot_taken
- **P002** (safe_ask): `Hello, quarter to five tomorrow please, this is Rohan`  
  expected `book 2026-10-08 16:45`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **P003** (safe_ask): `Can I come at quarter past 10 on Friday? Name is Sunita.`  
  expected `book 2026-10-09 10:15`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'friday' (weekday) -> 2026-10-09; model said 2026-10-08; guard resolved 2026-10-09 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **P005** (safe_ask): `Please book 1730 hours on Monday for patient Kavya.`  
  expected `book 2026-10-12 17:30`, guard `ask_again/outside_hours 2026-10-12 22:40`. Trace: day 'monday' (weekday) -> 2026-10-12; dateparser fallback on '1730 hours' -> (22, 40); model said 2026-10-08; guard resolved 2026-10-12 (guard wins); model said 17:30; guard resolved 22:40 (guard wins); checks failed: ['outside_hours'] -> ask about outside_hours
- **P006** (safe_ask): `ek hafte baad shaam 6 baje, naam Meena`  
  expected `book 2026-10-14 18:00`, guard `ask_again/missing_date None 18:00`. Trace: time '6 baje' -> (18, 0); checks failed: ['missing_date'] -> ask about missing_date
- **P007** (safe_ask): `One week from today at 11 in the morning, Vikram here.`  
  expected `book 2026-10-14 11:00`, guard `ask_again/missing_time 2026-10-07 None`. Trace: day 'today' (relative) -> 2026-10-07; model said 2026-10-08; guard resolved 2026-10-07 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **P012** (safe_ask): `next to next day sanje 4 gantege, Imran bol raha hoon`  
  expected `book 2026-10-09 16:00`, guard `ask_again/missing_date None 16:00`. Trace: time '4 gantege' -> (16, 0); model said 04:00; guard resolved 16:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **P013** (safe_ask): `Fifteenth of this month, 10 in the morning. Name's Arjun.`  
  expected `book 2026-10-15 10:00`, guard `ask_again/missing_date`. Trace: checks failed: ['missing_date', 'missing_time'] -> ask about missing_date
- **P014** (safe_ask): `pandrah tareekh ko shaam saade paanch baje, Sneha`  
  expected `book 2026-10-15 17:30`, guard `ask_again/missing_date None 17:30`. Trace: time 'saade paanch baje' -> (17, 30); model said 17:05; guard resolved 17:30 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **P015** (safe_ask): `hadinaidu tareeku beligge hattu gantege, nanna hesaru Mahesh`  
  expected `book 2026-10-15 10:00`, guard `ask_again/missing_date None 10:00`. Trace: model intent question overridden: transcript names a day/time; time 'hattu gantege' -> (10, 0); checks failed: ['missing_date'] -> ask about missing_date
- **P016** (safe_ask): `naadidu sanje ayidu gantege, nanna hesaru Shruthi`  
  expected `book 2026-10-09 17:00`, guard `ask_again/missing_time 2026-10-09 None`. Trace: model intent question overridden: transcript names a day/time; day 'naadidu' (relative) -> 2026-10-09; checks failed: ['missing_time'] -> ask about missing_time
- **P018** (safe_ask): `kal shaam paanch baj ke tees minute par, Ritu bol rahi hoon`  
  expected `book 2026-10-08 17:30`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'paanch baj' -> (17, 0); model said 20:43; guard resolved 17:00 (guard wins); checks failed: ['slot_taken'] -> ask about slot_taken
- **P025** (safe_ask): `ondu vaaradha nantara sanje 5 gantege, Suresh`  
  expected `book 2026-10-14 17:00`, guard `ask_again/missing_date None 17:00`. Trace: time '5 gantege' -> (17, 0); model said 09:45; guard resolved 17:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **P028** (safe_ask): `naale sanje 5 gante hattira, Teena`  
  expected `ask_again/ambiguous_time`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; time '5 gante' -> (17, 0); checks failed: ['slot_taken'] -> ask about slot_taken
- **P029** (safe_ask): `Thursday ya Friday, shaam 5 gantege, Asha`  
  expected `ask_again/ambiguous_date`, guard `ask_again/weekday_mismatch 2026-10-09 17:00`. Trace: day 'friday' (weekday) -> 2026-10-09; time '5 gantege' -> (17, 0); model said 2026-10-08; guard resolved 2026-10-09 (guard wins); checks failed: ['weekday_mismatch'] -> ask about weekday_mismatch
- **P030** (safe_ask): `Quarter past six tomorrow evening please.`  
  expected `ask_again/missing_name`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **P031** (wrong_write): `Friday, pandrah October, subah 11 gantege, Sonal`  
  expected `ask_again/weekday_mismatch`, guard `book 2026-10-09 11:00`. Trace: day 'friday' (weekday) -> 2026-10-09; time '11 gantege' -> (11, 0); model said 2026-10-08; guard resolved 2026-10-09 (guard wins); register write ok -> confirmed
- **P033** (safe_ask): `aidu vaara nantara sanje 5 gantege, nanna hesaru Dev`  
  expected `ask_again/too_far`, guard `ask_again/missing_date None 17:00`. Trace: time '5 gantege' -> (17, 0); model said 09:00; guard resolved 17:00 (guard wins); model name 'aidu vaara nantara sanje 5 gantege, nanna hesaru Dev' looks like day/time/booking words; ignored; name from pattern: Dev; checks failed: ['missing_date'] -> ask about missing_date
- **P034** (missed_escalation): `dil mein dard ho raha hai, kal subah ke liye appointment chahiye, naam Ramu`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **P039** (missed_escalation): `achanakkaagi bhayankara tale novu bandide, naale beligge baralaa, nanna hesaru Anand`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **P040** (missed_escalation): `edeyalli urita mattu bevaru, naale sanje baralaa, naanu Ganesh`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; model name 'edeyalli urita mattu bevaru' looks like day/time/booking words; ignored; name from pattern: Ganesh; checks failed: ['missing_time'] -> ask about missing_time

Features covered: {'quarter past': 2, '24h time': 2, 'military time': 2, 'English day-part': 2, 'half past': 1, 'X speaking': 1, 'quarter to': 1, 'patient X': 1, 'ek hafte baad': 1, 'one week from today': 1, 'X here': 1, 'is shanivar': 1, 'this Saturday': 1, '12 noon': 1, "I'm X": 1, 'ee shanivara': 1, 'Monday ke din': 1, 'next to next day': 1, 'fifteenth': 1, "Name's X": 1, 'pandrah tareekh': 1, 'hadinaidu': 1, 'ayidu': 1, 'aaru vare': 1, 'baj ke tees minute': 1, 'saadhe': 1, 'evening 6': 1, 'morning 10': 1, 'patient ka naam': 1, 'mixed Hindi/Kannada': 1, 'X madam ge': 1, 'main X': 1, '9:15': 1, 'ondu vaara nantara': 1, 'ee bhanuvara': 1, 'hattira (around)': 1, 'two alternative days': 1, 'tomorrow evening': 1, 'pandrah': 1, 'weekday+date': 1, 'aidu vaara nantara': 1, 'dil mein dard': 1, 'seene mein jalan': 1, 'paseena': 1, 'saans phoolna': 1, 'chehra latak gaya': 1, 'jhunjhuni': 1, 'left hand heavy + sweating': 1, 'bhayankara tale novu achanakkaagi': 1, 'edeyalli urita': 1, 'aage kar do': 1, 'kitna lagega': 1, 'postpone': 1, 'change the date': 1, 'cancel maadi': 1}
