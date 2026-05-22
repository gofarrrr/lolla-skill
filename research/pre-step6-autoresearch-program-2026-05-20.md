# Pre-Step-6 Autoresearch Program

Date: 2026-05-20

Status: research-only operating program. This file does not change `SKILL.md`,
runtime behavior, default `/lolla`, or promotion policy.

## Why This Exists

Karpathy's `autoresearch` pattern is useful because it treats research as an
iterated experiment loop:

```text
change one thing -> run a fixed evaluation -> log result -> keep, discard, or
retest -> repeat
```

For Lolla, the target is not a lower training loss. The target is better
private context for Step 6:

```text
more useful reasoning material, less public bloat, less premature pruning,
better preservation of off-frame edge pressure.
```

The loop must preserve Lolla's values:

```text
Enrichment over narrowing.
Depth and breadth over premature neatness.
Compact representation, not compact possibility.
Step 6 remains the solver.
Pre-Step-6 improves what Step 6 receives; it does not do Step 6's job.
```

## Autoresearch Translation

| Autoresearch concept | Lolla adaptation |
| --- | --- |
| `program.md` tells the agent how to research | this file tells agents how to iterate on pre-Step-6 context design |
| `train.py` is the only edited research target | research-only fixtures, validators, prompts, and readouts are the editable target |
| fixed 5-minute training budget | fixed case suite and fixed rubric budget |
| `val_bpb` decides keep/discard | multi-criterion quality/readout decides keep/retest/discard |
| `results.tsv` logs experiments | `research/pre-step6-autoresearch-ledger-*.tsv` or readout addenda log experiments |
| reset losing code | keep losing research fixtures only if they teach a boundary or falsifier |

## In-Scope Files

Agents may edit research-only files:

- `research/pre-step6-*.md`
- `research/pre-step6-*/*.json`
- `scripts/research/pre_step6_*.py`
- `tests/test_pre_step6_*.py`
- `tasks/tasks-step6-reasoning-portfolio.md`

Agents must not edit during this loop:

- `SKILL.md`
- runtime/default `/lolla` behavior
- product docs
- canonical knowledge base files
- non-research pipeline code

Any exception requires a separate promotion decision.

## Fixed Evaluation Suite

Every serious experiment must be evaluated against at least:

- `founder-grant-marcus-equity.high-clutter`
- `third-year-phd-student` or `third-year-phd-student.v2`
- `mid-level-consultant-report-2`
- `mother-address-year`

Roles:

- Founder: high-clutter positive case where portfolio should preserve edge
  pressure better than raw dumping or compact hybrid flattening.
- PhD: live-tension case where active/parked placement matters.
- Consultant: negative control where rendered hybrid may already be enough and
  portfolio must be willing to stop.
- Mother: humane/weak-evidence negative-control case where extra machinery can
  easily overburden the answer.

## Fixed Rubric

Each experiment must compare against the previous best using these criteria:

- decision usefulness
- source grounding
- overclaim risk
- answer length / cognitive load
- machinery hygiene
- conflict preservation
- duplicate demotion
- unforcedness
- edge pressure preservation
- reserve overuse
- premature pruning risk
- breadth/depth preservation
- negative-control discipline

The tie-break rule:

```text
New machinery must beat, materially simplify, or preserve important edge
pressure the previous best flattened. Otherwise it does not promote.
```

## Experiment Loop

Loop one experiment at a time:

1. Name a hypothesis.
2. Identify the smallest research-only change that tests it.
3. Add or update one fixture/test/readout slice.
4. Run the focused tests.
5. Compare against previous best cases.
6. Record the result as `keep`, `retest`, `discard`, or `boundary_case`.
7. Keep research evidence even when the result loses, if it teaches a boundary.
8. Do not edit `SKILL.md` or runtime defaults unless a separate promotion gate
   is opened.

## Result Status

Use these statuses:

- `keep`: improves or simplifies without violating values.
- `retest`: promising but not enough; needs another case, replay, or lens.
- `discard`: worsens quality, bloat, grounding, or negative-control discipline.
- `boundary_case`: loses but teaches where the system should stand down.
- `crash`: invalid schema, broken test, leaked private machinery, or unusable
  output.

## Keep / Discard Rules

Keep an experiment only if:

- it improves at least one positive case without regressing negative controls;
- it preserves source-grounded off-frame pressure with receipts;
- it does not replace Step 6 judgment with pre-Step-6 conclusions;
- it keeps public-answer machinery hidden;
- it improves or preserves answer naturalness;
- it leaves a clear falsifier.

Discard or retest if:

- it optimizes for compactness by deleting useful edge pressure;
- it forces every lens into active context;
- it turns Bevelin, Polya, or any lens pack into a public taxonomy;
- it makes the deterministic layer decide the final answer;
- it wins only by adding more prompt mass;
- it over-promotes on mother or future negative-control cases;
- a consultant-triggered false-positive probe overturns the current positive
  classification.

## Research Values

The loop must protect these values even when they conflict with simplicity:

- Preserve broad source-backed optionality.
- Delay rejection until Step 6 has enough context to decide.
- Prefer scan/parked receipts over deletion.
- Keep false friends visible as false friends, not silently removed.
- Treat noise as sometimes useful, but make forcing risks explicit.
- Use caps to control prose length, not intellectual range.
- Let losing cases teach the gate.

## Lens Pack Policy

Bevelin is the first lens pack to test, not the architecture.

Allowed lens packs:

- `bevelin_seeking_wisdom_v0`
- `polya_problem_solving_v0`
- future private presets with source-grounded boundaries

Rules:

- Lens packs produce reasoning affordances, not final advice.
- Lens packs must include `risk_if_forced` and `risk_if_ignored`.
- Lens packs must preserve at least one off-narrative candidate when
  source-grounded.
- Lens packs must include `do_not_force` guidance.
- Lens outputs must be evaluated against negative controls.

## Prompt Budget Policy

Start with four small prompt templates:

1. Problem Read
2. Artifact Affordance Mapper
3. Lens Pack Probe
4. Anti-Pruning / Diversity Critic

Do not combine them into one broad prompt. The Sully/context-engineering lesson
still applies: small targeted calls are easier to evaluate and less likely to
produce brittle prompt bloat.

## Logging Template

Use a TSV or readout table with these columns:

```text
experiment_id	status	cases_changed	quality_read	breadth_read	bloat_read	negative_control_read	next_step	description
```

Example:

```text
bevelin_v0_founder_phd_consultant	retest	founder,phd,consultant	improves founder/phd edge pressure	preserves off-frame denominator and Silva constraints	no public bloat	consultant must still stop	run static fixtures	Add Bevelin lens probe as private affordance source
```

## Current Next Decision

The design-preamble research contracts now exist. The current bottleneck is not
another schema by default; it is calibration coverage.

Current finding:

```text
The four-case suite is a seed suite, not calibration. Runtime promotion remains
blocked until false-standdown recall and case-type coverage are measured.
```

Evidence now available:

- Cost/cache miss behavior: normal runtime cache misses stand down with 0 net
  new LLM calls.
- Generic private-card interface: Bevelin, Polya, clean hybrid, and a synthetic
  future card validate through one schema.
- Unified private-consideration ledger: hot-context dedupe preserves source
  custody and negative-shape fixtures prove dedupe is conditional.
- Payload omission gate: six protected categories are checked as a post-visibility
  tripwire, not as an answer selector.
- Visibility asymmetry: runtime is explicitly deck-private/anchor-biased when
  unresolved; research/experimental retest is bounded.
- Calibration floor: current coverage is 4 seed cases, below the required 12-20
  cases, with 0 V60 on/off pairs.
- V60 on/off pair origin: a valid pair means the same case run twice with the
  same prompt contract and card-deck policy, once with V60 selected items
  available and once with those items withheld. Substantive-vs-minimal V60 is a
  useful stratum, not a substitute.
- Payload preservation caveat: the omission gate can currently preserve a
  category marker while losing concrete anchor entities inside that category.
  Calibration must track this as
  `preserved_by_marker_anchor_entities_missing`.

Next valid moves:

- `false_standdown_bridge_probe_v0` has now run and triggered
  `design_review_required`: all three pre-registered bridge cases were
  confirmed `false_standdown` by two reviewer families.
- `design_preamble_visibility_policy_redesign_v0` has now run as a policy
  contract: Step 6's private ledger can surface deck-aware output when it records
  additive pressure and protected payload is preserved, with no runtime reviewer
  loop.
