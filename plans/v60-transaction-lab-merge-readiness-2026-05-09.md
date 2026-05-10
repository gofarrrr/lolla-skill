# V60 Transaction Lab Merge Readiness

Date: 2026-05-09
Branch: `feat/v60-transaction-local-replay-lab`
Decision posture: merge dormant lab infrastructure only; do not merge runtime
pickup.

## Merge Thesis

This branch is ready to be prepared for a scoped PR, but the PR must be framed
as a dormant v60 transaction packet lab, not product integration.

Merge the machinery that lets us test reasoning transport. Do not merge any
behavior that injects v60 cards into live `/lolla`, Step 6, Step 8, memo output,
Observatory, or user-facing chat.

The first-principles reason is simple:

- transport has been proven useful enough to keep;
- direct final-answer injection has not been proven product-ready;
- C1 and C2 both show that full-packet prompting can create either visible
  model theater or private consideration theater;
- the next architecture should split private delta audit from final
  composition.

## Current Evidence

Local and paid replay evidence now says:

- grouped v60 card transport works;
- absence records, weak support, confidence, and provenance can be carried in
  dormant packets;
- the card ledger validator catches real trace/schema failures;
- hidden-ledger C2 preserves the public/private boundary better than C1;
- neither visible C1 nor hidden C2 is ready for product runtime;
- Arm B beat hidden C2 in 4 of 4 edge-audit paid cases.

Therefore, the mergeable artifact is the lab, not the product behavior.

## Recommended PR Scope

### Core Code

Include:

- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `engine/system_b/card_transaction_ledger.py`

These changes are additive and dormant:

- `reviewed_affordance_cards` is added as grouped per-affordance identity;
- `reviewed_affordance_fields` remains for backward compatibility;
- the Markdown review renderer can show grouped cards;
- the ledger validator validates shape and trace IDs only.

### Replay Harnesses

Include:

- `scripts/run_v60_transaction_replay_lab.py`
- `scripts/run_v60_transaction_replay_matrix.py`
- `scripts/run_v60_transaction_paid_replay.py`

These scripts are offline/replay tooling. They must remain outside runtime
paths and must require explicit `affordances_v60.json`.

### Tests

Include:

- `tests/test_reasoning_substrate_packet.py`
- `tests/test_reasoning_substrate_packet_review_render.py`
- `tests/test_card_transaction_ledger.py`
- `tests/test_v60_transaction_replay_lab.py`
- `tests/test_v60_transaction_replay_matrix.py`
- `tests/test_v60_transaction_paid_replay.py`

### Plans And Reports

Include:

- `plans/reasoning-substrate-affordance-transaction-handover-2026-05-08.md`
- `plans/v60-transaction-packet-local-replay-plan-2026-05-09.md`
- `plans/reasoning-substrate-v60-local-transaction-lab-handover-2026-05-09.md`
- `plans/v60-transaction-lab-merge-readiness-2026-05-09.md`
- `research/v60-transaction-replay-case-manifest-2026-05-09.json`
- `research/v60-transaction-replay-preflight-report-2026-05-09.md`
- `research/v60-transaction-replay-matrix-report-2026-05-09.md`
- `research/v60-transaction-paid-pilot-readout-2026-05-09.md`
- `research/v60-transaction-c2-hidden-ledger-readout-2026-05-09.md`
- `research/v60-transaction-c43-consideration-router-readout-2026-05-10.md`

These documents preserve the negative results. That is important: the branch
should not read as "v60 is product-ready." It should read as "we now have the
lab that proved what is not ready."

## Evaluation Artifacts

The evaluation directory currently contains full local replay artifacts under:

- `data/evaluations/v60_transaction_replay_lab/`

Current local size is roughly 14 MB with 299 files.

Recommended default:

- commit high-level `summary.json` and generated Markdown reports only if we
  want auditable replay evidence in-repo;
- do not commit raw `cases/`, `packets/`, `prompt_packets/`, `outputs/`, or
  `ledger_templates/` directories unless they are intentionally promoted into
  fixtures;
- do not commit smoke or aborted partial run directories unless a report
  explicitly depends on them.

