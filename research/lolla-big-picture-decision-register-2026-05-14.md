# Lolla Big-Picture Decision Register

Date: 2026-05-14

Status: research control document. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, Lane 1, the canonical knowledge base, or default
`/lolla` execution.

Parent:

- `research/lolla-reasoning-preservation-core-vision-2026-05-14.md`

Related:

- `research/pre-step6-cognitive-worker-system-plan-2026-05-16.md`
- `research/pre-step6-comparison-subagent-readout-2026-05-16.md`
- `research/pre-step6-handoff-best-practices-as-of-2026-05-16.md`
- `research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md`
- `research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md`
- `research/pre-step6-raw-artifact-render-validation-slice-2026-05-16.md`
- `research/pre-step6-raw-artifact-four-fixture-render-readout-2026-05-16.md`
- `research/pre-step6-raw-artifact-answer-consumption-readout-2026-05-16.md`
- `research/pre-step6-raw-vs-control-rubric-comparison-readout-2026-05-16.md`
- `research/pre-step6-native-subagent-producer-test-readout-2026-05-16.md`
- `research/pre-step6-pressure-card-phd-test-readout-2026-05-16.md`
- `research/pre-step6-pressure-card-three-case-replay-readout-2026-05-16.md`
- `research/meta-reasoning-corpus-question-bank-2026-05-15.md`
- `research/post-lane-inquiry-card-vision-2026-05-15.md`
- `research/provider-use-operating-structure-2026-05-15.md`
- `research/lane1-reasoning-bridge-subagent-slice-readout-2026-05-15.md`
- `research/subagent-cognitive-worker-architecture-vision-2026-05-15.md`
- `research/subagent-cognitive-worker-contract-slice-2026-05-15.md`
- `research/subagent-cognitive-worker-live-replay-readout-2026-05-15.md`
- `research/subscription-orchestrator-handoff-local-test-readout-2026-05-15.md`
- `research/candidate-shift-handoff-research-plan-2026-05-14.md`
- `research/candidate-shift-research-harness-reset-2026-05-14.md`
- `research/grounding-audited-source-gate-vs-deterministic-readout-2026-05-14.md`
- `research/source-gate-first-survivor-inspection-2026-05-14.md`
- `research/pre-step6-bevelin-candidate-shift-plan-2026-05-14.md`
- `research/pre-step6-candidate-shift-schema-slice-2026-05-14.md`
- `research/pre-step6-openrouter-candidate-shift-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-dry-run-v2-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-expansion-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-consumption-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-strict-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-strict-control-ablation-2026-05-14.md`
- `research/step6-source-discipline-rule-slice-2026-05-14.md`
- `research/step6-source-discipline-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-refined-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-slice-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-probe-2026-05-14.md`
- `research/step6-provenance-revision-packet-slice-2026-05-14.md`
- `research/step6-provenance-clean-renderer-probe-2026-05-14.md`
- `research/step6-provenance-audit-passed-decision-comparison-2026-05-14.md`
- `research/step6-reviewer-smoothness-bias-audit-2026-05-15.md`
- `research/step6-grounded-practical-force-principle-2026-05-15.md`
- `research/step6-grounded-practical-force-card-provider-strategy-2026-05-15.md`
- `research/step6-card-consumption-ablation-readout-2026-05-15.md`
- `research/step6-card-consumption-operational-gate-followup-2026-05-15.md`
- `research/step6-central-gate-card-consumption-readout-2026-05-15.md`
- `research/lolla-judgment-learning-loop-2026-05-14.md`
- `research/lolla-context-engineering-lessons-2026-05-14.md`
- `research/step6-decomposition-red-team-2026-05-14.md`

## Verdict

REVISE the research path.

We are following some best practices, but not all of them consistently enough.
The biggest risk is confusing research motion with system improvement.

The evidence does not yet justify a runtime change.

## Contradicting Evidence First

The attractive story was:

> Bevelin gives richer interpretation, so if we preserve that interpretation
> better, Step 6 should improve.

The evidence is mixed:

- many variants beat no-addendum baselines but failed against deterministic
  carry-detail controls;
- source-gate-first looked promising in one direct comparison but failed the
  grounding-audited comparison against deterministic carry-detail;
- richer generated packets often preserved more source detail but made final
  answers worse or more overclaimed;
- repair prompts were unstable because they fused too many jobs in one call;
- OpenRouter is useful for narrow cheap cognition, but failed strict
  source-grounding audit consistency on two of three comparable withheld cases;
- OpenAI handled the audit better, but it still did not promote the candidate
  path;
- strict check-only subagent packets produced 2 real wins against a weaker
  control, but tied 2/2 when the deterministic control received the same strict
  source-discipline rule;
- the first prompt-only source-discipline probe on non-Availability cases was
  mixed: strict won Social Proof and baseline won Twaddle;
- refined prompt-only source discipline then won 3/3 on broader
  historical/withheld cases, removed decision-relevant unsupported precision in
  the refined variants, and preserved useful decision movement;
- runtime-shaped revision probing was mixed-negative: refined source discipline
  helped decision interpretation but did not solve grounding, and raw source
  context made the answer worse;
- generic reviewer preference was not enough to settle the question because it
  can reward smoothness; the friction-aware reviewer still preferred
  deterministic controls in parenting and whistleblower;
- grounded-practical-force cards produced a real positive signal on the
  real-estate boundary case, but did not preserve enough operational friction in
  parenting and whistleblower;
- the operational-gate follow-up improved the weak card variants but still lost
  to deterministic control in parenting and whistleblower, and slightly hurt the
  already-good real-estate boundary case;
- the central-gate card produced the best card result so far, winning
  friction-aware review on all three cases after a valid whistleblower rerun,
  but manual inspection still found source/overclaim and public-prose risks;
- the first worker/dossier live replay proved the contract can execute, but
  OpenRouter final consumption failed manual quality inspection in parenting
  and whistleblower by reintroducing unsupported age/legal/timing claims;
- the first subscription-orchestrator handoff pack fixed the parenting
  age/actor failure locally while staying small and path-based, but this is one
  case and not promotion evidence;
- the first Lane 1 reasoning-bridge subagent slice produced source-bound cards
  for real estate and oncologist examples, but only after validation rejected an
  overlong first card and the prompt contract was tightened;
- the 12k-line legacy harness became a burden, which means the research process
  itself started violating the small-slice principle.

