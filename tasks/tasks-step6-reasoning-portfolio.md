# Step 6 Reasoning Portfolio Layer

> Source PRD: `plans/lolla-solver-control-layer-prd-2026-05-19.md`
> Goal: build a local, research-only Step 6 reasoning-portfolio experiment
> using vertical red-green-refactor slices. Do not change `main` or default
> `/lolla` behavior unless the experiment earns promotion.

## Relevant Files

- `plans/lolla-solver-control-layer-prd-2026-05-19.md` - Source PRD for the reasoning-portfolio layer, schemas, constraints, and evaluation posture.
- `tasks/tasks-step6-reasoning-portfolio.md` - Implementation task list for the local experiment.
- `research/pre-step6-reasoning-portfolio-contract-2026-05-20.md` - New research contract defining schemas, caps, protected slots, local-only policy, and promotion gates.
- `research/pre-step6-autoresearch-program-2026-05-20.md` - Research operating program for iterating on the portfolio layer with fixed case-suite evaluation and keep/retest/discard decisions.
- `research/pre-step6-autoresearch-ledger-2026-05-20.tsv` - Autoresearch ledger recording fixed-suite hypotheses, outcomes, and next-step decisions.
- `scripts/research/pre_step6_problem_states.py` - New research-only validator/CLI for `problem_state.v1` fixtures.
- `tests/test_pre_step6_problem_states.py` - Behavior tests for `problem_state.v1` validation and fixture coverage.
- `research/pre-step6-problem-states/*.problem-state.v1.json` - New static fixtures for problem-state cases.
- `scripts/research/pre_step6_build_candidate_inventory.py` - New research-only builder/validator for candidate inventories from existing result, raw, hybrid, and pressure-card artifacts.
- `tests/test_pre_step6_candidate_inventory.py` - Behavior tests proving the candidate inventory preserves existing engineered artifacts and source refs.
- `research/pre-step6-candidate-inventories/*.candidate-inventory.v1.json` - New static candidate-inventory fixtures for replay and comparison.
- `scripts/research/pre_step6_reasoning_affordances.py` - New research-only validator/renderer/baseline transformer for `reasoning_affordance.v1`.
- `tests/test_pre_step6_reasoning_affordances.py` - Behavior tests for affordance validation, forbidden language, protected slots, and deterministic baseline conversion.
- `research/pre-step6-reasoning-affordances/*.reasoning-affordance.v1.json` - New static fixtures for per-candidate affordance records.
- `scripts/research/pre_step6_attention_maps.py` - New research-only validator/renderer for `step6_attention_map.v1`.
- `tests/test_pre_step6_attention_maps.py` - Behavior tests for attention-map validation, edge reserve preservation, parked refs, and render caps.
- `scripts/research/pre_step6_build_attention_map.py` - New research-only assembler that builds an attention map from problem state, candidate inventory, and affordance records.
- `research/pre-step6-attention-maps/*.step6-attention-map.v1.json` - New static fixtures for Step 6 attention maps.
- `scripts/research/pre_step6_portfolio_comparisons.py` - New research-only comparison helper for raw, hybrid, monolithic, and portfolio modes if the experiment needs a repeatable score/readout artifact.
- `tests/test_pre_step6_portfolio_comparisons.py` - Behavior tests for comparison payload validation if a comparison helper is added.
- `research/pre-step6-portfolio-comparisons/*.portfolio-comparison.v1.json` - New comparison fixtures measuring bloat, preservation, pruning, and answer-usefulness judgments.
- `research/pre-step6-raw-artifact-fixtures/*.raw-artifact-handoff.v1.json` - Existing raw handoff fixtures used as baseline inputs.
- `research/pre-step6-hybrid-handoff-fixtures/*.hybrid-handoff.v1.json` - Existing hybrid handoff fixtures used as baseline inputs.
- `research/pre-step6-pressure-card-fixtures/*.pressure-card.v1.json` - Existing pressure-card fixtures used as compact-card baseline inputs.
- `research/pre-step6-comparison-fixtures/*.md` - Existing conversation fixtures used for replay-style comparison.
- `research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24/marcus_new_path_result.json` - Existing high-clutter result fixture that exercises current engineered artifact shapes.
- `research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24/marcus_fresh_extraction.json` - Existing extraction fixture for the Marcus comparison case.
- `research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24/lolla_20260422T155622Z_conversation.txt` - Existing conversation fixture for the Marcus comparison case.
- `scripts/research/pre_step6_raw_artifacts.py` - Existing raw artifact validator/renderer to preserve compatibility with prior experiments.
- `scripts/research/pre_step6_hybrid_handoffs.py` - Existing hybrid handoff validator/renderer to preserve compatibility with prior experiments.
- `scripts/research/pre_step6_pressure_card_consumption.py` - Existing pressure-card consumption harness for baseline comparison.
- `scripts/research/pre_step6_semi_blind_comparisons.py` - Existing comparison harness that may inform portfolio comparison structure.
- `scripts/research/pre_step6_lens_probes.py` - New research-only validator for private cognitive lens probes such as Bevelin v0.
- `tests/test_pre_step6_lens_probes.py` - Behavior tests for lens-probe validation, forbidden advice language, source hooks, risks, and fixed-suite fixtures.
- `research/pre-step6-lens-probes/*.bevelin-lens-probe.v1.json` - Static Bevelin v0 fixtures for founder, PhD v2, consultant, and mother.
- `scripts/research/pre_step6_lens_answer_cores.py` - New research-only validator for lens-enhanced answer cores, including public hygiene and source hash checks.
- `tests/test_pre_step6_lens_answer_cores.py` - Behavior tests for Bevelin answer-core fixture validation.
- `research/pre-step6-lens-answer-cores/*.bevelin-answer-core.v1.json` - Static Bevelin-enhanced answer cores for the fixed suite.
- `scripts/research/pre_step6_lens_comparisons.py` - New research-only comparison gate for rendered-hybrid, base-portfolio, and lens-enhanced answers.
- `tests/test_pre_step6_lens_comparisons.py` - Behavior tests for Bevelin comparison scoring and promotion reads.
- `research/pre-step6-lens-comparisons/*.bevelin-comparison.v1.json` - Comparison fixtures showing when the lens improves, stands down, or needs retest.
- `scripts/research/pre_step6_lens_step6_replays.py` - New research-only replay validator for lens-enhanced Step 6 answers with explicit cognitive-gate records.
- `tests/test_pre_step6_lens_step6_replays.py` - Behavior tests proving Bevelin replay fixtures validate, keep the gate cognitive, and block runtime promotion.
- `research/pre-step6-lens-step6-replays/*.bevelin-lens-step6-replay.v1.json` - Static replay fixtures comparing Bevelin-positive answers to prior portfolio replays.
- `tests/test_pre_step6_polya_lens.py` - Behavior tests proving Polya probe, answer-core, and comparison fixtures validate through the same lens-pack interface.
- `research/pre-step6-lens-probes/*.polya-lens-probe.v1.json` - Static Polya v0 problem-shape lens probes for the fixed suite.
- `research/pre-step6-lens-answer-cores/*.polya-answer-core.v1.json` - Static Polya v0 answer cores for the fixed suite.
- `research/pre-step6-lens-comparisons/*.polya-comparison.v1.json` - Polya comparison fixtures showing generalization and stand-down behavior.
- `scripts/research/pre_step6_cognitive_gate_live.py` - Research-only live cognitive comparison gate for blinded answer-core candidates.
- `tests/test_pre_step6_cognitive_gate_live.py` - Behavior tests for gate packet blinding, prompt semantics, and judgment-payload validation.
- `research/pre-step6-cognitive-gate-judgments*/` - Live answer-core gate artifacts comparing rendered, portfolio, Bevelin, and Polya candidates.
- `scripts/research/pre_step6_context_composition_gate.py` - Research-only live context-composition gate comparing rendered-only against rendered plus protected receipts.
- `tests/test_pre_step6_context_composition_gate.py` - Behavior tests for private context packet composition, blinding, complexity-tax prompt semantics, and judgment validation.
- `research/pre-step6-context-composition-gate-judgments*/` - Live context-composition artifacts from no-tax, complexity-tax, and cross-model runs.
- `scripts/research/pre_step6_step6_card_deck.py` - Research-only builder/renderer for the broad private Step 6 card deck: clean hybrid anchor, Bevelin card, Polya card, problem read, source refs, and deterministic-limit statement.
- `tests/test_pre_step6_step6_card_deck.py` - Behavior tests proving the card deck preserves all three cards, problem context, source refs, and non-cognitive deterministic limits.
- `research/pre-step6-step6-card-decks/*.step6-card-deck.v1.json` - Generated four-case card-deck artifacts.
- `scripts/research/pre_step6_card_deck_replays.py` - Research-only live Step 6 replay harness that passes the full card deck and records Step 6's private card consideration ledger.
- `tests/test_pre_step6_card_deck_replays.py` - Behavior tests for full-card prompt composition, public hygiene, ledger coverage, and no runtime promotion.
- `research/pre-step6-card-deck-replays/*.card-deck-replay.v1.json` - Live Step 6 replay artifacts for the four-case suite.
- `scripts/research/pre_step6_card_deck_replay_comparisons.py` - Research-only blinded comparison gate for clean hybrid answers versus card-deck Step 6 replays.
- `tests/test_pre_step6_card_deck_replay_comparisons.py` - Behavior tests for reviewer blinding, deterministic deck-effect bookkeeping, and inconsistent judgment rejection.
- `research/pre-step6-card-deck-replay-comparisons/*.card-deck-replay-comparison.v1.json` - Live comparison artifacts from the corrected four-case card-deck replay suite.
- `research/pre-step6-card-deck-replay-comparisons-stability-gemini/*.card-deck-replay-comparison.v1.json` - Cross-model comparison artifacts for checking whether the card-deck result survives a second reviewer.
- `scripts/research/pre_step6_card_deck_visibility_policy.py` - Research-only policy artifact that records ledger-based anchor stand-down eligibility plus cognitive confirmation without letting code judge answer quality.
- `tests/test_pre_step6_card_deck_visibility_policy.py` - Behavior tests for mother-style anchor stand-down and founder-style card-deck visibility.
- `research/pre-step6-card-deck-visibility-policies/*.card-deck-visibility-policy.v1.json` - Generated four-case visibility policy artifacts.
- `research/pre-step6-design-preamble-autoresearch-track-2026-05-20.md` - Research-only design-preamble track converting the red-team preconditions into falsifiable autoresearch slices.
- `scripts/research/pre_step6_design_preamble_cost_cache.py` - Research-only cost/cache contract for compiled card-deck keys and mode-specific cache miss behavior.
- `tests/test_pre_step6_design_preamble_cost_cache.py` - Behavior tests proving runtime cached-only misses stand down without live generation and V60 hashes affect compiled keys.
- `research/pre-step6-design-preamble-cost-cache/*.cost-cache.v1.json` - Generated fixed-suite cost/cache artifacts for `runtime_cached_only` misses.
- `scripts/research/pre_step6_private_reasoning_cards.py` - Research-only generic private-card interface validator/adaptor for current and future cards.
- `tests/test_pre_step6_private_reasoning_cards.py` - Behavior tests proving clean-hybrid, Bevelin, Polya, and a synthetic future card validate through the same private-card schema.
- `research/pre-step6-private-reasoning-cards/*.private-reasoning-cards.v1.json` - Generated fixed-suite generic private-card interface artifacts.
- `scripts/research/pre_step6_private_consideration_ledger.py` - Research-only unified private-consideration ledger overlap fixture builder.
- `tests/test_pre_step6_private_consideration_ledger.py` - Behavior tests proving hot-context dedupe can preserve card and V60-style source custody.
- `research/pre-step6-private-consideration-ledgers/*.ledger-overlap.v1.json` - Generated ledger-overlap fixture for the founder case.
- `scripts/research/pre_step6_payload_omission_gate.py` - Research-only protected-payload omission gate comparing anchor and deck answers with mechanistic category detectors.
- `tests/test_pre_step6_payload_omission_gate.py` - Behavior tests proving omission checks are per-category, diff-based, and not visibility selectors.
- `research/pre-step6-payload-omission-gates/*.payload-omission.v1.json` - Generated fixed-suite payload-omission artifacts.
- `scripts/research/pre_step6_visibility_asymmetry_policy.py` - Research-only policy contract naming runtime anchor bias, deck-private default, bounded retest behavior, and second-reviewer threshold.
- `tests/test_pre_step6_visibility_asymmetry_policy.py` - Behavior tests proving runtime has no reviewer loop and research/experimental tie or disagreement cases retest at most once.
- `research/pre-step6-visibility-asymmetry-policies/*.visibility-asymmetry.v1.json` - Generated visibility-asymmetry policy fixtures.
- `scripts/research/pre_step6_calibration_floor_manifest.py` - Research-only calibration-floor manifest that records the four-case suite as seed evidence and names missing promotion coverage.
- `tests/test_pre_step6_calibration_floor_manifest.py` - Behavior tests proving the seed suite blocks promotion and tracks false-standdown recall requirements.
- `research/pre-step6-calibration-floor/*.calibration-floor.v1.json` - Generated calibration-floor manifest fixture.
- `scripts/research/pre_step6_calibration_corpus.py` - Research-only calibration corpus builder, Step 6 sampler, stability aggregator, and validator.
- `tests/test_pre_step6_calibration_corpus.py` - Behavior tests proving corpus-floor coverage, V60-pair labeling, broad private prompt surface, answer-delta vocabulary, and stability aggregation.
- `research/pre-step6-calibration-corpus/*.json` - Calibration corpus contract, Step 6 sample artifacts, and aggregate stability result.
- `research/pre-step6-calibration-corpus-step6-readout-2026-05-21.md` - Readout recording the n=3 Step 6 stability result and reviewer-phase blocker.
- `research/pre-step6-calibration-corpus-repeat-unstable/` - Same-prompt repeat samples and stability review for the seven unstable calibration cases.
- `research/pre-step6-calibration-corpus-repeat-unstable-readout-2026-05-21.md` - Readout recording the repeat result and reframe-only diagnostic recommendation.
- `scripts/research/pre_step6_reframe_diagnostic_review.py` - Research-only reviewer diagnostic over saved Step 6 samples to test whether reframe-only outputs are useful or correctly suppressed.
- `tests/test_pre_step6_reframe_diagnostic_review.py` - Behavior tests for diagnostic contract selection, blind packet custody, and two-family result aggregation.
- `research/pre-step6-reframe-diagnostic-review/` - Contract, reviewer judgments, aggregate result, and readout for the reframe-only diagnostic.
- `research/pre-step6-reframe-diagnostic-review-readout-2026-05-21.md` - Readout recording that answer-delta vocabulary design review is required.
- `research/pre-step6-answer-delta-structural-delta-design/` - Structural-delta vocabulary repair artifacts, live diagnostic samples, aggregate result, and stability review.
- `research/pre-step6-answer-delta-structural-delta-design-readout-2026-05-21.md` - Readout recording the structural-delta repair, specificity bar, live diagnostic result, and remaining calibration limits.
- `research/pre-step6-calibration-corpus-kimi-structural-delta/` - Repaired Kimi calibration corpus artifacts, including 63 saved Step 6 samples, aggregate result, and stability review.
- `research/pre-step6-calibration-corpus-kimi-structural-delta-readout-2026-05-21.md` - Readout recording the repaired Kimi full calibration result, stable partition, and remaining Step 6 ledger-variance blocker.
- `scripts/research/pre_step6_partitioned_reviewer_phase.py` - Research-only stable-partition reviewer phase with blinded A/B packets, dual reviewer families, label/winner-arm consistency checks, and runtime-promotion blocks.
- `tests/test_pre_step6_partitioned_reviewer_phase.py` - Tests proving stable cases are selected, variable cases are excluded, reviewer packets are blinded, and two-family support is required.
- `research/pre-step6-partitioned-reviewer-phase/` - Stable-partition reviewer contract, live judgments, and aggregate result.
- `research/pre-step6-partitioned-reviewer-phase-readout-2026-05-21.md` - Readout recording 6/6 stable positives supported, 6/7 stand-downs supported, one benign ambiguity, and no promotion.
- `scripts/research/pre_step6_variable_case_diagnostic.py` - Research-only diagnostic for quarantined variable cases, including ledger distributions, answer-level variance, answer-delta summaries, and runtime-promotion blocks.
- `tests/test_pre_step6_variable_case_diagnostic.py` - Tests proving the diagnostic selects the four quarantined cases and characterizes saved-sample variance without making a policy choice.
- `research/pre-step6-variable-case-diagnostic/` - Kimi variable-case diagnostic contract and result.
- `research/pre-step6-variable-case-alt-model-gpt51/` - Alternative-model probe artifacts for the four variable cases using `openai/gpt-5.1-chat`.
- `research/pre-step6-variable-case-diagnostic-readout-2026-05-21.md` - Readout recording answer-level variance under Kimi, model-family sensitivity under GPT, and first live pure `structural_delta_present` observations.
- `scripts/research/pre_step6_founder_v60_symmetry_check.py` - Research-only founder V60-on/off symmetry checker comparing saved Kimi and GPT sample stability without deciding answer wisdom.
- `tests/test_pre_step6_founder_v60_symmetry_check.py` - Behavior tests proving the founder symmetry contract is research-only and precommits V60/noise interpretations.
- `research/pre-step6-founder-v60-symmetry-check/` - Founder V60 symmetry contract and aggregate result.
- `research/pre-step6-founder-v60-symmetry-kimi/` - Fresh Kimi founder V60-off samples for the symmetry check.
- `research/pre-step6-founder-v60-symmetry-gpt51/` - Fresh GPT founder V60-off samples for the symmetry check.
- `scripts/research/pre_step6_gpt_stability_correctness_review.py` - Research-only split-rubric reviewer phase for GPT-stable variable-case outputs.
- `tests/test_pre_step6_gpt_stability_correctness_review.py` - Behavior tests proving GPT-stable review selection, split output/visibility rubric, structural-delta tracking, and rejection semantics.
- `research/pre-step6-gpt-stability-correctness-review/` - GPT-stability correctness contract, live reviewer judgments, and aggregate result.
- `research/pre-step6-model-family-and-v60-review-readout-2026-05-21.md` - Readout summarizing founder V60 destabilization evidence, GPT-stability adjudication, and model-commitment consequences.
- `scripts/research/pre_step6_founder_v60_private_context_audit.py` - Research-only V60/private-context audit for Founder that characterizes saved V60-on/off evidence without deciding answer wisdom.
- `tests/test_pre_step6_founder_v60_private_context_audit.py` - Behavior tests proving the V60 audit names scope limits, preserves precommitted outcome channels, and blocks runtime promotion.
- `research/pre-step6-founder-v60-private-context-audit/` - Founder V60 private-context audit contract and aggregate result.
- `research/pre-step6-founder-v60-private-context-audit-readout-2026-05-22.md` - Readout recording that the V60 chunk is related but destabilizing, and that Consultant/PhD remain queued separately.
- `scripts/research/pre_step6_consultant_deck_composition_review.py` - Research-only Consultant cleaning review and cleaning-variant builder.
- `tests/test_pre_step6_consultant_deck_composition_review.py` - Behavior tests proving Consultant review is about cleaning the Step 6 table, not adding visibility gates.
- `research/pre-step6-consultant-deck-composition-review/` - Consultant deck-composition contract, result, and cleaning-variant artifacts.
- `research/pre-step6-consultant-deck-composition-review-readout-2026-05-22.md` - Readout recording the Consultant cleaning diagnosis and variant replay recommendation.
- `scripts/research/pre_step6_consultant_cleaning_variant_replay.py` - Research-only replay harness for the cleaned Consultant micro-card table.
- `tests/test_pre_step6_consultant_cleaning_variant_replay.py` - Behavior tests proving the replay remains runtime-dormant, passes concrete micro-cards without broad lens labels, and measures consideration stability.
- `research/pre-step6-consultant-cleaning-variant-replay/` - Consultant cleaning replay contract, live Step 6 samples, and aggregate result.
- `research/pre-step6-consultant-cleaning-variant-replay-readout-2026-05-22.md` - Readout recording that the replay improves consideration legibility but remains mixed, with the counsel-gated reversibility boundary as the recurring useful delta.
- `scripts/research/pre_step6_consultant_anchor_boundary_patch_probe.py` - Research-only graduation-hypothesis probe for the Consultant counsel-gated reversibility boundary.
- `tests/test_pre_step6_consultant_anchor_boundary_patch_probe.py` - Behavior tests proving the probe is a hypothesis test rather than patch architecture, keeps the same micro-cards, and classifies upstream-pressure carry.
- `scripts/research/pre_step6_phd_kimi_variance_cleaning_review.py` - Research-only PhD atomic-decomposition review for Kimi variance, with runtime-dormant sample/result validation.
- `tests/test_pre_step6_phd_kimi_variance_cleaning_review.py` - Behavior tests proving PhD review stays research-only, passes atomic cards without broad lens labels, and classifies cross-sample atom use as discrimination.
- `research/pre-step6-phd-kimi-variance-cleaning-review/` - PhD cleaning review contract, six live Step 6 samples, and aggregate result.
- `research/pre-step6-phd-kimi-variance-cleaning-review-readout-2026-05-22.md` - Readout recording that PhD atomic decomposition generalized as distributed atom selection, not one graduation candidate.
- `scripts/research/pre_step6_cleaning_evidence_surface.py` - Research-only evidence-surface builder aggregating cleaning-lane atom recurrence without automatic graduation.
- `tests/test_pre_step6_cleaning_evidence_surface.py` - Behavior tests proving the evidence surface is human-curation support, not runtime promotion or automatic graduation.
- `research/pre-step6-cleaning-evidence-surface/` - JSON and Markdown evidence surface for Consultant and PhD cleaning results.
- `research/pre-step6-cleaning-research-closeout-2026-05-22.md` - Closeout decision document for the cleaning research chapter, including shadow definition, stop rule, and Founder V60 handoff.
- `research/pre-step6-consultant-anchor-boundary-patch-probe/` - Consultant anchor-boundary patch contract, live Step 6 samples, and aggregate result.
- `research/pre-step6-consultant-anchor-boundary-patch-probe-readout-2026-05-22.md` - Readout recording Consultant as a graduation candidate and stopping Consultant work for this research chapter.
- `research/pre-step6-answer-delta-structural-delta-targeted-rerun/` - Two-sample targeted rerun for prior reframe-useful samples under the repaired prompt and pinned Step 6 model.
- `research/pre-step6-answer-delta-structural-delta-targeted-rerun-readout-2026-05-21.md` - Readout recording that both prior reframe-useful samples now classify as concrete deltas with structural-delta custody.
- `scripts/research/pre_step6_false_standdown_bridge_probe.py` - Research-only false-standdown bridge-probe contract, live reviewer packet builder, and aggregate result validator.
- `tests/test_pre_step6_false_standdown_bridge_probe.py` - Behavior tests proving confirmed false stand-down requires two reviewer families and pre-run selection labels.
- `research/pre-step6-false-standdown-bridge-probe/*.json` - Bridge-probe contract and aggregate result artifacts.
- `research/pre-step6-false-standdown-bridge-probe/judgments/*.false-standdown-bridge-judgment.v1.json` - Live bridge-probe reviewer judgments.
- `research/pre-step6-false-standdown-bridge-probe-readout-2026-05-21.md` - Readout recording the bridge-probe stop-condition result and recommendation.
- `scripts/research/pre_step6_visibility_policy_redesign.py` - Research-only visibility-policy redesign using Step 6's private ledger as the cognitive signal while deterministic code validates cache, ledger, payload, and custody.
- `tests/test_pre_step6_visibility_policy_redesign.py` - Behavior tests proving bridge false-standdown cases surface through additive ledger signals and guardrails still fall back to anchor/current Step 6.
- `research/pre-step6-visibility-policy-redesign/*.visibility-policy-redesign.v1.json` - Generated visibility-redesign fixtures for bridge cases and guardrail cases.
- `research/pre-step6-visibility-policy-redesign-readout-2026-05-21.md` - Readout for the ledger-mediated visibility redesign.
- `scripts/research/pre_step6_bridge_step6_ledger_replay.py` - Research-only bridge replay harness proving whether Step 6 itself records additive ledger pressure on the false-standdown bridge packets.
- `tests/test_pre_step6_bridge_step6_ledger_replay.py` - Behavior tests for bridge Step 6 prompt composition, ledger-signal derivation, aggregate result validation, and fixture coverage.
- `research/pre-step6-bridge-step6-ledger-replays/*.bridge-step6-ledger-replay.v1.json` - Live Step 6 bridge replay artifacts.
- `research/pre-step6-bridge-step6-ledger-replays/bridge-step6-ledger-replay-result.v1.json` - Aggregate bridge Step 6 ledger replay result.
- `research/pre-step6-bridge-step6-ledger-replay-readout-2026-05-21.md` - Readout recording the live additive-ledger result and remaining promotion limits.
- `research/pre-step6-ledger-mediated-integration-design-draft-2026-05-21.md` - Research-only integration design draft for dormant ledger-mediated Step 6 visibility.
- `scripts/research/pre_step6_false_positive_visibility_probe.py` - Research-only mirror probe for deck overpromotion under the ledger-mediated visibility policy.
- `tests/test_pre_step6_false_positive_visibility_probe.py` - Behavior tests proving split reviewers become ambiguity, failure response is cheap-first, marker/entity null evidence is `not_observed`, and confirmed false positives require two reviewer families.
- `research/pre-step6-false-positive-visibility-probe/*.json` - False-positive visibility probe contract and aggregate result.
- `research/pre-step6-false-positive-visibility-probe/step6-replays/*.false-positive-step6-replay.v1.json` - Live Step 6 replays for false-positive probe cases.
- `research/pre-step6-false-positive-visibility-probe-readout-2026-05-21.md` - Readout recording the mirror-probe result and remaining marker/entity risk.
- `scripts/research/pre_step6_marker_entity_loss_followup.py` - Research-only follow-up probe for marker-present/entity-lost false-positive risk.
- `tests/test_pre_step6_marker_entity_loss_followup.py` - Behavior tests for marker/entity construction attempts, replay classification, and null-evidence handling.
- `research/pre-step6-marker-entity-loss-followup/*.json` - Marker/entity follow-up contract and aggregate result.
- `research/pre-step6-marker-entity-loss-followup/step6-replays/*.marker-entity-step6-replay.v1.json` - Live Step 6 replays for marker/entity construction attempts.
- `research/pre-step6-marker-entity-loss-followup-readout-2026-05-21.md` - Readout recording the focused marker/entity follow-up result.
- `engine/system_b/pre_step6_shadow_portfolio.py` - Dormant runtime module that computes cached-deck keys, records cache hit/miss, derives Step 6 ledger signal, validates shadow-only gates, and writes sidecars.
- `tests/test_pre_step6_shadow_portfolio_runtime.py` - Behavior tests proving shadow cache misses stand down, additive ledgers remain shadow-only, payload omissions guardrail deck visibility, and sidecars use the existing run-id shape.
- `scripts/run_pipeline.py` - Runtime entry point updated with default-off `--pre-step6-portfolio shadow` support and optional cached-deck directory.
- `scripts/archive_run.py` - Archive copier updated to preserve `pre_step6_shadow_portfolio.json` sidecars.
- `observatory/serve_result.py` - Observatory updated to expose the shadow portfolio in the case API and `/audit/pre-step6`.
- `research/pre-step6-shadow-portfolio-integration-readout-2026-05-21.md` - Readout for the ultra-dormant shadow implementation slice.
- `scripts/research/pre_step6_shadow_portfolio_evidence.py` - No-model-call evidence harness for prior-result cache misses and fixed-suite cache hits.
- `tests/test_pre_step6_shadow_portfolio_evidence.py` - Behavior tests proving the evidence harness materializes cached decks, normalizes Step 6 ledgers, and records cache-miss stand-downs.
- `research/pre-step6-shadow-portfolio-evidence/` - Generated shadow evidence artifacts for prior-result cache misses and fixed-suite cache hits.
- `research/pre-step6-shadow-evidence-run-readout-2026-05-21.md` - Readout for the first shadow evidence run.
- `scripts/research/pre_step6_consultant_triggered_false_positive_probe.py` - Contract builder for the consultant-triggered false-positive probe surfaced by the shadow harness.
- `tests/test_pre_step6_consultant_triggered_false_positive_probe.py` - Behavior tests proving the consultant probe is pre-registered as a positive seed under falsification.
- `research/pre-step6-consultant-triggered-false-positive-probe/` - Contract, live Step 6 replays, reviewer judgments, and aggregate result for the consultant-triggered probe.
- `research/pre-step6-consultant-triggered-false-positive-probe-readout-2026-05-21.md` - Readout resolving consultant classification and false-positive outcome.
- `SKILL.md` - Skill instructions; edit only in the gated integration draft after local evidence supports it, and keep defaults off.
- `tests/test_skill_contract.py` - Existing skill contract tests; extend only if the gated integration draft changes `SKILL.md`.

