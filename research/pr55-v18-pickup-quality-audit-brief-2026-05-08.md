# PR55 V18 Pickup Quality Audit Brief

**Date:** 2026-05-08
**Status:** review-only research / audit PR; no product injection
**Decision label:** `v18_pickup_quality_audit_required`
**Current local branch observed:** `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`
**Current observed HEAD:** `fbc0242`

## Verdict

PR55 should be a red-flag audit and packet stress review, not another
extraction PR by default.

v18 completed the corpus coverage objective. The next question is not:

> Do we have reviewed cards?

The next question is:

> Can reviewed cards survive pickup, compression, display, and LLM use without
> losing their epistemic shape?

The answer is not proven yet. Therefore:

- **PASS** as dormant reviewed substrate.
- **REVISE** before runtime pickup.
- **BLOCK** any live `/lolla`, prompt, memo, Step 6, Step 8, or user-facing use
  until PR55 or a successor audit resolves the pickup risks.

## Audit Outputs

This PR55 audit is split into focused artifacts:

- `research/pr55-v18-full-corpus-distribution-audit-2026-05-08.md`
  - full v18 distribution, weak/medium support, absence counts, source-ref
    concentration, and one-affordance dominance.
- `research/pr55-v18-richness-red-flag-audit-2026-05-08.md`
  - selective richness review and under-extraction red flags.
- `research/pr55-v18-packet-stress-review-2026-05-08.md`
  - static packet stress review across broad/meta, weak-support,
    absence-heavy, normal, pressure, and narrow fixtures.
- `research/pr55-per-affordance-traceability-review-2026-05-08.md`
  - why the current flattened packet is adequate for card-level inspection but
    not for affordance-level transaction ledgers.
- `research/pr55-lane-to-nomination-provenance-contract-2026-05-08.md`
  - future dormant adapter contract for mapping Lane 1/2/3/4 outputs into
    nominations without losing attribution.
- `research/pr55-runtime-readiness-blockers-2026-05-08.md`
  - gate table for what blocks live `/lolla` pickup.

Related decoder handover:

- `plans/reasoning-substrate-affordance-transaction-handover-2026-05-08.md`
  - low-level staged implementation plan for grouped affordance cards, decoder
    ledger, receiver prompt, renderer hardening, and offline replay.

## PR Discipline

This PR must remain review-only.

Recommended branch:

`feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Branch discipline:

- Preferred final PR base is current `main`, but local `main` does not yet
  contain `affordances_v18.json`; until v18 lands on `main`, this PR is a
  stacked audit branch over the v18-bearing substrate state.
- Keep existing untracked local work out of the PR unless explicitly selected.
- Prefer research docs, deterministic audit reports, and static fixtures.
- Do not modify live runtime behavior.
- Do not import `reasoning_substrate_packet.py` or review renderers into
  `engine/system_b/pipeline.py`.
- Do not change `/lolla` behavior.
- Do not change prompts.
- Do not change memo or Observatory surfaces.
- Do not add final-answer generation.
- Do not auto-select latest affordance artifacts.

Merge discipline:

- PR55 may merge to `main` only as an audit / research hardening PR.
- It should leave the product path unchanged.
- Any later runtime experiment should be a separate PR with a separate review
  gate.

## Verified Current State

Local read-only verification found:

- Current branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`.
- Local `main` does not contain `data/compiled/model_affordances/affordances_v18.json`.
- `data/compiled/model_affordances/affordances_v18.json` exists.
- v18 artifact: `model_affordances_v18`.
- v18 status: `draft_review_only`.
- v18 records: `222`.
- v18 affordances: `258`.
- v18 absence records: `429`.
- v18 record statuses:
  - `supported`: `220`.
  - `weak_support`: `2`.
- v18 affordance confidence:
  - `high`: `251`.
  - `medium`: `7`.
  - `weak`: `0`.
- Schema validation failures: `0`.
- Source-quote rejections: `0`.
- No `affordances_v18` or `model_affordances_v18` references were found in
  `engine/` or `scripts/`.
- The dormant packet producer still defaults to
  `data/compiled/model_affordances/affordances_v4.json` unless an explicit
  artifact path is passed.

This is a good safety posture. It also means v18 completion does not equal v18
runtime use.

## Why PR55 Exists

The extraction program solved coverage. It did not yet solve pickup quality.

Current risks:

1. Full coverage can create false equality.
   Every model now has a reviewed record, but not every record has the same
   depth, confidence, support strength, or runtime suitability.

