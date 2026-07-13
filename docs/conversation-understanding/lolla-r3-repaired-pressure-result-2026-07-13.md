# Lolla R3 repaired pressure result

Status: R3 closed after one repaired response failed its mechanical contract

Date: 2026-07-13

Provider calls: one

Exact provider-reported cost: `$0.0062705`

Quiet-control calls: zero

## Plain-language result

The schema repair worked at the transport boundary. Gemini 3.1 Flash-Lite,
served by Google through the pinned OpenRouter route, accepted the repaired
request and returned one strict JSON object. This resolves the earlier narrow
unknown: the projected schema can reach inference on this route.

The returned object still failed Lolla's deterministic response contract. For
the third pressure item, the model chose `park` while labeling the effect as
`uncertainty_change`. In this contract, `park` means the pressure does not earn
a material effect now and may be reopened only under a stated condition. The
two labels therefore contradict one another.

Lolla did not silently change `uncertainty_change` to `no_material_effect`,
reinterpret `park` as `apply`, retry the call, change models, or ask a judge to
rescue the output. The exact candidate is preserved as a failed response. This
is a useful negative result: provider transport works, but this single cheap
operator did not reliably satisfy the complete cross-field contract in one
pass.

## What this does and does not prove

It establishes that:

- the documented-subset schema repair solved the observed pre-inference
  interoperability failure for this request;
- the pinned Gemini 3.1 Flash-Lite/Google route returned strict JSON on the one
  authorized attempt;
- deterministic validation detected a fluent internal contradiction that a
  schema alone could not express;
- the response, exact provider cost, generation identity, budget, and failure
  are under hash-linked custody;
- no retry, fallback, response healing, premium model, evaluator, or quiet
  control was used.

It does not establish that:

- the pressure produced a useful or source-grounded reasoning delta;
- Gemini 3.1 Flash-Lite cannot do this task under a different task design;
- another model would be better;
- R3's fresh-consumer approach is product-valid;
- a mechanically valid answer would be better than the original answer.

Because the mechanical contract failed, the seven semantic review dimensions
were not scored. Reading the prose and declaring it useful after the gate
failed would be post-hoc rescue. Only exact-cost and failure custody passed.
There is no scalar quality score.

## Exact execution outcome

| Item | Result |
| --- | --- |
| Requested model | `google/gemini-3.1-flash-lite` |
| Served model | `google/gemini-3.1-flash-lite` |
| Served provider | Google |
| Provider route | `google-vertex/global` only |
| Calls | 1 of 1 |
| Exact cost | `$0.0062705` of `$0.01` |
| Automatic retries | 0 |
| Fallbacks | 0 |
| Response healing | none |
| Strict JSON returned | yes |
| Canonical compiler accepted | no |
| Mechanical findings | 1 |
| Source-first semantic review | prohibited after mechanical failure |
| Quiet control | not authorized and not run |

The provider included one opaque reasoning-continuation signature but no
readable reasoning text. The raw payload is preserved outside Git. The public
payload replaces that signature with a redaction marker and records the raw
file and value hashes. The frozen runner conservatively marked the presence of
`reasoning_details`; the closeout explains that this was opaque metadata, not
visible chain-of-thought, without rewriting the original call record.

## Constitutional interpretation

This is the intended hybrid boundary in action:

- the LLM handled the messy semantic work: attempted nine lenses, selected
  dispositions, cited source turns, and wrote a reconsidered answer;
- deterministic code owned identity, ordering, allowed labels, cross-field
  consistency, cost, provider policy, and stop rules;
- deterministic code did not decide whether a mental model was relevant;
- a failed explicit contract stopped the workflow without pretending that the
  response was good or bad in a broader semantic sense.

The experiment therefore did not dumb down the product. It exposed the next
real uncertainty: the final-consumer task asks one inexpensive model to make
nine semantic judgments, maintain exact cross-field discipline, and draft a
bounded answer in one pass. We should reassess that task shape locally before
paying for another attempt. That reassessment must preserve the same product
idea and must not turn into brittle deterministic semantic gating.

## Decision and next boundary

R3's semantic exit condition was not met. The quiet control is blocked. No
additional provider call is authorized.

The next goal is provider-free: audit whether the final-consumer contract
combines too many responsibilities, and compare the smallest constitutionally
honest alternatives using the preserved response and local fixtures. Candidate
changes may separate disposition from answer drafting or reserve a stronger
operator for final synthesis, but neither is adopted merely because it sounds
plausible. The work must first show which responsibility caused the failure,
what custody must remain exact, what cost would change, and how a future test
could falsify the proposed repair. Model shopping and ad-hoc retries remain
stopped.

## Evidence

- Execution contract: `docs/evals/lolla-r3-repaired-pressure-execution-contract-v1.json`
- One-time authorization: `docs/evals/lolla-r3-repaired-pressure-authorization-v1.json`
- Started record: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/pressure-call-started.json`
- Exact call result: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/pressure-call-result.json`
- Exact budget: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/provider-budget.json`
- Commit-safe payload: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/provider-payload-redacted.json`
- Mechanical closeout: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/failure-closeout.json`
- Terminal result: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/r3-terminal-result.json`
- Runner: `scripts/evals/run_r3_repaired_pressure.py`
- Closeout: `scripts/evals/finalize_r3_repaired_pressure_failure.py`
- Tests: `tests/test_r3_repaired_pressure_execution.py` and
  `tests/test_r3_repaired_pressure_failure_closeout.py`
