# Semantica-Inspired Accountability PRD v0

Status: PR55 docs-only source artifact / implementation queue plan
Date: 2026-06-28

This note turns the Semantica architecture review into an actionable Lolla
roadmap. It is intentionally selective. The goal is not to copy Semantica or
turn Lolla into a knowledge-graph platform. The goal is to borrow the smallest
accountability primitives that make Lolla's existing reasoning-audit harness
more inspectable, reviewable, and hard to overclaim.

This is the PR55 source artifact. PR55 lands this plan and light handoff links
only. It does not implement any primitive described below, and it does not
approve PR56 through PR65 as code work.

PR66 has now landed as a separate approved implementation slice for only the
audit decision record exporter, and PR67 has now reviewed exporter smoke output
without integrating it into runtime. That does not broaden the PR55 plan into
archive integration, automatic generation, graph/memory/platform work, scoring,
or judge behavior.

This note is not a runtime approval. It does not approve graph databases,
embeddings, memory, automatic value extraction, policy enforcement, high-stakes
use, LLM judges, answer-quality scoring, or broad platform work.

## Source Inspiration

Semantica presents itself as a context and accountability layer for AI systems.
Its repo emphasizes:

- context graphs;
- first-class decision records;
- W3C PROV-O-style provenance;
- conflict detection;
- policy/rule checks;
- reasoning engines;
- pipeline orchestration;
- preflight diagnostics such as `semantica doctor`.

Useful source links:

- Semantica README:
  <https://github.com/semantica-agi/semantica/blob/main/README.md>
- Semantica architecture:
  <https://github.com/semantica-agi/semantica/blob/main/ARCHITECTURE.md>
- Semantica context module:
  <https://github.com/semantica-agi/semantica/tree/main/semantica/context>
- Semantica provenance module:
  <https://github.com/semantica-agi/semantica/tree/main/semantica/provenance>
- Semantica conflicts module:
  <https://github.com/semantica-agi/semantica/tree/main/semantica/conflicts>
- Semantica pipeline module:
  <https://github.com/semantica-agi/semantica/tree/main/semantica/pipeline>

Local Lolla context to read first:

- `docs/evals/current-system-capabilities-v0.md`
- `docs/evals/current-state-anti-drift-handoff-v0.md`
- `docs/evals/evaluation-flywheel-action-plan-v0.md`
- `docs/lolla-evaluation-methodology.md`
- `docs/lolla-reasoning-audit-harness-prd.md`
- `PROGRESS.md`

## Current Lolla Context

Lolla's current product thesis is:

```text
probabilistic interpretation inside deterministic custody
```

The LLM is allowed to interpret messy conversation, find pressure points, and
revise the answer. Deterministic code preserves artifacts, validates schemas,
records run health, exports review data, and makes absence or presence visible.
Human reviewers decide whether the revised answer actually improved the
decision surface.

Current shipped capabilities include:

- normal `$lolla` runs that produce revised answers and memos;
- local archive artifacts;
- `agent_result.json`;
- `evaluation.json`;
- `reasoning_trace.json`;
- extraction adequacy and semantic coverage reports;
- review-corpus JSONL and manifests;
- human-owned review labels;
- actionable-delta rubric;
- adversarial fixtures;
- risk-mode reliance visibility;
- user-values/priorities worksheet v0.

Current stop points:

- no real high-stakes reliance-present archive evidence yet;
- no automatic answer-quality judge;
- no automatic human-review labels;
- no automatic user-values extraction;
- no graph DB, embeddings, chunking, or memory layer;
- no specialist runtime/archive integration;
- no `conversation_understanding_ir.v0`;
- no runtime prompt rewrite or `SKILL.md` expansion by default.

## Product Read From Semantica

Semantica is broader than Lolla. It is closer to an infrastructure platform:

```text
ingest -> parse -> normalize -> split -> extract -> conflict detect
-> deduplicate -> knowledge graph -> provenance/reasoning/policy
-> storage/export/API/explorer
```

Lolla should not become that.

Lolla is narrower: a local reasoning-audit harness that runs one audit, writes
local artifacts, exposes custody/readiness, and leaves semantic quality
judgment to humans. It should not become a generic context platform, global
memory system, compliance layer, or answer-quality authority.

