# Subagent Cognitive Worker Architecture Vision

Date: 2026-05-15

Status: research architecture document. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, or the canonical
knowledge base.

Latest local contract slice:

- `research/pre-step6-cognitive-worker-system-plan-2026-05-16.md`
- `research/pre-step6-comparison-subagent-readout-2026-05-16.md`
- `research/pre-step6-handoff-best-practices-as-of-2026-05-16.md`
- `research/provider-use-operating-structure-2026-05-15.md`
- `research/lane1-reasoning-bridge-subagent-slice-readout-2026-05-15.md`
- `research/subagent-cognitive-worker-contract-slice-2026-05-15.md`
- `research/subagent-cognitive-worker-live-replay-readout-2026-05-15.md`
- `research/subscription-orchestrator-handoff-local-test-readout-2026-05-15.md`

2026-05-16 update:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-comparison-subagent-readout-2026-05-16.md
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
```

is now the central system-plan handover. The older `CognitiveWorkpack`,
`CognitiveWorkerPacket`, and `cognition_dossier` names below are historical
research scaffolding. They preserve lessons from the first local slice.

The candidate family remains:

```text
reasoning_workpack.v1 -> reasoning_artifact.v1 -> reasoning_bundle.v1
```

But the 2026-05-16 corrective pass demotes `reasoning_bundle.v1` from default
next build to optional challenger. Raw `reasoning_artifact.v1` consumption
discipline is now the baseline to beat, and any subagent should be treated as a
bounded worker-as-tool call, not a true handoff.

## Purpose

This document records the current priority shift.

The book-question corpus can wait.

The more important architecture question is:

```text
How do we provide Claude Code, or any future orchestrator, only the relevant
information it needs to reason well?
```

The likely answer is not to keep subagents mainly as an after-check. The current
corrected direction is to first test raw artifact consumption discipline, then
use subagents only as narrow cognitive workers when the admission gate proves
Step 6 needs a bounded extra call before final synthesis.

They should do thinking on separate parts of the system output, then provide
compact, source-bound, relevance-filtered pressure to the reasoner.

## Current Product Shape

Current stable product behavior:

```text
conversation
  -> deterministic/LLM lane pipeline
  -> Step 6 final reconsideration
  -> Step 6b persistence / V60 ledger
  -> Step 7 pressure-check subagents
  -> Step 8 comparison
  -> memo / observatory / archive
```

This works as a safety mechanism.

But it is late.

The subagents currently inspect the answer after the main reasoner has already
formed it. That can catch misses, but it does not solve the deeper context
engineering problem:

```text
the final reasoner still receives too much mixed material and has to decide what
is relevant while also writing the answer.
```

## Target Direction

The target research architecture is:

```text
conversation
  -> lane cognition, embeddings, selected chunks, source evidence
  -> deterministic custody / caps / validation
  -> relevance assembly
  -> parallel subagent cognitive workers
  -> compact reasoning_artifact.v1 outputs
  -> deterministic validation / dedupe / caps / receipts
  -> reasoning_bundle.v1 arbitration index
  -> Step 6 final reasoner
  -> optional post-hoc check only during research
```

In this shape, subagents are not "judges after the fact."

They are brains assigned to narrow cognitive work before the final reasoner
writes.

The final reasoner still owns synthesis, voice, tradeoffs, and the final public
answer. Subagents do not write the answer and do not decide truth.

## Why This Is Different From Moving Step 7 Earlier

Do not move current Step 7 earlier as-is.

Current Step 7 asks:

```text
What did Step 6 miss?
```

The new worker layer asks:

```text
Given this selected slice of system evidence, what should the final reasoner
seriously consider, use, question, set aside, or keep private?
```

That is a different task.

It requires different prompts, different schemas, different validation, and
different evaluation.

## What Subagents Should Own

Subagents are useful where judgment-heavy compression is needed.

Candidate worker jobs:

1. Lane-pressure worker
   - Receives one lane card plus its source evidence and relevant chunks.
   - Decides what, if anything, matters for final reasoning.
   - Produces compact pressure, not a lane summary.

2. Inquiry/boundary worker
   - Receives selected pressures.
   - Produces the question or evidence gate that controls how pressure should
     be used.
   - Includes one anti-confirmation or alternative-frame check.

3. Source/overclaim worker
   - Receives proposed pressure and source evidence.
   - Identifies what can be said, what must be softened, and what should be
     set aside.

4. Compression worker
   - Receives multiple valid worker outputs.
   - Compresses them into a small handoff dossier.
   - Removes duplication, generic caution, machinery language, and low-value
     material.

These workers can be tested one at a time. The first slice should not build all
four.

The 2026-05-16 core plan narrows the first future implementation to two worker
types only:

```text
boundary/evidence-gate worker
duplicate/priority worker
```

That narrowing is deliberate. The earlier Lane 1 bridge worker remains evidence
from a local slice, not the default shape to promote.

Historical concrete worker slice:

```text
Lane1ReasoningBridgeWorker
  input: one Lane 1 finding + route trace + V60 selected model card
  output: one compact bridge card
