# Source-first cluster labeling — `mid-level-consultant-report`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this case.

Case: `mid-level-consultant-report`
Run timestamp: `20260424T124651Z`
Original bucket hypothesis: false-positive risk control (per design memo §4)

## Discovery: case 7 is the same conversation as case 3

Reading `conversation.txt` Turn-by-Turn: the user messages and assistant responses on `mid-level-consultant-report` are **byte-identical** to `mid-level-consultant-decides` (case 3). Same Turn 1 user kickoff, same assistant Turn 1 ("Before giving any recommendation…"), continuing through all 14 turns.

Case 7 is therefore a **run-to-run stability test on the same source**, not a different conversation. The design memo's "false-positive risk control" framing turns out to be a stability test framing in disguise — the cases were said to be "same kickoff family, different conversation," but they're actually the same conversation with two archived runs that produced different anchor sets:

- Case 3 (`mid-level-consultant-decides`): 5 anchors — Authority Bias, Information Asymmetry, Principal Agent Problem, Probabilistic Thinking, Confidence Calibration.
- Case 7 (`mid-level-consultant-report`): 3 anchors — Power Dynamics, Probabilistic Thinking, Confidence Calibration.

This makes case 7 a sharper test than originally planned. F2 predicts **stability** — if a source quote operationalizes a model's mechanism, the verifier should accept that model consistently across runs. Different anchors on identical source = run-to-run variance F2 doesn't directly explain.

## Reusing case 3's gold cluster table

The gold cluster table from `case_mid-level-consultant-decides_step1_source_first.md` applies directly to case 7. The 8 clusters are:

- C1 — Probabilistic obstruction read (*Probabilistic Thinking* primary, *Confidence Calibration* secondary)
- C2 — Three-dimensional decomposition (*Problem Framing And Reframing* primary, *Decomposition* secondary)
- C3 — External preserves information asymmetry (*Information Asymmetry* primary, *Second Order Thinking* + *Premortem* secondary)
- C4 — Principal-Agent on GC (*Principal Agent Problem* primary; *Authority Bias*, *Information Asymmetry*, *Power Dynamics* secondary)
- C5 — 90/70 pre-registered threshold (*Confidence Calibration* primary, *Probabilistic Thinking* secondary)
- C6 — Career reframe (*Problem Framing And Reframing* primary, *Optionality* secondary)
- C7 — Premortem on future self-doubt (*Premortem* primary, *Confidence Calibration* secondary)
- C8 — Refuse other-person responsibility (`no_clean_primary`, *Boundaries* potential secondary)

Per the source-first discipline, the gold cluster table is fixed. The audit question on case 7 is whether the same gold predicts the same Lane 2 behavior under run-to-run stochasticity.

## F2 stress test: three Marcin-pre-registered test goals applied to a stability case

### Test 1 — Generic-career-anchor risk

Case 7's anchor set has **Power Dynamics, Probabilistic Thinking, Confidence Calibration** — these can be honest under F2 (PT/CC accepted on case 3 with explicit operational language; PD accepted on case 4 with explicit power mechanism), or they can be generic "any career decision" overlays.

Strict criteria per Marcin:
- *Power Dynamics*: accept only if source quote names concrete authority, leverage, retaliation risk, partner/client hierarchy, or dependency. Otherwise noisy-adjacent risk.
- *Probabilistic Thinking*: accept only if source uses explicit uncertainty/probability/range/scenario-weighting language. Generic "maybe this could happen" should not count.
- *Confidence Calibration*: accept only if source contrasts confidence level with evidence quality, threshold, or uncertainty. Generic "be less sure" should not count.

For this conversation, all three have specific cluster homes with explicit mechanism language:
- PD on C4: "senior partner who likely has significant revenue and political weight" — concrete authority/leverage. PD-compatible.
- PT on C1: "less than 1 in 5", "non-zero chance" — explicit probability language.
- CC on C5: "90%+", "70% or below", "60-65%" — explicit confidence thresholds.

So if Lane 2's case-7 anchors land cluster-aligned (PD on C4, PT on C1, CC on C5), they pass the strict criteria. If they drift to other turns or generic conversation overlay, they fail.

### Test 2 — F2 under run-to-run variance

F2 predicts the verifier accepts when source operationalizes mechanism. Case 3 already established that for IA, PAP, PT, CC, AB on this exact conversation. Case 7's identical source should predict identical F2 outcomes.