The useful lesson is narrower:

```text
accountability needs first-class records, not only prose explanations
```

The dangerous lesson would be:

```text
because graphs/provenance/policies are powerful, add them everywhere
```

That is exactly what this PRD rejects.

## Selective Borrowing Rule

Borrow only ideas that satisfy all of these:

- they improve local inspectability of a Lolla run;
- they preserve human ownership of semantic judgment;
- they can start as docs, fixtures, or local read-only exports;
- they do not require graph DBs, embeddings, global memory, or hosted services;
- they do not turn inferred values into durable user-profile facts;
- they do not imply answer quality, domain approval, or automatic safe use;
- they are useful even if no future LLM judge is ever built.

Do not borrow ideas that primarily serve:

- broad enterprise data ingestion;
- permanent shared agent memory;
- regulatory-compliance claims;
- general knowledge management;
- automatic policy enforcement;
- automatic conflict resolution;
- model-based risk classification;
- domain-specific authority.

## Product Goal

Add a Semantica-inspired accountability layer around Lolla's existing local
artifacts.

The desired future shape is:

```text
conversation
-> Lolla audit
-> revised answer and memo
-> deterministic archive artifacts
-> decision record
-> provenance map
-> conflict register
-> optional case graph view
-> human review / evaluation flywheel
```

The goal is not to make the machine "know" the conversation. The goal is to
make the machine's interpretation easier to inspect, challenge, and improve.

## Non-Goals

Do not build any of these from this PRD:

- graph database;
- vector embeddings;
- chunking pipeline;
- global context graph;
- persistent user memory;
- user profile;
- automatic user-values extraction;
- automatic conflict resolution;
- policy enforcement engine;
- compliance platform;
- generic agent safety layer;
- domain authority;
- SHACL/OWL/RDF compliance surface;
- hosted API;
- broad MCP server;
- Observatory redesign;
- `SKILL.md` rewrite;
- high-stakes run batch;
- LLM judge;
- answer-quality score;
- automatic `safe_for_agent_use`;
- domain-specific legal, medical, financial, crisis, safety, or employment
  protocol.

## Borrowed Primitives

### 1. Decision Record

Semantica makes decisions first-class objects. Lolla should borrow this as a
local projection, not as a permanent graph node.

Candidate artifact:

```text
lolla.audit_decision_record.v0
```

Purpose:

- summarize what decision the run audited;
- show what the original answer favored;
- show what the revised answer changed;
- show which action, threshold, sequence, gate, written term, or stop rule was
  added;
- link to local artifacts and review labels;
- stay safe for review-corpus export.

This is not:

- a truth record;
- a user-memory record;
- a domain decision approval;
- a complete conversation-understanding IR.

### 2. Provenance Map

Semantica's provenance module uses W3C PROV-O-style ideas such as entity,
activity, agent, used, generated, and derived-from. Lolla should borrow the
vocabulary, not the full compliance stack.

Candidate artifact:

```text
lolla.provenance_map.v0
```

Purpose:

- show how `conversation.txt`, `extraction.json`, `result.json`,
  `revised.txt`, `memo.md`, `evaluation.json`, `agent_result.json`, and review
  artifacts relate;
- preserve local hashes, byte counts, schema versions, and custody flags;
- make artifact lineage explicit for reviewers and future tooling.

This is not:

- a regulatory proof claim;
- an RDF export;
- a source-quote dump;
- a replacement for quote validation.

### 3. Conflict Register

Semantica treats conflicting sources/facts as first-class signals. Lolla should
borrow this for review conflicts.

Candidate artifact:

```text
lolla.review_conflict_register.v0
```

Candidate conflict categories:

- user-values conflict;
- stakeholder-obligation conflict;
- live-constraint conflict;
- recommendation/action conflict;
- risk-mode reliance conflict;
- artifact-health conflict;
- provider-boundary conflict;
- unresolved user-question conflict;
- human-review disagreement.

This is not:

- an automatic resolver;
- a severity score that decides answer quality;
- a replacement for human review.

