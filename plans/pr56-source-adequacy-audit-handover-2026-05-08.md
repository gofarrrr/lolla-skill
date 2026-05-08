# PR56 Source Adequacy Audit Handover

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: dormant audit handover; no runtime/product changes

## Goal

Prove whether v18 extracted the source corpus at the right operational granularity before testing reviewed affordances inside the system.

The decision question is:

> Is each card complete-as-compressed, or does the source support a transaction-distinct affordance, absence, or rewrite that v18 missed?

## Non-Goals

Do not:

- add live `/lolla` pickup;
- change prompts;
- change memo or Observatory surfaces;
- auto-select v18 or any latest artifact;
- rewrite affordance records inside PR56;
- expand records merely because the source is rich;
- upgrade weak-support records for symmetry;
- make Python infer semantic affordances.

## Current PR56 Artifacts

- `scripts/audit_v18_source_adequacy_queue.py`
  - deterministic queue generator.
- `research/pr56-v18-source-adequacy-audit-brief-2026-05-08.md`
  - central decision frame.
- `research/pr56-v18-source-adequacy-risk-queue-2026-05-08.md`
  - P0/P1/P2 queue summary.
- `research/pr56-v18-granularity-decision-rubric-2026-05-08.md`
  - review labels and split criteria.
- `research/pr56-v18-source-adequacy-ledger-pilot-2026-05-08.md`
  - first manual source-read pilot.

## Stage 1: Finish P0/P1 Ledger

Records:

- `systems-thinking`
- `confidence-calibration`
- `inversion`
- `price-discrimination`
- `devops-and-continuous-integration`
- `theory-of-constraints`
- `lindy-effect`
- `premortem`
- `principal-agent-problem`
- `sunk-cost-fallacy`

Tasks:

- [ ] Reopen source Markdown.
- [ ] Reopen compiled record JSON.
- [ ] List source operational clusters.
- [ ] Map each cluster to current affordance, absence, guard, or dropped material.
- [ ] Assign verdict labels.
- [ ] Identify whether v19 should add positive affordance, absence enrichment, rewrite, or no change.

Acceptance:

- [ ] No `split_candidate` without transaction-distinct proof.
- [ ] No weak-support upgrade without stronger source evidence.
- [ ] Zero absence is treated as a review signal, not automatic failure.

## Stage 2: Prove Or Reject Pilot Split Candidates

Current serious pilot split candidate:

- `chain-of-thought`

Possible question:

> Is "auditable stepwise decomposition" a different receiver transaction from "anti-rationalization / trace-as-proof audit"?

Split proof must include:

- [ ] candidate affordance ID;
- [ ] source lines;
- [ ] different `use_when`;
- [ ] different `case_evidence_needed`;
- [ ] different `do_not_use_when`;
- [ ] different treatment requirement;
- [ ] different misuse guard;
- [ ] different receiver action;
- [ ] reason it is not merely an absence or supporting detail.

If the proof fails:

- [ ] keep one affordance;
- [ ] enrich absence/misuse guards instead.

## Stage 3: P2 Stratified Sampling

Sample buckets:

- broad/meta one-affordance records;
- zero-absence multi-affordance records;
- one-affordance high-source-ref records;
- medium-confidence records;
- absence-heavy records;
- late controlled one-affordance records;
- a control group of obviously narrow cards.

Initial P2 queue heads:

- `decision-trees`
- `markov-chains`
- `optionality`
- `power-dynamics`
- `chain-of-thought`
- `latticework-of-mental-models`
- `mental-models-of-reality`
- `meta-cognitive-reflection`
- `reasoning-mode-router`
- `antifragility`
- `multi-criteria-decision-analysis`
- `pareto-principle`
- `resilience`

Acceptance:

- [ ] Stop sampling only after new source-read patterns stop appearing.
- [ ] Preserve complete-as-compressed records.
- [ ] Record every dropped candidate and why it is not transaction-distinct.

## Stage 4: v19 Candidate List

Only after the source adequacy ledger, produce a candidate list:

```text
model_id:
recommended_change:
change_type: positive_affordance | absence_enrichment | rewrite | no_change
source_lines:
transaction_difference:
risk_if_unchanged:
risk_if_changed:
```

Acceptance:

- [ ] No bulk enrichment.
- [ ] No record edited without source-line support.
- [ ] Every new positive affordance must change downstream receiver behavior.
- [ ] Absence enrichment is preferred over positive expansion when the issue is overclaim risk.

## Stage 5: Targeted v19 PR

Only after PR56 passes:

- create a separate v19 branch;
- edit selected records only;
- recompile artifact;
- update quality report;
- add tests for changed records;
- keep artifact `draft_review_only`;
- keep runtime import guard.

## Stage 6: Packet Shape Before Runtime

After source adequacy and targeted v19, return to PR55 packet blockers:

- grouped per-affordance cards;
- confidence visibility;
- weak-support warnings;
- absence blockers;
- duplicate provenance aggregation;
- broad/meta caps;
- static replay packets.

Runtime testing remains blocked until these are addressed.

## Bottom Line

PR56 is the bridge between extraction and usefulness testing.

It should make us comfortable saying either:

- "this card is concise because the source has one operational transaction"; or
- "this card is compressed because coverage pressure made us too cautious, and here is the exact source-backed fix."
