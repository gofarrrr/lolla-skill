# Lane 2 Attribution Design Memo

Date: 2026-04-26
Status: pre-implementation design note

## Verdict

Do the Lane 2 attribution PR, but do not frame it as "reduce 60 candidates to 30." That would confuse a measurement problem with a quality fix.

The goal is to understand where Lane 2 loses quality or stability while preserving the information needed for good reasoning. The first branch should make the deterministic/probabilistic boundary visible, not tune the candidate cap or split the verifier yet.

## What Lane 2 Is For

Lane 2 is not just "find mental models." Its product role is to identify mental models already active in the assistant's reasoning, then attach curated failure modes, premortems, antagonists, allies, heuristics, and identity chunks that help Step 6 reconsider the original advice with more specific structural pressure.

If Lane 2 returns nothing, Step 6 loses a source of model-specific enrichment. It can still use Lane 1 findings, Lane 3 reframes, Lane 4 gaps, and the Bullshit Index, but it loses the ability to say "this advice is leaning on Opportunity Cost / Endowment Effect / Reciprocity" with curated failure modes and tensions attached.

## Current Code Facts

- Live companion flow is `fingerprint -> recall -> verify -> select`: `SystemBPipeline._run_companion` builds a packet, runs fingerprint, recalls candidates, verifies them, then builds `CompanionCard`.
- The live recall path uses `recall_candidates(...)` with default `max_candidates=60`; the pipeline does not override it.
- The older `retrieve_candidate_models(..., max_candidates=30)` function is not called by the live path.
- The verifier receives up to 60 candidates in one LLM call and returns accepted/rejected judgments with evidence quotes and presence explanations.
- Verification then silently truncates accepted models to top 5 via `detected_models = detected_models[:5]`.
- `CompanionCard` enforces a maximum of 5 detected models, so the cap is real. The problem is not the existence of a cap; the problem is silent, order-driven truncation without pre-cap observability.
- `stability_check.py` rerun mode calls `run_pipeline.py --skip-revision`, so it measures upstream pipeline stability, not Claude's real Step 6 output in the skill flow.
- `run_pipeline.py` currently enables embeddings whenever `OPENAI_API_KEY` is present. The attribution work therefore needs an explicit embedding-mode control; otherwise an ON/OFF comparison cannot be trusted.

## Stage Map

| Stage | Input | Obligation | Output | Boundary Type | Information Dropped Today |
|---|---|---|---|---|---|
| Fingerprint | Conversation packet with CONTEXT/SOURCE split | Extract assistant reasoning moves backed by assistant-turn substrings | Raw, validated, dropped fingerprint moves | Probabilistic extraction plus deterministic quote validation | Raw moves failing quote validation are dropped with reasons |
| Recall | Assistant text plus validated fingerprint moves plus KG/signals/embeddings | Produce candidate mental models worth verifying | Ordered candidate list | Mostly deterministic keyword overlap, optionally probabilistic embedding query expansion | Candidates beyond cap are excluded without audit visibility |
| Verify | Source text, fingerprint moves, candidate list | Decide executed/violated/neither for each candidate with evidence | Accepted and rejected model judgments | Probabilistic semantic judgment plus deterministic quote validation | Accepted items after top 5 are silently dropped |
| Card Build | Post-cap detected models plus KG/relation graph | Attach curated chunks and relations | `CompanionCard` | Deterministic graph walk | Drop already happened at Verify; Card Build operates only on the post-cap set |
| Cheat Sheet Selection | Companion card plus DeltaCard anti-echo plus optional embedding rerank | Produce bounded Step 6 surface | `CompanionCheatSheet.anchors` | Deterministic selection with optional embedding scoring | Candidate chunks not selected are not surfaced in the cheat sheet |
| Step 6 Consumption | Full conversation plus four cards | Reconsider the original advice | `revised_answer` | Claude-authored reasoning outside pipeline rerun harness | Not measured by pipeline-only stability runs |

## Deterministic And Probabilistic Roles

The deterministic system should preserve structure, provenance, caps, ordering, and audit trails. It should also make cheap, reversible routing decisions.

The probabilistic system should do semantic judgment where string matching and graph traversal are insufficient: extracting reasoning moves, judging whether a model is executed or violated, and later reconsidering the advice in Step 6.

The mistake to avoid is using deterministic code to discard uncertain but relevant information before semantic judgment has happened. The opposite mistake is asking one probabilistic call to judge too many unrelated items and then pretending the output order is stable.

Working principle:

> No irreversible discard before a semantic stage unless the discard is deterministic, principled, and audit-visible. If we need to reduce cognitive load, prefer partitioning the obligation into narrower calls over silently shrinking the information set.

That does not mean caps are forbidden. It means caps must be named, justified, measured, and reversible through audit data.

## Quality Definition

Lane 2 quality is not "highest Jaccard everywhere."

Better definition:

> Lane 2 is high quality when the load-bearing mental-model anchors that matter to Step 6 are present, evidence-backed, non-duplicative with Lane 1, and stable enough that repeated runs preserve the same structural pressure even if lower-priority anchors vary.

Observable proxies:

- Candidate set stability: are we giving the verifier a similar relevant universe?
- Accepted-before-cap stability: does semantic verification agree across runs?
- Post-cap detected stability: does the surfaced top set remain stable?
- Cheat-sheet anchor stability: does the Step 6-facing surface remain stable?
- Step 6 anchor use: does the final updated position name/account for anchors?

Working operational definitions for the first attribution pass:

- **Stable-core anchor:** a `companion_cheat_sheet.anchors[].model_id` that appears in at least 2 of 3 runs for the same case and embedding mode.
- **Step-6-visible anchor:** an anchor whose `display_name` appears in a persisted `revised_answer` from a full skill/archive run.
- **Candidate load-bearing anchor:** an anchor that is stable-core, Step-6-visible, or both.

These definitions are intentionally provisional. The attribution report should refine them instead of pretending they are the final product-quality definition.

Important caveat: the current stability rerun path skips real Step 6, so Step 6 anchor-use measurement only works on archived full skill runs where `revised_answer` was persisted. Pipeline-only N=3 runs can diagnose Lane 2, but they do not prove user-visible quality.

## Candidate Audit Schema

Persist normalized candidate diagnostics into `audit_summary.companion_candidates`.

Suggested shape:

```json
{
  "model_id": "opportunity-cost",
  "model_name": "Opportunity Cost",
  "recall_source": "keyword | embedding | both",
  "keyword_rank": 3,
  "embedding_rank": null,
  "final_rank": 3
}
```

Use per-source ranks rather than a single `source_rank`. A single rank becomes ambiguous when `recall_source` is `both`. The internal code can keep its current strings (`keyword_recall`, `embedding_recall`, `keyword_recall+embedding_recall`), but the serialized audit surface should normalize them.

If the current implementation cannot cheaply recover `embedding_rank` without deeper changes, persist `null` for now and add it later. `final_rank` is mandatory.

## Verification Audit Schema

Persist three separate sets:

- `companion_verification_accepted_before_cap`: every accepted model from verification before the 5-model card budget is applied.
- `companion_detected_models`: current surfaced, post-cap detected models.
- `companion_verification_capped_models`: accepted-but-not-surfaced models removed by the top-5 budget.

Do not put capped models into `companion_rejected_models`. Rejected means semantically rejected or validation-demoted. Capped means accepted but unsurfaced because of budget.

## Archive Consumption Sanity Check

Completed on 2026-04-26 against archived full skill runs under `~/.local/share/lolla/runs`.

Method:

- Read archived `result.json` files with non-empty `companion_cheat_sheet.anchors[]`.
- Use persisted `revised_answer`, falling back to sibling `revised.txt` when needed.
- Count exact case-insensitive `display_name` appearances in the revised text. This matches the Step 6 anchor-naming invariant, which requires verbatim display names.

Result:

- 11 archived full runs qualified.
- Aggregate anchor naming: 27 of 38 anchors, 71.1%.
- This clears the "attribution is directly load-bearing" threshold.
- Caveat: two consultant/whistleblower-style runs were weak, at 20.0% and 33.3%, so downstream Step 6 consumption remains a parallel risk for high-stakes authority/legal cases.

Conclusion:

Proceed with Lane 2 attribution first. Do not demote the attribution PR behind a Step 6 consumption fix, but keep Step 6 anchor consumption in the report as a user-visible risk.

## Measurement Plan

Before opening future Lane 2 behavior-changing PRs, repeat the archive sanity check:

- Walk archived full skill runs that contain both `companion_cheat_sheet.anchors[]` and `revised_answer`.
- For each run, compute what fraction of anchor `display_name`s appear in the revised answer.
- If the aggregate rate is below 30%, upstream Lane 2 variance may be mostly invisible to the product and Step 6 consumption should move ahead of upstream attribution.
- If the aggregate rate is at least 70%, attribution is directly load-bearing for the user-visible product.
- If the rate lands between 30% and 70%, keep attribution first but report Step 6 consumption as a parallel risk.

Then run `stability_check.py` once per case and embedding mode. Follow with a cross-case synthesis script.

Cases:

- Marcus baseline case.
- `whistleblower`: dense legal/authority/protocol pressure.
- `multi_offer`: opportunity cost, identity, incentive, and tradeoff pressure.
- `friendship_money`: reciprocity, boundary, emotional/social pressure.

Modes and N:

- Run each case with embeddings ON and embeddings OFF.
- Use N=3 per case per mode for the first pass.
- Total planned first pass: 4 cases * 2 embedding modes * 3 runs = 24 pipeline runs.
- Add an explicit run control for embedding mode instead of relying on whether `OPENAI_API_KEY` is set.

Per-case output:

- Existing `stability.json` and `variance.md`.
- Add Lane 2 substage Jaccards:
  - fingerprint validated moves, using normalized `reasoning_move` and/or evidence quotes, not LLM-generated `move_id`;
  - recalled candidates;
  - embedding-unique candidates versus keyword/both candidates;
  - accepted before cap;
  - detected after cap;
  - capped models;
  - cheat-sheet anchors;
  - Step 6 anchor mentions when `revised_answer` exists.
- Add per-stage boundary token cost.
- Add direct embedding/query-expansion cost as a separate sidecar metric. The report should distinguish `boundary_only`, `embedding_expansion`, and `total_observed` instead of quietly under-counting Lane 2 spend.

Cross-case output:

- Add `scripts/lane2_attribution_report.py`.
- It reads multiple `stability.json` files and emits one side-by-side Markdown table.
- It groups rows by case and embedding mode so we can answer whether recall variance disappears when embeddings are OFF.
- It carries a `step6_consumption_baseline` column per case, sourced from the archive sanity check (or recomputed from `~/.local/share/lolla/runs` at report time). This contextualizes each case's Lane 2 variance numbers against historical Step 6 anchor-naming rate — Marcus / multi_offer / friendship_money sit near 100%; whistleblower is structurally similar to the consultant/report-writing cases that landed at 20–33%, so its variance should be read with that caveat.
- Purpose: prevent three isolated reports from becoming three isolated anecdotes.

## Pre-Registered Decision Tree

- If fingerprint stability is low and candidate stability is low, fix fingerprint/query construction first.
- If candidate-set Jaccard is below 0.70, fix recall/candidate contract before changing verifier prompts.
- If candidate-set Jaccard is at least 0.85 but accepted-before-cap Jaccard is below 0.50, split or narrow the verifier.
- If accepted-before-cap Jaccard is at least 0.85 but post-cap detected/anchor Jaccard is below 0.50, top-5 ordering/truncation is the main amplifier.
- If post-cap detected models are stable but cheat-sheet anchors vary, diagnose companion selection/reranking.
- If anchors are stable but Step 6 naming varies on full skill runs, diagnose downstream consumption.
- If all Lane 2 substage Jaccards are at least 0.85 across cases and modes, declare a null result for Lane 2 and look elsewhere before changing this lane.

These thresholds are diagnostic bands, not product law.

## Allowed Fixes After Attribution

- Add observability without behavior change.
- Make caps explicit and config-visible while preserving current defaults.
- Split verifier calls by model family if verification is the unstable stage.
- Use deterministic merge after parallel verification.
- Preserve pre-cap accepted models in audit even when only 5 anchors are surfaced.
- Add family/rank metadata so downstream selection has a principled tie-break.
- Make probabilistic recall configurable: embeddings on/off, query expansion on/off, and deterministic expansion settings such as temperature 0.
- Use a stronger model for a narrower verifier obligation if cost/quality justify it.

## Disallowed Fixes For This PR

- Reducing 60 to 30 as a quality fix.
- Adding score thresholds that discard candidates before we know recall quality.
- Splitting verifier prompts before attribution proves verifier instability.
- Changing ranking semantics while claiming the PR is only diagnostic.
- Treating Jaccard as the product-quality metric.
- Treating pipeline-only stability runs as proof of Step 6 user-visible quality.

## First PR Scope

Branch:

`fix/lane2-variance-attribution-2026-04-26`

Deliverables:

- Add `companion_candidate_cap: int = 60` to pipeline config and thread it into `recall_candidates(max_candidates=...)`.
- Add explicit embedding-mode controls for the attribution harness so the same case can run with embeddings ON and OFF independent of local environment variables.
- Persist `companion_candidates` with normalized recall source and ranks.
- Persist accepted-before-cap and capped verification outputs separately from rejected outputs.
- Extend `stability_check.py` with Lane 2 substage stability, embedding-mode metadata, per-stage boundary token costs, and direct embedding/query-expansion sidecar costs where observable.
- Add `scripts/lane2_attribution_report.py` for cross-case synthesis.
- Run N=3 for each embedding mode on Marcus, `whistleblower`, `multi_offer`, and `friendship_money`.

Out of scope:

- Cap-value tuning.
- Verifier split.
- Ranking changes.
- Fingerprint decomposition.
- Step 6 quality eval beyond reporting anchor mentions when full revised answers exist.

## Open Questions

- Does anchor variance matter to the user if Step 6 still reaches the same revised position?
- Should accepted-but-capped models be visible only in audit, or should the Observatory expose a "considered but not surfaced" panel?
- Does the optional embedding expansion path materially reorder candidates in real runs, or is most variance coming from fingerprint and verifier?
- Should future quality evaluation include a Step 6 replay harness, separate from pipeline stability?
- Is the cheat sheet's current shape, up to 5 anchors with chunks, the right Step 6 target? If Step 6 only uses 2 or 3 anchors, deeper anchors may be more valuable than more anchors.