### Notes

- Unit tests for this repo live in `tests/` and should exercise public research script or validator behavior, not private implementation details.
- Use focused commands while working, for example:

```text
PYTHONPATH=. pytest tests/test_pre_step6_problem_states.py
PYTHONPATH=. pytest tests/test_pre_step6_candidate_inventory.py
PYTHONPATH=. pytest tests/test_pre_step6_reasoning_affordances.py
PYTHONPATH=. pytest tests/test_pre_step6_attention_maps.py
PYTHONPATH=. pytest tests/test_pre_step6_lens_probes.py tests/test_pre_step6_lens_answer_cores.py tests/test_pre_step6_lens_comparisons.py
PYTHONPATH=. pytest tests/test_pre_step6_lens_step6_replays.py tests/test_pre_step6_polya_lens.py
PYTHONPATH=. pytest tests/test_pre_step6_cognitive_gate_live.py tests/test_pre_step6_context_composition_gate.py
PYTHONPATH=. pytest tests/test_pre_step6_step6_card_deck.py tests/test_pre_step6_card_deck_replays.py tests/test_pre_step6_card_deck_replay_comparisons.py
PYTHONPATH=. pytest tests/test_pre_step6_card_deck_visibility_policy.py
PYTHONPATH=. pytest tests/test_pre_step6_design_preamble_cost_cache.py
PYTHONPATH=. pytest tests/test_pre_step6_private_reasoning_cards.py
PYTHONPATH=. pytest tests/test_pre_step6_private_consideration_ledger.py
PYTHONPATH=. pytest tests/test_pre_step6_payload_omission_gate.py
PYTHONPATH=. pytest tests/test_pre_step6_visibility_asymmetry_policy.py
PYTHONPATH=. pytest tests/test_pre_step6_calibration_floor_manifest.py
PYTHONPATH=. pytest tests/test_pre_step6_false_standdown_bridge_probe.py
PYTHONPATH=. pytest tests/test_pre_step6_visibility_policy_redesign.py
PYTHONPATH=. pytest tests/test_pre_step6_bridge_step6_ledger_replay.py
PYTHONPATH=. pytest tests/test_pre_step6_false_positive_visibility_probe.py
PYTHONPATH=. pytest tests/test_pre_step6_marker_entity_loss_followup.py
PYTHONPATH=. pytest tests/test_pre_step6_shadow_portfolio_runtime.py
PYTHONPATH=. pytest tests/test_pre_step6_shadow_portfolio_evidence.py
PYTHONPATH=. pytest tests/test_pre_step6_consultant_triggered_false_positive_probe.py
PYTHONPATH=. pytest tests/test_pre_step6_founder_v60_symmetry_check.py tests/test_pre_step6_gpt_stability_correctness_review.py
PYTHONPATH=. pytest tests/test_pre_step6_founder_v60_private_context_audit.py
PYTHONPATH=. pytest tests/test_pre_step6_consultant_deck_composition_review.py
```

