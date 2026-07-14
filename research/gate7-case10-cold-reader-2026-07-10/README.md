# Gate 7 Case 10 cold-reader package — 2026-07-10

Status: **agent half complete; partial transfer pass; human feedback required**

Read in this order:

1. `result.md` — concise outcome and limits;
2. `human-feedback-surface.md` — the compact surface for the one required human
   question;
3. `receipt-contract.json` — frozen provider-free receipt-build inputs;
4. `receipt.md` — self-contained receipt given to the reader;
5. `reader-contract.json` — prompt, model, schema, call, timeout, and cost freeze;
6. `run/lolla_gate7_case10_reader_20260710_a1/run-summary.json` — mechanical gates;
7. `run/lolla_gate7_case10_reader_20260710_a1/reader-output.json` — typed fresh
   reconstruction;
8. `source-first-review.json` — source comparison and preserved failures;
9. `decision.json` — claim and authorization boundary.

The reader used one call, zero retries, and zero evaluator calls. No completed
Case 10 artifact was tuned after the output. The package does not claim human
validation, answer improvement, graph value, product proof, or runtime readiness.

Focused Gate 7 verification passed eight tests. The no-unbudgeted-call
repository run passed 4,011 tests with one skip; the legacy stability module was
excluded because its present unit path invokes live OpenAI embeddings.
