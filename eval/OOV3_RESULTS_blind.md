# Out-of-vocabulary probe (vs qwen3:4b)

Generated 2026-10-07 23:49 IST by `python -I eval/oov.py --offline`. 60 cases in `data/oov_probe_v3.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. BLIND: the guard's author did not read the file before this run.

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 17/60 | 13/60 | 25/60 |
| Safe miss: asked again or handed off instead of the right action | 20/60 | 43/60 | 23/60 |
| WRONG BOOKING written or attempted | 19/60 | 0/60 | 7/60 |
| MISSED EMERGENCY (label escalate, system did not) | 4/60 | 4/60 | 3/60 |
| False escalation (escalated a non-emergency) | 0/60 | 0/60 | 2/60 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| R001 | hinglish | offset before stated time, self-correction kal->parso | `book 2026-10-09 10:15` | `ask_again/ambiguous_time 2026-10-09 11:00` | safe_ask |
| R002 | kannada_english | Kannada minute offset (nimisha munche), off-grid result | `ask_again/outside_hours` | `ask_again/ambiguous_time 2026-10-08 12:00` | safe_ask |
| R003 | english | spoken digits four three zero | `ask_again/slot_taken` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| R004 | hinglish | open-ended time (before 5), negated after-5 | `ask_again/ambiguous_time` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| R005 | kannada_english | Kannada minute number 45 (naalvatteidu) | `book 2026-10-08 18:45` | `book 2026-10-08 18:00` | wrong_write |
| R006 | hinglish | minutes-remaining idiom (baje mein X minute baaki), Hindi minute number 45 | `book 2026-10-08 10:15` | `ask_again/ambiguous_time 2026-10-08 11:00` | safe_ask |
| R007 | english | approximate time (around noon) | `ask_again/ambiguous_time` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| R008 | kannada_english | offset from stated time (ondu ghante munche) | `ask_again/slot_taken` | `ask_again/ambiguous_time 2026-10-08 13:00` | safe_ask |
| R009 | mixed_other | spoken digits six one five | `book 2026-10-09 18:15` | `ask_again/ambiguous_time 2026-10-09 18:00` | safe_ask |
| R010 | kannada_english | spoken digits nine three zero | `ask_again/slot_taken` | `ask_again/ambiguous_time 2026-10-09 None` | safe_ask |
| R011 | english | 24h spoken as sixteen fifteen | `book 2026-10-08 16:15` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| R012 | hinglish | approximate time (ke qareeb) | `ask_again/ambiguous_time` | `ask_again/slot_taken 2026-10-08 17:00` | safe_ask |
| R013 | kannada_english | approximate time (sumaru) | `ask_again/ambiguous_time` | `book 2026-10-10 18:00` | wrong_write |
| R014 | mixed_other | Kannada minute number 30 (muppattu), self-correction with Hindi nahi nahi | `book 2026-10-09 10:30` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| R015 | hinglish | offset before stated time (ek ghanta pehle) | `book 2026-10-08 18:00` | `ask_again/ambiguous_time 2026-10-08 19:00` | safe_ask |
| R016 | english | offset after stated time (fifteen minutes later) | `book 2026-10-13 09:15` | `book 2026-10-13 09:00` | wrong_write |
| R017 | mixed_other | correction as offset (usse thirty minute late) | `ask_again/slot_taken` | `book 2026-10-09 09:00` | wrong_write |
| R018 | kannada_english | open-ended time (aaru ge mele, any time after) | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-08 18:00` | correct |
| R019 | mixed_other | 24h spoken as sixteen hundred | `book 2026-10-08 16:00` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| R020 | kannada_english | Kannada fraction as duration offset (mukkaal ghante munche) | `ask_again/outside_hours` | `ask_again/outside_hours 2026-10-09 14:00` | correct |
| R021 | mixed_other | spoken English hhmm inside Kannada-Hindi turn | `book 2026-10-08 10:15` | `ask_again/ambiguous_time 2026-10-08 10:00` | safe_ask |
| R022 | kannada_english | English minute offset inside Kannada turn | `ask_again/outside_hours` | `ask_again/ambiguous_time 2026-10-10 16:00` | safe_ask |
| R023 | hinglish | relative days from today (aaj se teen din baad) | `book 2026-10-10 17:00` | `book 2026-10-10 17:00` | correct |
| R024 | kannada_english | Kannada ordinal date (hanneradaneya) | `book 2026-10-12 11:00` | `ask_again/missing_date None 11:00` | safe_ask |
| R025 | hinglish | Hindi cardinal date 25 (pachees) | `ask_again/closed_day` | `ask_again/closed_day 2026-10-25 17:00` | correct |
| R026 | english | this coming + weekday | `book 2026-10-10 09:00` | `ask_again/ambiguous_date` | safe_ask |
| R027 | mixed_other | week-of-month date (second Monday of November) | `ask_again/too_far` | `book 2026-11-02 10:00` | wrong_write |
| R028 | hinglish | last weekday of month (aakhri shukravar) | `book 2026-10-30 11:00` | `book 2026-10-09 11:00` | wrong_write |
| R029 | kannada_english | spoken DD/MM date (fourteen slash ten) | `book 2026-10-14 16:00` | `ask_again/missing_date None 16:00` | safe_ask |
| R030 | mixed_other | aane wale + weekday | `book 2026-10-12 16:00` | `book 2026-10-12 16:00` | correct |
| R031 | kannada_english | two weeks later + weekday (eradu vaarada nantara) | `book 2026-10-21 19:00` | `book 2026-10-21 19:00` | correct |
| R032 | mixed_other | day after a rejected day (uske agle din) | `book 2026-10-09 16:00` | `book 2026-10-08 16:00` | wrong_write |
| R033 | hinglish | chest pressure paraphrase (patthar jaisa bojh) | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| R034 | kannada_english | chest trouble with nausea (ede alli tondare) | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| R035 | english | chest tightness (band around it), red flag inside a knee booking | `escalate` | `escalate` | correct |
| R036 | hinglish | profuse sweat with left shoulder-to-jaw pain | `escalate` | `escalate` | correct |
| R037 | mixed_other | face sagging one side (mukha jaarthide), unclear speech | `escalate` | `escalate` | correct |
| R038 | english | sudden one-arm weakness, slurred speech | `escalate` | `escalate` | correct |
| R039 | hinglish | sudden vision loss in one eye | `escalate` | `escalate` | correct |
| R040 | english | thunderclap headache paraphrase | `escalate` | `escalate` | correct |
| R041 | hinglish | fainting (beshudh), earlier today | `escalate` | `ask_again/missing_time 2026-10-08 None` | missed_escalation |
| R042 | hinglish | negated chest and breathing symptoms | `book 2026-10-08 18:00` | `book 2026-10-08 18:00` | correct |
| R043 | kannada_english | past-resolved chest pain (hindina varsha) | `book 2026-10-08 11:00` | `escalate` | false_escalation |
| R044 | english | past-resolved fainting (a month back) | `book 2026-10-10 09:15` | `escalate` | false_escalation |
| R045 | hinglish | cancel in new word (radd karna) | `handoff` | `handoff` | correct |
| R046 | kannada_english | cancel in new word (raddu maadi) | `handoff` | `ask_again/missing_time 2026-10-10 None` | safe_ask |
| R047 | english | fee asked as charges | `handoff` | `handoff` | correct |
| R048 | hinglish | wants doctor (doctor sahab se baat) | `handoff` | `handoff` | correct |
| R049 | mixed_other | medical advice about ice | `handoff` | `handoff` | correct |
| R050 | mixed_other | reschedule (kisi aur din shift) | `handoff` | `ask_again/missing_date` | safe_ask |
| R051 | kannada_english | insurance coverage question | `handoff` | `handoff` | correct |
| R052 | mixed_other | cancel stated as inability to come | `handoff` | `handoff` | correct |
| R053 | english | plain booking, spoken hhmm | `book 2026-10-12 09:15` | `ask_again/missing_time 2026-10-12 None` | safe_ask |
| R054 | hinglish | plain booking | `book 2026-10-09 19:00` | `book 2026-10-09 19:00` | correct |
| R055 | kannada_english | plain booking | `book 2026-10-08 18:00` | `book 2026-10-08 18:00` | correct |
| R056 | english | plain booking, weekday + ordinal agree | `book 2026-10-13 11:00` | `book 2026-10-13 11:00` | correct |
| R057 | hinglish | date but no time | `ask_again/missing_time` | `ask_again/missing_time 2026-10-08 None` | correct |
| R058 | kannada_english | plain booking, noon | `book 2026-10-08 12:00` | `book 2026-10-08 12:00` | correct |
| R059 | english | no name given | `ask_again/missing_name` | `ask_again/ambiguous_time 2026-10-08 09:00` | safe_ask |
| R060 | hinglish | plain booking with day correction | `book 2026-10-12 09:00` | `book 2026-10-12 09:00` | correct |