So the current honest conclusion is:

> We have not justified a new architecture layer. We now have two narrow
> research candidates worth testing against controls: refined source discipline
> and a validated private Lane 1/V60 bridge. Neither is promotion evidence.

## Current Safe System

Do not lose this baseline.

The safe current shape is:

```text
conversation
  -> OpenRouter / boundary LLM lane cognition
  -> embeddings for recall and vocabulary bridging
  -> deterministic custody, routing, caps, validation, cards, telemetry
  -> Claude/Codex Step 6 final synthesis
  -> Step 6b persistence and V60 private ledger
  -> Step 7/8 post-hoc pressure-check sub-agents and comparison
```

Provider budget doctrine:

```text
subscription orchestrator first
OpenRouter/API only for narrow controlled artifacts
deterministic code for custody, not truth
```

Reason:

- the intended user is already working inside Claude Code, Codex, or a similar
  high-context agent environment;
- adding paid API calls for broad reasoning can burn tokens while weakening
  context handling;
- OpenRouter is valuable when strong prompting, strict JSON, repeatability, or
  cheap parallel ablation gives us a small artifact that prevents prompt bloat;
- final synthesis and high-stakes judgment should stay with the stronger
  high-context reasoner unless tests prove otherwise.

This is still the production-safe architecture because:

- each LLM call has a bounded job;
- deterministic code does not decide truth;
- Step 6 remains the coherent final reasoner;
- post-hoc sub-agents can catch misses without contaminating the initial
  synthesis;
- product docs describe stable behavior, not experimental behavior.

## 2026-05-16 Original Decision: Pre-Step-6 Cognitive Worker Plan

Status: revised later the same day by the corrective handoff-practices decision
below. Keep this section as the receipt for the original docs-only plan, not as
the current build instruction.

Decision:

```text
docs-only first
subagents default producer
Reasoning Bundle handoff
no product promotion
no product docs change
```

