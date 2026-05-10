# Sonnet 4.6 V60 Live Skill Run Evaluation

Date: 2026-05-10
Run ID: `20260510T203614Z`
Archived case: `solo-founder-deciding-pivot`
Archive path: `/Users/marcin/.local/share/lolla/runs/solo-founder-deciding-pivot/20260510T203614Z/`

## Executive Read

The run proves that the V60 enrichment layer is now attached to the live skill result and that embeddings are active. It does not yet prove that the orchestrating model gives V60 the full accountable consideration we designed, because Sonnet skipped the Step 6b V60 consideration ledger.

The product output improved versus the older `startup_pivot` baseline: it added denominator discipline, a hybrid/add-on path, post-commitment exit signal, cap-table risk framing, build-cost pressure, and a "why is growth flat?" diagnostic. But the live V60 selection did not reproduce the strongest prior V60 lab evidence for this case: `optionality.expand-before-evaluating` and `premortem.simulated-failure-to-plan-change` were both outside the packet cap.

So the honest conclusion is mixed:

- V60 transport: on.
- Embedding enrichment: on.
- Final product usefulness: improved.
- V60 accountability ledger: missing.
- V60 selection reliability for known best chunks: not good enough yet.

## Verified Artifacts

Runtime artifacts in `/tmp`:

- `/tmp/lolla_20260510T203614Z_conversation.txt`
- `/tmp/lolla_20260510T203614Z_extraction.json`
- `/tmp/lolla_20260510T203614Z_result.json`
- `/tmp/lolla_20260510T203614Z_revised.txt`
- `/tmp/lolla_20260510T203614Z_gapcheck.txt`
- `/tmp/lolla_20260510T203614Z_gapcheck_lanes.json`
- `/tmp/lolla_20260510T203614Z_memo.md`
- `/tmp/lolla_20260510T203614Z_memo_note.json`
- `/tmp/lolla_20260510T203614Z_subagents.json`

Missing artifact:

- `/tmp/lolla_20260510T203614Z_v60_ledger.json`

The archive result matches the `/tmp` result for the inspected fields, including `run_health`, `v60_enrichment`, and `usage_summary`. This is not an archive-loss problem. The ledger was missing before archival.

## Run Health

`run_health.overall`: `degraded`

Known issue:

- `quote_fabrication`
- `quote_fabrication_count`: 6
- The extractor dropped all six `reasoning_passages` after retry because it could not verify them as literal substrings.

This is not a new regression for this case. The older scratch baseline for `startup_pivot` also had `quote_fabrication_count: 6` and `run_health.overall: degraded`.

Important V60 fields:

- `v60_enrichment`: `active`
- `v60_selected_chunk_count`: 16
- `v60_consideration_ledger`: missing
- `v60_consideration_validation`: missing

## Cost

Total estimated cost: `$0.251466`

Breakdown:

- OpenRouter / Grok pipeline: `$0.022466`, 41 calls, 118,542 total tokens.
- OpenAI embeddings bucket: `$0.00148`, 7 calls.
- Anthropic subagents: `$0.22752`, 4 calls, 75,840 estimated tokens.

Read: V60 and embeddings are not the cost problem. The pressure-check subagents dominate cost.

## V60 Selection

Artifact:

- `model_affordances_v60`
- status: `draft_review_only`
- path: `/Users/marcin/Desktop/Apps/lolla-skill/data/compiled/model_affordances/affordances_v60.json`
- model records: 222
- affordances: 306
- absence records: 697

Selection policy:

- max cards: 8
- lane slots: 4
- embedding affordance slots: 2
- embedding absence slots: 1
- hybrid slots: 1
- snippet cap: 2

Selected cards:

1. `power-dynamics` from `lane_preserved`
2. `base-rates` from `lane_preserved`
3. `statistics-concepts` from `lane_preserved`
4. `scientific-method-evidence-testing` from `lane_preserved`
5. `switching-costs` from `embedding_model_recall`
6. `lean-startup-methodology` from `embedding_model_recall`
7. `jobs-to-be-done` from `embedding_absence_reserved`
8. `intellectual-humility` from `hybrid_rrf`

Selected chunk count: 16, one affordance plus one absence record per card.

Key skipped candidates:

- `optionality`: not presented because of packet cap.
- `premortem`: not presented because of packet cap.
- `decision-trees`: not presented because of packet cap.
- `sunk-cost-fallacy`: not presented because of packet cap.
- `representativeness-heuristic`: not presented because of packet cap.
- `falsifiability`: not presented because of packet cap.
- `lock-in`: not presented because of packet cap.

## Comparison To Older Startup Pivot Baseline

Compared file:

- `research/test-cases/phase2c-lane1-equivalence-2026-04-24/_scratch/startup_pivot_new_run0.json`

Health:

- Old: degraded, quote fabrication 6, no V60.
- New: degraded, quote fabrication 6, V60 active with 16 chunks.

Lane 1:

- Old detected one finding: `availability-misweighing-tendency`.
- New detected two findings: `availability-misweighing-tendency` and `kantian-fairness-tendency`.

Companion anchors:

- Old: `boundaries`, `theory-of-constraints`, `experimentation`.
- New: `sunk-cost-fallacy`, `representativeness-heuristic`, `scientific-method-evidence-testing`, `decision-trees`, `social-proof`.

Frame pressure:

- Old hybrid reframe: "What other strategic paths exist besides pivoting fully or pushing the current product..."
- New hybrid reframe: "What if we built the workflow tool as an add-on module to the current product instead of a full pivot?"

The new frame is more product-actionable and easier to test.

Structural coverage gaps:

- Old: `competitive-dynamics`, `resource-allocation`, `information-quality`, `risk-response`.
- New: `commitment-reversibility`, `information-quality`, `resource-allocation`, `competitive-dynamics`.

The new structural result is better aligned with the case because it spots reversibility/lock-in risk around the pivot itself.

## Comparison To Prior V60 Labs

Compared file:

- `data/evaluations/v60_transaction_replay_lab/2026-05-10-c44c-exact-chunk-private-replay-hardened-paid/outputs/startup-pivot.json`

C4.4 private trace verdict:

- packet usefulness: `useful`
- assessment count: 16
- route counts:
  - `private_reasoning`: 5
  - `guardrail`: 4
  - `evidence_gate`: 2
  - `reject_irrelevant`: 2
  - `public_delta_candidate`: 1
  - `diagnostic_question_candidate`: 1
  - `defer_missing_evidence`: 1

Selected opportunities from that lab:

- `aff::optionality.expand-before-evaluating`
  - public candidate: "Consider hybrid: test pivot while maintaining current product minimally."
- `aff::premortem.simulated-failure-to-plan-change`
  - public candidate: "What failure modes does the pivot plan have?"

Live run overlap:

- Live V60 selected models: `base-rates`, `intellectual-humility`, `jobs-to-be-done`, `lean-startup-methodology`, `power-dynamics`, `scientific-method-evidence-testing`, `statistics-concepts`, `switching-costs`.
- Prior lab models: `base-rates`, `boundaries`, `decision-trees`, `lean-startup-methodology`, `optionality`, `premortem`, `scientific-method-evidence-testing`, `statistics-concepts`.
- Common models: 4 of 8.
- Common chunks: 6 of 16.
- Prior lab opportunity chunks present live: 0 of 2.

This is the biggest selection-policy warning from the run.

## Product Output Assessment

Useful changes that made it to the user-facing memo:

- Denominator before the bar: the three customers are self-selected enthusiasts, not a representative sample.
- Hybrid/add-on path: ask whether the workflow tool could be an add-on to the current subscription rather than a standalone pivot.
- Post-commitment exit signal: define a 60-day leading indicator before green-lighting the pivot.
- Co-founder framing: not courtesy, but cap-table risk management.
- Build-cost prerequisite: estimate the time/cost of building the new product before commit-or-walk.
- Flat-growth diagnostic: identify whether flat growth is PMF failure, sales execution failure, or market ceiling.

Things that are product-risky:

- The revised answer and memo still name internal mental models publicly in the appendix and revised answer. That may be acceptable for current audit mode, but it is not ideal for the polished skill experience.
- Sonnet narrated internal orchestration steps in chat despite instructions to keep them silent.
- Step 6 did not incorporate the later pressure-check findings; the memo did, but the staged output may feel fragmented.
- Without the V60 ledger, we cannot distinguish "used V60" from "arrived at a similar idea through lane pressure."

## Architecture Assessment

What worked:

- Existing lanes still produce meaningful deterministic pressure.
- V60 attaches after the lanes as private enrichment, not as a fifth lane.
- Embeddings broaden the candidate pool cheaply.
- Telemetry captures selected V60 cards, selected chunks, skipped candidates, source counts, embedding mode, cost, and artifact custody.

What failed:

- Prompt-only ledger compliance is insufficient. Sonnet skipped Step 6b even though the instructions are present.
- Missing ledger is not currently escalated in `run_health`, so an operator might think V60 was fully considered when only transport is proven.
- The current 8-card cap plus source balancing can drop the exact chunks that prior labs found most useful.

## Recommendation Before Next Full Rerun

Do not burn another full skill run just to confirm the same failure mode.

Patch first:

1. Add a post-Step-6b/finalization validator that marks active V60 without a ledger as `v60_consideration_ledger_missing`.
2. Make the archive/finalization stage update `run_health` even if the orchestrator skips Step 6b.
3. Adjust V60 selection so Lane 3 binary-collapse/reframing candidates and prior exact embedding opportunity chunks do not get crowded out by generic lane-preserved cards.
4. Consider reducing public mental-model naming in user-facing memo output while preserving it in the audit appendix or Observatory.
5. Treat Sonnet as a compliance stress test: if Sonnet is supported, the system must not depend on Sonnet faithfully executing a long manual step.

After that, rerun the same `startup_pivot`/solo-founder pivot case once. The acceptance bar should be:

- V60 enrichment active.
- V60 ledger present and valid.
- Ledger has one transaction per selected chunk.
- Final memo preserves the useful deltas above.
- `optionality`/`premortem` or equivalent exact opportunity chunks are either selected, or explicitly skipped for a defensible reason visible in telemetry.
- User-facing prose does not leak internal orchestration.

