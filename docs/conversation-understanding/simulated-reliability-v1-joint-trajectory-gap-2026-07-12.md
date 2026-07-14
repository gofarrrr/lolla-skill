# V1 joint-trajectory mechanism gap

Status: causal semantic gap identified; provider-free repair complete  
Date: 2026-07-12

## Failure

The A2 product-scope calibration run was operationally complete and the role
records were substantially source-faithful. Nevertheless, the mechanism
interpreter activated `counterpressure_acknowledged_not_integrated` even though
the authoritative conversation's final assistant response had already turned
the user's two concerns into concrete treatment:

- allow a bounded disposable prototype rather than production integration; and
- ask Northline to reflect back what it believes the discovery sessions mean.

The direct and graph pressure arms then repeated those same moves. The direct
arm also invented CSV timing/column details and imposed a stronger sequencing
gate than the source supported. The graph additions did not create a unique
useful delta beyond the transcript-only control.

## Cause

The V2.4.2 role interface intentionally describes the user's starting position,
current position, and unresolved qualification. The V3 mechanism interpreter
claims to assess the joint trajectory, but its input contained only those user
role records. It never saw the assistant's later repair.

This is a context-responsibility mismatch under Constitution house rule 14. The
probabilistic task was evaluated as if it understood both sides of the
conversation while its visible context represented only one side.

## Prospective repair

The user-role microtasks remain unchanged. Before the mechanism call, V1 now
attaches every assistant message from the authoritative conversation as a
source-linked contribution with turn number and exact text. No assistant message
is selected by keyword, model relevance, chronology gate, or hand-authored
importance rule.

The mechanism interpreter is instructed to distinguish:

- an unresolved concern that remains merely acknowledged;
- a concern already operationalized into a test, boundary, alternative, or
  reopening condition by the vanilla conversation; and
- a passing assistant mention that does not amount to integration.

The judgment remains probabilistic. Code only verifies that every assistant
message is present, identities and hashes are valid, and the resulting routing
projection remains fact-free and controlled-ID-only.

## Why this is not architecture drift

- no provider call is added;
- no deterministic semantic gate is added;
- no candidate is removed after graph recall;
- no keyword declares an issue resolved;
- no role contract or controlled mechanism identity changes; and
- the graph still receives only fact-free controlled mechanism nodes.

The packet becomes larger, so fan-in, cost, and model behavior remain calibration
gates. If the revised mechanism task still calls already-operationalized advice
unresolved, this context repair has failed and another prompt variant is not
automatically authorized.

