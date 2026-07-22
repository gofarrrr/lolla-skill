# How Lolla works

This document describes the current reachable system, not the full history of
everything in the repository. For current lifecycle status, start with
[PROJECT_STATUS.md](PROJECT_STATUS.md). For the evidence behind the map, use the
[Constitution Stage 0 addendum](docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md)
and its
[machine register](docs/evals/lolla-constitution-stage0-addendum-register-v1.json).

## The design boundary

```text
LLMs interpret messy conversational meaning.
Deterministic code owns identity, custody, exact evidence, bounds, replay,
budgets, graph traversal, and ledgers.
The graph introduces pressure; it does not certify relevance.
The reconsidering reasoner may apply, reject, or park pressure.
The receipt proves what process occurred, not that the result is wise.
The human owns the decision and its consequences.
```

Lolla is an experimental reasoning-pressure system. It is not a factuality
checker, an answer-quality certifier, an autonomous decision maker, or a
reliable general conversation-understanding system.

## One current system map

```text
ORDINARY LIVE PATH

available user/assistant prose
  -> capture and authoritative conversation.txt
  -> bounded initial-extraction view when needed
  -> model extraction
  -> ConversationContext / ConversationIR
  -> four pressure lanes
       tendency | model companion | frame | structural coverage
       ^ canonical mental-model registry and retrieval
       ^ relationship graph
       ^ constitutional graph survival: active set + reserve
  -> same-context reconsideration
  -> apply / reject / park custody
  -> revised answer + memo
  -> archive + manifests + health + usage/cost/privacy custody
  -> agent result + receipt
  -> read-only Observatory

BOUNDED COMPLETED-ARTIFACT SEAMS

archive --explicit offline CLI--> Decision Trail / Product Delta
archive --default-off flag-----> Decision Work resolver and sidecar
supplied interpretation -------> Decision Work validate/package/render/write
archive or sidecar ------------> Observatory / portable Markdown
Teacher packets ---------------> optional read-only projection

RESEARCH-ONLY OR DISCONNECTED

R3/R4 readers -> builders, frozen runners, replay, evidence
R4 readers -X-> ordinary live pipeline
R4 readers -X-> automatic Decision Work supply
Product Delta -X-> live answer
Mental Model Teacher -X-> ordinary pressure runtime
fixtures/tests -X-> proof of real-user usefulness
```

An artifact handoff is not the same as a runtime call or shared semantic
authority. A component can render supplied meaning without being able to
generate that meaning reliably.

## 1. Orchestration and run identity

The ordinary entry contract is [SKILL.md](SKILL.md). Detailed steps live in
[docs/skill/STEPS.md](docs/skill/STEPS.md), while setup and run-state helpers
live under `scripts/skill/`.

Setup creates a run ID, run-specific state, transcript and operator logs, and
guarded paths. Helpers reject stale or guessed run identity. This is mechanical
custody: it keeps one run from accidentally borrowing another run's artifacts.

The skill is a conductor. It captures source, invokes bounded scripts, presents
pressure to a reasoner, persists the reasoner's dispositions, and finalizes the
archive. It must not silently replace model judgment with keyword or
turn-count rules.

## 2. Source capture and bounded views

The authoritative conversational source is the complete prose available from
user and assistant turns. The declared source boundary excludes system
instructions, tool calls/results, file contents, and other non-prose host
context unless separately supplied.

For material above 80,000 characters, `scripts/run_extract.py` creates a
bounded initial-extraction view containing the first 3 and last 15 parsed
message blocks. That view is derivative. The original source remains
available, exact omitted windows are recorded, and later conversation-native
pressure input is loaded from the full authoritative transcript. Compactness
is not proof that omitted material was irrelevant, and full later input does
not prove that a partial initial scaffold caused no semantic loss.

Run health calls this condition `extraction_processing_view_partial` and
degrades the run. `capture_truncated` remains only as a deprecated boolean
compatibility alias; it does not mean `conversation.txt` was truncated.

