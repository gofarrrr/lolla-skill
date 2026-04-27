# Step 2 attribution — `user-launch-independent-fintech`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: gold cluster table from `case_user-launch-independent-fintech_step1_source_first.md` v2 (locked by Marcin).

Artifacts opened in this step:
- `result.json.audit_summary.companion_fingerprint_validated` (8 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (2 accepted)
- `result.json.audit_summary.companion_rejected_models` (58 rejected with reason)
- `result.json.companion_cheat_sheet.anchors` (2 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 60 (58 rejected + 2 accepted). Cap was filled.

## Gold cluster rows

### C1 — Refuse tactics-first framing

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `acceptable_secondary_models` | *Theory Of Constraints* |
| `fingerprint_found_cluster` | yes (Move 1 + Move 4) |
| `fingerprint_move_text` | M1: "Identify critical uncertainties before providing tactical advice…"; M4: "Prioritize fundamentals over tactics, insisting on acknowledgment of risks before proceeding to details." |
| `candidate_recall_hit` (Problem Framing) | **no** — `problem-framing-and-reframing` not in candidate list |
| `verifier_accepted` (Problem Framing) | n/a |
| `surfaced_top5` | n/a |
| `step6_treatment` | hidden |
| `failure_owner` | **recall_failed** |
| `notes` | Fingerprint extraction was clean and specific. Recall did not surface *Problem Framing And Reframing* despite Move 1 and Move 4 both naming "tactics" / "fundamentals" / "right problem" — keyword overlap should have hit. This is a real producer leak. |

### C2 — Network interest is not pipeline (base-rate correction)

| Field | Value |
|---|---|
| `expected_primary_models` | *Base Rates* |
| `acceptable_secondary_models` | *Optimism Bias And Planning Fallacy* |
| `fingerprint_found_cluster` | yes (Move 2) |
| `fingerprint_move_text` | "Debunk optimistic assumptions about network conversations by citing typical low conversion rates and reclassifying them as potential rather than actual pipeline." |
| `candidate_recall_hit` (Base Rates) | **yes** |
| `verifier_accepted` (Base Rates) | **no** — rejection_reason: `execution_quote_not_literal_substring` |
| `failure_owner` (Base Rates) | **post_verifier_validation_failed** (NEW stage — see §"Surprises") |
| `candidate_recall_hit` (Optimism Bias) | yes |
| `verifier_accepted` (Optimism Bias) | yes |
| `surfaced_top5` (Optimism Bias) | yes |
| `step6_treatment` (Optimism Bias) | primary (revised.txt: "This is planning fallacy territory — I built the three-phase…timeline at the optimistic end of the same base rates I'd just cited.") |
| `failure_owner` (Optimism Bias) | **none** (secondary hit, but see partial-credit ruling below) |
| `partial_credit_ruling` | per Marcin v2 verdict: secondary hit + primary miss. Optimism Bias is NOT a clean true positive on C2 because the *evidence quote Lane 2 attached to it* is from C3's source text ("8 months at zero revenue is tight…"), not from C2's "1-in-5 conversion" content. The semantic concept is plausible across both clusters, but the quote attribution lands on C3. See observed-anchor row for full handling. |

### C3 — Runway as safety buffer + signed-LOI exit trigger

| Field | Value |
|---|---|
| `expected_primary_models` | *Margin Of Safety* |
| `acceptable_secondary_models` | *Optionality* |
| `should_reject_models` | *Loss Aversion* |
| `fingerprint_found_cluster` | partial (Move 3 captures runway, LOI exit-trigger not in any move's evidence_quotes) |
| `fingerprint_move_text` | M3: "Assess runway adequacy against realistic timelines for first engagements and setup, highlighting pressure points." |
| `candidate_recall_hit` (Margin Of Safety) | yes |
| `verifier_accepted` (Margin Of Safety) | yes |
| `surfaced_top5` (Margin Of Safety) | yes |
| `step6_treatment` (Margin Of Safety) | primary (revised.txt: "The Margin Of Safety frame was already running in the original advice…") |
| `failure_owner` (Margin Of Safety) | **none** — primary HIT |
| `evidence_attribution_note` | Lane 2's evidence_quote for Margin Of Safety is from C4 ("Option 3: Launch on current timeline but with a specific safety net — a part-time arrangement…"), not C3's runway/LOI text. The anchor is a primary hit; the evidence selection picked the C4 instance over the C3 instance. Sub-optimal but not a leak. |
| `candidate_recall_hit` (Optionality, secondary) | yes |
| `verifier_accepted` (Optionality, secondary) | **no** — rejection_reason: `mechanism absent` |
| `failure_owner` (Optionality, secondary) | verifier_failed (also see C4) |

### C4 — Three launch paths with explicit tradeoffs

| Field | Value |
|---|---|
| `expected_primary_models` | *Optionality* |
| `acceptable_secondary_models` | *Second Order Thinking* |
| `should_reject_models` | *Decomposition* |
| `fingerprint_found_cluster` | yes (Move 5) |
| `fingerprint_move_text` | "Generate structured decision options with tradeoffs, incorporating delay, aggressive launch, and de-risked hybrid paths." |
| `candidate_recall_hit` (Optionality) | yes |
| `verifier_accepted` (Optionality) | **no** — rejection_reason: `mechanism absent` |
| `surfaced_top5` (Optionality) | n/a |
| `step6_treatment` (Optionality) | hidden |
| `failure_owner` (Optionality) | **verifier_failed** |
| `notes` | The cluster is "generate three explicit options with named tradeoffs" — a textbook Optionality move. Fingerprint named it. Recall surfaced it. Verifier rejected with "mechanism absent" — that rejection looks wrong on inspection. This is the v1/v2/v3/B verifier-instability story playing out as systematic over-rejection on a single run. |
| `should_reject_check` (Decomposition) | not in candidate list — no false-positive triggered |

### C5 — Spouse alignment on specifics, not concept

| Field | Value |
|---|---|
| `expected_primary_models` | `no_clean_primary` |
| `acceptable_secondary_models` | *Information Asymmetry* |
| `should_reject_models` | *Principal Agent Problem* |
| `fingerprint_found_cluster` | yes (Move 6) |
| `fingerprint_move_text` | "Insist on explicit spousal alignment on specific financial risks rather than conceptual support." |
| `candidate_recall_hit` (Information Asymmetry, secondary) | yes |
| `verifier_accepted` (Information Asymmetry, secondary) | **no** — rejection_reason: `mechanism absent` |
| `failure_owner` | **none** — `no_clean_primary` means there's no expected primary to lose. The verifier correctly did not surface either Information Asymmetry or Principal Agent Problem as anchors for this cluster. |
| `should_reject_check` (Principal Agent Problem) | in candidate list, rejected with "mechanism absent" — verifier correctly rejected the should_reject candidate ✓ |
| `notes` | This cluster validates the `no_clean_primary` rule. Lane 2 also did not force-fit a model here, which is the correct behavior. |

### C6 — Fractional work tradeoff

| Field | Value |
|---|---|
| `expected_primary_models` | *Opportunity Cost* |
| `acceptable_secondary_models` | *Margin Of Safety* |
| `fingerprint_found_cluster` | partial — Move 7 captures the implementation detail ("specific ask"), not the tradeoff structure |
| `fingerprint_move_text` | "Provide concrete implementation details for de-risking options like fractional roles to make them actionable." |
| `candidate_recall_hit` (Opportunity Cost) | yes |
| `verifier_accepted` (Opportunity Cost) | **no** — rejection_reason: `mechanism absent` |
| `surfaced_top5` (Opportunity Cost) | n/a |
| `step6_treatment` (Opportunity Cost) | hidden |
| `failure_owner` (Opportunity Cost) | **verifier_failed** (or possibly `fingerprint_failed`/partial — see notes) |
| `notes` | Fingerprint Move 7 captures the fractional context but the *tradeoff reasoning* (locks you into cadence / makes larger engagements harder / pays less per hour) is not in any move's evidence quote. Verifier still saw Opportunity Cost as a candidate (via keyword match elsewhere) and rejected with "mechanism absent" — same pattern as C4 Optionality. The deeper question: would a fingerprint move that named the *tradeoff* explicitly have caused the verifier to accept Opportunity Cost? Cannot answer from this case alone. |

### C7 — Pre-registered checkpoint and signal discipline

| Field | Value |
|---|---|
| `expected_primary_models` | *Premortem* |
| `acceptable_secondary_models` | *Confidence Calibration* |
| `fingerprint_found_cluster` | yes (Move 8) |
| `fingerprint_move_text` | "Set conditional checkpoints for launch decision based on evidence from key actions, distinguishing signal from noise." |
| `candidate_recall_hit` (Premortem) | yes |
| `verifier_accepted` (Premortem) | **no** — rejection_reason: `mechanism absent` |
| `surfaced_top5` | n/a |
| `step6_treatment` | hidden |
| `failure_owner` (Premortem) | **verifier_failed** |
| `notes` | Same pattern as C4, C6: fingerprint move was clear and specific ("conditional checkpoints… distinguishing signal from noise"), keyword recall surfaced *Premortem* into candidates, verifier rejected with "mechanism absent". |

## Observed-anchor rows

### Observed: *Margin Of Safety*

| Field | Value |
|---|---|
| `best_matching_cluster` | C3 (primary) — the runway/LOI safety reasoning is the strongest primary fit |
| `secondary_match` | C4 (secondary) — Option 3's "specific safety net" also fits |
| `evidence_quote_attribution` | Lane 2 attached the C4 quote ("Option 3: Launch on current timeline but with a specific safety net — a part-time arrangement…") |
| `classification` | **`acceptable_primary_match_with_quote_drift`** — anchor is the right primary for C3, but evidence quote sources from C4. The anchor is correct; the evidence-quote selection is sub-optimal but traceable. |
| `failure_owner` | none |

### Observed: *Optimism Bias And Planning Fallacy*

| Field | Value |
|---|---|
| `best_matching_cluster` | C2 (where I labeled it acceptable_secondary) OR a meta-pattern crossing C2 + C3 (the user's general optimism) |
| `evidence_quote_attribution` | Lane 2 attached a C3 quote ("8 months at zero revenue is tight for a first-time independent consultant. Industry experience suggests the first paid engagement often takes 3-5 months from launch…") |
| `classification` | **`acceptable_secondary_with_quote_drift`** — the anchor concept is plausible (the user's runway optimism is the model's mechanism), and Step 6 uses it well as a primary critique. But Lane 2's evidence quote is sourced from C3, not C2. Per Marcin's partial-credit discipline: this is **secondary hit + primary miss on C2** (where Base Rates was rejected) — not a clean true positive. |
| `failure_owner` | none on Optimism Bias itself, but the C2 `Base Rates` post-validation rejection means C2's primary expectation was missed. |

## Aggregate metrics (this case only — N=1, single run)

Cluster denominator excludes C5 (`no_clean_primary`) for primary-recall metrics, since it has no expected primary to recover.

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 7/7 = 100% (or 6/7 = 85.7% if C3's missing LOI half counts as partial) | Fingerprint extraction is strong on this case. Every cluster has at least one move targeting it. |
| `fingerprint_specificity` | 6/8 moves specific enough; 2 moves (M7 implementation, partial M3) are slightly too generic | Mostly fine. M7 captures fractional context but not tradeoff structure; M3 captures runway but not LOI exit-trigger. |
| `candidate_recall@60` (expected primaries that reached candidates) | 5/6 = 83.3% (Problem Framing And Reframing missing; Base Rates, Optionality, Margin Of Safety, Opportunity Cost, Premortem present) | Strong but C1 leak. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries that were candidates) | 2/5 = 40% (*Margin Of Safety* and *Base Rates*; Optionality / Opportunity Cost / Premortem rejected with "mechanism absent") | This is **raw verifier judgment**, before post-verifier validation. *Base Rates* was accepted by the verifier and demoted afterwards. |
| `post_verifier_validation_failure_rate` | 1/2 = 50% (1 of 2 raw verifier acceptances demoted by the literal-substring gate; *Base Rates*) | One demotion on one case. Existence established (code at `companion_routing.py:521-549`); significance pending recurrence on other cases. |
| Final validated acceptance on expected primaries | 1/5 = 20% (Margin Of Safety only; Base Rates demoted, three rejected at verifier) | The user-visible result: 1 of 5 candidate-stage primaries reached the cheat sheet. |
| `surfacing_recall@5` | 1/1 = 100% (every validated-accepted model survived top-5; cap not binding here with 2 accepted) | n/a (denominator too small) |
| `noisy_anchor_rate` | 0/2 = 0% — both surfaced anchors are correct primaries somewhere in the cluster table; no false-positive observed-anchor rows | Clean precision. |
| `step6_treatment_accuracy` | 2/2 — both surfaced anchors get primary treatment in revised.txt, which matches the cluster mapping for Margin Of Safety on C3 | Step 6 consumed correctly. |

### Product-level friction metrics (per memo §8.3)

Anchor-worthy denominator: 6 clusters (C1, C2, C3, C4, C6, C7). C5 is `no_clean_primary` and excluded.

Strict and broad variants are reported per memo §8.3, so the metric is harder to game and evidence-quote drift / fingerprint-specificity caveats stay visible.

| Metric | Value | What's counted (and what's caveated) |
|---|---|---|
| `friction_yield_strict` | **1/6 = 16.7%** | Only C3: Margin Of Safety is the cluster's expected primary AND survived validation AND Step 6 used it as primary pressure. C2 is excluded from the strict numerator: although Optimism Bias And Planning Fallacy survived as a validated anchor, its evidence quote sources from C3 (`acceptable_secondary_with_quote_drift`), so the cluster-aligned reading does not credit it. |
| `friction_yield_any_honest` | **2/6 = 33.3%** | C3 (clean primary) + C2 (validated secondary with quote drift, but Step 6 used it as primary critique pressure — honest curated friction reached the user). |
| `strictness_failure_rate_strict` | **2/4 = 50%** | C4 (*Optionality*) and C7 (*Premortem*) — fingerprint specificity was sufficient, expected model reached candidates, verifier rejected with "mechanism absent." C6 (*Opportunity Cost*) is excluded because fingerprint specificity was partial (Move 7 captured implementation detail, not the tradeoff structure). C2 is excluded because Optimism Bias secondary survived, so the cluster did not fully strictness-fail. C1 is excluded because the failure was at recall, not strictness. |
| `strictness_failure_rate_broad` | **3/5 = 60%** | Above plus C6, on the broader reading that the verifier was strict even given partial fingerprint context. The strict/broad gap (10 pts) is a measure of how much the strictness signal depends on what we treat as "fingerprint did its job." |
| Trust axis (this case) | clean | `noisy_anchor_rate` 0%, both surfaced anchors map to expected models on some cluster, Step 6 used them honestly. Quote drift on both anchors is a sub-signal but not a trust violation. |
| Friction axis (this case) | weak under either reading | Strict: 16.7% friction yield, 50% strictness failure. Generous: 33.3% friction yield, 60% strictness failure. Under either reading, anchor-worthy clusters delivered nothing on at least half of the cases where the producer chain successfully extracted them. |

## Findings — case 1 only

### Discipline first

These are findings *for this single case, single run*. Do not generalize until at least the failure-rich and FP-risk cases have been audited. The "verifier over-rejects" pattern below could be case-specific (the verifier prompt may struggle with this particular conversation's reasoning style) or systemic.

### F1 — Verifier "mechanism absent" rejection accounts for most low-recall on this case

Three expected primaries on this case were rejected by the verifier with `mechanism absent`:

- *Optionality* on C4 — clearly executed in the three-options structure with named tradeoffs. Looks like a clean verifier miss.
- *Premortem* on C7 — pre-registered conditions for reversal with explicit signal/noise discipline. Looks like a clean verifier miss.
- *Opportunity Cost* on C6 — explicitly framed tradeoff ("locks you into cadence / makes larger engagements harder / pays less per hour"). **Mixed signal**: the fingerprint captured the fractional-work *implementation detail* (Move 7) but not the tradeoff *structure*. The verifier may be too strict when the fingerprint gives it surrounding context but not the exact mechanism language. C6 stays `verifier_failed` with a `fingerprint_specificity_partial` caveat.

The directional read is that verifier judgment is doing strict over-rejection on this case. The certainty is one notch lower than "the verifier is the bottleneck": Optionality and Premortem look unambiguously like verifier misses, but Opportunity Cost has a fingerprint-specificity shadow. Hold this distinction across cases 2–7 before drawing a verifier-side architectural conclusion.

### F2 — A 6th failure stage emerged: post_verifier_validation

The design memo's chain originally had 5 stages (fingerprint / recall / verifier / surfacing / Step 6). This case surfaced a 6th: a quote-validation gate downstream of verifier judgment that drops models when the verifier's evidence quote is not a literal substring of the source (`engine/system_b/companion_routing.py:521-549`). *Base Rates* was rejected on C2 with `execution_quote_not_literal_substring` — meaning the verifier judged it executed but the validation gate dropped it.

This is a real but separate failure mode. It's not "verifier disagreed"; it's "verifier agreed but the quote it produced wasn't an exact substring." That's a code-level guard against verifier hallucination, and it's catching legitimate cases when the verifier paraphrases the evidence slightly.

The 6th stage is now part of the design memo (§6.5 failure owners, §7.1 schema, §8.1 metrics including `post_verifier_validation_failure_rate`, §9 decision tree).

### F3 — Recall correctly screens broad models (C5 should_reject check passed)

*Principal Agent Problem* was a `should_reject_models` candidate on C5 (spouse alignment). It appeared in the candidate list and was rejected with "mechanism absent". That's the correct behavior — the verifier correctly screened a broad model that recall surfaced via lexical adjacency.

This validates that the verifier IS doing real work on screening adjacency; the F1 problem is over-rejection of in-domain models, not a precision problem.

### F4 — Lane 2 evidence-quote selection is sometimes cross-cluster

*Margin Of Safety* on C3 (primary) and *Optimism Bias* on C2 (secondary) both have evidence quotes that source from a different cluster than where the anchor is structurally most load-bearing. The anchors are correct; the evidence-quote selection picks a different sentence. Not a leak, but worth flagging as a sub-finding for the leak map: anchor-to-quote attribution is not always to the most load-bearing source.

### F5 — Hidden anchor rate is high relative to expected primary count

5 expected primaries (out of 6) hidden vs 1 surfaced. **Lane 2 on this case is high-precision, very-low-recall.**

### Locked bottom-line for this case

`user-launch-independent-fintech` shows **high precision and low validated recall.** Fingerprint and recall mostly worked. **One primary failed recall** (*Problem Framing And Reframing* on C1), **one primary failed post-verifier quote validation** (*Base Rates* on C2 — `execution_quote_not_literal_substring`), and **three expected primaries failed verifier judgment** (*Optionality* on C4, *Opportunity Cost* on C6, *Premortem* on C7), with C6's miss carrying a fingerprint-specificity caveat.

**Two-axis read.** Trust is high (no false positives, evidence quotes real, Step 6 framing honest). Friction yield is weak under either scoring: even under generous credit, only 2/6 anchor-worthy clusters delivered usable pressure; under strict cluster-aligned scoring, only 1/6 did. Per the memo's interpretive rule, high precision with low friction yield is not acceptable just because `noisy_anchor_rate` is low — the product job is to import curated pressure into Step 6, and on this case Optionality / Opportunity Cost / Premortem (and Base Rates and Problem Framing And Reframing) all failed to surface despite being clearly executed in the assistant's reasoning.

That is the case-1 conclusion. It is *not* "the verifier is the bottleneck" — that generalization is held until the calibration case and the failure-rich cases are audited. It is also not "post-verifier validation is significant" — one demotion on one case does not establish significance, only existence. The friction-yield signal is similarly first-only: case 1 alone says "this calibration may be too strict for the product on this kind of conversation"; recurrence across cases decides whether the calibration is systematically too strict, or whether case 1 is a fintech-launch-specific outlier or a labeling-granularity artifact.

## Surprises

1. **Post-verifier validation gate.** I did not know (or had forgotten) that there's a literal-substring check downstream of the verifier judgment. This was a 6th failure stage and is now reflected in the memo (resolved in commit `a4c865d`).
2. **Validated rejection volume is high; raw verifier rejection is slightly lower.** The persisted artifact shows 58/60 candidates in the rejected list. That count includes the post-verifier validation demotions, not pure verifier judgment. The clean breakdown is:
   - Final accepted (post-validation): **2/60**
   - Final rejected (validated): **58/60**
   - Known post-verifier validation demotions: **1** (Base Rates on C2)
   - Raw verifier rejection is therefore **at most 57/60**, possibly lower if other accepted entries were demoted and collapsed in the persisted artifact.

   The distinction matters: blaming "the verifier" for what is partly a code guard would route us to the wrong fix. The quote-validation gate is correctly protecting against hallucinated evidence; the candidate fix when this stage dominates is "make the verifier produce verbatim quotes" or "add fuzzy quote repair before demotion," not "trust paraphrased quotes."
3. **Fingerprint quality is good.** I expected fingerprint to be a major leak source on at least some clusters; on this case, it is not. Every cluster has at least one move targeting it. M7 and M3 are slightly under-specific, but not failure-mode under-specific.

## Resolved notes

Items raised by this case that have since landed in the memo:

- `post_verifier_validation_failed` added as a failure owner with code reference (commit `a4c865d`).
- Two-axis frame (trust + friction yield) added to memo §1, §8.3, §9, §11 (commit `5fa7b5d`).
- Strict / broad metric variants added to make scoring harder to game (commit `623fc0e`).
- Observed-anchor schema enriched to capture evidence-quote drift as a first-class trust signal (commit `623fc0e`).
- Cross-cluster evidence-quote attribution: handled via `acceptable_*_with_quote_drift` classifications and the strict/broad friction-yield split, which together surface the drift without forcing a separate metric.

## Remaining open question

**Cross-case recurrence is the only thing left.** Whether F1 (verifier over-strictness) and the low friction-yield signal repeat on `year-old-oncologist-accept` (calibration case, source-first by Marcin) and on the failure-rich cases. If they do, the audit's decision-tree call is the friction-yield branch from §9 — calibration design questions (verifier-quote literalness, fuzzy quote repair, hypothesis-grade soft-friction surfacing), not a verifier resplit. If they don't, case 1 may be a fintech-launch-specific outlier.