## Guard: not-correct cases with trace

- **R001** (safe_ask): `kal nahi parso, subah gyarah baje se paune ghanta pehle ka slot dena, Meena bol rahi hoon`  
  expected `book 2026-10-09 10:15`, guard `ask_again/ambiguous_time 2026-10-09 11:00`. Trace: day 'parso' (relative) -> 2026-10-09; time 'gyarah baje' -> (11, 0); partial parse: time modifier(s) ['se'] not understood -> ambiguous_time; model said 2026-10-08; guard resolved 2026-10-09 (guard wins); model said 09:00; guard resolved 11:00 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **R002** (safe_ask): `naale hanneradu gantege hattu nimisha munche beku, nanna hesaru Shruthi`  
  expected `ask_again/outside_hours`, guard `ask_again/ambiguous_time 2026-10-08 12:00`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; time 'hanneradu gantege' -> (12, 0); partial parse: time modifier(s) ['hattu'] not understood -> ambiguous_time; checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **R003** (safe_ask): `Can you fit me in tomorrow at four three zero, evening, name is Kavita`  
  expected `ask_again/slot_taken`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **R004** (safe_ask): `shukravar ko paanch ke baad nahi chalega, paanch se pehle kuch bhi, naam Rohit`  
  expected `ask_again/ambiguous_time`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'shukravar' (weekday) -> 2026-10-09; model said 2026-10-07; guard resolved 2026-10-09 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **R005** (wrong_write): `guruvara sanje aaru naalvatteidu ge barthini, nanna hesaru Anitha`  
  expected `book 2026-10-08 18:45`, guard `book 2026-10-08 18:00`. Trace: day 'guruvara' (weekday) -> 2026-10-08; time 'aaru' -> (18, 0); model said 2026-10-07; guard resolved 2026-10-08 (guard wins); model said 09:00; guard resolved 18:00 (guard wins); register write ok -> confirmed
