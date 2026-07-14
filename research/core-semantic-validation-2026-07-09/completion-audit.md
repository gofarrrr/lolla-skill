# Core Semantic Validation Case 01 — Completion Audit

Date: 2026-07-09

| Objective requirement | Authoritative evidence | Result |
| --- | --- | --- |
| Turn Run 01 into a fixed evaluation case | Fixture conversation SHA-256 matches the archived Run 01 source; `gold.json` defines 15 required observations and five bounded absences. | Complete |
| Process the identical conversation through the compact path | `case-01-runs/compact-01.json` through `compact-03.json`; hashes locked in `case-01-runs/manifest.json`. | Complete |
| Process the identical conversation through the richer Decision Work-aligned path | `case-01-runs/shadow-01.json` through `shadow-03.json`; each reports four successful calls and the same source conversation hash. | Complete |
| Compare question changes | `question_events` recovered initial and current evidence-gate questions in all shadow repeats; compact path kept only the original broad decision. | Complete |
| Compare user corrections and pressures | Shadow runs stably recover no signed commitment, capacity, purchase-commitment concern, and opportunity-loss pressure; known misses are recorded. | Complete |
| Compare assistant positions and revisions | Four exact assistant stance spans recovered in all shadow repeats; condition-versus-commitment label instability recorded. | Complete |
| Compare constraints and options | Constraint and option family counts, grounding, and repeatability recorded in `two-path-comparison.json`; threshold captured stably. | Complete |
| Compare dropped threads | Compact thread identity changes across repeats; shadow always captures commitment concern and inconsistently captures board/name pressure. Result drives the merged thread-status decision. | Complete |
| Compare uncertainty and evidence boundaries | Shadow boundary events measured at 0.611 repeatability; weak-email and label completeness defects recorded. Compact has no first-class boundary. | Complete |
| Check repeatability | Three repeats per path; span and label Jaccard plus per-observation recovery persisted in `two-path-comparison.json`. | Complete |
| Decide every Decision Work field | `field-decisions.json` contains exactly 46 unique contract fields: 17 keep, 17 merge, 10 defer, 2 remove; contract equality test passes. | Complete |
| Design the clean reasoning-pattern packet only after field decisions | Design document, JSON Schema, and example separate provenance from a fact-free routing projection. | Complete |
| Do not modify graph behavior | No graph/routing/runtime file is changed; packet metadata and tests assert `graph_runtime_modified: false`. | Complete |
| Verify implementation | 123 focused and adjacent tests pass under Python 3.12; the example packet validates against its JSON Schema; privacy/raw-content scan is clean. | Complete |

The Case 01 objective is complete. Production promotion is deliberately not
claimed: the next evidence gate is the remaining multi-case core corpus.