### 4. Doctor / Preflight

Semantica's `doctor` idea is directly useful. Lolla has repeatedly needed to
confirm archive wiring, provider config, model/cost behavior, and review-corpus
visibility before spending tokens.

Candidate CLI:

```text
python3 scripts/lolla_doctor.py
```

or later:

```text
lolla doctor
```

Purpose:

- check archive root exists;
- check expected runtime scripts exist;
- check `.env`/provider configuration is present without printing secrets;
- check configured provider/model fields are visible in sanitized form;
- check latest review-corpus export can run read-only;
- check manifest counts are understandable;
- check no output path points inside an archive;
- check current repo has no tracked runtime diff when running from repo;
- print a compact readiness report.

This is not:

- a Lolla run;
- a model call;
- a prompt validator;
- a runtime behavior change;
- a provider-boundary policy change.

### 5. Case Graph View

Semantica's context graph is broad. Lolla should borrow only a run-local case
graph view.

Candidate artifact:

```text
lolla.case_graph.v0
```

Candidate nodes:

- decision;
- option;
- constraint;
- stakeholder;
- value/priorities item;
- unresolved conflict;
- original recommendation;
- revised recommendation;
- evidence gate;
- stop rule;
- user question;
- artifact;
- review label.

Candidate edges:

- `derived_from`;
- `changed_by`;
- `supports`;
- `blocks`;
- `requires_confirmation`;
- `adds_gate`;
- `narrows_scope`;
- `overclaim_retracted_by`;
- `reviewed_as`.

This is not:

- a graph DB;
- global memory;
- entity resolution;
- embeddings;
- GraphRAG;
- persistent shared context.

## Durable Architectural Decisions

- New work starts as docs, fixtures, and local read-only exports.
- Runtime integration is not approved by this PRD.
- All artifacts remain local-first.
- Review artifacts must be raw-content safe by default.
- Human labels remain human-owned.
- `evaluation.json` remains deterministic run-readiness, not advice wisdom.
- `caller_action` remains caller guidance, not human approval.
- `risk_mode` remains reliance/review context, not answer-quality scoring.
- User values/priorities remain confirmation-needed unless explicitly stated by
  the user in the source material and reviewed by a human.
- Graph-like exports are views over local run artifacts, not a new memory
  subsystem.

## PR Queue

The numbering below assumes the next available slice starts at PR55. If the
actual repo state differs, preserve the sequence intent and rename the PR
numbers accordingly.

This queue is a proposed implementation sequence. It is not approval for all
future work. Each later PR still needs its own scope, validation, boundary
checks, and merge decision.

### PR55: Semantica Comparative Architecture Note / Accountability PRD v0

Type: docs-only

Goal:

Capture the Semantica analysis in-repo so future sessions understand the
inspiration and the anti-copying boundary.

Likely files:

- `docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`
- `docs/conversation-understanding/research-and-design-v0.md`
- `docs/evals/current-state-anti-drift-handoff-v0.md`
- `docs/evals/evaluation-flywheel-action-plan-v0.md`
- `docs/lolla-reasoning-audit-harness-prd.md`
- `HOW_IT_WORKS.md`
- `PROGRESS.md`

Must include:

- what Semantica does well;
- where Lolla differs;
- what to borrow;
- what not to borrow;
- explicit rejection of graph DB, embeddings, memory, policy engine, and broad
  platform drift.
- the PR56-PR65 queue as a plan, not an approval.

Acceptance criteria:

- [ ] Explains Semantica inspiration in Lolla terms.
- [ ] Names the selective borrowing rule.
- [ ] Lists allowed primitives: decision record, provenance map, conflict
      register, doctor/preflight, case graph view.
- [ ] Lists non-goals clearly.
- [ ] No runtime code changes.

Validation:

- `git diff --check`
- Markdown link check over touched docs.
- Privacy/content scan over touched docs.
- Runtime boundary check for `SKILL.md`, `engine`, `scripts`, `observatory`.

Stop rule:

Do not implement any primitive in PR55.

### PR56: Lolla Doctor / Preflight Plan v0

Type: docs-only design