Receipt:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
```

What was locked for the original docs-only plan:

- live lanes and V60 stay unchanged;
- `SKILL.md` remains the live execution source of truth;
- the current `HOW_IT_WORKS.md` Step 7 timing contradiction is documented but
  not fixed in this research slice;
- workers are admitted only through a narrow gate: exact question, reason Step 6
  should not handle it directly, needed artifacts, excluded artifacts, and what
  would make the worker unnecessary;
- every worker receives a shared situation brief plus a narrow local slice;
- the planned input is `reasoning_workpack.v1`;
- the worker output remains compact `reasoning_artifact.v1`;
- the Step-6 handoff is `reasoning_bundle.v1`;
- the bundle index is a map of pressure, duplicate, conflict, discard, hard
  boundary, and relaxation, not a truth selector;
- Step 6 remains the final cognition point;
- OpenRouter remains secondary for strict JSON audits, cheap ablations, narrow
  repeatable checks, and optional source/overclaim review.

Critic-pass constraint:

- this is a research default, not a product default;
- "more fresh-context cognition" is not a sufficient rationale;
- every future worker slice must name the control it must beat and the kill
  condition that would stop that worker type;
- if raw artifacts or strict prompt-only controls tie the worker/bundle path,
  the simpler path wins.

Why this decision exists:

- previous worker/dossier and bridge slices proved useful contracts but not
  broad answer-quality lift;
- raw artifacts can perform well when they already carry humility fields;
- the likely value of the bundle is under mixed-producer, high-clutter,
  duplicate/conflict conditions;
- product promotion before that evidence would confuse research motion with
  system improvement.

Original follow-up decision:

```text
research/pre-step6-next-slice-decision-note-2026-05-16.md
```

Before building workers, test whether `reasoning_bundle.v1` improves
Step-6-style consumption over raw compact artifacts. This isolates handoff value
from producer quality. If the bundle ties raw artifacts, raw artifacts win and
the worker/bundle machinery stays unpromoted.

The corrective decision below records the first result of that follow-up: raw
artifacts tied the indexed bundle, so raw artifacts won under the simpler-path
rule.

## 2026-05-16 Corrective Decision: Handoff Best Practices

Decision:

```text
no true handoff
Step 6 remains manager/final reasoner
bounded worker-as-tool calls only after admission
raw reasoning_artifact.v1 consumption first
reasoning_bundle.v1 optional until it beats raw artifacts
no product promotion
no product docs change
```

Receipts:

```text
research/pre-step6-comparison-subagent-readout-2026-05-16.md
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
research/pre-step6-comparison-aggregate-readout-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md
research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md
```

Why this correction exists:

- the manual comparison said the indexed bundle won all three fixtures;
- a less-author-biased subagent comparison found raw artifacts tied the indexed
  bundle in all three fixtures;
- under the standing rule, ties go to the simpler path, so raw artifacts won
  all three;
- source-backed handoff research points toward manager/worker or worker-as-tool
  patterns for Lolla, not true user-facing handoff;
- current handoff best practice requires strong single-agent/raw-artifact
  baselines, small explicit payloads, separated state and visible context,
  provenance, validation, and boundary observability.

What changed:

- `reasoning_bundle.v1` is no longer the default next build;
- subagents remain a research option, but only as bounded worker calls;
- raw `reasoning_artifact.v1` discipline becomes the immediate baseline to
  harvest and test;
- any future bundle work must prove final-answer lift over careful raw artifact
  use, not merely better private auditability.

## 2026-05-16 Follow-Up Decision: Raw Artifact Discipline First

Decision:

```text
raw artifact consumption discipline is the current next path
mother address no-worker sentinel added
bundle runtime remains paused
worker orchestration remains paused
implementation-if-any starts with raw artifact render/validation fixture
no product promotion
no product docs change
```

Receipts:

```text
research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md
research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md
research/pre-step6-raw-artifact-render-validation-slice-2026-05-16.md
research/pre-step6-raw-artifact-four-fixture-render-readout-2026-05-16.md
research/pre-step6-raw-artifact-answer-consumption-readout-2026-05-16.md
research/pre-step6-raw-vs-control-rubric-comparison-readout-2026-05-16.md
research/pre-step6-comparison-fixtures/mother-deciding-address-year-20260430T113301Z.md
```

Why this follow-up exists:

- it harvests the simpler-path lesson from the subagent comparison;
- it makes Step 6 consumption rules explicit before any renderer exists;
- it adds a negative case where the correct decision is to decline extra
  cognition rather than force a worker lens;
- it keeps the burden of proof on bundle and worker machinery.

Implementation follow-up:

```text
scripts/research/pre_step6_raw_artifacts.py
tests/test_pre_step6_raw_artifacts.py
research/pre-step6-raw-artifact-fixtures/mother-address-year.raw-artifact-handoff.v1.json
```

This follow-up is a dormant research harness only. It validates and renders the
mother no-worker raw handoff; it does not change product behavior.

Four-fixture follow-up:

```text
PhD, founder, consultant, and mother raw handoffs validate and render under cap
next check is Step-6-style answer consumption, not more schema
```

Answer-consumption follow-up:

```text
authored Step-6-style answer cores validate for all four raw handoffs
public machinery hygiene passes
next check is less-author-biased comparison against current-control answer cores
```

Strict-rubric follow-up:

```text
raw answer cores beat current-control answer cores in all four comparisons
control wins zero criteria
no bundle challenger triggered
no worker orchestration authorized
```

Native-producer follow-up:

```text
native subagent boundary/evidence-gate workers produced useful artifacts
admission gate failed the mother no-worker sentinel
next slice must test admission before worker production
no runtime promotion
```

Admission-gate follow-up:

```text
separate admission-only stage admitted PhD, founder, consultant
mother no-worker sentinel declined
production ran only for admitted cases
produced artifacts recovered targeted boundary/evidence gates
research-only pass for two-stage shape
no runtime promotion
```

Workpack-harness follow-up:

```text
research-only pre_step6_workpacks.py validator/renderer added
four admission fixtures added
three admitted boundary/evidence-gate workpack fixtures added
mother no-worker sentinel has no workpack
pytest covers admission pattern, caps, prompt order, declined-reference rejection
no runtime promotion
```

Rendered-workpack replay follow-up:

```text
rendered prompts reproduced targeted content lift in PhD, founder, consultant
mother no-worker sentinel stayed skipped
founder returned strict JSON
PhD and consultant returned human-readable field lists
content contract promising, serialization contract too loose
next slice must require exact reasoning_artifact.v1 JSON and validate outputs
no runtime promotion
```

Strict-output-contract follow-up:

```text
workpack renderer now requires exactly one JSON object
worker-output validator added
three normalized rendered-replay worker-output fixtures added
tests reject missing fields, oversized payloads, invalid arrays, unknown fields
next slice must rerun native subagents against strict JSON prompt
no runtime promotion
```

Strict-JSON replay follow-up:

```text
strict JSON syntax passed 3/3
exact key set passed 3/3
content lift passed 3/3
mother sentinel stayed skipped
outputs were 2,810-3,134 serialized chars
1,500-char cap passed 0/3
schema now allows short arrays for source_grounding and contribution
compression is next blocker
no runtime promotion
```

Compact-JSON replay follow-up:

```text
compact skeleton prompt reduced PhD from 3,091 to 1,769 chars
compact skeleton prompt reduced consultant from 3,134 to 2,068 chars
content stayed useful
1,500-char cap still passed 0/2
do not rerun more workers until compression strategy changes
recommended next slice: one-case rich-worker plus compact-card compressor test
no runtime promotion
```

PhD producer/compressor follow-up:

```text
separate native compressor preserved fallback executability and Silva/data gates
compression attempts: 1,677 -> 1,617 -> 1,569 -> 1,540 validator chars
1,500-char cap passed 0/4
meaning preservation passed
cap-obedient compression failed
next useful test is smaller Step-6 card schema, not another full artifact retry
no runtime promotion
```

Pressure-card follow-up:

```text
smaller pre_step6_pressure_card.v1 contract added for Step-6 consumption
native PhD attempt without field budgets preserved gates but failed: 1,070 chars
native PhD retry with field budgets passed: 689 chars
fallback executability and Silva/data access survived
full reasoning_artifact.v1 remains audit/provenance, not default consumption
next useful check is founder and consultant pressure-card replay
no runtime promotion
```

Three-case pressure-card follow-up:

```text
same field-budgeted pressure-card prompt passed PhD, founder, consultant
validator sizes: 689, 682, 679 chars
case-specific gate survival passed in tests
pressure cards are now the next challenger to careful raw artifact consumption
final-answer lift remains unproven
no runtime promotion
```

## Target Architecture If Research Eventually Wins

The likely long-term target is not a Bevelin lane, not a giant prompt, and not
a deterministic selector pretending to reason.

The current near-term target is smaller:

```text
conversation
  -> existing lane cognition stays stable
  -> selected pressures and V60 material preserve source custody
  -> deterministic render/validation produces small reasoning_artifact.v1 inputs
  -> Step 6 consumes raw artifacts under explicit discipline
  -> optional bounded worker or bundle challenger only if raw artifacts lose
```

The larger worker/bundle target below is conditional. It should return only if
the raw artifact path fails or a future high-clutter challenger proves visible
final-answer lift.

The larger conditional target is:

```text
conversation
  -> existing lane cognition stays stable
  -> selected pressures and V60 material preserve source custody
  -> deterministic relevance planner creates small reasoning_workpack.v1 tasks
  -> subagent cognitive workers produce reasoning_artifact.v1 pressure
  -> deterministic code validates, caps, dedupes, and receipts artifacts
  -> reasoning_bundle.v1 maps pressure, duplicate, conflict, discard, and boundary
  -> Step 6 synthesizes from full context plus compact indexed pressure
  -> optional source/overclaim audit remains during research
```

The older immediate target for this branch was smaller than that architecture:

```text
current Step6 path
  -> optional validated private bridge from selected Lane 1/V60 pressure
  -> compare archived final answers against current controls
```

That bridge work remains part of the evidence trail. The current favored target
is now raw-first but still research-only:

```text
raw reasoning_artifact.v1
  -> optional compact pre_step6_pressure_card.v1 rendering
  -> Step 6 final arbitration
  -> optional reasoning_workpack.v1 / reasoning_bundle.v1 only if earned
