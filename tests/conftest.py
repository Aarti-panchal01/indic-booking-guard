"""Shared fixtures. MockModel only: no Ollama, no network."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import pytest

BUILD = Path(__file__).resolve().parent.parent
if str(BUILD) not in sys.path:
    sys.path.insert(0, str(BUILD))

from guard.guard import Guard  # noqa: E402
from guard.model import MockModel  # noqa: E402
from guard.register import Register  # noqa: E402
from guard.schema import Decision, Extraction  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
REF = datetime(2026, 10, 7, 20, 40, tzinfo=IST)  # Wednesday


@pytest.fixture
def ref() -> datetime:
    return REF


@pytest.fixture
def register() -> Register:
    return Register()


@pytest.fixture
def decide():
    """decide(utterance, extraction=None, fail_writes=False, ref=None, register=None) -> Decision.

    The register used is available afterwards as `decide.last_register`.
    """

    def _decide(utterance: str, extraction: Optional[Extraction] = None, fail_writes: bool = False,
                ref: Optional[datetime] = None, register: Optional[Register] = None) -> Decision:
        reg = register or Register(fail_writes=fail_writes)
        if register is not None:
            reg.fail_writes = fail_writes
        _decide.last_register = reg
        ex = extraction or Extraction(intent="book")
        when = ref or REF
        mr = MockModel(responses={utterance: ex}).extract(utterance, when)
        return Guard(reg).decide(utterance, when, mr)

    _decide.last_register = None
    return _decide
