# Path D D0 — proxy validation interpretation

Date: 2026-04-26
Status: D0 complete; routes Path D to wording-only Step 6 changes
Companions:
- `report.md` — raw verdicts + per-case AUROC + threshold rules
- `proxy_rows.json` — 76 anchor-instance rows
- `research/lane2-pathD-step6-robustness-design-2026-04-26.md` — pre-registered Path D scope + gates

## Verdict

**No proxy clears D0 gates. Path D D1 routes to wording-only Step 6 changes** without proxy-driven differentiation.

| Proxy | Verdict | Pooled AUROC | Marcus collapse |
|---|---|---|---|
| `is_broad_overlay` | NO_SIGNAL | 0.475 | no |
| `final_rank` | WORDING_ONLY_EVIDENCE | 0.667 | YES |
| `evidence_quote_length` | NO_SIGNAL | 0.492 | no |
| `quote_collision_count` | NO_SIGNAL | 0.501 | no |
| `accepted_before_cap_position` | WORDING_ONLY_EVIDENCE | 0.666 | YES |
| `recall_source` | NO_SIGNAL (categorical, all "keyword") | n/a | n/a |

The two proxies with directional signal (`final_rank`, `accepted_before_cap_position`) at AUROC ~0.67 are **case-coupled**, not conversation-independent. Both fail the Marcus stress test by ≥0.55 AUROC: marcus-on values plummet to 0.08 / 0.58 against pooled 0.67. The proxy "works" on consultant/PhD/mother and inverts on Marcus. That's the conversation-independence axis doing its job: it surfaces the case-coupling that pooled AUROC alone hides.

## What this means

The pre-registration framed this clearly: "if proxies fail, we still ship wording-only Step 6 changes, but we do not ship tiered anchor metadata." The data says fail.

That's not a setback. It's the answer to the load-bearing technical question:

> Can we predict cross-run anchor stability from a single run using only deterministic substrate facts on `main`?

**No, not at the AUROC ≥0.70 / cross-case-stable bar we set.** The proxies that look directionally promising are too tightly coupled to specific case structures to support general-purpose tiering. Without a reliable single-run stability proxy, tiered Step 6 anchor metadata would be making confidence claims it cannot actually back.

## Why the surprises landed where they did

**`is_broad_overlay` AUROC 0.475 (slightly < 0.50):** broad-overlay models are SLIGHTLY MORE stable than non-broad in this dataset, the opposite of the prior. Two reads:
- The `_BROAD_OVERLAY_MODELS` set has only 6 entries with positive_rate 0.053 (4 of 76 rows). At that sample size, the AUROC is statistically indistinguishable from 0.50 noise.
- Or the curated broad-overlay list captures models that happen to be high-recall, well-evidenced models on these specific cases. They flip in/out of the cheat sheet just as readily as specific-mechanism models.

Either way, this proxy is too sparse to be load-bearing without a real broad-overlay curation pass — which the pre-registration explicitly flagged as out of scope for D0.

**`evidence_quote_length` AUROC 0.492:** the user's quick sniff was right. Quote length is heavily conversation-content-coupled and carries no stability signal. Confirmed.

**`quote_collision_count` AUROC 0.501:** dead null. Quote overlap between accepted models doesn't predict stability.

**`final_rank` and `accepted_before_cap_position`** are essentially the same signal at different stages — both code "this candidate was prominent in the input pipeline." They show modest pooled AUROC but heavy per-case variance. Reading the per-case table: in cases where the verifier broadly agrees with recall ranking (consultant-off, marcus-off), low rank predicts stability; in cases where verifier judgment overrides recall (marcus-on, phd-on, phd-off, mother-on, mother-off), the relationship inverts or breaks. The proxy doesn't measure stability; it measures whether the verifier is "going with the obvious top-of-recall picks" on a given run.

## Routing decision for Path D D1

**Wording-only Step 6 changes, no tiered metadata.** Lane 2 anchors stay prominent in Step 6, but the wording becomes evidence-proportional rather than canonical:

- Avoid "the answer is using X" unless the evidence quote is direct and specific.
- Use "appears to lean on", "possible lens", "adjacent risk", "one plausible structure" for anchors with weaker evidence.
- Don't force every anchor into equally prominent §1/§3 language. Let secondary anchors be acknowledged briefly or folded into caveats.
- The anchor-naming invariant in `SKILL.md:336` stays — every anchor must be addressed — but the wording weight is no longer uniform.

The pre-registered D1 wording-only gates:
- Anchor overclaim rate ≤ 10% on the 4-case audit set.
- Step 6 still names or uses the most evidence-supported anchor in ≥75% of runs.
- Secondary anchors framed as possible/adjacent rather than canonical in ≥90% of runs.
- Human review confirms the output feels more honest without becoming mushy.

## What we learned about Lane 2 stability (the deeper finding)

The architecture-side investigation (v1/v2/v3/B) and the proxy-side investigation (D0) converge on the same conclusion:

**Lane 2's per-candidate verifier judgment has a probabilistic floor that is NOT predictable from any single deterministic substrate fact we currently store.**

That's a real architectural finding, not a failure. It says:
1. The probabilistic-edges/deterministic-middle doctrine doesn't extend to "predict stability deterministically from one probabilistic run." Single-run determinism doesn't recover multi-run stability.
2. The right product contract is: Lane 2 anchors are evidence-bearing hypotheses, not canonical facts. Step 6 must consume them accordingly.
3. Future Path D iterations could try richer substrate proxies (curated broad-vs-specific, edge density in the relationship graph, archetype-specific stability priors) IF a separate research effort produces them. None are on `main` today, and the wording-only path doesn't depend on them.

## Next concrete artifact

Path D D1 design doc. NOT code. The doc should specify:
- Concrete `SKILL.md:320` Step 6 wording rules per anchor evidence-strength tier (single-run heuristic, not multi-run-dependent).
- Concrete D1 acceptance gates as already pre-registered in the Path D scoping doc.
- Audit method: small human-review pass on the existing 4 archived cases (Marcus, consultant, PhD, mother) where revised_answer is persisted. Compare current Step 6 wording against proposed wording rules.

After the design doc lands and is reviewed, we implement the wording rules in `SKILL.md` directly (no engine changes; this is a Step 6 contract change).

## Methodology recap

- 8 baseline campaigns (PR #39 / PR-A substrate; pre v2/v3/B).
- 22 runs, 30 unique models surfaced as anchors-or-accepted, 76 anchor-instance rows.
- Stable label: appeared in ≥2/3 runs per case-mode.
- 51.3% positive class balance — well-balanced for AUROC.
- AUROC: Wilcoxon-Mann-Whitney with tie correction. Pooled + per-case-mode.
- Marcus stress test: per-case Marcus AUROC must be within 0.15 of pooled, else explicit caveat.
- No LLM calls.
