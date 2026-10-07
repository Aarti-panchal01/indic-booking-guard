"""THE safety property: never say "confirmed" unless the register write succeeded."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from guard.guard import Guard
from guard.model import MockModel
from guard.register import Register
from guard.schema import Extraction

GOLDEN = Path(__file__).resolve().parent.parent / "data" / "golden.jsonl"
VALID = "kal shaam 4 baje, naam Ravi"  # Oct 8 16:00: free


def test_write_failure_is_not_confirmed(decide, register):
    d = decide(VALID, fail_writes=True, register=register)
    assert d.action == "write_failed"
    assert d.confirmed is False
    assert "Booked" not in d.say
    assert "Confirmed." not in d.say
    assert "NOT confirmed" in d.say
    # nothing was written
    assert [b for b in register.bookings() if b[2] != "seed"] == []


def test_write_failure_still_reports_resolved_fields(decide):
    d = decide(VALID, fail_writes=True)
    assert (d.name, d.date, d.time) == ("Ravi", "2026-10-08", "16:00")


def test_successful_write_confirms_and_persists(decide, register):
    d = decide(VALID, register=register)
    assert d.action == "book"
    assert d.confirmed is True
    assert "Confirmed." in d.say and "NOT confirmed" not in d.say
    assert ("2026-10-08T16:00", "Ravi", "guard") in register.bookings()
    assert len(register.bookings()) == 10


def test_double_booking_same_slot_fails_second_time(decide, register):
    first = decide(VALID, register=register)
    second = decide("kal shaam 4 baje, naam Sita", register=register)
    assert first.action == "book" and first.confirmed
    assert second.action == "ask_again" and second.reason == "slot_taken"
    assert second.confirmed is False
    assert [b[1] for b in register.bookings() if b[0] == "2026-10-08T16:00"] == ["Ravi"]


def test_race_write_conflict_is_not_confirmed(register, ref):
    """The slot looks free at check time but is taken before the write (another caller)."""
    class RacyRegister(Register):
        def is_taken(self, d, t):
            return False  # check passes, the INSERT then collides with the seeded row

    reg = RacyRegister()
    mr = MockModel().extract("kal subah 10 baje, naam Ravi", ref)  # Oct 8 10:00 is seeded
    d = Guard(reg).decide("kal subah 10 baje, naam Ravi", ref, mr)
    assert d.action == "write_failed"
    assert d.confirmed is False
    assert "NOT confirmed" in d.say


def _golden_cases():
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.mark.parametrize("fail_writes", [False, True])
def test_confirmed_only_when_booked_over_all_golden(fail_writes):
    cases = _golden_cases()
    assert len(cases) >= 72
    for c in cases:
        reg = Register(fail_writes=fail_writes)
        ref = datetime.fromisoformat(c["reference_datetime"])
        mr = MockModel().extract(c["utterance"], ref)
        d = Guard(reg).decide(c["utterance"], ref, mr)
        if d.confirmed:
            assert d.action == "book", (c["id"], d.action)
            assert fail_writes is False, (c["id"], "confirmed although writes fail")
            assert "Confirmed." in d.say
        else:
            assert "Confirmed." not in d.say and "Booked" not in d.say, (c["id"], d.say)
        if d.action == "write_failed":
            assert "NOT confirmed" in d.say
        # a booking is only reported if a row exists
        if d.action == "book":
            assert any(b[2] == "guard" for b in reg.bookings()), c["id"]
        else:
            assert not any(b[2] == "guard" for b in reg.bookings()), (c["id"], d.action)


def test_fail_writes_turns_every_golden_book_into_write_failed_not_book():
    for c in _golden_cases():
        ref = datetime.fromisoformat(c["reference_datetime"])
        ok = Guard(Register()).decide(c["utterance"], ref, MockModel().extract(c["utterance"], ref))
        bad = Guard(Register(fail_writes=True)).decide(c["utterance"], ref, MockModel().extract(c["utterance"], ref))
        if ok.action == "book":
            assert bad.action == "write_failed", c["id"]
        else:
            assert bad.action == ok.action and bad.reason == ok.reason, c["id"]
