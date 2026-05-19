# Pre-Step-6 Auto-Research Operating Loop

Date: 2026-05-19

Status: research-process contract. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, public output, workers, bundles, handoff modes, or
generator implementation.

Related:

```text
research/pre-step6-replay-ledger-aggregate-readout-2026-05-18.md
research/pre-step6-selector-boundary-decision-memo-2026-05-19.md
research/pre-step6-off-default-candidate-generator-boundary-proposal-2026-05-19.md
research/pre-step6-no-rendered-handoff-v1-readout-2026-05-19.md
research/pre-step6-generated-decline-evaluation-readout-2026-05-19.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/llm-decomposition-handover.md
research/extraction-contract-roadmap.md
README.md
```

External inspiration:

```text
https://github.com/karpathy/autoresearch
```

## Purpose

The user wants the research process to stop pausing after every small result and
return to a disciplined auto-research style:

```text
read the local evidence
pick the next narrow question
build or record one research slice
validate it
commit it
derive the next question
continue until a real blocker appears
```

This document adapts that pattern to the pre-Step-6 work.

It is not an instruction to run uncontrolled experiments. It is an autonomy
contract for research-only iteration while keeping the product boundary clean.

## What Auto-Research Means Here

Karpathy's `autoresearch` loop is simple:

```text
fixed substrate
one editable experimental surface
fixed experiment budget
one comparable metric
experiment log
keep, discard, or crash
repeat without asking after setup
```

For Lolla pre-Step-6, the same spirit applies, but the shape changes.

We do not have one metric like validation bits per byte. We have a judgment
system where the important result may be:

```text
rendered wins
control wins
raw wins
tie
rendered passes audit but does_not_count
decline is healthy
path is killed
schema is not earned
```

So the Lolla version is:

```text
stable product substrate
small research-only experimental layer
predeclared question and gates
static fixtures or docs before runtime
replay/source/naturalness evidence
honest pass, tie, loss, stop, or kill record
commit every useful evidence slice
repeat until blocked by evidence or product boundary
```

## Stable Substrate

These are treated like `prepare.py` in the original auto-research pattern. They
are read for context but not edited by the loop:

```text
SKILL.md
HOW_IT_WORKS.md
default /lolla runtime
engine/system_b runtime behavior
Lane 1 / Lane 2 / Lane 3 / Lane 4 production interfaces
V60 and compiled knowledge artifacts
product docs
canonical knowledge base
public answer behavior
```

Changing these requires explicit user approval or a later promotion decision.

The loop may inspect them. It may not quietly change them.

## Experimental Layer

These are the allowed research surfaces:

```text
research/pre-step6-*.md
research/pre-step6-*/**/*.json
scripts/research/pre_step6_*.py
tests/test_pre_step6_*.py
```

Even here, the loop stays narrow. A slice should normally touch one concept:

```text
a schema proposal
a validator
a fixture
a comparison record
a source/overclaim audit
a replay ledger record
a readout
a decision memo
```

Do not use the research layer to smuggle product behavior.

## Current Research State

Current evidence state before the next loop round:

```text
replay records: 6
rendered_hybrid replay wins: 4
control/raw/tie replay stops: 2
source/overclaim audit failures: 0
naturalness debt low: 1
naturalness debt medium: 5
naturalness debt high: 0
native/semi-blind judge records: 3
local-rubric records: 3
runtime/product promotion records: 0
```

Established behaviors:

```text
card_first can preserve selected pressure
no_extra_pressure can decline extra cognition
quiet_receipts can demote clutter without deleting custody
the ledger can record rendered stops without schema bending
rendered can pass audit and still does_not_count
```

Current blocker:

```text
we know decline is sometimes correct
we do not yet know how to represent or evaluate generated decline cleanly
```

The next missing primitive is therefore:

```text
no_rendered_handoff as a first-class research output
```

## Loop Setup

Before each auto-research round:

```text
1. Confirm worktree is clean.
2. Read the latest aggregate, selector, and boundary docs.
3. Identify the current blocker in one sentence.
4. Choose exactly one narrow research question.
5. Predeclare pass, tie, stop, and kill conditions.
6. Predeclare which files are allowed to change.
7. Run the smallest implementation that can answer the question.
```

If the worktree is not clean, do not start a new round until the state is
understood.

## Round Shape

Every round should produce one of these:

```text
pass readout
tie/restraint readout
loss/stop readout
kill memo
schema proposal
fixture plus validator
replay ledger record
aggregate or boundary memo
```

A losing result can be a successful round if it improves the boundary.

Examples:

```text
rendered wins and passes audit:
  useful evidence, not promotion

control wins and rendered does_not_count:
  useful decline evidence, not failure

raw ties rendered while simpler:
  useful stop evidence

schema is too vague to validate:
  useful blocker memo
```

## Keep, Stop, Or Discard

The original auto-research loop keeps changes that improve the metric and
discards worse ones. Lolla needs a wider evidence rule:

Keep the slice when it:

```text
adds valid evidence
clarifies a boundary
records a loss/tie/stop honestly
adds custody validation without product drift
reduces future ambiguity
```

Stop or kill the path when it:

```text
requires product/runtime changes to answer a research question
turns deterministic code into judgment
adds fields because the artifact feels incomplete
creates a hidden answer plan
cannot define what would count as failure
```

Discard or revise the working diff before commit when it:

```text
touches blocked product files
adds a new mode without evidence
implements a generator before its decline primitive exists
adds workers or bundle behavior
changes public answer behavior
```

Because this repo is shared with the user, do not use destructive git resets as
normal loop mechanics. Prefer small edits, clean commits, and explicit stop
readouts.

