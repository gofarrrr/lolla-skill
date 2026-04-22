# Track B — Pass 1 Clustering — Phase 1 Research

## Status

**Research artifact, not shipped. Pending user review of the taxonomy.**

Part of the Cycle-1 sequence per `research/llm-decomposition-handover.md` §0g step 4. This document is the "re-read each of the 25 Munger tendencies in `prompts.py` and confirm the clustering is semantically clean" validation the handover requires before Phase 2 implementation.

## What was found reading `engine/system_b/prompts.py` + `data/knowledge_graph.json`

The Pass 1 system prompt (`PASS_1_TRIAGE_SYSTEM`) scores all 25 Munger tendencies in a single LLM call with 9 general "CRITICAL RULES" + 11 "COMMON CONFUSION GUARDRAILS" — exactly the overload shape the handover §4b identified.

The canonical 25 tendencies (from `data/knowledge_graph.json`):

1. reward-and-punishment-superresponse-tendency
2. liking-loving-tendency
3. disliking-hating-tendency
4. doubt-avoidance-tendency
5. inconsistency-avoidance-tendency
6. curiosity-tendency
7. kantian-fairness-tendency
8. envy-jealousy-tendency
9. reciprocation-tendency
10. influence-from-mere-association-tendency
11. simple-pain-avoiding-psychological-denial
12. excessive-self-regard-tendency
13. overoptimism-tendency
14. deprival-superreaction-tendency
15. social-proof-tendency
16. contrast-misreaction-tendency
17. stress-influence-tendency
18. availability-misweighing-tendency
19. use-it-or-lose-it-tendency
20. drug-misinfluence-tendency
21. senescence-misinfluence-tendency
22. authority-misinfluence-tendency
23. twaddle-tendency
24. reason-respecting-tendency
25. lollapalooza-tendency

## Issues with the handover's draft taxonomy

The handover §Track B listed this draft (normalized to canonical names where possible):

| Draft cluster | Draft members | Issue |
|---|---|---|
| authority | authority-misinfluence, doubt-avoidance, reciprocation, liking-loving, social-proof | Mixes authority/influence with doubt-avoidance (closure, not social pressure) |
| incentive | "incentive-caused-bias", reward-and-punishment, envy-jealousy, "self-serving" | `incentive-caused-bias` and `self-serving` are NOT in the canonical catalog |
| stress_commitment | stress-influence, inconsistency-avoidance, "commitment-and-consistency", deprival-superreaction | `commitment-and-consistency` is NOT canonical (likely same as inconsistency-avoidance) |
| availability | availability-misweighing, contrast-misreaction, over-optimism, excessive-self-regard | Mixes denominator errors with self-enhancement |
| residual | curiosity, kantian-fairness, simple-psychological-denial, use-it-or-lose-it, drug-misinfluence, senescence, "false-consensus", lollapalooza, twaddle | `false-consensus` NOT canonical; `simple-psychological-denial` should be `simple-pain-avoiding-psychological-denial`; lollapalooza belongs in the compound-check pass, not a triage cluster |

**Three canonical tendencies unassigned in the draft:** `disliking-hating-tendency`, `influence-from-mere-association-tendency`, `reason-respecting-tendency`.

## Proposed revised taxonomy (6 clusters + lollapalooza)

