"""Regressions for the fixes made after the blind out-of-vocabulary probe (eval/OOV_RESULTS_blind.md).

MockModel only. The utterances here are written for the tests, not copied from the probe file.
"""
import pytest

from guard.guard import Guard
from guard.normalise import parse
from guard.redflags import red_flag_hits
from guard.register import Register
from guard.schema import Extraction, ModelResult

from conftest import REF


def decide(utterance, name="Ravi"):
    mr = ModelResult(model="MOCK", extraction=Extraction(intent="book", patient_name=name), mock=True)
    return Guard(Register()).decide(utterance, REF, mr)


# ---- the dangerous path: a partial parse must never book
@pytest.mark.parametrize("utt", [
    "kal shaam 6 baje ke aas paas, naam Ravi",           # was a strict xfail until after the blind OOV v2 run
    "kal shaam around 6 baje, naam Ravi",
    "naale sanje 6 gante hattira, naanu Ravi",
    "kal subah lagbhag 10 baje, naam Ravi",
])
def test_unconsumed_time_modifier_never_books(utt):
    d = decide(utt)
    assert d.action == "ask_again" and d.reason == "ambiguous_time", (d.action, d.reason, d.trace)
    assert not d.confirmed


@pytest.mark.parametrize("utt,date,time", [
    ("tomorrow half past five pm, Ravi here", "2026-10-08", "17:30"),
    ("kal shaam half past six baje, naam Ravi", "2026-10-08", "18:30"),   # before the fix: 18:00
    ("quarter past 10 on Friday, name is Ravi", "2026-10-09", "10:15"),
    ("quarter to six tomorrow evening, this is Ravi", "2026-10-08", "17:45"),
    ("kal shaam chhe baj ke tees minute, naam Ravi", "2026-10-08", "18:30"),
    ("Monday 1745 hours, patient Ravi", "2026-10-12", "17:45"),
    ("Friday at 11 in the morning, this is Ravi", "2026-10-09", "11:00"),
])
def test_english_and_minute_forms(utt, date, time):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", date, time), d.trace


@pytest.mark.parametrize("utt,date", [
    ("solah tareekh ko shaam 6 baje, naam Ravi", "2026-10-16"),
    ("hadinaaru tareeku sanje aaru gantege, nanna hesaru Ravi", "2026-10-16"),
    ("the sixteenth, 6 in the evening, Ravi here", "2026-10-16"),
    ("ek hafte baad shaam 6 baje, naam Ravi", "2026-10-14"),
    ("ondu vaarada nantara sanje 6 gantege, naanu Ravi", "2026-10-14"),
    ("one week from today at 6 pm, Ravi", "2026-10-14"),
])
def test_word_dates_and_spans(utt, date):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", date, "18:00"), d.trace


def test_next_to_next_day():
    d = decide("next to next day evening 7 baje, Ravi")
    assert (d.action, d.date, d.time) == ("book", "2026-10-09", "19:00"), d.trace


def test_word_date_with_wrong_weekday_is_caught():
    # the blind wrong write: the date was not recognised, so the weekday check never ran
    d = decide("Friday, solah October, subah 11 baje, Ravi")   # Oct 16 is a Friday -> ok
    assert (d.action, d.date) == ("book", "2026-10-16")
    d = decide("Thursday, solah October, subah 11 baje, Ravi")
    assert (d.action, d.reason) == ("ask_again", "weekday_mismatch")


def test_span_far_away_is_too_far():
    d = decide("chhe hafte baad shaam 6 baje, naam Ravi")
    assert (d.action, d.reason) == ("ask_again", "too_far")


def test_symptom_history_is_not_a_span():
    p = parse("do hafte se ghutne mein dard hai, kal shaam 6 baje")
    assert [x.words for x in p.days] == ["kal"]


def test_number_word_before_date_is_not_a_date():
    assert parse("do date bata dijiye").days == []


def test_alternative_days_are_ambiguous():
    d = decide("Thursday ya Friday, shaam 6 baje, naam Ravi")
    assert (d.action, d.reason) == ("ask_again", "ambiguous_date")


