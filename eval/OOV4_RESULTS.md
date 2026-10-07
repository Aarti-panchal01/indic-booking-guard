# Out-of-vocabulary probe (vs qwen3:4b)

Generated 2026-10-08 01:45 IST by `python -I eval/oov.py --offline`. 60 cases in `data/oov_probe_v4.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. NOT BLIND: the guard was changed after its author read earlier results on this file (dev numbers).

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 16/60 | 15/60 | 35/60 |
| Safe miss: asked again or handed off instead of the right action | 27/60 | 42/60 | 23/60 |
| WRONG BOOKING written or attempted | 14/60 | 0/60 | 1/60 |
| MISSED EMERGENCY (label escalate, system did not) | 3/60 | 3/60 | 1/60 |
| False escalation (escalated a non-emergency) | 0/60 | 0/60 | 0/60 |
| All wrong bookings, incl. booked emergencies (not exclusive) | 14/60 | 0/60 | 1/60 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| S001 | hinglish | offset from parso | `ask_again/closed_day` | `book 2026-10-09 10:00` | wrong_write |
| S002 | hinglish | past resolved cardiac history | `book 2026-10-08 19:00` | `book 2026-10-08 19:00` | correct |
| S003 | english | worst headache of my life | `escalate` | `escalate` | correct |
| S004 | english | negated symptoms | `ask_again/missing_time` | `ask_again/missing_time 2026-10-10 None` | correct |
| S005 | mixed_other | naale alla correction | `book 2026-10-09 17:00` | `book 2026-10-09 17:00` | correct |
| S006 | kannada_english | ivattu = today | `ask_again/past_time` | `ask_again/past_time 2026-10-07 17:00` | correct |
| S007 | hinglish | boli ladkhada gayi | `escalate` | `escalate` | correct |
| S008 | mixed_other | barolla, cancel kar do | `handoff` | `handoff` | correct |
| S009 | english | ibuprofen | `handoff` | `handoff` | correct |
| S010 | english | after lunch open-ended | `ask_again/ambiguous_time` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| S011 | hinglish | parso ke agle din = +3 | `book 2026-10-10 12:00` | `ask_again/ambiguous_time 2026-10-09 12:00` | safe_ask |
| S012 | hinglish | aage khiskani | `handoff` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| S013 | mixed_other | pehli tareekh = 1st | `ask_again/closed_day` | `ask_again/missing_date None 18:00` | safe_ask |
| S014 | mixed_other | weekend | `ask_again/ambiguous_date` | `ask_again/missing_date None 17:00` | safe_ask |
| S015 | kannada_english | ayyo filler | `ask_again/missing_name` | `ask_again/missing_name 2026-10-08 18:00` | correct |
| S016 | kannada_english | mooru dina nantara | `book 2026-10-10 16:45` | `book 2026-10-10 16:45` | correct |
| S017 | hinglish | ice or heat | `handoff` | `handoff` | correct |
| S018 | mixed_other | weekday+date agree | `book 2026-10-19 16:00` | `ask_again/ambiguous_time 2026-10-19 16:00` | safe_ask |
| S019 | kannada_english | charge yeshtu | `handoff` | `handoff` | correct |
| S020 | kannada_english | muvattu = 30 | `book 2026-10-08 09:30` | `ask_again/ambiguous_time 2026-10-08 09:00` | safe_ask |
| S021 | kannada_english | negated chest and breathing | `book 2026-10-08 18:00` | `book 2026-10-08 18:00` | correct |
| S022 | kannada_english | mukha jaarthide | `escalate` | `escalate` | correct |
| S023 | mixed_other | chhe November, weekday+date | `book 2026-11-06 18:00` | `book 2026-11-06 18:00` | correct |
| S024 | english | oh-eight-hundred | `ask_again/outside_hours` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| S025 | english | sixteen hundred | `ask_again/slot_taken` | `ask_again/missing_time 2026-10-10 None` | safe_ask |
| S026 | hinglish | N din baad, sava spelling | `book 2026-10-10 10:15` | `book 2026-10-10 10:15` | correct |
| S027 | hinglish | bhaari bhaari, paseena paseena | `escalate` | `escalate` | correct |
| S028 | english | gasping, blue lips | `escalate` | `escalate` | correct |
| S029 | hinglish | retraction without replacement | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-08 17:00` | correct |
| S030 | mixed_other | Tuesday ge | `book 2026-10-13 10:00` | `book 2026-10-13 10:00` | correct |
| S031 | kannada_english | pain worse with exercise | `handoff` | `handoff` | correct |
| S032 | kannada_english | munde hakbahuda | `handoff` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| S033 | kannada_english | illa illa correction | `book 2026-10-08 16:00` | `book 2026-10-08 16:00` | correct |
| S034 | kannada_english | hattu dina nantara | `book 2026-10-17 09:00` | `book 2026-10-17 09:00` | correct |
| S035 | kannada_english | feels like someone sitting on chest | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| S036 | mixed_other | weekday+ippattondu | `ask_again/weekday_mismatch` | `ask_again/weekday_mismatch 2026-10-21 09:00` | correct |
| S037 | hinglish | radd karwana | `handoff` | `handoff` | correct |
| S038 | kannada_english | kodi = please give | `book 2026-10-08 09:00` | `book 2026-10-08 09:00` | correct |
| S039 | english | week after next | `book 2026-10-20 11:00` | `ask_again/missing_time 2026-10-13 None` | safe_ask |
| S040 | hinglish | MRI report | `handoff` | `handoff` | correct |
| S041 | kannada_english | ee budhavara, hannondu mukkaalu | `book 2026-10-14 11:45` | `book 2026-10-14 11:45` | correct |
| S042 | english | 2nd of November | `book 2026-11-02 17:00` | `ask_again/missing_time 2026-11-05 None` | safe_ask |
| S043 | mixed_other | weekday+date agree | `book 2026-10-10 12:00` | `book 2026-10-10 12:00` | correct |
| S044 | hinglish | kal ke baad wala din | `ask_again/missing_time` | `ask_again/missing_time 2026-10-08 None` | correct |
| S045 | hinglish | do mahine baad | `ask_again/too_far` | `ask_again/missing_date None 11:00` | safe_ask |
| S046 | english | 24h spoken time | `book 2026-10-08 16:15` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| S047 | hinglish | aane wale weekday | `book 2026-10-12 18:00` | `ask_again/ambiguous_time 2026-10-12 18:00` | safe_ask |
| S048 | mixed_other | naale yaane kal | `book 2026-10-08 11:00` | `ask_again/ambiguous_time 2026-10-08 11:00` | safe_ask |
| S049 | kannada_english | aidu mukkaalu, banthini | `ask_again/missing_date` | `ask_again/missing_date None 17:45` | correct |
| S050 | english | package price | `handoff` | `handoff` | correct |
| S051 | hinglish | N din baad, pauna X | `book 2026-10-09 16:45` | `ask_again/ambiguous_time 2026-10-09 17:00` | safe_ask |
| S052 | hinglish | N hafte baad + weekday | `book 2026-10-21 17:00` | `book 2026-10-21 17:00` | correct |
| S053 | hinglish | baees = 22 | `book 2026-10-22 09:00` | `ask_again/ambiguous_time 2026-10-22 09:00` | safe_ask |
| S054 | kannada_english | ippattondu = 21, hanneradu kaalu | `book 2026-10-21 12:15` | `ask_again/missing_date None 12:15` | safe_ask |
| S055 | kannada_english | muvattu = 30 | `ask_again/slot_taken` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| S056 | hinglish | aas paas approximate | `ask_again/ambiguous_time` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| S057 | mixed_other | left arm+jaw+bevarthide | `escalate` | `escalate` | correct |
| S058 | kannada_english | ee shanivara, banni | `book 2026-10-10 10:00` | `ask_again/ambiguous_time 2026-10-10 10:00` | safe_ask |
| S059 | mixed_other | this Friday | `book 2026-10-09 19:00` | `book 2026-10-09 19:00` | correct |
| S060 | english | noon, the 13th | `book 2026-10-13 12:00` | `ask_again/ambiguous_date 2026-10-13 12:00` | safe_ask |

