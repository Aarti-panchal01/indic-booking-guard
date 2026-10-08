"""POST /book over HTTP with the MockModel (no Ollama). The guard logic itself is tested elsewhere."""
from fastapi.testclient import TestClient

from api import create_app
from guard.model import MockModel
from guard.register import Register
from guard.schema import Extraction

REF = "2026-10-07T20:40:00+05:30"


def client(**kw) -> TestClient:
    return TestClient(create_app(model=MockModel(fn=lambda u, r: Extraction(intent="book", patient_name="Ramesh")), **kw))


def test_book_then_same_slot_is_taken():
    c = client()
    body = {"utterance": "kal shaam saade chaar baje appointment chahiye, naam Ramesh hai", "reference_datetime": REF}
    r1 = c.post("/book", json=body).json()
    assert r1["mock"] is True
    # 2026-10-08 16:30 is seeded as taken in clinic.json
    assert (r1["decision"]["action"], r1["decision"]["reason"], r1["decision"]["confirmed"]) == ("ask_again", "slot_taken", False)

    free = {"utterance": "kal shaam sawa paanch baje, naam Ramesh", "reference_datetime": REF}
    r2 = c.post("/book", json=free).json()["decision"]
    assert (r2["action"], r2["date"], r2["time"], r2["confirmed"]) == ("book", "2026-10-08", "17:15", True)
    r3 = c.post("/book", json=free).json()["decision"]
    assert (r3["action"], r3["reason"]) == ("ask_again", "slot_taken")
    assert {"slot": "2026-10-08T17:15", "name": "Ramesh", "source": "guard"} in c.get("/bookings").json()["bookings"]


def test_red_flag_escalates_and_failed_write_is_not_confirmed():
    c = client()
    esc = c.post("/book", json={"utterance": "seene mein dard ho raha hai, kal 5 baje aana hai", "reference_datetime": REF}).json()
    assert esc["decision"]["action"] == "escalate"
    assert esc["decision"]["confirmed"] is False

    failing = client(register=Register(fail_writes=True))
    wf = failing.post("/book", json={"utterance": "parso subah 10 baje, naam Ramesh", "reference_datetime": REF}).json()["decision"]
    assert (wf["action"], wf["confirmed"]) == ("write_failed", False)
    assert all(b["source"] == "seed" for b in failing.get("/bookings").json()["bookings"])
