"""Red flags: every sign family escalates; physio pain does not; escalate beats booking and tool failure."""
import pytest

from guard.redflags import red_flag_hits

VALID = "kal shaam 4 baje, naam Ravi"

# (family, phrase)
ESCALATE = [
    # chest pain
    ("chest_pain", "mujhe seene mein dard ho raha hai"),
    ("chest_pain", "papa ko chhati mein dard hai subah se"),
    ("chest_pain", "chhati mein bhaaripan lag raha hai"),
    ("chest_pain", "amma ge ede novu ide"),
    ("chest_pain", "edeli novu aagtide"),
    ("chest_pain", "he has chest pain since morning"),
    ("chest_pain", "I feel pain in my chest"),
    ("chest_pain", "chest discomfort and heaviness"),
    ("chest_pain", "सीने में दर्द है"),
    ("chest_pain", "छाती में भारीपन है"),
    # breathing
    ("breathing", "saans lene mein takleef ho rahi hai"),
    ("breathing", "mummy ki saans phool rahi hai"),
    ("breathing", "usiru kattide amma ge"),
    ("breathing", "usiraadoke aagtilla"),
    ("breathing", "she has difficulty breathing"),
    ("breathing", "he is breathless since night"),
    ("breathing", "सांस लेने में तकलीफ है"),
    # cold sweat
    ("cold_sweat", "thanda paseena aa raha hai"),
    ("cold_sweat", "thandi paseena aur haath mein dard"),
    ("cold_sweat", "tanna bevaru bartide"),
    ("cold_sweat", "he is in a cold sweat"),
    ("cold_sweat", "ठंडा पसीना आ रहा है"),
    # stroke
    ("face_droop", "chehra tedha ho gaya hai"),
    ("face_droop", "munh tedha lag raha hai achanak"),
    ("face_droop", "mukha sottagide ajji ge"),
    ("face_droop", "her face is drooping"),
    ("face_droop", "चेहरा टेढ़ा हो गया है"),
    ("one_side_weak", "haath sunn ho gaya hai"),
    ("one_side_weak", "ek taraf kamzori hai achanak"),
    ("one_side_weak", "kai jom hidide"),
    ("one_side_weak", "ondu kade shakti illa"),
    ("one_side_weak", "sudden weakness on one side"),
    ("speech", "bolne mein dikkat ho rahi hai"),
    ("speech", "zabaan ladkhada rahi hai"),
    ("speech", "maatadoke aagtilla"),
    ("speech", "he has slurred speech"),
    ("speech", "बोलने में दिक्कत है"),
    ("vision", "achanak dikhna band ho gaya"),
    ("vision", "sudden vision loss in one eye"),
    ("headache", "bahut tez sar dard achanak se"),
    ("headache", "severe headache sudden"),
    ("headache", "tumba tale novu bartide"),
    ("faint", "papa behosh ho gaye the"),
    ("faint", "she fainted yesterday"),
    ("faint", "prajne tappide"),
    ("faint", "वो बेहोश हो गए"),
    # arm / jaw pain WITH nausea or sweat
    ("referred", "left arm pain and ulti jaisa lag raha hai"),
    ("referred", "haath mein dard aur vomiting"),
    ("referred", "jaw pain with nausea since last night"),
]


@pytest.mark.parametrize("family,phrase", ESCALATE, ids=[p for _, p in ESCALATE])
def test_red_flag_phrase_hits_and_escalates(decide, family, phrase):
    assert red_flag_hits(phrase), f"{family}: no hit for {phrase!r}"
    d = decide(f"{phrase}, {VALID}")
    assert d.action == "escalate"
    assert d.confirmed is False
    assert "108" in d.say


NO_ESCALATE = [
    "meri kamar mein dard hai",
    "kamar dard hai kal se",
    "mere knee mein dard hai",
    "ghutne mein dard hai",
    "right shoulder pain hai",
    "kandha dard hai",
    "left shoulder pain alone, since gym",
    "neck pain from desk work",
    "gardan dard hai",
    "sonta novu ide",
    "mandi novu ide",
    "chest physiotherapy ke liye aana hai",
    "breathing exercises sikhane hain",
    "seene mein dard nahi hai, sirf kamar dard",
    "last year chest pain tha, ab theek hai, ab knee ke liye",
    "frozen shoulder and sciatica",
    "ankle sprain after football",
    "tingling in fingers from typing",
]


@pytest.mark.parametrize("phrase", NO_ESCALATE)
def test_pain_not_red_flag_negatives(decide, phrase):
    assert red_flag_hits(phrase) == []
    d = decide(f"{phrase}, {VALID}")
    assert d.action == "book", d.trace


def test_arm_pain_alone_does_not_escalate():
    assert red_flag_hits("haath mein dard hai") == []
    assert red_flag_hits("pain in my left arm after lifting") == []


def test_escalate_beats_valid_booking(decide, register):
    d = decide("seene mein dard hai, kal shaam 4 baje, naam Ravi", register=register)
    assert d.action == "escalate"
    assert [b for b in register.bookings() if b[2] == "guard"] == []


def test_escalate_beats_tool_failure(decide):
    d = decide("seene mein dard hai, kal shaam 4 baje, naam Ravi", fail_writes=True)
    assert d.action == "escalate"
    assert "NOT confirmed" not in d.say


def test_escalate_beats_handoff_and_ask_again(decide):
    assert decide("chest pain, cancel my appointment").action == "escalate"
    assert decide("saans phool rahi hai").action == "escalate"


def test_model_red_flag_alone_escalates(decide):
    from guard.schema import Extraction
    d = decide(VALID, Extraction(intent="book", red_flag=True))
    assert d.action == "escalate"


# Negation is a 30-char look-ahead that fires on any "nahi/not/theek" within 2 words, so a
# real symptom followed by an unrelated negative is swallowed. Each of these is a live chest
# pain report that the guard lets through to booking.
MISSED_BY_NEGATION = [
    "chest pain, not going away",
    "chest pain hai, theek nahi lag raha",
    "papa ko seene mein dard hai, hospital nahi gaye",
    "mere seene mein dard hai theek nahi hota",
]


@pytest.mark.parametrize("phrase", MISSED_BY_NEGATION)
# Regression (was BUG 2, fixed Oct 7): an unrelated later "nahi/not/theek" used to cancel the red flag.
def test_symptom_followed_by_unrelated_negative_still_escalates(decide, phrase):
    d = decide(f"{phrase}, {VALID}")
    assert d.action == "escalate"
