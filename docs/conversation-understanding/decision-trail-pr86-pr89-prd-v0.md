# Decision Trail PR86-PR89 PRD v0

Status: PRD / implementation sequence

Date: 2026-06-29

Scope: PR86 through PR89 only. This PRD translates the Decision Trail readiness audit into a staged implementation plan that keeps Lolla aligned with its core architecture:

> probabilistic interpretation inside deterministic custody

The goal is not to build a parallel product. The goal is to turn existing Lolla run artifacts into a coherent Decision Trail surface: a readable and machine-inspectable process report that can eventually travel with a revised answer.

## Executive Summary

Lolla currently captures conversations, extracts a compact decision shape, applies audit pressure, produces revised answers, archives artifacts, and supports offline Product Delta evaluation. That is real.

The missing product surface is a first-class Decision Trail report:

- what conversation produced the answer;
- what Lolla understood;
- what the audit challenged;
- what changed;
- what remains uncertain;
- what artifacts support the report;
- what must not be overclaimed.

PR86-PR89 should build this carefully:

1. PR86 defines the report contract.
2. PR87 builds a read-only exporter over existing artifacts.
3. PR88 reviews exported fixtures for field population, readability, and overtrust risk.
4. PR89 decides whether the next bottleneck is conversation interpretation, report simplification, local-private enrichment, or no further work yet.

The sequence must not add runtime behavior, default specialist calls, graph/memory infrastructure, automatic labels, or a broad LLM judge.

## Product Claim

The target claim is:

> Given a serious AI conversation and a Lolla revised answer, Lolla can preserve a useful decision trail: the answer, the pressure applied, what changed, what remains missing, and the non-claims needed for responsible review.

The target claim is not:

- Lolla proves the answer is good;
- Lolla scores decision quality;
- Lolla replaces human judgment;
- Lolla certifies agent action;
- Lolla fully understands every messy conversation;
- clean artifacts prove good advice.

## Grounded Current-State Findings

This PRD is based on code and merged/tracked docs, not just research notes.

### Live Runtime Flow

The skill runtime is a conductor. It captures the current conversation, runs extraction and audit pipeline helpers, produces a revised answer, renders a memo, and archives run artifacts.

The PR86-PR89 work must not alter this runtime flow.

### Current Extraction Code

`scripts/run_extract.py` performs the live semantic extraction. It asks an LLM to produce:

- `decision_situation`;
- `live_constraints`;
- `synthesized_position`;
- `reasoning_passages`;
- `original_framing`;
- `dropped_threads`.

It also performs deterministic quote validation for `reasoning_passages`, validates capture shape, handles long-conversation truncation, and builds compatibility fields for older tooling.

Important implication:

The current live extraction is intentionally compact. It is not a full decision-trail interpretation.

### Current Runtime Entry Shape

`engine/system_b/conversation_context.py` defines the live pipeline entry shape:

- `Turn`;
- `LiveConstraint`;
- `DroppedThread`;
- `ExtractionPayload`;
- `ConversationContext`.

This is enough for the current audit pipeline, but it does not first-class:

- live options;
- option status;
- stakeholders;
- user values/priorities;
- assistant influence;
- evidence ledger;
- useful versus noisy friction;
- lost value.

### Existing Conversation IR

`engine/system_b/ir.py` and `engine/system_b/ir_constructor.py` already provide a provenance-aware `ConversationIR` with:

- turns;
- turn refs;
- span refs;
- span provenance;
- derivation provenance;
- frame anchors;
- user issue events;
- stance events.

The constructor supports optional specialist extractors for stance, live constraints, and dropped threads.

Default construction remains deterministic and conservative. The optional LLM-backed specialists are not default runtime behavior.

Important implication:

PR86-PR89 should reuse these ideas. It should not invent a second hidden conversation system unless missingness proves the existing one cannot carry the product surface.

### Existing Read-Only Exporter Pattern

`engine/system_b/audit_decision_record.py` is the pattern to copy for PR87:

- read structured artifacts;
- avoid raw transcript/memo/revised-answer content by default;
- record source artifact status;
- record missing or malformed artifacts;
- validate output paths outside the run directory;
- preserve field statuses and non-claims;
- do not call models;
- do not mutate archives;
- do not create labels or scores.

### Existing Product Delta Pattern

The PR71-PR85 Product Delta package gives useful internal scaffolding:

- PR72 review protocol;
- PR78 deterministic boundary lint;
- PR80 specialist review contracts;
- PR81 specialist packet builder;
- PR82 trap fixtures;
- PR83 specialist batch;
- PR84 fan-in/disagreement report;
- PR85 package gate.

Important implication:

The Decision Trail should not replace Product Delta. Product Delta studies whether revised answers create decision-useful deltas. Decision Trail packages the process evidence around a single run.

## What Has Already Been Done

### Runtime And Artifacts

Already built:

- conversation capture;
- compact extraction;
- audit lanes;
- revised answer generation;
- memo rendering;
- archive finalization;
- `agent_result.json`;
- `evaluation.json`;
- `reasoning_trace.json`;
- capture adequacy;
- doctor/preflight;
- audit decision record exporter.

### Conversation-Understanding Research

Already researched:

- semantic extraction review pilot;
- semantic coverage report;
- semantic coverage corpus survey;
- specialist extractor probe runner;
- real specialist extractor probe;
- broader specialist evidence gate;
- specialist runtime design without integration;
- user values/priorities signal design.

Key research outcome:

Specialist LLM extractors improved span-grounding for live constraints, dropped threads, and assistant stance in offline probes. Runtime integration remains blocked because evidence is not yet clean enough and user-values extraction remains unsolved.

### Product Delta Evidence

Already packaged:

- PR71-PR85 non-human Product Delta evidence phase.

Key useful signal:

The specialist review downgraded `accept-operations-role-startup` from `material_improvement_candidate` to `partial_improvement_candidate`, preserving lost-value and interpretation uncertainty instead of laundering a broad positive read.

Key unresolved risk:

The evidence remains thin, prior-positive, compressed, and human-unvalidated.

## What Is Not Done

Not done yet:

- first-class Decision Trail report;
- Decision Trail schema;
- Decision Trail read-only exporter;
- Decision Trail field-missingness review;
- local-private Decision Trail mode;
- specialist enrichment for Decision Trail;
- runtime integration of Decision Trail;
- automatic report attachment to the revised answer;
- agent-facing Decision Trail handoff contract;
- human validation of Decision Trail usefulness.

Also not done:

- default specialist extraction during `$lolla`;
- `conversation_understanding_ir.v0` archive artifact;
- automatic user-values extraction;
- graph database;
- memory layer;
- embeddings/chunking;
- answer-quality judge.

## Non-Negotiable Architecture Doctrine

Messy interpretation belongs to LLMs, not deterministic code.

Deterministic code may:

- read files;
- validate schemas;
- preserve source refs;
- record artifact health;
- record missingness;
- record field status;
- hash artifacts;
- enforce privacy boundaries;
- enforce non-claims;
- route fields;
- render reports;
- compare declared status against allowed vocabularies.

Deterministic code must not:

- infer user values from prose;
- decide whether advice improved;
- decide whether a gate is useful;
- infer unstated live options;
- infer stakeholder obligations from vague text;
- decide whether friction is useful or noisy;
- decide whether the user would have acted differently;
- convert clean artifacts into quality claims.

If a field requires semantic interpretation of messy conversation, it must be:

- supplied by an existing LLM-produced artifact;
- supplied by a future bounded LLM specialist;
- explicitly marked `not_supplied`, `not_measured`, `unclear`, `requires_llm_interpretation`, `available_but_redacted_in_safe_mode`, or `available_in_private_artifact_not_exported`;
- or left empty with a non-claim explanation.

Trying to solve messy conversation with deterministic rules is a lost game. The deterministic layer exists to keep probabilistic interpretation in custody, not to replace it.

## System Boundary

PR86-PR89 are offline/reporting work.

