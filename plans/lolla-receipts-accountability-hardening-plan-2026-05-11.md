# Lolla Receipts And Accountability Hardening Plan

Date: 2026-05-11  
Status: Implemented first hardening pass; ready for team review  
Scope: First hardening pass after the independent architecture audit  

## Implementation Notes

The first pass followed the plan with a few concrete choices now reflected in code:

- Lane 4 uses `run_structural_coverage_with_traces_from_ir(...)` so classification, detection, and gap-question calls emit distinct traces at call time.
- Extraction uses a central `_emit_result(...)` path for edge exits and treats no-header transcripts ending on a user turn as critical.
- V60 writes a deterministic consideration ledger skeleton; validation now checks card/model/chunk identity, route/disposition compatibility, used-visible/private effects, and absence blocker/boundary fields.
- Run health now has `issue_details[]` with severity, axis, and trust impact. Optional embeddings-off remains visible without degrading the run; missing/invalid V60 ledgers and product-output leaks degrade.
- Archive finalization scans product outputs (`revised.txt`, `memo.md`, `memo_note.json`) and records `product_output_hygiene` plus `run_health.product_output_*`.
- V60 chunk selection is no longer `record_order_first` by default. It uses local relevance within each model record, records fallback when needed, and labels selected chunk effect types.
- `scripts/compare_archived_runs.py` now provides a health-first Markdown/JSON comparison surface for archived runs.
- Post-flight live testing exposed two idempotency bugs and one UX gap. V60 finalization and product-output hygiene finalization now clear stale issue state before re-validating. `scripts/finalize_v60_telemetry.py --require-valid` is the required stop gate before pressure checks, memo rendering, Observatory, or archive. The older instruction to launch pressure-check agents before Step 6 was removed because it contradicted that gate.
- Live Claude Code narration is now treated as product surface in the orchestration docs. The scanner flags observed leak patterns such as `Beat 2`, `pressure-check agents`, `V60`, and `ledger` when they appear on a product surface; normal public phrases such as `pressure check` remain allowed.
- V60 local-relevance telemetry now filters more explanatory stopwords so selection reasons are less likely to cite non-informative overlap terms such as `after`, `all`, `before`, `being`, or `should`.

## Executive Stance

The next danger is false confidence, not failed execution.

V60 can run. The pipeline can archive. Observatory can show panels. A ledger can validate. A memo can render. That is not enough. The system has to prove that its receipts are true before we use those receipts to compare live runs or claim product improvement.

This plan therefore prioritizes:

1. Trace truth before comparison.
2. Capture/output consistency before product-health claims.
3. Ledger accountability before V60 success claims.
4. Health severity before operator decisions.
5. Product-output cleanliness before calling a run user-safe.
6. Selection quality before increasing context caps.
7. Comparison only after the underlying signals are trustworthy.

## Shared Invariant

The target invariant should not be "V60 was used."

The target invariant should be:

> Lolla captures the conversation, produces deterministic and probabilistic reasoning opportunities with inspectable custody, privately presents selected source-backed material to the runner, lets the runner accept, reject, defer, or keep material private without forcing theater, records what happened truthfully, and keeps user-facing output clean.

The current system has the bones of this invariant. The weak parts are trace truth, extraction edge-path consistency, ledger quality, absence selection, health semantics, and product-surface enforcement.

## Alignment And Pushback

### Agreed

- Lane 4 telemetry is P0. If call traces are stale, costs and payloads can look precise while being false.
- Extraction edge paths are not polish. A bad capture that escapes as `unknown` or fails to write the requested output file can poison downstream health.
- V60 selection is transparent but too coarse. `record_order_first` is custody, not reasoning-grade selection.
- The V60 ledger is currently accounting, not proof of useful thought.
- Health semantics are too blunt. Optional embeddings-off should not share severity with broken capture or missing active-V60 ledger.
- Qt/app claim checks out: no Qt app was found. Current product surfaces are skill chat, deterministic memo, archive folders, Observatory, and the sibling Svelte Observatory app.

### Pushback

- Product-output hygiene should not wait until late P2 if archives are being used as evidence. It is cheap, local, and directly affects whether a run is product-safe. I would make it P1 or a parallel P0.5 gate after trace/capture fixes.
- Comparison should not be a feature sprint until P0/P1 receipts are fixed. Build a small archive comparison report first; only then invest in Observatory UI.
- Do not add a second LLM judge as the first ledger-quality solution. It may help later, but it can create another opaque "looks evaluated" layer before deterministic consistency checks are in place.
- Absence records are not only a V60 selection issue. They also require ledger semantics. If a selected absence is marked `used`, the ledger should say what overclaim it blocked or what uncertainty boundary it enforced.

## Workstream 1: Lane 4 Boundary Trace Truth