- `bridge_step6_ledger_replay_v0` has now run on the three bridge packets with
  `openai/gpt-5.1-chat`: all three produced
  `ledger_signal: additive_pressure_present`, and the aggregate result is
  `step6_additive_signal_supported`.
- The redesigned policy now has live bridge-replay support for its ledger
  dependency, but this is still packet-level evidence rather than full runtime
  promotion evidence.
- `pre-step6-ledger-mediated-integration-design-draft-2026-05-21.md` now pins
  the dormant integration shape: broad private deck, Step 6 answer plus ledger,
  deterministic guards, visibility resolver, archive fields, Observatory view,
  cost envelope, promotion gates, and falsifiers.
- `false_positive_visibility_probe_v0` has now run: Step 6 stood down on the
  tempting Bevelin and Polya overpromotion cases, and the marker/entity-loss
  dimension is `not_observed` rather than passed.
- `marker_entity_loss_followup_v0` has now run: three focused construction
  attempts all produced `all_private_or_confirming`; Step 6 preserved concrete
  anchor entities and kept generic deck pressure private/confirming.
- The marker/entity-loss failure shape remains technically `not_observed`, but
  the highest-risk construction attempts did not produce overpromotion.
- Next engineering move, if approved, should be an ultra-dormant
  flags/archive/validation slice with visibility shadow-only. Runtime promotion
  remains blocked.
- `ultra_dormant_shadow_portfolio_integration_v0` has now landed as the
  approved engineering move: default-off shadow flag, cached-only deck lookup,
  Step 6 ledger-signal recording, payload/custody guardrail recording, sidecar
  archive support, and Observatory/API visibility. It adds no runtime reviewer
  calls, performs no live card generation, applies nothing to visible output,
  and leaves `SKILL.md` behavior unchanged.
- The next learning move is to run real cases in shadow mode first with cache
  misses, then with precomputed decks for the fixed suite, and inspect whether
  the archives teach us anything before any Step 6 prompt integration.
- `shadow_evidence_run_v0` has now run. Eight prior result artifacts all stood
  down cleanly on cache miss. The fixed-suite cache-hit arm reproduced the
  research pattern: founder, PhD, and consultant produced
  `deck_visible_shadow_only`; mother produced
  `anchor_visible_deck_private_shadow_only`; all visible applications remained
  zero.
- This confirms shadow mode can gather policy evidence without becoming a
  selector. The new bottleneck is cache coverage and broader Step 6 ledger
  behavior, not the runtime plumbing.
- `consultant_triggered_false_positive_probe_v0` has now run. Consultant was
  corrected from `negative_control_seed` to `sensitive_safety_legal` /
  `positive_seed` before the probe. Live Step 6 replay emitted
  `additive_pressure_present`; both reviewer families returned `true_visible`;
  Bevelin temptation stood down; marker/entity loss remained `not_observed`.
- The shadow harness therefore did the right job: it surfaced a probe candidate.
  The dual-reviewer probe then adjudicated it and did not find a false positive.
- `shadow_triggered_false_positive_probe_v0` has now run. The harness was
  extended to record per-category payload-preservation outcomes and flag
  `deck_visible_with_marker_entity_loss`. Founder, PhD, and consultant surfaced
  as candidates. Fresh Step 6 stood down on PhD and consultant; founder emitted
  `additive_pressure_present`, but the aggregate result is
  `continue_probe_with_ambiguity` because reviewer labels and blind winner arms
  were tense.
- The new custody rule is important: reviewer labels are not accepted alone.
  The result builder records winner arms, non-inferiority reads, and label
  consistency; tense `true_visible` cases become `ambiguous_visibility`.
- `answer_delta_specificity_v0` has now run. Step 6 ledger items can carry
  structured `answer_delta` arrays: `added_entities`, `removed_entities`,
  `reordered_sequences`, and `reframed_emphasis`. The shadow resolver now
  blocks additive ledgers unless a concrete delta is present.
- Rerunning the shadow evidence harness changed old fixed-suite additive replay
  cases from `deck_visible_shadow_only` to
  `anchor_visible_answer_delta_guardrail_shadow_only`, because those historical
  ledgers lacked structured deltas.
- A fresh answer-delta live probe on founder, PhD, and consultant produced
  `all_private_or_confirming` for all three. When Step 6 had to account for the
  concrete public delta, it stopped making the ambiguous additive claim.
