# Lane 2 Producer Audit — Design Memo

Date: 2026-04-26
Branch: `feat/lane2-producer-audit-design-2026-04-26`
Depends on: PR #41 merged (Step 6 wording contract)
Author: Claude (with Marcin as the gold-label owner and direction-setter)

## 0. Five framing locks (the memo's spine)

Before anything else, this memo commits to five things. Every later section is built on top of these. If any of these shifts, the audit shifts.

1. **Buckets are hypotheses, not ground truth.** The corpus is split into "failure-rich," "candidate positive controls," and "false-positive risk controls." Those labels are *audit hypotheses about what we expect to see* — not asserted truths. The audit exists to test those intuitions. If a "candidate positive control" turns out to have leaks, that is a finding, not a category error.
2. **Gold labels are cluster-level, not case-level.** "Marcus should have Endowment Effect, Optionality, Inversion" is too mushy and invites hindsight. The unit is *one anchor-worthy reasoning cluster from the assistant's response, with one expected reasoning shape and 1–3 plausible mental models.*
3. **Cluster labels are drafted source-first, before opening current Lane 2 outputs.** The first labeling pass reads the assistant's answer and marks reasoning clusters without consulting Lane 2 anchors. Only after the source-first pass exists do we open the current artifacts and attribute hits/misses/false positives. Otherwise the audit becomes "did Lane 2 find things similar to what Lane 2 found" — circular and useless.
4. **Human review (Marcin) owns ambiguous clusters and all `expected_primary_models` labels.** Claude drafts. Marcin owns. Especially: any cluster where multiple primary models are plausible, and any expected model not already surfaced by current Lane 2.
5. **The audit's product is a failure-owner map, not an architecture proposal.** The output is a per-cluster attribution table that says "this expected model was lost at *this* stage." The decision tree in §9 maps that table to next-track architecture work, but the memo and the audit script do not propose architecture themselves.

## 1. Purpose

Determine whether Lane 2 producer quality is limited by **fingerprint, recall, verifier, surfacing, or Step 6 consumption.**

Concretely: for every expected mental model on every reasoning cluster in the audit corpus, we want to attribute presence/absence to one of those five stages, plus a `gold_disagreement` bucket for cases where the expected label itself was wrong.

## 2. Why this, why now

The original Sully critique was that we ask one LLM call to do too much when reading a conversation. Across the last weeks of Lane 2 work, what we actually did was:

- PR #38: Lane 1 audit cleanup
- PR #39: Lane 2 attribution measurement infrastructure
- PR #40: verifier dedupe bug + candidate-conditional metric
- v1 / v2 / v3 / B verifier architectures: all gate-failed, preserved as research evidence (tag `lane2-architecture-research-2026-04-26`)
- PR #41: Step 6 wording contract — three rhetorical treatments + verbatim naming + section-shape rule

None of that touched the producer chain itself. v1–v3/B were verifier work (downstream of the producer). PR #41 was Step 6 (way downstream). We made the *consumer* of Lane 2 honest about uncertainty, but we never tested whether the *producer* preserves the right signal.

What this audit answers: when the producer chain reads a conversation, does it preserve enough reasoning structure for the right mental models to be recalled and verified — and where does it leak when it doesn't?

## 3. Producer chain map

Reference: `engine/system_b/companion_routing.py`, `engine/system_b/pipeline.py`.

```
assistant text
   │
   ▼
[fingerprint LLM call]              # companion_routing.py:212, :291
   │  produces: 3–8 abstract reasoning moves
   │  explicitly told: do not name mental models
   ▼
[deterministic keyword recall]      # companion_routing.py:703
   │  uses: assistant text + fingerprint move text
   │  produces: up to 60 candidate models
   │  embeddings: only used if keyword pass does not fill cap
   ▼
[verifier LLM call]                 # companion_routing.py:401, :589
   │  judges each candidate as executed / violated / rejected
   ▼
[surfacing / cheat-sheet selection]
   │  top-5 anchors with engagement field
   ▼
[Step 6 consumption]                # SKILL.md (PR #41 contract)
   │  primary pressure / secondary lens / set aside with a reason
```

This audit instruments every arrow. For every expected mental model on every reasoning cluster, we will record whether it survived each stage.

