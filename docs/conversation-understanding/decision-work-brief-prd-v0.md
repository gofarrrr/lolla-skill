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

Status: implemented in previous PR.

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

Status: implemented in current schema slice.

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

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-v0.json`
- `docs/conversation-understanding/decision-work-brief-schema-v0.md`
- `tests/test_decision_work_brief_schema.py`
- light discoverability updates in `README.md`, `HOW_IT_WORKS.md`,
  `PROGRESS.md`, and `docs/board/README.md`

Current meaning:

- the Decision Work Brief is now a first-class schema contract;
- the schema requires the user-facing semantic sections;
- every section carries source status, source refs, interpreter, uncertainty,
  human-validation state, value, and empty meaning;
- lower-claim custody flags and explicit non-claims are required;
- authority, score, approval, and agent-action fields remain forbidden;
- no populated brief, generator, packet builder, renderer, runtime integration,
  model call, archive mutation, or semantic inference has been added.

Next recommended slice:

```text
PR115 Decision Work Brief Local Packet Builder v0
```

### PR115: Decision Work Brief Local Packet Builder v0

Status: implemented in current packet-builder slice.

Build deterministic packets for bounded LLM or human interpretation. The packet
builder gathers source availability and custody metadata from a completed run
directory and preserves source refs without checking in raw/private content.

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
- mode flag: `metadata_only` or `local_private`;
- optional local-private `--include-private-text` flag.

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

Implemented in this PR:

- `engine/system_b/decision_work_brief_packets.py`
- `scripts/evals/build_decision_work_brief_packets.py`
- `tests/test_decision_work_brief_packets.py`
- `docs/conversation-understanding/decision-work-brief-packet-builder-v0.md`

Current meaning:

- maintainers can build `lolla.decision_work_brief_packets.v0` from a completed
  run directory;
- metadata-only mode is the default checked-in-safe packet mode;
- optional Decision Work Receipt, Decision Trail, and Product Delta reports can
  be linked by metadata only;
- local-private include-text mode is explicit and marked unsafe for commit;
- all eight future Decision Work Brief sections get packet questions, allowed
  source refs, missing/redacted refs, known limits, and PR114 schema refs;
- no populated brief, renderer, runtime integration, model call, archive
  mutation, answer-quality scoring, product-proof claim, or agent-action
  authorization has been added.

Next recommended slice:

```text
PR116 Codex-Assisted Brief Draft Pilot v0
```

### PR116: Codex-Assisted Brief Draft Pilot v0

Status: implemented in current draft-pilot slice.

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

Implemented in this PR:

- `reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md`
- `tests/test_decision_work_brief_draft_pilot.py`

Current meaning:

- PR116 uses one completed run,
  `ceo-remove-founding-cofounder/20260627T093131Z_59d153`;
- a PR115 metadata-only packet was generated locally and used as bounded source
  and custody input, but the packet was not checked in;
- no local-private include-text packet was used for the checked-in draft;
- the review artifact embeds one checked-in-safe
  `lolla.decision_work_brief.v0` object;
- the draft carries all eight required brief sections, source refs,
  uncertainty, a human follow-up question set, an action-consequence read,
  missingness, a lost-value or overcorrection note, custody flags, and
  non-claims;
- the draft is Codex-assisted, provisional, not human validated, not product
  proof, not answer-quality measurement, and not agent action authorization;
- no renderer, runtime integration, model-call code, archive mutation, broad
  batch, customer board demo, or usefulness review has been added.

Next recommended slice:

```text
PR117 Decision Work Brief Markdown Renderer v0
```

### PR117: Decision Work Brief Markdown Renderer v0

Status: implemented in current renderer slice.

Render a populated structured brief JSON into a simple user-facing Markdown
brief.

Likely files:

- `engine/system_b/decision_work_brief_renderer.py`
- `scripts/evals/render_decision_work_brief.py`
- `tests/test_decision_work_brief_renderer.py`
- `docs/conversation-understanding/decision-work-brief-renderer-v0.md`
- optional sanitized example under `docs/conversation-understanding/` unless it
  is ready for board/customer demo use.

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

Implemented in this PR:

- `engine/system_b/decision_work_brief_renderer.py`
- `scripts/evals/render_decision_work_brief.py`
- `tests/test_decision_work_brief_renderer.py`
- `docs/conversation-understanding/decision-work-brief-renderer-v0.md`
- `docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md`

Current meaning:

- existing `lolla.decision_work_brief.v0` JSON can be rendered to Markdown;
- the CLI can render either a standalone brief JSON or an embedded PR116 pilot
  review brief by index;
- the rendered Markdown begins with the decision-story sections before evidence
  receipt, non-claims, and custody limits;
- uncertain or missing sections render status plainly instead of being smoothed
  into prose;
- non-claims, custody flags, source refs, source status, uncertainty, and
  human-validation state remain visible;
- the checked-in rendered example stays in conversation-understanding rather
  than `docs/board/`;
- no generator, semantic inference, runtime integration, model-call code,
  archive mutation, answer-quality measurement, product proof, human
  validation, broad batch, or agent action authorization has been added.

### PR118: Brief Usefulness Review And Delivery Gate v0

Status: implemented in current usefulness-review slice.

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

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-usefulness-review-v0/review.json`
- `tests/test_decision_work_brief_usefulness_review.py`

Current meaning:

- PR118 reviews the receipt/debug-summary layer, the PR116 structured draft, and
  the PR117 rendered Markdown example;
- the rendered brief is judged promising because it names decision consequence
  more clearly than receipt inventory;
- the strongest missingness/thinness risk is that one Codex-assisted
  checked-in-safe case cannot establish starting direction, vanilla overlap,
  user intent, or lost-value severity;
- the strongest overclaim risk is that clean Markdown can make provisional
  interpretation feel more complete than the source boundary permits;
