# Activation Condition Doctrine Audit — Phase 0.5 Baseline

**Audit date:** 2026-04-21
**Audited against:** `data/relationship_graph.json` post-Phase-0 compile (867 edges with `activation_condition`)
**Sample:** 100 of 867 (seed=42, random, 11.5%)
**Split by edge type:** 61 ally / 39 antagonist (population: 523 ally / 344 antagonist — proportional)
**Rater:** Claude Opus 4.7 (single-pass)
**Source data:** `/tmp/phase0_5_sample.json`

---

## Rubric

Each activation_condition is rated as one of three categories:

| Category | Definition | Linguistic markers |
|----------|------------|--------------------|
| **cognitive-move** | Describes a reasoning operation or cognitive action the thinker performs or fails to perform. | Verbs of thinking/evaluating/testing/comparing; references to cognitive state (bias, belief, assumption, attention); contrasts between two reasoning approaches. |
| **situational** | Describes an external state, domain, topic, or organizational condition. Does not specify a cognitive move. | Passive voice about systems/structures; organizational/operational framing without reasoning content. |
| **mixed** | Blends cognitive-move language with situational framing. The move is present but diluted by topic or organizational content. | Both patterns coexist; the move is not cleanly isolable from the frame. |

**Why this rubric:** the matcher (Phase 3+) compares activation_conditions against reasoning-shape prose emitted by the deterministic lanes (`TriggeredTendency`, `FrameRoute`, `DimensionRoute`). Cognitive-move conditions match that prose at the right level of abstraction; situational conditions bind to topics the lanes don't emit. Mixed conditions match inconsistently — sometimes yes, sometimes no — and are the noise class the noise-floor guard in Phase 3 must absorb.

---

## Aggregate results

| Category | Count | % of sample | % of projection (867) |
|---|---|---|---|
| **cognitive-move** | **84** | **84.0%** | ~728 of 867 |
| situational | 8 | 8.0% | ~69 |
| mixed | 8 | 8.0% | ~69 |
| **Total** | **100** | **100.0%** | 867 |

### Split by edge type

| | cognitive-move | situational | mixed | n |
|---|---|---|---|---|
| **ally** | 50 (82.0%) | 6 (9.8%) | 5 (8.2%) | 61 |
| **antagonist** | 34 (87.2%) | 2 (5.1%) | 3 (7.7%) | 39 |

Antagonist edges rate slightly higher than ally because the natural linguistic form ("when bias X creates failure Y") is inherently cognitive. Ally edges have a small tail of operational/organizational framing ("when X mechanisms are established", "when scaffolding into procedures") that pushes them toward situational.

---

## Revision to prior estimate

The first-draft Section 14 audit (2026-04-21 morning) sampled 20 conditions and estimated ~45% cognitive-move. The 100-sample measurement here revises that to **84%**.

The 20-sample estimate was wrong for two reasons:
1. **Small-n variance.** 20 is too small to resolve an 84/8/8 distribution; any single clustering of situational cases could skew the estimate by 15+ points.
2. **Rater calibration drift.** The earlier spot check was informal; borderline cases that this audit classifies as cognitive-move were more easily labeled "ambiguous" without a formal rubric.

**The 45% figure in the prior Section 14 REV-1 commentary is superseded by 84%.** Handover Section 14's gates were designed around a conservative baseline — they still hold, just with the Phase 2 "≥ Layer 1+2 baseline" gate calibrated to 84% instead of 45%.

---

## Situational conditions (8)

These describe external state rather than cognitive action. Keeping them — they match some lane outputs (e.g. organizational-state prose) but will miss others. The Phase 3 matcher should abstain (noise-floor guard) when scoring them against purely cognitive-shape inputs.