- `answer_delta_bridge_rerun_v0` has now run against the three original
  false-standdown bridge cases. All three still produced
  `additive_pressure_present` and `concrete_delta_present` under the structured
  answer-delta prompt, so the answer-delta guarded policy would unlock them.
- The dual-reviewer bridge review also preserved the original finding: both
  reviewer families labeled hiding the fresh Step 6 answer behind the anchor as
  `false_standdown` on all three cases. In this rerun, that is a positive
  verification signal because the guarded policy would not hide those outputs.
- `calibration_corpus_step6_stability_v0` has now run as the next corpus-level
  gate. The calibration corpus has 17 pre-registered cases, including high
  clutter, sequencing/problem-shape, sensitive/safety/legal, negative controls,
  and two same-case V60 on/off pairs. It produced 51 live Step 6 samples with
  `openai/gpt-5.1-chat`.
- The corpus floor is met, but the Step 6 stability floor is not. Ten cases are
  stable and seven are unstable. False-positive controls, mother, consultant,
  and two bridge wins behaved cleanly; high-clutter and V60-pair cases carried
  most of the variance. Aggregate read:
  `stability_review_required_before_reviewer_phase`.
- Do not run reviewer adjudication yet. The next move is a no-redesign
  stability review over the saved 51 samples, so reviewer cognition does not get
  mixed with sampling noise.
- The no-redesign stability review has now run and repeat-sampled the seven
  unstable cases with the same Step 6 prompt and model. Two cases resolved:
  `marker-entity-attempt-1-resource-generalization` became stable stand-down,
  and `third-year-phd-student.v2.v60-on` became stable positive.
- Five cases remain unstable or borderline. The pattern is concentrated in
  high-clutter/V60-adjacent cases where Step 6 often sees additive pressure but
  expresses the visible change as `reframed_emphasis` rather than concrete
  `added_entities`, `removed_entities`, or `reordered_sequences`.
- Do not keep blindly repeating samples and do not add a new deterministic
  gate. The next learning move is `calibration_reframe_diagnostic_review_v0`:
  a narrow reviewer diagnostic over saved samples to test whether reframe-only
  outputs are genuinely useful or correctly suppressed by the answer-delta
  guardrail.
- `calibration_reframe_diagnostic_review_v0` has now run against 10 saved
  samples: 3 stable controls and 7 reframe-only diagnostics. Two reviewer
  families reviewed each sample under blind shuffle.
- The result is `answer_delta_vocabulary_design_review_required`. Two
  reframe-only samples were confirmed useful/non-inferior; no reframe-only
  sample was confirmed correctly suppressed; six records were ambiguous and
  five had reviewer label/winner-arm tension.
- The interpretation is narrow: do not loosen the guardrail in runtime. The
  current vocabulary is probably missing a way for Step 6 to record concrete
  structural reasoning changes, such as decision boundaries, stop conditions,
  test designs, or commitment-shape changes, without pretending those are
  added entities.
- Next move: `answer_delta_structural_delta_design_v0`, research-only. Generic
  `reframed_emphasis` should still not unlock. A new structural-delta field
  should be tested on the persistent samples before any broader calibration.

- `answer_delta_structural_delta_design_v0` has now run as the last planned
  pre-calibration vocabulary repair. The `answer_delta` schema now includes
  `structural_delta` for specific structural public-answer changes such as stop
  conditions, unlock conditions, decision boundaries, test designs, commitment
  boundaries, sequencing gates, and deadline/window logic.
- The specificity bar remains mechanical: vague entries such as `added
  structural framing` do not unlock and remain `reframe_only`. Runtime and
  `SKILL.md` stay dormant.
- A small live diagnostic produced 10 samples: founder V60-on 3/3 positive,
  PhD V60-off 3/3 positive, startup 1/1 positive, and the Bevelin
  irrelevant-incentives negative control 3/3 stand-down. Aggregate:
  `unlock_sample_count = 7`, `reframe_only_sample_count = 0`,
  `structural_delta_field_sample_count = 7`, and
  `structural_delta_sample_count = 0`.
- Interpretation: Step 6 naturally used the new `structural_delta` field, but
  the live positives also named concrete added payload, so pure
  `structural_delta_present` remains unobserved in live samples. The repair is
  still useful because it gave Step 6 a more precise reporting language without
  creating an obvious false-positive loophole on the negative control.
