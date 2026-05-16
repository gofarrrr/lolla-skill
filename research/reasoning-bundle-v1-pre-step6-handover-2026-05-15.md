# Reasoning Bundle v1 Pre-Step-6 Handover

Date: 2026-05-15

Status: local research only. No product docs, default runtime, canonical
knowledge base, Lane 1, V60, or live skill behavior changed.

Current system-plan source of truth:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
```

This document remains the v1 bundle handover. The 2026-05-16 plan adds the
planned worker input concept, admission gate, and shared-brief requirements that
should precede bundle construction.

## Why This Exists

The final boss is still Step 6:

```text
Claude Code / Codex receives the system outputs and rethinks its standpoint
before writing the user-facing answer.
```

The goal is not to make every subagent output smooth. The goal is to make the
bundle legible enough that the final reasoner can pick from noisy, useful data.

The handoff can contain friction. It should not contain unstructured clutter.

## Current Product Shape

Current product subagents are post-Step-6 pressure checks.

Shape:

```text
Step 6 writes updated position
Step 6b persists answer and V60 ledger
Step 7 launches cold subagents, one per non-empty lane
Step 8 compares subagent outputs against Step 6
```

Those subagents currently receive:

```text
extracted decision structure
one audit card
no full conversation history
no other lanes
no session context
```

They answer:

```text
what did Step 6 miss, minimize, or fail to connect?
```

This is valuable as an after-check, but it is not the same as pre-Step-6
cognition.

## Desired Pre-Step-6 Shape

Pre-Step-6 subagents should not act like reviewers of an answer that does not
exist yet.

They should act like narrow cognitive workers:

```text
given this selected evidence and pressure,
what should the final reasoner seriously consider,
what should it preserve,
what should it set aside,
what would make the pressure relax,
and what goes wrong if this is forced?
```

The final reasoner then receives a bundle:

```text
multiple small worker/lane artifacts
arbitration index
re-thinking instruction
conversation context
```

Claude Code / Codex still performs the final reasoning.

## Shared Brief Guardrail

Pre-Step-6 workers should be narrow, but they must not be blind.

Every worker should receive the same small situation brief before its local
evidence packet:

```text
user question
decision situation
live constraints
what the conversation is trying to resolve
which lane / V60 / worker artifact types exist
why this worker was launched
what would count as useful output
what would count as noise
```

Then the worker receives only the few artifacts and source excerpts needed for
its question.

This prevents two opposite failures:

```text
too much context -> every worker becomes a mini Step 6 and adds bloat
too little context -> workers produce locally correct but globally irrelevant
output
```

The target is:

```text
small shared big picture
plus narrow local slice
plus compact output
plus Step 6 final arbitration
```

## Worker Admission Gate

Before any worker is launched, the planner must answer:

```text
What exact question is this worker answering?
Why can Step 6 not just handle this directly?
Which artifacts does it need?
Which artifacts are excluded?
What would make this worker unnecessary?
```

The planner must also state the value hypothesis, the control this worker must
beat, why a no-worker Step 6 would likely miss the pressure, and what result
would kill this worker type.

Admission should fail when the worker would merely summarize a lane, restate
pressure already compactly available to Step 6, require all lanes or the full
transcript, use "fresh context" as its only rationale, or produce generic
caution without a boundary, relaxation condition, or discard condition.

The healthiest default remains 0-2 workers. No worker is better than a worker
whose purpose is only "more cognition."

## Planned Workpack Input

The planned worker input object is:

```text
reasoning_workpack.v1
```

It packages a worker task. It does not decide truth.

Required contents:

```text
admission_gate
shared_situation_brief
worker_question
local_artifacts
source_excerpts
forbidden_moves
output_contract
caps
```

Caps for v1:

```text
max local artifacts: 2-5
max source excerpts: 2-4
```

If a worker needs more than that, the planner should narrow the question, split
the task, or decline the worker.

## Reasoning Bundle v1

Prior WIP/spike artifact names, not promoted implementation in this docs-only
checkpoint:

```text
scripts/research/reasoning_bundle.py
tests/test_reasoning_bundle.py
scripts/research/run_reasoning_bundle_prompt_replay.py
```

Those paths are useful breadcrumbs if reviewing the local experimentation pile,
but this document should not be read as saying those files are shipped,
promoted, or present on a clean docs-only branch. Future implementation should
restart from the 2026-05-16 core plan and cherry-pick only what survives review.

Schema versions:

```text
reasoning_workpack.v1  # planned input concept
reasoning_artifact.v1
reasoning_bundle.v1
reasoning_bundle_consumption.v1
```

## Artifact Contract

Each artifact must say:

```text
what this artifact is for
what source fact activates it
what it contributes
what hard boundary it protects
what would relax that boundary
when to discard it
how it relates to the bundle
how much priority it should get
what goes wrong if forced
what goes wrong if ignored
```

This is the key difference from a smart paragraph. It is designed for
arbitration.

## Bundle Contract

The bundle contains:

```text
artifacts[]
arbitration_index
final_reasoner_instruction
```

The bundle index is a map, not a truth selector. It may say an artifact is
primary, duplicate, quiet, conflicting, or boundary-bearing, but Step 6 still
decides what to use, reject, defer, or keep private.

The index must preserve artifact IDs and compact grounding. It should organize
pressure, not create a new ungrounded synthesis before the final reasoner sees
the artifacts.

The arbitration index names:

```text
primary_pressure
supporting_pressures
duplicate_or_lower_priority
conflicts_or_tensions
hard_boundaries
relaxation_conditions
quiet_or_discard
rethinking_questions
```

This lets the final reasoner see the shape of the bundle before reading every
artifact.

## Final Reasoner Prompt

The consumption prompt tells the final reasoner:

```text
rethink your standpoint from the private reasoning bundle
some inputs may be useful, noisy, redundant, weak, or in tension
your job is arbitration, not obedience
do not optimize for smoothness
set aside duplicate or weak artifacts privately
do not expose internal machinery in the final answer
```

This is the core Step-6 direction.

## First Test Case

Case:

```text
speculative EV concrete-access
```

The user first lacked concrete access for a $12,000 founder retreat, then got
two confirmed relevant investor meetings before payment. The decision changed
from:

```text
no concrete access, no $12,000 spend
```

to:

```text
concrete access exists, but no spend unless the known revenue path survives
```

Artifacts:

```text
lane2-opportunity-cost
lane1-expected-value-bridge
```

Arbitration:

```text
lane2-opportunity-cost = primary
lane1-expected-value-bridge = lower-priority duplicate/support
```

Why:

```text
the opportunity-cost artifact already carries the strongest source-grounded
pressure: protect onboarding and three pilots
```

## Result

The final answer sample validated.

It did the desired arbitration:

- used opportunity cost as primary pressure;
- used the expected-value bridge only as supporting pressure;
- set aside detailed EV framing;
- did not repeat duplicate pressure;
- preserved the hard boundary;
- relaxed the old no-access stop-rule because source facts changed;
- did not expose internal machinery.

The answer's core decision:

```text
The earlier rule no longer means automatic no.
Two confirmed meetings are concrete access.
But do not spend most remaining cash unless onboarding and the three pilots can
survive if the meetings produce nothing.
```

## Receipts

Artifacts:

```text
research/spikes/reasoning-bundle/speculative-ev-concrete-access-artifacts-v1-2026-05-15.json
```

Bundle:

```text
research/spikes/reasoning-bundle/speculative-ev-concrete-access-reasoning-bundle-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-concrete-access-reasoning-bundle-v1-2026-05-15.md
```

Prompt:

```text
research/spikes/reasoning-bundle/speculative-ev-concrete-access-reasoning-bundle-consumption-prompt-v1-2026-05-15.md
```

Answer:

```text
research/spikes/reasoning-bundle/speculative-ev-concrete-access-reasoning-bundle-answer-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-concrete-access-reasoning-bundle-prompt-pack-v1-answer-2026-05-15.json
```

## What This Proves

This proves:

- a multi-artifact bundle can be validated;
- the renderer can make duplicate/lower-priority pressure visible;
- the final prompt can ask Claude/Codex to arbitrate instead of obey;
- the final answer can preserve useful friction without exposing machinery;
- not-smoothed-out private context can be useful if it is structured.

## What This Does Not Prove

This does not prove:

- the bundle beats the live skill;
- the bundle beats current Step 6 with V60 ledger;
- all subagents should move pre-Step-6;
- OpenRouter should do final synthesis;
- the architecture should be promoted.

The final proof is still running the real skill.

## Next Tests

1. Compare Reasoning Bundle v1 against the prior bundled control/bridge answers.
2. Run on a case where artifacts conflict rather than duplicate.
3. Run on a case where one artifact should be quiet or discarded.
4. Run on a case with three or more artifacts to test overload.
5. Run source/overclaim audit on the bundle-consumed final answer.
6. Only later, test inside the real skill flow.

## Current Decision

Keep the Reasoning Bundle v1 path as local research.

Do not promote.

The next useful question is:

```text
does the indexed bundle beat raw bundled context when the final reasoner has to
choose among multiple lane/subagent artifacts?
```

## Follow-Up Slices: 2026-05-15

Local deterministic receipts:

```text
research/spikes/reasoning-bundle/reasoning-bundle-local-slices-report-v1-2026-05-15.md
research/spikes/reasoning-bundle/reasoning-bundle-local-slices-report-v1-2026-05-15.json
```

Live subagent receipts:

```text
research/spikes/reasoning-bundle/reasoning-bundle-live-subagent-readout-v1-2026-05-15.md
research/spikes/reasoning-bundle/reasoning-bundle-live-subagent-readout-v1-2026-05-15.json
```

### Slice 1: Raw Versus Indexed

Raw control:

```text
research/spikes/reasoning-bundle/speculative-ev-concrete-access-raw-consumption-answer-subagent-v1-2026-05-15.json
```

Result:

- the raw control produced a good answer;
- it preserved the same main boundary;
- it used both artifacts;
- it set no artifact aside.

Interpretation:

```text
raw extra context can work on a simple two-artifact case
```

But the indexed bundle still has a real edge:

```text
it tells the final reasoner which artifact is primary, duplicate,
lower-priority, conflicting, quiet, or discardable
```

The raw control did not fail, but it also did not demote the duplicate
expected-value bridge. That matters more as bundle size grows.

### Slice 2: Conflict

Receipt:

```text
research/spikes/reasoning-bundle/speculative-ev-conflict-reasoning-bundle-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-conflict-reasoning-bundle-v1-2026-05-15.md
```

Result:

```text
cash-preservation-hard-stop is indexed as a tension
```

This proves the bundle can preserve conflict instead of deleting one side. It
does not yet prove the final reasoner handles conflict correctly in a live run.

### Slice 3: Overload

Receipt:

```text
research/spikes/reasoning-bundle/speculative-ev-overload-reasoning-bundle-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-overload-reasoning-bundle-v1-2026-05-15.md
```

Result:

```text
quiet/discard artifacts are capped in the arbitration index
the full artifact list remains in the JSON receipt
```

This supports the idea that Step 6 should see the important shape first, not a
flat pile of every worker output.

### Slice 4: Bevelin Boundary Worker

Live receipt:

```text
research/spikes/reasoning-bundle/speculative-ev-bevelin-boundary-worker-artifact-subagent-v1-2026-05-15.json
```

Result:

- valid `reasoning_artifact.v1`;
- did not write the final answer;
- did not select mental models;
- did not add a new tendency;
- produced evidence gate, hard boundary, relaxation condition, discard
  condition, and risks.

Interpretation:

```text
Bevelin is strongest here as interpretation discipline
```

It can become a pre-Step-6 worker style:

```text
what observation changed?
what evidence gate matters?
what boundary must survive?
what would relax it?
when should we discard it?
what false positive appears if forced?
```

Concern:

```text
worker outputs must stay short and ordinary
```

The live artifact was useful but slightly wordy. Future worker prompts should
push for compact language.

### Slice 5: Source / Overclaim Audit

Live receipt:

```text
research/spikes/reasoning-bundle/speculative-ev-answer-source-audit-subagent-v1-2026-05-15.json
```

Result:

```text
verdict: pass
unsupported_source_claims: []
unsupported_precision: []
boundary_errors: []
smoothing_or_force_errors: []
public_machinery_issues: []
```

This is important because the judge was instructed not to reward polish or
smoothness. It checked source alignment and whether the hard boundary survived.

Updated current read:

```text
narrow workers -> reasoning artifacts -> indexed reasoning bundle
-> Step 6 final arbitration -> source/overclaim audit
```

This is still local research only. Promotion remains blocked until we run the
same pattern across multiple case families.

## Conflict And Overload Live Follow-Up

Readout:

```text
research/spikes/reasoning-bundle/reasoning-bundle-conflict-overload-live-readout-v1-2026-05-15.md
```

Four fresh final-reasoner subagent checks were run:

```text
conflict indexed
conflict raw
overload indexed
overload raw
```

### Conflict Result

Both indexed and raw answers were strong.

Indexed:

```text
research/spikes/reasoning-bundle/speculative-ev-conflict-indexed-answer-subagent-v1-2026-05-15.json
```

Raw:

```text
research/spikes/reasoning-bundle/speculative-ev-conflict-raw-answer-subagent-v1-2026-05-15.json
```

Observed difference:

- indexed explicitly set aside duplicate numerical EV framing;
- raw used every artifact and set none aside;
- raw public prose was slightly smoother;
- indexed notes made the tension more explicit.

Conclusion:

```text
indexed did not clearly beat raw on public answer quality
indexed did better on visible arbitration behavior
```

### Overload Result

Indexed:

```text
research/spikes/reasoning-bundle/speculative-ev-overload-indexed-answer-subagent-v1-2026-05-15.json
```

Raw:

```text
research/spikes/reasoning-bundle/speculative-ev-overload-raw-answer-subagent-v1-2026-05-15.json
```

Observed difference:

- indexed set aside duplicate cautions as groups;
- raw also set aside quiet duplicates because artifact-level priority hints
  survived inside the raw dump;
- indexed produced more natural user-facing set-aside behavior;
- raw named quiet duplicate ids directly.

Updated lesson:

```text
artifact-level humility fields are already powerful
bundle-level arbitration is still useful as a first-pass map
```

The future design should preserve both:

```text
artifact fields: relation, priority, discard, risk-if-forced
bundle index: primary, duplicate, conflict, hard boundary, relaxation,
quiet/discard
```

This changes the value claim. We should not say:

```text
raw artifacts fail and indexed bundles win
```

We should say:

```text
well-formed artifacts can already help Step 6
the index is most likely valuable under broader/messier/mixed-producer load
```

Promotion remains blocked until broader reasoning-shape coverage or the real
skill test.

## Important Correction: Cases Are Fixtures, Not Targets

The purpose of these cases is not to learn how to answer founder-retreat,
real-estate, legal, parenting, or career questions.

The case facts are disposable fixtures.

What matters is the abstract reasoning behavior:

```text
can the final reasoner relax an old rule when source facts change?
can it preserve a hard boundary without becoming blindly conservative?
can it demote duplicate artifacts?
can it keep conflict visible without freezing?
can it ignore weak/noisy pressure without losing useful friction?
can it avoid invented precision while still giving a useful answer?
```

So when this document says "broader case families," it should be read as:

```text
broader reasoning-shape families
```

Not:

```text
more topical domains for their own sake
```

The cases matter only because they create different reasoning conditions. The
system is being tested on reasoning about reasoning, not on the factual content
of the scenario.