```

This worker does not pick a new model.

It explains how a model already selected by Lane 1/V60 should be used or set
aside by Step 6:

- why consider it;
- what conversation evidence grounded it;
- what evidence gate controls use;
- what calibration boundary prevents overclaim;
- what use sequence Step 6 should follow;
- when to discard or keep it private.

Bevelin's role in this worker is discipline, not content:

```text
evidence gate
calibration boundary
sequence of use
set-aside condition
```

The first local slice validated three subagent-produced cards across real-estate
and oncologist artifacts after tightening the compression contract.

## What Subagents Should Not Own

Subagents should not:

- redo the whole Lolla pipeline;
- rerun lane detection from scratch;
- write final answer prose;
- decide the whole human situation;
- receive every lane and every chunk at once;
- produce long reports;
- create public machinery language;
- act as truth authorities;
- force the final reasoner to accept their output.

## Deterministic System Boundary

Deterministic code should own:

- workpack assembly;
- source references;
- schema validation;
- caps;
- dedupe;
- privacy labels;
- provenance receipts;
- failure states;
- cost/latency telemetry;
- artifact persistence.

Deterministic code should not own:

- which pressure is true;
- which interpretation is best;
- which question matters most;
- whether a human should act;
- final answer synthesis.

The deterministic path carries cognition. It does not replace cognition.

## Historical Candidate Workpack

Each subagent should receive a narrow workpack. The first local slice called
that object `CognitiveWorkpack`; that name is now historical scaffolding.

Current favored input concept:

```text
reasoning_workpack.v1
```

The old `CognitiveWorkpack` schema remains useful because it proved the right
shape of the boundary: shared situation brief, narrow local slice, source
evidence, forbidden moves, and output contract. Future work should carry those
lessons forward under `reasoning_workpack.v1` rather than extending the old name
as the target architecture.

Implemented local schema:

```text
cognitive_workpack.v1
```

Current shape:

```text
CognitiveWorkpack
- schema_version
- workpack_id
- work_type
- shared_situation_brief
- decision_situation
- selected_lane_or_pressure
- source_evidence
- relevant_chunks
- known_constraints
- forbidden_moves
- output_contract
```

Important:

- include the same small situation brief for every worker;
- only include the slice needed for the worker;
- do not include all lanes by default;
- do not include the full conversation unless the worker truly needs it;
- include enough source evidence to prevent free-floating interpretation;
- include explicit forbidden moves.

## Shared Situation Brief

Narrow context does not mean contextless work.

Every worker needs a small shared brief that says what the conversation is
actually about before it receives its local slice. Otherwise a worker can produce
a correct small answer that is irrelevant to the full system.

The shared brief should be stable across all pre-Step-6 workers:

```text
user question
decision situation
live constraints
what the conversation is trying to resolve
which lane artifacts exist
why this worker is being asked anything at all
what would count as useful output
what would count as noise
```

The shared brief should not include:

```text
full transcript
all lane cards
all mental model details
all prior session context
every deterministic chunk
```

This is the anti-bloat compromise:

```text
shared brief = enough big picture to stay relevant
local slice = only the evidence needed for the worker question
final reasoner = full arbitration across the bundle
```

If a worker cannot answer from the shared brief plus its local slice, the planner
should either give it a better slice or not run that worker.

## Historical Candidate Output

Each worker returns a compact reasoning artifact. The first local slice called
that object `CognitiveWorkerPacket`; that name is now historical scaffolding.

Current favored worker output:

```text
reasoning_artifact.v1
```

The older packet taught the right behavior: a worker should state source basis,
evidence gate, calibration boundary, alternative/disconfirmation, risk if
ignored, risk if forced, and set-aside reason. The new `reasoning_artifact.v1`
contract preserves those lessons while adding explicit bundle relation,
priority, relaxation, and discard fields.

Implemented local schema:

```text
cognitive_worker_packet.v1
```

Current shape:

```text
CognitiveWorkerPacket
- schema_version
- producer
- packet_id
- source_basis
- main_relevance_claim
- why_it_matters
- evidence_gate_or_question
- calibration_boundary
- alternative_frame_or_disconfirmation
- risk_if_ignored
- risk_if_forced
- recommended_disposition
- set_aside_reason_if_weak
```

Allowed `recommended_disposition`:

```text
use_as_private_pressure
convert_to_user_question_if_blocking
convert_to_final_answer_diagnostic
hold_for_audit_only
set_aside
```

This packet is not final answer prose.

## Historical Compact Cognition Dossier

The final reasoner should not receive every worker artifact. The first local
slice compressed worker packets into a `CognitionDossier`; that object is now a
historical bridge toward the current bundle plan.

Current favored Step-6 handoff:

```text
reasoning_bundle.v1
```

The dossier lesson still holds: do not dump every worker paragraph into the
final reasoner. The replacement is not a larger dossier but an arbitration
index that names primary pressure, support, duplicates, conflicts, hard
boundaries, relaxation conditions, quiet/discard candidates, and rethinking
questions.

Implemented local schema:

```text
cognition_dossier.v1
```

Current shape:

```text
CognitionDossier
- schema_version
- producer
- source_packet_ids
- central_pressure
- central_question_or_gate
- strongest_alternative_frame
- source_overclaim_boundary
- set_aside_notes
- final_reasoner_instruction
```

Caps:

```text
max 1 central pressure
max 1 central question or gate
max 1 alternative frame
max 3 set-aside notes
max 1200-1800 tokens total
```

In the older slice, the dossier was the object given to Claude Code or another
orchestrator. In the current plan, `reasoning_bundle.v1` fills that role.

The rich worker outputs are stored for audit, not injected by default.

## Relationship To Existing Cards

`CentralGateCard` was considered a possible field inside the dossier.

`PostLaneInquiryCard` was considered another possible field inside the dossier.

At the time of the dossier slice, the possible target was one compact
orchestrator-facing object:

```text
CognitionDossier =
  central gate
  + controlling question
  + calibration boundary
  + alternative frame
  + set-aside notes
