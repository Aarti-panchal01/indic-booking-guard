# Out-of-vocabulary probe (vs qwen2.5-coder:7b)

Generated 2026-10-08 01:31 IST by `python -I eval/oov.py --offline`. 50 cases in `data/oov_probe_v2.jsonl`, written by a separate agent to use phrasing that `data/TAXONOMY.md` does not list. Synthetic, AI-written, not native-speaker-audited. NOT BLIND: the guard was changed after its author read earlier results on this file (dev numbers).

| Outcome | Raw model + register | Model words + dateparser + register | Model + guard |
|---|---|---|---|
| Correct (same action, and same slot or reason) | 13/50 | 11/50 | 34/50 |
| Safe miss: asked again or handed off instead of the right action | 17/50 | 32/50 | 16/50 |
| WRONG BOOKING written or attempted | 16/50 | 3/50 | 0/50 |
| MISSED EMERGENCY (label escalate, system did not) | 4/50 | 4/50 | 0/50 |
| False escalation (escalated a non-emergency) | 0/50 | 0/50 | 0/50 |

## Guard result per case

| id | lang | oov features | expected | guard | outcome |
|---|---|---|---|---|---|
| Q001 | kannada_english | no_name_oov_phrasing | `ask_again/missing_name` | `ask_again/missing_name 2026-10-09 10:00` | correct |
| Q002 | hinglish | seene_pe_pressure, tez_dhadkan | `escalate` | `escalate` | correct |
| Q003 | hinglish | relative_time_correction, aadha_ghanta_pehle | `book 2026-10-08 16:45` | `ask_again/ambiguous_time 2026-10-08 17:15` | safe_ask |
| Q004 | kannada_english | bele_daypart_variant, muvattu_for_thirty | `book 2026-10-08 09:30` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| Q005 | hinglish | agla_wala_weekday | `book 2026-10-12 18:00` | `book 2026-10-12 18:00` | correct |
| Q006 | kannada_english | kaal_spelling_of_kaalu, noon_hour_no_daypart | `book 2026-10-13 12:15` | `book 2026-10-13 12:15` | correct |
| Q007 | hinglish | agla_wala_weekday | `ask_again/ambiguous_date` | `ask_again/ambiguous_date None 17:00` | correct |
| Q008 | hinglish | solah_number_word, weekday_date_mismatch | `ask_again/weekday_mismatch` | `ask_again/weekday_mismatch 2026-10-16 17:00` | correct |
| Q009 | mixed_other | ordinal_teesri, agle_mahine | `book 2026-11-03 18:00` | `ask_again/missing_date None 18:00` | safe_ask |
| Q010 | kannada_english | weekend_bittu_exclusion | `book 2026-10-12 09:00` | `ask_again/ambiguous_time 2026-10-12 09:00` | safe_ask |
| Q011 | hinglish | fees_kitni_hai | `handoff` | `handoff` | correct |
| Q012 | kannada_english | kai_kaalu_jom_aagide | `escalate` | `escalate` | correct |
| Q013 | kannada_english | nalku_spelling | `book 2026-10-10 16:15` | `book 2026-10-10 16:15` | correct |
| Q014 | hinglish | thoda_baad_on_known_fraction | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-08 17:30` | correct |
| Q015 | hinglish | digit_time_before_daypart | `book 2026-10-08 17:30` | `book 2026-10-08 17:30` | correct |
| Q016 | english | move_appointment_phrase | `handoff` | `handoff` | correct |
| Q017 | english | ordinal_word_date, weekday_date_match | `book 2026-10-17 11:00` | `book 2026-10-17 11:00` | correct |
| Q018 | english | friday_after_this_one | `book 2026-10-16 10:30` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| Q019 | mixed_other | derh_spelling_of_dedh | `ask_again/outside_hours` | `ask_again/outside_hours 2026-10-08 13:30` | correct |
| Q020 | mixed_other | doctor_jothe_baat, report_discussion | `handoff` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| Q021 | mixed_other | cancel_maadi_in_hindi_sentence | `handoff` | `handoff` | correct |
| Q022 | english | day_month_date_order | `ask_again/too_far` | `ask_again/too_far 2026-11-20 16:00` | correct |
| Q023 | english | time_spelled_in_words_no_ampm, name_X_here | `book 2026-10-12 09:15` | `ask_again/missing_time 2026-10-12 None` | safe_ask |
| Q024 | kannada_english | hannondu_ganteyalli_no_daypart | `book 2026-10-09 11:00` | `ask_again/missing_time 2026-10-09 None` | safe_ask |
| Q025 | kannada_english | bayi_vakra, maatu_baralla | `escalate` | `escalate` | correct |
| Q026 | hinglish | paune_barah_with_subah | `book 2026-10-08 11:45` | `book 2026-10-08 11:45` | correct |
| Q027 | english | in_the_evening_phrase, name_X_here | `book 2026-10-08 16:45` | `book 2026-10-08 16:45` | correct |
| Q028 | kannada_english | nalku_spelling, moovattu_for_thirty | `book 2026-10-12 16:30` | `ask_again/ambiguous_time 2026-10-12 16:00` | safe_ask |
| Q029 | mixed_other | chest_alli_novu_codemixed | `escalate` | `escalate` | correct |
| Q030 | kannada_english | mukkal_spelling_of_mukkaalu | `book 2026-10-09 17:45` | `book 2026-10-09 17:45` | correct |
| Q031 | hinglish | achanak_gir_gaye_hosh_nahi | `escalate` | `escalate` | correct |
| Q032 | english | relative_time_correction, booking_under_name | `book 2026-10-13 17:00` | `ask_again/ambiguous_time 2026-10-13 18:00` | safe_ask |
| Q033 | kannada_english | cancel_maadi | `handoff` | `handoff` | correct |
| Q034 | mixed_other | agle_week_english_week, hindi_number_with_kannada_gante | `book 2026-10-15 09:00` | `book 2026-10-15 09:00` | correct |
| Q035 | mixed_other | naale_beda_negation, dot_time_with_pm | `book 2026-10-09 19:15` | `book 2026-10-09 19:15` | correct |
| Q036 | mixed_other | office_ke_baad_phrase, aaj_nahi_naale_correction, dot_time_with_ge | `book 2026-10-08 18:15` | `ask_again/ambiguous_time 2026-10-08 18:15` | safe_ask |
| Q037 | kannada_english | saaynkaal_spelling, aidu_ganteyalli | `ask_again/slot_taken` | `ask_again/missing_time 2026-10-08 None` | safe_ask |
| Q038 | hinglish | theek_modifier_on_hour | `book 2026-10-10 10:00` | `book 2026-10-10 10:00` | correct |
| Q039 | kannada_english | english_number_words_in_kannada | `book 2026-10-09 10:45` | `ask_again/ambiguous_time 2026-10-09 10:00` | safe_ask |
| Q040 | kannada_english | medicine_question_knee_pain | `handoff` | `handoff` | correct |
| Q041 | kannada_english | ede_hididhange | `escalate` | `escalate` | correct |
| Q042 | mixed_other | sandhya_daypart | `ask_again/past_time` | `ask_again/past_time 2026-10-07 18:00` | correct |
| Q043 | english | time_spelled_in_words_with_pm | `book 2026-10-13 16:30` | `ask_again/missing_time 2026-10-13 None` | safe_ask |
| Q044 | hinglish | gas_jaisa_dard_seene, paseena | `escalate` | `escalate` | correct |
| Q045 | hinglish | lunch_ke_baad_as_daypart | `book 2026-10-08 16:00` | `ask_again/ambiguous_time 2026-10-08 16:00` | safe_ask |
| Q046 | english | open_ended_after_X_pm, name_X_here | `ask_again/ambiguous_time` | `ask_again/ambiguous_time 2026-10-13 17:00` | correct |
| Q047 | english | heavy_weight_on_chest_simile, drenched_in_sweat | `escalate` | `escalate` | correct |
| Q048 | hinglish | itwaar_spelling_of_ravivar | `ask_again/closed_day` | `ask_again/missing_date None 17:00` | safe_ask |
| Q049 | hinglish | pone_spelling_of_paune, no_baje, no_daypart | `book 2026-10-09 16:45` | `book 2026-10-09 16:45` | correct |
| Q050 | mixed_other | chaudah_number_word, weekday_date_match, mixed_hindi_kannada_date | `book 2026-10-14 17:00` | `book 2026-10-14 17:00` | correct |

## Guard: not-correct cases with trace

- **Q003** (safe_ask): `kal shaam sawa paanch baje... nahi nahi, usse aadha ghanta pehle, naam Aditi`  
  expected `book 2026-10-08 16:45`, guard `ask_again/ambiguous_time 2026-10-08 17:15`. Trace: day 'kal' (relative) -> 2026-10-08; time 'sawa paanch baje' -> (17, 15); partial parse: time modifier(s) ['correction+pehle'] not understood -> ambiguous_time; model said 17:30; guard resolved 17:15 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **Q004** (safe_ask): `naale bele ombattu muvattu ge, nanna hesaru Girish`  
  expected `book 2026-10-08 09:30`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'naale' (relative) -> 2026-10-08; model said 2026-10-07; guard resolved 2026-10-08 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **Q009** (safe_ask): `teesri tareekh agle mahine, sanje aaru gantege, naam Bhavna`  
  expected `book 2026-11-03 18:00`, guard `ask_again/missing_date None 18:00`. Trace: time 'aaru gantege' -> (18, 0); checks failed: ['missing_date'] -> ask about missing_date
- **Q010** (safe_ask): `weekend bittu Monday beligge ombattu gantege, nanna hesaru Anjali`  
  expected `book 2026-10-12 09:00`, guard `ask_again/ambiguous_time 2026-10-12 09:00`. Trace: day 'monday' (weekday) -> 2026-10-12; time 'ombattu gantege' -> (9, 0); model said 2026-10-09; guard resolved 2026-10-12 (guard wins); allowlist window: unrecognised words ['weekend', 'bittu'] next to the day/time -> ambiguous_time
- **Q018** (safe_ask): `Friday after this one, ten thirty am, my name is Tara`  
  expected `book 2026-10-16 10:30`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'friday' (weekday) -> 2026-10-09; model said 2026-10-13; guard resolved 2026-10-09 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **Q020** (safe_ask): `doctor jothe baat karbeku, meri MRI report ke baare mein, kal call karwa dijiye`  
  expected `handoff`, guard `ask_again/missing_time 2026-10-08 None`. Trace: model intent question overridden: transcript names a day/time; day 'kal' (relative) -> 2026-10-08; checks failed: ['missing_name', 'missing_time'] -> ask about missing_time
- **Q023** (safe_ask): `Could I have next Monday at nine fifteen in the morning? Nisha here.`  
  expected `book 2026-10-12 09:15`, guard `ask_again/missing_time 2026-10-12 None`. Trace: day 'monday' (next_weekday) -> 2026-10-12; model said 2026-10-16; guard resolved 2026-10-12 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **Q024** (safe_ask): `Friday hannondu ganteyalli bartini, nanna hesaru Suresh`  
  expected `book 2026-10-09 11:00`, guard `ask_again/missing_time 2026-10-09 None`. Trace: day 'friday' (weekday) -> 2026-10-09; checks failed: ['missing_time'] -> ask about missing_time
- **Q028** (safe_ask): `Monday sanje nalku moovattu gantege, nanna hesaru Lakshmi`  
  expected `book 2026-10-12 16:30`, guard `ask_again/ambiguous_time 2026-10-12 16:00`. Trace: day 'monday' (weekday) -> 2026-10-12; time 'nalku' -> (16, 0); partial parse: time modifier(s) ['moovattu'] not understood -> ambiguous_time; model said 2026-10-15; guard resolved 2026-10-12 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **Q032** (safe_ask): `Tuesday at 6 pm. Actually no, make it an hour earlier. Booking under Kabir.`  
  expected `book 2026-10-13 17:00`, guard `ask_again/ambiguous_time 2026-10-13 18:00`. Trace: day 'tuesday' (weekday) -> 2026-10-13; time '6 pm' -> (18, 0); partial parse: time modifier(s) ['correction+earlier'] not understood -> ambiguous_time; model said 2026-10-06; guard resolved 2026-10-13 (guard wins); model said 17:00; guard resolved 18:00 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **Q036** (safe_ask): `aaj nahi, naale office ke baad 6.15 ge barthini, nanna hesaru Divya`  
  expected `book 2026-10-08 18:15`, guard `ask_again/ambiguous_time 2026-10-08 18:15`. Trace: day 'naale' (relative) -> 2026-10-08; time '6:15' -> (18, 15); allowlist window: unrecognised words ['office', 'baad'] next to the day/time -> ambiguous_time
- **Q037** (safe_ask): `naale saaynkaal aidu ganteyalli, nanna hesaru Harish`  
  expected `ask_again/slot_taken`, guard `ask_again/missing_time 2026-10-08 None`. Trace: day 'naale' (relative) -> 2026-10-08; checks failed: ['missing_time'] -> ask about missing_time
- **Q039** (safe_ask): `Friday beligge ten forty-five ge barthini, naanu Prakash`  
  expected `book 2026-10-09 10:45`, guard `ask_again/ambiguous_time 2026-10-09 10:00`. Trace: day 'friday' (weekday) -> 2026-10-09; time 'ten' -> (10, 0); partial parse: time modifier(s) ['forty', 'five'] not understood -> ambiguous_time; model said 2026-10-06; guard resolved 2026-10-09 (guard wins); model said 10:45; guard resolved 10:00 (guard wins); checks failed: ['ambiguous_time'] -> ask about ambiguous_time
- **Q043** (safe_ask): `Hello, I'd like four thirty pm on Tuesday please. This is Anand.`  
  expected `book 2026-10-13 16:30`, guard `ask_again/missing_time 2026-10-13 None`. Trace: day 'tuesday' (weekday) -> 2026-10-13; model said 2026-10-10; guard resolved 2026-10-13 (guard wins); checks failed: ['missing_time'] -> ask about missing_time
