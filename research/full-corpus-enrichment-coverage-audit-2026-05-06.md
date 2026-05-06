# Full-Corpus Enrichment Coverage Audit

**Date:** 2026-05-06
**PR slice:** PR25 - enrichment placement; updated by PR26 source custody backfill
**Status:** deterministic review-only audit, source custody backfilled
**Audit module:** `engine/system_b/reasoning_substrate_coverage.py`
**Decision label:** `coverage_expansion_ready`

## Verdict

The full-corpus substrate is ready for a controlled enrichment road, but not
for broad blind extraction.

The deterministic audit confirms the PR24 substrate story:

- Runtime graph: `222` model records.
- v4 reviewed affordance records: `55` model records.
- Graph-only runtime models after v4: `167`.
- v4 IDs outside the runtime graph: `0`.
- Repo-local source custody in `data/model_sources/manifest.json`: `222`
  runtime model IDs after PR26.
- Runtime model IDs missing source custody: `0` after PR26.
- Canonical markdown availability in
  `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`: directory
  exists, `222` runtime source files available, `0` missing by runtime
  `source_file`.

That means the next expansion bottleneck is not whether the source corpus
exists or whether it is under repo-local custody. It is whether packet
fixtures, extraction, validation, absence records, and review discipline can
scale without flattening graph-only models into fake reviewed evidence.

## Inputs Compared

The audit compares:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v4.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- canonical markdown under
  `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`

No model calls, judges, extraction, prompt changes, or runtime imports are
performed.

## Runtime Graph Field Coverage

Every one of the `222` runtime models has the six runtime graph fields needed
for graph-only candidate cards.

| Field | Models with field | Total items |
| --- | ---: | ---: |
| `select_when` | 222 | 874 |
| `danger_when` | 222 | 453 |
| `failure_modes` | 222 | 678 |
| `premortem_questions` | 222 | 674 |
| `heuristics` | 222 | 680 |
| `reasoning_types` | 222 | 453 |

Implication: graph-only models are not empty. They can remain eligible as
runtime cards with honest `graph_only_runtime_card` labels while v4 grows.

## Reasoning-Type Coverage Gaps

The audit uses existing `reasoning_types` rather than inventing pressure
families. The biggest graph-only gaps are:

| Reasoning type | Runtime models | v4 reviewed | Graph-only |
| --- | ---: | ---: | ---: |
| `diagnostic` | 102 | 19 | 83 |
| `metacognitive` | 77 | 13 | 64 |
| `systems` | 87 | 25 | 62 |
| `causal` | 77 | 16 | 61 |
| `deductive` | 26 | 6 | 20 |
| `probabilistic` | 34 | 17 | 17 |
| `counterfactual` | 27 | 11 | 16 |
| `analogical` | 18 | 3 | 15 |
| `abductive` | 5 | 1 | 4 |

Interpretation:

- Diagnostic, metacognitive, systems, and causal cards are the broadest gaps.
- Probabilistic and counterfactual coverage is less wide, but still relevant
  because those models often carry operational gates and dismissal conditions.
- The audit does not conclude that any family is semantically more important.
  It only shows where v4 depth is currently thinnest relative to graph breadth.

## Lane-Signal Priority For Graph-Only Models

The audit counts static lane-route signals already present in graph and
compiled-chunk artifacts. These are not live case frequencies. They are a
deterministic proxy for "this graph-only model is already likely to be
nominated by existing lanes."

Top graph-only priorities:

| Model ID | Static lane signals | Sources |
| --- | ---: | --- |
| `step-back` | 19 | `lane1_compiled_chunk`: 16, `lane3_reframing_route`: 3 |
| `constraints` | 15 | `lane1_compiled_chunk`: 12, `lane3_reframing_route`: 2, `lane4_structural_route`: 1 |
| `delays` | 12 | `lane1_compiled_chunk`: 11, `lane4_structural_route`: 1 |
| `obligations-controls-mapping` | 12 | `lane1_compiled_chunk`: 12 |
| `peer-review-your-perspectives` | 11 | `lane1_compiled_chunk`: 7, `lane3_reframing_route`: 4 |
| `scientific-method-evidence-testing` | 11 | `lane1_compiled_chunk`: 11 |
| `formal-reasoning` | 10 | `lane1_compiled_chunk`: 10 |
| `authority-bias` | 9 | `lane1_compiled_chunk`: 5, `lane3_reframing_route`: 4 |
| `first-principles-thinking` | 8 | `lane1_compiled_chunk`: 4, `lane3_reframing_route`: 4 |
| `five-whys-method` | 8 | `lane1_compiled_chunk`: 5, `lane3_reframing_route`: 2, `lane4_structural_route`: 1 |
| `intellectual-humility` | 8 | `lane1_compiled_chunk`: 4, `lane3_reframing_route`: 4 |
| `root-cause-analysis` | 7 | `lane1_compiled_chunk`: 4, `lane3_reframing_route`: 2, `lane4_structural_route`: 1 |
| `user-centered-design` | 6 | `lane1_compiled_chunk`: 2, `lane3_reframing_route`: 4 |
| `boundaries` | 5 | `lane3_reframing_route`: 4, `lane4_structural_route`: 1 |
| `creative-destruction` | 5 | `lane3_reframing_route`: 4, `lane4_structural_route`: 1 |

