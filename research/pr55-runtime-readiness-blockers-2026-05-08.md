# PR55 Runtime Readiness Blockers

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Status: review-only gate list

Scope: what must be true before any future live `/lolla` pickup experiment can use v18 or later reviewed affordance artifacts.

## Verdict

Runtime readiness is blocked.

Dormant reviewed substrate is acceptable. Live pickup is not.

The blocker is not corpus coverage. v18 covers the runtime model set. The blocker is whether reviewed cards can survive pickup, compression, display, and LLM use without losing epistemic shape.

## Gate Table

| Gate | Current status | Runtime verdict | Required before live pickup |
| --- | --- | --- | --- |
| Full model coverage | v18 has 222 records. | PASS dormant | No extraction needed for coverage. |
| Live pickup absence | No v18 references found in `engine/` or `scripts/`. | PASS safety | Keep this until explicit runtime PR. |
| Runtime import guard | Existing guard tests assert v18 is not imported by live runtime paths. | PASS safety | Preserve until approved experiment. |
| Explicit artifact selection | Packet producer defaults to v4 unless path is passed. | REVISE before adapter | Future adapter must pass an explicit artifact path and should fail closed if missing. |
| No "latest artifact" magic | No live latest-glob pickup found. | PASS safety | Keep forbidden. |
| Grouped affordance identity | Current packet flattens reviewed fields. | BLOCK live | Add grouped per-affordance card structure. |
| Decoder transaction grammar | Not implemented. | BLOCK live | Define use/reject/defer/merge/block ledger before receiver experiment. |
| Confidence visibility | Confidence exists internally but is not first-class in review display. | REVISE | Render confidence and medium/weak status visibly. |
| Weak-support warning | Weak records map to weak/conflicting coverage, but warning is quiet. | BLOCK live | Add explicit warning and non-promotion rule. |
| Absence visibility | Absences exist, but renderer shows one item per field. | BLOCK live | Promote absences into overclaim rails and blockers. |
| Lane provenance contract | Lane surfaces exist, but no adapter contract is implemented. | REVISE | Implement provenance-preserving nomination adapter, still dormant. |
| Duplicate provenance aggregation | Current packet dedupes by model ID and can lose later reasons. | BLOCK live | Merge provenance before dedupe or extend packet schema. |
| Broad/meta card discipline | Broad cards can appear in normal packet caps. | REVISE | Add broad/meta cap or visible pressure label. |
| Packet cap behavior | 12-card packets are plausible; 16-card packets are heavy. | REVISE | Stress caps with static fixtures and replay cases. |
| Renderer truncation | One item per reviewed detail field. | REVISE | Keep compact review mode, but add grouped transaction view or selected blocker view. |
| Receiver instruction | Existing packet instruction is review-oriented. | REVISE | Add candidate-material-not-mandatory rubric before receiver use. |
| Final-answer pressure | No live final pressure from v18. | PASS safety | Do not add deterministic final selection. |
| Offline replay | Not yet done for v18 pickup. | BLOCK live | Generate static replay packets from archived cases before any live test. |

## Minimum To Move From BLOCK To Experiment Candidate

A future PR could move toward live experiment only after these are true:

1. A dormant lane-to-nomination adapter preserves lane provenance.
2. Duplicate nominations are provenance-merged, not silently discarded.
3. Packet internals preserve grouped affordance identity.
4. Renderer or receiver handoff shows confidence and weak-support warnings.
5. Absence records are visible as blockers or overclaim rails.
6. Broad/meta cards have cap discipline.
7. Artifact selection is explicit and fail-closed.
8. Static replay packets remain compact and useful.
9. A decoder ledger can say what was used, rejected, deferred, merged, or blocked.
10. No live `/lolla` path imports the artifact until the above is reviewed.

## What PR55 Should Not Do

PR55 should not:

- add live pickup;
- inject v18 into product prompts;
- auto-select v18 as latest artifact;
- split records into v19 by default;
- use model calls to justify extraction changes;
- make Python choose final reasoning moves;
- convert broad cards into strategic priority signals.

## What PR55 Should Do

PR55 should:

- document distribution quality;
- identify richness red flags;
- stress packet compactness;
- show traceability blockers;
- draft lane provenance contract;
- define runtime readiness gates;
- keep all work dormant and reviewable.

## The Product Smell To Avoid

The bad outcome is not that the system fails to use enough mental models.

The bad outcome is that the system starts sounding more thoughtful while merely passing a larger, more authoritative-looking set of internal model names into the next stage.

The reviewed substrate should make reasoning less wrong, not more decorative.

## Bottom Line

v18 can be merged as knowledge-base substrate if the PR is clearly scoped as audit and dormant hardening.

It should not be merged as runtime pickup readiness.