```

The key phrase is:

> Step 6 synthesizes from compact candidate shifts. It does not merely gather
> them, and it does not receive raw Bevelin theory.

Candidate shifts are not commands. They are pressure with receipts.

Each useful candidate shift must answer:

- what might change in the answer;
- what source evidence supports it;
- what evidence gate would test it;
- what happens if it is ignored;
- what goes wrong if it is forced;
- whether it should be visible advice, a diagnostic question, a private
  guardrail, or set aside.

## Crossed-Out Paths

These should not be reopened without new evidence.

### Bevelin Lane 1.5

Decision: parked.

Reason:

- overlaps too much with the Munger tendency spine;
- creates taxonomy and brand complexity;
- risks destabilizing Lane 1 recall and distribution.

### Canonical KB Mutation

Decision: blocked during this research phase.

Reason:

- the canonical corpus has a prepared distribution;
- adding Bevelin after the fact can over-promote it;
- this would hide an editorial choice inside the knowledge base.

### Add Bevelin Directly To Step 6

Decision: blocked.

Reason:

- Step 6 is already overloaded;
- this adds abstract theory to the heaviest prompt;
- likely creates generic caution rather than better reasoning.

### Source-Gate-First As Promotion Candidate

Decision: do not promote.

Reason:

- grounding-audited comparison did not beat deterministic carry-detail;
- OpenAI judged deterministic stronger on two comparable withheld cases and
  tied one;
- source-gate-first gained concreteness partly through unsupported precision.

Survivor:

- the renderer is parked;
- a smaller `source_specific_check` field may survive inside future
  candidate-shift packets;
- that field may ask a source-specific question or evidence gate, but must not
  invent odds, counts, timelines, or thresholds.

### One-Call Source-Preservation Repair

Decision: do not promote.

Reason:

- it fused omission detection, source-use judgment, safety judgment, and rewrite;
- it sometimes revived invented thresholds or over-preserved weak details.

### Full Micro-Bevelin Packet Replacement

Decision: parked.

Reason:

- preserved source details better in some runs;
- hurt final answer quality in comparable withheld cases;
- gave too much framing authority to the generated packet.

### Hybrid Micro-Carry As Runtime Change

Decision: parked.

Reason:

- strong on withheld cases;
- failed to generalize cleanly on historical cases;
- deterministic carry-detail remained the stronger broad local control.

### Source-Exact Carry Alone

Decision: parked.

Reason:

- clean and cheap generation;
- too thin to preserve decision structure;
- PhD case regressed.

### Source-First Rendering

Decision: parked.

Reason:

- mixed direct comparison against deterministic carry-detail;
- did not solve material/high-severity omission pattern.

### Compact Source-Detail Contract

Decision: parked.

Reason:

- improved one omission metric;
- worsened material omissions and lost strict direct comparison.

### Broad Direct-Compare Judge As Promotion Oracle

Decision: blocked.

Reason:

- it can notice unsupported precision and still reward the answer containing it;
- evaluation must be decomposed before it can guide promotion.

### Grow The 12k-Line Legacy Harness

Decision: blocked.

Reason:

- it stopped being a clean experiment surface;
- new work belongs in small, disposable research modules.

## Still-Alive Research Paths

### 1. Deterministic Carry-Detail Control

Status: current local control.

This is not a magical final design. It is simply the strongest control we have
not yet beaten reliably.

### 2. Decomposed Evaluation

Status: keep local.

Useful because it separates:

- source-grounding audit;
- decision-quality comparison;
- final human inspection.

Not useful as a promotion oracle yet.

### 3. Source-Use Adjudication

Status: keep as research idea.

The useful insight is not the repair. The useful insight is the disposition:

- preserve as detail;
- convert to question;
- convert to gate;
- hold private;
- set aside.

This may become part of a candidate-shift packet if it proves useful.

### 4. Pre-Step6 Candidate-Shift Sub-Agents

Status: live research idea, weakened by strict-control ablation, not promotion
evidence.

Why alive:

- aligns with context-engineering best practice;
- lets each sub-agent reason in a narrower context;
- may reduce Step 6 overload without stuffing Step 6 with more theory.

Why not promoted:

- final-answer consumption is now tested only on two fair cases;
- both fair cases are still Availability-family cases;
- strict deterministic control tied strict control plus check-only subagent
  checks in both fair cases;
- the best result may come from the strict no-new-concrete-categories rule, not
  from the subagent checks themselves;
- OpenAI/OpenRouter provider repeatability was unavailable for this slice;
- Codex subagents generated, audited, and judged the results, so model-family
  independence is limited;
- cost may be high;
- may create committee prose;
- sub-agents may overfit narrow lane context.

Planning update:

- compare subagents and OpenRouter as producers of the same
  `CandidateShiftPacket`, not as separate architectures;
- define the packet contract before choosing the producer;
- first schema/validator/prompt-contract slice is implemented locally in
  `scripts/research/candidate_shift_eval/handoff.py`;
- manual archived Lane 1 handoff validated structurally on 7 cases and 16
  packets;
- OpenRouter producer quality remains untested because the first live dry-run
  produced 7 `missing_api_key` provider failures and 0 packets;
- failed provider calls are now explicitly marked `provider_failed`, not
  `valid_empty`;
- first subagent producer dry run returned 2 candidate shifts on one case, but
  failed tightened validation because one packet leaked `Step 6` in generated
  prose;
- second subagent dry run on the same case validated cleanly after exact
  source-ref and lane-only source-evidence instructions;
- expanded subagent dry run now validates on three withheld Availability cases
  with 6 packets, after catching label leakage and per-packet precision drift;
- PhD remains producer-valid only and should not enter final-answer comparison
  until the long-context visibility issue is handled;
- first consumption probe against deterministic carry-detail produced 2 weak
  candidate wins and 0 real wins, with no public machinery leakage but some
  unsupported precision in every answer variant;
- the useful part was the source-specific question/gate; the risky part was
  broad generated candidate prose that invited adjacent concrete examples;
- check-only rendering, which hides broad generated candidate prose, kept the
  2 weak wins and 0 real wins while reducing candidate decision-relevant
  unsupported precision from 2 cases to 1;
- strict check-only rendering added a private rule against new concrete
  categories unless source-backed and produced 2 real candidate wins, 0 weak
  wins, 0 public machinery leaks, and 0 candidate variants with
  decision-relevant unsupported precision on the same two cases;
- strict-control ablation then tied both fair cases, 9 vs 9, when the
  deterministic control received the same strict source-discipline rule;
- current best lesson is strict source discipline, not the subagent layer;
- refined source-discipline prompt-only testing now has positive evidence
  across three broader reasoning shapes, which shifts the next step away from subagent
  runtime work and toward a tiny prompt-placement experiment;
- this makes subagents a research tool and possible future candidate, not a
  promotion candidate;
- start research-only and off by default;
- see `research/pre-step6-bevelin-candidate-shift-plan-2026-05-14.md` and
  `research/pre-step6-subagent-candidate-shift-consumption-probe-2026-05-14.md`
  and `research/pre-step6-subagent-candidate-shift-check-only-probe-2026-05-14.md`
  and `research/pre-step6-subagent-candidate-shift-check-only-strict-probe-2026-05-14.md`
  and `research/pre-step6-subagent-candidate-shift-strict-control-ablation-2026-05-14.md`.

### 5. OpenRouter Micro-Bevelin As Support, Not Owner

Status: weak/conditional.

Possible role:

- cheap generation of small candidate handles from selected Lane 1 pressure;
- schema-bound grounded-practical-force cards for ablation.

Not allowed:

- final judgment;
- source-grounding audit ownership when strictness matters;
- mental-model remapping;
- standalone promotion.

Latest card result:

- `strict_card` won both generic and friction-aware review on the real-estate
  boundary case;
- `strict_card` lost friction-aware review to `deterministic_control` in
  parenting;
- `strict_card` lost both V1 reviews to `deterministic_control` in
  whistleblower;
- V2 is a fixture warning because the last archived user turns are often
  closure/thanks turns, not the main decision target.
- the operational-gate follow-up improved operational card scores but did not
  beat deterministic control; real estate still preferred the prior strict card.
- the central-gate follow-up then won friction-aware review on all three cases
  after a valid whistleblower rerun, but still needs source/overclaim audit.

Decision:

- keep cards as research machinery;
- do not promote;
- do not keep enlarging the consumer prompt;
- central-gate card is the best current card shape;
- next step is source/overclaim audit, not runtime promotion.

### 6. Provenance Packet Plus Clean Renderer

Status: keep-local, research-only.

Why alive:

- the packet separates user facts from assistant-draft claims;
- it caught real unsupported draft precision;
- the clean renderer removed visible patch machinery and produced usable prose;
- a hardened post-render audit caught unsupported certainty that clean prose
  smuggled back in;
- audit-driven clean revision passed the same hardened re-audit on the first
  real-estate case;
- the audit-passed answer then won the first decision-quality comparison against
  prior local controls on the same case;
- the broader parenting repeat passed after a useful claim-type contract repair
  and won decision comparison 9 vs 8 vs 6;
- the whistleblower / institutional-risk repeat passed the first audit without
  targeted revision and won decision comparison 9 vs 8 vs 7;
- this fits the context-engineering pattern of one narrow cognitive job per
  call.

Why not promoted:

- V1 clean renderer reintroduced unsupported numeric precision;
- V2 fixed the largest numeric rebound but still produced unsupported certainty
  such as categorical margin claims and market/old-house color;
- V3 modal-guard renderer-only run still had over-strong phrasing;
- three case families are still a small sample;
- the broader parenting run cost 35,390 tokens and the whistleblower run cost
  24,640 tokens, so cost is a real constraint.

Surviving lesson:

```text
Numeric de-precision is insufficient.
The renderer also needs modal-strength discipline.
```

Next:

- compare the audit-passed revised clean answer against the prior best local
  controls; done on real estate, where it won 9 vs 6 vs 5, and parenting, where
  it won 9 vs 8 vs 6, and whistleblower, where it won 9 vs 8 vs 7;
- package the sequence as a reusable off-by-default research harness next;
- only consider promotion after both provenance cleanliness and decision
  usefulness hold with defensible cost;
- do not treat a clean answer as provenance-clean merely because it hides
  machinery.

### 7. Meta-Reasoning Corpus As Process Design Input

Status: live research input, not runtime change.

Why alive:

- the current bottleneck is no longer only "which mental model applies";
- the harder question is how the system should think, compress, evaluate, and
  pass useful pressure without bloating Step 6;
- the ready-book corpus contains material on inquiry, question design,
  uncertainty, disconfirmation, framing, stopping rules, systems, AI skill
  design, and sycophancy risk;
- this can sharpen OpenRouter prompts, central-gate cards, source/overclaim
  audits, and subagent review roles.

Why not promoted:

- book-derived process principles are hypotheses, not system behavior;
- asking many books can create a new kind of bloat if the output is not
  compressed into narrow questions or card fields;
- this does not justify mutating the canonical knowledge base;
- this does not justify adding a new lane;
- the output must still improve final answers, not only sound wiser.

Surviving doctrine:

```text
store rich cognition for audit;
inject only compressed survivor pressure;
use corpus questions to improve the thinking process, not to add more names.
```

Next:

- put the Priority A batch from
  `research/meta-reasoning-corpus-question-bank-2026-05-15.md` into RAG;
- ask the compact 24-question universal set about question design, evidence
  gates, calibration, sequence/stop-rules, set-aside, compression, OpenRouter
  versus subagent roles, and evaluation;
- keep the 120-question bank as an appendix only if the compact synthesis shows
  a specific blind spot;
- synthesize across books before changing code;
- test whether the resulting process changes beat the current central-gate /
  deterministic-control baselines.

### 8. Post-Lane Inquiry Cards

Status: live research idea, not runtime change.

Why alive:

- pre-system question generation is likely to be generic and weakly
  differentiated;
- after lanes, retrieval, selected pressures, and source custody, the system can
  ask questions about what it actually found;
- this may preserve Lolla's edge better than generic clarification prompts;
- a post-lane inquiry card can help the final reasoner decide whether selected
  pressure should be used, set aside, softened, or converted into a user-facing
  diagnostic question.

Why not promoted:

- it has not been implemented or tested;
- post-lane questions may inherit lane bias and confirm the system's own picks;
- it can create question spam or answer paralysis;
- it can bloat Step 6 unless only a compact card is injected;
- it must beat current controls on final-answer usefulness, not just produce
  clever questions.

Surviving doctrine:

```text
do not ask generic questions before Lolla creates differentiation;
ask post-lane questions about selected pressure, source evidence, missing
denominators, alternative frames, and overclaim risk.
```

Candidate object:

```text
PostLaneInquiryCard
- central_question
- linked_pressure_or_lane
- why_it_matters
- missing_fact_or_denominator
- evidence_gate
- alternative_frame_or_disconfirmation
- overreach_warning
- answer_now_or_ask_user
- user_facing_question_if_blocking
- private_use_instruction
```

Next:

- keep this research-only and off by default;
- compare current flow, `PostLaneInquiryCard`, `CentralGateCard`, and combined
  card consumption on archived cases;
- require anti-confirmation questions so the card does not merely reinforce
  lane picks;
- judge final-answer improvement, not question quantity.

### 9. Subagent Cognitive Workers Before Final Synthesis

Status: highest-priority research architecture idea, not runtime change.

Why alive:

- the immediate problem is relevance delivery to Claude Code or another
  orchestrator;
- post-hoc pressure checks catch misses late, but they do not reduce the
  context burden before the final answer is written;
- subagents can do narrow judgment-heavy work on separate slices and return
  compact pressure before final synthesis;
- this aligns with context-engineering best practice: decompose cognitive work,
  keep each worker context narrow, then synthesize from compressed outputs.

Why not promoted:

- previous pre-Step6 subagent tests did not beat strict prompt-only controls
  convincingly;
- the old prompts were still close to "checks" rather than a full worker /
  dossier architecture;
- subagents can overfit narrow lane context;
- multiple workers can create committee noise;
- cost can climb quickly;
- replacing post-hoc checks too early would remove a useful safety net.

Surviving doctrine:

```text
subagents should not be after-checks in the target architecture;
they should be narrow cognitive workers whose outputs are validated,
compressed, and given to the final reasoner only when relevant.
```

Historical candidate flow from the first worker/dossier slice:

```text
lane cards / chunks / source evidence
  -> CognitiveWorkpack
  -> subagent cognitive worker
  -> CognitiveWorkerPacket
  -> deterministic validation / dedupe / caps
  -> CognitionDossier
  -> final reasoner
