# Blind ledger (recomputed by `python -I eval/ledger.py` from the committed blind-run files)

| Blind run | Guard at | Cases | Guard correct | Guard wrong bookings | Guard missed emergencies | Raw model wrong bookings | dateparser wrong bookings | Raw / dateparser correct |
|---|---|---|---|---|---|---|---|---|
| Held-out v1 (spec vocabulary) [from RESULTS_v1_frozen_563f11e.md] | `563f11e` | 24 | 23 | 1 | 0/3 | 8 | 1 | 4 / 1 |
| Golden G073 to G156, first run | `134afc9` | 84 | 81 | 1 | 1/10 | 26 | 3 | 16 / 15 |
| Held-out v2 (spec vocabulary, adversarial) | `134afc9` | 48 | 47 | 0 | 0/6 | 17 | 1 | 12 / 9 |
| OOV probe v1 | `b17251e` | 45 | 24 | 1 | 3/7 | 11 | 0 | 14 / 10 |
| OOV probe v2 | `021e809` | 50 | 31 | 6 | 4/8 | 12 | 2 | 12 / 10 |
| OOV probe v3 | `e9af785` | 60 | 25 | 7 | 3/9 | 19 | 0 | 17 / 13 |
| OOV probe v4, after the allowlist change | `b485dac` | 60 | 35 | 1 | 1/7 | 14 | 0 | 16 / 15 |
| OOV probe v5, second run of the allowlist guard | `333fae9` | 60 | 33 | 0 | 4/7 | 7 | 1 | 21 / 14 |
| OOV probe v6, after the red-flag and stacked-day fix (18 emergencies) | `84ae5c2` | 60 | 45 | 1 | 6/18 | 15 | 2 | 17 / 12 |
| OOV probe v7, after the two-tier, loss-of-function and Marathi round (22 emergencies) | `280db73` | 60 | 43 | 0 | 7/22 | 16 | 2 | 11 / 10 |

Totals over 551 blind cases (97 emergencies): raw: correct 140, wrong bookings 145, missed emergencies 60; dateparser: correct 109, wrong bookings 12, missed emergencies 60; guard: correct 387, wrong bookings 18, missed emergencies 29
