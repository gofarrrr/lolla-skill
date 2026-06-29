# Lolla Progress Report

Status: Living PM report
Last updated: 2026-06-28

This file tracks where Lolla stands against the big-picture product direction in
`docs/lolla-reasoning-audit-harness-prd.md`.

Use it after each PR to answer four questions:

1. What changed?
2. Which PRD item did it move?
3. What did it deliberately not change?
4. Did it preserve the product boundary?

## Big-Picture Anchor

Lolla is evolving from a human-triggered skill into a local, inspectable,
agent-callable reasoning-audit harness.

Core thesis:

> Lolla lets LLMs do semantic judgment, but surrounds that judgment with
> deterministic custody: fixed steps, structured artifacts, validation gates,
> run health, telemetry, archive, replay, and eventually evaluation.

Product boundary:

> Lolla asks whether the reasoning that led to an answer or action deserves
> trust.

Lolla is not:

- a generic guardrail,
- a sandbox,
- an HTTP proxy or firewall,
- an identity broker,
- a policy engine,
- a domain expert,
- a fact-checking engine,
- a naive LLM judge.

The practical product loop we are improving first:

```text
call Lolla manually
-> produce revised answer and memo
-> archive the run
-> inspect health, trace, and custody
-> decide what to trust
```

The broader harness loop remains:

```text
conversation or agent run
-> reasoning audit
-> machine-readable result
-> risk/mode metadata
-> local artifact custody
-> evaluation
-> optional control-plane integration
```

## Fresh-Session Handoff: 2026-06-29

Current handoff state:

```text
PR63 Accountability View Fixture Pack v0 is the
latest completed accountability slice recorded in this file. PR48 remains the
high-stakes evidence gate. PR54 remains the paused v0 values/priorities
worksheet gate. Use git log for the exact current commit hash.
```

Current product state:

> Lolla now has the local reasoning-audit harness skeleton, deterministic run
> custody, evaluation receipts, review-corpus scaffolding, extraction adequacy
> reporting, semantic coverage reporting, offline specialist probe evidence,
> a clean six-case complex conversation baseline, and a first human/product
> review seed over those six complex runs. The risk-mode track now has policy,
> fixtures, fixture review, a pre-code implementation plan, contract-lock tests,
> deterministic evaluation-artifact clarity for high-stakes reliance, and a
> review-corpus surface and manifest counts for that reliance caveat. PR45 adds
> a compact anti-drift handoff so fresh sessions do not confuse fixture-backed
> readiness with real high-stakes archive evidence. PR46 adds the docs-only
> approval and custody plan for creating high-stakes evidence later without
> running cases now. PR47 adds paraphrase-only fixtures so reviewers can test
> high-stakes expectations before real runs exist. PR48 adds the read-only
> manifest analyzer that says whether a review-corpus manifest actually contains
> high-stakes reliance-present archive evidence. PR49 through PR54 complete
> the v0 user-values/priorities worksheet lane as a human-owned review surface
> and pause it before extraction, runtime integration, automatic labels, memory,
> or judging. PR55 lands the Semantica-inspired accountability PRD as a
> docs-only plan: borrow accountability primitives, not Semantica's graph,
> memory, policy, compliance, judge, or scoring platform. PR56 adds the
> docs-only Lolla Doctor / Preflight plan for a future read-only, local,
> deterministic, model-call-free readiness command. PR57 implements that
> command as a read-only local CLI without running `$lolla`, calling models,
> mutating archives, or approving high-stakes use. PR58 designs
> `lolla.audit_decision_record.v0` as a paraphrase-only accountability
> projection over existing artifacts and PR31 labels without implementing an
> exporter, judge, score, memory layer, or conversation-understanding IR. PR59
> reviews six paraphrase-only decision-record fixtures and finds the shape
> understandable enough for a future exporter design prototype, with no
> exporter, runtime integration, automatic labels, scoring, or judge. PR60
> designs `lolla.provenance_map.v0` as a local artifact-lineage map without
> implementing an exporter, archive reading, runtime integration, RDF/W3C
> compliance, graph DB, memory, labels, scoring, or judge. PR61 designs
> `lolla.review_conflict_register.v0` as a human-review-owned conflict surface
> without conflict resolution, severity automation, policy enforcement,
> labels, scoring, or judge. PR62 designs `lolla.case_graph.v0` as a future
> run-local case graph export/view shape without implementing an exporter,
> reading archives, adding graph DB, adding memory, adding GraphRAG, adding
> entity resolution, labels, scoring, or judge. PR63 adds three
> paraphrase-only accountability-view fixture bundles across audit decision
> record, provenance map, review conflict register, and case graph views, with
> no exporter, archive reading, runtime behavior, labels, scoring, or judge.

What this means in plain terms:

- Normal `$lolla` is still the product surface.
- The current harness can capture a serious conversation, extract decision
  structure, run the audit, produce a revised answer and memo, archive the run,
  emit `agent_result.json`, `evaluation.json`, `reasoning_trace.json`, and
  expose deterministic health/custody signals.
- The six complex test conversations all completed with full 12-user /
  12-assistant capture, healthy run state, clean provider-boundary state, clean
  product output, zero quote-fabrication, and `caller_action:
  use_revised_answer`.
- The revised answers were not just smoother. They repeatedly changed action
  shape: added gates, narrowed claims, corrected over-clean frames, exposed
  capacity and stakeholder constraints, and rejected checklist theater.
- Risk-mode implementation is test-locked at the contract level,
  `evaluation.json` surfaces high-stakes reliance caveats explicitly, and
  review-corpus records now expose those caveats as compact
  `risk_mode_reliance` metadata. PR43 verified the surface with fixtures after
  a read-only local export found zero real high-stakes reliance-present archive
  records. PR44 now adds manifest-level aggregate visibility for that absence
  without runtime enforcement.
- The current real local review-corpus evidence is 80 records, all
  `risk_mode: standard`; `risk_mode_reliance_present_counts` is `false: 80` and
  `true: 0`.
- PR46 defines allowed, excluded, and domain-review-required high-stakes
  scenario categories for a future approved seed, but it does not create any
  real high-stakes records.
- PR47 adds six paraphrase-only high-stakes evidence fixtures; they are not
  archive outcome evidence, human labels, judge calibration truth, or runtime
  enforcement.
- PR48 reads only review-corpus manifest JSON and reports
  `no_high_stakes_reliance_evidence`, `has_high_stakes_reliance_evidence`, or
  `insufficient_manifest_fields`; it does not read raw archives, call models,
  judge answer quality, or approve real high-stakes runs.
- PR49 through PR54 complete the v0 user-values/priorities worksheet lane as a
  human-owned review surface: plan, fixtures, fixture review, blank export,
  human pilot, and pilot review. That lane is now paused before extraction,
  runtime integration, automatic labels, memory, or judging.
- PR55 records the Semantica-inspired accountability plan. It preserves a queue
  for local decision records, provenance maps, review conflict registers,
  doctor/preflight, and run-local case graph views while explicitly rejecting
  graph DBs, embeddings, chunking, global memory, policy engines, compliance
  platforms, generic agent safety layers, domain authority, LLM judges,
  answer-quality scoring, automatic labels, and runtime behavior changes.
- PR56 records the Lolla Doctor / Preflight plan. It defines a future
  read-only doctor report for local runtime discovery, archive-root discovery,
  helper script availability, provider/cost readiness, review-manifest
  visibility, high-stakes evidence absence/presence, output-path safety, and
  privacy-safe reporting without adding the CLI.
- PR57 implements the smallest read-only doctor CLI and JSON contract. It
  checks local runtime wiring, archive-root shape, helper availability,
  provider credential presence, cost-table readiness, optional review-corpus
  manifest counts, high-stakes evidence visibility, output-path safety,
  repo/runtime boundary state, and privacy flags without running `$lolla`,
  calling models, or mutating archives.
- PR58 designs `lolla.audit_decision_record.v0` as a local accountability
  projection over existing artifacts. It summarizes the audited decision,
  original/revised recommendation shape, PR31 actionable deltas, unresolved
  conflicts/questions, source artifact refs, review refs, custody flags, and
  limitations without copying raw content or judging answer quality.
- PR59 creates six paraphrase-only audit decision record fixtures and a
  human-owned fixture review. All six pass, PR31 mapping is useful in all six,
  reviewer use without raw content is `yes` in all six, and the review marks
  the shape ready for a future read-only exporter design prototype with
  caveats.
- PR60 designs `lolla.provenance_map.v0` as a local artifact-lineage map across
  run and review artifacts. It borrows entity/activity/agent vocabulary without
  claiming PROV-O/W3C compliance, requiring RDF, adding graph DB, adding memory,
  implementing an exporter, reading archives, or judging answer quality.
- PR61 designs `lolla.review_conflict_register.v0` as a human-review-owned
  register of unresolved values, stakeholder, action, reliance, artifact,
  provenance, and review conflicts. It preserves conflicts for review without
  resolving them, scoring severity into actions, enforcing policy, or creating
  labels.
- PR62 designs `lolla.case_graph.v0` as a future run-local case graph
  export/view shape. It shows how decision, delta, artifact, provenance,
  conflict, doctor, and review nodes can relate without implementing an
  exporter, reading archives, adding graph DB, memory, GraphRAG, entity
  resolution, labels, scoring, or judging.
