# Pre-Step-6 Subagent Comparison Readout

Date: 2026-05-16

Status: research comparison readout only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-comparison-aggregate-readout-2026-05-16.md
research/pre-step6-handoff-best-practices-as-of-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
```

## Setup

The previous manual comparison said:

```text
manual comparison: bundle wins all three fixtures
promotion decision: no promotion
next decision: run a less-author-biased answer-variant comparison
```

This readout records that less-author-biased comparison.

Three subagents were launched with `fork_context=false`. Each received only:

```text
1. the comparison readout template;
2. one fixture;
3. instructions to compare Arm A / Arm B / Arm C;
4. the rule that ties go to the simpler path.
```

They were not asked to edit files. They were not given the manual readout
verdict that Arm C had won all three cases.

## Arms Compared

```text
Arm A: current control summary only
Arm B: raw reasoning_artifact.v1 specimens without bundle index
Arm C: indexed reasoning_bundle.v1, with artifact details available if needed
```

The question was not whether Arm C was easier to audit privately. The question
was whether Arm C improved the final public answer enough to beat careful raw
artifact use.

## Results

| Case | Primary Shape | Subagent Verdict | Decision |
| --- | --- | --- | --- |
| `third-year-phd-student` | conflict / fallback viability | tie, simpler path wins | prefer raw artifacts |
| `founder-grant-marcus-equity` | duplicate / systems pressure | tie, simpler path wins | prefer raw artifacts |
| `mid-level-consultant-report-2` | hard boundary / option expansion | tie, simpler path wins | prefer raw artifacts |

Aggregate:

```text
raw artifacts tied indexed bundle: 3/3
indexed bundle won final-answer quality: 0/3
indexed bundle improved private auditability: 3/3
decision under tie rule: prefer raw artifacts
```

## What The Subagents Found

Across all three cases, the subagents gave the bundle credit for:

- making primary/supporting/quiet material easier to inspect;
- preserving traceable artifact roles;
- demoting duplicates or quiet material more cleanly;
- making overclaim risks more visible before writing.

But they did not find enough final-answer lift over Arm B.

Repeated pattern:

```text
Arm C is cleaner to audit.
Arm B can produce the same public answer if the final reasoner is careful.
Therefore Arm C does not beat the simpler path.
```

## Per-Case Notes

### Third-Year PhD Student

The subagent found the best answer came from two substantive moves that were
available to both raw artifacts and the bundle:

```text
make the 18-month pivot conditional on an executable fallback
make Silva/data access a measured constraint test rather than a hopeful dependency
```

Arm C was cleaner, but not meaningfully better than Arm B. Arm B was slightly
more forceful on hard boundaries.

Decision:

```text
prefer_raw_artifacts
```

### Founder Grant Marcus Equity

The subagent found Arm A too weak on the net-new gap: it did not convert Marcus's
request into a dependency map plus measurement plan. Arms B and C both produced
the important improvements:

```text
dependency-system framing
measurable staged commitment
valuation caveat as boundary, not center
no unsupported software architecture diagnosis
```

Arm C was the cleanest operator handoff, but the public answer did not improve
enough over careful raw artifacts.

Decision:

```text
prefer_raw_artifacts
```

### Mid-Level Consultant Report

The subagent found Arm A preserved the core safety sequence but left gains on
the table. Arms B and C both improved the answer by adding:

```text
counsel-incentive testing
Wednesday interaction protocol
GC / audit committee / regulator channel distinction
compact tripwires
continued rejection of leverage framing
```

Arm C was slightly more ordered, but not materially better than Arm B.

Decision:

```text
prefer_raw_artifacts
```

## Interpretation

This is a corrective result.

The manual comparison was useful because it showed what the bundle was trying
to do. The subagent comparison is more decision-relevant because it tested the
standing kill condition:

```text
If raw artifacts tie the indexed bundle, raw artifacts win.
```

The result does not prove that bundles are useless. It proves that this bundle
shape has not yet earned default or implementation status.

## Updated Decision

```text
do_not_build_bundle_runtime
do_not_build_worker_orchestration
research_handoff_best_practices
prefer_raw_artifact_consumption_discipline_first
keep_reasoning_bundle_optional_until_it_beats_raw_artifacts
```

## Follow-Up

The next research slice should not ask "can we make a nicer bundle?"

It should ask:

```text
What is the smallest raw reasoning_artifact.v1 contract that lets Step 6
preserve hard boundaries, demote duplicates, avoid overclaim, and keep conflict
visible without an index?
```