```

Current favored flow:

```text
lane cards / chunks / source evidence
  -> reasoning_workpack.v1
  -> subagent cognitive worker
  -> reasoning_artifact.v1
  -> deterministic validation / dedupe / caps
  -> reasoning_bundle.v1
  -> Step 6 final reasoner
```

First worker to test:

```text
inquiry / boundary worker
```

Reason:

- it connects directly to the post-lane inquiry direction;
- it is narrow enough for a first slice;
- it can produce a central question, evidence gate, alternative frame, and
  source/overclaim boundary;
- it can be compared against the current central-gate card.

Next:

- keep current Step 7/8 after-check path as the product/control baseline;
- design a single-worker off-by-default research slice;
- compare current flow, central-gate card, inquiry-card, and worker dossier;
- promote nothing until final answers improve across case families with
  defensible cost and no machinery leakage.

## What A Real Improvement Must Look Like

A real improvement is not:

- more artifacts;
- more models;
- more precise-looking thresholds;
- better intermediate JSON;
- a prettier readout;
- a judge saying "candidate wins" on one case.

A real improvement is:

- final Step 6 answer is sharper;
- fewer important source-backed pressures disappear;
- unsupported precision goes down, not up;
- Step 8 finds fewer meaningful misses;
- the answer stays decisive and human-readable;
- no public machinery leaks;
- gains hold across at least withheld and historical cases;
- cost and latency remain defensible.

## Best-Practice Alignment Check

We are aligned when:

- every cognitive task has a narrow owner;
- deterministic code carries receipts but does not decide truth;
- Step 6 remains the final synthesizer;
- context given to Step 6 is smaller and more useful, not simply larger;
- negative results are recorded as carefully as wins;
- candidate paths are compared against the current best control, not only
  against no-addendum;
- product docs remain untouched until runtime behavior changes.

We are drifting when:

- a research script grows faster than evidence;
- we add another repair prompt after a failure instead of asking why the first
  pass is weak;
- we judge by intermediate artifact quality;
- we keep testing one promising case family;
- we let a deterministic route become a hidden truth selector;
- we treat sub-agent agreement as truth;
- we keep reopening already-parked paths without new evidence.

## Current Recommendation

Stop broad experimentation for a moment.

The next useful slice is not another agent layer by default and not raw source
context. The runtime-shaped probe showed the bottleneck more precisely:

```text
the revision model can treat old assistant-draft details as if they are source
evidence
```

The provenance-shaped revision packet contract now exists and the first
producer/consumer/clean-renderer probe has run.

```text
source-provenance packet producer
  -> validator
  -> patch-style revision consumer
  -> clean renderer