Priority: P0  
Primary files:

- `engine/system_b/structural_coverage.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/boundary_tracing.py`
- `tests/test_structural_coverage_contextual.py`
- likely new or updated pipeline telemetry regression test

### What We Are Trying To Solve

Lane 4 makes multiple LLM calls inside `run_structural_coverage_from_ir`: question classification, dimension detection, and sometimes gap-question generation. The pipeline currently captures only two traces after the lane function returns. Because `_capture_boundary_call` reads `boundary.last_call_metadata`, those traces can point to the last call rather than the intended stage.

The result: Observatory and `usage_summary` can display incorrect payloads, token counts, and costs for structural coverage stages.

### Why This Is A Problem

This breaks the core receipt model. The operator believes they are seeing stage-level evidence, but the trace can be stale. If we compare two runs using this telemetry, we are comparing partly fictional traces.

### Candidate Fixes

#### Option A: Return Stage Traces From Structural Coverage

Change Lane 4 orchestration so the structural coverage module captures metadata immediately after each LLM call and returns it alongside the `StructuralCoverageCard`.

Possible shape:

```python
@dataclass(frozen=True)
class StructuralCoverageRun:
    card: StructuralCoverageCard | None
    boundary_calls: tuple[BoundaryCallTrace, ...]
```

Then `pipeline._run_lane4_structural_coverage` appends the returned traces instead of reading `last_call_metadata` after the fact.

Pros:

- Directly fixes the stale metadata bug.
- Keeps stage labels close to the calls.
- Low conceptual risk.
- Testable with fake boundaries that return distinct payloads/tokens per call.

Cons:

- Changes a public-ish return shape.
- Requires compatibility care for direct callers/tests of `run_structural_coverage_from_ir`.

#### Option B: Add Global Boundary Auto-Tracing

Teach the boundary client to append a trace on every `run_json` call, probably through a stage context manager or explicit `stage=` argument.

Pros:

- Solves this class of bug everywhere.
- Reduces manual capture footguns.
- Long-term clean architecture.

Cons:

- Bigger refactor.
- Requires stage propagation across all lanes.
- Risky before we stabilize the current telemetry.

#### Option C: Wrap The Boundary During Lane 4

In `pipeline._run_lane4_structural_coverage`, pass a proxy boundary that intercepts each `run_json` call, captures metadata immediately, and labels calls by call order.

Pros:

- Minimal changes to `structural_coverage.py`.
- Can be implemented quickly.

Cons:

- Labels are order-dependent.
- If Lane 4 call sequence changes, labels can become wrong again.
- This fixes the symptom while preserving an awkward hidden-call contract.

### Selected Approach

Choose Option A now. Consider Option B later as a broader boundary-tracing refactor.

Lane functions that hide multiple LLM calls should return their own traces. That is the most direct way to make receipts true without global churn.

### Implementation Plan

1. Add a `StructuralCoverageRun` or equivalent internal result object.
2. Capture stage metadata immediately after:
   - `run_question_classification_from_packet`
   - `run_dimension_detection_from_packet`
   - `generate_gap_questions_from_packet`, when called
3. Return both `card` and `boundary_calls`.
4. Update `pipeline._run_lane4_structural_coverage` to append returned traces.
5. Preserve a compatibility function if needed:
   - `run_structural_coverage_from_ir(...) -> StructuralCoverageCard | None`
   - `run_structural_coverage_with_traces_from_ir(...) -> StructuralCoverageRun`
6. Add regression tests proving traces are distinct.

### Acceptance Criteria

- A Lane 4 run with gaps records three distinct stages:
  - `structural_coverage_classification`
  - `structural_coverage_detection`
  - `structural_coverage_gap_questions`
- A Lane 4 run without gaps records two distinct stages.
- Stage traces contain distinct raw payloads when the fake boundary returns distinct payloads.
- Token/cost attribution in `usage_summary` uses those distinct traces.
- No pipeline code captures Lane 4 traces by reading `last_call_metadata` after the lane returns.

### Avoid

- Do not infer stage labels purely from call order in production code.
- Do not call the bug fixed if Observatory looks different but `usage_summary` still receives stale traces.

## Workstream 2: Extraction Output Consistency And Capture Criticality

Priority: P0  
Primary files:

- `scripts/run_extract.py`
- `tests/test_run_extract.py`
- `engine/system_b/conversation_loader.py`, only if loader behavior needs compatibility coverage

### What We Are Trying To Solve

Every extraction exit path should produce a durable output when `--output-file` is provided, and every output should carry capture diagnostics. Malformed capture ending on a user turn should be critical even without a parseable `CONVERSATION:` header.

### Why This Is A Problem