- the gate outcome is `proceed_to_tiny_second_case`;
- no product readiness, runtime integration, human validation, broad batch,
  customer marketing copy, answer-quality measurement, product proof, or agent
  action authorization has been added.

Recommended next slice:

```text
PR119 Decision Work Brief Second Tiny Case Pilot v0
```

### PR119: Decision Work Brief Second Tiny Case Pilot v0

Status: implemented in current second-case pilot slice.

Repeat the PR115 to PR117 path on exactly one additional completed run from a
different decision type, then compare it to the first PR116/PR117 case.

Likely files:

- `docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md`
- `reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md`
- `tests/test_decision_work_brief_second_tiny_case_pilot.py`

How to do it:

- Select one completed run that is not `ceo-remove-founding-cofounder`.
- Generate PR115 metadata-only packet context locally.
- Use Codex-assisted provisional interpretation only as an offline review aid.
- Check in only sanitized review JSON and rendered Markdown.
- Compare the second case to the first case.
- Decide whether the next responsible move is a small pattern review, a third
  diversity case, a schema/renderer patch, human review, or simplification.

Must not:

- run `$lolla`;
- invoke the skill;
- call providers from repo code;
- check in raw/private text;
- mutate archives;
- create a broad batch;
- create customer marketing copy;
- recommend runtime integration from two cases alone;
- claim product proof, human validation, answer-quality scoring, or agent
  authorization.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md`
- `reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md`
- `tests/test_decision_work_brief_second_tiny_case_pilot.py`

Current meaning:

- PR119 uses `launch-public-enterprise-beta/20260627T104146Z_7bfe79`;
- PR115 metadata-only packets and local metadata-only Decision Trail/Decision
  Work Receipt support artifacts were generated locally and not checked in;
- no local-private include-text packet was used;
- the checked-in review embeds one sanitized `lolla.decision_work_brief.v0`
  draft and links the rendered Markdown example;
- the second brief names a concrete action consequence: do not default to the
  largest logo or public launch; make both prospects accept the same paid,
  scoped private-pilot shape and choose based on evidence-producing buyer
  behavior plus tripwire gates;
- the comparison finds the brief shape also works, provisionally, outside the
  founder/cofounder governance case;
- the strongest risk remains thin safe context and overclaim from clean
  Markdown;
- the gate outcome is `proceed_to_small_pattern_review`;
- no runtime integration, product readiness, human validation, broad batch,
  customer demo, answer-quality measurement, product proof, or agent action
  authorization has been added.

Recommended next slice:

```text
PR120 Decision Work Brief Small Pattern Review v0
```

### PR120: Decision Work Brief Small Pattern Review v0

Status: implemented in current small-pattern review slice.

Compare the first two checked-in-safe rendered Decision Work Brief pilots and
decide one narrow follow-on.

Likely files:

- `docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-small-pattern-review-v0/review.json`
- `tests/test_decision_work_brief_small_pattern_review.py`

How to do it:

- Review `ceo-remove-founding-cofounder`.
- Review `launch-public-enterprise-beta`.
- Ask whether both briefs name action consequence, preserve uncertainty, and
  remain useful because they explain decision work rather than internal
  artifacts.
- Choose only one follow-on path.

Must not:

- create a new case;
- run `$lolla`;
- invoke the skill;
- call providers from repo code;
- mutate archives;
- broaden to a batch;
- patch the renderer unless the review gate chooses that path;
- claim product proof, human validation, answer-quality scoring, or agent
  authorization.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-small-pattern-review-v0/review.json`
- `tests/test_decision_work_brief_small_pattern_review.py`

Current meaning:

- PR120 compares the first two rendered briefs;
- both cases name concrete action consequences and preserve uncertainty;
- the renderer still feels somewhat internal, but not enough to block one more
  diversity case;
- the strongest useful signal is action consequence;
- the strongest overclaim risk is false confidence from clean brief prose before
  human validation or local-private adequacy checks;
- the gate outcome is `proceed_to_third_diversity_case`;
- no runtime integration, product readiness, human validation, broad batch,
  customer demo, answer-quality measurement, product proof, or agent action
  authorization has been added.

Recommended next slice:

```text
PR121A Decision Work Brief Third Diversity Case Pilot v0
```

### PR121A: Decision Work Brief Third Diversity Case Pilot v0

Status: implemented in current third-diversity-case slice.

Follow PR120's `proceed_to_third_diversity_case` gate and run exactly one more
checked-in-safe pilot on a third decision type.

Likely files:

- `docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md`
- `reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md`
- `tests/test_decision_work_brief_third_diversity_case_pilot.py`

How to do it:

- Use the preferred completed run, `deploy-assisted-intake-routing`, if
  available.
- Generate PR115 metadata-only packet context locally.
- Use Codex-assisted provisional interpretation only as an offline review aid.
- Check in only sanitized review JSON and rendered Markdown.
- Compare briefly to the first two cases.
- Decide the next gate.

Must not:

- implement PR121B or PR121C in the same slice;
- create a fourth case;
- call providers from repo code;
- check in raw/private text;
- mutate archives;
- create a broad batch;
- create customer marketing copy;
- recommend runtime integration from three cases alone;
- claim product proof, human validation, answer-quality scoring, or agent
  authorization.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md`
- `reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json`
- `docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md`
- `tests/test_decision_work_brief_third_diversity_case_pilot.py`

Current meaning:

- PR121A uses `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`;
- PR115 metadata-only packets and local metadata-only Decision Trail/Decision
  Work Receipt support artifacts were generated locally and not checked in;
- no local-private include-text packet was used;
- the checked-in review embeds one sanitized `lolla.decision_work_brief.v0`
  draft and links the rendered Markdown example;
- the third brief names a concrete action consequence: run a 48-hour backlog
  diagnostic, keep the pilot to one clinic and scheduling/billing routing,
  compress controls into four operating gates, and predefine pause triggers;
- the comparison finds the brief shape also works, provisionally, outside
  founder governance and enterprise launch decisions;
- the strongest risk remains source thinness and overclaim from clean Markdown;
- the gate outcome is `proceed_to_three_case_pattern_review`;
- no runtime integration, product readiness, human validation, broad batch,
  customer demo, answer-quality measurement, product proof, or agent action
  authorization has been added.

Recommended next slice:

```text
PR122 Decision Work Brief Three-Case Pattern Review v0
```

### PR122: Decision Work Brief Three-Case Pattern Review v0

Status: implemented in this slice.

Purpose:

Review the three existing checked-in-safe rendered Decision Work Brief pilots
and decide whether the brief format is useful enough to expand, needs renderer
language repair, needs local-private adequacy checking, should pause for human
review, or should simplify.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-three-case-pattern-review-v0/review.json`
- `tests/test_decision_work_brief_three_case_pattern_review.py`

Current meaning:

- PR122 reviews exactly three existing cases:
  `ceo-remove-founding-cofounder`, `launch-public-enterprise-beta`, and
  `deploy-assisted-intake-routing`;
- the pattern read is `useful_but_language_too_internal`;
- the strongest useful signal is that all three briefs name concrete action
  consequences that differ by decision family;
- the strongest missingness/thinness risk is that checked-in-safe context still
  cannot verify private nuance, user intent, starting-direction overlap, lost
  value, buyer reality, compliance tolerance, or human judgment;
- the strongest overclaim risk is that clean rendered prose can create false
  confidence before human validation or local-private adequacy checks;
- the strongest product-language risk is that the current renderer still puts
  field labels, status vocabulary, source refs, and custody details too close to
  the main story;
- the gate outcome is `proceed_to_plain_language_renderer_patch`;
- no fourth case, five-case batch, runtime integration, local-private checked-in
  text, product readiness, human validation, broad judge, answer-quality
  scoring, product proof, or agent authorization has been added.

Recommended next slice:

```text
PR123 Decision Work Brief Plain-Language Renderer Patch v0
```

### PR123: Decision Work Brief Plain-Language Renderer Patch v0

Status: implemented in this slice.

Purpose:

Patch the deterministic Markdown renderer so the main body reads like a
product-facing decision brief while preserving uncertainty, source limits,
custody flags, and non-claims in a compact evidence section.

Implemented in this PR:

- `engine/system_b/decision_work_brief_renderer.py`
- `tests/test_decision_work_brief_renderer.py`
- `tests/test_decision_work_brief_plain_language_renderer_patch.py`
- `docs/conversation-understanding/decision-work-brief-renderer-v0.md`
- `docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md`
- `docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md`
- `docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md`
- `docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md`

Current meaning:

- PR123 changes renderer presentation only; it does not change
  `lolla.decision_work_brief.v0`;
- the renderer maps the eight schema sections into six plain-language headings:
  "The decision", "What changed", "What this means for action", "What still
  might be wrong", "What this does not prove", and "Evidence and limits";
- source refs, section uncertainty, custody flags, and non-claims move into the
  compact "Evidence and limits" section;
- PR116, PR119, and PR121A review-wrapper inputs remain supported;
- all three checked-in rendered examples are regenerated;
- no fourth case, five-case batch, runtime integration, model-call code,
  archive mutation, human validation, product proof, answer-quality scoring, or
  agent authorization has been added.

Recommended next slice:

```text
PR124 Plain-Language Brief Re-Review v0
```

PR124 should review whether the regenerated examples actually read better
before moving to local-private adequacy checks, more cases, or runtime planning.

### PR124: Plain-Language Brief Re-Review v0

Status: implemented in this slice.

Purpose:

Review the three PR123 regenerated rendered briefs and decide whether the
plain-language renderer patch solved enough of the product-surface problem to
move the next blocker to source depth.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md`
- `reviews/codex-assisted/decision-work-brief-plain-language-rereview-v0/review.json`
- `tests/test_decision_work_brief_plain_language_rereview.py`

Current meaning:

- PR124 reviews exactly the three PR123 rendered examples;
- the main body is readable enough for a busy decision-maker to name the
  decision, action consequence, uncertainty, and non-claims;
- the main remaining blocker is source depth/private context, not renderer
  language;
- the decision gate is `proceed_to_local_private_adequacy_check`;
- no renderer changes, new cases, local-private checked-in text, runtime
  integration, product proof, human validation, answer-quality scoring, or
  agent authorization has been added.

Recommended next slice:

```text
PR125 Decision Work Brief Local-Private Adequacy Check v0
```

### PR125: Decision Work Brief Local-Private Adequacy Check v0

Status: implemented in this slice.

Purpose:

Run exactly one read-only local-private shadow review against an existing
plain-language brief and record only safe conclusions about whether richer
context changes the brief story.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md`
- `reviews/codex-assisted/decision-work-brief-local-private-adequacy-check-v0/review.json`
- `tests/test_decision_work_brief_local_private_adequacy_check.py`

Current meaning:

- PR125 follows PR124's `proceed_to_local_private_adequacy_check` gate;
- it selects one existing case:
  `launch-public-enterprise-beta/20260627T104146Z_7bfe79`;
- it completes a read-only local-private shadow review and checks in only safe
  conclusions;
- the local-private adequacy result is
  `adequate_but_missing_private_nuance`;
- the decision read, starting-direction read, and action consequence did not
  materially change;
- source-depth, lost-value, buyer reality, and overclaim risks remain material;
- the decision gate is `proceed_to_expansion_or_runtime_decision_gate`;
- no raw conversation, raw revised answer, raw memo, provider text, private
  ledgers, local absolute paths, secrets, runtime integration, product proof,
  human validation, answer-quality scoring, or agent authorization has been
  checked in or added.

