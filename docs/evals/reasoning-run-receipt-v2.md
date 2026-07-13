# Reasoning Run Receipt v2

Status: frozen after first closed-case application; not runtime integrated  
Date: 2026-07-10

## Purpose

This contract repairs the specific transfer failures exposed by the frozen
Case 10 cold-reader test. It defines the next self-contained research receipt
before a different holdout is selected or any new model call is authorized.

The receipt should let a fresh agent or person reconstruct:

- the authoritative conversation;
- the decision state at the final source message;
- the interpretation and transformations applied to that source;
- admitted, rejected, deferred, and used pressure;
- the strong-control comparison and its limits;
- graph exposure, exact lineage, disposition custody, and causal evidence as
  separate facts;
- what the artifacts support and do not establish;
- the authorization state at the moment the receipt was frozen;
- which questions belong to the case, the cold reader, and the human product
  reviewer.

It does not judge whether the answer or decision is correct.

## What Case 10 taught us

The first receipt transferred most of the run but exposed six defects:

1. The summary softened the user's exact raise-and-walk plan and omitted its
   imminent deadline.
2. Broad custody wording invited the reader to say execution was “proven.”
3. A pre-call authorization snapshot was presented as current state after the
   reader call completed.
4. One `human_questions` field mixed case-domain diligence with product review.
5. The reader collapsed “no exact graph contribution was isolated” into the
   stronger claim that graph chunks were not used.
6. A supported claim was duplicated without a deterministic failure.

The frozen Case 10 receipt and output remain unchanged. This v2 contract is
prospective only.

The first attempted application to the closed Case 06 evidence stopped before
receipt assembly and exposed four additional structural requirements:

- exact anonymous outputs and reveal mapping must live inside the receipt, not
  only behind repository references;
- a pressure record must separate the frozen expected ID from the ID returned
  by the consumer;
- semantic hearing, identity custody, and visible/private effect consistency
  are distinct facts;
- partial token evidence needs an explicit state and scope rather than a false
  zero or a misleading whole-run total;
- the origin vocabulary must name V60 affordance pressure directly.

These fields were added before any Case 06 receipt or reader call. The stopped
application is preserved at
`research/gate7-case06-receipt-v2-2026-07-10/v2-application-audit.json`.

## What the Case 06 reader taught us

After provider-free assembly and validation, one frozen Case 06 reader call
tested v2 with zero retries and zero evaluator calls. It recovered the source
action, pressure-ID mismatch, semantic hearing, disposition/effect
contradiction, correct public stand-down, graph non-claim, bounded custody, and
as-of authorization more cleanly than the Case 10 reader.

It still omitted an explicit negative fact (`deadline_or_time_constraint` was
`not_stated`), failed to surface a material final user conditional inference,
compressed exact V60-affordance lineage into “no exact lineage,” and omitted
exact operating figures while retaining their evidence scope.

These are preserved transfer failures. This v2 contract and the completed Case
06 receipt are not retuned after the reader output. Any next version should
consider a bounded source-end field for user-stated beliefs or conditional
inferences and separate exact non-graph lineage from exact graph lineage in the
reader output. It should not add deterministic semantic judgment or more gates
merely to force a passing reconstruction.

## Hybrid boundary

The contract preserves the product's division of labor.

LLMs or humans remain responsible for:

- interpreting the messy conversation;
- describing the final decision state;
- identifying reasoning patterns and possible pressure;
- deciding whether a pressure applies, should be rejected, or should be
  deferred;
- explaining what changed and what remains uncertain;
- judging whether the receipt is useful.

Deterministic code may only:

- require explicit fields and bounded vocabularies;
- validate source and artifact references;
- preserve hashes, IDs, time scope, caps, and disposition identity;
- reject duplicate claims or questions;
- prevent graph exposure from being mislabeled as causal contribution;
- prevent custody-support fields from using unbounded proof language.

The validator does not read prose to decide which mental model is relevant. It
does not suppress an unusual lens because it appears unlikely. It allows an
empty pressure list, because correct no-pressure and stand-down outcomes must
remain representable.

## Two deterministic layers

The machine contract is:

`docs/evals/reasoning-run-receipt-v2.json`

It defines static JSON shape, required fields, allowed statuses, caps, and
field-level types.

The provider-free companion is:

`scripts/evals/validate_reasoning_run_receipt_v2.py`

It checks only cross-field relationships that are awkward in JSON Schema:

- source and artifact references exist;
- a source-stated action or an explicit `not_stated`/`unknown` value is present;
- deadline state is explicit rather than silently omitted;
- authorization time matches receipt-freeze time;
- the reader call and human review are named as future events outside that
  snapshot;
- question categories do not overlap;
- exact graph lineage and individual disposition are subsets of graph exposure;
- causal graph claims require a frozen ablation, exact lineage, and complete
  individual disposition;
- non-use dispositions cannot claim visible or private effects;
- normalized duplicate claims, questions, IDs, and required non-claims fail.

It also checks that anonymous output labels and reveal mappings match, that
expected and observed pressure IDs obey their declared identity state, and that
partial or unknown token evidence cannot masquerade as a whole-run total.