Extraction is the front door for all later reasoning. If an early exit prints to stdout but does not write the output file, the orchestrator or archive path can lose the reason. If a missing header downgrades a final-user-turn capture to `unknown`, the system can audit an incomplete assistant answer without loud failure.

### Candidate Fixes

#### Option A: Centralize Extraction Result Writing

Create a helper that merges capture diagnostics into every result and writes to `--output-file` before returning.

Possible helper:

```python
def _emit_result(payload: dict, *, output_file: str | None, capture_result: dict) -> None:
    payload.update(capture_result)
    print(json.dumps(payload))
    if output_file:
        Path(output_file).write_text(json.dumps(payload, indent=2))
```

Pros:

- Low-risk patch.
- Makes edge-path behavior consistent.
- Easy to test.

Cons:

- Keeps `main()` branchy.

#### Option B: Introduce A Canonical ExtractionExit Object

Represent every exit as a structured object with status, code, payload, capture diagnostics, and output-writing behavior.

Pros:

- Cleaner long-term control flow.
- Reduces future branch drift.

Cons:

- Larger refactor for a small but important bug.
- More surface area for accidental behavior changes.

#### Option C: Patch Only The Two Known Branches

Add output-file writes to `not_strategic` and missing-required-field branches.

Pros:

- Fastest.

Cons:

- Leaves the underlying footgun.
- Future branches can repeat the same mistake.

### Selected Approach

Choose Option A now. It is the smallest fix that changes the pattern, not just the two symptoms.

### Capture Criticality Options

#### Option A: Critical Warnings Override Missing Header

If turn markers show the last turn is `USER`, return `capture_health: "critical"` even when the header is missing. If the header is missing but the last turn is assistant, return `unknown` or `degraded` with warnings.

Pros:

- Preserves the strongest safety rule.
- Avoids auditing incomplete answers.
- Minimal behavior change.

Cons:

- `unknown` no longer always means "no critical condition found."

#### Option B: Missing Header Is Always Degraded

If there is no parseable header, never return `unknown`; return `degraded` unless a critical condition is found.

Pros:

- More conservative.
- Operators cannot mistake missing header for harmless unknown.

Cons:

- More behavior change.
- Some old ad hoc transcripts may become degraded even if usable.

#### Option C: Missing Header Is Always Critical

Require header for all production extraction.

Pros:

- Strong discipline.

Cons:

- Too strict for old fixtures/manual debugging.
- Could block useful recovery paths.

### Selected Capture Approach

Choose Option A now. Consider Option B after reviewing archived/manual transcript usage.

### Implementation Plan

1. Add `_emit_result` or equivalent helper.
2. Use it for success, `capture_critical`, `not_strategic`, missing required fields, and API error outputs.
3. Update no-header capture validation so final user turn remains critical.
4. Add tests:
   - `not_strategic` writes output file and includes capture diagnostics.
   - missing required fields writes output file and includes capture diagnostics.
   - no-header transcript ending on user turn is critical.
   - no-header transcript ending on assistant turn remains non-critical but warns.

### Acceptance Criteria

- Every `main()` branch with `--output-file` writes a JSON file.
- Every emitted extraction result contains `capture_manifest`, `capture_health`, and `capture_warnings`.
- A transcript ending on a user turn is critical even without a header.
- Existing successful extraction behavior remains unchanged.

### Avoid

- Do not bury capture diagnostics in logs only.
- Do not let stdout-only branches survive.

## Workstream 3: V60 Ledger Accountability

Priority: P1  
Primary files:

- `engine/system_b/v60_enrichment.py`
- `scripts/finalize_v60_telemetry.py`
- `scripts/archive_run.py`
- `SKILL.md`
- `references/private-enrichment-treatment.md`
- `tests/test_v60_enrichment_runtime.py`
- `tests/test_archive_run_v60_telemetry.py`
- likely new ledger skeleton tests

### What We Are Trying To Solve

The ledger should prove at least structured consideration discipline, not merely that the runner wrote one row per selected chunk.

The runner should fill decisions into a deterministic ledger skeleton rather than inventing transaction structure.

### Why This Is A Problem

Current validation can pass a ledger that is complete but shallow. It catches missing chunks, duplicate chunks, unknown chunks, bad enums, and missing text fields. It does not catch many contradictions that matter:

- chunk belongs to a different card/model
- chunk kind does not match the row's claimed kind
- `used` with route `irrelevant`
- `used` with no visible effect and no private-guardrail claim
- absence record treated as positive affordance
- rejection/deferment with generic `risk_if_forced`
- freeform summary counts contradict transaction counts

### Candidate Fixes

#### Option A: Deterministic Skeleton Plus Stronger Deterministic Validation

Generate a ledger template from `v60_enrichment.selected_cards`, with one transaction shell per selected chunk:

- `chunk_id`
- `card_id`
- `model_id`
- `chunk_kind`
- `source_file`
- `selection_source`
- empty runner-fillable fields:
  - `disposition`
  - `route`
  - `strongest_plausible_application`
  - `why`
  - `visible_effect`
  - `private_guardrail`
  - `risk_if_forced`
  - absence-specific fields when `chunk_kind == "absence"`

Then validate filled rows against the skeleton.

Pros:

- Low-token and deterministic.
- Removes structure invention from Step 6.
- Greatly improves accounting reliability.

Cons:

- Still cannot fully prove semantic consideration.
- Requires SKILL.md/process updates.

#### Option B: Add A Second LLM Ledger Judge

After the runner writes the ledger, ask another LLM to judge whether each transaction is meaningful.

Pros:

- Can catch semantic shallowness better than pure schema checks.

Cons:

- Adds cost.
- Adds another opaque judgment layer.
- Can create false confidence before deterministic checks are fixed.

#### Option C: Split Step 6 Into Private Consideration And Public Composition

Make the runner first fill the ledger skeleton privately, then produce the revised answer from the accepted/deferred/rejected considerations, then run a deterministic sanitizer.

Pros:

- Reduces one-step cognitive overload.
- Aligns private accountability with public hygiene.

Cons:

- Requires more orchestration discipline.
- May be awkward in manual skill-run environments.

#### Option D: Diff-Based Visible Effect Validation

For every `used` chunk, require a pointer to a user-visible change category and compare revised answer/memo against original answer.

Pros:

- Connects V60 to product effect.

Cons:

- Some valid uses are private guardrails or confidence boundaries, not obvious textual additions.
- Diffing prose is noisy.

### Selected Approach

Choose Option A now, with a narrow piece of Option C: skeleton first, public answer second. Add Option D as a validation field, not as a hard proof requirement for all chunks.

Do not add Option B until deterministic checks are in place and we have examples of failures deterministic validation cannot catch.

### Implementation Plan

1. Add a ledger skeleton builder in `v60_enrichment.py`.
2. Store the skeleton in `result.json` or a sidecar before Step 6.
3. Update `SKILL.md` so the runner fills the skeleton, not freehands the ledger.
4. Extend validation:
   - transaction count equals skeleton count
   - `chunk_id`, `card_id`, `model_id`, and `chunk_kind` match skeleton
   - route/disposition compatibility is checked
   - `used` requires `visible_effect` or `private_guardrail`
   - absence chunks require `blocked_or_guarded_claim` or `uncertainty_boundary`
   - non-used chunks require specific `risk_if_forced`
5. Preserve existing summary fields for Observatory compatibility, but compute counts from transactions.
6. Add tests for bad combinations.

### Route/Disposition Compatibility Draft

Allowed examples:

- `used + changed_answer`
- `used + private_guardrail`
- `used + sharpened_test`
- `rejected + irrelevant`
- `rejected + unsupported_by_case`
- `deferred + insufficient_evidence`
- `not_considered + overflow_or_duplicate`, only if explicitly allowed

Suspicious or invalid examples:

- `used + irrelevant`
- `used + unsupported_by_case`
- `rejected + changed_answer`
- absence chunk with `changed_answer` but no blocker/guardrail field
- affordance chunk marked as absence blocker

### Acceptance Criteria

- The runner receives a deterministic ledger skeleton.
- The runner cannot pass validation by inventing shorter card ids, wrong model ids, or wrong chunk kinds.
- Every selected chunk has exactly one transaction.
- Every `used` chunk declares either a visible product effect or a private guardrail.
- Every selected absence record says what it blocked, guarded, or bounded.
- Missing, invalid, or contradiction-bearing ledgers degrade active V60 run health.

### Avoid

- Do not treat `used_chunk_count` as success.
- Do not require every useful V60 chunk to visibly change the answer; private guardrails are legitimate.
- Do not let the LLM invent transaction ids or card ids.

## Workstream 4: Run Health Severity Model

Priority: P1  
Primary files:

- `scripts/run_pipeline.py`
- `engine/system_b/v60_enrichment.py`
- `observatory/serve_result.py`
- `../Lolla-system-b/observatory/svelte-app/src/lib/RunHealthView.svelte`, if updating sibling UI
- `tests/test_run_pipeline_contract_default.py`
- `tests/test_v60_enrichment_runtime.py`

### What We Are Trying To Solve

Run health should tell operators what failed, what was unavailable by mode, what is still trustworthy, and what product surfaces are safe.

### Why This Is A Problem

The current `issues` list is too blunt. Any issue degrades overall health. This makes optional embeddings-off look similar to broken capture or invalid V60 ledger. It also makes comparison noisy because "degraded" can mean very different things.

