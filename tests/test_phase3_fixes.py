"""Regression tests for the Oct 8 red-flag and stacked-day fixes (Phase 3).

Every phrase here is NEW wording written for these tests, not copied from any probe or golden file.
One test group per rule: co-occurrence, stems, list negation, past history, option (b) jaw / left arm,
sudden limb weakness, and stacked day expressions.
"""
from datetime import date

import pytest

from guard.guard import stacked_days
from guard.normalise import parse
from guard.redflags import red_flag_hits

VALID = "kal shaam 4 baje, naam Ravi"

# rule 1: body part near a symptom word, not an exact phrase
COOCCUR = [
    "uske chhaati ke andar ajeeb sa bhaaripan hai",
    "my mother says her breath keeps getting short",
    "mama ka dum ghut raha hai baithe baithe",
    "his left eye went blurry a few minutes ago",
    "her mouth is drooping to the right",
    "appa ka awaaz achanak ajeeb ho gaya",
    "one side of his body went numb",
    "thatha ge kannu kaanisuthilla eega",
]

# rule 2: inflected stems
STEMS = [
    "avarige edegu novu ide",
    "seeney ke beech dard uth raha hai",
    "yedeyalli bhaara ide swalpa",
]

# rule 3: one negation covers a list, only when the words between are symptoms and joiners
LIST_NEGATED = [
    "No chest tightness, no sweating and no breathing trouble, just stiff knees",
    "Seene mein dard ya saans ki takleef kuch nahi hai, bas ghutna",
    "edeyalli novu mattu bevaru enu illa, sonta novu ashte",
]
NEGATION_UNCLEAR = [  # something other than symptoms sits between, so it escalates
    "No fever but my chest feels tight since an hour",
    "no x-ray done yet, seene mein dard hai abhi",
    "No, it is not the knee, mere seene mein dard hai",
]

# rule 4: past history does not escalate unless a current symptom is also present
PAST_ONLY = [
    "Do saal pehle bypass hua tha aur tab seene mein dard tha, ab sirf kamar ke liye aana hai",
    "Five years back he had a stroke, now he walks fine, need physio for the knee",
]
PAST_AND_NOW = [
    "Teen saal pehle attack aaya tha aur abhi phir se seene mein dabav lag raha hai",
]

# option (b): jaw or left-arm pain alone escalates; plain arm or shoulder pain with a reason does not
JAW_LEFT_ARM = [
    "Since twenty minutes my jaw is aching badly",
    "Pati ke baayein haath mein dard ho raha hai",
    "edagai novu from the morning",
]
NOT_JAW_LEFT_ARM = [
    "Right arm pain after carrying a suitcase",
    "Left shoulder pain since my badminton game",
    "jaw pain after the dentist pulled my tooth",
    "kai din se left arm me halka dard hai",
]

# a limb that suddenly cannot move escalates; frozen shoulder does not
LIMB_SUDDEN = ["Achanak se unka pair hil nahi raha"]
LIMB_PHYSIO = ["Frozen shoulder hai, haath upar uth nahi raha, dard bhi hai"]


@pytest.mark.parametrize("text", COOCCUR + STEMS + NEGATION_UNCLEAR + PAST_AND_NOW + JAW_LEFT_ARM + LIMB_SUDDEN)
def test_escalates(text):
    assert red_flag_hits(text), text


@pytest.mark.parametrize("text", LIST_NEGATED + PAST_ONLY + NOT_JAW_LEFT_ARM + LIMB_PHYSIO)
def test_does_not_escalate(text):
    assert red_flag_hits(text) == [], (text, red_flag_hits(text))


@pytest.mark.parametrize("text", COOCCUR[:3] + JAW_LEFT_ARM[:1])
def test_escalation_beats_a_valid_booking(decide, text):
    assert decide(f"{VALID}. {text}").action == "escalate"


def test_service_request_is_not_a_symptom():
    assert red_flag_hits("chest physiotherapy ke liye slot chahiye") == []


def test_mother_in_law_is_not_breath():
    # "saas" (mother-in-law) must not be read as "saans" (breath)
    assert red_flag_hits("meri saas ko ghutne mein dikkat hai") == []


def test_comma_part_bounds_pairs():
    # "dikkat" belongs to the first part; "saans" to the second, which says it is fine
    assert red_flag_hits("Seene mein koi takleef nahi hai, saans bhi bilkul theek hai, bas peeth dard") == []


# rule 5: stacked day expressions
REF_D = date(2026, 10, 7)
STACKED = [
    "parso ke teen din baad sham ko",
    "kal se do din baad subah",
    "naale inda mooru dina nantara",
    "tomorrow then after 2 days",
]
NOT_STACKED = [
    "aaj se teen din baad shaam ko",
    "kal, haan kal hi",
    "kal nahi, parso",
    "tomorrow, no wait, the day after tomorrow",
    "pain since the 2nd. Book me for the 15th",
]


@pytest.mark.parametrize("text", STACKED)
def test_stacked_days_ask_again(text):
    assert stacked_days(parse(text), REF_D), text


@pytest.mark.parametrize("text", NOT_STACKED)
def test_not_stacked(text):
    assert stacked_days(parse(text), REF_D) is None, text


def test_stacked_days_never_books(decide):
    d = decide("parso ke teen din baad subah 11 baje, naam Meena")
    assert d.action == "ask_again" and d.reason == "ambiguous_date" and d.date is None