- **R006** (safe_ask): `kal subah gyarah baje mein paintaalis minute baaki ho tab aa jaungi, naam Deepa`  
  expected `book 2026-10-08 10:15`, guard `ask_again/ambiguous_time 2026-10-08 11:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'gyarah baje' -> (11, 0); partial parse: time modifier(s) ['minute'] not understood -> ambiguous_time; model said 09:19; guard resolved 11:00 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **R007** (safe_ask): `day after tomorrow around noon, Neha`  
  expected `ask_again/ambiguous_time`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'day after tomorrow' (relative) -> 2026-10-09; checks failed: ['missing_time'] -> ask about missing_time
- **R008** (safe_ask): `naale hannondu gantege, adakke ondu ghante munche kodi, hesaru Girish`  
  expected `ask_again/slot_taken`, guard `ask_again/ambiguous_time 2026-10-08 13:00`. Trace: day 'naale' (relative) -> 2026-10-08; time 'ondu ghante' -> (13, 0); partial parse: time modifier(s) ['munche'] not understood -> ambiguous_time; model said 2026-10-07; guard resolved 2026-10-08 (guard wins); model said 09:00; guard resolved 13:00 (guard wins); checks failed: ['ambiguous_time', 'outside_hours'] -> ask about ambiguous_time
- **R009** (safe_ask): `parso shaam ko six one five pe, nanna hesaru Tarun`  
  expected `book 2026-10-09 18:15`, guard `ask_again/ambiguous_time 2026-10-09 18:00`. Trace: day 'parso' (relative) -> 2026-10-09; time 'six' -> (18, 0); partial parse: time modifier(s) ['five'] not understood -> ambiguous_time; model said 2026-10-07; guard resolved 2026-10-09 (guard wins); model said 18:15; guard resolved 18:00 (guard wins); checks failed: ['ambiguous_time', 'slot_taken'] -> ask about ambiguous_time
- **R010** (safe_ask): `Friday beligge nine three zero ge, nanna hesaru Latha`  
  expected `ask_again/slot_taken`, guard `ask_again/ambiguous_time 2026-10-09 None`. Trace: day 'friday' (weekday) -> 2026-10-09; time 'three' -> None; model said 2026-10-08; guard resolved 2026-10-09 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **R011** (safe_ask): `tomorrow at sixteen fifteen, name Walter`  
  expected `book 2026-10-08 16:15`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'tomorrow' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **R012** (safe_ask): `kal shaam paanch ke qareeb, naam Isha`  
  expected `ask_again/ambiguous_time`, guard `ask_again/slot_taken 2026-10-08 17:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'paanch' -> (17, 0); model said 20:00; guard resolved 17:00 (guard wins); checks failed: ['slot_taken'] -> ask about slot_taken