- PR63 creates three accountability-view fixture bundles from checked-in
  reviewed summaries. Each bundle includes audit decision record, provenance
  map, review conflict register, and case graph views, but remains
  paraphrase-only docs/JSON with placeholder hashes and relative artifact refs.

Primary evidence notes to read first in a fresh session:

- `docs/conversation-understanding/complex-conversation-baseline-v0.md`
- `docs/evals/complex-baseline-human-review-v0.md`
- `docs/evals/evaluation-flywheel-action-plan-v0.md`
- `docs/evals/current-system-capabilities-v0.md`
- `docs/evals/current-state-anti-drift-handoff-v0.md`
- `docs/evals/high-stakes-evidence-seed-plan-v0.md`
- `docs/evals/high-stakes-evidence-fixtures-v0.md`
- `docs/evals/high-stakes-evidence-fixtures-v0.json`
- `docs/evals/review-corpus-evidence-readiness-v0.md`
- `docs/evals/user-values-priorities-worksheet-plan-v0.md`
- `docs/evals/user-values-priorities-worksheet-fixtures-v0.md`
- `docs/evals/user-values-priorities-worksheet-fixture-review-v0.md`
- `docs/evals/user-values-priorities-blank-worksheet-export-v0.md`
- `docs/evals/user-values-priorities-worksheet-human-pilot-v0.md`
- `docs/evals/user-values-priorities-pilot-review-v0.md`
- `docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`
- `docs/conversation-understanding/audit-decision-record-v0.md`
- `docs/conversation-understanding/audit-decision-record-v0.json`
- `docs/evals/audit-decision-record-fixtures-v0.md`
- `docs/evals/audit-decision-record-fixtures-v0.json`
- `reviews/human/audit-decision-record-fixture-review-v0/review.json`
- `docs/conversation-understanding/provenance-map-v0.md`
- `docs/conversation-understanding/provenance-map-v0.json`
- `docs/evals/review-conflict-register-v0.md`
- `docs/evals/review-conflict-register-v0.json`
- `docs/conversation-understanding/case-graph-export-v0.md`
- `docs/conversation-understanding/case-graph-export-v0.json`
- `docs/evals/accountability-view-fixtures-v0.md`
- `docs/evals/accountability-view-fixtures-v0.json`
- `docs/evals/lolla-doctor-preflight-plan-v0.md`
- `docs/evals/lolla-doctor-readonly-cli-v0.md`
- `engine/system_b/lolla_doctor.py`
- `scripts/lolla_doctor.py`
- `tests/test_lolla_doctor.py`
- `reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json`
- `reviews/human/user-values-priorities-pilot-review-v0/review.json`
- `engine/system_b/review_corpus_evidence_readiness.py`
- `scripts/analyze_review_corpus_evidence_readiness.py`
- `tests/test_review_corpus_evidence_readiness.py`
- `docs/conversation-understanding/broader-specialist-evidence-gate-v0.md`
- `docs/conversation-understanding/specialist-runtime-design-without-integration-v0.md`
- `docs/conversation-understanding/research-and-design-v0.md`
- `docs/lolla-evaluation-methodology.md`
- `docs/lolla-reasoning-audit-harness-prd.md`
- `docs/evals/risk-mode-implementation-plan-v0.md`
- `tests/test_risk_mode_contract.py`
- `tests/test_evaluation_artifact.py`
- `tests/test_review_corpus_export.py`

Current stop rule:

> Do not run more random smokes by default. We have enough complex-run evidence
> to pause and turn toward evaluation.

Latest completed slice:

```text
PR63 Accountability View Fixture Pack v0
```

Result:

- lands `docs/evals/accountability-view-fixtures-v0.md` and
  `docs/evals/accountability-view-fixtures-v0.json`;
- creates three fixture bundles for `launch-public-enterprise-beta`,
  `deploy-assisted-intake-routing`, and `ceo-remove-founding-cofounder`;
- includes all four accountability views per fixture:
  `audit_decision_record`, `provenance_map`, `review_conflict_register`, and
  `case_graph`;
- keeps every fixture paraphrase-only, with safe custody flags, relative
  artifact refs, and placeholder hashes only;
- recommends PR64 Accountability View Fixture Review v0 as the next
  docs/eval-only evidence gate before any implementation decision.

Stop point:

```text
Do not start real high-stakes run work without explicit maintainer approval.
PR48 remains the high-stakes evidence gate.
The separate user-values/priorities lane is now paused at PR54 unless a later
implementation gate is explicitly approved.
PR63 only creates paraphrase-only accountability-view fixtures. Do not
implement an exporter, runtime integration, archive-reading behavior, graph DB,
embeddings, memory, GraphRAG, entity resolution, conflict resolution, severity
automation, policy enforcement, labels, scoring, judging, or any other
accountability primitive from PR63 alone. The next slice is PR64 fixture review,
not implementation.
```

The broader action map for this next phase is:

`docs/evals/evaluation-flywheel-action-plan-v0.md`

Non-goals for the next slice:

- no generic LLM judge;
- no answer-quality score;
- no automatic human-review labels;
- no approved high-stakes run batch without explicit product approval;
- no prompt rewrite;
- no runtime behavior change unless explicitly scoped as a later phase;
- no `SKILL.md` change;
- no quote-validation repair;
- no specialist runtime/archive integration;
- no `conversation_understanding_ir.v0`;
- no graph DB, embeddings, chunking, or memory layer.
- no Semantica-style policy engine, compliance platform, generic agent safety
  layer, domain authority, answer-quality score, automatic labels, LLM judge, or
  PR58+ implementation.

## PRD Checkpoint: Built, Missing, Opportunities

### Built

- [x] Agent-facing result contract: `agent_result.json` /
  `lolla_agent_result.v1`.
- [x] Risk-mode metadata propagation.
- [x] Optional control-plane sidecars: `control_input.json` /
  `control_result.json`.
- [x] Capture adequacy metadata and evaluation checks.
- [x] Deterministic `evaluation.json` run-readiness receipt.
- [x] Reasoning trace custody and archive artifact indexing.
- [x] Observatory custody parity for current/archived sidecars.
- [x] Provider-boundary classification and signature-only metadata filtering.
- [x] Review corpus export with local-only scope and blank human-review fields.
- [x] Human-review taxonomy and workflow v0.
- [x] Synthetic-review boundary, prompt, and validator.
- [x] Review-readiness tiers.
- [x] Extraction adequacy report, corpus export, findings drilldown, and quote
  validation diagnostics.
- [x] Modern quote-validation baseline: no runtime quote repair justified.
- [x] Semantic coverage report and corpus survey.
- [x] Specialist extractor fake-boundary and real-boundary probe harnesses.
- [x] Broader mixed-custody specialist evidence gate.
- [x] Six clean complex conversation baseline.
- [x] PR30 human/product review seed over the six complex baseline runs.
- [x] PR31 actionable-delta rubric.
- [x] PR32 adversarial pair fixture seed set.
- [x] PR33 broader human-review corpus batch.
- [x] PR34 first-class user-values/priorities design.
- [x] PR35 live-output hygiene decision.
- [x] PR36 risk-mode behavior plan.
- [x] PR37 risk-mode fixture matrix.
- [x] PR38 risk-mode fixture review.
- [x] PR39 risk-mode implementation plan.
- [x] PR40 risk-mode contract-lock tests.
- [x] PR41 risk-mode evaluation-artifact clarity.
- [x] PR42 risk-mode review-surface integration.
- [x] PR43 fixture-backed risk-mode reliance review batch.
- [x] PR44 review-corpus reliance manifest counts.
- [x] PR45 current-state anti-drift handoff.
- [x] PR46 approved high-stakes evidence seed plan.
- [x] PR47 high-stakes evidence fixture pack.
- [x] PR48 review-corpus evidence readiness analyzer.
- [x] PR49 user-values/priorities worksheet plan.
- [x] PR50 user-values/priorities worksheet fixture pack.
- [x] PR51 user-values/priorities worksheet fixture review.
- [x] PR52 user-values/priorities blank worksheet export.
- [x] PR53 user-values/priorities worksheet human pilot.
- [x] PR54 user-values/priorities pilot review / v0 decision.
- [x] PR55 Semantica-inspired accountability PRD / comparative architecture
  note.
- [x] PR56 Lolla Doctor / Preflight plan.
- [x] PR57 Lolla Doctor Read-Only CLI.
- [x] PR58 Audit Decision Record Design.
- [x] PR59 Audit Decision Record Fixture Review.
- [x] PR60 Provenance Map Design.
- [x] PR61 Review Conflict Register Design.
- [x] PR62 Case Graph Export Design.
- [x] PR63 Accountability View Fixture Pack.
- [x] Current system capabilities explainer, grounded in recorded cases.
- [x] Public pitch/docs refreshed around Lolla as a reasoning-audit harness.

### Missing / Not Done

