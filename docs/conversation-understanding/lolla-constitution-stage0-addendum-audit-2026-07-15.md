# Lolla Constitution Stage 0 addendum audit

Date: 2026-07-15

Canonical base: `f4493e20634544addd6633d8e92a836c6488f61e`

Canonical tree: `83ba656bb41a8c3d6073d4967e8535db181ce3d5`

Status: complete provider-free architecture audit; local and unpublished

Selected conclusion: `preserve_live_pressure_and_custody_bound_optional_interpretation_retire_incremental_r4_restart_from_human_truthfulness_gate`

Provider calls: `0`

Provider cost: `$0.00`

## Executive conclusion

Lolla currently is a working, experimental reasoning-pressure skill with strong
run custody. Its ordinary path captures the available user/assistant prose,
creates a bounded semantic view, applies four kinds of pressure, preserves
constitutional graph pressure, asks the same conversational context to
reconsider, records apply/reject/park dispositions, and archives an inspectable
process record. That is more than a prototype diagram: the entrypoints, helper
calls, artifacts, health handling, archive, receipt, and read-only Observatory
are connected in code.

Lolla is not yet a trustworthy general conversation-understanding or Decision
Trail system. Complete available prose is preserved, but preservation is not
comprehension. Rich Decision Work reads are optional supplied interpretations,
fixture-backed projections, or fields needing human judgment. The sidecar can
validate, package, render, and explicitly write supplied meaning; it does not
reliably generate arbitrary-run meaning. The stopped R4 readers have no live
path, and A2 established that splitting their two surfaces did not remove the
unsafe companion behavior.

The trustworthy Stage 0 baseline is therefore:

- keep the live pressure loop and deterministic custody active;
- keep Decision Trail reports, Decision Work, portable views, Product Delta,
  and Observatory bounded by their actual optional/offline/read-only roles;
- preserve experiment runners and frozen evidence as research only;
- park Teacher and general Decision Work semantic generation;
- retire the incremental R4 reader architecture without deleting its evidence;
- treat usefulness, semantic completeness, and market value as unknown until a
  named human evidence gate is passed.

This addendum does not change Constitution v5 or runtime behavior. It changes
the cold-start map: a file, schema, fixture, import, or test no longer counts as
proof that a product capability is live.

## One canonical system map

```text
ORDINARY SUPPORTED SKILL PATH

available user/assistant prose
  -> capture + exact authoritative conversation.txt
  -> bounded processing view (only when needed; omissions recorded)
  -> LLM extraction -> ConversationContext / ConversationIR
  -> four live pressure lanes
       tendency | mental-model companion | frame | structural coverage
       ^ canonical model registry / retrieval / relationship graph
       ^ constitutional graph survival -> active set + reserve
  -> same-context reconsideration
  -> apply / reject / park ledger
  -> revised answer + memo
  -> archive + manifests + run health + usage/cost/privacy custody
  -> agent result + receipt
  -> Observatory (GET/read-only projection)

BOUNDED SEAMS FROM COMPLETED ARTIFACTS

archive --explicit offline CLI--> Decision Trail report / Product Delta
archive --default-off flag-----> Decision Work safe resolver + sidecar
supplied interpretation read --> Decision Work package/triage/render/write
archive/sidecar ---------------> Observatory / portable Markdown projections
Teacher packets ---------------> optional Observatory projection

RESEARCH-ONLY, TEST-ONLY, OR DISCONNECTED

R3/R4 readers -> eval builders/runners/frozen evidence only
R4 readers -X-> live pipeline
R4 readers -X-> automatic Decision Work semantic supply
Product Delta -X-> live output
Mental Model Teacher -X-> ordinary runtime pressure
fixtures/tests -X-> proof of product reachability
```

The seams matter. Several systems exchange artifacts without calling one
another. Decision Trail reports and Product Delta read completed-run artifacts.
Decision Work may consume references to those artifacts. Observatory reads the
resulting archive and sidecars. None of those handoffs makes the upstream
semantic judgment reliable or authorizes a downstream action.

## What actually exists

### Ordinary live components — `keep_active`

**Skill orchestration and run-state guards.** `SKILL.md`, `docs/skill/STEPS.md`,
and the `scripts/skill/` helpers define and enforce the supported sequence.
Helpers reject guessed paths and stale run identity. This is the ordinary entry
contract.

**Conversation capture and processing views.** The skill preserves the complete
available user/assistant prose as authoritative source. For long inputs,
`scripts/run_extract.py` creates a bounded processing view plus omission
metadata without replacing the source. System instructions, tool payloads, and
file contents are not automatically part of that source contract. The honest
claim is “complete available prose,” not “everything the agent ever saw.”

