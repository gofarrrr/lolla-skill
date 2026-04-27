# Lane 2 quote-repair smoke test

Date: 2026-04-27
Branch: `feat/lane2-quote-validation-repair-2026-04-27`
Case: `user-launch-independent-fintech`

## Scope

This is a one-case smoke test for the quote-validation repair implementation. It is not the full five-case audit gate.

Inputs:

- `~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/extraction.json`
- `~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/conversation.txt`

Command shape:

```bash
python3 scripts/run_pipeline.py \
  --extraction-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/extraction.json \
  --conversation-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/conversation.txt \
  --skip-revision \
  --embeddings off \
  --output full \
  --output-file research/stability-runs/lane2-quote-repair-smoke-2026-04-27/<output>.json
```

`--skip-revision` avoids the Step 6 revision call. The pipeline still runs its normal Lane 2 producer path and post-pipeline Bullshit Index path.

## Runs

| Output | Code state | Result |
|---|---|---|
| `user-launch-independent-fintech.json` | initial implementation | Unusable Lane 2 sample: verifier returned malformed payload with missing `accepted` / `rejected`; 60 candidates, 0 accepted, 0 rejected. |
| `user-launch-independent-fintech-rerun2.json` | initial implementation | Interpretable sample, but no quote repairs. 6 accepted-before-cap, 3 `execution_quote_not_literal_substring` demotions remained. |
| `user-launch-independent-fintech-rerun3.json` | after whitespace-normalized literal matching + single-fragment ellipsis repair | 4 quote repairs, 5 surfaced anchors, 0 remaining quote-validation demotions. **Trust review found 1 false-positive (Reasoning Mode Router) — repair grabbed the literal first half of an ellipsis quote whose second half lived in a different turn, producing a literal-substring anchor that no longer supported the model.** |
| `user-launch-independent-fintech-rerun4.json` | **after both-halves ellipsis tightening** (commit `435df7f`) | **0 quote repairs.** 5 surfaced anchors with a different composition than rerun3. **1 ellipsis quote (`decomposition`) correctly demoted by the new rule.** Triggers "large anchor churn" stop condition vs rerun3. |

## Rerun 4 details (post both-halves tightening)

### What the both-halves rule did

One ellipsis quote was attempted: `decomposition` with `original_evidence_quote` that included a literal `...` between two halves. The both-halves rule rejected the repair (one half not findable literally, or bounded window exceeded — the persisted artifact records the original quote but not the per-half match outcome). Result: `execution_quote_not_literal_substring` demotion. **Mechanically correct: decomposition was not a literal-substring match, and the rule refused to salvage it from a single half.**

The other 5 surfaced anchors **did not require repair** — the verifier produced literal evidence quotes that passed `_find_normalized_literal_quote` directly. Repair logic was never engaged for them.

`companion_verification_quote_repairs` = 0 entries.

### Surfaced anchors (rerun 4)

| Anchor | presence_mode | Quote source (turn) | Cluster (case 1 gold) | Trust classification |
|---|---|---|---|---|
| Step Back | executed | Turn 3 (fundamentals-before-tactics) | C1 | acceptable_secondary — Step Back is plausibly the "pull back from immediate concerns" mechanism that C1 is doing; not C1's expected primary (PFR) but defensible. |
| Time Tested Validation | executed | Turn 2 (1-in-5 conversion) | C2 | borderline acceptable_secondary — TTV mechanism is "long-track-record evidence"; the conversion stat is industry experience, but the cluster's load-bearing read is base-rate correction, not TTV. Stretched fit. |
| Checklists | executed | Turn 7 (three-things action plan) | C7 | **noisy_adjacent** — Checklists matches the literal numbered-list surface (1/2/3) but misses C7's load-bearing mechanism (pre-registered failure conditions for reversal, the Premortem-flavored move). The verifier surfaced a surface-form match without the cluster's reasoning shape. |
| WYSIATI | executed | Turn 1 (clarifying questions) | C1 | acceptable_secondary — clarifying-questions IS WYSIATI-shaped (surface what the user has implicitly but not explicitly considered). Defensible secondary on C1. |
| Cognitive Dissonance | violated | Turn 3 (fundamentals-before-tactics) | C1 | **noisy_adjacent** — CD's mechanism is "holding contradictory beliefs." The Turn 3 quote is the assistant pushing back on the user's frame, not the assistant exhibiting or addressing dissonance. Stretched fit with no clear CD mechanism in the source. |

**Trust review verdict: 2 of 5 anchors are noisy_adjacent (Checklists, Cognitive Dissonance). Trust axis is NOT clean on this rerun.**

Crucially: **none of the noisy anchors went through quote repair.** They were accepted by the verifier with literal evidence quotes. The repair logic isn't the source of the noise.