The honest claim is “complete available user/assistant prose,” not “everything
the host agent saw” and not “complete semantic comprehension.”

## 3. Provisional extraction

A model interprets the decision situation and code normalizes the result into
`ConversationContext` and `ConversationIR`. These objects support the live
pressure pipeline, but their semantic fields remain provisional model output.

Strict schemas and local admission can establish that fields exist, types are
valid, bounds are respected, and source references resolve. They cannot prove
that a conversational role, adoption state, chronology, or materiality judgment
is correct.

The system currently has no trustworthy arbitrary-run longitudinal reader for
all Decision Trail fields.

## 4. Four pressure lanes

The live pipeline in `engine/system_b/pipeline.py` and `scripts/run_pipeline.py`
creates four distinct forms of challenge:

1. **Tendency pressure** surfaces candidate cognitive tendencies and concrete
   reversal or protection questions.
2. **Mental-model companion** presents candidate lenses, failure modes,
   antagonists, and premortem questions.
3. **Frame pressure** examines assumptions embedded in the question and
   counterfactual frames suppressed by it.
4. **Structural coverage** identifies dimensions the answer may not have
   entered and questions only the decision maker can answer.

The lanes are separate jobs with different products, but “separate” does not
prove statistically independent errors or reliable semantic accuracy. Their
outputs are pressure hypotheses.

## 5. Mental-model substrate and constitutional graph survival

The repository contains all 222 canonical Markdown sources, reviewed model and
relation curation, explicit source-anchor and compiler-input manifests, the
published model and relationship projections, optional activation embeddings,
and the candidate-only compiler needed to reproduce the published graph bytes.
No other checkout is needed. Deterministic code controls canonical IDs,
provenance, authored direction, traversal, deduplication, ordering under
declared nonsemantic rules, and volume bounds.

Current consumers load one immutable published-substrate snapshot. The snapshot
owns exact model and relation identity, source order, available custody, and
outgoing, incoming-reference, and incident indexes without reversing authored
edges. It does not compile, repair aliases, rank models, allocate pressure, or
call a provider.

One named, versioned planner and policy snapshot declare the current policy:
six direct-active candidates, expansion from direct-active seeds only, authored
outgoing relations only, one hop, antagonist/tension/ally slots, deterministic
ordering and deduplication, and explicit reserve. For compatibility, the
current wrapper renders that plan through the frozen historical serializer and
asserts that identities match. The live pipeline also declares a degraded
raw-payload fallback when no published snapshot is available. This is one
policy contract, not one physical implementation owner. Exact active and
reserve output is preserved for all 163 frozen corpus windows.

Constitution v5 requires bounded graph candidates to survive before a
probabilistic verifier can remove them. The live system therefore writes an
active pressure portfolio plus reserve. The reconsidering reasoner sees every
active item and must apply, reject, or park it.

This is the key distinction:

- graph recall is a hypothesis, not relevance proof;
- graph recall proves identity and reachability;
- it does not prove relevance;
- rejection is a valid outcome;
- application does not prove the model correct;
- reserve is capacity custody, not semantic rejection.

A prospective provider-free custody projection can serialize every exact path
inside that same bounded scope, including convergent paths that the current
outer active item does not carry. It preserves current active identity and
order but is deliberately not connected to the live reasoner, receipt,
Decision Trail, Atlas, or Observatory. Incoming-reference pressure, two-hop
traversal, graph-wide summaries, and new ranking policies remain separate
experiments, not latent current behavior.

The operational boundary and validation commands are in
[references/knowledge-substrate-operations.md](references/knowledge-substrate-operations.md).

## 6. Reconsideration and disposition

The reasoner receives the authoritative conversation plus bounded pressure and
updates its position. Every active constitutional pressure item receives one
of three dispositions:

- `apply`: it earns a visible shift, test, condition, guardrail, or decision
  question;
- `reject`: the strongest plausible application fails, with the failed
  condition and forcing risk recorded;