```

Decision:

```text
revise
```

The path is alive but not promotable. It improved source custody and public
shape, but clean prose still smuggled unsupported certainty after numeric
precision was softened.

The first post-render audit was too lenient and passed the flawed answer. The
hardened audit returned:

```text
verdict: revise_material
recommended_action: revise
```

It flagged the same class of issue the fresh judge noticed: zero-buffer claims,
the boiler example, and over-strong modal language.

The audit-driven clean revision then passed the same hardened audit:

```text
clean rendered answer
  -> focused source-grounding and modal-strength audit
  -> audit-driven clean revision
  -> re-audit
  -> re-audit verdict: pass
```

Receipt:

```text
research/spikes/candidate-shift-handoff/step6-provenance-audit-driven-clean-revision-real-estate-v1-2026-05-14.json
```

Next:

```text
audit-passed revised clean answer
  -> decision-quality comparison against prior best controls
  -> broader reasoning-shape repeat
```

The decision-quality comparison completed on the same real-estate case:

```text
audit_passed_revision: 9
prior_grounded_draft: 6
deterministic_control: 5
recommended_next_action: broaden_reasoning_shapes
```

The broader reasoning-shape repeat then completed the same sequence after repairing a
too-narrow claim-type contract:

```text
packet validation: valid
first audit: revise_minor
re-audit after targeted revision: pass
decision comparison:
  audit_passed_revision: 9
  prior_grounded_draft: 8
  deterministic_control: 6
total tokens: 35390
```

The whistleblower / institutional-risk repeat then passed the first audit
without targeted revision:

```text
packet validation: valid
first audit: pass
decision comparison:
  audit_passed_revision: 9
  prior_grounded_draft: 8
  deterministic_control: 7