### Candidate Fixes

#### Option A: Structured Issue Objects With Severity And Axis

Keep legacy `issues: list[str]`, but add `issue_details`:

```json
{
  "code": "embeddings_off",
  "severity": "optional_off",
  "axis": "retrieval",
  "trust_impact": "embedding recall unavailable; deterministic lanes still usable",
  "mode_expected": false
}
```

Pros:

- Backward-compatible.
- Lets Observatory show precise health.
- Low implementation risk.

Cons:

- Two representations can drift unless generated from one source.

#### Option B: Multiple Top-Level Health Axes

Replace one overall status with axes:

- `capture_health`
- `telemetry_health`
- `v60_health`
- `product_output_health`
- `retrieval_health`
- `archive_health`

Pros:

- Productively precise.

Cons:

- Bigger schema migration.
- More UI changes.

#### Option C: Keep Current Shape, Add Severity Map

Keep `issues` and add a static map from issue code to severity.

Pros:

- Fast.

Cons:

- Less expressive.
- Harder to include mode-specific details.

### Selected Approach

Choose Option A now. Design it so Option B can emerge later from the same issue objects.

### Proposed Severity Levels

- `critical`: run should not be trusted for audit output. Example: capture ends on user turn.
- `degraded`: a required component failed, and reasoning/product output may be incomplete. Example: active V60 ledger missing or invalid.
- `partial`: a non-fatal evaluator or lane failed, but core run exists. Example: stakeholder check failed after being triggered.
- `optional_off`: optional capability unavailable by mode/configuration. Example: embeddings off when embeddings were not required.
- `info`: state worth recording but not a health issue.

### Implementation Plan

1. Introduce a small health issue builder in `run_pipeline.py`.
2. Generate both:
   - legacy `issues`
   - new `issue_details`
3. Compute `overall` from highest severity, not from any issue existing.
4. Treat embeddings as:
   - `optional_off` if no key/config says auto-off
   - `degraded` only if mode explicitly required embeddings and they failed
5. Update V60 finalization to add structured issue details for missing/invalid ledger.
6. Update Observatory rendering to display severity and axis.

### Acceptance Criteria

- No-OpenAI-key runs are not automatically `overall: degraded` when embeddings are optional.
- Capture-critical still yields `overall: critical`.
- Active V60 missing/invalid ledger yields `overall: degraded`.
- Existing consumers reading `issues` still work.
- Observatory makes severity visible without forcing the operator to interpret raw codes.

### Avoid

- Do not collapse every non-perfect state into `degraded`.
- Do not remove legacy fields until archived result compatibility is solved.

## Workstream 5: Product Output Hygiene Gate

Priority: P1, or P0.5 if live comparisons continue soon  
Primary files:

- likely new `engine/system_b/output_hygiene.py`
- `scripts/archive_run.py`
- `scripts/render_memo.py`
- `SKILL.md`
- `tests/test_render_memo.py`
- likely new archive/finalization hygiene tests

### What We Are Trying To Solve

A run should be able to say whether its user-facing artifacts are clean product outputs. This should cover revised/chat output and memo output, not just deterministic memo fields.

### Why This Is A Problem

The memo renderer has improved, but chat/revised answer hygiene is mostly prompt-enforced. A run can have valid internal telemetry and still leak internal machinery to the user. That should mark the product surface unsafe.

### Candidate Fixes

#### Option A: Deterministic Scanner Gate

Scan user-facing artifacts for banned internal terms and attribution phrases:

- `V60`
- `affordance`
- `chunk`
- `ledger`
- `lane`
- `pipeline`
- internal model ids where detectable
- `independent review`
- `private enrichment`
- `selected cards`

Allow configured exceptions for Observatory/audit appendices, not for clean chat/memo.

Pros:

- Cheap.
- Deterministic.
- Easy to archive and compare.

Cons:

- Can false-positive on legitimate ordinary uses of words like "pipeline" in user domain.
- Needs context-aware allowlist.

#### Option B: LLM Sanitizer/Rewriter

Ask an LLM to detect and rewrite internal-mechanism leaks.

Pros:

- Better nuance.

Cons:

- Adds cost and another possible failure.
- Can hide the evidence of a leak by rewriting it away.

#### Option C: Renderer-Only Enforcement

Rely on `render_memo.py` stripping and tests.

Pros:

- Existing path already improved.

Cons:

- Does not cover chat/revised answer.
- Does not produce whole-run product-safety telemetry.

### Selected Approach

Choose Option A now. Add Option B later only as an optional repair mode, not as the first gate.

### Implementation Plan

1. Add a deterministic scanner with:
   - artifact role: `revised_answer`, `memo_clean`, `memo_audit_appendix`, `observatory`
   - banned terms by role
   - phrase rules for known mechanism leaks
   - allowlist support for domain words if needed