| # | Edge | Condition | Why situational |
|---|---|---|---|
| 9 | social-proof → incentives (ally) | When reward structures align with or amplify herd behavior patterns | Describes structural alignment, not a cognitive move. |
| 28 | reciprocity-principle → incentives (ant) | When unspoken reciprocity obligations create shadow incentives that conflict with the formally designed incentive system. | Describes a social/structural condition; no reasoning action specified. |
| 55 | premortem → commitment-bias (ant) | When the team has already publicly committed to the plan and sunk cost makes reversing feel psychologically costly | Describes situation and psychological state; the "cognitive move" is implied elsewhere. |
| 70 | constraints → checklists (ally) | When identified constraints need to be converted into repeatable operational procedures... | Operational translation, not a reasoning action. |
| 78 | black-swan-events → checklists (ally) | When robust execution discipline is needed to close the gap between intellectual awareness... | Organizational execution framing. |
| 84 | psychological-safety → boundaries (ally) | When establishing clear behavioral boundaries creates the structured environment needed for safe, open dialogue. | Environment description, not cognitive action. |
| 94 | reciprocity-principle → psychological-safety (ally) | When a psychologically safe environment enables genuine reciprocal exchanges... | Environment state description. |
| 96 | principal-agent-problem → incentives (ally) | When designing mechanisms to align agent behavior with principal objectives... | Design/operational action, not a reasoning action. |

**Pattern:** situational conditions cluster around models that describe social/organizational structures (incentives, principal-agent, psychological-safety, constraints). These domains don't naturally emit "cognitive move" prose — the curator honestly described what the domain actually carries. This is not a correctable authoring defect; it's a boundary of the matcher's usable surface. The Phase 3 noise-floor guard must absorb it.

---

## Mixed conditions (8)

The move is present but diluted. Phase 3 matching against these will be unreliable — sometimes the move-laden clause is closest to the query, sometimes the situational clause is.

| # | Edge | Condition | Why mixed |
|---|---|---|---|
| 15 | power-dynamics → lock-in (ally) | When analyzing negotiations or partnerships where commitment costs are asymmetric and leverage may invert after integration or migration | "Analyzing" is cognitive but the bulk describes the situation. |
| 16 | iteration → status-quo-bias (ant) | When iteration cycles produce evidence for change but organizational inertia maintains the existing approach through ceremonial rather than genuine review | Organizational framing + "ceremonial vs genuine review" cognitive move. |
| 39 | tier-2-high-value → curse-of-knowledge (ant) | When abstract Tier-2 strategic thinking fails to translate into concrete, actionable implementation guidance | Describes a failure mode rather than specifying a cognitive move to make. |
| 54 | flow → feedback-loops (ally) | When sustained peak performance requires immediate feedback signals that enable rapid self-correction... | "Self-correction" is cognitive; "peak performance" is situational. |
| 63 | black-swan-events → resilience (ally) | When black-swan awareness needs to be converted into practical preparation through vulnerability reduction... | Operational "preparation" with a cognitive "awareness" frame. |
| 76 | survivorship-bias → confirmation-bias (ant) | When analyzing evidence for a hypothesis and the data comes predominantly from successful or surviving examples | "Analyzing" is cognitive; the data-selection description is situational. |
| 87 | habit-formation → scaffolding (ally) | When new habits must be built incrementally from simpler component behaviors... | Procedural strategy, not a reasoning move. |
| 98 | compounding → feedback-loops (ally) | When compounding depends on outputs being fed back as inputs... and understanding the feedback structure is needed... | "Understanding feedback structure" is cognitive, but wrapped in operational language. |

**Pattern:** mixed conditions are usually long, multi-clause strings where a clean cognitive-move sentence is padded with domain-specific color. They are the hardest class for the matcher because cosine similarity will catch whichever clause is closest in the query's embedding neighborhood — which may not be the cognitive-move clause.

---

## Implications for Phase 2 gate

**The 84% baseline is NOT Phase 2's gate** (this is a revision — an earlier draft of this document proposed it as one). It's a calibration input for Phase 3 matcher tuning.

Per the "curated corpus is the authority" principle (feedback memory, 2026-04-21): the activation_condition the corpus should carry for any given edge is whatever the canonical article actually supports — not whatever hits a cognitive-move target. If tension-prose in the articles is honestly less cognitive-move than ally-prose, a faithful re-read will rate lower, and that's correct. Demanding a distribution match would force synthesis beyond the source text.

