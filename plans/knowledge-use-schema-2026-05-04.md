# Knowledge Use Schema - From Buried Markdown To Runtime Judgment

**Date:** 2026-05-04
**Last updated:** 2026-05-05
**Audience:** future coding session with no prior conversation context
**Status:** living schema doctrine; PR 1 schema/fixtures, pilot, Batch 1, Batch 2, v4 compilation, and PR 11 Gate 4 harness are implemented; current frontier is no-paid Decision Pressure generalization review
**Related roadmap:** `plans/knowledge-substrate-roadmap-2026-05-04.md`
**External architecture study:** `research/gbrain-architecture-learning-handover-2026-05-05.md`
**External decision-process study:** `research/clear-thinking-lolla-learning-handover-2026-05-05.md`
**Primary source substrate:** reviewed source files in `data/model_sources/`, copied from `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/` with SHA-256 manifest
**Current runtime repo:** `/Users/marcin/Desktop/Apps/lolla-skill/`

---

## 0. Current Implementation State - 2026-05-05

This document began as a target schema. The first implementation slices are now
real. Future sessions should treat the following as current baseline:

- Active runtime graph: `222` models in `data/knowledge_graph.json`.
- Source residency: `55` reviewed canonical markdown files copied into
  `data/model_sources/` with hash manifest at
  `data/model_sources/manifest.json`. This source-custody set matches the v4
  affordance records; it is not yet all `222` runtime models.
- Schema: `data/schemas/model_affordance.schema.json`.
- Extraction contract: `references/model-affordance-extraction.md`.
- Validation code: `engine/system_b/model_affordance_validation.py`.
- Schema tests: `tests/test_model_affordance_schema.py`.
- Pilot records: `data/model_affordances/pilot/` for 10 models.
- Batch 1 records: `data/model_affordances/batch_1/` for 20 models.
- Batch 2 records: `data/model_affordances/batch_2/` for 20 Lane-4-frequency models.
- Compiled v3 artifact:
  `data/compiled/model_affordances/affordances_v3.json`.
- v3 corpus shape: `50` model records, `86` affordances, `83` absence records.
- v3 validation: `0` schema failures and `0` source-quote rejections.
- Current experiment: PR 11 Gate 4 edge-probe harness, branch
  `feature/knowledge-substrate-pr11-gate4-edge-probes`.
- Gate 4 dry-run: `10` usable cases, `39` Lane 4 routes, `165/205` v3-covered
  candidate appearances, max packet estimate `32,935` tokens, no budget-driven
  omissions.
- Gate 4 judge contract includes `out_of_distribution` and
  `out_of_distribution_arms`. `constructive_edge` is diagnostic only.
- Gate 4 3-case paid generation stopped before judging when validation caught
  quote-exactness and missing-corpus trace failures. The useful product signal
  is now captured in `research/gate4-3case-product-readout-2026-05-05.md` and
  `research/decision-pressure-surface-spec-2026-05-05.md`: raw enriched probes
  are not the user surface; they must be compressed into Decision Pressure.
- PR 13 dry-surface work now adds
  `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md` and
  `research/affordance-batch3a-coverage-priority-2026-05-05.md`: in this dry
  product review, the 12-route readout compressed to `3` Decision Pressures and
  justified only a targeted `extract_5` Batch 3a coverage patch.
- PR 13 verification conclusion: the dry surface is product-valid as a
  docs/research checkpoint, but selection stability is still untested. A second
  reviewer should select 1-3 pressures from the same packet and gates before
  Batch 3a extraction or user-facing promotion proceeds.
- PR 14 selection-stability review now records a second-review convergence:
  `3/3` PR13 pressure clusters were selected again, with the same gate
  rationale. This is stable enough for Batch 3a planning, with a blindness
  caveat; it is not runtime, memo, Step 8, Step 6, or Lane 4 promotion
  evidence.
- PR 15 defined the Batch 3a extraction contract in
  `research/affordance-batch3a-extraction-brief-2026-05-05.md`: extraction
  should target Decision Pressure-ready operational constraints for exactly
  five models, not general model explanations.
- PR 16 executed that targeted patch and records the result in
  `research/pr16-batch3a-extraction-report-2026-05-05.md`: `5` narrow
  affordances and `12` absence records were compiled into
  `data/compiled/model_affordances/affordances_v4.json`, still
  `draft_review_only` and runtime-dormant.
- PR 17 dry-reviewed v4 against the same Decision Pressure gates in
  `research/gate4-3case-decision-pressure-v4-dry-review-2026-05-05.md`:
  decision label `v4_improves_fields_without_changing_selection`. v4 improves
  field quality and coverage honesty for the same compact surface, but does
  not justify a fourth pressure, Batch 3b, paid rerun, or runtime/user-facing
  promotion.
- PR 18 prototyped the operator-facing Observatory trace in
  `research/gate4-3case-decision-pressure-observatory-prototype-2026-05-05.md`:
  prototype verdict `observatory_trace_clearer`. The trace shows the same three
  pressures with provenance, source affordances, v4 contribution, suppressed
  candidates, and the PhD competitive-dynamics coverage blank. It is a static
  research artifact, not UI, runtime integration, or user-facing promotion.
- PR 19 defined and validated the dormant trace object in
  `research/decision-pressure-trace-data-shape-2026-05-05.md`: decision label
  `decision_pressure_trace_contract_ready`. The contract adds
  `data/schemas/decision_pressure_trace.schema.json`,
  `engine/system_b/decision_pressure_trace_validation.py`, a PR18 golden
  fixture, and tests for runtime dormancy, three-pressure compression,
  provenance completeness, v4 source-affordance lookup, coverage-transparency
  blanks, suppression references, and principal-agent medium-confidence
  caution.
