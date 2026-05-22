# Pre-Step-6 Option A PR Audit

Date: 2026-05-22

Purpose: make the dormant-foundation PR reviewable without confusing it with
skill activation.

## Scope

Option A merges the research evidence and dormant/shadow infrastructure needed
to preserve the pre-Step-6 portfolio learning in the repo.

It does not activate portfolio behavior.

It does not redesign the operational skill flow.

It does not remove or deprecate Step 7 pressure-check agents.

It does not change user-visible answers.

## File Buckets

Dormant runtime-adjacent infrastructure:

- `engine/system_b/pre_step6_shadow_portfolio.py`
- `scripts/run_pipeline.py`
- `scripts/archive_run.py`
- `observatory/serve_result.py`
- `engine/system_b/boundary_provider.py`

Research scripts and tests:

- `scripts/research/pre_step6_*.py`
- `tests/test_pre_step6_*.py`
- `tests/test_pr1_boundary_call_persistence.py`
- `tests/test_archive_run_v60_telemetry.py`
- `tests/test_pr3_observatory_panels.py`

Research evidence and closeout:

- `research/pre-step6-*`
- `plans/lolla-solver-control-layer-prd-2026-05-19.md`
- `tasks/tasks-step6-reasoning-portfolio.md`

Architecture documentation:

- `HOW_IT_WORKS.md`
- `docs/how-it-works/*`

Explicitly out of scope:

- `SKILL.md`
- skill-flow behavior changes
- runtime `on` activation
- automatic card graduation
- model routing
- runtime reviewer loops

## Verification Commands

Zero operational skill diff:

```bash
git diff -- SKILL.md
```

Expected: empty.

Default pipeline contract:

```bash
PYTHONPATH=. pytest tests/test_run_pipeline_contract_default.py
```

Expected: passes.

Default-off search:

```bash
rg "LOLLA_PRE_STEP6_PORTFOLIO|pre_step6_shadow_portfolio|pre-step6-portfolio" scripts/run_pipeline.py engine/system_b/pre_step6_shadow_portfolio.py
```

Expected: runtime hook is only reachable through `--pre-step6-portfolio shadow`
or `LOLLA_PRE_STEP6_PORTFOLIO=shadow`; default resolves to `off`.

Broad PR verification:

```bash
PYTHONPATH=. pytest tests/test_pre_step6_*.py tests/test_archive_run_v60_telemetry.py tests/test_pr3_observatory_panels.py
PYTHONPATH=. pytest tests/test_run_pipeline_contract_default.py tests/test_pipeline_context_runtime.py tests/test_stability_check.py
```

Expected: passes.

## Decision Boundary

This PR may be merged if the repository can honestly say:

```text
default runtime behavior unchanged
SKILL.md unchanged
shadow portfolio off by default
shadow mode records only
no visible answer decision is applied
no automatic graduation
no deterministic wisdom selector
```

The next program, if approved, is skill redesign. That program should test the
hypothesis that a cleaner pre-Step-6 table reduces Step 7's useful residual work.
It should not assume Step 7 agents are obsolete before measuring that residual
work.