```

That lesson has been superseded by the bundle plan: Step 6 should receive an
indexed `reasoning_bundle.v1`, not a standalone `CognitionDossier`, when more
than one artifact is in play.

## Why This May Beat Post-Hoc Pressure Checks

Post-hoc checks are useful because they catch misses.

But they are structurally limited:

- they run after the answer is already formed;
- they can create patch-like corrections;
- they force the orchestrator to compare answer versus critique;
- the memo may depend on late pressure;
- the final reasoner still had to write before getting the best compressed
  thinking.

Pre-synthesis cognitive workers may be better because:

- each worker has a narrower context;
- the final reasoner receives relevant pressure before writing;
- source/overclaim boundaries can shape the answer early;
- alternative frames can compete before prose hardens;
- less material reaches the final context.

## Red-Team Concerns

Do not treat this as proven.

Risks:

- subagents may overfit their narrow slice;
- multiple workers may create committee noise;
- cost can rise quickly;
- latency may rise unless workers run in parallel;
- the final reasoner may overtrust worker packets;
- worker outputs can inherit lane bias;
- packet compression can flatten nuance;
- deterministic caps can hide something important;
- replacing post-hoc checks too early can remove a useful safety net.

Guardrails:

- keep post-hoc checks as a research control until the new path wins;
- require anti-confirmation in worker packets;
- compare against strict prompt-only controls;
- compare against central-gate controls;
- inspect final answers manually;
- cap injected dossier size;
- log set-aside reasons;
- never treat subagent agreement as truth.

## First Implementation Slice

Do not build the whole architecture first.

Historical contract slice completed locally:

```text
scripts/research/candidate_shift_eval/cognitive_workers.py
tests/test_cognitive_workers.py
research/subagent-cognitive-worker-contract-slice-2026-05-15.md
```

What this older slice proved:

- `CognitiveWorkpack` builder and validator;
- subagent worker prompt builder;
- `CognitiveWorkerPacket` validator;
- `CognitionDossier` builder, validator, and renderer;
- Step 6-style dossier consumption prompt builder;
- tests for exact schema, source basis, anti-confirmation, precision discipline,
  unsupported conclusion terms, machinery leakage, set-aside disposition, and
  private dossier rendering.

Tests passed:

```text
pytest tests/test_cognitive_workers.py -q
11 passed

