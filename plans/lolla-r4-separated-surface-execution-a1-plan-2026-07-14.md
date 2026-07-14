# Lolla R4 separated-surface execution A1 plan and closeout

Status: terminal execution complete; semantic comparison not evaluable

Date: 2026-07-14

Canonical start: `5bc8408341c11513a335977c9922d4971a78701b`

Execution branch: `agent/r4-separated-surface-execution-a1`

Frozen contract SHA-256:
`2e3a731ba3880ed883044e5aa0ee039d4cf1f38925b785cf3325a0ffb4b18dde`

Decision: `semantic_result_not_evaluable`

## Question

Does asking for the two existing residual surfaces in separate provider calls
reduce unsupported opposite-surface companion records relative to asking for
both surfaces together, while preserving genuine findings?

## Executed boundary

One exact authorization permitted twelve calls, no retries or fallbacks, and a
`$0.30` hard provider-reported ceiling. The runner attempted ordinals 1 through
7 in frozen order. Ordinals 1 through 6 completed. Ordinal 7 returned the
allowed model and provider identities but `finish_reason: "error"`, no usable
usage object, and no provider-reported cost. The runner preserved the terminal
bytes and made no later call.

The authorization is consumed. Ordinals 8 through 12 are not authorized under
this plan and must not be issued as replacement calls.

## Custody sequence

1. Validate canonical state, contract, twelve requests, target isolation,
   official operator practice, key availability, and dry-run zero state.
2. Create and validate one temporary exact authorization.
3. Execute once and stop on the first terminal failure.
4. Seal exact raw evidence and remove the temporary authorization.
5. Commit raw execution in `9f1b308ca852b86d640e481a32bc6efc8f5320e9`.
6. Only then open protected evidence and review every admitted record.
7. Apply the frozen categorical matrix without a scalar score.
8. Freeze closeout, verify the repository, and leave a clean unpublished local
   branch.

## Result boundary

The six completed calls cover only the two quiet controls. Both separated
decision-gap calls returned correct zero. Both separated dependency calls
still emitted governed-machinery false positives. The paired calls failed both
quiet surfaces. Nine admitted records were reviewed and all nine are false
positives.

The positive cases lack a complete matched comparison: ordinal 7 failed and
ordinals 8 through 12 were not attempted. Therefore neither companion-pressure
causality nor genuine-finding preservation can be evaluated. The frozen
decision is `semantic_result_not_evaluable`.

## Authorization and next gate

Current authorization is zero calls and `$0.00`. No retry, rerun, replacement
call, publication, integration, model comparison, or R5 work is authorized.
The next founder decision is only whether to publish this terminal evidence.
A new paid execution would require a new scientific and authorization decision;
it is not implied or recommended automatically by this mechanical failure.
