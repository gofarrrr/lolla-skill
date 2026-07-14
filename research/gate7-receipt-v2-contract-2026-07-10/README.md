# Gate 7 receipt v2 repair — 2026-07-10

Status: **complete; first closed-case transfer observed**

Read in this order:

1. `result.md` — short outcome and boundary;
2. `decision.json` — exact hashes, authorizations, and non-claims;
3. `docs/evals/reasoning-run-receipt-v2.md` — human-readable contract;
4. `docs/evals/reasoning-run-receipt-v2.json` — JSON Schema;
5. `scripts/evals/validate_reasoning_run_receipt_v2.py` — provider-free
   cross-field checks;
6. `tests/fixtures/reasoning_run_receipt_v2/prospective-valid.json` — synthetic
   valid fixture;
7. `tests/test_reasoning_run_receipt_v2.py` — adversarial tests.

No provider was called, no runtime was changed, and no Case 10 artifact was
rewritten. The initial Case 06 application stopped before receipt assembly and
is preserved in its application audit. The contract was then repaired before a
replacement receipt was assembled. Its separate one-call reader result is at
`research/gate7-case06-receipt-v2-2026-07-10/`; this contract package itself did
not authorize that call.

Verification: 22 focused tests and 4,025 no-unbudgeted-call repository tests
passed; one test was skipped. The live-embedding stability module was excluded.
Those counts describe the contract-repair checkpoint. Later Case 06 package
verification is recorded in that package.
