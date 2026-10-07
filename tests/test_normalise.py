"""TAXONOMY section 3 rules, via parse/resolve_* and via the full guard."""
from datetime import date, time

import pytest

from guard.normalise import parse, resolve_day, resolve_time
from guard.register import Register

REF_D = date(2026, 10, 7)  # Wednesday
REG = Register()


def in_session(h, m):
    return REG.in_session(time(h, m))


def day_of(text, ref=REF_D):
    p = parse(text)
    assert p.days, f"no day parsed from {text!r}"
    return resolve_day(p.days[-1], ref)


def time_of(text):
    p = parse(text)
    assert p.times, f"no time parsed from {text!r}"
    return resolve_time(p.times[-1], in_session)


# ---- 3.1 days
@pytest.mark.parametrize("text,expected", [
    ("kal", date(2026, 10, 8)),
    ("naale", date(2026, 10, 8)),
    ("nale", date(2026, 10, 8)),
    ("tomorrow", date(2026, 10, 8)),
    ("parso", date(2026, 10, 9)),
    ("parson", date(2026, 10, 9)),
    ("naadidu", date(2026, 10, 9)),
    ("day after tomorrow", date(2026, 10, 9)),
    ("aaj", date(2026, 10, 7)),
    ("indu", date(2026, 10, 7)),
    ("today", date(2026, 10, 7)),
])
def test_relative_days(text, expected):
    assert day_of(text) == (expected, None)


@pytest.mark.parametrize("text,expected", [
    ("budhvar", date(2026, 10, 14)),      # Wed said on Wed = +7
    ("Wednesday", date(2026, 10, 14)),
    ("budhwar", date(2026, 10, 14)),
    ("guruvar", date(2026, 10, 8)),
    ("shukravara", date(2026, 10, 9)),
    ("somvar", date(2026, 10, 12)),
    ("ravivar", date(2026, 10, 11)),
    ("Monday", date(2026, 10, 12)),
])
def test_bare_weekday_strictly_after_reference(text, expected):
    assert day_of(text) == (expected, None)


@pytest.mark.parametrize("text,expected", [
    ("agle hafte somvar", date(2026, 10, 12)),
    ("agle hafte shukravar", date(2026, 10, 16)),
    ("mundina vaara shukravara", date(2026, 10, 16)),
    ("Friday next week", date(2026, 10, 16)),
])
def test_next_week_weekday(text, expected):
    assert day_of(text) == (expected, None)


@pytest.mark.parametrize("text", ["next Friday", "agle shukravar", "mundina shukravara"])
def test_next_friday_on_wednesday_is_ambiguous(text):
    assert day_of(text) == (None, "ambiguous_date")


@pytest.mark.parametrize("text", ["next Monday", "agle somvar", "mundina somavara"])
def test_next_monday_on_wednesday_is_unambiguous(text):
    assert day_of(text) == (date(2026, 10, 12), None)


@pytest.mark.parametrize("text,ref,expected", [
    ("10 tareekh", REF_D, date(2026, 10, 10)),
    ("7 tareekh", REF_D, date(2026, 10, 7)),
    ("3 tareekh", REF_D, date(2026, 11, 3)),          # rolls to next month
    ("5th", REF_D, date(2026, 11, 5)),
    ("October 20", REF_D, date(2026, 10, 20)),
    ("12 ne tareeku", REF_D, date(2026, 10, 12)),
    ("2 tareekh", date(2026, 12, 20), date(2027, 1, 2)),  # rolls over the year
])
def test_n_tareekh(text, ref, expected):
    assert day_of(text, ref) == (expected, None)


# ---- 3.3 hours and fractions
@pytest.mark.parametrize("text,hm", [
    ("shaam saade chaar baje", (16, 30)),
    ("shaam sawa paanch baje", (17, 15)),
    ("shaam paune paanch baje", (16, 45)),
    ("dopahar paune ek baje", (12, 45)),
    ("dopahar dedh baje", (13, 30)),
    ("dopahar dhai baje", (14, 30)),
    ("subah saade dus baje", (10, 30)),
    ("sanje naalku uvare", (16, 30)),
    ("sanje naalkuvare gantege", (16, 30)),
    ("sanje naalku-vare gantege", (16, 30)),
    ("sanje naalakkuvare gantege", (16, 30)),
    ("sanje 4-vare gantege", (16, 30)),
    ("sanje naalku kaalu gantege", (16, 15)),
    ("sanje naalku mukkaalu gantege", (16, 45)),
    ("sanje aaru gantege", (18, 0)),
    ("beligge hattu gantege", (10, 0)),
])
def test_fractions_and_dayparts(text, hm):
    assert time_of(text) == (hm, None)


@pytest.mark.parametrize("text", ["shaam 10 baje", "subah 4 baje", "dopahar 9 baje"])
def test_daypart_conflict_is_ambiguous_time(text):
    assert time_of(text)[1] == "ambiguous_time"


def test_daypart_fits_but_closed_is_outside_hours_in_guard(decide):
    d = decide("kal subah 7 baje, naam Ravi")
    assert (d.action, d.reason) == ("ask_again", "outside_hours")


