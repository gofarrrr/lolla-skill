# Conversation-state extraction recovery plan

Status: recovery foundation complete; current semantic extraction design closed for material redesign  
Date: 2026-07-11

## Goal

Determine whether small, source-linked semantic extractors can jointly populate
the existing conversation-state handoff without repeating the monolithic
extractor's ownership, thread, source-strength, coverage, quote, and trajectory
failures.

The target representation remains unchanged. This plan changes how candidates
are proposed and composed, not what the deterministic graph receives.

## Sequence

### R1 — Typed source and provider projections

Status: complete.

- Define one typed candidate family for evidence references, contributions,
  threads, and constraints.
- Generate local validation and provider schemas from it.
- Add descriptions, explicit unclear/not-found states, and valid empty lists.
- Produce a provider compatibility report for the selected OpenRouter model.

Exit: no hand-maintained divergence; all provider-free schema tests pass.

Evidence: `engine/system_b/conversation_state_candidates.py` is the typed source
of truth for local parsing plus OpenAI and Gemini projections. Both projections
pass the frozen compatibility checks without a provider call. Compatibility is
not provider acceptance or semantic-quality evidence.

### R2 — Stable source catalog

Status: complete.

- Build deterministic turn and sentence/clause IDs without assigning relevance.
- Validate speaker, turn, exact excerpt, and source hash.
- Preserve unresolved or non-unique excerpt resolution as invalid evidence.

Exit: non-contiguous quote joins and wrong-turn citations cannot enter validated
candidates.

Evidence: all 70 messages in the five reviewed conversations receive stable
turn and sentence identities. Exact source excerpts resolve to one span;
non-contiguous joins are quarantined.

### R3 — Three micro-extraction contracts

Status: complete as provider-free contracts; automatic extraction remains
untested.

- Position/contribution candidates: who originated, developed, qualified,
  challenged, or accepted what.
- Focal thread/trajectory candidates: introduced, engaged, resolved,
  superseded, genuinely dropped, unclear, or not found.
- Atomic constraint candidates: one source-strength claim per record.

Each contract gets its own prompt, shallow schema, zero-call fixture replay,
failure custody, and separate coverage metrics. No call assembles the final
handoff.

Exit: reviewed packets can be decomposed into expected micro-results and
adversarial outputs fail for the intended reasons.

Evidence: 30 frozen prompt contracts cover three microtasks, five sources, and
two provider projections. Four adversarial fixtures test unsupported joint
ownership, non-contiguous evidence, explicit absence, and forbidden mixed
source strength.

### R4 — Deterministic compiler and candidate ledger

Status: complete.

- Persist every candidate and terminal state.
- Assemble only validated records by stable IDs.
- Do not semantically merge, deduplicate, or promote candidates.
- Require both speakers for joint ownership and resolution evidence for resolved
  threads.
- Quarantine invalid packets without an accepted observed path.

Exit: the existing five reviewed packets replay through decomposition and
reassembly without provenance or coverage loss.

Evidence: the ledger preserves 60 reviewed candidates and every terminal state.
Invalid evidence cannot receive an event snapshot or accepted observed path.
Compilation preserves five joint positions, five focal-thread trajectories,
and late Turn 7 contributions while permitting zero direct graph seeds.

### R5 — Cross-case provider-free eval design

Status: complete.

- Score each micro-extractor separately and the compiler as composition.
- Include all five designed cases so Case 03 cannot become the only tuning
  target.
- Preserve six existing axes and add candidate loss/invalid disposition.
- Freeze output mode, provider projection, examples, cost, and zero-retry rule.

Exit: only then decide whether a bounded provider call is justified.

Evidence: the frozen replay at
`research/conversation-state-recovery-v1-2026-07-11/` passes all five reviewed
cases and all four adversarial fixtures with zero provider calls, graph calls,
or runtime changes. The atomic rule exposed two legacy `mixed` constraints;
source review split them into four candidates, so the recovery corpus contains
45 atomic constraints rather than the legacy 43 records.

## What this establishes

The recovery path is mechanically ready for a prospective extractor test:

- one typed contract generates local and provider-facing shapes;
- complete source custody is available without preselecting relevance;
- semantic candidates remain separate until deterministic validation;
- abstention is a valid outcome;
- bad evidence fails closed;
- reviewed state can be reassembled without graph leakage.

It does **not** establish that a model can populate these contracts accurately.
The five targets were source-reviewed in the same development session and are
not independent gold. Schema compatibility is not provider acceptance. No
downstream-answer or graph value has been measured.

## Next explicit decision

The founder authorized one bounded, prospectively frozen extraction-only
experiment on Case 02. It is now closed after two of three permitted calls:

- positions reached inference but all three candidates were quarantined because
  every returned source ID omitted its literal `span-` prefix;
- the reviewed joint trajectory was again fragmented into separately user- and
  assistant-owned positions;
- the thread schema received HTTP 400 `INVALID_ARGUMENT` from Google AI Studio
  through OpenRouter before inference;
- the frozen operational stop rule prevented the constraint call;
- there were zero retries, graph, pipeline, evaluator, or runtime calls.

The next decision is whether to authorize a prospective transfer repair on Case
05. The repair should be OpenRouter-Gemini-specific: use the `anyOf` nullable
shape already accepted in the positions call, constrain model-facing span IDs
to the source catalog through the schema rather than silently adding a missing
prefix, and generically prevent a qualification from being split from the focal
plan it modifies. Direct-Gemini projection behavior should remain unchanged.
Case 02 must not be retried and the missing constraint call must not be executed
under the closed v1 contract. Full evidence is at
`research/conversation-state-microtask-probe-v1-2026-07-11/`.

The founder then authorized that exact Case 05 transfer test. The prospective
OpenRouter-Gemini adapter replaced the nullable type array with `anyOf`, added a
source-specific full-ID enum, retained direct-Gemini behavior, and changed the
call order to threads, constraints, positions. Google still returned HTTP 400
`INVALID_ARGUMENT` on the first thread call before inference. The stop rule
prevented the remaining two calls. This falsifies the nullable representation
as a sufficient repair but does not identify the exact provider cause or
measure semantic transfer.

The next recommended boundary is JSON object mode with the exact typed schema
in the prompt and unchanged local typed validation, source custody, candidate
ledger, and quarantine. This does not relax accepted-state admission; it moves
syntax enforcement away from the provider adapter that is blocking inference.
Any such call requires a new prospective contract and authorization. Case 05
must not be retried under v2. Full evidence is at
`research/conversation-state-microtask-probe-v2-2026-07-11/`.

The founder delegated the remaining experiment program. JSON mode then reached
all three readers on Case 05, but source-first review failed every semantic
family. One generic repair round transferred prospectively to Cases 01 and 04;
both also failed. Strict constraint recall remained 0.20–0.22, source strength
was inflated, thread trajectories were omitted, truncated, or falsely resolved,
and current positions were fragmented or polluted by adjacent disagreements.
The predefined material-redesign stop fired after 9 program calls and
$0.02172925. No further prompt tuning or calls are justified for the current
one-call-per-family design. See
`research/conversation-state-extraction-program-conclusion-2026-07-11/`.

## Explicit non-goals

- no graph calls or graph-schema growth;
- no full pipeline or downstream answer pair;
- no runtime integration;
- no new framework dependency;
- no hidden correction loop;
- no claim that more micro-prompts necessarily mean better understanding.