2. Run scanner before archive finalization.
3. Write hygiene results into `result.json.run_health` or archive manifest:
   - `product_output_health`
   - `product_output_leak_count`
   - `product_output_leaks`
4. Treat leaks in clean user-facing artifacts as at least `partial`; for live-comparison eligibility, require zero leaks.
5. Keep Observatory/audit pages exempt from clean-product rules.

### Acceptance Criteria

- Clean memo and revised answer are scanned.
- A leak of `V60`, `affordance`, `chunk`, `ledger`, or `independent review` in clean artifacts is detected.
- Observatory and audit appendix are not falsely treated as clean product artifacts.
- Archive records hygiene status.
- Comparison can filter to product-clean runs.

### Avoid

- Do not silently rewrite leaks and call the run clean.
- Do not block legitimate user-domain terms without context review. Example: a user might genuinely discuss a sales pipeline.

## Workstream 6: V60 Selection Quality

Priority: P2  
Primary files:

- `engine/system_b/v60_enrichment.py`
- `engine/system_b/embedding_retriever.py`
- `observatory/serve_result.py`
- `tests/test_v60_enrichment_runtime.py`
- V60 replay/lab tests

### What We Are Trying To Solve

Replace `record_order_first` with relevance-aware affordance and absence selection. Select fewer, better chunks rather than more chunks.

### Why This Is A Problem

The substrate has 306 affordances and 697 absence records. Selecting the first affordance and first absence from the parent model record is custody-preserving but not reasoning-grade. It can miss the chunk that would actually introduce the missing option, block an overclaim, or sharpen the test.

### Candidate Fixes

#### Option A: Query-Aware Chunk Ranking Within Selected Models

For each selected model record, rank its affordances and absences against a query built from:

- decision situation
- user constraints
- dropped threads
- lane challenge/reason
- candidate evidence
- revised-answer risks if available

Pros:

- Improves selection without changing candidate source.
- Can be deterministic lexical scoring first, embedding-assisted later.

Cons:

- Needs careful scoring to avoid keyword noise.

#### Option B: Absence-Specific Blocker Detection

Run a deterministic or lightweight LLM step that looks for tempting overclaims/missing evidence in the answer/context, then selects absence records that match those risks.

Pros:

- Treats absences as guardrails, not decorations.
- Directly supports overclaim blocking.

Cons:

- Harder than affordance ranking.
- LLM version adds cost; deterministic version may be brittle.

#### Option C: Diversity And Family Caps

Prevent early lanes or related model families from consuming all hot-context slots. Reserve slots by effect type:

- missing option
- evidence gate
- uncertainty boundary
- overclaim blocker
- sequencing/test

Pros:

- Reduces redundant selections.
- Helps cap pressure.

Cons:

- Requires taxonomy/effect tags or heuristics.

#### Option D: Learned/Scored Selector From Replay Data

Use replay outcomes to learn which chunk types tend to produce useful deltas.

Pros:

- Could improve with data.

Cons:

- Premature. Current telemetry is not yet trustworthy enough to train on.

### Selected Approach

Use A + B + C in phases. Do not use D yet.

1. Start with deterministic lexical/field-aware chunk ranking inside selected model records.
2. Add explicit absence-selection logic tied to blocked claims or uncertainty boundaries.
3. Add diversity/effect-type slotting after the first two are observable.

### Implementation Plan

1. Replace `_build_card` `[:1]` selection with a scoring function.
2. Score affordances against lane reason, evidence, decision, constraints, and dropped threads.
3. Score absences against:
   - unsupported claims
   - tempting interpretations
   - model misuse warnings
   - missing evidence gates
4. Preserve `record_order_first` only as a fallback, and record when fallback was used.
5. Add telemetry:
   - selected chunk score
   - selected chunk reason
   - alternatives skipped within the same model
   - absence selected because of which blocker signal
6. Update Observatory labels:
   - "selected by lane custody"
   - "chunk chosen by local relevance"
   - "absence chosen as overclaim guardrail"
7. Run offline replay before live testing.

### Acceptance Criteria

- `record_order_first` is no longer the normal path.
- Every selected absence has a blocker or guardrail reason.
- Selection telemetry shows why the specific chunk was chosen over siblings.
- Increasing `--v60-max-cards` is not needed to recover known useful chunks in replay fixtures.
- Offline replay demonstrates improved pickup of optionality/premortem-style chunks without increasing public mechanism leakage.

### Avoid

- Do not solve weak selection by increasing hot-context caps.
- Do not select absence records just because the parent model was selected.
- Do not treat embedding rank as semantic confidence.

## Workstream 7: First-Class Run Comparison