- Next move: rerun the full calibration corpus under the repaired prompt
  contract. Track unlock frequency, reframe-only frequency,
  structural-delta-only frequency, structural-delta field usage, n=3 Step 6
  stability, and reviewer label/winner-arm tension. Do not add more vocabulary
  fields before calibration; another missing category should trigger design
  review, not another quick patch.

- `answer_delta_structural_delta_targeted_rerun_v0` has now closed the small
  evidence gap from the structural-delta diagnostic. The two prior
  reframe-useful samples were rerun under the repaired prompt:
  `founder-grant-marcus-equity.high-clutter.v60-on` sample 0 and
  `third-year-phd-student.v2.v60-off` sample 2.
- Both reruns produced `additive_pressure_present` and
  `concrete_delta_present`, with `structural_delta` populated. Neither stayed
  trapped as `reframe_only`. Pure `structural_delta_present` is still
  unobserved in live samples, so full calibration must track it explicitly.
- The calibration Step 6 model is pinned to `moonshotai/kimi-k2.6`. The repaired
  diagnostic and targeted rerun both used this model, and the OpenRouter env
  default returned `404` during the first live attempt. Do not blend Kimi,
  GPT-family, or other model-family samples inside one calibration read.
- The repaired Kimi calibration corpus has now run with 63 saved Step 6
  samples: 51 planned samples plus 12 same-prompt repeats on variable cases.
  The corpus floor is met and no samples remain incomplete.
- Aggregate: 13 stable cases, 4 unstable cases, 33 unlock samples,
  `reframe_only_sample_count = 0`,
  `structural_delta_field_sample_count = 38`, and
  `structural_delta_sample_count = 0`.
- The stable partition is meaningful: the three original bridge wins stayed
  stable positive; mother and false-positive controls stayed stable stand-down;
  generic Bevelin/Polya pressure did not become visible merely because
  `structural_delta` exists.
- The remaining blocker is now precise Step 6 ledger variance, not answer-delta
  vocabulary. Four cases flip under the same Kimi prompt:
  founder V60-on 4/6 unlock, consultant 3/6 unlock, PhD V60-off 3/6 unlock,
  and PhD V60-on 5/6 unlock.
- Do not move to shadow implementation globally and do not add another
  deterministic selector. The next safe move is a partitioned reviewer phase
  over the 13 stable cases only, while quarantining the four variable cases for
  Step 6 ledger-stability design review.
- The partitioned reviewer phase has now run with two blinded reviewer
  families over the 13 stable cases. All 6 stable-positive cases were supported
  by both reviewers. Stable stand-downs had 6 supported, 0 rejected, and 1
  benign ambiguity where the answers differed only by "specific" before
  "tripwires." There was no label/winner tension.
- The variable-case diagnostic shows all four quarantined Kimi cases have
  answer-level variance, not merely ledger-label variance. Kimi unlock ratios:
  founder V60-on 4/6, consultant 3/6, PhD V60-off 3/6, PhD V60-on 5/6.
- A targeted `openai/gpt-5.1-chat` alternative-model probe showed the variance
  is partly model-family-sensitive: consultant became stable stand-down, both
  PhD cases became visibility-stable positive, and founder V60-on remained
  variable.
- The alternative-model probe also produced five pure
  `structural_delta_present` live samples, so the structural-delta path is no
  longer theoretical and should not be collapsed away.
- The next design bottleneck is model-family and answer-core review for variable
  cases, especially founder V60-on. Do not add a deterministic selector to hide
  this variance.
- `founder_v60_symmetry_check_v0` has now run. Kimi is variable on founder
  V60-on (4/6 unlock) and stable positive on founder V60-off (6/6). GPT is also
  variable on founder V60-on (2/3) and stable stand-down on founder V60-off
  (0/3). Both model families become unstable specifically when V60-on private
  context is present, so the current read is
  `v60_on_specific_destabilization_plausible`. This is a V60/private-context
  audit finding, not a portfolio runtime gate.
- `gpt_stability_correctness_review_v0` has now run with the split reviewer
  rubric. GPT-stable PhD visible outputs were supported 6/6 by two reviewer
  families, including all 3 pure `structural_delta_present` outputs. GPT's
  stable consultant stand-down was not cleanly supported: 1 sample was rejected
  as a wrong anchor-visible decision, 2 were ambiguous, and 1 record had
  label/winner-arm tension.
