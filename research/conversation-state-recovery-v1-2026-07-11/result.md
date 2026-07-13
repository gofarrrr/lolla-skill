# Conversation-state candidate recovery result

Decision: **provider-free foundation passed; stop before model execution**.

## In simple terms

The earlier extractor tried to understand too much in one response and lost
important parts of messy conversation. We have now separated that job into
three smaller semantic reads—positions and contributions, focal threads and
their trajectory, and atomic constraints—while keeping deterministic code in
charge of source identity, validation, custody, quarantine, and composition.

Across five reviewed 14-message conversations, the recovery path preserved:

- five joint positions;
- four addressed-but-unresolved focal threads and one resolved thread;
- both user and assistant Turn 7 contributions in every position trajectory;
- 45 atomic constraints;
- zero invalid reviewed candidates;
- zero direct graph seeds.

The 45 count is deliberate. Two legacy records combined claims with different
source strength. They were split into four atomic candidates instead of
weakening the new contract to allow `mixed` claims.

Four adversarial cases also behaved correctly: unsupported joint ownership and
a non-contiguous quote were quarantined, a mixed constraint was rejected by the
typed parser, and `not_found` was preserved as an honest absence rather than
forcing a candidate.

## What we learned

The deterministic half is now doing the work it is suited for: stable source
custody, exact validation, state preservation, fail-closed admission, and
composition. The probabilistic half still owns the genuinely semantic work:
interpreting positions, contributions, trajectories, and constraints. No
brittle deterministic relevance gate was added in front of the conversation.

This makes the next experiment interpretable. If a model fails, we can tell
whether it failed position ownership, focal-thread trajectory, atomic
constraints, evidence custody, or composition instead of receiving one opaque
bad packet.

## What remains unknown

No model populated the new contracts in this package. Provider schema
compatibility was checked locally, but actual provider acceptance, extraction
quality, model variance, cost, latency, graph value, and downstream decision
value remain untested. The five targets are development fixtures reviewed in
the same work session, not independent gold.

## Stop line and recommended next decision

Do not integrate this into the live skill yet. The next possible step is one
prospectively frozen extraction-only experiment on a development case other
than Case 03. It should run the three microtasks with no retry, score each family
separately, preserve all failures, stop before a second case, and avoid the
graph and full pipeline. Provider/model and call/cost envelope require explicit
authorization.