Status after PR56: completed as the dedicated doctor/preflight plan:
`docs/evals/lolla-doctor-preflight-plan-v0.md`.

Goal:

Define the preflight checks that help users avoid wasting model calls or
writing outputs into the wrong place.

Likely files:

- `docs/evals/lolla-doctor-preflight-plan-v0.md`
- `docs/evals/current-state-anti-drift-handoff-v0.md`
- `docs/lolla-reasoning-audit-harness-prd.md`
- `PROGRESS.md`

Must specify checks for:

- archive root;
- runtime skill directory;
- expected scripts;
- provider config present but secret-safe;
- model/provider/cost telemetry visibility;
- review-corpus export availability;
- manifest counts;
- no in-archive output;
- worktree/runtime diff warnings;
- privacy-safe output.

Acceptance criteria:

- [x] Defines exact future CLI output sections.
- [x] Defines pass/warn/fail semantics.
- [x] States that doctor never calls models.
- [x] States that doctor never runs `$lolla`.
- [x] States that doctor never mutates archives.
- [x] Defines what counts as a blocking failure.

Stop rule:

Do not add the CLI in PR56.

### PR57: Lolla Doctor Read-Only CLI v0

Type: code/tests/docs

Status after PR57: completed as the smallest read-only doctor CLI:
`docs/evals/lolla-doctor-readonly-cli-v0.md`.

Goal:

Add the smallest local read-only preflight CLI.

Likely files:

- `engine/system_b/lolla_doctor.py`
- `scripts/lolla_doctor.py`
- `tests/test_lolla_doctor.py`
- `docs/evals/lolla-doctor-readonly-cli-v0.md`
- handoff docs as needed

Required behavior:

- accepts archive root and optional manifest path;
- reads local filesystem only;
- sanitizes provider/config information;
- never prints secrets;
- never reads raw transcripts, memos, or revised answers;
- never calls models;
- never writes inside archives;
- returns machine-readable JSON and optional compact text.

Acceptance criteria:

- [x] Standard healthy local config produces `status: pass` or `status: warn`
      with explicit caveats.
- [x] Missing archive root produces deterministic fail.
- [x] Missing provider config produces deterministic warning/fail according to
      plan.
- [x] Existing review-corpus manifest counts are surfaced without leaking local
      raw content.
- [x] Secrets and local absolute paths are not printed except where explicitly
      documented as local-only and not intended for checked-in output.
- [x] Tests prove no model/client loader is called.

Validation:

- `python3 -m py_compile engine/system_b/lolla_doctor.py scripts/lolla_doctor.py`
- `PYTHONPATH=. pytest -q tests/test_lolla_doctor.py`
- focused related tests if review-corpus helpers are used.
- `git diff --check`
- privacy scan over generated sample output.

Boundary:

No `$lolla`, no model calls, no prompt changes, no `SKILL.md`, no archive
mutation.

### PR58: Audit Decision Record Design v0

Type: docs/JSON fixture design

Status after PR58: completed as the audit decision record design:
`docs/conversation-understanding/audit-decision-record-v0.md` and
`docs/conversation-understanding/audit-decision-record-v0.json`.

Goal:

Define `lolla.audit_decision_record.v0` as a local projection over existing
artifacts.

Likely files:

- `docs/conversation-understanding/audit-decision-record-v0.md`
- `docs/conversation-understanding/audit-decision-record-v0.json`
- roadmap/handoff docs as needed

Candidate fields:

- schema_version;
- case_id;
- run_id;
- archive_relpath;
- decision_question;
- original_recommendation_summary;
- revised_recommendation_summary;
- changed_action;
- added_thresholds;
- added_evidence_gates;
- added_stop_rules;
- added_written_terms;
- narrowed_scope;
- overclaim_retractions;
- values_or_stakeholder_conflicts;
- unresolved_user_questions;
- source_artifacts;
- review_refs;
- custody_flags;
- limitations.

Acceptance criteria:

- [x] The schema is compact and local-review safe.
- [x] It does not copy raw transcript, memo, or revised-answer text.
- [x] It does not claim answer quality.
- [x] It maps cleanly to PR31 actionable-delta labels.
- [x] It states why this is not `conversation_understanding_ir.v0`.

