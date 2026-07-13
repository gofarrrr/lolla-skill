# Joint-process reasoning invariance — result

Status: **failed as frozen; routing behavior directionally passed**

## What improved over Batch 3

The fact-swapped conversations produced:

- identical fact-free active/edge projections;
- identical active graph seed candidates;
- identical edge-reserve candidates;
- the four predeclared base weaknesses as `unresolved` in both cases.

This fixes the main Batch 3 product-surface failure: irrelevant factual
substitution did not change graph routing.

The repaired conversation also produced no active graph seeds. The model
recognized the ambiguous-demand, missing-reversal, and omitted-reversible-path
weaknesses as repaired, and did not route any of them.

## Why the frozen contract still failed

The expected result declared `acknowledged_constraint_not_gated` as
`resolved_in_conversation` in the repaired fixture. The model returned
`not_observed`.

Source review shows that `not_observed` is defensible. The user mentions the
constraints, and the assistant immediately makes them decision gates. The
assistant never first acknowledges and ignores them. Both statuses correctly
produce no active seed.

The contract remains failed because expected labels were frozen before the
call. We do not repair the gold, rerun the fixture, or claim a pass.

## Meaning

This is primarily an F8 scorer/ontology mismatch rather than a routing
failure:

```text
fact invariance at routing surface: passed
reasoning-change sensitivity: passed
repaired conversation active seeds: zero
exact historical-status gold: failed on one defensible distinction
runtime integration: not authorized
```

Future contracts should score two things separately:

1. whether a mechanism is active, edge-reserved, or non-active for routing;
2. whether the audit history calls a non-active mechanism `not_observed` or
   `resolved_in_conversation`.

Where both historical readings are source-defensible, the allowed set must be
declared prospectively. It must not be repaired after a run.

Three calls used 3,552 tokens and an estimated `$0.002933`. No evaluator,
retry, embedding call, or runtime change occurred.
