# Step 2 attribution — `mid-level-consultant-report`

Status: **STEP 4–6 attribution** (per design memo §6.4–§6.6). Source: gold cluster table from `case_mid-level-consultant-decides_step1_source_first.md` (case 3 — same conversation as case 7) + F2 stability prediction table from `case_mid-level-consultant-report_step1_source_first.md`.

Artifacts opened:
- `result.json.audit_summary.companion_fingerprint_validated` (7 fingerprint moves)
- `result.json.audit_summary.companion_detected_models` (3 final accepted)
- `result.json.audit_summary.companion_rejected_models` (57 rejected; 51 "mechanism absent", 4 "execution_quote_not_literal_substring", 2 "too generic")
- `result.json.companion_cheat_sheet.anchors` (3 surfaced)
- `revised.txt` (Step 6 output)

Total candidate slate: 60 (57 rejected + 3 accepted).

## Pre-registered F2 stability prediction test results

Predictions locked in commit `2a05891` BEFORE Lane 2 outputs were opened. The unique value of case 7 is that it is **the same conversation as case 3** — predictions can compare directly to case 3 outcomes, testing F2's stability claim.

### Side-by-side: case 3 vs case 7 on identical source

| Cluster | Expected primary | Case 3 outcome | Case 7 outcome | F2 stability? |
|---|---|---|---|---|
| C1 | *Probabilistic Thinking* | ACCEPTED, cluster-aligned | **ACCEPTED, cluster-aligned** | ✓ stable |
| C2 | *PFR* / *Decomposition* | NOT IN CANDIDATES | **NOT IN CANDIDATES** | ✓ stable (same recall hole) |
| C3 | *Information Asymmetry* | ACCEPTED, cluster-aligned, Step-6 primary | **REJECTED at verifier** ("mechanism absent") | **✗ unstable** — same source, different verifier judgment |
| C4 | *Principal Agent Problem* | ACCEPTED (cluster-aligned, primary) + AB secondary | **PAP NOT IN CANDIDATES; PD acceptable_secondary ACCEPTED** (cluster-aligned, Step-6 primary) | partial — cluster yielded an agency-family anchor on both runs, but composition swapped (PAP→PD) |
| C5 | *Confidence Calibration* | ACCEPTED, cluster-aligned, Step-6 primary | **ACCEPTED, cluster-aligned, Step-6 primary** | ✓ stable |
| C6 | *PFR* | NOT IN CANDIDATES | **NOT IN CANDIDATES** | ✓ stable |
| C7 | *Premortem* | REJECTED ("mechanism absent") | **REJECTED ("mechanism absent")** | ✓ stable |
| C8 | `no_clean_primary` | n/a | n/a | n/a |

**Score: 5 stable predictions (C1, C2, C5, C6, C7), 1 partial (C4 swap within agency family), 1 unstable (C3 IA accept→reject), 1 recall-variance (C4 PAP recall changed).**

### Where stability held

- *PT* (C1) and *CC* (C5) accepted on both runs with cluster-aligned quotes — F2's strongest stability signal.
- *PFR* (C2 + C6) and *Premortem* (C7) failed the same way on both runs — chronic-fail patterns recurring on identical source.

### Where stability broke

- **C3 IA:** case 3 accepted it cleanly with the C3 source quote ("An internal report... likely to tip off the partner... cover story"); case 7 rejected it with "mechanism absent." Same source. Different verifier judgment. F2's "operational language → accept" prediction held on case 3 but failed on case 7.
- **C4 PAP recall:** case 3 had PAP in candidates and accepted; case 7 didn't have PAP in candidates at all (recall miss). Same source, different recall behavior.
- **C4 anchor composition:** case 3 yielded PAP (primary) + AB (secondary); case 7 yielded PD (acceptable_secondary). The cluster yields an agency-family anchor on both runs, but which family member varies stochastically.

The C4 swap is honest hypothesis diversity (similar to Marcus C6 across runs). The C3 IA swap is harder to explain — same source, same operational language, different verifier outcome.

## Gold cluster rows — case 7 specifics

I'll only show clusters where outcomes diverged from case 3 (others repeat case 3's analysis exactly).

### C3 — Information Asymmetry stability failure

| Field | Case 3 | Case 7 |
|---|---|---|
| `candidate_recall_hit` (IA) | yes | yes |
| `verifier_accepted` (IA) | **yes** | **no** — `mechanism absent` |
| `failure_owner` | none — clean primary hit | **verifier_failed** |
| `notes` | Same source, same fingerprint coverage. Different verifier judgment. F2 predicts accept under "tip off / cover story" operational language; case 3 confirms; case 7 falsifies. |

### C4 — Anchor composition swap