@pytest.mark.parametrize("text,hm", [
    ("4 baje", (16, 0)),       # 04:00 closed, 16:00 open
    ("10 baje", (10, 0)),
    ("11 baje", (11, 0)),
    ("5 baje", (17, 0)),
    ("7 baje", (19, 0)),
    ("4:30", (16, 30)),
    ("4.30", (16, 30)),
])
def test_bare_hour_resolved_by_clinic_hours(text, hm):
    assert time_of(text) == (hm, None)


@pytest.mark.parametrize("text", ["8 baje", "2 baje"])
def test_bare_hour_nothing_fits_is_outside_hours(text):
    got, prob = time_of(text)
    assert prob == "outside_hours"


@pytest.mark.parametrize("text,hm", [
    ("4 pm", (16, 0)),
    ("4 am", (4, 0)),
    ("10 am", (10, 0)),
    ("6pm", (18, 0)),
    ("12 pm", (12, 0)),
])
def test_explicit_ampm_is_trusted(text, hm):
    assert time_of(text) == (hm, None)


# ---- through the guard
def test_4am_is_outside_hours(decide):
    d = decide("kal 4 am, naam Ravi")
    assert (d.action, d.reason) == ("ask_again", "outside_hours")


@pytest.mark.parametrize("utt,date_,time_", [
    ("parso shaam saade chaar baje appointment chahiye, naam Ramesh hai", "2026-10-09", "16:30"),
    ("naadidu sanje naalku-vare gantege, nanna hesaru Rashmi", "2026-10-09", "16:30"),
    ("parso subah gyarah baje, naam Asha", "2026-10-09", "11:00"),
    ("naadidu beligge hattu gantege, naanu Kiran", "2026-10-09", "10:00"),
    ("agle hafte somvar subah 11 baje, mera naam Sunil hai", "2026-10-12", "11:00"),
    ("next Monday at 5 pm, my name is Priya", "2026-10-12", "17:00"),
    ("budhvar shaam paune paanch baje, naam Meena", "2026-10-14", "16:45"),
    ("10 tareekh subah 9 baje, naam Vikram", "2026-10-10", "09:00"),
    ("3 tareekh subah 9 baje, naam Vikram", "2026-11-03", "09:00"),
    ("kal dopahar paune ek baje, naam Zoya", "2026-10-08", "12:45"),
])
def test_guard_resolves_to_label(decide, utt, date_, time_):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", date_, time_), d.trace


def test_dedh_baje_1330_is_outside_hours_in_guard(decide):
    d = decide("kal dopahar dedh baje, naam Zoya")
    assert (d.action, d.reason, d.time) == ("ask_again", "outside_hours", "13:30")


def test_next_friday_asks_again_in_guard(decide):
    d = decide("next Friday 5 pm, my name is Anil")
    assert (d.action, d.reason) == ("ask_again", "ambiguous_date")


def test_next_week_friday_books_oct_16(decide):
    d = decide("Friday next week 5 pm, my name is Anil")
    assert (d.action, d.date) == ("book", "2026-10-16")


def test_budhvar_on_wednesday_is_plus_seven(decide):
    d = decide("budhvar subah 10 baje, naam Gita")
    assert (d.action, d.date) == ("book", "2026-10-14")


def test_kal_se_dard_is_not_a_day(decide):
    d = decide("kal se kamar mein dard hai, parso subah 10 baje aana hai, naam Mohan")
    assert (d.action, d.date, d.time) == ("book", "2026-10-09", "10:00"), d.trace
    assert parse("kal se dard hai").days == []


def test_kal_raat_se_is_not_a_day():
    assert parse("kal raat se dard hai").days == []


@pytest.mark.parametrize("utt,date_,time_", [
    ("kal 5 baje, nahi nahi, 6 baje, naam Ravi", "2026-10-08", "18:00"),
    ("naale, alla alla, naadidu subah 10 gantege, naanu Raju", "2026-10-09", "10:00"),
    ("kal subah 10 baje, sorry, parso subah 11 baje, naam Ravi", "2026-10-09", "11:00"),
])
def test_self_correction_last_value_wins(decide, utt, date_, time_):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", date_, time_), d.trace


@pytest.mark.parametrize("utt", [
    "kal kal shaam shaam 4 baje, naam Ravi",
    "kal kal kal shaam 4 baje 4 baje, naam Ravi",
])
def test_asr_repeats_mean_same_as_one(decide, utt):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", "2026-10-08", "16:00"), d.trace


@pytest.mark.parametrize("utt", [
    "parso sham 4.30 baje, naam Ravi",
    "parson shaam 4:30 baje, naam Ravi",
    "naadidu sanje naalku-vare ganteg, naanu Ravi",
    "nadidu sanje naalakkuvare gantege, naanu Ravi",
])
def test_spelling_variants(decide, utt):
    d = decide(utt)
    assert (d.action, d.date, d.time) == ("book", "2026-10-09", "16:30"), d.trace


# Regression (was BUG 1, fixed 22:3x Oct 7): ":30" was dropped and 16:00 confirmed.
def test_space_separated_hour_minute_with_daypart(decide):
    d = decide("kal shaam 5 30 baje, naam Ravi")
    assert (d.action, d.time) == ("book", "17:30")


# Regression (was BUG 1b): no time parsed without a day-part.
def test_space_separated_hour_minute_bare(decide):
    d = decide("kal 5 30 baje, naam Ravi")
    assert (d.action, d.time) == ("book", "17:30")