2. The packet handoff flattens affordances.
   Current candidate cards pool `use_when`, `do_not_use_when`,
   `case_evidence_needed`, `treatment_requirements`, `diagnostic_questions`,
   `misuse_guards`, and `source_evidence` into shared fields. That is useful
   for compact fixture review, but too lossy for future use/reject/defer
   transactions at the affordance level.

3. Weak support is too quiet.
   `devops-and-continuous-integration` and `price-discrimination` are
   `weak_support` records with medium confidence. Packet/render surfaces must
   not let them look like ordinary high-confidence reviewed cards.

4. Absences are under-displayed relative to their importance.
   v18 has `429` absence records. If absence records are overclaim rails, they
   cannot be treated as minor footers.

5. One compact affordance became a coverage-mode operating rule.
   This was probably good medicine during corpus completion. It now needs an
   under-extraction audit, because it may compress multiple downstream-relevant
   affordances into one identity.

6. Broad/meta cards can become attractive nuisance material.
   Models such as `systems-thinking`, `latticework-of-mental-models`,
   `chain-of-thought`, `meta-cognitive-reflection`,
   `mental-models-of-reality`, and `reasoning-mode-router` sound strategic and
   may crowd out narrower cards unless packet shape and caps make them earn
   their place.

7. Duplicate nomination dedupe can erase provenance.
   Current packet construction suppresses duplicate `model_id` nominations
   after the first card. That is acceptable for static fixtures, but a future
   adapter must merge provenance before dedupe or the same model pulled by Lane
   1, Lane 3, and Lane 4 will look like it came from only one source.

## Key Distinction

PR55 must separate two questions:

1. **Coverage question:** Did we extract enough to represent every runtime
   model at least once?
   - Current answer: yes. v18 passes.

2. **Pickup question:** Did we extract and package enough for future
   use/reject/defer decisions without flattening epistemic shape?
   - Current answer: not proven.

The second question is PR55's job.

## Split Candidate Criterion

Do not split records merely because the source contains more material. Most
sources do.

A record becomes a `split_candidate` only if the source supports multiple
distinct affordances with different downstream transaction behavior:

- different activation conditions;
- different case evidence required;
- different do-not-use boundaries;
- different misuse guards;
- different treatment requirements;
- different source confidence;
- different likely use/reject/defer outcome;
- different final-answer delta.

The practical test:

> Would separating this material change what the downstream LLM uses, rejects,
> defers, asks, warns about, or refuses to overclaim?

If yes, mark `split_candidate`.
If no, keep compressed.

## Red-Flag Labels

Use these labels in PR55 audit tables:

- `compression_ok`
  - One affordance is enough for downstream transaction behavior.
- `split_candidate`
  - One record may be carrying multiple transaction-distinct operational moves.
- `too_broad_for_runtime`
  - The record is source-backed but likely too broad to hand off without
    rewrite, grouping, or stricter cap.
- `grouped_affordance_required`
  - The model has multiple affordances or mixed blockers that must stay grouped
    by affordance ID before any transaction-level receiver use.
- `display_hardening_needed`
  - The record is acceptable, but packet/render/receiver surfaces hide important
    confidence, absence, or support-status information.
- `needs_source_recheck`
  - Exact quotes validate, but semantic normalization should be re-read against
    source before any runtime use.
- `weak_support_warning_required`
  - Medium/weak record must be visibly marked before receiver use.
- `absence_first_handoff_required`
  - The absence record is more important than the positive affordance for
    preventing overclaiming.
- `runtime_do_not_promote_yet`
  - The record should remain dormant until additional review or evaluation.

## Audit Stage 1: Full-Corpus Distribution Audit

Goal: understand the full v18 shape before any packet pickup.

Tasks:

- [ ] Count records by top-level status.
- [ ] Count affordances by status.
- [ ] Count affordances by confidence.
- [ ] Count affordances per model.
- [ ] Count absence records per model.
- [ ] Count source evidence spans per affordance.
- [ ] List all `weak_support` records.
- [ ] List all medium-confidence records.
- [ ] List all records with zero absence records.
- [ ] List all one-affordance records with high source-evidence count.
- [ ] List all broad/meta model IDs.
- [ ] List all records flagged by `quality_report_v18.md` as not safe to
      runtime-promote without rewrite review.

Expected output:

`research/pr55-v18-full-corpus-distribution-audit-2026-05-08.md`

Acceptance:

- [ ] The audit distinguishes "reviewed" from "runtime-ready".
- [ ] The audit makes weak/medium support visible.
- [ ] The audit shows whether one-affordance dominance is benign or suspicious.

## Audit Stage 2: Source-Vs-Affordance Richness Review

Goal: determine whether the one-affordance convention left useful
transaction-distinct knowledge on the table.