- **Q045** (safe_ask): `kal lunch ke baad 4 baje ka time dedo, naam Sunil`  
  expected `book 2026-10-08 16:00`, guard `ask_again/ambiguous_time 2026-10-08 16:00`. Trace: day 'kal' (relative) -> 2026-10-08; time '4 baje' -> (16, 0); allowlist window: unrecognised words ['lunch', 'baad'] next to the day/time -> ambiguous_time
- **Q048** (safe_ask): `itwaar ko shaam paanch baje aa jaunga, naam Gopal`  
  expected `ask_again/closed_day`, guard `ask_again/missing_date None 17:00`. Trace: time 'paanch baje' -> (17, 0); checks failed: ['missing_date'] -> ask about missing_date

Features covered: {'name_X_here': 3, 'relative_time_correction': 2, 'agla_wala_weekday': 2, 'nalku_spelling': 2, 'weekday_date_match': 2, 'no_name_oov_phrasing': 1, 'seene_pe_pressure': 1, 'tez_dhadkan': 1, 'aadha_ghanta_pehle': 1, 'bele_daypart_variant': 1, 'muvattu_for_thirty': 1, 'kaal_spelling_of_kaalu': 1, 'noon_hour_no_daypart': 1, 'solah_number_word': 1, 'weekday_date_mismatch': 1, 'ordinal_teesri': 1, 'agle_mahine': 1, 'weekend_bittu_exclusion': 1, 'fees_kitni_hai': 1, 'kai_kaalu_jom_aagide': 1, 'thoda_baad_on_known_fraction': 1, 'digit_time_before_daypart': 1, 'move_appointment_phrase': 1, 'ordinal_word_date': 1, 'friday_after_this_one': 1, 'derh_spelling_of_dedh': 1, 'doctor_jothe_baat': 1, 'report_discussion': 1, 'cancel_maadi_in_hindi_sentence': 1, 'day_month_date_order': 1, 'time_spelled_in_words_no_ampm': 1, 'hannondu_ganteyalli_no_daypart': 1, 'bayi_vakra': 1, 'maatu_baralla': 1, 'paune_barah_with_subah': 1, 'in_the_evening_phrase': 1, 'moovattu_for_thirty': 1, 'chest_alli_novu_codemixed': 1, 'mukkal_spelling_of_mukkaalu': 1, 'achanak_gir_gaye_hosh_nahi': 1, 'booking_under_name': 1, 'cancel_maadi': 1, 'agle_week_english_week': 1, 'hindi_number_with_kannada_gante': 1, 'naale_beda_negation': 1, 'dot_time_with_pm': 1, 'office_ke_baad_phrase': 1, 'aaj_nahi_naale_correction': 1, 'dot_time_with_ge': 1, 'saaynkaal_spelling': 1, 'aidu_ganteyalli': 1, 'theek_modifier_on_hour': 1, 'english_number_words_in_kannada': 1, 'medicine_question_knee_pain': 1, 'ede_hididhange': 1, 'sandhya_daypart': 1, 'time_spelled_in_words_with_pm': 1, 'gas_jaisa_dard_seene': 1, 'paseena': 1, 'lunch_ke_baad_as_daypart': 1, 'open_ended_after_X_pm': 1, 'heavy_weight_on_chest_simile': 1, 'drenched_in_sweat': 1, 'itwaar_spelling_of_ravivar': 1, 'pone_spelling_of_paune': 1, 'no_baje': 1, 'no_daypart': 1, 'chaudah_number_word': 1, 'mixed_hindi_kannada_date': 1}