Candidate evidence files to commit, if we want in-repo summaries:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight/preflight_report.md`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/matrix_report.md`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-first-half/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-first-half/paid_replay_report.md`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-remainder/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-remainder/paid_replay_report.md`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c2-hidden-edge/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c2-hidden-edge/paid_replay_report.md`
- `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-dry-run/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-dry-run/paid_replay_report.md`

Keep local-only by default:

- `data/evaluations/v60_transaction_replay_lab/**/cases/`
- `data/evaluations/v60_transaction_replay_lab/**/packets/`
- `data/evaluations/v60_transaction_replay_lab/**/prompt_packets/`
- `data/evaluations/v60_transaction_replay_lab/**/outputs/`
- `data/evaluations/v60_transaction_replay_lab/**/ledger_templates/`
- smoke directories;
- partial aborted directories.

## Explicit Exclusions

Do not include these in the v60 lab PR unless separately reviewed:

- `.assay/`
- `.claude/`
- `.tmp/`
- `__pycache__/` files
- unrelated research documents created outside this v60 lab scope
- unrelated `tasks/` files
- `scripts/spikes/`
- raw replay output directories unless intentionally promoted as fixtures

The current working tree contains unrelated untracked files. Do not stage by
directory glob.

## Runtime Safety Checks

Before PR:

- confirm no import from runtime pipeline to the v60 lab harnesses;
- confirm no live `/lolla` path references `reviewed_affordance_cards`,
  `card_transaction_ledger`, or `private_transaction_ledger`;
- confirm replay harnesses require explicit `affordances_v60.json`;
- confirm no "latest artifact" glob/promotion exists;
- confirm the old flat packet field remains available.

Current quick check:

- no matches for v60 transaction lab symbols in `engine/system_b/pipeline.py`
  or `scripts/run_pipeline.py`;
- replay harnesses guard on explicit `affordances_v60.json`.

## Verification Command

Run before PR:

```bash
env PYTHONPATH=. pytest \
  tests/test_v60_transaction_paid_replay.py \
  tests/test_v60_transaction_replay_matrix.py \
  tests/test_v60_transaction_replay_lab.py \
  tests/test_card_transaction_ledger.py \
  tests/test_reasoning_substrate_packet.py \
  tests/test_reasoning_substrate_packet_review_render.py

python3 -m py_compile \
  scripts/run_v60_transaction_paid_replay.py \
  scripts/run_v60_transaction_replay_lab.py \
  scripts/run_v60_transaction_replay_matrix.py

git diff --check
```

Latest focused run before the C4.3 note:

- `python3 -m pytest tests/test_v60_transaction_paid_replay.py -q`
- result: `33 passed`
- `python3 -m py_compile scripts/run_v60_transaction_paid_replay.py`
- C4.3 dry run generated
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-dry-run/summary.json`

## Merge Blockers

Do not merge if any of these become true:

- live runtime imports replay lab code;
- packet builder auto-loads a "latest" affordance artifact;
- C1/C2 product behavior is described as ready;
- raw replay outputs are committed accidentally;
- generated caches are staged;
- ledger validation is relaxed to accept invalid trace IDs or enum drift;
- final-answer injection is added under the same PR.

## Next Post-Merge Experiment

The next test is C4.3: consideration-router paid replay.

C4.3 should:

- receive grouped v60 cards as private enrichment for Claude Code / Codex;
- return public answer fields for blinded comparison;
- return a private `consideration_usefulness_report` with one assessment per
  candidate card;
- evaluate useful-to-consider material separately from visible public uptake;
- preserve ledger validation, public machinery-leak checks, and no-runtime
  integration boundaries.
- let a separate composer apply accepted deltas to Arm B;
- safely collapse to Arm B when no accepted deltas survive.

Promotion bar:

- C3 beats or ties B on at least 3 of 4 edge-audit cases;
- C3 public output contains grounded edges or evidence gates when it wins;
- all ledgers are `valid` or `valid_after_summary_repair`;
- no private mechanism leaks;
- no full-answer copy-back;
- no runtime attachment until replay evidence supports it.
