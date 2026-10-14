---
type: llm
focus: mock_calls
arm: with-only
---

The user asked for: HER2-targeted antibody-drug conjugates in breast cancer, with assets, sponsors, highest phase, and key readouts expected in 2026 and 2027.

Look at the research question Claude sent to Sleuth with send_message (the `message` field).

PASS if that message asks for what the user asked. Rewording, tidier structure, and naming the four requested fields as columns are fine.

FAIL if the message adds columns, filters, or scope the user didn't ask for, such as payload or linker details, drug-to-antibody ratio, trial IDs, comparators or endpoints, partner licensing regions, approval status by region, or source citations. Also FAIL if no research question was sent.
