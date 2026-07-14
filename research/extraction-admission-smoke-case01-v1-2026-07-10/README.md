# Case 01 extraction-admission smoke v1 — 2026-07-10

Status: passed; executed exactly once; rerun forbidden

This is the first live test of the transactional extraction-call custody
repair. It uses the heavily reused enterprise-logo-beta fixture, which has
already appeared in semantic, downstream, receipt, review, and Teacher work.
It is permanently excluded from future holdout claims.

The experiment is extraction-only. It gets one orchestrator invocation, one
initial OpenRouter extraction call, at most one built-in quote-repair call,
zero experiment retries, a 45-second provider socket timeout, and a 120-second
outer wall-clock ceiling. The graph, pressure pipeline, reconsideration,
embeddings, evaluators, and holdouts are outside scope.

The historical Case 12 smoke remains failed and is not reused. This run may
authorize planning an untouched Stage A holdout only if every v1 admission gate
passes. It cannot itself prove reasoning value or authorize a paired holdout.

Read order after execution:

1. `contract.json`;
2. `result.json`;
3. `call-evidence.json` (sanitized durable sidecar evidence);
4. `decision.json`;
5. `review.md`.

Final decision: all v1 gates passed. A separate goal may plan and freeze one
untouched Stage A extraction-plus-pipeline contract. Paired downstream calls
remain blocked.

Final repository verification: 87 focused tests and 3,980 non-network tests
passed, with one expected skip, under Python 3.12.