**Extraction, context, and IR.** A model interprets a bounded decision situation
and code normalizes turns, context, and IR. This is live and necessary, but its
semantic fields are provisional. The extractor is not a general longitudinal
conversation reader.

**Four pressure lanes.** The pipeline runs tendency pressure, the mental-model
companion, frame pressure, and structural coverage. These are the current
experimental product core for “pressure now.”

**Mental-model substrate and relationship graph.** Canonical model identity,
retrieval, optional embeddings, and deterministic relationships feed pressure.
Graph recall and canonical IDs prove identity and reachability, not relevance.

**Constitutional graph survival, active set, and reserve.** Graph-derived
pressure survives before probabilistic verification. The active/reserve split
and survival report are explicit. This is the key implemented Constitution-v5
repair.

**Reconsideration and dispositions.** Step 6 asks the same context to reconsider
and records apply/reject/park. The friction and ledger are real. Independent
semantic validation is not: same-context reconsideration can still rationalize
its prior answer.

**Revision, archive, receipts, health, usage, cost, provider, and privacy
custody.** The system writes revised output, memo, result, manifests, reasoning
trace, health, usage, and a functional receipt. This is strong mechanical
evidence. It proves the process record, not the wisdom or usefulness of the
answer.

### Supported but bounded components — `keep_bounded`

**Observatory.** The server implements GET-oriented views over current and
archived artifacts and adapters. It does not mutate the run or authorize work.
Its many product documents describe a larger design family; those document
titles must not be read as equivalent live capabilities.

**Decision Trail reports and portable views.** Offline builders create
checked-in-safe projections from structured completed-run artifacts. They
deliberately avoid raw private prose in safe mode and mark sections that need an
LLM or human. They support later inspection, not complete decision history.

**Product Delta.** Readiness, report, and specialist-packet builders operate on
completed artifacts. Product Delta does not change the live answer. Semantic
claims such as preserved value or overcorrection remain review judgments.

**Decision Work.** Brief, packet, triage, resolver, handoff, and explicit write
paths exist. The post-archive hook is guarded by
`LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`, defaults off, is nonblocking, and
fails closed. The operator runner and queue arrange supplied work. The sidecar
does not create reliable conversation meaning from nothing.

**Portable Markdown and agent-memory views.** These render bounded projections
and locators. They remain inspection aids; portability does not upgrade source
authority or action authorization.

### Research components — `preserve_research_only`

**R4 frozen evidence and custody harnesses.** Sources, priors, protected targets,
requests, raw responses, manifests, closeouts, runners, replay, and tests remain
valuable scientific evidence. The A2 decision remains
`separated_tasks_ineffective_companions_persist`.

**R3 and legacy reasoning-process readers.** Shard, role, stance, position, and
fresh-consumer work documents the search history. It is not the current product
reader and cannot silently supply live state.

**Evaluation and fake-transport machinery.** These are unusually strong assets:
hashes, call plans, target isolation, replay, budget guards, and first-terminal
evidence. Preserve them as experimental infrastructure without allowing them to
become semantic authority.

**Fixtures and test adapters.** They prove contract behavior under declared
inputs. They do not prove ordinary reachability, reliable population on real
runs, or user value.

### Parked components

**Mental Model Teacher.** Teacher contracts, renderers, lesson graphs, packets,
and Observatory projections exist. A specific current user job and usefulness
gate do not. Park expansion; retain code and artifacts.

**General Decision Work semantic generation.** The desired contract is detailed
and supplied-read intake is implemented. A trustworthy arbitrary-run supplier
is missing. Reopening requires a materially different semantic architecture
and source-first human evaluation, not a renamed R4 prompt.

### Retired component

**Incremental R4 residual and separated-surface readers.** R4 has no import,
call, artifact-consumer, or configuration edge into the ordinary skill.
Its provider-visible mapping exists only in experimental modules/builders.
Positive findings were recoverable, but false dependency and opposite-surface
companions persisted after separation. Stop using and extending this
architecture. Retirement does not authorize deletion.

### Explicit unknown

**Real-user and market value.** The repository has extensive mechanical and
simulated evidence, but insufficient canonical evidence that users make better
decisions, value the friction, understand later, or adopt the product. The
appropriate disposition is unknown, not optimism or abandonment.

## Connection audit

The machine register records 24 material or explicitly absent edges with
trigger, activation, contract, failure behavior, status, and exact evidence.
The main distinctions are:

| Connection class | Current examples | Meaning |
|---|---|---|
| direct runtime | capture -> extraction -> IR -> pressure | ordinary supported execution |
| dynamic runtime | provider boundary -> semantic pressure | bounded model interpretation with usage/cost custody |
| artifact handoff | dispositions -> archive; archive -> reports | components exchange durable artifacts without implying shared semantics |
| optional flagged hook | archive -> Decision Work sidecar | default off and fail closed |
| explicit operator | report/read -> sidecar write | supplied meaning, bounded target, no automatic action |
| offline builder | archive -> Decision Trail/Product Delta | completed-run evaluation only |
| read-only projection | archive/sidecar -> Observatory | inspection, not mutation |
| research runner | R4 evidence -> replay/runner | frozen experiment only |
| test-only | fixtures -> adapters | contract evidence, not product reachability |
| no connection | R4 -> live; R4 -> Decision Work; Product Delta -> live; Teacher -> live | absence is a product boundary |

Documentation most often disagrees with code by breadth rather than by a single
false statement. Root and product indexes enumerate years of implemented
slices, proposed slices, reviews, fixtures, and experiments in one visual
plane. The code shows a narrower system: one live pressure path, several
bounded projections/workflows, and a large research estate.

## Constitution-v5 addendum: rules 1–17

1. **Source before reduction — partially conforms.** Available prose is
   preserved and processing omissions are recorded. Non-prose agent context is
   outside capture.
2. **No compactness Goodhart — partially conforms.** Original bytes survive,
   but bounded views can still miss global semantic trajectory.
3. **Active set plus reserve — conforms.** Both are explicit artifacts.
4. **Real pressure, not friction theater — partially conforms.** Four lanes are
   real and inspectable; unique human value is not established.
5. **Apply/reject/park — conforms mechanically.** The ledger distinguishes
   consideration from absorption.
6. **LLMs interpret; code owns custody — partially conforms repository-wide.**
   The live boundary is sound; historical deterministic/experimental semantic
   machinery remains and must stay isolated.
7. **Graph pressure cannot be erased by a verifier — conforms.** Survival occurs
   before probabilistic verification.
8. **Unknown-unknown pressure — partially conforms.** Frame and structural
   lanes exist; novelty and usefulness are not human-proven.
9. **Private/public output boundary — conforms in current validators.** Private
   ledgers and live-output hygiene are checked.
10. **No false proof of work — partially conforms.** Receipts carry nonclaims;
    some broad documentation still makes mechanical density look product-like.
11. **Avoid same-context self-justification — partially conforms.** Protected
    experiments use stronger review custody; ordinary reconsideration remains
    same-context.
12. **Narrow reversible evidence gates — conforms.** Freeze order, manifests,
    stop rules, and closeouts are strong.
13. **Fresh current-practice claims — partially conforms.** Experiments freeze
    dated checks; ordinary provider/pricing prose can age.
14. **Global conversation visibility and role/modal fidelity — partially
    conforms.** Turns and source are preserved; a reliable rich longitudinal
    semantic read is missing.
15. **Stop local reinvention — conforms now.** R4 is closed and no incremental
    prompt/task-shape continuation is earned.
16. **Canonical identity, semantic applicability — partially conforms.** Live
    canonical IDs are controlled; historical aliases and readers remain visible.
17. **Constitutional graph survival — conforms.** The R2 repair is active and
    tested.

There is no newly discovered runtime violation requiring an emergency code
change. Immediate responses are documentary: publish the actual map, keep R4
isolated, preserve missingness, and stop presenting optional/research surfaces
as one integrated product. Later evidence gates address same-context review,
semantic completeness, and human usefulness.

The still-relevant product evils are premature relevance pruning in bounded
views, context dumping as a substitute for interpretation, compactness
Goodhart, forced pressure absorption, laundering non-consideration as reject,
friction theater, deterministic cognitive machinery, false proof of work,
same-context self-justification, stale-practice certainty, context-invisible
labels, hidden fan-in overload, local reinvention loops, canonical-looking
semantic drift, and probabilistic re-domestication of graph pressure. The last
is mechanically controlled; the others remain design and evidence checks.

## Decision Trail artifact coverage

The register audits 26 field groups. Coverage is deliberately non-scalar.

**Deterministically available:** pressure provenance; apply/reject/park
dispositions; artifact-level original/revised differences; privacy receipts;
missingness and health; source custody and hashes; declared human-review gates;
agent-inspection suitability; action-authorization prohibition.

These fields establish exact identity, presence, state, and provenance. They do
not decide what the conversation meant.

