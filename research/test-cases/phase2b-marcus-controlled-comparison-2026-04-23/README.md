# Controlled Marcus comparison — Phase 2b Lane 4 (old path vs new path)

**Date:** 2026-04-23 (post-iteration)
**Phase:** 2b (Lane 4 Structural Coverage migration to `ConversationContext`)
**Purpose:** the cleanest single piece of evidence that Phase 2b **changes how Lane 4 grounds coverage evidence, not what it audits.**

## The controlled setup

- **Same conversation:** `lolla_20260422T155622Z_conversation.txt` (9-turn Marcus founder-CEO equity case; same as Phase 2a's controlled comparison)
- **Same fresh extraction:** `marcus_fresh_extraction.json` (reused from Phase 2a — extraction unchanged between phases)
- **Only difference between the two pipeline runs:** the Lane 4 input shape. Old path receives a collapsed `CritiqueRequest`; new path receives a `ConversationContext` via `--new-contract`.

Run sequence: `run_extract.py` once → `run_pipeline.py` twice (with and without `--new-contract`).

## The headline: same audit, different grounding

**Both paths produce identical structure:**

| axis | old path | new path |
|------|----------|----------|
| `question_type` | decision-evaluation | decision-evaluation |
| dimensions detected | 8 | 8 |
| gaps flagged | 4 | 4 |
| gap dim_ids | `existing-vs-new`, `information-quality`, `resource-allocation`, `risk-response` | `existing-vs-new`, `information-quality`, `resource-allocation`, `risk-response` |
| gap questions generated | 12 | 12 |

**Where they differ — `coverage_evidence` attribution language:**

Every one of the 4 gap citations on new path explicitly attributes to the assistant's reply content. Old path citations describe the same material in extractor-paraphrase-style without attribution.

### Side-by-side on the same 4 gaps

**`resource-allocation`:**
- OLD: `"Mentions $80K platform sprint opportunity cost but does not identify displaced alternatives (e.g., agency projects forgone)..."`
- NEW: `"Assistant proposes platform validation ($80K opp cost, 2 engineers 50% time) but does not explicitly identify displaced alternatives (e.g., client work revenue foregone, other hires)..."`

**`risk-response`:**
- OLD: `"Names risks (Marcus leaves, EBITDA drop, client loss) and sizes downside ($11M vs $5M exit) but does not distinguish mitigate (vesting/IP) vs adapt (succession)..."`
- NEW: `"Assistant acknowledges risks (Marcus leaves causing EBITDA drop from $2.2M to $1.5M, exit value $11M to $5M; platform failure burns cash; partner blocks/exits) and quantifies some downsides, but does..."`

**`information-quality`:**
- OLD: `"Uses valuation math and constraints as fact without assessing bias (e.g., self-reported 40% capability, prototype impressiveness)..."`
- NEW: `"No assessment of evidence quality (e.g., reliability of '40% capability' self-estimate, prototype impressiveness as biased by founder view, market rate comp data, EBITDA projections, Tom precedent gen..."`

**`existing-vs-new`:**
- OLD: `"Acknowledges agency (existing) vs platform (new) tension but does not separate metrics/risks (e.g., cannibalization of agency time, distraction from $2.2M EBITDA)..."`
- NEW: `"Assistant notes agency (existing, 4-6x) vs SaaS potential (new, 8-15x) but does not separate metrics/risks (e.g., cannibalization of agency time, distraction from $14M base)..."`

## Why this is the cleanest evidence

Because gap dim_ids + gap count + qtype match exactly between paths, the comparison isolates **one variable**: how Lane 4 grounds its coverage analysis.

- **Old path** reads a compiled `vanilla_answer` (synthesized_position + flattened assistant turns) and cites it as summary content ("Mentions...", "Names...", "Uses...").
- **New path** reads turn-structured assistant replies and cites with explicit attribution ("Assistant proposes...", "Assistant acknowledges...", "Assistant notes...").

This matches Phase 2a's Lane 3 finding (evidence quotes shift from extractor paraphrase to verbatim user words) applied one layer deeper: Lane 4's coverage analysis now grounds in what the assistant actually said, not what the extractor's compiled view looked like.

## What this doesn't show

- That new path produces *more* output volume. On Marcus, count is identical (12 gap_qs each path).
- That new path is better on every case. The 10-case aggregate shows +15% gap_qs on new path post-iteration, with some per-case variance — see `../phase2b-lane4-equivalence-2026-04-23/lane4-quality-report.md`.

## Context: this required one prompt iteration

First-draft new-path detection prompt under-flagged abstract dimensions (timing, uncertainty, competitive-dynamics) that don't surface verbatim in user turns. The LLM biased toward concrete dimensions surfacing directly from turn text and missed structurally-present-but-implicit dimensions.

Fix: added a `CHECKLIST — COMMONLY-MISSED DIMENSIONS` section to `_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT` explicitly listing the 4 most commonly-missed dimensions and reinforcing "LOW BAR for detection, HIGH BAR for coverage."

Post-iteration Marcus A/B (documented above) is the clean state. Pre-iteration Marcus A/B (see commit history) had new path detecting a different gap set (`stakeholder-alignment` instead of `existing-vs-new`) and fewer gap_qs (8 vs 12). Worth naming because **Phase 2c (Lane 1) will re-encounter this same pattern**: a new-path prompt that reads turn-structured input needs an explicit reminder to check abstract structural dimensions, not just what surfaces from user text. This is a durable lesson for any lane that judges structural properties.

## Companion evidence in this PR

- **10-case corpus measurement** (`../phase2b-lane4-equivalence-2026-04-23/`) — N=3 per path × 10 cases; post-iteration aggregate shows +15% gap_qs on new path with zero regressions.
- **Architecture-vs-volume ablation on `friendship_money`** (`scripts/phase2b_ablation_architecture_vs_volume.py`) — SOURCE=user-turns for classification is load-bearing independently of volume.
- **0-gap-qs anomaly diagnosis** (`scripts/phase2b_diagnose_gap_qs_anomaly.py`) — N=5 re-run ruled out name-keying + malformed-JSON hypotheses; post-iteration measurement shows anomaly rate on new path dropped from 2/30 to 0/29.

Three angles: Marcus A/B (this directory — same audit, different grounding) + scale measurement (+15% gap_qs, zero regressions) + targeted ablation (architecture isolated on classification).
