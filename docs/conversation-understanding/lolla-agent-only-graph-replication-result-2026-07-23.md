# Agent-only graph replication result

Date: 2026-07-23

Status: complete and honestly `not_evaluable`

Owner: existing offline Product Delta evaluation

Contract:
[`lolla-agent-only-graph-replication-contract-v1.json`](../evals/lolla-agent-only-graph-replication-contract-v1.json)

Plan:
[`lolla-agent-only-graph-replication-2026-07-23.md`](../../plans/lolla-agent-only-graph-replication-2026-07-23.md)

Machine result:
[`consolidated-diagnostic.json`](../../research/agent-only-graph-replication-2026-07-23/consolidated-diagnostic.json)

Repository provider/API calls: **0**

Repository provider/API cost: **$0.00**

Codex development contexts attempted: **10**—eight generation and two blind
review contexts. The two conditional post-reveal contexts did not start.
Codex's ambient platform route, tokens, and economic cost were unavailable to
the repository operator and are not reported as zero.

## Plain-language result

The graph question was not answered.

All eight answer-generation attempts worked. That means the new missingness
design repaired the earlier experiment's generation bottleneck: the system
successfully preserved four direct-only answers and four answers receiving the
exact current outgoing one-hop graph increment. All eight compiled against
their frozen candidate sets, and all eight neutral comparison pairs were
mechanically available.

The experiment then needed two independent blind reviewers. The first reviewer
returned a valid result. The second returned JSON, but used arrays for all 29
`cognitive_effect` fields where the frozen contract required one enum string.
The response-shape presentation showed the allowed enum values as a list, so a
fresh reviewer could reasonably read it as a multi-select field. That is an
evaluation-envelope ambiguity, not evidence that the review's meaning was bad.
The frozen validator nevertheless had to reject the response.

The second response was not repaired, healed, reformatted, or rerun. Its exact
first-terminal payload and a 29-check failure receipt are preserved. Because
the contract required two valid blind reviews, the availability gate closed
and the two post-reveal interpretation contexts did not start. The only honest
result is:

```text
not_evaluable
```

## What was inspected

The bounded run inspected exactly one checked-in synthetic decision case under:

- four new direct-only generation draws;
- four new direct-plus-current-one-hop generation draws;
- two direct/direct pairs;
- two graph/graph pairs;
- four aligned direct/graph pairs;
- the existing Product Delta qualification traps;
- the existing exact-duplicate null;
- the existing legitimate stand-down;
- two fresh, isolated, lineage-blind reviewer contexts.

Every generation and review context used the frozen packet for its role. No
context received a sibling output, sibling review, hidden pair role, or prior
result. The second review's failure was discovered by deterministic shape
validation over its untouched terminal response.

## Exact terminal states

| Stage | Frozen terminal state |
| --- | --- |
| Direct-only generation draws | 4 complete |
| Direct-plus-current-one-hop generation draws | 4 complete |
| Available neutral comparisons | 8 of 8 |
| Primary blind review | complete and shape-valid |
| Skeptical blind review | failed: 29 enum-shape checks |
| Post-reveal primary interpretation | not started |
| Post-reveal skeptical interpretation | not started |
| Replication interpretation | `not_evaluable` |

The primary review remains provisional agent evidence. It is preserved because
it happened, but one valid review cannot stand in for the required pair. The
invalid skeptical payload is preserved as terminal execution evidence and is
not partially mined for a graph conclusion.

## What changed

This result adds only offline Product Delta experiment custody:

- exact first-terminal generation outputs;
- a neutral blind-review packet and separately sealed lineage manifest;
- one valid blind review;
- one exact invalid blind-review payload plus failure receipt;
- deterministic import, validation, gate, and closeout machinery;
- focused regression tests;
- this result and cold-start documentation.

## What did not change

The run did not change:

- any of the 222 mental-model Markdown sources;
- any of the 1,358 curated directed relations;
- graph direction, hop depth, active/reserve policy, ranking, or traversal;
- the graph compiler, pressure planner, live skill, or reconsideration prompt;
- Decision Trail, Decision Work, Observatory, Atlas, or any interface;
- principal-human fields or private archives;
- provider routing or production policy.

The existing outgoing one-hop graph remains a bounded pressure source. The
result neither supports nor rejects incoming edges, two-hop traversal,
community search, embeddings, a graph database, or global graph exploration.

## Evidence class and limits

This is a checked-in-safe, agent-only, single-case Product Delta development
result. It establishes:

- first-terminal and failure custody;
- exact candidate/compiler admission for eight generations;
- reviewer lineage isolation;
- fail-closed behavior when one required review violates the response shape;
- zero retries, replacements, healing, or post-gate calls.

It does not establish:

- graph causation, relevance, correctness, value, or usefulness;
- that either answer condition is better;
- expected model behavior or a variance estimate;
- semantic correctness of the valid primary review;
- principal-human review or a source-first human target;
- F2/F3 completion;
- permission to alter the graph or runtime.

## Artifact custody

The important SHA-256 identities at closeout are:

| Artifact | SHA-256 |
| --- | --- |
| Frozen contract | `2b772fe4da84510c7bb9083c62038febe82c8f95d91ce3a07ff8153cb9fd2068` |
| Generation packets | `2292f1c2ff087d30032d18a1a43f382b30fb63a66fa6855b3785908d528ad68b` |
| Pre-output sealed manifest | `2a5e46e9eb66d533fb85ee85eeec7d94a342bc39947973f4f7f613264f9ca242` |
| Blind-review packet | `26d298f8c2f4d44ae9fce8704303e23d536d5d75c359d86a62d86b7db7a268ab` |
| Execution sealed manifest | `cfec80403cffec63e77416f5cf0695eb492ab8df970f0937a1e72fe2c777eb8a` |
| Primary blind review | `8fdd3eb60d03b3c07c9fe092fd3940acf4b4f53d019bcd64be991c1b96238ec6` |
| Skeptical terminal payload | `60f19ac3c2364db98709399d321f87fbae8967051b516143952b752c39b1fe84` |
| Skeptical failure receipt | `1ccd8a0caffa6a6bcddc480f0bf24a6b21409273efcaf97c93f72a37c667fe36` |
| Consolidated diagnostic | `6c2a5a603e6ade498466155f92590d8ba333be4d43e34f8d5ba5ddab97bc615a` |

## Next decision

Do not run another graph replication and do not change traversal on this
evidence.

The next graph-evaluation opportunity is narrower and earlier in the pipeline:
version the reviewer envelope so scalar enum fields are unambiguous and, where
the execution surface supports it, structurally enforced. Test that prospective
envelope provider-free with fixtures before freezing any new semantic run.
Breaking the large review into bounded role-specific jobs is another possible
design, but it must be compared against lost whole-packet context rather than
assumed to be safer.

Any new Codex semantic contexts, retry, corrected skeptical review, model
comparison, wider case, or graph change requires a new exact founder
authorization. July's checked-in-safe Stage 1 Decision Trail truthfulness
option remains separate, eligible, and unauthorized.