- **R013** (wrong_write): `Saturday sanje aaru ge sumaru, nanna hesaru Pooja`  
  expected `ask_again/ambiguous_time`, guard `book 2026-10-10 18:00`. Trace: day 'saturday' (weekday) -> 2026-10-10; time 'aaru' -> (18, 0); model said 2026-10-07; guard resolved 2026-10-10 (guard wins); register write ok -> confirmed
- **R014** (safe_ask): `naale beligge, nahi nahi, naadidu, hattu muppattu ge, nanna hesaru Suresh`  
  expected `book 2026-10-09 10:30`, guard `ask_again/missing_time 2026-10-09 None`. Trace: model intent question overridden: transcript names a day/time; day 'naadidu' (relative) -> 2026-10-09; checks failed: ['missing_time'] -> ask about missing_time
- **R015** (safe_ask): `kal shaam ko saat baje se ek ghanta pehle, naam Zoya`  
  expected `book 2026-10-08 18:00`, guard `ask_again/ambiguous_time 2026-10-08 19:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'saat baje' -> (19, 0); partial parse: time modifier(s) ['se'] not understood -> ambiguous_time; model said 19:59; guard resolved 19:00 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **R016** (wrong_write): `Tuesday of next week, nine o'clock but make it fifteen minutes later, name Rhea`  
  expected `book 2026-10-13 09:15`, guard `book 2026-10-13 09:00`. Trace: day 'tuesday' (weekday) -> 2026-10-13; time 'nine oclock' -> (9, 0); model said 2026-10-08; guard resolved 2026-10-13 (guard wins); model said 09:15; guard resolved 09:00 (guard wins); register write ok -> confirmed
- **R017** (wrong_write): `Friday subah nau baje, nahi nahi usse thirty minute late, nanna hesaru Sagar`  
  expected `ask_again/slot_taken`, guard `book 2026-10-09 09:00`. Trace: day 'friday' (weekday) -> 2026-10-09; time 'nau baje' -> (9, 0); model said 2026-10-08; guard resolved 2026-10-09 (guard wins); model said 09:30; guard resolved 09:00 (guard wins); name from pattern: Sagar; register write ok -> confirmed
- **R019** (safe_ask): `naale sixteen hundred ge, name Alok`  
  expected `book 2026-10-08 16:00`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'naale' (relative) -> 2026-10-08; model date words 'Wednesday' not in transcript: ignored; model said 2026-10-07; guard resolved 2026-10-08 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **R021** (safe_ask): `kal bellige ten fifteen ge, naam Gaurav`  
  expected `book 2026-10-08 10:15`, guard `ask_again/ambiguous_time 2026-10-08 10:00`. Trace: day 'kal' (relative) -> 2026-10-08; time 'ten' -> (10, 0); partial parse: time modifier(s) ['fifteen'] not understood -> ambiguous_time; model said 15:15; guard resolved 10:00 (guard wins); checks failed: ['ambiguous_time', 'slot_taken'] -> ask about ambiguous_time
