# Extraction admission smoke — review

Status: **failed; another paired holdout is not authorized**

## What the one attempt established

The frozen smoke ran once under contract hash
`3221aaa8541d7c5106863758ba8ece78648cd00d3dbbc99b40d27629775cff12`.
Case 12 is permanently excluded from future downstream holdout claims.

The pre-call and conversation-custody repairs worked:

- the output parent did not exist before execution and was created before the
  provider boundary;
- the extractor persisted a terminal error artifact instead of losing the
  run;
- capture was `good`, full, and run-bound: 2/2 turns captured, zero omitted;
- the extractor ran under the exact frozen fixture, prompt, model, runner, and
  transitive code hashes;
- there was one experiment invocation and no experiment retry.

These facts retire the earlier missing-output-directory failure. They do not
admit the extraction.

## Why admission failed

The provider boundary returned an empty parsed object after about 207 seconds.
The extractor correctly rejected it because `decision_situation` and
`synthesized_position` were missing, then persisted `status: error`.

That terminal path did **not** persist the boundary client's call log. The raw
extraction-call sidecar is absent even though the code necessarily crossed the
provider boundary before producing the missing-required-fields error. As a
result, the sealed receipt cannot recover:

- provider-call status;
- requested versus served model attribution;
- tokens;
- actual call count from the provider record;
- cost.

The result's canonical usage aggregator consequently contains zero calls and
`estimated_total_cost_usd: 0.0` with `cost_estimate_state: not_applicable`.
That numeric zero is not evidence of zero cost. For this failed run, cost is
unknown because telemetry custody failed.

Fifteen of 31 gates failed, mostly as downstream consequences of the two root
failures: no admissible extraction and no persisted call evidence. There was
no quote-validation opportunity, pipeline run, graph routing, downstream
generation, evaluator call, or embedding call.

## Classification

This is an operability and receipt-custody failure, not a reasoning-quality
result and not a graph result. It extends the evaluation taxonomy with a
provider/schema/telemetry class: a provider-bound operation returned no
admissible object and its call evidence did not survive the terminal path.

The failure reinforces the hybrid boundary:

- the LLM remains responsible for interpreting messy conversation;
- deterministic code is responsible for output readiness, exact evidence,
  terminal-state persistence, timing, and honest unknowns;
- no deterministic rule should fabricate the two missing semantic fields or
  treat an empty object as understanding.

## Prospective repair

Before any new paid reasoning experiment:

1. persist extraction call records on every terminal path after client
   initialization, including missing fields, `not_strategic`, provider error,
   invalid JSON, and quote-repair failure;
2. distinguish `call_attempted`, `call_record_persisted`, and
   `admissible_extraction` rather than inferring one from another;
3. report cost as unknown, never zero, when a call was attempted but usage
   evidence is absent;
4. measure end-to-end wall time and freeze an outer wall-clock ceiling; the
   provider socket timeout alone did not bound this 207-second run;
5. keep raw provider content local while sealing a review-safe usage summary;
6. test these paths without provider calls;
7. only then freeze one new smoke contract on a different designated
   non-holdout fixture.

The failed Case 12 smoke will not be rerun. A fresh smoke is a new experiment,
not a retry, and remains required before another paired holdout.

## Decision

- `next_holdout_authorized`: **false**
- `runtime_integration_authorized`: **false**
- extraction semantic or graph promotion: **none**
- retain: output-path preflight, complete capture, frozen hash custody, and
  the admission harness
- next bounded engineering goal: terminal-path extraction call custody and
  wall-clock enforcement

## Verification

- 79 focused extraction, capture, quote, usage, run-state, constitution, and
  measurement tests passed;
- 3,972 non-network repository tests passed with one expected skip under
  Python 3.12;
- the legacy `tests/test_stability_check.py` module was excluded from the
  non-network total because six tests invoke the unavailable OpenAI client for
  embeddings; no key was loaded and no verification call was spent;
- contract, result, and decision JSON parse cleanly;
- Python compilation and changed-file whitespace checks passed.
