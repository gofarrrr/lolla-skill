# Pre-Step-6 Native Subagent Admission Gate Readout

Date: 2026-05-16

Status: research-only readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-native-subagent-producer-test-readout-2026-05-16.md
research/pre-step6-raw-vs-control-rubric-comparison-readout-2026-05-16.md
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
research/lolla-reasoning-preservation-core-vision-2026-05-14.md
```

## Question

Can a native subagent path separate admission from production?

More specifically:

```text
stage 1: decide whether a worker should exist
stage 2: produce a compact artifact only for admitted cases
```

This tests whether the system has a real "do nothing" muscle. The prior native
producer slice created useful artifacts, but it also admitted the mother
no-worker sentinel. That meant producer quality looked promising while admission
quality failed.

This slice asks whether a separate admission gate fixes that failure.

## What Was Compared

This was not a final-answer quality comparison. It compared two worker-launch
shapes:

```text
prior slice:
  producer prompt implicitly put every case inside a worker role
  result: all four cases admitted, including the no-worker sentinel

current slice:
  admission-only prompt first, default decline
  production prompt only after admission
  result: three expected cases admitted, no-worker sentinel declined
```

The control pressure in the background is the raw-artifact path:

```text
raw reasoning_artifact.v1 answer cores already beat current-control answer cores
in the four strict local comparisons
```

Therefore the worker path is not trying to prove "more cognition is always
better." It is trying to prove a narrower claim:

```text
when a specific missing boundary/evidence gate is likely to be missed by Step 6
reading raw pressure directly, a bounded native subagent can produce a compact
artifact with enough marginal value to justify its cost and attention load
```

## How It Was Run

Stage 1 used four admission-only native subagents with `fork_context=false`:

```text
third-year-phd-student
founder-grant-marcus-equity
mid-level-consultant-report-2
mother-deciding-address-year
```

Each admission agent received:

```text
case brief
current-control strengths
known weaknesses
candidate worker type
candidate worker question
expected value hypothesis
what would make the worker unnecessary
```

Each admission agent had to return only:

```text
decision
reason
exact_worker_question
expected_artifact_contribution
unnecessary_if
kill_condition
```

The admission prompt defaulted to decline. It allowed admission only when a
narrow boundary/evidence-gate worker had clear marginal value over careful Step
6 reading of the current lane/V60 pressure.

Stage 2 ran production only for admitted cases. The mother sentinel received no
producer run.

Each producer received:

```text
shared situation brief
one worker question
2-4 relevant artifacts or source excerpts
explicit forbidden moves
reasoning_artifact.v1 output contract
```

Each producer did not receive:

```text
authored raw artifacts
reasoning_bundle.v1 specimens
full transcript
all lane outputs
all V60 chunks
product docs
```

## Criteria

Admission pass criteria:

```text
mother no-worker sentinel declines
PhD admits only for fallback viability and/or Silva/data boundary
founder admits only for dependency-system / measurable staged gates
consultant admits only for counsel/channel / Wednesday-conduct boundary
admission output names what would make the worker unnecessary
admission output names a kill condition
no artifact production during admission
no final-answer prose
no public machinery language
```

Production pass criteria:

```text
production runs only for admitted cases
artifact is compact reasoning_artifact.v1, not an essay
artifact is source grounded
artifact names contribution, hard boundary, relaxation condition, discard condition
artifact gives risk_if_forced and risk_if_ignored
artifact does not advise the final answer directly
artifact does not invent precision
artifact does not make legal or clinical certainty claims
artifact does not ask for full transcript or all lanes
```

## Admission Results

| Case | Admission Decision | Expected? | Admission Reason Quality | Verdict |
| --- | --- | --- | --- | --- |
| Third-year PhD student | `admit_worker` | Yes | Targeted fallback executability and Silva/data retesting as a hard boundary problem | Pass |
| Founder grant Marcus equity | `admit_worker` | Yes | Targeted dependency loops and measurable staged-commitment gates | Pass |
| Mid-level consultant report | `admit_worker` | Yes | Targeted counsel incentives, internal-channel distinctions, and Wednesday conduct | Pass |
| Mother deciding address year | `decline_worker` | Yes | Said Step 6 can directly add surveillance-silence and conditional-commitment pressure | Pass |

Aggregate:

```text
admission agents run: 4
admitted: 3
declined: 1
no-worker sentinel correctly declined: yes
producer agents run: 3
producer agents skipped by admission: 1
runtime promotion authorized: no
bundle challenger triggered: no
OpenRouter used: no
```

## Production Results

| Case | Production Run? | Useful Lift | Boundary Quality | Main Risk | Verdict |
| --- | --- | --- | --- | --- | --- |
| Third-year PhD student | Yes | Converts fallback and Silva/data into binding evidence gates | Strong | May overconstrain flexible exploration | Pass |
| Founder grant Marcus equity | Yes | Maps Marcus/Jake/Lina/platform/client/exit dependencies and staged metrics | Strong | Could over-focus on metrics if terms also need human handling | Pass |
| Mid-level consultant report | Yes | Separates counsel, GC/audit committee/external channels, and ordinary Wednesday conduct | Strong | Could drift into legal advice if not capped | Pass |
| Mother deciding address year | No | None needed | Correctly skipped | Step 6 must still carry surveillance/tripwire pressure directly | Pass |

## Artifact Summaries

### Third-Year PhD Student

The producer recovered the missing boundary better than the prior producer
slice. It told Step 6 not to recommend a trigger-based dissertation plan unless
the plan includes:

```text
dated fallback-executability check
separate Silva/data retest
concrete evidence for data access before treating feasibility as real
explicit conditions under which option 1 is still advisor-supported and restartable
```

The important improvement over the prior producer slice is that Silva/data
access was no longer missed. The artifact also gave a clear risk if ignored:
Step 6 may create a plan where "fallback" is fictional and missing Silva/data
evidence is laundered into feasibility.

### Founder Grant Marcus Equity

The producer turned the equity/CTO/board request into a dependency-system map:

```text
Marcus -> Jake/Lina -> delivery capacity
Marcus -> prototype -> platform option value
founder -> clients/commercial control -> agency cash engine
platform -> exit story
governance/title/equity -> irreversible leverage
```

It preserved the 90-day validation sprint as a measurement tool, not as a
delay tactic. The hard boundary is that final title/equity/board terms should
not be handled as isolated concessions before the company has evidence about
technical autonomy, team retention, platform progress, client continuity,
decision rights, and governance escalation triggers.

### Mid-Level Consultant Report

The producer stayed inside the high-stakes boundary. It did not decide the law,
did not encourage investigation, and did not collapse all internal reporting
into "tell GC."

It preserved three distinctions:

```text
counsel: independent whistleblower / regulatory-employment counsel, with conflict and incentive checks
channels: GC, audit committee / independent directors, and external routes are different paths
Wednesday: ordinary conduct only; no probing, confrontation, unusual access, downloads, photos, or asking around
```

The strongest boundary was that the final answer must not imply company GC is
the user's personal lawyer and must not pick a legally correct reporting path.

### Mother Deciding Address Year

No producer ran. That is the point.

The admission agent declined because the useful pressure is already simple
enough for Step 6 to carry directly:

```text
surveillance silence is weak evidence
durable commitments should stay sized to observed behavior, professional guidance,
legal advice, and renewed-contact tripwires
```

This is a better result than a clever artifact. The case was selected to test
whether the system can resist adding an attractive worker when the current
control already has enough structure.

## Interpretation

This slice fixes the exact failure mode from the prior native producer test:

```text
prior problem: producer role made every case feel worker-worthy
current improvement: separate admission stage declined the no-worker sentinel
```

It does not prove that pre-Step-6 workers should be live in `/lolla`. The
sample is still small, manually prompted, and judged locally. It also does not
prove that a `reasoning_bundle.v1` index is needed.

The strongest claim supported by this slice is:

```text
native subagents are promising as bounded producers after a strict admission gate
```

The stronger claim is not supported:

```text
pre-Step-6 subagents should run broadly or by default
```

## What This Means For Bevelin

The useful behavior looked like Bevelin as interpretation discipline, not
Bevelin as a lane or taxonomy.

The agents did useful work when they asked:

```text
What tendency or incentive changes the meaning of this pressure?
What fallback is fake comfort?
What evidence would relax the boundary?
What would make this artifact discardable?
What risk appears if this pressure is forced?
What risk appears if this pressure is ignored?
```

They did not need public Bevelin labels. They did not need a new Bevelin lane.
They needed a narrow question, a shared situation brief, and a compact artifact
contract.

## Decision

```text
two_stage_admission_first_shape_passes_this_research_slice
keep_raw_artifacts_as_baseline_to_beat
continue_native_subagent_worker_research
do_not_build_one_worker_per_lane
do_not_promote_runtime
do_not_build_reasoning_bundle_yet
do_not_use_openrouter_as_broad_worker_producer
```

## Next Slice

The next slice should codify this manually successful shape as research-only
machinery, still outside live `/lolla`:

```text
reasoning_workpack.v1 builder / validator
admission record schema
producer prompt renderer for boundary/evidence-gate worker only
static validation for caps, forbidden moves, required fields, and source grounding
local replay fixture that includes the mother no-worker sentinel
```

Promotion remains blocked until a harness can show durable improvement over:

```text
current control
raw reasoning_artifact.v1 consumption
admission-first native worker artifacts
```

The kill condition is also clear:

```text
if admission starts admitting obvious no-worker cases again, pause the worker path
and improve the gate before adding worker types or bundle machinery
```
