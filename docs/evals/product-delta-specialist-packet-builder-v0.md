# Product Delta Specialist Packet Builder v0

Status: read-only deterministic packet builder
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR81 Specialist Review Packet Builder v0

## Purpose

PR81 implements the deterministic packetization stage defined by
[Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md)
and targeted at the typed contracts in
[Product Delta Specialist Review Contracts v0](product-delta-specialist-review-contracts-v0.md).

The packet builder prepares narrow, source-aware, privacy-safe input packets for
future Product Delta specialist reads. It does not run the specialist reads.

It does not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, read raw transcripts, read raw revised answers, read raw memos,
persist revised answers, launch Observatory, change prompts, change
`SKILL.md`, change runtime behavior, add a judge, measure answer quality,
create automatic labels, or authorize agent action.

## Runtime And Eval Boundary

The runtime/eval split remains load-bearing:

```text
Lolla runtime:
  captures the current conversation
  runs OpenRouter-backed audit lanes
  produces the revised answer
  persists custody artifacts, memo, Observatory, and archive

Product Delta eval lane:
  reads existing safe artifacts later
  packetizes cases
  supports provisional specialist review outside runtime
  validates schemas and non-claims
  preserves disagreement and uncertainty
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies it later.

PR81 lives entirely in the eval lane. It prepares inputs for later review; it
does not alter the object being studied.

## What It Reads

In `checked_in_safe_mode`, the builder reads checked-in Product Delta eval
artifacts:

- `docs/evals/product-delta-seed-cases-v0.json`
- `reviews/codex-assisted/product-delta-provisional-run-v0/review.json`
- `reviews/codex-assisted/product-delta-batch-v0/review.json`
- `docs/evals/product-delta-specialist-review-contracts-v0.json`

The builder uses:

- case IDs, run IDs, and relative archive references;
- readiness status from PR75;
- structured artifact presence metadata;
- structured run signals already present in PR75 output;
- review-safe context fields;
- source references to prior broad provisional PR76 reads.

It does not copy PR76 semantic conclusions into specialist answers. Prior broad
reads are referenced as source context only, not as truth.

## What It Outputs

The generated JSON uses:

```text
lolla.product_delta_specialist_packets.v0
```

Top-level fields include:

- `schema_version`
- `generated_by`
- `mode`
- `input_refs`
- `boundary`
- `packet_policy`
- `case_count`
- `cases`
- `non_claims`

Each case includes:

- `case_id`
- `run_id`
- `archive_relpath`
- `readiness_status`
- `source_refs`
- `available_context`
- `missing_or_thin_context`
- `packets`

Each case has one input packet for each PR80 role:

- `conversation_interpretation`
- `vanilla_likely_next_action`
- `lolla_likely_next_action`
- `structural_delta`
- `friction_lost_value`
- `interpretation_adequacy`
- `advisory_overclaim`
- `conservative_fan_in`

Each packet records:

- specialist role;
- PR80 contract reference;
- input mode;
- allowed input refs;
- forbidden output categories;
- review questions;
- source refs;
- safe context;
- known limits;
- required non-claims;
- expected output contract.

The packet's `expected_output_contract` names the future output shape. It is
not a filled specialist read.

## Checked-In Safe Mode

PR81 implements `checked_in_safe_mode`.

This mode excludes:

- raw transcripts;
- raw revised answers;
- raw memos;
- provider private text;
- private reasoning;
- local absolute paths;
- secrets or private content.

The checked-in fixture is:

```text
reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json
```

It contains two cases only. The full seed list can be packetized locally with
the CLI, but the compact fixture keeps the repo review surface readable.

## Deferred Local Private Mode

`local_private_mode` is documented by PR80 but deferred for PR81.

Future local private mode may allow an operator to reference local raw artifacts
when explicitly allowed. It must remain read-only, record exactly what was read,
keep archive mutation false, and avoid copying raw/private content into
checked-in outputs.

## What Packets Are Not

Packets are not:

- specialist reviews;
- human validation;
- ground truth;
- judge calibration data;
- product proof;
- answer-quality measurement;
- automatic labels;
- agent permission;
- runtime integration.

PR81 may ask:

```text
Review whether the revised answer changed action, threshold, sequence, or gate.
```

PR81 must not answer:

```text
The action changed.
```

That answer belongs to a later provisional specialist-review slice, and even
then remains non-human-validated until a human reviewer corrects or confirms it.

## PR78 Lint

PR81 packet outputs must pass
[Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).

Passing lint means only:

```text
The packet artifact stayed inside Product Delta evidence-boundary rules.
```

Passing lint does not mean:

- Lolla changed the decision usefully;
- a specialist read is correct;
- a human validated anything;
- a judge is calibrated;
- the packet is product proof;
- an agent may act.

## How To Run

Build the checked-in safe fixture shape:

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --limit 2 \
  --out reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json
```

Build a temporary sanity-check output:

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --limit 2 \
  --out /tmp/product_delta_specialist_packets_check.json
```

Filter to one case:

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --case-id ceo-remove-founding-cofounder \
  --out /tmp/product_delta_specialist_packets_case.json
```

## Validation Meaning

Validation can show:

- the CLI can deterministically construct packets from checked-in safe inputs;
- packets include all PR80 specialist roles;
- lower-claim metadata remains conservative;
- source refs and known limits are preserved;
- checked-in outputs avoid raw/private content;
- PR78 lint accepts the packet artifacts.

Validation cannot show:

- the future specialist reads will be correct;
- Lolla improved a decision;
- the PR76 broad reads were correct;
- a human validated any case;
- a future fan-in read should be trusted.

## Next PR

PR82 has now added checked-in-safe trap fixtures:

```text
docs/evals/provisional-reviewer-trap-set-v0.md
docs/evals/provisional-reviewer-trap-set-v0.json
```

PR83 has now used the two-case PR81 fixture for the first specialist-review
batch:

```text
reviews/codex-assisted/specialist-review-batch-v0/review.json
```

Recommended next slice:

```text
PR84 Fan-In / Disagreement Report v0
```

PR84 should compare the PR83 specialist outputs to the PR76 broad reads and
preserve disagreements without voting, scoring, runtime integration, or product
proof.
