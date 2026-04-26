# Path D — Step 6 robustness to Lane 2 anchor variance

Date: 2026-04-26
Status: design scoping (no code yet)
Companions:
- `research/lane2-architecture-research-frozen-2026-04-26.md` — why architecture-side iteration on Lane 2 stops here
- `research/stability-runs/lane2-pathB-2026-04-26/interpretation.md` — the data + decision that produced this pivot
- `SKILL.md` — current Step 6 contract (the surface this doc proposes to redesign)

## The question

The Lane 2 architecture experiments (v1 → v2 → v3 → B) mapped the design space and reached a clear conclusion: per-candidate verifier judgment has a probabilistic floor that LLM-side architecture changes cannot cross. The verifier sometimes flips the same model accept↔weak across runs of the same conversation. Adding more LLM stages (Path B's calibrator) doesn't smooth this out — it adds new variance.

This is not a Lane 2 failure; it's an LLM property. The right move is to stop pretending Lane 2 produces a deterministic anchor set and **redesign the consumer (Step 6) to handle anchors as probabilistic evidence rather than canonical truth**.

The core question this doc must answer:

> **How should Step 6 use Lane 2 output when anchors are probabilistic evidence rather than a canonical top-5 list?**

The answer needs to work in production where typically only N=1 run exists per conversation — we cannot rely on N=3 stability sampling at user-facing latency.

## Why this is the right framing

Three reasons the data supports this pivot:

1. **The architecture floor is mapped.** v1 → v2 → v3 → B explored four architectural axes (granularity, calibration rubric, sharding, post-fan-in calibration). v3 cleared cost and count gates; none cleared judgment-stability gates. The remaining variance lives in LLM judgment, not in pipeline shape.
2. **Calibration as another LLM stage doesn't help — it hurts.** Path B's calibrator added run-to-run variance on top of verifier variance (PhD: 0.51 → 0.16). This is empirical evidence that you can't stabilize probabilistic judgment by stacking another probabilistic stage.
3. **The product contract is the wrong abstraction.** Currently `SKILL.md`'s anchor-naming invariant treats every cheat-sheet anchor as canonical: "every anchor must end up in §1, §2, or §3." That assumes the anchor set is a deterministic ground truth. When anchors are probabilistic evidence, this contract makes Step 6 over-confident in unstable signal.

## Design directions (proposed by the v3/B design conversation)

Four candidate shapes, ordered roughly from least to most invasive:

### 1. Step 6 wording changes
Smallest delta. Keep Lane 2 output shape unchanged; change how Step 6 references anchors.

Current (canonical):
> "The answer is leaning on Endowment Effect."

Proposed (probabilistic):
> "The answer appears to be leaning on Endowment Effect — a likely structural lens; secondary candidates Loss Aversion and Sunk Cost Fallacy may also apply."

Open question: does wording alone reduce false confidence, or do users still anchor on the named model?

### 2. Stability-tiered anchors
Add a tier per anchor based on a confidence proxy. Step 6 routes by tier.
- **Stable core:** high-confidence proxy → §1 / §3 weight (drove or absorbed pressure).
- **Variable candidates:** lower-confidence proxy → §2 (set aside with reason "appeared with weaker structural evidence").
- The anchor-naming invariant stays — every anchor must be addressed — but the wording weight follows the tier.

Open question: what's the confidence proxy? See "Single-run stability proxy" below.

### 3. Anchor distribution, not top-5 list
Restructure Lane 2 output. Instead of a flat `anchors[]`, produce:

```json
{
  "stable_core": [...],
  "secondary_candidates": [...],
  "weak_or_borderline": [...]
}
```

Step 6 consumes this richer structure and renders accordingly. More invasive: changes Lane 2's output contract, downstream renderer (Observatory), memo template, anchor-naming invariant, and SKILL.md instructions.

Open question: does the richer structure actually improve Step 6 quality, or just add complexity without evidence of benefit?

### 4. Multi-run sampling (production-impractical baseline)
Run Lane 2 N=3 times per conversation, derive stability from cross-run frequency. Display anchors with cross-run counts: "Endowment Effect: 3/3, Loss Aversion: 1/3."

This is the gold-standard signal but **not viable in production** at typical latency budgets. It is, however, a useful thought experiment: the proxies in option 2 should approximate what multi-run sampling would tell us, ideally without actually running 3 times.

## The real challenge: single-run stability proxies

Production typically runs N=1. We can't measure cross-run frequency at user-facing latency. So Path D's load-bearing technical question is:

> **What signals from a single Lane 2 run plausibly indicate that a given anchor would be stable across hypothetical re-runs?**

Candidate proxies (need empirical validation):

- **Recall rank dominance**: the anchor's `final_rank` was high (e.g., top 10 of 60). High-rank candidates are more likely to be selected by the verifier across runs because the input itself is consistent.
- **Multi-source recall**: `recall_source = "both"` means keyword AND embedding recall surfaced this candidate. Two independent paths agreeing is evidence of robustness.
- **Strict-rubric strength**: the verifier supplied strong `why_not_merely_compatible` evidence (post-v2). Anchors with weak/short `why_not_merely_compatible` may be borderline.
- **Shard agreement (if v3 substrate enables this)**: under rank-stratified sharding, an anchor that survives a shard with low overall acceptance rate (the shard was selective) is more likely stable than one from a shard that accepted everything.
- **Weak-conflict count**: how many `weak_matches` overlap the anchor's `model_id` family or evidence passage? More overlap = more borderline.
- **Specific vs broad classification**: broad-overlay models (second-order-thinking, systems-thinking) inherently flip more than specific-mechanism models (authority-bias, opportunity-cost). The substrate already knows which is which.

These proxies are **hypotheses**, not validated metrics. The Path D campaign's job is to validate which of these (alone or in combination) actually correlates with cross-run stability on the existing v3 / monolithic baselines.

## How we'd validate Path D

The validation campaign needs both:
1. **Multi-run ground truth.** Pick the same 4 cases (Marcus, consultant, PhD, mother) and use the existing N=3 v3 runs as ground truth for "this anchor was stable" (appeared in ≥2/3 runs) vs. "this anchor was unstable" (appeared in 1/3).
2. **Single-run proxy correlation.** For each anchor across the runs, compute the candidate proxies (recall rank, recall source, strict-rubric evidence length, etc.). Measure: do anchors with "high" proxy values correlate with anchors that turned out to be cross-run-stable?

Pre-registered proxy validation gates (placeholder; refine in scope conversation):
- A proxy is **load-bearing** if its high-vs-low split correlates with cross-run stability at AUC ≥ 0.70.
- A proxy combination is **robust** if it correctly classifies stable-vs-unstable anchors with precision ≥ 0.75 and recall ≥ 0.60 on at least 3 of 4 cases.
- Marcus stays in the validation set; if a proxy works on consultant/PhD/mother but fails on Marcus, that's evidence Marcus has a structural ambiguity the proxy can't detect.

If a proxy clears these gates, we move to Step 6 wording / tier / structure changes that consume the proxy. If no proxy clears, Path D becomes "wording-only changes": Step 6 gets more tentative language without claiming any tier, because we have no reliable single-run signal.

## Pre-registered scope: what Path D is and is not

**In scope:**
- Empirical validation of single-run stability proxies against the existing v3 multi-run data.
- Wording changes in `SKILL.md` Step 6 instructions to reduce false confidence.
- Optional (gated by proxy validation): stability-tiered anchor metadata in `companion_cheat_sheet`.
- Optional (gated by validation): the anchor-naming invariant routing by tier.

**Out of scope:**
- Any further Lane 2 verifier architecture iteration. (The architecture floor is mapped.)
- Promoting the v3 substrate to production default. (That decision waits on Path D's validation result; if v3's audit fields turn out load-bearing for the proxies, we revisit.)
- Multi-run sampling in production. (Latency-prohibitive.)
- Reranker / calibrator-style LLM stages. (B failed; pre-registered no-iterate.)

**Open questions to settle in the next design session:**
1. Which proxies do we validate first? (Suggested order: recall rank, multi-source recall, broad-vs-specific — cheapest to compute from existing data.)
2. What's the unit of validation — per anchor across runs, per case, or both?
3. Does the validation campaign use only existing v3 data, or does it require a fresh measurement run?
4. If proxies fail validation, do we still ship wording-only changes, or do we accept that Lane 2 anchors are inherently noisy and lower their prominence in Step 6 entirely?
5. How does this interact with the cheat-sheet semantic rerank (currently powered by embeddings)? Is rerank itself a stability source or noise source?

## Reference: what Lane 2 produces today (post-PR-A on main)

For Path D's design grounding, here's what one Lane 2 run produces in production today (without v3/B research changes):

- `companion_cheat_sheet.anchors[]` — the consumer surface; up to 5 anchors with `display_name`, `presence_mode`, `evidence_quote`, chunks (failure_modes, premortems, antagonists, allies, heuristics, identity).
- `audit_summary.companion_candidates[]` — recall input with `recall_source`, `keyword_rank`, `embedding_rank`, `final_rank`. (PR #39 / PR-A.)
- `audit_summary.companion_verification_accepted_before_cap[]` — the verifier's full strong set before top-5 truncation. (PR-A.)
- `audit_summary.companion_verification_capped_models[]` — accepted-but-truncated. (PR-A.)
- `audit_summary.companion_verification_duplicate_accepts[]` — verifier-side dedupe drops. (PR-A.)

These fields are the substrate for proxy computation. They're already on main.

What's NOT on main (sits on the frozen research branch):
- Strict-rubric `activation_strength` + `why_not_merely_compatible` per accepted item (v2).
- `companion_verification_weak_matches[]` (v2).
- `companion_verification_shard_breakdown` (v3).
- Per-shard rank-stratified verifier output.

If a proxy needs any of these v2/v3 fields, that's a forcing function to selectively promote those pieces from the frozen branch.

## What this doc is asking for

A scoping conversation that decides:
1. **Confirm the framing.** Is "Step 6 should consume Lane 2 anchors as probabilistic evidence" the right product-level reframe?
2. **Pick the proxies to validate first.** From the candidate list above, which 2–3 are cheapest to compute and most likely to correlate with cross-run stability?
3. **Decide the validation unit.** Per anchor, per case, per run, or some combination.
4. **Choose between wording-only vs proxy-driven changes.** If proxies fail, are we OK shipping wording-only Step 6 changes as the Path D outcome?
5. **Set Path D acceptance gates.** What does "Path D succeeded" look like, in pre-registered terms?

After this scoping conversation, Path D becomes a measurable, testable plan with its own pre-registered gates and falsification clause. Same discipline that kept Lane 2's architecture work honest.