- Run regression checks before handoff:

```text
PYTHONPATH=. pytest \
  tests/test_pre_step6_raw_artifacts.py \
  tests/test_pre_step6_hybrid_handoffs.py \
  tests/test_pre_step6_pressure_card_consumption.py \
  tests/test_pre_step6_semi_blind_comparisons.py \
  tests/test_pre_step6_replay_ledger.py
git diff --check
```

- Work in vertical red-green-refactor slices: write one failing behavior test, implement the smallest code that passes it, then continue.
- Do not write all tests first. Do not build the whole feature first and test afterward.
- Do not use provider/OpenRouter calls in automated tests. Use static fixtures or deterministic baselines. Any live model call must remain manual and research-only.
- Do not change default `/lolla` behavior during Tasks 1-5.
- Do not merge to `main` unless Task 7 concludes the experiment earns promotion.
- Use the autoresearch program for the next iteration: one hypothesis, one
  smallest research-only change, fixed case-suite evaluation, logged
  keep/retest/discard/boundary-case decision.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` after completing.

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Check current branch and working tree with `git status --short` and `git branch --show-current`.
  - [x] 0.2 Create and checkout a local experiment branch, for example `git switch -c feature/step6-reasoning-portfolio`.
  - [x] 0.3 Confirm the PRD and task file are present on the branch and remain uncommitted until the first intentional checkpoint.
  - [x] 0.4 Record in the eventual handoff that `main` was not changed and the experiment is branch-local.

- [x] 1.0 Lock the local reasoning-portfolio contract
  - [x] 1.1 Read the PRD, existing raw/hybrid handoff validators, and comparison readouts to ground the contract in prior behavior.
  - [x] 1.2 Create `research/pre-step6-reasoning-portfolio-contract-2026-05-20.md` with the local-only policy, non-goals, and promotion gate.
  - [x] 1.3 Define `problem_state.v1`, `candidate_inventory.v1`, `reasoning_affordance.v1`, and `step6_attention_map.v1` in the contract.
  - [x] 1.4 Define allowed affordance classes, attention weights, protected slots, expansion refs, caps, and forbidden language.
  - [x] 1.5 Add the core doctrine to the contract: no artifact dump, no premature pruning, cap prose not possibility, broad availability with delayed rejection.
  - [x] 1.6 Add TDD rules to the contract: one behavior test at a time, no provider calls in automated tests, no default runtime wiring.
  - [x] 1.7 Review the contract manually against the PRD and revise only for clarity, not implementation speculation.

- [x] 2.0 Build the problem-state and candidate-inventory tracer bullet
  - [x] 2.1 RED: Add one failing test in `tests/test_pre_step6_problem_states.py` showing that a valid `problem_state.v1` fixture validates.
  - [x] 2.2 GREEN: Implement the minimum `scripts/research/pre_step6_problem_states.py` validator needed to pass the valid-fixture test.
  - [x] 2.3 Add the first `research/pre-step6-problem-states/*.problem-state.v1.json` fixture for one existing comparison case.
  - [x] 2.4 RED: Add one failing test that rejects `problem_state.v1` when `source_refs` are missing or empty.
  - [x] 2.5 GREEN: Extend the validator to reject missing source refs while keeping the public interface stable.
  - [x] 2.6 RED: Add one failing test that rejects final-advice or answer-plan language inside `problem_state.v1`.
  - [x] 2.7 GREEN: Add the smallest forbidden-language guard needed for the test.
  - [x] 2.8 RED: Add one failing test in `tests/test_pre_step6_candidate_inventory.py` showing that the Marcus result fixture produces candidate records for `delta_card`, `companion_card`, `frame_pressure_card`, `structural_coverage_card`, `audit_summary`, and `run_health`.
  - [x] 2.9 GREEN: Implement the minimum `scripts/research/pre_step6_build_candidate_inventory.py` builder needed to pass the Marcus inventory test.
  - [x] 2.10 RED: Add one failing test that candidate inventory preserves source refs or expansion refs for raw and hybrid handoff inputs.
  - [x] 2.11 GREEN: Extend the builder to include raw/hybrid source refs without deciding usefulness.
  - [x] 2.12 Add static candidate-inventory fixtures for `mother-address-year`, `third-year-phd-student`, and `marcus_new_path_result`.
  - [x] 2.13 REFACTOR: Remove duplication between validators only after all focused tests pass.

- [x] 3.0 Build reasoning-affordance vertical slices
  - [x] 3.1 RED: Add one failing test showing that a valid `reasoning_affordance.v1` fixture with `attention_weight: active` validates.
  - [x] 3.2 GREEN: Implement the minimum `scripts/research/pre_step6_reasoning_affordances.py` validator needed for the valid active fixture.
  - [x] 3.3 RED: Add one failing test that rejects an affordance with unsupported `affordance_class`, `attention_weight`, or `protected_slot`.
  - [x] 3.4 GREEN: Add enum validation for affordance classes, attention weights, and protected slots.
  - [x] 3.5 RED: Add one failing test that rejects final advice, "use/drop because correct", or generic "add nuance" language.
  - [x] 3.6 GREEN: Add forbidden-language validation without blocking legitimate boundary or risk language.
  - [x] 3.7 RED: Add one failing test that an edge or scan affordance must keep `cheap_test_for_step6`, `risk_if_forced`, `risk_if_ignored`, and `expansion_ref`.
  - [x] 3.8 GREEN: Implement required-field validation for edge/scan affordances.
  - [x] 3.9 RED: Add one failing test for a deterministic baseline conversion from an existing raw artifact into a `reasoning_affordance.v1` record.
  - [x] 3.10 GREEN: Implement only the baseline conversion needed for the raw artifact test, preserving source grounding and risks.
  - [x] 3.11 RED: Add one failing test that low-fit protected-slot material is parked with a receipt instead of silently suppressed.
  - [x] 3.12 GREEN: Add parked-affordance support that records `selection_basis`, `protected_slot`, `discard_condition`, and `expansion_ref`.
  - [x] 3.13 Add fixture affordances for direct pressure, contrarian edge, negative space, duplicate support, false friend, and parked receipt.
  - [x] 3.14 REFACTOR: Consolidate shared string/list validation only after the affordance tests pass.

- [x] 4.0 Build Step 6 attention-map assembly
  - [x] 4.1 RED: Add one failing test showing that a valid `step6_attention_map.v1` fixture validates with active, edge, weak/negative-space, and parked sections.
  - [x] 4.2 GREEN: Implement the minimum `scripts/research/pre_step6_attention_maps.py` validator needed for the valid map test.
  - [x] 4.3 RED: Add one failing test that rejects edge reserve items without `protected_slot`, `cheap_test`, `risk_if_forced`, `risk_if_ignored`, or `expansion_ref`.
  - [x] 4.4 GREEN: Add edge reserve validation.
  - [x] 4.5 RED: Add one failing test that rejects parked items without `park_reason`, `reactivate_if`, and `expansion_ref`.
  - [x] 4.6 GREEN: Add parked-item validation.
  - [x] 4.7 RED: Add one failing test that `step6_instruction` is advisory and does not contain final advice, public model labels, or "Step 6 should conclude" language.
  - [x] 4.8 GREEN: Add instruction hygiene validation.
  - [x] 4.9 RED: Add one failing test that the attention-map builder preserves at least one active item and at least one protected edge item from affordance inputs.
  - [x] 4.10 GREEN: Implement the minimum `scripts/research/pre_step6_build_attention_map.py` assembler needed to pass the preservation test.
  - [x] 4.11 RED: Add one failing test that low-fit protected-slot items move to `edge_latticework_reserve` or `parked_but_preserved`, not deletion.
  - [x] 4.12 GREEN: Extend assembly to preserve protected material with receipts and expansion refs.
  - [x] 4.13 RED: Add one failing test that rendered private Step 6 context stays under the research render budget while keeping archive refs.
  - [x] 4.14 GREEN: Implement the smallest private renderer needed to satisfy the cap and archive-ref test.
  - [x] 4.15 Add attention-map fixtures for the first comparison cases and validate all of them.
  - [x] 4.16 REFACTOR: Simplify budget and rendering helpers only after all attention-map tests pass.

- [x] 5.0 Compare portfolio output against raw, hybrid, and monolithic baselines
  - [x] 5.1 RED: Add one failing comparison test or readout check that every comparison payload names its mode, case id, source refs, and aggregate judgment.
  - [x] 5.2 GREEN: Add the minimum `scripts/research/pre_step6_portfolio_comparisons.py` helper or static validation needed for comparison payloads.
  - [x] 5.3 Generate comparison fixtures for at least `mother-address-year`, `third-year-phd-student`, `founder-grant-marcus-equity.high-clutter`, and `mid-level-consultant-report-2`.
  - [x] 5.4 Compare modes A-F from the PRD where possible: current default, raw handoff, hybrid handoff, monolithic control note if available, portfolio map, and portfolio plus optional reviewers if available.
  - [x] 5.5 Record latency proxy, render size, item counts, source-ref coverage, active/edge/parked distribution, premature-pruning risk, and answer-usefulness judgment.
  - [x] 5.6 Add one explicit negative-control judgment where no extra active pressure is a successful outcome.
  - [x] 5.7 Add one high-clutter judgment where broad edge reserve beats raw artifact dumping.
  - [x] 5.8 Add one falsifier section explaining where the portfolio distracted Step 6, lost pressure, or failed to justify cost.
  - [x] 5.9 Write a research readout summarizing whether the portfolio approach beats raw/hybrid enough to justify gated integration.

- [x] 6.0 Draft gated skill integration without changing the default runtime
  - [x] 6.1 Do not start this task until Tasks 1-5 have passing focused tests and a comparison readout.
  - [x] 6.2 Decide whether the evidence supports a local gated draft or whether the experiment should stop at research artifacts.
  - [x] 6.3 RED: If editing `SKILL.md`, add or update a focused skill contract test proving the new behavior is flag-gated and default-off. Not applicable: decision was to stop at research artifacts.
  - [x] 6.4 GREEN: Add the minimum `SKILL.md` draft language for `LOLLA_STEP6_ATTENTION_MAP=off|on` and `LOLLA_PRESSURE_CHECK_MODE=off|manual`, keeping default behavior unchanged. Not applicable: `SKILL.md` was not edited.
  - [x] 6.5 Add explicit language that Step 6 receives the attention map as private advisory context, not as a verdict or answer plan. Captured in the research contract and handoff, not `SKILL.md`.
  - [x] 6.6 Add explicit language that post-Step-6 pressure checks remain optional and intentional skips are valid receipts. Captured in the research contract and handoff, not `SKILL.md`.
  - [x] 6.7 Run `tests/test_skill_contract.py` and the focused pre-Step-6 tests.
  - [x] 6.8 If skill-contract changes create ambiguity or runtime risk, revert only the gated integration draft and keep the research artifacts.

- [x] 7.0 Review promotion evidence and keep changes local unless the experiment earns a merge
  - [x] 7.1 Run focused tests for problem states, candidate inventory, reasoning affordances, attention maps, and portfolio comparisons.
  - [x] 7.2 Run pre-Step-6 regression tests for raw artifacts, hybrid handoffs, pressure-card consumption, semi-blind comparisons, replay ledger, no-rendered handoffs, and decline evaluations.
  - [x] 7.3 Run `git diff --check`.
  - [x] 7.4 Review the final diff for accidental runtime wiring, default behavior changes, public output leakage, or provider-call assumptions.
  - [x] 7.5 Prepare a handoff note with test commands, fixture paths, comparison results, falsifiers, and recommendation.
  - [x] 7.6 Decide one of three outcomes: abandon/revise, keep research-only, or prepare a PR for gated integration.
  - [x] 7.7 If the decision is not "prepare a PR", leave `main` unchanged and document the next experiment.
  - [x] 7.8 If the decision is "prepare a PR", keep the PR scoped to the branch and require human review before merge. Not applicable: decision is keep research-only.

- [x] 8.0 Capture the autoresearch loop for the next research iteration
  - [x] 8.1 Read Karpathy's `autoresearch` README and `program.md` to extract the process pattern rather than copying the training-specific mechanics.
  - [x] 8.2 Create a Lolla-specific autoresearch program that uses fixed case-suite evaluation instead of a single scalar training metric.
  - [x] 8.3 Preserve the values: enrichment, depth, breadth, delayed rejection, scan/parked receipts, and Step 6 as the solver.
  - [x] 8.4 Name Bevelin as the first lens-pack experiment without making it the architecture.
  - [x] 8.5 Update the PRD, contract, and handoff so the next iteration uses the autoresearch loop instead of ad hoc prompting.

- [x] 9.0 Run the first Bevelin lens-pack autoresearch slice
  - [x] 9.1 RED: Add a focused lens-probe fixture test for the fixed suite.
  - [x] 9.2 GREEN: Add `pre_step6_lens_probes.py` and Bevelin v0 probe fixtures for founder high-clutter, PhD v2, consultant, and mother.
  - [x] 9.3 RED: Add a focused lens-answer-core fixture test for public-clean Bevelin-enhanced answers.
  - [x] 9.4 GREEN: Add `pre_step6_lens_answer_cores.py` and four Bevelin answer-core fixtures.
  - [x] 9.5 RED: Add a focused lens-comparison fixture test that expects founder and PhD v2 to improve while consultant and mother do not over-promote.
  - [x] 9.6 GREEN: Add `pre_step6_lens_comparisons.py` and four Bevelin comparison fixtures.
  - [x] 9.7 Record the fixed-suite result in the readout, contract, PRD, handoff, and autoresearch ledger.
  - [x] 9.8 Keep all Bevelin work research-only and leave `SKILL.md` and runtime untouched.

- [x] 10.0 Add cognitive replay gate and run Bevelin-positive replays
  - [x] 10.1 RED: Add a focused replay test requiring Bevelin replay fixtures to include a `cognitive_gate`.
  - [x] 10.2 GREEN: Add `pre_step6_lens_step6_replays.py` with validation for cognitive judgment mode, source refs, public hygiene, and promotion blocks.
  - [x] 10.3 Add Bevelin replay fixtures for founder high-clutter and PhD v2 against prior portfolio replays.
  - [x] 10.4 Record that code validates custody and consistency while cognition judges quality.
  - [x] 10.5 Keep runtime wiring and `SKILL.md` promotion blocked.

- [x] 11.0 Test Polya as an independent problem-shape lens
  - [x] 11.1 RED: Add a focused test requiring Polya probe, answer-core, and comparison fixtures for the fixed suite.
  - [x] 11.2 GREEN: Generalize the lens comparison validator to accept `polya_problem_solving_v0`.
  - [x] 11.3 Add Polya probe fixtures for founder high-clutter, PhD v2, consultant, and mother.
  - [x] 11.4 Add Polya answer-core fixtures and keep Polya labels out of public answers.
  - [x] 11.5 Add Polya comparison fixtures and record fixed-suite results.
  - [x] 11.6 Update readout, PRD, contract, handoff, and ledger with the Polya generalization result.

- [x] 12.0 Run live cognitive comparison gates
  - [x] 12.1 RED: Add a focused test requiring blinded live-gate packets and validated judgment payloads.
  - [x] 12.2 GREEN: Add `pre_step6_cognitive_gate_live.py` with research-only runtime blocks, provider metadata, static-agreement scoring, and dry-run packet rendering.
  - [x] 12.3 Run a four-case live answer-core comparison with the current fast OpenRouter reviewer model after the env default returned 404.
  - [x] 12.4 Tighten the reviewer prompt when the first run judged final-answer template quality instead of private Step 6 context quality.
  - [x] 12.5 Record that answer-core replacement is the wrong abstraction: rendered hybrid often beats lens answer cores because it preserves concrete case nuance.

- [x] 13.0 Test rendered-anchor plus protected-receipt composition
  - [x] 13.1 RED: Add a focused test requiring private context packets that compare rendered-only against rendered plus protected receipts.
  - [x] 13.2 GREEN: Add `pre_step6_context_composition_gate.py` with blinded packet construction, judgment validation, and live-call support.
  - [x] 13.3 Run the no-tax composition gate and observe that it over-promotes dual receipts in negative controls.
  - [x] 13.4 RED/GREEN: Add explicit smallest-sufficient-packet and complexity-tax prompt pressure.
  - [x] 13.5 Run the complexity-tax composition gate with Gemini and a GPT-5.1 cross-model check.
- [x] 13.6 Record the current recommendation: keep runtime dormant, retain rendered hybrid as anchor, and retest novelty-filtered protected receipts before any skill integration.

- [x] 14.0 Build and evaluate the broad Step 6 private card deck
  - [x] 14.1 RED: Add a focused test requiring a private Step 6 card deck to include clean hybrid, Bevelin, and Polya cards without letting code decide cognitive usefulness.
  - [x] 14.2 GREEN: Add `pre_step6_step6_card_deck.py` with schema validation, rendering, source refs, problem read, deterministic-limit text, and four generated deck artifacts.
  - [x] 14.3 RED: Add a focused replay test requiring Step 6 to receive the full deck and return a private consideration ledger for every card.
  - [x] 14.4 GREEN: Add `pre_step6_card_deck_replays.py` with public hygiene checks, ledger validation, runtime-promotion blocks, and live-call support.
  - [x] 14.5 Run live Step 6 card-deck replays on the fixed four-case suite using the env file keys and `openai/gpt-5.1-chat`.
  - [x] 14.6 RED: Add a focused comparison test requiring blinded reviewer packets and rejecting internally inconsistent winner/effect judgments.
  - [x] 14.7 GREEN: Add `pre_step6_card_deck_replay_comparisons.py`; keep reviewer cognition blinded to source arms and let deterministic code only map the blind winner to `improves`, `equivalent`, or `regresses`.
  - [x] 14.8 Fix the first comparison-gate flaw where the blinded reviewer was asked to report `deck_effect`, then rerun the four-case gate with corrected blinding.
  - [x] 14.9 Refine the Step 6 replay prompt after founder/mother regressions showed over-compression risk: preserve minimum useful specificity and do not compress away tripwires, actor-specific steps, or irreversible-risk distinctions merely to be concise.
- [x] 14.10 Rerun the four-case replay and comparison suite; record the result: card deck improved founder, PhD v2, and consultant, while mother still favored clean hybrid for tighter sensitive-safety wording.

- [x] 15.0 Add novelty-role ledger and anchor-payload preservation
  - [x] 15.1 RED: Add a focused replay-prompt test requiring `novelty_role` and private guardrail language in the Step 6 ledger contract.
  - [x] 15.2 GREEN: Extend `pre_step6_card_deck_replays.py` so every ledger item records `visible_backbone`, `additive_pressure`, `confirming_support`, or `private_guardrail`.
  - [x] 15.3 RED/GREEN: Add prompt language that the ledger is where card consideration lives and the public answer should not grow merely to prove every card was considered.
  - [x] 15.4 RED/GREEN: Add sensitive safety/legal handling so visible enrichment must add a concrete safeguard, tripwire, or channel distinction.
  - [x] 15.5 RED/GREEN: Add anchor-payload preservation for named channels/resources, communication boundaries, dated windows, gates, actor sequence, tripwires, and evidence checks.
  - [x] 15.6 RED/GREEN: Add public hygiene reminder after a founder replay correctly failed validation for forbidden terms such as `bundle` and `lane`.
- [x] 15.7 Rerun the live four-case suite and a Gemini cross-model comparison; record robust wins for founder, PhD v2, and consultant, and clean-hybrid stand-down for mother.

- [x] 16.0 Add ledger-based visible-answer stand-down policy
  - [x] 16.1 RED: Add a focused test showing mother is anchor-standdown eligible only because Step 6 marked both non-anchor cards private/confirming and the cognitive reviewer preferred clean hybrid.
  - [x] 16.2 RED: Add a focused test showing founder is not anchor-standdown eligible because Step 6 marked non-anchor cards as additive pressure and the cognitive reviewer preferred card-deck replay.
  - [x] 16.3 GREEN: Add `pre_step6_card_deck_visibility_policy.py` with schema validation, source refs, ledger summary, deterministic read, cognitive confirmation, visible policy result, and runtime-promotion blocks.
  - [x] 16.4 Generate four visibility-policy artifacts and validate them.
  - [x] 16.5 Record the key boundary: code may record stand-down eligibility from Step 6's ledger, but visible-answer preference still requires cognitive confirmation.

- [x] 17.0 Run `design_preamble_cost_cache_v0`
  - [x] 17.1 RED: Add a focused cost/cache contract test proving `runtime_cached_only` cache misses stand down without live card generation.
  - [x] 17.2 GREEN: Add `pre_step6_design_preamble_cost_cache.py` with compiled key material, mode-specific cache read, cost envelope, runtime effect, validation, and fixture writing.
  - [x] 17.3 RED/GREEN: Add a focused test proving V60 selected-item hashes change the compiled card-deck key.
  - [x] 17.4 RED/GREEN: Add a focused test proving research misses may cold-fill while normal runtime reviewer calls remain 0.
  - [x] 17.5 Generate four `runtime_cached_only` miss fixtures for the fixed suite and validate them.
  - [x] 17.6 Record the result in the design-preamble track, handoff, autoresearch program, and autoresearch ledger.
  - [x] 17.7 Keep `SKILL.md` and runtime untouched; move the current next experiment to `design_preamble_card_interface_v0`.

- [x] 18.0 Run `design_preamble_card_interface_v0`
  - [x] 18.1 RED: Add a focused generic-card-interface test proving existing card-deck cards validate through one schema.
  - [x] 18.2 RED: Add a focused synthetic future-card test proving a non-Bevelin/Polya card can validate without policy or ledger fields.
  - [x] 18.3 GREEN: Add `pre_step6_private_reasoning_cards.py` with `private_reasoning_card.v1`, interface validation, synthetic future-card fixture, and fixture writing.
  - [x] 18.4 Generate four private-card-interface fixtures for the fixed suite and validate them.
  - [x] 18.5 Record the result in the design-preamble track, handoff, PRD, autoresearch program, and autoresearch ledger.
  - [x] 18.6 Keep `SKILL.md` and runtime untouched; move the current next experiment to `design_preamble_ledger_overlap_v0`.

- [x] 19.0 Run `design_preamble_ledger_overlap_v0`
  - [x] 19.1 RED: Add a focused ledger-overlap test proving hot context presents one representative while ledger custody preserves both a reasoning card and V60-style item.
  - [x] 19.2 GREEN: Add `pre_step6_private_consideration_ledger.py` with `private_consideration_item.v1`, overlap groups, presentation policy, custody policy, and validation.
  - [x] 19.3 Generate the founder ledger-overlap fixture and validate it.
  - [x] 19.4 Record the result in the design-preamble track, handoff, PRD, autoresearch program, and autoresearch ledger.
  - [x] 19.5 Keep `SKILL.md` and runtime untouched; move the current next experiment to `design_preamble_payload_omission_v0`.

- [x] 20.0 Run `design_preamble_payload_omission_v0`
  - [x] 20.1 RED: Add a focused test proving the omission gate emits one record per protected category and only anchor-present/deck-absent rows are omission signals.
  - [x] 20.2 GREEN: Add `pre_step6_payload_omission_gate.py` with six protected categories, mechanistic detectors, diff judgments, gate result/action, and runtime-promotion blocks.
  - [x] 20.3 RED/GREEN: Add a synthetic introduced-omission test proving a missing anchor date triggers `introduced_omission` and `retest`.
  - [x] 20.4 RED/GREEN: Add a detector-noise test and narrow named-resource detection so ordinary capitalized words are not treated as resources.
  - [x] 20.5 Generate four fixed-suite payload-omission fixtures and validate them.
  - [x] 20.6 Record that all four fixed-suite deck-aware answers preserved protected payload categories; mother stand-down remains phrasing/tightness, not omission.
  - [x] 20.7 Keep `SKILL.md` and runtime untouched; run ledger negative-shape fixtures before visibility asymmetry.

- [x] 21.0 Add ledger negative-shape fixtures
  - [x] 21.1 RED: Add a focused non-overlap test proving card and V60-style items both remain in hot context when no overlap group applies.
  - [x] 21.2 RED: Add a focused V60-only/no-deck test proving `private_consideration_item.v1` validates without a card deck.
  - [x] 21.3 GREEN: Extend `pre_step6_private_consideration_ledger.py` with non-overlap and V60-only fixture builders plus CLI fixture-kind support.
  - [x] 21.4 Generate and validate non-overlap and V60-only fixtures.
  - [x] 21.5 Record the result in the design-preamble track, handoff, PRD, autoresearch program, and autoresearch ledger.
  - [x] 21.6 Keep `SKILL.md` and runtime untouched; move the current next experiment to `design_preamble_visibility_asymmetry_v0`.

- [x] 22.0 Run `design_preamble_visibility_asymmetry_v0`
  - [x] 22.1 RED: Add a focused runtime-asymmetry test proving runtime unresolved/tie-like cases default to anchor-visible/deck-private without a reviewer loop.
  - [x] 22.2 RED: Add a focused research-mode test proving tie/disagreement cases retest at most once with a second reviewer spec.
  - [x] 22.3 GREEN: Add `pre_step6_visibility_asymmetry_policy.py` with mode-specific visibility policy, runtime asymmetry, retest policy, and validation.
  - [x] 22.4 Generate and validate fixtures for runtime unresolved, deck-confirmed, anchor-confirmed, tie, and ledger/reviewer disagreement.
  - [x] 22.5 Record the result in the design-preamble track, handoff, PRD, autoresearch program, and autoresearch ledger.
  - [x] 22.6 Keep `SKILL.md` and runtime untouched; move the current next experiment to `design_preamble_calibration_floor_v0`.

- [x] 23.0 Run `design_preamble_calibration_floor_v0`
  - [x] 23.1 RED: Add a focused calibration-floor test proving the four fixed cases are seed evidence, not a promotion floor.
  - [x] 23.2 RED: Add a focused bucket-gap test proving missing high-clutter, sequencing/problem-shape, sensitive/safety/legal, negative-control, and V60 on/off coverage is explicit.
  - [x] 23.3 GREEN: Add `pre_step6_calibration_floor_manifest.py` with required floor, current suite, bucket gaps, false-standdown recall fields, and runtime-promotion blocks.
  - [x] 23.4 Generate and validate `seed-suite.calibration-floor.v1.json`.
  - [x] 23.5 Record that calibration remains unmet and case curation is the next non-code bottleneck.
  - [x] 23.6 Keep `SKILL.md` and runtime untouched; block integration draft until the board accepts either a bridge set or full calibration curation.
  - [x] 23.7 RED/GREEN: Pin V60 on/off pairs as same-case toggles, not substantive-vs-minimal V60 curation.
  - [x] 23.8 RED/GREEN: Track `preserved_by_marker_anchor_entities_missing` as a calibration-time payload outcome without changing the omission gate verdict logic.
  - [x] 23.9 RED/GREEN: Add `false_standdown_bridge_probe_v0` as the next non-promotional 2-3 case probe before full curation.

- [x] 24.0 Run `false_standdown_bridge_probe_v0`
  - [x] 24.1 RED: Add a focused bridge-probe contract test requiring pre-run selection labels and a two-reviewer-family definition of confirmed false stand-down.
  - [x] 24.2 GREEN: Add `pre_step6_false_standdown_bridge_probe.py` with probe contract validation, live reviewer packet construction, judgment validation, and aggregate result validation.
  - [x] 24.3 Generate and validate the pre-registered bridge-probe contract fixture.
  - [x] 24.4 Dry-run a reviewer packet to inspect the prompt surface before live calls.
  - [x] 24.5 Run the three bridge cases with `openai/gpt-5.1-chat` and `google/gemini-3.1-flash-lite`.
  - [x] 24.6 Generate and validate six reviewer judgment artifacts plus the aggregate bridge result.
  - [x] 24.7 Record the result: all three bridge cases confirmed `false_standdown`; stop condition triggered; integration draft blocked.
  - [x] 24.8 Keep `SKILL.md` and runtime untouched; move the next research slice to `design_preamble_visibility_policy_redesign_v0`.

- [x] 25.0 Run `design_preamble_visibility_policy_redesign_v0`
  - [x] 25.1 RED: Add a focused policy test proving a confirmed bridge false-standdown case moves from legacy anchor suppression to deck visibility when Step 6 records additive pressure and payload is preserved.
  - [x] 25.2 RED: Add guardrail tests proving private/confirming ledgers, payload omissions, cache misses, and missing ledgers still fall back to anchor/current Step 6.
  - [x] 25.3 GREEN: Add `pre_step6_visibility_policy_redesign.py` with ledger-mediated runtime policy validation and fixture writing.
  - [x] 25.4 Generate and validate bridge-case and guardrail fixtures.
  - [x] 25.5 Record the result: universal anchor fallback is replaced at contract level by Step-6-ledger mediated visibility without adding a runtime reviewer loop.
  - [x] 25.6 Keep `SKILL.md` and runtime untouched; block integration until bridge Step 6 ledger replay or full calibration proves the upstream additive signal.

- [x] 26.0 Run `bridge_step6_ledger_replay_v0`
  - [x] 26.1 RED: Add a prompt-surface test requiring bridge Step 6 replay to pass anchor/deck-pressure candidates and request a private consideration ledger.
  - [x] 26.2 RED: Add ledger-signal tests proving code derives `additive_pressure_present` only from Step 6 ledger entries, and does not unlock the redesigned policy for private/confirming deck pressure.
  - [x] 26.3 GREEN: Add `pre_step6_bridge_step6_ledger_replay.py` with replay prompt construction, live replay support, ledger normalization, signal derivation, aggregate result validation, and fixture writing.
  - [x] 26.4 Generate and validate bridge replay fixtures and aggregate result artifacts.
  - [x] 26.5 Run live bridge Step 6 replay with `openai/gpt-5.1-chat` on all three false-standdown bridge packets.
  - [x] 26.6 Record the result: all three live bridge replays produced `ledger_signal: additive_pressure_present`; aggregate `replay_result: step6_additive_signal_supported`.
  - [x] 26.7 Keep `SKILL.md` and runtime untouched; treat this as support for a research-only integration design draft, not runtime promotion.

- [x] 27.0 Write the ledger-mediated integration design draft
  - [x] 27.1 Draft the research-only integration shape: broad private deck, Step 6 answer plus private ledger, deterministic guards, and visible answer decision.
  - [x] 27.2 Pin mode gates, cache-hit-only behavior, cache-miss stand-down, and no normal runtime reviewer loop.
  - [x] 27.3 Define the Step 6 prompt/ledger contract, unified ledger fields, payload tripwire role, visibility resolver, archive fields, and Observatory view.
  - [x] 27.4 Record promotion gates, falsifiers, implementation slices, and the explicit boundary that runtime promotion remains blocked.
  - [x] 27.5 Update PRD, handoff, design-preamble track, autoresearch program, and autoresearch ledger.
  - [x] 27.6 Keep `SKILL.md` and runtime untouched.

- [x] 28.0 Run `false_positive_visibility_probe_v0`
  - [x] 28.1 Patch the ledger-mediated design draft so it is explicitly a proposed dormant architecture, not an approved implementation contract.
  - [x] 28.2 RED: Add probe-contract tests for split reviewer outcomes, cheap-first failure response, marker/entity null evidence, and two-family confirmation.
  - [x] 28.3 GREEN: Add `pre_step6_false_positive_visibility_probe.py` with contract validation, Step 6 replay, blind-review packet construction, aggregate result logic, and live mode.
  - [x] 28.4 Generate and validate the false-positive probe contract fixture.
  - [x] 28.5 Run live Step 6 replay with `openai/gpt-5.1-chat` on all three mirror-risk cases.
  - [x] 28.6 Record the result: Bevelin and Polya temptation cases stood down; marker/entity-loss case is `not_observed`; aggregate `continue_probe_with_not_observed`.
  - [x] 28.7 Keep `SKILL.md` and runtime untouched; leave marker/entity-loss risk as a live calibration or follow-up-probe item.

- [x] 29.0 Run `marker_entity_loss_followup_v0`
  - [x] 29.1 RED: Add a focused follow-up contract test requiring three pre-registered marker/entity construction attempts and an explicit null-evidence warning.
  - [x] 29.2 RED: Add detector and aggregate-result tests proving marker-present/entity-lost plus two reviewer families triggers design review, while no additive loss remains `not_observed`.
  - [x] 29.3 GREEN: Add `pre_step6_marker_entity_loss_followup.py` with contract validation, marker/entity detector, Step 6 replay, conditional reviewer packet construction, live mode, and aggregate result logic.
  - [x] 29.4 Generate and validate the marker/entity follow-up contract fixture.
  - [x] 29.5 Run live Step 6 replay with `openai/gpt-5.1-chat` on all three construction attempts.
  - [x] 29.6 Record the result: all three attempts produced `all_private_or_confirming`; Step 6 preserved concrete anchor entities; aggregate `not_observed`; no reviewer calls needed.
  - [x] 29.7 Keep `SKILL.md` and runtime untouched; allow only ultra-dormant shadow implementation or full calibration as next step.

- [x] 30.0 Implement `ultra_dormant_shadow_portfolio_integration_v0`
  - [x] 30.1 RED: Add runtime contract tests for cache miss stand-down, cache hit plus additive Step 6 ledger, payload-omission guardrail, ledger-signal derivation, and sidecar naming.
  - [x] 30.2 GREEN: Add `engine/system_b/pre_step6_shadow_portfolio.py` with compiled cache keys, cached-only lookup, shadow visibility decision records, closed gates, validation, and sidecar writing.
  - [x] 30.3 RED/GREEN: Add archive coverage proving `pre_step6_shadow_portfolio.json` is copied into the run archive.
  - [x] 30.4 RED/GREEN: Add Observatory coverage proving `/audit/pre-step6` renders the shadow decision and the case API exposes `pre_step6_shadow_portfolio`.
  - [x] 30.5 Add default-off `--pre-step6-portfolio shadow` runtime plumbing and optional cache-dir support without changing visible output or `SKILL.md`.
  - [x] 30.6 Run focused and broad pre-Step-6/Observatory regression checks.
  - [x] 30.7 Record the result: shadow mode is now an evidence-gathering instrument only; runtime promotion and visible behavior remain blocked.

- [x] 31.0 Run `shadow_evidence_run_v0`
  - [x] 31.1 RED: Add an evidence-harness test proving fixed-suite cache-hit runs materialize decks, normalize Step 6 replay ledgers, and aggregate shadow decisions.
  - [x] 31.2 RED: Add an evidence-harness test proving prior result files produce cache-miss stand-down artifacts without live deck generation.
  - [x] 31.3 GREEN: Add `pre_step6_shadow_portfolio_evidence.py` with `result-cache-miss`, `fixed-suite-cache-hit`, and `all` modes.
  - [x] 31.4 Run the evidence harness on eight prior-result artifacts and the four fixed-suite cached decks.
  - [x] 31.5 Record the result: eight prior results safely stood down on cache miss; fixed-suite cache hits produced three `deck_visible_shadow_only` records and one mother stand-down, all with zero visible applications.
  - [x] 31.6 Keep runtime promotion and `SKILL.md` behavior blocked; move next learning to cache-coverage expansion or shadow Observatory review.

- [x] 32.0 Run `consultant_triggered_false_positive_probe_v0`
  - [x] 32.1 RED: Add a contract-builder test pinning consultant as `positive_seed` under falsification rather than a negative-control seed.
  - [x] 32.2 GREEN: Add `pre_step6_consultant_triggered_false_positive_probe.py` to generate a custom false-positive probe contract with consultant, marker/entity-loss, and Bevelin-temptation cases.
  - [x] 32.3 Update the calibration-floor manifest and tests so consultant is `sensitive_safety_legal` / `positive_seed`; mother remains the only current negative-control stand-down seed.
  - [x] 32.4 Run live Step 6 replay with `openai/gpt-5.1-chat` and dual-reviewer adjudication with `openai/gpt-5.1-chat` plus `google/gemini-3.1-flash-lite`.
  - [x] 32.5 Record the result: consultant produced `additive_pressure_present`; both reviewer families labeled it `true_visible`; Bevelin temptation stood down; marker/entity loss remained `not_observed`.
  - [x] 32.6 Keep runtime promotion and `SKILL.md` behavior blocked; use shadow telemetry as candidate discovery, not final adjudication.

- [x] 33.0 Run `shadow_triggered_false_positive_probe_v0`
  - [x] 33.1 RED: Add shadow-evidence expectations for per-category payload preservation outcomes and `deck_visible_with_marker_entity_loss` candidate flags.
  - [x] 33.2 GREEN: Extend `pre_step6_shadow_portfolio_evidence.py` to load full payload-omission gates, record marker/entity-loss outcomes, and aggregate candidate flags without changing runtime visibility.
  - [x] 33.3 RED/GREEN: Add `pre_step6_shadow_triggered_false_positive_probe.py` to convert shadow-triggered candidates into a formal false-positive probe contract.
  - [x] 33.4 Run the shadow evidence harness again; fixed-suite cache hits surfaced founder, PhD, and consultant as deck-visible marker/entity-loss candidates.
  - [x] 33.5 Run live Step 6 replay and dual-reviewer adjudication on the shadow-triggered probe.
  - [x] 33.6 RED/GREEN: Tighten the false-positive result contract so reviewer winner arms, non-inferiority reads, and label-consistency tension are recorded and tense `true_visible` cases demote to `ambiguous_visibility`.
  - [x] 33.7 Record the result: founder is `ambiguous_visibility`, PhD and consultant stood down under fresh Step 6 replay, no confirmed false positive, runtime and `SKILL.md` remain blocked.

- [x] 34.0 Run `answer_delta_specificity_v0`
  - [x] 34.1 RED: Add a shadow-runtime test proving additive pressure with only `reframed_emphasis` falls to an answer-delta guardrail rather than `deck_visible_shadow_only`.
  - [x] 34.2 GREEN: Add `derive_answer_delta_specificity` and `anchor_visible_answer_delta_guardrail_shadow_only` to the dormant shadow resolver.
  - [x] 34.3 RED/GREEN: Extend the false-positive Step 6 prompt and static replay fixtures with structured `answer_delta` fields.
  - [x] 34.4 RED/GREEN: Record `answer_delta_specificity` in shadow evidence records and false-positive aggregate results.
  - [x] 34.5 Rerun the shadow evidence harness; old historical additive ledgers now fall to `anchor_visible_answer_delta_guardrail_shadow_only` because they lack structured deltas.
  - [x] 34.6 Run a fresh answer-delta live probe on founder, PhD, and consultant; all three stood down as `all_private_or_confirming`.
  - [x] 34.7 Record the result: structured answer-delta accountability materially reduces ambiguous additive claims without changing runtime or `SKILL.md`.

- [x] 35.0 Run `answer_delta_bridge_rerun_v0`
  - [x] 35.1 RED: Extend the bridge Step 6 replay test so the prompt and replay artifacts require structured `answer_delta` specificity.
  - [x] 35.2 GREEN: Add answer-delta normalization, specificity derivation, and answer-delta guarded policy reads to `pre_step6_bridge_step6_ledger_replay.py` while preserving old artifact validation.
  - [x] 35.3 Run the three original false-standdown bridge cases under the new answer-delta Step 6 prompt.
  - [x] 35.4 Record that all three bridge cases still produce `additive_pressure_present`, `concrete_delta_present`, and `would_unlock_answer_delta_guarded_policy: true`.
  - [x] 35.5 Run the dual-reviewer bridge review against the fresh answer-delta Step 6 `answer_core` outputs.
  - [x] 35.6 Record that both reviewer families still mark hiding those outputs as `false_standdown`, confirming the new guardrail did not over-suppress the original bridge wins.
  - [x] 35.7 Keep runtime promotion and `SKILL.md` blocked; move the next bottleneck to calibration coverage rather than more probe-shaped slices.

- [x] 36.0 Run `calibration_corpus_step6_stability_v0`
  - [x] 36.1 RED: Add a calibration-corpus test requiring a 12-20 case contract with high-clutter, sequencing/problem-shape, sensitive/safety/legal, negative-control, and V60 on/off coverage.
  - [x] 36.2 RED: Add a prompt-surface test proving Step 6 receives broad private material: anchor, deck pressure, V60 context when available, and structured `answer_delta` instructions.
  - [x] 36.3 RED: Add a stability-aggregation test proving n=3 samples classify stable and unstable cases before reviewer adjudication.
  - [x] 36.4 GREEN: Add `pre_step6_calibration_corpus.py` with corpus building, live Step 6 sampling, sample validation, aggregate stability result generation, and runtime-promotion blocks.
  - [x] 36.5 Generate and validate a 17-case calibration corpus with two same-case V60 on/off pairs and explicit synthetic V60 evidence labeling.
  - [x] 36.6 Run 51 live Step 6 samples with `openai/gpt-5.1-chat` across the corpus.
  - [x] 36.7 Record the result: corpus floor met, but Step 6 stability floor not met; 10 cases stable, 7 unstable, reviewer phase blocked by `stability_review_required_before_reviewer_phase`.
  - [x] 36.8 Keep runtime promotion and `SKILL.md` blocked; move the next bottleneck to no-redesign stability review of the unstable cases.

- [x] 37.0 Run `calibration_corpus_unstable_repeat_v0`
  - [x] 37.1 RED: Add a stability-review test that classifies saved samples into stable positive, stable stand-down, borderline unlock, abstract-additive-only, and unstable mixed buckets.
  - [x] 37.2 GREEN: Extend `pre_step6_calibration_corpus.py` with `calibration-stability-review.v1` generation and validation.
  - [x] 37.3 Generate the first stability-review artifact from the 51 saved calibration samples.
  - [x] 37.4 Record that the reviewer phase remains blocked and seven unstable cases require same-prompt repeat sampling.
  - [x] 37.5 Run 21 live repeat Step 6 samples for the seven unstable cases with the same prompt and model.
  - [x] 37.6 Generate and validate the repeat stability-review artifact.
  - [x] 37.7 Record the result: two cases resolved, five remained unstable or borderline, with the persistent issue concentrated in high-clutter/reframe-only answer-delta custody.
  - [x] 37.8 Keep runtime promotion and `SKILL.md` blocked; move next learning to a narrow reviewer diagnostic over saved samples, not another deterministic gate.

- [x] 38.0 Run `calibration_reframe_diagnostic_review_v0`
  - [x] 38.1 RED: Add a diagnostic-review test requiring saved-sample contract selection, stable anchors, reframe-only diagnostics, and runtime-promotion blocks.
  - [x] 38.2 RED: Add a blind-review packet test proving candidate arm labels are hidden while diagnostic role and answer-delta custody remain visible.
  - [x] 38.3 RED: Add a two-family result test proving consistent non-inferior Step 6 judgments become `reframe_useful`.
  - [x] 38.4 GREEN: Add `pre_step6_reframe_diagnostic_review.py` with contract generation, live reviewer support, judgment validation, label/winner consistency, and aggregate result generation.
  - [x] 38.5 Generate the 10-sample diagnostic contract from saved calibration and repeat-unstable samples.
  - [x] 38.6 Run 20 live reviewer calls across `openai/gpt-5.1-chat` and `google/gemini-3.1-flash-lite`.
  - [x] 38.7 Record the result: 2 reframe-only samples confirmed useful/non-inferior, 0 confirmed correctly suppressed, 6 ambiguous records, and 5 tension records.
  - [x] 38.8 Keep runtime promotion and `SKILL.md` blocked; move next learning to `answer_delta_structural_delta_design_v0` rather than loosening the guardrail directly.

- [x] 39.0 Run `answer_delta_structural_delta_design_v0`
  - [x] 39.1 RED: Add shadow-resolver and bridge-replay tests proving a specific `structural_delta` can unlock separately from generic `reframed_emphasis`.
  - [x] 39.2 RED: Add prompt-surface tests proving Step 6 sees `structural_delta` in bridge, false-positive, and calibration prompt contracts.
  - [x] 39.3 GREEN: Extend `answer_delta` with `structural_delta` across the dormant shadow resolver and research scripts while preserving runtime-promotion blocks.
  - [x] 39.4 GREEN: Add a specificity bar so vague entries like `added structural framing` remain `reframe_only`.
  - [x] 39.5 GREEN: Extend calibration aggregation to track structural-delta-only frequency and structural-delta field usage frequency separately.
  - [x] 39.6 Run focused tests proving structural deltas unlock mechanically, generic framing stays blocked, and false-positive/static fixtures normalize the new field.
  - [x] 39.7 Run a small live diagnostic with `moonshotai/kimi-k2.6`: founder and PhD positive triplets, one startup sample, and a three-sample Bevelin irrelevant-incentives negative control.
  - [x] 39.8 Record the result: 7/10 samples unlocked with concrete deltas and structural field usage, 0 structural-only live samples observed, 0 reframe-only samples, and the negative control stood down 3/3.
  - [x] 39.9 Keep runtime promotion and `SKILL.md` blocked; declare this the last vocabulary repair before full calibration.

- [x] 40.0 Close the structural-delta repair prerequisite
  - [x] 40.1 Pin the calibration Step 6 model to `moonshotai/kimi-k2.6` in the calibration corpus manifest.
  - [x] 40.2 Rerun the two prior reframe-useful samples under the repaired prompt: founder V60-on sample 0 and PhD V60-off sample 2.
  - [x] 40.3 Generate targeted rerun samples, aggregate result, stability review, and readout.
  - [x] 40.4 Record that both reruns became `additive_pressure_present` / `concrete_delta_present` with `structural_delta` populated, and neither remained `reframe_only`.
  - [x] 40.5 Preserve the constraint: pure `structural_delta_present` remains unobserved and must be measured in full calibration, not forced by another vocabulary patch.

- [x] 41.0 Run repaired Kimi full calibration corpus
  - [x] 41.1 RED/GREEN: Harden the calibration runner for resumable live sampling, outer per-sample timeout handling, retryable `IncompleteRead` failures, and stale error-log clearing.
  - [x] 41.2 RED/GREEN: Mark partial `n<3` case results as `incomplete_sampling` rather than stable evidence.
  - [x] 41.3 Run the full 17-case corpus with `moonshotai/kimi-k2.6`, the repaired `structural_delta` prompt, and saved sample custody.
  - [x] 41.4 Fill incomplete samples through targeted resume retries until the planned 51-sample corpus is complete.
  - [x] 41.5 Repeat the four variable cases under the same prompt and model, producing 12 additional repeat samples.
  - [x] 41.6 Generate and validate the final aggregate result and stability review from 63 saved samples.
  - [x] 41.7 Record the result: 13 stable cases, 4 variable cases, 0 reframe-only samples, 38 structural-delta field uses, and 0 pure structural-only live unlocks.
  - [x] 41.8 Keep runtime promotion and `SKILL.md` blocked; allow only a partitioned reviewer phase over the 13 stable cases while quarantining the four variable cases for Step 6 ledger-stability design review.

- [x] 42.0 Run stable-partition reviewer phase
  - [x] 42.1 RED: Add tests proving only stable cases enter the reviewer phase and variable cases remain excluded.
  - [x] 42.2 GREEN: Add `pre_step6_partitioned_reviewer_phase.py` with blinded reviewer packets, strict JSON judgments, two-family result aggregation, and runtime-promotion blocks.
  - [x] 42.3 Generate the stable-partition reviewer contract from the repaired Kimi stability review.
  - [x] 42.4 Run 26 live reviewer calls across `openai/gpt-5.1-chat` and `google/gemini-3.1-flash-lite`.
  - [x] 42.5 Record the result: all 6 stable positives supported, 6/7 stable stand-downs supported, 1 benign ambiguity, 0 rejections, 0 label/winner tension.
  - [x] 42.6 Keep runtime promotion and `SKILL.md` blocked because variable cases still need an answer.

- [x] 43.0 Run variable-case ledger-stability diagnostic
  - [x] 43.1 RED: Add tests proving the diagnostic selects the four quarantined variable cases and blocks runtime promotion.
  - [x] 43.2 GREEN: Add `pre_step6_variable_case_diagnostic.py` to summarize ledger distributions, answer-delta distributions, answer-core variance, V60 metadata, and sample observations.
  - [x] 43.3 Generate the Kimi variable-case diagnostic result from 24 saved samples.
  - [x] 43.4 Run a targeted alternative-model probe with `openai/gpt-5.1-chat` on the four variable cases.
  - [x] 43.5 Record the result: Kimi variable cases include answer-level variance; GPT stabilizes consultant as stand-down and PhD cases as visibility-positive while founder V60-on remains variable.
  - [x] 43.6 Record the structural-delta update: GPT produced five pure `structural_delta_present` samples, so the structural-delta path is now observed in live samples.
  - [x] 43.7 Keep global shadow implementation blocked; move next bottleneck to model-family and answer-core review for variable cases.

- [x] 44.0 Run model-family and V60 review
  - [x] 44.1 RED: Add tests proving the founder V60 symmetry contract is research-only, precommits outcomes, and blocks runtime promotion.
  - [x] 44.2 GREEN: Add `pre_step6_founder_v60_symmetry_check.py` to compare saved Kimi/GPT founder V60-on/off samples without deciding answer wisdom.
  - [x] 44.3 Run fresh Kimi founder V60-off samples to n=6 and fresh GPT founder V60-off samples to n=3.
  - [x] 44.4 Generate the founder symmetry contract and result; record that both model families are variable on V60-on and stable on V60-off.
  - [x] 44.5 RED: Add tests proving the GPT-stability review selects exactly the GPT-stable outputs, separates answer correctness from visibility correctness, and correctly treats reviewer-visible judgments as anchor rejection when expected stand-down was anchor.
  - [x] 44.6 GREEN: Add `pre_step6_gpt_stability_correctness_review.py` with the split rubric, two-family reviewer aggregation, structural-delta-only tracking, and runtime-promotion blocks.
  - [x] 44.7 Run 18 live reviewer calls over the nine GPT-stable saved outputs.
  - [x] 44.8 Record the result: PhD GPT-visible outputs supported 6/6, pure `structural_delta_present` supported 3/3, consultant GPT anchor stand-down had 1 rejection, 2 ambiguities, and 1 tense record.
  - [x] 44.9 Update the PRD, autoresearch program, integration design draft, and readout with the model-commitment rule: model-family stability is evidence, not authority; any model/provider/backend change is a recalibration event.
  - [x] 44.10 Keep `SKILL.md`, runtime promotion, and global shadow implementation blocked.

- [x] 45.0 Run `founder_v60_private_context_audit_v0`
  - [x] 45.1 RED: Add a focused contract test proving the audit exits the pre-Step-6 perimeter, names explicit limits, queues Consultant/PhD follow-ups, and blocks runtime promotion.
  - [x] 45.2 RED: Add a focused result test proving the audit characterizes V60-on destabilization without deciding Founder answer correctness.
  - [x] 45.3 GREEN: Add `pre_step6_founder_v60_private_context_audit.py` with contract/result validation, saved-sample reading, mechanical relevance checks, and separate outcome-evidence channels.
  - [x] 45.4 Generate and validate the Founder V60 private-context audit contract and result artifacts.
  - [x] 45.5 Record the result: V60 context is related to Founder but destabilizing; `joint_overload` and genuine-edge-pressure interpretations are plausible, selection-noise is weak, and cross-chunk diagnosis is insufficient.
  - [x] 45.6 Update PRD, autoresearch program, task list, and readout while keeping `SKILL.md`, runtime promotion, and global shadow implementation blocked.
  - [x] 45.7 Queue `consultant_case_ambiguity_design_review_v0` and `kimi_phd_variance_diagnostic_v0` as separate follow-ups so the Founder V60 audit does not absorb heterogeneous variance findings.

- [x] 46.0 Run `consultant_deck_composition_review_v0`
  - [x] 46.1 RED: Add a focused contract test proving the Consultant slice is a cleaning review, not a visibility-gate review.
  - [x] 46.2 RED: Add a focused result test proving the slice characterizes Kimi/GPT Consultant variance, V60 absence, and deck-material quality without policy promotion.
  - [x] 46.3 GREEN: Add `pre_step6_consultant_deck_composition_review.py` with saved-artifact loading, deck-material analysis, sample-stability summary, reviewer-feedback summary, and hypothesis evidence.
  - [x] 46.4 Generate and validate the Consultant deck-composition contract and result artifacts.
  - [x] 46.5 RED/GREEN: Add `consultant_cleaning_variant_v0` as a research-only variant that keeps the anchor as backbone and converts broad lens pressure into three concrete micro-cards.
  - [x] 46.6 Generate and validate `consultant-cleaning-variant.v1.json`.
  - [x] 46.7 Record the result: anchor is strong, deck pressure is thin but useful, V60 is not active, and the next step is replaying the cleaner table rather than adding a gate.
  - [x] 46.8 Keep `SKILL.md`, runtime promotion, global shadow implementation, and model-routing blocked.

- [x] 47.0 Run `consultant_cleaning_variant_replay_v0`
  - [x] 47.1 RED: Add focused tests proving the replay contract is research-only, prompt composition passes concrete micro-cards without broad Bevelin/Polya labels, and the result measures consideration stability.
  - [x] 47.2 GREEN: Add `pre_step6_consultant_cleaning_variant_replay.py` with contract/sample/result validation, live Step 6 replay support, micro-card signal derivation, answer-delta specificity checks, and protected-payload presence checks.
  - [x] 47.3 Generate and validate the replay contract.
  - [x] 47.4 Run six completed live Step 6 samples with `moonshotai/kimi-k2.6`; record sample `4` as stalled twice and use replacement sample `6`.
  - [x] 47.5 Generate and validate the aggregate replay result.
  - [x] 47.6 Record the result: the cleaned table preserved protected payload in 6/6 samples, improved legibility, and narrowed the recurring useful delta to the counsel-gated reversibility boundary, but consideration remains mixed at 4/6 additive and 2/6 private/confirming.
  - [x] 47.7 Keep `SKILL.md`, runtime promotion, global shadow implementation, deterministic selectors, and model-routing blocked.
  - [x] 47.8 Queue `consultant_anchor_boundary_patch_probe_v0` as a cleaning follow-up, not a visibility-gate follow-up.

- [x] 48.0 Run `consultant_anchor_boundary_patch_probe_v0`
  - [x] 48.1 RED: Add focused tests proving the probe is a graduation-hypothesis test, not patch architecture; pins the one-phrase patch, same three micro-cards, five-question preflight, and four-state outcome schema.
  - [x] 48.2 GREEN: Add `pre_step6_consultant_anchor_boundary_patch_probe.py` with contract/sample/result validation, minimal anchor patching, live Step 6 replay support, reversibility-card additive detection, patched-boundary detection, and protected-payload checks.
  - [x] 48.3 Generate and validate the patch-probe contract.
  - [x] 48.4 Run six live Step 6 samples with `moonshotai/kimi-k2.6`; record that sample `2` needed one longer-timeout retry and sample `4` needed one invalid-output retry.
  - [x] 48.5 Generate and validate the aggregate patch-probe result.
  - [x] 48.6 Record the result: patched boundary present in 6/6, protected payload preserved in 6/6, all micro-cards stood down in 5/6, reversibility card additive fell from 4/6 to 1/6, `upstream_pressure_carried=yes`, Consultant classification `graduation_candidate`.
  - [x] 48.7 Stop Consultant refinement for this research chapter; queue `consultant_upstream_origin_investigation_v0` as a separate upstream-origin finding, not a patch layer.
  - [x] 48.8 Keep `SKILL.md`, runtime promotion, global shadow implementation, deterministic selectors, and model-routing blocked.

- [x] 49.0 Run `phd_kimi_variance_cleaning_review_v0`
  - [x] 49.1 RED: Add focused tests proving the PhD review is research-only, uses V60-off to avoid V60 confounds, passes concrete atomic PhD cards without broad Bevelin/Polya labels, and blocks runtime/skill promotion.
  - [x] 49.2 GREEN: Add `pre_step6_phd_kimi_variance_cleaning_review.py` with contract/sample/result validation, live Step 6 replay support, micro-card signal derivation, answer-delta specificity checks, and protected-payload checks.
  - [x] 49.3 Add an opt-in `LOLLA_OPENROUTER_DISABLE_REASONING` boundary-client switch and set it only for this research script after the first Kimi call hung at the provider/model layer.
  - [x] 49.4 Generate and validate the PhD cleaning-review contract.
  - [x] 49.5 Run six live Step 6 samples with `moonshotai/kimi-k2.6`, OpenRouter, and research-script reasoning disabled.
  - [x] 49.6 Tighten the aggregate classification so cross-sample use of all cards still counts as discrimination when each run uses only a subset.
  - [x] 49.7 Generate and validate the aggregate result.
  - [x] 49.8 Record the result: 6/6 samples marked at least one micro-card additive, protected payload was preserved in 6/6, and atom selection was distributed across cards rather than one Consultant-style graduation candidate.
  - [x] 49.9 Keep `SKILL.md`, runtime promotion, global shadow implementation, deterministic selectors, model-routing, and automatic graduation blocked.
  - [x] 49.10 Queue `evidence_surface_v0` as the final stop-boundary slice before closeout.

- [x] 50.0 Build `evidence_surface_v0`
  - [x] 50.1 RED: Add focused tests proving the evidence surface is research-only, runtime-dormant, blocks automatic graduation, and encodes "code may nominate; humans decide."
  - [x] 50.2 RED: Add tests proving the surface nominates the Consultant reversibility-until-counsel atom for human review while marking PhD atoms as distributed watch items, not graduation candidates.
  - [x] 50.3 GREEN: Add `pre_step6_cleaning_evidence_surface.py` to aggregate Consultant and PhD cleaning results into case summaries, atom rows, and graduation candidates.
  - [x] 50.4 Generate `cleaning-evidence-surface.v1.json` and a human-readable `cleaning-evidence-surface.md`.
  - [x] 50.5 Record the result: the surface makes recurring pressure atoms readable without deciding wisdom, moving cards upstream, changing runtime visibility, or touching `SKILL.md`.
  - [x] 50.6 Move to closeout decision document; no further probe-shaped slices before closeout.

- [x] 51.0 Write cleaning research closeout
  - [x] 51.1 Create `research/pre-step6-cleaning-research-closeout-2026-05-22.md`.
  - [x] 51.2 Record what was built: custody contracts, probe/calibration evidence, cleaning-lane slices, and evidence surface.
  - [x] 51.3 Record what was learned: Consultant has one human-review graduation candidate; PhD has distributed atomic discrimination; Founder V60 is a separate V60 handoff; model commitment includes call configuration.
  - [x] 51.4 Define what must not be automated: card graduation, upstream migration, lens relevance, model selection as correctness, recurrence-based visibility, and borderline suppression.
  - [x] 51.5 Define shadow implementation concretely as dormant production-adjacent recording behind `LOLLA_STEP6_PORTFOLIO=off|shadow|on`, default `off`, with no visible answer change.
  - [x] 51.6 Make the stop decision: research chapter complete; dormant shadow implementation allowed only as a separate program; runtime-on and `SKILL.md` behavior changes blocked; more probe-shaped research not recommended.
