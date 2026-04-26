# Lane 2 follow-up tracking

Date: 2026-04-26
Status: pre-implementation tracking doc
Companions:
- `research/lane2-attribution-design-2026-04-26.md` — original Lane 2 attribution memo (the contract that PR #39 implemented)
- `research/stability-runs/lane2-attribution-2026-04-26/synthesis.md` — campaign cross-case data
- `research/stability-runs/lane2-attribution-2026-04-26/interpretation.md` — post-campaign reading

## What the campaign told us

Headline: the verifier is the dominant observed amplifier. Recall is moderately stable (Candidates Jaccard ~0.72); the verifier collapses that to ~0.06–0.39 Accepted-pre Jaccard. Even controlling for candidate availability — the candidate-conditional `shared_available_acceptance_agreement` metric — the verifier's per-candidate judgment is unstable (overall mean 0.28).

Remediation that follows from the data: partition the verifier obligation into narrower per-bucket calls, preserving the full information per call. The memo's allowed-fixes list explicitly authorizes "split or narrow the verifier" when verification is the unstable stage.

A pre-existing duplicate-accepts bug surfaced as a side-effect: the verifier sometimes accepts the same `model_id` more than once, which propagates to duplicate `DetectedModel` objects, which trips `CompanionCard cannot contain more than 3 expansions per detected model` at card build (`engine/system_b/companion.py:126`). Mother-deciding-OFF was unrunnable for this reason. The bug is independent of the verifier-decomposition work but compounds with it, because parallel verifiers create more dedupe pressure, not less.

## Sequencing

Two sequential PRs. Do NOT open both branches yet.

- **PR-A** lands first. Mechanical, small, unblocks the next architecture work.
- **PR-B** lands after PR-A is merged. Architecture change, gated by pre-registered acceptance criteria below.

The dependency order keeps blame attribution clean: if PR-B regresses, we know it's decomposition, not the duplicate-accept bug.

## PR-A scope: dedupe + first-class candidate-conditional metric

Branch (suggested): `fix/lane2-dedupe-and-candidate-conditional-metric-2026-04-XX`

**Code changes:**
- Dedupe verifier accepted entries by `model_id` in `engine/system_b/companion_routing.py::run_verification_call_from_packet`. Preserve the first valid accepted item's `evidence_quote` and `presence_explanation`.
- If cheap, expose duplicate accepted entries as a separate audit field (e.g., `companion_verification_duplicate_accepts`) — model_id + count, drop reason "duplicate_accept_dedupe". Do NOT merge into `companion_rejected_models` (semantic rejection is different).
- Threading: dedupe must happen BEFORE the top-5 surfacing budget is applied, so the cap counts unique accepted models, not raw verifier output.

**Stability-harness changes:**
- Add candidate-conditional verifier-stability metric to `scripts/stability_check.py`:
  ```
  shared_available_acceptance_agreement =
    | accepted_in_both_runs |
    / | (accepted_in_run_a ∪ accepted_in_run_b) ∩ candidate_present_in_both_runs |
  ```
- Surface in `stability.json` per-pair AND aggregated mean per case-mode.
- Render in `variance.md` and `synthesis.md` cross-case table — first-class, alongside Accepted-pre Jaccard, not buried.
- Reading-guide line: "this controls for candidate availability — set Jaccard treats 'absent in B' the same as 'present in B but rejected'; this metric isolates the verifier's per-judgment instability."

**Tests:**
- Regression: verifier returns the same `model_id` twice in `accepted` → exactly one `DetectedModel`, evidence/explanation from the first valid entry, audit shows the duplicate-drop count.
- Regression: with deduplication, a payload that previously violated the CompanionCard expansion invariant now succeeds.

**Re-measurement:**
- Re-run only `mother-deciding-address-year-lane2-off` at N=3, embeddings OFF. If dedupe is the right fix, the case completes cleanly and we get the missing 4th paired data point.
- Add the new metric retroactively to the existing 7 stability files by re-running the synthesizer (no pipeline reruns needed; metric is computable from stored candidate + accepted lists).

**Out of scope (PR-A):**
- Verifier decomposition.
- Bucketing / reasoning_types.
- Top-5 cap tuning.
- Embedding flag splits.
- Fingerprint paraphrase fixes.
- Lifting the CompanionCard expansion invariant. (Dedupe is the right fix; the invariant is a useful safety check that should stay.)

## PR-B scope: reasoning-type partitioned verifier

Branch (suggested): `feat/lane2-reasoning-type-partitioned-verifier-2026-04-XX`. Open only after PR-A is merged.

**Architecture:**
- Partition recalled candidates deterministically by `reasoning_types[0]` from `data/knowledge_graph.json`. Models without a `reasoning_types` field bucket to `"unknown"`.
- Run one verifier call PER non-empty bucket, in parallel (matches Pass 1 family-cluster pattern).
- Each per-bucket verifier receives:
  - The full assistant source text (not partitioned).
  - The full validated fingerprint (not partitioned).
  - Only the candidates assigned to its bucket.
- Fan-in is deterministic:
  1. Concatenate all per-bucket accepted lists.
  2. Dedupe by `model_id` (preserves first occurrence by bucket-iteration order then per-bucket order — both deterministic).
  3. Sort by `(candidate.final_rank, model_id)` so global ordering is stable independent of which bucket finished first.
  4. Apply existing top-5 surfacing budget.

**Audit additions:**
- Persist `verifier_bucket` per candidate.
- Persist `candidate_final_rank` (already added in PR #39 as `final_rank` — confirm it survives partitioning).
- Per-bucket boundary call traces (so per-bucket cost is measurable).

**Pre-registered acceptance gates** (must clear before PR-B can flip ready-for-review). Baselines from the PR #39 campaign:

| Metric | Baseline (this campaign) | PR-B gate |
|---|---|---|
| Accepted-pre Jaccard mean across paired cases | 0.21 | ≥ 0.50 |
| Accepted-pre Jaccard worst case | 0.06 | ≥ 0.30 |
| Shared-available accept agreement mean | 0.28 | ≥ 0.60 |
| Shared-available accept agreement worst case | 0.06 | ≥ 0.35 |
| Candidates Jaccard mean | 0.72 | unchanged ± 0.05 |
| Accepted count mean per run | 3–5 | 2–7 |
| All-zero-accepted cases | 0 | 0 (unless monolithic baseline was also 0) |
| Verifier boundary token share | 9–16% | ≤ 30% |
| Qualitative spot check | n/a | no obvious generic over-acceptance from removed competition |

**Why these gates:**
- Accepted-pre and candidate-conditional metrics together pin "judgment is more stable" without letting one mask the other.
- Candidates Jaccard "unchanged ± 0.05" makes sure we didn't accidentally change recall semantics under the architecture.
- Accepted count `2–7` floor catches the worst failure mode: stable-because-everything-is-rejected. The upper bound catches stable-because-all-broad-models-accepted (removed competition, not reduced overload).
- Verifier token share ≤ 30% allows growth from 9–16% (~2x) but not 3x — partitioning IS expected to cost more, but a 3x rise would mean we've lost the obligation-narrowing gain.
- Qualitative spot-check is non-negotiable. Count gates don't catch a per-bucket verifier accepting a broad overlay model the monolithic verifier would have rejected because a more specific candidate elsewhere outcompeted it. A human reads the per-case evidence quotes.

**Measurement plan:**
- Re-run the same 4 cases (Marcus, consultant, PhD, mother-deciding) at N=3 each, embeddings ON only. Embeddings already shown to not be the variance source; ON-only halves the campaign cost.
- Synthesizer report against PR-B's `stability.json` files; compare directly to the PR #39 baselines via the gate table above.
- If any gate fails: report findings, do not merge, decide whether to iterate or revert.

**Out of scope (PR-B):**
- Lane 4 changes.
- Fingerprint decomposition.
- Embedding flag refactors.
- Cap value tuning beyond the existing top-5.

## Open questions

These are surfaced explicitly so we don't drift into them under PR-A or PR-B scope.

- **List-aware bucketing.** `reasoning_types[0]` is the deterministic safe choice for PR-B. List-aware (model in every applicable bucket, dedupe at fan-in) maximizes signal but introduces cross-bucket duplicate acceptance pressure that makes the fan-in part of the experiment, not a constant. Defer until PR-B's per-case data shows a load-bearing model getting bucketed wrong.
- **Fingerprint stability under embedding cosine.** Text Jaccard on `reasoning_move` under-reports stability because LLM paraphrases the same move differently each run. Worth measuring under embedding cosine before deciding whether fingerprint actually IS unstable. Separate investigation.
- **CompanionCard expansion invariant.** Dedupe (PR-A) is the right fix for the observed failure mode. The invariant itself is a useful safety check that should stay. Lift only if a future case shows a legitimate model with >3 distinct expansions in the relation graph that we want to surface.
- **Decision-tree threshold tuning.** The pre-registered tree's absolute bands are too strict; a relative metric (e.g. "Candidates − Accepted-pre delta ≥ 30 points") would have fired correctly. Open question whether to update the tree's band rules in a future iteration of the design memo, or just rely on the candidate-conditional metric to do the work.
- **Mother-deciding family coverage.** The reciprocity / boundary / emotional family is currently the weakest covered family in our case mix because mother-OFF is blocked. Once PR-A unblocks it and PR-B's measurement re-runs, this coverage gap closes.

## Definition of done for this tracking doc

This doc closes when:
- PR-A is merged.
- PR-B is merged.
- A post-PR-B campaign report (in `research/stability-runs/lane2-partitioned-verifier-2026-XX-XX/`) shows the gates above were met or names which gate failed and why.

Until then, treat this doc as the active source of truth for what comes next on Lane 2.
