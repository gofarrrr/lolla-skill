# Gate 7 Case 06 receipt v2 package — 2026-07-10

Status: **agent reconstruction partial pass; human usefulness pending**

Read in this order:

1. `result.md` — concise outcome and limits;
2. `human-feedback-surface.md` — compact human review surface;
3. `receipt-contract.json` and `receipt-contract-repaired.json` — initial freeze
   and the prospective repair completed before assembly;
4. `v2-application-audit.json` — why assembly stopped before the repair;
5. `receipt.json` or `receipt.md` — self-contained closed-case receipt;
6. `receipt-preflight.json` — source-first review before the reader contract;
7. `reader-contract.json` — frozen prompt, model, output, call, timeout, and cost;
8. `run/lolla_gate7_case06_reader_20260710_a1/run-summary.json` — mechanical
   reader gates;
9. `run/lolla_gate7_case06_reader_20260710_a1/reader-output.json` — typed fresh
   reconstruction;
10. `source-first-review.json` — post-call source comparison;
11. `post-reader-status.json` — current authorization state after the frozen
    receipt snapshot;
12. `decision.json` — earned and blocked claim boundary.

No Case 06 pipeline stage was rerun. Receipt assembly used frozen evidence only.
The reader used one call, zero retries, and zero evaluator calls. No frozen
receipt, prompt, or response was tuned after the output.

This package does not claim human validation, answer improvement, graph value,
product proof, or runtime readiness.

Focused verification passed 36 tests. The non-network repository suite passed
4,039 tests with one skip and 93 subtests under Python 3.12; the live-embedding
stability module was excluded to avoid unbudgeted provider calls.