The architectural split is:

```text
Lolla runtime:
  captures conversation
  runs audit pressure
  produces revised answer
  archives artifacts

Decision Trail lane:
  reads completed artifacts
  exports a report
  records missingness, redaction, source status, and non-claims
  supports review
```

The runtime produces the object of study. The Decision Trail lane studies completed artifacts later. PR86-PR89 must not become a shadow runtime or feed provisional outputs back into the live skill automatically.

They must not:

- run `$lolla`;
- invoke the Lolla skill;
- change `SKILL.md`;
- change `scripts/skill/*`;
- change runtime prompts;
- change live audit behavior;
- call providers in normal validation;
- mutate archive folders;
- launch Observatory;
- create runtime temp state;
- add graph or memory infrastructure;
- add an LLM judge;
- add answer-quality scoring;
- add automatic labels;
- authorize agent action.

## Product Surfaces And How They Relate

| Surface | Purpose | Current state | PR86-PR89 relationship |
| --- | --- | --- | --- |
| Runtime revised answer | The answer Lolla gives after audit pressure | Built | Source input to future Decision Trail. |
| Memo | Human-readable summary of current run | Built | May be referenced, but raw memo content should not be copied into checked-in examples. |
| `agent_result.json` | Compact agent handoff and run readiness | Built | Decision Trail should reuse run health/caller-action signals but not turn them into approval. |
| `evaluation.json` | Deterministic run envelope evaluation | Built | Decision Trail should reuse artifact/schema/custody health. |
| `reasoning_trace.json` | Local custody index of run artifacts | Built | Decision Trail should reuse source refs and artifact pointers. |
| Audit decision record | Accountability shell | Built as read-only exporter | Decision Trail should borrow field-status and non-claim patterns, not duplicate the ADR. |
| Product Delta eval | Offline evidence about vanilla-vs-Lolla delta | Built internally | Decision Trail should not claim Product Delta proof; it may later point to Product Delta reviews when present. |
| Decision Trail report | Customer-facing answer-plus-process report | Schema, read-only exporter, and safe fixture review built; interpretation-gap decision not done | Target of PR86-PR89. |

## PR86: Decision Trail Report PRD And Schema v0

Completion note: PR86 is implemented by
[`decision-trail-report-prd-v0.md`](decision-trail-report-prd-v0.md),
[`decision-trail-report-v0.json`](decision-trail-report-v0.json), and focused
schema/contract tests. It remains design/schema only: no exporter, runtime
integration, model calls, archive mutation, prompt changes, specialist calls,
review fixtures, labels, scoring, judge, agent action authorization, or product
proof.

### Type

Docs and JSON schema only.

### Purpose

Define `lolla.decision_trail_report.v0` as the first-class process report that can eventually travel with a revised answer.

PR86 should answer:

- What fields belong in the report?
- Which fields can be populated from existing artifacts?
- Which fields require LLM interpretation?
- Which fields are explicitly missing in v0?
- How does the report avoid becoming a product-proof or approval artifact?

### What Is Already Done Before PR86

Inputs available:

- Decision Trail readiness audit;
- customer-facing Decision Trail web-page draft;
- Product Delta PR71-PR85 package;
- audit decision record schema/exporter;
- current runtime artifact chain;
- conversation-understanding research/design;
- specialist extractor probe evidence.

### What Needs To Be Done

Create:

- `docs/conversation-understanding/decision-trail-report-prd-v0.md`;
- `docs/conversation-understanding/decision-trail-report-v0.json`.

The schema should define:

- report metadata;
- source artifacts;
- custody flags;
- trace context;
- report mode;
- conversation understanding summary;
- decision question;
- vanilla likely next action;
- revised likely next action;
- option map;
- constraints;
- stakeholders;
- values/priorities;
- assistant influence;
- audit pressure summary;
- structural delta;
- useful/noisy friction;
- lost value;
- unresolved questions;
- artifact health;
- field population policy;
- limitations;
- non-claims.

