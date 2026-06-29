# PRD: Lolla As A Reasoning-Audit Harness

Status: Draft
Last updated: 2026-06-28
Audience: Lolla maintainers, agent builders, evaluation/governance reviewers, early technical collaborators

## Source Material

This PRD converts the June 2026 architecture discussion into an actionable product direction.

Primary inputs:

- Existing Lolla runtime and docs, especially `SKILL.md`, `HOW_IT_WORKS.md`, `docs/how-it-works/architecture-and-evolution.md`, `docs/how-it-works/live-flow.md`, and `docs/how-it-works/operations-and-limits.md`.
- The local paper `2604.14228v1.pdf`, "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems" by Jiacheng Liu, Xiaohan Zhao, Xinyi Shang, and Zhiqiang Shen.
- The local paper `2509.10147v1.pdf`, "Virtual Agent Economies" by Nenad Tomasev, Matija Franklin, Joel Z. Leibo, Julian Jacobs, William A. Cunningham, Iason Gabriel, and Simon Osindero.
- The local eval methodology notes supplied by the project owner:
  `AI Evals Methodology Deep Dive.md` and
  `Hamel Husain & Shreya Shankar on AI Evals Philosophy, Methodology, and an Evaluation OS Blueprint.md`.
- Current Lolla pitch document: `docs/lolla-pitch-and-invitation.md`.
- Lolla-specific eval doctrine: `docs/lolla-evaluation-methodology.md`.
- Agent-control research note: `docs/agent-control-layers-and-lolla-integration.md`, covering CrabTrap-style proxies, guardrails, approval systems, sandboxes, identity scopes, and observability/eval tools.
- Semantica-inspired accountability plan:
  `docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`.
- Lolla doctor/preflight plan:
  `docs/evals/lolla-doctor-preflight-plan-v0.md`.
- Lolla doctor read-only CLI:
  `docs/evals/lolla-doctor-readonly-cli-v0.md`.
- Audit decision record design:
  `docs/conversation-understanding/audit-decision-record-v0.md`.
- Provenance map design:
  `docs/conversation-understanding/provenance-map-v0.md`.

## Executive Summary

Lolla should evolve from a powerful conversation skill into a reusable reasoning-audit harness for AI agents and serious AI conversations.

The core product thesis:

> Lolla lets LLMs do semantic judgment, but surrounds that judgment with deterministic custody: fixed steps, structured artifacts, validation gates, run health, telemetry, archive, replay, and eventually evaluation.

The immediate product gap is not that Lolla lacks audit output. It already produces a revised answer, memo, Observatory, private ledgers, run health, and archive artifacts. The gap is that Lolla is still primarily operated as a human-triggered skill ritual. To become useful for agents, teams, and evaluation workflows, it needs a cleaner machine-readable contract, risk modes, better capture adequacy, and an evaluation layer that can say whether the audit improved the answer, not merely whether the audit ran.

This PRD proposes a staged roadmap with small mergeable PRs. The near-term target is not a full hosted product. It is a local, inspectable, agent-callable harness layer.

## Problem

The dangerous AI answer is often not obviously wrong. It is fluent, plausible, and slightly too settled.

For a human user, that can create borrowed certainty. For an agent, it can become operational action: sending a message, changing code, recommending a decision, triggering a workflow, or escalating a plan.

Current Lolla already audits these answers well in a local skill setting. But the current product surface has four practical limitations:

1. **Agent integration is only beginning.** New archived runs now produce a compact `lolla_agent_result.v1` handoff, metadata-first `risk_mode`, and a deterministic `evaluation.json` run-readiness receipt, but trigger policy, risk-mode enforcement, subjective evaluation, and deeper integration behavior are still roadmap items.
2. **Observability is ahead of subjective evaluation.** Lolla records what happened and can now check deterministic run-envelope consistency, but does not yet systematically evaluate whether the revised answer is better, more grounded, less overconfident, or more actionable.
3. **Long-conversation capture is still blunt.** The first-3-plus-last-15 rule is practical, but can omit middle turns where constraints, reversals, or dropped threads were introduced.
4. **Risk level is not behaviorally first-class yet.** A career decision, legal whistleblower scenario, product roadmap choice, and casual strategy brainstorm should not all use the same cost, evidence standard, optional reviewer behavior, or final warning language. Today `risk_mode` is persisted and PR36 defines the reliance policy, but risk mode does not yet change prompts, cost, Step 7, capture strictness, domain routing, or evaluation behavior.

The Claude Code design-space paper strengthens the architectural direction: successful agent systems keep the model loop simple and invest in the deterministic harness around it. Lolla should apply that lesson to reasoning quality.

## Product Thesis

Lolla is not another prompt pack, not another model, and not a generic critic.

Lolla is a reasoning-audit harness.

The LLM should handle:

- interpreting messy multi-turn conversations,
- detecting reasoning pressure,
- synthesizing counterarguments,
- applying private audit material to a revised position,
- writing human-readable advice.

The deterministic harness should handle:

- step sequencing,
- artifact creation,
- artifact validation,
- quote and provenance rules,
- private/public surface separation,
- telemetry,
- run health,
- archive,
- replay,
- evaluation eligibility,
- machine-readable handoff.

This boundary is the product. It is how Lolla avoids becoming one more fluent system that claims to audit fluency.

## Goals

- Make Lolla easy for an AI agent or external orchestrator to call after a serious recommendation.
- Preserve the current human-facing skill experience.
- Add a compact machine-readable audit result that says what changed, what still needs human judgment, and whether the run is safe to rely on.
- Fit beside agent control layers rather than replacing them, with optional trace, action, approval, policy, sandbox, and credential metadata.
- Introduce audit modes and risk handling so cost and strictness match stakes.
- Upgrade long-conversation capture from chronological truncation toward decision-aware capture.
- Add an evaluation layer that checks answer improvement, overcorrection, evidence support, and run-to-run stability.
- Keep all sensitive run artifacts local by default.
- Keep public prose clean. The user should see the improved reasoning, not a pile of internal machinery.

## Non-Goals

- Do not turn Lolla into a domain expert for law, medicine, finance, hiring, security, or therapy.
- Do not turn Lolla into a fact-checking engine. It may surface fact-sensitive reasoning, but factual verification remains a separate tool layer.
- Do not replace proxy gates, permission systems, sandboxes, identity brokers, or human approval systems.
- Do not make post-Step-6 subagents default-on again.
- Do not expose V60 chunk IDs, private ledger details, lane names, card IDs, or internal source IDs in ordinary user-facing chat.
- Do not replace the existing local Observatory with a hosted service in this roadmap.
- Do not build a complex graph workflow unless a concrete requirement proves the simple loop cannot carry the work.

## Target Users

### Human AI Power User

Uses Lolla after asking an AI for strategic advice. Wants a better second pass and a memo they can share or keep.

Need:

- clear revised advice,
- understandable take-backs,
- strong counterargument,
- portable memo,
- confidence that the run did not silently fail.

### Agent Builder

Builds agents that plan, recommend, or act. Wants a local audit layer before final action.

Need:

- stable input/output contract,
- machine-readable risk and run-health fields,
- artifact pointers,
- explicit stop conditions,
- ability to decide whether to proceed, ask the user, or rerun deeper.

### Evaluation Or Governance Reviewer

Looks at whether agents are improving, failing silently, or creating unsafe confidence.

Need:

- archive,
- trace,
- run-to-run comparison,
- cost and model-call metadata,
- product-output health,
- eval eligibility,
- reason why a run is clean, partial, degraded, or unsafe.

### Domain Expert Or Advisor

Uses Lolla as a second reader on reasoning structure, not as a replacement for expertise.

Need:

- no fake certainty,
- clear domain-boundary warnings,
- questions only the human/domain expert can answer,
- artifact trail for later review.

### AI Agent As Direct Caller

Calls Lolla when its own answer is ready but consequential.

Need:

- low-friction command/API,
- compact result,
- unambiguous proceed/hold/escalate signals,
- no requirement to parse a long human memo.

## Product Principles

### 1. Simple Loop, Strong Harness

The live flow should stay conceptually simple:

capture -> extract -> audit -> reconsider -> persist -> memo -> archive.

New complexity should live in typed contracts, helpers, validators, telemetry, evaluation, and docs. Avoid stuffing more obligations into `SKILL.md`.

### 2. Model Judgment Inside Deterministic Custody

The model may decide what the audit pressure means for the answer. Code decides whether required artifacts exist, whether IDs match, whether private material was accounted for, whether quotes validate, and whether a run can claim to be clean.

### 3. Observability Is Not Evaluation

A beautiful trace does not prove the answer got better. Lolla needs explicit evaluation artifacts that inspect the delta between original and revised answer.

### 4. Useful Friction Beats Smooth Approval

Lolla exists to add earned, actionable friction to over-smooth AI advice. Evaluation must not reward generic helpfulness, coherence, warmth, or comfort over decision protection. A revised answer can be less smooth and still be better if it adds a grounded gate, stop rule, threshold, or question that changes action quality.

### 5. Context Is A Product Resource

Capture quality is part of audit quality. A long conversation should not be reduced only by chronology. It should preserve load-bearing decision pivots.

### 6. Risk Should Change The Harness

High-stakes decisions need stricter capture, stricter output warnings, stronger evaluation, and possibly optional deeper review. Low-stakes decisions should remain cheap and fast.

### 7. Human Capability Matters

Lolla should help users become better readers of AI advice. The product should not merely replace user judgment with a second oracle.

### 8. Complement The Control Plane

Lolla should feed and consume control-plane context, but it should not pretend to be the whole control plane. CrabTrap-style proxies, permissions, approvals, sandboxes, identity brokers, and trace stores answer different questions. Lolla's slot is reasoning quality before advice/action and after problematic runs.

### 9. Local First, Inspectable By Default

Run data should remain local unless the user explicitly exports it. Artifacts should be human-readable where possible and machine-readable where needed.

## Current Baseline

As of 2026-06-28, Lolla already has:

- conversation-native runtime through `ConversationContext`,
- typed `ConversationIR`,
- four audit lanes,
- deterministic routing through curated substrate,
- V60 private enrichment,
- pre-Step-6 private thinking table,
- Step 6 revised answer,
- Step 6b private custody ledgers,
- default-off Step 7 pressure-check subagents,
- memo rendering,
- Observatory,
- run health,
- operator log,
- live transcript artifact,
- run-event log,
- archive under `~/.local/share/lolla/runs/`,
- `agent_result.json` with the `lolla_agent_result.v1` machine-readable handoff,
- `reasoning_trace.json`,
- export script for reasoning trace dataset.

Since the first harness PRD pass, the shipped harness layer has also added:

- `risk_mode` metadata propagation;
- optional local control-plane input/result sidecars;
- `capture_adequacy` metadata;
- deterministic `evaluation.json` run-readiness receipts;
- provider-boundary classification and signature-only reasoning-metadata
  filtering;
- review-corpus export with blank human-review fields;
- human-review taxonomy and workflow v0;
- synthetic-review boundary, prompt, and validator;
- review-readiness tiers;
- extraction adequacy reports, corpus export, findings analysis, and quote
  validation diagnostics;
- semantic coverage reports and corpus survey;
- offline specialist extractor probe harnesses and evidence notes;
- a six-case complex conversation baseline with full modern artifacts;
- the PR30-PR69 evaluation/accountability handoff chain from human review seed
  through risk-mode reliance visibility, current-state anti-drift docs,
  human-owned values/priorities review, and the Semantica-inspired
  accountability plan through decision-record fixtures, provenance map, review
  conflict register, case graph export/view design, and combined
  accountability-view fixtures, fixture review, implementation decision gate,
  read-only decision-record exporter, smoke review, schema/exporter
  refinement, and refined export review re-run.

The current complex baseline is recorded in:

`docs/conversation-understanding/complex-conversation-baseline-v0.md`

The current evaluation flywheel action plan is recorded in:

`docs/evals/evaluation-flywheel-action-plan-v0.md`

The plain-language current capability map is recorded in:

`docs/evals/current-system-capabilities-v0.md`

Current product read:

> The harness can now prove that a complex run was captured, archived, checked,
> and handed off cleanly. It can also show that the revised answer changed. It
> still cannot automatically prove that the change was good.

That keeps evaluation as the active frontier. The local PR30 review seed
performs the first human/product review pass over the six complex traces: all
six answer-level reviews passed, all six revised answers were labeled
improved, and all six remain `safe_for_agent_use: with_human_review` because
saved artifacts are reviewable while live output remains `not_checked`.

PR31 now defines the actionable-delta rubric. It names changed action, changed
threshold, changed sequence, added evidence gate, added stop rule, added
written term, added user question, narrowed scope, and retracted overclaim as
candidate units of improvement, while rejecting smoother prose, warmth, length,
generic comprehensiveness, extra caveats without action change, and
judge-palatable blandness as improvement by themselves.

PR32 now defines a six-fixture adversarial pair seed set. It tests smoothness,
status/aura, checklist theater, generic balance, warmth/confidence, market
excitement, and authority/loyalty traps without becoming a judge, score, or
runtime integration.

PR33 now broadens the human review set with a 14-record corpus batch. Twelve
full-modern records count as positive answer-level eval evidence; one older
partial record is `needs_followup`, and one degraded record is
`exclude_from_eval`. This supports the rubric, but still does not create a
judge, score, automatic labeler, benchmark claim, or runtime integration.

PR34 now designs the first-class `user_values_or_priorities_signal` surface. It
defines values, priorities, tradeoffs, obligations, non-negotiables, grounding,
confidence, reviewer use, and implementation gates without adding extraction,
runtime behavior, prompt changes, memory, automatic labels, or judging.

PR35 now decides live-output hygiene policy. `live_output_health: not_checked`
remains the honest default for normal runs; `clean` requires a complete trusted
transcript path; manual transcripts are not proof of clean live output; and
live-output hygiene does not relax `caller_action` or score answer quality.

PR36 now decides risk-mode behavior policy. Existing `risk_mode` names remain
the vocabulary; risk mode raises review and reliance strictness, but does not
approve actions, make Lolla a domain authority, relax `caller_action`, or change
runtime behavior.

PR37 now adds a risk-mode fixture matrix. It covers `quick`, `standard`,
`deep`, `high_stakes`, `stability`, and excluded/domain-review routing with
expected answer-level, run-envelope, `safe_for_agent_use`, and `caller_action`
reads before any enforcement.

PR38 now reviews the fixture matrix. All original PR37 fixtures passed, one
missing high-stakes values/priorities conflict fixture was added, and the matrix
is usable as a future implementation gate without approving runtime
enforcement.

PR39 now plans the risk-mode implementation path. It names high-stakes
reliance/readiness tightening as the smallest future behavior change and
recommends contract-lock tests before artifact clarity or runtime enforcement.

PR40 now locks the current risk-mode contract in tests. Otherwise clean
`high_stakes` runs keep `caller_action: ask_user_first`; degraded high-stakes
runs keep `caller_action: do_not_use_run_degraded`; clean `standard` behavior
does not regress; and review corpus records preserve risk/reliance metadata.

PR41 now clarifies `evaluation.json` with `risk_mode_reliance_policy` for
high-stakes runs. The check makes reliance caveats visible without changing
`caller_action`, scoring answer quality, approving domain use, or enforcing
runtime behavior.

PR42 now exposes that caveat as compact `risk_mode_reliance` metadata in
review-corpus records and human-review workflow docs. It keeps
`safe_for_agent_use` human-owned and does not change `caller_action`.

PR43 reviews that surface with fixtures because the local real archive
corpus has zero high-stakes `risk_mode_reliance.present: true` records. The
fixture-backed batch validates that reviewers can read
`risk_mode_reliance.status: pass` as a conservative reliance-policy expression,
not as answer-quality pass, domain approval, or automatic
`safe_for_agent_use`.

PR44 now adds additive review-corpus manifest counts for
`risk_mode_reliance.present`, presence by `risk_mode`, and reliance-check
status. It keeps the existing review-corpus manifest schema name and does not
change per-record `risk_mode_reliance`, runtime behavior, caller action, judge
behavior, or archive contents.