Review sample:

- [ ] All records with more than one affordance.
- [ ] All `weak_support` records.
- [ ] All records with zero absence records.
- [ ] All broad/meta model records.
- [ ] A stratified sample of one-affordance records:
  - [ ] diagnostic;
  - [ ] systems;
  - [ ] metacognitive;
  - [ ] causal;
  - [ ] probabilistic;
  - [ ] communication/product;
  - [ ] economic/systems.

For each reviewed model:

- [ ] Read source Markdown.
- [ ] Read compiled affordance record.
- [ ] Identify source operational clusters.
- [ ] Ask whether each cluster changes downstream transaction behavior.
- [ ] Apply red-flag labels.
- [ ] Do not rewrite the record in PR55 unless explicitly approved.

Expected output:

`research/pr55-v18-richness-red-flag-audit-2026-05-08.md`

Acceptance:

- [ ] Every `split_candidate` is justified by transaction-distinct behavior, not
      by source richness alone.
- [ ] Every `compression_ok` explains why the extra source material is support,
      not a separate affordance.
- [ ] Broad/meta models receive explicit treatment.

## Audit Stage 3: Packet Handoff Safety Review

Goal: test whether v18 remains useful and honest after packet compression.

Stress fixture types:

- [ ] Broad/meta-heavy packet.
- [ ] Weak-support packet.
- [ ] Absence-heavy packet.
- [ ] 12-card normal packet.
- [ ] 16-card pressure packet.
- [ ] Mixed Lane 1/2/3/4 provenance packet.
- [ ] Narrow-card packet with no broad/meta cards.

For each fixture:

- [ ] Build packet with explicit `affordances_v18.json` path.
- [ ] Confirm no implicit default artifact is used.
- [ ] Record candidate count, reviewed count, weak/conflicting count, and
      absence count.
- [ ] Render review Markdown.
- [ ] Inspect whether confidence is visible enough.
- [ ] Inspect whether weak support is visible enough.
- [ ] Inspect whether absence records are visible enough.
- [ ] Inspect whether multi-affordance records are flattened.
- [ ] Inspect whether broad cards crowd out narrower cards.
- [ ] Inspect whether source custody is preserved.

Expected output:

`research/pr55-v18-packet-stress-review-2026-05-08.md`

Acceptance:

- [ ] Packet stress does not answer the user case.
- [ ] Packet stress does not generate final pressure.
- [ ] Packet stress identifies handoff hardening needs before runtime.

## Audit Stage 4: Per-Affordance Traceability Review

Goal: determine whether the current packet can support a future card
transaction ledger.

Questions:

- [ ] Can the receiver identify which affordance was used?
- [ ] Can the receiver identify which affordance was rejected?
- [ ] Can the receiver identify which affordance was deferred?
- [ ] Can the receiver trace a treatment requirement back to an affordance ID?
- [ ] Can the receiver tell which absence blocked use?
- [ ] Can the receiver preserve confidence and weak-support status?
- [ ] Can the receiver avoid mixing `use_when` from one affordance with
      `misuse_guard` from another?

Expected answer:

Current flattened packet is probably sufficient for human fixture review, but
not sufficient for robust affordance-level transaction ledgers.

Expected output:

`research/pr55-per-affordance-traceability-review-2026-05-08.md`

Acceptance:

- [ ] The audit decides whether card-level decisions are enough.
- [ ] If affordance-level decisions are required, the audit recommends grouped
      `reviewed_affordance_cards`.
- [ ] The audit does not implement grouping yet unless explicitly approved.

## Audit Stage 5: Lane-To-Nomination Provenance Contract

Goal: specify how existing lane outputs could become nominations without
running new reasoning.

Lane sources:

- Lane 1:
  - `DeltaFinding`
  - `TendencyRoute`
  - `primary_model_id`
  - `supporting_model_ids`
  - `risk_model_ids`
  - `selected_model_ids`
  - tendency ID, sub-pattern, challenge, next move
- Lane 2:
  - `DetectedModel`
  - assistant evidence quote
  - presence mode
  - confidence
  - companion expansion model IDs
- Lane 3:
  - `ExtractedFrameElement`
  - user evidence quote
  - frame pattern
  - `FrameRoute.candidate_model_ids`
  - reframing grounding model
- Lane 4:
  - uncovered dimension
  - materiality note
  - `DimensionRoute.candidate_model_ids`
  - generated discovery questions

Contract rules:

- [ ] Recall broadly.
- [ ] Attribute narrowly.
- [ ] Preserve whether evidence came from user framing, assistant answer,
      structural gap, or route metadata.
