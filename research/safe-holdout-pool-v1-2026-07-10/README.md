# Safe holdout pool v1 — 2026-07-10

Status: **closed without an admitted pool; new source input required**

Read in this order:

1. `result.md` — concise outcome and lessons;
2. `decision.json` — claims, authorizations, and next boundary;
3. `source-strategy-options.md` — acceptable next sources;
4. `generation-contract.json`, `generation-contract-v2.json`, and
   `generation-contract-v3.json` — frozen prospective contracts;
5. `v1-failure.json`, `v2-failure.json`, and `v3-failure.json` — preserved
   classifications;
6. `run/` — exact call custody, pool outputs, summaries, and unselected case
   files;
7. `scripts/evals/run_fixed_safe_holdout_pool*.py` — frozen runner lineage;
8. `tests/test_fixed_safe_holdout_pool.py` — provider-free contract tests.

No run used an automatic retry or evaluator call. No case was selected. The v2
case texts are failed fixtures and are not authorized as holdouts. The package
does not authorize Stage A, Stage B, graph work, runtime changes, or product
claims.

Verification passed 12 focused pool tests and 4,051 non-network repository
tests with one skip and 93 subtests. The live-embedding stability module was
excluded to avoid additional provider calls.