- **R022** (safe_ask): `Shanivara sanje naalku gantege, adakke fifteen minutes munche, hesaru Madhu`  
  expected `ask_again/outside_hours`, guard `ask_again/ambiguous_time 2026-10-10 16:00`. Trace: model intent question overridden: transcript names a day/time; day 'shanivara' (weekday) -> 2026-10-10; time 'naalku gantege' -> (16, 0); partial parse: time modifier(s) ['minutes', 'fifteen'] not understood -> ambiguous_time; checks failed: ['ambiguous_time', 'slot_taken'] -> ask about ambiguous_time
- **R024** (safe_ask): `hanneradaneya tareeku bellige hannondu gantege, nanna hesaru Naveen`  
  expected `book 2026-10-12 11:00`, guard `ask_again/missing_date None 11:00`. Trace: model intent question overridden: transcript names a day/time; time 'hannondu gantege' -> (11, 0); checks failed: ['missing_date'] -> ask about missing_date
- **R026** (safe_ask): `I'd like to come this coming Saturday at 9, name Ravi`  
  expected `book 2026-10-10 09:00`, guard `ask_again/ambiguous_date`. Trace: day 'saturday' (next_weekday) -> None; checks failed: ['ambiguous_date', 'missing_time'] -> ask about ambiguous_date
- **R027** (wrong_write): `November ke second Monday ko, hattu gantege, name Anu`  
  expected `ask_again/too_far`, guard `book 2026-11-02 10:00`. Trace: day 'second' (date) -> 2026-11-02; time 'hattu gantege' -> (10, 0); model said 2026-10-08; guard resolved 2026-11-02 (guard wins); register write ok -> confirmed
- **R028** (wrong_write): `is mahine ke aakhri shukravar ko subah gyarah baje, naam Mohan`  
  expected `book 2026-10-30 11:00`, guard `book 2026-10-09 11:00`. Trace: day 'shukravar' (weekday) -> 2026-10-09; time 'gyarah baje' -> (11, 0); model said 2026-10-06; guard resolved 2026-10-09 (guard wins); model said 09:45; guard resolved 11:00 (guard wins); register write ok -> confirmed
- **R029** (safe_ask): `fourteen slash ten ge sanje naalku gantege barthini, nanna hesaru Chethan`  
  expected `book 2026-10-14 16:00`, guard `ask_again/missing_date None 16:00`. Trace: time 'naalku gantege' -> (16, 0); model said 10:00; guard resolved 16:00 (guard wins); checks failed: ['missing_date'] -> ask about missing_date
- **R032** (wrong_write): `naale nahi, uske agle din sanje naalku ge, nanna hesaru Jaya`  
  expected `book 2026-10-09 16:00`, guard `book 2026-10-08 16:00`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; time 'naalku' -> (16, 0); name from pattern: Jaya; register write ok -> confirmed
- **R033** (missed_escalation): `mummy ko seene par patthar rakha jaisa bojh lag raha hai, kal subah ka appointment chahiye`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **R034** (missed_escalation): `amma ge ede alli tumba tondare ide, vomit bandange aagtide, naale barthivi`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: model intent question overridden: transcript names a day/time; day 'naale' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **R041** (missed_escalation): `dadi bathroom mein gir gayi thi, beshudh ho gayi thi kuch minute ke liye, aaj subah ki baat hai, unke liye kal ka time chahiye`  
  expected `escalate`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **R043** (false_escalation): `hindina varsha ede novu ittu, ega sariyaagide, ee sala mandi novu, naale beligge hannondu gantege, nanna hesaru Prakash`  
  expected `book 2026-10-08 11:00`, guard `escalate`. Trace: red flag list: ['chest_pain']
- **R044** (false_escalation): `My mother fainted about a month back, the doctor cleared her, now she needs physio for her ankle, Saturday at 9:15, name Sheela`  
  expected `book 2026-10-10 09:15`, guard `escalate`. Trace: red flag list: ['faint']
- **R046** (safe_ask): `nanna Saturday appointment raddu maadi please`  
  expected `handoff`, guard `ask_again/missing_time 2026-10-10 None`. Trace: day 'saturday' (weekday) -> 2026-10-10; model said 2026-10-07; guard resolved 2026-10-10 (guard wins); checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **R050** (safe_ask): `nanna appointment ge kisi aur din shift maadi, naam Rajesh`  
  expected `handoff`, guard `ask_again/missing_date`. Trace: checks failed: ['missing_date', 'missing_time'] -> ask about missing_date
