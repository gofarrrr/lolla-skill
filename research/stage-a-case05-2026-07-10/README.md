# Case 05 full Stage A — 2026-07-10

Status: **formal admission failed; executed exactly once; rerun forbidden**

This package is the first full extraction-plus-existing-pipeline attempt after
the transactional extraction-custody smoke passed. The case was selected by a
frozen hash rule from the remaining uncontaminated core-corpus cases, not by
expected ease or likely success.

Read in this order:

1. `selection-contract.json`;
2. `contract.json`;
3. `run/lolla_stage_a_case05_20260710_a1/execution-result.json`;
4. `pipeline-gate-result.json`;
5. `call-evidence.json`;
6. `decision.json`;
7. `result.md`.

The extraction and pipeline both actually exited zero. Capture, exact quotes,
transactional call custody, model attribution, embeddings, usage, cost, private
table, and V60 gates all passed. The frozen sealer nevertheless failed because
the runner wrote `extractor_exit_zero` while the sealer requested
`extraction_exit_zero`. This is an F8 deterministic scorer/contract mismatch.
It is preserved as a failure rather than repaired after seeing the run.

No control, treatment, consumer, evaluator, or user-facing advice call was
made. Gate 4 and runtime integration remain blocked.

