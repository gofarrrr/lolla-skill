# PR 11 Coder Brief — Gate 4 Edge Probe Experiment

**Date:** 2026-05-05
**Branch:** `feature/knowledge-substrate-pr11-gate4-edge-probes` (branch from `feature/knowledge-substrate-pr10-compile-affordances-v3`)
**Target branch:** `feature/knowledge-substrate-pr10-compile-affordances-v3`
**Status:** Draft — do not merge to main

---

## What This PR Is

An offline three-arm archived-case experiment testing whether affordance-guided Lane 4 produces constructive, source-traced edge probes that neither the current Lane 4 baseline nor a strong generic edge-seeking LLM prompt reliably produces.

**This is not a "better gap questions" experiment.**
This is an Edge Probe experiment.

The whole substrate program merges only if Arm C beats Arm B on constructive edge. Arm B is the critical control: it isolates what a well-prompted LLM can already produce from model names alone. Arm C only earns its keep if the compiled affordance records add something the LLM was statistically unlikely to foreground — specifically: `do_not_use_when` conditions, `case_evidence_needed` items, `treatment_requirements`, and `misuse_guards`.

---

## The Enrichment Thesis

The affordance layer is not a knowledge base that teaches the LLM what mental models mean. Strong LLMs already know the central meaning of common mental models.

The affordance layer exists to surface **peripheral-but-load-bearing operational constraints**:

- "Do not use this if the team merely relabels views without changing the standard of evidence."
- "Require a case quote showing which failures are absent from the visible sample."
- "Ask what would make this buffer insufficient, not just whether a buffer exists."

Those are not "what the model means." Those are how the model bites. **The bite is the product.**

A good edge probe has five parts:
1. The question or pressure
2. Why this is an edge (what hidden failure/misuse/missing evidence it targets)
3. The affordance field it traces to
4. What changes if the edge is true
5. How to dismiss it if false

The dismissal condition is not optional. Without it, the system creates mud, not edge.

---

## Three Arms

| Arm | Description |
| --- | --- |
| **A** | Current Lane 4 baseline — the existing `gap_questions` in archived `result.json` |
| **B** | Generic strong edge-seeking prompt — routed model names + instruction to surface edge questions, **no affordance records** |
| **C** | Same edge-seeking prompt + retrieved affordance records from `affordances_v3.json` |

Arm A answers: does the system improve at all?
Arm B answers: is the improvement from better prompting alone?
Arm C answers: does the compiled substrate add something beyond better prompting?

**Win condition:** C beats B on constructive edge, and those wins trace to `do_not_use_when` / `case_evidence_needed` / `treatment_requirements` / `misuse_guards`.

---

## Case Selection

Use these 10 archived cases from `~/.local/share/lolla/runs/`:

| Case slug | Routes | v3-covered / candidates | Why included |
| --- | ---: | ---: | --- |
| `marcus-equity` | 5 | 23/28 (82%) | 5 familiar cases; rich routes |
| `mother-deciding-address-year` | 3 | 12/15 (80%) | 5 familiar cases; personal stakes |
| `mid-level-consultant-report` | 3 | 12/16 (75%) | 5 familiar cases; advisory domain |
| `third-year-phd-student` | 5 | 16/25 (64%) | 5 familiar cases; professional decision |
| `user-launch-independent-fintech` | 3 | 13/16 (81%) | 5 familiar cases; startup domain |
| `year-old-oncologist-accept` | 5 | 22/27 (81%) | High coverage, high routes; medical domain |
| `grant-equity-partnership-status` | 4 | 20/22 (91%) | Highest v3 coverage; equity domain variant |
| `founder-grant-marcus-equity` | 4 | 19/21 (90%) | High coverage; founder domain |
| `mid-level-consultant-decides` | 4 | 15/19 (79%) | Decision domain variant |
| `mother-deciding-protect-year` | 3 | 13/16 (81%) | Personal stakes variant |

The generated case-selection artifact is the source of truth for exact candidate-appearance coverage. The table above should match `research/pr11-gate4-case-selection-2026-05-05.md`.

Use the **latest run** for each case (sort run timestamp directories and take the last). If a case has no `result.json` or no `structural_coverage_card.gap_routes`, skip it and log the skip.

