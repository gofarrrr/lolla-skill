# Pre-Step-6 Reasoning Portfolio Handoff

Date: 2026-05-20

Branch: `feature/step6-reasoning-portfolio`

Status: research-only local experiment. `SKILL.md` and default `/lolla`
runtime behavior were not changed.

## What Was Built

- Local PRD update for the Step 6 reasoning-portfolio layer.
- Task plan with vertical red-green-refactor slices.
- Research contract for `problem_state.v1`, `candidate_inventory.v1`,
  `reasoning_affordance.v1`, and `step6_attention_map.v1`.
- Validators and deterministic builders for problem states, candidate
  inventories, reasoning affordances, attention maps, and portfolio comparison
  fixtures.
- Static fixtures for problem states, candidate inventories, reasoning
  affordances, attention maps, and comparison readouts.
- A comparison readout that keeps the work research-only until Step 6 replay
  evidence exists.
- Portfolio answer-core fixtures and blind comparisons against previous best
  raw/rendered-hybrid outputs.
- A founder high-clutter static Step 6 replay record using the rendered
  portfolio attention map.
- Additional boundary tests: a consultant negative-control portfolio that
  correctly loses to rendered hybrid, and a PhD v2 retest that activates Silva
  executability pressure while preserving fallback as a stop-rule receipt.
- A PhD v2 static Step 6 replay record, which passed to the next replay stage
  while still blocking runtime and skill promotion.
- A local autoresearch operating program for the next iteration loop, adapted
  from Karpathy's fixed-evaluation keep/discard pattern to Lolla's case-suite
  and quality-rubric needs.
- Bevelin v0 lens-probe, lens-answer-core, and lens-comparison fixtures for
  founder high-clutter, PhD v2, consultant, and mother.
- Bevelin v0 lens Step 6 replay fixtures for founder high-clutter and PhD v2,
  with an explicit cognitive gate record.
- Polya v0 lens-probe, lens-answer-core, and lens-comparison fixtures for the
  same fixed suite.
- A local autoresearch ledger recording the Bevelin v0 fixed-suite result.

## Main Paths

- `plans/lolla-solver-control-layer-prd-2026-05-19.md`
- `tasks/tasks-step6-reasoning-portfolio.md`
- `research/pre-step6-reasoning-portfolio-contract-2026-05-20.md`
- `research/pre-step6-reasoning-portfolio-comparison-readout-2026-05-20.md`
- `research/pre-step6-autoresearch-program-2026-05-20.md`
- `research/pre-step6-autoresearch-ledger-2026-05-20.tsv`
- `scripts/research/pre_step6_problem_states.py`
- `scripts/research/pre_step6_build_candidate_inventory.py`
- `scripts/research/pre_step6_reasoning_affordances.py`
- `scripts/research/pre_step6_attention_maps.py`
- `scripts/research/pre_step6_build_attention_map.py`
- `scripts/research/pre_step6_portfolio_comparisons.py`
- `scripts/research/pre_step6_portfolio_answer_cores.py`
- `scripts/research/pre_step6_portfolio_blind_comparisons.py`
- `scripts/research/pre_step6_portfolio_step6_replays.py`
- `scripts/research/pre_step6_lens_probes.py`
- `scripts/research/pre_step6_lens_answer_cores.py`
- `scripts/research/pre_step6_lens_comparisons.py`
- `scripts/research/pre_step6_lens_step6_replays.py`
- `tests/test_pre_step6_problem_states.py`
- `tests/test_pre_step6_candidate_inventory.py`
- `tests/test_pre_step6_reasoning_affordances.py`
- `tests/test_pre_step6_attention_maps.py`
- `tests/test_pre_step6_portfolio_comparisons.py`
- `tests/test_pre_step6_portfolio_answer_cores.py`
- `tests/test_pre_step6_portfolio_blind_comparisons.py`
- `tests/test_pre_step6_portfolio_step6_replays.py`
- `tests/test_pre_step6_lens_probes.py`
- `tests/test_pre_step6_lens_answer_cores.py`
- `tests/test_pre_step6_lens_comparisons.py`
- `tests/test_pre_step6_lens_step6_replays.py`
- `tests/test_pre_step6_polya_lens.py`
- `tests/test_pre_step6_cognitive_gate_live.py`
- `tests/test_pre_step6_context_composition_gate.py`

## Verification

Focused tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_problem_states.py tests/test_pre_step6_candidate_inventory.py tests/test_pre_step6_reasoning_affordances.py tests/test_pre_step6_attention_maps.py tests/test_pre_step6_portfolio_answer_cores.py tests/test_pre_step6_portfolio_blind_comparisons.py tests/test_pre_step6_portfolio_step6_replays.py
```

Result:

```text
27 passed
```

Focused lens-pack tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_lens_probes.py tests/test_pre_step6_lens_answer_cores.py tests/test_pre_step6_lens_comparisons.py
```

Result:

```text
6 passed
```

Focused lens replay and Polya tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_lens_step6_replays.py tests/test_pre_step6_polya_lens.py
```

Result:

```text
2 passed
```

Focused live-gate tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_cognitive_gate_live.py tests/test_pre_step6_context_composition_gate.py
```

Result:

```text
4 passed
```