- [ ] Do not collapse all reasons into generic "relevant model".
- [ ] Do not run new semantic reasoning in the adapter.
- [ ] Do not promote raw Lane 4 questions as product surface.

Expected output:

`research/pr55-lane-to-nomination-provenance-contract-2026-05-08.md`

Acceptance:

- [ ] Every lane source maps to `CandidateNomination` without losing evidence
      type.
- [ ] The contract makes user-vs-assistant attribution explicit.
- [ ] The contract remains dormant.

## Audit Stage 6: Runtime-Readiness Blockers

Goal: produce a final gate list before any future live experiment.

Blockers to check:

- [ ] Explicit artifact selection required.
- [ ] No default `affordances_v4.json` for future pickup adapters.
- [ ] No glob or "latest wins" artifact loading.
- [ ] Confidence visible in receiver handoff.
- [ ] Weak support visible as warning.
- [ ] Absence records visible as overclaim rails.
- [ ] Per-affordance grouping available if ledger is affordance-level.
- [ ] Broad/meta cards capped or labeled.
- [ ] Lane provenance contract defined.
- [ ] Packet caps tested against 12-card and 16-card stress cases.
- [ ] No runtime import in live paths until explicitly approved.
- [ ] No deterministic final pressure selection.
- [ ] No mental-model name dumping in user output.

Expected output:

`research/pr55-runtime-readiness-blockers-2026-05-08.md`

Acceptance:

- [ ] The audit can say `PASS`, `REVISE`, or `BLOCK` for each blocker.
- [ ] Any future runtime PR has a checklist to satisfy.

## What Would Falsify The Concern

The concern would weaken if PR55 finds:

- Most one-affordance records are truly single-action cards.
- Multi-affordance records remain readable even when grouped.
- Renderer truncation does not change reviewer judgment.
- Weak support remains obvious in actual receiver review.
- Broad/meta packets do not crowd out narrower cards.
- A decoder can reliably produce use/reject/defer decisions from current
  flattened fields.
- Absence records visibly change receiver behavior.

Do not assume these will hold. Test them.

## Minimum Requirements Before Any Runtime Pickup

Before any future live `/lolla` experiment:

- [ ] Decide whether runtime wants card-level or affordance-level decisions.
- [ ] If affordance-level, preserve grouped affordance identity in packet shape.
- [ ] Make confidence visible.
- [ ] Make weak support visible as warning.
- [ ] Make absence records operationally visible.
- [ ] Define lane-to-nomination provenance mapping.
- [ ] Define broad/meta-card cap behavior.
- [ ] Require explicit affordance artifact path.
- [ ] Keep deterministic code out of semantic card activation.
- [ ] Keep final answer LLM-owned.

## Suggested PR55 Outputs

Minimum PR55 can include:

- `research/pr55-v18-pickup-quality-audit-brief-2026-05-08.md`
- `research/pr55-v18-full-corpus-distribution-audit-2026-05-08.md`
- `research/pr55-v18-richness-red-flag-audit-2026-05-08.md`
- `research/pr55-v18-packet-stress-review-2026-05-08.md`
- `research/pr55-per-affordance-traceability-review-2026-05-08.md`
- `research/pr55-lane-to-nomination-provenance-contract-2026-05-08.md`
- `research/pr55-runtime-readiness-blockers-2026-05-08.md`

If the team wants a smaller first PR, merge only the audit brief plus
distribution audit, then do packet stress in PR56.

## Do Not Do In PR55

- Do not extract v19 by default.
- Do not split records yet.
- Do not update runtime packet producer.
- Do not update skill runtime prompts.
- Do not wire `/lolla`.
- Do not add a decoder call.
- Do not generate user-facing answers.
- Do not add Observatory UI.
- Do not select final pressure.
- Do not rank cards by "wisdom" or "importance".

## Bottom Line

v18 succeeded at corpus coverage. PR55 should test whether that coverage
survives product compression.

The knowledge base improvement agenda now has two fronts:

1. **Corpus quality**
   - detect under-extraction, over-compression, weak support, broad cards, and
     absence handling problems;
   - decide later whether selected records deserve splitting or rewrite.

2. **Pickup quality**
   - preserve provenance, confidence, absences, and affordance identity as the
     reviewed substrate moves toward a receiver packet;
   - ensure the LLM can use, reject, or defer cards without being forced into
     mental-model theater.

PR55 should not ask whether v18 is complete. It is complete.

PR55 should ask whether v18 can be safely compressed into a receiver packet
without flattening affordances, hiding absences, over-authorizing weak cards, or
making broad mental-model vocabulary feel like judgment.
