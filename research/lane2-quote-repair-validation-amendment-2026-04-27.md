# Lane 2 quote-repair validation amendment (after the case-1 smoke)

Date: 2026-04-27
Branch: `feat/lane2-quote-validation-repair-2026-04-27`
Triggering artifact: `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/report.md`
Related: PR #43 (Lane 2 producer audit), `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`

## What this amendment changes

The original quote-repair validation plan called for a bounded 5-case audit gate after a clean single-case smoke. The case-1 smoke (rerun 4, after the both-halves ellipsis tightening at commit `435df7f`) invalidated that plan. This document records why and defines the methodology adjustment that has to happen before any further producer-side change is evaluated against the PR #43 audit corpus.

This is **not** a code change and **not** a revert. The both-halves repair rule stays. What changes is how we evaluate producer-side changes going forward.

## What the smoke found

Rerun 4 (post both-halves rule) result:

- Repair behavior was mechanically correct: 0 quote repairs fired, the only ellipsis quote (decomposition) was correctly demoted.
- The Reasoning Mode Router single-fragment trust breach from rerun 3 cannot recur under the new rule (covered by unit test).
- **However**, 2 of 5 surfaced anchors were noisy_adjacent: *Checklists* on C7 (surface numbered-list match, missing the cluster's pre-registration mechanism) and *Cognitive Dissonance* on C1 (stretched fit with no clear CD mechanism in source).
- Neither of those anchors went through quote repair. They were accepted by the verifier with literal evidence quotes that passed validation directly.
- 4 of 5 surfaced anchors changed identity vs rerun 3 on identical source. WYSIATI was the only overlap, and on a different cluster than rerun 3 picked.

## What this means

The quote-repair branch is no longer the suspected source of trust-axis problems on case 1. The verifier itself produced noisy literal-accepted anchors on a fresh run. The PR #43 audit's "0 observed false positives" finding was true for the archived runs in the corpus, but it was **not a stable property of Lane 2 across reruns of the same source**. Fresh reruns can produce noisy anchors with no quote-repair involvement.

This reframes the producer-side problem:

- **Quote repair** is a local parser/evidence fix. The both-halves rule is mechanically correct and the RMR failure mode is now blocked.
- **Trust-axis failure** is a *producer stability* problem, separable from quote repair. The verifier's judgment varies enough across runs that a single rerun can land on a worse anchor set than the audit's archived runs.

## Why the original 5-case audit gate is no longer well-isolated

The bounded 5-case audit was designed to check whether quote-repair changes preserved the audit's trust signal. That depended on the trust signal being stable per case. Fresh reruns disprove that assumption.

If we run the 5-case audit now and any case shows new noisy anchors, we cannot tell whether:

- The quote-repair fix introduced the noise, or
- The verifier produced a stochastically-worse run that has nothing to do with quote repair.

That is expensive ambiguity. Spending the run-cost without isolation buys us no decision power.

## The methodology amendment

Going forward, **producer-side validation must report two layers separately**:

1. **Repair-local trust.** Among anchors that went through quote repair specifically, did any become noisy_adjacent or false_positive? This isolates the repair branch's effect.
2. **Whole-run trust.** Among all surfaced anchors (regardless of repair involvement), did the producer produce any noisy anchors? This measures the producer chain's overall behavior.

A whole-run trust failure **blocks product-readiness** for any change that touches Lane 2, but **does not automatically falsify the specific change**. The two layers must be evaluated separately.

To evaluate producer stability — i.e., is whole-run trust a property we can measure on a single run, or do we need multi-run consensus — we need multi-run characterization, not single-case smoke.

## Next-step plan: N=3 baseline stability characterization on case 1

Before any further audit work, run a small multi-run characterization on case 1 to answer one specific question:

> Is the case-1 rerun-4 trust breach a one-off bad sample, or is the producer frequently surfacing noisy anchors on this source?

Spec:

- **Case**: `user-launch-independent-fintech`
- **Reruns**: 3 fresh runs (call them rerun 5, 6, 7), in addition to the 2 already in artifacts (rerun 3 + rerun 4)
- **Args**: same as rerun 4 (`--skip-revision --embeddings off`), against the same archived extraction + conversation
- **Output**: 3 new JSON files in `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/`, plus a characterization report

For each run, score:

- **Surfaced anchor identities** (which models did the cheat sheet contain).
- **Quote repairs fired** (count + identity + repair_method).
- **Quote-validation demotions** (count + identity).
- **noisy_adjacent / false_positive anchor count** (per the PR #43 trust rubric, applied to that run's anchors against the case-1 gold cluster table).
- **Overlap with prior runs** (which anchors recur, which churn).
- **Source of any noisy anchor**: quote repair, or direct literal verifier acceptance.

This is not validation of quote repair. It is characterization of producer stability so that the next decision (resume 5-case audit vs investigate producer-side architecture vs other) can be made on evidence rather than on one bad rerun.

## Decision tree after the N=3 characterization

| N=3 finding | Next track |
|---|---|
| Most reruns clean; rerun 4 was an outlier | Resume the bounded 5-case audit, but report repair-local and whole-run trust separately. Do not promote the PR until both layers are evaluated. |
| Most reruns produce noisy literal-accepted anchors | Stop. Quote repair is not the lever. Producer stability is the next track. The audit's "0 false positives" finding is conditional on archive-favorable runs and needs an updated framing in the synthesis memo. |
| Mixed (1-2 of 3 noisy) | Inconclusive. Either widen N or treat case 1 as inherently noisy and audit the other 4 cases independently. |

## What this amendment does NOT do

- **Does not revert the both-halves rule.** Commit `435df7f` is correct and stays.
- **Does not change the quote-repair code.** No tightening, no loosening.
- **Does not declare the quote-repair fix a quality lift.** The fix is mechanical hardening — it blocks a known unsafe path. Any product-quality claim has to be backed by evidence the smoke didn't provide.
- **Does not jump to DSPy / decomposition / prompt optimization.** One smoke isn't enough evidence to change architecture again. The N=3 characterization is the small step that lets us decide which architectural lever, if any, to pull next.

## Branch and PR framing

The quote-repair branch (`feat/lane2-quote-validation-repair-2026-04-27`) stays alive. The PR should be in this state going forward:

- **Code**: probably good (mechanical correctness verified by unit tests)
- **Unit tests**: good (4 ellipsis + repair tests covering the failure modes)
- **Repair safety**: improved (RMR pattern blocked)
- **Product validation**: blocked by producer stochasticity discovered during smoke
- **Next evidence needed**: N=3 baseline characterization on case 1

The PR should not be merged with a claim like "quote repair improves Lane 2 quality." It should be merged (when the time comes) with a claim like "quote repair eliminates the literal-but-undercovering ellipsis-fragment failure mode without weakening the trust gate." That is a narrower and honest claim.

## The uncomfortable lesson

The PR #43 audit's strongest finding — high trust, 0 observed false positives — was a property of the archived runs we audited, not a property of Lane 2 in general. Fresh reruns can break it. Single-run smoke is not a sufficient gate for producer-side changes.

This is progress. Not the clean kind, but the kind that stops us from lying to ourselves about what the audit proves.
