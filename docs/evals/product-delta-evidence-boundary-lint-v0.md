# Product Delta Evidence Boundary Lint v0

Status: read-only deterministic lint
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR78 Product Delta Evidence Boundary Lint v0

## Purpose

PR78 adds a deterministic lint for Product Delta Evidence artifacts. It exists
to keep provisional eval outputs inside their evidence boundary before the repo
adds any future specialist-review architecture.

The lint does not decide whether Lolla improved a decision. It only checks
whether Product Delta artifacts stayed honest about what they are allowed to
claim.

## Runtime Boundary

Product Delta eval is offline and downstream from the Lolla runtime.

```text
Lolla runtime:
  produce audited revised answers and custody artifacts.

Product Delta eval lane:
  inspect existing artifacts later, provisionally and offline.
```

The lint must not invoke `$lolla`, invoke the Lolla skill, run skill setup,
create `/tmp/lolla_*` runtime state, call OpenRouter or provider APIs, mutate
archives, persist revised answers, render memos, launch Observatory, change
prompts, change `SKILL.md`, or change runtime behavior.

The runtime produces the object of study. The eval lane studies it later.

## What It Checks

The lint can check Product Delta JSON and Markdown artifacts that are passed to
it explicitly.

Blocking errors include:

- `human_validated` not set to `false`;
- `ground_truth` not set to `false`;
- `judge_calibration_eligible` not set to `false`;
- `model_calls` not set to `0`;
- `archive_mutated` not set to `false`;
- `raw_private_content_included` not set to `false`;
- `safe_for_agent_use` fields;
- score, rating, winner, approval, certification, or pass/fail fields;
- automatic label, answer-quality scoring, or LLM-judge flags set to true;
- PR72-shaped review cases missing required lower-claim fields;
- positive candidate reads without lost-value status, uncertainty notes, or
  human follow-up questions;
- provisional taxonomy entries missing `not_a_score: true`;
- provisional taxonomy entries not marked `provisional_until_human_review`;
- privacy/content markers such as local absolute paths or secret-like names.

Warnings include targeted prose risks:

- Markdown that may imply Lolla proved or validated product value;
- Markdown that may imply Codex validated a result;
- positive candidate distributions without agreement-bias, selection-bias, or
  compressed-safe-summary caveats;
- Product Delta reports without falsification language.

Warnings are intentionally narrower than a global word ban. Product docs must
be able to discuss rejected judges, product hypotheses, and non-claims without
failing lint.

## What It Cannot Prove

Passing lint does not mean:

- Lolla improved the decision;
- the answer is correct;
- a human validated the result;
- the artifact is ground truth;
- the artifact can calibrate a judge;
- the case is product proof;
- an agent may act on the answer;
- clean artifacts prove good advice.

Passing lint means only:

```text
The checked artifact stayed inside Product Delta evidence-boundary rules.
```

## How To Run

Run against the current Product Delta artifacts:

```bash
python3 scripts/evals/lint_product_delta_evidence.py \
  --paths \
  docs/evals/vanilla-vs-lolla-provisional-review-v0.json \
  reviews/codex-assisted/paired-review-dry-run-v0/review.json \
  docs/evals/provisional-product-delta-failure-taxonomy-v0.json \
  reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  reviews/codex-assisted/product-delta-batch-v0/review.json \
  docs/evals/product-delta-provisional-report-v0.md
```

Write a JSON report:

```bash
python3 scripts/evals/lint_product_delta_evidence.py \
  --paths reviews/codex-assisted/product-delta-batch-v0/review.json \
  --json-out /tmp/product_delta_boundary_lint.json \
  --format json
```

The JSON report uses:

```text
lolla.product_delta_boundary_lint.v0
```

It includes checked paths, finding counts, findings with path and location, and
boundary flags that state no model calls, runtime invocation, skill invocation,
archive mutation, human validation, or product proof occurred.

## Exit Behavior

- Exits `0` when there are no blocking errors.
- Exits nonzero when blocking errors are present.
- Warnings do not fail by default.
- `--fail-on-warning` makes warnings fail the command.

## Future Use

PR79 defines the future specialist-review architecture:
[Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md).

PR80 defines the typed contracts for those specialist reads:
[Product Delta Specialist Review Contracts v0](product-delta-specialist-review-contracts-v0.md).

PR81 builds checked-in-safe packets against those contracts:
[Product Delta Specialist Packet Builder v0](product-delta-specialist-packet-builder-v0.md).

PR82 adds checked-in-safe trap fixtures before any real specialist batch:
[Provisional Reviewer Trap Set v0](provisional-reviewer-trap-set-v0.md).

Any future specialist-review schemas, packet outputs, or review artifacts should
pass this lint before Codex-assisted provisional outputs are treated as review
packets. PR78 is the seatbelt before additional LLM-assisted interpretation: it
protects the evidence lane from turning provisional reads into faux-evidence.