## 4. Corpus (7 cases, three buckets)

Buckets are **audit hypotheses**, not ground truth.

### Failure-rich (3) — already have N=3 stability runs

| Case | Anchors (current) | Step 6 cons. | Accepted-pre stability | Why this case |
|---|---|---|---|---|
| `mid-level-consultant-decides` | 5 | 20% | 0.16 | Clearest failure-rich. Dense ethical/regulatory reasoning. High signal for whether the producer chain preserves specific moves. |
| `mother-deciding-address-year` | 5 | 60% | 0.20 | Different domain (safety planning under power asymmetry). Tests whether the chain handles non-business-decision reasoning. |
| `marcus-equity` | 2 | 100% | 0.13 | High consumption, low stability. Tests whether high consumption is masking poor producer quality (Step 6 takes whatever Lane 2 hands it). |

### Candidate positive controls (2) — Lane 2 anchors look semantically right *as a hypothesis*

| Case | Anchors (current) | Status | Why this case |
|---|---|---|---|
| `third-year-phd-student` | 5 (Optionality, Premortem, Status Quo Bias, Base Rates, Problem Framing And Reframing) | **mixed-positive** (semantically plausible, but stability 0.39 is not strong) | Worth labeling clusters to test whether plausibility holds at the cluster level. |
| `user-launch-independent-fintech` | 2 (Margin Of Safety, Optimism Bias And Planning Fallacy) | cleaner positive control | Low anchor count, concrete runway/launch-plan logic, easy to confirm from clusters. |

### False-positive risk controls (2)