## Autonomy Rules

Continue without asking the user when all of these are true:

```text
the next step is research-only
the worktree is clean or the dirty state is understood
the slice has one narrow question
the pass/stop/kill conditions are clear
no product/runtime files are touched
no paid or external model call is required
no destructive git operation is required
the result can be validated locally
```

Pause and ask the user when any of these are true:

```text
the next step would touch SKILL.md, HOW_IT_WORKS.md, runtime, product docs, or /lolla
the next step requires paid or external model calls not already approved
the next step requires destructive git operations
the evidence supports two materially different product directions
the research question has no falsifiable gate
the loop would only collect another easy win
the user value depends on taste rather than local evidence
```

This is the adapted version of "do not ask every loop." It means:

```text
do not stop for permission after every clean research slice
do stop when the next move changes the product boundary or lacks a real gate
```

## Deterministic System Boundary

The deterministic layer may:

```text
validate shape
check refs
enforce caps
check cross-ref custody
render private research surfaces
record comparisons
record audits
record naturalness debt
record pass, stop, retest, or kill decisions
block promotion
```

The deterministic layer may not:

```text
decide final advice
decide which pressure is true
force Step 6 to use a handoff
convert valid nuance into public obligation
turn naturalness debt into a formula
promote rendered by default
launch workers because pressure exists
create new modes to make a fixture pass
```

The doctrine remains:

```text
deterministic code keeps custody
the LLM performs judgment
valid pressure is rejectable
decline is first-class
```

## Predeclared Metrics And Gates

Each round chooses the smallest relevant subset of these gates:

```text
schema validates
fixture validates
renderer stays under cap
source refs exist
cross-ref equality holds
public machinery terms do not leak
source/overclaim audit passes or records failure
naturalness debt is low/medium/high and explained
comparison decision is recorded honestly
rendered counts or does_not_count honestly
runtime_wiring_allowed is false
product_promotion_allowed is false
```

Qualitative criteria are allowed, but they must be named before judging:

```text
decision usefulness
source grounding
overclaim risk
answer length / cognitive load
machinery hygiene
conflict preservation
duplicate demotion
unforcedness
```

Do not let expected inclusions become the whole quality standard. Inclusion
tests are regression guards, not proof of better advice.

## Standard Validation Commands

For pre-Step-6 research slices, default to:

```text
PYTHONPATH=. pytest tests/test_pre_step6_raw_artifacts.py tests/test_pre_step6_workpacks.py tests/test_pre_step6_pressure_card_consumption.py tests/test_pre_step6_hybrid_handoffs.py tests/test_pre_step6_semi_blind_comparisons.py tests/test_pre_step6_replay_ledger.py tests/test_pre_step6_no_rendered_handoffs.py tests/test_pre_step6_decline_evaluations.py
git diff --check
```

When a specific validator exists, also run the relevant CLI command. Examples:

```text
python3 scripts/research/pre_step6_semi_blind_comparisons.py <comparison.json> --repo-root .
python3 scripts/research/pre_step6_replay_ledger.py <audit.json> --repo-root . --source-overclaim-audit
python3 scripts/research/pre_step6_replay_ledger.py <replay-record.json> --repo-root . --replay-record
python3 scripts/research/pre_step6_no_rendered_handoffs.py <no-rendered-handoff.json> --repo-root .
python3 scripts/research/pre_step6_decline_evaluations.py <decline-evaluation.json> --repo-root .
```

Docs-only rounds still run the focused suite unless there is a clear reason not
to. The point is to keep the workspace boring.

## Commit Discipline

Each useful research slice should end in a clean commit.

Commit messages should describe the evidence, not hype:

```text
Record no-rendered handoff boundary proposal
Record generated decline dry run
Record rendered decline validator slice
Record negative control stop
Record source-overclaim audit failure
```

Do not leave untracked research artifacts as informal memory.

Do not mix unrelated research questions in one commit.

## Next Round Queue

The next rounds should proceed in this order unless evidence changes the queue.

Completed on 2026-05-19:

```text
1. Docs/test proposal for no_rendered_handoff.v1
   Question: can decline be represented without becoming another pressure surface?

2. One manually authored no_rendered_handoff fixture
   Question: does the receipt help evaluation without smuggling an answer plan?

3. Minimal validator for no_rendered_handoff.v1
   Question: can decline validate as first-class output while keeping runtime blocked?

4. Replay-style generated-decline evaluation record
   Question: can a declined rendered handoff count as healthy evidence?
```

Current next queue:

```text
5. Only after 1-4, revisit whether an off-default candidate generator spec is
   worth more than another static replay.
```

Still blocked:

```text
generator implementation
runtime wiring
product promotion
new handoff modes
bundle
workers
subagent orchestration
SKILL.md updates
HOW_IT_WORKS.md updates
product docs
```

## Stop Conditions For The Whole Track

Pause the whole pre-Step-6 rendered-handoff track if:

```text
decline receipts become hidden answer plans
naturalness debt remains medium without decision lift
control/raw keeps tying or beating rendered in low-pressure cases
generated candidates cannot find decline cases
source/overclaim audits begin failing after rendered wins
the only benefit is operator traceability
the system needs new modes to keep passing fixtures
```

Killing or pausing the path is a valid research success if it prevents product
complexity.

## Operator Summary

The auto-research loop for this branch is:

```text
small question
static research slice
predeclared gate
local validation
honest readout
clean commit
next question
```

The current next question is:

```text
Can no_rendered_handoff be represented as a first-class successful research
output without becoming another private pressure surface?
```

Do that next unless new evidence changes the blocker.
