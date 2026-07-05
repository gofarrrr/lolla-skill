# Balanced Batch Candidate Selector / Readiness Builder Plan v0

Status: plan / phase gate
Date: 2026-07-04

Review artifact:
`reviews/codex-assisted/balanced-batch-candidate-selector-readiness-builder-plan-v0/review.json`

Source plan:
[Balanced Offline Product Delta Evidence Batch Plan](balanced-offline-product-delta-evidence-batch-plan-v0.md)

## Purpose

This plan defines how a future deterministic candidate selector / readiness
builder should identify archived cases for a balanced offline Product Delta
evidence batch without biasing toward flattering Lolla.

The future builder should prepare a checked-in-safe candidate packet or
operator-local packet that routes cases to review. It should not decide whether
Lolla improved an answer.

This PR is plan-only. It does not implement the selector, scan archives
broadly, run Product Delta review, create batch outputs, call providers or
models, invoke the Lolla skill, create new Lolla runs, create a live evaluator,
create an LLM-as-judge system, score answer quality, claim product proof,
claim human validation, validate advice correctness, approve agent use, mutate
archives, touch runtime behavior, or change protected skill/archive scripts.

The selector/readiness builder principle is:

```text
The selector/readiness builder is not trying to find wins.
It is trying to build a balanced evidence set where Lolla can be found useful,
partial, no-change, noisy, worse, or inconclusive.
```

## Source Rules

The future selector should accept an explicit source scope. That scope may be a
checked-in case manifest, a safe review-corpus export, a Product Delta readiness
packet, or a local operator-supplied list of archive refs. It should not crawl
broad private directories looking for cases.

Allowed selection signals are deterministic, already-existing, and lower-claim:

- existing Product Delta readiness metadata;
- existing provisional labels;
- specialist disagreement or fan-in signals;
- human-review taxonomy labels where available;
- failure taxonomy hints where available;
- archived case metadata without copying raw conversation text;
- run-health and capture-adequacy metadata;
- review-corpus readiness metadata.

Candidate source rules:

- use existing safe metadata and checked-in eval artifacts first;
- keep raw/private artifacts local unless an approved workflow creates a
  checked-in-safe summary;
- record source refs and custody summaries rather than copying raw content;
- treat missing buckets as findings, not as permission to fabricate examples;
- require the future builder to report its source scope and candidate count;
- require the future builder to preserve no-change, noisy, worse, and
  inconclusive possibilities;
- require a future human or Codex-assisted review step before any Product Delta
  conclusion is recorded.

## Readiness Criteria

A case should be marked ready only when it has enough deterministic artifacts
for a future balanced Product Delta review to inspect the delta without
exporting raw/private content into broad checked-in files.

Readiness requires:

- a stable case ref or candidate ID;
- at least one safe source ref to existing Product Delta, human-review, review
  corpus, or archive metadata;
- enough custody metadata to know whether raw/private artifacts remain local;
- a proposed bucket hypothesis with a short reason summary;
- a readiness status;
- missing required artifact fields when review cannot proceed;
- explicit non-claims;
- no final Product Delta label;
- no answer-quality score;
- no product-proof, advice-correctness, or agent-approval claim.

The readiness builder may say that artifacts are missing, private context is
required, capture health is insufficient, schema/custody failed, or a candidate
is excluded. Those states are useful because they make review limits visible.

## Candidate Buckets

The future builder should support these proposed buckets. These are routing
hypotheses for balanced review, not final labels.

| Bucket | Selection hint |
|---|---|
| `likely_material_improvement_candidate` | Prior safe provisional material-improvement signals or review notes suggesting Lolla changed verification, deferral, boundaries, or decision leverage in a material way. |
| `partial_improvement_candidate` | Prior safe signals where Lolla added some leverage but left important uncertainty, proportionality, or lost-value risk unresolved. |
| `likely_no_change_candidate` | Metadata or prior review indicates the revised answer closely tracks what the vanilla answer likely would have done. |
| `noisy_or_worse_candidate` | Failure taxonomy, human-review, specialist, or fan-in signals indicate added burden, weaker advice, unsupported claims, or unhelpful friction. |
| `inconclusive_candidate` | Capture, source depth, or review disagreement makes a lower-claim result more honest than a positive or negative read. |
| `lost_user_intent_candidate` | Prior notes indicate the revised answer may have drifted from the user's actual goal, constraints, desired tone, or action shape. |
| `friction_without_leverage_candidate` | Lolla appears to add caution, process, or caveats without changing a decision variable the user could act on. |
| `vanilla_already_good_enough_candidate` | Metadata suggests the original answer already handled the user need well enough, making extra friction suspect. |
| `useful_verification_deferral_boundary_candidate` | Signals point to useful verification, deferral, boundary-setting, or decision leverage without claiming correctness. |
| `overcorrection_or_user_need_drift_candidate` | Signals indicate advice may have become too timid, generic, or misaligned after Lolla pressure. |

