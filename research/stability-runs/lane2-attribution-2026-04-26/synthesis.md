# Lane 2 attribution — cross-case synthesis

Generated: 2026-04-26T11:20:20Z
Archive root for Step 6 consumption baseline: `/Users/marcin/.local/share/lolla/runs`

Contract: research/lane2-attribution-design-2026-04-26.md

Reading guide:
- Per-cell value = pairwise Jaccard mean across N runs (1.0 is a warning, not a target).
- Decision call applies the memo's pre-registered band rules; not a fix recommendation.
- Step 6 consumption baseline is derived from archived full skill runs at report time, matched to the case_id by token overlap. Read variance in cases with low consumption with that caveat — Lane 2 stability is an upper bound on user-visible quality there.

**Implementation literacy — what each row actually measures:**

- `Candidates`, `Accepted-pre`, `Detected`, `Capped` — clean Lane 2 recall→verify measurements. Pass 1 does not feed Lane 2 recall and cheat-sheet rerank is downstream, so these rows isolate the recall-and-verifier pipeline.
- `Anchors` — downstream product-facing row, but **contaminated by cheat-sheet selection/reranking** when embeddings flip globally. The `--embeddings on/off` switch is global to the pipeline, not Lane-2-only — flipping it also affects Pass 1 embedding tendency hits, Lane 1 relevance scoring, and cheat-sheet semantic reranking. Read `Anchors` ON-vs-OFF deltas with that caveat; read `Candidates` ON-vs-OFF deltas as the cleanest Lane-2-recall isolation.
- `FP moves` — keyed on normalized `reasoning_move` text, **not** the LLM-generated `move_id`. If the LLM paraphrases the same move differently across runs (e.g. "weighing opportunity cost" vs. "considers opportunity costs"), this metric under-reports stability. Cross-check with the per-run diff list before concluding fingerprint is unstable.
- `Capped` stability is meaningful only when `Accepted-pre` exceeds the top-5 surfacing budget; otherwise capped is empty by construction across runs.

## Embedding mode: `off`

| Case | N | FP moves | Candidates | Accepted-pre | Detected | Capped | Anchors | Step 6 cons. | Boundary tok | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| `marcus-equity-lane2-off` | 3 | 0.03 | 0.70 | 0.13 | 0.13 | 1.00 | 0.13 | 100% (n=1) | 428458 | `fix_fingerprint_or_query_construction` |
| `mid-level-consultant-decides-lane2-off` | 3 | 0.05 | 0.68 | 0.16 | 0.16 | 1.00 | 0.16 | 20% (n=1) | 246034 | `fix_fingerprint_or_query_construction` |
| `third-year-phd-student-lane2-off` | 3 | 0.00 | 0.75 | 0.39 | 0.30 | 0.00 | 0.30 | 80% (n=1) | 323533 | `inconclusive_widen_n_or_cases` |

## Embedding mode: `on`

| Case | N | FP moves | Candidates | Accepted-pre | Detected | Capped | Anchors | Step 6 cons. | Boundary tok | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| `marcus-equity-lane2-on` | 3 | 0.00 | 0.72 | 0.17 | 0.17 | 1.00 | 0.17 | 100% (n=1) | 439143 | `inconclusive_widen_n_or_cases` |
| `mid-level-consultant-decides-lane2-on` | 3 | 0.00 | 0.72 | 0.22 | 0.22 | 1.00 | 0.22 | 20% (n=1) | 327970 | `inconclusive_widen_n_or_cases` |
| `mother-deciding-address-year-lane2-on` | 3 | 0.12 | 0.75 | 0.06 | 0.06 | 1.00 | 0.06 | 60% (n=1) | 228994 | `inconclusive_widen_n_or_cases` |
| `third-year-phd-student-lane2-on` | 3 | 0.20 | 0.76 | 0.37 | 0.37 | 1.00 | 0.37 | 80% (n=1) | 443305 | `inconclusive_widen_n_or_cases` |

## Embedding-induced delta (paired ON vs OFF)

Difference of `Candidates` Jaccard mean (`off` − `on`). Positive = embeddings destabilize recall. Negative = embeddings stabilize recall. Near zero = embeddings not the dominant variance source for this case.

| Case | ON candidates | OFF candidates | Δ (off − on) |
|---|---|---|---|
| `marcus-equity-lane2` | 0.72 | 0.70 | -0.02 |
| `mid-level-consultant-decides-lane2` | 0.72 | 0.68 | -0.04 |
| `third-year-phd-student-lane2` | 0.76 | 0.75 | -0.01 |

## Sources

- `marcus-equity-lane2-on` (on): N=3
- `marcus-equity-lane2-off` (off): N=3
- `mid-level-consultant-decides-lane2-on` (on): N=3
- `mid-level-consultant-decides-lane2-off` (off): N=3
- `third-year-phd-student-lane2-on` (on): N=3
- `third-year-phd-student-lane2-off` (off): N=3
- `mother-deciding-address-year-lane2-on` (on): N=3
