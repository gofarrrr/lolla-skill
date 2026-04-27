# Step 2 attribution — `marcus-equity`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: locked gold cluster table + F1''' prediction table from `case_marcus-equity_step1_source_first.md`.

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (6 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (2 final accepted)
- `result.json.audit_summary.companion_rejected_models` (11 rejected; 5 "mechanism absent", 4 "execution_quote_not_literal_substring", 2 "too generic")
- `result.json.companion_cheat_sheet.anchors` (2 surfaced)
- `revised.txt` (Step 6 output)

**Total candidate slate: 13 (11 rejected + 2 accepted).** Cap is 60. Marcus's slate is 78% under cap — recall is severely truncated relative to all prior cases.

## Pre-registered F1''' prediction test results

Predictions locked in commit `8284556` BEFORE Lane 2 outputs were opened.

| Cluster | Expected primary | Op level | Predicted | Actual | Match? |
|---|---|---|---|---|---|
| C1 | *Problem Framing And Reframing* | medium | recall-risk | **REJECTED at verifier** ("mechanism absent") | ✗ — PFR DID reach candidates here, then verifier rejected. New PFR failure mode for the audit. |
| C2 | *PFR* OR *Decomposition* (ambiguous) | medium | recall-risk PFR; possibly accept Decomposition | PFR rejected at verifier; Decomposition NOT IN CANDIDATES | partial |
| C3 | *Second Order Thinking* | high | accept (per F1''' high-op chain) | **REJECTED with "too generic"** | ✗ — F1''' fails for SOT here despite operational chain |
| C4 | *Representativeness Heuristic* | high | accept | **ACCEPTED**, cluster-aligned quote | ✓ |
| C5 | *Opportunity Cost* | high (numbers + mutual exclusion) | accept (per case-4 update) | **REJECTED with "mechanism absent"** | ✗ — **falsifies the case-4 F1''' OC update.** Highest source operationalization in the audit, still rejected. |
| C6 | AMBIGUOUS (SCF / Endowment / Inversion / PFR) | medium-high | accept some primary in defensible range | **Sunk Cost Fallacy ACCEPTED** (within defensible range) | ✓ partial — anchor in defensible range BUT evidence quote drifts to C1 territory |
| C7 | *PFR* OR `no_clean_primary` (ambiguous) | medium | recall-risk if PFR | PFR rejected at verifier; no clean C7 anchor surfaced | partial |

**Score: 1 clean match (C4), 1 partial match (C6 with quote drift), 2 partial mismatches (C2 + C7), 3 outright misses (C1, C3, C5).**

The C5 miss is the most consequential. F1''' was updated on case 4 to include explicit mutual-exclusion phrasing as sufficient OC operationalization. Marcus C5 has the highest operationalization in the audit — explicit dollar math AND explicit mutual-exclusion ("$1.3-2M to protect $6M of value") AND comparison-of-paths reasoning. Verifier rejected with "mechanism absent." That falsifies F1''' as a sufficient predictor for OC.

## Marcus has a different failure shape than cases 1–4

Three things make Marcus distinct:

### Truncated recall slate
13 candidates vs 60 cap (78% under). Cases 1–4 all hit or approached the 60-candidate cap. Marcus's recall is producing far fewer candidates, which means the verifier sees a smaller and possibly more lexically-homogeneous slate. Possible mechanisms: keyword overlap with assistant text is narrower (equity-specific vocabulary doesn't match many of the 222 model display names); embeddings substrate is also coming up empty for this conversation.

### Aggressive post-verifier validation
4 of 6 raw verifier acceptances were demoted by the literal-substring quote gate (`execution_quote_not_literal_substring`). The demoted models: *Endowment Effect*, *Inversion*, *Optionality*, and one other. **`post_verifier_validation_failure_rate` = 4/6 = 67%** — the highest in the audit.

This means the verifier accepted 6 of 13 candidates (46% raw acceptance rate, similar to other cases), but the quote gate dropped 4 of those. If the demoted models had survived, friction yield would be substantially higher. The gate is doing real work protecting against verifier paraphrase, but it's dropping models that match cluster reasoning.

Notably: **Endowment Effect** was raw-accepted by the verifier and demoted by the quote gate. *Endowment Effect* is one of the four defensible primaries I flagged for C6's gold ambiguity. It would have been a clean cluster-aligned anchor. The quote gate dropping it is a productive friction loss — the verifier saw the model executed in the founder-bias reasoning, but the verifier's evidence quote wasn't a literal substring.

### Selective verifier strictness on operational language
C5 OC was rejected with "mechanism absent" despite the audit's clearest operational-language source quote. That's a clean F1''' counter-example. Two possibilities:

1. **F1''' is necessary but not sufficient.** Operational language increases acceptance probability but doesn't guarantee it. The verifier's rubric has additional constraints not yet identified.
2. **The verifier reads broader context, not just the operational quote.** Recall surfaces OC into candidates via lexical overlap somewhere in the conversation; the verifier judges OC against the full assistant text and finds it too interpretive even though the C5 quote is operationalized. This is consistent with the case-3 observation that the verifier reads beyond fingerprint moves.

Either way, F1''' weakens for Marcus. The case 4 update on OC (mutual-exclusion sufficient) doesn't survive Marcus C5 — needs further refinement.

## Gold cluster rows

### C1 — Subsidy reframe

| Field | Value |
|---|---|
| `expected_primary_models` | *Problem Framing And Reframing* |
| `fingerprint_found_cluster` | no (no fingerprint move quotes Turn 1's subsidy framing directly) |
| `candidate_recall_hit` (PFR) | yes (in candidates) |
| `verifier_accepted` (PFR) | **no** — `mechanism absent` |
| `failure_owner` | **verifier_failed** |
| `notes` | New PFR failure mode for the audit. Cases 1+3+4 had PFR fail at recall (3 cases). Case 2 had PFR fail at verifier (1 case). Case 5 has PFR also failing at verifier. So PFR's pattern is: recall-failed 3/5 cases, verifier-rejected 2/5 cases. The user-visible outcome is the same (PFR consistently absent from Step 6); the failure mechanism varies. |

### C2 — Equity + platform tangled

| Field | Value |
|---|---|
| `expected_primary_models` | *PFR* OR *Decomposition* (ambiguous) |
| `fingerprint_found_cluster` | partial (M6 covers the partner-vs-employee reframe) |
| `candidate_recall_hit` (PFR) | yes (rejected at verifier with "mechanism absent") |
| `candidate_recall_hit` (Decomposition) | **no** |
| `failure_owner` | **verifier_failed** for PFR primary; **recall_failed** for Decomposition secondary |
| `notes` | Decomposition's recall failure here is interesting. Decomposition was accepted on case 2 C1 with the literal three-way separation. On case 5 C2, the move IS decomposition-flavored ("two problems tangled, untangle") but Decomposition didn't reach candidates. Possible reason: case 2's quote literally said "career question / family question / financial question" (explicit three-part list), while case 5's quote said "two problems tangled together and you need to untangle them" (decomposition concept without a literal list). Recall may anchor on the literal list structure. |

### C3 — Departure as competitive threat

| Field | Value |
|---|---|
| `expected_primary_models` | *Second Order Thinking* |
| `fingerprint_found_cluster` | yes (M1 covers Turn 4's exit-math chain; M2 partially covers Tom comparison's downstream) |
| `candidate_recall_hit` (SOT) | yes (rejected with "too generic") |
| `failure_owner` | **verifier_failed** with `too generic` rejection reason |
| `notes` | F1''' counter-example. The source has explicit causal chain ("Marcus leaves → Jake/Lina follow → competitive threat" + the full Turn 4 chain "EBITDA drops → multiple drops → $11M to $5M"). High operational language. SOT rejected as "too generic." Same pattern as case 3 (SOT rejected as "too generic" when not the cluster-primary anchor of a small specific quote). On case 4, SOT was accepted as cluster-primary on a single specific quote ("blocking drives communication underground"). The verifier may apply "too generic" when SOT is being evaluated against a multi-step extended chain, but accept when the quote is a single specific consequence statement. |

### C4 — Tom wrong reference class

| Field | Value |
|---|---|
| `expected_primary_models` | *Representativeness Heuristic* |
| `fingerprint_found_cluster` | yes (M2 quotes Tom comparison directly) |
| `candidate_recall_hit` (RH) | yes |
| `verifier_accepted` (RH) | **yes** |
| `evidence_quote_attribution` | "The Tom situation. You're using Tom as a data point, but it's the wrong comparison. Tom was a senior designer. Marcus is your head of engineering who built your core infrastructure, has six years of institutional knowledge, and would take your two best engineers with him. The Tom..." — exactly C4's source quote. |
| `step6_treatment` | named in revised.txt §"What I'd set aside" — "The Representativeness Heuristic finding is real but I'm setting aside the sub-agent's suggestion to heavily caveat the equity direction." Treatment is "set aside with a reason" per PR #41 contract — anchor named, used honestly, not load-bearing primary. |
| `failure_owner` | **none — CLEAN PRIMARY HIT.** |
| `notes` | This is the high-confidence F1''' prediction that survives. Operationalization is high (named bias + explicit "wrong comparison" + analogy "flat tire vs car accident"). Accepted, surfaced, named in Step 6. |

### C5 — Exit math opportunity cost

| Field | Value |
|---|---|
| `expected_primary_models` | *Opportunity Cost* |
| `fingerprint_found_cluster` | yes (M1 quotes Turn 4 exit-math chain extensively) |
| `candidate_recall_hit` (OC) | yes |
| `verifier_accepted` (OC) | **no** — `mechanism absent` |
| `failure_owner` | **verifier_failed** |
| `notes` | **Clean F1''' counter-example.** Source has the highest operational language in the audit: "$11M exit", "$5M exit", "$6M difference", "$1.3-2M dilution", explicit mutual-exclusion ("you're worried about giving away X to protect Y"), comparison-of-paths reasoning. Verifier rejected with "mechanism absent." Falsifies the case-4 F1''' update that mutual-exclusion language operationalizes OC sufficiently. The "interpretive translation" required to recognize OC's mechanism is apparently still too much for the verifier even with this language. F1''' needs further refinement — operational language is necessary but not sufficient. |
| `secondary check` (Inversion) | in candidates, **demoted by quote gate** (`execution_quote_not_literal_substring`). Raw-accepted by verifier; quote not literal substring. |

### C6 — Founder "I built this" emotional bias [GOLD AMBIGUITY]

| Field | Value |
|---|---|
| `expected_primary_models` | gold_ambiguity_note: *Sunk Cost Fallacy* / *Endowment Effect* / *Inversion* / *PFR* all defensible |
| `fingerprint_found_cluster` | no (M1 covers Turn 4's exit-math but not the founder-bias content; the "two contradictory calculations" call-out is not in any move's evidence quote) |
| `candidate_recall_hit` (Sunk Cost Fallacy) | yes |
| `verifier_accepted` (SCF) | **yes** |
| `evidence_quote_attribution` | "you say you took all the early risk. That's true, and it matters. But Marcus has been there since year two out of eight. He's been accumulating risk too — career opportunity cost, building institutional knowledge that's only valuable here, becoming the guy your clients trust." — Turn 1. **Quote drifts:** the SCF model concept maps to C6's founder-bias reasoning, but the literal evidence quote is from Turn 1's reciprocal-risk argument, not from Turn 4's "I built this / shared territory" content where the founder bias is most explicit. |
| `step6_treatment` | named in revised.txt §"What I'd set aside" — "The Sunk Cost Fallacy analysis... was right in direction but I applied it recklessly in one specific place." Treatment is "set aside with reason" per PR #41 contract. |
| `failure_owner` | **none — anchor IS within the defensible C6 range; quote drift acknowledged in classification.** |
| `secondary check` (Endowment Effect) | in candidates, **demoted by quote gate**. Raw-accepted by verifier — meaning the verifier identified Endowment Effect as executed somewhere in this conversation. EE is one of the defensible C6 primaries. The quote gate dropped a cluster-aligned anchor. |
| `notes` | **The C6 ambiguity-discipline call holds.** Lane 2's SCF anchor is one of the four defensible primaries I flagged. The quote gate also dropped EE (another defensible primary). If both SCF and EE had survived validation, C6 would have two cluster-aligned anchors. As-is, C6 yields one anchor with quote drift. Per Marcin's branch: this is the "honest hypothesis diversity" signal — different defensible reads can land cluster-aligned across runs. The cross-run instability (Accepted-pre 0.13) is consistent with this; on different runs, the verifier may pick SCF, EE, Inversion, or PFR for the same C6 reasoning. |

### C7 — Pattern of avoiding the question

| Field | Value |
|---|---|
| `expected_primary_models` | *PFR* OR `no_clean_primary` (ambiguous) |
| `fingerprint_found_cluster` | yes (M3 covers the cash-alternative dismissals) |
| `candidate_recall_hit` (PFR) | yes (rejected at verifier with "mechanism absent") |
| `failure_owner` | **verifier_failed** for PFR; if `no_clean_primary` is the right read, no failure |
| `notes` | Same PFR pattern as C1 / C2. Cluster yielded no anchor. If the right gold call is `no_clean_primary`, this is correct behavior. If PFR was the right call, it's a verifier failure. The ambiguity discipline doesn't resolve this from this run alone. |

## Observed-anchor rows

### Observed: *Sunk Cost Fallacy*

| Field | Value |
|---|---|
| `best_matching_cluster` | C6 (one of the four defensible primaries in the gold ambiguity) |
| `evidence_quote_attribution` | Turn 1 quote (reciprocal-risk argument). C6's load-bearing source is Turn 4's "I built this / shared territory" content. Quote drifts. |
| `classification` | **`acceptable_primary_match_with_quote_drift`** — anchor IS in the C6 defensible range; quote sources from C1 territory (Turn 1) rather than C6's load-bearing Turn 4 content. |
| `step6_visibility` | named in revised.txt as "Sunk Cost Fallacy analysis", treatment = `set_aside_with_reason`. |
| `failure_owner` | none. |

### Observed: *Representativeness Heuristic*

| Field | Value |
|---|---|
| `best_matching_cluster` | C4 (cluster's expected primary) |
| `evidence_quote_attribution` | C4-aligned. |
| `classification` | **`acceptable_primary_match`** — clean. |
| `step6_visibility` | named in revised.txt as "Representativeness Heuristic finding", treatment = `set_aside_with_reason`. |
| `failure_owner` | none. |

## Aggregate metrics

| Metric | Value | Reading |
|---|---|---|
| `cluster_recall` (fingerprint) | 4-5/7 anchor-worthy clusters cleanly hit (C3, C4, C5, C7; C2 partial; C1 + C6 missed by fingerprint) | Lower than cases 1, 2, 4. Marcus has fingerprint coverage gaps. |
| `candidate_recall@60` (across all 222 models reaching the 60-cap candidate slate) | **13/60 cap** — slate severely truncated | Recall substrate is producing far fewer candidates on Marcus than on other cases. |
| `candidate_recall@60` (expected primaries that reached candidates) | 5/7 expected primaries reached candidates (PFR ×2, SOT, RH, OC; Decomposition not in cand for C2, fingerprint missed C1 + C6) | Despite truncated slate, expected primaries are mostly present. |
| `verifier_acceptance_rate` (raw verifier judgment on expected primaries) | 1/5 = 20% (only RH; PFR ×2, SOT, OC all rejected at verifier) | **Lowest in audit.** |
| `verifier_acceptance_rate` (raw verifier judgment on all candidates) | 6/13 = 46% (2 final + 4 demoted) | Moderate; consistent with cases 1, 2. |
| **`post_verifier_validation_failure_rate`** | **4/6 = 67%** | **Highest in audit.** Quote gate dropped 4 of 6 raw acceptances, including *Endowment Effect* (defensible C6 primary). |
| Final validated acceptance | 2/13 = 15% (SCF + RH) | Lowest in audit. |
| `noisy_anchor_rate` | 0/2 = 0% — both surfaced anchors map to defensible cluster positions, with one quote drift on SCF | Trust axis still clean. |
| `step6_treatment_accuracy` | 2/2 — both anchors named, treatment = set_aside_with_reason per PR #41 | Step 6 consumes anchors correctly even though it doesn't use them as primary pressure. |

### Product-level friction metrics

Anchor-worthy denominator: 7 (or 6 if C7 read as no_clean_primary). I'll report 7 with a parenthetical for 6.

| Metric | Value | What's counted |
|---|---|---|
| `friction_yield_strict` (cluster-aligned + quote-aligned) | **1/7 = 14.3%** (C4 only) | C4 RH only. SCF on C6 has quote drift — excluded from strict. |
| `friction_yield_any_honest` (allows quote drift) | **2/7 = 28.6%** (C4 + C6) | Adds C6 SCF with quote drift. |
| `strictness_failure_rate_strict` (fingerprint specific + model in candidates → verifier rejected) | **3/4 = 75%** | C3 SOT rejected (too generic); C5 OC rejected (mechanism absent); C7 PFR rejected (mechanism absent). C4 is the only strict-denominator cluster that yielded. |
| `strictness_failure_rate_broad` | 4/5 = 80% (adds C2 with partial fingerprint) | |
| Trust axis | clean | 0% noisy_anchor_rate; 1 quote drift on SCF (productive flag, not failure). |
| Friction axis | **weakest in audit** | 14% strict yield, 75% strictness failure. |

## Findings

### F1''' partially falsified by Marcus C5

The case-4 update (mutual-exclusion phrasing operationalizes OC) does NOT survive Marcus C5. The C5 source has the highest operational language in the audit — explicit dollar math, mutual-exclusion phrasing, comparison-of-paths reasoning. Verifier rejected OC with "mechanism absent."

F1''' is now: **operational language is correlated with verifier acceptance but not sufficient.** Other factors matter — possibly conversation-level lexical density, candidate slate size, or model-specific verifier rules. The hypothesis weakens but isn't fully falsified — RH on C4 is still a clean F1''' confirmation.

The cumulative N=5 picture for F1''':
- Strong support: cases 2, 3, 4 (where operational language predicted acceptance correctly across many clusters)
- Counter-evidence: case 5 C5 (explicit operational language; rejected anyway)
- Partial counter: case 5 C3 SOT (explicit chain; rejected as "too generic")

### Marcus failure shape: recall truncation + quote-validation aggression

Marcus has two distinctive failure modes that don't recur on cases 1-4:

1. **Recall truncation.** 13/60 candidate slate. Whatever the recall substrate is doing on this conversation, it's producing far fewer candidates. This may be a vocabulary / keyword-overlap issue specific to equity/founder-dynamics conversations — the language of the source may not match the 222 model display names well.
2. **Quote-validation aggression.** 67% of raw verifier acceptances were demoted by the literal-substring quote gate. This includes Endowment Effect, which is one of the four defensible C6 primaries. The gate is correctly protecting against hallucinated evidence, but it's also dropping models the verifier accepted with paraphrased quotes that match the cluster's reasoning.

If Marcus is representative of equity/founder conversations, the producer-side fix would be:
- Better recall vocabulary for ownership/equity reasoning
- Verifier prompt asking for verbatim substrings (or fuzzy quote repair before quote-validation demotion)

### C6 ambiguity discipline holds

The pre-registered hypothesis was: Marcus C6 has genuine source-level ambiguity, and Lane 2 will pick *some* defensible primary. Result: SCF accepted (one of four defensible primaries) + EE raw-accepted-then-demoted (another defensible primary). **Two of four defensible primaries surfaced for C6** — the verifier IS finding the ambiguity-cluster reasoning, just at a slightly different evidence quote (SCF on Turn 1 instead of Turn 4) and the second one (EE) was lost to quote validation.

This supports Marcin's branch: **Marcus's low cross-run stability (Accepted-pre 0.13) is most plausibly explained as honest hypothesis diversity** — different runs picking different defensible C6 primaries. Not producer-chain failure.

### Step 6 behavior is interesting on Marcus

revised.txt names both anchors with treatment = `set_aside_with_reason` (PR #41 valid treatment). It also introduces a model NOT surfaced by Lane 2 ("Deprival-Superreaction") and applies it to critique the assistant's own exit-math reasoning. Step 6 is doing some independent enrichment beyond the curated friction.

This is informative for the audit's product question: the user-visible Step 6 has 3 mental-model concepts at play (SCF, RH, plus the introduced Deprival-Superreaction), with 2 from Lane 2 and 1 from Step 6's own reasoning. The friction Lane 2 imported is meaningful but not the whole curated-friction surface.

## Cross-case comparison: cases 1 + 2 + 3 + 4 + 5

| Dimension | Case 1 | Case 2 | Case 3 | Case 4 | Case 5 (Marcus) |
|---|---|---|---|---|---|
| Total candidate slate | 60 | 60 | 60 | 56 | **13** |
| `cluster_recall` (fingerprint) | 7/7 | 7/7 | 4/7 | 6/7 | 4-5/7 |
| `candidate_recall@60` (expected primaries) | 83% | 86% | 71% | 71% | 71% |
| `verifier_acceptance_rate` (on expected primaries) | 40% | 33% | 80% | 100% | **20%** |
| `post_verifier_validation_failure_rate` | 50% | 0% | 0% | 0% | **67%** |
| `noisy_anchor_rate` | 0% | 0% | 0% | 0% | 0% |
| `friction_yield_strict` | 17% | 43% | 43% | 57% | **14%** |
| `strictness_failure_rate_strict` | 50% | 40% | 0% | 0% | **75%** |

### Recurring patterns N=5

1. **PFR consistently absent** (5/5 cases now). Different mechanisms continue: recall on cases 1, 3, 4 (×2); verifier on cases 2, 5 (×3 across C1, C2, C7).
2. **Trust axis stays clean.** 0/21 false positives across 5 cases.
3. **F1''' is partially supported, partially falsified.** Hypothesis evolution needed: operational language is correlated with acceptance but not sufficient. Other factors (slate size, model-specific verifier rules, conversation vocabulary) matter.

### Marcus is a different failure shape — but the leak modes were already known

Cases 1-4 had verifier or step6 issues with full candidate slates. Marcus has recall truncation + post-validation aggression. The producer chain has at least three independent leak modes that the audit has surfaced cumulatively (none discovered freshly on Marcus, but Marcus makes one of them dominant):

1. **Recall vocabulary gaps**: some conversation domains produce thin candidate slates. Equity/founder-dynamics is the first such domain in the audit. The recall-substrate hole was already known via the PFR pattern across cases 1-4; Marcus's broader thin-slate behavior extends the same kind of finding.
2. **Quote-validation strictness**: existed already in case 1 (Base Rates demoted on C2). Marcus makes it dominant — 67% of raw acceptances dropped vs case 1's 50% on a much smaller numerator.
3. **Verifier interpretive rejection**: cases 1+5 OC, cases 1+3 Premortem, PFR across all 5 cases. F1''' (now F2) describes this.

The Marcus-distinctive *combination* — not the individual modes — is:

- Thin slate (13 candidates, not the usual 56–60)
- Very high post-verifier demotion (67%)
- Verifier rejection even on highly operational source language (C5 OC, C3 SOT)
- Genuine ambiguity around C6 that makes low cross-run stability partly *honest hypothesis diversity*, not merely broken producer

That combination is what makes Marcus a different audit case, not the individual leak modes themselves. The product diagnosis becomes: **Marcus is not "Lane 2 unstable." Marcus is "thin recall + quote-gate loss + model-family verifier strictness + honest hypothesis diversity."** That richer diagnosis is the productive output of case 5.

## Locked bottom-line for case 5

`marcus-equity` shows **the weakest friction yield in the audit (14% strict, 29% with quote drift) and the most distinctive failure shape**: severely truncated recall (13/60), aggressive post-verifier validation drops (67% of raw acceptances), and selective verifier strictness on operational language (C5 OC rejected despite explicit numbers + mutual exclusion).

The C6 ambiguity-discipline pre-registration held: SCF accepted within the defensible primaries range, with quote drift; EE raw-accepted-then-demoted (also defensible). Marcus's low cross-run stability is most plausibly **honest hypothesis diversity** rather than producer-chain failure.

Trust axis stays clean (0 false positives, 0 noisy_adjacent classifications across all 5 cases). The product-side question on Marcus is: **the producer chain is producing too little curated friction** (only 2 anchors with set_aside Step 6 treatment) on a conversation that contains substantial structural reasoning Lane 2 could legitimately import.

Per Marcin's pre-registered branches, Marcus shows **the first branch most strongly** (low friction yield from recall/fingerprint churn + verifier strictness + post-validation drops), with a secondary signal from **the second branch** (C6 ambiguity is genuine; honest hypothesis diversity explains cross-run instability).

The implications for next-track architecture work:
- Recall substrate work for equity/founder-dynamics vocabulary
- Quote-validation flexibility (fuzzy quote repair before demotion, OR verifier prompt asking for verbatim substrings)
- F1''' refinement — operational language is necessary but not sufficient

Holding cases 6 (third-year-phd-student) and 7 (mid-level-consultant-report) per Marcin's order.

## Resolved notes

- F1''' partially falsified at Marcus C5 (OC with explicit mutual-exclusion + numbers, rejected anyway). Hypothesis still has predictive power but is not deterministic.
- Marcus's failure shape is distinct from cases 1-4: recall truncation + quote-validation aggression dominate.
- C6 ambiguity discipline held — SCF + EE both surfaced as defensible C6 primaries (one final, one demoted).
- Trust axis clean across all 5 cases.
- Cases 6, 7 still pending per Marcin's pre-registered slate order.