Recommended next slice:

```text
PR126 Decision Work Brief Expansion / Runtime Attachment Decision Gate v0
```

### PR126: Decision Work Brief Expansion / Runtime Attachment Decision Gate v0

Status: implemented in this slice.

Purpose:

Use PR124 readability evidence, PR125 local-private adequacy evidence, and the
three-case action-consequence pattern to choose the next phase without
implementing runtime attachment.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md`
- `reviews/codex-assisted/decision-work-brief-expansion-runtime-decision-gate-v0/review.json`
- `tests/test_decision_work_brief_expansion_runtime_decision_gate.py`

Current meaning:

- PR126 follows PR125's `proceed_to_expansion_or_runtime_decision_gate`;
- it selects `run_more_local_private_adequacy_checks`;
- runtime attachment is still premature;
- the brief is readable and one local-private check did not undermine it, but
  one case is not enough to bound source-depth and overclaim risk;
- no runtime integration, five-case batch, renderer patch, new case, model-call
  code, archive mutation, product proof, human validation, answer-quality
  scoring, broad judge, automatic labels, or agent authorization has been
  added.

Recommended next slice:

```text
PR127 Decision Work Brief Conversation Interpretation Gap Map v0
```

### PR127: Decision Work Brief Conversation Interpretation Gap Map v0

Status: implemented in this slice.

Purpose:

Map what richer conversation information the current Decision Work Brief lane
can and cannot preserve before building more extraction or runtime machinery.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md`
- `reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json`
- `tests/test_decision_work_brief_conversation_interpretation_gap_map.py`

Current meaning:

- PR127 reviews the three existing brief cases:
  `ceo-remove-founding-cofounder`, `launch-public-enterprise-beta`, and
  `deploy-assisted-intake-routing`;
- it classifies desired conversation fields as clear, partial,
  local-private-only, LLM-interpretable, human-review-dependent, not currently
  captured, unsafe to check in, not relevant, or unclear;
- it separates fields deterministic code can preserve as metadata/custody from
  fields that require LLM interpretation or later human review;
- it finds repeated gaps around likely starting direction, live and abandoned
  options, option status, user values, stakeholder constraints, assistant
  influence, lost value, overcorrection risk, and safe handoff boundaries;
- it selects `define_interpretation_target_contract`;
- no extractor, runtime integration, prompt change, live skill change,
  model-call code, archive mutation, product proof, human validation,
  answer-quality scoring, broad judge, automatic label, or agent authorization
  has been added.

Recommended next slice:

```text
PR128 Decision Work Conversation Interpretation Target Contract v0
```

### PR128: Decision Work Conversation Interpretation Target Contract v0

Status: implemented in this slice.

Purpose:

Define the future target contract for conversation interpretation and custody
fields without implementing extraction.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`
- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json`
- `tests/test_decision_work_conversation_interpretation_contract.py`

Current meaning:

- PR128 follows PR127's `define_interpretation_target_contract` gate;
- it defines `lolla.decision_work_conversation_interpretation_contract.v0`;
- it groups target fields under decision shape, options and paths,
  conversation process, provided context and evidence, stakeholders and values,
  constraints and unknowns, audit pressure and change, losses and
  overcorrection, evidence and custody, brief handoff, and agent-inspection
  handoff;
- every field records owner, interpretation requirement, deterministic
  allowance, human-review conditions, source-ref requirement, empty meaning,
  privacy handling, checked-in-safe policy, local-private policy, brief feed,
  agent-inspection feed, and the rule that it must not be used as a quality
  label;
- deterministic code owns schema shape, source refs, source status,
  missingness, redaction/private availability, custody flags, validation, and
  non-claims;
- messy interpretation remains owned by bounded LLM interpretation or later
  human review;
- no runtime extraction, prompt change, live skill change, model-call code,
  archive mutation, product proof, human validation, answer-quality scoring,
  broad judge, automatic label, or agent authorization has been added.

Recommended next slice:

```text
PR129 Decision Work Conversation Interpretation Contract Packet Review v0
```

### PR129: Decision Work Conversation Interpretation Contract Packet Review v0

Status: implemented in this slice.

Purpose:

Compare the PR128 conversation interpretation target contract against the
current completed-run artifact and Decision Work Brief packet surface.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-contract-packet-review-v0/review.json`
- `tests/test_decision_work_conversation_interpretation_contract_packet_review.py`

Current meaning:

- PR129 reviews the cofounder, launch-beta, and intake-routing cases;
- it confirms current PR115 metadata-only packets can carry source refs,
  source availability, redaction/private availability, missingness, custody
  flags, and section-level future questions;
- it maps every PR128 contract field to current support, support source,
  required next capability, brief feed, agent-inspection feed, privacy/redaction
  policy, and the rule that the field must not become a quality label;
- it finds that current artifacts can support some checked-in-safe fields and
  status-only custody fields, but many fields remain partial, local-private
  only, LLM-interpretable, human-review-dependent, or not captured;
- it selects `build_offline_interpretation_packet`;
- no contract implementation, runtime extractor, prompt change, live skill
  change, model-call code, archive mutation, product proof, human validation,
  answer-quality scoring, broad judge, automatic label, or agent authorization
  has been added.

Recommended next slice:

```text
PR130 Decision Work Conversation Interpretation Offline Packet v0
```

### PR130: Decision Work Conversation Interpretation Offline Packet v0

Status: implemented in this slice.

Purpose:

Build a deterministic offline packet that prepares bounded source/status input
for future interpretation against the PR128 contract.

Implemented in this PR:

- `engine/system_b/decision_work_conversation_interpretation_packets.py`
- `scripts/evals/build_decision_work_conversation_interpretation_packets.py`
- `tests/test_decision_work_conversation_interpretation_packets.py`
- `docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md`

Current meaning:

- PR130 follows PR129's `build_offline_interpretation_packet` gate;
- it defines `lolla.decision_work_conversation_interpretation_packets.v0`;
- it reuses the PR115 metadata-only packet builder to collect completed-run
  source availability, redaction/private status, missingness, and custody
  facts;
- it maps the PR128 contract field groups into a packet with source refs,
  source status, field policies, future interpretation questions, known limits,
  and required future output refs;
- it supports `checked_in_safe` and `local_private_metadata` modes, but both
  remain metadata/status only;
- it records `semantic_fields_filled: false`, `model_calls: 0`,
  `human_validated: false`, `product_proof: false`,
  `answer_quality_scored: false`, and `agent_action_authorized: false`;
- no semantic PR128 fields are filled;
- no runtime extractor, prompt change, live skill change, model-call code,
  archive mutation, product proof, human validation, answer-quality scoring,
  broad judge, automatic label, or agent authorization has been added.

Recommended next slice:

```text
PR131 Decision Work Conversation Interpretation Tiny Offline Read v0
```

### PR131: Decision Work Conversation Interpretation Tiny Offline Read v0

Status: implemented in this slice.

Purpose:

Use exactly one bounded PR130 packet to test whether a tiny provisional offline
conversation interpretation read can safely fill a small PR128 field subset.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json`
- `tests/test_decision_work_conversation_interpretation_tiny_offline_read.py`

