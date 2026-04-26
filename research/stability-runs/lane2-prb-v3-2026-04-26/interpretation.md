# PR-B v3 — interpretation

Date: 2026-04-26
Status: post-campaign reading; gates partially pass; decision-pending
Companions:
- `research/lane2-followup-tracking-2026-04-26.md` — pre-registered scopes + gates
- `research/stability-runs/lane2-attribution-2026-04-26/synthesis.md` — baseline (monolithic)
- `research/stability-runs/lane2-prb-v2-2026-04-26/interpretation.md` — v1+v2 reading
- `research/stability-runs/lane2-prb-v3-2026-04-26/synthesis.md` — v3 cross-case data (this campaign)

## Headline

**v3 cleanly passes the load-bearing structural gates (cost, accepted count mean, recall stability). It narrowly misses the per-judgment stability Jaccard gates by 0.02–0.16 points.** The granularity hypothesis was right; the per-judgment-stability question remains.

## Three-way comparison

| Metric | Baseline | v2 | **v3** | Gate | v3 pass? |
|---|---|---|---|---|---|
| Accepted-pre Jaccard mean | 0.21 | 0.31 | **0.36** | ≥ 0.50 | ❌ |
| Accepted-pre Jaccard worst | 0.06 | 0.21 | **0.28** | ≥ 0.30 | ❌ (off by 0.02) |
| Cand-cond. mean | 0.28 | 0.35 | **0.44** | ≥ 0.60 | ❌ |
| Cand-cond. worst | 0.06 | 0.23 | **0.31** | ≥ 0.35 | ❌ (off by 0.04) |
| Candidates Jaccard mean | 0.72 | 0.80 | 0.78 | ±0.05 | ✅ |
| **Accepted count mean** | 3–5 | 10.8 | **6.5** | 2–7 | ✅ |
| Accepted count worst | ~5 | 18.0 | **7.7** | 2–7 | ❌ (off by 0.7) |
| All-zero accepted | 0 | 0 | 0 | 0 | ✅ |
| **Verifier token share** | 9–16% | 41% | **22.4%** | ≤ 30% | ✅ |
| Weak matches per run | n/a | 42 | 34.6 | diagnostic | ✅ |

## What v3 demonstrably fixed

1. **Verifier token share: 41% → 22.4%.** Cleared the gate by ~7 points. Three shards instead of 4–9 means roughly the same total verifier tokens as monolithic — the fixed context (system prompt, rubric, assistant text, fingerprint) repeats only 3× instead of 4–9×. Empirically, mother-deciding has the highest share at 29.8% (still under gate); marcus/consultant/phd are at 18–21%. **Granularity was the cost driver.**

2. **Accepted count mean: 10.8 → 6.5.** Cleared the 2–7 gate at the mean level. Per-case: marcus 6.7, consultant 6.0, phd 5.7, mother 7.7. Per-shard breakdown on mother-run-0: each shard accepted 3 (totaling 9), dedupe to 7–8. The structural floor IS roughly `n_shards × ~2-3` as predicted; with 3 shards, the floor sits at 6–9 — close enough to the 2–7 gate that mean clears.

3. **PhD case-level breakthrough.** PhD anchors went 0.16 (v1) → 0.45 (v2) → **0.51** (v3). PhD Cand-cond. went 0.47 → 0.38 → **0.71**. PhD case alone clears the Cand-cond. gate (≥ 0.60) decisively. PhD was the previously most-overloaded case; it got the most help from the architecture progression.

## What v3 didn't fully fix

The per-judgment stability gates are within striking distance but not cleared:

- **Accepted-pre worst 0.28** (gate 0.30) — `mid-level-consultant-decides` is the holdout. Same case where v1 had 0.65 and v2 had 0.33 — the variance there is inherently high.
- **Cand-cond. worst 0.31** (gate 0.35) — `marcus-equity` is the holdout. Marcus has been stuck at ~0.13 anchor stability across all three architecture variants.
- **Accepted count worst 7.7** — mother-deciding accepts an average of 7.7, just over the upper bound of 7. The "0-2 per shard soft cap" is being respected on average (3 shards × 2.5 = 7.5) but not strictly.

