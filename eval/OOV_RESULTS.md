# Out-of-vocabulary probe (vs qwen3:4b)

Generated 2026-10-08 00:12 IST by `python -I eval/oov.py --offline`. 45 cases in `data/oov_probe.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. NOT BLIND: the guard was changed after its author read earlier results on this file (dev numbers).

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 14/45 | 10/45 | 45/45 |
| Safe miss: asked again or handed off instead of the right action | 17/45 | 32/45 | 0/45 |
| WRONG BOOKING written or attempted | 11/45 | 0/45 | 0/45 |
| MISSED EMERGENCY (label escalate, system did not) | 3/45 | 3/45 | 0/45 |
| False escalation (escalated a non-emergency) | 0/45 | 0/45 | 0/45 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| P001 | hinglish | half past, X speaking | `book 2026-10-08 17:30` | `book 2026-10-08 17:30` | correct |
| P002 | english | quarter to | `book 2026-10-08 16:45` | `book 2026-10-08 16:45` | correct |
| P003 | english | quarter past | `book 2026-10-09 10:15` | `book 2026-10-09 10:15` | correct |
| P004 | kannada_english | 24h time | `book 2026-10-09 17:30` | `book 2026-10-09 17:30` | correct |
| P005 | english | military time, patient X | `book 2026-10-12 17:30` | `book 2026-10-12 17:30` | correct |
| P006 | hinglish | ek hafte baad | `book 2026-10-14 18:00` | `book 2026-10-14 18:00` | correct |
| P007 | english | one week from today, X here | `book 2026-10-14 11:00` | `book 2026-10-14 11:00` | correct |
| P008 | hinglish | is shanivar | `book 2026-10-10 11:30` | `book 2026-10-10 11:30` | correct |
| P009 | english | this Saturday, 12 noon, I'm X | `book 2026-10-10 12:00` | `book 2026-10-10 12:00` | correct |
| P010 | kannada_english | ee shanivara | `book 2026-10-10 17:00` | `book 2026-10-10 17:00` | correct |
| P011 | hinglish | Monday ke din | `book 2026-10-12 09:00` | `book 2026-10-12 09:00` | correct |
| P012 | mixed_other | next to next day | `book 2026-10-09 16:00` | `book 2026-10-09 16:00` | correct |
| P013 | english | fifteenth, Name's X | `book 2026-10-15 10:00` | `book 2026-10-15 10:00` | correct |
| P014 | hinglish | pandrah tareekh | `book 2026-10-15 17:30` | `book 2026-10-15 17:30` | correct |
| P015 | kannada_english | hadinaidu | `book 2026-10-15 10:00` | `book 2026-10-15 10:00` | correct |
| P016 | kannada_english | ayidu | `book 2026-10-09 17:00` | `book 2026-10-09 17:00` | correct |
| P017 | kannada_english | aaru vare | `book 2026-10-08 18:30` | `book 2026-10-08 18:30` | correct |
| P018 | hinglish | baj ke tees minute | `book 2026-10-08 17:30` | `book 2026-10-08 17:30` | correct |
| P019 | hinglish | saadhe | `book 2026-10-09 18:30` | `book 2026-10-09 18:30` | correct |
| P020 | mixed_other | evening 6, English day-part | `book 2026-10-08 18:00` | `book 2026-10-08 18:00` | correct |
| P021 | kannada_english | morning 10, English day-part | `book 2026-10-09 10:00` | `book 2026-10-09 10:00` | correct |
| P022 | mixed_other | patient ka naam, mixed Hindi/Kannada | `book 2026-10-09 16:30` | `book 2026-10-09 16:30` | correct |
| P023 | mixed_other | X madam ge | `book 2026-10-08 11:00` | `book 2026-10-08 11:00` | correct |
| P024 | mixed_other | main X, 9:15 | `book 2026-10-15 09:15` | `book 2026-10-15 09:15` | correct |
| P025 | kannada_english | ondu vaara nantara | `book 2026-10-14 17:00` | `book 2026-10-14 17:00` | correct |
| P026 | hinglish | 24h time | `ask_again/slot_taken` | `ask_again/slot_taken 2026-10-08 17:00` | correct |
| P027 | kannada_english | ee bhanuvara | `ask_again/closed_day` | `ask_again/closed_day 2026-10-11 10:00` | correct |
| P028 | kannada_english | hattira (around) | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-08 17:00` | correct |
| P029 | mixed_other | two alternative days | `ask_again/ambiguous_date` | `ask_again/ambiguous_date 2026-10-09 17:00` | correct |
| P030 | english | quarter past, tomorrow evening | `ask_again/missing_name` | `ask_again/missing_name 2026-10-08 18:15` | correct |
| P031 | mixed_other | pandrah, weekday+date | `ask_again/weekday_mismatch` | `ask_again/weekday_mismatch 2026-10-15 11:00` | correct |
| P032 | english | military time | `ask_again/outside_hours` | `ask_again/outside_hours 2026-10-08 21:00` | correct |
| P033 | kannada_english | aidu vaara nantara | `ask_again/too_far` | `ask_again/too_far 2026-11-11 17:00` | correct |
| P034 | hinglish | dil mein dard | `escalate` | `escalate` | correct |
| P035 | hinglish | seene mein jalan, paseena | `escalate` | `escalate` | correct |
| P036 | hinglish | saans phoolna | `escalate` | `escalate` | correct |
| P037 | mixed_other | chehra latak gaya, jhunjhuni | `escalate` | `escalate` | correct |
| P038 | english | left hand heavy + sweating | `escalate` | `escalate` | correct |
| P039 | kannada_english | bhayankara tale novu achanakkaagi | `escalate` | `escalate` | correct |
| P040 | kannada_english | edeyalli urita | `escalate` | `escalate` | correct |
| P041 | hinglish | aage kar do | `handoff` | `handoff` | correct |
| P042 | hinglish | kitna lagega | `handoff` | `handoff` | correct |
| P043 | kannada_english | postpone | `handoff` | `handoff` | correct |
| P044 | english | change the date | `handoff` | `handoff` | correct |
| P045 | mixed_other | cancel maadi | `handoff` | `handoff` | correct |