Stop rule:

Do not implement an exporter yet.

### PR59: Audit Decision Record Fixture Review v0

Type: docs/eval-only

Status after PR59: completed as the fixture/review gate:
`docs/evals/audit-decision-record-fixtures-v0.md`,
`docs/evals/audit-decision-record-fixtures-v0.json`, and
`reviews/human/audit-decision-record-fixture-review-v0/review.json`.

Goal:

Test whether the proposed decision record shape is useful on existing reviewed
cases before code generation exists.

Likely files:

- `docs/evals/audit-decision-record-fixtures-v0.md`
- `docs/evals/audit-decision-record-fixtures-v0.json`
- `reviews/human/audit-decision-record-fixture-review-v0/review.json`
- handoff docs as needed

Scope:

- 3-6 existing reviewed cases;
- paraphrase-only;
- no raw transcript/memo/revised-answer content.

Acceptance criteria:

- [x] Reviewers can see what changed in the recommendation.
- [x] Reviewers can map changes to PR31 labels.
- [x] Reviewers can see unresolved conflicts/questions.
- [x] Reviewers do not mistake the record for approval or truth.
- [x] Any confusing fields are revised before implementation.

Stop rule:

Do not add exporter or runtime integration.

### PR60: Provenance Map Design v0

Type: docs/JSON design

Status after PR60: completed as the provenance map design:
`docs/conversation-understanding/provenance-map-v0.md` and
`docs/conversation-understanding/provenance-map-v0.json`.

Goal:

Design a local provenance map for Lolla artifacts, inspired by PROV-O but not
claiming standards compliance.

Likely files:

- `docs/conversation-understanding/provenance-map-v0.md`
- `docs/conversation-understanding/provenance-map-v0.json`
- roadmap/handoff docs as needed

Candidate concepts:

- artifact entity;
- generation activity;
- agent/tool responsible;
- `used`;
- `generated`;
- `derived_from`;
- local hash;
- byte count;
- schema version;
- custody flags;
- privacy flags.

Acceptance criteria:

- [x] Maps current artifacts without changing runtime.
- [x] Avoids raw content and absolute checked-in paths.
- [x] Differentiates artifact existence from answer quality.
- [x] Can represent missing/degraded artifacts.
- [x] Does not require RDF, OWL, SHACL, or graph DB.

Stop rule:

No exporter implementation.

### PR61: Review Conflict Register Design v0

Type: docs/eval-only design

Status after PR61: completed as the review conflict register design:
`docs/evals/review-conflict-register-v0.md` and
`docs/evals/review-conflict-register-v0.json`.

Goal:

Define how Lolla should record unresolved conflicts for human review.

Likely files:

- `docs/evals/review-conflict-register-v0.md`
- `docs/evals/review-conflict-register-v0.json`
- roadmap/handoff docs as needed

Candidate conflict categories:

- user_values_conflict;
- stakeholder_obligation_conflict;
- live_constraint_conflict;
- recommendation_action_conflict;
- risk_mode_reliance_conflict;
- artifact_health_conflict;
- provider_boundary_conflict;
- unresolved_user_question_conflict;
- human_review_disagreement;
- provenance_gap_conflict;
- decision_record_flattening_risk.

Acceptance criteria:

- [x] Conflicts remain human-owned.
- [x] No automatic severity-to-action behavior.
- [x] No automatic resolution.
- [x] Supports values/priorities worksheet findings.
- [x] Supports high-stakes reliance caveat interpretation.
- [x] Supports later review-corpus export if approved.

Stop rule:

Do not integrate into runtime or review-corpus exporter.

If a future continuation feels tempted to add code, tests, exporters, schemas
under `engine/`, CLI support, runtime integration, or archive-reading behavior,
stop and report. PR61 is only a design artifact and safe example JSON.

### PR62: Case Graph Export Design v0

Type: docs/fixture design

Status after PR62: completed as the case graph export/view design:
`docs/conversation-understanding/case-graph-export-v0.md` and
`docs/conversation-understanding/case-graph-export-v0.json`.

Goal:

Design a run-local graph-shaped view over existing artifacts.

Likely files:

- `docs/conversation-understanding/case-graph-export-v0.md`
- `docs/conversation-understanding/case-graph-export-v0.json`
- roadmap/handoff docs as needed

Required constraints:

- JSON only;
- no graph DB;
- no embeddings;
- no entity-resolution system;
- no global memory;
- no raw transcript/memo/revised-answer content.

Acceptance criteria:

- [x] Defines node types.
- [x] Defines edge types.
- [x] Includes custody flags.
- [x] Shows how decision record, provenance map, conflict register, values
      worksheet, and human review can appear as nodes/edges.
- [x] States clearly that this is a view, not the source of truth.

Stop rule:

Do not implement exporter.

If a future PR62 continuation feels tempted to add code, tests, exporters,
schemas under `engine/`, CLI support, runtime integration, or archive-reading
behavior, stop and report. PR62 is only a design artifact and safe example
JSON.

### PR63: Accountability View Fixture Pack v0

Type: docs/JSON fixture

Status after PR63: completed as the accountability view fixture pack:
`docs/evals/accountability-view-fixtures-v0.md` and
`docs/evals/accountability-view-fixtures-v0.json`.

Goal:

Create paraphrase-only fixture bundles from existing reviewed cases that show
how audit decision record, provenance map, review conflict register, and case
graph views work together before any exporter exists.

Likely files:

- `docs/evals/accountability-view-fixtures-v0.md`
- `docs/evals/accountability-view-fixtures-v0.json`
- handoff docs as needed

Acceptance criteria:

- [x] 3 fixtures.
- [x] Every fixture has all four accountability views, custody flags, and
      limitations.
- [x] Reviewers can trace from decision to changed action and unresolved
      conflict.
- [x] No raw content copied.
- [x] No graph DB or exporter.

Stop rule:

Do not build code until fixture review passes.

### PR64: Accountability View Fixture Review v0

Type: docs/eval-only review

Status after PR64: completed as the accountability view fixture review:
`docs/evals/accountability-view-fixture-review-v0.md` and
`reviews/human/accountability-view-fixture-review-v0/review.json`.

Goal:

Have human/product review decide whether the combined accountability-view
fixtures are useful, whether any view creates false certainty, and which view,
if any, should move toward a later implementation decision.

Likely files:

- `docs/evals/accountability-view-fixture-review-v0.md`
- `reviews/human/accountability-view-fixture-review-v0/review.json`
- roadmap/handoff docs as needed

Review questions:

- Does the bundle make the Lolla run easier to inspect?
- Does the decision record clarify what changed?
- Does the provenance map clarify artifact lineage?
- Does the conflict register preserve unresolved tensions?
- Does the case graph clarify relationships, or does it create decorative
  structure?
- Does any view create false certainty?
- Which view seems most implementation-ready?
- Which view should remain design-only?

Acceptance criteria:

- [x] Review records pass/revise/exclude for each fixture.
- [x] Explicit implementation-readiness read for each view.
- [x] No exporter unless future PR is approved.

Result:

- 3 pass, 0 revise, 0 exclude;
- `audit_decision_record` is ready for a later exporter-design decision;
- `provenance_map` and `review_conflict_register` need more fixtures;
- `case_graph` should hold before implementation.

### PR65: Implementation Decision Gate v0

Type: docs-only decision

Status after PR65: completed as the accountability implementation decision
gate:
`docs/evals/accountability-implementation-decision-gate-v0.md`.

Goal:

Choose which primitive, if any, should move from design/fixtures to code.

Candidate outcomes:

- A: implement `audit_decision_record` exporter next;
- B: implement `provenance_map` exporter next;
- C: implement `review_conflict_register` helper/exporter next;
- D: implement `case_graph` exporter next;
- E: do more fixtures/review before implementation;
- F: stop the accountability-view lane for now.

Acceptance criteria:

- [x] Uses evidence from PR55-PR64.
- [x] Names exactly one future code-bearing next slice, or explicitly chooses no
      implementation.
- [x] Keeps all other lanes blocked.
- [x] Preserves no graph DB / no memory / no judge boundary.

