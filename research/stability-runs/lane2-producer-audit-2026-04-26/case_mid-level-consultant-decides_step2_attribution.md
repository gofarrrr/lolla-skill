# Step 2 attribution — `mid-level-consultant-decides`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: gold cluster table from `case_mid-level-consultant-decides_step1_source_first.md` v1 (locked, with heavy author-bias disclosure).

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (7 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (5 final accepted)
- `result.json.audit_summary.companion_rejected_models` (55 rejected; 38 "mechanism absent", 9 "topic-adjacent", 7 "too generic", 1 "execution_quote_not_literal_substring")
- `result.json.companion_cheat_sheet.anchors` (5 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 60 (55 rejected + 5 accepted). Cap was filled.

## Family-prediction test (run BEFORE writing attribution)

Pre-registered predictions from step 1 vs actual outcome:

| Cluster | Family | Predicted | Actual | Hypothesis test |
|---|---|---|---|---|
| C1 — Probabilistic obstruction read | calibration / abstract-cognitive | **REJECT** | **ACCEPTED** with cluster-aligned quote | **BREAKS hypothesis** |
| C2 — Three-dimensional decomposition | interpretive / reframing | REJECT | NOT IN CANDIDATES (recall failed) | matches "missing" but at recall, not verifier |
| C3 — Information Asymmetry preservation | external-information / diligence | ACCEPT | ACCEPTED with cluster-aligned quote | **MATCHES** |
| C4 — Principal-Agent on GC | agency / incentive-structure (stress test) | OPEN | ACCEPTED with cluster-aligned quote | **establishes agency family as PASSING** |
| C5 — Pre-registered 90/70 threshold | calibration / abstract-cognitive | **REJECT** | **ACCEPTED** with cluster-aligned quote | **BREAKS hypothesis** |
| C6 — Career reframe | interpretive / reframing | REJECT | NOT IN CANDIDATES (recall failed) | matches "missing" but at recall |
| C7 — Premortem on future self-doubt | counterfactual / failure-planning | REJECT | REJECTED at verifier (mechanism absent) | **MATCHES** |

Per Marcin's pre-registered stop condition:

> *"if Confidence Calibration / Probabilistic Thinking pass cleanly with aligned quotes... the family hypothesis weakens."*

That is exactly what happened. **The "external-legible passes / interpretive misses" frame as previously stated does not survive case 3.** Both Probabilistic Thinking and Confidence Calibration are abstract cognitive operations; both passed the verifier with cluster-aligned quotes. The hypothesis as stated needs replacement.

A sharper hypothesis fits the data so far (§"Findings" §F1''').

## Gold cluster rows

### C1 — Probabilistic obstruction read

| Field | Value |
|---|---|
| `expected_primary_models` | *Probabilistic Thinking* |
| `acceptable_secondary_models` | *Confidence Calibration* |
| `fingerprint_found_cluster` | yes (Move 2 — "Weigh probability of obstruction against benign alternatives based on contextual factors") |
| `candidate_recall_hit` (Probabilistic Thinking) | yes |
| `verifier_accepted` (Probabilistic Thinking) | **yes** |
| `surfaced_top5` | yes |
| `evidence_quote_attribution` | Lane 2's PT quote: "A reasonable person would conclude this is likely obstruction-related conduct. I want to be careful not to conclude it definitively — there's a non-zero chance there's a legitimate explanation…" — **exactly the C1 source quote.** |
| `step6_treatment` | **hidden** — revised.txt §1 contains probabilistic reasoning ("that's strong evidence") but does NOT explicitly name *Probabilistic Thinking*. Curated label is hidden in Step 6, though the underlying reasoning is preserved. |
| `failure_owner` | **step6_failed** for the named-anchor surface; the Step 6 layer didn't name the curated model the way it named PAP / IA / CC / AB. |
| `notes` | The case-1+2 hypothesis predicted PT would be rejected as a calibration/abstract-cognitive model. It wasn't. The verifier accepted it cleanly with the source quote that explicitly operationalizes probability ("less than 1 in 5", "non-zero chance"). |

### C2 — Three-dimensional decomposition

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `acceptable_secondary_models` | *Decomposition* |
| `fingerprint_found_cluster` | yes (Move 3 — "Structure decision into triadic framework of legal, career, and moral dimensions") |
| `candidate_recall_hit` (Problem Framing And Reframing) | **no** |
| `candidate_recall_hit` (Decomposition, secondary) | **no** |
| `failure_owner` | **recall_failed** — neither the primary nor the secondary reached candidates, despite a clean fingerprint move |
| `notes` | Same shape as case 1 C1 (PFR recall failure). Fingerprint extraction is sharp; recall doesn't surface PFR via keyword/embedding overlap. PFR has now had 3 different failure modes across 3 cases: recall_failed (case 1 C1, case 3 C2 + C6), verifier_failed (case 2 C1). Common outcome: *Problem Framing And Reframing* is consistently absent from the user-visible product. |

### C3 — External-with-counsel preserves information asymmetry

| Field | Value |
|---|---|
| `expected_primary_models` | *Information Asymmetry* |
| `acceptable_secondary_models` | *Second Order Thinking*, *Premortem* |
| `should_reject_models` | *Power Dynamics* |
| `fingerprint_found_cluster` | partial — no fingerprint move directly extracts C3's source quote ("internal report likely to tip off the partner"), but the cluster is logically adjacent to M4/M5's internal-vs-external filtering content |
| `candidate_recall_hit` (Information Asymmetry) | yes |
| `verifier_accepted` (IA) | **yes** |
| `evidence_quote_attribution` | "An internal report in a situation like this is likely to tip off the partner you saw, giving him time to construct a cover story." — **exactly the C3 source quote.** |
| `step6_treatment` | primary in revised.txt §3: "Information asymmetry runs both ways: she may control proof you don't have, and a pattern of two events two years apart on the same account is a different filing than a single observation." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | The verifier reads beyond fingerprint moves — even when fingerprint doesn't directly extract a cluster's source quote, the verifier can find the model executed against the full assistant text. This is consistent with case 2 C4/C8 where the same pattern held. |
| `should_reject_check` (Power Dynamics) | NOT IN CANDIDATES — recall filtered it out before verifier, validating the should_reject expectation. |

### C4 — Principal-Agent Problem on GC

| Field | Value |
|---|---|
| `expected_primary_models` | *Principal Agent Problem* |
| `acceptable_secondary_models` | *Authority Bias*, *Information Asymmetry*, *Power Dynamics* |
| `fingerprint_found_cluster` | partial — M4/M5 cover the filtering and threshold reasoning around C4/C5, but no move directly extracts C4's PAP-specific quote |
| `candidate_recall_hit` (Principal Agent Problem) | yes |
| `verifier_accepted` (PAP) | **yes** |
| `evidence_quote_attribution` | "Internal reporting requires you to trust that the general counsel will take action against a senior partner who likely has significant revenue and political weight." — **exactly C4's source quote.** |
| `step6_treatment` | primary in revised.txt §1: "The principal-agent problem with the general counsel is real: you're asking a salaried fiduciary to act against a senior partner whose book of business pays the firm." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `candidate_recall_hit` (Authority Bias, secondary) | yes |
| `verifier_accepted` (AB, secondary) | **yes** with `presence_mode = violated` (the assistant pushed *against* authority deference, not exhibited it) |
| `evidence_quote_attribution` (AB) | "your most protected path is probably a whistleblower attorney who files on your behalf with the regulator" — Turn 4. C4's source spans Turn 4 (setup) through Turn 5/6 (PAP elaboration). The AB-violated quote sits at the C4 setup boundary, close enough to count as cluster-aligned. |
| `classification` (AB) | `acceptable_secondary` — anchor IS the cluster's secondary, evidence quote close to source, presence_mode "violated" matches the cluster's pushback structure. |
| `agency_family_signal` | **established as PASSING.** This is the first agency/incentive-structure model in the audit corpus, and the verifier accepted it with a cluster-aligned quote and an explicit operational mechanism in the source ("financial and political incentives", "salaried fiduciary", "book of business pays the firm"). |

### C5 — Pre-registered 90/70 threshold

| Field | Value |
|---|---|
| `expected_primary_models` | *Confidence Calibration* |
| `acceptable_secondary_models` | *Probabilistic Thinking* |
| `fingerprint_found_cluster` | yes (Move 5 — "Threshold confidence calibration to select reporting path") |
| `candidate_recall_hit` (Confidence Calibration) | yes |
| `verifier_accepted` (CC) | **yes** |
| `evidence_quote_attribution` | "Test it this way: if the general counsel got a report about a senior partner, how confident are you that action would actually follow? If you're 90%+ confident, internal first is reasonable. If you're 70% or below, external-with-counsel is safer." — **exactly C5's source quote.** |
| `step6_treatment` | primary in revised.txt §3: "the confidence-calibration failure mode: an irreversible maximum-commitment action staged on moderate confidence, with no defined reversal point." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | Second of the two predicted-REJECTED calibration models that actually passed. The source quote operationalizes confidence with explicit thresholds (90%, 70%), and the verifier accepted. The case-1+2 hypothesis ("calibration/abstract-cognitive will be rejected") fails decisively here. |

### C6 — Career reframe

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `acceptable_secondary_models` | *Optionality* |
| `should_reject_models` | *Status Quo Bias*, *Sunk Cost Fallacy* |
| `fingerprint_found_cluster` | no (no fingerprint move directly extracts Turn 12's "career-as-different-thing" reframe) |
| `candidate_recall_hit` (Problem Framing And Reframing) | **no** |
| `candidate_recall_hit` (Optionality, secondary) | yes — but rejected at verifier ("mechanism absent") |
| `failure_owner` | **recall_failed** for primary; **verifier_failed** for secondary |
| `notes` | Same PFR-recall pattern as C2 / case 1 C1. Optionality recall succeeded but verifier rejected — same as case 1's Optionality treatment. |
| `should_reject_check` (Status Quo Bias, Sunk Cost Fallacy) | both NOT IN CANDIDATES — recall correctly filtered the should_reject candidates ✓ |

### C7 — Premortem on future self-doubt

| Field | Value |
|---|---|
| `expected_primary_models` | *Premortem* |
| `acceptable_secondary_models` | *Confidence Calibration* |
| `fingerprint_found_cluster` | no (Turn 14's "second-guessing → write down what you saw" reasoning is not in any move's evidence quotes; M7 covers Turn 8 timeline, not Turn 14) |
| `candidate_recall_hit` (Premortem) | yes (recall succeeded via keyword overlap with "doubt" / "second-guess" / "write down") |
| `verifier_accepted` (Premortem) | **no** — `mechanism absent` |
| `failure_owner` | **verifier_failed** with `fingerprint_specificity_partial` caveat (fingerprint missed Turn 14 entirely) |
| `notes` | Third case in a row where Premortem fails. Cases 1 + 3 reject at verifier; case 2 had Premortem only as acceptable_secondary on C8 (where it was correctly absent). The Premortem rejection pattern is the most consistent miss across the audit so far. |

### C8 — Other-person responsibility refusal (`no_clean_primary`)

| Field | Value |
|---|---|
| `expected_primary_models` | `no_clean_primary` |
| `fingerprint_found_cluster` | yes (Move 6 — "Isolate current obligation from others' past decisions to avoid decision displacement") |
| `failure_owner` | **none** — `no_clean_primary` means there's no expected primary to lose. Lane 2 did not surface a model for this cluster (correct behavior). |

## Observed-anchor rows

### Observed: *Probabilistic Thinking*

| Field | Value |
|---|---|
| `best_matching_cluster` | C1 (cluster's expected primary) |
| `evidence_quote_attribution` | C1-aligned. |
| `classification` | `acceptable_primary_match` — anchor IS C1's expected primary, quote aligned. |
| `step6_visibility` | **hidden** — Step 6 doesn't name the curated label, though the reasoning is preserved. |
| `failure_owner` | none for the producer chain; **step6_failed** for the user-visible curated-name surface. |

### Observed: *Confidence Calibration*

| Field | Value |
|---|---|
| `best_matching_cluster` | C5 (cluster's expected primary) |
| `evidence_quote_attribution` | C5-aligned. |
| `classification` | `acceptable_primary_match`. |
| `step6_visibility` | named in revised.txt §3 ("the confidence-calibration failure mode"). |
| `failure_owner` | none. |

### Observed: *Principal Agent Problem*

| Field | Value |
|---|---|
| `best_matching_cluster` | C4 (cluster's expected primary) |
| `evidence_quote_attribution` | C4-aligned. |
| `classification` | `acceptable_primary_match`. |
| `step6_visibility` | named in revised.txt §1 ("The principal-agent problem with the general counsel is real"). |
| `failure_owner` | none. |

### Observed: *Information Asymmetry*

| Field | Value |
|---|---|
| `best_matching_cluster` | C3 (cluster's expected primary) |
| `evidence_quote_attribution` | C3-aligned. |
| `classification` | `acceptable_primary_match`. |
| `step6_visibility` | named in revised.txt §3 ("Information asymmetry runs both ways"). |
| `failure_owner` | none. |

### Observed: *Authority Bias*

| Field | Value |
|---|---|
| `best_matching_cluster` | C4 (cluster's `acceptable_secondary_model`) |
| `evidence_quote_attribution` | Turn 4 quote, slightly ahead of C4's main source span (Turn 5/6) but logically continuous. Could be classified as `acceptable_secondary_with_quote_drift` on a strict reading; I'm marking `acceptable_secondary` because the AB-violated mode aligns with the C4 cluster's pushback structure. |
| `classification` | `acceptable_secondary`. |
| `step6_visibility` | named in revised.txt §1 ("the authority-bias guardrail, substituting independent expertise for deference to firm authority"). |
| `failure_owner` | none. |

## Aggregate metrics

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 4/7 = 57.1% (C1, C2, C5, C8 cleanly hit; C3, C4, C6, C7 missed by fingerprint but C3 + C4 still yielded anchors via recall + verifier) | Lower than cases 1+2 (~85%+). The verifier compensated for fingerprint misses on C3 and C4. |
| `fingerprint_specificity` | 4/7 sufficient | The cases the fingerprint did extract (C1 / C2 / C5 / C8) were specific. |
| `candidate_recall@60` (expected primaries that reached candidates) | 5/7 = 71.4% (PT, IA, PAP, CC, Premortem present; PFR ×2 missing) | PFR is the recurring recall-side hole. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries that were candidates) | 4/5 = 80% (PT, IA, PAP, CC accepted; only Premortem rejected) | **Dramatically higher than cases 1 (40%) and 2 (33%).** The verifier on this conversation accepted nearly everything the producer chain handed it. |
| `post_verifier_validation_failure_rate` | 0/4 = 0% | Quote validation gate did not fire on this case. |
| Final validated acceptance on expected primaries | 4/5 = 80% | Same as verifier rate (no validation demotions). |
| `surfacing_recall@5` | 5/5 = 100% | All accepted models surfaced in top-5. |
| `noisy_anchor_rate` | 0/5 = 0% — all 5 surfaced anchors classify as `acceptable_primary_match` or `acceptable_secondary` with cluster-aligned (or near-aligned) quotes | Clean precision. |
| `step6_treatment_accuracy` | 4/5 — PAP / IA / CC / AB named and used as primary; PT hidden in revised.txt | One Step 6 consumption miss for *Probabilistic Thinking*. |

### Product-level friction metrics

Anchor-worthy denominator: 7 (C1–C7, excluding C8 `no_clean_primary`).

| Metric | Value | What's counted |
|---|---|---|
| `friction_yield_strict` (Step 6 must name the anchor + cluster-aligned quote) | **3/7 = 42.9%** | C3 (IA primary), C4 (PAP primary + AB secondary), C5 (CC primary). C1's PT was validated and surfaced but Step 6 doesn't name it. |
| `friction_yield_strict_including_anchor_present_but_step6_hidden` | **4/7 = 57.1%** | Above + C1's PT (validated, surfaced, but hidden in revised.txt). The gap (1 cluster) measures Step 6 consumption miss on a validated anchor. |
| `friction_yield_any_honest` | **4/7 = 57.1%** | Same as above; on this case strict-vs-broad converges except for the Step-6-hidden distinction. No quote drift. |
| `strictness_failure_rate_strict` | **0/2 = 0%** | Denominator: clusters with sufficient fingerprint specificity AND expected model in candidates. C1 and C5 qualify; both were accepted. **No verifier strictness failure on the strict denominator.** |
| `strictness_failure_rate_broad` | **1/5 = 20%** | Denominator: clusters where expected primary reached candidates. C7 (Premortem rejected) is the only verifier rejection. |
| Trust axis (this case) | clean | 0% noisy_anchor_rate, 0% post-verifier validation, all anchors aligned. |
| Friction axis (this case) | mid-strong | 43%–57% friction yield (vs case 1's 17–33%, case 2's 43%). Strictness failure 0%–20% (vs case 1's 50–60%, case 2's 40–50%). **The verifier-strictness signal does not recur strongly here.** |

## Findings

### F1''' — The case-1+2 family hypothesis breaks; a sharper hypothesis fits the data

The "external-legible passes / interpretive misses" frame predicted *Probabilistic Thinking* and *Confidence Calibration* would be rejected as calibration/abstract-cognitive operations. Both passed cleanly with cluster-aligned quotes and primary Step 6 use (CC) or near-primary visibility (PT preserved as reasoning, model name hidden). The frame as stated needs replacement.

A sharper hypothesis fits all three cases so far:

> **The verifier accepts a model when the source quote contains operationalized mechanism language for that model — explicit numbers, named processes, or observable behaviors that map directly to the model's mechanism. The verifier rejects when the model's mechanism requires interpretive translation between the source language and the model concept.**

Evidence:
- *Probabilistic Thinking* passed because the C1 quote contained "less than 1 in 5", "non-zero chance" — operationalized probability.
- *Confidence Calibration* passed because the C5 quote contained "90%+", "70% or below", "60-65%" — operationalized confidence thresholds.
- *Principal Agent Problem* passed because the C4 quote contained "financial and political incentives", "salaried fiduciary", "book of business pays the firm" — operationalized agency mechanism.
- *Information Asymmetry* passed because the C3 quote contained "tip off the partner... cover story" — operationalized info-mechanism.
- *Theory Of Constraints* passed on case 2 C4 because the quote contained "everything else is speculative", "his buy-in is what blocks yes" — operationalized blocking condition.
- *Margin Of Safety* passed on case 1 because the quote contained explicit dollar/month math.
- *Premortem* fails consistently because the source rarely contains explicit "if X happens, we reverse" pre-registration language — it's a reasoning pattern *about* failure planning rather than the literal pre-registration operation.
- *Inversion* failed on case 2 because "remove prestige and test attraction" is a counterfactual *thinking move* without operational language.
- *Opportunity Cost* fails consistently because comparing values requires interpretive recognition rather than naming a specific mechanism, even when explicit numbers exist (case 1 fractional-dollar tradeoff was rejected).
- *Optionality* fails consistently because "generate paths" is an interpretive move; the substrate's mechanism for Optionality may not match how the assistant typically writes about option-design.
- *Problem Framing And Reframing* fails consistently — but interestingly, on cases 1 and 3 it fails at recall, and on case 2 at the verifier. PFR's mechanism may not have keyword anchors for recall to find, AND its mechanism is interpretive enough that the verifier rejects it when it does land in candidates.

This is a more useful hypothesis: it predicts behavior from the *source quote's language properties*, not from the model's category. To test it, the next case should compare predictions made by reading the quote and asking "is the mechanism literally present in operational language?"

### F2''' — Recall is a separate failure mode from verifier strictness

Case 3 has high verifier acceptance (80% on candidates) but moderate friction yield (43–57%) because two clusters had recall failures (C2, C6 — both PFR primary). The producer chain has at least two distinct leak points:

- **Recall hole** for PFR specifically. Across 3 cases, PFR is missing from the user-visible product on case 1 (recall_failed), case 2 (verifier_failed after reaching candidates), case 3 (recall_failed twice). Different mechanisms, same outcome.
- **Verifier rejection** for interpretive-mechanism models (Premortem, Optionality, Inversion, Opportunity Cost).

The §9 decision tree can route both. PFR's recall hole points at the recall substrate (keyword + embedding); the interpretive-mechanism rejection points at verifier-prompt or verifier-rubric calibration.

### F3''' — Step 6 named-anchor consumption is high here

4 of 5 anchors are named in revised.txt with primary treatment (PAP, AB, IA, CC). Only PT is hidden. That's better Step 6 consumption than the lane2-attribution synthesis suggests for this case (20%) — likely because the synthesis's measurement was based on token-overlap with anchor display names, not curated-label recognition, and revised.txt uses lowercase hyphenated forms ("principal-agent problem", "confidence-calibration") rather than verbatim Title Case.

This is also a pre-PR-#41 archive. Future runs under the verbatim-naming PR #41 contract should produce more discoverable Step 6 surfaces, which would also narrow the "validated anchor not named in Step 6" gap (C1 PT here).

### F4''' — Authority Bias as `presence_mode = violated` is a useful signal

The AB anchor is the only anchor in the corpus so far with `presence_mode = violated` rather than `executed`. The mode reflects that the assistant pushed AGAINST authority deference (recommending external whistleblower counsel rather than trusting GC). This is meaningful product behavior — the system identified a bias the user was at risk of and surfaced it as a counter-pressure. That is exactly the curated-friction job Lolla promises.

## Cross-case comparison: cases 1 + 2 + 3

| Dimension | Case 1 | Case 2 | Case 3 |
|---|---|---|---|
| `cluster_recall` | 7/7 | 7/7 | 4/7 |
| `candidate_recall@60` | 5/6 = 83% | 6/7 = 86% | 5/7 = 71% |
| `verifier_acceptance_rate` | 2/5 = 40% | 2/6 = 33% | 4/5 = 80% |
| `post_verifier_validation_failure_rate` | 1/2 = 50% | 0/2 = 0% | 0/4 = 0% |
| `noisy_anchor_rate` | 0% | 0% | 0% |
| `friction_yield_strict` | 1/6 = 17% | 3/7 = 43% | 3/7 = 43% (4/7 = 57% if Step-6-hidden PT counts) |
| `strictness_failure_rate_strict` | 2/4 = 50% | 2/5 = 40% | 0/2 = 0% |
| `strictness_failure_rate_broad` | 3/5 = 60% | 3/6 = 50% | 1/5 = 20% |

### Recurring patterns

1. **PFR is consistently absent** from the user-visible product, with different failure mechanisms across cases (recall on cases 1 + 3, verifier on case 2). This is the most consistent miss in the audit.
2. **Premortem is rejected at the verifier** when it reaches candidates (cases 1 + 3); not tested on case 2.
3. **Optionality is consistently absent** (verifier rejection on case 1 C4, recall failure on cases 2 + 3).
4. **Information Asymmetry passes cleanly** when its mechanism is operationalized in the source (cases 2 C8, 3 C3).
5. **Trust axis stays clean** on all 3 cases. Zero false positives across 14 surfaced anchors.

### Pattern that broke between cases 1+2 and case 3

- **Verifier strictness on calibration/abstract-cognitive models.** Cases 1+2 had no calibration models in the gold set; case 3's Probabilistic Thinking + Confidence Calibration both passed. The "calibration/abstract-cognitive will miss" prediction failed.

### Updated cross-case picture (N=3)

The verifier's behavior is *not* well-described by mental-model categories. The sharper hypothesis ($F1'''$) is **operational-language presence** in the source quote. The next case (mother-deciding-address-year) is the test: predict per cluster based on whether the source quote operationalizes the mechanism, then see if predictions hold.

## Locked bottom-line for case 3

`mid-level-consultant-decides` shows **mid-strong friction yield (43–57%) with zero verifier strictness on clusters where the producer chain delivered.** Five anchor-worthy clusters delivered honest curated pressure (C1 PT validated, C3 IA primary, C4 PAP+AB primary+secondary, C5 CC primary), with C1's PT preserved as reasoning but not named in Step 6. Two clusters had recall failures (PFR on C2 + C6). One cluster had a clean verifier rejection (Premortem on C7).

The **family hypothesis from cases 1+2 broke decisively**: Probabilistic Thinking and Confidence Calibration both passed cleanly when their source quotes contained operationalized mechanism language. The replacement hypothesis ($F1'''$) is that **operational-language presence in the source quote** — not mental-model category — predicts verifier behavior. This is testable on case 4 (mother-deciding-address-year) by making per-cluster predictions from the source quotes' language properties before opening Lane 2 outputs.

The **PFR-consistently-absent** pattern is now N=3 cases of the same outcome via different failure mechanisms (recall, verifier, recall+recall). PFR is a distinct producer-side bug independent of the strictness story.

Holding cases 4 (mother), 5 (marcus-equity), 6 (mother-baseline), 7 (phd-student) per discipline. The hypothesis test is now: does $F1'''$ predict verifier behavior on mother-deciding-address-year, where the source mixes power-dynamics, opportunity-cost, second-order-thinking, and feedback-loops reasoning?

## Resolved notes

- Family hypothesis from cases 1+2 BROKEN by case 3 (Probabilistic Thinking and Confidence Calibration both passed). New hypothesis ($F1'''$) is operational-language presence in source quotes.
- PFR pattern (3/3 cases consistently missing) is now established as a distinct recall-and-verifier hole, independent of the verifier-strictness story.
- Trust axis remains clean across all 3 cases. The trust gates are doing their work.
- Cases 4–7 still pending. Per Marcin's discipline: do not redesign yet, do not loosen the trust gates, and do continue updating the family hypothesis as new cases test it.