Focused card-deck tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_card_deck_visibility_policy.py tests/test_pre_step6_step6_card_deck.py tests/test_pre_step6_card_deck_replays.py tests/test_pre_step6_card_deck_replay_comparisons.py
```

Result:

```text
10 passed
```

Card-deck artifact validation:

```text
python3 scripts/research/pre_step6_card_deck_replays.py research/pre-step6-card-deck-replays/*.card-deck-replay.v1.json
python3 scripts/research/pre_step6_card_deck_replay_comparisons.py research/pre-step6-card-deck-replay-comparisons/*.card-deck-replay-comparison.v1.json research/pre-step6-card-deck-replay-comparisons-stability-gemini/*.card-deck-replay-comparison.v1.json
python3 scripts/research/pre_step6_card_deck_visibility_policy.py research/pre-step6-card-deck-visibility-policies/*.card-deck-visibility-policy.v1.json
```

Result: clean.

Full pre-Step-6 and skill-contract regression:

```text
PYTHONPATH=. pytest tests/test_pre_step6_*.py tests/test_skill_contract.py
```

Result:

```text
156 passed
```

Static check:

```text
git diff --check
```

Result: clean.

## Recommendation

Keep this research-only for now.

The high-clutter founder fixture shows the strongest reason to continue: the
portfolio preserves denominator, opportunity-cost, and model-forcing pressure
without dumping raw artifacts. The mother fixture works as a negative-control
case because it preserves weak-evidence caution without demanding extra public
machinery.

Do not edit `SKILL.md` or default runtime yet. The founder high-clutter
portfolio answer won the local blind rubric against the previous rendered
hybrid answer, and the static Step 6 replay also passed to the next replay
stage. Mother remains a tie/retest case. Consultant is now a stronger negative
control: rendered hybrid wins and portfolio promotion stops. PhD v2 now wins
the local blind comparison after activating Silva executability pressure, and
its static Step 6 replay passed to the next replay stage. It still needs a
manual or additional live-style replay before any integration discussion.

Next process: use the autoresearch program, not ad hoc prompting. The first
loop tested Bevelin as `Lens Pack 001` against founder, PhD v2, consultant,
and mother. Keep the result research-only. The fixed-suite result is:

- founder high-clutter: `lens_improves`, `expand_replay`;
- PhD v2: `lens_improves`, `expand_replay`;
- consultant: `lens_boundary_case`, `stop`;
- mother: `lens_boundary_case`, `retest`.

The useful lesson is that Bevelin preserves incentive, denominator,
commitment, inversion, and absence-of-evidence pressure when carried as a
private lens probe. The equally important lesson is that a lens can contribute
an edge and still lose the promotion decision. Consultant should stand down
because rendered hybrid is cleaner; mother should retest because the lens
improves uncertainty language but may not beat the simpler base answer.

The follow-up loop ran one more replay-style comparison for the founder and PhD
v2 Bevelin answer cores, then tested a Polya problem-shape lens as an
independent preset. The gate is explicitly cognitive: the fixture records what
the reviewer judged, while code validates source custody, hygiene, consistency,
and promotion blocks.

Bevelin replay results:

- founder high-clutter: `lens_replay` wins, `pass_to_polya_comparison`;
- PhD v2: `lens_replay` wins, `pass_to_polya_comparison`;
- product promotion remains `blocked`.

Polya fixed-suite results:

- founder high-clutter: `lens_boundary_case`, `stop`;
- PhD v2: `lens_improves`, `expand_replay`;
- consultant: `lens_boundary_case`, `stop`;
- mother: `lens_boundary_case`, `retest`.

Interpretation: the interface generalizes. Bevelin is stronger for incentives,
false precision, commitment pressure, and inversion. Polya is stronger for
problem type, knowns/unknowns, next informative move, and sequencing. Neither
should become runtime default yet.

## Live Gate Follow-Up

We then ran live cognitive gates to test the gate itself. The env file supplied
keys correctly; the configured default OpenRouter model returned 404, so the
manual research calls used explicit current models.

New files:

- `scripts/research/pre_step6_cognitive_gate_live.py`
- `tests/test_pre_step6_cognitive_gate_live.py`
- `scripts/research/pre_step6_context_composition_gate.py`
- `tests/test_pre_step6_context_composition_gate.py`
- `research/pre-step6-cognitive-gate-judgments*/`
- `research/pre-step6-context-composition-gate-judgments*/`

The answer-core gate compared rendered hybrid, portfolio base, Bevelin answer
core, and Polya answer core as alternatives. That was a useful failure. It
showed that rendered hybrid often wins because it preserves concrete case
nuance that shorter lens answer cores can shave off.

The context-composition gate then compared rendered-only against rendered plus
protected private receipts. The no-tax version over-promoted dual receipts in
negative controls. The complexity-tax version repaired mother and mostly
repaired consultant, but founder stood down and PhD moved to retest rather than
expand.

Current recommendation:

- keep runtime and `SKILL.md` dormant;
- keep rendered hybrid as the Step 6 anchor;
- use Bevelin/Polya as candidate receipt generators, not answer-core
  replacements;
- add a novelty filter before the cognitive gate so it sees only receipts that
  add decision pressure not already present in the rendered anchor;
- retest PhD v2 and consultant first, because they distinguish useful
  enrichment from overpromotion.

## Step 6 Card-Deck Follow-Up

We then tested the broader user-preferred shape: pass Step 6 a private deck
containing the clean hybrid anchor, Bevelin card, and Polya card together, and
let Step 6 decide.

New files:

- `scripts/research/pre_step6_step6_card_deck.py`
- `tests/test_pre_step6_step6_card_deck.py`
- `scripts/research/pre_step6_card_deck_replays.py`
- `tests/test_pre_step6_card_deck_replays.py`
- `scripts/research/pre_step6_card_deck_replay_comparisons.py`
- `tests/test_pre_step6_card_deck_replay_comparisons.py`
- `scripts/research/pre_step6_card_deck_visibility_policy.py`
- `tests/test_pre_step6_card_deck_visibility_policy.py`
- `research/pre-step6-step6-card-decks/`
- `research/pre-step6-card-deck-replays/`
- `research/pre-step6-card-deck-replay-comparisons/`
- `research/pre-step6-card-deck-visibility-policies/`

Important gate fix: the first comparison attempt asked a blinded reviewer to
report `deck_effect`, which is incoherent because the reviewer does not know
which blind label is the deck. The corrected gate asks only for A/B/tie visible
quality judgment. Deterministic code then maps the blind winner to
`improves`, `regresses`, or `equivalent` and rejects inconsistent artifacts.
That keeps cognition in the reviewer and keeps code to bookkeeping.

Prompt fix: the first Step 6 replay pass was too compression-oriented. The
prompt now tells Step 6 to write "as short as possible, but no shorter" and not
to compress away concrete tripwires, conditions, actor-specific steps, or
irreversible-risk distinctions merely to be concise.

Follow-up prompt/ledger fixes:

- The private ledger now records `novelty_role` for each card:
  `visible_backbone`, `additive_pressure`, `confirming_support`, or
  `private_guardrail`.
- The prompt says the ledger is where card consideration lives; the public
  answer should not get longer merely to prove that every card was considered.
- Sensitive safety/legal contexts require visible enrichment to add a concrete
  safeguard, tripwire, or channel distinction; otherwise the lens stays
  private.
- The prompt now preserves concrete anchor payload: named channels or
  resources, communication boundaries, dated windows, gates, actor sequence,
  tripwires, and evidence checks.
- A founder replay leaked forbidden public terms and was rejected by the
  validator, proving the hygiene guard works; the prompt now names those terms
  explicitly.

Latest four-case live comparison with `openai/gpt-5.1-chat`:

- founder high-clutter: card deck replay wins, `improves`, high confidence;
- PhD v2: card deck replay wins, `improves`, high confidence;
- consultant: card deck replay wins, `improves`, high confidence;
- mother: clean hybrid wins, `regresses`, high confidence.

Cross-model stability check with `google/gemini-3.1-flash-lite`:

- founder high-clutter: card deck replay wins;
- PhD v2: card deck replay wins;
- consultant: card deck replay wins;
- mother: clean hybrid wins.

Interpretation:

- The broad card deck is now the strongest research shape because it gives
  Step 6 breadth without asking deterministic code to think.
- The card deck should be treated as private context, not as a public template
  or a new default lane.
- The mother case remains the safety negative control: the deck answer was
  good, but the clean hybrid version was tighter and less redundant across both
  reviewers.
- No runtime or `SKILL.md` promotion is justified yet.

Next recommended research slice:

- keep the broad card deck as the leading research shape;
- treat mother as an explicit stand-down condition, not a target to force;
- test a small meta-policy next: when the Step 6 ledger marks all non-anchor
  cards as `private_guardrail` or `confirming_support`, the clean hybrid anchor
  may be the visible answer while the deck remains private context;
- only discuss `SKILL.md` integration after that stand-down behavior is
  represented without letting deterministic code decide quality.

## Visibility Policy Follow-Up

The meta-policy was built research-only.

New artifact:

```text
pre_step6_card_deck_visibility_policy.v1
```

Result:

- founder high-clutter: non-anchor cards had additive pressure, cognitive
  reviewer preferred card-deck replay, policy result
  `card_deck_visible_after_cognitive_confirmation`;
- PhD v2: non-anchor cards had additive pressure, cognitive reviewer preferred
  card-deck replay, policy result
  `card_deck_visible_after_cognitive_confirmation`;
- consultant: one non-anchor card had additive pressure and one was private
  guardrail, cognitive reviewer preferred card-deck replay, policy result
  `card_deck_visible_after_cognitive_confirmation`;
- mother: all non-anchor cards were private/confirming and the cognitive
  reviewer preferred clean hybrid, policy result
  `anchor_visible_after_cognitive_confirmation`.

This is the current best answer to the concern that deterministic code must
not become the cognitive brain. Code only records Step 6's private ledger roles
and maps the already-cognitive comparison result into a policy artifact. It
does not infer answer quality from additive counts.

The next integration discussion, if any, should start from this shape:

```text
broad private deck always available
Step 6 ledger records visible/additive/private roles
cognitive comparison confirms visible answer policy
runtime remains dormant until this is represented behind a flag
```

## Design Preamble Autoresearch Track

Round-two red-team review turned the design preamble into a new autoresearch
track instead of a direct runtime design draft.

New artifact:

```text
research/pre-step6-design-preamble-autoresearch-track-2026-05-20.md
```

This track keeps the design local and research-only. It converts the remaining
load-bearing decisions into six falsifiable experiments:

- `design_preamble_cost_cache_v0` - prove the cached-cards-first path uses
  per-run compiled card decks from cached lens substrates, with normal runtime
  cache misses standing down instead of generating cards live.
- `design_preamble_card_interface_v0` - prove Bevelin and Polya are
  implementations of a generic private-card schema, not hardcoded
  infrastructure.
- `design_preamble_ledger_overlap_v0` - prove V60/card redundancy can be
  deduped in hot context while preserving full source custody in a unified
  private-consideration ledger.
- `design_preamble_payload_omission_v0` - prove critical omissions can be
  surfaced as checklist candidates before cognitive severity review.
- `design_preamble_visibility_asymmetry_v0` - make runtime anchor bias explicit:
  broad private deck, narrow public answer, no normal live reviewer loop, one
  bounded retest only in research/experimental modes.
- `design_preamble_calibration_floor_v0` - treat the four-case suite as a seed,
  then define the 12-20 case calibration manifest and false-stand-down recall
  measurement.

As of the current pass, all six design-preamble slices have been run
research-only and recorded in the ledger.

Design-preamble promotion remains blocked because the calibration floor is not
met. The next decision is case curation or a board-approved non-promotional
bridge set, not `SKILL.md` or runtime wiring.

## Cost/Cache Contract Follow-Up

`design_preamble_cost_cache_v0` has now been run as the first design-preamble
autoresearch slice.

New artifact:

```text
pre_step6_design_preamble_cost_cache.v1
```

Files:

- `scripts/research/pre_step6_design_preamble_cost_cache.py`
- `tests/test_pre_step6_design_preamble_cost_cache.py`
- `research/pre-step6-design-preamble-cost-cache/*.cost-cache.v1.json`

Result:

- `runtime_cached_only` cache misses stand down to current Step 6.
- Normal runtime cache misses add 0 LLM calls.
- Live card generation is disallowed in normal runtime cached-only mode.
- Normal runtime reviewer calls remain 0.
- The compiled card-deck key includes schema/version/source/problem/V60/safety
  and Step 6 prompt-contract material.
- Static research fixtures explicitly mark `ConversationIR` and V60 selected
  chunks as research-proxy/not-attached fields rather than pretending this is a
  full live run.

Interpretation:

The cached-cards-first design is plausible only as a compiled/cache-hit path.
It is not a license to generate Bevelin/Polya cards live on every normal
runtime miss. A miss records `card_deck_cache_miss` and uses the current Step 6
path.

Next autoresearch slice:

```text
design_preamble_card_interface_v0
```

That slice must prove Bevelin and Polya satisfy a generic private-card schema
before the cache-hit path can mean anything useful.

## Generic Card Interface Follow-Up

`design_preamble_card_interface_v0` has now been run as the second
design-preamble autoresearch slice.

New artifacts:

```text
pre_step6_private_reasoning_card_interface.v1
private_reasoning_card.v1
```

Files:

- `scripts/research/pre_step6_private_reasoning_cards.py`
- `tests/test_pre_step6_private_reasoning_cards.py`
- `research/pre-step6-private-reasoning-cards/*.private-reasoning-cards.v1.json`

Result:

- Existing clean-hybrid, Bevelin, and Polya cards validate through one generic
  private-card schema.
- The schema carries `card_type`, `source_kind`, `source_ref`,
  `cognitive_role`, receipts, handling rule, activation scope, misuse guard,
  stand-down condition, public hygiene terms, and expansion ref.
- A synthetic future card validates without adding visibility-policy or ledger
  fields.
- The interface read records that Bevelin/Polya are not special-cased and that a
  new card should not require policy or ledger changes.

Interpretation:

The card layer is no longer Bevelin/Polya-specific at the schema level. This
does not prove cache-hit usefulness or runtime readiness. It only earns the next
design slice: V60/card overlap in the unified private-consideration ledger.

Next autoresearch slice:

```text
design_preamble_ledger_overlap_v0
```

## Unified Ledger Overlap Follow-Up

`design_preamble_ledger_overlap_v0` has now been run as the third
design-preamble autoresearch slice.

New artifacts:

```text
pre_step6_private_consideration_ledger_overlap.v1
private_consideration_item.v1
```

Files:

- `scripts/research/pre_step6_private_consideration_ledger.py`
- `tests/test_pre_step6_private_consideration_ledger.py`
- `research/pre-step6-private-consideration-ledgers/*.ledger-overlap.v1.json`

Result:

- The founder fixture presents one hot-context representative:
  `reasoning_card:bevelin_card`.
- The unified ledger preserves both `reasoning_card:bevelin_card` and
  `v60_chunk:overcommitment_without_evidence`.
- The V60-style item is marked `supporting_ref_not_repeated`, so Step 6 is not
  forced to read the same pressure twice.
- The overlap group records one presentation policy and one custody policy:
  `single_representative_with_supporting_refs` and
  `all_source_items_preserved`.

Interpretation:

The unified ledger can represent V60/card redundancy without either hot-context
bloat or source-custody deletion. The V60 item is synthetic in this slice, so
this is a schema proof, not a runtime V60 integration.

Next autoresearch slice:

```text
design_preamble_payload_omission_v0
```

## Payload Omission Gate Follow-Up

`design_preamble_payload_omission_v0` has now been run as the fourth
design-preamble autoresearch slice.

New artifact:

```text
pre_step6_payload_omission.v1
```

Files:

- `scripts/research/pre_step6_payload_omission_gate.py`
- `tests/test_pre_step6_payload_omission_gate.py`
- `research/pre-step6-payload-omission-gates/*.payload-omission.v1.json`

Result:

- The gate uses exactly six protected categories: dates/windows, actor sequence,
  named resources/channels, communication boundaries, tripwires/gates, and
  evidence checks.
- It is anchor-activated and diff-based: only anchor-present/deck-absent rows
  become `introduced_omission`.
- Detection is mechanistic-first. The RED/GREEN loop caught and fixed an overly
  broad named-resource detector that was counting ordinary capitalized words as
  resources.
- The gate explicitly records
  `visibility_decision: not_decided_by_omission_gate`.
- All four fixed-suite fixtures validate as `preserved` at the protected
  category level.

Interpretation:

The deck-aware answers did not subtract the six protected anchor-payload
categories. The mother stand-down remains a sensitive-safety phrasing/tightness
result, not a protected-payload omission result.

Next work before visibility-asymmetry:

```text
ledger negative-shape fixtures
```

Add the two residual ledger fixtures: non-overlap and V60-only/no-deck.

## Ledger Negative-Shape Fixture Follow-Up

The residual ledger fixtures have now been added.

Updated artifact:

```text
pre_step6_private_consideration_ledger_overlap.v1
```

New fixtures:

- `founder-grant-marcus-equity.high-clutter.non-overlap.ledger-overlap.v1.json`
- `synthetic-v60-only.ledger-overlap.v1.json`

Result:

- Non-overlap fixture keeps both `reasoning_card:polya_card` and
  `v60_chunk:absence_blocker_false_precision` in hot context because no overlap
  group applies.
- V60-only/no-deck fixture validates a single
  `v60_chunk:standalone_margin_of_safety` with no private card deck.
- This proves dedupe is conditional and the unified ledger schema does not
  depend on the card deck being present.

Next autoresearch slice:

```text
design_preamble_visibility_asymmetry_v0
```

## Visibility Asymmetry Follow-Up

`design_preamble_visibility_asymmetry_v0` has now been run.

New artifact:

```text
pre_step6_visibility_asymmetry.v1
```

Files:

- `scripts/research/pre_step6_visibility_asymmetry_policy.py`
- `tests/test_pre_step6_visibility_asymmetry_policy.py`
- `research/pre-step6-visibility-asymmetry-policies/*.visibility-asymmetry.v1.json`

Result:

- Runtime mode has no normal comparison loop and 0 normal runtime reviewer
  calls.
- Runtime unresolved/tie-like conditions produce
  `anchor_visible_deck_private`.
- Research and experimental modes may retest at most once.
- The second-reviewer spec is explicit: different model family if available,
  same rubric, fresh blind shuffle.
- Deck-visible after retest requires the second reviewer to prefer the deck;
  non-inferior keeps the deck alive for research only.
- False stand-down is named as the primary runtime failure mode.

Interpretation:

Runtime is intentionally asymmetric:

```text
broad private deck, anchor-biased public answer when unresolved
```

That is the right safety posture for normal runtime, but it makes
false-standdown recall the load-bearing measurement before promotion.

Next autoresearch slice:

```text
design_preamble_calibration_floor_v0
```

## Calibration Floor Follow-Up

`design_preamble_calibration_floor_v0` has now been run.

New artifact:

```text
pre_step6_calibration_floor.v1
```

Files:

- `scripts/research/pre_step6_calibration_floor_manifest.py`
- `tests/test_pre_step6_calibration_floor_manifest.py`
- `research/pre-step6-calibration-floor/seed-suite.calibration-floor.v1.json`

Result:

- The fixed four-case suite is recorded as `seed_suite_not_calibration`.
- Required promotion floor is 12-20 cases.
- Required bucket coverage is 3 high-clutter, 3 sequencing/problem-shape, 3
  sensitive/safety/legal, 3 negative controls, and 2 V60 on/off pairs.
- Current coverage is 1 high-clutter, 1 sequencing/problem-shape, 1
  sensitive/safety/legal, 2 negative controls, and 0 V60 on/off pairs.
- A V60 on/off pair means the same case run twice with the same prompt contract
  and card-deck policy: one run with V60 selected items available and one run
  with those items withheld. "Substantive V60" versus "minimal V60" is only a
  stratification label.
- Mother is recorded only as a `true_standdown_candidate` with `seed_only`
  calibration weight.
- Calibration will track `preserved_by_marker_anchor_entities_missing` so the
  payload gate's marker-level limitation does not disappear inside a generic
  `preserved` verdict.
- The next bridge probe is pinned as `false_standdown_bridge_probe_v0`: 2-3
  deliberately dangerous non-promotional cases targeting false stand-down.
- `calibration_floor_met: false` and
  `promotion_read: runtime_promotion_blocked`.

Interpretation:

The remaining blocker is not another deterministic rule. It is evidence. We
should run the false-standdown bridge probe first, then either curate the full
calibration floor or pause for board review before writing the integration
draft.

## False-Standdown Bridge Probe Follow-Up

`false_standdown_bridge_probe_v0` has now been run.

New artifacts:

```text
pre_step6_false_standdown_bridge_probe.v1
pre_step6_false_standdown_bridge_judgment.v1
pre_step6_false_standdown_bridge_result.v1
```

Files:

- `scripts/research/pre_step6_false_standdown_bridge_probe.py`
- `tests/test_pre_step6_false_standdown_bridge_probe.py`
- `research/pre-step6-false-standdown-bridge-probe/false-standdown-bridge-probe.v1.json`
- `research/pre-step6-false-standdown-bridge-probe/judgments/*.false-standdown-bridge-judgment.v1.json`
- `research/pre-step6-false-standdown-bridge-probe/false-standdown-bridge-result.v1.json`
- `research/pre-step6-false-standdown-bridge-probe-readout-2026-05-21.md`

Result:

- All three pre-registered bridge cases were confirmed `false_standdown`.
- Confirmation required two reviewer families under the same rubric and fresh
  blind shuffles.
- Reviewer families were `openai` and `google`.
- Aggregate result is `design_review_required`.
- `promotion_effect` remains `none_bridge_only`.
- Runtime wiring and skill updates remain blocked.

Interpretation:

The bridge probe falsifies a universal runtime rule of:

```text
unresolved -> anchor visible, deck private
```

The false-standdown pattern appeared in all three dangerous-corner packets.
This does not prove full runtime card-deck behavior, because the probe used
pre-registered packet cases rather than the full production generator. But it
does prove that integration should not proceed with unconditional runtime
anchor fallback.

Next research slice:

```text
design_preamble_visibility_policy_redesign_v0
```

The redesign should test whether normal runtime can use Step 6's own private
ledger as the cognitive signal: deck-aware output may be visible when Step 6
records additive pressure and protected payload is preserved; anchor remains
the fallback for private/confirming ledgers, missing/unclear ledgers, cache
misses, or payload omissions.

## Visibility Policy Redesign Follow-Up

`design_preamble_visibility_policy_redesign_v0` has now been run.

New artifact:

```text
pre_step6_visibility_policy_redesign.v1
```

Files:

- `scripts/research/pre_step6_visibility_policy_redesign.py`
- `tests/test_pre_step6_visibility_policy_redesign.py`
- `research/pre-step6-visibility-policy-redesign/*.visibility-policy-redesign.v1.json`
- `research/pre-step6-visibility-policy-redesign-readout-2026-05-21.md`

Result:

- The three confirmed false-standdown bridge cases move from legacy
  `anchor_visible_deck_private` to
  `deck_visible_from_step6_additive_pressure` when cache is hit, Step 6 records
  additive pressure, and payload is preserved.
- `mother-address-year` still falls back to `anchor_visible_deck_private` when
  Step 6 records all non-anchor cards as private/confirming.
- Cache miss falls back to `current_step6_visible_no_deck`.
- Missing or unclear ledger falls back to
  `anchor_visible_unclear_ledger_guardrail`.
- Introduced protected-payload omission falls back to
  `anchor_visible_payload_omission_guardrail`.
- Normal runtime reviewer calls remain 0.

Interpretation:

The policy flaw found by the bridge probe is fixed at contract level. The
redesigned policy does not ask deterministic code to decide wisdom. It lets Step
6's private ledger supply the cognitive signal, then lets code validate whether
that signal can be surfaced.

Remaining gap:

```text
The bridge cases are still packet-level evidence. We have not proven that the
full Step 6 replay path will produce additive ledger signals on these bridge
cases.
```

Next possible slice:

```text
bridge_step6_ledger_replay_v0
```

or full calibration-floor curation.

## Bridge Step 6 Ledger Replay Follow-Up

`bridge_step6_ledger_replay_v0` has now been run.

New artifacts:

```text
pre_step6_bridge_step6_ledger_replay.v1
pre_step6_bridge_step6_ledger_replay_result.v1
```

Files:

- `scripts/research/pre_step6_bridge_step6_ledger_replay.py`
- `tests/test_pre_step6_bridge_step6_ledger_replay.py`
- `research/pre-step6-bridge-step6-ledger-replays/*.bridge-step6-ledger-replay.v1.json`
- `research/pre-step6-bridge-step6-ledger-replays/bridge-step6-ledger-replay-result.v1.json`
- `research/pre-step6-bridge-step6-ledger-replay-readout-2026-05-21.md`

Result:

- Live Step 6 replay used `openai/gpt-5.1-chat` on the three pre-registered
  false-standdown bridge packets.
- All three produced `ledger_signal: additive_pressure_present`.
- Aggregate result:
  `replay_result: step6_additive_signal_supported`.
- Runtime wiring and `SKILL.md` updates remain blocked.

Interpretation:

This clears the immediate gap in the visibility redesign. The ledger-mediated
policy is no longer relying only on a hand-set bridge fixture; Step 6 itself can
mark the deck-pressure candidate as additive in the dangerous-corner packets.
The deterministic role remains bounded to contract validation, ledger-schema
validation, signal derivation, and audit custody.

Remaining gap:

```text
This is still bridge-packet evidence, not runtime promotion evidence. It does
not prove full production card compilation, cache hit behavior, V60 overlap,
or protected-payload omission behavior across calibrated live cases.
```

Next valid moves:

- Write a research-only integration design draft that uses Step 6 ledger
  signals as the cognitive visibility input while keeping runtime dormant.
- Or curate the full 12-20 case calibration floor before any integration draft.

## Ledger-Mediated Integration Design Draft

The research-only integration draft has now been written:

```text
research/pre-step6-ledger-mediated-integration-design-draft-2026-05-21.md
```

Design summary:

```text
broad private deck -> Step 6 answer + private ledger -> deterministic guards -> visible answer decision
```

The draft pins:

- integration modes from `off` through `experimental_shadow`,
  `experimental_visible`, and blocked `runtime_on`;
- cache-hit-only runtime behavior with cache-miss stand-down to current Step 6;
- Step 6 prompt contract requiring a public answer and private consideration
  ledger;
- one unified ledger for anchor, reasoning cards, and V60 chunks;
- deterministic visibility resolver inputs and outcomes;
- payload gate role as a tripwire, not a selector;
- archive fields and Observatory view;
- normal runtime cost envelope: no reviewer loop and no live card generation;
- promotion gates and falsifiers.

Important boundary:

```text
The design draft is permission to implement a dormant/shadow integration slice,
not permission to promote runtime behavior.
```

Follow-up correction:

The design draft has been patched to make this stricter. It is now explicitly a
research-only design-review response and proposed dormant architecture, not an
approved integration contract. The false-positive visibility direction must be
probed before the draft is treated as implementation-ready.

## False-Positive Visibility Probe Follow-Up

`false_positive_visibility_probe_v0` has now been run.

New artifacts:

```text
pre_step6_false_positive_visibility_probe.v1
pre_step6_false_positive_step6_replay.v1
pre_step6_false_positive_visibility_result.v1
```

Files:

- `scripts/research/pre_step6_false_positive_visibility_probe.py`
- `tests/test_pre_step6_false_positive_visibility_probe.py`
- `research/pre-step6-false-positive-visibility-probe/false-positive-visibility-probe.v1.json`
- `research/pre-step6-false-positive-visibility-probe/step6-replays/*.false-positive-step6-replay.v1.json`
- `research/pre-step6-false-positive-visibility-probe/false-positive-visibility-result.v1.json`
- `research/pre-step6-false-positive-visibility-probe-readout-2026-05-21.md`

Result:

- Live Step 6 replay used `openai/gpt-5.1-chat`.
- Step 6 emitted `all_private_or_confirming` on all three pre-registered
  overpromotion cases.
- No reviewer calls were needed because the redesigned visibility precondition
  did not fire.
- `fp-bevelin-irrelevant-incentives`: `step6_stood_down`.
- `fp-polya-true-but-useless`: `step6_stood_down`.
- `fp-marker-preserved-entity-lost`: `not_observed`.
- Aggregate result: `continue_probe_with_not_observed`.

Interpretation:

The probe did not find a false positive. Step 6 correctly kept tempting but
unhelpful deck pressure private in the Bevelin and Polya cases. However, the
marker/entity-loss dimension remains live risk because the constructed case did
not reach the failure mode where Step 6 marks additive while dropping concrete
anchor entities.

Next valid moves:

- Run a focused marker/entity-loss construction follow-up.
- Or implement only ultra-dormant flags/archive/validation contracts while
  keeping visibility shadow-only until marker/entity risk is observed or covered
  by full calibration.

## Marker/Entity-Loss Follow-Up

`marker_entity_loss_followup_v0` has now been run.

New artifacts:

```text
pre_step6_marker_entity_loss_followup.v1
pre_step6_marker_entity_loss_step6_replay.v1
pre_step6_marker_entity_loss_followup_result.v1
```

Files:

- `scripts/research/pre_step6_marker_entity_loss_followup.py`
- `tests/test_pre_step6_marker_entity_loss_followup.py`
- `research/pre-step6-marker-entity-loss-followup/marker-entity-loss-followup.v1.json`
- `research/pre-step6-marker-entity-loss-followup/step6-replays/*.marker-entity-step6-replay.v1.json`
- `research/pre-step6-marker-entity-loss-followup/marker-entity-loss-followup-result.v1.json`
- `research/pre-step6-marker-entity-loss-followup-readout-2026-05-21.md`

Result:

- Live Step 6 replay used `openai/gpt-5.1-chat`.
- Three construction attempts tested resource generalization, tripwire
  compression, and actor-sequence blur.
- Step 6 emitted `all_private_or_confirming` on all three attempts.
- No reviewer calls were needed because the additive-plus-entity-loss
  precondition did not fire.
- Aggregate result: `not_observed`.

Interpretation:

The target failure shape still was not observed, but the evidence is more
useful than a weak null. Step 6 actively preserved the anchor's concrete
entities and treated generic deck pressure as rejected, private guardrail, or
confirming support. This reduces marker/entity false-positive concern while
leaving the omission gate's marker-vs-content-loss limitation as a calibration
dimension.

Next valid move:

- Proceed only to an ultra-dormant shadow implementation slice: flags, archive
  fields, validators, and Observatory/readout plumbing. No visible behavior
  change and no `SKILL.md` behavior change.
- Or pause implementation and curate the full calibration floor.

## Ultra-Dormant Shadow Portfolio Integration

`ultra_dormant_shadow_portfolio_integration_v0` has now landed.

New runtime artifact:

```text
pre_step6_shadow_portfolio.v1
```

Files:

- `engine/system_b/pre_step6_shadow_portfolio.py`
- `tests/test_pre_step6_shadow_portfolio_runtime.py`
- `scripts/run_pipeline.py`
- `scripts/archive_run.py`
- `observatory/serve_result.py`
- `research/pre-step6-shadow-portfolio-integration-readout-2026-05-21.md`

Result:

- Default behavior remains off.
- Shadow mode is explicit: `--pre-step6-portfolio shadow`.
- Shadow mode can read a precomputed card-deck cache but cannot generate one.
- Cache miss stands down to current Step 6 with 0 reviewer calls.
- Cache hit plus Step 6 additive ledger can record
  `deck_visible_shadow_only`, but never applies that to the visible answer.
- Payload omission and custody guardrails block deck-visible shadow decisions.
- Sidecars are written as `/tmp/lolla_{run_id}_pre_step6_shadow_portfolio.json`
  and archived as `pre_step6_shadow_portfolio.json`.
- Observatory exposes `/audit/pre-step6`; the case API includes the same block.
- `SKILL.md` behavior is unchanged.

Interpretation:

This is the first real runtime-adjacent learning instrument. It keeps the
portfolio philosophy intact: broad private evidence, Step 6 as cognition,
deterministic code as custody and guardrail, public output untouched.

Next valid move:

- Run archived cases in shadow mode and inspect whether the sidecars teach us
  something coherent.
- Then add fixed-suite precomputed decks and inspect cache-hit behavior.
- Do not inject decks into Step 6 or change visible-answer selection until the
  shadow evidence justifies the next gated slice.

## First Shadow Evidence Run

`shadow_evidence_run_v0` has now run.

Files:

- `scripts/research/pre_step6_shadow_portfolio_evidence.py`
- `tests/test_pre_step6_shadow_portfolio_evidence.py`
- `research/pre-step6-shadow-portfolio-evidence/`
- `research/pre-step6-shadow-evidence-run-readout-2026-05-21.md`

Result:

- Eight prior result artifacts from the phase2d scratch corpus produced
  `cache_miss -> current_step6_visible_no_deck`, with zero visible-output
  applications.
- Four fixed-suite cached decks produced cache hits.
- Founder, PhD, and consultant produced `deck_visible_shadow_only`.
- Mother produced `anchor_visible_deck_private_shadow_only`.
- Visible applications remained zero in both arms.

Read:

The shadow system is behaving like a learning instrument. It does not narrow
Step 6 early. It records whether cached broad context exists, preserves Step 6's
ledger distinction, and keeps public output locked.

Next best move:

- Expand cache coverage for more prior-result cases, then rerun the shadow
  evidence harness.
- Inspect representative `/audit/pre-step6` panels before any new prompt or
  visibility integration.

## Consultant-Triggered False-Positive Probe

`consultant_triggered_false_positive_probe_v0` has now run.

Files:

- `scripts/research/pre_step6_consultant_triggered_false_positive_probe.py`
- `tests/test_pre_step6_consultant_triggered_false_positive_probe.py`
- `research/pre-step6-consultant-triggered-false-positive-probe/false-positive-visibility-probe.v1.json`
- `research/pre-step6-consultant-triggered-false-positive-probe/step6-replays/*.json`
- `research/pre-step6-consultant-triggered-false-positive-probe/judgments/*.json`
- `research/pre-step6-consultant-triggered-false-positive-probe/false-positive-visibility-result.v1.json`
- `research/pre-step6-consultant-triggered-false-positive-probe-readout-2026-05-21.md`

Result:

- Consultant classification was corrected before the probe:
  `sensitive_safety_legal` / `positive_seed`.
- Consultant Step 6 replay emitted `additive_pressure_present`.
- Both reviewer families returned `true_visible`.
- Bevelin temptation stood down at Step 6.
- Marker/entity loss remained `not_observed`.

Read:

The team was right to separate telemetry from adversarial validation. The shadow
harness did not prove the consultant decision; it surfaced it. The probe then
tested it, and the decision survived.

Next best move:

- Keep using shadow telemetry for candidate discovery.
- For any surprising `deck_visible_shadow_only` case, run a pre-registered
  dual-reviewer probe before treating it as calibration evidence.

## Shadow-Triggered False-Positive Probe

`shadow_triggered_false_positive_probe_v0` has now run.

Files:

- `scripts/research/pre_step6_shadow_triggered_false_positive_probe.py`
- `tests/test_pre_step6_shadow_triggered_false_positive_probe.py`
- `research/pre-step6-shadow-triggered-false-positive-probe/false-positive-visibility-probe.v1.json`
- `research/pre-step6-shadow-triggered-false-positive-probe/step6-replays/*.json`
- `research/pre-step6-shadow-triggered-false-positive-probe/judgments/*.json`
- `research/pre-step6-shadow-triggered-false-positive-probe/false-positive-visibility-result.v1.json`
- `research/pre-step6-shadow-triggered-false-positive-probe-readout-2026-05-21.md`

Result:

- The shadow harness now records payload preservation outcomes and flags
  `deck_visible_with_marker_entity_loss`.
- Founder, PhD, and consultant surfaced as candidates.
- Fresh Step 6 stood down on PhD and consultant.
- Founder emitted `additive_pressure_present`, but the case is now
  `ambiguous_visibility` because reviewer labels and blind winner arms were
  tense.

Read:

The system got smarter in the right way. Shadow telemetry found the candidate,
fresh Step 6 reduced two historical replay signals to stand-downs, and the
reviewer-custody check prevented a tense `true_visible` label from being
remembered as a clean pass.

Next best move:

- Add a cheap answer-delta visible-effect specificity check before any runtime
  promotion discussion.
- Keep entity-level payload gating as the next fallback if founder-like
  ambiguity repeats.
- Keep `SKILL.md` unchanged.

## Answer-Delta Specificity

`answer_delta_specificity_v0` has now run.

Files:

- `research/pre-step6-answer-delta-specificity-probe/`
- `research/pre-step6-answer-delta-specificity-readout-2026-05-21.md`

Result:

- Step 6 replay prompts now request structured `answer_delta`.
- The dormant shadow resolver now blocks additive pressure when the ledger
  contains only missing or reframe-only deltas.
- Historical fixed-suite additive replay ledgers now produce
  `anchor_visible_answer_delta_guardrail_shadow_only`.
- Fresh answer-delta live replay on founder, PhD, and consultant produced
  `all_private_or_confirming` for all three.

Read:

This is the cheap-first fix doing real work. The system did not narrow private
context. It made Step 6 explain what concrete public payload changed. When the
deck only supplied confirming/reframing pressure, Step 6 stood down.

Next best move:

- Move from preamble mechanics to calibration coverage.
- Do not add entity-level payload gating unless a future
  `concrete_delta_present` case is rejected by reviewers.
- Keep `SKILL.md` unchanged.

## Falsifiers

- Step 6 over-explains every reserve item and recreates answer bloat.
- The compact map loses why a pressure mattered.
- Negative-control cases get extra active pressure because the map exists.
- Provider-generated affordance calls do not beat deterministic baseline
  conversion enough to justify cost.
