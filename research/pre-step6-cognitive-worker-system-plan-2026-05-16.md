# Pre-Step-6 Cognitive Worker System Plan

Date: 2026-05-16

Status: research system plan only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

This is now the central handover for the pre-Step-6 cognitive-worker direction.
Older `CognitiveWorkpack`, `CognitiveWorkerPacket`, and `cognition_dossier`
documents remain useful research scaffolding, but the favored handoff family is:

```text
reasoning_workpack.v1 -> reasoning_artifact.v1 -> reasoning_bundle.v1
```

The system goal is not more artifacts. The goal is a final answer that is
sharper, better grounded, more honest about uncertainty, and better at using or
rejecting selected pressure.

## 2026-05-16 Critic Pass

Verdict: revise before implementation, pass only as docs-only research.

Contradicting evidence first:

- prior strict-control ablations did not prove that pre-Step-6 subagents create
  durable answer-quality lift;
- raw artifacts can already perform well when they carry source grounding,
  humility, discard, and risk-if-forced fields;
- a bundle can make private notes prettier without improving the final answer;
- extra cognition can worsen Step 6 by increasing attention load, duplicate
  pressure, and false confidence.

Therefore the burden of proof is on the worker/bundle path. Future slices must
name the strong control they are trying to beat, the expected marginal gain, and
the kill condition that would stop the line of work. "More fresh-context
cognition" is not enough.

## Product Boundary

No product promotion is authorized by this document.

Do not change:

- `SKILL.md`;
- `HOW_IT_WORKS.md`;
- `/lolla` default runtime behavior;
- product memo/chat surfaces;
- Lane 1 or the canonical knowledge base;
- V60 selection or ledger behavior;
- live Step 7/8 pressure-check behavior.

The next work is research-only design, validation, and local comparison. Product
docs should change only after the research harness shows durable improvement and
the promotion gates below are satisfied.

## Live System Truth

The live execution source of truth is `SKILL.md`.

Current stable product shape:

```text
conversation capture
  -> OpenRouter extraction
  -> four existing lanes
  -> V60 private enrichment attached after lanes by default
  -> Step 6 final reconsideration by Claude/Codex
  -> Step 6b revised-answer persistence and V60 consideration ledger
  -> V60 ledger finalization gate
  -> Step 7 cold pressure-check subagents
  -> Step 8 comparison against Step 6
  -> Step 8b pressure-check persistence
  -> Step 8c memo decision-note persistence and memo render
  -> Step 9 Observatory
  -> Step 10 archive
```

Step 5 is intentionally a placeholder. The Observatory is deferred until Step 9
so the run contains cards, revised answer, pressure check, memo fields, and memo.

Important current invariants:

- Steps 1-4 are pipeline orchestration and lane execution. The orchestrator
  captures the conversation and runs scripts; lane semantic judgment runs through
  calibrated prompts and persisted artifacts.
- Step 6 is the primary user-facing cognition point. It weighs lane pressure,
  V60 private material, user context, and the original conversation. It may use,
  reject, defer, or keep pressure private.
- V60 is not a fifth lane. It is private source-backed affordance/absence
  material selected after the lanes. The public answer should show better
  reasoning, not `V60`, chunk, ledger, affordance, or packet language.
- Step 6b persists the revised answer and the private V60 consideration ledger.
  Finalization validates the ledger before pressure checks continue.
- Step 7/8 are current post-Step-6 pressure checks. They are not the proposed
  pre-Step-6 cognitive-worker layer.
- Public chat and memo must not expose machinery language.

## Timing Contradiction

There is currently a product-document timing contradiction.

`SKILL.md` says Step 7 pressure-check subagents launch only after Step 6b and
V60 finalization succeed. In particular, Step 6 carries a timing note not to
launch pressure-check subagents before Step 6b finalization, and Step 7 repeats
that launch is only after finalization succeeds.

`HOW_IT_WORKS.md` still contains the older description that Step 7 subagents are
fired before Step 6 and run in the background while Step 6/6b are written.

For research planning, assume `SKILL.md` is authoritative because it is the live
execution contract. Do not edit `HOW_IT_WORKS.md` as part of this research plan.
Fixing product docs belongs to a later promotion or product-doc cleanup step.

## Target Architecture

The research target is:

```text
conversation
  -> existing lanes and V60 stay unchanged
  -> deterministic relevance planner creates small workpacks
  -> subagent cognitive workers produce compact reasoning artifacts
  -> Reasoning Bundle indexes pressure / conflict / duplicate / discard / boundary
  -> Step 6 final reasoner arbitrates and writes the answer
  -> optional source/overclaim audit during research
```

The key change is where fresh cognition appears. Current Step 7 asks:

```text
what did Step 6 miss, minimize, or fail to connect?
```

The proposed workers ask before Step 6:

```text
what should Step 6 seriously consider, preserve, relax, set aside, or avoid
forcing before it writes?
```

Workers provide pressure, not truth. Step 6 remains the final cognition point.

## Why This Is Not A New Lane

This is not Lane 5, Lane 1.5, or a replacement for existing lanes.

Reasons:

- Workers run after existing lane outputs and V60/private source custody exist.
- Workers do not detect broad categories from the whole conversation.
- Workers receive narrow workpacks selected by deterministic relevance planning.
- Workers output compact reasoning artifacts, not cards, diagnoses, or public
  sections.
- Workers have explicit discard and relaxation conditions.
- The Reasoning Bundle indexes artifacts for Step 6; it does not become a truth
  selector.
- Step 6 still decides the public answer.

The right mental model is:

```text
lanes detect and preserve structured pressure
workers interpret selected pressure under narrow questions
bundle maps the resulting private pressure
Step 6 reasons
```

## Why This Is Not Bevelin-As-Taxonomy

Do not add a Bevelin lane, Bevelin tendency IDs, public Bevelin labels, or a
knowledge-base mutation as part of this path.

Bevelin fits as interpretation discipline:

- evidence gates;
- calibration boundaries;
- sequence and stop rules;
- relaxation conditions;
- discard conditions;
- source/overclaim caution;
- avoiding attractive but unsupported precision.

Bevelin does not fit here as:

- a second mental-model taxonomy;
- a public explanatory brand;
- a new canonical spine;
- raw theory stuffed into Step 6;
- a reason to over-promote Lane 1 material.

The practical use is small and private:

```text
use Bevelin-style discipline to ask what must be true,
what would falsify or relax the pressure,
what source fact actually supports it,
and when forcing it would mislead Step 6
```

## Provider Roles

Default worker producer: subagents.

Reason:

- the work is judgment-heavy;
- workers need enough situation awareness to avoid locally correct but globally
  irrelevant output;
- prior OpenRouter final-consumer tests reintroduced unsupported claims in
  operational and legal-adjacent cases;
- the user is already working inside a high-context orchestrator/subscription
  environment.

This is a research default for judgment-heavy worker production, not a product
default. If strict prompt-only controls, raw artifacts, or narrow OpenRouter
checks tie or beat subagent workers, prefer the simpler path.

OpenRouter remains secondary. Use it for:

- strict JSON audits;
- cheap ablations;
- narrow repeatable checks;
- source/overclaim audits;
- small schema-bound artifacts where the API boundary itself is useful.

Do not use OpenRouter for broad final synthesis in this path unless future tests
prove it beats the high-context orchestrator.

## Deterministic Boundary

Deterministic code should own:

- relevance planning;
- workpack assembly;
- source excerpt custody;
- artifact identity;
- schema validation;
- caps;
- dedupe;
- privacy labels;
- rendering;
- telemetry;
- failure states;
- receipts.

Deterministic code should not own:

- which pressure is true;
- which interpretation is best;
- which question matters most;
- whether the human should act;
- the final public answer.

The deterministic system prepares a better reasoning surface. It does not
replace reasoning.

## Worker Admission Gate

Before launching any worker, the planner must answer:

```text
What exact question is this worker answering?
Why can Step 6 not just handle this directly?
Which artifacts does it need?
Which artifacts are excluded?
What would make this worker unnecessary?
```

The admission record must also state:

```text
value hypothesis
control this worker must beat
why a no-worker Step 6 would likely miss this pressure
kill condition for this worker type
```

Admission should fail when:

- the worker question is broad or generic;
- the output would merely summarize a lane card;
- Step 6 already receives the same compact pressure clearly;
- no source excerpt or artifact activates the worker;
- the worker would need all lanes or the full transcript to do useful work;
- the answer would be obvious deterministic dedupe/capping;
- the likely output is a generic caution with no boundary, relaxation, or discard
  condition.
- the reason for the worker is only "fresh context," "more attention," or
  agreement from another model.

In v1, default worker count is 0-2. A run with no admitted workers is a healthy
outcome when Step 6 already has enough clear material.

## Shared Situation Brief

Every admitted worker receives the same small shared brief before its local
slice.

Required brief fields:

```text
user question
decision situation
live constraints
what the conversation is trying to resolve
which lane / V60 / worker artifacts exist
why this worker was launched
what counts as useful output
what counts as noise
```

The shared brief should not include:

```text
full transcript
all lane cards
all mental model details
all prior session context
all V60 chunks
unbounded source material
```

The brief is an orientation header, not a backdoor to the whole run. "Which
artifacts exist" means small inventory and relevance metadata, not pasted lane
cards or V60 chunks.

Purpose:

```text
small shared big picture
plus narrow local slice
plus compact output
plus Step 6 final arbitration
```

This avoids two failures:

- too much context, where every worker becomes a miniature Step 6;
- too little context, where workers produce locally correct but globally
  irrelevant artifacts.

## reasoning_workpack.v1

`reasoning_workpack.v1` is the planned worker input object. It is research-only
until implemented and validated.

Required fields:

```text
schema_version
workpack_id
worker_type
admission_gate
shared_situation_brief
worker_question
local_artifacts
source_excerpts
forbidden_moves
output_contract
caps
```

`admission_gate` should include:

```text
exact_question
why_step6_should_not_handle_directly
required_artifacts
excluded_artifacts
unnecessary_if
```

`local_artifacts` should contain at most 2-5 relevant lane/V60/worker artifacts.
`source_excerpts` should contain at most 2-4 compact excerpts. If the worker
needs more, the planner should either split the task, narrow the question, or
decline the worker.

The workpack must not select truth. It packages a bounded reasoning task.

If a worker needs a broad local slice to be useful, the correct answer is usually
to skip the worker and let Step 6 handle the case directly.

## Worker Prompt Principles

Worker prompts should:

- state the shared situation brief first;
- state exactly one worker question;
- include only the local artifact slice and source excerpts needed for that
  question;
- tell the worker that Step 6 is the final reasoner;
- require compact `reasoning_artifact.v1` output;
- require source grounding and a discard/relaxation condition;
- ask for risk if forced and risk if ignored;
- make machinery/public-output leakage forbidden;
- cap output at about 1,500 characters.

Worker prompts should forbid:

- writing the final answer;
- deciding what the user should do;
- summarizing all lanes;
- treating agreement as truth;
- inventing facts, probabilities, legal claims, medical claims, financial
  claims, or timing details;
- turning absence evidence into positive claims;
- public labels such as lane names, V60, chunk ids, ledgers, packets, bundle
  machinery, or "mental model" unless the artifact is for private audit only;
- adding new artifacts or questions outside the assigned worker question.

First worker types to implement later:

```text
boundary/evidence-gate worker
duplicate/priority worker
```

## reasoning_artifact.v1

Workers must output compact artifacts, not essays.

Required fields:

```text
schema_version
artifact_id
worker_type
why_provided
source_grounding
contribution
hard_boundary
relaxation_condition
discard_condition
relation_to_bundle
priority_hint
risk_if_forced
risk_if_ignored
```

Field intent:

- `why_provided`: why this artifact exists at all.
- `source_grounding`: the source fact or artifact that activates the pressure.
- `contribution`: the one useful pressure Step 6 should consider.
- `hard_boundary`: what must not be lost if the pressure is used.
- `relaxation_condition`: what source fact would soften or alter the pressure.
- `discard_condition`: when Step 6 should set it aside.
- `relation_to_bundle`: primary, support, duplicate, conflict, boundary,
  quiet, or discard candidate.
- `priority_hint`: high, medium, low, or quiet, with humility.
- `risk_if_forced`: how the answer gets worse if Step 6 overuses it.
- `risk_if_ignored`: how the answer gets worse if Step 6 misses it.

The artifact should be able to demote itself. A correct artifact can still be
low marginal value when another artifact carries the same pressure better.

## reasoning_bundle.v1

The Reasoning Bundle is the planned Step-6 handoff index.

It should contain:

```text
schema_version
bundle_id
source_artifact_ids
primary_pressure
supporting_pressures
duplicate_or_lower_priority
conflicts_or_tensions
hard_boundaries
relaxation_conditions
quiet_or_discard_candidates
rethinking_questions
final_reasoner_instruction
rendering_limits
```

The bundle index is a map, not a truth selector.

Each index entry should preserve artifact IDs and compact grounding. The bundle
may organize pressure, but it must not rewrite artifact claims into a new,
unsupported synthesis before Step 6 sees them.

It should help Step 6 see:

- what is likely primary;
- what merely supports or duplicates;
- what conflicts;
- what boundary should survive;
- what new evidence would relax the boundary;
- what artifacts are quiet or discardable;
- which questions would change the final answer.

It must not hide conflict, delete weak artifacts without a receipt, or imply
that the highest-priority artifact is automatically correct.

Max rendered bundle for v1: about 5,000-7,000 characters.

## Step 6 Consumption Rules

Step 6 receives the bundle as private reasoning context.

Step 6 must:

- arbitrate, not obey;
- keep the full conversation and user situation central;
- consider primary pressure seriously;
- use support only when it changes action, threshold, sequence, evidence gate,
  or risk treatment;
- demote duplicates privately;
- preserve conflicts when the answer depends on unresolved facts;
- preserve hard boundaries unless relaxation conditions are met;
- set aside quiet artifacts without public machinery;
- reject weak artifacts with a real reason;
- keep public prose clean of lane, worker, bundle, V60, chunk, ledger, packet,
  or internal model language;
- produce the final answer in ordinary user-facing language.