## Guard: not-correct cases with trace

- **S001** (wrong_write): `parso ke do din baad subah das baje, naam Lalita`  
  expected `ask_again/closed_day`, guard `book 2026-10-09 10:00`. Trace: day 'do din baad' (relative) -> 2026-10-09; time 'das baje' -> (10, 0); model said 09:00; guard resolved 10:00 (guard wins); register write ok -> confirmed
- **S010** (safe_ask): `Tomorrow, sometime after lunch is fine, Meera.`  
  expected `ask_again/ambiguous_time`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **S011** (safe_ask): `haan ji, parso ke agle din dopahar barah baje ka time mil jayega? Neha naam hai mera`  
  expected `book 2026-10-10 12:00`, guard `ask_again/ambiguous_time 2026-10-09 12:00`. Trace: day 'parso' (relative) -> 2026-10-09; time 'barah baje' -> (12, 0); model said 2026-10-08; guard resolved 2026-10-09 (guard wins); allowlist window: unrecognised words ['agle'] next to the day/time -> ambiguous_time
- **S012** (safe_ask): `meri date thodi aage khiskani hai, Friday wali`  
  expected `handoff`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'friday' (weekday) -> 2026-10-09; model said 2026-10-08; guard resolved 2026-10-09 (guard wins); checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **S013** (safe_ask): `pehli tareekh ko shaam chhe baje, naanu Osman`  
  expected `ask_again/closed_day`, guard `ask_again/missing_date None 18:00`. Trace: time 'chhe baje' -> (18, 0); model said 20:00; guard resolved 18:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **S014** (safe_ask): `weekend pe evening paanch gantege aaunga, name Tanvir`  
  expected `ask_again/ambiguous_date`, guard `ask_again/missing_date None 17:00`. Trace: time 'paanch gantege' -> (17, 0); model said 18:00; guard resolved 17:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **S018** (safe_ask): `19 tareekh Monday ge, sanje naalku gantege, naan hesaru Pranav`  
  expected `book 2026-10-19 16:00`, guard `ask_again/ambiguous_time 2026-10-19 16:00`. Trace: day '19 tareekh' (date) -> 2026-10-19; time 'naalku gantege' -> (16, 0); model said 2026-10-07; guard resolved 2026-10-19 (guard wins); model said 09:00; guard resolved 16:00 (guard wins); allowlist window: unrecognised words ['naan'] next to the day/time -> ambiguous_time