Result:

- chooses outcome A: implement `audit_decision_record` exporter next;
- recommends future PR66 Audit Decision Record Read-Only Exporter v0;
- keeps provenance map, review conflict register, and case graph out of
  implementation for now;
- does not implement PR66, add exporter code, add runtime integration, read
  archives, call models, mutate archives, score answers, create labels, add
  graph DB, or add memory.

### PR66: Audit Decision Record Read-Only Exporter v0

Type: code/tests/docs

Status after PR66: completed as the read-only exporter:
`docs/evals/audit-decision-record-readonly-exporter-v0.md`,
`engine/system_b/audit_decision_record.py`,
`scripts/build_audit_decision_record.py`, and
`tests/test_audit_decision_record.py`.

Goal:

Implement the narrow local exporter that PR65 selected: build a safe
`lolla.audit_decision_record.v0` JSON artifact from an existing run directory
without running `$lolla`, calling models, mutating archives, or judging answer
quality.

Result:

- reads structured/custody-safe JSON surfaces only:
  `evaluation.json`, `agent_result.json`, `reasoning_trace.json`,
  `extraction_adequacy_report.json`, and optional `--review-json`;
- stats but does not semantically read `extraction.json` and `result.json`;
- does not read or copy `conversation.txt`, `memo.md`, `revised.txt`,
  `live_transcript.txt`, provider/model text, private reasoning artifacts, or
  private ledgers;
- emits all PR31 actionable-delta buckets as stable keys but does not infer
  labels from prose;
- records safe source-artifact metadata with relative paths only;
- refuses output paths equal to or inside the run directory;
- keeps `model_calls: 0`, `archive_mutated: false`, and all raw/private
  inclusion flags false;
- does not implement provenance-map, conflict-register, or case-graph
  exporters.

Stop rule:

Do not continue into PR67 automatically. Any next slice must be approved after
maintainer review of PR66 output and must not treat exported records as labels,
answer-quality scores, `safe_for_agent_use`, domain approval, memory, graph DB,
or runtime integration.

### PR67: Audit Decision Record Export Smoke / Review v0

Type: docs/review/data

Status after PR67: completed as the exporter smoke review:
`docs/evals/audit-decision-record-export-smoke-review-v0.md` and
`reviews/human/audit-decision-record-export-smoke-review-v0/review.json`.

Goal:

Review whether PR66 exporter output is understandable, useful, raw-content-safe,
and properly caveated before any archive integration, automatic generation, or
batch export is considered.

Result:

- reviews six exports: four existing reviewed archives and two fixture-backed
  temp runs;
- records 6 pass, 0 revise, 0 fail, 0 exclude;
- confirms artifact statuses are useful in all six;
- confirms custody and limitation clarity in all six;
- confirms raw-content safety in all six;
- keeps false-certainty risk none or low;
- finds empty PR31 buckets only partly clear in real archive exports because
  they can look like "no meaningful delta" instead of "labels were not supplied
  or inferred";
- does not change the exporter, production code, runtime behavior, archive
  integration, labels, scoring, judges, graph DB, memory, or Semantica-style
  platform work.

Stop rule:

Do not continue into PR68 automatically. PR67 recommends PR68 Audit Decision
Record Schema/Exporter Refinement v0 only after maintainer review, focused on
clarifying PR31 bucket and semantic-field population policy before deeper
integration.

## Coder Operating Rules

For every PR in this queue:

1. Start from current `origin/main`.
2. Use a dedicated branch.
3. Keep unrelated untracked local docs/plans/reviews untouched.
4. Use explicit file whitelists when staging.
5. Do not run `$lolla`.
6. Do not call models unless a future PR explicitly approves it.
7. Do not mutate archives.
8. Do not touch `SKILL.md` unless the PR explicitly says so.
9. Do not change prompts.
10. Do not add runtime behavior unless the PR explicitly says code-bearing and
    names the exact behavior.
11. Do not add graph DB, embeddings, chunking, global memory, policy engine,
    LLM judge, answer-quality scoring, or automatic labels.