- Interpretation: model-family stability is useful evidence only when reviewer
  cognition supports it. Do not route to GPT merely because it is more stable.
  Do not use model choice as an unaccountable cognitive shortcut.
- Model commitment is now part of the research contract. Any Step 6 model
  upgrade, provider swap, OpenRouter backend change, or model-family switch is
  a recalibration event. Mixed model-family samples are diagnostic evidence,
  not a single promotion read.
- `founder_v60_private_context_audit_v0` has now run as an explicit V60 audit,
  outside the pre-Step-6 portfolio perimeter. It reads saved Founder V60-on/off
  samples and the V60 private context without running live selection or adding
  any runtime gate.
- The audited V60 chunk is related to Founder through concrete surface overlap
  (`board`, `commitments`, `evidence`), so the current evidence does not support
  a simple "unrelated selection noise" story.
- Aggregate audit read:
  `v60_context_related_but_destabilizing`. Both model families are variable on
  V60-on, neither is variable on V60-off, and V60-off still leaves Kimi/GPT in
  opposite stable directions. Founder answer correctness remains
  `not_decided`.
- Precommitted outcome channels stay distinct:
  `genuine_edge_pressure_structurally_borderline = plausible`,
  `selection_noise = weak`, `joint_overload = plausible`, and
  `cross_chunk_consideration_gap = insufficient`.
- Interpretation: V60 looks individually defensible but destabilizing inside
  the combined private packet. The next V60-facing question is packet
  presentation/selection interaction, not a portfolio-policy gate.
- Consultant and PhD are not resolved by the Founder V60 audit. Queue
  `consultant_case_ambiguity_design_review_v0` and
  `kimi_phd_variance_diagnostic_v0` separately. Do not let the V60 audit absorb
  heterogeneous variance findings.
- `consultant_deck_composition_review_v0` has now run as a cleaning slice, not
  another visibility-gate slice. The question changed from "did the resolver
  choose correctly?" to "did Step 6 receive the right material?"
- The review found `cleaning_read =
  anchor_strong_deck_pressure_thin_but_useful`. Consultant has no V60 context.
  The anchor is strong and carries the counsel-first safety payload; the useful
  deck deltas are small: independent counsel, built-in channel-bias checking,
  minimal/narrow partner response, and the reversibility boundary "until counsel
  guides you."
- This explains why Kimi split 3/6 and GPT stood down 3/3 while reviewers did
  not cleanly support GPT's stand-down. The deck pressure is useful but thin, so
  Step 6 can plausibly read it as visible additive pressure or private
  confirming support.
- `consultant_cleaning_variant_v0` was built as a research-only table-cleaning
  artifact. It keeps the anchor as backbone and replaces broad Bevelin/Polya
  identity with three concrete micro-cards:
  `counsel_independence_and_channel_bias_card`,
  `wednesday_tripwire_preservation_card`, and
  `reversibility_until_counsel_boundary_card`.
- Next move should be `consultant_cleaning_variant_replay_v0`: replay the
  cleaner table through Step 6 and test whether consideration becomes more
  stable. The success criterion is cleaner Step 6 cognition/custody, not
  automatic deck visibility.
- `consultant_cleaning_variant_replay_v0` has now run with six completed live
  `moonshotai/kimi-k2.6` samples. Sample `4` stalled twice at the provider/model
  call layer and was replaced by sample `6`; this is an operational observation,
  not a visibility read.
- Aggregate result: 4/6 samples marked a micro-card as additive, 2/6 kept all
  micro-cards private or confirming, 0 were missing/unclear, and protected
  Consultant payload was preserved in 6/6. The old Kimi unlock ratio was 0.5;
  the cleaned table produced 0.667 but still reads as `mixed`.
- Interpretation: the cleaning variant improved consideration legibility more
  than stability. Step 6 did not use the cards as a generic bundle. It kept the
  counsel/channel-bias and Wednesday-tripwire cards private or confirming and
  repeatedly treated only `reversibility_until_counsel_boundary_card` as
  additive.
- The current Consultant learning is the narrow boundary "keep first moves
  reversible until counsel guides the next action." The next cleaning move is
  `consultant_anchor_boundary_patch_probe_v0`: patch that boundary into the
  anchor candidate and replay the same micro-cards to see whether they mostly
  stand down. Do not add a deterministic visibility gate.