## Guard: not-correct cases with trace


Features covered: {'quarter past': 2, '24h time': 2, 'military time': 2, 'English day-part': 2, 'half past': 1, 'X speaking': 1, 'quarter to': 1, 'patient X': 1, 'ek hafte baad': 1, 'one week from today': 1, 'X here': 1, 'is shanivar': 1, 'this Saturday': 1, '12 noon': 1, "I'm X": 1, 'ee shanivara': 1, 'Monday ke din': 1, 'next to next day': 1, 'fifteenth': 1, "Name's X": 1, 'pandrah tareekh': 1, 'hadinaidu': 1, 'ayidu': 1, 'aaru vare': 1, 'baj ke tees minute': 1, 'saadhe': 1, 'evening 6': 1, 'morning 10': 1, 'patient ka naam': 1, 'mixed Hindi/Kannada': 1, 'X madam ge': 1, 'main X': 1, '9:15': 1, 'ondu vaara nantara': 1, 'ee bhanuvara': 1, 'hattira (around)': 1, 'two alternative days': 1, 'tomorrow evening': 1, 'pandrah': 1, 'weekday+date': 1, 'aidu vaara nantara': 1, 'dil mein dard': 1, 'seene mein jalan': 1, 'paseena': 1, 'saans phoolna': 1, 'chehra latak gaya': 1, 'jhunjhuni': 1, 'left hand heavy + sweating': 1, 'bhayankara tale novu achanakkaagi': 1, 'edeyalli urita': 1, 'aage kar do': 1, 'kitna lagega': 1, 'postpone': 1, 'change the date': 1, 'cancel maadi': 1}
