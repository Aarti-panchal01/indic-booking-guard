# Provenance of the held-out sets and blind probes

This repository was split out of a private working repo (`git subtree split` of its `build/` folder), so every commit
hash changed. The private repo kept a running log (STATE.md, not published) where each held-out file and blind probe was
recorded with its sha256 at the moment it was committed, before the guard was run on it. Those records are copied here.

"Recorded" is the sha256 written into the log or the commit message at commit time. "Matches" means the file in this
repository today has exactly that sha256 (checked when this file was generated). "Added in" and "first run with guard"
are the new hashes in this repository.

| File | Cases | sha256 recorded at commit time | Recorded at | Added in | First run with guard | Matches today |
|---|---|---|---|---|---|---|
| `data/held_out.jsonl` | 24 (H001-H024) | `6d865a7cbf5a57c5dcbb4c1239912ab11d3af62b6f48a0ac17c127813a8f1844` | 2026-10-07 22:08 IST | `f336251` | `563f11e` | yes |
| `data/held_out_v2.jsonl` | 48 (V001-V048) | `5d435d314b5ea874ecf34ded8a3ec837a7fd52f23ac21e77e18d3f6c73540678` | 2026-10-07 22:46 IST | `f58148b` | `134afc9` | yes |
| `data/golden.jsonl (grown to 156)` | 84 new (G073-G156) | `6b4d9be411c32bbd3b469fbec0ab20dbc121784b603ab112f5717cb0dcadb5b7` | 2026-10-07 22:48 IST | `31c162c` | `134afc9` | yes |
| `data/oov_probe.jsonl` | 45 (P001-P045) | `f8515d6ed0beebe87da777dd7f9aabddb8f687ca6971a3b9282247e4a593e619` | 2026-10-07 22:58 IST | `f559d02` | `b17251e` | yes |
| `data/oov_probe_v2.jsonl` | 50 (Q001-Q050) | `a35787f53ead17b589f44cd4403a7a81c8dc082cd222d89bc2ae1c26e6905b10` | 2026-10-07 23:24 IST | `9a6cdc1` | `021e809` | yes |
| `data/oov_probe_v3.jsonl` | 60 (R001-R060) | `ba3f0ceca7b6a13decb562b145f369ee1e60c9118dc334f92493e65a1cfc830d` | 2026-10-07 23:39 IST | `24d0fd1` | `e9af785` | yes |
| `data/oov_probe_v4.jsonl` | 60 (S001-S060) | `d19fd55c7e5e032eb7a517adabccfa5c343204faccd8a3cc543897297f506d9c` | 2026-10-08 00:00 IST | `fff8de7` | `b485dac` | yes |
| `data/oov_probe_v5.jsonl` | 60 (T001-T060) | `1082f45b23a9b70e0f393a0e095fd5dc6c9dda64d2773c12f4d1ebd814627b97` | 2026-10-08 01:51 IST | `7172343` | `333fae9` | yes |
| `data/oov_probe_v6.jsonl` | 60 (T001-T060) | `0867384be8b046be519de6c0810e3ab3be772b01666aab17ed21131b99d14761` | 2026-10-08 11:42 IST | `84e2020` | `84ae5c2` | yes |
| `data/oov_probe_v7.jsonl` | 60 (T001-T060) | `e3733e85d934e3a9ae107e286aa85dcbd010aaa5fbe14d8a979d8e25ecf1aa9e` | 2026-10-08 13:22 IST | `b2e350b` | `280db73` | yes |

The first 72 golden cases (G001-G072, commit `ba9d688`) were written before any guard code, but their sha256 was not
logged at the time; computed from git on 2026-10-08: `6397dd4ebffebe1e8fe249a19b164b8932528c29ce780a718deac1efcb4ee8f2`.

## Old to new commit hashes cited in the README and eval files

| Private repo | This repo | What it is |
|---|---|---|
| `b721436` | `563f11e` | Guard iteration 2: question/other intent with a day/time is a booking request (main set 60 |
| `00f0c25` | `134afc9` | Phase 3 stretch: FastAPI POST /book + GET /bookings wrapper, 2 HTTP tests (mock model); re |
| `759faf4` | `b17251e` | STATE: golden first-run failures; OOV must run on frozen guard |
| `92dcbd9` | `021e809` | Guard fixes from blind OOV probe v1: partial-parse rule (unconsumed time modifier near a t |
| `2f4b7be` | `e9af785` | Guard fixes from blind OOV v2: structural partial-parse rule (unconsumed number or qualifi |
| `0a55b09` | `b485dac` | Guard: allowlist window (polarity flip after 3 blind OOV probes). Before a write, every to |
| `5903181` | `333fae9` | Second model (qwen2.5-coder:7b, all 443 cases) through the same guard; found V031 (model r |
| `180bd58` | `84ae5c2` | Red flags: body-part x symptom on stems, list negation, past history, jaw/left-arm option  |
| `5ef403e` | `280db73` | Guard round 2: urgent vs human-check tiers, loss of function, Marathi (AI-written), underp |

`759faf4` was a log-only commit in the private repo; the guard code at that moment is identical to the commit it maps to
(empty diff of `build/`). Commit messages in this history still mention the old hashes; use this table to translate.
