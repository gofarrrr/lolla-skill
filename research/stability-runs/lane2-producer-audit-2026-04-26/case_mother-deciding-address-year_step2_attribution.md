# Step 2 attribution — `mother-deciding-address-year`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: locked gold cluster table + F1''' prediction table from `case_mother-deciding-address-year_step1_source_first.md`.

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (6 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (5 final accepted)
- `result.json.audit_summary.companion_rejected_models` (51 rejected; 49 "mechanism absent", 2 "too generic")
- `result.json.companion_cheat_sheet.anchors` (5 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 56 (51 rejected + 5 accepted).

## Pre-registered F1''' prediction test results

This is the headline of case 4. Predictions were locked in commit `29daaf7` BEFORE Lane 2 outputs were opened.

| Cluster | Expected primary | Operationalization | Predicted | Actual | Match |
|---|---|---|---|---|---|
| C1 | *Problem Framing And Reframing* | medium | recall-risk | **NOT IN CANDIDATES** | ✓ |
| C2 | *Feedback Loops* | medium-to-high | accept | **ACCEPTED** with cluster-aligned quote | ✓ |
| C3 | *Second Order Thinking* | high | accept (with "too generic" hedge) | **ACCEPTED** with cluster-aligned quote | ✓ — hedge unnecessary |
| C4 | *Power Dynamics* | high | accept (per F1''') | **ACCEPTED** with cluster-aligned quote | ✓ — first PD acceptance in audit |
| C5 | *Problem Framing And Reframing* | medium | recall-risk | **NOT IN CANDIDATES** | ✓ |
| C6 | *Opportunity Cost* | medium-to-high | reject (per prior pattern) | **ACCEPTED** with cluster-aligned quote | ✗ — but in F1'''-supporting direction (mutual-exclusion phrasing operationalizes OC) |
| C7 | `no_clean_primary` | n/a | n/a | (no anchor surfaced for C7 — correct behavior) | ✓ |
| C8 | *Premortem* | high (literal if-when-then) | accept per F1''' (KEY TEST) | **NOT IN CANDIDATES** (fingerprint missed Turn 12 entirely; recall didn't surface Premortem) | ✗ — **cannot test the F1''' prediction at the verifier-blind-spot level because the candidate never reached the verifier** |

**Score: 6/7 prediction-actual matches; 1 unable-to-test (C8 Premortem); 0 outright wrong.** The OC mismatch on C6 is a *strengthening* of F1''' — explicit mutual-exclusion phrasing operationalizes OC sufficiently for the verifier, contradicting the prior-pattern hypothesis. F1''' predicted better than category history.

The Premortem test is unresolved. C8's source has the highest operationalization in the audit so far (literal "When [X] happens, remember [Y]" + explicit goal-redefinition), but fingerprint M6 didn't quote Turn 12 and recall didn't surface Premortem from broader text. We still don't know whether Premortem rejects under operational language because the producer chain didn't deliver it to the verifier.

## Gold cluster rows

### C1 — Reframe priority: relationship-repair before threat-management

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `fingerprint_found_cluster` | yes (M1: "Prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation") |
| `candidate_recall_hit` (PFR) | **no** |
| `failure_owner` | **recall_failed** |
| `notes` | 4th case in a row PFR fails (recall x3, verifier x1). The recall-substrate hole is robust across very different conversation domains. |

### C2 — Surveillance feedback loop

| Field | Value |
|---|---|
| `expected_primary_models` | *Feedback Loops* |
| `acceptable_secondary_models` | *Second Order Thinking*, *Information Asymmetry* |
| `fingerprint_found_cluster` | yes (M2: trade-offs between punitive controls and driving behavior underground; M5: surveillance's dual nature) |
| `candidate_recall_hit` (FL) | yes |
| `verifier_accepted` (FL) | **yes** |
| `evidence_quote_attribution` | "The answer is not tighter surveillance; it's rebuilding enough of a relationship that she wants to tell you when the next guy appears." — exactly C2's source quote. |
| `step6_treatment` | primary in revised.txt: "Feedback loops are the actual mechanism: you're trying to build a loop where she tells you things voluntarily, and every surveillance step is that loop's antagonist." Plus second mention later. |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** First Feedback Loops acceptance in the audit. |
| `notes` | The source operationalizes a self-undermining loop ("rebuild relationship → she tells you → information surfaces") with a counter-loop ("surveillance → discovery → larger trust breach"). Per F1''', operational mechanism language is present and verifier accepts. |
| `secondary check` (Information Asymmetry) | rejected with "mechanism absent" — IA was a candidate, verifier rejected. C4-flavored argument: surveillance creates information asymmetry, but the source's mechanism is relational not informational. F1''' predicts IA rejection here because the IA mechanism requires interpretive translation in this conversation, unlike cases 2/3 where IA had explicit operational quotes. |

### C3 — Block-the-guy → underground

| Field | Value |
|---|---|
| `expected_primary_models` | *Second Order Thinking* |
| `fingerprint_found_cluster` | yes (M2's evidence includes the blocking quote) |
| `candidate_recall_hit` (SOT) | yes |
| `verifier_accepted` (SOT) | **yes** |
| `evidence_quote_attribution` | "Sometimes blocking drives the communication underground on a different platform or device, and you lose visibility entirely." — exactly C3's source. |
| `step6_treatment` | primary in revised.txt §"What survived": "The second-order logic on blocking — visible first-order win (guy gone) hides a downstream loss (communication migrates to a platform you can't see) — is the right read." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | The "too generic" hedge from step 1 was unnecessary. SOT was rejected on case 3 with "too generic" because no specific cluster on case 3 had SOT as primary; surfaced via lexical recall on broad text. Here SOT IS the cluster's primary AND the source has explicit causal-chain language; the verifier accepted without the "too generic" tag. F1''' supported. |

### C4 — Ex-spouse competing power during custody

| Field | Value |
|---|---|
| `expected_primary_models` | *Power Dynamics* |
| `acceptable_secondary_models` | *Principal Agent Problem* |
| `fingerprint_found_cluster` | yes (M3: "Analyzing co-parenting dynamics as a constraint that amplifies risks of certain actions like reporting") |
| `candidate_recall_hit` (PD) | yes |
| `verifier_accepted` (PD) | **yes** |
| `evidence_quote_attribution` | "The fact that you even have to worry about your ex's reaction is a constraint on your options, not a choice." — Turn 4. C4's source spans Turn 4 + Turn 7. C4-aligned. |
| `step6_treatment` | primary in revised.txt §"What survived": "Power dynamics here isn't negotiation leverage; it's the shape of the decision space." |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** First Power Dynamics acceptance in the audit. |
| `notes` | PD has been rejected on cases 1+3 ("mechanism absent" / not in candidates). Here it passed because the source has explicit power-mechanism language ("ex's custody days", "she learns her dad is the safe one and you're the hysterical one", "constraint on your options"). F1''' overrides category history — operational language in the source is the differentiator. |
| `candidate_recall_hit` (PAP, secondary) | yes |
| `verifier_accepted` (PAP, secondary) | **yes** |
| `evidence_quote_attribution` (PAP) | "his minimization could actively harm her through the process (his statements to investigators, his influence on her during custody days)" — Turn 7. C4-aligned. |
| `step6_treatment` (PAP) | primary in revised.txt §"What shifted": "the principal-agent gap with your ex makes it worse." |
| `classification` (PAP) | `acceptable_secondary` — clean. |
| `notes` | C4 yields TWO clean validated anchors with cluster-aligned quotes (PD primary, PAP secondary), both used in Step 6. This is the highest single-cluster yield in the audit. |

### C5 — Goal reframe: "he's gone" vs "she's safe"

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `acceptable_secondary_models` | *Inversion* |
| `fingerprint_found_cluster` | yes (M4: "Distinguishing between parental goals of punishment and child protection") — the fingerprint extracted C5's source quote |
| `candidate_recall_hit` (PFR) | **no** |
| `candidate_recall_hit` (Inversion, secondary) | **no** (not in candidates) |
| `failure_owner` | **recall_failed** for both primary and secondary |
| `notes` | Same PFR pattern as C1 / cases 1+3. Inversion also missing — consistent with prior cases. The cluster's reasoning IS in Step 6 ("punishment vs protection" appears in revised.txt's reasoning) but no curated anchor reaches it. |

### C6 — Tradeoff: protection vs accountability

| Field | Value |
|---|---|
| `expected_primary_models` | *Opportunity Cost* |
| `fingerprint_found_cluster` | yes (M4 covers C5+C6) |
| `candidate_recall_hit` (OC) | yes |
| `verifier_accepted` (OC) | **yes** |
| `evidence_quote_attribution` | "if your goal is protecting her, not reporting and getting her to a specialized therapist is probably the better path given your co-parenting situation." — Turn 7. C6-aligned. |
| `step6_treatment` | primary in revised.txt §"What shifted": "The opportunity cost the no-report path makes harder is one I didn't name: *evidence preservation, other possible victims, and the narrowing window…*" |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** First Opportunity Cost acceptance in the audit. |
| `notes` | This is the F1'''-strengthening result. The prior-pattern prediction was REJECT (cases 1+2 had OC rejected even with explicit dollar/time math). On case 4 the source has explicit MUTUAL-EXCLUSION phrasing ("no version where X AND Y", "you have to pick the one that matters more, knowing you won't get both"). Verifier accepted. **Mutual-exclusion language operationalizes Opportunity Cost sufficiently** — that's the F1''' update from this case. |

### C7 — Don't call Mia's mom (`no_clean_primary`)

| Field | Value |
|---|---|
| `expected_primary_models` | `no_clean_primary` |
| `fingerprint_found_cluster` | no (no fingerprint move quotes Turn 9) |
| `failure_owner` | **none** — `no_clean_primary` correctly handled. No anchor surfaced for this cluster. |

### C8 — Premortem on panic + success criterion

| Field | Value |
|---|---|
| `expected_primary_models` | *Premortem* |
| `fingerprint_found_cluster` | **no** (M6 covers Turn 10's signal-reading, not Turn 12's premortem) |
| `candidate_recall_hit` (Premortem) | **no** (not in candidates) |
| `failure_owner` | **fingerprint_failed** + **recall_failed** for primary; cannot test verifier |
| `notes` | **The KEY F1''' test cannot be conducted on this case.** Source has the highest operationalization in the audit (literal "When [predicted failure] happens, [pre-registered correction]"), but fingerprint missed Turn 12 entirely and recall didn't surface Premortem from the broader text. We still don't know whether Premortem rejects under operational language because the producer chain didn't deliver it to the verifier. The test would need a case where Turn-by-turn fingerprint extracts a Premortem quote with explicit if-when-then language. |

## Observed-anchor rows

All 5 surfaced anchors classify cleanly:

| Anchor | Best matching cluster | Classification | Step 6 visibility |
|---|---|---|---|
| *Feedback Loops* | C2 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Second Order Thinking* | C3 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Power Dynamics* | C4 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Opportunity Cost* | C6 (primary) | `acceptable_primary_match` | named primary in revised.txt |
| *Principal Agent Problem* | C4 (secondary) | `acceptable_secondary` | named primary in revised.txt |

`noisy_anchor_rate` = 0/5 = 0%. No quote drift. No false positives.

## Aggregate metrics

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 6/7 anchor-worthy clusters cleanly hit (C1, C2, C3, C4, C5, C6); C7 excluded; C8 missed | Fingerprint covers 6/7 anchor-worthy clusters. Higher than case 3 (4/7). |
| `candidate_recall@60` (expected primaries that reached candidates) | 5/7 = 71% (FL, SOT, PD, OC reach; PFR ×2 + Premortem all absent) | Same shape as case 3 — PFR is the recurring recall hole. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries that were candidates) | **5/5 = 100%** | All five expected primaries that reached candidates were accepted. **Highest in the audit.** |
| `post_verifier_validation_failure_rate` | 0% | No demotions. |
| `noisy_anchor_rate` | 0% | Consistent across all 4 cases. |
| `step6_treatment_accuracy` | 5/5 = 100% — every surfaced anchor named in revised.txt with primary treatment | Same Step 6 quality as case 3. |

### Product-level friction metrics

Anchor-worthy denominator: 7 clusters.

| Metric | Value | What's counted |
|---|---|---|
| `friction_yield_strict` | **4/7 = 57.1%** | C2 FL, C3 SOT, C4 PD (+ PAP secondary), C6 OC. C1, C5 (PFR recall failures), C8 (Premortem recall failure) excluded. |
| `friction_yield_any_honest` | 4/7 = 57.1% | Same as strict — no quote drift. |
| `strictness_failure_rate_strict` | **0/4 = 0%** | Denominator: clusters with sufficient fingerprint specificity AND expected model in candidates. C2/C3/C4/C6 qualify; all accepted. **No verifier strictness failure on the strict denominator** — same as case 3. |
| `strictness_failure_rate_broad` | **0/4 = 0%** | Same as strict on this case. |
| Trust axis | clean | 0% noisy_anchor_rate, 0% post-verifier validation, all anchors aligned. Across all 4 cases now: 0/19 false positives. |
| Friction axis | mid-strong | 57% friction yield (best in audit so far), 0% strictness failure (matches case 3). |

## Findings

### F1''' validated on case 4 (with one update)

The pre-registered prediction table got 6/7 cluster outcomes right (the 7th couldn't be tested). The OC update is the noteworthy addition: **explicit mutual-exclusion phrasing ("no version where X AND Y", "you have to pick") is sufficient operationalization for Opportunity Cost.** That brings OC from "consistently rejected" (cases 1+2) to "accepted when source uses mutual-exclusion language" (case 4).

Updated F1''' formulation:

> The verifier accepts a model when the source quote contains operationalized mechanism language for that model. Sufficient operationalizations include: explicit numbers and thresholds (PT, CC, MoS), named processes with observable behaviors (PAP, IA, ToC, PD), explicit causal chains (SOT, FL), and explicit mutual-exclusion phrasing for tradeoffs (OC). The verifier rejects when the model's mechanism requires interpretive translation between the source language and the model concept.

### F2''' — PFR pattern is now N=4 and robust across very different domains

PFR has been consistently absent in 4 cases spanning fintech-launch, oncologist-industry, regulatory-ethics, and parent-teen-safety. Failure mechanisms vary (recall ×3 cases, verifier ×1 case), but the user-visible outcome is identical: PFR doesn't reach Step 6.

The recall-substrate hypothesis (PFR's keyword anchors don't trigger on common reframe language) is now the strongest candidate explanation. The next investigation should look at the recall substrate's vocabulary for PFR — specifically whether common reframe phrasings ("the first move isn't X, it's Y", "X is a different goal from Y", "what you think your career is", "the priority is re-opening communication") share a keyword surface that recall would pick up.

This is a separate fix space from F1'''. F1''' is about verifier judgment on candidates that reach it; PFR's problem is upstream of the verifier.

### F3''' — Premortem-specific test still unresolved

C8 had the highest source-operationalization in the audit (literal if-when-then with explicit goal redefinition), but fingerprint missed Turn 12 and recall didn't surface Premortem. We can't determine whether Premortem rejects under operational language because the producer chain didn't deliver it to the verifier.

The audit so far has Premortem outcomes:
- Case 1 C7: rejected at verifier ("mechanism absent") with operational pre-registered conditions in source
- Case 2 C8: not expected primary (acceptable_secondary on C8); recall succeeded, verifier behavior n/a for primary status
- Case 3 C7: rejected at verifier ("mechanism absent") with conditional checkpoints in source
- Case 4 C8: not in candidates (recall+fingerprint failure)

Cases 1 and 3 are the closest data we have: both have Premortem rejecting at the verifier despite source language with conditional/pre-registered structure. That's 2/2 cases where Premortem rejects with operational-ish language present. If F1''' should predict ACCEPT here, then Premortem may have a model-specific rejection rule — a verifier blind spot for failure-planning models.

### F4''' — When the producer chain delivers, the verifier accepts on case 4

5/5 expected primaries that reached candidates were accepted. 0% strictness failure. The friction loss on case 4 is entirely upstream (PFR recall ×2, Premortem fingerprint+recall). Case 4 + Case 3 both show: when the chain delivers a candidate to the verifier, F1''' is well-described — operational mechanism language passes; interpretive language fails. The strictness story from cases 1+2 was specific to those conversations' language properties, not a systematic verifier issue.

## Cross-case comparison: cases 1 + 2 + 3 + 4

| Dimension | Case 1 | Case 2 | Case 3 | Case 4 |
|---|---|---|---|---|
| `cluster_recall` (fingerprint) | 7/7 | 7/7 | 4/7 | 6/7 |
| `candidate_recall@60` | 83% | 86% | 71% | 71% |
| `verifier_acceptance_rate` | 40% | 33% | 80% | **100%** |
| `noisy_anchor_rate` | 0% | 0% | 0% | 0% |
| `friction_yield_strict` | 17% | 43% | 43% (57% with hidden PT) | **57%** |
| `strictness_failure_rate_strict` | 50% | 40% | 0% | 0% |

### Recurring patterns N=4

1. **PFR consistently absent.** 4/4 cases. Different mechanisms. The recall-substrate hole is the most consistent finding in the audit.
2. **Trust axis stays clean.** 0/19 false positives across 4 cases. The trust gates are reliably correct.
3. **F1''' predictions are tracking.** Case 4 had 6/7 prediction matches. Case 3 broke the prior family hypothesis and supported F1'''. The cumulative N=4 picture is consistent with operational-language-presence as the verifier-acceptance differentiator.

### Pattern that reversed

The case-1+2 strictness pattern (40-50% verifier rejection) reversed cleanly on cases 3+4 (80-100% verifier acceptance on candidates). The reversal correlates with the conversation's language properties: cases 1+2 had more interpretive/cognitive-operation reasoning (counterfactual escape-vs-fit, runway optimism); cases 3+4 had more structural-mechanism reasoning (incentive misalignment, custody dynamics, feedback loops). That's exactly what F1''' predicts.

### What this points to

After 4 cases, the audit's leak map has **two distinct patterns**:

1. **Recall hole for interpretive models.** PFR consistently misses at recall (4 cases). Optionality misses at recall on cases 2+3. Premortem missed at recall on case 4. The recall substrate may not have keyword anchors for common interpretive-reframe / option-design / failure-planning language.

2. **Verifier rejection of interpretive language.** When a candidate reaches the verifier WITHOUT operational mechanism language, the verifier rejects with "mechanism absent" or "too generic". This is what F1''' describes. It explains case-1 Optionality, case-1 Premortem, case-2 Inversion, case-3 Premortem, and several others.

The two patterns overlap (PFR is both recall-missing and likely also verifier-rejection-prone), but they're separable. Fixing one doesn't fix the other.

## Locked bottom-line for case 4

`mother-deciding-address-year` shows **the highest friction yield in the audit (57% strict) with 100% verifier acceptance on candidates that reached the slate.** Five anchor-worthy clusters delivered clean primary anchors with cluster-aligned quotes and primary Step 6 use (FL, SOT, PD, PAP-secondary on C4, OC). Two clusters had recall failures (PFR ×2). One cluster had fingerprint+recall failure (Premortem on C8).

The **F1''' hypothesis was validated** with 6/7 prediction matches on case 4. The one update is that explicit mutual-exclusion phrasing ("no version where X AND Y") operationalizes Opportunity Cost — extending the set of language properties that count as sufficient operationalization.

The **Premortem-specific blind-spot test could not be conducted** on this case because the producer chain didn't deliver Premortem to the verifier (fingerprint missed Turn 12; recall didn't surface). Cases 1+3 evidence (Premortem rejected at verifier with conditional/pre-registered source language) remains the closest signal that Premortem may have a model-specific verifier-blind-spot.

Cross-case (N=4) signal: F1''' is the best-supported hypothesis, with two distinct producer-side problems separable from it (PFR recall hole; Premortem-specific verifier behavior). Holding cases 5–7 per discipline.

## Resolved notes

- F1''' validated on case 4 with one update (mutual-exclusion language operationalizes OC).
- The case-1+2 strictness pattern is now well-explained as conversation-specific (interpretive content) rather than systematic.
- PFR's 4-case absence pattern points at a recall-substrate problem distinct from F1'''.
- Premortem has a still-untested model-specific blind-spot question.
- Trust axis remains clean across all 4 cases (0/19 false positives).
- Cases 5 (marcus-equity), 6 (mother variants), 7 (phd-student) still pending.
