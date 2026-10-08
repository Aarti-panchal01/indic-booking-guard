# Blind ledger (recomputed by `python -I eval/ledger.py` from the committed blind-run files)

| Blind run | Guard at | Cases | Guard correct | Guard wrong bookings | Guard missed emergencies | Raw model wrong bookings | dateparser wrong bookings | Raw / dateparser correct |
|---|---|---|---|---|---|---|---|---|
| Held-out v1 (spec vocabulary) [from RESULTS_v1_frozen_b721436.md] | `b721436` | 24 | 23 | 1 | 0/3 | 8 | 1 | 4 / 1 |
| Golden G073 to G156, first run | `00f0c25` | 84 | 81 | 1 | 1/10 | 26 | 3 | 16 / 15 |
| Held-out v2 (spec vocabulary, adversarial) | `00f0c25` | 48 | 47 | 0 | 0/6 | 17 | 1 | 12 / 9 |
| OOV probe v1 | `759faf4` | 45 | 24 | 1 | 3/7 | 11 | 0 | 14 / 10 |
| OOV probe v2 | `92dcbd9` | 50 | 31 | 6 | 4/8 | 12 | 2 | 12 / 10 |
| OOV probe v3 | `2f4b7be` | 60 | 25 | 7 | 3/9 | 19 | 0 | 17 / 13 |
| OOV probe v4, after the allowlist change | `0a55b09` | 60 | 35 | 1 | 1/7 | 14 | 0 | 16 / 15 |
| OOV probe v5, second run of the allowlist guard | `5903181` | 60 | 33 | 0 | 4/7 | 7 | 1 | 21 / 14 |
| OOV probe v6, after the red-flag and stacked-day fix (18 emergencies) | `180bd58` | 60 | 45 | 1 | 6/18 | 15 | 2 | 17 / 12 |

Totals over 491 blind cases (75 emergencies): raw: correct 129, wrong bookings 129, missed emergencies 44; dateparser: correct 99, wrong bookings 10, missed emergencies 44; guard: correct 344, wrong bookings 18, missed emergencies 22