Trace context is optional and future-compatible only. PR86 should not adopt OpenTelemetry, OpenInference, OpenAI Agents tracing, or any external trace dependency. It should only leave a small mapping surface so Lolla can later interoperate with modern agent observability if that becomes useful.

Recommended trace fields:

- `trace_context.status`;
- `trace_context.source_refs`;
- `trace_context.external_trace_id`;
- `trace_context.otel_genai_semconv_status`;
- `source_artifacts[*].activity_kind`;
- `source_artifacts[*].generated_by`;
- `source_artifacts[*].used_by`.

Recommended `trace_context.status` values:

- `not_used`;
- `future_compatible`;
- `experimental_mapping`.

Recommended `otel_genai_semconv_status` values:

- `not_used`;
- `future_compatible`;
- `experimental_mapping`.

Every semantic section should support:

- `status`;
- `source_status`;
- `source_refs`;
- `items` or `value`;
- `empty_meaning`;
- `owner`;
- `requires_llm_interpretation`;
- `exporter_inferred_from_prose: false` when the deterministic exporter populates it.

Recommended status vocabulary:

- `not_supplied`;
- `not_measured`;
- `not_applicable`;
- `available_from_structured_artifact`;
- `available_from_review_artifact`;
- `available_but_redacted_in_safe_mode`;
- `available_in_private_artifact_not_exported`;
- `requires_llm_interpretation`;
- `unavailable_missing_artifact`;
- `unavailable_malformed_artifact`;
- `unclear`.

The two redaction/private-availability statuses are important. Checked-in safe mode must distinguish "the system does not have this" from "the system may have this locally, but it was not exported because the safe report cannot include raw/private material."

Recommended report modes:

- `checked_in_safe_mode`;
- `local_private_mode`;
- `future_runtime_mode_not_implemented`.

PR86 must also define the difference between:

- deterministic field population;
- LLM-supplied interpretation;
- human-supplied review;
- absent or unmeasured fields.

### How We Want It Done

Use the existing ADR and Product Delta patterns.

PR86 should not invent a giant ontology. It should define the minimum report needed to explain:

- what changed;
- what evidence exists;
- what is missing;
- what cannot be claimed.

The schema should be tolerant of missing fields. Missingness is a product feature because it tells the reviewer where the current artifact chain is thin.

Do not require the report to be beautiful before it is honest.

### What Needs To Be Checked

Required validation:

- `jq . docs/conversation-understanding/decision-trail-report-v0.json`;
- local Markdown link check over touched docs;
- `git diff --check`;
- trailing whitespace scan;
- privacy/content marker scan;
- PR78 boundary lint over the PR86 docs/schema if applicable;
- schema test that forbidden authority fields are absent.

The PR should also check:

- every semantic field has a status;
- every empty semantic field has `empty_meaning`;
- safe-mode redaction is distinguishable from missingness;
- optional trace fields are present only as no-dependency future-compatibility metadata;
- no field implies approval, score, certification, or agent action;
- field names do not conflict with Product Delta or ADR vocabulary;
- `checked_in_safe_mode` excludes raw transcript, memo, revised-answer, provider text, private content, and local absolute paths.

### Must Not Do

PR86 must not:

- implement an exporter;
- add runtime integration;
- call models;
- inspect archives;
- add specialist calls;
- create review fixtures;
- claim the report is already produced by `$lolla`;
- claim human validation;
- add a broad judge.

### Done Definition

PR86 is done when a fresh coder can read the PRD/schema and know exactly how to build a conservative read-only exporter without guessing report semantics.

## PR87: Decision Trail Read-Only Exporter v0

Completion note: PR87 is implemented by
[`decision_trail_report.py`](../../engine/system_b/decision_trail_report.py),
[`build_decision_trail_report.py`](../../scripts/evals/build_decision_trail_report.py),
[`test_decision_trail_report.py`](../../tests/test_decision_trail_report.py),
and [`decision-trail-readonly-exporter-v0.md`](decision-trail-readonly-exporter-v0.md).
It remains a deterministic offline exporter only: no runtime integration, model
calls, archive mutation, prompt changes, `SKILL.md` changes, `scripts/skill/*`
changes, labels, scoring, judge, agent action authorization, fixture review, or
product-proof claim.

