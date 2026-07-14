# Designed extraction quality v1 — result

The extractor understands what the conversations are about, but it does not yet
preserve the process faithfully enough to treat every downstream pressure as a
real blind spot.

Across five fourteen-message development conversations, capture was good in all
five, the broad decision was identified in all five, and all 31 selected
assistant passages were source-grounded. Twenty-nine were stored as exact
transcript substrings; two differed only by initial capitalization and passed
the intentionally narrow tolerant matcher. Those are real strengths, now stated
at the precision the artifacts actually earn.

The repeated weaknesses are more consequential:

- In all five cases, the user supplied or materially completed the provisional
  final plan, but `synthesized_position` recast it as assistant advice.
- All five extracted dropped-thread statuses were contradicted by the source.
  The assistant had engaged the thread, and often returned to it in the final
  turn. Case 04 proved the downstream consequence: the false citation status
  supported a false Curiosity pressure.
- Only 18 of 43 source-reviewed load-bearing constraints appeared faithfully in
  `live_constraints` (41.9%). This is a development diagnostic, not a population
  estimate, but the misses are large enough to matter.
- All five cases contained some source strengthening; three were material, such
  as turning a possible grant benefit into a deadline or active participation
  into a health condition.
- Only two of five reasoning-passage sets included the final assistant turn, so
  exact quotes did not guarantee trajectory coverage.

The clearest architectural lesson is that the current schema asks for the AI's
final recommendation and offers no representation for user-originated or jointly
developed positions. This cannot be solved honestly by scoring the current field
more strictly. The smallest next repair should add conversation-state ownership
and thread disposition without adding brittle semantic gates or expanding the
graph.

The two new extraction-only calls completed without repair or retry and cost an
estimated $0.003446. No pipeline, graph, revision, or answer-comparison call was
made or authorized.