Neither layer makes a provider call or produces a semantic quality score.

## Exact source-end state

`source_end_state` always contains two explicit evidence fields:

```text
stated_next_action
deadline_or_time_constraint
```

Each has one of three statuses:

- `present` — requires a summary and exact source references;
- `not_stated` — requires an explicit empty summary and no source references;
- `unknown` — requires an explicit empty summary and no source references.

This is not a deterministic truth detector. The source summary is still written
by an LLM or human and later reviewed source-first. The contract merely makes
silent omission impossible.

## Self-contained comparison evidence

`comparison_evidence` contains the exact anonymous response objects, their
response hashes and token custody, the reveal mapping, and the blind review
summary. Artifact references remain for integrity and repository navigation,
but a fresh reader no longer has to trust an assembler's paraphrase of what the
two arms said.

## Pressure identity and semantic hearing

Every pressure record separates:

- `pressure_id` — the exact frozen expected identity;
- `observed_consumer_pressure_id` — the identity actually returned, or empty;
- `identity_status` — exact match, mismatch, not returned, or not applicable;
- `semantic_hearing_status` — substantive, thin, not reached, or unknown;
- `effect_consistency_status` — whether the returned visible/private effect is
  coherent with the output.

A renamed pressure can therefore receive a substantive semantic hearing while
still failing exact custody. Neither fact erases the other.

`lineage_ids` accepts exact non-empty trace strings rather than forcing every
existing JSON pointer or selector into the compact-ID grammar. Graph pressure
identities retain their stricter ID field separately.

## Authorization is a snapshot

The receipt no longer has a field called “current authorizations.” It has:

```text
authorization_snapshot.scope_label =
  receipt_freeze_snapshot_not_current_state
```

Its event ID, timestamp, and sequence must match receipt metadata. It must state
that `reader_call` and `human_review` occur outside the snapshot and require a
separate post-reader status artifact. A cold reader should reconstruct the
snapshot as-of state, not claim that it remains current after the call.

## Graph claim ladder

Graph evidence is split into four non-interchangeable levels:

1. `exposure_status` — whether exact graph IDs reached any relevant context;
2. `exact_lineage_status` — whether exact graph IDs entered a pressure;
3. `individual_disposition_status` — whether those exact IDs received their own
   use/reject/defer/private-guardrail decision;
4. `causal_contribution_status` — whether a prospectively frozen ablation
   identified a directional or replicated contribution.

Indirect exposure cannot support “the graph was used,” “the graph was not
used,” or “the graph changed the answer.” Exact lineage alone cannot support a
causal claim. This protects both against graph promotion and against false
stand-down.

## Question audiences

The receipt keeps three separate arrays:

- `case_domain_unknowns` — missing facts about the underlying decision;
- `reader_reconstruction_checks` — what the fresh agent should be able to
  recover from the receipt;
- `human_product_review_questions` — whether the receipt is understandable,
  useful, misleading, or too burdensome.

The last array is capped at three. The normal review flow should still ask one
human question at a time.

## Custody language

The only allowed claim level is:

```text
recorded_artifact_integrity_only
```

The positive custody summary and `artifacts_support` list may say that hashes,
IDs, and references support the recorded artifact relationship. They may not
use `proof`, `prove`, or `proven`. A separate negative list states that the
artifacts do not establish answer correctness, reasoning quality, real-world
outcomes, or independently verified external execution.

This lexical guard is intentionally narrow. It is not a general prose judge.

## Partial operability evidence

Token custody has its own `token_evidence_state` and `token_scope`. When only a
downstream pair has recorded token totals, the receipt may preserve that number
as `partial` and name its exact scope. Unknown totals use `null`, never numeric
zero. Cost, call, retry, and latency evidence retain their separate fields.

## Relationship to the Decision Work Receipt

`lolla.reasoning_run_receipt.v2` is a research/evaluation artifact for cold-
reader evidence. It is not a replacement for
`lolla.decision_work_receipt.v0`, the broader offline product artifact.

If Gate 7 later passes across multiple cases, the smallest useful v2 fields may
inform the Decision Work Receipt or runtime surface. That integration is Gate 8
work and is not authorized here.

## Next holdout protocol

1. Validate the synthetic prospective fixture and adversarial tests with zero
   provider calls.
2. Freeze a separate holdout-selection contract. Do not select for a favorable
   graph story.
3. Run the existing Stage A and strong-control/Lolla stages only under their own
   frozen call, cost, time, source-fidelity, and stop contracts.
4. Build a `frozen_for_reader` v2 receipt without tuning completed output.
5. Validate static shape and cross-field relationships before any reader call.
6. Freeze the reader prompt, schema, model, calls, cost, and timeout.
7. Use one reader call, zero retries, and zero evaluator calls.
8. Preserve a separate post-reader status artifact and perform source-first
   review before asking one human question.

## Non-authorizations

This contract does not authorize:

- a provider call;
- selecting or running the next holdout;
- changing the live skill or runtime;
- changing the graph or sending more graph material to Step 6;
- rewriting Case 10;
- judging answer quality;
- claiming human validation;
- Gate 8 integration.