### Type

Code, CLI, tests, and a small safe fixture.

### Purpose

Build a deterministic read-only exporter that produces `lolla.decision_trail_report.v0` from existing run artifacts.

The exporter should answer:

> What can we safely say about this run's decision trail from existing structured artifacts, without new model calls and without pretending to interpret what was not supplied?

### What Is Already Done Before PR87

Inputs available:

- PR86 schema;
- `audit_decision_record.py` exporter pattern;
- `product_delta_readiness.py` readiness pattern;
- `product_delta_boundary_lint.py` boundary pattern;
- current archive artifacts.

### What Needs To Be Done

Create likely files:

- `engine/system_b/decision_trail_report.py`;
- `scripts/evals/build_decision_trail_report.py`;
- `tests/test_decision_trail_report.py`;
- `docs/conversation-understanding/decision-trail-readonly-exporter-v0.md`;
- a tiny checked-in-safe example output if privacy-safe.

The exporter should read structured artifacts only in v0:

- `evaluation.json`;
- `agent_result.json`;
- `reasoning_trace.json`;
- `extraction_adequacy_report.json` if present;
- `extraction.json` carefully, avoiding raw/legacy fields that may contain assistant text;
- `result.json` carefully, using only structured summary fields that are already product artifacts.

Raw artifacts not read by default:

- `conversation.txt`;
- `memo.md`;
- `revised.txt`;
- live transcript;
- private ledgers;
- provider messages;
- operator logs.

The exporter should:

- validate output path is outside the run directory;
- record artifact presence, missingness, malformedness, byte counts, and hashes where safe;
- populate deterministic fields only from known structured fields;
- mark semantic fields as `requires_llm_interpretation`, `not_supplied`, or `not_measured` when existing artifacts do not safely provide them;
- record `model_calls: 0`;
- record `archive_mutated: false`;
- record `runtime_invoked: false`;
- record `skill_invoked: false`;
- record raw/private inclusion flags as false for checked-in safe mode.

### How We Want It Done

Copy the ADR exporter style:

- sanitized input errors;
- structured artifact record helper;
- JSON rendering helper;
- output-path guard;
- field-status helpers;
- no broad string scraping;
- no deterministic semantic inference from free prose.

Where a field is populated from an LLM-produced structured artifact, say so.

Example:

```text
decision_question.status = available_from_structured_artifact
decision_question.source_refs = extraction.json#/decision_situation
decision_question.exporter_inferred_from_prose = false
```

Where a field cannot be safely populated:

```text
option_map.status = requires_llm_interpretation
option_map.empty_meaning = absence is not evidence that no options existed
```

This makes the report honest even when sparse.

### What Needs To Be Checked

Required validation:

- `python3 -m py_compile engine/system_b/decision_trail_report.py scripts/evals/build_decision_trail_report.py tests/test_decision_trail_report.py`;
- focused pytest for the new tests and existing boundary/exporter tests;
- `jq .` over generated report;
- output path outside run dir test;
- missing artifact test;
- malformed artifact test;
- raw artifact non-reading test;
- no archive mutation test;
- no model-call flag test;
- privacy/content marker scan over checked-in examples;
- PR78 boundary lint over generated checked-in-safe report;
- `git diff --check`;
- Markdown link check.

The tests should prove:

- the exporter does not read raw artifacts in checked-in safe mode;
- empty semantic fields are explicit non-claims;
- deterministic exporter does not infer user values, options, useful friction, noisy friction, or lost value from prose;
- artifact health fields populate even when semantic fields remain missing;
- generated report has stable schema version.

### Must Not Do

PR87 must not:

- call providers;
- run `$lolla`;
- invoke the skill;
- mutate archive folders;
- add runtime generation;
- copy raw transcript/memo/revised-answer content into checked-in examples;
- infer PR31/Product Delta labels;
- claim product proof;
- add a UI/dashboard.

