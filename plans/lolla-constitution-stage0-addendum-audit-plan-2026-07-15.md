# Lolla Constitution Stage 0 addendum audit plan

Date: 2026-07-15

Status: active provider-free audit plan

Canonical base: `f4493e20634544addd6633d8e92a836c6488f61e`

Canonical tree: `83ba656bb41a8c3d6073d4967e8535db181ce3d5`

Provider calls authorized and made: `0`

Provider cost authorized and spent: `$0.00`

## Goal

Produce a ground-up Constitution-v5 addendum that lets a founder, new coder,
or reviewer distinguish what Lolla actually runs from what it can run only by
explicit command, what merely exchanges checked-in or archived artifacts, what
is read-only, what is research evidence, what is a prototype or proposal, and
what is stopped.

This goal documents the canonical system. It does not change product/runtime
behavior, generate a new semantic read, inspect a private run archive, restart
R4, or create Constitution v6.

## Binding inputs and authority

The incorporated Constitution v0-v5 is binding. The post-R4 closeout decision
is `stop_current_r4_reader_preserve_core_pressure_and_decision_trail`; the A2
scientific decision remains `separated_tasks_ineffective_companions_persist`.

Evidence is ordered as follows:

1. canonical runtime, CLI, import, call, or artifact-consumer path;
2. canonical checked-in artifact, manifest, receipt, or fixture;
3. canonical test exercising a real path;
4. current canonical product or architecture documentation;
5. historical result or frozen research evidence;
6. superseded proposal or PR-era design;
7. founder intent or architectural inference.

Lower levels explain intent but never override a higher-level implementation
fact.

Two noncanonical founder-intent inputs are permitted read-only:

- `/Users/marcin/Desktop/lolla-skill-main/docs/conversation-understanding/lolla-founder-product-vision-2026-07-14.md` — initial SHA-256 `dfd53588912165768837770e225352b3c556f91d1bdbfc99dc8222331905c984`;
- `/Users/marcin/Desktop/lolla-skill-main/docs/conversation-understanding/lolla-strategic-presentation-proposition-2026-07-14.md` — initial SHA-256 `0789d85a544635e6efc6c56cc0030c0c6c9f510ce7349918005cb9120f7e73ab`.

Their hashes will be rechecked at closeout. They are product-intent evidence,
not implementation proof, and Constitution v5 wins on conflict.

## Scope

The audit traces:

- the ordinary skill path from prose capture through archive, receipt, and
  read-only inspection;
- optional/default-off hooks and explicit operator commands;
- offline Decision Trail, Product Delta, Decision Work, and export paths;
- Observatory projections and server mutation boundaries;
- Mental Model Teacher prototypes;
- R3/R4 and earlier reasoning-process research runners and frozen evidence;
- all canonical Python implementation files under `engine/system_b/`,
  `scripts/`, `scripts/evals/`, and `observatory/`;
- the required documentation families, checked-in-safe artifacts, fixtures,
  tests, data, and reviews at family level;
- all 17 Constitution house rules;
- all required Decision Trail field groups;
- the three product values: pressure now, understand later, and inspect the
  process.

The canonical inventory at plan time contains 250 Python files under
`engine/system_b/`, 381 under `scripts/` including 255 under `scripts/evals/`,
and three under `observatory/`. Deduplicated audited Python scope: 634 files.
`config/` is absent. The register must assign all 634 files to an audited
subsystem or an explicit exclusion class.

## Exclusions

- `.env` files, credentials, keys, and secret stores;
- `~/.lolla/runs`, `~/.local/share/lolla/runs`, and all other noncanonical
  private archives;
- real conversation execution or source inspection;
- provider transport or semantic generation;
- runtime, graph, relationship, sidecar, Observatory, prompt, schema, model,
  route, or frozen-evidence changes;
- deletion or historical gardening;
- publication;
- broad presentation rewrite;
- implementation of the post-audit architecture.

When representative checked-in-safe evidence is unavailable, the finding is
`unknown` or `unavailable`; no replacement fixture will be synthesized.

## Classification taxonomies

Connection types:

- `direct_runtime_call`
- `dynamic_or_indirect_runtime_call`
- `artifact_handoff`
- `optional_flagged_hook`
- `explicit_operator_command`
- `offline_builder_or_cli`
- `read_only_projection`
- `test_or_fixture_only`
- `research_runner_only`
- `documentation_only`
- `no_connection`
- `unknown`

Primary component dispositions:

- `keep_active`
- `keep_bounded`
- `preserve_research_only`
- `park`
- `retire`
- `abandon`
- `unknown`

Constitution findings:

- `conforms`
- `partially_conforms`
- `current_violation`
- `not_evaluable`
- `not_applicable`

Decision Trail coverage:

- `deterministic_available`
- `provisional_semantic_available`
- `human_review_required`
- `unavailable`
- `private_or_locator_only`
- `unsafe_for_action`
- `unknown`

Product values:

- `pressure_now`
- `understand_later`
- `inspect_the_process`
- `enabling_infrastructure`
- `no_current_product_value`

Evidence maturity remains a separate vector: implemented capability,
mechanical evidence, semantic-reliability evidence, human-usefulness evidence,
and market/adoption evidence are never collapsed into one score.

## Trace method

1. Read binding sources and founder-intent inputs under the declared authority.
2. Inventory canonical files, entrypoints, imports, flags, commands, artifact
   contracts, schemas, and tests.
3. Trace ordinary live calls from `SKILL.md` helpers into extraction, pipeline,
   reconsideration persistence, ledgers, memo, archive, agent result,
   evaluation, reasoning trace, and Observatory.
4. Trace optional and offline systems independently. An import, schema field,
   fixture, or default-off hook is not treated as ordinary runtime activation.
5. Record every material edge with trigger, contract, activation class,
   authority carried, missingness/failure behavior, implementation status, and
   exact evidence references.
6. Assign each subsystem one disposition and every audited Python file one
   subsystem or exclusion class.
7. Evaluate Constitution rules 1-17 and all required Decision Trail groups.
8. Reconcile the actual system against `preserve -> pressure -> reconsider ->
   record`, preserving disagreements between code, docs, and founder intent.
9. Freeze one machine register, one founder-readable addendum, and a roadmap of
   no more than four stages with exactly one immediate founder decision.

## Test-driven validator plan

The register validator will be added through vertical red/green slices:

1. RED/GREEN: public CLI rejects a missing or invalid register and accepts the
   canonical register shape.
2. RED/GREEN: enum, unique-ID, connection-endpoint, path, and subsystem
   disposition integrity.
3. RED/GREEN: all 17 Constitution rules and required Decision Trail groups.
4. RED/GREEN: every canonical Python file in the four audited scopes is
   accounted for exactly once.
5. RED/GREEN: R4 cannot be declared active/integrated, provider calls/cost must
   be zero, and required nonclaims must be present.

Deterministic validation checks completeness and consistency only. It does not
infer dispositions, semantic coverage, or connection meaning from filenames,
imports, keywords, or chronology.

## Deliverables

- this plan;
- `docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md`;
- `docs/evals/lolla-constitution-stage0-addendum-register-v1.json`;
- `plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md`;
- one minimal audit-register validator and focused test;
- minimal cold-start/index updates only after findings stabilize.

## Verification

- focused validator tests during implementation;
- register JSON parse and public validator;
- exact implementation-file coverage;
- Constitution and Decision Trail coverage;
- A2 raw seal and final closeout validators;
- changed Python compilation;
- changed Markdown local links;
- `git diff --check`;
- added-material secret-pattern scan;
- Git object integrity;
- complete repository suite once at final handoff;
- founder-intent hash recheck;
- clean isolated worktree and no publication.

## Stop rules

Stop before semantic or product invention if canonical custody drifts, a
founder-intent hash changes ambiguously, a necessary claim requires a private
archive or provider call, frozen evidence drifts, runtime implementation is
required to answer the question, or final tests fail without an evidence-based
explanation. Otherwise record unknowns with their exact missing evidence and a
bounded future resolution gate.

## Completion boundary

The audit ends with exactly one immediate founder decision: whether to publish
the Stage 0 addendum and adopt its provider-free first restart gate. It does
not automatically begin that gate.
