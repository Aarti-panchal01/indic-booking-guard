"""Regression tests for the second Oct 8 round: two-tier escalation, loss of function, Marathi, underplay, dates.

Every phrase is NEW wording written for these tests: not copied from any probe, golden set, or the v6 misses.
Marathi phrases are AI-written, not native-speaker audited.
"""
from datetime import date

import pytest

from guard.guard import stacked_days
from guard.normalise import parse, resolve_day
from guard.redflags import human_check_hits, red_flag_hits

REF_D = date(2026, 10, 7)
VALID = "kal shaam 4 baje, naam Ravi"

# ---- tier 2: human check (body region + complaint word + onset today, sign word unknown)
HUMAN_CHECK = [
    "Since this afternoon my father says his left cheek feels strange",
    "Amma ge ivattu beligge inda tale alli eno vichitra agtide",
    "Aaji la sakalpasun dolyat kahitari vegla vatatay",
    "Nani ki awaaz abhi kuch alag si lag rahi hai",
]
NOT_HUMAN_CHECK = [
    "Gym ke baad se kandhe mein kuch ajeeb sa lag raha hai",          # benign cause
    "Since this morning my knee feels stiff",                        # not a red-flag region
    "Daant nikalwaya aaj subah, tab se jabde mein dard",              # dental
    "Teen saal pehle seene mein kuch hota tha, ab sab theek hai",     # old history, fine now
    "Aaj shaam chest x-ray ka report dikhana hai",                   # service request
]


@pytest.mark.parametrize("text", HUMAN_CHECK)
def test_human_check_fires_without_a_known_sign(text):
    assert red_flag_hits(text) == [], (text, red_flag_hits(text))
    assert human_check_hits(text), text


@pytest.mark.parametrize("text", NOT_HUMAN_CHECK)
def test_human_check_quiet_on_benign_or_old(text):
    assert red_flag_hits(text) == [] and human_check_hits(text) == [], (text, red_flag_hits(text), human_check_hits(text))


def test_english_possessive_reads_as_the_body_part():
    assert red_flag_hits("my mother's left arm's aching since lunch") == ["jaw_or_left_arm_pain"]


def test_meal_onset_counts_as_today():
    assert human_check_hits("since breakfast her face feels odd")


def test_tiers_on_the_decision(decide):
    urgent = decide(f"{VALID}. papa ke seene mein dard ho raha hai")
    check = decide(f"{VALID}. Since this afternoon my father says his left cheek feels strange")
    assert (urgent.action, urgent.tier) == ("escalate", "urgent")
    assert (check.action, check.tier) == ("escalate", "human_check")
    assert not check.confirmed and check.date is None


def test_urgent_wins_over_human_check():
    text = "Abhi se seene mein dard hai aur gaal mein kuch ajeeb lag raha"
    assert red_flag_hits(text) and human_check_hits(text) == []


# ---- loss of function (Hindi, Kannada, Marathi, English)
LOSS_OF_FUNCTION = [
    "Papa achanak se spoon nahi pakad pa rahe, haath mein jaan nahi",
    "Ajji ge kai etthakke aagtilla, novu enu illa",
    "Aai la haat uchalta yet nahi achanak",
    "his fingers went numb and he could not hold the glass",
    "her right leg is not working since an hour",
]
NOT_LOSS_OF_FUNCTION = [
    "Frozen shoulder hai, haath upar nahi uthta, dard bhi hai",
    "After the fall yesterday I cannot move my wrist much",
]


@pytest.mark.parametrize("text", LOSS_OF_FUNCTION)
def test_loss_of_function_escalates(text):
    assert red_flag_hits(text) or human_check_hits(text), text


@pytest.mark.parametrize("text", NOT_LOSS_OF_FUNCTION)
def test_loss_of_function_with_benign_cause(text):
    assert red_flag_hits(text) == [] and human_check_hits(text) == [], (text, red_flag_hits(text), human_check_hits(text))


def test_painless_sudden_is_urgent_not_check():
    assert "loss_of_function" in red_flag_hits("Papa achanak se spoon nahi pakad pa rahe, haath mein jaan nahi")


# ---- Marathi (AI-written, not native-speaker audited)
MARATHI_URGENT = [
    "Baba na chhatit jad vatatay ani ghaam yetoy",
    "Tyanna shwas gheta yet nahi",
    "Aai che tond ek bajula vakda zala",
    "Ajoba na bolta yet nahi neet",
    "dolyan samor achanak andhar aala",
    "dava haat dukhtoy kalpasun nahi, aatach suru zala",
]
MARATHI_NOT = [
    "Chhatit dukhat nahi ani shwas pan vyavasthit aahe, fakt gudghe dukhtat",
]


@pytest.mark.parametrize("text", MARATHI_URGENT)
def test_marathi_signs(text):
    assert red_flag_hits(text) or human_check_hits(text), text


@pytest.mark.parametrize("text", MARATHI_NOT)
def test_marathi_negated_list(text):
    assert red_flag_hits(text) == [], (text, red_flag_hits(text))


# ---- underplay must not reduce escalation
UNDERPLAYED = [
    "Thoda sa hi hai, gas hoga, bas seene mein bhaari lag raha hai abhi se",
    "Kuch khaas nahi, seene mein dabav sa hai",
    "Swalpa ashte, edeyalli bhaara ide",
    "seene mein ajeeb lag raha, theek ho jaayega shayad",
    "probably nothing, no big deal, but his chest feels tight",
]


@pytest.mark.parametrize("text", UNDERPLAYED)
def test_underplay_does_not_cancel(text):
    assert red_flag_hits(text), (text, red_flag_hits(text))


# ---- dates: weekday + offset, onset days, "N in the evening", months
STACKED = [
    "Guruvar ke teen din baad sham 5 baje",
    "somavara aadmele eradu dina nantara",
    "Friday and then 2 days after that",
]
NOT_STACKED = [
    "ivattu sanje inda kaalu novu, naale beligge 11 ge",
    "aaj subah se kamar dard, kal shaam 5 baje",
    "Guruvar shaam 5 baje",
]


@pytest.mark.parametrize("text", STACKED)
def test_weekday_plus_offset_asks(text):
    assert stacked_days(parse(text), REF_D), text


@pytest.mark.parametrize("text", NOT_STACKED)
def test_onset_day_is_not_a_booking_day(text):
    assert stacked_days(parse(text), REF_D) is None, text


def test_number_in_the_evening_is_a_time_not_a_date():
    p = parse("the 3rd of November, six in the evening")
    assert [resolve_day(d, REF_D)[0] for d in p.days] == [date(2026, 11, 3)]
    assert [(t.hour, t.minute) for t in p.times] == [(6, 0)]


@pytest.mark.parametrize("text,expected", [("november 12th", date(2026, 11, 12)), ("12th of november", date(2026, 11, 12)),
                                           ("12th", date(2026, 10, 12))])
def test_month_is_kept(text, expected):
    assert [resolve_day(d, REF_D)[0] for d in parse(text).days] == [expected]