- `park`: evidence or timing is insufficient, with a reopening condition.

The live reconsideration occurs in the same conversational context. It is real
friction and auditable custody, but it is not independent validation. Same-
context rationalization remains a known risk.

Constitutional graph survival only proves that bounded candidates reached this reasoner; it does not prove that the authoring trajectory seriously tested disruptive pressure. A fresh consumer is research-only and is not automatically better: it can inherit the supplied vanilla frame or force selected noise into the answer. The provider-free
[consumer-context contract](docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json) compares pressure-specific deltas in isolated trajectory continuations and fresh reconstructions before any context architecture change.

## 7. Revision, archive, receipts, and health

A complete ordinary run persists a revised answer, memo, disposition records,
pressure-check state, health, usage, provider and privacy metadata, archive
manifest, `agent_result.json`, `evaluation.json`, and `reasoning_trace.json`.
`agent_result.json` separately reports authoritative source preservation and
initial extraction coverage under `source_coverage`.

State semantics are explicit:

- `complete`: required work and artifacts exist;
- `completed_zero`: a job ran and returned an admitted zero result;
- `partial`: some required work is absent or degraded;
- `failed`: a terminal failure occurred;
- `missing`: no result exists.

Missing is not zero. Schema-valid zero is not automatically semantically
correct. A clean receipt proves mechanical completion and declared custody, not
answer quality.

## 8. Observatory

Observatory is a local read-only view over artifacts its adapters can locate.
It helps humans inspect a run, sidecar, or supported projection. It does not:

- change the archived run;
- create source authority;
- generate reliable conversation meaning;
- approve the revised answer;
- authorize downstream work.

Many Observatory documents describe implemented slices, UX reviews,
prototypes, and proposals. The lifecycle-organized entrypoint is
[docs/README.md](docs/README.md); titles alone do not prove product reachability.

## 9. Completed-artifact tools

### Decision Trail and Product Delta

Offline builders inspect existing completed-run artifacts. Checked-in-safe
views prefer hashes, source locators, declared fields, and missingness over raw
private prose. Product Delta can prepare review material about changes between
original and revised outputs, but preserved value and overcorrection remain
human judgments.

Neither system changes the live answer.

### Decision Work

Decision Work contains schemas, validators, packet builders, triage, safe
resolution, renderers, an explicit writer, and a default-off post-archive hook.
It can package supplied semantic interpretation. It does not have a trustworthy
general supplier for arbitrary conversations.

The post-archive hook is disabled unless explicitly enabled. It is nonblocking
and fails closed. A sidecar is derivative and operator-directed; it does not
authorize action.

### Mental Model Atlas and Teacher

The Atlas is a checked-in, source-bound Phase 1 interface candidate over the
canonical model and relation identities. Atlas V2 owns current repository
custody; V1 is frozen comparison evidence. The Abstraction source is primary
and is presented through five reviewed human chapters with persistent
orientation and an optional full-source mode. Dated relationship-curation
residue is kept in a collapsed appendix; compiled operational guidance and all
incident connections remain separately labelled, progressively disclosed
layers. The source is complete while the broader learning page remains partial.

Atlas remains undeployed and parked because founder visual acceptance, native
screen-reader review, publication rights, and real-user usefulness are open.
Teacher's wider lessons, journeys, packets, and learning-product hypothesis are
a separate parked family. Neither participates in the ordinary pressure
runtime.

## 10. Retired R4 readers

R3/R4 attempted to recover richer conversation state such as unresolved
matters and future reconsideration dependencies. The final R4 experiment
preserved two genuine findings but produced unsafe false positives on both
paired and separated task shapes. Separation did not remove opposite-surface
companions, and the separated dependency reader still misclassified governed
machinery.

The incremental R4 reader architecture is retired. Its sources, targets,
requests, responses, contracts, runners, manifests, and closeouts remain
immutable research evidence. It has no supported edge into the live skill or
automatic Decision Work supply.