- [ ] Human labels on 50-100 archive/corpus records.
- [ ] Calibrated binary subjective judges.
- [ ] Agent trigger-policy docs for external builders.
- [ ] Behavioral risk-mode enforcement; PR36 is design-only, PR37 is fixture
  work, PR38 is fixture review, PR39 is a pre-code implementation plan, PR40 is
  a contract-lock test slice, PR41 only clarifies `evaluation.json`, PR42 only
  exposes that caveat in review-corpus records, PR43 only validates reviewer
  interpretation with fixtures, PR44 only adds manifest counts, PR45 only
  documents the current state, PR46 only plans future approved high-stakes
  evidence, PR47 only adds paraphrase-only high-stakes evidence fixtures, PR48
  only analyzes review-corpus manifests for evidence readiness, PR49 only
  plans a human values/priorities worksheet, PR50 only adds paraphrase-only
  worksheet fixtures, PR51 only reviews those fixtures, PR52 only creates blank
  deterministic worksheet structure, and PR53 only pilots human-filled
  worksheets from already-reviewed summaries. PR54 only reviews that pilot and
  pauses the lane at v0 for human-owned review.
  Current pipeline behavior is still mostly metadata-first.
- [ ] Decision-aware capture for long conversations and middle-turn hinges.
- [ ] First-class user-values/priorities extraction or offline report; PR34 is
  design-only, PR49 is worksheet planning only, PR50 is fixture-only, PR51 is
  fixture-review-only, PR52 is blank-template-only, and PR53 is
  human-pilot-only. PR54 is pilot-review-only and explicitly pauses before
  extraction or runtime integration.
- [ ] Span-grounded runtime/archive semantic coverage.
- [ ] Runtime or archive integration for specialist extractors.
- [ ] `conversation_understanding_ir.v0` or persisted conversation-understanding
  projection.
- [ ] Semantica-inspired accountability primitives beyond the first safe
  surfaces. PR55 is the docs-only accountability roadmap, PR56 is the docs-only
  doctor/preflight plan, PR57 implements only the read-only doctor CLI, PR58
  designs only `lolla.audit_decision_record.v0`, and PR59 only reviews
  paraphrase-only decision-record fixtures. PR60 designs only
  `lolla.provenance_map.v0`; PR61 designs only
  `lolla.review_conflict_register.v0`; PR62 designs only
  `lolla.case_graph.v0`; PR63 only creates paraphrase-only accountability-view
  fixtures; no decision-record exporter, provenance exporter,
  conflict-register exporter, case-graph exporter, graph DB, memory, GraphRAG,
  or runtime integration is implemented.
- [ ] Live-output hygiene implementation beyond conservative `not_checked`;
  PR35 is decision-only.
- [ ] Run-to-run stability workflow for repeated conversations.
- [ ] Optional human capability surface: "What To Learn From This Audit."
- [ ] Selected archived dashboard render/readback stabilization beyond the
  custody-panel bridge.

### Opportunities To Make The Machine Work Better

1. **Approved high-stakes evidence seed, only with explicit approval.** PR44
   makes the current absence visible and PR48 makes the readiness read explicit;
   real high-stakes reliance-present archive evidence should be created only
   from approved cases, not by default.
2. **User-values/priorities worksheet v0 is paused after review.** PR34 designs the signal,
   PR49 plans the human worksheet, PR50 adds paraphrase-only fixtures, PR51
   reviews those fixtures, PR52 creates blank worksheet structure, and PR53
   pilots four human-filled local review worksheets. PR54 reviews that pilot,
   marks the v0 worksheet surface complete for human-owned review, and pauses
   before any populated extraction, automatic label, runtime integration,
   memory, or judge.
3. **PR64 Accountability View Fixture Review v0.** PR63 now creates three
   combined accountability-view fixtures. The next slice should review whether
   those bundles help human/product review and which view, if any, deserves a
   later implementation decision. It must remain docs/eval-only and must not
   add exporters, runtime integration, graph DB, memory, GraphRAG, answer
   scoring, or automatic labels.
4. **Live-output hygiene implementation.** PR35 keeps `not_checked` honest and
   defines a trusted-transcript path; later work can implement only when needed.
5. **Span-grounded semantic enrichment.** Existing specialists help with live
   constraints, dropped threads, and stance lineage, but integration remains
   blocked until a clean 15-20 full-modern sample and provider-boundary behavior
   are settled.
6. **Human capability surface.** Later, add a compact memo/Observatory section
   that teaches the user what reasoning pattern the audit caught.

## Current Pause: Specialist Integration Track

Status: paused as of `origin/main`
`43e15841a88b114c3186dc6b55f1f9bc322d7863`.

Product read:

> Existing specialists are useful as an offline/deep-review direction, but
> runtime and archive integration remain blocked.

What the evidence now says:

- PR29B showed the existing specialists can improve semantic coverage on four
  full-modern runs.
- The broader evidence gate showed 56 of 57 target semantic elements improved
  across 19 mixed-custody runs.
- The broader sample did not clear the full-modern gate: only four sampled
  archives had the complete modern artifact chain, while 15 were
  legacy-limited reasoning-trace runs.
- Provider-boundary warnings occurred on 57 of 57 broader-probe calls.
- The stance specialist had 12 validation drops and one non-improving run.
- `user_values_or_priorities_signal` remains unsolved by the current
  specialists.
- After the signature-only metadata filter, normal complex `$lolla` runs are
  provider-boundary clean; specialist probe provider-boundary behavior remains
  a separate explicit-model-call issue.

Boundaries held:

- normal `$lolla` remains unchanged;
- runtime specialist integration remains blocked;
- archive integration remains blocked;
- no `SKILL.md` changes;
- no prompt changes;
- no `archive_run.py` changes;
- no semantic coverage archive integration;
- no `conversation_understanding_ir.v0`;
- no user-values extractor;
- no graph DB, embeddings, chunking, memory layer, LLM judge,
  answer-quality scoring, provider-boundary policy change, or automatic
  human-review labels.

Next evidence gate:

- Do not build specialist runtime integration until there are 15-20
  full-modern archives.
- Re-run the broader specialist gate only when that clean full-modern sample
  exists and provider-boundary behavior is understood.
- Until then, treat specialists as preserved offline/research machinery, not
  product runtime behavior.

## Current PRD Progress

Sequence note: the PRD's original order put trigger-policy and control-plane
docs earlier. We intentionally pulled R10 Observatory parity forward because the
current product loop is manual: run Lolla, open Observatory, inspect the local
archive, then decide what to trust. That is a sequencing choice, not a product
boundary change.