| Case | Anchors (current) | Why this case |
|---|---|---|
| `year-old-oncologist-accept` | 4 (Batna, Information Asymmetry, Theory Of Constraints, Decomposition) | Theory Of Constraints on a job-offer decision smells like over-recall (it's a manufacturing/throughput model). Tests whether keyword recall surfaces semantically-adjacent-but-wrong models. |
| `mid-level-consultant-report` | 3 (Power Dynamics, Probabilistic Thinking, Confidence Calibration) | Same kickoff family as `consultant-decides`, different conversation. Anchors are generic "any-career-decision" shapes. Tests whether Lane 2 surfaces specific reasoning or shape-of-discussion lexical hits. |

### Cases left out, with why

- `founder-grant-marcus-equity`, `grant-equity-partnership-status` — same kickoff family as `marcus-equity`. Useful later for "same kickoff, different evolution" analysis. Right now diversity matters more than another Marcus variant.

## 5. Gold label unit and source-first protocol

### 5.1 The unit

A **reasoning cluster** is a contiguous or near-contiguous portion of the assistant's response that performs one anchor-worthy structural move. A cluster may wrap multiple sentences or span multiple turns when they serve the same structural move (e.g., a Turn 1 question sequence and a Turn 3 "fundamentals before tactics" pushback are one cluster — refusing tactics-first framing). The cluster — not the underlying substring — is the gold-label unit.

Each cluster gets:

- `source_quotes` (one or more exact substrings from the assistant's answer that together form the cluster)
- `reasoning_shape` (one of the 11 shapes in §6.2)
- `expected_primary_models` (1 model if there is a clear one; max 2 only if the cluster genuinely contains two distinct reasoning moves; `no_clean_primary` is valid)
- `acceptable_secondary_models` (plausible related lenses, optional)
- `should_reject_models` (tempting but too broad/adjacent)

### 5.2 The source-first rule (anti-bias)

> **Read the assistant answer and mark reasoning clusters without looking at Lane 2 anchors for that run.**

For cases where Claude already remembers the anchor set from prior work, the discipline still applies: cite the cluster's source quotes first, then think about which model fits, *then* open the current Lane 2 output.

This is the single most important methodological rule in this memo. Without it, the audit answers "did Lane 2 find things similar to what Lane 2 found," which is circular.

## 6. Labeling protocol (6 steps)

### 6.1 Source-first cluster pass

Read **`conversation.txt` Turn N ASSISTANT messages only.** Mark anchor-worthy reasoning clusters with `assistant_quote` and `cluster_id`. **Do not open** `revised.txt`, `result.json`, `companion_cheat_sheet`, or any prior anchor analysis at this stage. `revised.txt` is Step 6 output and contains anchor mentions and Step-6-shaped reasoning that would leak back into gold labels — it is opened only in §6.4 attribution, when scoring Step 6 consumption.

**Anchor-worthiness rule.** A good assistant answer can contain many locally valid cognitive moves; not every one of them is anchor-worthy. The audit unit is a *load-bearing reasoning cluster that deserves a mental-model anchor*, not every reasoning sentence. If a turn contains five sentences of correct reasoning that are all serving one structural move, that's one cluster, not five. Pseudo-precision (over-splitting) biases the audit toward "Lane 2 has terrible recall" before that conclusion is earned. Right granularity for a typical case is roughly 5–8 clusters; if you find yourself at 10+, reconsider whether you're splitting on real structural shifts or on local sentence variation.

### 6.2 Shape label

Each cluster gets one broad cognitive shape:

- `tradeoff_opportunity_sizing`
- `evidence_calibration`
- `incentives_agency`
- `power_social_dynamics`
- `systems_feedback`
- `option_design`
- `framing_reframing`
- `base_rate_statistical`
- `constraint_bottleneck`
- `commitment_reversibility`
- `other`

The `other` bucket exists so we don't force-fit. If `other` shows up frequently, the taxonomy needs revision before audit work proceeds.

### 6.3 Gold model labels

For each cluster:

- `expected_primary_models` — 1 preferred model if there is a clear one. Max 2 *only* if the cluster genuinely contains two distinct reasoning moves (the "one primary per reasoning move" rule from PR #41 applies here too). **`no_clean_primary` is a valid label.** If the cluster contains real reasoning but no model in the 222 corpus fits cleanly as primary, mark it `no_clean_primary` rather than force-fitting a stretched model. We are auditing whether Lane 2 preserves load-bearing reasoning structures that *deserve* anchors — not whether every reasoning move maps to a 222 model.
- `acceptable_secondary_models` — plausible related lenses, optional.
- `should_reject_models` — tempting false-positive candidates that the audit is *expecting* the system to NOT surface.

The `should_reject_models` field is what makes the false-positive risk controls testable.

### 6.4 Now open current Lane 2 artifacts

After §6.1–§6.3 are committed for a case, open:

- `extraction.json` (fingerprint moves)
- `companion_candidates` (recall output, if persisted)
- accepted-before-cap, detected-after-cap (from stability runs for the 4 cases, single-run for the others)
- `companion_cheat_sheet.anchors[]`
- `revised.txt` (Step 6 output) — anchor mentions and treatment

### 6.5 Attribute failures

For each `expected_primary_model` and `acceptable_secondary_model`, assign one failure owner:

- `fingerprint_failed` — the cluster's source quote(s) were not extracted, or were extracted in language too generic to support recall
- `recall_failed` — the expected model was not in the candidate slate
- `verifier_failed` — the expected model was a candidate but verifier rejected it
- `surfacing_failed` — verifier accepted but the model didn't survive top-5 / cheat-sheet selection
- `step6_failed` — surfaced but Step 6 dropped or mistreated it
- `gold_disagreement` — on review, the expected label was wrong

For each *observed* anchor (current Lane 2 output) that does not match a gold cluster:

- `acceptable_secondary` — defensible but not load-bearing
- `noisy_adjacent` — keyword-adjacent, semantically wrong fit
- `false_positive` — clearly wrong

### 6.6 Ambiguity rule

Any cluster where the draft gold set has more than one plausible primary, OR where a current accepted anchor feels "not wrong but not load-bearing," gets `ambiguous=yes` and goes to Marcin for review. Marcin's call is final.

## 7. Audit table shape

### 7.1 Gold cluster rows

| Field | Meaning |
|---|---|
| `case_id` | archived case |
| `run_id` | timestamp of the archived run; for stability cases, run_1 / run_2 / run_3 |
| `cluster_id` | human-created cluster id (e.g., C1, C2, …) |
| `source_quotes` | one or more exact assistant substrings forming the cluster |
| `reasoning_shape` | one of the 11 shapes |
| `expected_primary_models` | model display_names expected as primary (verbatim); `no_clean_primary` is valid |
| `acceptable_secondary_models` | plausible but not required |
| `should_reject_models` | tempting false-positive candidates |
| `fingerprint_found_cluster` | yes / no / partial |
| `fingerprint_move_text` | matched current fingerprint move (if any) |
| `candidate_recall_hit` | did expected model reach candidates? |
| `candidate_rank` | final_rank in the candidate list, if present |
| `verifier_accepted` | yes / no |
| `surfaced_top5` | yes / no |
| `step6_treatment` | primary / secondary / set_aside / hidden / not_applicable |
| `failure_owner` | fingerprint / recall / verifier / surfacing / step6 / none / gold_disagreement |
| `ambiguous` | yes / no |
| `reviewer_notes` | Marcin's final judgment if ambiguous |

### 7.2 Observed-anchor rows (false-positive catcher)

For every current Lane 2 anchor that does NOT map cleanly to an expected_primary_model on a gold cluster:

| Field | Meaning |
|---|---|
| `case_id` | archived case |
| `run_id` | run identifier |
| `observed_model` | current Lane 2 anchor |
| `best_matching_cluster` | gold cluster_id or none |
| `classification` | acceptable_secondary / noisy_adjacent / false_positive |
| `failure_owner` | usually verifier or recall |
| `notes` | reviewer notes |

This is how false positives get caught. Without §7.2, the audit only measures recall and misses precision.

## 8. Metrics

### 8.1 Per-case + aggregate (single-run)

- `cluster_recall` — share of gold clusters that fingerprint extracted (or near-equivalent)
- `fingerprint_specificity` — share of fingerprint-extracted moves that are *specific enough* to support model recall (judged by reviewer; "weighing options" = not specific; "balancing $1.3M cost against $6M of value" = specific)
- `candidate_recall@60` — share of `expected_primary_models` + `acceptable_secondary_models` present in companion_candidates before verification
- `candidate_rank_distribution` — where in the candidate list the expected models land (top-10, top-20, tail, absent)
- `verifier_acceptance_rate` — share of expected models accepted *given that they were candidates*
- `surfacing_recall@5` — share of accepted expected models that survive top-5
- `noisy_anchor_rate` — share of observed-anchor rows classified as `noisy_adjacent` or `false_positive`
- `step6_treatment_accuracy` — share of surfaced anchors handled correctly by Step 6 (primary anchor used as primary, etc.)

### 8.2 Stability recurrence (4 N=3 cases only)

For each expected model on each gold cluster, across the 3 runs:

- candidate-list presence: 3/3, 2/3, 1/3, 0/3
- verifier acceptance: 3/3, 2/3, 1/3, 0/3
- noisy-anchor recurrence on observed-anchor rows

This is especially important for `marcus-equity`, where Step 6 consumption is high (100%) but `Accepted-pre` stability is low (0.13). The hypothesis: each run picks different anchors, all of which Step 6 happily uses. The recurrence metrics will show whether expected models are absent in many runs (producer leak) or present but inconsistently surfaced (downstream variance).

## 9. Pre-registered decision tree

The memo commits to this mapping from audit results to next-track work, *before* the audit runs. This protects against post-hoc story-fitting (the same discipline that protected Path D when v3 failed gates).

- If `cluster_recall` is weak (< threshold), **decompose fingerprint first.**
- If cluster recall is good but `candidate_recall@60` is weak, **fix recall** (shape-scoped recall, embedding recall, or substrate change).
- If candidate recall is good but `verifier_acceptance_rate` is weak, **revisit verifier** with narrower slates.
- If upstream works but `noisy_anchor_rate` is high, **fix surfacing/fan-in.**
- If upstream works and Step 6 mistreats anchors, **continue PR #41-style consumer work.**
- **If all stages are acceptable, do not redesign Lane 2 just because Sully makes decomposition feel elegant.** We are not trying to cosplay decomposition. We are trying to find the leak.

## 10. What this memo does NOT do

Explicit non-goals — the next implementation must hold to these.

- No shape-classified producer decomposition design. That's downstream of audit results.
- No candidate-cap tuning.
- No verifier resplit (v1/v2/v3/B is enough evidence; preserved at tag `lane2-architecture-research-2026-04-26`).
- No further Step 6 wording changes beyond what PR #41 already shipped.
- No LLM-only gold labeling. LLMs may *draft* candidate labels; humans own the gold set.
- No multi-LLM "consensus" labeling. Adds complexity, doesn't fix the blind-spot problem.

## 11. Pre-registered "good enough" gate

To prevent the audit from ending in "mediocre but not terrible, let's redesign anyway," pre-register what acceptable looks like.

**Threshold values are deferred to a calibration step with Marcin before the audit script runs.** This memo locks the *shape* of the gate, not the numbers. Suggested shape:

- `cluster_recall` ≥ X% — fingerprint extracts the moves we care about
- `candidate_recall@60` ≥ Y% on `expected_primary_models` — the right model reaches the verifier
- `verifier_acceptance_rate` ≥ Z% on candidates that were present — verifier doesn't reject correct candidates
- `surfacing_recall@5` ≥ W% — top-5 budget doesn't drop them
- `noisy_anchor_rate` ≤ V% — false-positive rate is bounded

If all five clear, **Lane 2 producer is acceptable** and the next track is consumer-side polish, not decomposition. If any fails, the decision tree in §9 routes to a specific next-track design.

## 12. Author-bias safeguards

I (Claude) authored PR #41 and lean toward the consumer-side narrative. Three controls:

1. **Source-first labeling** (§5.2). Spans are drafted before opening current Lane 2 outputs.
2. **Marcin owns expected_primary_models.** Especially when the expected model is NOT in the current Lane 2 output — that is the case most likely to surface a real producer leak, and the case most vulnerable to Claude's "the system was probably right" bias.
3. **Ambiguous clusters escalate.** Any cluster where Claude's draft has multiple plausible primaries goes to Marcin. The default should be "ambiguous" if there is genuine doubt, not "Claude picks a primary and moves on."
4. **Cross-labeler calibration on at least one case.** For at least one false-positive risk control case (preferably `year-old-oncologist-accept`), Marcin does the source-first cluster pass *before* Claude attribution. If Marcin's clustering and primary labels diverge meaningfully from Claude's style on the other cases, pause and recalibrate before completing the rest. This is the cheapest way to detect systematic Claude-bias in clustering or label selection without forcing Marcin to label all 7 cases.

A fifth informal control: this memo gets a once-over before audit work starts. If the framing is wrong, we want to find that out *before* gold labels are built on top of it.

## 13. Next artifact

After this memo:

1. **Calibration step** — Marcin and Claude agree on threshold values for §11.
2. **Audit artifact** — `scripts/lane2_producer_audit.py` (or a structured table doc, depending on what's faster). Output: per-case `gold_cluster_rows.csv` and `observed_anchor_rows.csv`, plus an aggregate `metrics.md`.
3. **Reading the leak map** — apply §9 decision tree to the metrics, pick the next track.

The audit artifact does not propose architecture. It only produces the leak map.

## 14. Open questions for Marcin before audit work starts

1. **Threshold values for §11.** What numbers count as "acceptable" for cluster_recall, candidate_recall@60, verifier_acceptance_rate, surfacing_recall@5, noisy_anchor_rate?
2. **Run multiplicity for non-stability cases.** The 3 new cases (`user-launch-independent-fintech`, `year-old-oncologist-accept`, `mid-level-consultant-report`) only have single-run archives. Do we re-run them N=3 to get stability data, or use single-run as the unit and accept that recurrence metrics are only available for the original 4?
3. **Reasoning shape taxonomy lock.** Is the 11-shape taxonomy (§6.2) acceptable as-is, or should it be refined before labeling starts? `other` will be a useful canary if it shows up too often.
4. **Labeling ownership cadence.** Sync as Claude finishes each case, or batch all 7 then review? My preference: case-by-case for the first 2, then assess whether batching is safe.
5. **Whether this memo gets a Codex/GPT review pass before audit work begins.** It's the spine of the next track; a second voice on the framing might be worth the cost.

## 15. Status

This memo is the next artifact after PR #41. It does not change code. It does not propose architecture. It locks the audit's framing, scope, protocol, and decision tree, so that the audit's product (the leak map) gets to drive next-track design rather than the other way around.

Open for review.