Current meaning:

- PR131 uses only `launch-public-enterprise-beta/20260627T104146Z_7bfe79`;
- it generates a fresh PR130 checked-in-safe packet locally, but does not check
  that source packet into the repo;
- it defines `lolla.decision_work_conversation_interpretation_tiny_offline_read.v0`;
- it fills only the selected tiny subset of PR128 fields:
  `decision_question`, `likely_starting_direction`,
  `revised_direction_or_action_consequence`, `live_options`,
  `abandoned_or_rejected_options`, `decision_thresholds`, `evidence_gates`,
  `useful_friction`, `noisy_friction`, `lost_value`, and
  `what_the_final_answer_does_not_prove`;
- it keeps every interpreted field source-bound, provisional, privacy-limited,
  and barred from quality-label use;
- it marks starting direction and abandoned options as partial, and lost value
  as insufficient context;
- it records `human_validated: false`, `product_proof: false`,
  `model_calls: 0`, `answer_quality_scored: false`, and
  `agent_action_authorized: false`;
- no runtime extractor, prompt change, live skill change, model-call code,
  archive mutation, product proof, human validation, answer-quality scoring,
  broad judge, automatic label, source-packet fixture, private-content check-in,
  or agent authorization has been added.

Recommended next slice:

```text
PR132 Decision Work Conversation Interpretation Second Tiny Offline Read v0
```

### PR132: Decision Work Conversation Interpretation Second Tiny Offline Read v0

Status: implemented in this slice.

Purpose:

Repeat the PR131 tiny offline interpretation read on a different decision
family, using exactly one generated PR130 checked-in-safe packet for
`deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json`
- `tests/test_decision_work_conversation_interpretation_second_tiny_offline_read.py`

Current meaning:

- PR132 uses only `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`;
- it generates a fresh PR130 checked-in-safe packet locally, but does not check
  that source packet into the repo;
- it defines
  `lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0`;
- it fills only the same tiny PR128 subset used in PR131;
- it keeps every interpreted field source-bound, provisional, privacy-limited,
  and barred from quality-label use;
- it finds the same tiny field set works in a healthcare
  operations/deployment decision, with action consequence, thresholds, evidence
  gates, useful/noisy friction, and non-proof boundaries useful;
- it keeps starting direction, abandoned options, and lost value partial or
  insufficient-context;
- it records `human_validated: false`, `product_proof: false`,
  `model_calls: 0`, `answer_quality_scored: false`, and
  `agent_action_authorized: false`;
- no runtime extractor, prompt change, live skill change, model-call code,
  archive mutation, product proof, human validation, answer-quality scoring,
  broad judge, automatic label, source-packet fixture, private-content check-in,
  or agent authorization has been added.

Decision gate:

```text
define_interpretation_read_schema
```

### PR133: Decision Work Conversation Interpretation Read Schema v0

Status: implemented in this slice.

Purpose:

Formalize the shared schema for future offline conversation interpretation
reads after PR131 and PR132 both used the same small field shape successfully.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md`
- `docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json`
- `tests/test_decision_work_conversation_interpretation_read_schema.py`

Current meaning:

- PR133 defines
  `lolla.decision_work_conversation_interpretation_read.v0`;
- every interpreted field must carry source refs, source status, uncertainty,
  interpretation basis, privacy limits, human-review requirement, brief/agent
  inspection handoff flags, and `must_not_be_used_as_quality_label: true`;
- custody flags remain conservative: no human validation, product proof, model
  calls, runtime invocation, skill invocation, archive mutation,
  answer-quality scoring, or agent action authorization;
- the schema is a contract only: it does not implement an interpreter, runtime
  extractor, prompt change, model-call code, broad batch, brief enrichment,
  product proof, or agent authorization.

Recommended next slice:

```text
PR134 Decision Work Conversation Interpretation Read Comparison v0
```

### PR134: Decision Work Conversation Interpretation Read Comparison v0

Status: implemented in this slice.

Purpose:

Compare the PR131 and PR132 tiny offline interpretation reads through the PR133
schema shape and decide whether the next move should be another read, a brief
enrichment test, a packet-builder patch, human review, or simplification.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json`
- `tests/test_decision_work_conversation_interpretation_read_comparison.py`

Current meaning:

- PR134 compares exactly two reads:
  `launch-public-enterprise-beta` and `deploy-assisted-intake-routing`;