Retirement does not mean every future conversation-understanding architecture
must fail. Reopening requires a materially different architecture, explicit
founder authorization, new source-first targets, and human semantic review—not
another prompt variant or R5 renaming.

## 11. Provider, privacy, and cost boundary

Running the live skill uses provider calls under the operator's credentials.
Provider routes, models, prices, structured-output behavior, and privacy
policies can change. The current live operating contract must be checked at run
time; old experiment routes and prices are historical evidence.

Repository development and experiments require separate founder authorization
bound to an exact contract, call maximum, and USD ceiling. No such development
authorization currently exists. Automatic retries, fallbacks, healing,
substitution, and auxiliary provider calls are forbidden unless the same exact
authorization permits them.

Secrets must never enter artifacts or Git. Only safe route policy,
response/generation identity, usage, cost, hashes, and redactions belong in
custody records.

## 12. Evidence ladder

Keep these evidence classes separate:

1. **Mechanical evidence:** code paths, schemas, hashes, tests, replay,
   manifests, health, and cost custody.
2. **Simulated semantic evidence:** protected targets and provider outputs on
   designed conversations.
3. **Human semantic evidence:** source-first judgments about meaning,
   authority, chronology, and value.
4. **Real-user usefulness evidence:** whether a consented user understands,
   trusts, corrects, and benefits from the product.
5. **Market evidence:** whether a coherent user group adopts or pays.

Lolla has strong mechanical evidence, mixed simulated semantic evidence, and
insufficient real-user and market evidence.

## 13. Current development sequence

The canonical restart roadmap is
[plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md](plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md).

The Stage 0.6 long-conversation source-coverage repair is complete. The next
eligible decision is whether to authorize a provider-free review of
checked-in-safe Decision Trail truthfulness. It is not authorization for a new
reader, private archive access, a provider run, runtime change, R4/R5,
automation, Teacher expansion, or integration.

The separate Atlas implementation is consolidated around one identity source.
Its 16-model orientation view is a bounded presentation of the
same records owned by the 222-model / 1,358-relation navigation index; selecting
a model builds its exact incident neighborhood, and model/relation routes retain
that identity even when no complete teaching page exists. Card-first artifacts
alone own complete model-page availability. The ordinary renderer is SVG;
Canvas and frozen fixtures require explicit review mode. The binding
achromatic design system uses one shared solid/dashed/double relationship
grammar and route-scoped styles. See the
[current Atlas custody V2 result](docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md)
and the [frozen V1 publication checkpoint](docs/product/lolla-mental-model-atlas-baseline-publication-result-2026-07-17.md).
The local first-viewport repair now awaits provider-free human re-review. Later Atlas
phases, deployment, Teacher journeys, provider use, and runtime or Observatory
links remain unauthorized.

## 14. Verification entrypoints

For the current architecture and public handoff:

```bash
PYTHONPATH=. python3 scripts/evals/validate_constitution_stage0_addendum_register.py \
  --register docs/evals/lolla-constitution-stage0-addendum-register-v1.json
PYTHONPATH=. python3 scripts/evals/validate_stage0_public_handoff.py
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
PYTHONPATH=. pytest -q tests/test_constitution_stage0_addendum_register.py \
  tests/test_stage0_public_handoff.py
PYTHONPATH=. pytest -q
```

Provider-free validation proves document and custody consistency. It does not
prove semantic correctness or product value.

## Where the detailed history lives

- [Current documentation map](docs/README.md)
- [Stage 0 architecture audit](docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md)
- [R4 product and architecture closeout](docs/conversation-understanding/lolla-r4-product-architecture-closeout-2026-07-14.md)
- [Evaluation and frozen research index](docs/evals/README.md)
- [Historical documentation guidance](docs/history/README.md)

Git history preserves the previous long-form README and HOW_IT_WORKS
chronology. The current root documents intentionally describe the reachable
system and point to historical evidence instead of replaying every experiment.
