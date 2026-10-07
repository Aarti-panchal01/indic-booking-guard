"""The clinic register (system of record), in SQLite.

Deterministic. Shared by every system in the eval (raw model, dateparser baseline,
guard), so differences between them come from date/time resolution and the
guard's checks, not from one system having a register and another not.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Optional

DATA = Path(__file__).resolve().parent.parent / "data"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class RegisterWriteError(Exception):
    """The write to the register failed (timeout, 500, lock)."""


def load_clinic(path: Path = DATA / "clinic.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class Register:
    def __init__(self, clinic: Optional[dict] = None, db_path: str = ":memory:", fail_writes: bool = False):
        self.clinic = clinic or load_clinic()
        self.fail_writes = fail_writes  # simulate a tool failure
        self.db = sqlite3.connect(db_path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS bookings (slot TEXT PRIMARY KEY, name TEXT NOT NULL, source TEXT NOT NULL)"
        )
        for slot in self.clinic["booked"]:
            self.db.execute("INSERT OR IGNORE INTO bookings VALUES (?, ?, ?)", (slot, "existing", "seed"))
        self.db.commit()
        self.sessions = [(time.fromisoformat(s["start"]), time.fromisoformat(s["end"])) for s in self.clinic["sessions"]]
        self.slot_minutes = int(self.clinic["slot_minutes"])

    # ---- checks (pure reads) ----
    def is_closed_day(self, d: date) -> bool:
        return WEEKDAYS[d.weekday()] in self.clinic["closed_weekdays"]

    def in_session(self, t: time) -> bool:
        if (t.hour * 60 + t.minute) % self.slot_minutes or t.second:
            return False
        for start, end in self.sessions:
            last = (datetime.combine(date.min, end) - timedelta(minutes=self.slot_minutes)).time()
            if start <= t <= last:
                return True
        return False

    def is_taken(self, d: date, t: time) -> bool:
        slot = f"{d.isoformat()}T{t.strftime('%H:%M')}"
        return self.db.execute("SELECT 1 FROM bookings WHERE slot = ?", (slot,)).fetchone() is not None

    def slot_problem(self, d: date, t: time) -> Optional[str]:
        """None if the slot can be booked, else the TAXONOMY reason code."""
        if self.is_closed_day(d):
            return "closed_day"
        if not self.in_session(t):
            return "outside_hours"
        if self.is_taken(d, t):
            return "slot_taken"
        return None

    # ---- the write (the action with real cost) ----
    def book(self, d: date, t: time, name: str, source: str = "agent") -> str:
        if self.fail_writes:
            raise RegisterWriteError("register write timed out")
        slot = f"{d.isoformat()}T{t.strftime('%H:%M')}"
        try:
            self.db.execute("INSERT INTO bookings VALUES (?, ?, ?)", (slot, name, source))
            self.db.commit()
        except sqlite3.IntegrityError as e:
            raise RegisterWriteError(f"slot already taken: {slot}") from e
        return slot

    def bookings(self) -> list[tuple[str, str, str]]:
        return self.db.execute("SELECT slot, name, source FROM bookings ORDER BY slot").fetchall()