PR45 now records the current-state anti-drift handoff. It summarizes the PR30-PR54
chain, records that the current 80-record real review corpus is all `standard`
with zero high-stakes reliance-present records, and names the approval gates
before real high-stakes evidence creation, values worksheet automation, or trusted
live-output implementation. It does not change runtime behavior, prompts,
`SKILL.md`, archives, caller action, judges, scoring, or automatic labels.

PR46 now defines the approval and custody plan for future high-stakes evidence
creation without running any cases. PR47 adds paraphrase-only high-stakes
fixtures so reviewers can test expectations before real archive records exist.
PR48 adds a read-only review-corpus evidence-readiness analyzer that consumes
manifest JSON and reports whether high-stakes reliance-present records actually
exist. It treats old or thin manifests as insufficient, not as evidence, and it
does not read raw archives, call models, judge answer quality, or approve real
high-stakes runs.

PR49 now plans the user-values/priorities worksheet surface. It makes PR34's
missing values/priorities signal actionable for human review without adding
extraction, exports, memory, runtime behavior, `conversation_understanding_ir.v0`,
automatic labels, `safe_for_agent_use` automation, or a judge.

PR50 now adds paraphrase-only worksheet fixtures for that surface. It tests
whether the worksheet is understandable through human-review examples before
any exporter, extraction, memory, runtime behavior, automatic labels, or judge
work.

PR51 now reviews those worksheet fixtures. It marks all six PR50 fixtures as
pass examples for human review, preserves the human-owned boundary, and
recommends blank worksheet/export structure before any extraction, runtime
behavior, automatic labels, or judge work.

PR52 now adds that blank worksheet/export structure. It creates empty
`lolla.user_values_priorities_worksheet.v0` JSON from optional compact metadata
without reading archives, extracting values, populating labels, changing
runtime behavior, or adding a judge.

PR53 now pilots human-filled worksheets on existing reviewed records. It stores
four paraphrase-only local-review worksheets, keeps confirmation needs visible,
and recommends a pilot review / v0 decision before any extraction, runtime
behavior, automatic labels, or judge work.

PR54 now reviews that pilot and closes the user-values/priorities worksheet lane
at v0 for human-owned review. It marks all four pilot worksheets pass and
pauses before extraction, memory, runtime integration, automatic labels,
`safe_for_agent_use` automation, answer-quality scoring, or judge work.

PR55 now lands the Semantica-inspired accountability PRD:

`docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`

It borrows accountability primitives from Semantica in Lolla terms: local
decision records, provenance maps, review conflict registers, doctor/preflight
diagnostics, and run-local case graph views. It does not approve graph
databases, embeddings, chunking, memory, policy enforcement, compliance
platform work, generic agent safety layers, domain authority, runtime behavior,
automatic labels, answer-quality scoring, LLM judges, prompts, `SKILL.md`, or
archive mutation. PR56 has now carved out the doctor/preflight design as a
separate docs-only plan.

PR56 now lands the Lolla Doctor / Preflight plan:

`docs/evals/lolla-doctor-preflight-plan-v0.md`

It defines the future read-only doctor check groups, pass/warn/fail semantics,
blocking versus warning examples, and `lolla.doctor_report.v0` draft shape. It
does not add the CLI, run `$lolla`, call models, mutate archives, change
prompts, change `SKILL.md`, change provider-boundary policy, change
`caller_action`, approve high-stakes runs, add judges, add scoring, add
automatic labels, or begin Semantica-style platform work. PR57 has now
implemented the smallest read-only doctor CLI from that plan.

PR57 now lands the Lolla Doctor Read-Only CLI:

`docs/evals/lolla-doctor-readonly-cli-v0.md`

It implements `lolla.doctor_report.v0` as a local deterministic preflight
report for runtime discovery, archive-root discovery, helper availability,
provider/config presence, cost-table readiness, optional review-corpus manifest
counts, high-stakes evidence visibility, output-path safety, repo/runtime
boundary state, and privacy flags. It does not run `$lolla`, call models, read
archive payloads, mutate archives, change prompts, change `SKILL.md`, change
provider-boundary policy, approve high-stakes use, judge answer quality, or
populate labels. Its planned next slice was PR58 Audit Decision Record Design
v0, docs/JSON design only.

PR58 now lands the Audit Decision Record design:

`docs/conversation-understanding/audit-decision-record-v0.md`

It defines `lolla.audit_decision_record.v0` as a paraphrase-only local
accountability projection over existing artifacts. It summarizes the audited
decision, original/revised recommendation shape, PR31 actionable-delta buckets,
unresolved conflicts/questions, source artifacts, review refs, custody flags,
and limitations. It does not implement an exporter, run `$lolla`, call models,
mutate archives, change prompts, change `SKILL.md`, approve high-stakes use,
judge answer quality, create automatic labels, or create
`conversation_understanding_ir.v0`. Its planned next slice was PR59 Audit
Decision Record Fixture Review v0, docs/eval-only.

PR59 now lands the Audit Decision Record fixture review:

`docs/evals/audit-decision-record-fixtures-v0.md`

It creates six paraphrase-only decision-record fixtures from existing reviewed
cases and reviews all six as `pass`. PR31 mapping is useful in all six, and
reviewers can use all six without raw content. The review marks the shape ready
for a future read-only exporter design prototype with caveats. It does not
implement an exporter, run `$lolla`, call models, mutate archives, change
prompts, change `SKILL.md`, approve high-stakes use, judge answer quality, or
create automatic labels.

PR60 now lands the Provenance Map design:

`docs/conversation-understanding/provenance-map-v0.md`

It defines `lolla.provenance_map.v0` as a local artifact-lineage map for how
run and review artifacts depend on each other. It uses Lolla-shaped entity,
activity, agent, and relationship vocabulary, but it does not claim RDF,
PROV-O, W3C, OWL, or SHACL compliance. It does not implement an exporter, read
archives, run `$lolla`, call models, mutate archives, change prompts, change
`SKILL.md`, add graph DB, add memory, approve high-stakes use, judge answer
quality, or create automatic labels. PR61 followed it as a docs/JSON design
slice.

PR61 now lands the Review Conflict Register design:

`docs/evals/review-conflict-register-v0.md`

It defines `lolla.review_conflict_register.v0` as a human-review-owned surface
for unresolved tensions across values, stakeholder obligations, live
constraints, recommendation/action changes, risk-mode reliance, artifact
health, provider boundaries, unresolved questions, review disagreement,
provenance gaps, and decision-record flattening risk. It does not resolve
conflicts, automate severity, enforce policy, implement an exporter, run
`$lolla`, call models, read or mutate archives, add labels, score answer
quality, or judge advice. PR62 followed it as a docs/JSON design slice.

PR62 now lands the Case Graph Export design:

`docs/conversation-understanding/case-graph-export-v0.md`

It defines `lolla.case_graph.v0` as a future run-local case graph export/view
shape over existing review-safe artifacts. It shows how decision, original and
revised recommendation, PR31 delta, evidence gate, stop rule, user question,
unresolved conflict, artifact, provenance activity, review record, doctor
check, and limitation nodes can relate. It does not implement an exporter, read
archives, run `$lolla`, call models, mutate archives, change prompts, change
`SKILL.md`, add graph DB, add memory, add GraphRAG, add entity resolution,
approve high-stakes use, judge answer quality, or create automatic labels. It
stopped before the later fixture evidence gate.

PR63 now lands the Accountability View fixture pack:

`docs/evals/accountability-view-fixtures-v0.md`

It creates three paraphrase-only fixture bundles that show audit decision
record, provenance map, review conflict register, and case graph views together
for existing reviewed cases. It does not implement exporters, read archives,
run `$lolla`, call models, mutate archives, change prompts, change `SKILL.md`,
add graph DB, add memory, add GraphRAG, add entity resolution, score answer
quality, create labels, or judge advice. PR64 followed it as docs/eval-only
fixture review.

PR64 now lands the Accountability View fixture review:

`docs/evals/accountability-view-fixture-review-v0.md`

