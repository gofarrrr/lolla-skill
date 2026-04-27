# Case-1 producer stability characterization (N=5 across reruns 3–7)

Date: 2026-04-27
Branch: `feat/lane2-quote-validation-repair-2026-04-27`
Triggering artifact: `research/lane2-quote-repair-validation-amendment-2026-04-27.md`
Case: `user-launch-independent-fintech` (single conversation, repeated reruns)

## Scope

Per the validation amendment, run N=3 fresh runs of case 1 (rerun5, rerun6, rerun7) on the same archived extraction + conversation, with the both-halves ellipsis rule active (commit `435df7f`). Combine with rerun3 (pre-fix) and rerun4 (post-fix) for a 5-rerun cross-run picture.

The question being answered:

> Is the case-1 rerun-4 trust breach a one-off bad sample, or is the producer frequently surfacing noisy anchors on this source?

## Method

Reruns 5, 6, 7 each:

```bash
python3 scripts/run_pipeline.py \
  --extraction-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/extraction.json \
  --conversation-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/conversation.txt \
  --skip-revision \
  --embeddings off \
  --output full \
  --output-file research/stability-runs/lane2-quote-repair-smoke-2026-04-27/user-launch-independent-fintech-rerunN.json
```

Trust classification per anchor uses the PR #43 §7.2 schema against the case-1 gold cluster table (`research/stability-runs/lane2-producer-audit-2026-04-26/case_user-launch-independent-fintech_step1_source_first.md` v2):

- `acceptable_primary_match` — anchor IS the cluster's expected primary, evidence aligned
- `acceptable_primary_match_with_quote_drift` — anchor IS expected primary, evidence quote drifts
- `acceptable_secondary` — anchor is the cluster's `acceptable_secondary_model`
- `noisy_adjacent` — keyword/lexically adjacent, semantically wrong fit
- `false_positive` — clearly wrong

## Cross-run anchor surfacing

Anchors that surfaced in each rerun. `R` = repaired by quote repair, `L` = literal verifier acceptance.

| Anchor | r3 (pre-fix) | r4 | r5 | r6 | r7 | Count |
|---|---|---|---|---|---|---|
| `optimism-bias-and-planning-fallacy` | L | | L | R | R | 4/5 |
| `wysiati` | R | L | | | L | 3/5 |
| `optionality` | R | | L | | | 2/5 |
| `premortem` | R | | | L | | 2/5 |
| `cognitive-dissonance` | | L | | L | | 2/5 |
| `checklists` | | L | L | | | 2/5 |
| `reasoning-mode-router` | R (trust breach) | | | | | 1/5 |
| `step-back` | | L | | | | 1/5 |
| `time-tested-validation` | | L | | | | 1/5 |
| `probabilistic-thinking` | | | | L | | 1/5 |
| `commitment-bias` | | | | L | | 1/5 |
| `representativeness-heuristic` | | | | | L | 1/5 |
| `feedback-loops` | | | | | L | 1/5 |
| `information-asymmetry` | | | | | L | 1/5 |

**14 unique anchors across 5 reruns of identical source.** Only Optimism Bias And Planning Fallacy appears in 4/5 reruns. WYSIATI in 3/5. The remaining 12 anchors appear in ≤ 2/5 reruns. **Producer surfacing is highly stochastic.**

## Per-rerun trust classification

| Rerun | Anchors | Acceptable | Borderline | Noisy_adjacent / false_positive |
|---|---|---|---|---|
| r3 (pre-fix) | 5 | Optimism Bias (sec C2), Premortem (drift C7), Optionality (drift C4), WYSIATI (sec C2) | 0 | RMR (false-positive via single-fragment ellipsis repair) |
| r4 | 5 | Step Back (sec C1), TTV (borderline sec C2), WYSIATI (sec C1) | 0 | Checklists (noisy on C7), Cognitive Dissonance (noisy on C1) |
| r5 | 3 | Optimism Bias (sec C2), Optionality (drift C4) | 0 | Checklists (noisy on C7) |
| r6 | 5 | Premortem (drift C7), Optimism Bias (sec C2) | Commitment Bias (defensible-borderline sec C3) | Cognitive Dissonance (noisy), Probabilistic Thinking on runway-pressure quote (noisy — runway is deterministic if-then, not probabilistic) |
| r7 | 5 | Optimism Bias (sec C2), WYSIATI (sec C1), RH (defensible alternative on C2) | Information Asymmetry (borderline sec on spouse-keep-in-head quote) | Feedback Loops on Turn-7 pre-registered-checkpoint quote (noisy on C7 — checkpoint is Premortem-flavored, not feedback-loop-flavored) |

### Cumulative trust score across N=5 reruns

- **Total surfaced anchors**: 23 (5+5+3+5+5)
- **Acceptable (primary-match / drift / secondary / defensible alternative)**: 14 (61%)
- **Borderline**: 2 (9%)
- **Noisy_adjacent / false_positive**: 7 (30%)

**Every rerun produced at least one noisy or borderline anchor.** Case 1's trust axis is not clean on any single fresh rerun.

## Quote-repair behavior across reruns

