# Lolla Run 20260623T095719Z Post-Run Analysis

Date: 2026-06-23

Run analyzed:

- Archive: `/Users/marcin/.local/share/lolla/runs/accept-founding-engineer-role/20260623T095719Z/`
- Memo: `/tmp/lolla_20260623T095719Z_memo.md`
- Observatory during run: `http://localhost:8080`
- Case id: `accept-founding-engineer-role`
- Branch used by skill: `lolla-skill-reasoning-eval-pr`
- Purpose: analyze whether the new trace/accountability machinery captures useful reasoning evidence, silent failures, graph/lens survival, and future eval material.

## Bottom Line

This was a useful run and a good product signal, but not a full green run.

The user-facing audit improved the advice in a materially meaningful way. It moved from:

> if wife support is real and B passes tests, take B; otherwise take A

to:

> do not accept B yet; make B pass proof tests; make A pass an authority-and-scope test; if neither passes, stay only briefly with a written exit or transfer plan

That shift is exactly the product thesis: add friction to confident AI advice, surface the hidden commitment, and force reasoning to become testable before it becomes action.

However, the run also exposed a silent-degradation risk. The companion verification step produced malformed/truncated JSON after starting to return useful accepted lens detections. The parser turned that into zero accepted models, the companion card became empty, and health did not flag the companion lane as degraded. The final answer was still useful because other lanes carried the run, but one subsystem lost signal while the run still looked clean enough.

Verdict:

- Product output: useful.
- Capture and archive: good.
- Reasoning trace: materially better than before, still thin for future review.
- Graph survival artifact: strong.
- Health labeling: improved for vendor boundary, incomplete for lane-level parse failure.
- Longitudinal case matching: not good enough yet.
- Rerun status: okay to rerun for research, but do not call this fully green.

## Source Artifacts Present

The archive contains the expected durable artifacts:

- `conversation.txt`
- `extraction.json`
- `result.json`
- `revised.txt`
- `memo.md`
- `memo_note.json`
- `live_transcript.txt`
- `pre_step6_private_table.json`
- `pre_step6_private_table.md`
- `pre_step6_private_table_ledger.json`
- `v60_ledger_skeleton.json`
- `v60_ledger.json`
- `reasoning_trace.json`
- `graph_survival_report.json`
- `graph_survival_report.md`
- `gapcheck.txt`
- `gapcheck_lanes.json`

Missing expected/optional artifacts:

- `pre_step6_shadow_portfolio.json`
- `user_usefulness_review.json`
- `outcome_review.json`

The trace records those as missing artifacts, which is good. They are no longer invisible gaps.

## Capture And Extraction

Extraction status:

- `status`: `ok`
- `capture_health`: `good`
- user turns: 15
- assistant turns: 15
- char length: 15749
- last turn role: `ASSISTANT`
- decision situation: `Whether to accept a founding engineer role at a Series B startup, a staff+ role at a different FAANG, or remain in a current senior SWE position.`
- reasoning passages: 7
- live constraints: 4
- dropped threads: 1
- nested extraction: true, but the new inspection script correctly resolves it

Assessment:

The extraction is good enough for this run. It captured the decision shape, not just the final answer. The nested JSON footgun is less dangerous now because `scripts/inspect_extraction.py` reports the resolved extraction source path and counts.

Remaining issue:

The capture manifest says turn counts are good, but the trace still marks future review as thin because live output health is `not_checked` and no usefulness/outcome artifacts exist.

## Run Health

Final run health:

- `overall`: `partial`
- `capture`: `good`
- `substrate`: `ok`
- `embeddings`: `active`
- `fingerprint`: `ok`
- `findings_produced`: true
- `quote_fabrication_count`: 0
- `product_output_health`: `clean`
- `live_output_health`: `not_checked`
- `issues`: `vendor_boundary_reasoning_leak`
- `issue_axis_counts`: `{ "vendor_boundary": 1 }`
- `partial_health_causes`: `vendor_boundary_reasoning_leak`

This is a real improvement from previous behavior. Partial health is now labeled as a vendor-boundary issue rather than being conflated with capture, product, or ledger failure.

Vendor warning:

- 53 calls returned reasoning details despite reasoning being disabled.
- The affected model was `google/gemini-3.1-flash-lite-20260507`.
- The warning spans extraction, structural passes, frame passes, companion fingerprint, and other stages.

Assessment:

This is correctly separated as a vendor-boundary issue. Product output can still be evaluated as clean, but boundary-comparison and provider-compliance research should treat the run as partial.

## Silent Degradation: Companion Verification

This is the most important red-team finding.

The console showed:

```text
[companion_verification] field 'accepted': expected list[dict], got <missing> - returning []
```

The final `companion_card` in `result.json` is empty:

- detected models: 0
- expansions: 0
- failure hints: 0
- heuristic hints: 0
- premortem hints: 0
- identity chunks: 0

But the raw companion verification boundary call did contain useful data before becoming invalid JSON. It started returning accepted items including:

- `decomposition`
- `understanding-motivations`
- `constructive-feedback-models`
- `mental-simulation`
- `optionality`

Then the raw message cut off at:

```json
"rejected":
```

The parser could not parse the malformed object, returned an empty accepted list, and the run health did not flag a lane-level parse failure.

Why this matters:

This is exactly the failure mode we are trying to catch. The system looked as if the companion lane found nothing, but in reality it found useful case-specific lenses and then lost them because of malformed output. The final answer survived because Lane 1, Lane 3, V60 enrichment, and graph survival carried the run. But the trace should not let a lane silently collapse into "nothing found."

Recommended fix:

- Add a health issue such as `companion_verification_parse_failed`.
- Persist raw malformed companion verification with a parse status and salvage status.
- Distinguish `no_companion_models_found` from `companion_models_lost_to_parse_failure`.
- If the raw text contains a partial `accepted` array, attempt best-effort salvage into a low-trust artifact.
- Add a graph survival field showing `lane2_status: malformed_verification`.

## Reasoning Trace

Trace file:

- `reasoning_trace.json`
- schema: `lolla.reasoning_trace.v0.2`
- trace id: `trace_20260623T095719Z`
- raw transcript duplicated in trace: false
- local privacy mode: `local_only`
- raw transcript saved: true
- selected commitment snippets saved: true
- external egress by trace builder: false

Trace adequacy:

- `status`: `thin`
- `future_review_ready`: false
- `error_analysis_ready`: true
- missing context: `live_output_health is not_checked`
- commitment detection status: `heuristic_v0`
- candidate commitments: 12
- escalation recommended count: 12
- outcome review: not started

Assessment:

This is the right shape for the product thesis. The trace is locally replayable and useful for error analysis, but honestly says it is not yet future-review-ready. That honesty matters.

## Candidate Commitments

The new candidate commitment classification worked materially better than the earlier local runs.

Counts:

- total candidates: 12
- actor split: assistant 10, user 2
- kinds: recommendation 10, plan 1, gate 1
- impact: high 10, medium 2
- reversibility: costly_reversible 5, bounded_reversible 3, unknown 4
- evidence: evidence_missing 8, evidence_attached_or_requested 4
- correction status: observed_uncorrected_or_carried_forward 9, post_audit 3

Examples captured:

- Assistant original commitment: `If the wife conversation goes well, take B. If it doesn't, take A... Don't stay.`
- User plan: `tonight, conversation with my wife. Tomorrow, ask for extension...`
- Revised gate: `Ask for more time, run the proof test, and let B win only if the company, role, and marriage constraints all clear it.`
- Revised recommendation: `do not accept B yet.`

What worked:

- Source actor is captured.
- Human plan versus AI recommendation is separated.
- Source refs point back to `conversation.txt` or `revised.txt`.
- Claims are hashed.
- Impact, reversibility, evidence status, and correction status are present.
- Decision packet readiness is false with blockers:
  - human has not confirmed intent
  - outcome has not been reviewed

What is still weak:

- The classifier marks all 12 as escalation recommended. That may be acceptable for high-stakes career/family decisions, but we need negative controls to know whether this overfires.
- `correction_status` is useful but too coarse. For example, "wife yes is necessary but not sufficient" is a semantic correction, not merely a post-audit commitment.
- User acceptance of assumptions is not captured. The user plan is captured, but not whether the user accepted the revised framing after the audit.

## Revised Answer Quality

The revised answer became meaningfully better.