| PRD item | Status | Current read |
|---|---:|---|
| R1: Agent-Facing Result Contract | Done | `agent_result.json` / `lolla_agent_result.v1` exists, is archived, copied to `/tmp`, indexed in `reasoning_trace.json`, documented, tested, and smoke-tested. |
| R2: Risk Modes | Metadata plus policy/fixture/plan/tests/eval/review clarity done | `LOLLA_AUDIT_MODE` accepts `quick`, `standard`, `deep`, `high_stakes`, and `stability`; normalized value persists as `risk_mode`; invalid explicit values fail before model calls. The pipeline remains mostly metadata-first. The agent-result contract already keeps otherwise clean `high_stakes` runs conservative with `caller_action: ask_user_first`. PR36 documents policy, PR37 adds fixtures, PR38 reviews them, PR39 plans high-stakes reliance/readiness tightening, PR40 locks the current conservative contract in tests, PR41 adds deterministic `evaluation.json` reliance-policy clarity, PR42 exposes that caveat in review-corpus records, PR43 validates reviewer interpretation with fixtures, PR44 adds manifest counts, PR45 records the anti-drift handoff, PR46 plans future approved high-stakes evidence, PR47 adds high-stakes evidence fixtures, and PR48 adds a manifest-only evidence-readiness analyzer without implementing enforcement. |
| R3: Trigger Policy For Agents | Deferred | Not urgent for current manual workflow. Keep for later external agent-builder docs. |
| R4: Control-Plane Integration Contract | Done | `lolla_control_input.v1` and `lolla_control_result.v1` now exist as optional local sidecars. External trace/action/approval metadata can be preserved and summarized without changing ordinary `$lolla` runs or making Lolla an approval/sandbox/policy system. |
| R5: Capture Adequacy Upgrade | Done | `capture_adequacy` / `lolla.capture_adequacy.v0` now makes capture shape, omitted windows, and critical capture problems visible across extraction, run health, agent result, reasoning trace, and evaluation. It does not reconstruct omitted turns or change capture strategy. Real `$lolla` smoke passed with full capture. |
| R6: Evaluation Methodology And Failure Taxonomy | Human-review v0 done; PR30-PR63 eval/design/test/docs seeds done | `docs/lolla-evaluation-methodology.md`, `docs/evals/lolla-human-review-v0.json`, `docs/evals/lolla-failure-taxonomy.md`, and `docs/evals/human-review-workflow.md` exist. PR14 added the human-owned label contract. PR15 added a synthetic-review boundary so subagents can help without becoming ground truth. PR16 added a validator and prompt so synthetic candidate outputs must match the human-review schema without becoming human labels. PR30 added the first human/product review seed over the six complex baseline runs. PR31 added the human-owned actionable-delta rubric. PR32 added seed adversarial pair fixtures. PR33 added a 14-record broader human-review corpus batch with 12 counted positives, one partial boundary record, and one degraded exclusion. PR34 designed the first-class user-values/priorities signal without implementing extraction. PR35 documented live-output hygiene policy without runtime changes. PR36 documented risk-mode behavior policy without runtime changes. PR37 added risk-mode fixture examples without runtime changes. PR38 reviewed those fixtures and added the high-stakes values-conflict fixture without runtime changes. PR39 planned the high-stakes reliance/readiness implementation path without runtime changes. PR40 added contract-lock tests without runtime changes. PR41 added deterministic evaluation-artifact clarity without runtime enforcement. PR42 added review-corpus surface integration without runtime enforcement. PR43 and PR44 verified reviewer interpretation and manifest visibility without runtime enforcement. PR45 records the current state and decision gates. PR46 plans future approved high-stakes evidence without running cases. PR47 adds paraphrase-only high-stakes evidence fixtures. PR48 adds a read-only manifest analyzer for high-stakes evidence readiness. PR49 plans a human-owned values/priorities worksheet without extraction, exports, runtime behavior, or judging. PR50 adds paraphrase-only worksheet fixtures without extraction, export code, runtime behavior, automatic labels, or judging. PR51 reviews those fixtures without code, extraction, automatic labels, runtime behavior, or judging. PR52 adds blank worksheet export structure without reading archives, extracting values, populating labels, changing runtime behavior, or judging. PR53 pilots human-filled worksheets on existing reviewed summaries without raw content, extraction, automatic labels, runtime behavior, or judging. PR54 reviews the pilot, marks the v0 worksheet lane complete for human-owned review, and pauses before extraction, memory, runtime integration, automatic labels, or judging. PR55 lands a Semantica-inspired accountability plan without implementing doctor/preflight, decision records, provenance maps, conflict registers, case graph exports, graph DBs, embeddings, memory, policy engines, automatic labels, answer-quality scoring, or judges. PR56 plans a future read-only doctor/preflight command without implementing the CLI, running `$lolla`, calling models, mutating archives, changing prompts, changing `SKILL.md`, or changing runtime behavior. PR57 implements the smallest read-only doctor CLI without running `$lolla`, calling models, mutating archives, changing prompts, changing `SKILL.md`, changing provider-boundary policy, approving high-stakes use, or judging answer quality. PR58 designs `lolla.audit_decision_record.v0` as a paraphrase-only local accountability projection without implementing an exporter, runtime integration, automatic labels, answer-quality scoring, or judges. PR59 reviews six paraphrase-only decision-record fixtures and marks the shape ready for a future read-only exporter design prototype with caveats, without implementing that exporter. PR60 designs `lolla.provenance_map.v0` as a local artifact-lineage shape without implementing a provenance exporter, archive reading, runtime integration, graph DB, memory, compliance claims, scoring, or judges. PR61 designs `lolla.review_conflict_register.v0` as a human-review-owned conflict surface without implementing an exporter, resolving conflicts, automating severity, enforcing policy, scoring, labeling, or judging. PR62 designs `lolla.case_graph.v0` as a future run-local case graph export/view shape without implementing an exporter, archive reading, runtime integration, graph DB, memory, GraphRAG, entity resolution, scoring, labeling, or judging. PR63 creates three paraphrase-only accountability-view fixture bundles without implementing exporters, reading archives, changing runtime behavior, scoring, labeling, or judging. |
| R7: Deterministic Evaluation Artifact v0 | Done | `evaluation.json` / `lolla.evaluation.v0` is generated, copied to `/tmp`, indexed in `reasoning_trace.json`, and exposed through Observatory custody. It checks artifacts, schemas, custody, health, hygiene, and caller-policy consistency without judging advice quality. |
| R8: Calibrated Subjective Judges | Not started | Correctly deferred. Generic LLM judges may punish useful friction. PR30 supplies a six-run human-reviewed seed, PR31 defines actionable delta, PR32 supplies seed adversarial fixtures, PR33 broadens the human-reviewed corpus batch, PR34 designs values/priorities review context, PR35 keeps live-output hygiene honest, PR36 defines risk-mode reliance policy, PR37 adds risk-mode fixtures, PR38 reviews those fixtures, PR39 plans contract-first high-stakes reliance tightening, PR40 locks the current contract in tests, PR41 clarifies high-stakes evaluation artifacts, PR42 exposes the caveat to review-corpus records, PR43 validates reviewer interpretation with fixtures, PR44 makes aggregate absence/presence visible, PR45 records the anti-drift handoff, PR46 plans future high-stakes evidence creation without running it, PR47 adds paraphrase-only high-stakes fixtures, PR48 adds deterministic evidence-readiness analysis, PR49 makes values/priorities reviewable by humans before extraction, PR50 tests that worksheet with paraphrase-only fixtures, PR51 reviews fixture quality, PR52 adds blank deterministic worksheet structure, PR53 pilots human-filled worksheets, PR54 closes the worksheet lane at human-owned v0, PR55 records accountability primitives as inspectability aids rather than judge/scoring surfaces, PR56 plans a deterministic doctor/preflight readiness report, PR57 implements that report as a read-only CLI, PR58 designs a decision-delta record, PR59 reviews six paraphrase-only fixtures, PR60 designs a provenance map, PR61 designs a review conflict register, PR62 designs a case graph export/view shape, and PR63 creates combined accountability-view fixtures. The next safe accountability step is PR64 fixture review, not judge automation. |
| R9: Archive Corpus And Stability Workflow | Corpus/readiness/extraction/semantic surveys done | PR13 adds deterministic JSONL corpus + manifest export around `agent_result.json`, `evaluation.json`, capture adequacy, run health, provider-boundary status, usage/model metadata, artifact availability, and optional control-plane summaries. PR15 adds deterministic review-readiness tiers and batch recommendations. Later work added extraction adequacy corpus export, semantic coverage corpus export, and local findings analyzers. |
| R10: Observatory Parity | Done for current custody loop | Archive parity audit, selected archived sidecar APIs, selected-run custody UI, active-run custody sidecar parity, and evaluation custody parity are landed. Remaining known gap: selected archived dashboard render/readback can still hang after the full case payload resolves. |
| R11: Human Capability Surface | Not started | Later: optional "what to learn from this audit" surface. |
| R12: Public Docs Update | Strong progress | README, HOW_IT_WORKS, pitch, PRD, eval methodology, control-layer integration, agent-result contract, and archive parity docs now exist or have been updated. |

## Completed / Merged Foundation

Merged stack now on `origin/main`:

```text
407cc2c Agent result contract
30e9ad0 / 502e3c0 Risk mode metadata
bbdbed3 Observatory archive parity audit
b1ff0ad Selected archive sidecar APIs
25ddf45 Observatory selected-run custody panel
23672b4 Active-run custody sidecar parity
57b47ff Provider-boundary health classification
adfa9fa Provider-boundary conservative reclassification
af31e4a Deterministic evaluation artifact v0
070be72 Evaluation custody Observatory parity
9e499ff Capture adequacy metadata
385019a Evaluation contained-provider degraded policy
10397f4 SKILL.md conductor artifact-chain refresh
b196714 Control-plane integration contract
116507b Archive review corpus export
de08812 Human review taxonomy workflow
2b833d0 Review readiness tiers and synthetic review boundary
18d044b Synthetic review validator and prompt
```

### PR 1: Agent Result Contract

Commit:

- `407cc2c Add agent-facing Lolla result contract`

What changed:

- Added `agent_result.json` as `lolla_agent_result.v1`.
- Wrote it into archived runs.
- Copied it to `/tmp/lolla_<run_id>_agent_result.json`.
- Indexed it in `reasoning_trace.json` as `agent_facing_result`.
- Added public docs in `docs/lolla-agent-result-contract.md`.

Why it matters:

- Agents and future callers no longer need to parse the memo or Observatory to
  know the run status, `caller_action`, core deltas, human questions, artifact
  pointers, and usage summary.

Did not change:

- audit prompts,
- Step 6 reasoning,
- model calls,
- cost,
- Step 7 behavior,
- high-stakes policy,
- evaluation behavior.

Validation:

- Focused tests passed.
- A real `$lolla` smoke produced `lolla_agent_result.v1`.
- Partial run health mapped conservatively to
  `caller_action: "do_not_use_run_degraded"`.

### PR 2: Risk Mode Metadata

Commits:

- `30e9ad0 Add Lolla audit mode metadata`
- `502e3c0 Clarify risk mode metadata scope`

What changed:

- Added normalized `LOLLA_AUDIT_MODE`.
- Accepted values:
  - `quick`
  - `standard`
  - `deep`
  - `high_stakes`
  - `stability`
- Missing or empty mode defaults to `standard`.
- Invalid explicit mode fails before model calls.
- Persisted `risk_mode` into:
  - `result.json`,
  - `agent_result.json`,
  - `reasoning_trace.json`,
  - archive metadata,
  - run-event metadata.

Why it matters:

- The harness can now record caller/operator intent without pretending behavior
  has changed.

Did not change:

- prompts,
- cost,
- Step 7 behavior,
- high-stakes warnings,
- evaluation strictness,
- capture strictness,
- replay/comparison behavior.

Validation:

- Focused tests passed.
- Invalid mode was verified to fail before model calls.

### PR 3: Observatory Archive Parity Audit

Commit:

- `bbdbed3 Audit Observatory archive parity`

What changed:

- Added a small Observatory risk-mode surfacing fix.
- Added `docs/observatory-archive-parity-audit.md`.
- Confirmed archive discovery works.
- Identified the real parity gap:

```text
The SPA can list/load archived runs, but deeper /audit/* telemetry pages are
still scoped to the active served run.
```

Why it matters:

- The problem became precise. "Local history is broken" is now more accurately:

```text
local history can find archived runs, but full custody inspection does not yet
follow the selected archived run.
```

Did not change:

- Observatory UI design,
- audit behavior,
- model calls,
- artifact generation,
- evaluation behavior.

Validation:

- Focused Observatory tests passed.
- Real archive endpoint smoke confirmed `risk_mode`, run health, and usage data
  surfaced.

### PR 4: Selected Archived Sidecar APIs

Commit:

- `b1ff0ad Add selected archive sidecar APIs`

What changed:

- Added read-only selected-archive sidecar endpoints:
  - `/api/case/<id>/agent-result`
  - `/api/case/<id>/reasoning-trace`
  - `/api/case/<id>/events`
  - `/api/case/<id>/memo`
  - `/api/case/<id>/graph-survival`
- Kept sidecar resolution fixed to known filenames inside the selected run
  directory.
- Added missing-sidecar 404 behavior.
- Added archive-path escape tests.
- Bound the Observatory server to `127.0.0.1` so the "local-only" claim is
  technically true.

Why it matters:

- Selected archived run custody artifacts are now reachable without pretending
  the `/audit/*` pages already follow SPA selection.

Did not change:

- UI design,
- audit behavior,
- model calls,
- artifact generation,
- evaluation behavior,
- control-plane schema,
- replay behavior,
- Step 7 behavior.

Validation:

- Focused tests passed.
- Real archive smoke confirmed all new sidecar endpoints returned expected
  payloads.

### PR 5: Observatory Selected-Run Custody Panel

Commit:

- `25ddf45 Add Observatory selected-run custody panel`

What changed:

- Consume the selected archived sidecar APIs in the Observatory SPA.
- When an archived case is selected, show a compact custody/inspection panel for:
  - `agent_result.json`,
  - `reasoning_trace.json`,
  - `run_events.json`,
  - `memo.md`,
  - `graph_survival_report.*`.

Expected behavior:

- Available artifacts show status, links, or lightweight previews.
- Missing artifacts show "unavailable" rather than broken UI.
- Selected archived run B must show B's sidecars, not active run A's.
- The custody panel can render as a compact floating panel when the selected
  archived dashboard/sidebar is stuck on `Loading...`, then relocate into the
  sidebar if the sidebar later appears.

Non-goals:

- no Observatory redesign,
- no `/audit/*` selected-run rewrite yet,
- no eval artifact,
- no new artifact generation,
- no model calls,
- no Step 7 behavior,
- no risk-mode behavior,
- no control-plane schema.

Why it matters:

- It completes the current manual inspection loop:

```text
run Lolla manually
-> open Observatory
-> select local history item
-> inspect selected run custody artifacts
```

PM read:

- Product alignment is good.
- Scope is appropriately boring: no redesign, no audit behavior, no model calls,
  no eval, no new artifact generation.
- The implementation uses the sidecar APIs from PR 4 instead of pretending the
  deeper `/audit/*` pages already follow selected archived runs.
- This moves R10 but does not expand Lolla into a guardrail, sandbox, policy
  engine, fact-checker, or generic judge.

SKILL.md alignment:

- Do not add selected-run custody-panel mechanics to `SKILL.md`.
- `SKILL.md` is already doing the right job as a conductor surface: it mentions
  audit-mode setup, the durable artifact chain, Observatory, archive, agent
  result, and reasoning trace.
- R10 implementation details belong in `docs/how-it-works/live-flow.md`,
  `docs/observatory-archive-parity-audit.md`, and this progress report.
- Keeping PR 5 out of `SKILL.md` preserves the Track 1 defragmenting direction
  and avoids making the executable instruction file large again.

Verification already run:

```bash
PYTHONPATH=. pytest -q \
  tests/test_pr3_observatory_panels.py \
  tests/test_audit_mode.py \
  tests/test_agent_result.py \
  tests/test_reasoning_trace_archive.py \
  tests/test_skill_contract.py \
  tests/test_archive_run_case_identity.py \
  tests/test_archive_run_v60_telemetry.py \
  tests/test_finalize_trusted_transcript.py

python3 -m py_compile observatory/serve_result.py
git diff --check origin/main..HEAD
```

Result:

```text
102 passed
compile clean
diff check clean
```

Real browser/server smoke evidence:

- Active served run A:
  `<archive-root>/accept-founding-engineer-role/20260624T125142Z_2aa96f/result.json`
- Selected archived run B:
  `archive:founder-months-runway-flat:20260624T192039Z_c6c235`
- After selecting B, server logs showed selected-run sidecar requests with
  encoded archive id and `200` responses for:
  - `/agent-result`
  - `/reasoning-trace`
  - `/events`
  - `/memo`
  - `/graph-survival`
- An older real archived run,
  `archive:mid-level-consultant-report-2:20260624T133814Z_b4a2dd`, returned
  `404` for missing `agent_result.json` and `200` for sidecars that existed.
  That supports the "unavailable rather than broken" path.
- Stronger Playwright proof passed:
  - performed the real click on the founder archive case,
  - deliberately delayed the heavy selected `/api/case/archive:...` response,
  - inspected only `.lolla-custody-panel`, avoiding the known selected
    dashboard render/readback hang.
- The clicked archive produced a floating panel with:
  - 5 rows,
  - `agent_result.json` with `lolla_agent_result.v1`, `status partial`,
    `caller do_not_use_run_degraded`, `mode standard`,
  - `reasoning_trace.json` with 19 artifacts,
  - `run_events.json`,
  - `memo.md`,
  - `graph_survival_report.*`,
  - 5 selected-archive links,
  - 0 `lolla-audit` links.

Merge read:

- PR 5 was mergeable and has been fast-forwarded to `origin/main`.
- The custody panel works from the real archived-case click path and stays
  available even when the main selected dashboard is stuck on `Loading...`.
- The remaining selected dashboard render/readback instability still exists
  after the full selected-case payload resolves, but it is no longer a blocker
  for this custody-panel bridge.

Follow-up issue after merge:

- Stabilize selected archived dashboard render/inspection so the main selected
  case view itself can be read/screenshot reliably after the full payload
  resolves. Keep that as a separate small Observatory lifecycle PR.

### PR 6: Active-Run Custody Sidecar Parity

Commit:

- `23672b4 Fix active-run custody sidecar resolution`

Why it exists:

- The 2026-06-25 real `$lolla` smoke showed the artifact chain was healthy
  enough to inspect:
  - `agent_result.json` existed,
  - `reasoning_trace.json` indexed the agent result,
  - `run_events.json` recorded the archive path,
  - the archive held the expected sidecars.
- But active `lolla-audit` custody endpoints returned `404`:
  - `/api/case/lolla-audit/agent-result`
  - `/api/case/lolla-audit/reasoning-trace`
  - `/api/case/lolla-audit/events`
  - `/api/case/lolla-audit/memo`
  - `/api/case/lolla-audit/graph-survival`
- Selected archived custody endpoints already worked. The bug was active-run
  sidecar resolution, not artifact generation.

What changed:

- Selected-case sidecar APIs now branch on whether the case is the active
  current `lolla-audit` run or a selected archived run.
- For active `lolla-audit`, sidecar lookup supports:
  - prefixed `/tmp/lolla_<run_id>_<filename>` files,
  - archive fallback through
    `run_events.json -> archive_completed.details.archive_path`,
  - same-directory fixed filenames for archive-style active result layouts.
- For selected archived runs, behavior remains strict:
  - fixed known filenames,
  - inside the selected archive directory,
  - no broad path lookup.
- The route layer now passes `is_current` from `_load_case_result(case_id)` into
  the sidecar helpers.

Why it matters:

- The custody panel can now inspect the run the user just finished, not only
  older archived runs.
- This completes the current manual inspection path at the sidecar/API level:

```text
finish Lolla run
-> open Observatory
-> inspect active lolla-audit custody artifacts
-> select older archive
-> inspect archived custody artifacts
```

Non-goals preserved:

- no `SKILL.md` changes,
- no audit behavior changes,
- no prompt changes,
- no model calls,
- no provider-boundary health policy,
- no risk-mode behavior changes,
- no eval artifact,
- no control-plane schema,
- no UI redesign.

Validation:

- Focused Observatory tests:

```text
70 passed
```

- Full focused suite:

```text
107 passed
compile clean
diff check clean
```

- Live endpoint smoke against
  `/tmp/lolla_20260625T081013Z_9580b5_result.json` confirmed:
  - active `lolla-audit` returns `200` for all five custody endpoints,
  - selected archived founder run still returns `200` for all five custody
    endpoints.

PM read:

- PR 6 was mergeable and has been fast-forwarded to `origin/main`.
- It fixes a crisp inspection-loop bug without expanding product scope.
- The security posture looks preserved because selected archived runs still use
  strict archive-directory containment, and active runs only gain fixed
  known-filename lookup plus archive fallback from local run events.

### PR 7A: Provider-Boundary Health Classification

Branch:

- `pr/provider-boundary-health-policy`

Commit:

- `57b47ff Classify provider-boundary health metadata`

Why it exists:

- Real runs frequently show `vendor_boundary_reasoning_leak` because the model
  provider returned reasoning details despite reasoning being disabled.
- Before changing `caller_action` or `run_health.overall`, we need to know
  whether this is:
  - a provider-boundary warning only,
  - product-output contamination,
  - live-output contamination,
  - archive/custody contamination.

What changed:

- Added `provider_boundary_health` metadata with explicit statuses:
  - `clean`,
  - `warning_unknown_persistence`,
  - `warning_contained`,
  - `confirmed_contamination`.
- Attached the metadata to `run_health.provider_boundary_health`.
- Refreshes the classification after product/live hygiene, so pipeline-time
  state can be `warning_unknown_persistence` and archive-time state can become
  `warning_contained` or `confirmed_contamination`.
- Exposes a compact summary in `agent_result.json`.
- Carries enriched health through `reasoning_trace.json`.
- Updates public docs for agent-result and pipeline-lane health fields.

What it deliberately does not change:

- `caller_action`,
- `run_health.overall`,
- prompts,
- model routing,
- Step 7,
- risk-mode behavior,
- eval artifacts,
- control-plane schema,
- Observatory UI,
- `SKILL.md`.

Validation:

```text
142 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Rebuilding the agent result from the 2026-06-25 smoke archive returns:
  - `status: partial`,
  - `caller_action: do_not_use_run_degraded`,
  - `provider_boundary_health.status: warning_contained`.

PM read:

- PR 7A was mergeable and has been fast-forwarded to `origin/main`.
- It is the right first move: classify and expose the provider-boundary issue
  without weakening the conservative caller contract.
- It should not be followed by an automatic green-light change until we decide
  the exact PR7B policy.

## Recent Foundation PRs

### PR 7B: Provider-Boundary Conservative Reclassification

Branch:

- `pr/provider-boundary-reclassification-decision`

Commit:

- `adfa9fa Keep contained provider-boundary warnings conservative`

Policy choice:

- Keep contained provider-boundary warnings conservative.
- Do not add a new caller action.
- Do not introduce `ok_with_warnings`.
- Do not change `run_health.overall`.
- Do not change `caller_action`.

What changed:

- Pure contained provider-boundary warnings now get a more specific
  `status_reason`:

```text
provider-boundary warning is contained; conservative policy still requires inspection
```

- Pure contained provider-boundary warnings also get a more specific note in
  `agent_result.json`.
- The special case only applies when the contained provider-boundary warning is
  the only partial/degraded/critical cause.
- Runs with another partial issue, such as `bullshit_index_partial`, stay on
  the generic partial reason.

What it deliberately does not change:

- `caller_action`,
- `run_health.overall`,
- `provider_boundary_health` classification,
- prompts,
- model routing,
- Step 7,
- risk-mode behavior,
- eval artifacts,
- control-plane schema,
- Observatory UI,
- `SKILL.md`.

Validation:

```text
48 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Rebuilding the agent result from the 2026-06-25 smoke archive returns:
  - `status: partial`,
  - `status_reason: run_health.overall is partial`,
  - `caller_action: do_not_use_run_degraded`,
  - `provider_boundary_health.status: warning_contained`.
- This is correct because that real run also has another partial cause, so
  provider-boundary is not the only reason for partial health.

PM read:

- PR 7B has landed on `origin/main`.
- It makes the policy decision explicit while preserving conservative caller
  behavior.
- This closes the immediate provider-boundary health-policy loop. A future
  warning-bearing usable action can still be designed later, but it is no
  longer the next necessary PR.

### PR 8: Deterministic Evaluation Artifact v0

Branch:

- `pr/deterministic-evaluation-artifact-v0`

Commit:

- `af31e4a Add deterministic evaluation artifact`

What changed:

- Added `evaluation.json` with schema `lolla.evaluation.v0`.
- Generates it during archive creation after `agent_result.json` and the first
  `reasoning_trace.json` exist.
- Writes `/tmp/lolla_<run_id>_evaluation.json` as a convenience copy.
- Regenerates `reasoning_trace.json` so `evaluation.json` is indexed as
  `deterministic_evaluation`.
- Checks deterministic run-readiness only:
  - required artifact presence,
  - schema versions,
  - agent-result caller policy,
  - reasoning-trace custody,
  - artifact hashes,
  - product/live hygiene states,
  - provider-boundary policy consistency,
  - archive readiness.

What it deliberately does not change:

- no LLM judge,
- no advice-quality scoring,
- no helpfulness/coherence/correctness scoring,
- no model calls,
- no prompt changes,
- no Step 7 changes,
- no risk-mode behavior changes,
- no control-plane schema,
- no Observatory redesign,
- no `SKILL.md`.

Validation:

```text
148 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Building an evaluation for the older 2026-06-25 smoke archive returns:
  - `schema_version: lolla.evaluation.v0`,
  - `overall: warn`,
  - `caller_readiness: do_not_use`.
- The warnings are reasonable for that older archive:
  - provider-boundary metadata was not present yet,
  - live output was `not_checked`,
  - provider-boundary policy was therefore `unknown`.

PM read:

- PR 8 has landed on `origin/main`.
- It lands the correct kind of first eval: a deterministic envelope/readiness
  receipt, not a subjective judge.
- The next narrow follow-up should expose `evaluation.json` through the same
  Observatory custody path as the other run artifacts.

### PR 9: Evaluation Custody Observatory Parity

Branch:

- `pr/evaluation-custody-observatory-parity`

Commit:

- `070be72 Expose evaluation artifact in Observatory custody`

What changed:

- Added read-only selected-case endpoint:

```text
/api/case/<id>/evaluation
```

- Reuses the existing sidecar resolver:
  - active `lolla-audit` can resolve `/tmp/lolla_<run_id>_evaluation.json`,
  - active `lolla-audit` can fall back through
    `run_events.json -> archive_completed.details.archive_path`,
  - selected archived runs resolve fixed `evaluation.json` inside the selected
    archive directory only,
  - missing `evaluation.json` returns `404`,
  - archive escape protection remains in force.
- Adds `evaluation.json` to the selected-run custody panel with compact preview:

```text
lolla.evaluation.v0 · overall <status> · readiness <caller_readiness>
```

What it deliberately does not change:

- no evaluation schema changes,
- no new evaluation checks,
- no archive-generation changes,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no `/audit/*` selected-run rewrite,
- no Observatory redesign,
- no `SKILL.md`.

Validation:

```text
148 passed
compile clean
diff check clean
```

Additional live-route sanity check:

- Against older pre-PR8 archives, `/api/case/<id>/evaluation` returns clean
  `404` with a sidecar-missing message. This is acceptable legacy behavior and
  should render as unavailable rather than broken.
- Tests cover `200` behavior for active tmp, active archive fallback, selected
  archived run, missing sidecar, archive escape, and custody-panel injection.

### PR 10: Capture Adequacy Manifest Upgrade

Branch:

- `pr/capture-adequacy-manifest-upgrade`

Commit:

- `9e499ff Add capture adequacy metadata`

Why it exists:

- The manual inspection loop can now expose the run's artifacts, health,
  evaluation, and trace.
- The next weakest point is upstream: whether Lolla captured enough of the
  conversation for the audit to deserve trust.
- Long conversations can preserve opening/recent turns while omitting middle
  turns that may contain constraints, reversals, stakeholder facts, or dropped
  threads.

What changed:

- Added deterministic capture adequacy metadata with schema
  `lolla.capture_adequacy.v0`.
- `run_extract.py` emits `capture_adequacy`.
- `run_pipeline.py` carries it into `result.run_health`.
- `agent_result.json` exposes a compact summary without raw transcript text.
- `reasoning_trace.json` includes capture adequacy in its capture section.
- `evaluation.json` checks capture adequacy deterministically:
  - missing metadata warns for older archives,
  - warning-level capture warns,
  - critical capture is blocking.

Important policy nuance:

- PR10 makes capture loss visible. It does not make capture smarter yet.
- Ordinary first-N-plus-last-N truncation can warn in metadata/evaluation
  without necessarily degrading the whole run-health state.
- Critical capture problems stay conservative and can block caller readiness.

What it deliberately does not change:

- no `SKILL.md`,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no long-conversation summarizer,
- no decision-aware capture rewrite,
- no Observatory redesign,
- no control-plane schema.

Validation:

```text
226 passed
compile clean
diff checks clean
```

Additional legacy-archive sanity check:

- Building `evaluation.json` against the older 2026-06-25 smoke archive returns:
  - `overall: warn`,
  - `caller_readiness: do_not_use`,
  - capture adequacy checks warning that metadata is missing.
- Building `agent_result.json` for the same older archive returns:
  - `capture_adequacy.status: unknown`.
- This is correct backwards compatibility: older archives warn instead of
  crashing or pretending capture adequacy was known.

PM read:

- PR10 has landed on `origin/main`.
- It is the right boring version of capture adequacy: first make omitted capture
  visible, then decide whether to change capture strategy.
- Real `$lolla` smoke confirmed the new capture metadata survives extraction,
  result health, agent result, reasoning trace, archive, evaluation, and active
  Observatory custody.

Real smoke:

- Run id: `20260625T125625Z_aae54e`
- Archive:
  `<archive-root>/prioritize-control-plane-contract/20260625T125625Z_aae54e`
- Capture adequacy:
  - `schema_version: lolla.capture_adequacy.v0`
  - `status: good`
  - `capture_strategy: full`
  - `declared_turn_count: 4`
  - `captured_turn_count: 4`
  - `omitted_turn_count: 0`
  - `omitted_windows: []`
  - `risk_flags: []`
- Evaluation capture checks:
  - `capture_adequacy_schema_version: pass`
  - `capture_adequacy_status: pass`
- Active Observatory custody returned `200` for:
  - `/agent-result`
  - `/reasoning-trace`
  - `/events`
  - `/memo`
  - `/graph-survival`
  - `/evaluation`

Smoke note:

- `/tmp/lolla_<run_id>_reasoning_trace.json` is still not emitted as a temp
  convenience copy. The archived `reasoning_trace.json` exists and active
  Observatory serves it correctly. Track this as minor artifact-parity polish,
  not a PR10 blocker.

### PR 10b: Evaluation Contained-Provider Degraded Policy

Branch:

- `pr/evaluation-contained-provider-degraded-policy`

Commit:

- `385019a Fix contained provider-boundary evaluation policy`

Why it exists:

- The PR10 real smoke exposed a deterministic-evaluation false fail.
- `provider_boundary_contained_policy` failed when provider-boundary health was
  `warning_contained` but the run was already `degraded` for another
  conservative reason.
- That is too strict: exact `partial` should be required for pure
  provider-boundary-only partial runs, not for runs that are degraded/incomplete
  for additional causes while still keeping `caller_action` conservative.

What changed:

- For pure contained provider-boundary-only runs, the evaluation still expects:
  - `status: partial`,
  - `caller_action: do_not_use_run_degraded`.
- For contained provider-boundary warnings plus other conservative run-health
  causes, the evaluation now accepts:
  - `status: partial`,
  - `status: degraded`,
  - or `status: incomplete`,
  - as long as `caller_action: do_not_use_run_degraded`.
- Added a regression test for warning-contained plus `no_fingerprint` degraded
  health.

What it deliberately does not change:

- no `caller_action` relaxation,
- no `run_health.overall` relaxation,
- no provider-boundary classification change,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no Observatory changes,
- no `SKILL.md`.

Validation:

```text
32 passed
compile clean
diff checks clean
```

Real-archive rebuild after the fix:

```text
schema_version: lolla.evaluation.v0
overall: warn
caller_readiness: do_not_use
capture_adequacy_schema_version: pass
capture_adequacy_status: pass
provider_boundary_contained_policy: pass
provider_boundary_policy: warn
```

PM read:

- PR10b has landed on `origin/main`.
- It fixes an evaluation-policy false fail without weakening the conservative
  machine-caller contract.
- The deterministic eval no longer false-fails a conservative degraded run, but
  still leaves that run non-actionable for machine callers.

## Latest Landed PR

### PR 12: Control-Plane Integration Contract v0

Branch:

- `pr/control-plane-integration-contract-v0`

Commit:

- `b196714 Add control-plane integration contract`

Why it exists:

- R4 asks Lolla to fit beside external agent frameworks, approvals, proxies,
  sandboxes, identity scopes, and trace stores without becoming any of them.
- The goal is optional metadata preservation and handoff, not enforcement.

What changed:

- Adds `engine/system_b/control_plane.py`.
- Defines:
  - `lolla_control_input.v1`,
  - `lolla_control_result.v1`,
  - caller-action to control-plane outcome mappings,
  - compact control metadata summaries.
- Archive now preserves optional `/tmp/lolla_<run_id>_control_input.json` as
  `control_input.json`.
- Archive generates `control_result.json` only when control input exists.
- Archive writes `/tmp/lolla_<run_id>_control_result.json` as a convenience copy
  only when generated.
- `agent_result.json` adds optional `control_context` only when control input
  exists.
- `reasoning_trace.json` indexes:
  - `control_input.json` as `control_plane_input`,
  - `control_result.json` as `control_plane_result`,
  - compact `process.control_plane` metadata when supplied.

Boundary and privacy posture:

- Ordinary `$lolla` runs remain unaffected.
- Lolla does not approve actions, enforce approvals, sandbox execution, proxy
  traffic, grant credentials, or replace policy engines.
- Raw proposed-action argument values are preserved only in local
  `control_input.json`; public/agent-facing summaries expose argument keys, not
  values.

What it deliberately does not change:

- no auto-triggering,
- no approval enforcement,
- no sandboxing,
- no proxy behavior,
- no tool execution,
- no model calls,
- no prompt changes,
- no risk-mode behavior,
- no eval judges.

Validation:

```text
157 passed
compile clean
diff checks clean
```

PM read:

- PR12 has landed on `origin/main`.
- It implements the PRD's R4 v0 correctly: optional, vendor-neutral,
  local-first, additive, and non-enforcing.
- The main operational caveat is expected and documented: raw external
  proposed-action metadata lives in `control_input.json`, so that artifact must
  be treated as local/sensitive.

Next PRD-backed choices after PR12:

- R6: evaluation methodology human-review pack and first failure taxonomy.
- R9: archive corpus/stability export expansion around `agent_result.json`,
  `evaluation.json`, capture adequacy, control metadata, and repeated-run
  grouping.
- R10 polish: selected archived dashboard lifecycle stabilization.
- R3 trigger policy docs only if external agent-builder onboarding becomes
  urgent.

Research/backlog note:

- The human-exception / omitted-hinge idea is not currently an implementation
  item in this PRD. It can inform future thinking or a PRD revision, but the
  current R11 "Human Capability Surface" is narrower: an optional compact
  "What To Learn From This Audit" memo/Observatory section.

## Current Product Work

### Synthetic Review Pilot After PR15

Pilot folder:

- `reviews/synthetic/pr15-modern-batch-2026-06-26/`

Why it exists:

- R9 now has a corpus export, but not every archive is equally reviewable.
- R6 now has a human-owned review taxonomy, but we want to use subagents as
  review aids without confusing their output with `lolla.human_review.v0`.
- The first synthetic rehearsal showed that older archives can support
  answer-level practice, but most do not support full custody review.

What PR15 changed:

- Adds deterministic review-readiness fields to each corpus record:
  - `review_readiness_tier`,
  - `content_review`,
  - `custody_review`,
  - `batch_recommendation`.
- Adds manifest aggregate counts for those fields.
- Defines four tiers:
  - `full_modern_reviewable`,
  - `modern_partial_reviewable`,
  - `legacy_content_reviewable`,
  - `not_reviewable`.
- Defines batch recommendations:
  - `recommended_modern_review_batch`,
  - `recommended_legacy_rehearsal_batch`,
  - `exclude_or_needs_backfill`.
- Adds `docs/evals/lolla-synthetic-review-v0.json` as the tiny boundary schema
  for subagent/synthetic review notes.
- Updates evaluation docs so synthetic notes may propose candidate labels but
  may not populate `lolla.human_review.v0` without human ratification.

Boundary and privacy posture:

- No model calls.
- No LLM judge.
- No advice-quality score.
- No approval decision.
- No automatic `safe_for_agent_use`.
- No capture/chunking redesign.
- No human-exception / omitted-hinge implementation.
- No runtime `$lolla` behavior change.
- Human review stays human-owned. Subagents can produce rehearsal notes,
  candidate labels, QA notes, or disagreement reports.

PR15 validation:

```text
43 focused tests passed locally during PM review
compile clean
JSON schema docs parse cleanly
diff checks clean
no SKILL.md diff
real local export produced 63 records
```

Real local export counts:

```text
full_modern_reviewable: 1
modern_partial_reviewable: 14
legacy_content_reviewable: 46
not_reviewable: 2

content_review_available_count: 61
custody_review_available_count: 1

recommended_modern_review_batch: 15
recommended_legacy_rehearsal_batch: 46
exclude_or_needs_backfill: 2
```

Pilot read:

- PR15 is merged.
- The first 15-record synthetic pilot ran with three independent subagents.
- Subagents broadly agreed that Lolla added useful friction across the batch.
- The pilot exposed two next-step issues:
  - the synthetic prompt used a wrong severity vocabulary before correction,
  - the workflow needs a clearer rule for answer-level pass versus
    run-envelope/live-output failure.

Implemented follow-up:

```text
PR16: Synthetic Review Output Validator + Pilot Prompt Fix
```

PR16 validated synthetic outputs against `lolla.human_review.v0` allowed values
when they include `candidate_human_review`, added a corrected synthetic-review
prompt/template, and clarified that synthetic outputs are not human-review
ground truth.

### Validated Synthetic Pilot After PR16

Pilot folder:

- `reviews/synthetic/pr16-validated-modern-batch-2026-06-26/`

Status:

```text
completed
```

What PR16 changed:

- Added `engine/system_b/synthetic_review.py`.
- Added validation for `lolla.synthetic_review.v0`.
- Required synthetic `candidate_human_review` labels to validate against
  `lolla.human_review.v0`.
- Rejected invalid severity values such as `minor`, `material`, and `unclear`.
- Rejected blank candidate labels in completed synthetic output.
- Added `docs/evals/synthetic-review-prompt-template.md`.

What the validated pilot showed:

- Three independent subagents completed the same 15-record modern batch.
- All three reported validator-passing outputs.
- The PR15 severity-vocabulary problem did not recur.
- Lolla's useful-friction signal remained strong across the batch.
- No reviewer treated the batch as autonomous-agent-ready.
- The main remaining disagreement is review-surface policy, not schema
  validity.

Findings:

- `reviews/synthetic/pr16-validated-modern-batch-2026-06-26/findings.md`

Stable disagreements to resolve:

- Records 13 and 15: saved answer usefulness versus live-output machinery leak.
- Record 1: degraded/eval-fail run envelope versus answer-level usefulness.
- Record 7: degraded envelope and quote-fabrication validation caveat.
- Record 8: high-stakes unsupported legal/domain claim risk.

Recommended next PR:

```text
PR17: Review Surface Policy + Validated Pilot Findings
```

Preferred shape:

- docs/workflow first,
- no runtime behavior,
- no LLM judge,
- no capture/chunking change,
- no human-exception implementation.

Clarify:

- answer-level review,
- run-envelope/custody review,
- live-output hygiene review,
- agent-readiness review.

If docs-only clarification is not enough for future corpus analysis, consider a
tiny additive schema field such as `review_surface` or `surface_findings`, but
do not start there unless the ambiguity blocks validation.

### PR17: Review Surface Policy + Validated Pilot Findings

Branch:

- `pr/review-surface-policy-validated-pilot`

Commit reviewed:

- `d07c2f86 Clarify review surface policy for synthetic pilots`

Status:

```text
merged to origin/main; Pilot 3 completed
```

What changed:

- `docs/evals/human-review-workflow.md` now explicitly separates:
  - answer-level review,
  - run-envelope/custody review,
  - live-output hygiene review,
  - agent-readiness review.
- `docs/evals/synthetic-review-prompt-template.md` now uses the same review
  surface language and asks synthetic reviewers to summarize surface conflicts
  in `qa_notes`.
- `docs/evals/pr16-validated-synthetic-pilot-findings.md` captures the
  validated Pilot 2 findings in checked-in docs.
- `docs/lolla-evaluation-methodology.md` links the finding and names review
  surface ambiguity as the lesson.

Boundary preserved:

- no `SKILL.md` change,
- no `$lolla` runtime change,
- no schema fields added,
- no model calls,
- no LLM judge,
- no automatic `human_review`,
- no automatic `safe_for_agent_use`,
- no capture/chunking work,
- no Observatory work.

Verification:

```text
19 focused tests passed
JSON docs parse cleanly
diff checks clean
docs-only PR
```

PM read:

- PR17 does the right small thing.
- It names the ambiguity before we build machinery on top of it.
- Pilot 3 showed the docs-only surface clarification was enough for the old
  Records 13/15 dispute.
- Do not add `surface_findings` yet.
- The next remaining policy issue is narrower: when should
  `safe_for_agent_use` be `no` versus `with_human_review` for high-stakes,
  degraded, or custody-limited runs?

### Pilot 3: Disputed Surface Rehearsal After PR17

Pilot folder:

- `reviews/synthetic/pr17-disputed-surface-pilot-2026-06-26/`

Scope:

```text
five disputed records from the PR16 validated modern batch
```

Validation:

```text
reviewer-a.json PASS
reviewer-b.json PASS
reviewer-c.json PASS
```

What changed:

- The old disagreement on records 13 and 15 collapsed into a shared surface
  summary:

```text
answer=pass; envelope=warn/degraded; live_output=fail; agent=with_human_review
```

- Record 1 became cleanly separable:

```text
answer=pass; envelope=fail; agent=no
```

- Record 8 became a true answer-level failure:

```text
unsupported_new_claim; agent=no
```

Remaining disagreement:

- Record 7 still split on `safe_for_agent_use`:
  - one reviewer chose `no`,
  - two reviewers chose `with_human_review`.

PM read:

- PR17 worked.
- The surface policy is now good enough without schema changes.
- PR18 implements the tiny docs-only clarification for agent-readiness labels.

```text
When does degraded/high-stakes/custody-limited mean no rather than
with_human_review?
```

### PR18: Agent-Readiness Label Policy v0

Branch:

- `pr/agent-readiness-label-policy-v0`

Commit reviewed:

- `37ab38f Clarify agent readiness review labels`

Status:

```text
merged to origin/main
```

What changed:

- `docs/evals/human-review-workflow.md` clarifies
  `safe_for_agent_use: yes | with_human_review | no | unclear`.
- `docs/evals/synthetic-review-prompt-template.md` mirrors the same
  agent-readiness policy.
- `docs/evals/pr17-disputed-surface-pilot-findings.md` records the Pilot 3
  evidence behind the cleanup.

Boundary preserved:

- no `SKILL.md` change,
- no `$lolla` runtime change,
- no schema fields added,
- no model calls,
- no LLM judge,
- no automatic `human_review`,
- no automatic `safe_for_agent_use`,
- no capture/chunking work,
- no Observatory work.

Verification:

```text
19 focused tests passed
JSON docs parse cleanly
diff checks clean
docs-only PR
```

PM read:

- PR18 is merged.
- It resolves the Record 7-style label ambiguity without adding machinery.
- After PR18, pause eval PRs unless a real review batch shows a new blocker.

## Drift Checks For Every PR

Before approving or merging a PR, check:

1. Does it move a named PRD item or a clearly justified operational blocker?
2. Does it preserve the distinction between shipped behavior and roadmap?
3. Does it keep Lolla as a reasoning-audit harness rather than:
   - guardrail,
   - sandbox,
   - firewall,
   - identity broker,
   - policy engine,
   - fact checker,
   - generic judge?
4. Does it avoid exposing private machinery in ordinary user-facing output?
5. Does it avoid adding LLM judges before deterministic and human-review
   foundations exist?
6. Does it keep high-stakes mode honest: stricter metadata or routing is not
   domain assurance?
7. Does it add or preserve tests for the changed artifact path?
8. Does it keep local artifacts local by default?
9. Does it avoid broad UI redesign when a narrow custody/API fix would do?
10. Does it leave `SKILL.md` as a conductor surface, with details in linked docs?

## Verification Habit

Prefer focused tests tied to the changed path, plus compile checks for edited
Python modules.

Recent focused verification sets have included:

```bash
python3 -m py_compile \
  engine/system_b/audit_mode.py \
  engine/system_b/agent_result.py \
  engine/system_b/reasoning_trace.py \
  scripts/archive_run.py \
  scripts/run_extract.py \
  scripts/run_pipeline.py \
  scripts/skill/validate_audit_mode.py \
  observatory/serve_result.py

PYTHONPATH=. pytest -q \
  tests/test_audit_mode.py \
  tests/test_agent_result.py \
  tests/test_reasoning_trace_archive.py \
  tests/test_skill_contract.py \
  tests/test_archive_run_case_identity.py \
  tests/test_archive_run_v60_telemetry.py \
  tests/test_finalize_trusted_transcript.py \
  tests/test_pr3_observatory_panels.py
```

For real-run smoke tests, inspect:

```bash
jq '{schema_version,status,caller_action,risk_mode}' \
  /path/to/archive/run/agent_result.json

jq '.process.risk_mode' \
  /path/to/archive/run/reasoning_trace.json

jq '.artifacts[] | select(.path | endswith("agent_result.json"))' \
  /path/to/archive/run/reasoning_trace.json
```

## Current Big-Picture Read

Harness foundation completion:

```text
about 65%
```

Manual inspection loop completion:

```text
about 90%
```

Reason:

- Lolla can already run, revise, memoize, archive, and expose machine-readable
  custody.
- Active and archived custody sidecar APIs now work, and the custody UI bridge
  has real-click Playwright proof.
- Provider-boundary health is now structured enough to support a policy
  decision instead of a blunt partial-health blob.
- Deterministic evaluation v0 is implemented as a run-readiness receipt.
- Evaluation custody surfacing has landed through PR9.
- Capture adequacy has landed and passed a real `$lolla` smoke.
- Evaluation-policy correction PR10b has landed.
- Control-plane contract v0 has landed, giving external agent/control systems a
  local metadata contract without making Lolla an enforcement layer.
- Archive corpus export, human-review taxonomy/workflow, review-readiness
  tiers, and the synthetic-review validator have landed.
- The validated PR16 pilot shows the next eval-methodology issue is review
  surface policy, not judge implementation.

The current strategy is still sound:

```text
custody first
-> inspection
-> deterministic evaluation
-> control-plane metadata contract
-> archive corpus and human-review workflow
-> calibrated subjective evaluation only later
-> deeper vendor-specific integration only after the local contract is stable
```