**Provisionally semantic:** decision shape, current direction, constraints, and
assumptions/unknowns are populated by the live extractor or completed-run
projection. They are usable as hypotheses with source references, not protected
truth.

**Human review required:** starting direction; assistant influence; user
adoption/rejection/qualification/deferral; option lifecycle; changes of mind;
stakeholders and values; preserved original value; lost value or
overcorrection. These require role, chronology, modal force, and value judgment.

**Private or locator-only:** user questions/challenges and supplied context often
live in `conversation.txt`. Checked-in-safe reports point to, hash, or summarize
safe structured artifacts rather than copying private prose.

**Unavailable or unsafe:** reliable arbitrary-run unresolved matters are
unavailable. Future reopen conditions from the retired R4 reader or an
unreviewed supplied read are unsafe for action. A displayed next action or
decision gate remains operator material, never authorization.

Empty, missing, partial, failed, and completed-zero are distinct throughout.
Missing semantic supply is not a quiet result. A zero-record review is not
correct merely because it is schema-valid. Observatory can display only what
its adapters receive; the sidecar can render only what its resolver or supplied
read provides.

## Product-value interpretation

### Pressure now

Implemented: capture, provisional extraction, four lanes, model substrate,
graph survival, active/reserve, reconsideration, and dispositions.

Mechanical evidence: strong. Semantic reliability: mixed and lane-specific.
Human usefulness: insufficient. Market evidence: absent.

### Understand later

Implemented: authoritative prose custody, archive, Decision Trail report,
portable projections, and optional Decision Work packaging.

Mechanical evidence: partial-to-strong. Semantic completeness: provisional or
human-required. A general conversation reader is not implemented.

### Inspect the process

Implemented: manifests, route/pressure provenance, ledgers, health, usage/cost,
receipt, archive, Observatory, and offline evaluation artifacts.

Mechanical evidence: strong. The constitutional promise is appropriately
limited: the record proves the process, not the wisdom of the decision.

The founder loop maps as follows:

- **preserve:** implemented within the declared prose capture boundary;
- **pressure:** implemented as an experimental four-lane core;
- **reconsider:** implemented in the same context, with independence unproven;
- **record:** implemented strongly for custody and partially for semantics.

That is a coherent product skeleton, not a finished product claim.

## Documentation-family findings

- Constitution v0-v5: binding, active.
- `SKILL.md` and `docs/skill/`: current live contract, active.
- root README/HOW_IT_WORKS: mixed current behavior and long historical
  chronology; keep as entrypoints but add a Stage 0 status pointer.
- conversation-understanding docs: mixed audits, contracts, results, and
  stopped research; status must be read per anchor.
- eval docs/research: frozen/historical and research-only.
- board/Decision Work: optional operator workflow with a missing general
  semantic supplier.
- product/Observatory/Teacher: Observatory is implemented read-only; Teacher
  and many UI slices are prototype, review, or proposal families.
- old roadmap: historical evidence, superseded for next-step guidance by the
  Stage 0 restart roadmap.
- reviews: review evidence, not runtime activation.
- the two founder drafts: unchanged during audit, noncanonical intent only.

## Disposition does not mean deletion

No code or evidence was deleted, moved, or normalized. `retire` means stop using
and extending the architecture. `park` means require a named evidence gate.
`preserve_research_only` means retain reproducibility and prevent automatic
product supply. `unknown` names missing evidence rather than forcing optimism.

## Immediate restart recommendation

The new roadmap has four gates and no automatic continuation. The first is a
provider-free, checked-in-safe truthfulness review of the Decision Trail
projection boundary. It asks whether a cold human reviewer can distinguish
source fact, provisional interpretation, missingness, and non-authorization
from existing completed-run fixtures. It must not build another reader.

The sole immediate founder decision is whether to publish this addendum and
authorize that first provider-free gate. Publication and the gate remain
separate mutations; this local audit authorizes neither automatically.

## Machine custody

The complete component, connection, Constitution, Decision Trail, product-value,
documentation-family, implementation-file, disposition, unknown, and nonclaim
records are in
`docs/evals/lolla-constitution-stage0-addendum-register-v1.json`.
`scripts/evals/validate_constitution_stage0_addendum_register.py` checks the
register without inferring semantics. It accounts for all 634 canonical Python
implementation files under `engine/system_b/`, `scripts/`, and `observatory/`
through explicit ordered assignments and excludes only the new audit validator
from the canonical-base inventory.

This addendum is an evaluation of Constitution v5. It is not Constitution v6.
