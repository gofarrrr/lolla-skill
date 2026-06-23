# Lolla System 2 Red-Team Readiness

**Date:** 2026-06-23  
**Branch:** `feat/reasoning-trace-eval-substrate`  
**Purpose:** Decide what the next rerun can prove, what it cannot prove, and what silent failures we must guard against before treating Lolla as a reasoning-trace/eval substrate.

## Verdict

Lolla is already useful as a reasoning-friction system. The previous career-decision runs show the core product promise: the system made the assistant revise from a smooth, identity-fluent recommendation into a more gated, reversible, family-aware decision process.

But the current system is not yet decision-grade as a trace/eval layer. It is ready for another instrumented rerun, not ready for strong claims like "we captured everything needed for accountable AI-assisted decisions."

The key distinction:

- **Green for:** collection-quality smoke test, graph-survival test, reasoning-trace archive test, artifact-custody test.
- **Not green for:** proving outcome quality, proving complete live-output capture, proving tool/action provenance, proving that selected mental models caused the final answer to improve.

## What Prior Runs Actually Show

I inspected 49 archived runs under `~/.local/share/lolla/runs`.

Archive coverage:

- `result.json`: 49/49
- `extraction.json`: 49/49
- `memo.md`: 49/49
- `conversation.txt`: 48/49
- `revised.txt`: 48/49
- `gapcheck.txt` and `gapcheck_lanes.json`: 48/49
- `live_transcript.txt`: 25/49
- `pre_step6_private_table_ledger.json`: 24/49
- `v60_ledger.json`: 27/49
- `reasoning_trace.json`: 1/49
- `graph_survival_report.json`: 0/49, because this was added after those runs

Health distribution:

- `healthy`: 18
- `partial`: 12
- `degraded`: 19

Useful but important caveat: older archives are not uniform evidence. They were produced across slightly different skill versions. For example, the later June 22 run has stronger pre-Step-6 source provenance than the earlier June 22 run.

## What The Two June 22 Runs Found

### Run 1

Path:

`/Users/marcin/.local/share/lolla/runs/user-accept-founding-engineer/20260622T195723Z`

Health:

- `overall`: partial
- capture: good
- embeddings: active
- V60: active
- pressure check: `not_run_default_off`
- live output: `not_checked`

Substantive value:

- The original answer was too quick to treat A as mostly delay and B as higher-information value.
- The audit forced a better comparator: A as a paid diagnostic if it has real scope.
- The final answer became more reversible, more family-aware, and more honest about what the year of dissatisfaction could and could not prove.

Generated with current code on a temp copy:

- graph lane candidates: 31
- raw lane signals: 41
- embedding hits: 24
- selected V60 cards: 8
- answer-delta models: 8
- private-guardrail models: 5
- suppressed models: 41
- suppressed/unadjudicated signals: 82
- candidate commitments: 12, all escalation-recommended as candidates

Important caveat:

The run is not future-review ready because live output is manual/untrusted. It is a good reasoning artifact, not a fully trusted product trace.

### Run 2

Path:

`/Users/marcin/.local/share/lolla/runs/senior-software-engineer-accept/20260622T203350Z`

Health:

- `overall`: degraded
- capture: good
- embeddings: active
- V60: active
- pressure check: `not_run_default_off`
- live output: unsafe because one internal term appeared in live narration

Substantive value:

- The original answer over-converted "wife yes" into "take B."
- The audit corrected the gate structure: spouse yes is necessary, not sufficient.
- The revised answer introduced evidence gates, stop-loss/reversal triggers, a family trade-off ledger, story-based diligence, and A as a deliberate diagnostic option.

Generated with current code on a temp copy:

- graph lane candidates: 27
- raw lane signals: 35
- embedding hits: 24
- selected V60 cards: 8
- answer-delta models: 10
- private-guardrail models: 6
- suppressed models: 36
- suppressed/unadjudicated signals: 72
- candidate commitments: 12, all escalation-recommended as candidates

Important caveat:

The run is degraded and the saved revised answer did not fully appear in the live transcript. The trace correctly reports `surface_divergence: diverged` when regenerated with current code.

## The System 2 Value Is Real

The strongest evidence that Lolla is more than prompting is not that it "red-teamed" the answer. A normal LLM prompt can do that.

The stronger evidence is that it created pressure from structured routes:

- Lane 1 detected reasoning tendencies and routed them through corrective mental models.
- Lane 2 reverse-engineered mental-model anchors from the assistant's reasoning.
- Lane 3 challenged the user-introduced frame.
- Lane 4 checked missing structural territory.
- V60 added source-backed affordances and absences.
- The pre-Step-6 table forced the reviser to account for what was used, rejected, guarded, or set aside.
- The graph-survival report now preserves selected and suppressed signals without pretending the suppressed ones are noise.

In the June 22 case, that produced concrete nontrivial shifts:

- "B if spouse agrees" became "B only if spouse, company, role, household, and reversal gates clear."
- "A is delay" became "A may be a paid diagnostic with lower volatility."
- "We can afford it" became "what family trade-offs are being bought with money, evenings, stress, and optionality?"
- "Diligence" became story-based questions about CEO behavior, boundary behavior, and missed-deadline behavior.

That is the System 2 thesis in practice: not a better first answer, but a second process that forces the answer through lenses it did not naturally choose.

## Where We Can Fool Ourselves

### 1. A Trace Can Exist Without Being Decision-Grade

`reasoning_trace.json` is a custody manifest, not proof that all relevant reasoning was captured.

Current adequacy can say `thin` for good reasons:

- degraded run health,
- unsafe or untrusted live output,
- missing core artifacts,
- no reasoning lens route data,
- no complete trusted live transcript.

For the next rerun, "trace exists" is not enough. We need the trace adequacy status and missing-context list.

### 2. Default-Off Pressure Check Can Look Like A Check

`gap_check` is intentionally written even when Step 7 did not run.

Default state:

```json
{
  "status": "not_run_default_off",
  "reason": "post_step6_pressure_check_default_off",
  "lanes": []
}
```

This is honest, but easy to misread. It proves the state was recorded, not that an independent post-Step-6 pressure check happened.

Two archived runs were marked `healthy` while also having:

- `gap_check.status = not_run_default_off`
- `live_output_health = not_checked`

That means `healthy` currently means "pipeline-compatible," not "fully evaluated reasoning trace."

### 3. Graph Survival Measures Ledger Uptake, Not Causal Impact

The new graph-survival report is important, but it mostly joins:

- lane candidates,
- embedding recalls,
- selected V60 cards,
- skipped candidates,
- V60 ledger transactions,
- pre-Step-6 ledger dispositions.

When it says `answer_delta_model_count`, it is measuring visible-effect claims in ledgers, not an independent diff proving that the model caused the final answer to change.

This is still useful. It is not yet causal evidence.

### 4. Ledgers Are Authored By The Same Reviser

The Step 6 output and the Step 6 ledgers are produced by the same orchestrating model. Validation checks shape, required fields, and trace references. It does not prove semantic honesty.

So the ledgers are custody and self-accounting, not independent verification.

This is acceptable if we name it. It becomes dangerous if we call it eval proof.

### 5. Commitment Detection Is Useful But Over-Inclusive

Current `CommitmentCandidate` detection is heuristic.

On regenerated June 22 traces it found 12 candidates per run, including real action advice, but also some explanatory statements that are not true commitments.

This is acceptable at the candidate layer. It must not escalate automatically into `DecisionPacket` without stricter classification.

### 6. Tool And Artifact Provenance Is Missing

The skill capture currently says to omit tool calls, tool results, system messages, and file contents from `conversation.txt`.

That is reasonable for a conversational audit, but it is a major gap for the product thesis.

For AI-assisted engineering work, the decision often depends on:

- shell commands,
- test outputs,
- diffs,
- file contents,
- search results,
- browser evidence,
- GitHub state,
- CI status,
- tool actions the agent can actually execute.

If these are omitted entirely, Lolla can audit the prose but cannot reconstruct the work reasoning.

Needed later: tool/artifact manifests with hashes, paths, command summaries, exit codes, changed-file refs, and privacy-safe snippets. Not raw everything by default, but enough provenance to replay why a recommendation became credible.

### 7. Activation Tiebreaker Is "On" But Often Not Actually In Play

All 49 archived runs report activation tiebreaker as on.

But I inspected 300 tiebreaker trace records and found:

- attempted: 0
- fired: 0
- abort reason: blank

The code explains why: the tiebreaker only runs when `relevance_scores is None`; with embeddings active, Lane 1 neighbor routing gets relevance scores, so the tiebreaker is bypassed. The default trace is then an empty `TiebreakerTrace`.

This is a silent observability weakness. The system is not lying about selected models, but it is not explaining why the advertised activation-match gate did not participate.

Recommended fix: record a non-attempt reason such as `relevance_scores_present`, `missing_reasoning_context`, or `missing_embeddings_db_path` whenever the outer gate prevents `_activation_retie_if_near_tie` from running.

### 8. Companion Omissions Are Visible But Noisy

27/49 archived runs had `companion_verification_silently_omitted` entries, totaling 1,233 omitted candidates.

This is good because silent omission is no longer hidden.

But it also means Lane 2's candidate verifier is not a precise adjudicator. The product contract should continue to treat Lane 2 as a lens generator, not a verdict engine.

### 9. Embedding Scores Are Retrieval Signals, Not Relevance Truth

The June 22 embedding recalls were useful:

- calculated-risk-taking,
- regret-theory,
- optionality,
- risk-vs-uncertainty,
- status-quo-bias,
- lock-in,
- switching-costs,
- power-dynamics,
- expected-value.

But the scores are low and relative. They should be preserved as rank/recall evidence, not interpreted as probability that a model applies.

### 10. Outcome Review Is Still Empty

The PRD's real eval loop requires later outcome labels:

- good decision,
- bad decision,
- false alarm,
- missed risk,
- policy too strict,
- policy too weak,
- outcome unknown.

Current traces have empty `outcome_reviews`. That is expected, but it means we cannot yet know which warnings were useful, which were noise, or which suppressed lenses would have mattered later.

## What We Are Not Gathering Yet

High-priority missing data:

- complete trusted live transcript,
- tool call and tool result manifests,
- code/file/artifact hashes tied to reasoning claims,
- factual verification status for important claims,
- owner and approver identity,
- action capability and impact classification,
- reversibility/rollback classification,
- explicit assumptions accepted by the user,
- evidence attachments and missing-evidence list,
- alternatives considered and alternatives suppressed,
- which lens was selected because of deterministic routing versus embedding recall versus Step 6 judgment,
- independent check of whether final answer actually changed,
- user usefulness rating immediately after the run,
- later outcome review,
- forced-lens replay results,
- baseline comparison against ordinary prompt-only red team,
- negative controls on low-stakes/non-strategic conversations,
- model/version/config fingerprints for every semantic call,
- retention and deletion events.

## What We Are Not Evaluating Yet

We do not yet evaluate:

- whether a selected mental model was actually helpful to the user,
- whether a suppressed model would have changed the user's view,
- whether the answer got better or merely more process-heavy,
- whether friction was worth the cognitive cost,
- whether the same case rerun is stable enough,
- whether the system over-favors familiar decision vocabulary,
- whether graph choices are outperforming direct LLM prompting,
- whether V60 absences prevent misuse or merely make Step 6 conservative,
- whether "private guardrail" effects are real in final prose,
- whether `healthy` should require trusted live output in research mode,
- whether the product creates surveillance/process-theater feelings.

## Recommended Next Rerun Conditions

The next rerun should be treated as an instrumented smoke test of the new trace/graph-survival layer.

Minimum pass conditions:

- Archive writes `graph_survival_report.json`.
- Archive writes `graph_survival_report.md`.
- Archive writes `reasoning_trace.json`.
- `reasoning_trace.process.graph_survival.status == "ready"`.
- `reasoning_trace.trace_adequacy.status` is inspected, not assumed.
- `candidate_commitments` are present and manually sampled for false positives.
- `surface_divergence.status` is inspected.
- `v60_consideration_validation.status == "valid"` when V60 is active.
- `pre_step6_private_table_ledger_validation.status == "valid"` when table is ready.
- `gap_check.status` is explicitly read as either actual optional pressure-check or `not_run_default_off`.
- `run_health.live_output_health` is read; `not_checked` is not treated as clean.
- suppressed models and embedding hits are preserved and inspected.

Research-mode stricter pass conditions:

- Run `finalize_live_output_hygiene.py` with `--require-live-output-clean` only if a trusted complete transcript is available.
- If trusted live transcript is not available, call the run "trace-thin" even if archive succeeds.
- Force-review at least one suppressed/high-rank lens manually after the run.
- Compare revised answer against original answer for concrete deltas, not just ledger claims.
- Record one human usefulness note: "what changed in my view, if anything?"

## Recommended Fixes Before Treating Runs As Evidence

P0 before strong claims:

1. Add explicit tiebreaker outer-gate non-attempt reasons.
2. Add a post-archive validator that prints a single readiness table for the latest run.
3. Make `healthy` versus `decision_grade` separate concepts.
4. Add graph survival presence to trace adequacy.
5. Add a trusted/live capture path or keep all runs with manual transcript as trace-thin.

P1 for the product thesis:

1. Add tool/artifact manifest capture.
2. Add stronger CommitmentCandidate classifier with candidate type, impact, reversibility, and action capability.
3. Add DecisionPacket v0 for manually escalated candidates.
4. Add OutcomeReview v0 and a local review command.
5. Add forced-lens replay: pick a suppressed model and ask the reviser to answer strictly through that lens.
6. Add prompt-only red-team baseline so we can measure what the deterministic substrate adds beyond prompting.

P2 for eval maturity:

1. Stability harness over same case across model versions.
2. Negative controls.
3. User usefulness labels.
4. Outcome-linked private eval dataset export.
5. Lens-specific utility metrics: selected, rejected, private guardrail, forced-use changed answer, forced-use changed user view, later outcome relevance.

## Red-Team Conclusion

The idea is strong, and the June 22 case is a good example of why. A normal LLM answer converged on a smooth recommendation. Lolla made the recommendation pass through structured opposition: trade-offs, premortem, status quo, optionality, spouse/stakeholder alignment, reversibility, risk versus uncertainty, and suppressed alternatives.

That is not just "better prompting." It is a process layer that preserves why a second-pass answer changed.

The main risk now is overclaiming. The system is beginning to gather the right material, but some of the most important evidence is still self-reported, default-off, manually captured, or absent. The next rerun should be used to verify the new archive artifacts and inspect their failure modes, not to declare that the full trace-layer product is done.

