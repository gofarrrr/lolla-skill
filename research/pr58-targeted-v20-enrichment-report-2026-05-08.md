# PR58 Targeted v20 Enrichment Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr58-targeted-v20-enrichment`

Status: targeted knowledge-substrate enrichment; dormant compiled artifact; no runtime pickup

## Purpose

PR57 proved that v18 could be enriched without turning the affordance substrate into a dump. PR58 applies the same method to the next small ring of PR56 split candidates.

The rule stayed unchanged:

> Add a new affordance only when the receiver would need a separate transaction identity to use, reject, defer, merge, or block the material.

This PR is still not a runtime PR. It does not change `/lolla`, packet pickup, prompts, renderer behavior, lane outputs, or product surfaces.

## Scope

Edited four existing records:

- `data/model_affordances/batch_5/lock-in.json`
- `data/model_affordances/batch_11/mental-simulation.json`
- `data/model_affordances/pilot/power-dynamics.json`
- `data/model_affordances/batch_5/path-dependence.json`

Generated dormant compiled outputs:

- `data/compiled/model_affordances/affordances_v20.json`
- `data/compiled/model_affordances/quality_report_v20.md`

## Artifact Delta

Compared to v19:

| Metric | v19 | v20 | Delta |
| --- | ---: | ---: | ---: |
| Model records | 222 | 222 | 0 |
| Affordances | 262 | 266 | +4 |
| Absence records | 429 | 429 | 0 |
| Schema failures | 0 | 0 | 0 |
| Source quote rejections | 0 | 0 | 0 |

The intended shape is v20 equals v19 plus four targeted affordance identities, with no model churn, no absence churn, and no runtime pickup.

## Changes By Record

### `lock-in`

Added:

- `lock-in.productive-standardization-commitment`

Why split:

- Existing `lock-in.reversal-cost-dependency-audit` is a defensive audit for accidental lock-in, dual-run traps, and reversal-cost compounding.
- The new card is a positive but bounded transaction: deliberately choose what should stay sticky when standardization, trust, coordination, or execution quality compounds.

Source support:

- `Lock_In_rag.md:61`: stability can create compounding advantage.
- `Lock_In_rag.md:61`: consistency, standardization, or deep commitment can lower coordination cost and improve execution quality.
- `Lock_In_rag.md:63`: frequent reframing can destroy trust, focus, or efficiency.
- `Lock_In_rag.md:65`: productive lock-in is deliberate when leaders choose what stays sticky and what remains revisable.

Risk controls:

- Requires novelty to be low enough and switching/stability evidence to be present.
- Requires explicit revisability boundaries.
- Routes reversal-cost and dependency-hardening cases back to the existing audit card.

### `mental-simulation`

Added:

- `mental-simulation.skill-rehearsal-response-prep`

Why split:

- Existing `mental-simulation.assumption-bound-scenario-rehearsal` evaluates costly or risky decisions across possible futures.
- The new card rehearses future performance: conversations, interventions, component moves, and response availability under pressure.

Source support:

- `Mental_Simulation_rag.md:15`: mental simulation can be mental practice or rehearsal that builds skills.
- `Mental_Simulation_rag.md:15`: it requires breaking a competency into parts.
- `Mental_Simulation_rag.md:73`: rehearsing an argument or intervention can make the right words available.
- `Mental_Simulation_rag.md:79`: mental simulation is not as good as doing and needs direct engagement for mastery.

Risk controls:

- Blocks rehearsal-as-proof.
- Requires direct engagement, feedback, or validation after rehearsal.
- Routes strategic scenario comparison back to the existing scenario-rehearsal card.

### `power-dynamics`

Added:

- `power-dynamics.weakest-link-constraint-map`

Why split:

- Existing cards cover bilateral outside-option credibility and leverage inversion after commitment.
- The new card handles multi-party cases where the constrained actor with the least slack sets the effective floor for everyone else.

Source support:

- `Power_Dynamics_rag.md:31`: name the weakest-link dependency.
- `Power_Dynamics_rag.md:31`: the actor with least slack or narrowest fallback can set the constraint.
- `Power_Dynamics_rag.md:53`: several parties can depend on one constrained actor.
- `Power_Dynamics_rag.md:119`: teams can focus on the loudest negotiator instead of the constrained actor setting the true floor.

Risk controls:

- Does not generalize into stakeholder mapping.
- Does not blame the constrained actor.
- Does not apply when bilateral outside-option mapping is sufficient or when the constraint is exogenous regulation/physics.

### `path-dependence`

Added:

- `path-dependence.old-behavior-reproduction-map`

Why split:

- Existing `path-dependence.installed-dependency-unwind-map` prices inherited operational dependencies in redesign, migration, or exit cases.
- The new card handles cases where new intent fails because old habits, schemas, standards, handoffs, tooling, or approvals keep reproducing the old route.

Source support:

- `Path_Dependence_rag.md:1`: established habits and foundational structures can constrain later choices.
- `Path_Dependence_rag.md:55`: systems can reproduce old behavior despite new intent.
- `Path_Dependence_rag.md:57`: changing course can require more than a better argument.
- `Path_Dependence_rag.md:57`: habits, standards, interfaces, or prior investments can lock the system into the current route.

Risk controls:

- Routes platform/migration dependency pricing back to the existing unwind card.
- Blocks history-as-excuse.
- Requires a reproduced behavior plus path mechanism, not just preference for the status quo.

## Non-Goals

This PR does not:

- make v20 live;
- change `/lolla` pickup;
- change prompts or receiver instructions;
- change packet shape;
- auto-select latest affordance files;
- broaden weak or source-thin records;
- split broad/meta cards;
- add positive affordances for symmetry.

## Rejected Candidate

`category-decisions.grouping-to-synthesis-insight` was audited and rejected as a positive split for PR58.

The Category Decisions source does support grouping-to-synthesis language, but the sidecar review found the transaction is already owned by `synthesis-and-integration.governing-thought-integration-check`. The correct behavior is to keep `category-decisions` focused on precommitment and taxonomy validation, and route grouped-findings-to-governing-insight cases to synthesis instead of duplicating the same transaction under a category card.

## Validation

Edited records validated against schema and source custody:

```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('engine').resolve())); from system_b.model_affordance_validation import validate_model_affordance_file; files=['data/model_affordances/batch_5/lock-in.json','data/model_affordances/batch_11/mental-simulation.json','data/model_affordances/pilot/power-dynamics.json','data/model_affordances/batch_5/path-dependence.json']; [validate_model_affordance_file(Path(f), source_roots=(Path('data/model_sources'),)) for f in files]; print('validation_ok', len(files))"
```

Compiled v20 with all record directories:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v20.json --quality-report-filename quality_report_v20.md --artifact-id model_affordances_v20 --report-title "Model Affordance Quality Report v20"
```

## Bottom Line

PR58 adds four small, source-custodied transaction identities:

- productive lock-in;
- skill rehearsal;
- weakest-link power constraint;
- old-behavior path reproduction.

The corpus becomes sharper, not louder. The runtime story remains unchanged: v20 is reviewed substrate only.
