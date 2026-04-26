# Lane 2 architecture research — frozen 2026-04-26

Status: **research artifact, NOT merged to main**
Branch: `feat/lane2-reasoning-type-partitioned-verifier-2026-04-26`
Tag: `lane2-architecture-research-2026-04-26`

## Why this branch is frozen, not merged

The branch contains v1 → v2 → v3 → B — four sequential architecture iterations of Lane 2's verifier. All four were measured against the pre-registered acceptance gates in `research/lane2-followup-tracking-2026-04-26.md`. None cleared the gates as written.

> v3 is the best Lane 2 verifier substrate discovered so far: it fixes the cost and over-acceptance failures introduced by finer-grained decomposition. However, it does not clear the pre-registered judgment-stability gates. The remaining failure appears to be a probabilistic floor in per-candidate verifier judgment and/or final anchor selection. Therefore v3 should be preserved as a research candidate, but not promoted to production default until paired with a consumer-side robustness design.

The discipline distinction matters: "best failed variant" is not the same as "merge-ready." Merging v3-only because it's directionally better than the baseline would silently change the experiment's meaning from "ship if gates pass" to "ship the best partial win." The gates existed to prevent that slope.

## What's preserved on the branch

Architecture iterations (committed on this branch only, NOT on main):
- **v1** — reasoning-type partition with parallel calls. Removed monolithic-call overload; introduced per-bucket over-acceptance.
- **v2** — added strict shared rubric (`activation_strength="strong"` + `why_not_merely_compatible`) + weak_matches category. Sorted candidates correctly but per-bucket accept floor remained.
- **v3** — replaced reasoning-type partition with rank-stratified 3-shard sharding. Cleared cost gate (22.4% verifier share) and accept-count mean gate (6.5). Did NOT clear judgment-stability gates (Accepted-pre 0.36 < 0.50, Cand-cond. 0.44 < 0.60).
- **B** — added global anchor calibrator after fan-in. Failed gates AND demonstrated that calibration as another LLM call adds variance rather than removing it (PhD regressed 0.51 → 0.16).

Research outputs:
- 4 measurement campaigns (v1, v2, v3, B) at 12 runs each (mostly), 8 paired ON-vs-OFF cases on the original baseline.
- Per-case stability artifacts in `research/stability-runs/`.
- Three interpretation notes:
  - `lane2-prb-v2-2026-04-26/interpretation.md` — v1+v2 reading
  - `lane2-prb-v3-2026-04-26/interpretation.md` — v3 reading + design conversation that produced Path B
  - `lane2-pathB-2026-04-26/interpretation.md` — B reading + the architectural-floor finding

## What landed in production from this work

The dedupe fix (PR #40, commit `7e2c2c5`) is already on main. That fix:
- Deduplicates verifier accepted entries by `model_id`.
- Fixed the `CompanionCard cannot contain more than 3 expansions per detected model` invariant trips that blocked `mother-deciding-address-year-lane2-off` during the original attribution campaign.
- Independently valuable; doesn't depend on any architecture iteration being "right."

The candidate-conditional verifier-stability metric (`shared_available_acceptance_agreement`) is also on main (PR #40). It's the metric used by all subsequent campaigns.

## What the data tells us about Lane 2

The architecture progression mapped the design space:

| Variant | Token cost | Accept count | Verifier judgment | Final anchor stability |
|---|---|---|---|---|
| Monolithic | low | 3–5 | unstable (~0.21) | unstable |
| v1 (reasoning-type partition) | high | 14.6 | improved per-bucket | over-acceptance |
| v2 (+ strict rubric) | high | 10.8 | improved | per-bucket floor remains |
| v3 (rank-stratified, 3 shards) | low ✓ | 6.5 ✓ | partial (0.36/0.44) | mixed (PhD strong) |
| B (+ global calibrator) | low | 2.9 ✓ | unchanged | regressed; calibrator adds noise |

**Empirical conclusion:** Lane 2's per-candidate verifier judgment has a probabilistic floor that no architecture-side change has cleared. v3 found the architectural sweet spot for cost and count; B confirmed that adding more LLM stages doesn't help the stability gap.

## What comes next

**Path D — Step 6 robustness.** Design a consumer-side architecture that handles probabilistic Lane 2 anchors gracefully rather than treating them as a deterministic top-5 list. Scope and design questions are in `research/lane2-pathD-step6-robustness-design-2026-04-26.md`.

The architecture-side investigation on Lane 2 stops with this branch. If Path D's product design later identifies a specific Lane 2 substrate it depends on (e.g., "we need v3's audit fields to compute a single-run stability proxy"), we revisit and selectively promote pieces. Until then: don't merge.

## Branch hygiene

- Branch: `feat/lane2-reasoning-type-partitioned-verifier-2026-04-26` (pushed; not deleted).
- Tag: `lane2-architecture-research-2026-04-26` (created at branch HEAD; pushed).
- Path D doc references this branch's commits and interpretation notes as evidence.
- If Path D conclusively decides Lane 2 should change, we cherry-pick or rebuild from this branch — not blanket merge.