The next batch recommendation also includes same-count graph-only candidates
such as `game-theory-payoffs`, `jobs-to-be-done`, `lock-in`,
`path-dependence`, `status-quo-bias`, `brainstorming`, `chain-of-thought`,
`checklists`, `confirmation-bias`, and
`cross-cultural-communication-frameworks`.

## Recommended Expansion Sequence

### Step 1 - Source-Custody Backfill Before More Extraction

Done by PR26: the remaining graph-only canonical markdown files were copied
into repo-local source custody before broad v4 extraction.

Reason:

- The external canonical directory currently has `222` available source files.
- Repo-local source custody now covers all `222` runtime models.
- v4 affordances should continue to reference source material under explicit
  custody, with manifest hashes, not external-path assumptions.

PR26 took the deterministic all-remaining-files route: it copied the `167`
missing source files and regenerated the manifest. Extraction should still
happen in batches.

### Step 2 - Extract In Batches Of 20-30

Recommended batch size: `20-30` model records.

Reason:

- v4 records need reviewed operational affordances, absence records, quote
  validation, and schema checks.
- Too-large batches encourage shallow generic extraction.
- Small batches let product review catch whether cards are becoming useful to
  the next LLM rather than merely increasing coverage count.

### Step 3 - Select Batches By Multiple Signals

Batch selection should combine:

- static lane signals from graph routing and compiled chunks;
- observed lane frequency once route-trace archives are available;
- reasoning-type gaps, especially diagnostic/metacognitive/systems/causal;
- source quality and quote density;
- graph centrality or relationship fan-out when it predicts repeated route
  nomination;
- coverage blanks discovered in packet fixture reviews.

It should not be selected by model popularity, name familiarity, or desire to
complete all 222 as fast as possible.

### Suggested First Extraction Batch

The deterministic audit recommends this first 25-model batch:

1. `step-back`
2. `constraints`
3. `delays`
4. `obligations-controls-mapping`
5. `peer-review-your-perspectives`
6. `scientific-method-evidence-testing`
7. `formal-reasoning`
8. `authority-bias`
9. `first-principles-thinking`
10. `five-whys-method`
11. `intellectual-humility`
12. `root-cause-analysis`
13. `user-centered-design`
14. `boundaries`
15. `creative-destruction`
16. `game-theory-payoffs`
17. `jobs-to-be-done`
18. `lock-in`
19. `path-dependence`
20. `status-quo-bias`
21. `brainstorming`
22. `chain-of-thought`
23. `checklists`
24. `confirmation-bias`
25. `cross-cultural-communication-frameworks`

This batch is high-priority because the existing lane substrate already points
at these graph-only shelves. It is still not a request to extract them in PR26.

## Lower-Priority Models For Now

Graph-only can be sufficient for now when:

- the model has low or no lane-route signal;
- runtime graph fields are rich enough for a compact recall card;
- the canonical source appears thin, generic, or redundant;
- the model is unlikely to affect near-term packet reviews;
- the next LLM only needs it as a lightweight neighboring shelf, not as a
  source-backed operational constraint.

Lower priority does not mean excluded. It means "eligible as graph-only until
lane evidence or packet reviews show the need for v4 depth."

## Quality Gates Before Broad Expansion

Before any broad extraction beyond a reviewed batch:

- Source files must be under repo-local custody with manifest hashes.
- Every extracted record must validate against
  `data/schemas/model_affordance.schema.json`.
- Source quotes must be exact and traceable to the copied source file.
- Absence records must be allowed and expected when source does not support a
  useful affordance.
- Generic summaries should fail review. The record should say when to use,
  when not to use, what evidence is needed, what treatment requirements apply,
  and how misuse is prevented.
- The compiled artifact should keep v4 status dormant until product review
  explicitly approves a later runtime boundary.
- Coverage reports must distinguish `v4_reviewed_affordance_available`,
  `graph_only_runtime_card`, `absence_only`, `missing_reviewed_record`,
  `source_too_thin`, and `conflicting_or_weak_support`.
- Packet producer tests must prove v4 enrichment does not swallow graph-only
  candidates.
- Drift checks must ensure no extraction batch silently becomes a Decision
  Pressure selector, case-type template, prompt change, or user-facing surface.

## Tests And Validators Needed Before Expansion

Existing checks to keep running:

- `tests/test_model_affordance_schema.py`
- affordance compiler tests, if the compiler or records are touched
- focused packet tests that prove graph-only eligibility and forbidden fields
- focused coverage tests that count runtime/v4/source-custody gaps

Suggested next checks:

- the PR26 source-custody validator for canonical markdown copy plus SHA-256
  manifest update;
- a batch-level quote validator that reports exact source path and quote
  failures before compilation;
- a packet-fixture usefulness review that inspects whether enriched cards are
  compact enough for the next LLM;
- a route-trace-to-nomination adapter test, still dormant, after the explicit
  nomination producer has one fixture review.

## Current PR25 Boundary

PR25 adds deterministic audit and dormant packet packaging only. It does not:

- extract new v4 records;
- copy the remaining 167 source files; PR26 has already done this;
- run paid model calls or judges;
- run live lanes to build packets;
- wire `/lolla`, Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- rank wisdom or choose final pressure.

The next slice should choose between packet-producer hardening or a tiny
reviewed packet fixture. It should not start broad Batch 3b or broad extraction
by momentum.