**Revised Phase 2 gate (handover Section 14 REV-5):** faithfulness to source article. For each of 49 sampled tensions, every substantive claim in the extracted `affinity_rationale` and `activation_condition` must be traceable to specific prose in the canonical article. Failures: content synthesized to sound more cognitive-move than the source, conflation across sections, drift into commentary beyond what the article supports.

**How the 84% baseline is used downstream:**
- **Phase 3 noise-floor threshold calibration.** The matcher must abstain on approximately the 16% tail — whatever the tension distribution turns out to be, the threshold is set so that situational/mixed conditions fall below it and route to deterministic fallback. Fixture-calibrated, see below.
- **Sanity check after Phase 2 extraction.** If the post-extraction distribution looks wildly different from 84/8/8 (e.g., 40% cognitive-move), that's a signal to verify Phase 2's faithfulness gate actually held — either tensions really are less cognitive-move in the articles (fine), or the extraction drifted the other direction and ADDED situational framing beyond what the source supports (also a faithfulness failure, but in the opposite direction from "purification"). Either outcome is honest data; neither triggers a "fix the corpus" response.

---

## Implications for Phase 3 tuning

Phase 3's noise-floor guard threshold must be set such that the guard **abstains on approximately the 16% tail** (situational + mixed). Cleaner inputs should route through the matcher; the tail should fall through to deterministic ordering.

Two estimation paths for the threshold:
1. **Fixture-calibrated.** Embed all 867 activation_conditions + the ~30 authored fixture queries. For each fixture whose target is a situational/mixed condition, record the cosine of the intended match. Set the threshold just above the highest of those "should not have matched" cosines.
2. **Distribution-calibrated.** Compute pairwise cosines among the 867 conditions themselves. The 16th percentile from the top ≈ the implicit floor below which matches are plausibly against situational content.

Recommend path (1) — tied to real query shapes, not self-similarity.

---

## Source-model histogram (not collected)

Handover Section 14 Phase 0.5 called for a per-source-model histogram to see whether the situational/mixed tail is concentrated on specific curators. The 100-sample covers 222 source models thinly (≤1 edge per model on average), so a meaningful per-model histogram is not resolvable at this sample size.

**Deferred to a follow-up audit** if the 16% tail turns out to block Phase 3 calibration. In that case, a full 867-pass rating (not a sample) plus per-model aggregation would identify whether a handful of models are responsible for the bulk of the tail — which would permit a targeted remediation pass rather than a whole-corpus review. For the current calibration purpose (set Phase 2 gate and inform Phase 3 threshold), the 16% aggregate is sufficient.

---

## Test: re-run stability

Handover Section 14 Phase 0.5 specifies:
> deterministic re-run on a 10% subset produces the same categorical ratings on ≥85% of items (LLM-rating noise floor).

Not executed in this pass. A second-pass re-rating of the 10-item subset (indices 1, 11, 21, ..., 91) should be run by a fresh Claude session or a different rater before this baseline is considered locked. If re-rating agreement drops below 85%, tighten the rubric (likely by collapsing mixed into situational, or writing concrete positive/negative examples for each category) before Phase 2 uses the 84% figure as a gate.

**Follow-up task:** re-rating pass, likely deferred into Phase 2 work (the tension re-read would need this anyway for self-verification).

---

## Bottom line

- **Layer 1+2 baseline: 84% cognitive-move, 8% situational, 8% mixed.** Calibration measurement of the corpus as-is, not a gate.
- **Phase 2 gate (Section 14 REV-5): faithfulness to source article**, not a rubric distribution. The curated corpus is the authority; rubrics evaluate, never override.
- **Phase 3 noise-floor threshold:** tune so the matcher abstains on approximately the 16% tail of Layer 1+2 (and whatever the Phase-2-post tension tail turns out to be). Calibrated via fixture queries, not self-similarity.
- Rubric and rating process are single-rater. Re-rating stability pass on the 10-item subset is a test of the rating process (LLM noise floor), not of the corpus, and can run before or after Phase 2 without affecting Phase 2's faithfulness gate.