It reviews all three PR63 bundles. All three pass as useful inspection evidence,
but the implementation-readiness signal is narrow: only
`audit_decision_record` is ready for a later exporter-design decision;
`provenance_map` and `review_conflict_register` need more fixtures; `case_graph`
should hold before implementation. PR64 does not implement exporters, read
archives, run `$lolla`, call models, mutate archives, change prompts, change
`SKILL.md`, add graph DB, add memory, score answer quality, create labels, or
judge advice.

PR65 now lands the Accountability Implementation Decision Gate:

`docs/evals/accountability-implementation-decision-gate-v0.md`

It chooses outcome A and recommends a future PR66 Audit Decision Record
Read-Only Exporter v0. It does not implement that exporter, start PR66, read
archives, run `$lolla`, call models, mutate archives, change prompts, change
`SKILL.md`, add graph DB, add memory, score answer quality, create labels, or
judge advice.

PR66 now lands the Audit Decision Record Read-Only Exporter:

`docs/evals/audit-decision-record-readonly-exporter-v0.md`

It implements `lolla.audit_decision_record.v0` as a local deterministic export
from structured/custody-safe run artifacts. It reads `evaluation.json`,
`agent_result.json`, `reasoning_trace.json`,
`extraction_adequacy_report.json`, and optional `--review-json`; it does not
read raw transcript, memo, revised-answer, provider/model text, or private
reasoning artifacts. It refuses output inside the run directory, keeps
`model_calls: 0` and `archive_mutated: false`, does not infer PR31 labels, and
does not score answer quality, approve recommendations, decide
`safe_for_agent_use`, or integrate with runtime behavior.

PR67 now lands the Audit Decision Record Export Smoke Review:

`docs/evals/audit-decision-record-export-smoke-review-v0.md`

It reviews six PR66 exporter outputs from four existing reviewed archives and
two fixture-backed temp runs. All six pass as useful, raw-content-safe
accountability shells, and artifact status, custody, and limitation clarity are
strong. The review recommends PR68 schema/exporter refinement before archive
integration or automatic generation because empty PR31 buckets are only partly
clear as "not supplied / not inferred" non-claims.

PR68 now lands that Audit Decision Record Schema / Exporter Refinement:

`docs/evals/audit-decision-record-schema-exporter-refinement-v0.md`

It keeps `lolla.audit_decision_record.v0` and adds PR31 population policy,
per-bucket status, nested buckets, and semantic-field empty-meaning metadata so
empty fields read as non-claims. It does not add label inference, scoring,
judges, archive integration, automatic generation, or runtime behavior.

PR69 now lands the Audit Decision Record Export Review Re-Run:

`docs/evals/audit-decision-record-export-review-rerun-v0.md`

It reviews seven refined PR68 exporter outputs and confirms the original PR67
empty-field confusion is fixed: empty PR31 bucket clarity is seven
`clear_non_claim`, semantic empty-field clarity is seven `clear_non_claim`, raw
content safety remains safe, and no reviewer needs docs to avoid the basic
non-claim misread. It recommends a future PR70 archive-integration decision
gate, not archive integration implementation.

This roadmap should build on that. It should not restart the architecture.

## Proposed Product

Build **Lolla Reasoning-Audit Harness v1**: a local, agent-callable audit layer that wraps the existing skill/runtime with a stable result contract, risk modes, evaluation artifacts, and improved context custody.

The user-facing experience can remain `$lolla`.

The agent-facing experience should become:

1. Agent produces a serious recommendation.
2. Agent calls Lolla with transcript and current answer.
3. Lolla returns a compact result:
   - run status,
   - risk mode,
   - strongest counter-pressure,
   - revised position summary,
   - action recommendation for the caller,
   - stop/escalate conditions,
   - unanswered human questions,
   - artifact pointers.
4. Agent decides:
   - continue with revised answer,
   - ask user for missing information,
   - rerun in deep mode,
   - stop because run health is degraded or stakes exceed supported use.

## Functional Requirements

### R1: Agent-Facing Result Contract

Priority: P0
Owner area: runtime/artifacts/docs
Status: Implemented for archive-time `lolla_agent_result.v1`

Create a stable machine-readable result file:

`/tmp/lolla_<run_id>_agent_result.json`

and archive copy:

`agent_result.json`

Required schema name:

`lolla_agent_result.v1`

Minimum fields:

```json
{
  "schema_version": "lolla_agent_result.v1",
  "run_id": "20260624T000000Z_example",
  "status": "ok",
  "run_health_overall": "healthy",
  "risk_mode": "standard",
  "caller_action": "use_revised_answer",
  "main_counter_pressure": "The answer treated a useful frame as settled before testing reversal conditions.",
  "position_changed": true,
  "changed_advice_summary": [
    "Add stop-loss criteria before acting.",
    "Treat spouse approval as first gate, not final gate."
  ],
  "take_backs": [
    "The original answer overtreated information value as sufficient reason to move."
  ],
  "human_questions": [
    "What condition would make this plan unacceptable after three months?"
  ],
  "do_not_act_before": [
    "Run diligence on equity terms.",
    "Get an informed spouse yes with explicit boundaries."
  ],
  "artifact_paths": {
    "memo": "/tmp/lolla_run_memo.md",
    "archive": "<archive-root>/case/run",
    "reasoning_trace": "<archive-root>/case/run/reasoning_trace.json",
    "observatory_url": "http://localhost:8084"
  }
}
```

Acceptance criteria:

- Generated during archive for completed, degraded, partial, incomplete, or capture-critical runs.
- Archived with the rest of the run.
- Does not include private chunk IDs, V60 internals, lane labels, or hidden ledger details.
- `caller_action` is from a closed enum:
  - `use_revised_answer`
  - `ask_user_first`
  - `rerun_deeper`
  - `do_not_use_run_degraded`
  - `unsupported_high_stakes_domain`
- Test covers clean run, partial run, capture-critical run, and product-output-unsafe run.

### R2: Risk Modes

Priority: P0
Owner area: runtime/docs/skill
Status: Implemented as metadata-first runtime propagation plus PR36 policy
design

Add explicit audit modes:

- `quick`
- `standard`
- `deep`
- `high_stakes`
- `stability`

Current implementation:

- Mode is selected with `LOLLA_AUDIT_MODE`.
- Missing or empty mode defaults to `standard`.
- Invalid explicit mode fails before model calls.
- The normalized value is persisted as `risk_mode` in `result.json`,
  `agent_result.json`, `reasoning_trace.json`, and archive metadata.
- The mode is metadata-first for now. It does not change prompts, cost, Step 7,
  high-stakes domain policy, evaluation strictness, capture strictness, or
  replay/comparison behavior.
- The agent-result contract already keeps otherwise clean `high_stakes` runs
  conservative with `caller_action: ask_user_first`.
- PR36 documents the behavior policy without implementing enforcement.
- PR37 documents fixture expectations without implementing enforcement.
- PR38 reviews the fixture expectations without implementing enforcement.
- PR39 plans high-stakes reliance/readiness tightening and recommends
  contract-lock tests first, without implementing enforcement.
- PR40 locks the current high-stakes conservative contract in tests without
  changing runtime behavior.
- PR41 adds deterministic high-stakes reliance-policy clarity to
  `evaluation.json` without changing caller-action policy.
- PR42 exposes that reliance-policy clarity in review-corpus records and
  human-review workflow docs without changing caller-action policy.
- PR43 verifies reviewer interpretation with fixtures because the real local
  corpus has no high-stakes reliance-present examples.
- PR44 adds manifest-level counts for the PR42 surface without changing the
  manifest schema name or per-record behavior.
- PR45 records the anti-drift handoff and current decision gates without
  changing runtime behavior.
- PR48 adds manifest-only evidence-readiness analysis without changing runtime
  behavior.
- PR49 plans a human-owned values/priorities worksheet without changing runtime
  behavior.
- PR50 adds paraphrase-only worksheet fixtures without changing runtime
  behavior.
- PR51 reviews those worksheet fixtures without changing runtime behavior.
- PR52 adds blank worksheet/export structure without changing runtime behavior.
- PR53 pilots human-filled worksheets without changing runtime behavior.
- PR54 reviews the pilot and pauses the worksheet lane without changing runtime
  behavior.