Each case produces 3–5 gap routes. Each route produces one set of Arm A questions, one Arm B edge probe call, one Arm C edge probe call. Do not aggregate routes across cases.

---

## Archive Structure

```
~/.local/share/lolla/runs/
  {case_slug}/
    .case-manifest.json
    {timestamp}/              # use latest by sort order
      result.json             # has structural_coverage_card.gap_routes, gap_questions
      gapcheck_lanes.json
      extraction.json
```

From `result.json`:
- `structural_coverage_card.gap_routes[].{dimension_id, dimension_name, candidate_model_ids}`
- `structural_coverage_card.gap_questions[].{dimension_id, questions}` — this is Arm A baseline

The archive root is `~/.local/share/lolla/runs/` by default. Support a `--archive-root` CLI flag.

---

## Affordance Records

Compiled artifact: `data/compiled/model_affordances/affordances_v3.json`

For each `candidate_model_id` in a gap route, look up its affordance record in the compiled artifact. The lookup is by `model_id`. If no record exists, log it and continue — do not infer or synthesize.

For Arm C, include all affordance records for all candidate models in the route. If total token budget would be exceeded, cap by route's `candidate_model_ids` order and log what was omitted. Do not have Python choose "best" affordances semantically.

---

## Deterministic Layer Responsibilities

Python **must do**:
- Load archived case inputs
- Look up affordance records by `model_id`
- Assemble LLM packets (case context + gap route + affordance records for Arm C)
- Enforce token budget per call; log what was included vs. omitted
- Validate returned JSON shape (required fields present, correct types)
- Validate that returned `model_id`, `affordance_id`, and `treatment_requirement_id` exist in `affordances_v3.json`
- De-duplicate identical question text mechanically (exact string match)
- Write deterministic output files per case per arm
- Count judge outcomes (win/loss/tie per arm)
- Log provider, model, tokens, and cost per call

Python **must not do**:
- Decide whether an affordance is active
- Match `use_when` or `do_not_use_when` against case text
- Rank affordances by keyword overlap or semantic similarity
- Score whether a question is "good" using regexes
- Infer missing affordances
- Rewrite records to make the experiment look better
- Route to different models to increase apparent coverage
- Add any runtime imports or change any `/lolla` behavior

---

## LLM Responsibilities

The Arm B and Arm C LLM call should instruct:

> Given this case and the candidate mental models for this gap route, generate only **edge probes** that challenge the current reasoning trajectory. An edge probe is not a restatement of what the model means — it is a bounded, source-traceable pressure that the analysis might be missing. Prefer questions that come from `do_not_use_when` conditions, `case_evidence_needed` requirements, `treatment_requirements`, and `misuse_guards`. Do not restate central model definitions. For each probe, explain why it is an edge, what changes if it is live, and how to dismiss it if it is not.

For each affordance record included, the LLM must also make an **activation call** — explicitly stating whether each affordance is activated, set aside, unclear, or duplicate. Set-asides must be explicitly named.

---

## Output Schemas

### Edge Probe (Arms B and C output)

```json
{
  "case_id": "string",
  "route_id": "string (dimension_id)",
  "arm": "B | C",
  "call_metadata": {
    "provider": "string",
    "model": "string",
    "input_tokens": "integer",
    "output_tokens": "integer",
    "cost_usd": "number"
  },
  "activation_calls": [
    {
      "model_id": "string",
      "affordance_id": "string",
      "activation_status": "activated | set_aside | unclear | duplicate",
      "case_quote": "string (exact substring or empty string)",
      "rationale": "string"
    }
  ],
  "edge_probes": [
    {
      "edge_probe": "string",
      "trace": {
        "model_id": "string",
        "affordance_id": "string",
        "field_source": "do_not_use_when | case_evidence_needed | treatment_requirement | misuse_guard | diagnostic_question | mechanism | general_knowledge",
        "treatment_requirement_id": "string or null"
      },
      "why_this_is_edge": "string",
      "if_true_changes": "string",
      "dismissal_condition": "string",
      "clarity_cost": "low | medium | high"
    }
  ],
  "set_asides": [
    {
      "model_id": "string",
      "affordance_id": "string",
      "reason": "string"
    }
  ]
}
```

