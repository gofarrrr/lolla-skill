# Simulated Reliability V1: Separated Mechanism State

Status: provider-free design implemented; provider calibration pending.

## Problem

Calibration A6 showed that one `joint_status` label was being asked to answer
two different questions:

1. Does a weakness remain in the user's reasoning process?
2. Has the vanilla assistant answer already converted that weakness into an
   actionable test, boundary, alternative, or reopening condition?

In the product-scope sentinel, the user still expressed two concerns while the
final assistant turn operationalized both. The model cited that assistant turn
but still returned `unresolved`. More context and typed evidence did not repair
the conflation.

## V1 contract

Each controlled mechanism receives three separate probabilistic
interpretations:

- `user_process_status`: `unresolved`, `resolved`, `ambiguous`, or
  `not_observed`;
- `vanilla_answer_coverage`: `operationalized`, `acknowledged_only`,
  `not_covered`, `not_applicable`, or `ambiguous`;
- `routing_disposition`: `route_uncovered_pressure` or `preserve_no_route`.

The user may remain unresolved while the vanilla answer is operationalized.
That combination is preserved in the receipt and does not route duplicate
pressure.

Pressure routes only for this declared combination:

```
user_process_status = unresolved
AND vanilla_answer_coverage IN {acknowledged_only, not_covered}
AND routing_disposition = route_uncovered_pressure
```

`acknowledged_only` requires assistant evidence. `not_covered` must not cite
assistant coverage. Every observed user-process status requires a user role
record. An unresolved user process remains `present` or
`missing_protection` even when answer coverage prevents routing; the separate
routing disposition alone controls routing. `not_observed` requires empty
evidence arrays.

## Deterministic boundary

Code may validate only:

- exact controlled mechanism identity and exhaustive coverage;
- enum and schema conformance;
- exact source-ID custody;
- the declared cross-field consistency rules above;
- fact-free routing projection;
- replayable downstream portfolio construction.

Code does not infer semantic status, merge role records, judge relevance, or
delete recalled mental-model candidates. The separation happens before graph
recall. Once graph candidates exist, the existing active/reserve custody rules
remain unchanged.

## Non-claims

- Answer coverage is not user adoption.
- Routing is not proof that a mental model applies.
- Preserving without routing is not proof that the reasoning is good.
- The mechanism interpretation remains probabilistic and source-linked.
- The receipt is evidence of process, not a quality score.

## Calibration gate

The product-scope case is the first sentinel because it exposed the precise
failure. Expected source-reviewed behavior for
`counterpressure_acknowledged_not_integrated` is:

- user process: unresolved;
- vanilla answer coverage: operationalized, citing `assistant-turn-007`;
- routing disposition: preserve without routing.

If the model again routes this mechanism, calibration stops. If it preserves
the separation, the quiet and creative sentinels may run under the same frozen
contract. No transfer case is authorized until the calibration batch is
reviewed.