Future behavior:

| Mode | Use case | Behavior |
|---|---|---|
| `quick` | low-stakes strategic check | May target fewer optional calls and a compact memo after behavior is explicitly implemented. |
| `standard` | default serious conversation | Current default behavior. |
| `deep` | user asks for deeper review | May enable optional deeper review after Step 6b ledger validation in a later PR. |
| `high_stakes` | legal, medical, financial, safety, severe career/family consequences | May add stronger capture/eval gates and warning language later; it currently makes no domain-assurance claim. |
| `stability` | test or regression mode | May run comparison/replay flow across repeated runs or archived pairs later. |

PR36 adds the policy decision: risk mode changes review and reliance burden
before it changes runtime. High-stakes mode is stricter reasoning hygiene, not
domain assurance. Runtime enforcement requires fixtures, tests, contract docs,
and a later PR.

PR37 adds the first fixture matrix. Future implementation should cite those
fixtures and explain whether behavior stays the same or changes before touching
runtime, caller-action policy, or `SKILL.md`.

PR38 reviews those fixtures and adds the high-stakes values/priorities conflict
case. Future implementation should cite PR36, PR37, and PR38 before touching
runtime, caller-action policy, or `SKILL.md`.

PR39 names the smallest future behavior change as high-stakes
reliance/readiness tightening. It recommends a test-only contract-lock slice
before artifact clarity, runtime enforcement, caller-action changes, or judge
work.

PR40 adds that contract-lock test slice. Future evaluation-artifact clarity
work should keep those tests green and should not redesign `caller_action`.

PR41 adds the deterministic evaluation-artifact clarity slice. Future
review/corpus surface work should expose the same caveat for humans without
making `safe_for_agent_use` automatic.

PR42 adds that review/corpus surface integration. Future review batches should
test whether reviewers can use the caveat consistently before any judge,
runtime enforcement, or automatic labeling work.

Acceptance criteria:

- Mode is recorded in `result.json`, `reasoning_trace.json`, `agent_result.json`, and archive metadata.
- Mode changes are visible in local artifacts.
- Default remains `standard`.
- Existing `$lolla` behavior does not become more expensive or run additional
  review steps from mode metadata alone.

### R3: Trigger Policy For Agents

Priority: P0
Owner area: docs/agent contract

Define when an agent should call Lolla.

Trigger if all are true:

- The conversation produced advice, a plan, recommendation, or strategic judgment.
- The advice could materially affect a person, organization, budget, legal posture, operational workflow, or important relationship.
- The answer sounds settled enough that the user may act on it.
- No independent reasoning-quality check has run.

Do not trigger for:

- ordinary coding fixes with tests,
- simple factual Q&A,
- trivial brainstorming,
- pure style rewrites,
- tasks where deterministic verification is clearly better.

Acceptance criteria:

- Add a short docs section that agent builders can copy.
- Include examples of trigger and non-trigger cases.
- Connect trigger policy to `risk_mode`.

### R4: Control-Plane Integration Contract

Priority: P0
Owner area: agent contract/docs/runtime artifacts

Status: v0 metadata sidecar implemented. Archived runs can now preserve
optional `control_input.json`, summarize compact control references in
`agent_result.json` and `reasoning_trace.json`, and generate
`control_result.json` when input is supplied. This does not add auto-triggering,
approval enforcement, sandboxing, proxy behavior, or tool execution.

Define optional metadata so Lolla can be called from agent frameworks, approval systems, proxies, sandboxes, or trace pipelines without depending on one vendor.

The point is not to make Lolla a security layer. The point is to let security, approval, and observability systems attach Lolla's reasoning-audit result to the decisions they already control.

Optional input metadata:

- `external_trace_id`
- `external_span_ids`
- `agent_run_id`
- `agent_framework`
- `proposed_action`
- `tool_call_ids`
- `approval_id`
- `policy_engine`
- `policy_decision`
- `sandbox_id`
- `credential_scope`

Pre-action gate result fields:

- `control_mode`, for example `pre_final_answer`, `pre_action_reasoning_gate`, `post_run_review`, or `regression_eval`.
- `caller_action`, still from a closed enum, with mappings to approval systems.
- `human_approval_context`, including approval summary and suggested rejection or follow-up language when relevant.
- `do_not_act_before`, with concrete gates the calling system can show to a human.

Acceptance criteria:

- Lolla can receive optional external trace/control metadata without requiring any specific vendor integration.
- `agent_result.json` includes external trace references when supplied.
- The contract documents how `caller_action` maps to approval outcomes such as proceed, ask user, require approval, reject, or block because reasoning is incomplete.
- Docs explain how Lolla complements, not replaces, CrabTrap-style proxies, sandboxes, permission hooks, identity scopes, and observability/eval systems.
- No external metadata is required for ordinary `$lolla` use.

### R5: Capture Adequacy Upgrade

Priority: P1
Owner area: extraction/capture/runtime

Status: First metadata slice implemented; decision-aware capture remains roadmap.

Current shipped behavior adds a compact deterministic `capture_adequacy` summary
with schema `lolla.capture_adequacy.v0`. It records status, strategy,
declared/captured/omitted counts, captured windows, omitted windows, risk flags,
and notes, then carries that through run health, `agent_result.json`,
`reasoning_trace.json`, and deterministic `evaluation.json` checks.

This makes capture loss visible before changing capture strategy. It does not
semantically reconstruct omitted turns, preserve middle-turn pivots, or replace
the current first-3-plus-last-15 fallback.

Future work should replace or augment blunt long-conversation truncation with
decision-aware capture.

The current fallback can remain, but a new capture manifest should identify:

- final assistant recommendation passage,
- user constraints,
- user objections/corrections,
- changed decision options,
- dropped threads,
- high-stakes claims,
- quotes used downstream,
- omitted middle-turn ranges.

Acceptance criteria:

- `capture_adequacy` records whether capture is full, first-N-plus-last-N, critical, or unknown.
- A long conversation run can show which omitted ranges were dropped.
- The extraction step refuses or degrades when final recommendation text is missing.
- Deterministic evaluation warns or fails on capture adequacy problems.

Future decision-aware capture acceptance:

- Tests cover a long conversation where a middle-turn constraint is preserved instead of merely recorded as omitted.

### R6: Evaluation Methodology And Failure Taxonomy

Priority: P1
Owner area: eval/docs/archive/Observatory

Before adding automated subjective judges, create a Lolla-specific evaluation methodology and failure taxonomy grounded in real archived runs.

The methodology lives in `docs/lolla-evaluation-methodology.md`. It is part of the product contract because Lolla's eval problem is unusual: generic LLM judges may prefer smoothness and agreement, while Lolla is intentionally trying to introduce useful friction.

Requirements:

- Treat full Lolla traces, not isolated final answers, as the eval unit.
- Run human error analysis on 50 to 100 archived or fixture runs before creating subjective judges.
- Record the first upstream failure per run.
- Build an initial failure taxonomy with clear labels, severity, and likely eval type.
- Use deterministic checks wherever possible.
- Use LLM judges only for fuzzy checks, only with binary labels, and only after calibration against human labels.
- Include adversarial judge-calibration pairs where the smoother answer is worse than the rougher but more decision-protective answer.

Current v0 slice:

- `docs/evals/lolla-failure-taxonomy.md` defines the initial human-review failure taxonomy.
- `docs/evals/lolla-human-review-v0.json` defines the machine-readable `lolla.human_review.v0` label contract.
- `docs/evals/human-review-workflow.md` defines the first reviewer workflow over PR13 review-corpus records.
- `engine/system_b/human_review.py` validates label objects for local tooling.
- Review-corpus records carry deterministic readiness tiers so legacy content-only
  archives are not confused with full modern custody runs.
- Synthetic/subagent review outputs are allowed only as rehearsal notes or
  candidate labels; they do not populate `lolla.human_review.v0` without human
  ratification.
- `engine/system_b/synthetic_review.py` validates synthetic review outputs and
  delegates candidate label validation to the human-review contract.
