# Position decomposition v1 result

Status: provider-free capacity pass; one reserved live probe failed; path closed  
Date: 2026-07-12

## Why we tried it

The closed position-plus-stance contract asked one model call to find temporal
roles, explain a trajectory, identify stance objects, classify expressions,
align evidence, and package nineteen record properties. Current research and
our cross-model failures suggested that valid structured output could still
hide semantic overload.

V1 split the job into one role-trajectory task and at most three fixed-role
stance tasks. Code joined only exact trajectory IDs and fixed roles. The design
kept a four-call ceiling and added no semantic keyword, compatibility, or score
gate.

## Provider-free result

- The reviewed source corpus contained 23 fixtures, eight of them position
  fixtures.
- Seven eligible position fixtures were mechanically projected; the agency
  case stayed reserved for the live probe.
- Seven trajectory records and 21 role-specific stance records compiled.
- All seven joins completed with zero missing or quarantined records.
- Maximum planned calls were four per shard.
- The largest decomposed response schema was 1,745 bytes and 13 properties,
  versus 3,597 bytes and 19 properties for v4.3.
- Ten adversarial contract tests covered wrong IDs, cross-role evidence,
  unequal columns, missing roles, valid-but-dubious category pairs, and empty
  starting roles.

This proved representational capacity only. It did not prove automatic
extraction.

## Reserved live probe

The frozen agency-acquisition probe used DeepSeek V4 Flash through the exact
Alibaba route on OpenRouter. It allowed at most four calls, no retries or
fallbacks, and a $0.01 ceiling.

Only the trajectory call ran:

- wire and exact provider/model attribution passed;
- one record returned;
- deterministic admission quarantined it;
- no stance calls ran;
- cost was $0.000273092.

The response described and cited a real starting position but selected
`qualified_current_only`, whose contract explicitly means that no starting
state is visible. Source review found a second, more important failure: it
preserved employee-timing uncertainty at e053 but omitted e057's deal-momentum
counterpressure and unavoidable employee-involvement cost. Current and
trajectory prose also ended mid-sentence at the field-length boundary.

## Local defect found

The frozen v1 join called the empty join `complete` because zero admitted
trajectory records produced zero missing stance roles. That was false: one
trajectory record was quarantined. The artifact remains unchanged. The
prospective role-first design makes any quarantined, missing, or unreferenced
record incomplete.

## Decision

V1 is closed failed as an automatic path. Its first role-trajectory call was
still a semantic bottleneck: it could omit a qualification before any
role-specific reader saw it. Removing only the contradictory category would
make admission easier but would not restore the missing evidence.

The evidence authorizes a provider-free role-first revision: independent
starting, current, and qualification jobs, followed by a fourth exact-ID
relationship job. It does not authorize a v1 retry, graph work, runtime
integration, or a product-quality claim.