- **S020** (safe_ask): `naale beligge ombattu muvattege appointment beku, hesaru Deepa`  
  expected `book 2026-10-08 09:30`, guard `ask_again/ambiguous_time 2026-10-08 09:00`. Trace: day 'naale' (relative) -> 2026-10-08; time 'ombattu' -> (9, 0); model said 2026-10-07; guard resolved 2026-10-08 (guard wins); model said null; guard resolved 09:00 (guard wins); allowlist window: unrecognised words ['muvattege'] next to the day/time -> ambiguous_time
- **S024** (safe_ask): `Tomorrow oh-eight-hundred please, Nikhil`  
  expected `ask_again/outside_hours`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **S025** (safe_ask): `This Saturday, sixteen hundred, Hari.`  
  expected `ask_again/slot_taken`, guard `ask_again/missing_time 2026-10-10 None`. Trace: day 'saturday' (weekday) -> 2026-10-10; model said 2026-10-08; guard resolved 2026-10-10 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **S032** (safe_ask): `nanna appointment swalpa munde hakbahuda? Shukravara ide`  
  expected `handoff`, guard `ask_again/missing_time 2026-10-09 None`. Trace: model intent question overridden: transcript names a day/time; day 'shukravara' (weekday) -> 2026-10-09; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **S035** (missed_escalation): `amma ge edeya mele yaaro kootkondange aagthide, naale beligge kaalu novu ge physio beku`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **S039** (safe_ask): `Week after next, Tuesday, eleven sharp in the morning, for Ritu.`  
  expected `book 2026-10-20 11:00`, guard `ask_again/missing_time 2026-10-13 None`. Trace: day 'tuesday' (next_weekday) -> 2026-10-13; model said 2026-10-14; guard resolved 2026-10-13 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **S042** (safe_ask): `I'd like the 2nd of November, five in the evening. Joseph.`  
  expected `book 2026-11-02 17:00`, guard `ask_again/missing_time 2026-11-05 None`. Trace: day '5 in' (date) -> 2026-11-05; model said 2026-10-08; guard resolved 2026-11-05 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **S045** (safe_ask): `do mahine baad subah gyarah baje, naam Alok`  
  expected `ask_again/too_far`, guard `ask_again/missing_date None 11:00`. Trace: time 'gyarah baje' -> (11, 0); model said 09:45; guard resolved 11:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **S046** (safe_ask): `Can I get sixteen fifteen tomorrow? Karthik here.`  
  expected `book 2026-10-08 16:15`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **S047** (safe_ask): `aane wale somvar ko shaam chhe baje, Imran naam hai`  
  expected `book 2026-10-12 18:00`, guard `ask_again/ambiguous_time 2026-10-12 18:00`. Trace: day 'somvar' (next_weekday) -> 2026-10-12; time 'chhe baje' -> (18, 0); model said 2026-10-08; guard resolved 2026-10-12 (guard wins); allowlist window: unrecognised words ['wale'] next to the day/time -> ambiguous_time
