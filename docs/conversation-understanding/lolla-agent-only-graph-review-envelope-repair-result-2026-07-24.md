# Agent-only graph reviewer-envelope repair result

Date: 2026-07-24

Status: provider-free structural repair complete; semantic rerun not authorized

Owner: existing offline Product Delta evaluation

Machine contract:
[`lolla-agent-only-graph-review-envelope-repair-contract-v1.json`](../evals/lolla-agent-only-graph-review-envelope-repair-contract-v1.json)

Plan:
[`lolla-agent-only-graph-review-envelope-repair-2026-07-24.md`](../../plans/lolla-agent-only-graph-review-envelope-repair-2026-07-24.md)

Fixture receipt:
[`fixture-validation-receipt.json`](../../research/agent-only-graph-review-envelope-repair-2026-07-24/fixture-validation-receipt.json)

Provider/API calls: **0**

Provider/API cost: **$0.00**

New Codex semantic contexts: **0**

## Plain-language result

The broken measuring cup has been replaced; the water has not been measured
again.

The previous graph replication preserved eight valid answers but lost one
required blind review because `cognitive_effect` was supposed to be one string
and came back as an array 29 times. The packet had shown possible values as a
list, so the difference between “choose one value from this list” and “return
this list-shaped field” was not clear enough.

The prospective v2 envelope now has one authoritative JSON Schema:

```json
{
  "type": "string",
  "enum": ["adds_burden", "adds_caution", "adds_test", "opens_path"]
}
```

The full schema contains every allowed value; the small excerpt only
illustrates the cardinality. Codex is instructed to use the schema through
`--output-schema`, and the first-terminal output must still pass local
deterministic admission.

The provider-free fixture result is exact:

| Fixture | Result |
| --- | ---: |
| Frozen valid scalar review adapted to v2 identity | 0 structural errors |
| Frozen invalid array review adapted to v2 identity | 29 structural errors |
| Errors specifically at array-shaped `cognitive_effect` fields | 29 |
| Primary post-reveal shape fixture | 0 structural errors |
| Skeptical post-reveal shape fixture | 0 structural errors |

This shows that the new envelope accepts the known valid shape and rejects
every occurrence of the known failure. It does not show that any review is
semantically correct.

## What was inspected

The repair hash-locks and validates the consumed:

- replication contract;
- blind-review packet;
- sealed execution manifest;
- valid primary first-terminal review;
- invalid skeptical first-terminal review;
- skeptical failure receipt;
- deterministic `not_evaluable` consolidation.

The repair also revalidated consumer-context contract v1 so this bounded
reviewer-envelope work is not confused with completing F2/F3, proving fresh
context better, forcing pressure absorption, or changing the live host.

At design time, the installed `codex-cli 0.144.5` exposed
`codex exec --output-schema`. Current official guidance describes that option
as requesting a final response conforming to a supplied JSON Schema. This
capability must be rechecked at any future execution because CLI behavior and
documentation can change. See
[OpenAI Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode.md).

## One causal change

Only the reviewer response boundary changes:

- old example-shaped response contract removed;
- lane-specific JSON Schema becomes the sole shape owner;
- enum fields declare `type: string`;
- Codex command templates include `--output-schema`;
- local schema-subset validation runs before the existing Product Delta
  validator.

The source, eight frozen answers, controls, answer-pair orientation, review
order, Product Delta atomic-move grammar, graph increment, graph lineage,
planner, compiler, and runtime are unchanged.

## Why the old review was not corrected

The skeptical payload is immutable first-terminal evidence. Reformatting its
arrays into strings would require choosing among values and would therefore
change meaning, not merely syntax. The repair uses that payload only as a
known-invalid shape fixture. Its observations do not enter a graph conclusion.

The valid historical primary review also cannot serve as one half of a new v2
pair. If a future run is authorized, both blind lanes must run fresh under the
same new schema. This avoids a selective retry after seeing one earlier result.

## Why the eight answers should be reused

The next question is whether the reviewer envelope can admit two valid
independent reviews over the already-frozen comparison. Generating more
answers would add new reasoner variation and obscure whether the envelope
repair worked. The prospective contract therefore freezes:

- zero generation contexts;
- two fresh blind-review contexts;
- two conditional post-reveal contexts;
- four new Codex contexts maximum;
- no retry, fallback, healing, replacement, reformatting, or semantic salvage.

Post-reveal may start only if both new blind reviews pass the structured schema
and the existing Product Delta validator.

## What changed

This result adds:

- a new Product Delta envelope builder and validator;
- two lane-specific blind-review schemas;
- two lane-specific post-reveal schemas;
- two blind packets with exact frozen semantic material;
- valid, invalid, and post-reveal structural fixtures;
- a machine-readable fixture receipt;
- an exact prospective run contract and authorization shape;
- regression tests and cold-start documentation.

## What did not change

Nothing changed in:

- the 222 mental-model Markdown sources;
- the 1,358 curated directed relations;
- graph direction, one-hop depth, slots, ordering, active/reserve policy, or
  traversal;
- the graph compiler or published artifacts;
- the live pressure planner, reasoner, skill, or receipt;
- Decision Trail, Decision Work, Observatory, Atlas, or an interface;
- provider routing, private archives, or principal-human fields;
- the frozen graph-replication result.

## Evidence class and limits

This is provider-free development-fixture and structural-contract evidence. It
establishes that:

- the consumed checkpoint is hash-locked;
- semantic review material is preserved exactly;
- the ambiguous v1 example shape is absent from v2 packets;
- the known scalar review passes;
- all 29 known array fields fail as strings are required;
- future command templates have a structural-output boundary;
- no unauthorized semantic result exists.

It does not establish:

- semantic correctness;
- reviewer reliability;
- graph causation, relevance, value, or usefulness;
- answer quality or a winning arm;
- expected model behavior;
- principal-human evidence;
- F2/F3 completion;
- permission to run another context or alter traversal.

## Next decision

The measuring boundary is ready, but the measurement remains separately
authorized.

The exact frozen authorization string is:

```text
AUTHORIZE_LOLLA_GRAPH_REVIEW_ENVELOPE_V2: reuse_frozen_generation_outputs=true; blind_review_contexts=2; conditional_post_reveal_contexts=2; maximum_codex_contexts=4; repository_provider_api_calls=0; repository_provider_api_cost_usd=0.00; no_retry=true
```

Until that exact scope is authorized, the correct state is:

```text
provider_free_repair_complete_semantic_execution_not_authorized
```

Do not expand the graph from this result. A better-shaped measuring instrument
is not evidence that the graph helped.