- it creates no third read and does not modify either existing read;
- it finds stable useful fields for decision question, action consequence,
  decision thresholds, evidence gates, useful friction, and non-proof
  boundaries;
- it keeps likely starting direction, abandoned or rejected options, and lost
  value source-limited;
- it identifies one safe next test: a compact plain-language enrichment of one
  existing Decision Work Brief;
- it records `human_validated: false`, `product_proof: false`,
  `model_calls: 0`, `answer_quality_scored: false`, and
  `agent_action_authorized: false`;
- no brief enrichment, runtime extractor, prompt change, live skill change,
  model-call code, archive mutation, product proof, human validation,
  answer-quality scoring, broad judge, automatic label, private-content
  check-in, or agent authorization has been added.

Decision gate:

```text
proceed_to_brief_enrichment_test
```

Recommended next slice:

```text
PR135 Decision Work Brief Interpretation Enrichment Test v0
```

### PR135: Decision Work Brief Interpretation Enrichment Test v0

Status: implemented in this slice.

Purpose:

Use exactly one existing interpretation read to create one separate enriched
Decision Work Brief and test whether interpretation can improve the
user-facing decision story.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md`
- `docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md`
- `reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json`
- `tests/test_decision_work_brief_interpretation_enrichment_test.py`

Current meaning:

- PR135 enriches only `launch-public-enterprise-beta`;
- it uses the PR131 tiny offline interpretation read;
- it leaves the original rendered brief untouched;
- it uses only the PR134 feed-now fields: decision question, likely starting
  direction with uncertainty, action consequence, thresholds, evidence gates,
  useful friction as descriptive language, and non-proof boundaries;
- it keeps live options, abandoned/rejected options, noisy friction, lost value,
  values, stakeholder obligations, and assistant influence out of the main
  user-facing body;
- it adds no runtime behavior, new interpretation read, model call, product
  proof, human validation, answer-quality scoring, or agent authorization.

Decision gate:

```text
proceed_to_original_vs_enriched_review
```

### PR136: Original vs Enriched Brief Review v0

Status: implemented in this slice.

Purpose:

Compare the original launch-beta brief with the PR135 enriched version before
testing enrichment on another case.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-original-vs-enriched-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-original-vs-enriched-review-v0/review.json`
- `tests/test_decision_work_brief_original_vs_enriched_review.py`

Current meaning:

- PR136 finds the enriched launch-beta brief appears clearer about what changed
  for action and what may already have been present;
- it preserves the warning that the comparison is provisional, non-human, and
  not product proof;
- it does not modify the original or enriched brief;
- it does not enrich a second case.

Decision gate:

```text
proceed_to_second_enriched_brief_test
```

### PR137: Second Enriched Brief Test v0

Status: implemented in this slice.

Purpose:

Repeat the enrichment test on a second decision family before deciding whether
the enrichment pattern is stable.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md`
- `docs/conversation-understanding/decision-work-brief-second-enrichment-test-v0.md`
- `reviews/codex-assisted/decision-work-brief-second-enrichment-test-v0/review.json`
- `tests/test_decision_work_brief_second_enrichment_test.py`

Current meaning:

- PR137 enriches only `deploy-assisted-intake-routing`;
- it uses the PR132 tiny offline interpretation read;
- it keeps the same conservative field subset and exclusions as PR135;
- it creates no new interpretation read and does not enrich the cofounder case;
- it preserves source-depth uncertainty and non-claims.

Decision gate:

```text
proceed_to_enriched_brief_pattern_review
```

### PR138: Enriched Brief Pattern Review v0

Status: implemented in this slice.

Purpose:

Compare the two enriched briefs and decide whether the next move is a rules
contract, a rule patch, evidence-only handling, human review, or simplification.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-enriched-pattern-review-v0/review.json`
- `tests/test_decision_work_brief_enriched_pattern_review.py`

Current meaning:

- PR138 compares the enriched launch-beta and intake-routing briefs;
- it finds enrichment appears useful in both cases for clarifying action
  consequence;
- it identifies stable future-rule fields: decision question, likely starting
  direction with uncertainty, action consequence, thresholds, evidence gates,
  useful friction as descriptive language, and non-proof boundaries;
- it keeps live options, abandoned/rejected options, noisy friction, lost value,
  values, stakeholder obligations, and assistant influence evidence-only or
  unresolved;
- it explicitly does not implement PR139;
- it adds no runtime behavior, new interpretation read, model call, product
  proof, human validation, answer-quality scoring, or agent authorization.

Decision gate:

```text
proceed_to_enrichment_rules_contract
```

Recommended next slice:

```text
PR139 Decision Work Brief Enrichment Rules Contract v0
```

PR139 is not implemented in this slice.

### PR139: Decision Work Brief Enrichment Rules Contract v0

Status: implemented after PR138.

Purpose:

Define conservative rules for turning interpretation reads into user-facing
brief enrichment before any deterministic builder exists.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.md`
- `docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json`
- `tests/test_decision_work_brief_enrichment_rules_contract.py`

Current meaning:

- only a small stable field set may enter the user-facing brief;
- `live_options`, `abandoned_or_rejected_options`, `noisy_friction`,
  `lost_value`, values, stakeholder obligations, and assistant influence stay
  evidence-only or unresolved;
- score, approval, certification, product-proof, human-validation, and
  agent-authorization concepts are forbidden for enrichment;
- any builder must preserve source refs, uncertainty, privacy limits,
  non-claims, and the original brief.

Decision gate:

```text
proceed_to_offline_enriched_builder
```

### PR140: Offline Enriched Brief Builder v0

Status: implemented after PR139.

Purpose:

Create a deterministic offline builder that applies an existing interpretation
read to an existing rendered brief under the PR139 rules contract.

Implemented in this PR:

- `engine/system_b/decision_work_brief_enrichment.py`
- `scripts/evals/enrich_decision_work_brief.py`
- `tests/test_decision_work_brief_enrichment.py`
- `docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md`
- `docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md`
- `docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md`

Current meaning:

- the builder inserts a single `What the interpretation adds` section;
- it preserves `What this does not prove` and `Evidence and limits`;
- it keeps evidence-only fields out of the main enrichment section;
- it rejects same input/output paths, unsupported schemas, non-conservative
  custody flags, and rules that allow forbidden fields;
- it leaves original and hand-built enriched briefs untouched.

### PR141: Enriched Brief Builder Output Review v0

Status: implemented after PR140.

Purpose:

Compare the builder-generated enriched outputs against the prior hand-built
enriched examples.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-enriched-builder-output-review-v0/review.json`
- `tests/test_decision_work_brief_enriched_builder_output_review.py`

