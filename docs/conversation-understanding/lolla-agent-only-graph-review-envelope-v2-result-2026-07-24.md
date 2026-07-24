# Agent-only graph review-envelope v2 result

Date: 2026-07-24

Status: complete and honestly `not_evaluable`

Owner: existing offline Product Delta evaluation

Machine result:
[`consolidated-diagnostic.json`](../../research/agent-only-graph-review-envelope-repair-2026-07-24/consolidated-diagnostic.json)

Frozen repair contract:
[`lolla-agent-only-graph-review-envelope-repair-contract-v1.json`](../evals/lolla-agent-only-graph-review-envelope-repair-contract-v1.json)

Repair plan:
[`lolla-agent-only-graph-review-envelope-repair-2026-07-24.md`](../../plans/lolla-agent-only-graph-review-envelope-repair-2026-07-24.md)

Repository publication:
[PR #396](https://github.com/gofarrrr/lolla-skill/pull/396)

Repository provider/API calls: **0**

Repository provider/API cost: **$0.00**

Codex development contexts attempted: **4**—two blind reviews and two
conditional post-reveal interpretations. All four returned first-terminal
payloads with process exit code zero. No context was retried, replaced, healed,
reformatted, or semantically salvaged. Codex's platform route, token
accounting, and economic cost were unavailable to the repository operator and
are not reported as zero.

## Plain-language result

The graph question is still unanswered.

The first repair worked. Both fresh blind reviewers returned the required
single-string enum fields, including every `cognitive_effect`, and both
payloads passed the new lane schema plus the existing Product Delta validator.
That opened the post-reveal gate honestly.

The final step then found a different measuring-envelope defect. Each
post-reveal reviewer returned the required ten-string
`nonclaims_acknowledged` array, but each rewrote the nonclaims instead of
copying the exact frozen wording. The JSON Schema controlled type and length;
it did not control the exact ten values. The existing deterministic validator
correctly rejected both payloads with one error:

```text
post-reveal nonclaims drifted
```

Both exact first-terminal payloads and both failure receipts are preserved.
The no-retry contract forbids correcting the wording or extracting a partial
semantic conclusion from the invalid payloads. The only valid overall state
is:

```text
not_evaluable
```

In five-year-old terms: we fixed the cup so it no longer spills at the first
pour. Both first pours worked. At the final label check, both labels used
different words from the label we had frozen. We kept the cups and labels
exactly as they were, but we cannot call the measurement finished.

## Exact authorized sequence

The founder authorized exactly:

```text
AUTHORIZE_LOLLA_GRAPH_REVIEW_ENVELOPE_V2: reuse_frozen_generation_outputs=true; blind_review_contexts=2; conditional_post_reveal_contexts=2; maximum_codex_contexts=4; repository_provider_api_calls=0; repository_provider_api_cost_usd=0.00; no_retry=true
```

The run used:

1. zero answer-generation contexts;
2. the same eight frozen, admitted replication answers;
3. two isolated blind-review contexts, one primary and one skeptical;
4. deterministic schema and existing Product Delta admission;
5. two isolated post-reveal contexts only after both blind reviews passed;
6. exact first-terminal capture at every context boundary;
7. zero retry, fallback, healing, replacement, reformatting, or semantic
   salvage.

Each context ran in a separate empty external temporary directory with
read-only sandboxing. A blind reviewer saw only its lane packet and schema. A
post-reveal reviewer saw only its own frozen blind review, deterministic
lineage reveal, availability receipt, and lane schema. No context received the
sibling review.

## Terminal-state ledger

| Stage | Primary | Skeptical |
| --- | --- | --- |
| Blind review process | exit 0 | exit 0 |
| Blind review schema and Product Delta admission | complete, 0 errors | complete, 0 errors |
| Post-reveal gate | opened | opened |
| Post-reveal process | exit 0 | exit 0 |
| Post-reveal admission | failed, 1 exact-nonclaim error | failed, 1 exact-nonclaim error |
| Retry or repair | none | none |
| Semantic use of invalid post-reveal payload | none | none |

The raw external capture hashes and imported repository hashes match for all
four contexts.

## What the two valid blind reviews recorded

The blind reviews are valid provisional agent observations. They are preserved
because they passed their frozen contract. They do not become a graph result
without the required valid post-reveal pair.

After both blind reviews froze, deterministic lineage showed:

| Frozen pair | Pair role | Primary material read | Skeptical material read |
| --- | --- | --- | --- |
| `within-direct-3-4` | within direct | present | absent |
| `within-direct-5-6` | within direct | present | present |
| `within-graph-3-4` | within graph | absent | absent |
| `within-graph-5-6` | within graph | present | present |
| `cross-3` | direct versus graph | present | absent |
| `cross-4` | direct versus graph | absent | absent |
| `cross-5` | direct versus graph | present | absent |
| `cross-6` | direct versus graph | present | present |

The controls also remained inspectable:

- both reviewers marked the exact duplicate's material difference `absent`;
- both supported the legitimate stand-down;
- the primary qualification lane returned seven
  `sufficient_for_bounded_comparison`, one `blocked_thin_context`, and two
  `needs_human_review`;
- the skeptical qualification lane returned eight
  `sufficient_for_bounded_comparison`, one `blocked_thin_context`, and one
  `needs_human_review`.

These rows show both within-condition variation and reviewer disagreement.
They are not counted into a score, significance test, vote, winning condition,
or graph attribution. The two invalid post-reveal payloads are not mined to
complete that interpretation.

## Why this is not evidence against the graph

The failure occurred in the evaluator's final response boundary, not in:

- the 222 mental-model Markdown sources;
- the 1,358 curated directed relations;
- graph direction, one-hop depth, relationship slots, ordering, or reserve;
- candidate survival;
- answer generation;
- blind comparison availability;
- the two valid blind-review payloads.

The run therefore does not show that the graph works, fails, helps, harms, is
relevant, or should expand. It shows that the automated experiment still has a
contract-custody defect after blind review.

## What changed

This result adds only offline Product Delta execution custody:

- exact v2 primary and skeptical blind reviews;
- success receipts for both blind contexts;
- deterministic lane-specific post-reveal packets;
- exact primary and skeptical post-reveal terminal payloads;
- failure receipts for both exact-nonclaim mismatches;
- deterministic `not_evaluable` consolidation;
- result import, validation, gating, and consolidation machinery;
- focused regression tests and current handoff documentation.

The deterministic result machinery was committed and pushed before any of the
four semantic contexts started. The semantic outputs therefore did not alter
their own admission rules.

## What did not change

Nothing changed in:

- mental-model source prose or relation curation;
- published graph bytes;
- graph direction, traversal, ranking, direct cap, active set, or reserve;
- graph compiler, published-substrate reader, or pressure planner;
- live Lolla prompts, reconsideration, skill, receipt, or archive behavior;
- Decision Trail, Decision Work, Observatory, Atlas, Teacher, or an interface;
- private archives or principal-human fields;
- provider routes or production policy.

No score, vote, answer winner, graph decision, product claim, or live
connection was created.

## Evidence and custody limits

This is checked-in-safe, agent-only, single-case Product Delta development
evidence. It establishes:

- exact authorization and four-context ceiling compliance;
- first-terminal capture and byte-exact import;
- zero retries and zero repository provider calls;
- v2 scalar-enum success for both blind reviews;
- deterministic sibling isolation and lineage gating;
- fail-closed exact-nonclaim validation at the post-reveal boundary;
- preservation of valid blind vectors, invalid terminal payloads, failure
  receipts, and missing semantic conclusion.

It does not establish:

- graph causation, relevance, correctness, value, or usefulness;
- answer quality or a preferred condition;
- expected model behavior or a variance estimate;
- principal-human evidence or a source-first human target;
- F2/F3 completion;
- permission to change or expand graph traversal;
- permission for another semantic context.

## Key artifact identities

| Artifact | SHA-256 |
| --- | --- |
| Primary blind review | `7717938872cd52240a67f1f5fb46b396481a12e25433aaa811901302527d0c54` |
| Skeptical blind review | `dda30d94f4fae03f39af249cd33be517236c1c930955936c33fb8166af770fc1` |
| Primary post-reveal packet | `88bfc70504f03fc9d137db7fa434391bdedb20d382618b6f6f11d2743997e3e1` |
| Skeptical post-reveal packet | `4d95805d7c56f4745c9bc0e2f329e1ea7c11d3f3c21ab628b81295f82ea23b50` |
| Primary post-reveal terminal payload | `d7a6ccb841a574561afc97569779096efb89de1176ba8fe0a95bc22948109e8f` |
| Primary post-reveal failure receipt | `62a0788a4bbed4759db7e73253d08ea4c4ead8746955b128855bb2c22cf3dedc` |
| Skeptical post-reveal terminal payload | `3ddade50b9ef0653156c8490d004e008c7328d494974328e54573000880895e6` |
| Skeptical post-reveal failure receipt | `66fc78806dfdc3ceb0a64d71f8bbffd3c5a3a1d9c46fae1bbdb4fe722de7e68b` |
| Consolidated diagnostic | `5d9d72645be12d17864c102b86336871387bce37b54a6e5ea98d789ca56fdf27` |

## Next opportunity

Do not rerun either lane and do not expand the graph.

The smallest eligible next task is provider-free only: decide how the
post-reveal response should preserve nonclaims without asking a model to
restate free text. One prospective option is a schema-owned object of fixed,
named boolean acknowledgments; another is to keep nonclaims entirely as
input-side guardrails and remove the exact-text echo from the generated
response. That design choice must be tested with fixtures and current
structured-output support before any new semantic authorization.

This result does not select that design and does not authorize its execution.
Any new Codex semantic context, corrected acknowledgment, retry, model
comparison, wider case, graph change, or runtime change requires a new exact
founder authorization.