total tokens: 24640
```

Readout:

```text
research/step6-provenance-audit-passed-decision-comparison-2026-05-14.md
research/meta-reasoning-corpus-question-bank-2026-05-15.md
```

Current recorded inspections:

- `research/source-gate-first-survivor-inspection-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-strict-control-ablation-2026-05-14.md`
- `research/step6-source-discipline-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-refined-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-slice-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-probe-2026-05-14.md`
- `research/step6-provenance-revision-packet-slice-2026-05-14.md`
- `research/step6-provenance-clean-renderer-probe-2026-05-14.md`

Result:

- park source-gate-first as a renderer;
- keep `source_specific_check` as a possible future candidate-shift packet
  field;
- keep subagents for research audits and fresh-context comparisons;
- carry forward source discipline as a useful principle, but do not promote it
  as a runtime default;
- do not add raw source-context bulk; it failed the first runtime-shaped probe;
- keep the provenance-shaped producer/consumer/clean-renderer/audit path local;
- the audit-driven revision passed hardened re-audit and won decision-quality
  comparison on real-estate, parenting, and whistleblower case families, so
  package a reusable off-by-default research harness and inspect cost before
  adding another repair layer;
- grounded-practical-force cards are alive only as a research addendum surface:
  current evidence says they help in boundary/numeric cases but are not yet
  reliable for high-stakes operational friction;
- the central-gate card is the strongest card candidate so far, but it still
  needs source/overclaim audit and high-context review;
- the meta-reasoning corpus question bank is now the control surface for asking
  books about process design: better questions, evidence gates, calibration,
  stop-rules, set-aside logic, compression, provider roles, and evaluation;
- do not promote a pre-Step6 subagent layer until it beats strict prompt-only
  controls across multiple case families.

Do not promote runtime default behavior until this produces a clear
system-level win inside the runtime-shaped path.

## Latest Decision: Subscription Handoff Harness

Date: 2026-05-15

Decision:

```text
keep_local
```

The current best architecture candidate is:

```text
small path-based handoff pack
  + high-context orchestrator synthesis
  + focused source/overclaim audit
```

Why:

- OpenRouter final consumption failed hard on parenting and over-specified
  whistleblower;
- the high-context handoff answers passed focused source audits on all three
  local cases;
- the handoff pack avoids base-prompt bloat by carrying source paths, critical
  anchors, and compact dossier pressure only;
- deterministic code is acting as custody and validation, not truth selection.

Constraint:

```text
source audit is secondary evidence
```

The audit caught the parenting age inversion, but it also passed a real-estate
future-supply comfort sentence that manual review still considers unsupported.
It also changed whistleblower from revise to pass across reruns, and the
central-gate whistleblower audit first surfaced a spouse-protection legal-ish
claim before passing it on rerun. This confirms the older System B rule: LLM
judges help, but do not decide product truth.

Next:

```text
compare high-context handoff answers against cleaner current default controls
record audit/manual disagreements
do not edit SKILL.md or HOW_IT_WORKS.md until the runtime-shaped path wins
```

Receipts:

```text
research/subscription-orchestrator-handoff-local-test-readout-2026-05-15.md
scripts/research/run_orchestrator_answer_source_audit.py
research/spikes/candidate-shift-handoff/orchestrator-answer-source-audit-*-openrouter-v1-2026-05-15.json
```

## Latest Test: Direct Handoff Control Comparison

Date: 2026-05-15

Decision:

```text
keep_local
```

Direct friction-aware comparison:

```text
parenting:
  winner: high-context handoff

real_estate_boundary:
  winner: central-gate final

whistleblower:
  winner: high-context handoff
```

Interpretation:

```text
the handoff path is not universally better
```

It looks valuable in operational/high-stakes cases where the answer has to
preserve sequence, counsel/safety gates, calibration, and source boundaries. But
in the clean real-estate budget-boundary case, the smaller central-gate answer
was sharper.

Architectural implication:

```text
use the smallest sufficient reasoning aid
```

Do not build a heavier handoff layer as default behavior. Keep it as a candidate
for richer cases until cleaner control comparisons confirm it.

Receipts:

```text
scripts/research/run_handoff_control_comparison.py
research/spikes/candidate-shift-handoff/handoff-control-comparison-*-openrouter-v1-2026-05-15.json
```

## Latest Test: Lane 1 Bridge Final Consumption

Date: 2026-05-15

Decision:

```text
keep_local_research_candidate
```

What changed:

```text
we tested the validated Lane 1 bridge card in final-answer consumption
```

Comparison:

```text
control = conversation + selected-model context
bridge  = conversation + selected-model context + compact bridge card
```

Cases:

```text
real-estate-reward-repair
oncologist-reward-repair
```

Result:

```text
real estate: bridge won narrowly
oncologist:  bridge won narrowly
```

Why this is not product promotion:

- controls were already strong;
- only two cases were tested;
- both LLM reviewers invented invalid promotion labels;
- no irrelevant/weak bridge case has been run yet;
- no human/high-context review has signed off.

What we learned:

```text
Bevelin is most useful here as reasoning hygiene, not as a new lane or
knowledge-base enrichment.
```

The valuable unit is a tiny private bridge:

```text
why surfaced
evidence gate
boundary
use instruction
discard condition
```

The evaluation rule is now sharper:

```text
do not reward smoothness
reward grounded practical force
```

Receipts:

```text
research/lane1-bridge-final-consumption-readout-2026-05-15.md
scripts/research/lane1_bridge_consumption.py
tests/test_lane1_bridge_consumption.py
research/spikes/lane1-bridge-consumption/
```

Boundary update:

```text
real-estate script-only:
  bridge narrow win

speculative EV direct decision:
  control win
  bridge label: smoothed_useful_friction
```

Decision stays:

```text
keep_local_research_candidate
```

Reason:

- the bridge is not a universal improvement;
- the speculative EV case shows it can soften a hard stop-rule;
- this is exactly the failure mode we were worried about with smoothness bias;
- the evaluator rejected the bridge in that case, which is a healthy signal.

Updated rule:

```text
do not move bridge findings to the real project until it wins or correctly
sets itself aside across negative cases, not only positive cases
```

Follow-up repair:

```text
speculative EV hard-stop v2:
  bridge win after the prompt/card explicitly preserved the hard stop-rule
  key line preserved: no concrete access, no $12,000 spend

speculative EV concrete-access:
  tie after new source facts appeared
  old automatic no relaxed because two relevant meetings were confirmed
  new boundary preserved: no numerical EV and no spend unless the downside
  plan survives