For Arm B, `trace.model_id` and `trace.affordance_id` may be inferred by the LLM from the model name and cannot be validated against `affordances_v3.json` — log them as unverified. For Arm C, all trace IDs must be validated.

### Arm A Baseline (extracted from archive)

```json
{
  "case_id": "string",
  "route_id": "string",
  "arm": "A",
  "questions": ["string"]
}
```

### Judge Output (one per case per route)

```json
{
  "case_id": "string",
  "route_id": "string",
  "judge_call_metadata": {
    "provider": "string",
    "model": "string",
    "input_tokens": "integer",
    "output_tokens": "integer",
    "cost_usd": "number"
  },
  "winner": "A | B | C | tie | all_bad",
  "constructive_edge": "A | B | C | none",
  "edge_source": "model_general_knowledge | diagnostic_question | treatment_requirement | do_not_use_when | case_evidence_needed | misuse_guard | none",
  "baseline_likely_would_reach": "yes | no | unclear",
  "generic_prompt_likely_would_reach": "yes | no | unclear",
  "decision_relevance_if_true": "high | medium | low",
  "dismissal_path": "clear | fuzzy | none",
  "clarity_cost": "low | medium | high",
  "theater_flag": "yes | no",
  "rationale": "string"
}
```

The judge must be blinded: labels A/B/C but not which is baseline, generic, or enriched. Randomize arm label assignment per judge call by seeded shuffle on `{case_id}_{route_id}` — deterministic by seed so the blind can be unblinded deterministically after judging.

**The judge must not be `x-ai/grok-4.1-fast`.** Grok returns `confidence: high` for every judgment (observed pattern). Use a stronger judge via OpenRouter. Record the exact model.

---

## Deliverables

1. **`research/pr11-gate4-case-selection-2026-05-05.md`**
   Per-case table: case slug, run timestamp, route count, v3-covered candidates, total candidates, why included.

2. **`scripts/run_gate4_edge_probe_experiment.py`**
   - `--archive-root` (default: `~/.local/share/lolla/runs/`)
   - `--affordances-path` (default: `data/compiled/model_affordances/affordances_v3.json`)
   - `--output-dir` (default: `data/evaluations/gate4_edge_probes/`)
   - `--cases` (optional: comma-separated slugs; default: the 10 listed above)
   - `--arms` (optional: A, B, C or subset; default: all three)
   - `--token-budget` per LLM call (default: 40,000; configurable; dry-run should report any budget-driven omissions separately from missing v3 records)
   - `--provider` and `--model` for Arm B/C calls
   - `--dry-run`: validates packets and output schemas without LLM calls; prints packet sizes and expected call count
   - `--seed` for any randomization (default: 42)

3. **`scripts/judge_gate4_edge_probes.py`**
   - `--input-dir` (default: `data/evaluations/gate4_edge_probes/`)
   - `--output-dir` (same or separate)
   - `--judge-provider` and `--judge-model`
   - `--seed` for arm label shuffle
   - `--dry-run`: validates input shape and prints judge call count without running
   - Writes one judge output JSON per route per case; writes a summary JSON with win/loss counts and trace-validity stats

4. **`data/evaluations/gate4_edge_probes/`**
   - `arm_a/{case_id}_{route_id}.json`
   - `arm_b/{case_id}_{route_id}.json`
   - `arm_c/{case_id}_{route_id}.json`
   - `judge/{case_id}_{route_id}.json`
   - `summary.json`

5. **`research/pr11-gate4-edge-probe-results-2026-05-05.md`**
   Written after judging. Contents:
   - Win/loss/tie table (per case and per route)
   - Constructive-edge attribution by arm and field_source
   - Regression table (C worse than A)
   - Theater flag count
   - Trace-validity stats (what % of C probes have validated IDs)
   - Judge model and total tokens/cost
   - Honest pass / inconclusive / fail verdict against precommitted bars

