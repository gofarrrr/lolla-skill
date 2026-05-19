# Pre-Step-6 Raw Artifact Consumption Discipline

Date: 2026-05-16

Status: research contract only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
research/pre-step6-comparison-subagent-readout-2026-05-16.md
research/pre-step6-comparison-aggregate-readout-2026-05-16.md
research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md
```

## Verdict

Before building `reasoning_bundle.v1` machinery or worker orchestration, test
whether Step 6 can consume a small set of raw `reasoning_artifact.v1` specimens
directly.

The discipline is:

```text
small raw artifact slice
  -> source and boundary check
  -> duplicate/conflict/discard handling
  -> Step 6 writes normal public prose
```

The goal is to preserve useful pressure without adding another architecture
layer. The artifact is not a mini-answer. It is private pressure for Step 6.

## Why This Comes Next

The manual bundle comparison made `reasoning_bundle.v1` look useful. The
less-author-biased subagent comparison found the bundle only tied careful raw
artifact consumption in all three fixtures. Under the standing rule, ties go to
the simpler path.

Therefore the next research question is:

```text
What is the smallest raw artifact contract that lets Step 6 preserve hard
boundaries, demote duplicates, avoid overclaim, and keep conflict visible
without an index?
```

## Input Caps

Use hard caps before doing any cognition:

```text
max artifacts: 5
default artifacts: 0-3
max source excerpts: 4
max raw handoff render: about 3,000-4,000 chars
max artifact text visible to Step 6: concise fields only, no essays
```

If the case needs more than this, do not enlarge the handoff by default. First
ask whether Step 6 can answer from the original lane/V60 material, whether a
worker is actually admitted, or whether the fixture is too broad.

## Required Artifact Fields

For raw Step-6 consumption, each `reasoning_artifact.v1` should carry:

```text
artifact_id
why_provided
source_grounding
contribution
hard_boundary
relaxation_condition
discard_condition
priority_hint
risk_if_forced
risk_if_ignored
```

Optional but useful:

```text
worker_type
relation_to_answer
source_excerpt_ids
duplicate_of
conflicts_with
public_render_hint
```

Do not require a bundle-level role. If a raw artifact needs its role explained,
the role should be inferable from `contribution`, `hard_boundary`,
`discard_condition`, and `priority_hint`.

## Step 6 Reading Order

Step 6 should read raw artifacts in this order:

```text
1. source_grounding
2. hard_boundary
3. relaxation_condition
4. discard_condition
5. contribution
6. risk_if_forced / risk_if_ignored
7. priority_hint
```

Reason: grounding and boundaries decide whether the artifact is usable at all.
`priority_hint` is intentionally last. It is a hint, not authority.

## Acceptance Rules

An artifact is usable only if:

- `source_grounding` names a case-local fact, not generic theory;
- `contribution` changes or protects the final answer;
- `hard_boundary` is relevant to the user's live decision;
- `discard_condition` gives Step 6 permission to ignore it;
- `risk_if_forced` warns against over-using it;
- `risk_if_ignored` explains the loss if Step 6 omits it.

Reject or demote an artifact if:

- it is mostly a label;
- it repeats current control without adding a boundary, trigger, or discard
  discipline;
- it imports a new theory lens without case-local grounding;
- it needs a broad source packet to make sense;
- it would leak machinery language into public prose;
- its public contribution is only "be more careful."

## Consumption Rules

### Source Grounding First

Step 6 may use an artifact only as far as the source grounding supports it.

```text
If grounding is specific, the answer may use the pressure.
If grounding is generic, the answer may use only a humility note.
If grounding is absent, discard the artifact.
```

### Boundaries Beat Upside

A hard boundary should survive attractive upside unless the artifact's
relaxation condition is present in the case facts.

Example:

```text
Do not recommend an 18-month pivot unless the fallback will still be executable.
```

Step 6 should not soften this just because the ambitious option is exciting.

### Relaxation Requires Facts

Do not relax a boundary because the final answer would be smoother.

Relax only when:

```text
the artifact names a relaxation condition
and the case facts satisfy that condition
```

If the facts are unknown, render the boundary as a test or trigger.

### Duplicates Become Checks, Not Prose

If an artifact duplicates current control or another artifact, Step 6 should use
it as a private check:

```text
confirm the point is already covered
avoid repeating it
keep any unique boundary or caution
```

Duplicate artifacts should almost never create new public paragraphs.

### Quiet Artifacts Stay Quiet

If `priority_hint` is quiet or the `discard_condition` is already met, the
artifact should stay private unless omitting it would create a concrete error.

Quiet does not mean useless. It means:

```text
use as guardrail
do not foreground
do not lengthen answer
```

### Preserve Conflict

If two artifacts create unresolved tension, Step 6 should preserve the tension
instead of picking the cleaner story.

Preferred public shape:

```text
Do X only if Y becomes true; otherwise default to Z.
```

Bad public shape:

```text
X is the answer.
```

### Do Not Force A Lens

If an artifact's `risk_if_forced` says the lens may misfit the case, Step 6
should treat it as a discard candidate. This is especially important for
power-dynamics, optionality, and base-rate artifacts that can sound smart while
weakening the actual advice.

### Overclaim Guard

Never convert an artifact into:

```text
calibrated probability
legal conclusion
clinical conclusion
causal certainty
source-backed claim
```

unless the artifact's source grounding actually supports that strength.

If not, render as:

```text
possibility
test
question
trigger
humility check
```

### Public Prose Is Normal

Step 6 must not expose these terms in public prose:

```text
artifact
bundle
worker
workpack
lane
V60
chunk
ledger
schema
priority_hint
hard_boundary
discard_condition
```

The final answer needs to read like direct judgment, not like a system trace.

## Minimal Raw Handoff Render

When rendering raw artifacts for a Step-6-style consumer, use this shape:

```text
RAW REASONING PRESSURE