Original settled answer under pressure:

- Spouse-first.
- Diligence.
- If wife conversation goes well, take B.
- If not, take A.
- Do not stay.

Revised answer:

- Do not accept B yet.
- Ask for more time.
- Run a proof test on B:
  - weekly load and travel
  - runway and financing risk
  - CEO decision style
  - founding-level authority versus founding-level hours
- Give A a real acceptance test:
  - decision rights
  - cross-org authority
  - platform mandate
  - budget/headcount
  - credible staff-plus scope now
- Reframe C from "do not stay" to "do not stay unchanged."
- If neither A nor B passes, stay briefly only with a written transfer, sponsor, staff-scope path, or exit plan.

This is better because it turns identity pull into evidence gates. It does not deny the user's desire to build; it prevents the first startup-shaped offer from inheriting that desire without proof.

The most important correction:

> A real yes from his wife makes B permissible to investigate; it does not make B the right choice.

That is the run's best product moment.

## Graph Survival And Mental Models

Graph survival report:

- status: ready
- lane candidates: 21
- raw lane signals: 29
- embedding hits: 24
- selected V60 cards: 8
- answer-delta models: 8
- private-guardrail models: 8
- suppressed models: 29
- suppressed or unadjudicated signals: 58

Selected models:

- `premortem`
- `risk-vs-uncertainty`
- `optionality`
- `second-order-thinking`
- `inversion`
- `decomposition`
- `calculated-risk-taking`
- `regret-theory`

Selection sources:

- lane preserved: 4
- frame opportunity reserved: 2
- embedding model recall: 2

Visible effects:

- `premortem`: startup premortem before signing
- `risk-vs-uncertainty`: B becomes a conditional wager, not default
- `optionality`: A, B, and changed-C remain visible until evidence gates close
- `second-order-thinking`: check reversal thresholds before signing
- `inversion`: C is viable only if structurally changed and dated
- `decomposition`: split decision into branches instead of judging the whole vibe
- `calculated-risk-taking`: make B earn acceptance through pressure testing
- `regret-theory`: do not drift, but do not let regret bypass diligence

This is useful. These are not generic factual checks. They are reasoning-about-reasoning interventions. They changed the answer's structure from "which option feels right?" into "which option survives the right proof gates?"

## Budget-Suppressed Lenses

Suppressed models:

- `endowment-effect`
- `power-dynamics`
- `lock-in`
- `true-uncertainty-navigation`
- `opportunity-cost`
- `expected-value`
- `commitment-bias`
- `conjunction-fallacy`
- `circle-of-competence`
- `status-quo-bias`
- `switching-costs`
- `rationalization`
- `aleatory-epistemic-uncertainty-recognition`
- `sunk-cost-fallacy`
- `circle-of-control`
- `intellectual-humility`
- `cognitive-biases`
- `system-1`
- `creative-destruction`
- `natural-selection-analogy`
- `path-dependence`
- `variation-and-selection`
- `boundaries`
- `first-principles-thinking`
- `jobs-to-be-done`
- `leverage-points`
- `multi-criteria-decision-analysis`
- `step-back`
- `trade-offs`

Important observation:

The clean budget-suppressed list is present in `graph_survival_report.json` and `graph_survival_report.md`, but not as a first-class top-level list in `reasoning_trace.json`. The trace does include many rejected lenses inside `reasoning_lenses`, but consumers have to infer suppression from fields like `selected`, `surfaced`, and `rejection_reasons`.

This partially satisfies the implementation goal, but not fully.

Recommended fix:

- Add top-level `budget_suppressed_lenses` to `reasoning_trace.json`.
- Add `top_budget_suppressed_lenses` with rank, source, reason, embedding rank/score, and why it might matter.
- Link each suppressed lens to graph survival refs.
- Preserve `unselected_does_not_mean_noise: true` directly in the trace, not only graph survival.

This matters because the product thesis says unknown noise is valuable. We should not make downstream eval scripts reconstruct it from generic lens records.

## Embeddings And Selection

Embedding mode was active.

Embedding hits: 24

Top embedding hits:

- `calculated-risk-taking`, rank 1, selected
- `regret-theory`, rank 2, selected
- `optionality`, rank 3, selected through lane preservation
- `endowment-effect`, rank 4, suppressed by packet cap
- `power-dynamics`, rank 5, suppressed by packet cap
- `lock-in`, rank 6, suppressed by packet cap
- `true-uncertainty-navigation`, rank 7, suppressed by packet cap
- `opportunity-cost`, rank 8, suppressed by packet cap
- `premortem`, rank 9, selected through lane preservation
- `inversion`, rank 10, selected through frame opportunity reservation

Assessment:

This is the right research shape. Embeddings did not simply pick the final lenses; they acted as semantic recall and surfaced plausible alternatives. Two embedding-recalled lenses became answer-delta models:

- `calculated-risk-taking`
- `regret-theory`

But several high-ranking embedding hits were suppressed:

- `endowment-effect`
- `power-dynamics`
- `lock-in`
- `true-uncertainty-navigation`
- `opportunity-cost`

Those may be noise, or they may be valuable antagonist lenses. We do not know yet. The report correctly labels them as unknown, not bad.

## Activation Tiebreaker

The new tiebreaker trace worked.

`result.json` contains:

- `tiebreaker_supporting.not_attempted_reason`: `relevance_scores_present`
- `tiebreaker_risk.not_attempted_reason`: `relevance_scores_present`
- `run_health.activation_tiebreaker`: `on`

Assessment:

This is good. We can now tell that the tiebreaker did not fail silently. It was skipped because relevance scores were already present.

## Ledgers

Pre-Step-6 ledger:

- status: completed
- item count: 15
- disposition counts:
  - used: 10
  - confirming_support: 5
- unaccounted source count: 0

V60 ledger:

- status: completed
- transactions: 16
- disposition counts:
  - used: 16
- route counts:
  - updated_position: 8
  - private_guardrail: 8

Assessment:

The ledgers are strong. They show how private reasoning pressure either changed the answer or acted as a guardrail. This is one of the clearest parts of the system.

The most important ledger-backed shifts:

- Overoptimism became proof gates.
- Temporal fixation became asking for more time.
- Proxy optimization became "spouse consent and emotional fit are necessary but not sufficient."
- Premortem became startup failure simulation before signing.
- Inversion became "do not stay unchanged."
- Regret theory became "do not drift, but do not let regret bypass diligence."

## Product Output Hygiene

Product output:

- status: clean
- leak count: 0
- scanned surfaces:
  - revised_txt
  - memo_markdown
  - memo_note

Live output:

- status: not_checked
- transcript status: clean
- required: false
- capture mode: manual_unverified

Assessment:

The saved product output is clean. Live output is not verified strongly enough for future review. The trace correctly marks this as a missing context item.

Recommended fix:

- If live transcript is part of the accountability claim, make live output hygiene required or explicitly mark the run as "product artifacts clean, live narration untrusted."

## Longitudinal Case Matching

This run fragmented from the previous similar runs.

Previous related case:

- case id: `senior-software-engineer-accept`
- runs:
  - `20260622T203350Z`
  - `20260623T085537Z`

New case:

- case id: `accept-founding-engineer-role`
- run:
  - `20260623T095719Z`

The decision situations differ slightly:

- Previous: `Whether a senior software engineer should accept...`
- New: `Whether to accept...`

The archive treated this as a new case, even though it is clearly the same research scenario.

Assessment:

This is a product gap. Local archival works, but longitudinal evals can fragment due to small wording changes in extracted decision situation.

Recommended fix:

- Add user-specified `LOLLA_CASE_ID` support or a prompt-level "same case as previous" mechanism.
- Add fuzzy fingerprint matching beyond truncated normalized decision text.
- Store case aliases.
- Add a case merge command for local research.
- Include `possible_related_cases` in archive output when fingerprints are close.

## Comparison With Prior Run 20260623T085537Z

Prior selected models:

- `premortem`
- `risk-vs-uncertainty`
- `aleatory-epistemic-uncertainty-recognition`
- `understanding-motivations`
- `optionality`
- `inversion`
- `calculated-risk-taking`
- `regret-theory`

Current selected models:

- `premortem`
- `risk-vs-uncertainty`
- `optionality`
- `second-order-thinking`
- `inversion`
- `decomposition`
- `calculated-risk-taking`
- `regret-theory`