Grouping principle: tendencies that **confuse with each other** (per the current prompt's 11 confusion guardrails) cluster together; quirky residuals keep their own bucket; lollapalooza is handled by the separate compound-check pass per handover §Track B.

### Cluster 1 — Authority & Social Influence (5)

**Members:** authority-misinfluence, social-proof, influence-from-mere-association, liking-loving, reciprocation

**Theme:** judgment distorted by prestige, peer behavior, halo, affection, or favor — "external endorsement treated as evidence."

**Confusion guardrails to include:** Authority vs Social Proof (both in the prompt), Influence-from-Mere-Association (prompt guardrail), Liking/Loving (prompt guardrail), Reciprocation (prompt guardrail). **5 of the 11 guardrails live here.**

### Cluster 2 — Closure Under Pressure (4)

**Members:** doubt-avoidance, inconsistency-avoidance, deprival-superreaction, stress-influence

**Theme:** pressure (time, loss, prior commitment) causes premature closure — "don't let me reconsider."

**Confusion guardrails to include:** Doubt Avoidance, Deprival Superreaction, Stress Influence, Inconsistency Avoidance. **4 of the 11 guardrails live here.**

### Cluster 3 — Reward / Incentive / Norm (3)

**Members:** reward-and-punishment-superresponse, envy-jealousy, kantian-fairness

**Theme:** motivational forces — incentives, peer-comparison, norm-of-fairness — driving the decision as causal mechanism.

**Confusion guardrails to include:** Reward and Punishment Superresponse. **1 of the 11.**

*Borderline:* `kantian-fairness` could alternatively join Cluster 1 (norm-of-reciprocity) — its "fairness as entitlement" flavor connects to reciprocation. Current placement: Cluster 3 because the failure mode is motivational (what drives the claim) rather than influence-borrowing (how the claim gets authority).

### Cluster 4 — Availability / Denominator (2)

**Members:** availability-misweighing, contrast-misreaction

**Theme:** cognitive denominator errors — vivid recent evidence or extreme anchors crowd out base rates.

**Confusion guardrails to include:** Availability Misweighing. **1 of the 11.**

*Note:* This is a small cluster (2 tendencies). Worth keeping separate because the failure mode is *structural* (wrong denominator) rather than emotional (self-regard) or social (halo). Mixing with overconfidence would muddy the guardrails.

### Cluster 5 — Self-Regard / Emotion (5)

**Members:** overoptimism, excessive-self-regard, simple-pain-avoiding-psychological-denial, disliking-hating, reason-respecting

**Theme:** self-referential filters that distort — "I already have an answer I prefer" / "I dislike this person so their claim is weaker" / "flimsy reasons are accepted because they confirm."

**Confusion guardrails to include:** None currently in the prompt. New triage cluster may need its own disambiguation guardrails (e.g., overoptimism vs excessive-self-regard; denial vs doubt-avoidance).

### Cluster 6 — Quirky Residual (5)

**Members:** curiosity, use-it-or-lose-it, drug-misinfluence, senescence-misinfluence, twaddle

**Theme:** tendencies that don't fit the standard failure-mode taxonomy — Munger's "quirky" chapters. Keeping together rather than forcing bad family placement.

**Confusion guardrails to include:** None.

### Separate — Lollapalooza

`lollapalooza-tendency` is NOT assigned to any triage cluster. Per handover §Track B, lollapalooza is the output of the **compound-check pass** that runs after the 6 clusters return: "Among these triggered tendencies, are 3 or more converging on the same passage or reasoning move?"

This addresses the handover's note that lollapalooza can't be meaningfully triaged as a standalone tendency within a cluster — it's inherently a compound signal.

## Coverage verification

Total: 5 + 4 + 3 + 2 + 5 + 5 = 24 tendencies across 6 clusters + lollapalooza = **25 canonical tendencies**, all assigned, no duplicates.

Guardrail distribution:
- Cluster 1 (Authority/Social): 5 of the 11 current guardrails
- Cluster 2 (Closure): 4 of the 11
- Cluster 3 (Reward/Incentive): 1
- Cluster 4 (Availability): 1
- Clusters 5, 6: 0 (may need new, intra-cluster guardrails)

**Obligation load per call:** 4-5 tendencies (vs 25), plus only cluster-relevant guardrails (0-5 vs 11). Significantly narrower than the current prompt.

## Compound-check pass design

Runs *after* the 6 cluster triage calls return. Input: the vanilla answer + the combined triggered-tendency list from all clusters (IDs only). Objective: "Among these triggered tendencies, are 3 or more converging on the same passage or reasoning move? If yes, flag as compound and name the converging passage." Output: zero or one compound record consumed by DeltaCard assembly.

Cost: one small call. Handover estimates ~$0.002/run.

## Implementation scope (Phase 2+)

1. **Prompt authoring.** 6 cluster prompts + 1 compound-check prompt. Each ~20-30 lines. Tone and shape mirror `deep_checks.py:230` (Pass 2) — narrow objective, bounded input, cluster-only guardrails.
2. **Prompt versioning.** Register 7 new IDs in `prompt_versioning.py`: `pass1_authority_v1`, `pass1_closure_v1`, `pass1_incentive_v1`, `pass1_availability_v1`, `pass1_self_regard_v1`, `pass1_residual_v1`, `pass1_compound_check_v1`.
3. **Pipeline wiring.** Extend `pipeline.py` `_run_pass1_*` (analogous to `_run_pass2_parallel`) to fan out 6 cluster calls in parallel, aggregate triggered tendencies, then run compound-check sequentially.
4. **Backward compat.** Old `PASS_1_TRIAGE_SYSTEM` stays but becomes unused. Can be retired in a follow-up commit once cluster path is validated.
5. **Harness validation.** Mode B rerun on Run 5's extraction with N=3 against the new cluster path. Compare Pass 1 Jaccard to the 0.40-0.50 range from the 5-run baseline and the 1.00 fixed-extraction snapshot.

Estimated work: half-day to day scale. Handover cost estimate: +$0.004-0.007/run (6 small parallel calls + 1 compound check) — small cost bump, wall-clock unchanged thanks to parallel fan-out.

## Questions for user review

1. **Cluster 3 `kantian-fairness` placement** — keep in Reward/Incentive, or move to Authority/Social (as a reciprocity-family cognate)? Argument for staying in Cluster 3: the failure mode is the norm driving the decision motivationally. Argument for moving to Cluster 1: confusion with reciprocation.
2. **Cluster 4 size** — 2 tendencies is small. Acceptable because the failure mode is structurally distinct, OR merge with Cluster 5 and accept a larger cluster?
3. **5 vs 6 clusters** — handover said "~5." I'm proposing 6 because the semantic boundaries are cleaner. If you prefer 5, we merge Cluster 4 into Cluster 5 (result: 7-item Self-Regard/Emotion/Availability cluster; slightly muddier but still workable).
4. **Should the old monolithic prompt stay as a rollback option**, or is git history rollback sufficient (mirroring the C-step1-3 decision)?

Once these are resolved, Phase 2 implementation can proceed.
