"""Register: session boundaries, closed day, seeded slots."""
from datetime import date, time

import pytest

from guard.register import Register, RegisterWriteError

OPEN_DAY = date(2026, 10, 13)  # Tuesday, nothing seeded


@pytest.mark.parametrize("hhmm,ok", [
    ("09:00", True), ("12:45", True), ("13:00", False), ("16:00", True),
    ("19:45", True), ("20:00", False), ("16:20", False), ("08:45", False),
    ("12:59", False), ("15:45", False), ("00:00", False), ("09:15", True),
])
def test_session_boundaries(register, hhmm, ok):
    assert register.in_session(time.fromisoformat(hhmm)) is ok


def test_seconds_are_not_on_a_slot(register):
    assert register.in_session(time(10, 0, 30)) is False


def test_sunday_closed(register):
    assert register.is_closed_day(date(2026, 10, 11)) is True
    assert register.slot_problem(date(2026, 10, 11), time(10, 0)) == "closed_day"


@pytest.mark.parametrize("d", [date(2026, 10, 12), date(2026, 10, 13), date(2026, 10, 10)])
def test_other_days_open(register, d):
    assert register.is_closed_day(d) is False


@pytest.mark.parametrize("slot", [
    "2026-10-08T10:00", "2026-10-08T16:30", "2026-10-08T17:00", "2026-10-09T09:30",
    "2026-10-09T18:00", "2026-10-10T11:00", "2026-10-10T16:00", "2026-10-12T10:00", "2026-10-14T16:30",
])
def test_seeded_slots_taken(register, slot):
    d, t = slot.split("T")
    assert register.is_taken(date.fromisoformat(d), time.fromisoformat(t)) is True
    assert register.slot_problem(date.fromisoformat(d), time.fromisoformat(t)) == "slot_taken"


def test_free_slot_not_taken(register):
    assert register.is_taken(OPEN_DAY, time(10, 0)) is False
    assert register.slot_problem(OPEN_DAY, time(10, 0)) is None


def test_slot_problem_order_closed_then_hours_then_taken(register):
    assert register.slot_problem(date(2026, 10, 11), time(2, 0)) == "closed_day"
    assert register.slot_problem(OPEN_DAY, time(2, 0)) == "outside_hours"


def test_book_writes_row_and_marks_taken(register):
    slot = register.book(OPEN_DAY, time(10, 0), "Ravi")
    assert slot == "2026-10-13T10:00"
    assert register.is_taken(OPEN_DAY, time(10, 0))
    assert ("2026-10-13T10:00", "Ravi", "agent") in register.bookings()


def test_double_book_raises(register):
    register.book(OPEN_DAY, time(10, 0), "Ravi")
    with pytest.raises(RegisterWriteError):
        register.book(OPEN_DAY, time(10, 0), "Sita")


def test_booking_a_seeded_slot_raises(register):
    with pytest.raises(RegisterWriteError):
        register.book(date(2026, 10, 8), time(10, 0), "Ravi")


def test_fail_writes_raises_and_writes_nothing():
    reg = Register(fail_writes=True)
    before = reg.bookings()
    with pytest.raises(RegisterWriteError):
        reg.book(OPEN_DAY, time(10, 0), "Ravi")
    assert reg.bookings() == before


def test_registers_are_independent():
    a, b = Register(), Register()
    a.book(OPEN_DAY, time(10, 0), "Ravi")
    assert b.is_taken(OPEN_DAY, time(10, 0)) is False


def test_nine_seeded_rows_only(register):
    assert len(register.bookings()) == 9