Changed:

- Dropped: `understanding-motivations`, `aleatory-epistemic-uncertainty-recognition`
- Added: `second-order-thinking`, `decomposition`

Interpretation:

The current run became less focused on why B emotionally pulls the user and more focused on proof branches, downstream consequences, and decision gates. That matches the revised answer. This is a good sign that the graph/lens layer is not just decorating the answer; it is changing the shape of the reasoning.

Caveat:

Because companion verification malformed, some of the dropped companion signals may not be true rejections. In fact, raw malformed companion output had already accepted `understanding-motivations`, `decomposition`, `mental-simulation`, and `optionality` before truncation. Therefore, this run's lane comparison is useful but not fully reliable.

## What The System Found Beyond Prompting

The system did more than ask an LLM to "red team this."

It found a specific reasoning failure:

- The original advice treated spouse consent and identity fit as if they were enough to make B the natural answer.

It forced a better decision grammar:

- necessary versus sufficient conditions
- risk versus uncertainty
- option preservation before commitment
- premortem before acceptance
- reversal thresholds
- role-specific proof gates
- temporary stay as a changed plan, not default drift

It also preserved antagonist lenses that did not make it into the answer. That is important because the goal is not only to make one run better. The goal is to build a local eval corpus that can later answer:

- Which lenses are repeatedly selected?
- Which suppressed lenses later prove useful?
- Which lenses overfire?
- Which lanes fail silently?
- Which recommendations change after graph pressure?
- Which changes users find useful?
- Which changes correlate with better outcomes?

This run contributes to that future corpus, but only if we fix lane-level failure labeling and collect usefulness/outcome feedback.

## What We Are Still Missing

High priority:

- User usefulness rating after the run.
- Later outcome review.
- Full live transcript trust, not just artifact trust.
- Case continuity across semantically identical reruns.
- Companion verification parse-failure health.
- Top-level budget-suppressed lenses in `reasoning_trace.json`.
- Forced-lens replay for suppressed models.
- Prompt-only baseline comparison.
- Negative controls on non-strategic conversations.

Medium priority:

- Better semantic correction detection for "necessary but not sufficient."
- Better distinction between direct recommendation, conditional recommendation, user plan, and acceptance of assumption.
- Quality scoring for each lane, not just whole-run health.
- Salvage path for malformed model JSON.
- Better usage/cost telemetry when a boundary call has raw content but zero tokens.

Lower priority:

- Nicer display of graph survival in Observatory.
- Human-readable diff of original advice versus revised advice.
- More explicit trace adequacy checklist in memo or receipt.

## Recommended Next Fixes

1. Add companion lane parse-failure health.

The system should not let malformed verifier output collapse into "no companion models found."

2. Add top-level budget-suppressed lens lists to `reasoning_trace.json`.

Graph survival has the clean view; trace consumers need it too.

3. Add case aliasing or case merge support.

This same fixture split into a new case folder. That will poison longitudinal evals.

4. Add first-class user usefulness collection.

The trace already has `user_usefulness_review`, but status is `not_collected`. We need a simple post-run local artifact.

5. Add later outcome review scaffolding.

The trace already has `outcome_review_state`, but status is `not_started`.

6. Add forced-lens replay for top suppressed models.

Especially test:

- `lock-in`
- `power-dynamics`
- `opportunity-cost`
- `true-uncertainty-navigation`
- `status-quo-bias`
- `commitment-bias`

7. Add prompt-only baseline comparison.

We need to know what the graph/lens system changes versus an LLM red-team prompt alone.

## Rerun Guidance

Green light to rerun for research: yes.

But do not treat the next rerun as validation until these are checked:

- Does companion verification parse cleanly?
- If it malforms, does run health show a companion lane issue?
- Does `reasoning_trace.json` expose suppressed lenses directly enough for downstream analysis?
- Does the archive attach this scenario to the existing case or show a related-case warning?
- Does the user provide a usefulness rating after reviewing the output?

Best next test:

Run the same fixture once more after fixing companion parse-failure health and trace-level suppressed lens exposure. Then compare:

- revised answer delta
- selected V60 cards
- suppressed top lenses
- commitment candidates
- case matching
- health issue axes
- user usefulness rating
