# Step 2 attribution — `third-year-phd-student`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: locked gold cluster table + F2 prediction table from `case_third-year-phd-student_step1_source_first.md`.

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (7 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (5 final accepted)
- `result.json.audit_summary.companion_rejected_models` (54 rejected; 45 "mechanism absent", 8 "too generic", 1 "topic-adjacent")
- `result.json.companion_cheat_sheet.anchors` (5 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 59 (54 rejected + 5 accepted).

## Pre-registered F2 prediction test results

Predictions locked in commit `e9d4e44` BEFORE Lane 2 outputs were opened.

| Cluster | Expected primary | F2 Prediction | Actual | Outcome |
|---|---|---|---|---|
| C1 | *Status Quo Bias* | accept (default-inertia named locally) | **ACCEPTED**, cluster-aligned | ✓ |
| C2 | *Base Rates* | accept (explicit frequency comparison) | **ACCEPTED**, cluster-aligned | ✓ |
| C3 | *Optionality* | lean-accept with hedge (chronic-fail across cases 1-3 even with explicit naming) | **ACCEPTED**, cluster-aligned | ✓ — **first Optionality acceptance in audit; explicit naming + path-listing was sufficient** |
| C4 | *Problem Framing And Reframing* | recall/verifier-risk (chronic-fail across N=5 cases) | **ACCEPTED**, cluster-aligned | **prediction_miss_but_hypothesis_strengthening** — F2 said PFR fragile; explicit "framing" language operationalized it. The PFR miss was conversation-shape-specific (cases 1-5 lacked explicit framing language), not a model-specific blind spot. |
| C5, C6 | ambiguous | no anchor expected | no anchor surfaced for either | ✓ |
| C7 | *Premortem* | KEY F2 TEST: accept under literal pre-registration | **ACCEPTED**, but quote drifts to Turn 6 failure-scenario imagining instead of Turn 17 go/no-go | ✓ partial — model accepted; evidence quote sources from a Premortem-flavored sub-cluster I didn't include in C7's source quotes |

**Score: 5 clean matches + 1 prediction_miss_but_hypothesis_strengthening (C4 PFR) + 1 partial match with quote drift (C7).**

The audit's two most chronically-failing models (PFR and Premortem) both passed cleanly on case 6. F2 predicts both outcomes — explicit "framing" language operationalizes PFR; failure-scenario imagining ("Worst case: the combination turns out to not work…") operationalizes Premortem.

## Gold cluster rows

### C1 — "Everyone does it" Status Quo Bias

| Field | Value |
|---|---|
| `expected_primary_models` | *Status Quo Bias* |
| `fingerprint_found_cluster` | no (no fingerprint move quotes Turn 5's "everyone is doing it" content) |
| `candidate_recall_hit` (SQB) | yes |
| `verifier_accepted` (SQB) | **yes** |
| `evidence_quote_attribution` | "'it's common in my department' is also a status-quo signal — if everyone is doing it, it's by definition not differentiating." — exactly C1's source quote. |
| `step6_treatment` | primary in revised.txt §"What I'd set aside": "Status quo bias. The line 'common in your department is a status-quo signal — if everyone is doing it, it's by definition not differentiating' was the right pressure to apply to option 1, and I'd say it again." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | F2 predicts accept under "default/staying-put inertia named locally." Source has "status-quo signal" + "everyone is doing it" — explicit operationalization. |

### C2 — Base rate 20-30%

| Field | Value |
|---|---|
| `expected_primary_models` | *Base Rates* |
| `fingerprint_found_cluster` | no |
| `candidate_recall_hit` (BR) | yes |
| `verifier_accepted` (BR) | **yes** |
| `evidence_quote_attribution` | "The base rate of success on genuinely novel combinations in a PhD timeline is probably 20-30%, not 50%." — exactly C2's source quote. |
| `step6_treatment` | primary in revised.txt §"What I'd set aside" — used to drive the "18-month checkpoint is too late" critique. |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | F2 predicts accept under "explicit frequency/base-rate comparison." Source has "20-30%, not 50%" — explicit frequencies. |

### C3 — Career-optionality argument

| Field | Value |
|---|---|
| `expected_primary_models` | *Optionality* |
| `fingerprint_found_cluster` | no |
| `candidate_recall_hit` (Optionality) | yes |
| `verifier_accepted` (Optionality) | **yes** |
| `evidence_quote_attribution` | "A novel combination that's 60% worked gives you: multiple paper possibilities, a methods contribution, industry interest if it has practical applications, and a unique pitch for both postdoc and direct-to-industry paths." — exactly C3's source quote. |
| `step6_treatment` | named in revised.txt §"What I'd set aside" — "Optionality on its purest form — 'generate more options before narrowing.' I'd partly set this aside…" Treatment is `set_aside_with_reason` per PR #41 contract. |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | **First Optionality acceptance in the audit.** Cases 1+2+3 all had Optionality recall-fail or verifier-fail. Case 6's source has explicit "career-optionality argument" + literal listing of preserved paths ("multiple paper possibilities, methods contribution, industry interest, unique pitch"). F2 predicts accept under "explicit naming of preserving multiple paths or option value" — exactly satisfied. The chronic-fail pattern was conversation-shape-specific. |

### C4 — Multi-instance reframing

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `fingerprint_found_cluster` | yes (M4 + M7 cover Turn 8 + Turn 16 reframing instances) |
| `candidate_recall_hit` (PFR) | yes |
| `verifier_accepted` (PFR) | **yes** |
| `evidence_quote_attribution` | "When you describe it that way, it's much more specific and much less wild. 'Apply existing tumor evolution methods to existing single-cell datasets to extract something the single-cell field currently can't see' is a defined project, not a blue-sky combination." — exactly C4's source quote (Turn 8). |
| `step6_treatment` | primary in revised.txt §"What survived": "The reframe of option 3 from 'moonshot' to 'apply known evolutionary methods to existing single-cell data' was the right move — that's problem-framing-and-reframing doing real work, not narrative polish." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | **First PFR acceptance in the audit.** Cases 1-5 all had PFR absent (recall-failed 3x, verifier-rejected 2x). Case 6's source has explicit "I'd push back gently on the framing" (Turn 16) + multi-instance reframing language. F2 predicts accept under "explicitly says the question/frame is wrong" — satisfied. **The PFR chronic-fail pattern was conversation-shape-specific, not a model-specific blind spot.** This is the strongest F2 confirmation in the audit. |

### C5 — Retiring advisor risk (ambiguous primary)

| Field | Value |
|---|---|
| `expected_primary_models` | ambiguous (TOC / PD / `no_clean_primary`) |
| `fingerprint_found_cluster` | no |
| `candidate_recall_hit` | TOC NOT IN CANDIDATES; Power Dynamics rejected ("mechanism absent") |
| `failure_owner` | **none** — ambiguous primary; no clean canonical fit; gold-discipline correct behavior is no anchor surfaced. |

### C6 — Co-advisor protection (ambiguous primary)

| Field | Value |
|---|---|
| `expected_primary_models` | ambiguous (MoS / Optionality / TOC) |
| `fingerprint_found_cluster` | no |
| `candidate_recall_hit` | MoS rejected ("mechanism absent"); TOC not in candidates; Optionality is in candidates and accepted but its evidence quote sources from C3, not C6 |
| `failure_owner` | **none** — ambiguous primary; the cluster's reasoning is reflected in the Optionality anchor (acceptable_secondary on C6 per gold), but the anchor's primary attribution is to C3. |

### C7 — Premortem with go/no-go pre-registration

| Field | Value |
|---|---|
| `expected_primary_models` | *Premortem* |
| `fingerprint_found_cluster` | partial (M6 covers Turn 17 go/no-go content; Turn 6 failure-scenario not in any move's quotes) |
| `candidate_recall_hit` (Premortem) | yes |
| `verifier_accepted` (Premortem) | **yes** |
| `evidence_quote_attribution` | "Worst case: the combination turns out to not work, and you end up in year 5 needing to pivot to option 1 anyway but with less time to execute it." — **Turn 6.** My C7 source quotes were from Turn 17 (go/no-go checkpoint) + Turn 22 (write-it-down baseline). Turn 6 is a different premortem-flavored sub-cluster I should have included in C7's source quotes. |
| `step6_treatment` | primary in revised.txt §"What survived": "The premortem on fallback paths (salvage, pivot, extend) holds." This treatment matches Turn 17's fallback-paths reasoning, even though Lane 2's evidence_quote sources from Turn 6. |
| `failure_owner` | **none — primary HIT with quote drift.** Anchor IS the cluster's expected primary (Premortem); Step 6 uses it correctly; evidence quote sources from a Premortem-flavored sub-cluster I didn't capture in C7's labeling. |
| `classification` | **`acceptable_primary_match_with_quote_drift`** |
| `notes` | **First Premortem acceptance in the audit.** Cases 1+3 had Premortem rejected at verifier; case 4 had Premortem absent at recall. Case 6's source has TWO premortem-flavored instances: Turn 6 ("Worst case: the combination turns out not to work…") with explicit failure-scenario imagining; Turn 17 ("Set a go/no-go checkpoint at 18 months… commit to pivoting if no") with literal pre-registration. F2 predicts accept under either pattern. The verifier picked Turn 6's quote — explicit "imagine this failed because X" language operationalizes Premortem. **Labeling lesson:** my C7 should have included Turn 6's failure-scenario imagining as a source quote. The cluster boundary I drew was too narrow. |

## Observed-anchor rows

All 5 surfaced anchors classify cleanly:

| Anchor | Best matching cluster | Classification | Step 6 visibility |
|---|---|---|---|
| *Status Quo Bias* | C1 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Base Rates* | C2 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Optionality* | C3 (primary) | `acceptable_primary_match` | named, treatment = `set_aside_with_reason` |
| *Problem Framing And Reframing* | C4 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Premortem* | C7 (primary, with quote drift to Turn 6 sub-cluster) | `acceptable_primary_match_with_quote_drift` | named primary in revised.txt (using Turn 17 fallback-paths reasoning) |

`noisy_anchor_rate` = 0/5 = 0%. Trust axis stays clean across all 6 cases.

## Aggregate metrics

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 2/7 cleanly hit (C4 + C7 partial); 5/7 missed (C1, C2, C3, C5, C6) | Lowest fingerprint coverage in audit. Verifier compensated heavily — accepted models for clusters fingerprint didn't even quote. |
| `candidate_recall@60` (expected primaries that reached candidates) | 5/5 = 100% | All 5 expected primaries reached the verifier. Highest in audit. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries) | **5/5 = 100%** | Tied with case 4. |
| `post_verifier_validation_failure_rate` | 0/5 = 0% | No demotions. |
| `noisy_anchor_rate` | 0% | Consistent across all 6 cases. |
| `step6_treatment_accuracy` | 5/5 = 100% — every anchor named in revised.txt with primary or set_aside_with_reason treatment | |

### Product-level friction metrics

Three reporting cuts, each with a different question:

| Metric | Value | Denominator | Question it answers |
|---|---|---|---|
| `friction_yield_strict` (cross-case conservative) | **4/7 = 57.1%** | All 7 source-first clusters | Cross-case comparison: how much of the conversation's anchor-worthy reasoning surfaced cluster- and quote-aligned. Apples-to-apples with cases 1-5. |
| `friction_yield_strict` on clean expected primaries (F2 theory testing) | **4/5 = 80%** | 5 clusters with non-ambiguous expected primary (excludes C5+C6 with `gold_ambiguity_note`) | F2 prediction quality: when a cluster has a clean canonical 222 fit, does Lane 2 surface it cluster- and quote-aligned? |
| `friction_yield_any_honest` on clean expected primaries (with caveat) | **5/5 = 100%** | Same 5 clusters | Product yield with quote-drift admitted. Caveat: Premortem on C7 has quote drift — model is right, evidence quote sources from Turn 6 sub-cluster I missed in labeling. |
| `strictness_failure_rate_strict` | **0/2 = 0%** | Clusters with sufficient fingerprint specificity AND expected model in candidates (C4, C7 partial) | Did the verifier reject anything that the producer chain delivered with clean fingerprint context? |
| `strictness_failure_rate_broad` | **0/5 = 0%** | All clusters where expected primary reached candidates | Did the verifier reject any expected primary at all? |
| Trust axis | clean | | 0% `noisy_anchor_rate`, 0% post-verifier validation across this case. Cumulative 0/23 across cases 1-6. |

## Findings

### F2 strongly validated; chronic-fail patterns were conversation-shape-specific

Case 6 is the strongest F2 confirmation in the audit. Two of the most chronically-failing models — PFR (5/5 absent on prior cases) and Premortem (3/4 fail on prior cases) — both **accepted cleanly** when the source operationalized their mechanisms in F2-predicted ways:

- PFR: explicit "framing" language ("I'd push back gently on the framing")
- Premortem: explicit failure-scenario imagining ("Worst case: the combination turns out to not work…")
- Optionality: explicit "career-optionality" + literal path-listing

**The chronic-fail patterns were conversation-shape-specific, not model-specific verifier blind spots.** When a conversation contains explicit, locally-recognizable mechanism language for a model, the verifier accepts it consistently across all of: PFR, Premortem, Optionality, Status Quo Bias, Base Rates, and the verifier-friendly families (FL, IA, ToC, PAP, PD, MoS, RH).

### F2 is now the best-supported hypothesis with N=6

| Family | Cases supporting F2 | Counter-evidence |
|---|---|---|
| External-information (IA) | 2, 3 | none |
| External-dependency (ToC) | 2 | none |
| Fallback posture (Batna) | 2 | none |
| Runway buffer (MoS) | 1 | none |
| Calibration (PT, CC) | 3 | none |
| Agency (PAP, PD) | 3, 4 | none |
| Feedback loops (FL) | 4 | none |
| Decomposition | 2 | none |
| Representativeness (RH) | 5 | none |
| Counterfactual (Inversion) | none yet | none yet |
| Comparative-value (OC) | 4 (mutual exclusion) | **Marcus 5 C5** (explicit dollar math + mutual exclusion, rejected) |
| Option-design (Optionality) | 6 (path-listing) | none in this case |
| Failure-planning (Premortem) | 6 (failure-scenario) | cases 1, 3 with conditional/pre-registered language rejected |
| Interpretive (PFR) | 6 (explicit framing language) | cases 1-5 absent (mostly recall failures) |

**Marcus C5 OC remains the only clean F2 counter-example.** Even with explicit mutual-exclusion phrasing and dollar math, OC was rejected with "mechanism absent." Possible explanations:
- Conversation-level lexical density (Marcus had a thin 13-candidate slate; the verifier may apply stricter criteria when candidates compete in a small slate)
- OC has a model-specific quirk — verifier may need very specific OC keywords ("forgone alternative", "trading off", "the cost of not choosing X is Y") that case-1 (cases 1+2+5) didn't have but case 4 did

This is a refinement question for F2, not a falsification.

### Fingerprint coverage was lowest in the audit; verifier compensated

Only 2 of 7 clusters (C4, C7 partial) had direct fingerprint coverage. The verifier read broader assistant text and surfaced models for C1, C2, C3 without fingerprint extracting their source quotes. This continues the pattern from cases 3 and 4: **fingerprint specificity is necessary for some downstream behaviors (presumably recall vocabulary anchors), but the verifier itself reads the full assistant text and judges models against it directly.**

The implication: fixing fingerprint to extract more clusters would help recall but is not the dominant lever for verifier acceptance. The verifier-side fix (when needed) is verifier-prompt work, not fingerprint work.

### My C7 labeling missed Turn 6's premortem-flavored sub-cluster

Lane 2 surfaced Premortem on Turn 6 ("Worst case: the combination turns out to not work…") rather than on the Turn 17 go/no-go checkpoint I labeled as C7's source. Both are premortem-flavored. My cluster boundary was too narrow.

This is a labeling lesson, not a producer-chain finding. For future cases I should look for premortem-flavored reasoning across the whole conversation, not just the explicit pre-registration moments. Per F2, "imagine this failed because X" language is sufficient operationalization for Premortem, and a conversation may contain multiple instances.

## Cross-case comparison: cases 1 + 2 + 3 + 4 + 5 + 6

| Dimension | Case 1 | Case 2 | Case 3 | Case 4 | Case 5 | Case 6 |
|---|---|---|---|---|---|---|
| Total candidate slate | 60 | 60 | 60 | 56 | **13** | 59 |
| `cluster_recall` (fingerprint) | 7/7 | 7/7 | 4/7 | 6/7 | 4-5/7 | **2/7** |
| `candidate_recall@60` (expected primaries) | 83% | 86% | 71% | 71% | 71% | **100%** |
| `verifier_acceptance_rate` | 40% | 33% | 80% | 100% | 20% | **100%** |
| `post_verifier_validation_failure_rate` | 50% | 0% | 0% | 0% | 67% | 0% |
| `noisy_anchor_rate` | 0% | 0% | 0% | 0% | 0% | 0% |
| `friction_yield_strict` | 17% | 43% | 43% | 57% | 14% | **57-80%** |
| `strictness_failure_rate_strict` | 50% | 40% | 0% | 0% | 75% | **0%** |

### Recurring patterns N=6

1. **Trust axis stays clean** across all 6 cases. 0/23 false positives. The trust gates are reliably correct.
2. **F2 holds for most cases** — operational language predicts acceptance with high accuracy (5/5 expected primaries accepted on case 6).
3. **PFR and Premortem are not model-specific blind spots.** Both passed when source operationalized their mechanisms. The chronic-fail patterns from cases 1-5 were conversation-shape-specific.

### What's distinctive across cases

- **Marcus 5** is the F2 counter-example case (thin slate, aggressive validation, OC rejected despite mutual exclusion).
- **Case 6** is the F2 confirmation case (PFR + Premortem + Optionality all accept).
- **Cases 1, 2** had verifier strictness; **cases 3, 4, 6** have near-perfect verifier acceptance.
- **Marcus 5** has the highest post-validation drop rate (67%); other cases are 0% or 50%.

### Cumulative producer-chain leak modes (N=6)

1. **Recall vocabulary gaps** — Marcus shows this most clearly (13/60 candidates). Equity/founder-dynamics has thin candidate slates.
2. **Quote-validation strictness** — Case 1 + Marcus 5. Demotes models the verifier accepted with paraphrased quotes.
3. **Verifier interpretive rejection (where F2 doesn't hold)** — Marcus C5 OC is the only clean instance. Other apparent verifier rejections (cases 1, 3) are now better explained by F2: the source quotes lacked explicit operational mechanism language.
4. **Recall hole for some interpretive models in some conversations** — PFR cases 1, 3, 4; Optionality cases 2, 3; Premortem case 4. Looks conversation-specific (case 6 had all three reach candidates and pass), but the recall substrate has a reproducibility problem.

The audit's diagnosis after N=6 is: **the producer chain works well when the source operationalizes mechanisms locally and literally; the producer chain has reliability holes (recall, quote validation, OC-specific verifier behavior) that show up unpredictably across conversations.** F2 explains most of the variance.

## Locked bottom-line for case 6

`third-year-phd-student` shows **the highest friction yield in the audit (57-80% strict depending on denominator), 100% verifier acceptance on expected primaries, 100% Step 6 consumption, and the strongest F2 confirmation in the audit.**

Two chronically-failing models — PFR (5/5 absent on prior cases) and Premortem (3/4 fail on prior cases) — both accepted cleanly when the source operationalized their mechanisms per F2 predictions. The chronic-fail patterns were conversation-shape-specific, not model-specific verifier blind spots.

The C7 Premortem evidence quote sourced from a Turn-6 sub-cluster I didn't include in C7's source quotes — labeling lesson, not a producer leak. Step 6 still used Premortem in the right reasoning location (Turn 17 fallback-paths content).

**F2 is now the best-supported hypothesis at N=6.** The only clean counter-example remains Marcus C5 OC, where explicit mutual-exclusion + dollar math was rejected. That outlier suggests an OC-specific or conversation-level refinement F2 doesn't yet capture, but doesn't falsify the core hypothesis.

Holding case 7 (mid-level-consultant-report) per discipline. Per Marcin's pre-registered slate order, that's the final case in the audit corpus.

## Resolved notes

- F2 strongly validated on case 6. PFR + Premortem + Optionality all accept when source operationalizes mechanism per F2 predictions.
- The "chronic-fail" pattern is now best understood as conversation-shape-specific source variation, not model-specific verifier blind spots.
- Marcus C5 OC remains the only clean F2 counter-example. Refinement question, not falsification.
- Trust axis clean across all 6 cases (0/23 false positives).
- C7 labeling lesson: Premortem-flavored reasoning can span multiple turns; don't draw cluster boundaries too narrowly.
- Case 7 (consultant-report) is the final case.