- `consultant_anchor_boundary_patch_probe_v0` has now run. It patched only one
  phrase into the anchor: `keep the first moves reversible until counsel guides
  the next action`. The same three micro-cards remained available. This was a
  hypothesis test, not a proposed patch architecture.
- Aggregate result: 6 live Kimi samples, 5/6 all-private-or-confirming, 1/6
  reversibility-card additive, 6/6 patched boundary present, 6/6 protected
  payload preserved. Outcome: `upstream_pressure_carried = yes`,
  `consultant_classification = graduation_candidate`, `next_investigation =
  synthesis`.
- Interpretation: the recurring pressure moved successfully into the anchor
  candidate. The single additive outlier appears to credit the micro-card with
  adding a phrase already present in the patched anchor, so it is a small
  meta-ledger attribution lag rather than evidence for a permanent card.
- Consultant stops here for this research chapter. The follow-up is
  `consultant_upstream_origin_investigation_v0`, scoped as an upstream-origin
  finding: why did original anchor synthesis compress the pressure to generic
  reversibility instead of carrying the counsel-gated terminal condition?
- Per the stop boundary, the next cleaning-lane case is
  `phd_kimi_variance_cleaning_review_v0`, to test whether atomic decomposition
  also explains Kimi's PhD variance or whether Consultant was case-specific.
- `phd_kimi_variance_cleaning_review_v0` has now run on
  `third-year-phd-student.v2.v60-off` with the visible anchor plus four atomic
  PhD cards: bounded probe/not commitment, single-cell collaborator
  feasibility, fallback re-entry readiness, and visible stop-date conditions.
- The first Kimi call hung at the provider/model layer, so the script added an
  opt-in OpenRouter reasoning-disable setting for this research slice only.
  After that, six live samples completed cleanly.
- Aggregate result: 6/6 samples marked at least one micro-card additive,
  0/6 were all-private-or-confirming, 0/6 were missing/unclear, and protected
  PhD payload was preserved in 6/6. Additive card counts were:
  bounded-probe 4, visible-stop-date 3, single-cell feasibility 2, fallback
  re-entry 1.
- Interpretation: atomic decomposition generalized beyond Consultant, but PhD
  has a distributed pressure pattern rather than one dominant graduation atom.
  Step 6 selected different subsets by run; this is discrimination, not a new
  bundle.
- No deterministic selector, model router, vocabulary patch, runtime promotion,
  or `SKILL.md` update follows from this. The next stop-boundary slice is
  `evidence_surface_v0`, so humans can read recurring pressure atoms and
  graduation candidates without opening JSON. Code may nominate; humans decide.
- `evidence_surface_v0` now exists as a runtime-dormant evidence surface:
  `research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.md`
  and `cleaning-evidence-surface.v1.json`.
- The surface aggregates the Consultant and PhD cleaning results into atom rows
  rather than raw JSON files. Consultant's
  `reversibility_until_counsel_boundary_card` is nominated for human review:
  4/6 additive before the anchor patch, 1/6 additive after patched anchor, and
  protected payload preserved 6/6. PhD atoms are marked
  `distributed_pressure_atom` / `watch_not_graduate`, not graduation
  candidates.
- The surface encodes the learning-system boundary directly:
  `code_may_nominate = true`, `humans_decide = true`,
  `automatic_graduation_allowed = false`, and
  `runtime_visibility_change_allowed = false`.
- The stop-boundary queue has now reached closeout. The next artifact is the
  closeout decision document, not another probe.
- Closeout has now landed:
  `research/pre-step6-cleaning-research-closeout-2026-05-22.md`.
- Closeout decision: the research chapter is complete. Dormant shadow
  implementation is allowed only as a separate next program. Runtime-on
  promotion and `SKILL.md` behavior changes remain blocked. More probe-shaped
  research is not recommended before the product/engineering decision.
- The closeout explicitly defines shadow implementation as production-adjacent
  recording behind `LOLLA_STEP6_PORTFOLIO=off|shadow|on`, default `off`, with
  no user-facing answer change. It also hands Founder V60-on instability to a
  separate V60 packet/selection audit rather than absorbing it into portfolio
  policy.

Promotion remains blocked until the calibration floor and Step 6 stability
requirements are met, or until the board explicitly approves a narrower
bridge-stage integration draft with runtime still dormant.