| Field | Case 3 | Case 7 |
|---|---|---|
| `candidate_recall_hit` (PAP) | yes | **no** (recall variance) |
| `verifier_accepted` (PAP) | yes | n/a |
| `candidate_recall_hit` (PD, acceptable_secondary) | yes (rejected on case 3) | yes |
| `verifier_accepted` (PD) | no — "mechanism absent" on case 3 | **yes** on case 7 |
| `evidence_quote_attribution` (PD on case 7) | n/a | "the conduct involves a senior partner, which means firm leadership has financial and political incentives to minimize" — Turn 5, C4-aligned |
| `step6_treatment` | PAP primary in revised.txt | PD primary in revised.txt: "The Power Dynamics read on 'senior partner with revenue weight creates institutional drag' holds" |
| `failure_owner` | none — clean primary hit | none — acceptable_secondary cluster-aligned hit |
| `classification` | acceptable_primary_match (PAP) | acceptable_secondary (PD) |
| `notes` | The cluster yields an agency-family anchor on both runs but the composition swaps. C4 has both PAP (primary) and PD (acceptable_secondary) defensible per gold; verifier picks one or the other across runs. **Honest hypothesis diversity, similar to Marcus C6.** |

## Observed-anchor rows — case 7

### Observed: *Probabilistic Thinking*