- `docs/evals/user-values-priorities-worksheet-plan-v0.md` defines the next
  human-review-only worksheet surface for PR34 values/priorities evidence
  before any exporter, extraction, memory, runtime behavior, or judge exists.
- `docs/evals/user-values-priorities-worksheet-fixtures-v0.md` and
  `docs/evals/user-values-priorities-worksheet-fixtures-v0.json` test that
  worksheet surface with paraphrase-only fixtures before code or judge work.
- `docs/evals/user-values-priorities-blank-worksheet-export-v0.md` defines the
  deterministic blank worksheet helper.
- `docs/evals/user-values-priorities-worksheet-human-pilot-v0.md` and
  `reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json`
  pilot human-filled worksheets before extraction, runtime behavior, automatic
  labels, or judge work.
- `docs/evals/user-values-priorities-pilot-review-v0.md` and
  `reviews/human/user-values-priorities-pilot-review-v0/review.json` close the
  worksheet lane at v0 for human-owned review before any automation.
- `docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`
  defines the PR55 accountability primitive queue and keeps future decision
  records, provenance maps, conflict registers, doctor/preflight, and case graph
  views separate from graph DBs, memory, policy engines, automatic labels,
  answer-quality scoring, and LLM judges.
- `docs/evals/lolla-doctor-preflight-plan-v0.md` defines the PR56
  doctor/preflight plan and keeps the future CLI read-only, local,
  deterministic, model-call-free, and outside archive mutation.
- `docs/evals/lolla-doctor-readonly-cli-v0.md` documents the PR57 doctor CLI,
  which implements `lolla.doctor_report.v0` without running `$lolla`, calling
  models, reading archive payloads, mutating archives, or judging answer
  quality.
- `docs/conversation-understanding/audit-decision-record-v0.md` defines the
  PR58 `lolla.audit_decision_record.v0` shape as a paraphrase-only review
  projection over existing artifacts and PR31 labels, before any exporter or
  runtime integration.
- `docs/evals/audit-decision-record-fixtures-v0.md` and
  `reviews/human/audit-decision-record-fixture-review-v0/review.json` review
  six PR59 paraphrase-only decision-record fixtures before any exporter,
  runtime integration, labels, scoring, or judge.
- `docs/conversation-understanding/provenance-map-v0.md` defines the PR60
  `lolla.provenance_map.v0` artifact-lineage shape before any exporter,
  runtime integration, graph DB, memory, or compliance claim.
- `docs/evals/review-conflict-register-v0.md` defines the PR61
  `lolla.review_conflict_register.v0` human-review-owned conflict surface
  before any exporter, conflict resolution, severity automation, policy
  enforcement, scoring, labels, or judge.
- `docs/conversation-understanding/case-graph-export-v0.md` defines the PR62
  `lolla.case_graph.v0` future run-local case graph export/view shape before
  any exporter, archive reading, runtime integration, graph DB, memory,
  GraphRAG, entity resolution, scoring, labels, or judge.
- `docs/evals/accountability-view-fixtures-v0.md` defines the PR63 combined
  accountability-view fixture pack before any exporter, archive reading,
  runtime integration, graph DB, memory, GraphRAG, scoring, labels, or judge.
- `docs/evals/audit-decision-record-readonly-exporter-v0.md` documents the
  PR66 read-only `lolla.audit_decision_record.v0` exporter, which reads only
  structured/custody-safe artifacts, writes only an explicit external output
  file, and remains outside raw content, model calls, archive mutation, labels,
  scoring, judges, graph DB, memory, and runtime integration.
- `docs/evals/audit-decision-record-export-smoke-review-v0.md` documents the
  PR67 smoke review of PR66 exporter outputs and recommends a small
  schema/exporter refinement before archive integration, automatic generation,
  batch export, labels, scoring, judges, or runtime behavior.
- `docs/evals/audit-decision-record-schema-exporter-refinement-v0.md`
  documents the PR68 refinement that makes empty PR31 buckets and semantic
  arrays explicit non-claims without adding labels, scoring, judges, archive
  integration, automatic generation, or runtime behavior.
- `docs/evals/audit-decision-record-export-review-rerun-v0.md` documents the
  PR69 review re-run showing the refined PR68 output is clear enough for a
  future archive-integration decision gate, while still adding no integration,
  labels, scoring, judges, automatic generation, or runtime behavior.

Acceptance criteria:

- The methodology doc is linked from this PRD and `HOW_IT_WORKS.md`.
- The first taxonomy is versioned.
- Human review fields are defined.
- The PRD explicitly rejects generic helpfulness/coherence scoring as a release gate.

### R7: Deterministic Evaluation Artifact v0

Priority: P1
Owner area: eval/runtime/archive/Observatory

Add a post-run evaluation artifact focused first on deterministic and heuristic checks.

Tentative artifact:

`evaluation.json`

Minimum checks:

- Are required artifacts present?
- Do schemas validate?
- Did private ledgers cover selected material exactly once?
- Is public output free of internal machinery leakage?
- Are revised answer and memo both persisted?
- Is memo content consistent enough with the revised answer to avoid obvious divergence?
- Is run health consistent with the artifact state?

Heuristic checks may flag possible issues for review, such as missing action delta, absent gate language, or overlong/underdeveloped output. These should not be treated as final truth until validated through human error analysis.

Current shipped slice:

- Archived runs now generate `evaluation.json` with schema `lolla.evaluation.v0`.
- The v0 artifact checks deterministic run-readiness: required artifacts, schema versions, reasoning-trace custody, capture adequacy, extraction/provenance adequacy when `extraction_adequacy_report.json` is present, product/live hygiene states, provider-boundary policy consistency, caller-action conservatism, and archive readiness.
- It does not score advice quality, helpfulness, coherence, wisdom, or correctness.
- It does not yet add heuristic answer-quality checks, an Observatory evaluation page, a compact summary inside `agent_result.json`, or run-health degradation beyond existing health policy.

Full R7 acceptance remains broader than this shipped v0 receipt.

Acceptance criteria:

- Evaluation artifact is generated for `standard`, `deep`, and `high_stakes` modes.
- `agent_result.json` includes a compact evaluation summary.
- Observatory has an evaluation page or section.
- Product run health can degrade when deterministic evaluation finds severe inconsistency.
- Tests include at least one fixture where revised answer is missing, one where memo contradicts revised answer, and one where artifact state and run health disagree.

### R8: Calibrated Subjective Judges

Priority: P1
Owner area: eval/runtime/archive/Observatory

Add subjective Lolla judges only after the human-labeled taxonomy exists.

Judge checks should be binary and failure-mode-specific, for example:

- `earned_friction`
- `actionable_delta`
- `pressure_absorption`
- `constraint_preservation`
- `overcorrection_absent`
- `unsupported_claim_absent`
- `decision_usefulness`

Acceptance criteria:

- Each judge has a named dataset, prompt version, and calibration record.
- TPR and TNR are reported per failure mode, not only overall agreement.
- Judges are advisory until they meet agreed thresholds.
- The judge prompt explicitly states that useful discomfort is not failure and smoothness is not the target.
- At least one adversarial pairwise set is used to test smoothness bias.

### R9: Archive Corpus And Stability Workflow

Priority: P1
Owner area: archive/evals/scripts/docs

Make archived runs useful as an evaluation corpus, not just local receipts.

Build on existing `scripts/export_reasoning_trace_dataset.py` and `scripts/compare_archived_runs.py`.

Requirements:

- Export `agent_result.json` fields into JSONL.
- Include mode, run health, evaluation status, cost, model IDs, and product-output health.
- Include capture adequacy, provider-boundary status, optional control-plane references, and artifact availability without copying raw transcript or memo text.
- Carry blank human-review fields so reviewers can label runs later without the exporter performing the review.
- Support repeated-run grouping by conversation hash.
- Surface run-to-run variance in:
  - main counter-pressure,
  - changed advice summary,
  - selected model IDs,
  - evaluation verdict,
  - caller action.

Current shipped slice:

- `scripts/export_review_corpus.py` exports a deterministic JSONL run-envelope corpus plus a manifest from archived runs.
- The export includes compact `agent_result.json`, `evaluation.json`, capture adequacy, run-health, usage/model, artifact-availability, and optional control-plane summaries.
- The export includes a blank `lolla.human_review.v0` template per run, but does not fill labels, score advice quality, approve actions, or call a model.
- Each record includes `review_readiness_tier`, `content_review`,
  `custody_review`, and `batch_recommendation` fields so reviewers can separate
  full modern custody runs from legacy content-only archives.
- `scripts/export_reasoning_trace_dataset.py` remains available for lower-level reasoning-trace/lens analysis.

Acceptance criteria:

- One command exports a local corpus.
- One command compares repeated runs for the same conversation hash.
- Output is safe to share after raw transcript exclusion, or clearly marked unsafe if it includes sensitive text.

### R10: Observatory Parity

Priority: P1
Owner area: Observatory/frontend/docs

Observatory should show every major artifact the system asks users or agents to trust.

Add or verify views for:

- agent result,
- risk mode,
- evaluation artifact,
- capture adequacy,
- product-output health,
- live-output health,
- run-event timeline,
- model-call/cost summary,
- external trace/control metadata when present,
- archive completeness,
- graph-survival/ledger uptake.

Acceptance criteria:

- A user can click through a completed archived run and answer:
  - What changed?
  - Why did it change?
  - What was private consideration only?
  - What failed or degraded?
  - What did this cost?
  - Can an agent safely use this run?

### R11: Human Capability Surface

Priority: P2
Owner area: memo/product/docs

Add an optional, compact section to the memo or Observatory:

`What To Learn From This Audit`

Purpose:

- help the user recognize the reasoning pattern next time,
- avoid making Lolla feel like a black-box oracle,
- support long-term human judgment rather than only answer correction.

Acceptance criteria:

- Default chat output remains concise.
- Memo section is short and practical.
- No model-name dumping.
- Can be disabled or omitted in `quick` mode.

### R12: Public Docs Update

Priority: P0
Owner area: docs

Update public docs so collaborators understand the direction:

- `docs/lolla-pitch-and-invitation.md`: add a paragraph explaining Lolla as a harness layer, not a prompt pack.
- `HOW_IT_WORKS.md`: link this PRD, the eval methodology, and the control-layer integration note, and clarify that this is roadmap, not current runtime behavior.
- Optional: add a short "For Agent Builders" section.

Acceptance criteria:

- Docs distinguish current behavior from proposed roadmap.
- No claim that evaluation layer exists before it ships.
- Sources are listed.

## Non-Functional Requirements

### Traceability

Every artifact used by agent-facing output must have a pointer in archive or `reasoning_trace.json`.

### Interoperability

External control-plane metadata should be optional, vendor-neutral, and preserved without making ordinary `$lolla` runs depend on a framework, proxy, approval system, sandbox, or hosted trace provider.

### Backward Compatibility

Existing `$lolla` human flow should keep working. New files should be additive unless a migration PR explicitly changes the contract.

### Local Privacy

No hosted upload. No default external archive sync. Export commands must make raw transcript inclusion explicit.

### Graceful Degradation

If evaluation fails, artifact generation should not erase the run. It should mark the run degraded and explain why.

### Public Surface Hygiene

Agent-facing summaries and user-facing prose must avoid private machinery terms unless the user explicitly opens Observatory or artifact docs.

### Cost Visibility

Any mode that adds model calls must record incremental cost in `usage_summary`.

## Suggested PR Sequence

### PR 1: Add The Agent Result Contract

Scope:

- Generate `agent_result.json` from existing `result.json`, memo path, archive path, and run health.
- Archive it.
- Add schema docs and tests.

Why first:

- It gives agents a stable handoff without changing the audit pipeline.

Acceptance:

- Existing standard run produces valid `agent_result.json`.
- Partial run produces `caller_action: "do_not_use_run_degraded"` or equivalent.

### PR 2: Add Risk Mode Metadata

Scope:

- Add `LOLLA_AUDIT_MODE` or CLI flag.
- Persist mode through result, agent result, reasoning trace, archive metadata, and run-event metadata.
- Explicit Observatory UI surfacing is deferred to the Observatory parity PR.
- No audit behavior changes: no prompt, cost, Step 7, high-stakes policy, eval, capture, or replay changes.

Why second:

- Establishes the product language before expensive behavior changes.

Acceptance:

- `$lolla` remains `standard`.
- Test fixtures verify mode propagation.

### PR 3: Agent Trigger Policy Docs

Scope:

- Add docs for when agents should call Lolla.
- Include examples.
- Link from pitch and HOW_IT_WORKS.

Why third:

- Makes the product legible to external builders before adding deeper mechanics.

Acceptance:

- Docs distinguish trigger policy from runtime enforcement.

### PR 4: Control-Plane Integration Contract

Scope:

- Define `lolla_control_input.v1` and `lolla_control_result.v1` as optional wrappers around the core agent result.
- Add optional external trace/control fields to `agent_result.json`.
- Document `caller_action` mappings for approval systems.
- Link the control-layer integration note from public docs.

Implementation status: v0 sidecar contract exists. External callers can stage
`/tmp/lolla_<run_id>_control_input.json`; archive generation preserves it,
adds compact control references to `agent_result.json` / `reasoning_trace.json`,
and writes `control_result.json` plus a `/tmp` convenience copy. Ordinary
`$lolla` runs are unaffected when no control input is supplied.

Why fourth:

- Gives future agent frameworks, approval systems, proxies, sandboxes, and trace pipelines a stable place to attach Lolla without changing the audit pipeline yet.

Acceptance:

- Ordinary `$lolla` runs do not require external metadata.
- Supplied trace/action/approval metadata is preserved in artifacts and archive.
- Docs explain that Lolla complements control layers rather than replacing them.

### PR 5: Eval Methodology And Human Review Pack

Scope:

- Add or refine `docs/lolla-evaluation-methodology.md`.
- Create a first review sheet/export format for archived runs.
- Define human review fields: pass/fail, first upstream failure, failure mode, critique, useful friction/missing friction/noisy friction, and agent-safe action.
- Create the initial Lolla failure taxonomy.

Why fifth:

- Prevents us from building a generic LLM judge that rewards smoothness.

Acceptance:

- At least 50 archived or fixture traces can be exported for review.
- Taxonomy is versioned and linked from the PRD.
- Docs explicitly reject generic helpfulness/coherence scoring as a release gate.

### PR 6: Deterministic Evaluation Artifact v0

Scope:

- Generate `evaluation.json` after memo render.
- Run deterministic checks for artifact custody, schemas, ledgers, public-surface hygiene, revised answer persistence, memo persistence, and run-health consistency.
- Include compact summary in `agent_result.json`.

Why sixth:

- Starts closing the observability-evaluation gap without pretending a broad judge is trustworthy.

Acceptance:

- Severe missing revised answer, memo mismatch, invalid ledger, or false-clean health degrades run health.
- Observatory can display evaluation summary or raw artifact link.

### PR 7: Calibrated Subjective Judge Prototype

Scope:

- Build one binary Lolla-specific judge after human labels exist.
- Start with one failure mode, probably `actionable_delta` or `earned_friction`.
- Use train/dev/test split and report TPR/TNR.
- Include adversarial smoothness-bias pairs.

Why seventh:

- Tests whether LLM judges can be useful without letting them reward blandness.

Acceptance:

- Judge is advisory unless calibration threshold is met.
- Judge prompt and dataset version are recorded.
- False positives and false negatives are reviewed.

### PR 10: Capture Adequacy Manifest Upgrade

Scope:

- Add compact deterministic capture adequacy metadata.
- Record omitted middle-turn windows and risk flags before changing capture strategy.
- Degrade or fail only on deterministic capture-shape problems.

Why now:

- Evaluation is only as good as capture. Do this after the first eval artifact exists.

Acceptance:

- Long-conversation fixture records omitted middle windows.
- `result.run_health`, `agent_result.json`, `reasoning_trace.json`, and `evaluation.json` surface capture adequacy.
- Omitted ranges are explicit.

### PR 9: Stability And Corpus Export

Scope:

- Extend dataset export to include `agent_result.json` and `evaluation.json`.
- Group by conversation hash.
- Compare repeated runs.