@pytest.mark.parametrize("utt", [
    "dil mein bahut dard ho raha hai, kal ka time chahiye",
    "edeyalli tumba uri ide, naale bartini",
    "chest alli novu, naale sanje",
    "seene mein jalan aur paseena aa raha hai",
    "left arm pain and sweating since morning",
    "achanak bahut tez sar dard shuru hua, kal aana hai",
    "achanakkaagi tumba tale novu, naale beligge",
])
def test_red_flag_paraphrases(utt):
    assert red_flag_hits(utt), utt


@pytest.mark.parametrize("utt", [
    "kandhe mein dard hai, frozen shoulder, kal shaam 6 baje",
    "sar dard rehta hai kabhi kabhi, kal aana hai",          # not sudden, not severe
    "chest physiotherapy ke liye kal aana hai",
])
def test_red_flag_negatives_still_quiet(utt):
    assert not red_flag_hits(utt), utt


# ---- after the blind OOV v2 probe: structural partial-parse rule (own phrasings, not copied from the probe)
@pytest.mark.parametrize("utt", [
    "kal shaam chhe baje ke baad aaunga, naam Ravi",          # open-ended
    "kal shaam 6 baje tak pahunch jaunga, naam Ravi",
    "before 6 pm tomorrow please, Ravi here",
    "naale sanje aaru ippattu gantege, naanu Ravi",          # unparsed Kannada minutes after the hour
    "kal shaam saade chhe ke thoda baad, naam Ravi",
    "kal shaam 6 baje, nahi nahi, usse ek ghanta baad, naam Ravi",  # time moved relative to itself
])
def test_leftover_number_or_offset_never_books(utt):
    d = decide(utt)
    assert d.action == "ask_again" and d.reason == "ambiguous_time", (d.action, d.reason, d.trace)


@pytest.mark.parametrize("utt,date,time", [
    ("3 din pehle gir gayi thi, kal shaam 6 baje aana hai, naam Ravi", "2026-10-08", "18:00"),   # 'pehle' is history
])
def test_history_and_name_corrections_still_book(utt, date, time):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", date, time), d.trace


@pytest.mark.parametrize("utt", [
    "seene pe bahut pressure hai, kal aana tha",
    "papa ka munh ek taraf jhuk gaya hai",
    "amma maatu sariyagi baralla, naale beku",
    "kal raat hosh kho diya tha thodi der, aaj physio ke liye",
    "her mouth looks crooked since an hour",
])
def test_red_flag_paraphrases_v2(utt):
    assert red_flag_hits(utt), utt


def test_unparsed_english_time_words_ask_not_book():
    # "six" is not marked as a time here, so nothing is parsed: safe (missing_time), never a booking
    d = decide("tomorrow at six fifteen pm, Ravi")
    assert d.action == "ask_again" and not d.confirmed


@pytest.mark.parametrize("utt", [
    "kal shaam 6 baje, naam Ravi, nahi nahi, Ravi Kumar",    # a correction after the time: we cannot tell what changed
    "kal shaam 6 baje 2 hafte pehle wala dard, naam Ravi",   # a number glued to the time
])
def test_allowlist_known_costs_ask_again(utt):
    # Accepted costs of the allowlist window (README failure analysis): safe, but one more question for the caller.
    d = decide(utt)
    assert d.action == "ask_again" and not d.confirmed


# ---- after the blind OOV v3 probe: allowlist window (own phrasings of the failure shapes)
@pytest.mark.parametrize("utt", [
    "kal ke agle din shaam 6 baje, naam Ravi",                  # 'agle' not consumed -> not plain 'kal'
    "is mahine ka aakhri shanivar subah 10 baje, naam Ravi",    # unknown qualifier on the weekday
    "October ka third Friday, subah 10 baje, naam Ravi",        # ordinal + weekday is not a day of the month
    "Friday 10 am but push it a bit, Ravi here",                # unknown words after the time
    "naale sanje aaru ippattaidu ge, nanna hesaru Ravi",        # unknown minute word
    "Friday subah 10 baje, nahi nahi usse thoda late, naam Ravi",  # correction tail
])
def test_unknown_words_near_day_or_time_never_book(utt):
    d = decide(utt)
    assert d.action == "ask_again" and not d.confirmed, d.trace


def test_narrative_before_the_clause_does_not_block():
    d = decide("gym mein shoulder strain ho gaya pichhle mahine, kal shaam 6 baje, naam Ravi")
    assert (d.action, d.date, d.time) == ("book", "2026-10-08", "18:00"), d.trace
