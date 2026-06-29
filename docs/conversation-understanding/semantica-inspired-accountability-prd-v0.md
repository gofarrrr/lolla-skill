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

- [ ] Maps current artifacts without changing runtime.
- [ ] Avoids raw content and absolute checked-in paths.
- [ ] Differentiates artifact existence from answer quality.
- [ ] Can represent missing/degraded artifacts.
- [ ] Does not require RDF, OWL, SHACL, or graph DB.

Stop rule:

No exporter implementation.

### PR61: Review Conflict Register Design v0

Type: docs/eval-only design

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
- recommendation_change_conflict;
- artifact_health_conflict;
- provider_boundary_conflict;
- risk_mode_reliance_conflict;
- review_label_disagreement;
- unanswered_user_question.

Acceptance criteria:

- [ ] Conflicts remain human-owned.
- [ ] No automatic severity-to-action behavior.
- [ ] No automatic resolution.
- [ ] Supports values/priorities worksheet findings.
- [ ] Supports high-stakes reliance caveat interpretation.
- [ ] Supports later review-corpus export if approved.

Stop rule:

Do not integrate into runtime or review-corpus exporter.

### PR62: Case Graph Export Design v0

Type: docs/fixture design

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

- [ ] Defines node types.
- [ ] Defines edge types.
- [ ] Includes custody flags.
- [ ] Shows how decision record, provenance map, conflict register, values
      worksheet, and human review can appear as nodes/edges.
- [ ] States clearly that this is a view, not the source of truth.

Stop rule:

Do not implement exporter.

### PR63: Case Graph Fixture Pack v0

Type: docs/JSON fixture

Goal:

Create paraphrase-only case graph examples from existing reviewed cases.

Likely files:

- `docs/evals/case-graph-fixtures-v0.md`
- `docs/evals/case-graph-fixtures-v0.json`
- handoff docs as needed

Acceptance criteria:

- [ ] 3-6 fixtures.
- [ ] Every fixture has nodes, edges, custody flags, and limitations.
- [ ] Reviewers can trace from decision to changed action and unresolved
      conflict.
- [ ] No raw content copied.
- [ ] No graph DB or exporter.

Stop rule:

Do not build code until fixture review passes.

### PR64: Case Graph Fixture Review v0

Type: docs/eval-only review

Goal:

Have human/product review decide whether the case graph view is actually useful
or merely pretty structure.

Likely files:

- `docs/evals/case-graph-fixture-review-v0.md`
- `reviews/human/case-graph-fixture-review-v0/review.json`
- roadmap/handoff docs as needed

Review questions:

- Does the graph view make the decision delta easier to inspect?
- Does it preserve conflicts and uncertainties?
- Does it create false certainty?
- Does it duplicate existing artifacts without adding clarity?
- Should an exporter be built later?

Acceptance criteria:

- [ ] Review records pass/revise/exclude for each fixture.
- [ ] Explicit decision: continue, revise, or stop the case graph lane.
- [ ] No exporter unless future PR is approved.

### PR65: Implementation Decision Gate v0

Type: docs-only decision

Goal:

Choose which primitive, if any, should move from design/fixtures to code.

Candidate outcomes:

- A: implement `lolla_doctor` only;
- B: implement `audit_decision_record` exporter;
- C: implement `provenance_map` exporter;
- D: implement `review_conflict_register` local helper;
- E: implement `case_graph` exporter;
- F: stop, because fixtures did not prove enough value.

Acceptance criteria:

- [ ] Uses evidence from PR55-PR64.
- [ ] Names exactly one code-bearing next slice.
- [ ] Keeps all other lanes blocked.
- [ ] Preserves no graph DB / no memory / no judge boundary.

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

Stop after PR59. The next recommended slice is PR60 Provenance Map Design v0
only after maintainer review of PR57 through PR59. PR60 should not start
automatically from this PRD update, and it should remain docs/JSON design only
if approved.
