# Agent-only graph review nonclaim-custody V3 repair result

Date: 2026-07-24

Status: provider-free repair complete; semantic execution not authorized

Owner: existing offline Product Delta evaluation

Machine contract:
[`lolla-agent-only-graph-review-nonclaim-custody-v3-contract-v1.json`](../evals/lolla-agent-only-graph-review-nonclaim-custody-v3-contract-v1.json)

Plan:
[`lolla-agent-only-graph-review-nonclaim-custody-v3-repair-2026-07-24.md`](../../plans/lolla-agent-only-graph-review-nonclaim-custody-v3-repair-2026-07-24.md)

Fixture receipt:
[`fixture-validation-receipt.json`](../../research/agent-only-graph-review-nonclaim-custody-v3-2026-07-24/fixture-validation-receipt.json)

Provider/API calls: **0**

Provider/API cost: **$0.00**

Codex semantic contexts: **0**

## Plain-language result

The V2 experiment asked each final reviewer to copy ten warnings back into its
answer. Both reviewers paraphrased those warnings. The experiment rejected the
answers even though text copying was not the graph question.

V3 removes that copying job.

The exact warnings now live only in a deterministic input-custody block. That
block gives every warning an ID, preserves its text and order, records the
count, and hashes the complete ordered list. The model's response contains no
warning echo and no forced `true` acknowledgments.

In simple terms:

```text
Old:
  We handed the reviewer ten rules.
  Then we asked the reviewer to recite the rules perfectly.

New:
  We hand the reviewer ten rules.
  The receipt proves exactly which rules were handed over.
  The reviewer spends its response on the actual comparison.
```

The receipt proves input presentation. It does not prove that a model
understood or obeyed the rules.

## Falsifiable provider-free result

The frozen question was:

> Can deterministic input-packet custody preserve the exact ten post-reveal
> nonclaims while the model-authored response omits every nonclaim echo field?

Within development fixtures, **yes**:

| Check | Result |
| --- | --- |
| Primary V3 response fixture without echo | passes |
| Skeptical V3 response fixture without echo | passes |
| Primary legacy response with echo | rejected as one unexpected property |
| Skeptical legacy response with echo | rejected as one unexpected property |
| Primary exact input-custody block | zero errors |
| Skeptical exact input-custody block | zero errors |
| Mutated nonclaim statement | exact statement and hash checks fail |
| Provider/API calls | 0 |
| Semantic contexts | 0 |

This establishes the contract mechanics only.

## Why input custody is the correct owner

Deterministic machinery can honestly prove:

- the exact ten statements included in an input packet;
- their stable IDs;
- their order and count;
- their byte-derived hash;
- the schema supplied to the output boundary;
- whether a captured output conformed to that schema.

It cannot prove:

- that the reasoner understood a warning;
- that the reasoner followed it;
- that a conclusion is semantically cautious;
- that the graph caused a difference;
- that an answer is better or useful.

A model-authored acknowledgment is self-report. A schema-forced boolean is
shape. Neither is stronger evidence than exact input custody.

## What changed

The prospective V3 package adds:

- two response schemas with the V2 semantic fields but no
  `nonclaims_acknowledged`;
- two deterministic packets with `NC-01` through `NC-10`, exact statements,
  count, order, and SHA-256;
- two valid no-echo fixtures;
- two rejected legacy-echo fixtures;
- one provider-free fixture receipt;
- one machine contract and prospective two-context boundary;
- a provider-free builder, validator, CLI, and tests;
- one backward-compatible option in the existing Product Delta post-reveal
  validator so historical V1/V2 calls continue requiring the echo while V3
  does not.

## What did not change

Nothing changed in:

- either failed V2 terminal payload;
- either V2 failure receipt;
- the V2 consolidated `not_evaluable` result;
- either valid V2 blind review;
- source conversation or answer content;
- the 222 mental-model Markdown files;
- the 1,358 graph relations;
- graph direction, traversal, ranking, active set, or reserve;
- graph compiler, immutable reader, or pressure planner;
- live Lolla prompts, skill, reconsideration, dispositions, receipt, or
  archive behavior;
- Decision Trail, Decision Work, Observatory, Atlas, Teacher, or an interface;
- provider routing or production policy.

No graph decision, answer winner, score, vote, or usefulness claim was
created.

## Frozen custody

The V3 builder byte- and hash-locks twelve V2 inputs:

- the consumed V2 contract;
- both V2 post-reveal schemas;
- both V2 structural fixtures;
- both V2 post-reveal packets;
- both valid V2 blind reviews;
- both V2 post-reveal failure receipts;
- the V2 consolidated diagnostic.

V3 therefore cannot silently change the evidence whose response boundary it is
repairing.

## Official structured-output recheck

On 2026-07-24:

- the installed CLI was `codex-cli 0.144.5`;
- `codex exec --help` exposed `--output-schema` and
  `--output-last-message`;
- the current official Codex manual documented `--output-schema` as requesting
  a final response conforming to a supplied JSON Schema and `-o` as writing
  the final message.

This supports the prospective shape boundary. A future run must recheck the
current CLI and official guidance because tool behavior can change.

## Evidence class and limitations

This is a provider-free development-contract result.

It establishes:

- exact V2 source custody;
- exact V3 nonclaim input custody;
- removal of model-authored echo from the response schema;
- backward-compatible historical validation;
- deterministic failure on input-custody drift;
- zero semantic contexts and zero repository provider calls.

It does not establish:

- that a future model will follow the nonclaims;
- that a future V3 response will be semantically valid;
- graph causation, relevance, correctness, value, or usefulness;
- answer quality or a preferred condition;
- expected model behavior;
- principal-human evidence;
- F2/F3 completion;
- permission to change traversal or runtime.

## Verification

The provider-free handoff passed:

- 5,197 repository tests and all 93 subtests;
- 51 focused V3, V2, replication, lifecycle, and handoff tests;
- 89 prescribed Stage 0 public-handoff tests;
- Constitution register validation over 678 implementation files;
- public cold-start validation with 17 questions and 152 local links;
- repository-local authority scan over 2,333 active files with zero active
  retired-location violations;
- self-contained skill validation over 222 models, 1,358 relations, and 163
  policy windows with published byte equivalence;
- changed JSON parsing and `git diff --check`.

The suite retained one existing `datetime.utcnow()` deprecation warning. No
failure was suppressed.

## Next decision

Do not change the graph and do not reinterpret the failed V2 payloads.

The provider-free repair is complete. A possible next step is the separately
authorized two-context V3 post-reveal run frozen in the machine contract. It
would reuse both valid V2 blind reviews and run only two fresh post-reveal
contexts.

That run is not authorized by this result. “Continue,” a green fixture, or the
existence of the runner contract is not authorization.