### Done Definition

PR87 is done when a report can be generated from an existing run directory as a conservative artifact-health and decision-trail shell, with missing semantic fields made legible rather than silently filled.

## PR88: Decision Trail Fixture Review v0

Completion note: PR88 is implemented by
[`decision-trail-export-fixture-review-v0.md`](decision-trail-export-fixture-review-v0.md),
[`review.json`](../../reviews/codex-assisted/decision-trail-fixture-review-v0/review.json),
and focused tests in
[`test_decision_trail_fixture_review.py`](../../tests/test_decision_trail_fixture_review.py).

PR88 used safe fixture evidence only. No local-private shadow review was run,
so PR89 must treat the evidence as safe-fixture-only.

### Type

Docs, safe fixtures, and review notes. Code changes only if PR87 has a blocking bug.

### Purpose

Test whether PR87 output is understandable and useful as a Decision Trail surface.

PR88 should answer:

- Which fields populate from existing artifacts?
- Which fields are missing or only status-marked?
- Which fields are available only privately or redacted in checked-in safe mode?
- Does the report help a reviewer understand how the answer moved?
- Does it create overtrust?
- Does it make interpretation gaps visible?
- Does it show where LLM interpretation would be needed next?
- Can a reviewer quickly answer what changed, what supports it, what is missing, what must not be claimed, and whether the report made them more careful or merely more impressed?

### What Is Already Done Before PR88

Inputs available:

- PR86 schema;
- PR87 exporter;
- existing safe cases;
- Product Delta PR71-PR85 package;
- Decision Trail readiness audit.

### What Needs To Be Done

Create likely files:

- `docs/conversation-understanding/decision-trail-export-fixture-review-v0.md`;
- `reviews/codex-assisted/decision-trail-fixture-review-v0/review.json`;
- optional checked-in-safe exported reports if they contain no raw/private content;
- `tests/test_decision_trail_fixture_review.py` if structured review JSON is added.

Review a small number of cases, preferably:

- one strong Product Delta candidate;
- one downgraded or partial candidate;
- one thin or inconclusive case;
- one case where artifact health is good but semantic fields are sparse.

PR88 should include one of two evidence modes:

- at least one local-private, non-checked-in shadow review over a real archive; or
- an explicit statement that no local-private review was run, and PR89 must treat the evidence as safe-fixture-only.

If only safe checked-in summaries are available, say so. Do not pretend these are complete archive reviews.

### How We Want It Done

PR88 should be a field-missingness and report-adequacy review, not a semantic correctness review.

It should classify each section as:

- `clear_and_populated`;
- `clear_but_missing`;
- `confusing`;
- `overclaim_risk`;
- `requires_llm_interpretation`;
- `requires_human_review`;
- `not_applicable`.

It should include a "what this report made easier to see" section and a "what this report failed to preserve" section.

It should also include a behavioral usefulness section that asks:

- What changed?
- What evidence supports the change?
- What is missing?
- What must not be claimed?
- Did the report make the reviewer more careful, or merely more impressed?

It should explicitly separate:

- report readability;
- artifact custody;
- semantic interpretation adequacy;
- Product Delta usefulness;
- human validation.

### What Needs To Be Checked

Required validation:

- `jq .` over review JSON and exported reports;
- PR78 boundary lint over review docs/JSON and exported reports;
- tests if schema fixture exists;
- source refs resolve where they point to checked-in files;
- local Markdown links resolve;
- privacy/content marker scan;
- `git diff --check`.

Review-specific checks:

- every positive statement about report usefulness includes a caveat about no human validation;
- no report fixture contains raw transcript, raw memo, raw revised answer, provider text, private content, or local absolute paths;
- every missing field has an empty meaning;
- redacted/private-available fields are not counted as missing;
- no report implies a good decision merely because artifacts are complete.

### Must Not Do

PR88 must not:

- change exporter behavior unless a blocker is found;
- call models/providers;
- use a broad judge;
- score report quality;
- treat Codex-assisted review as human validation;
- add runtime integration;
- expand the case set just to create better-looking evidence.