Current meaning:

- the builder preserved the useful enrichment signal in both launch-beta and
  intake-routing;
- it preserved uncertainty, source limits, and non-claims;
- it avoided evidence-only fields in the main enrichment body;
- it was more repetitive and template-shaped than the hand-built examples;
- rule compliance is useful but not yet product readiness.

Decision gate:

```text
proceed_to_builder_rule_patch
```

Recommended next slice:

```text
PR142 Decision Work Brief Enrichment Builder Rule Patch v0
```

### PR142: Decision Work Brief Enrichment Builder Rule Patch v0

Status: implemented after PR141.

Purpose:

Patch the deterministic offline enriched-brief builder so the generated
`What the interpretation adds` section is less repetitive and less
template-shaped while preserving the PR139 enrichment rules and all non-claims.

Implemented in this PR:

- `engine/system_b/decision_work_brief_enrichment.py`
- `docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md`
- `tests/test_decision_work_brief_enrichment_builder_rule_patch.py`
- regenerated builder examples:
  - `docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md`
  - `docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md`

Current meaning:

- the builder now groups the enrichment around the decision frame, uncertain
  starting point, clearer action consequence, visible thresholds, evidence
  gates, and non-claim;
- repeated stock phrases were reduced;
- evidence-only fields still stay out of the main body;
- uncertainty, source limits, and the non-proof boundary remain visible.

### PR143: Decision Work Brief Builder Patch Review v0

Status: implemented after PR142.

Purpose:

Review whether the patched builder output resolved the PR141 blocker well
enough to move to a system-level closure gate.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json`
- `tests/test_decision_work_brief_enrichment_builder_rule_patch_review.py`

Decision gate:

```text
proceed_to_offline_system_closure_gate
```

Current meaning:

- patched builder output is still visibly deterministic, but less robotic than
  the PR141-reviewed output;
- the action consequence is easier to understand in both builder-generated
  examples;
- uncertainty and non-claims remain visible;
- runtime integration remains not recommended.

### PR144: Decision Work Brief Offline System Closure Gate v0

Status: implemented after PR143.

Purpose:

Decide whether the offline Decision Work Brief system from PR114 through PR143
is coherent enough to package, or whether it needs more cases, local-private
checks, human review, or simplification first.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-offline-system-closure-gate-v0.md`
- `reviews/codex-assisted/decision-work-brief-offline-system-closure-gate-v0/review.json`
- `tests/test_decision_work_brief_offline_system_closure_gate.py`

Decision gate:

```text
package_pr114_pr144
```

Current meaning:

- the offline chain is coherent enough to package for review;
- packaging does not mean product readiness, human validation, runtime
  attachment, or proof that Lolla improved decisions;
- the strongest unresolved risk remains source depth and non-human
  interpretation.

### PR145: Decision Work Brief Offline Evidence Package Gate v0

Status: implemented after PR144.

Purpose:

Create a bounded package manifest and package gate for the offline Decision
Work Brief / Decision Work Conversation Interpretation surface from PR114
through PR144.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-pr114-pr144-packaging-gate-v0.md`
- `docs/conversation-understanding/decision-work-brief-pr114-pr144-package-manifest-v0.json`
- `tests/test_decision_work_brief_pr114_pr144_package_gate.py`

Current meaning:

- the package names the relevant docs, schemas, review artifacts, rendered and
  enriched examples, code modules, CLI scripts, and tests;
- it records the strongest useful signal, strongest unresolved risk, boundary
  summary, validation checklist, explicit staging list, do-not-stage warnings,
  suggested commit message, and suggested PR description;
- it excludes unrelated notes, plans, synthetic reviews, `SKILL.md`,
  `scripts/skill/*`, archive paths, raw/private text, provider text, and
  runtime temp state.

Recommended stop point:

```text
Stop after PR145 and decide whether to stage/package PR114-PR145 explicitly.
```

### PR146: Decision Work Brief Additional Local-Private Adequacy Checks v0

Status: implemented after the PR114-PR145 package was pushed.

Purpose:

Revisit the strongest unresolved package risk: checked-in-safe context is
compressed, while local-private nuance may change the starting-direction,
lost-value, stakeholder, relationship, legal, compliance, or user-intent read.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-additional-local-private-adequacy-checks-v0.md`
- `reviews/codex-assisted/decision-work-brief-additional-local-private-adequacy-checks-v0/review.json`
- `tests/test_decision_work_brief_additional_local_private_adequacy_checks.py`

Cases checked:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`
- `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`

Current meaning:

- both preferred cases were available for read-only local-private inspection;
- the checked-in-safe briefs remained adequate with private nuance;
- local-private context did not overturn the core action-consequence read;
- private nuance still changes confidence, severity, and human follow-up
  questions;
- the next narrow offline slice is a third builder case, not runtime
  integration.

Decision gate:

```text
proceed_to_third_builder_case
```

Recommended next slice:

```text
PR147 Decision Work Brief Third Builder Case v0
```

### PR147: Decision Work Brief Third Builder Case v0

Status: implemented after PR146.

Purpose:

Try to run the deterministic enriched-brief builder on the third decision
family, the CEO/cofounder governance case, without inventing a new
interpretation source or forcing the builder to consume the wrong schema.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-third-builder-case-v0.md`
- `reviews/codex-assisted/decision-work-brief-third-builder-case-v0/review.json`
- `tests/test_decision_work_brief_third_builder_case.py`

Current meaning:

- the cofounder rendered brief exists;
- the PR139 enrichment rules contract exists;
- PR146 found the cofounder checked-in-safe brief adequate with private nuance;
- no builder-compatible cofounder interpretation read exists;
- the deterministic builder was not run;
- no cofounder builder-enriched Markdown was created;
- the next safe step is to create the missing PR133-shaped interpretation read.

Decision gate:

```text
create_third_interpretation_read_first
```

Recommended next slice:

```text
PR147A Decision Work Conversation Interpretation Third Tiny Offline Read v0
```

### PR147A: Decision Work Conversation Interpretation Third Tiny Offline Read v0

Status: implemented after PR147.

Purpose:

Create the missing builder-compatible interpretation read for the
CEO/cofounder governance case, using the formal PR133 schema rather than a
third custom tiny-read schema.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-conversation-interpretation-third-tiny-offline-read-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json`
- `tests/test_decision_work_conversation_interpretation_third_tiny_offline_read.py`

Current meaning:

- the cofounder case now has a builder-compatible interpretation read;
- the read uses the same tiny field subset as PR131 and PR132;
- the action consequence is provisionally readable: align with the COO, move
  product execution authority first, narrow transition support, and define
  stop-loss triggers before the conversation;
- starting direction, abandoned/rejected options, option status, and lost value
  remain source-limited;
- the read is Codex-assisted, provisional, non-human-validated, not product
  proof, not answer-quality scoring, and not agent authorization;
- no cofounder builder output is created in PR147A.

Decision gate:

```text
test_brief_enrichment_from_interpretation
```

Recommended next slice:

```text
PR148 Decision Work Brief Third Builder Case Output v0
```

### PR148: Decision Work Brief Third Builder Case Output v0

Status: implemented after PR147A.

Purpose:

Run the deterministic offline enriched-brief builder on the CEO/cofounder case
now that PR147A provides a builder-compatible interpretation read.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md`
- `docs/conversation-understanding/decision-work-brief-third-builder-case-output-v0.md`
- `reviews/codex-assisted/decision-work-brief-third-builder-case-output-v0/review.json`
- `tests/test_decision_work_brief_third_builder_case_output.py`

Current meaning:

- the cofounder case now has a deterministic builder-generated enriched brief;
- the output preserves exactly one `What the interpretation adds` section,
  `What this does not prove`, and `Evidence and limits`;
- the action consequence is readable: align with the COO, move product
  execution authority first, narrow transition support, and define stop-loss
  triggers before the conversation;
- the output stays source-limited and does not claim product proof, human
  validation, answer-quality scoring, or agent authorization;
- the first enrichment paragraph still shows a mild deterministic-template
  weakness, so the next review should compare all three builder outputs before
  any further builder patch or human-review intake.

Decision gate:

```text
proceed_to_three_builder_case_pattern_review
```

Recommended next slice:

```text
PR149 Decision Work Brief Three Builder Case Pattern Review v0
```

### PR149: Decision Work Brief Three Builder Case Pattern Review v0

Status: implemented after PR148.

Purpose:

Compare the three builder-generated enriched briefs and decide whether the
offline builder evidence now points to another builder case, a rules patch,
more source-depth work, packaging, human review, or simplification.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-three-builder-case-pattern-review-v0.md`
- `reviews/codex-assisted/decision-work-brief-three-builder-case-pattern-review-v0/review.json`
- `tests/test_decision_work_brief_three_builder_case_pattern_review.py`

Current meaning:

- the builder-generated launch-beta, intake-routing, and cofounder enriched
  briefs all preserve the action-consequence signal;
- uncertainty, source limits, non-claims, and Evidence and limits remain
  visible across all three;
- PR139 evidence-only fields remain out of the main enrichment body;
- the builder is still visibly deterministic, and the cofounder output remains
  the highest overclaim risk because authority-transfer language can sound
  operationally decisive;
- the next useful step is human-review intake planning, not another
  deterministic builder case or runtime attachment.

Decision gate:

```text
proceed_to_human_review_intake_plan
```

Recommended next slice:

```text
PR150 Decision Work Brief Human Review Intake Plan v0
```

### PR150: Decision Work Brief Human Review Intake Plan v0

Status: implemented after PR149.

Purpose:

Create the intake plan that tells future human reviewers what to inspect before
the Decision Work Brief and enriched-brief surface can be treated as useful,
safe, user-facing, or runtime-adjacent.

Implemented in this PR:

- `docs/conversation-understanding/decision-work-brief-human-review-intake-plan-v0.md`
- `reviews/codex-assisted/decision-work-brief-human-review-intake-plan-v0/review.json`
- `tests/test_decision_work_brief_human_review_intake_plan.py`

Current meaning:

- PR150 targets exactly the three builder-generated enriched briefs for
  launch-beta, intake-routing, and cofounder/governance;
- it defines reviewer questions for usefulness, action consequence,
  uncertainty, source depth, private context, overtrust, and runtime blockers;
- it includes case review forms, cross-case review questions, stop conditions,
  and allowed human-review outcomes;
- it does not complete human review, claim human validation, claim product
  proof, score answer quality, authorize agent action, or attach the surface to
  runtime.

Decision gate:

```text
run_human_review_pilot
```

Recommended next slice:

```text
PR151 Decision Work Brief Human Review Pilot v0
```

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