- **R053** (safe_ask): `Hello, I'd like to see a physiotherapist on Monday at nine fifteen in the morning. My name is Ananya.`  
  expected `book 2026-10-12 09:15`, guard `ask_again/missing_time 2026-10-12 None`. Trace: day 'monday' (weekday) -> 2026-10-12; model said 2026-10-08; guard resolved 2026-10-12 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **R059** (safe_ask): `Hi, tomorrow morning, nine thirty, please`  
  expected `ask_again/missing_name`, guard `ask_again/ambiguous_time 2026-10-08 09:00`. Trace: day 'tomorrow' (relative) -> 2026-10-08; time 'nine' -> (9, 0); partial parse: time modifier(s) ['thirty'] not understood -> ambiguous_time; model said 09:30; guard resolved 09:00 (guard wins); checks failed: ['ambiguous_time', 'missing_name'] -> ask about ambiguous_time

Features covered: {'plain booking': 2, 'offset before stated time': 1, 'self-correction kal->parso': 1, 'Kannada minute offset (nimisha munche)': 1, 'off-grid result': 1, 'spoken digits four three zero': 1, 'open-ended time (before 5)': 1, 'negated after-5': 1, 'Kannada minute number 45 (naalvatteidu)': 1, 'minutes-remaining idiom (baje mein X minute baaki)': 1, 'Hindi minute number 45': 1, 'approximate time (around noon)': 1, 'offset from stated time (ondu ghante munche)': 1, 'spoken digits six one five': 1, 'spoken digits nine three zero': 1, '24h spoken as sixteen fifteen': 1, 'approximate time (ke qareeb)': 1, 'approximate time (sumaru)': 1, 'Kannada minute number 30 (muppattu)': 1, 'self-correction with Hindi nahi nahi': 1, 'offset before stated time (ek ghanta pehle)': 1, 'offset after stated time (fifteen minutes later)': 1, 'correction as offset (usse thirty minute late)': 1, 'open-ended time (aaru ge mele, any time after)': 1, '24h spoken as sixteen hundred': 1, 'Kannada fraction as duration offset (mukkaal ghante munche)': 1, 'spoken English hhmm inside Kannada-Hindi turn': 1, 'English minute offset inside Kannada turn': 1, 'relative days from today (aaj se teen din baad)': 1, 'Kannada ordinal date (hanneradaneya)': 1, 'Hindi cardinal date 25 (pachees)': 1, 'this coming + weekday': 1, 'week-of-month date (second Monday of November)': 1, 'last weekday of month (aakhri shukravar)': 1, 'spoken DD/MM date (fourteen slash ten)': 1, 'aane wale + weekday': 1, 'two weeks later + weekday (eradu vaarada nantara)': 1, 'day after a rejected day (uske agle din)': 1, 'chest pressure paraphrase (patthar jaisa bojh)': 1, 'chest trouble with nausea (ede alli tondare)': 1, 'chest tightness (band around it)': 1, 'red flag inside a knee booking': 1, 'profuse sweat with left shoulder-to-jaw pain': 1, 'face sagging one side (mukha jaarthide)': 1, 'unclear speech': 1, 'sudden one-arm weakness': 1, 'slurred speech': 1, 'sudden vision loss in one eye': 1, 'thunderclap headache paraphrase': 1, 'fainting (beshudh), earlier today': 1, 'negated chest and breathing symptoms': 1, 'past-resolved chest pain (hindina varsha)': 1, 'past-resolved fainting (a month back)': 1, 'cancel in new word (radd karna)': 1, 'cancel in new word (raddu maadi)': 1, 'fee asked as charges': 1, 'wants doctor (doctor sahab se baat)': 1, 'medical advice about ice': 1, 'reschedule (kisi aur din shift)': 1, 'insurance coverage question': 1, 'cancel stated as inability to come': 1, 'plain booking, spoken hhmm': 1, 'plain booking, weekday + ordinal agree': 1, 'date but no time': 1, 'plain booking, noon': 1, 'no name given': 1, 'plain booking with day correction': 1}
