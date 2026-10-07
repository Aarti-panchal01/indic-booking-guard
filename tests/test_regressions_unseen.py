"""Regressions from the first run on the 84 unseen golden cases (G112, G130, G140) and held-out v2 (V034)."""
from guard.guard import Guard
from guard.redflags import red_flag_hits
from guard.register import Register
from guard.schema import Extraction, ModelResult

from conftest import REF


def decide(utterance, **ex):
    mr = ModelResult(model="MOCK", extraction=Extraction(intent="book", **ex), mock=True)
    return Guard(Register()).decide(utterance, REF, mr)


def test_model_invented_date_words_are_not_booked():
    # G112: no day said; the model returned date_words "Wednesday" and the dateparser fallback booked Oct 14
    d = decide("namaste, hesaru Padma, sanje aaru baje chahiye, 2 hafte se dard ide",
               patient_name="Padma", date_words="Wednesday", time_words="sanje aaru baje")
    assert (d.action, d.reason) == ("ask_again", "missing_date")
    assert any("not in transcript" in t for t in d.trace)


def test_verbatim_english_date_words_still_used():
    # the fallback still works when the caller really said the words
    d = decide("this is Meera, 19/10/2026 at 10 am please",
               patient_name="Meera", date_words="19/10/2026", time_words="10 am")
    assert (d.action, d.date, d.time) == ("book", "2026-10-19", "10:00")
    assert any("dateparser fallback" in t for t in d.trace)


def test_past_weekday_is_not_the_booking_day():
    # G130: "last Monday ... gir gaye" was read as a second weekday -> weekday_mismatch
    d = decide("last Monday seedhiyon se gir gaye, tab se kandha dukh raha hai, budhvar ko shaam saade chaar baje chahiye, naam Ayesha",
               patient_name="Ayesha")
    assert (d.action, d.reason, d.date, d.time) == ("ask_again", "slot_taken", "2026-10-14", "16:30")
    # V034: Sunday is the booking day; "last Monday" is the fall
    d = decide("Clara here, Sunday 10 am please, I fell last Monday and my hip hurts.", patient_name="Clara")
    assert (d.action, d.reason) == ("ask_again", "closed_day")
    d = decide("pichhle somvar gir gayi thi, shukravar shaam 5 baje, naam Rekha", patient_name="Rekha")
    assert (d.action, d.date, d.time) == ("book", "2026-10-09", "17:00")


def test_shoulder_pain_with_nausea_escalates_inflected():
    # G140: "kandhe" (oblique case) was not in the referred-pain pattern
    assert red_flag_hits("subah se left kandhe mein dard hai aur nausea ho raha hai")
    assert red_flag_hits("baazu mein dard aur ulti jaisa lag raha hai")
    # alone it is a physio complaint
    assert not red_flag_hits("left kandhe mein dard hai, frozen shoulder hai shayad")