### Comparison: rerun 3 vs rerun 4

| Anchor | Rerun 3 | Rerun 4 |
|---|---|---|
| Premortem | accepted (via ellipsis repair) | not surfaced (not a candidate this run) |
| Optimism Bias And Planning Fallacy | accepted | not surfaced |
| Optionality | accepted (via ellipsis repair) | not surfaced |
| Reasoning Mode Router | accepted (via ellipsis repair — **trust breach**) | not surfaced |
| WYSIATI | accepted (via token-overlap repair, on C2) | accepted (literal, on C1) |
| Step Back | not surfaced | accepted (literal) |
| Time Tested Validation | not surfaced | accepted (literal) |
| Checklists | not surfaced | accepted (literal) |
| Cognitive Dissonance | not surfaced | accepted (literal) |

**Only WYSIATI overlaps between rerun 3 and rerun 4, and even then on a different cluster** (rerun 3 mapped WYSIATI to C2 base-rate; rerun 4 maps it to C1 framing). 4 of 5 rerun-3 anchors did not surface in rerun 4. 4 of 5 rerun-4 anchors did not exist in rerun 3.

This is the case 3 vs case 7 same-source stability story from PR #43 playing out again on the same case 1 across two reruns. The producer chain has substantial run-to-run variance at the verifier-judgment stage on identical source. Quote-repair changes do not address this.

### Rejection summary (rerun 4)

| Rejection reason | Count |
|---|---|
| `mechanism absent` | 51 |
| `execution_quote_not_literal_substring` | 1 (decomposition — correctly demoted by both-halves rule) |
| `too generic` | 1 |
| **Total rejected** | 53 |

## Mechanical verification of the both-halves rule

The implementation is verified clean by:

1. **Unit tests** (`tests/test_lane2_contextual.py`): both-halves success, only-one-half-found rejection, halves-exceed-bounded-window rejection, no-fallback-to-token-overlap. All pass.
2. **Smoke**: the only ellipsis quote in rerun 4 (`decomposition`) was correctly demoted. No quote repairs fired across 60 candidates. The repair logic is not the source of any rerun-4 surfaced anchor.

The `Reasoning Mode Router` trust breach pattern from rerun 3 cannot recur under the new rule. The unit test `test_run_verification_does_not_repair_ellipsis_when_only_one_half_in_source` reproduces that exact pattern and asserts demotion.

## Stop condition triggered: large anchor churn

Per the spec's stop conditions for proceeding to the bounded 5-case audit, this rerun triggers:

> the smoke output changes in an unexpected way, such as verifier malformed payloads or large anchor churn

4 of 5 surfaced anchors changed identity between rerun 3 and rerun 4 on identical source. WYSIATI shifted clusters. Two of the new anchors (Checklists, Cognitive Dissonance) are noisy_adjacent. **Single-run smoke does not give us a reliable trust-axis read on case 1.**

## Verdict

**Mechanical correctness: the both-halves ellipsis rule is verified clean.** Tests pass; the case-1 RMR trust-breach pattern cannot recur; the literal-substring guarantee is preserved.

**Smoke verdict: NOT clean enough to proceed to the bounded 5-case audit.** The trust axis on rerun 4 is broken by 2 noisy_adjacent anchors that did NOT go through quote repair — they came from verifier judgment variance on the same source. Expanding to 5 cases now would generate more anchor-churn data without isolating the quote-repair fix's effect.

## Decision point

Two reasonable next moves:

**(a) Multi-run characterization first.** Run case 1 N=3-5 times to characterize the anchor-set distribution. Compute trust-axis stability across runs. Only proceed to the 5-case audit if a single-run trust read is reliable enough to evaluate the fix in isolation.

**(b) Accept run-stochasticity and proceed to the 5-case audit anyway.** The both-halves rule is mechanically verified. The 5-case audit's job is to test whether the fix degrades the cumulative anchor-quality picture across cases — even with run-variance, a *systematic* degradation should be detectable. The risk: any negative finding might be run-noise, not fix-induced.

**(c) Hold and re-scope.** The smoke surfaced a deeper question — single-run trust assessments are unreliable. The PR #43 audit's "0 false positives" was anchored on archived runs that may have been favorable; fresh reruns can produce noisy_adjacent anchors that the audit's methodology wouldn't have caught. Worth reconsidering whether the audit-as-test-set framing needs a multi-run amendment before any producer change is evaluated.

## What this smoke does NOT decide

- Whether the both-halves rule moves friction yield up or down on case 1 (answer would require comparing same-anchor reruns, not different-anchor reruns).
- Whether the rule helps Marcus or case 7 (the other affected cases).
- Whether prior 0%-demotion cases (mother, phd) stay clean (regression check not yet run).

The decision on the bounded 5-case audit should be made before any of those questions can be answered.
