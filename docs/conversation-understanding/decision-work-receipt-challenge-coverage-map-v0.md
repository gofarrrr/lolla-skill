# Decision Work Receipt Challenge Coverage Map v0

Status: PR108 read-only exporter slice
Date: 2026-06-30
Schema: `lolla.decision_work_receipt.v0`

## Purpose

PR108 adds deterministic challenge-surface coverage to the Decision Work
Receipt exporter.

The slice answers a narrow product question:

> Which Lolla challenge and inspection surfaces appear to exist for this
> completed run?

It does **not** answer whether those surfaces were good, whether the challenge
was enough, whether the revised answer improved, or whether the user should act.

## What It Reads

The exporter still runs in `checked_in_safe_mode`.

It may read safe structured JSON fields from completed run artifacts, especially:

- `result.json`;
- `agent_result.json`;
- `reasoning_trace.json`;
- `evaluation.json`;
- generated structured artifacts such as `gapcheck_lanes.json` and
  `graph_survival_report.json`.

It may record that private artifacts exist without reading them, such as:

- `pre_step6_private_table.json`;
- private ledgers.

It does not read raw conversation text, raw memo text, raw revised-answer text,
provider text, private tables, or private ledgers.

## Surfaces It Maps

PR108 maps these surfaces when their structured fields or artifacts are present:

- Lane 1 structural pressure: `result.json#/delta_card`;
- Lane 2 model companion: `result.json#/companion_cheat_sheet` or
  `result.json#/companion_card`;
- Lane 3 frame pressure: `result.json#/frame_pressure_card`;
- Lane 4 structural coverage: `result.json#/structural_coverage_card`;
- delivery bullshit-index check: `result.json#/bullshit_profile`;
- audit summary and boundary trace: `result.json#/audit_summary`;
- V60 private enrichment: `result.json#/v60_enrichment`;
- optional Step-7 pressure-check state: `gapcheck_lanes.json` or
  `result.json#/gap_check`;
- pre-Step-6 private table: structured presence only, content not read;
- graph survival report: `graph_survival_report.json`.

Every surface carries:

- `surface_id`;
- `surface_name`;
- `status`;
- `present`;
- `source_refs`;
- `quality_not_assessed: true`;
- notes explaining the boundary.

## Run-Health Caveats

PR108 also surfaces structured run-health caveats that can weaken the receipt:

- degraded or partial `run_health.overall`;
- capture degradation or truncation;
- empty fingerprint;
- no findings produced;
- explicit run-health issue codes;
- warning counts;
- capture-adequacy warnings, omitted-turn counts, and risk flags.

These caveats say the challenge evidence should be read carefully. They do not
score the answer or the challenge.

## Readiness Label

When core challenge surfaces exist, `process_evidence_readiness.label` may become:

```text
challenged_and_revised_process
```

This is an artifact-readiness claim only. It means the run appears to have
structured Lolla challenge artifacts. It does not mean the challenge was
correct, sufficient, or useful.

If challenge surfaces are missing but multi-turn evidence exists, the label
remains:

```text
multi_turn_unreviewed_process
```

If only thin one-shot evidence exists, the label remains:

```text
one_shot_or_thin_process
```

## Product Meaning

PR108 lets the receipt say:

- this completed run has evidence of Lolla challenge surfaces;
- this completed run appears to be missing one or more expected surfaces;
- optional deeper pressure-check state was present, absent, or rested;
- run-health caveats may weaken the process evidence;
- private challenge context may exist but is not exported in checked-in safe mode.

That is useful because it separates:

- "the final output exists";
- "the conversation was captured";
- "Lolla challenge surfaces exist";
- "run health weakens or supports inspectability";
- "humans or LLM specialists still need to judge meaning."

## Boundary

PR108 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- read raw/private content in checked-in safe mode;
- infer whether challenge was useful;
- score lanes;
- score answer quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Current Meaning

A clean PR108 receipt means:

- challenge-surface presence can be represented from existing structured
  artifacts;
- missing or private challenge surfaces are legible;
- run-health caveats are visible;
- challenge quality remains explicitly unassessed.

It does not mean:

- the final answer is good;
- Lolla improved the decision;
- all relevant challenge was applied;
- the pressure was interpreted correctly;
- an agent may act on the result.

## Next Slice

The next slice is now implemented:

```text
PR109 Decision Work Receipt Exporter v0
```

- [Decision Work Receipt Exporter v0](decision-work-receipt-exporter-v0.md)

That slice composes source inventory, process map, challenge coverage, optional
Decision Trail references, optional Product Delta references, readiness labels,
missingness, non-claims, and boundary flags into the first sparse work-trail
receipt.

The next slice is also implemented:

```text
PR110 Decision Work Receipt Fixture Review v0
```

- [Decision Work Receipt Fixture Review v0](decision-work-receipt-fixture-review-v0.md)

That review finds the PR109 receipt useful as a work-trail shell, still too
thin to explain the messy semantic story, and risky if readiness labels are
read as approval. The next planned slice is PR111 Decision Work Receipt Decision
Gate v0.