The case 7 actual deltas from case 3:
- IA: case 3 ACCEPTED → case 7 will it accept again?
- PAP: case 3 ACCEPTED → case 7 will it accept again?
- AB: case 3 ACCEPTED (violated mode) → case 7 will it accept again?
- PD: case 3 NOT IN CANDIDATES → case 7 surfaces (so PD's recall changed run-to-run)

That last one is interesting — PD reached candidates on case 7 but not on case 3, on identical source. That's recall-side stochasticity. F2 doesn't address recall variance.

### Test 3 — Trust axis stress

Cumulative N=6 trust: 0/23 false positives. Case 7 with its more-generic-feeling anchor set (PD + PT + CC) is a good final stress test. If any of the three anchors are noisy-adjacent or generic-overlay rather than locally mechanized, this is where I'd expect them.

## Pre-registered predictions for case 7 (run-stability + sharpened F2)

| Cluster | Expected primary | Case 3 actual | Case 7 prediction (per F2 stability + Marcin's strict criteria) |
|---|---|---|---|
| C1 | *Probabilistic Thinking* | ACCEPTED (cluster-aligned, Step-6-hidden) | **accept** — same source, F2 predicts stability. Source has "less than 1 in 5", "non-zero chance" — explicit probability language, passes strict criteria. |
| C2 | *PFR* OR *Decomposition* | PFR not in candidates, Decomposition not in candidates | **recall-risk** — same source, same recall hole likely. F2 doesn't fix recall variance. |
| C3 | *Information Asymmetry* | ACCEPTED (cluster-aligned, Step-6 primary) | **accept** if recall surfaces it — F2 predicts stability on operational language ("tip off / cover story"). If absent on case 7, that's recall variance not F2 failure. |
| C4 | *Principal Agent Problem* | ACCEPTED (cluster-aligned, Step-6 primary) | **stress test** — case 7's anchor set has PD instead of PAP for C4. Either: (a) verifier picked the secondary (PD) instead of primary (PAP) under stochasticity; (b) recall surfaced PD but not PAP this run. Either way the verifier finds an agency-family anchor on C4 — what changes is which one. **F2-compatible if PD's evidence quote sources from C4.** |
| C5 | *Confidence Calibration* | ACCEPTED (cluster-aligned, Step-6 primary) | **accept** — same source, F2 predicts stability. Strict criteria: "90%+", "70% or below" thresholds satisfy. |
| C6 | *PFR* | not in candidates | **recall-risk** — same recall hole. |
| C7 | *Premortem* | rejected at verifier ("mechanism absent") | **reject expected** — same source, F2 predicts stability. Case 3 had Premortem rejected because Turn 14's "future-self / second-guess" reasoning lacks the explicit if-when-then language F2 requires. (Compare case 6 where Turn 6 + Turn 17 had explicit failure-scenario / pre-registration language and Premortem accepted.) |
| C8 | `no_clean_primary` | n/a | n/a |

### Predicted comparison: case 3 vs case 7

If F2 stability holds, case 7 should produce **PT + CC + agency-family-anchor (PD or PAP)**, with possibly IA returning. The case-7 corpus-survey anchor set was 3 (PD + PT + CC) — meaning IA + AB from case 3 dropped, PD added.

Per F2: same source, so the changes from case 3 to case 7 are:
- **Recall variance**: PAP/IA/AB were in candidates on case 3; PD was not. On case 7, PD reached candidates and the others may or may not have.
- **Verifier variance**: even if all four reached candidates this run, only some passed.

F2 doesn't fully predict run-to-run anchor swaps on identical source. The expected pattern is "F2 predictions hold direction-of-acceptance per cluster, but exact anchor composition varies." If anchors land cluster-aligned (PD on C4, PT on C1, CC on C5) with operational quotes, F2 is supported even though the anchor composition differs from case 3.

### Trust axis predictions

Per the strict criteria:
- PD on C4: **expected acceptable_primary_match_or_secondary** (cluster has PD as acceptable_secondary; if quote sources from C4's source, defensible). Trust check: confirm evidence quote is C4-aligned, not generic "senior partner" lexical match elsewhere in conversation.
- PT on C1: **expected acceptable_primary_match** (same as case 3).
- CC on C5: **expected acceptable_primary_match** (same as case 3).

If any of the three anchors has evidence quote from a generic conversation overlay (e.g., PD's quote is from a non-C4 turn that just mentions "partner" generically), that's noisy-adjacent and breaks the trust streak.

## What case 7 can decide

**If F2 stability holds AND trust axis stays clean:** the audit closes with "Lane 2 is high-trust but uneven-friction; F2 explains most yield variance; run-to-run anchor composition varies due to recall/verifier stochasticity but cluster-coverage stays defensible."

**If F2 stability holds but trust axis breaks (e.g., PD quote is generic overlay):** the audit closes with "Lane 2 is high-trust except where broad career models overlay; F2 needs a 'must be locally mechanized' refinement on agency models."

**If F2 stability fails (different anchors with different operational language interpretations):** F2 is more fragile than N=6 suggested.

## What I'm holding for step 2

- 8 clusters from case 3's gold (this is the same conversation).
- F2 stability prediction: PT, CC, and an agency-family anchor on C4 should reach Step 6. IA + PAP + AB are run-stochastic.
- Strict criteria on PD, PT, CC per Marcin's case-7 instruction.
- After opening Lane 2 artifacts, attribution will compare actuals to F2 stability predictions and check trust-axis cleanliness.