Priority: P3, blocked by P0 and most P1 work  
Primary files:

- likely new `scripts/compare_archived_runs.py`
- `observatory/serve_result.py`
- sibling Svelte Observatory app, later
- archive fixtures/tests

### What We Are Trying To Solve

Operators need to compare runs without eyeballing raw JSON or over-weighting final answer vibes.

### Why This Is A Problem

The system currently preserves enough artifacts to compare runs, but comparison is not first-class. Without a disciplined comparison layer, teams will overinterpret visible answer changes and underinspect trace health, hygiene, cost, and ledger quality.

### Candidate Fixes

#### Option A: CLI/Markdown Archive Comparison Report

Build a local script that compares two archived runs and emits Markdown/JSON:

- final answer diff
- memo diff
- visible change categories
- selected V60 cards/chunks
- ledger disposition counts
- health/severity differences
- quote/capture differences
- output-hygiene differences
- usage/cost differences

Pros:

- Cheap.
- Reviewable in PRs.
- Does not require UI design.

Cons:

- Less interactive.

#### Option B: Observatory Compare UI

Add a side-by-side comparison mode to Observatory.

Pros:

- Better operator workflow.
- Easier visual debugging.

Cons:

- Should not be built on untrustworthy telemetry.
- Higher implementation cost.

#### Option C: Blind Judge Comparison

Use an LLM or human rubric to judge which run has better reasoning.

Pros:

- Useful for experiments.

Cons:

- Not a replacement for trace comparison.
- Adds cost and variance.

### Selected Approach

Choose Option A first. Build Option B after the report shape stabilizes. Use Option C only as an experiment layer.

### Implementation Plan

1. Define comparison schema.
2. Build `scripts/compare_archived_runs.py`.
3. Support comparing:
   - same case across two run ids
   - baseline vs V60
   - before/after hardening
4. Emit both JSON and Markdown.
5. Add Observatory link later to load comparison output.

### Acceptance Criteria

- The report shows health and trace trust before answer-quality claims.
- Comparison refuses or warns when either run has untrusted telemetry.
- Product-output leak count is visible.
- V60 impact is shown as effect categories, not internal jargon.
- Cost and token deltas use corrected boundary-call telemetry.

### Avoid

- Do not launch comparison UI before P0 trace truth.
- Do not reduce comparison to "final answer changed."

## Workstream 8: Step 6 Load Reduction

Priority: Cross-cutting P1/P2  
Primary files:

- `SKILL.md`
- `references/private-enrichment-treatment.md`
- `references/chat-output-format.md`
- `references/memo-output-format.md`
- V60 ledger files/tests

### What We Are Trying To Solve

The runner is doing too much in one step. This creates predictable failures: skipped ledger, schema drift, public mechanism leaks, and shallow consideration.

### Why This Is A Problem

The system asks one model to reconsider the answer, privately consider V60, write a ledger, avoid leaks, produce chat, prepare memo fields, and preserve artifacts. That is too many simultaneous obligations, especially across different runner models.

### Candidate Fixes

#### Option A: Prompt Hardening Only

Add clearer instructions and warnings to `SKILL.md`.

Pros:

- Fast.

Cons:

- We already know prompt-only compliance is fragile.

#### Option B: Deterministic Skeletons And Ordered Substeps

Break Step 6 into required substeps:

1. Fill ledger skeleton privately.
2. Summarize accepted/rejected/deferred effect categories.
3. Compose clean revised answer.
4. Run deterministic hygiene scan.
5. Render/archive.

Pros:

- Reduces structure invention.
- Makes failure points inspectable.

Cons:

- More orchestration steps.

#### Option C: Delegate Private Consideration To A Separate Agent/Model

Use a separate worker to fill the ledger, then the main runner writes the public answer.

Pros:

- Separation of roles.

Cons:

- More operational complexity.
- More token cost.
- Not always available in skill runtime.

### Selected Approach

Choose Option B. Do not rely on Option A alone. Keep Option C as an experiment only.

### Acceptance Criteria

- Step 6 no longer requires the runner to invent ledger structure.
- Public answer generation happens after private transaction decisions.
- Hygiene scan runs after public composition.
- Missing ledger or hygiene failure is visible in run health.

## Suggested Sequence

### Phase 0: Receipts First

Goal: make trace and extraction receipts true.

1. Workstream 1: Lane 4 boundary trace truth.
2. Workstream 2: extraction output consistency and capture criticality.
3. Add targeted tests only. No full live runs required.

Exit criteria:

- Lane 4 telemetry regression passes.
- Extraction edge-path tests pass.
- Existing run-pipeline contract tests pass.

### Phase 1: Accountability And Health

Goal: make run health and V60 accountability interpretable.

