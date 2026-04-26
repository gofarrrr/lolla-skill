# Step 2 attribution — `year-old-oncologist-accept`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: gold cluster table from `case_year-old-oncologist-accept_step1_source_first.md` (authored by Marcin via blind subagent labelers, locked).

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (7 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (4 final accepted)
- `result.json.audit_summary.companion_rejected_models` (56 rejected: 53 "mechanism absent", 3 "too generic")
- `result.json.companion_cheat_sheet.anchors` (4 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 60 (56 rejected + 4 accepted). Cap was filled.

## Gold cluster rows

### C1 — Separate the bundled decision into different questions

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `acceptable_secondary_models` | *Decomposition* |
| `should_reject_models` | *Theory Of Constraints*, *Opportunity Cost* |
| `fingerprint_found_cluster` | yes (Move 1) |
| `fingerprint_move_text` | "Decomposing the decision into distinct categories to prevent conflation and enable targeted analysis" |
| `candidate_recall_hit` (Problem Framing And Reframing) | yes |
| `verifier_accepted` (PFR) | **no** — `mechanism absent` |
| `failure_owner` (PFR primary) | **verifier_failed** |
| `candidate_recall_hit` (Decomposition, secondary) | yes |
| `verifier_accepted` (Decomposition) | yes (final accepted, surfaced, primary in Step 6) |
| `step6_treatment` (Decomposition) | primary in revised.txt §1: "Decomposition into career/family/financial buckets in turn 1 was right; without it the conversation would have stayed tangled." |
| `notes` | The fingerprint move-name itself ("Decomposing the decision…") leans toward Decomposition framing, which may be why recall surfaced Decomposition strongly while *Problem Framing And Reframing* was rejected. The cluster's expected secondary surfaced as primary on the cluster's source quote — Marcin's narrow boundary holds (Decomposition gets credit only if the quote IS the explicit career/family/financial separation, which it is). Cluster yielded honest curated pressure to Step 6, but the *expected primary* was missed. |

### C2 — Escape-vs-fit test (counterfactual)

| Field | Value |
|---|---|
| `expected_primary_models` | *Inversion* |
| `acceptable_secondary_models` | *Problem Framing And Reframing*, *Confidence Calibration* |
| `should_reject_models` | *Status Quo Bias*, *Sunk Cost Fallacy*, *Opportunity Cost* |
| `fingerprint_found_cluster` | yes (Move 2) |
| `fingerprint_move_text` | "Distinguishing between motivation driven by dissatisfaction versus genuine opportunity fit using a hypothetical test" |
| `candidate_recall_hit` (Inversion) | yes |
| `verifier_accepted` (Inversion) | **no** — `mechanism absent` |
| `failure_owner` (Inversion) | **verifier_failed** |
| `notes` | Textbook *Inversion* — strip the prestige/upside, test whether the role still attracts. Fingerprint named the move sharply ("hypothetical test"). Verifier rejected. |
| `should_reject_check` | *Status Quo Bias*, *Sunk Cost Fallacy* both in candidate list, both rejected with "mechanism absent" — verifier correctly screened the should_reject candidates ✓ |

### C3 — Mother-time tradeoff

| Field | Value |
|---|---|
| `expected_primary_models` | *Opportunity Cost* |
| `acceptable_secondary_models` | *Inversion*, *Second Order Thinking* |
| `should_reject_models` | *Margin Of Safety*, *Power Dynamics*, *Theory Of Constraints*, *Decomposition* |
| `fingerprint_found_cluster` | yes (Move 3) |
| `fingerprint_move_text` | "Prioritizing irreplaceable finite-time commitments over compensable or negotiable ones" |
| `candidate_recall_hit` (Opportunity Cost) | yes |
| `verifier_accepted` (Opportunity Cost) | **no** — `mechanism absent` |
| `failure_owner` (Opportunity Cost) | **verifier_failed** |
| `notes` | The clearest Opportunity Cost source quote in either case so far ("3-5 good years where visits mean something is a specific quantity of time, and any plan that makes monthly visits impossible is trading that specific quantity for money"). Fingerprint move is sharp. Verifier rejected with "mechanism absent." Same pattern as case 1 C6 (Opportunity Cost on fractional tradeoff). |
| `should_reject_check` | *Margin Of Safety*, *Power Dynamics*, *Decomposition* all in candidate list, all rejected — verifier screening adjacency ✓ |

### C4 — Husband buy-in is the non-workaround constraint

| Field | Value |
|---|---|
| `expected_primary_models` | *Theory Of Constraints* (under narrow husband-as-blocking-condition boundary) |
| `acceptable_secondary_models` | *Information Asymmetry*, *Premortem*, *Power Dynamics* |
| `should_reject_models` | *Principal Agent Problem*, *Opportunity Cost*, *Status Quo Bias* |
| `fingerprint_found_cluster` | yes (Move 4) |
| `fingerprint_move_text` | "Identifying critical dependencies that must be resolved before downstream decisions" |
| `candidate_recall_hit` (Theory Of Constraints) | yes |
| `verifier_accepted` (Theory Of Constraints) | **yes** |
| `surfaced_top5` | yes |
| `step6_treatment` | primary in revised.txt §1: "Theory Of Constraints reads my reasoning correctly: until that conversation produces a concrete answer, the rest is speculative." |
| `evidence_quote_attribution` | Lane 2's evidence quote: "And — if the husband conversation hasn't happened, that's the thing that makes everything else speculative…" — **exactly the C4 source quote**, well within Marcin's narrow boundary. |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | This is the kind of result the audit is designed to detect: a broad model (Theory Of Constraints) that the bucket hypothesis flagged as a false-positive risk turns out to be the right primary under a sharp source-justified boundary, and Lane 2 surfaced it correctly with an aligned quote. The narrow-boundary discipline survives. |
| `should_reject_check` | *Principal Agent Problem*, *Opportunity Cost*, *Status Quo Bias* all in candidate list, all rejected ✓ |

### C5 — Convert constraints into negotiated terms

| Field | Value |
|---|---|
| `expected_primary_models` | *Optionality* |
| `acceptable_secondary_models` | *Batna*, *Information Asymmetry*, *Margin Of Safety* |
| `should_reject_models` | *Theory Of Constraints*, *Decomposition*, *Principal Agent Problem* |
| `fingerprint_found_cluster` | partial (Move 5 captures the "reframing perceived hard constraints as manageable costs" framing, but the *option-design* mechanism — redesigning the offer so threatened values remain possible — is broader than M5's framing) |
| `fingerprint_move_text` | "Reframing perceived hard constraints as manageable costs with specific mitigation strategies" |
| `candidate_recall_hit` (Optionality) | **no** — `optionality` is NOT in the candidate slate (neither accepted nor rejected list) |
| `failure_owner` (Optionality) | **recall_failed** |
| `candidate_recall_hit` (Batna, secondary) | yes |
| `verifier_accepted` (Batna, secondary) | yes |
| `evidence_quote_attribution` (Batna) | Lane 2's Batna evidence quote is from Turn 9 (non-compete review), which is **C8 territory, not C5.** |
| `notes` | C5's expected primary failed at recall — Optionality didn't reach candidates. Batna surfaced but with a C8-aligned quote, so it does not credit C5. C5 surfaced no anchor with C5-aligned quotes. |

### C6 — Duties vs vetoes triage

| Field | Value |
|---|---|
| `expected_primary_models` | `no_clean_primary` |
| `acceptable_secondary_models` | *Problem Framing And Reframing*, *Opportunity Cost* |
| `should_reject_models` | *Principal Agent Problem*, *Power Dynamics*, *Theory Of Constraints*, *Decomposition* |
| `fingerprint_found_cluster` | yes (Move 5 partially captures "Priya has a committee… she will not fail because you leave") |
| `failure_owner` | **none** — `no_clean_primary` means there is nothing to attribute as missed. |
| `notes` | Lane 2 did not surface a model for this cluster. That is the correct behavior: the cluster contains real reasoning but does not deserve an anchor. *Theory Of Constraints*, *Decomposition* both rejected from candidates — verifier correctly did not force-fit a model on this triage cluster. |

### C7 — Non-compete lock-in changes the exit option set

| Field | Value |
|---|---|
| `expected_primary_models` | *Switching Costs* |
| `acceptable_secondary_models` | *Optionality*, *Batna*, *Inversion* |
| `should_reject_models` | *Theory Of Constraints*, *Decomposition*, *Margin Of Safety* |
| `fingerprint_found_cluster` | partial (Move 7 mentions "exit options" but does not sharply name the lock-in / cost-of-switching mechanism) |
| `fingerprint_move_text` | "Weighing career-stage timing and exit options against family and role-specific risks" |
| `candidate_recall_hit` (Switching Costs) | yes |
| `verifier_accepted` (Switching Costs) | **no** — `mechanism absent` |
| `failure_owner` (Switching Costs) | **verifier_failed**, with `fingerprint_specificity_partial` caveat (analogous to case 1 C6 Opportunity Cost) |
| `notes` | The 2-year non-compete is an explicit lock-in / switching-cost mechanism in the source ("you're locked into it or you're going back to academia"). Verifier rejected. M7 does not isolate the lock-in mechanism cleanly, so this is the same caveat shape as case 1 C6: clean miss IF the verifier was supposed to recover from underspecified fingerprint context, mixed signal otherwise. |

### C8 — Resolve missing deal facts before counteroffer

| Field | Value |
|---|---|
| `expected_primary_models` | *Information Asymmetry* |
| `acceptable_secondary_models` | *Batna*, *Confidence Calibration*, *Premortem* |
| `should_reject_models` | *Decomposition*, *Theory Of Constraints*, *Power Dynamics* |
| `fingerprint_found_cluster` | yes (Move 6) |
| `fingerprint_move_text` | "Sequencing information gathering and negotiations to avoid premature commitments" |
| `candidate_recall_hit` (Information Asymmetry) | yes |
| `verifier_accepted` (Information Asymmetry) | yes |
| `surfaced_top5` | yes |
| `step6_treatment` | primary in revised.txt §1: "Information Asymmetry caught what turn 10 already corrected: Merck holds the substantive information about the role, and you need to surface it before pricing your asks." |
| `evidence_quote_attribution` | Lane 2's IA quote: "the second Merck conversation (portfolio + team) should happen before you draft the counter-offer, not in parallel…" — **exactly the C8 source quote.** |
| `failure_owner` (Information Asymmetry) | **none — CLEAN PRIMARY HIT.** |
| `candidate_recall_hit` (Batna, secondary) | yes |
| `verifier_accepted` (Batna, secondary) | yes |
| `evidence_quote_attribution` (Batna) | Lane 2's Batna quote: "get the non-compete reviewed by a lawyer you trust, not a Merck-provided one. Non-compete language in immunotherapy is frequently more aggressive…" — Turn 9, C8 territory. **Aligned.** |
| `failure_owner` (Batna) | **none — clean secondary hit, aligned quote.** |

## Observed-anchor rows

### Observed: *Decomposition*

| Field | Value |
|---|---|
| `best_matching_cluster` | C1 (cluster's `acceptable_secondary_model`) |
| `evidence_quote_attribution` | Lane 2 attached the C1 quote ("Before I say anything useful I want to separate a few things… career question / family question / financial question"). Aligned. |
| `classification` | **`acceptable_secondary`** — anchor IS the cluster's secondary, evidence quote sources from the cluster. Marcin's narrow boundary ("*Decomposition* can receive secondary credit only if the evidence quote is this explicit separation of career/family/financial questions") is exactly satisfied. |
| `failure_owner` | none |

### Observed: *Theory Of Constraints*

| Field | Value |
|---|---|
| `best_matching_cluster` | C4 (cluster's expected primary) |
| `evidence_quote_attribution` | Aligned to C4 source quote (husband-as-blocking-condition). |
| `classification` | **`acceptable_primary_match`** — anchor IS the cluster's expected primary, evidence quote aligned. The bucket hypothesis ("ToC is a false-positive risk on career decisions") was wrong on this case; ToC is the right primary under Marcin's narrow husband-buy-in boundary, and Lane 2 surfaced it cleanly. |
| `failure_owner` | none |

### Observed: *Batna*

| Field | Value |
|---|---|
| `best_matching_cluster` | C8 (cluster's `acceptable_secondary_model`) |
| `evidence_quote_attribution` | Aligned to C8 source quote (non-compete diligence / lawyer review). |
| `classification` | **`acceptable_secondary`** — clean secondary, aligned quote. |
| `failure_owner` | none |

### Observed: *Information Asymmetry*

| Field | Value |
|---|---|
| `best_matching_cluster` | C8 (cluster's expected primary) |
| `evidence_quote_attribution` | Aligned to C8 source quote (portfolio/team diligence before counter-offer). |
| `classification` | **`acceptable_primary_match`** — clean primary, aligned quote. |
| `failure_owner` | none |

## Aggregate metrics (this case only — N=1, single run)

Cluster denominator excludes C6 (`no_clean_primary`) for primary-recall metrics, so the anchor-worthy denominator is 7 (C1, C2, C3, C4, C5, C7, C8).

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 7/7 = 100% (or 5/7 = 71% if C5 and C7 partials are counted as miss) | Fingerprint extraction is strong. Two clusters have partial-specificity moves (C5, C7) — same shape as case 1's M3 / M7 partial moves. |
| `fingerprint_specificity` | 5/7 sufficient (C1, C2, C3, C4, C8); 2/7 partial (C5, C7) | Mostly fine. |
| `candidate_recall@60` (expected primaries that reached candidates) | 6/7 = 85.7% (Optionality on C5 missing; PFR, Inversion, Opportunity Cost, ToC, Switching Costs, Information Asymmetry all present) | Strong but C5 leak. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries that were candidates) | 2/6 = 33.3% (*Theory Of Constraints* and *Information Asymmetry*; PFR / Inversion / Opportunity Cost / Switching Costs all rejected with "mechanism absent") | Same shape as case 1: significant verifier rejection on clearly executed reasoning. |
| `post_verifier_validation_failure_rate` | 0/2 = 0% (no demotions on this case; both raw verifier acceptances passed quote validation) | The post-verifier validation gate did not fire on this case. Different from case 1 (where Base Rates was demoted). |
| Final validated acceptance on expected primaries | 2/6 = 33.3% (ToC + IA) | |
| `surfacing_recall@5` | 4/4 = 100% (every validated-accepted model survived top-5; cap not binding) | n/a small denominator |
| `noisy_anchor_rate` | 0/4 = 0% — all four observed anchors classify as `acceptable_primary_match` or `acceptable_secondary` with aligned quotes | Clean precision. The bucket hypothesis ("FP-risk control") was wrong: 0 false positives. |
| `step6_treatment_accuracy` | 4/4 — all four anchors get primary treatment in revised.txt and the treatment matches the cluster mapping | Clean. |

### Product-level friction metrics (per memo §8.3)

Anchor-worthy denominator: 7 clusters. Strict and broad variants reported.

| Metric | Value | What's counted |
|---|---|---|
| `friction_yield_strict` | **3/7 = 42.9%** | C1 (Decomposition validated secondary, C1-aligned quote), C4 (ToC validated primary, C4-aligned quote), C8 (Information Asymmetry validated primary + Batna validated secondary, both C8-aligned). |
| `friction_yield_any_honest` | **3/7 = 42.9%** | Same as strict. **No quote drift on this case** — every surfaced anchor's evidence quote sources from the cluster where the anchor is structurally located in the gold table. |
| `strictness_failure_rate_strict` | **2/5 = 40%** | C2 *Inversion* and C3 *Opportunity Cost* — fingerprint specific, expected model in candidates, verifier rejected with "mechanism absent." Denominator excludes C6 (no_clean_primary), C5 (recall failed, not strictness), C7 (partial fingerprint). |
| `strictness_failure_rate_broad` | **3/6 = 50%** | Above plus C7 *Switching Costs* on the broader reading. |
| Trust axis (this case) | clean | `noisy_anchor_rate` 0%, `post_verifier_validation_failure_rate` 0%, all anchors aligned, no quote drift. |
| Friction axis (this case) | mid | Friction yield 43% (better than case 1's 17%/33%), strictness failure 40-50% (similar to case 1's 50%/60%). |

## Findings

### F1' — The verifier "mechanism absent" rejection pattern recurs

Same shape as case 1: clearly executed mental models get rejected by the verifier with `mechanism absent`. On case 2:
- *Inversion* on C2 (escape-vs-fit counterfactual — textbook Inversion application)
- *Opportunity Cost* on C3 (mother-time as scarce non-fungible resource — explicit price-against-money reasoning)
- *Problem Framing And Reframing* on C1 (refusing to take the bundled decision at face value)
- *Switching Costs* on C7 (non-compete as 2-year lock-in on optimal exit)

Combined with case 1's rejected primaries (*Optionality*, *Opportunity Cost*, *Premortem*, *Problem Framing And Reframing*), a category pattern is starting to emerge:

| Category | Verifier behavior across both cases |
|---|---|
| Constraint / dependency / blocking-condition (*Theory Of Constraints*) | accepted cleanly when source-justified |
| Information / diligence / missing-info (*Information Asymmetry*) | accepted cleanly when source-justified |
| Fallback posture (*Batna*) | accepted as secondary when source-justified |
| Decomposition / separation-of-questions (*Decomposition*) | accepted as secondary when source-justified |
| Margin of safety / runway buffer (*Margin Of Safety*) | accepted on case 1 |
| Optimism / planning fallacy (*Optimism Bias And Planning Fallacy*) | accepted on case 1 |
| **Counterfactual / inversion** (*Inversion*) | **rejected** with "mechanism absent" |
| **Opportunity sizing of finite resources** (*Opportunity Cost*) | **rejected** with "mechanism absent" on both cases |
| **Option design / generating paths** (*Optionality*) | **rejected** with "mechanism absent" on case 1; **recall failed** on case 2 |
| **Pre-registered conditions / failure-mode planning** (*Premortem*) | **rejected** with "mechanism absent" on case 1 |
| **Problem reframing / refusing surface request** (*Problem Framing And Reframing*) | **rejected** with "mechanism absent" on both cases |
| **Switching costs / lock-in** (*Switching Costs*) | **rejected** on case 2 |

The pattern that's forming (N=2, hold for failure-rich cases): the verifier passes models with structural/economic mechanisms (constraint, information-flow, runway, fallback) and rejects models with cognitive/option-design mechanisms (counterfactual reframing, opportunity sizing of non-monetary value, optionality, pre-registration, problem reframing). This is a verifier-prompt or rubric calibration issue, not random noise.

### F2' — Trust axis is even cleaner on case 2

Zero false positives. Zero quote drift. Zero post-verifier validation demotions. Every anchor lands on its expected cluster with an aligned quote and Step 6 uses it correctly. The bucket hypothesis ("FP-risk control") was wrong on this case — the broad-looking models (ToC, Decomposition, IA, Batna) were all genuinely active under Marcin's narrow boundaries, and Lane 2's strict validation surfaced them correctly.

This is a positive finding for the trust axis. The system is not surfacing junk; what it surfaces is real.

### F3' — Friction yield improves but is not solved

Case 2 yields 42.9% friction (vs case 1's 17% strict / 33% generous). The improvement is real: when the source contains strong gating/dependency reasoning AND missing-information reasoning, Lane 2 surfaces them cleanly with full Step 6 consumption. **The product CAN work on this kind of source.**

But 42.9% means 4 of 7 anchor-worthy clusters surfaced nothing relevant: Inversion (C2), Opportunity Cost (C3), Optionality (C5), Switching Costs (C7). These are not edge cases — they are core reasoning moves on a major life decision. The friction-yield problem is asymmetric: it's not "Lane 2 surfaces nothing"; it's "Lane 2 systematically misses certain model categories."

### F4' — C1 is an interesting borderline case

Lane 2 surfaced *Decomposition* (cluster's secondary) on C1's source quote. Step 6 used Decomposition as primary. The cluster's expected primary (*Problem Framing And Reframing*) was rejected at the verifier.

On the trust axis, this is fine: Marcin's gold explicitly allows Decomposition as acceptable_secondary on C1 with the exact evidence quote that Lane 2 picked. So the surface is honest.

On the friction axis, it's borderline: the curated friction that reached Step 6 is correct but is the secondary lens, not the primary structural read. Step 6's user-facing version reads as "Decomposition into career/family/financial buckets in turn 1 was right" — which is true but slightly under-states the bigger structural move (refusing to accept the request at face value). This is the kind of subtle drift the friction-yield gap measures.

### F5' — Recall failure recurs but on a different model than case 1

Case 1's recall failure: *Problem Framing And Reframing* didn't reach candidates on C1.
Case 2's recall failure: *Optionality* didn't reach candidates on C5.

Different models, both general-purpose / option-design / problem-reframing flavor. May or may not be a pattern; needs more cases.

## Cross-case comparison: case 1 + case 2

| Dimension | Case 1 (`fintech-launch`) | Case 2 (`oncologist-accept`) |
|---|---|---|
| Bucket hypothesis | cleaner positive control | false-positive risk control |
| Bucket hypothesis result | partly wrong (low friction yield) | partly wrong (no false positives, broad models valid under narrow boundaries) |
| `cluster_recall` | 7/7 (or 6/7 partial) | 7/7 (or 5/7 partial) |
| `candidate_recall@60` | 5/6 = 83% | 6/7 = 86% |
| `verifier_acceptance_rate` | 2/5 = 40% | 2/6 = 33% |
| `post_verifier_validation_failure_rate` | 1/2 = 50% (Base Rates demoted) | 0/2 = 0% |
| `noisy_anchor_rate` | 0% | 0% |
| `friction_yield_strict` | 1/6 = 17% | 3/7 = 43% |
| `friction_yield_any_honest` | 2/6 = 33% | 3/7 = 43% |
| `strictness_failure_rate_strict` | 2/4 = 50% | 2/5 = 40% |
| `strictness_failure_rate_broad` | 3/5 = 60% | 3/6 = 50% |
| Trust axis | clean (with quote drift on 2 anchors) | clean (no quote drift) |
| Friction axis | weak (1/6 strict) | mid (3/7 strict, but still 4/7 anchor-worthy clusters yielding nothing) |

### What's recurring

1. **Verifier "mechanism absent" rejection of the same model categories.** Counterfactual / opportunity-sizing / optionality / problem-reframing / pre-registration consistently miss on both cases, despite clearly executed reasoning. **N=2; hold the verb "systematic" until failure-rich cases confirm.**
2. **Strictness failure rate of 40–60% on clusters where fingerprint + recall succeeded.** On both cases, the verifier rejects roughly half of the time the producer chain handed it sound input. The product job (curated pressure into Step 6) requires this to be lower, or for the friction-yield path to compensate.
3. **Trust axis remains clean.** Zero false positives across both cases. The validation gates are doing their work correctly.

### What's different

1. **Friction yield improved meaningfully on case 2** (43% vs 17–33% on case 1). When the source contains structural-economic reasoning (gating constraint, information asymmetry, runway), Lane 2 surfaces it cleanly. When the source contains cognitive-option reasoning, Lane 2 misses it.
2. **No quote drift on case 2.** Strict and broad converge. Anchor-to-evidence attribution is clean.
3. **No post-verifier validation demotion on case 2.** The literal-substring quote gate did not fire here.

## Locked bottom-line for case 2

`year-old-oncologist-accept` shows **moderate friction yield (43%) with clean trust (no false positives, no quote drift, no post-verifier demotions).** Two anchor-worthy clusters delivered clean primary anchors (C4 Theory Of Constraints, C8 Information Asymmetry); one delivered a clean secondary (C1 Decomposition); both anchors that Step 6 used as primary critique pressure are correctly placed. The bucket hypothesis ("FP-risk control") was wrong: broad-looking models surfaced *correctly* with aligned quotes, not as false positives. **Lane 2 can deliver curated friction when the source contains structural-economic reasoning and the verifier judges it executed.**

But four anchor-worthy clusters surfaced no useful pressure: *Inversion* on the escape-vs-fit counterfactual, *Opportunity Cost* on the mother-time tradeoff, *Optionality* on the negotiated-terms cluster, *Switching Costs* on the non-compete lock-in. The verifier's "mechanism absent" rejection pattern from case 1 recurs here on similar model categories.

## Cross-case signal

After two cases, an asymmetric pattern is forming: the verifier consistently passes models with structural/economic mechanisms (constraint, information-flow, fallback, runway buffer, decomposition) and consistently rejects models with cognitive-option mechanisms (counterfactual, opportunity sizing of non-monetary value, optionality, pre-registration, problem-reframing, switching costs). Hold the word "systematic" until failure-rich cases confirm — N=2 is small, and the same conversation styles (life decision under family pressure) on both cases may be selecting for the same source patterns. But the directional signal is meaningful enough that the audit's next step (failure-rich cases) is now usefully focused: does this category-asymmetry hold on conversations with different reasoning shapes (Marcus equity, consultant-decides regulatory, mother safety-planning)?

If yes, the §9 friction-yield branch fires not as "verifier is too strict generally" but as **"verifier is calibrated against a particular family of mental-model categories"** — which is a more specific and addressable problem than "decompose the producer."

If no, case 2's mid friction-yield is the better calibration, and case 1's worse outcome is type-of-conversation-specific.

## Resolved notes / open questions

This case **strengthens** the case-1 hypothesis that strictness is the dominant friction-yield bottleneck, while **softening** the case-1 hypothesis that broad models are systematically over-recalled. Holding cases 3–7 per the audit discipline. Failure-rich cases are next when Marcin chooses to proceed.