Use these as private pressure, not public sections.
Reject any item that is unsupported, duplicate, or misfit.
Ties go to the simpler answer.

Artifact: <artifact_id>
Grounding: <source_grounding>
Contribution: <contribution>
Boundary: <hard_boundary>
Relax if: <relaxation_condition>
Discard if: <discard_condition>
Force risk: <risk_if_forced>
Ignore risk: <risk_if_ignored>
```

Do not include full `why_provided` unless Step 6 needs admission context.
Do not include bundle roles.
Do not include long source quotes.

## Negative Admission Rule

Before adding a worker, ask:

```text
Can Step 6 use the raw artifacts directly?
Is the remaining question narrow enough for a worker?
Would a worker see facts Step 6 lacks?
Would a worker likely add answer quality, not just confidence?
What would make this worker unnecessary?
```

If the answer is "Step 6 can consume this directly," do not run the worker.

No-worker is a valid outcome, especially when:

- the control answer is already strong;
- the remaining pressure is a duplicate;
- the live issue is source discipline, not new cognition;
- the tempting lens is structurally misfit;
- the case is high-stakes and extra speculative cognition would raise risk.

## Four-Case Test Set

Use the current fixtures this way:

| Case | Role In Test | Expected Raw Discipline Move |
| --- | --- | --- |
| PhD direction choice | conflict / fallback viability | Preserve fallback and Silva gates; keep base rates qualitative; keep option expansion quiet. |
| Founder equity grant | duplicate / systems pressure | Use systems pressure; demote valuation and instrument-menu duplicates. |
| Consultant whistleblower | hard boundary / misfit discard | Preserve counsel-first and no-investigation boundaries; keep leverage framing discarded. |
| Mother address year | no-worker sentinel | Use instrument-trust and commitment-sizing pressure; decline power-dynamics worker/lens. |

## Win Standard

Raw artifact discipline wins if:

- it improves or ties the indexed bundle on final-answer quality;
- it beats current control where current control misses a real boundary or
  overclaim guard;
- it keeps answers compact;
- it preserves conflict and hard boundaries;
- it demotes duplicates without deleting the receipt;
- it prevents public machinery leakage;
- it declines at least one worker/lens that would add clutter or misfit pressure.

If raw artifacts tie the bundle, raw artifacts win.

## Current Decision

```text
test_raw_artifact_consumption_first
do_not_build_bundle_runtime
do_not_build_worker_orchestration
admit_workers_only_after_raw_artifacts_fail
```
