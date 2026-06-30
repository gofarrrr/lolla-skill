# Decision Work Brief PRD v0

Status: product-facing target PRD
Date: 2026-07-01

## Purpose

The Decision Work Brief is the user-facing layer that should travel with a
serious AI-assisted decision output.

The current Decision Work Receipt and Receipt Debug Summary can tell us whether
the process left inspectable artifacts. That is useful for maintainers, but it
is not enough for a customer. A customer does not mainly care that a pressure
surface existed or that a field has a status. They care:

- What decision was being made?
- What was the likely starting direction?
- What did Lolla challenge?
- What changed in the answer or action plan?
- What trade-off, risk, or missing condition became visible?
- What still might be wrong?
- What should nobody claim from this process?

The Decision Work Brief is the layer that should answer those questions in
plain language.

## Product Problem

AI can produce a polished memo very cheaply. The weak point is not prose. The
weak point is that the reader cannot easily see the work behind the prose:

- what conversation shaped the answer;
- what context was supplied;
- what assumptions were accepted too quickly;
- what alternatives were considered or dropped;
- what pushback happened;
- what changed after the pushback;
- what remains unresolved.

Lolla should make the decision less opaque. It should not merely produce a
better-sounding final answer. It should preserve enough of the reasoning process
that another person or agent can inspect how the answer came to be.

## Product Promise

The target promise is:

> Here is the revised answer, and here is the plain-language work brief showing
> what conversation produced it, what Lolla pressed on, what changed, what
> remains uncertain, and what the audit does not prove.

This is a proof-of-work style artifact, not a correctness certificate.

## Claim Stack

The public claim should be built in layers. Each layer must be backed by a
concrete artifact in the repo.

1. Problem claim
   AI can produce fluent recommendations without exposing what context,
   assumptions, missing information, or pressure shaped them.

2. Product claim
   Lolla adds a reasoning-audit layer between AI conversation and action.

3. Mechanism claim
   Lolla captures the conversation context, applies structured pressure,
   produces a revised answer, and preserves a decision trail.

4. User value claim
   A reviewer can inspect what was challenged, what changed, what remains
   missing, and what should not be overclaimed.

5. Boundary claim
   Lolla does not certify that the decision is correct. It makes the path to
   the decision more inspectable.

The Decision Work Brief must make this claim stack visible without forcing a
reader to understand Lolla's internal lanes.

## Current Repo Reality

Already built:

- Lolla runtime produces revised answers and archived artifacts.
- Decision Trail reports can preserve field status, missingness, source refs,
  and non-claims.
- Product Delta evals can compare vanilla and revised outputs in a non-human,
  provisional, internal way.
- Decision Work Receipts can inventory source/context, process shape, challenge
  surfaces, linked reports, missingness, and non-claims.
- Decision Work Receipt Debug Summary can render the receipt into Markdown for
  maintainers.

Not built:

- a user-facing brief that explains the decision consequence;
- a bounded interpretation pass that fills the brief from real local-private
  conversation/revised-answer context;
- a schema for the brief;
- validation showing the brief is useful rather than impressive-looking;
- runtime integration.

## Existing Codebase Anchors

This work should be nested into the system that already exists.

Use these existing production/eval modules as anchors:

- `engine/system_b/decision_work_receipt.py`
  The sparse receipt exporter. It already inventories source/context,
  process-shape metadata, challenge surfaces, linked report references,
  missingness, readiness, and non-claims.

- `engine/system_b/decision_work_receipt_debug_summary.py`
  The internal Markdown renderer over receipts. This should remain a maintainer
  diagnostic, not become the product brief.

- `engine/system_b/decision_trail_report.py`
  The sparse Decision Trail report exporter. It shows which semantic fields are
  available from structured artifacts and which require LLM or human
  interpretation.

- `engine/system_b/product_delta_boundary_lint.py`
  The deterministic overclaim lint. Future brief artifacts should pass this
  style of boundary check or an equivalent brief-specific lint.

- `scripts/evals/build_decision_work_receipt.py`
  Existing receipt CLI. Future brief work may read its outputs, but should not
  mutate run directories.

- `scripts/evals/render_decision_work_receipt_debug_summary.py`
  Existing internal debug renderer. Future user-facing brief rendering should be
  separate.

Use these docs as source-of-truth context:

- `docs/conversation-understanding/decision-work-receipt-prd-v0.md`
- `docs/conversation-understanding/decision-work-receipt-exporter-v0.md`
- `docs/conversation-understanding/decision-work-receipt-decision-gate-v0.md`
- `docs/conversation-understanding/decision-work-receipt-external-report-attachments-v0.md`
- `docs/conversation-understanding/decision-work-receipt-debug-summary-v0.md`
- `docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md`
- `docs/conversation-understanding/decision-trail-specialist-contracts-v0.md`
- `docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md`
- `docs/conversation-understanding/decision-trail-human-review-intake-packet-v0.md`

Use these review/eval artifacts as cautionary context:

- Product Delta found useful signals, but stayed non-human and provisional.
- Decision Trail specialist pilots found that local-private context is needed,
  but broad batches are not yet justified.
- The current Receipt Debug Summary proved that machinery labels are not enough
  for users.

Do not build a parallel interpretation system inside the receipt lane. The
Decision Work Brief may consume receipt, Decision Trail, and Product Delta
artifacts, but its semantic content must come from bounded LLM or human
interpretation with deterministic custody around it.

## Layering

The product should be layered like this:

1. Revised answer
   The answer the user might act on.

2. Decision Work Brief
   Plain-language explanation of what changed and what remains unresolved.

3. Evidence Receipt
   Machine-readable custody, source status, missingness, linked reports, and
   non-claims.

4. Local private archive
   Raw conversation, memo, revised answer, provider records, and private ledgers
   that should not be copied into checked-in artifacts.

The brief is the user-facing story. The receipt is the audit appendix.

## Required Brief Sections

The first version should use this structure:

```text
Decision
What decision was being made?

Starting Direction
What was the original or likely next action before Lolla pressure?

What Lolla Pressed On
What assumption, missing gate, ignored stakeholder, weak frame, or trade-off was challenged?

What Changed
What changed in recommendation, threshold, sequence, evidence gate, stop rule, or scope?

What This Means For Action
What would the decision-maker do differently now?

What Still Might Be Wrong
What remains unresolved, uncertain, missing, or dependent on human judgment?

What Was Not Proven
What this audit must not claim.

Evidence Receipt
Short references to the receipt, Decision Trail report, Product Delta report, and local archive custody.
```

## User-Facing Output Example Shape

The output should read more like this than like an artifact inventory:

```text
Decision
Whether to launch the public enterprise beta now.

Starting Direction
The starting answer leaned toward launch because enterprise interest looked strategically important.

What Lolla Pressed On
The audit challenged whether buyer interest was being treated as proof of readiness before support, security, rollback, and customer-success gates were named.

What Changed
The recommendation moved from "launch" to "launch only if specific readiness gates are met; otherwise keep the beta private."

What This Means For Action
The team should decide against a simple launch/no-launch frame and instead run a conditional readiness gate.

What Still Might Be Wrong
The audit cannot verify support capacity, actual enterprise buyer commitment, or internal owner alignment from the exported safe artifacts alone.

What Was Not Proven
This does not prove the beta should launch. It shows the decision conditions that emerged after pressure.
```

That is the product target. The receipt/debug summary should only back this
story; it should not replace it.

## Interpretation Boundary

The brief needs interpretation. Deterministic code should not pretend to know
what the messy conversation really meant.

LLMs or humans may interpret:

- likely starting action;
- revised likely action;
- important alternatives;
- stakeholder obligations;
- values and priorities;
- assistant influence;
- useful friction versus noisy friction;
- lost value;
- what changed;
- action consequence;
- unresolved judgment.

Deterministic code may preserve:

- schema shape;
- source refs;
- source status;
- redaction/private availability;
- artifact health;
- missingness;
- non-claims;
- required fields;
- lint against authority leakage;
- whether a field is LLM-interpreted, human-validated, structured, missing, or
  redacted.

This follows the core Lolla doctrine: probabilistic interpretation inside
deterministic custody.

## Input Modes

### checked_in_safe_mode

Use only checked-in safe artifacts. This mode may generate a sparse or mostly
missing brief. It must not copy raw transcripts, raw revised answers, raw memos,
provider text, private ledgers, local absolute paths, or secrets.

This mode is good for schema and custody testing. It is not enough for a real
customer-facing brief.

### local_private_mode

Use local private artifacts from a completed run directory, including raw
conversation and revised answer when explicitly allowed. The brief may be
generated locally, but checked-in examples must remain sanitized and should not
copy private content.

This is the mode most likely to produce a useful Decision Work Brief.

### future_runtime_mode_not_implemented

The brief may later become part of the live Lolla workflow, but that is out of
scope until the offline shape proves useful.

## Output Contract

A future `lolla.decision_work_brief.v0` schema should include:

- `schema_version`
- `brief_metadata`
- `mode`
- `human_validated: false` unless reviewed by a human
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls`
- `source_refs`
- `sections`
- `non_claims`
- `custody_flags`

Every semantic section should carry:

- `status`
- `source_status`
- `source_refs`
- `interpreted_by`
- `human_validated`
- `uncertainty`
- `value`
- `empty_meaning`

Recommended statuses:

- `populated_from_llm_interpretation`
- `populated_from_human_review`
- `available_from_structured_artifact`
- `not_supplied`
- `requires_llm_interpretation`
- `requires_human_review`
- `available_in_private_artifact_not_exported`
- `available_but_redacted_in_safe_mode`
- `unclear`

## What The Brief Must Not Do

The brief must not:

- score answer quality;
- say Lolla was right;
- say Lolla improved the decision unless a later review process supports that;
- authorize an agent to act;
- hide lost value;
- imply clean artifacts mean good advice;
- turn process evidence into correctness evidence;
- copy raw/private content into checked-in examples;
- use a broad LLM judge;
- flatten specialist disagreement into a score.

## Delivery PR Sequence

### PR113: Decision Work Brief PRD And Receipt Debug Correction v0

Status: current PR.

Purpose:

- Correct the previous "demo summary" abstraction error.
- Keep the receipt Markdown renderer as an internal debug summary.
- Define the Decision Work Brief as the product-facing target.

Already in this PR:

- `docs/conversation-understanding/decision-work-brief-prd-v0.md`
- `docs/conversation-understanding/decision-work-receipt-debug-summary-v0.md`
- `docs/conversation-understanding/decision-work-receipt-debug-summary-launch-public-enterprise-beta-v0.md`
- `engine/system_b/decision_work_receipt_debug_summary.py`
- `scripts/evals/render_decision_work_receipt_debug_summary.py`
- `tests/test_decision_work_receipt_debug_summary.py`
- top-level doc alignment in `README.md`, `HOW_IT_WORKS.md`,
  `PROGRESS.md`, and `docs/board/README.md`

Must not:

- present the debug summary as a customer proof-of-work artifact;
- add runtime behavior;
- invoke `$lolla`;
- add semantic interpretation;
- add a judge, score, automatic labels, or agent authorization.

Validation:

- focused debug-summary tests;
- Decision Work Receipt tests;
- Decision Trail report tests;
- Product Delta boundary lint;
- Markdown link check;
- privacy/content marker scan.

### PR114: Decision Work Brief Schema v0

Create the schema and docs only. No generator. No runtime integration.

Likely files:

- `docs/conversation-understanding/decision-work-brief-v0.json`
- `docs/conversation-understanding/decision-work-brief-schema-v0.md`
- `tests/test_decision_work_brief_schema.py`
- light updates to `README.md`, `HOW_IT_WORKS.md`, and `PROGRESS.md`

What it needs to define:

- `schema_version: lolla.decision_work_brief.v0`
- `brief_metadata`
- `mode`
- `source_refs`
- `custody_flags`
- `non_claims`
- semantic sections for the required brief sections
- per-section status, source status, source refs, interpreter, uncertainty,
  human validation flag, value, and empty meaning

Must not:

- build a generator;
- read archives;
- call models;
- add runtime integration;
- infer meaning from existing prose.

Validation should prove:

- required sections exist;
- authority fields are absent;
- non-claims are required;
- `human_validated` defaults false;
- `product_proof`, `answer_quality_scored`, and `agent_action_authorized` are
  false;
- source refs and source-status fields are mandatory for populated semantic
  sections.

### PR115: Decision Work Brief Local Packet Builder v0

Build local-private packets for bounded LLM interpretation. The packet builder
should gather the minimum needed context from a completed run directory and
preserve source refs without checking in raw/private content.

Likely files:

- `engine/system_b/decision_work_brief_packets.py`
- `scripts/evals/build_decision_work_brief_packets.py`
- `tests/test_decision_work_brief_packets.py`
- `docs/conversation-understanding/decision-work-brief-packet-builder-v0.md`
- optional checked-in metadata-only packet fixture under
  `reviews/codex-assisted/decision-work-brief-packets-v0/`

Inputs:

- completed run directory;
- optional Decision Work Receipt JSON;
- optional Decision Trail report JSON;
- optional Product Delta report JSON;
- mode flag: `metadata_only` or `include_text_local_private`.

The packet builder may read raw/private text only in explicit local-private
mode and must mark generated packets unsafe for commit when they contain text.

Must not:

- check in raw transcript, revised answer, memo, provider text, private ledgers,
  or local absolute paths;
- call models;
- generate a brief;
- mutate archives;
- write outputs inside the run directory;
- change runtime behavior.

Validation should prove:

- output path must be outside run dir;
- metadata-only fixtures are safe to commit;
- local-private include-text outputs are marked unsafe for commit;
- source refs resolve locally when safe;
- private/text fields are omitted from checked-in fixtures;
- errors are sanitized.

### PR116: Codex-Assisted Brief Draft Pilot v0

Use Codex-assisted provisional interpretation to fill brief sections for one or
two local-private runs. The output should be clearly marked unvalidated and
provisional.

Likely files:

- `reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md`
- `tests/test_decision_work_brief_draft_pilot.py`

How to do it:

- Use one or two operator-selected completed runs.
- Use PR115 packet outputs locally.
- Fill `lolla.decision_work_brief.v0` sections with Codex-assisted provisional
  interpretation.
- Check in only sanitized summaries, not raw/private content.

Must not:

- call providers from repo code;
- treat Codex output as human validation;
- claim product proof;
- hide lost value or unresolved uncertainty;
- present a positive brief without missingness and non-claims;
- broaden into a batch.

Validation should prove:

- every brief has the required sections;
- every semantic section has source refs/status and uncertainty;
- every populated section is marked `populated_from_llm_interpretation`;
- `human_validated` is false;
- `product_proof` is false;
- no raw/private markers or local absolute paths appear;
- at least one section records what remains unresolved;
- at least one section records what the audit must not claim.

### PR117: Decision Work Brief Markdown Renderer v0

Render a populated structured brief JSON into a simple user-facing Markdown
brief.

Likely files:

- `engine/system_b/decision_work_brief_renderer.py`
- `scripts/evals/render_decision_work_brief.py`
- `tests/test_decision_work_brief_renderer.py`
- `docs/conversation-understanding/decision-work-brief-renderer-v0.md`
- optional sanitized example under `docs/board/` only if it reads like the
  decision story, not like machinery inventory.

Must not:

- read arbitrary report prose;
- infer missing semantic content;
- transform missing sections into positive prose;
- copy private/raw text;
- hide uncertainty;
- imply approval or correctness.

Validation should prove:

- missing sections render as missing/uncertain, not as empty confidence;
- non-claims are always rendered;
- source/custody appendix is short and secondary;
- raw/private marker scan is clean;
- the output begins with the decision story, not the receipt inventory.

### PR118: Brief Usefulness Review And Delivery Gate v0

Review whether the brief finally answers the user question:

> What did this process make me see or do differently?

If the answer is still mostly artifact inventory, stop and simplify.

Likely files:

- `docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-usefulness-review-v0/review.json`
- `tests/test_decision_work_brief_usefulness_review.py`

Review questions:

- Can a reader name the decision in under 30 seconds?
- Can a reader name the starting direction?
- Can a reader name what Lolla pressed on?
- Can a reader name what changed?
- Can a reader name what action would be different now?
- Can a reader name what still might be wrong?
- Can a reader distinguish the brief from the receipt appendix?
- Does the brief feel useful, or merely impressive?
- Does it overclaim because the receipt is clean?

Decision outcomes:

- proceed toward a tiny runtime-adjacent plan only if the brief is genuinely
  useful;
- repeat PR116/PR117 on one more case if evidence is promising but thin;
- simplify the brief if it still reads like machinery;
- pause until human review if Codex-assisted interpretation is too agreeable.

Must not:

- declare product readiness;
- add runtime integration;
- claim human validation;
- score answer quality;
- authorize agent action.

## Success Criteria

The phase succeeds when a reader can quickly answer:

- what decision was being made;
- what the likely starting direction was;
- what Lolla challenged;
- what changed in action, threshold, sequence, gate, stop rule, or scope;
- what still might be wrong;
- what the audit does not prove;
- where the supporting receipt lives.

The phase fails if the output mainly lists internal Lolla machinery.

## Non-Build List

Do not build in this phase:

- runtime integration;
- prompt changes in `SKILL.md`;
- `scripts/skill/*` changes;
- graph DB, memory, embeddings, chunking, GraphRAG;
- broad judge;
- answer-quality score;
- automatic labels;
- agent action authorization;
- dashboard/UI;
- customer claims based only on checked-in safe fixtures.

## Relationship To Receipt Debug Summary

The Decision Work Receipt Debug Summary remains useful as an internal tool. It
can tell maintainers whether the process left inspectable artifacts and which
semantic fields are still missing.

But it should not be presented as the customer-facing proof-of-work artifact.
It names the machinery. The Decision Work Brief must explain the decision
consequence.