Step 6 should not:

- treat the bundle as a verdict;
- mention workers or subagents;
- mechanically enumerate artifacts;
- turn every pressure into a visible caveat;
- smooth away useful conflict for a tidy answer;
- overfit to a Bevelin-style evidence gate when another artifact has higher
  marginal value.

## Hard Caps For v1

```text
default workers: 0-2
maximum workers: 3 normal, 5 exceptional research-only
max artifacts per worker: 5
max source excerpts per worker: 4
max worker output: about 1,500 characters
max rendered bundle: about 5,000-7,000 characters
```

Exceptional research-only runs must explain why each extra worker is necessary.

## Future Implementation Slice

When implementation starts later, do it in this order:

1. Add research-only `reasoning_workpack.v1` builder/validator.
2. Inputs: shared brief, worker question, local artifact slice, source excerpts,
   forbidden moves.
3. The builder must not select truth; it only packages a worker task.
4. Add subagent worker prompt builders for two worker types only:
   `boundary/evidence-gate worker` and `duplicate/priority worker`.
5. Convert worker outputs into existing `reasoning_artifact.v1`.
6. Build `reasoning_bundle.v1` from worker/lane artifacts.
7. Render the bundle for a Step-6-style consumer.
8. Run local research comparisons only:
   `current control`, `raw artifacts`, `indexed reasoning bundle`.
9. Add optional source/overclaim audit after the final answer.

Do not wire this into live `/lolla` until the research harness shows real
improvement.

## Promotion Gates

Promotion requires evidence that the research path beats or ties strong
controls across reasoning shapes, not just topical domains.

Default decision: no promotion. A research slice must earn promotion against a
strong no-worker/control baseline; otherwise the simpler system wins.

Required reasoning-shape coverage:

- new evidence relaxes an old rule;
- hard boundary survives attractive upside;
- artifacts conflict;
- artifacts duplicate;
- artifact is correct but low marginal value;
- artifact tempts overclaim;
- worker should not run.

Required comparisons:

```text
current control
raw artifacts without bundle index
indexed reasoning bundle
```

Required quality checks:

- source alignment survives;
- unsupported precision decreases;
- hard boundaries survive;
- relaxation conditions are honored;
- duplicate/quiet artifacts are demoted;
- conflict is preserved instead of deleted;
- public prose is free of machinery;
- the final answer is shorter or clearer where possible;
- Step 6 remains free to reject the bundle.

Promotion remains blocked if:

- indexed bundle improves private notes but not final answer quality;
- raw artifacts perform just as well under the tested load;
- workers produce attractive generic caution;
- workers require broad context to be useful;
- public output leaks internal terms;
- OpenRouter or subagents reintroduce unsupported claims;
- cost/latency grows without clear answer-quality gain.

Treat a blocked result as a stop signal, not as a prompt to add more workers.
The next move after a failed comparison is usually compression, stricter source
custody, or killing the worker type.

## Known Failure Modes

1. Worker bloat.
   Workers receive too much context and become mini Step 6 agents.

2. Worker blindness.
   Workers receive too little shared situation context and produce irrelevant
   local correctness.

3. Beautiful artifact bias.
   Valid, polished artifacts are treated as more useful than they are.

4. Bundle as truth selector.
   The arbitration index starts deciding the answer instead of mapping pressure.

5. Duplicate pressure amplification.
   Multiple artifacts repeat the same point and make Step 6 overweight it.

6. Bevelin over-promotion.
   Evidence-gate language turns into a branded taxonomy or public model theater.

7. OpenRouter final-consumer drift.
   Narrow API calls expand into broad synthesis and reintroduce unsupported
   details.

8. Source-overclaim slip.
   A worker converts absence, weak hints, or old context into positive claims.

9. Conflict smoothing.
   The bundle or Step 6 hides tension to make the answer tidy.

10. Product-doc drift.
    Research docs describe future behavior so vividly that future agents mistake
    it for live `/lolla` behavior.

11. Research momentum bias.
    Because subagents are interesting and locally available, future work treats
    them as the answer before they beat simpler controls.

## Docs-Only Verification Checklist

For this planning slice:

- product docs and runtime are not changed;
- this core doc states the `SKILL.md` / `HOW_IT_WORKS.md` timing contradiction;
- linked research docs point here as the current source of truth;
- linked research docs do not describe absent WIP scripts as promoted
  implementation;
- terminology distinguishes deterministic custody, subagent cognition, Step 6
  final arbitration, and OpenRouter narrow audit/ablation;
- old `CognitiveWorkpack` / `cognition_dossier` language is marked historical
  where needed;
- no product promotion is implied.

## One-Sentence Doctrine

Use deterministic code to package and index small private reasoning tasks,
subagents to create compact source-grounded pressure, and Step 6 to perform the
actual final judgment.