12. Run hygiene checks before reporting:
    - `git diff --check`
    - `git diff --cached --check`
    - markdown link check over touched docs
    - trailing-whitespace scan over touched files
    - privacy/content scan for local paths, secret markers, raw-content
      markers, provider-reasoning markers, and credential markers
    - runtime-boundary check for `SKILL.md`, `engine`, `scripts`, and
      `observatory`, adjusted for code-bearing PRs.

## Success Criteria For This Program

This program succeeds if, after the queue, Lolla has clearer accountability
views over its own work while preserving the core boundary:

```text
LLMs interpret.
Deterministic code preserves and validates.
Humans judge quality.
No structure is allowed to masquerade as wisdom.
```

Evidence of success:

- reviewers can see the decision delta faster;
- provenance between artifacts is clearer;
- unresolved conflicts are not flattened;
- preflight checks reduce wasted runs;
- future coder sessions know not to build graph/memory/platform work;
- every new artifact is useful even without a judge.

Evidence of drift:

- the system starts storing user profiles;
- inferred values become durable facts;
- graph shape is treated as truth;
- deterministic checks are described as answer-quality checks;
- `caller_action` becomes human approval;
- high-stakes fixtures are described as real high-stakes evidence;
- generic knowledge-graph, embedding, or policy-engine work appears without a
  concrete Lolla review need.

## Recommended Immediate Next Step

Land PR55:

```text
Semantica Comparative Architecture Note / Accountability PRD v0
```

It should be docs-only. Its job is to make the inspiration and anti-copying
boundary durable before any code-bearing slice begins.

PR56 has now been carved out as the dedicated doctor/preflight docs-only plan:

```text
docs/evals/lolla-doctor-preflight-plan-v0.md
```

PR57 has now implemented the smallest local read-only doctor CLI:

```text
docs/evals/lolla-doctor-readonly-cli-v0.md
```

PR58 has now designed the audit decision record shape:

```text
docs/conversation-understanding/audit-decision-record-v0.md
docs/conversation-understanding/audit-decision-record-v0.json
```

PR59 has now reviewed six paraphrase-only decision-record fixtures:

```text
docs/evals/audit-decision-record-fixtures-v0.md
docs/evals/audit-decision-record-fixtures-v0.json
reviews/human/audit-decision-record-fixture-review-v0/review.json
```

PR60 has now designed the local provenance map shape:

```text
docs/conversation-understanding/provenance-map-v0.md
docs/conversation-understanding/provenance-map-v0.json
```

PR61 has now designed the local review conflict register shape:

```text
docs/evals/review-conflict-register-v0.md
docs/evals/review-conflict-register-v0.json
```

PR62 has now designed the local case graph export/view shape:

```text
docs/conversation-understanding/case-graph-export-v0.md
docs/conversation-understanding/case-graph-export-v0.json
```

PR63 has now created the local accountability-view fixture pack:

```text
docs/evals/accountability-view-fixtures-v0.md
docs/evals/accountability-view-fixtures-v0.json
```

PR64 has now reviewed those fixtures:

```text
docs/evals/accountability-view-fixture-review-v0.md
reviews/human/accountability-view-fixture-review-v0/review.json
```

PR65 has now made the accountability implementation decision:

```text
docs/evals/accountability-implementation-decision-gate-v0.md
```

PR66 has now implemented the read-only audit decision record exporter:

```text
docs/evals/audit-decision-record-readonly-exporter-v0.md
engine/system_b/audit_decision_record.py
scripts/build_audit_decision_record.py
tests/test_audit_decision_record.py
```

PR67 has now reviewed the exporter smoke output:

```text
docs/evals/audit-decision-record-export-smoke-review-v0.md
reviews/human/audit-decision-record-export-smoke-review-v0/review.json
```

PR66 remains the only approved code-bearing accountability implementation from
this lane so far. PR67 is review/data only. Neither slice adds runtime
integration, archive mutation, automatic generation, batch export,
provenance-map export, conflict-register export, case-graph export, graph DB,
embeddings, memory, entity resolution, GraphRAG, answer-quality scoring,
automatic labels, or Semantica-style platform work. Stop after PR67 unless a
new maintainer-approved slice explicitly starts PR68.