The future builder should not require all buckets to be full. It should record
empty or thin buckets explicitly so the evidence plan can see where the corpus
is weak.

## Output Shape For The Future Builder

The future selector/readiness builder should emit a structured artifact with at
least this shape:

- `schema`;
- `generated_at`;
- `source_scope`;
- `candidate_count`;
- `candidates[]`;
- `candidate_id` or `case_ref`;
- `proposed_bucket`;
- `bucket_reason_summary`;
- `readiness_status`;
- `missing_required_artifacts`;
- `custody_flags`;
- `private_artifact_refs`;
- `checked_in_safe_refs`;
- `non_claims`;
- `review_next_step`.

The artifact should be checked-in-safe only if it contains no raw/private
conversation text, raw revised answers, raw memos, provider/model text, private
ledgers, secrets, or local absolute private paths. If a safe summary cannot be
made, the builder should write a local/operator-only packet and record that
checked-in publication is blocked.

## Readiness Statuses

The future output should use these statuses:

- `ready_for_balanced_product_delta_review`;
- `deferred_missing_artifacts`;
- `deferred_private_context_required`;
- `blocked_privacy_risk`;
- `blocked_capture_or_run_health`;
- `blocked_schema_or_custody_failure`;
- `excluded_not_relevant`;
- `excluded_duplicate_or_near_duplicate`.

These statuses are routing and custody states. They are not quality labels,
approval labels, or proof that Lolla helped.

## Refusal And Defer Rules

The future selector/readiness builder must refuse or defer when:

- required artifacts are missing;
- private context is required for review but cannot be safely summarized;
- capture or run-health metadata is insufficient;
- schema or custody checks fail;
- raw/private conversation text would be copied into checked-in artifacts;
- raw revised answers, raw memos, provider text, private ledgers, local
  absolute private paths, or secrets would be copied;
- a case would need answer-quality inference to assign a bucket;
- the builder would need to assign a final Product Delta label;
- the builder would need to score a case;
- the builder would need a model/provider call, Lolla invocation, new Lolla run,
  live judge, archive mutation, runtime change, or agent-use approval.

## Forbidden Selection Behavior

The future selector/readiness builder must not:

- read or export raw/private conversation text into checked-in batch files;
- copy raw revised answers;
- copy raw memos;
- copy provider/model text;
- copy private ledgers;
- copy local absolute private paths;
- infer answer quality;
- assign final labels;
- score cases;
- claim product proof;
- claim human validation;
- claim advice correctness;
- approve agent use;
- call models or providers;
- invoke `$lolla` or the Lolla skill;
- create new Lolla runs;
- mutate archives;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- touch `scripts/archive_run.py`.

## Anti-Flattery Requirements

The future selector should not optimize for positive-looking evidence. It
should preserve cases where Lolla may be useful, partial, no-change, noisy,
worse, or inconclusive.

The prior `accept-operations-role-startup` downgrade remains the reference
anti-flattery signal. A healthy selector should keep downgrade and disagreement
pressure visible rather than filtering those cases away.

The selector should also preserve bucket imbalance. If the available safe
metadata yields many positive candidates and few noisy/worse candidates, that
is a corpus finding, not evidence that noisy/worse cases do not exist.

## Future Builder Guardrails

The future implementation PR should be deterministic and command-only. It may
prepare a candidate readiness packet, but it must not run the review batch. It
should leave final Product Delta reads to the existing provisional review
protocol, specialist decomposition, fan-in reporting, or human review.

The builder should require explicit inputs such as a source manifest, safe
review-corpus export, Product Delta readiness metadata, or checked-in eval
refs. Any optional archive metadata reads must stay local/operator-controlled
and must not copy raw/private content into checked-in outputs.

## Decision Gate

Gate options:

- `proceed_to_balanced_batch_candidate_selector_builder`
- `proceed_to_human_review_calibration_plan`
- `repair_candidate_selector_plan_before_builder`

Selected gate:

```text
proceed_to_balanced_batch_candidate_selector_builder
```

Recommended next PR:

```text
Balanced Batch Candidate Selector / Readiness Builder v0
```

That next PR should implement only the deterministic selector/readiness
builder. It should not run Product Delta review, call providers/models, run
Lolla, create a live judge, score answer quality, or claim product proof.