The mother-shard-1 breakdown reveals a tell: 20 candidates → 3 accepted, **18 weak**, 0 rejected. The verifier is using `weak_matches` as a soft-reject category rather than rejecting outright. That's the rubric working — but it also explains why the strict accepts/weaks split doesn't fully translate to per-judgment Jaccard improvement: indecision moves from "accept/reject coin flip" to "accept/weak coin flip" in cases like this.

## What this tells us about Lane 2

The architecture progression validated three claims:
1. **Decomposition reduces overload.** v1's monolithic-vs-partitioned cost split confirmed it.
2. **Strict shared rubric restores calibration.** v2's weak_matches sorting confirmed it.
3. **Coarser granularity restores cost AND competition.** v3's token-share + count clears confirmed it.

What it has NOT confirmed:
- **Per-candidate verifier judgment is fully stabilizable through architecture alone.** Even with 3 stratified shards + strict rubric + soft cap, the LLM's accept/weak decision varies run-to-run on borderline candidates. There appears to be an irreducible probabilistic floor at ~0.30–0.45 Cand-cond. for hard cases (marcus, consultant). PhD is now above that floor (0.71); other cases plateau around 0.30–0.42.

## The pre-registered next conversation

The follow-up tracking doc framed v3-fail as: "the next design conversation becomes **global calibration pass vs. Step 6 robustness**." That was right.

Two paths the data now supports — neither is "iterate v3 again":

**Path B (global calibration pass).** Add a single LLM call after fan-in: "rank these 6–8 strong accepts by structural load-bearing, surface top 5 with reasoning." Restores the global competitive comparison the monolithic verifier did, on a small input (just the union of strong accepts, not the full 60). Cost: one extra LLM call per run.

Pros: Targets the per-judgment-stability gap directly. Per-shard verifiers do their narrow job; reranker does the cross-shard calibration job. Each LLM call has one obligation.
Cons: Adds latency + cost (likely 5–15% additional verifier cost). Reranker stability becomes a new variable to measure. Could fail the same way v1/v2 did at this layer.

**Path D (Step 6 robustness).** Accept that Lane 2 has a per-candidate stability floor. Redesign Step 6 (the consumer) to handle probabilistic anchor variance gracefully — e.g., display "anchors observed across runs" with frequency counts instead of a single canonical set; or have Step 6 reason explicitly about which anchors are stable-core vs run-specific.

Pros: Targets the actual product problem (Step 6 over-trusting unstable anchor sets). Honest about LLM probabilistic limits. Could improve user-visible quality without further Lane 2 work.
Cons: A different problem to scope. Deferred from the current branch's job.

## What I'd recommend

**Don't loosen gates. Don't merge v3 as-is.** v3 is real progress on the structural gates but the judgment-stability gates were pre-registered for a reason and the variance signal in marcus/consultant matters.

I lean **Path B first.** It's a small, scoped, falsifiable next experiment:
- One additional LLM call after fan-in.
- Clear gate for evaluation: does Cand-cond. mean cross 0.60?
- Token cost rises modestly; verifier_share will rise from 22% but probably stay under 30% if the reranker is a single tight call.
- If B succeeds, we have the architecture: per-shard verifiers + global reranker + top-5 cap + strict rubric.
- If B fails the same way, we know stability has an irreducible floor and Path D is the answer.

Path D is a bigger surface area (touches Step 6, which is in `SKILL.md`) — worth doing, but only after we've genuinely exhausted the architecture-side improvements.

## Branch state

- v1 (commit history): reasoning-type partition, partial fix, over-acceptance.
- v2: partition + strict rubric, partial fix, structural per-bucket floor.
- v3 (current HEAD): rank-stratified shards + soft cap, structural gates pass, judgment-stability gates miss by small margins.

Tests: 372 passing. No regressions. Branch pushed but **NOT a PR**. Per the pre-registered "if any gate fails, do not merge" — the structural gates clearing is encouraging but doesn't override the failed stability gates.

Decision: Path B, Path D, or revise the v3 gate framing? Your call.