```

Decision stays:

```text
keep_local_research_candidate
do_not_promote
```

Reason:

- the v2 repair shows the bridge can preserve hard boundaries when instructed;
- the concrete-access probe shows it does not have to become blindly rigid;
- the tie shows a strong control should not lose just because a bridge exists;
- this is still a small local test set, and one repaired case is not product
  evidence.

Updated rule:

```text
promotion requires boundary behavior, not just bridge wins:
preserve hard stop-rules when facts support them
relax hard stop-rules when facts materially change
tie or lose when selected-model context already carries the reasoning
```

Additional constraint:

```text
promotion also requires multi-lane handoff behavior
```

Reason:

- the final user-facing answer will not be written from the Lane 1 bridge alone;
- Claude Code, Codex, or another orchestrator will receive other lane material;
- Lane 2 and deterministic mental-model support may already carry the needed
  reasoning;
- other subagents may add their own compact artifacts;
- the bridge must not become an attention hog inside the final bundle.

Decision:

```text
do not test only isolated bridge-vs-control after this phase
```

Next promotion gate:

```text
test bundled handoff:
  selected-model context
  Lane 1 bridge
  at least one other lane/card artifact
  final answer
  friction-aware review
```

Expected behavior:

```text
the final reasoner can prioritize across artifacts
the bridge can be used, ignored, or outweighed
no artifact gets automatic priority because it exists
```

First bundled test result:

```text
speculative EV concrete-access bundled:
  control wins narrowly
```

Meaning:

- the other lane / worker artifact carried the opportunity-cost pressure well;
- the bridge answer used expected value correctly but mostly repeated the same
  boundary;
- the control preserved the concrete contractor-help alternative more clearly;
- the reviewer correctly did not reward bridge presence as a win.

Decision impact:

```text
keep_local_research_candidate
do_not_promote
```

Promotion gate is now stricter:

```text
the bridge must prove marginal value inside a bundle,
or correctly demote itself when another lane already carries the reasoning
```

Latest research slice:

```text
Reasoning Bundle v1
```

Decision:

```text
keep_local_research_candidate
do_not_promote
```

Why:

- it models the real final boss: Claude Code / Codex rethinking from multiple
  artifacts before Step 6;
- it validates multi-artifact input, arbitration index, and final-consumption
  output shape;
- first run correctly made opportunity cost primary and expected value
  lower-priority support;
- it still has only one case and no source/overclaim audit yet.

Next gate:

```text
compare indexed bundle vs raw bundled context
```

Promotion remains blocked until bundle consumption beats or ties controls across
case families and survives source/overclaim review.

Update after live subagent follow-up:

```text
raw control: good answer, but no duplicate demotion
Bevelin worker: valid narrow artifact, promising as interpretation discipline
source/overclaim audit: pass on indexed-bundle answer
```

Receipts:

```text
research/spikes/reasoning-bundle/reasoning-bundle-live-subagent-readout-v1-2026-05-15.md
research/spikes/reasoning-bundle/speculative-ev-concrete-access-raw-consumption-answer-subagent-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-bevelin-boundary-worker-artifact-subagent-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-answer-source-audit-subagent-v1-2026-05-15.json
```

Decision remains:

```text
keep_local_research_candidate
do_not_promote
```

Why promotion is still blocked:

- only one compact decision case has live subagent receipts;
- the raw control was also strong, so the indexed bundle has not proven broad
  superiority;
- the indexed bundle's observed edge is duplicate/priority handling, which
  matters most in overload and conflict cases;
- those cases are prepared as deterministic receipts but still need live final
  reasoner runs.

Next promotion gate:

```text
run indexed-vs-raw on conflict-heavy and overload cases
run source/overclaim audit after each final answer
compare whether the index helps the final reasoner discard, demote, or preserve
artifacts without smoothing away useful friction
```

Update after conflict/overload live checks:

```text
indexed did not clearly beat raw on compact public-answer quality
raw performed well because artifacts already carried humility fields
indexed made arbitration behavior more explicit
```

Receipts:

```text
research/spikes/reasoning-bundle/reasoning-bundle-conflict-overload-live-readout-v1-2026-05-15.md
research/spikes/reasoning-bundle/speculative-ev-conflict-indexed-answer-subagent-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-conflict-raw-answer-subagent-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-overload-indexed-answer-subagent-v1-2026-05-15.json
research/spikes/reasoning-bundle/speculative-ev-overload-raw-answer-subagent-v1-2026-05-15.json
```

Revised decision:

```text
keep_local_research_candidate
do_not_promote
preserve artifact-level humility as mandatory
test bundle index under broader/messier conditions before promotion
```

This is a useful negative/nuanced result. It prevents the team from turning the
bundle index into a sacred architecture layer. The stronger lesson is:

```text
subagent artifacts must know how to demote themselves
the bundle index helps Step 6 see that demotion quickly
```

Terminology correction:

```text
"case-family testing" means reasoning-shape testing
```

The goal is not to cover topical domains. The goal is to cover abstract
reasoning conditions:

- new evidence changes a prior rule;
- a boundary must survive despite attractive upside;
- two artifacts conflict;
- many artifacts duplicate each other;
- one artifact is correct but low marginal value;
- an artifact tempts overclaim or invented precision;

Update on worker context:

```text
narrow workers still need a shared situation brief
```

Decision:

```text
keep shared big-picture context small but mandatory
do not broadcast all lane artifacts to every worker
do not let workers become miniature Step 6 agents
```

Reason:

- if workers only receive tiny local excerpts, they may provide technically
  correct but globally irrelevant advice;
- if workers receive the full conversation and all lanes, they recreate Step 6
  and add bloat;
- the stable compromise is a shared situation brief plus a narrow local slice;
- final arbitration still belongs to Step 6.

Required future workpack shape:

```text
shared_situation_brief:
  user question
  decision situation
  live constraints
  what the conversation is trying to resolve
  lane artifacts that exist
  why this worker was launched
local_slice:
  few artifacts needed for the worker question
  small source excerpts
  explicit forbidden moves
output:
  compact relevance claim
  boundary / relaxation / discard condition
  risk if ignored
  risk if forced
```
- the final reasoner must use noisy private context without exposing it.

The factual case is just the vessel. The system is being judged on whether it
improves reasoning about reasoning.
