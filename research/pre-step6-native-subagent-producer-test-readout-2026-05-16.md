# Pre-Step-6 Native Subagent Producer Test Readout

Date: 2026-05-16

Status: research-only readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
research/pre-step6-raw-vs-control-rubric-comparison-readout-2026-05-16.md
research/subagent-cognitive-worker-architecture-vision-2026-05-15.md
```

## Question

Can native job-specific subagents produce useful `reasoning_artifact.v1`
pressure from existing case fixtures, without seeing the authored raw artifacts
or indexed bundle specimens?

This tests producer quality, not final runtime behavior.

## Setup

Four native subagent workers were launched with `fork_context=false`, one per
fixture:

```text
third-year-phd-student
founder-grant-marcus-equity
mid-level-consultant-report-2
mother-deciding-address-year
```

Each worker received:

```text
case brief
reasoning shape
compact source excerpts
current-control strengths
known weaknesses
one boundary/evidence-gate job
reasoning_artifact.v1 output contract
```

Each worker did not receive:

```text
authored raw artifacts
reasoning_bundle.v1 specimens
raw-vs-control comparison scores
full transcript
all lane outputs
all V60 chunks
product docs
```

The worker prompt used Bevelin only as interpretation discipline:

```text
real issue
missing denominator or yardstick
displaced alternative
falsifier
boundary
relaxation condition
discard condition
risk if forced
risk if ignored
```

Workers were forbidden from writing final answer prose, adding public theory
labels, making legal/clinical claims, inventing probabilities, or producing long
reports.

## Important Method Flaw

The worker prompt asked each subagent to "act as a native job-specific
boundary/evidence-gate worker." That means the admission result is not a clean
independent admission test.

This matters because the mother case was selected as a no-worker sentinel. The
worker still returned `admit_worker`.

Therefore this slice should be read as:

```text
producer-quality probe: meaningful
admission-gate probe: failed / biased by setup
runtime evidence: none
```

## Results

| Case | Admission | Useful Production | Main Lift Recovered | Main Miss / Risk | Verdict |
| --- | --- | --- | --- | --- | --- |
| Third-year PhD student | `admit_worker` | Partial | Fallback viability boundary; advisor-incentive gate | Missed Silva/data constraint, which was an authored primary pressure | Promising but incomplete |
| Founder grant Marcus equity | `admit_worker` | Strong | Dependency-system map; measurable leverage / sprint gates | Worker type formatting drifted to `boundary_evidence_gate`; duplicate demotion not tested | Pass for producer |
| Mid-level consultant report | `admit_worker` | Strong | Counsel/channel incentive gate; Wednesday protocol / ordinary-conduct boundary | Career tripwires and leverage-discard pressure only partly covered | Pass for producer |
| Mother deciding address year | `admit_worker` | Useful artifacts, bad admission | Surveillance instrument boundary; commitment sizing to tripwires | Should have declined or stayed explicitly sentinel-only | Admission failure |

Aggregate:

```text
workers launched: 4
workers admitted themselves: 4
cases with useful artifacts: 4
cases with strong artifact recovery: 2
cases with partial artifact recovery: 2
no-worker sentinel correctly declined: no
runtime promotion authorized: no
bundle challenger triggered: no
OpenRouter producer used: no
```

## Case Notes

### Third-Year PhD Student

The worker produced a strong fallback viability boundary:

```text
Do not present option 1 as a future fallback unless the plan preserves a
concrete path to resume tumor-modeling work.
```

It also produced a useful advisor-incentive gate: advisor-first sequencing
should not become advisor deference.

This is real Bevelin-style interpretation: it asks what incentives, fallback
reality, and falsifiers control the pressure. But it missed the other authored
primary pressure: Silva/data access as a measured constraint retest.

Assessment:

```text
artifact quality: good
coverage: incomplete
promotability: no
```

### Founder Grant Marcus Equity

The worker recovered the two most important authored pressures:

```text
dependency-system map
measurable leverage / 90-day sprint gates
```

It avoided duplicating valuation caveats, budget correction, and Marcus
psychology claims. It also kept the systems frame at the business-dependency
level rather than inventing software architecture diagnosis.

Assessment:

```text
artifact quality: strong
coverage: strong for the boundary/evidence-gate job
promotability: research-only pass
```

### Mid-Level Consultant Report

The worker stayed inside the high-stakes boundary. It did not decide the law,
did not recommend self-directed reporting, and did not turn the case into a
negotiation.

It recovered:

```text
counsel incentive gate
GC / audit committee / external channel distinction
Wednesday ordinary-conduct protocol
```

This is the cleanest safety-case result in the slice.

Assessment:

```text
artifact quality: strong
coverage: strong for immediate channel and conduct boundaries
promotability: research-only pass
```

### Mother Deciding Address Year

The worker produced two useful artifacts:

```text
surveillance is an imperfect instrument
commitments should stay provisional and tripwire-triggered
```

Those match the strongest useful authored pressures.

But this case was intentionally a no-worker sentinel. The worker should have
been harder to admit. It should either have declined or returned a sentinel
artifact saying the current control already carries the useful pressure and no
new worker is needed.

Assessment:

```text
artifact quality: useful
admission quality: failed
promotability: no
```

## What This Means

The strongest conclusion is not "build subagents now."

The strongest conclusion is:

```text
native subagents can produce useful Bevelin-shaped reasoning_artifact.v1
pressure when given a small, well-scoped case slice
```

But:

```text
the admission gate is not solved
coverage is not reliable enough
the no-worker sentinel failed
runtime promotion is not justified
```

This result supports one more producer research slice. It does not support live
worker orchestration.

## What It Says About Bevelin

The useful worker outputs did not add Bevelin labels. They used Bevelin-like
discipline to sharpen selected pressure:

```text
What incentive is active?
What fallback is fake comfort?
What dependency is being bought down?
What evidence gate controls commitment?
What channel distinction matters?
What instrument cannot be trusted too much?
What would relax or discard the pressure?
```

That is the right placement.

Do not build:

```text
Bevelin lane
Bevelin public labels
Bevelin tendency taxonomy
Bevelin canonical KB mutation
```

Keep:

```text
Bevelin as interpretation grammar over selected Lane 1 / V60 pressure
```

## Decision

```text
continue_native_subagent_producer_research
do_not_build_bundle
do_not_promote_runtime
do_not_use_openrouter_as_broad_producer
fix_admission_gate_before_more_worker_types
```

## Next Slice

Run a two-stage admission-first test:

```text
stage 1: admission-only decision
stage 2: worker production only if admitted
```

Stage 1 input:

```text
case brief
current-control strengths
known weaknesses
candidate worker type
exact worker question
expected value hypothesis
what would make worker unnecessary
```

Stage 1 output:

```text
admit_worker or decline_worker
admission reason
unnecessary_if
kill_condition
expected artifact contribution
```

Stage 2 runs only after admission passes.

Pass standard for the next slice:

```text
mother no-worker sentinel declines
PhD admits only if Silva/data or fallback boundary is explicitly targeted
founder admits for dependency/measurement boundary
consultant admits for channel/conduct boundary
produced artifacts recover most authored-artifact lift
no final-answer prose
no unsupported precision
no legal/clinical certainty
no public machinery terms
```

If admission still admits every case, pause the worker path. The system needs a
better "do nothing" muscle before it earns live pre-Step-6 cognition.
