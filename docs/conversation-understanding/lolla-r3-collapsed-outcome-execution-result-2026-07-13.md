# Lolla R3 collapsed-outcome execution result

Status: one authorized attempt closed; frozen mechanical gate failed; semantic
question unresolved

Date: 2026-07-13

Provider calls: one

Exact provider-reported cost: `$0.005517`

Additional calls authorized: zero

## Plain-language result

The new collapsed-outcome interface reached the model and did the part that the
previous R3 response could not do: Gemini 3.1 Flash-Lite returned one strict
JSON object, all nine pressure items survived, and deterministic code compiled
all nine controlled outcomes without changing the response.

The experiment nevertheless failed its frozen mechanical contract before
semantic review. The runner was written to treat either `message.reasoning` or
any `message.reasoning_details` record as returned reasoning content. The
actual response had no `reasoning` field and no reasoning text, summary, or
encrypted data. It contained one `reasoning.text` detail with only an opaque
Google signature and format metadata. The frozen runner counted that
signature-only envelope as a reasoning-exclusion breach.

We preserve that result exactly. We do not rewrite the call as a pass, repair
the runner retroactively, open the hidden semantic review, or pay for another
attempt. This is an honest negative experiment that found a validator boundary,
not evidence that the collapsed outcomes were useful or useless.

## What happened

| Item | Result |
| --- | --- |
| Requested model | `google/gemini-3.1-flash-lite` |
| Served model | `google/gemini-3.1-flash-lite` |
| Served provider | Google |
| Calls | 1 of 1 |
| Exact cost | `$0.005517` of `$0.01` |
| Provider generation ID | preserved |
| Strict JSON object | returned |
| Candidate rows | 9 of 9 |
| Collapsed compiler | accepted without healing |
| Readable reasoning returned | no |
| Signature-only reasoning metadata | yes, redacted in Git |
| Frozen full mechanical contract | failed |
| Source-first semantic review | not run |
| Retry, fallback, model switch, judge, or quiet control | none |

The important distinction is:

```text
wire/schema/collapsed compiler: passed
frozen reasoning-exclusion validator: failed
therefore frozen full mechanical contract: failed
therefore semantic review: prohibited
```

Calling the candidate “mechanically valid” without that qualification would be
wrong. The collapsed business-response compiler accepted it, but the complete
pre-agreed experimental gate did not.

## Why the validator diagnosis is credible

OpenRouter's current reasoning documentation says that excluded reasoning
tokens are not returned and that plaintext reasoning appears in the message
`reasoning` field. It separately documents `reasoning_details` as a structured
preservation surface whose records may carry text, summaries, encrypted data,
and signatures:

- [OpenRouter reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)

The causal diagnosis is based on the exact payload, not on the documentation
alone:

- `message.reasoning` was absent;
- the one detail had exactly `format`, `index`, `signature`, and `type`;
- `text`, `summary`, and `data` were absent;
- the runner used `bool(message.reasoning or message.reasoning_details)`.

We therefore infer that the runner conflated the presence of reasoning
metadata with the presence of returned reasoning content. OpenRouter does not
explicitly document this exact signature-only Gemini envelope, so we do not
generalize from one response or claim a provider guarantee.

## What this teaches us

The controlled-outcome redesign solved the specific response-shape
contradiction that motivated it at the local compiler boundary. It did not
prove the larger product hypothesis because the semantic result was never
reviewed.

The more important system lesson is constitutional. Deterministic gates are
valuable only when they test the invariant we actually care about. Here the
invariant was “do not return reasoning content,” while the implementation
tested “do not return any reasoning-detail object.” The latter is narrower,
more brittle, and rejected evidence that did not contain readable reasoning.
This is exactly the kind of deterministic/semantic boundary error the
constitution tells us to find provider-free.

The stop rule also worked:

- the first result was preserved;
- no fluent output was rescued after a gate failed;
- no semantic value claim was made from an unread review;
- exact cost and custody survived;
- one unexpected harness failure did not expand the budget.

## What remains unknown

We still do not know:

- whether the nine dispositions were source-grounded and well judged;
- whether any direct or graph pressure added useful friction;
- whether the reconsidered answer preserved the original strengths;
- whether it introduced unsupported claims, bloat, hedging, or
  over-absorption;
- whether a corrected prospective validator would behave consistently across
  providers and reasoning-detail types;
- whether this synthetic 28-message case predicts real-user usefulness;
- whether the collapsed-outcome interface is reliable across cases.

These are real unknowns, not failed scores. The hidden semantic review remains
closed.

## Decision and next boundary

No additional provider call is authorized. Do not retry this case.

The next goal should be provider-free and narrow:

1. Define returned reasoning **content** as non-empty plaintext, summary, or
   encrypted reasoning data, not a signature-only metadata envelope.
2. Add fixtures for absent reasoning, empty fields, plaintext, summary,
   encrypted data, signature-only metadata, and mixed records.
3. Keep this frozen call and its result unchanged as historical evidence.
4. Apply the correction only to prospective contracts and verify that it does
   not weaken privacy or custody.
5. Then record an explicit decision to defer further paid R3 work or prepare a
   genuinely new prospective case. Do not use a corrected validator to reopen
   semantic review of this failed frozen experiment.

R4 should not start with provider calls. After the provider-free validator
correction, the recommended path is to defer more paid R3 attempts and begin
R4's local corpus/replay work unless a new falsifiable R3 question clearly
earns another call.

## Evidence map

- Frozen execution contract:
  `docs/evals/lolla-r3-collapsed-outcome-case-execution-contract-v1.json`
- Exact founder authorization:
  `docs/evals/lolla-r3-collapsed-outcome-case-authorization-v1.json`
- Call started:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/pressure-call-started.json`
- Exact call result:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/pressure-call-result.json`
- Exact provider budget:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/provider-budget.json`
- Commit-safe redacted payload:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/provider-payload-redacted.json`
- Failure closeout:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/failure-closeout.json`
- Terminal result:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/r3-terminal-result.json`
- Frozen runner: `scripts/evals/run_r3_collapsed_outcome_case.py`
- Closeout validator: `scripts/evals/finalize_r3_collapsed_outcome_case.py`
- Tests: `tests/test_r3_collapsed_outcome_case_closeout.py`
