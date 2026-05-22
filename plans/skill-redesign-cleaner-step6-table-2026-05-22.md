# Lolla Skill Redesign: Cleaner Step 6 Table

Date: 2026-05-22

Branch: `feature/skill-redesign-cleaner-step6-table`

Status: Stage 1/2 mapping. No `SKILL.md` behavior change in this slice.

## Why This Exists

The dormant pre-Step-6 foundation is now in `main`, and the substrate fixture
cleanup has landed. The next question is not whether the research was
interesting. The next question is whether the operational `/lolla` skill should
change.

The hypothesis to test is narrow:

```text
A cleaner pre-Step-6 thinking table may reduce the useful residual work that
Step 7 pressure-check agents find.
```

This is not the same as saying Step 7 is obsolete. Step 7 currently serves more
than one purpose, and only some of those purposes are expected to shrink when
Step 6 receives cleaner private context.

## Current State

Already landed:

- PR #175: dormant pre-Step-6 foundation, with runtime default unchanged.
- PR #176: substrate fixture cleanup, restoring a clean test baseline before
  skill redesign work.
- Cleaning research closeout:
  `research/pre-step6-cleaning-research-closeout-2026-05-22.md`.

Still true:

- `SKILL.md` is the executable instruction source.
- Runtime visible behavior waits.
- Step 6 remains the cognitive solver.
- Deterministic code selects, validates, records, and preserves custody. It
  does not decide wisdom.
- Evidence surfaces may nominate patterns. Humans decide curation.

## Current Skill Flow

The current flow is:

```text
Step 1   Capture conversation
Step 2   Extract decision structure
Step 2.5 Readback and audit promise
Step 3   Run Lolla pipeline
Step 4   Render counterargument lead
Step 6   Claude/Codex writes updated position
Step 6b  Persist revised answer and private ledger
Step 7   Run pressure-check sub-agents
Step 8   Compare Step 6 against pressure-check outputs
Step 8b  Persist pressure check
Step 8c  Prepare memo fields and render memo
Step 9   Observatory
Step 10  Archive
```

Step 7 launches only after Step 6b finalization and V60 ledger validation. That
ordering is deliberate: invalid private-consideration traces must not flow into
pressure checks, memo rendering, Observatory, or archive.

## Step 7 Role Classification

Step 7 must be classified by role before any redesign can claim it is no longer
needed.

| Role | What Step 7 Does Today | Redesign Implication |
|---|---|---|
| Cognitive independence | Gives a clean-context read from agents that did not argue the original position. This breaks the self-audit loop. | A cleaner Step 6 table does not automatically remove this role. It may remain valuable even when Step 6 improves. |
| Correction / residual divergence | Finds shifts Step 6 dismissed, findings Step 6 treated as noise, or named mechanisms Step 6 did not connect. | This is the role most likely to shrink if Step 6 receives a cleaner table. |
| Lane coverage insurance | One pressure check per non-empty lane makes it harder for a lane to disappear silently after Step 6. | A future portfolio ledger may replace some of this accounting, but only if it preserves custody and auditability. |
| Memo dependency | Step 8c memo rendering currently waits for Step 8 because Step 8 can contain the last useful correction. | Making Step 7 optional requires memo/archive changes so an intentional skip is a valid run state, not an incomplete run. |
| Cost and latency burden | Up to four Claude sub-agents can be the largest non-OpenRouter cost line. | Cost control is a reason to test optionalization. It is not evidence by itself that optionalization is correct. |

The key distinction:

```text
Cleaner pre-Step-6 context primarily attacks the correction role.
It does not automatically eliminate the cognitive-independence role.
```

## Candidate Skill Modes To Test

### 1. Legacy Mode

The current flow. Step 7 runs for each non-empty lane after Step 6b succeeds.
This remains the baseline.

### 2. Cleaner-Table Shadow Mode

Step 6 receives a cleaner private table derived from the dormant pre-Step-6
foundation, but Step 7 still runs. This mode tests whether Step 7 finds fewer
meaningful residual divergences when Step 6 had better private context.

No user-facing behavior changes in this mode.

### 3. Cleaner-Table Optional-Pressure Mode

Future candidate only. Step 7 becomes optional or manual-triggered for normal
runs, while high-stakes or uncertain runs can still request a clean-context
pressure check.

This mode is not earned until shadow comparison shows that Step 7's useful
residual work has actually shrunk.

## What This Slice Does Not Do

This slice does not:

- edit `SKILL.md`;
- make Step 7 default-off;
- add a model selector;
- add a deterministic borderline selector;
- make recurrence automatically graduate cards upstream;
- change runtime output;
- change archive semantics;
- change memo timing.

Those are downstream choices and require evidence.

## Evidence Needed Before Any `SKILL.md` Behavior Change

Before changing the skill flow, the next research/engineering slice should
define and run a shadow comparison:

```text
legacy Step 6 + required Step 7
vs.
cleaner-table Step 6 + required Step 7
```

Minimum comparison questions:

1. Does the cleaner table reduce meaningful Step 7 divergences?
2. Are the remaining Step 7 divergences mostly cognitive independence, rather
   than correction of preventable Step 6 misses?
3. Does the cleaner table preserve broad private edge pressure and protected
   payload?
4. Does Step 6 use the private table discriminately, rather than mechanically
   parroting cards?
5. Does memo/archive persistence remain complete and product-clean?
6. Does cost/latency improve enough to justify changing the default later?

Suggested metrics:

- `step7_meaningful_divergence_rate`
- `question_1_shift_missed_rate`
- `question_2_material_noise_rate`
- `question_3_named_mechanism_missed_rate`
- `clean_table_atom_uptake_rate`
- `protected_payload_preservation`
- `memo_completeness`
- `anthropic_subagent_cost_delta`
- `operator_review_label`

## Stop Boundary

We can call the current branch complete when it has:

1. mapped the current skill flow;
2. classified Step 7 by role;
3. defined the hypothesis to test;
4. defined what evidence would justify a later `SKILL.md` behavior change;
5. kept `SKILL.md` untouched.

That makes this branch a Stage 1/2 planning PR, not the skill-change PR.

The next branch, if approved, should be a shadow-comparison contract and
harness. Only after that evidence lands should the team consider editing
`SKILL.md`.

## Principles Carried Forward

```text
1. The system learns by making the thinking table better.
2. Code may nominate; humans decide.
3. Cards are diagnostic instruments, not permanent answer engines.
4. Pressure atoms graduate upstream only through human curation.
5. Runtime waits.
6. Model choice must not silently become the cognitive answer.
7. Step 7 is a hypothesis to test against, not debt to delete by assertion.
```