### Done Definition

PR88 is done when maintainers can see whether the Decision Trail report is useful, too sparse, too confusing, or too authoritative-looking before any new interpretation machinery is added.

## PR89: Conversation Interpretation Gap Decision v0

### Type

Docs-only decision gate.

### Purpose

Decide what the PR86-PR88 evidence says about the next bottleneck.

PR89 should answer:

> Is the current artifact chain enough for a useful Decision Trail v0, or do we need additional LLM-backed interpretation before this can become a real product surface?

### What Is Already Done Before PR89

Inputs available:

- PR86 schema;
- PR87 exporter;
- PR88 fixture review;
- semantic extraction review pilot;
- specialist extractor probe evidence;
- Product Delta PR71-PR85 package;
- current runtime code map.

### What Needs To Be Done

Create:

- `docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md`.

The decision gate should choose one of these outcomes:

#### Outcome A: Exporter v0 is enough for now

Use if PR88 shows that the report is readable and useful even with many status-marked missing fields.

Next work would be packaging, examples, and later human review.

#### Outcome B: Add narrow offline LLM specialist enrichment

Use if PR88 shows repeated missingness in fields that cannot be deterministically inferred:

- live options;
- option status;
- values/priorities;
- stakeholders;
- assistant influence;
- evidence used/missing;
- useful/noisy friction;
- lost value.

This would be a future offline/local-private or Codex-assisted specialist sequence, not runtime integration.

Outcome B should be the expected next move if PR88 repeatedly misses these messy semantic fields and the exporter otherwise works. Do not jump to a broad durable `conversation_understanding_ir.v0` just because the first report is sparse. First ask whether bounded offline LLM specialists can supply the missing interpretation under custody.

#### Outcome C: Design `conversation_understanding_ir.v0`

Use only if PR88 shows the report needs a durable intermediate conversation artifact rather than direct export from scattered existing artifacts.

This should reuse current `ConversationIR` primitives where possible.

#### Outcome D: Strengthen existing extraction

Use only if the gap is clearly in the current live extraction shape and can be improved without overloading the prompt or breaking runtime cost/latency.

This should be treated carefully because live extraction is already doing several cognitive tasks.

#### Outcome E: Stop and simplify

Use if the Decision Trail report is too sparse, too confusing, too overclaim-prone, or not obviously useful.

### How We Want It Done

Put contradicting evidence first.

The decision must say:

- what PR88 showed;
- which fields were most missing;
- which fields were available only privately or redacted in safe mode;
- which fields were most useful;
- whether missing fields require LLM interpretation or better deterministic custody;
- what would falsify the chosen path;
- what work is explicitly deferred.

If the chosen path is LLM specialist enrichment, PR89 must define the first specialist family narrowly and explain why deterministic rules are insufficient.

If the chosen path is `conversation_understanding_ir.v0`, PR89 must explain why existing `ConversationIR`, ADR, and Product Delta contracts are not enough.

### What Needs To Be Checked

Required validation:

- local Markdown link check;
- PR78 boundary lint over the PR89 decision doc;
- `git diff --check`;
- trailing whitespace scan;
- privacy/content marker scan.

Decision-quality checks:

- clear selected outcome;
- rejected alternatives recorded;
- no runtime integration approval unless explicitly supported by evidence;
- no hidden judge;
- no product-proof language;
- no deterministic semantic inference proposal for messy conversation fields;
- explicit next PR recommendation.

### Must Not Do

PR89 must not:

- implement anything;
- add schema/code/tests beyond docs validation;
- start specialist calls;
- approve runtime integration;
- treat missingness as failure by itself;
- treat clean reports as product success.

### Done Definition

PR89 is done when the next phase is unambiguous and evidence-bounded: either continue with a narrow, justified interpretation path or stop/simplify before adding machinery.

## Cross-PR Validation Matrix

