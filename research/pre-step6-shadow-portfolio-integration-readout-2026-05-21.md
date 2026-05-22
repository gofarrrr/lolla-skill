# Pre-Step-6 Shadow Portfolio Integration Readout

Date: 2026-05-21

Slice:

```text
ultra_dormant_shadow_portfolio_integration_v0
```

## What Changed

This slice moved the ledger-mediated portfolio design from paper-only research
into an ultra-dormant runtime artifact.

New runtime module:

```text
engine/system_b/pre_step6_shadow_portfolio.py
```

New behavior:

- computes a stable compiled card-deck cache key from problem state, prompt
  versions, and selected V60 chunk ids;
- checks only for an already cached card deck;
- records cache miss as stand-down to current Step 6;
- derives a visibility-policy signal from Step 6's private ledger when supplied;
- blocks deck visibility in shadow when payload/custody guardrails fail;
- writes `/tmp/lolla_{run_id}_pre_step6_shadow_portfolio.json` sidecars;
- archives the sidecar;
- exposes the artifact in Observatory and the case API.

Default behavior is unchanged:

```text
LOLLA_PRE_STEP6_PORTFOLIO=off
```

Opt-in shadow mode:

```text
--pre-step6-portfolio shadow
--pre-step6-portfolio-cache-dir /path/to/precomputed/decks
```

or:

```text
LOLLA_PRE_STEP6_PORTFOLIO=shadow
LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR=/path/to/precomputed/decks
```

## Contract

The shadow artifact uses:

```text
pre_step6_shadow_portfolio.v1
```

The runtime gates remain closed:

```json
{
  "runtime_wiring_allowed": false,
  "skill_update_allowed": false,
  "visible_behavior_change_allowed": false
}
```

The shadow decision always carries:

```json
{
  "normal_runtime_reviewer_calls": 0,
  "applied_to_user_visible_output": false
}
```

Live card generation is never allowed in this path:

```json
{
  "live_card_generation_allowed": false
}
```

## Why This Matters

The system can now learn from the proposed portfolio policy without giving that
policy control of the answer.

That preserves the central philosophy:

- Step 6 is still the cognitive layer.
- deterministic code is cache lookup, validation, custody, and audit;
- broad private context remains the preferred shape;
- public visibility remains blocked until evidence earns it;
- `SKILL.md` behavior is unchanged.

This is the difference between "we are integrating the portfolio" and "we are
instrumenting the portfolio hypothesis." The first would be too early. The
second is useful now.

## Key Observation

The strongest design lesson from this slice is that dormant integration should
not try to simulate cognition.

The deterministic layer can safely answer:

```text
Was a cached deck available?
Did Step 6's own ledger say additive pressure was present?
Did the protected payload gate report an omission?
Did custody validate?
Was anything applied to visible output?
```

It cannot safely answer:

```text
Was the portfolio wise?
Should this reasoning be public?
Is the deck better than the anchor?
```

Those remain Step 6 and calibration questions.

## Result

Implemented files:

- `engine/system_b/pre_step6_shadow_portfolio.py`
- `tests/test_pre_step6_shadow_portfolio_runtime.py`
- `scripts/run_pipeline.py`
- `scripts/archive_run.py`
- `observatory/serve_result.py`
- `tests/test_archive_run_v60_telemetry.py`
- `tests/test_pr3_observatory_panels.py`

Behavior proven:

- cache misses stand down without live generation;
- cache hits plus Step 6 additive ledger signal produce
  `deck_visible_shadow_only`, not a real visible-answer change;
- payload omissions block deck-visible shadow decisions;
- ledger signal derivation treats Step 6's ledger as cognitive input, not
  deterministic wisdom;
- sidecars use the existing `lolla_{run_id}_...` scratch-file convention;
- archive copies the sidecar;
- Observatory renders the shadow decision;
- case API includes `pre_step6_shadow_portfolio`.

## Verification

Focused checks:

```text
PYTHONPATH=. pytest tests/test_pre_step6_shadow_portfolio_runtime.py tests/test_archive_run_v60_telemetry.py::test_archive_run_copies_pre_step6_shadow_portfolio_sidecar tests/test_pr3_observatory_panels.py::test_pre_step6_shadow_panel_renders_shadow_decision tests/test_pr3_observatory_panels.py::test_case_api_includes_pre_step6_shadow_portfolio
```

Result:

```text
8 passed
```

Broader pre-Step-6/Observatory regression:

```text
PYTHONPATH=. pytest tests/test_pre_step6_*.py tests/test_archive_run_v60_telemetry.py tests/test_pr3_observatory_panels.py
```

Result:

```text
261 passed
```

Note: the broad suite needs local socket permissions for Observatory HTTP smoke
tests. Inside the default sandbox, those two tests fail with `PermissionError`
on port binding; with local-port permission, the same suite passes.

## Recommendation

Treat this as an evidence-gathering instrument, not promotion.

Next good moves:

1. Run several real archived cases with `--pre-step6-portfolio shadow` and no
   cached deck to measure cache-miss prevalence and archive shape.
2. Add a small precomputed-deck cache for fixed-suite cases and run shadow mode
   again to inspect ledger/payload/custody records in Observatory.
3. Only after shadow archives are readable and stable, decide whether Step 6
   should receive the actual deck behind an experimental prompt flag.

Do not promote runtime visibility. Do not edit `SKILL.md` for visible behavior.
The calibration floor still owns that gate.
