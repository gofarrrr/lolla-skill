# Lane 2 producer audit — synthesis (N=7 runs over 6 distinct conversations)

Date: 2026-04-27
Branch: `feat/lane2-producer-audit-impl-2026-04-26`
Audit design memo: `research/lane2-producer-audit-design-2026-04-26.md`
Per-case files: `research/stability-runs/lane2-producer-audit-2026-04-26/case_*_step{1,2}_*.md`

This memo consolidates the audit's findings into the artifact a reviewer or next-track designer needs. Per-case detail lives in the 7×2 step files; this is the single decision-input document.

## §1 Audit scope correction

The design memo §4 described the corpus as 7 distinct cases across three buckets. Reading the conversation files revealed:

> `mid-level-consultant-report` and `mid-level-consultant-decides` are **byte-identical conversations** archived as separate runs.

Actual corpus: **6 distinct conversations + 1 same-conversation rerun** (case 7 = same source as case 3).

This changes case 7's role from "false-positive risk control" to "same-source stability test." That is more informative than the original framing — case 3 vs case 7 is the audit's only run-to-run stability comparison on identical source — but it requires the corrected scope to be read honestly.

The design memo has been patched (§4 erratum) to reflect the corrected corpus.

## §2 Main finding

**Lane 2 is high-trust but uneven-friction.**

- **Trust axis:** 0 false positives across 26 surfaced anchor rows in 7 runs. Every observed anchor classifies as `acceptable_primary_match`, `acceptable_secondary`, or `acceptable_*_with_quote_drift`. No `noisy_adjacent` or `false_positive` rows.
- **Friction axis:** strict yield varies materially by case, including a same-source 80% → 40% drop between case 3 and case 7 on clean expected primaries.

The product implication: **a user re-running the same conversation can get materially different curated pressure** while the false-positive rate stays at zero. That is a stability problem on the friction axis alone.

## §3 F2 final status

The audit's working hypothesis after Marcus and PhD:

> **F2 — Lane 2 tends to accept models when the source quote locally and literally exposes the model's mechanism in recognizable terms (numbers, named processes, observable behaviors, explicit if/then, mutual-exclusion phrasing). But identical source can still produce different recall, verifier, and quote-validation outcomes across runs.**

F2 has predictive power for the *direction* of verifier acceptance per cluster shape. F2 does not predict run-to-run stochasticity. Cases 3 vs 7 (same source, different anchors at multiple stages) is the strongest evidence of this limit.

The single clean F2 counter-example remains Marcus C5 (Opportunity Cost rejected with explicit dollar math + mutual-exclusion phrasing). That is most plausibly an OC-specific or thin-slate-specific verifier behavior, not a falsification of F2 in general.

## §4 Five leak modes

Cumulative findings across N=7. Each shows up unevenly across cases; none is universal.

1. **Recall vocabulary gaps.** Some conversation domains produce thin candidate slates (Marcus 13/60 vs typical 56–60). Some chronic absences (PFR across cases 1, 3, 4 at recall; Optionality cases 2, 3 at recall) point at recall-substrate vocabulary that doesn't trigger on common interpretive-reframe / option-design language.
2. **Quote-validation strictness.** The literal-substring gate at `engine/system_b/companion_routing.py:521-549` correctly protects against hallucinated evidence but also drops models the verifier accepted with paraphrased quotes. Demotion rates: case 1 = 50%, Marcus = 67%, case 7 = 57%, others = 0%. Variable across runs of the same conversation (case 3 = ~17% vs case 7 = 57%).
3. **Verifier interpretive rejection.** When a candidate reaches the verifier without operational mechanism language in its source quote, the verifier rejects with `mechanism absent` or `too generic`. F2 describes this. Examples: Marcus C5 OC (explicit math, still rejected as F2 counter-example); cases 1, 3 PFR / Premortem on weakly-operationalized source.
4. **Run-to-run variance at all producer stages.** Cases 3 vs 7 on identical source: recall picks different candidates (PAP in cand on case 3, missing on case 7), verifier judges differently (IA accepted on case 3, rejected on case 7), quote validation demotes at different rates. The producer chain is stochastic at every stage.
5. **Stochastic anchor identity within genuinely ambiguous clusters.** When a cluster has multiple defensible 222 fits (Marcus C6 founder bias, case 7 C4 agency family), different runs surface different defensible options. This is *honest hypothesis diversity*, not a leak — but it explains low Accepted-pre stability without implying producer failure.

These five modes are addressable by *different* fixes. F2-shaped fixes (verifier prompt, quote literalness, fuzzy quote repair) only address modes 2 and 3.

## §5 What the audit does not prove

To keep the next-track decision honest:

- The audit **does not prove** Lane 2 "picks the right models" reliably. It proves the chain is observable, that friction yield varies by case and run, and that trust holds — not that the cumulative friction is product-sufficient.
- The audit **does not prove** false positives cannot happen. It proves 0 observed false positives across 29 anchor rows, which is strong evidence but not proof. The trust axis can still break in untested conversation domains.
- The audit **does not yet choose architecture.** §6 below feeds the design memo's §9 decision tree; the architectural next-track is a separate deliverable.
- The audit **does prove** the producer chain is more trustworthy than feared on false positives, but less stable than desired on friction yield.

## §6 Decision-tree input

Feeding the design memo §9 decision tree:

| Stage | Audit verdict | Branch implication |
|---|---|---|
| Trust axis | **pass** | No fix needed at trust gates. Do not loosen quote validation. |
| Friction yield | **mixed / uneven** (range 14% to 80% strict on clean primaries across cases) | Friction-yield branch fires. The §9 fix space is calibration around the trust gates, not loosening them. |
| Quote validation | **fail / needs work** (50–67% demotion rates on cases 1, 5, 7; 0% on others) | Verifier verbatim-quote prompt OR fuzzy quote repair before demotion. |
| Recall | **domain/model-family gaps** (Marcus thin slate, PFR/Optionality/Premortem chronic absences) | Recall substrate work — possibly shape-scoped recall, possibly vocabulary expansion. |
| Stability | **fail / needs explicit treatment** (cases 3 vs 7 on identical source produce 80% vs 40% friction yield) | Honest run-stochasticity treatment — possibly N-run consensus, possibly hypothesis-diversity surfacing alongside primary anchors. |

The architectural next-track gets its own deliverable. This synthesis is the input, not the design.

## §7 What this audit costs to redo on a future Lane 2 change

For future investigations: the audit infrastructure (gold cluster labeling protocol, F2 prediction tables, observed-anchor schema with quote drift, strict/broad metric variants) is a research methodology that survives. Re-running it on a new Lane 2 architecture would cost:

- 6–8 archived `/lolla` runs from a representative slate (the existing slate is reusable)
- Source-first cluster labeling per case (Claude can draft, human owns gold)
- F2 prediction table per case (locked before Lane 2 outputs are opened)
- Step 2 attribution per case (Claude reads Lane 2 artifacts, scores against gold)
- Synthesis memo at the end

Approx 2–3 sessions of human review time per audit run, mostly on gold-label sign-off and cross-case synthesis.

## Audit closure

The corpus is complete. The leak map is consolidated in §4 + §6. Trust axis is the most robust finding. F2 is the best-supported hypothesis with named limits. The next-track decision is now a separate exercise.