| Field | Value |
|---|---|
| `best_matching_cluster` | C1 (cluster's expected primary) |
| `evidence_quote_attribution` | C1-aligned (Turn 2 "non-zero chance" + "timing and location make any benign explanation hard to believe") |
| `classification` | **`acceptable_primary_match`** |
| `step6_visibility` | **hidden** (same as case 3 — PT's curated label not named in revised.txt; reasoning "the benign explanations got dropped too fast" preserves the probabilistic frame without the model name) |
| `failure_owner` | **step6_failed** for the user-visible curated-name surface; producer chain succeeded |
| `notes` | Cumulative finding: PT is consistently Step-6-hidden across cases 3 and 7 (same conversation). Step 6 names PAP / IA / CC / AB / PD when surfaced, but apparently not PT. This is a Step-6 pattern, not run-stochastic. |

### Observed: *Confidence Calibration*

| Field | Value |
|---|---|
| `best_matching_cluster` | C5 (cluster's expected primary) |
| `evidence_quote_attribution` | C5-aligned (Turn 5 90/70 thresholds) |
| `classification` | **`acceptable_primary_match`** |
| `step6_visibility` | named primary in revised.txt: "the 60–65% confidence number was doing too much work. That's confidence-calibration failure" |
| `failure_owner` | none |
| `notes` | F2's strongest stability prediction: identical operational language → identical acceptance + Step-6-naming across both runs of the same source. |

### Observed: *Power Dynamics*

| Field | Value |
|---|---|
| `best_matching_cluster` | C4 (cluster's `acceptable_secondary_model`; PAP was the expected primary but recall missed it on this run) |
| `evidence_quote_attribution` | "the conduct involves a senior partner, which means firm leadership has financial and political incentives to minimize" — Turn 5, C4-aligned |
| `classification` | **`acceptable_secondary`** — anchor IS one of C4's defensible models, evidence quote is from C4's source |
| `step6_visibility` | named primary in revised.txt: "The Power Dynamics read on 'senior partner with revenue weight creates institutional drag' holds — that's not anchoring bias, it's how these firms actually work" |
| `failure_owner` | none |
| `trust_check_per_marcin` | Per Marcin's strict criteria for PD: "accept only if the source quote names concrete authority, leverage, retaliation risk, partner/client hierarchy, or dependency." Quote names: "senior partner" (hierarchy), "firm leadership" (authority), "financial and political incentives" (dependency mechanism). **Trust criteria satisfied — locally mechanized, not generic overlay.** |

## Aggregate metrics

| Metric | Value | Reading vs case 3 (same source) |
|---|---|---|
| `cluster_recall` (fingerprint) | 4/7 cleanly hit | Similar to case 3 |
| `candidate_recall@60` (expected primaries) | 4/7 = 57% (PT, IA, CC, Premortem in cand; PFR ×2, PAP, no clean for C8) | **Lower than case 3 (5/7 = 71%)** — PAP recall miss is the difference |
| `verifier_acceptance_rate` (raw, on expected primaries that reached candidates) | 2/4 = **50%** | **Lower than case 3 (4/5 = 80%)** — IA verifier rejection is the difference |
| `post_verifier_validation_failure_rate` | 4/7 = **57%** (4 demotions out of 7 raw acceptances; 3 final accepts) | **Higher than case 3 (~17%)** — quote-validation more aggressive this run |
| `noisy_anchor_rate` | 0/3 = 0% | Same as case 3 |
| `step6_treatment_accuracy` | 2/3 (CC + PD named primary; PT hidden) | 4/5 case 3 (PT also hidden on case 3) |

### Product-level friction metrics

Three reporting cuts (per case 6's framing):

| Metric | Value | Denominator | Question it answers |
|---|---|---|---|
| `friction_yield_strict` (cross-case conservative) | **3/7 = 42.9%** | All 7 source-first clusters | Cross-case comparison. Lower than case 3 (4/7 = 57%, or 5/7 with AB on C4 secondary) on identical source. |
| `friction_yield_strict` on clean expected primaries | **2/5 = 40%** | 5 clusters with clean expected primary (excludes C4 which has gold ambiguity post-swap; C5/C6 = no_clean_primary or ambiguous; here C4 = ambiguous because PAP missing) — alternative reading: 1/5 = 20% if C4 is treated as expected-PAP-failed | F2 theory test. Lower than case 3's 4/5 = 80% on same denominator. |
| `friction_yield_any_honest` | **3/7 = 42.9%** | Same as strict (no quote drift) | Same. |
| `strictness_failure_rate_strict` | **1/4 = 25%** (C3 IA rejected on a cluster fingerprint covered + IA in candidates) | Clusters with sufficient fingerprint specificity AND expected model in candidates | Higher than case 3 (0/2 = 0%). |
| `strictness_failure_rate_broad` | **2/4 = 50%** (C3 IA + C7 Premortem) | All clusters where expected primary in candidates | Higher than case 3 (1/5 = 20%). |
| Trust axis | clean | | 0% noisy_anchor_rate; all 3 anchors locally mechanized per Marcin's strict criteria. |

## Findings

### F1''' / F2 stability is partial, not deterministic

The cleanest test of F2 stability would have predicted: same source → same anchors. Case 7 vs case 3 shows partial stability:
- **5 of 7 clusters had stable outcomes** (C1, C2, C5, C6, C7).
- **2 of 7 clusters had unstable outcomes** (C3 IA accepted vs rejected; C4 PAP→PD swap).

For the 2 unstable clusters:
- C3 IA: the source quote operationalizes IA's mechanism ("tip off / cover story"). F2 predicts accept consistently. Case 3 confirmed; case 7 falsified. **Same operational language, different verifier judgment.** This is the strongest evidence that F2 is probabilistic, not deterministic.
- C4 PAP→PD swap: both anchors are F2-compatible for C4 (PAP via "salaried fiduciary / book of business"; PD via "senior partner / firm leadership / political incentives"). The verifier picks one or the other across runs. This is honest hypothesis diversity within the gold ambiguity, not F2 failure.

### Run-to-run variance happens at multiple producer stages

Case 7 vs case 3 differences:
- **Recall variance**: PAP was a candidate on case 3, not on case 7. AB was a candidate on case 3, not on case 7. The recall substrate produces different candidate slates from identical source.
- **Verifier judgment variance**: IA accepted on case 3, rejected on case 7. Same source, same operational language, different judgment.
- **Quote-validation variance**: case 7 has 4 demotions (57% rate); case 3 had 1 (~17%). Same source.

The producer chain is stochastic at every stage. Trust axis is the only consistently stable property.

### Trust axis stays clean across N=7

0/29 false positives across 7 cases. All 3 case-7 anchors satisfied Marcin's strict criteria for not being noisy-adjacent:
- PT quote has explicit probability language ("non-zero chance")
- CC quote has explicit confidence thresholds ("90%+", "70% or below")
- PD quote names concrete hierarchy + authority + dependency mechanism

Even with stochastic recall + verifier behavior, when an anchor surfaces, it surfaces honestly. The trust gates are doing their work.

### PT remains Step-6-hidden across both runs

A non-stochastic Step-6 pattern: PT is in the cheat sheet on both runs but Step 6 doesn't name it in revised.txt either time. The probabilistic reasoning is preserved without the model name. This is a Step 6 consumption pattern, not run-stochastic.

### Friction yield varies significantly across runs of the same conversation

Same conversation:
- Case 3: 4/5 = 80% friction yield on clean expected primaries
- Case 7: 2/5 = 40% friction yield on clean expected primaries

That's a substantial product-level instability. A user re-running the same conversation gets meaningfully different curated pressure.

This is a stability problem the audit hadn't fully named before. The cumulative leak modes (recall vocabulary, quote validation, OC-specific verifier) all contribute, but case 7 vs case 3 shows the *combined* effect on the user-visible product is run-stochastic in a way that affects friction yield directly.

## Cross-case final summary (N=7)

| Dimension | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| Total candidate slate | 60 | 60 | 60 | 56 | **13** | 59 | 60 |
| `verifier_acceptance_rate` | 40% | 33% | 80% | 100% | 20% | 100% | 50% |
| `post_verifier_validation_failure_rate` | 50% | 0% | 0% | 0% | 67% | 0% | 57% |
| `noisy_anchor_rate` | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| `friction_yield_strict` (cross-case conservative) | 17% | 43% | 43% | 57% | 14% | 57% | 43% |
| `strictness_failure_rate_strict` | 50% | 40% | 0% | 0% | 75% | 0% | 25% |

### Cumulative trust axis: 0/29 false positives across 7 cases

The most robust finding in the audit. Across very different conversation domains (fintech, oncology, regulatory ethics, parent-teen safety, founder equity, academic dissertation, and a stability re-run), the trust gates have not produced a single false positive. This is the audit's strongest product confidence signal.

### F2 cumulative N=7

F2 has predictive power for verifier acceptance but is not deterministic. Across cases:
- **Strong support**: cases 2, 3, 4, 6 — operational language predicted acceptance well across many clusters.
- **Counter-evidence**: case 5 Marcus C5 OC (explicit operational language, rejected); case 7 C3 IA (same operational language as case 3 where it accepted, rejected here).
- **Stability note**: F2 holds direction-of-acceptance per cluster shape but exact composition is stochastic, especially in clusters with multiple defensible models (C4 agency family, Marcus C6 founder bias).

### Producer-chain leak modes (N=7)

Cumulative diagnosis:
1. **Recall vocabulary gaps** — Marcus most clearly (13/60); also case 7 PAP recall miss on identical source as case 3.
2. **Quote-validation strictness** — case 1, Marcus, case 7 (57% rate). Variable across runs.
3. **Verifier interpretive rejection** — Marcus C5 OC, case 7 C3 IA. F2 doesn't fully predict.
4. **Run-to-run variance at all producer stages** — cases 3 vs 7 show recall, verifier, and quote-validation all vary on identical source.
5. **Cluster-aligned but stochastic anchor identity** — Marcus C6 (4 defensible primaries), case 7 C4 (PAP↔PD swap).

These five modes are cumulative findings across the audit. F2 explains pattern 3 partially. Patterns 4 and 5 are run-stochasticity the audit hasn't fully separated from F2.

## Locked bottom-line for case 7

`mid-level-consultant-report` is the **same conversation as case 3 (mid-level-consultant-decides)**, archived as a separate run that produced a different anchor set. This makes case 7 a run-to-run stability test on identical source — the sharpest available F2 stability test in the audit.

**F2 stability holds for 5 of 7 clusters** (PT, PFR×2, CC, Premortem stable across runs). **F2 stability fails for 1 cluster** (C3 IA accepted on case 3, rejected on case 7 with same operational language). **F2 stability is mixed for 1 cluster** (C4 PAP↔PD swap within the agency family, both defensible per gold).

**Run-to-run variance happens at every producer stage**: recall (PAP missing on case 7), verifier judgment (IA rejected on case 7), quote validation (57% demotion rate vs case 3's 17%).

**Trust axis stays clean across all 7 cases**: 0/29 false positives. The trust gates are the most stable property in the producer chain.

**Friction yield varies significantly across runs of the same conversation**: case 3's 4/5 = 80% on clean expected primaries vs case 7's 2/5 = 40%. A product-level instability the audit hadn't directly named before this case.

The audit closes (per Marcin's pre-registered framing for case 7) with the more cautious of his two end-states:

> **"Lane 2 is high-trust, but generic career conversations still risk plausible-overlay anchors."**

Wait — actually all three case-7 anchors passed strict criteria, so noisy-adjacent didn't materialize. The right end-state is closer to:

> **"Lane 2 is high-trust but uneven-friction; F2 explains most yield variance but run-stochasticity adds a layer F2 doesn't fully model. Same source can yield 40% or 80% friction across runs."**

That's the audit's final picture at N=7.

## Resolved notes

- F2 partially supported, not deterministic. Run-stochasticity is a separate effect F2 doesn't fully model.
- Trust axis clean across all 7 cases — 0/29 false positives. Strongest finding.
- Producer chain has 5 cumulative leak modes (recall vocabulary, quote validation, verifier interpretive rejection, run-stochasticity at all stages, anchor identity stochasticity within clusters).
- Step 6 has independent enrichment patterns (introduces models not in cheat sheet on cases 5+7) and stable hidden patterns (PT consistently Step-6-hidden on cases 3+7).
- Case 7 was the final pre-registered case in the audit corpus. The audit corpus is now complete.

## Audit corpus complete (N=7)

All 7 pre-registered cases from the design memo §4 have been audited:
- ✓ failure-rich (3): mid-level-consultant-decides, mother-deciding-address-year, marcus-equity
- ✓ candidate positive controls (2): third-year-phd-student, user-launch-independent-fintech
- ✓ false-positive risk controls (2): year-old-oncologist-accept, mid-level-consultant-report

Per the design memo §13, the next track is reading the leak map and applying the §9 decision tree to pick the next architectural work. That's a separate deliverable from this audit — the audit's product is the leak map across 7 cases, not architecture proposals.
