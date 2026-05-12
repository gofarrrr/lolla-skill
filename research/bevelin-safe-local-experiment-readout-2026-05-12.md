# Bevelin Safe Local Experiment Readout

Date: 2026-05-12

## Short Answer

Keep the implementation as a local experiment and do not promote it into the
default system yet.

The Bevelin candidate records are source-backed, schema-valid, and useful when
explicitly nominated in tiny probes. But in the normal 8-case dry replay, the
two new owner records never enter the selected packet. That means the candidate
does not currently reach the LLM in realistic archived-case flow, so it has no
proven runtime edge.

## What Changed Locally

- Added review-only Bevelin source excerpts at
  `data/model_sources/Seeking_Wisdom_Bevelin_rag.md`.
- Added two candidate overlay records:
  - `data/model_affordances/bevelin_candidate/baseline-establishment.json`
  - `data/model_affordances/bevelin_candidate/obligations-controls-mapping.json`
- Added compiler overlay support through `--overlay-record-dir`, so candidate
  records can replace matching model IDs during compilation without editing the
  default source records.
- Added a compiler guard that rejects overlay records whose `model_id` does not
  already exist in the base records, preventing local experiments from quietly
  adding a new model layer.
- Kept the Bevelin source manifest entry neutral as
  `bevelin-candidate-source`; the compiler includes it in candidate metadata
  because the overlay records cite the filename, not because default owner
  models were globally remapped.
- Compiled the candidate artifact to:
  `data/compiled/model_affordances/bevelin_candidate/affordances_v60.json`.
- Added four tiny one-pressure cases under
  `research/spikes/bevelin-safe-local-substrate-experiment/`.

## Candidate Artifact

| Check | Result |
| --- | --- |
| Artifact id | `model_affordances_v60` |
| Filename contract | `affordances_v60.json` in explicit `bevelin_candidate/` directory |
| Contributing records | 222 |
| Affordances | 308, two more than default V60 |
| Absence records | 697 |
| Schema validation failures | 0 |
| Source quote rejection failures | 0 |
| Bevelin source metadata | One entry: `Seeking_Wisdom_Bevelin_rag.md` |
| Default `affordances_v60.json` mutation | No |

## Tests Run

```bash
PYTHONPATH=. pytest tests/test_model_affordance_compiler.py tests/test_model_affordance_schema.py tests/test_bevelin_candidate_records.py tests/test_v60_transaction_replay_lab.py tests/test_v60_enrichment_runtime.py
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --overlay-record-dir data/model_affordances/bevelin_candidate --output-dir data/compiled/model_affordances/bevelin_candidate --compiled-filename affordances_v60.json --quality-report-filename quality_report_v60.md --artifact-id model_affordances_v60 --report-title "Model Affordance Quality Report v60 Bevelin Candidate"
python3 scripts/run_v60_transaction_replay_lab.py --case-manifest research/spikes/bevelin-safe-local-substrate-experiment/tiny_case_manifest.json --affordances-path data/compiled/model_affordances/bevelin_candidate/affordances_v60.json --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-12-bevelin-candidate-tiny-dry-run-final --card-cap 8 --max-nominations 18 --dry-run
python3 scripts/run_v60_transaction_replay_lab.py --case-manifest research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json --affordances-path data/compiled/model_affordances/affordances_v60.json --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-12-bevelin-baseline-8case-dry-run-final --card-cap 8 --max-nominations 18 --dry-run
python3 scripts/run_v60_transaction_replay_lab.py --case-manifest research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json --affordances-path data/compiled/model_affordances/bevelin_candidate/affordances_v60.json --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-12-bevelin-candidate-8case-dry-run-final --card-cap 8 --max-nominations 18 --dry-run
```

The focused pytest suite passed: 47 passed in 3.42s. No paid/private LLM calls
were made because the dry-replay gate stopped the experiment first.

## Tiny Probe Results

| Case | Intended unit | Result |
| --- | --- | --- |
| `bevelin-absolute-yardstick-tiny` | BVL-04 | Candidate packet selected `baseline-establishment.absolute-yardstick-before-contrast` alongside the existing baseline gate. |
| `bevelin-role-reversal-system-fairness-tiny` | BVL-06 | Candidate packet selected `obligations-controls-mapping.role-reversal-system-rule` alongside the existing obligation/control trace. |
| `bevelin-postmortem-learning-trace-control-tiny` | BVL-08 control | Existing `hindsight-bias.predecision-record-for-learning-review` was selected, confirming duplicate coverage. |
| `bevelin-disconfirmation-control-tiny` | BVL-01 control | Existing `falsifiability.disconfirming-reversal-gate` was selected, confirming duplicate coverage. |

Tiny probes prove the candidate chunks are valid and packetable. They do not
prove normal runtime usefulness because the cases explicitly nominate the owner
models.

## 8-Case Dry Replay Results

Baseline and candidate broad dry runs produced the same packet-level counts:
each of the 8 cases selected 8 candidate cards, with identical reviewed
affordance counts and absence counts per case. Token estimates changed only by
the small candidate metadata/record delta.

The candidate-specific IDs did not appear in the normal 8-case packets:

- `baseline-establishment.absolute-yardstick-before-contrast`: not selected.
- `obligations-controls-mapping.role-reversal-system-rule`: not selected.

The selected 8-case model IDs did include adjacent records such as
`power-dynamics`, `boundaries`, `opportunity-cost`, `falsifiability`,
`feedback-loops`, and `optionality`, but not the two candidate owner records.

## Decision

Do not promote the Bevelin candidate substrate into the default V60 artifact or
live runtime yet.

What is useful:

- The overlay compiler path is useful and safe for local substrate experiments.
- BVL-04 and BVL-06 are coherent source-backed operators.
- BVL-01 and BVL-08 are confirmed as duplicate/control material for this slice.

What is not yet useful enough:

- The two new candidate chunks do not naturally reach realistic archived-case
  packets in the current dry replay.
- Without packet entry, Step 6 never gets the chance to use, reject, defer, or
  keep them as private guardrails.
- Running paid/private LLM calls now would test forced usefulness, not the
  actual system path.

## Next Revision Hypothesis

If we want to continue later, the next experiment should not add more Bevelin
records. It should ask why the relevant owner models are not being surfaced:

- Is `baseline-establishment` the right owner for contrast/yardstick cases, or
  should the pressure live in an existing selected owner such as
  `price-discrimination`, `margin-of-safety`, `opportunity-cost`, or
  `statistical-discipline`?
- Is `obligations-controls-mapping` the right owner for fairness cases, or
  should the role-reversal rule be tested under `boundaries`, `power-dynamics`,
  `principal-agent-problem`, or `reciprocity-principle`?
- Would a future embedding refresh surface these owners, or does the Lane 1
  route/subpattern menu need source-backed sharpening before V60 can help?

Until that is answered, the candidate should remain local and explicit-path
only.
