# Core Semantic Corpus — Completion Audit

Date: 2026-07-09

| Requirement | Evidence | Result |
| --- | --- | --- |
| Reuse complete source conversations rather than summaries | `tests/fixtures/core_semantic_validation/corpus-v0/manifest.json` locks 12 source paths and SHA-256 hashes. | Complete |
| Define source-first gold before new model runs | Eleven new gold files plus the fixed Case 01 gold contain 102 exact-span observations; manifest integrity test verifies every quote against speaker and turn. | Complete |
| Run the same compact contract three times per case | 36 compact artifacts exist; 33 new runs retain call-level usage and the three Case 01 runs remain fixed. | Complete |
| Run the same shadow contract three times per case | 36 shadow artifacts and 144 successful call records exist. | Complete |
| Preserve operational failures | One empty compact provider response is retained as `case-06-friendship-money/compact-01-attempt-01.error.json`; bounded retry succeeded. | Complete |
| Compare coverage and repeatability across cases | `corpus-comparison.json` and `.md` aggregate macro, weighted, per-case, and per-dimension results. | Complete |
| Correct grounding measurement | Derivation labels no longer receive literal-span credit when only turn references survive serialization; a regression test covers the boundary. | Complete |
| Reassess the 46 field decisions | `field-decisions-corpus-reassessment.json` covers the exact 46-field set, records no structural reversals, and separates contract decisions from implementation readiness. | Complete |
| Make a graph-integration decision | `core-semantic-corpus-result.md` confirms the semantic-kernel direction and blocks graph integration pending a locked v0.1 gate. | Complete |
| Avoid graph/runtime changes | All 11 new case manifests and the Case 01 manifest state `graph_runtime_modified: false`; no graph, routing, or live runtime file appears in the worktree changes. | Complete |
| Verify implementation and artifacts | 98 focused and adjacent tests pass; Python files compile; every new JSON parses; credential/raw-provider-content scan is clean. | Complete |

The corpus phase is complete. The next development plan is governed by
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`. Its first
implementation slice repairs exact derivation provenance; later question,
stance, pressure, evidence, and thread-treatment judgments remain LLM/human
semantic work inside a deterministic evidence and custody harness.