6. **Tests** in `tests/test_gate4_edge_probe_experiment.py`:
   - Dry-run validates packet assembly without LLM calls
   - Packet assembly includes v3 affordance records by `model_id`
   - Arm C packet does not include affordance records not in `affordances_v3.json`
   - Arm B packet includes model names but no affordance records
   - No Python semantic matching of `use_when` / `do_not_use_when` in packet assembly
   - Generated arm outputs pass schema validation
   - Trace IDs in Arm C outputs are validated against `affordances_v3.json`
   - Blinded judge label shuffle is deterministic by seed
   - No runtime imports (no `from engine` imports that affect `/lolla` behavior)

---

## Precommitted Success Bars (do not move these after running)

### Gate 4 passes if:
- Arm C has the strongest `constructive_edge` in at least **6/10 cases**
- In at least **5/10** winning C cases, `edge_source` is `do_not_use_when`, `case_evidence_needed`, `treatment_requirement`, or `misuse_guard`
- Arm C has no more than **1 clear regression** versus Arm A (`winner: A` and `constructive_edge: A`)
- **Theater flag** appears in no more than **2/10** C outputs
- No more than **2/10** C outputs have `clarity_cost: high`
- At least **80%** of C edge probes have valid trace IDs into `affordances_v3.json`
- Marcin spot-checks 3–5 wins and agrees they are real edge contributions, not better phrasing

### Gate 4 is inconclusive if:
- C beats A but ties or loses to B (`constructive_edge` B >= C in 6/10 cases)
- C wins mostly from `diagnostic_question` or `general_knowledge` field sources
- C produces sharper wording but not new operational pressure
- Judge confidence is mostly low
- Marcin sees wins as "nice but not edge"

### Gate 4 fails if:
- C loses to B (`constructive_edge: B` in 6+/10 cases)
- C adds noise with `dismissal_path: none` in 3+ cases
- C produces jargon, verbosity, or clever detours (theater flag ≥ 4/10)
- C mostly repeats known templates (`what would you have to believe` / `what assumptions are embedded`)
- C required Python semantic matching to produce its probes
- C trace IDs fail validation in more than 20% of probes

### If inconclusive:
Analyze whether the failure is: (a) wrong surface — Lane 4 questions may not be the right place to test edge probes; (b) corpus coverage — the 50-model corpus may not cover the most relevant routes for these cases; (c) prompt design — the edge-seeking instruction may need revision. Name the failure mode before commissioning follow-up work.

---

## Demotion Criteria (preserved as honest record)

Demote or pause the affordance-to-runtime path if:
- Enriched questions sound better but do not change decisions (`decision_relevance_if_true: low` dominates)
- Questions mostly duplicate existing Pressure Check / Lane 4 questions
- The LLM overuses affordance jargon without grounding in the case
- The trace is formally valid but `why_this_is_edge` is generic
- The judge prefers enriched because it is longer
- Best enriched questions come from `general_knowledge`, not extracted operational fields
- Operators would not want the extra questions in the product

Demotion does not kill the corpus. If Gate 4 fails on this surface, the corpus may still be valuable for Observatory, audit, or a different runtime surface. Name the surface failure specifically.

---

## What PR 11 Must Not Build

- No live Lane 4 augmentation
- No chat, memo, or Pressure Check changes
- No routing changes
- No compilation changes
- No model-affordance record edits
- No embedding-based retrieval unless packet size forces a narrowly scoped step (document if so)
- No merge to main
- No import of any experiment code into the runtime engine

PR 11 produces evidence. If Gate 4 passes, PR 12 is the first guarded runtime integration.

---

## Cost Awareness

Before running the full experiment, run `--dry-run` and report:
- Estimated call count per arm per case
- Estimated token budget per call and total
- Estimated judge calls and budget

Get cost approval before running the full 10-case experiment. A partial run on 3 cases is acceptable for calibration before committing to the full 10.

---

## Architecture Reminder

The retrieval-and-delivery principle applies here as everywhere:

> Python looks up affordance records by `model_id` and assembles a packet. The LLM decides activation. The LLM decides which affordances are edge-producing. The LLM generates the probes. Python validates shape and trace IDs. Python does not evaluate semantic conditions.

The discipline test: if the packet assembly can be implemented without reading the semantic content of `use_when`, `do_not_use_when`, or `case_evidence_needed`, it is on the right side of the line.