- PR 20 defines the fixture-only producer/adapter boundary in
  `research/decision-pressure-trace-producer-adapter-plan-2026-05-05.md`:
  decision label `producer_adapter_plan_ready`. Deterministic code may validate,
  normalize, package, or report on reviewed trace fixtures, but must not choose
  semantic pressure quality, invent pressure fields, smooth coverage gaps, or
  render live product surfaces.
- PR 21 adds the fixture-only adapter smoke test in
  `research/decision-pressure-trace-adapter-smoke-test-2026-05-05.md`:
  decision label `fixture_adapter_smoke_ready`. The adapter loads an explicit
  reviewed trace fixture, validates it against compiled v4, and can write a
  review-only report under `.tmp/` when requested. It does not generate
  pressure text, select pressures, render UI, or touch runtime behavior.
- PR 22 records the adapter-report usefulness review in
  `research/decision-pressure-trace-adapter-report-usefulness-review-2026-05-05.md`:
  decision label `adapter_report_useful_as_smoke_guard`. The adapter report is
  useful as review infrastructure and structural drift detection; the main
  product review surface remains the trace fixture and prototype/review docs.
- PR 23 records a no-paid generalization readout in
  `research/decision-pressure-generalization-readout-2026-05-05.md`: decision
  label `generalization_signal_positive_but_not_runtime_ready`. Five archived
  cases outside the original PR13 packet can be compressed into useful
  case-level Decision Pressures, but the result remains reviewed product
  evidence, not runtime or user-facing promotion. PR23 also clarifies that the
  five cases are not deterministic templates. They test whether the reviewed
  surface travels; they do not create case-type routing rules.
- External architecture reference: `gbrain` was reviewed as a mature
  memory/knowledge architecture. The handover in
  `research/gbrain-architecture-learning-handover-2026-05-05.md` captures the
  product translation for Lolla: deterministic tooling should own packet
  assembly, validation, traceability, replay, and maintenance, while LLMs own
  semantic judgment over source-backed operational records.
- External decision-process reference: Shane Parrish's *Clear Thinking* was
  reviewed as a product-value study. The handover in
  `research/clear-thinking-lolla-learning-handover-2026-05-05.md` captures the
  translation for Lolla: the runtime should not only retrieve better knowledge;
  it should leave behind a better decision position, including explicit
  assumptions, missing checks, tripwires, safeguards, and a reviewable decision
  record.
- Combined external-study doctrine: use `gbrain` lessons for the trustworthy
  substrate/runtime discipline; use *Clear Thinking* lessons for the
  decision-note, tripwire, safeguard, and process-record surface.

The schema is still dormant for live `/lolla` behavior. No chat, memo, Pressure
Check, or Lane 4 runtime promotion is justified after PR23. Decision Pressure
is not a new lane; it is a compact synthesis object that can feed Step 6, Step
8 Pressure Check, memo, or Observatory. C-only OOD remains the strongest
evidence mode, but not the only value mode; grounded double-down, confirmation,
and coverage transparency can be product-worthy when concise, actionable, and
dismissible. Batch 3a has now extracted the five targeted coverage patch
records under the PR15 contract, and PR17 found that v4 sharpens the same
Decision Pressure surface without changing selection. PR18 then found that a
manual Observatory trace is clearer when it shows provenance, suppression, and
coverage transparency. PR19 turns that hand-authored trace into a validated,
runtime-dormant `decision_pressure_trace` contract. PR20 defines the boundary
for fixture-only producer/adapter work. PR21 exercises that boundary with a
fixture-only adapter smoke test. PR22 records that the adapter report is useful
as a mechanical smoke guard, not as product-quality review. PR23 then adds
no-paid directional generalization evidence from five fresh archived cases. The
next step, if any, is to review whether the existing
`decision_pressure_trace.v1` contract can represent a multi-case
generalization fixture without bloat or example imitation. This is still not
live Observatory integration.

The post-PR23 deterministic boundary is explicit:

- deterministic code may validate shape, caps, provenance classes,
  source-affordance references, runtime dormancy, coverage gaps, blocked
  surfaces, and review-only drift counts;
- deterministic code must not infer pressures from case type, gap label, route
  label, keywords, or example similarity;
- deterministic code must not rank novelty, tone, actionability, or usefulness;
- deterministic code must not merge semantically similar pressures or smooth
  missing coverage into generic model-name reasoning;
- LLM/reviewer judgment owns semantic selection and wording, while Python owns
  custody, validation, packaging, and drift detection.

---

## 1. Purpose

This document answers a narrower question than the roadmap:

> What would excellent usage of knowledge buried in the canonical markdown files look like, end to end?

The answer is not "retrieve more text."
The answer is not "pick more mental models."
The answer is not "fill every schema field."

Excellent usage means:

1. The source markdown is read with real semantic judgment.
2. Only source-backed knowledge becomes structured substrate.
3. Runtime model activation is based on mechanism fit, not topic or vocabulary overlap.
4. The selected model contributes a specific treatment requirement.
5. The final output either performs that treatment, explicitly sets it aside, or leaves a visible treatment gap.
6. Observatory can show the whole path without relying on memory or trust.

The system should be able to answer:

- Why did this model activate?
- What source-backed affordance did it bring?
- What case evidence supported using it?
- What should Claude or OpenRouter do with it?
- Did the final answer actually use it well?
- If it was not used, was that because it was weak, duplicate, unsafe, or ignored?

The monetizable product standard is stricter than "useful critique":

> Lolla should surface source-backed operational pressure that ordinary strong
> prompting would probably not reach, or explain why no such pressure cleared
> the bar.

This is the difference between a prompt wrapper and a reasoning-audit product.
A strong LLM already knows the central meanings of common mental models. The
affordance schema exists to expose peripheral-but-load-bearing constraints:
`do_not_use_when`, `case_evidence_needed`, treatment requirements, misuse
guards, and dismissal paths.

Prompting tends to pull toward the center of a concept. The substrate should
pull toward the edge conditions where the concept actually bites.

---

## 2. Current Knowledge-Use Chain

The current system already has a strong chain. The new schema should deepen it, not bypass it.

### 2.1 Source Truth

Raw source files currently reside in:

- `data/model_sources/*.md`

They were copied from:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/*.md`

The copied files are governed by `data/model_sources/manifest.json`, including
SHA-256 hashes. These are the semantic root. They include:

- core principles
- playbook material
- application contexts
- strengths and weaknesses
- common anti-patterns
- risks and mitigations
- premortem questions
- allies, antagonists, and structured tensions

### 2.2 Reviewed Curation

Existing curation layers:

- Wave 1: `curation/{model_id}.json`
- Wave 2: `curation/intervention_semantics/{model_id}.json`
- Wave 3: `curation/relation_semantics/{model_id}.json`
- Wave 5: `curation/reframing_semantics/`
- structural coverage routing: `curation/structural_coverage/`

These are operational normalization layers. They are not more authoritative than the source markdown.

### 2.3 Compiled Runtime Artifacts

Current `lolla-skill` runtime reads compiled artifacts such as:

- `data/knowledge_graph.json`
- `data/relationship_graph.json`

These expose:

- model identity
- `select_when`
- `danger_when`
- failure modes
- heuristics
- premortem questions
- relation edges
- reframing routes
- structural coverage routes

The dormant affordance compiler also produces:

- `data/compiled/model_affordances/affordances_v1.json`
- `data/compiled/model_affordances/affordances_v2.json`
- `data/compiled/model_affordances/affordances_v3.json`

These are `draft_review_only` knowledge artifacts. The live runtime must not use
them by default until evaluation earns a specific surface.

### 2.4 Runtime Lanes

Current lanes:

- **Lane 1:** detects cognitive tendency failures, routes to corrective models, builds `DeltaCard`
- **Lane 2:** fingerprints assistant reasoning, verifies active mental models, builds `CompanionCheatSheet`
- **Lane 3:** audits the user's frame, routes frame patterns to models, builds `FramePressureCard`
- **Lane 4:** detects structural dimensions/gaps, routes dimensions to models, builds `StructuralCoverageCard`

### 2.5 Claude Code Synthesis

The `/lolla` skill uses Claude Code as the orchestrator and final synthesis voice:

- Step 2.5: readback
- Step 4: counterargument lead
- Step 6: updated position
- Step 7: pressure-check sub-agents
- Step 8: pressure-check comparison
- Step 8c: memo decision note

OpenRouter owns calibrated semantic boundary calls. Claude Code owns final user-facing synthesis, but must use the audit cards and references as pressure, not as a dashboard to dump.

For formal Gate 4 measurement, OpenRouter remains the measurement boundary for
Arm B/C generation and blinded judging. Codex sub-agents are useful as
reviewer-eye after the measured run, but they should not become the formal
generator or judge unless a real provider adapter, isolation story, telemetry
story, and reproducibility story are built.

---

## 3. What "Good Use" Means

Good use of a mental model is not naming it.

Good use means the model changes one of the following:

- what evidence is required
- what assumption is challenged
- what question should be asked
- what sequence should change
- what threshold or reversal trigger should exist
- what risk treatment is needed
- what option should be set aside
- what alternative mechanism should be considered

If a model does not change any of those, it may still be interesting, but it has not earned runtime weight.

### 3.1 The Model-Use Chain

Every serious use of a model should follow this chain:

```text
source-backed model affordance
  -> runtime activation condition
  -> case evidence quote
  -> treatment requirement
  -> output move
  -> treatment trace
```

If any link is missing, the system should know which link failed.

### 3.2 Mechanism Fit Beats Topic Fit

Bad:

> The case mentions stakeholders, so use Power Dynamics.

Good:

> The advice depends on a party's ability to delay, veto, walk away, force commitment, or privately change the other party's alternatives. Power Dynamics applies because its mechanism is running.

Bad:

> The case mentions time, so use Second Order Thinking.

Good:

> The recommended move creates a local win whose delayed effects could remove a cheap recovery path. Second Order Thinking applies because the downstream chain matters.

### 3.3 Source Support Beats Runtime Desire

Bad:

> Lane 4 would benefit from a crisp diagnostic question, so infer one from the model name.

Good:

> If the source markdown supports a diagnostic question, use it. If not, record absence. The runtime can still work without that model affordance.

### 3.4 Treatment Beats Mention

Bad:

> Mention `Base Rates` in Step 6.

Good:

> Re-anchor the recommendation to the right reference class, identify what denominator is missing, and change confidence or sequencing accordingly. Then name `Base Rates` only if the prose benefits from it.

The product value is the changed treatment, not the displayed model name. A
future CLI/API should be able to prove whether the treatment changed, even when
the final user-facing prose never names the model.

### 3.5 Set-Aside Is A First-Class Outcome

Not every activated model should change the answer.

Good use includes:

- "This model activated, but it is secondary here because another model better explains the same passage."
- "This model is plausible, but the source affordance requires evidence the case does not contain."
- "This pressure is already covered by the existing Pressure Check."
- "This model should stay Observatory-only."

Silent omission is bad. Honest set-aside is good.

### 3.6 Activation Judgment Belongs to the LLM, Not to Python

The `activation_shape` fields — `use_when`, `do_not_use_when`, `case_evidence_needed` — are written in natural language because they require semantic judgment to evaluate. Python must not attempt to match them against case content.

The deterministic system's role in the activation flow is:

1. Route to a model (existing routing mechanisms — tendency lookup, graph traversal, embedding recall).
2. Look up the affordance record for that model by ID.
3. Deliver the record to the LLM consumer.

The LLM reads both the affordance record and the case. It decides whether `use_when` conditions are met, whether `do_not_use_when` guards apply, and whether the necessary case evidence is present. This applies at every consumer:

- **OpenRouter boundary call:** receives the affordance record as part of the judgment packet; decides activation through semantic reading of the case.
- **Claude Code Step 6:** receives selected affordance records as treatment contracts; applies or sets aside based on its reading of the case.
- **Treatment audit:** receives affordance records alongside output; LLM judge determines whether treatment was performed.

None of these consumers should receive Python pre-evaluations of activation conditions. The right design is rich material delivered cleanly, not partially digested conclusions delivered as if they were facts.

This distinction is what keeps the deterministic middle from drifting into a brittle, bloated, case-by-case approximation of the LLM's judgment. The system has a smart LLM. Use it for semantic work. Use Python for structural work: routing, retrieval, deduplication, budget enforcement, and trace assembly.

### 3.7 Decision Pressure Beats Better Wording

The current Gate 4 experiment sharpened and then reframed the evaluation
standard.

An enriched output does not pass merely because it is clearer, more specific, or
longer than the baseline. It passes only if it improves the user's decision
position without noise, bloat, or fake confidence.

PR 11 originally added:

- `out_of_distribution`
- `out_of_distribution_arms`
- C-only OOD summaries
- C-included OOD summaries
- OOD-by-source summaries

Those fields remain useful for measurement. C-only OOD remains the cleanest
evidence that the affordance kernel adds signal beyond a strong model-name
prompt.

But the 3-case product readout showed that C can be valuable even when B has
the general idea. The accepted product value modes are now:

- `new_edge`: C adds a pressure B did not substantially provide.
- `grounded_double_down`: B had the general idea, but C operationalizes it with
  evidence, dismissal, treatment discipline, or a concrete gate.
- `confirmation`: B and C converge, increasing confidence that this is a real
  pressure point.
- `coverage_transparency`: C honestly says no substrate-backed edge is
  available instead of faking traceability.

`grounded_double_down` only counts if C changes the user's next action,
evidence standard, dismissal path, tripwire, sequencing, or decision record.
Better wording alone does not count.

`confirmation` usually affects prioritization rather than creating another
user-visible pressure. It is user-visible only when convergence changes
priority, confidence, or the user's willingness to act without another check.

The highest-value pressures should trace to:

- `do_not_use_when`
- `case_evidence_needed`
- `treatment_requirement`
- `misuse_guard`

Pressures traced mainly to `diagnostic_question`, `mechanism`, or
`model_general_knowledge` are weaker. They may still be useful, but they do not
prove the extracted affordance kernel is adding much beyond normal LLM priors.

The user-facing shape should not be raw probes. It should be a compact Decision
Pressure object:

- `pressure`
- `what_to_verify`
- `why_it_matters`
- `dismiss_if`
- `tripwire_or_next_action`
- `coverage_status`

Each field should carry or imply a provenance class:

- `source_backed`
- `case_grounded`
- `llm_synthesized`
- `user_to_verify`

This matters especially for `dismiss_if`, `tripwire_or_next_action`, and
`coverage_status`. A neat dismissal path or tripwire that lacks provenance is
fake precision.

---

## 4. When Knowledge Should Be Used

The same source-backed knowledge should not be used the same way everywhere. The schema must support different consumers.

### 4.1 Offline Extraction Time

Purpose:

- convert buried markdown into reviewed structured substrate

Consumer:

- LLM extractor
- human/code reviewer
- compiler

Input:

- full source markdown
- existing Wave 1-3 curation
- target schema

Output:

- affordance records
- absence records
- provenance
- quality notes

Rule:

- broad source reading is allowed here because this is offline substrate work

### 4.2 OpenRouter Boundary Calls

Purpose:

- make narrow semantic judgments about the current conversation

Consumer:

- extraction call
- Lane 1 tendency triage/deep checks
- Lane 2 fingerprint/verification
- Lane 3 frame extraction
- Lane 4 classification/dimension detection/gap question generation
- future model-treatment audit

Input:

- compact candidate list
- strict schema
- source/context split
- exact evidence quote requirements where possible
- source-backed affordance snippets only when relevant

Output:

- typed JSON
- evidence quotes
- accepted/rejected items
- confidence and reasons

Rule:

- OpenRouter should not receive the whole knowledge base. It should receive a narrow packet that makes the judgment possible and inspectable.

### 4.3 Deterministic Middle

Purpose:

- route, filter, dedupe, trace, budget, and compile pressure packets

Consumer:

- pipeline code
- Observatory
- Claude Code synthesis

Input:

- boundary outputs
- compiled knowledge graph
- model affordance layer
- relation graph
- anti-echo state

Output:

- selected model IDs
- selected affordance IDs
- exclusions
- why-not trace
- pressure packets

Rules:

- The deterministic middle should not invent semantics. It should preserve and select among reviewed semantic objects.
- For affordance records specifically: retrieve the record by model ID and deliver it to the LLM consumer. Do not evaluate `use_when`, `do_not_use_when`, or `case_evidence_needed` conditions against case content. Do not validate `treatment_requirements` by pattern matching. Activation judgment is a semantic task — it belongs to the LLM, not to Python.

### 4.4 Claude Code Step 6

Purpose:

- produce the updated position

Consumer:

- user
- memo renderer
- Observatory

Input:

- extraction
- four audit cards
- companion anchors
- selected affordance/treatment packet if future work earns it
- voice and output rules

Output:

- revised answer with what survived, what was set aside, what shifted

Rule:

- Claude should receive compact treatment requirements, not raw source files. It should reason from cards and source-backed packets, then write user-facing prose with no machinery leaks.

### 4.5 Claude Code Step 7/8 Pressure Check

Purpose:

- break Step 6 anchoring and catch missed shifts

Consumer:

- Step 8 comparison
- memo note

Input:

- decision structure
- one lane packet per isolated review
- future: affordance pressure packet only if it adds non-duplicative value

Output:

- concrete divergences

Rule:

- pressure-check material should ask "what should shift?" not "what is interesting?"

### 4.6 Observatory

Purpose:

- inspect the system
- debug routing and treatment
- compare proposed lenses against the baseline

Consumer:

- operator/maintainer
- future validation agents

Input:

- everything, including fields that are not user-facing

Output:

- trace surfaces
- route graph
- why-not decisions
- treatment audit
- source provenance

Rule:

- Observatory is where experimental knowledge-use fields belong first.

### 4.7 User-Facing Chat And Memo

Purpose:

- give the user a better decision artifact

Consumer:

- user

Input:

- final compressed synthesis only

Output:

- updated position
- pressure check
- memo decision note

Rule:

- no affordance field names, schema names, route traces, lane names, or debug vocabulary. User-facing promotion only happens after baseline comparison proves value.

---

## 5. Target Schema Family

We should not create one giant schema. We need a small family of schemas that match the lifecycle.

### 5.1 `ModelSourceRecord`

Purpose:

- identify the model and source state

Shape:

```json
{
  "model_id": "theory-of-constraints",
  "display_name": "Theory Of Constraints",
  "source_file": "Theory_Of_Constraints_rag.md",
  "source_path": "/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Theory_Of_Constraints_rag.md",
  "source_hash": "sha256:...",
  "source_status": "available",
  "curation_status": {
    "wave1": "available",
    "wave2": "available",
    "wave3": "available"
  },
  "notes": []
}
```

Rules:

- `source_status` may be `available`, `missing`, `source_too_thin`, or `deferred`.
- A missing/thin source is not a validation failure by itself.

### 5.2 `SourceEvidenceSpan`

Purpose:

- make every semantic extraction auditable

Shape:

```json
{
  "source_file": "Theory_Of_Constraints_rag.md",
  "source_quote": "Before committing: what is the single measured limit that would still cap throughput if every local improvement in this plan succeeded next week?",
  "section_hint": "Risks and Mitigations",
  "extraction_type": "explicit",
  "confidence": "high"
}
```

Rules:

- `source_quote` must be an exact substring of the source markdown.
- `extraction_type` should be `explicit`, `normalized`, or `not_supported_by_source`.
- `confidence` should be `high`, `medium`, `weak`, or `not_applicable`.

### 5.3 `ModelAffordanceRecord`

Purpose:

- capture what a source-backed model can operationally do for the runtime

Shape:

```json
{
  "model_id": "theory-of-constraints",
  "affordance_id": "theory-of-constraints.constraint-proof-before-optimization",
  "status": "supported",
  "name": "Constraint proof before optimization",
  "mechanism": "The model forces the plan to prove the binding throughput limit before optimizing visible work.",
  "activation_shape": {
    "use_when": [
      "The advice optimizes a visible painful step without proving it is the binding constraint.",
      "The plan adds work, people, or process before naming the capacity limit."
    ],
    "do_not_use_when": [
      "The source case has no throughput, dependency, queue, capacity, or scarce-resource structure.",
      "The answer already proves and measures the binding constraint."
    ],
    "case_evidence_needed": [
      "a proposed intervention",
      "a possible bottleneck or scarce capacity",
      "evidence that non-bottleneck work may consume attention or resources"
    ]
  },
  "treatment_requirements": [
    {
      "requirement_id": "name-binding-constraint",
      "description": "Name the single constraint that still caps the outcome if local improvements succeed.",
      "evidence_required": [
        "constraint name",
        "metric or observable limit",
        "dependency controlled by the constraint"
      ],
      "good_output_shape": [
        "The binding constraint is X, not Y.",
        "The first metric that should move is Z.",
        "Stop or subordinate A until X moves."
      ]
    }
  ],
  "diagnostic_questions": [
    "What measured limit would still cap throughput if every local improvement succeeded next week?",
    "If this bottleneck moved, what would become the next cap within two weeks?"
  ],
  "misuse_guards": [
    "Do not mistake visible work for the binding constraint.",
    "Do not keep fixing the old constraint after the constraint moves."
  ],
  "source_evidence": [
    {
      "source_file": "Theory_Of_Constraints_rag.md",
      "source_quote": "Before committing: what is the single measured limit that would still cap throughput if every local improvement in this plan succeeded next week?",
      "section_hint": "Risks and Mitigations",
      "extraction_type": "explicit",
      "confidence": "high"
    }
  ],
  "review_notes": {
    "normalization_note": "Merged the source's constraint-proof and visible-work warnings into one operational affordance.",
    "dropped_material": [],
    "open_questions": []
  }
}
```

Allowed `status` values:

- `supported`
- `weak_support`
- `not_supported_by_source`
- `source_too_thin`
- `duplicate_of_existing_field`
- `deferred_for_review`

Rules:

- `status != supported` records are allowed.
- A `not_supported_by_source` record should not contain invented treatment requirements.
- `weak_support` records may compile for Observatory but should not affect runtime by default.

### 5.4 `KnowledgeUsePacket`

Purpose:

- the compact object passed to runtime consumers after routing

Shape:

```json
{
  "packet_id": "run123.lane4.feedback-system-dynamics.second-order-thinking",
  "consumer": "lane4_gap_questions",
  "model_id": "second-order-thinking",
  "affordance_id": "second-order-thinking.recovery-path-check",
  "route_source": {
    "lane": "structural_coverage",
    "route_reason": "uncovered feedback-system-dynamics gap",
    "dimension_id": "feedback-system-dynamics",
    "candidate_rank": 2,
    "anti_echo_status": "not_excluded"
  },
  "runtime_evidence": {
    "case_quote": "exact user or assistant quote when available",
    "evidence_source": "user_turn",
    "fit_note": "The user's deadline makes sequencing and disappearing recovery paths material."
  },
  "treatment_payload": {
    "one_sentence_pressure": "Test whether the recommended sequence removes the cheap recovery path before the hidden dependency surfaces.",
    "questions": [
      "Which later dependency becomes harder to reverse because this move happens now?",
      "What is the first signal that the cheap recovery path has disappeared?"
    ],
    "avoid": [
      "Do not invent long second-order chains without a named mechanism."
    ]
  },
  "surface_policy": {
    "observatory": true,
    "openrouter_prompt": true,
    "claude_step6": false,
    "pressure_check": false,
    "memo": false
  }
}
```

Rules:

- This is what runtime should consume, not the full source markdown.
- `surface_policy` defaults to Observatory-only until evaluation proves value.
- `consumer` should be explicit so packets do not drift into every prompt.

### 5.5 `RuntimeModelUseTrace`

Purpose:

- show how a model or affordance moved through the run

Shape:

```json
{
  "model_id": "second-order-thinking",
  "affordance_id": "second-order-thinking.recovery-path-check",
  "run_id": "20260504T000000Z",
  "events": [
    {
      "stage": "lane4_route",
      "status": "candidate",
      "reason": "feedback-system-dynamics gap routed to second-order-thinking"
    },
    {
      "stage": "anti_echo",
      "status": "kept",
      "reason": "not already covered by lanes 1-3"
    },
    {
      "stage": "gap_question_generation",
      "status": "used",
      "reason": "affordance questions included in prompt packet"
    },
    {
      "stage": "step8_pressure_check",
      "status": "not_surfaced",
      "reason": "existing pressure check already covered disappearing fallback"
    }
  ]
}
```

Rules:

- The trace should distinguish candidate, selected, excluded, used, surfaced, and set aside.
- This is Observatory/debug data, not user copy.

### 5.6 `ModelTreatmentAudit`

Purpose:

- judge whether selected model affordances were actually treated in final outputs

Shape:

```json
{
  "run_id": "20260504T000000Z",
  "audited_output": "revised_answer",
  "items": [
    {
      "model_id": "theory-of-constraints",
      "affordance_id": "theory-of-constraints.constraint-proof-before-optimization",
      "treatment_status": "treated",
      "output_quote": "The real bottleneck is not literature search time; it is whether Silva can provide data access and co-advising terms.",
      "treatment_note": "The revised answer names the binding constraint and changes sequencing around it.",
      "missing_requirements": [],
      "duplicate_of_existing_pressure": false,
      "confidence": "high"
    }
  ]
}
```

Allowed `treatment_status` values:

- `treated`
- `partially_treated`
- `set_aside_with_reason`
- `duplicate_existing_pressure`
- `not_treated`
- `not_applicable`

Rules:

- This audit likely needs a narrow LLM judge, because treatment is semantic.
- The judge must quote the output passage used as evidence.
- The audit should remain Observatory-only until it proves user value.

### 5.7 `AbsenceRecord`

Purpose:

- preserve honest gaps without making them look like failures

Shape:

```json
{
  "model_id": "some-model",
  "attempted_field": "diagnostic_questions",
  "status": "not_supported_by_source",
  "reason": "The source explains the model conceptually but does not provide operational diagnostic prompts.",
  "source_evidence": [
    {
      "source_file": "Some_Model_rag.md",
      "source_quote": "closest relevant source quote if useful",
      "extraction_type": "not_supported_by_source",
      "confidence": "medium"
    }
  ],
  "runtime_policy": "do_not_promote"
}
```

Rules:

- Absence records are part of the substrate.
- They prevent future agents from repeatedly trying to fill the same unsupported slot.
- They help the compiler report current corpus state honestly.

---

## 6. Prompting Implications

The schema should change how we prompt both OpenRouter and Claude Code.

### 6.1 OpenRouter Prompting

OpenRouter calls should receive:

- the narrow task
- the exact allowed schema
- relevant candidate models or affordances only
- source/context separation
- explicit acceptance and rejection rules
- exact evidence quote requirement where possible

OpenRouter calls should not receive:

- the entire model corpus
- all affordances for all models
- raw source markdown at runtime
- vague instructions like "use the knowledge base"

Good OpenRouter prompt pattern:

```text
You are judging whether this candidate affordance is active in this conversation.
Accept only if the case evidence instantiates the affordance mechanism.
Reject if the passage is merely compatible, topical, or vocabulary-overlapping.
Return accepted/rejected with exact evidence quotes from SOURCE.
```

This mirrors the existing Lane 2 verification discipline:

- accept executed model only when mechanism runs
- accept violated model only when substitute mechanism is visible
- reject compatible-but-generic models
- reject vocabulary-only matches
- require exact evidence quotes

### 6.2 Claude Code Step 6 Prompting

Claude Code should receive treatment packets only after the pipeline has selected them.

Good shape:

```text
The selected model pressure is not a conclusion. It is a treatment requirement.
For each selected affordance:
- either perform the required move,
- set it aside with a reason,
- or leave it for Pressure Check if it is a real divergence.
Do not mention affordance IDs or schema names.
```

Bad shape:

```text
Here are 30 model affordances. Use them to improve the answer.
```

That turns the source substrate into fog.

### 6.3 Claude Code Step 7/8 Prompting

Pressure-check agents should receive:

- one lane's evidence
- selected treatment requirements if they are material
- the synthesized position
- the question "what should shift?"

They should not receive:

- every source-backed affordance
- every rejected model
- graph details

### 6.4 Memo Prompting

The memo should not have a separate affordance section.

If affordance material ever earns user-facing promotion, it should appear as:

- a changed action
- a changed threshold
- a changed sequence
- a changed condition
- a changed risk treatment
- a changed decision question

No model affordance machinery in the memo.

---

## 7. Model Selection Rules

The schema should support model selection by mechanism fit.

### 7.1 Accept A Model When

Accept when:

- the case evidence instantiates the model's mechanism
- the source-backed activation shape fits
- the model would change a treatment requirement
- the evidence quote is specific enough
- no narrower model already explains the same passage better

### 7.2 Reject A Model When

Reject when:

- it is merely topical
- it is vocabulary overlap
- it is a broad-overlay model piggybacking on a specific model's passage
- it is compatible but not diagnostic
- the source-backed affordance requires evidence the case lacks
- it duplicates existing Pressure Check material
- it is interesting but not decision-changing

### 7.3 Prefer The Narrower Mechanism

If two models explain the same passage:

- prefer the narrower, more diagnostic model
- keep the broader model only if it has a distinct passage or distinct treatment requirement
- record broad-model suppression in the why-not trace

This preserves the current Lane 2 anti-overclaim discipline.

### 7.4 Keep Broad Models On A Short Leash

Models like `systems-thinking`, `second-order-thinking`, and `multi-criteria-decision-analysis` are useful but dangerous because they can explain almost anything.

They should require:

- distinct runtime evidence
- specific affordance match
- explicit treatment requirement
- no piggybacking on a narrower model's passage

---

## 8. Surface Policy

Every schema object should carry or imply a surface policy.

Default:

- Observatory: yes
- compiled artifact: yes if reviewed
- OpenRouter prompt: only when selected and task-relevant
- Claude Step 6: only after evaluation
- Pressure Check: only after evaluation
- memo: only after evaluation
- user chat: only as compressed decision movement, never as schema vocabulary

This prevents PR #74's failure mode: technically valid material drifting into user-facing synthesis before baseline value is proven.

Current surface policy as of 2026-05-05:

- v3 affordance records: compiled and reviewable, not live runtime material.
- Gate 4 packets: evaluation-only, under `.tmp/` or `data/evaluations/`.
- Chat/memo/Pressure Check: no affordance surfacing yet.
- Observatory: acceptable first surface for route/treatment inspection.
- CLI/API future: artifact-first, not prose-first.

The future CLI should expose a stable audit bundle:

```bash
lolla audit \
  --conversation conversation.txt \
  --output ./lolla-run \
  --surface memo,observatory,json
```

The CLI should own packet assembly, validation, tracing, archive, cost, and
rendering. It should not pretend to understand source markdown mechanically.
The LLM reads; Python preserves and verifies.

---

## 9. Evaluation Standard

The new schema should be judged by whether it improves knowledge use, not by field coverage.

### 9.1 Substrate Evaluation

Ask:

- Are records source-backed?
- Are unsupported fields left absent?
- Are source quotes exact?
- Are normalized fields faithful?
- Are broad models kept specific?
- Are generic records rejected?

### 9.2 Runtime Evaluation

Ask:

- Did selected affordances match case evidence?
- Did they improve model routing or why-not visibility?
- Did they sharpen Lane 4 gap questions?
- Did they catch missed treatment in Step 6?
- Did they avoid duplicating existing Pressure Check?

### 9.3 User-Value Evaluation

Ask:

- Did the user-facing answer change in a useful way?
- Did it change action, threshold, sequence, condition, risk, or decision question?
- Did it stay concise?
- Did it avoid machinery leaks?
- Did it beat the existing baseline?

If user-value evidence is weak, keep the schema Observatory-only.

### 9.4 Decision Pressure Product Evaluation

For monetizable runtime promotion, ask the product question:

- Did the affordance-enriched material improve the user's decision position?
- Was the improvement a `new_edge`, `grounded_double_down`, `confirmation`, or
  `coverage_transparency`?
- Did the pressure trace to high-value affordance fields?
- Did the edge change an action, threshold, sequence, condition, risk treatment,
  fallback, evidence requirement, option set, or decision question?
- Did it include a dismissal path?
- Did it avoid sophistication theater?
- Did it avoid fake coverage traces?
- Did it change what the user should verify, delay, test, document, monitor,
  dismiss, or stop?

Gate 4 should now be read this way:

- **C-only OOD:** cleanest evidence that the affordance kernel adds signal.
- **Grounded double-down:** useful when C turns B's broad concern into evidence,
  dismissal, tripwire, or treatment discipline.
- **Confirmation:** useful when convergence helps prioritize a real pressure.
- **Coverage transparency:** useful when C refuses to fake substrate-backed
  grounding.
- **Noise/bloat:** suppress or merge.
- **Fake trace:** hard rejection.

The schema earns live runtime weight only when raw enriched probes can be
compressed into a small Decision Pressure surface that reviewer-eye would show
to a real user. Normal user-facing target is 1-3 total pressures per run, with
additional valid material kept in Observatory/operator surfaces.

Zero-output success is allowed:

> No additional source-backed pressure cleared the bar.

That is preferable to padding the user experience with weak pressure.

---

## 10. First Implementation Slice

This section is historical. The first implementation slice is done.

Before extracting any real model affordances across the corpus, implement the schema and fixtures.

Suggested PR:

**PR 1: Knowledge Use Schema And Validation Fixtures**

Files:

- `references/model-affordance-extraction.md`
- `data/schemas/model_affordance.schema.json`
- `data/model_affordances/fixtures/theory_of_constraints_valid.json`
- `data/model_affordances/fixtures/generic_invalid.json`
- `data/model_affordances/fixtures/missing_source_quote_invalid.json`
- `data/model_affordances/fixtures/source_too_thin_valid.json`
- `tests/test_model_affordance_schema.py`

The valid thin fixture is important. It proves we are not building completeness theater.

### 10.1 Minimal Schema Requirements For PR 1

The schema should support:

- `model_id`
- `source_file`
- `status`
- `affordances[]`
- `absence_records[]`
- `source_evidence[]`
- `review_notes`

Each affordance should support:

- `affordance_id`
- `name`
- `mechanism`
- `activation_shape`
- `treatment_requirements`
- `diagnostic_questions`
- `misuse_guards`
- `source_evidence`
- `confidence`

Each absence record should support:

- `attempted_field`
- `status`
- `reason`
- `runtime_policy`
- optional `source_evidence`

### 10.2 Validation Rules For PR 1

Tests should prove:

- a strong source-backed record validates
- a generic record fails
- a missing source quote fails
- a `source_too_thin` record validates
- an affordance with no source evidence fails
- an affordance with unknown status fails
- a supported record with zero affordances fails unless it carries an absence reason

This creates the rails before the extraction work begins.

### 10.3 Current Implementation Slice

The current slice is no longer schema creation or more paid Gate 4 calibration.
It is complete through the PR23 no-paid generalization readout and
anti-casuistry lock.

Current task:

1. Default to `stop_and_review_after_pr23`.
2. Preserve the three selected Decision Pressure clusters from PR13/PR14.
3. Keep PR17's decision label: `v4_improves_fields_without_changing_selection`.
4. Treat PR18's Observatory trace as the manual prototype baseline.
5. Keep coverage transparency visible, especially the PhD competitive-dynamics
   zero-output.
6. Preserve PR19's runtime-dormant `decision_pressure_trace` contract before
   any UI or runtime work.
7. Treat PR20's producer/adapter plan as a boundary, not as a producer.
8. Treat PR21's adapter smoke test as review infrastructure, not live product.
9. Treat PR22's usefulness review as a smoke-guard conclusion, not as
   permission for a package function.
10. Treat PR23's generalization readout as directional product evidence, not
   as runtime evidence, deterministic case logic, or permission for PR24.
11. Keep field-level provenance, global compression, zero-output success, and
   action-delta requirements explicit.
12. Preserve coverage honesty and no-casuistry rails.
13. Do not run more paid model calls until the surface is reviewed.
14. Do not start package functions, UI, trace-fixture stress tests, new adapter
   work, Batch 3b, prompt changes, or runtime work by default.

Do not expand the corpus or wire live runtime behavior until this surface is
specified, reviewed, and then tested against product-value evidence.

---

## 11. Final Schema Principle

The schema is not there to make the knowledge base look complete.

The schema is there to preserve the full path from source-backed knowledge to runtime judgment:

```text
source truth
  -> reviewed semantic affordance
  -> runtime activation fit
  -> selected treatment requirement
  -> Claude/OpenRouter prompt packet
  -> final output treatment
  -> Observatory trace
```

If the source does not support a link, stop and record the absence.

If a model is interesting but not decision-changing, keep it out of user output.

If a schema field would make the corpus smoother but less true, leave it blank.

The knowledge base should stay sharp, uneven, and honest. The system should be designed around that reality.

The updated 2026-05-05 product principle:

```text
source truth
  -> reviewed affordance
  -> routed candidate
  -> LLM activation judgment
  -> OOD operational edge test
  -> treatment trace
  -> selective product surfacing, only if earned
```

The system is not trying to out-answer frontier models. It is trying to show
what fluent, confident AI advice failed to check.
