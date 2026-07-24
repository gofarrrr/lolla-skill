# Bundled runtime import repair result

Date: 2026-07-24

Status: repository-published through
[PR #399](https://github.com/gofarrrr/lolla-skill/pull/399) at merge
`1ef617f1d2354752a672330bbf93378aed789e67`

Scope: the ordinary `$lolla` boundary between completed conversation
extraction and the four-lane reasoning pipeline

Graph, planner, prompts, provider route, and answer behavior changed: **no**

## Plain-language result

The reported run captured all 14 messages and completed its initial decision
read. It then stopped before producing any reasoning findings because one
bundled Python file referred to Lolla's engine by a second package name.

That second name was available when the calling session happened to start
inside the repository. It was unavailable when `$lolla` ran from another
folder. The skill therefore depended on an invisible detail of the user's
session even though it had already found its own files correctly.

The repair makes the live entry point expose its bundled skill root explicitly.
Lolla can now load both historical package names from its own installation
location regardless of the caller's current folder. The existing package names
are preserved to avoid a broader refactor of tested runtime identity.

In simpler terms: Lolla knew where its toolbox was, but one tool expected the
room itself to have a particular name. The repair gives that tool the toolbox's
full address.

## Reproduction and repair evidence

The provider-free regression starts a separate Python process:

- in an unrelated temporary directory;
- with isolated mode enabled;
- with `PYTHONPATH` removed;
- with OpenRouter and OpenAI keys blank;
- by loading the real `scripts/run_pipeline.py` entry point and then importing
  the real `SystemBPipeline`.

Before the repair, that test failed through the same module chain and ended
with:

```text
ModuleNotFoundError: No module named 'engine'
```

After the path-boundary change, the same subprocess imports
`SystemBPipeline` successfully.

The self-contained-skill validator now repeats this check on every public
handoff. This closes the reason the existing packaging checks missed the bug:
they proved that all files existed and that the graph reproduced, but they did
not import the live pipeline from outside the repository.

## Failed-run custody

The failed run `20260724T140450Z_f1af78` was inspected only through its
operator traceback. It was not retried, resumed, repaired in place, or treated
as a completed audit. Its completed extraction does not make its missing
pipeline findings valid.

A future test must begin with a new `$lolla` invocation and a new run ID.

## Verification

The exact external-working-directory regression first failed with the reported
`No module named 'engine'` traceback and then passed after the repair.

The final provider-free checkpoints are:

- 38 focused live-pipeline, skill-contract, helper, and isolated-package tests
  passed;
- 5,207 repository tests and all 93 subtests passed;
- one pre-existing `datetime.utcnow()` deprecation warning remained;
- the skill-authoring validator, self-contained-skill validator, Constitution
  Stage 0 register validator, repository-local-authority validator, public
  handoff validator, Python compilation, Bash syntax, JSON parsing, and
  `git diff --check` passed.

No provider or embedding call was made by these checks.

## Boundaries and nonclaims

- This repair does not change the 222 mental-model sources or 1,358 relations.
- It does not change one-hop graph traversal, candidate bounds, pressure lanes,
  reconsideration, or apply/reject/park custody.
- It does not change prompts, model selection, provider routing, retries, or
  cost policy.
- It does not prove that extraction meaning is correct, that graph pressure is
  useful, or that a revised answer is better.
- It does not hide operating-system temp artifacts from an operator. The prior
  capture repair separately removed the user-facing editor-diff workflow.
