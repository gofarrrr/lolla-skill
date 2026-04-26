# Lane 2 attribution — cross-case synthesis

Generated: 2026-04-26T14:42:49Z
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
- `Cand-cond.` (candidate-conditional shared-available acceptance agreement) — the verifier-quality metric introduced post-campaign. Numerator: model_ids accepted in BOTH runs. Denominator: model_ids accepted in EITHER, AND present as a candidate in BOTH runs. Renders "—" when no candidate was accepted in either run (undefined). Read alongside `Accepted-pre`: when `Accepted-pre` and `Cand-cond.` diverge, the gap is recall-induced variance; when they agree, verifier judgment instability is the story.

## Embedding mode: `on`

| Case | N | FP moves | Candidates | Accepted-pre | Cand-cond. | Detected | Capped | Calibrated | Anchors | Step 6 cons. | Boundary tok | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `marcus-equity-pathB-on` | 3 | 0.03 | 0.77 | 0.19 | 0.19 | 0.08 | 1.00 | 0.08 | 0.08 | 100% (n=1) | 514317 | `inconclusive_widen_n_or_cases` |
| `mid-level-consultant-decides-pathB-on` | 3 | 0.18 | 0.80 | 0.46 | 0.48 | 0.37 | 1.00 | 0.37 | 0.37 | 20% (n=1) | 367351 | `inconclusive_widen_n_or_cases` |
| `mother-deciding-address-year-pathB-on` | 3 | 0.06 | 0.75 | 0.26 | 0.33 | 1.00 | 1.00 | 1.00 | 1.00 | 60% (n=1) | 294326 | `inconclusive_widen_n_or_cases` |
| `third-year-phd-student-pathB-on` | 3 | 0.05 | 0.77 | 0.15 | 0.19 | 0.16 | 1.00 | 0.16 | 0.16 | 80% (n=1) | 509031 | `inconclusive_widen_n_or_cases` |

## Sources

- `marcus-equity-pathB-on` (on): N=3
- `mid-level-consultant-decides-pathB-on` (on): N=3
- `third-year-phd-student-pathB-on` (on): N=3
- `mother-deciding-address-year-pathB-on` (on): N=3