pytest tests/test_cognitive_workers.py \
  tests/test_candidate_shift_eval_handoff.py \
  tests/test_grounded_force_preservation.py -q
64 passed
```

This proves only the local contract. It does not prove the architecture improves
answers.

Older next live research slice:

```text
one archived case
  -> assemble one CognitiveWorkpack from existing lane output and source evidence
  -> run one subagent worker
  -> validate CognitiveWorkerPacket
  -> render a tiny CognitionDossier
  -> consume in Step 6-style final answer prompt
  -> compare against current flow and central-gate card
```

Current next implementation slice is defined in:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
```

In short:

```text
reasoning_workpack.v1 builder/validator
  -> two subagent prompt builders only
  -> reasoning_artifact.v1 outputs
  -> reasoning_bundle.v1 rendering
  -> local current/raw/indexed comparisons
```

The older slice started with one worker type:

```text
inquiry/boundary worker
```

The current planned first worker types are:

```text
boundary/evidence-gate worker
duplicate/priority worker
```

Reason the older boundary worker was chosen:

- it directly connects to the post-lane inquiry idea;
- it is narrow;
- it can produce a central question, evidence gate, alternative frame, and
  overclaim boundary;
- it can be compared against the existing central-gate card.

## Success Bar

This architecture is useful only if final answers improve.

Signs of improvement:

- final answer receives less but better context;
- central decision is clearer;
- fewer unsupported assumptions survive;
- useful action is preserved;
- fewer generic cautions;
- fewer late Step 8 divergences;
- no machinery leaks;
- cost and latency remain defensible;
- wins hold across multiple case families.

Not enough:

- subagent output sounds smart;
- packets validate;
- the dossier is elegant;
- one case improves;
- the system asks more questions;
- the final answer gets longer.

## Current Recommendation

Prioritize this architecture over the book-question corpus for now.

Keep the corpus as a source of principles later.

Live replay correction:

> The first OpenRouter worker/dossier replays proved the contract can execute,
> but they did not prove quality. Parenting and whistleblower failed manual
> quality inspection when OpenRouter was used as the final consumer. The worker
> packets were much safer than the final answers.

Current provider boundary:

```text
OpenRouter = narrow worker / cheap ablation / focused audit
not = trusted final reasoner for operational or legal-adjacent cases
```

Subscription-first cost rule:

```text
Use the user's Claude Code / Codex subscription for high-context reasoning.
Spend OpenRouter/API tokens only for small controlled artifacts that reduce
later context bloat or improve validation.
```

This matters for product fit. Lolla should not become an API-token-heavy
parallel-agent system just because every cognitive step can be decomposed. Each
extra call needs a reason:

- it creates a compact artifact the final reasoner can actually use;
- it avoids bloating the main prompt;
- it can be validated mechanically;
- it produces evidence we could not get as cheaply inside the orchestrator;
- it improves final-answer quality enough to justify the cost.

Next research step:

```text
Use the existing worker packets and dossiers with a stronger/high-context final
consumer, then run source/overclaim review before comparing answer quality.
```

Do not edit product docs or runtime defaults until this beats current controls.

## Lane 1 Bridge Consumption Update

Date: 2026-05-15

New readout:

```text
research/lane1-bridge-final-consumption-readout-2026-05-15.md
```

The Lane 1 bridge card is now the best small example of the cognitive-worker
shape we want:

```text
one narrow worker
one already-selected model pressure
one compact private artifact
final reasoner may use, reject, or set aside
validator blocks leakage and unsupported promotion
```

The test suggests:

```text
subagents are useful when they create bounded reasoning artifacts,
not when they become a second final reasoner or another broad lane
```

Good worker output is not a brilliant mini-essay. It is a small artifact that
helps the final reasoner preserve grounded friction:

```text
evidence gate
calibration boundary
decision branch
stop-rule
no-signal
discard condition
```

The final-consumption slice produced narrow bridge wins on real estate and
oncologist cases, but it remains local research only. The next subagent tests
must include cases where the worker should set itself aside. If the system only
tests positive cases, it will overfit toward adding pretty pressure.

Boundary follow-up:

```text
speculative EV boundary:
  control beat bridge
  bridge label = smoothed_useful_friction
```

This is an important architecture lesson. A subagent artifact can be valid,
compact, grounded, and still make the final answer worse if the final consumer
turns a hard stop-rule into softer prose.

Subagent worker promotion should therefore require negative-case behavior:

```text
the worker artifact must help the final reasoner reject weak model pressure,
not merely give it a more elegant way to mention the model
```

For future worker contracts, include explicit instructions to preserve hard
source-grounded stop-rules. The worker should not turn:

```text
no concrete access, no $12,000 spend
```

into:

```text
consider whether the access is concrete enough
```

when the source supports the harder line.

Hard-stop repair follow-up:

```text
speculative EV hard-stop v2:
  bridge answer preserved "no concrete access, no $12,000 spend"
  reviewer preferred bridge narrowly

speculative EV concrete-access:
  two relevant meetings became confirmed before payment
  bridge and control tied
  old hard no relaxed
  new boundary became downside-plan survival
```

Architecture lesson:

```text
subagent artifacts should preserve boundaries, not freeze them
```

A good worker artifact must say both:

```text
hold this line when these facts are present
change the line when these facts change
```

That means future cognitive-worker contracts need boundary polarity:

```text
hard boundary:
  the source-grounded line that should not be softened

relaxation condition:
  the source-grounded change that should loosen or replace the line
```

Without the relaxation condition, the system can become brittle. Without the
hard boundary, the system becomes smooth and weak. The useful shape is both.

## Multi-Worker / Multi-Lane Constraint

The Lane 1 bridge worker is only one possible worker.

Future handoffs may include several cognitive artifacts:

```text
Lane 1 bridge worker
Lane 2 model-use worker
source / overclaim worker
question-generation worker
boundary / inquiry worker
deterministic affinity summaries
canonical model cards
```

This means the worker contract must assume crowded context. A good worker output
is not just compact; it is composable.

Composable worker output should include:

```text
what this artifact is for
what source fact activates it
what boundary it protects
what would relax or discard it
how much priority it should get
```

Bad worker output:

```text
this is important
use this model
consider this lens
```

Better worker output:

```text
use this only if the final answer is deciding X
preserve this stop-rule unless Y changes
set aside if another lane already carries the same reasoning
```

The final orchestrator should receive a bundle it can arbitrate, not a pile of
smart paragraphs. This is why future tests need bundled handoffs with more than
one artifact.

First bundled-handoff probe:

```text
case: speculative EV concrete-access
other worker/lane artifact: opportunity-cost support
result: control wins narrowly over bridge
```

The bridge did not fail by being wrong. It failed to add enough marginal value
once another artifact already carried the important pressure:

```text
protect onboarding and three pilots
do not treat meetings as funding probability
only go if the downside plan survives
```

Worker-contract lesson:

```text
workers need duplicate-awareness
```

Each worker should be able to say:

```text
this pressure is already carried by another artifact
my output should stay quiet or lower-priority
```

Without duplicate-awareness, a correct worker can still add clutter. In a
multi-worker system, correct but redundant artifacts are not free.

## Reasoning Bundle v1

The current pre-Step-6 research path is now:

```text
worker/lane artifacts
  -> Reasoning Bundle v1
  -> final reasoner rethinks standpoint
  -> source/overclaim review
```

Receipt:

```text
research/reasoning-bundle-v1-pre-step6-handover-2026-05-15.md
```

This is separate from the current product Step 7/8 after-check subagents.

Current product subagents ask:

```text
what did Step 6 miss?
```

Pre-Step-6 cognitive workers should ask:

```text
what should Step 6 seriously consider, preserve, relax, set aside, or avoid
forcing before it writes?
```

Reasoning Bundle v1 adds the missing arbitration layer. It lets several worker
outputs coexist without pretending each one deserves equal attention.

The first valid bundle test used:

```text
lane2-opportunity-cost = primary pressure
lane1-expected-value-bridge = lower-priority duplicate/support
```

The final answer sample correctly:

- treated two confirmed meetings as new evidence;
- kept the downside-survival gate;
- set aside detailed numerical EV framing;
- did not repeat duplicate opportunity-cost pressure;
- kept public prose free of machinery.

Architecture implication:

```text
subagent output should not go straight to Claude Code as a pile
it should be indexed into a bundle that says what is primary, duplicate,
conflicting, hard-boundary, relaxable, quiet, or discardable
```

## Live Follow-Up: Raw, Bevelin Worker, Audit

Readout:

```text
research/spikes/reasoning-bundle/reasoning-bundle-live-subagent-readout-v1-2026-05-15.md
```

Three fresh subagent checks were run:

```text
raw artifact dump consumption
Bevelin boundary-worker artifact generation
source/overclaim audit of the indexed-bundle answer
```

Findings:

- raw unindexed context can still produce a good answer on a small case;
- without an index, the final reasoner used both artifacts and set none aside;
- the Bevelin worker worked best as a narrow boundary/evidence-gate producer;
- the independent audit passed the indexed-bundle answer and found no
  unsupported precision, boundary loss, or public machinery leakage.

Updated architecture lesson:

```text
the index is not there to make weak content strong
the index is there to preserve useful pressure while reducing cognitive clutter
```

That means pre-Step-6 subagents should optimize for compact artifacts with
priority humility. They are not trying to win the answer. They are trying to
give the final reasoner one clear reason to preserve, relax, or discard a
pressure.

## Conflict / Overload Lesson

Readout:

```text
research/spikes/reasoning-bundle/reasoning-bundle-conflict-overload-live-readout-v1-2026-05-15.md
```

The conflict and overload tests sharpened the architecture:

```text
artifact-level humility matters as much as bundle-level indexing
```

The raw overload answer also set aside quiet duplicates because the raw artifact
dump still included priority and discard fields. That is good news. It means the
worker contract itself is doing real work.

The bundle index should therefore not replace rich artifact contracts. It should
summarize them:

```text
worker artifact says why it may matter and when to demote itself
bundle index gives Step 6 the first-pass map across all artifacts
Step 6 still performs cognition and final arbitration
```

Red-team note:

```text
do not oversell Reasoning Bundle v1 as the cause of all improvement
```

In compact cases, a strong final reasoner can use raw artifacts well. The likely
edge of the index is under mixed-producer, high-clutter, cross-lane conditions.

## Reasoning Shapes, Not Domain Cases

Future tests should not be selected because the topic is interesting. They
should be selected because they stress a reasoning operation.

Examples:

```text
rule relaxation after new evidence
hard-boundary preservation
duplicate demotion
conflict preservation
quiet/discard behavior
source-overclaim control
low-value-artifact rejection
mixed-producer arbitration
```

The factual story is only a carrier. A founder retreat, a legal-adjacent
question, or a family decision can all be useful only if they force one of those
abstract operations.

This keeps the architecture aligned with the doctrine:

```text
we are improving the reasoning surface
we are not optimizing a deterministic answer for a specific factual case
```