Why ninth:

- Turns archived runs into a learning corpus.

Acceptance:

- One command exports corpus.
- One command produces stability summary for repeated runs.

### PR 10: Mode Behavior

Scope:

- Make `quick`, `deep`, `high_stakes`, and `stability` modes actually alter behavior.
- Keep changes conservative.

Candidate behavior:

- first add contract-lock tests for current high-stakes conservative behavior;
- `quick`: skip optional expensive eval checks.
- `deep`: enable optional Step 7.
- `high_stakes`: stricter warning, stricter capture/eval, stronger unsupported-domain handling.
- `stability`: repeated-run comparison or archive replay.

Acceptance:

- Cost impact visible.
- Mode behavior documented.
- Existing standard mode remains stable.

### PR 11: Human Capability Section

Scope:

- Add optional "What To Learn From This Audit" memo/Observatory section.

Why later:

- Valuable, but should not precede agent contract and evaluation.

Acceptance:

- No public machinery leak.
- Section is short and actionable.

## Milestones

### Milestone A: Agent-Callable Harness Skeleton

Includes:

- PR 1,
- PR 2,
- PR 3,
- PR 4.

Definition of done:

- A local agent can run Lolla and consume `agent_result.json`.
- Risk mode is present as metadata.
- Docs explain when to call Lolla.
- Optional external trace/action/approval metadata can be preserved for future control-plane integrations.

### Milestone B: Evaluation Begins

Includes:

- PR 5,
- PR 6,
- PR 7.

Definition of done:

- Lolla has a human-reviewed failure taxonomy.
- Lolla can run deterministic evaluation checks over completed runs.
- At least one subjective judge has been prototyped and calibrated, or explicitly rejected because it failed calibration.

### Milestone C: Learning From Runs

Includes:

- PR 8,
- PR 9,
- PR 10.

Definition of done:

- Capture adequacy is visible and stricter for long conversations.
- Archived runs can become an eval corpus.
- Repeated-run stability can be inspected.
- Modes change behavior in controlled ways.

### Milestone D: Human Judgment Support

Includes:

- PR 11.

Definition of done:

- Lolla helps the user learn from the audit, not only consume the revised answer.

## Metrics

### Product Metrics

- Percentage of completed runs with valid `agent_result.json`.
- Percentage of runs with clean or partial run health.
- Percentage of runs where `position_changed` is true.
- Percentage of high-pressure audits where revised answer shows material shift.
- Number of runs where eval flags "audit acknowledged but no real change."
- Number of runs where eval flags overcorrection.
- Number of runs where useful friction is present, missing, or noisy according to human review.
- Percentage of externally supplied trace/action/approval metadata preserved in archive artifacts.

### Quality Metrics

- Capture adequacy rate for long conversations.
- Quote/provenance validation failures.
- Memo/revised-answer consistency failures.
- Run-to-run stability for repeated conversations.
- Product-output hygiene failures.
- Live-output hygiene failures.
- Failure taxonomy coverage across reviewed traces.
- Judge TPR/TNR by failure mode.
- Smoothness-bias adversarial-pair pass rate.

### Operational Metrics

- Cost by mode.
- Boundary call count by mode.
- Model provider mismatch rate.
- Deterministic evaluation failure rate.
- Subjective judge calibration status.
- Archive completeness rate.
- External control metadata preservation failures.

### Human Usefulness Metrics

Later, optionally:

- User marks revised answer useful/not useful.
- User marks memo shareable/not shareable.
- User says decision changed, clarified, or stayed the same.
- Follow-up review: did the run help after the decision played out?

## Risks And Mitigations

### Risk: Lolla Becomes Too Heavy

Mitigation:

- Keep `standard` mode close to current behavior.
- Make expensive checks mode-gated.
- Keep `quick` mode cheap.

### Risk: Evaluation Creates False Certainty

Mitigation:

- Label evaluation as an audit artifact, not proof.
- Record severity and uncertainty.
- Do not make a single evaluator verdict the only gate.
- Require human-labeled calibration before subjective judges become blocking.

### Risk: Judges Reward Blandness

Mitigation:

- Do not use generic helpfulness, coherence, or broad preference scores as release gates.
- Use Lolla-specific binary checks such as `earned_friction`, `actionable_delta`, and `overcorrection_absent`.
- Include adversarial pairs where the smoother answer is worse than the rougher but more decision-protective answer.
- Treat judge-palatable blandness as a judge failure, not a Lolla success.

### Risk: Agent Result Hides Too Much

Mitigation:

- Keep compact result for agents.
- Preserve full artifact pointers.
- Observatory remains the inspection surface.

### Risk: Capture Upgrade Adds Complexity

Mitigation:

- Add manifest first.
- Keep chronological fallback.
- Use fixtures before changing default truncation behavior.

### Risk: High-Stakes Mode Looks Like Domain Assurance

Mitigation:

- Explicitly say high-stakes mode is stricter reasoning hygiene, not legal/medical/financial validation.
- Use `unsupported_high_stakes_domain` when needed.
- Keep PR36's distinction between answer improvement, run readiness, and action
  approval.
- Use PR37 fixtures before changing runtime behavior.

### Risk: More Modes Confuse Users

Mitigation:

- Default remains `standard`.
- Human command can stay simple.
- Modes are mainly for agent/tool callers and explicit power-user requests.

### Risk: Control-Plane Integration Overclaims Safety

Mitigation:

- State explicitly that Lolla is a reasoning-quality layer, not a network firewall, sandbox, identity broker, or approval authority.
- Preserve external control decisions as context, not as proof that the run is safe.
- Use `caller_action` to advise the caller, while the caller's policy engine remains responsible for enforcement.

## Open Questions

1. Should `agent_result.json` be produced before or after archive path finalization? Answer for v1: archive-time generation writes both the archived file and `/tmp/lolla_<run_id>_agent_result.json`; earlier pre-archive generation remains a possible future addition if a caller needs it.
2. Which 4 to 6 failure modes should become the first official Lolla taxonomy after open coding archived runs?
3. Should high-stakes mode block certain domains or only warn?
4. Should risk mode be selected by the caller, inferred by extraction, or both?
5. Which external integration target should come first: OpenAI Agents SDK approvals, LangGraph interrupts, CrabTrap audit logs, LiteLLM tool permissions, or Langfuse/Braintrust traces?
5. How much of the revised answer should appear in `agent_result.json` versus only in memo/artifact pointers?
6. Should stability mode rerun the pipeline automatically or only compare existing archived runs?
7. What minimal eval signal is strong enough to affect `run_health`?
8. Should user usefulness review live inside Observatory or as a separate optional artifact?
9. Who is the principal reviewer whose Lolla taste calibrates early subjective judges?
10. Which judge failures should be advisory, and which should become release blockers?

## Decision Log

### 2026-06-24

- Decision: Treat Lolla's next product step as a reasoning-audit harness, not a larger prompt.
- Decision: Prioritize `agent_result.json` before deeper evaluation, because agents need a stable handoff first.
- Decision: Implement `agent_result.json` as an archive-time additive artifact first, without changing the audit pipeline, risk-mode behavior, or control-plane wrappers.
- Decision: Keep Step 7 default-off. Deeper review belongs behind explicit mode or user request.
- Decision: Treat evaluation as the main frontier after observability, but start with error analysis and deterministic checks rather than a generic LLM judge.
- Decision: Lolla evals must reward earned, actionable friction rather than smoothness.
- Decision: Keep all new behavior local-first and additive.

## Appendix: Architecture Lesson From The Claude Code Paper

The Claude Code design-space paper argues that production agents often use a simple model loop surrounded by dense deterministic infrastructure. The LLM handles local judgment. The harness handles permissions, context, tools, recovery, persistence, and auditability.

Lolla should apply the same pattern to reasoning quality.

In Lolla:

- The LLM reads the conversation and writes the revised answer.
- The pipeline routes through calibrated audit prompts and curated substrate.
- Deterministic code validates custody, ledgers, artifacts, health, telemetry, archive, and replay.
- Future evaluation should check whether the revised answer actually improved.

That is the durable direction: not more mystique around the model, more discipline around the loop.
