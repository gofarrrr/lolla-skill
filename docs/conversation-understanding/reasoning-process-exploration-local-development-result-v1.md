# Exploration-local development result

Status: development case passed; prospective transfer may be designed  
Date: 2026-07-11

## Simple explanation

The full-conversation exploration reader repeatedly saw the broad option but
lost a small, important qualification attached to it. The local design stops
asking one model call to choose among an entire conversation. It reads one
user/assistant turn pair at a time and returns at most two pairs:

1. the alternative being considered;
2. the condition, limit, tradeoff, or failure condition attached to it.

The immediately preceding turn pair is available as context. Its aliases may
be cited only as the alternative side when the focal pair adds a new limit. The
new limit must always be cited from the focal pair. Code enforces this source
boundary but never decides what the conversation means.

## What passed provider-free

- 35 focal windows across five fourteen-message conversations;
- every one of 335 source sentence aliases focal exactly once;
- five of five same-pair protected alternative-limit fixtures;
- one cross-turn adversarial fixture;
- a real 24-message stress conversation with 12 windows and 292/292 focal
  sentence custody;
- maximum development packet size: 3,944 bytes;
- maximum stress packet size: 6,159 bytes;
- maximum future fan-out: seven calls and fourteen records per fourteen-message
  case;
- no auxiliary ledger, global synthesizer, semantic merge, graph, or runtime
  behavior.

The first cold-reader version failed because it could not represent an option
introduced in one turn and limited in the next. The v2 role-specific carry-
forward rule fixed that before any model call.

## What happened in the model-backed development case

The smallest Case-02 Turn-3 call passed first. Gemini, through OpenRouter,
returned the named-role recruitment test with `e026` and the previously lost
“not necessarily all ownership” qualification with `e027`.

The other six windows were then called once. Four admitted completely. Turn 4
contained one valid focal record and one exact `e026/e027` prior-window
duplicate that incorrectly cited the prior limit as focal; record-level custody
admitted the valid sibling and quarantined the duplicate. Turn 5 received an
OpenRouter 429 and remained missing under the original contract.

After a documented cool-off, one separately frozen operational retry used the
same packet, prompt, schema, Gemini model, and routing. It succeeded with two
source-supported records. The original 429 remains preserved.

Terminal vector:

| dimension | result |
| --- | ---: |
| eventual windows completed | 7/7 |
| first-attempt operational success | 6/7 |
| provider requests including cooled retry | 8 |
| raw model records | 14 |
| admitted records | 13 |
| quarantined exact prior-window duplicate | 1 |
| admitted stable alias references | 32/32 |
| protected target visibility | 1/1 |
| invalid admitted records | 0 |
| source-strength inflations | 0 |
| estimated cost | $0.00698625 |

## What we learned

The local semantic job works materially better for the minority relationship
that defeated the global reader. Deterministic machinery is useful for stable
source regions, role-valid citations, record-level admission, exact duplicate
identity, terminal custody, and replay. It must not decide whether something is
an alternative or whether two source-valid records mean the same thing.

Response-level all-or-nothing quarantine is too coarse. One invalid sibling
must not erase another valid record. Record-level custody is therefore required
in every future contract.

The lane produces 13 admitted records rather than the former 88–95 events, but
some source-valid fragmentation remains. For example, one broad alternative
may appear as two conditional branches or a pilot and its refinement. That is
an inspectability and later-consumer cost, not something deterministic code
should silently merge.

The first-attempt 429 also matters. OpenRouter's current official guidance says
rate-limit errors may provide `Retry-After`; future runners should preserve that
header and canonical error type. Evaluation retries must remain prospective,
bounded, and visible. There is no automatic semantic retry.

## Decision and next step

The exploration-local development case passes. This completes the semantic
mechanism test, not Phase 4.

A prospective transfer contract may now be designed. Transfer should combine:

- four relationship-explicit full-conversation readers;
- seven local exploration windows;
- record-level candidate custody;
- at most one explicitly evidenced operational retry;
- complete call, latency, cost, fan-out, duplicate, and source-review custody.

Transfer provider calls are not authorized by this result. Graph, live-skill,
runtime, final-output evaluation, and scalar quality or trust scores remain
out of scope.

## Continuation evidence

- provider-free v2 report:
  `research/reasoning-process-exploration-local-v2-2026-07-11/report.json`;
- single-window source review:
  `research/reasoning-process-exploration-local-probe-2026-07-11/source-review.json`;
- initial case replay and source review:
  `research/reasoning-process-exploration-local-case02-replay-2026-07-11/`;
- terminal result and review:
  `research/reasoning-process-exploration-local-terminal-2026-07-11/`;
- current-practice amendment:
  `docs/conversation-understanding/reasoning-process-exploration-local-current-practice-2026-07-11.md`.
