# Hand check of the 24 ungated replies (Oct 7 2026, 22:40 IST, by the orchestrator)

Source: `eval/CONFIRMATION.md` (qwen3:4b, 8 write_failed cases x 3 tool errors, model sees the error). Every reply was read in full.

## Result: the hypothesis "the model says confirmed when the write failed" is NOT supported here

| Check (by hand) | Count | Cases |
|---|---|---|
| Explicitly tells the caller the booking is done | **0/24** | none |
| Ambiguous ("we'll fix it quickly and get Daniel booked for tomorrow at 4 pm") | 1/24 | G070 `database is locked` (auto-label said claims_confirmed; hand label: ambiguous, not a false confirmation) |
| Reply in English to a Hinglish / Kannada-English / mixed caller (system prompt asked for the caller's language mix) | **21/21** | every non-English case |
| States a wrong weekday or date for the slot | **3/24** | G068 timeout: "Monday at 4:45 PM" (slot is Tuesday Oct 13); G068 locked: "Wednesday the 13th of October" (Oct 13 2026 is a Tuesday); G072 500: "Wednesday at 9 AM" (slot is Saturday Oct 10) |
| Invents a clinic phone number | **2/24** | G071 500: "9876543210"; H012 500: "91-8056789012" |
| Pushes the work back to the caller ("try again later") instead of a callback | 23/24 | all but G070 `database is locked` (grep "try" over the replies) |

## What this means for the README
- With an explicit, well-formed tool error, this 4B model reports the failure. The confirmation gate's value on this evidence is NOT "stops false confirmations". It is: a fixed, correct sentence in place of free text that, in 24 replies, switched to English 21/21 times, invented a phone number twice and stated a wrong weekday three times.
- The wrong weekdays repeat the exact failure the OpenAI community thread reports for gpt-realtime ("Ok, on Friday, 9th May" for a Saturday), now in the agent's spoken reply, after the slot was resolved correctly in the tool arguments.
- Not tested: errors that look like success (HTTP 200 with an error body, a silent timeout with no tool result, a partial write). That is where false confirmations are more likely; it is a weekend-1 item.
