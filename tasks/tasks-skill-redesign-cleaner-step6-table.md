# Skill Redesign: Cleaner Step 6 Table

> Source: `plans/skill-redesign-cleaner-step6-table-2026-05-22.md`
> Goal: redesign the `/lolla` skill cautiously so cleaner pre-Step-6 context can
> be tested before any default Step 7 behavior changes.

## Relevant Files

- `plans/skill-redesign-cleaner-step6-table-2026-05-22.md` - Stage 1/2 mapping and hypothesis contract for the skill redesign program.
- `SKILL.md` - Executable skill instructions; should remain untouched until shadow-comparison evidence justifies a behavior change.
- `docs/how-it-works/live-flow.md` - Human-readable mirror of the current skill flow, including Step 7/8 purpose and memo dependency.
- `research/pre-step6-cleaning-research-closeout-2026-05-22.md` - Closeout from the cleaning research chapter and source of the principles carried forward.
- `research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.md` - Existing human-readable evidence surface for pressure-atom recurrence.
- `scripts/research/pre_step6_skill_shadow_comparison_contract.py` - Research-only contract builder/validator for the legacy-vs-cleaner-table comparison.
- `tests/test_pre_step6_skill_shadow_comparison_contract.py` - Tests proving the comparison contract keeps Step 7 required, stays runtime-dormant, and does not authorize `SKILL.md` edits.
- `research/pre-step6-skill-shadow-comparison-contract/skill-shadow-comparison-contract.v1.json` - Generated JSON contract for the skill shadow comparison.
- `research/pre-step6-skill-shadow-comparison-contract/skill-shadow-comparison-contract.md` - Human-readable rendering of the skill shadow comparison contract.
- `tests/test_skill_contract.py` - Existing skill contract tests that guard Step 6b/Step 7 ordering and live-output hygiene.
- `docs/cost-and-telemetry.md` - Canonical cost/telemetry reference, including Step 7 sub-agent cost accounting.

### Notes

- This program is not allowed to treat Step 7 as obsolete by assertion.
- The first branch is documentation and contract only. `SKILL.md` stays unchanged.
- If later work changes `SKILL.md`, update `tests/test_skill_contract.py` in the same PR.
- Use focused verification commands such as:

```text
git diff -- SKILL.md
PYTHONPATH=. pytest tests/test_skill_contract.py -q
git diff --check
```

## Instructions for Completing Tasks

**IMPORTANT:** As each task is completed, check it off in this file by changing
`- [ ]` to `- [x]`. Update the file after completing each sub-task, not only
after completing a whole parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout `feature/skill-redesign-cleaner-step6-table`
- [x] 1.0 Map current skill flow and Step 7 purpose
  - [x] 1.1 Read the current `SKILL.md` Step 6b, Step 7, Step 8, Step 8b, and Step 8c sections.
  - [x] 1.2 Read `docs/how-it-works/live-flow.md` for the readable Step 7/8 explanation.
  - [x] 1.3 Read the cleaning research closeout and evidence surface.
  - [x] 1.4 Classify Step 7 by role: cognitive independence, correction, coverage insurance, memo dependency, and cost burden.
  - [x] 1.5 Write the Stage 1/2 redesign mapping in `plans/skill-redesign-cleaner-step6-table-2026-05-22.md`.
- [x] 2.0 Design the shadow-comparison contract
  - [x] 2.1 Define legacy-vs-cleaner-table comparison arms.
  - [x] 2.2 Choose a small case set that includes Consultant, PhD, Founder/V60, and at least one negative-control shape if fixtures support it.
  - [x] 2.3 Define metrics for Step 7 residual work, atom uptake, protected payload preservation, memo completeness, and cost.
  - [x] 2.4 Define pass, fail, and ambiguous outcomes before running any comparison.
  - [x] 2.5 Keep the comparison research-only and runtime-dormant.
- [ ] 3.0 Decide whether a `SKILL.md` behavior change is earned
  - [ ] 3.1 Review shadow-comparison results against the precommitted outcomes.
  - [ ] 3.2 Decide whether Step 7 correction work has shrunk enough to test optional pressure checks.
  - [ ] 3.3 Preserve the cognitive-independence role unless evidence shows it is no longer materially useful.
  - [ ] 3.4 If evidence is insufficient, stop and keep the current skill flow.
- [ ] 4.0 Prepare a gated skill-change PR only if evidence supports it
  - [ ] 4.1 Update `SKILL.md` behind an explicit mode or manual trigger; preserve legacy mode.
  - [ ] 4.2 Update memo/archive semantics so intentional pressure-check skips are valid, observable run states.
  - [ ] 4.3 Update `docs/how-it-works/live-flow.md` to mirror the new skill behavior.
  - [ ] 4.4 Update `tests/test_skill_contract.py` to cover the new mode and preserve Step 6b/ledger ordering.
  - [ ] 4.5 Verify that default runtime behavior stays unchanged unless the PR explicitly proposes otherwise.
- [ ] 5.0 Close the skill redesign program
  - [ ] 5.1 Document what changed, what stayed legacy, what remains optional, and what evidence justified the choice.
  - [ ] 5.2 Decide whether to merge, park, or continue in a separate activation program.