- **S048** (safe_ask): `naale yaane kal, subah gyarah baje, Prakash anta`  
  expected `book 2026-10-08 11:00`, guard `ask_again/ambiguous_time 2026-10-08 11:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'gyarah baje' -> (11, 0); model said 2026-10-06; guard resolved 2026-10-08 (guard wins); model said 09:45; guard resolved 11:00 (guard wins); allowlist window: unrecognised words ['yaane', 'anta'] next to the day/time -> ambiguous_time
- **S051** (safe_ask): `do din baad shaam ko pauna paanch baje, Rakesh bol raha hoon`  
  expected `book 2026-10-09 16:45`, guard `ask_again/ambiguous_time 2026-10-09 17:00`. Trace: day 'do din baad' (relative) -> 2026-10-09; time 'paanch baje' -> (17, 0); model said 2026-10-07; guard resolved 2026-10-09 (guard wins); allowlist window: unrecognised words ['pauna'] next to the day/time -> ambiguous_time
- **S053** (safe_ask): `baees tareekh ko subah nau baje chalega? Sunita bol rahi hoon`  
  expected `book 2026-10-22 09:00`, guard `ask_again/ambiguous_time 2026-10-22 09:00`. Trace: model intent question overridden: transcript names a day/time; day '22 tareekh' (date) -> 2026-10-22; time 'nau baje' -> (9, 0); allowlist window: unrecognised words ['chalega'] next to the day/time -> ambiguous_time
- **S054** (safe_ask): `ippattondne tareeku madhyahna hanneradu kaalu ge, nanna hesaru Chaitra`  
  expected `book 2026-10-21 12:15`, guard `ask_again/missing_date None 12:15`. Trace: time 'hanneradu kaalu' -> (12, 15); model said 12:00; guard resolved 12:15 (guard wins); model name 'nanna hesaru Chaitra' looks like day/time/booking words; ignored; name from pattern: Chaitra; checks failed: ['missing_date'] -> ask about missing_date
- **S055** (safe_ask): `naadidu ombattu muvattege beku, hesaru Rekha`  
  expected `ask_again/slot_taken`, guard `ask_again/missing_time 2026-10-09 None`. Trace: model intent question overridden: transcript names a day/time; day 'naadidu' (relative) -> 2026-10-09; checks failed: ['missing_time'] -> ask about missing_time
- **S056** (safe_ask): `kal shaam ke aas paas aa jaunga, naam Dinesh`  
  expected `ask_again/ambiguous_time`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **S058** (safe_ask): `ee shanivara beligge hattu gantege banni, nanna hesaru Mahesh`  
  expected `book 2026-10-10 10:00`, guard `ask_again/ambiguous_time 2026-10-10 10:00`. Trace: day 'shanivara' (weekday) -> 2026-10-10; time 'hattu gantege' -> (10, 0); model said 2026-10-07; guard resolved 2026-10-10 (guard wins); allowlist window: unrecognised words ['banni'] next to the day/time -> ambiguous_time
- **S060** (safe_ask): `Noon on the 13th works for me, it's Ismail.`  
  expected `book 2026-10-13 12:00`, guard `ask_again/ambiguous_date 2026-10-13 12:00`. Trace: day '13 th' (date) -> 2026-10-13; dateparser fallback on 'Noon' -> (12, 0); allowlist window: unrecognised words ['works'] next to the day/time -> ambiguous_date

Features covered: {'weekday+date agree': 2, 'muvattu = 30': 2, 'N din baad': 2, 'offset from parso': 1, 'past resolved cardiac history': 1, 'worst headache of my life': 1, 'negated symptoms': 1, 'naale alla correction': 1, 'ivattu = today': 1, 'boli ladkhada gayi': 1, 'barolla': 1, 'cancel kar do': 1, 'ibuprofen': 1, 'after lunch open-ended': 1, 'parso ke agle din = +3': 1, 'aage khiskani': 1, 'pehli tareekh = 1st': 1, 'weekend': 1, 'ayyo filler': 1, 'mooru dina nantara': 1, 'ice or heat': 1, 'charge yeshtu': 1, 'negated chest and breathing': 1, 'mukha jaarthide': 1, 'chhe November': 1, 'weekday+date': 1, 'oh-eight-hundred': 1, 'sixteen hundred': 1, 'sava spelling': 1, 'bhaari bhaari': 1, 'paseena paseena': 1, 'gasping': 1, 'blue lips': 1, 'retraction without replacement': 1, 'Tuesday ge': 1, 'pain worse with exercise': 1, 'munde hakbahuda': 1, 'illa illa correction': 1, 'hattu dina nantara': 1, 'feels like someone sitting on chest': 1, 'weekday+ippattondu': 1, 'radd karwana': 1, 'kodi = please give': 1, 'week after next': 1, 'MRI report': 1, 'ee budhavara': 1, 'hannondu mukkaalu': 1, '2nd of November': 1, 'kal ke baad wala din': 1, 'do mahine baad': 1, '24h spoken time': 1, 'aane wale weekday': 1, 'naale yaane kal': 1, 'aidu mukkaalu': 1, 'banthini': 1, 'package price': 1, 'pauna X': 1, 'N hafte baad + weekday': 1, 'baees = 22': 1, 'ippattondu = 21': 1, 'hanneradu kaalu': 1, 'aas paas approximate': 1, 'left arm+jaw+bevarthide': 1, 'ee shanivara': 1, 'banni': 1, 'this Friday': 1, 'noon': 1, 'the 13th': 1}