| Check | PR86 | PR87 | PR88 | PR89 |
| --- | --- | --- | --- | --- |
| `git diff --check` | Required | Required | Required | Required |
| Markdown links | Required | Required | Required | Required |
| JSON parse | Schema only | Report fixtures | Review/report fixtures | If JSON added |
| Unit tests | Optional schema tests | Required | Required if JSON fixture | Not required |
| PR78 boundary lint | Required | Required | Required | Required |
| Privacy/content scan | Required | Required | Required | Required |
| Raw artifact non-reading | N/A | Required | Verify outputs | N/A |
| Archive mutation check | N/A | Required | Required if exporter run | N/A |
| Source-ref resolution | Schema examples | Required | Required | Required for cited files |
| No model calls | Required | Required | Required | Required |
| No runtime changes | Required | Required | Required | Required |
| Redaction vs missingness | Required | Required | Required | Required |
| Optional trace compatibility stays dependency-free | Required | Required | Review only | Review only |
| Local-private shadow review or safe-fixture-only caveat | N/A | N/A | Required | Required |

## Field Ownership Policy

Decision Trail fields should declare owner/source explicitly.

Recommended owner values:

- `deterministic_exporter`;
- `existing_llm_runtime_artifact`;
- `product_delta_review_artifact`;
- `future_llm_specialist`;
- `future_human_review`;
- `not_supplied`.

Examples:

| Field | v0 likely owner | Notes |
| --- | --- | --- |
| Artifact health | `deterministic_exporter` | Safe and deterministic. |
| Capture adequacy | `deterministic_exporter` | Read from existing structured artifacts. |
| Decision question | `existing_llm_runtime_artifact` | From extraction; exporter only copies/statuses. |
| Live constraints | `existing_llm_runtime_artifact` | From extraction; better span grounding may need specialists later. |
| Live options | `future_llm_specialist` | Do not deterministically infer. |
| Values/priorities | `future_llm_specialist` or `future_human_review` | High over-inference risk. |
| Assistant influence | `future_llm_specialist` | Existing stance specialist research is relevant. |
| Useful/noisy friction | `product_delta_review_artifact` or `future_llm_specialist` | Not deterministic. |
| Lost value | `product_delta_review_artifact` or `future_llm_specialist` | Must remain provisional. |
| Non-claims | `deterministic_exporter` | Strong deterministic fit. |

## Falsification Tests

This PRD should be considered wrong if:

- PR87 cannot populate even artifact health and basic decision/custody fields from existing artifacts;
- PR88 shows readers cannot understand the report without reading many other docs;
- the report makes people more confident without giving them better inspection power;
- fields marked as missing are treated as negative semantic findings;
- deterministic code starts filling qualitative interpretation fields from prose heuristics;
- Product Delta and Decision Trail become two duplicate report families;
- privacy-safe examples require copying raw conversation or revised-answer text;
- the next phase cannot explain what it is not claiming.

## Main Pre-Mortem

The failure mode is not that the report is too conservative.

The failure mode is that the report looks complete.

If the first Decision Trail report is polished, users may assume the decision has been audited deeply even when key interpretation fields are missing. This is why field status, empty meaning, source refs, and non-claims are not cosmetic. They are the product boundary.

## Recommended Commit Shape

Do not combine all four PRs.

Keep the sequence staged:

1. PR86: schema and design only.
2. PR87: exporter and tests only.
3. PR88: fixture review only.
4. PR89: decision gate only.

This prevents implementation momentum from hiding the evidence that should decide the next move.

## Final Recommendation

PR88 is complete. Proceed with PR89 next.

PR88 found that the PR87 sparse shell is useful as a custody and missingness
surface, but too thin for the full Decision Trail product without later bounded
interpretation. The right next move is PR89: decide whether to pursue narrow
offline LLM specialist enrichment, local-private review, simplification, or a
pause.

The most important design constraint is:

> Deterministic code carries the report. LLM interpretation supplies messy meaning. Field status tells the reader which is which.

That is the line that keeps Lolla from becoming either a brittle deterministic judge or an unbounded LLM opinion machine.