| Rerun | Repairs fired | Repaired anchors | Demotions (post-validation) | Outcomes |
|---|---|---|---|---|
| r3 (pre-fix) | 4 | wysiati, optionality, RMR, premortem | 0 | 1 trust breach (RMR via single-fragment ellipsis) |
| r4 (post-fix) | 0 | — | 1 (decomposition correctly demoted by both-halves rule) | Repair logic clean; verifier-side noise present (Checklists, CD) |
| r5 (post-fix) | 0 | — | 2 (RMR + WYSIATI ellipsis quotes correctly demoted) | **Both-halves rule blocked the same RMR pattern from rerun 3.** ✓ |
| r6 (post-fix) | 1 | optimism-bias-and-planning-fallacy (token-overlap, score 0.967) | 0 | Clean repair: verifier quote was a paraphrase missing "It means they like you", repair found the longer literal source span. |
| r7 (post-fix) | 1 | optimism-bias-and-planning-fallacy (token-overlap, score 0.967) | 0 | Same clean repair as r6, on identical original verifier quote. |

### Repair-local trust verdict (across r4-r7 with the both-halves rule active)

- **Repairs fired**: 2 across 4 reruns (rerun6 + rerun7, both Optimism Bias).
- **Trust classification of repaired anchors**: both are `acceptable_secondary` on C2 with C2-aligned quotes.
- **Trust breaches via quote repair**: 0 across all post-fix reruns.
- **Ellipsis quotes correctly demoted**: 3 (decomposition r4, RMR r5, WYSIATI r5).

**The both-halves rule is doing exactly what it was designed to do.** It blocks the single-fragment ellipsis trust-breach pattern (RMR pattern reproduced and blocked on rerun5) without preventing legitimate token-overlap repairs (rerun6/rerun7 Optimism Bias rescue is clean).

### Whole-run trust verdict (across all 5 reruns)

- 7 of 23 surfaced anchors (30%) are noisy_adjacent.
- All 7 noisy anchors entered Step 6 via **direct literal verifier acceptance**, not through quote repair.
- Every rerun produced at least one noisy or borderline anchor.

**The verifier itself produces noisy anchors at a non-trivial rate on this conversation.**

## Decision tree resolution (per amendment §"Decision tree after the N=3 characterization")

The amendment defined three branches:

| N=3 finding | Next track |
|---|---|
| Most reruns clean; rerun 4 was an outlier | Resume the bounded 5-case audit, but report repair-local and whole-run trust separately. Do not promote the PR until both layers are evaluated. |
| **Most reruns produce noisy literal-accepted anchors** | **Stop. Quote repair is not the lever. Producer stability is the next track. The audit's "0 false positives" finding is conditional on archive-favorable runs and needs an updated framing in the synthesis memo.** |
| Mixed (1-2 of 3 noisy) | Inconclusive. Either widen N or treat case 1 as inherently noisy and audit the other 4 cases independently. |

**The middle branch fires.** All 5 reruns produced at least one noisy_adjacent or borderline anchor. None came from quote repair. The producer's trust axis is the active problem on this case.

## What this means for the quote-repair branch

- **Repair-local trust: clean.** Both-halves rule + token-overlap rule combined produce 0 trust breaches across 4 post-fix reruns. The fix delivers what it promises (block single-fragment ellipsis salvage; preserve legitimate token-overlap repair).
- **Whole-run trust: not clean enough to claim quote-repair improves Lane 2 quality.** The verifier-side noise is independent of quote repair.

The quote-repair branch should land as **mechanical hardening that blocks a known unsafe path**. Not as a "Lane 2 quality lift." The PR description should reflect that.

## What this means for the audit synthesis

The PR #43 synthesis memo (`research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`) reported "0 false positives across 26 surfaced anchor rows in 7 runs." That finding remains literally true for the archived runs in the audit corpus. **But it is now established that the trust axis is not a stable property of Lane 2 across reruns of the same source.** Across 5 fresh reruns of case 1 alone, we observed 7 noisy_adjacent anchors. The audit's 0-FP signal was conditional on the archive sample being favorable.

The synthesis memo deserves a small post-script (separate deliverable, separate branch) noting this finding so future readers don't over-interpret the original headline.

## What this means for the next track

Quote repair is not the lever for the Lane 2 friction-yield problem. The next architecturally relevant track is producer stability — specifically the verifier's tendency to accept noisy_adjacent anchors with literal evidence quotes when running the same conversation multiple times.

This is consistent with PR #43 leak mode #4 ("run-to-run variance at all producer stages") and #5 ("stochastic anchor identity within ambiguous clusters"). The fix space includes: verifier prompt hardening for mechanism specificity, hypothesis-diversity surfacing, multi-run consensus, or shape-scoped recall to reduce the noisy-adjacent surface.

The next deliverable on this track should be a design memo, not code. Picking the architecture from one case-1 characterization would be the same kind of single-evidence mistake the amendment was written to prevent.

## Status

- Both-halves ellipsis rule: **mechanically clean and verified across 4 post-fix reruns.**
- Quote-repair branch readiness: **mechanical hardening complete; product validation blocked by producer-stability noise unrelated to quote repair.**
- 5-case bounded audit: **still blocked.** Running it now would conflate quote-repair effects with verifier stochasticity. Per amendment, do not run.
- Next track: **producer-side verifier/stability work**, scoped via a separate design memo.

The branch can be promoted when we frame the PR honestly: "ellipsis repair tightening blocks the RMR single-fragment trust breach without weakening trust gates, while leaving the broader producer-stability problem untouched as a separate track."