1. Workstream 3: deterministic V60 ledger skeleton and stronger validation.
2. Workstream 4: structured health severities.
3. Workstream 5: product-output hygiene gate.
4. Update `SKILL.md` and private-enrichment references.

Exit criteria:

- Active V60 missing/invalid/shallow ledger is degraded with specific reason.
- Optional embeddings-off is not confused with broken run state.
- Clean product artifacts are scanned and archived with hygiene status.

### Phase 2: Selection Quality

Goal: improve V60 chunk usefulness without increasing caps.

1. Workstream 6: relevance-aware affordance selection.
2. Workstream 6: absence-specific blocker selection.
3. Offline replay on known cases before live tests.

Exit criteria:

- Known useful chunks are recovered in offline replay without larger caps.
- Absence selections have explicit blocker reasons.
- No increase in public mechanism leakage.

### Phase 3: Comparison

Goal: learn from runs without storytelling.

1. Workstream 7: CLI/Markdown comparison report.
2. Only after schema stabilizes, add Observatory compare UI.
3. Optional blind-judge experiments after trace health is reliable.

Exit criteria:

- Comparison reports start with trace/product-health eligibility.
- Cost, health, ledger, hygiene, and answer deltas are all visible.

## Minimum Test Matrix

### Unit Tests

- `tests/test_structural_coverage_contextual.py`
  - three-call orchestration returns three traces
  - two-call no-gap path returns two traces
- `tests/test_run_extract.py`
  - no-header final user turn is critical
  - `not_strategic` writes output file with capture diagnostics
  - missing-required-field writes output file with capture diagnostics
- `tests/test_v60_enrichment_runtime.py`
  - skeleton includes every selected chunk
  - validator rejects mismatched card/model/kind
  - validator rejects `used + irrelevant`
  - validator rejects absence used without blocker/guardrail
  - valid private-guardrail use passes without visible answer change
- output hygiene tests
  - clean memo/revised answer passes
  - internal terms fail clean-product status
  - Observatory/audit appendix not treated as clean-product artifact
- health tests
  - optional embeddings-off does not degrade overall
  - required embeddings failure degrades
  - capture critical remains critical
  - active V60 invalid ledger degrades

### Integration Tests

- Pipeline fixture with Lane 4 gaps produces correct boundary summaries.
- Archive finalization updates run health for V60 and product hygiene.
- Compare-report fixture refuses to treat untrusted telemetry as comparison-ready.

### Offline Replay Checks

- Solo-founder pivot archived cases:
  - verify prior Lane 4 trace bug is fixed in new run/fixture
  - verify optionality/premortem selection improves without cap increase
  - verify no internal mechanism leakage in clean memo/revised answer
- V60 transaction replay cases:
  - good rejection accepted as success
  - absence-only guardrail accepted as success
  - mechanical ledger rejected

## Open Decisions For Team Feedback

1. Should missing `CONVERSATION:` header with assistant as last turn be `unknown` or `degraded`?
   - My recommendation: keep `unknown` for now, but make final-user-turn critical override it.
2. Should product-output hygiene failure make overall health `degraded` or a separate `product_output_health: unsafe`?
   - My recommendation: separate axis plus `partial` or `degraded` depending on live-test mode.
3. Should V60 ledger skeleton live inside `result.json`, as `/tmp/lolla_<RUN_ID>_v60_ledger_skeleton.json`, or both?
   - My recommendation: both. Put canonical skeleton in result for archive custody; write sidecar for runner ergonomics.
4. Should absence selection use an LLM in Phase 2?
   - My recommendation: start deterministic/lexical plus telemetry. Add LLM only if replay shows deterministic matching misses important blockers.
5. Should comparison live first in Observatory or CLI?
   - My recommendation: CLI/Markdown first, UI second.

## Definition Of Done For This Hardening Pass

The hardening pass is done when:

- Lane 4 boundary traces are stage-true.
- Extraction always writes durable output with capture diagnostics.
- Capture criticality cannot be hidden by missing header.
- V60 ledger structure is generated deterministically.
- Ledger validation catches identity, route, disposition, effect, and absence-blocker contradictions.
- Health separates critical/degraded/partial/optional states.
- Clean user-facing artifacts are scanned for internal machinery leaks.
- V60 selection no longer normally uses `record_order_first`.
- First comparison report refuses to overclaim when telemetry or product output is untrusted.

## What Not To Optimize Yet

- Do not run more paid live comparisons before P0 fixes.
- Do not increase V60 hot-context caps as the first selection fix.
- Do not add a second LLM judge before deterministic ledger validation is stronger.
- Do not build a polished comparison UI before the comparison schema and trust gates are settled.
- Do not define success as final-answer change. Good rejection, absence guardrail, sharper uncertainty, and clean no-op can all be success.
