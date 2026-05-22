# Pre-Step-6 Design Preamble Autoresearch Track

Date: 2026-05-20

Status: research-only design track. This file does not change `SKILL.md`,
runtime behavior, default `/lolla`, or promotion policy.

## Board Thesis

The next step is not a runtime integration draft. The next step is an
autoresearch track that turns the design preamble into falsifiable contracts.

The governing invariant remains:

```text
Broad private context.
Narrow public answer.
Accountable bridge between them.
```

The deterministic system handles selection, custody, validation, cache keys,
schema checks, overlap groups, omission candidates, hygiene, and archive
truthfulness. It does not decide cognitive usefulness.

Step 6 remains the solver. It receives broader private material, accounts for
what it used or kept private, and writes the user-facing answer.

Cognitive review is a research and experimental calibration tool. It is not a
normal runtime correction loop.

## Design Claims To Test

### 1. Cost And Cache Contract

Experiment id: `design_preamble_cost_cache_v0`

Hypothesis:

```text
A cached-cards-first runtime can be viable only if the card deck is compiled
per run from cached lens substrates and current run artifacts, without live
LLM card generation on the normal runtime path.
```

Smallest research-only change:

- Define a `compiled_card_deck_key` contract.
- Record cache mode, cache hit/miss behavior, and cold-path policy in a fixture.
- Prove a miss in normal runtime stands down to current Step 6 instead of
  generating cards live.

Required cache key fields:

- card-deck schema version
- deck-builder version
- lens-pack versions
- lens-substrate hashes
- `conversation_ir` hash
- problem-state hash
- rendered-hybrid anchor hash
- V60 selected-item hash set, when V60 is active
- safety/profile flags
- Step 6 prompt-contract version

Promotion read:

- `off`: 0 added calls.
- `research`: live card generation allowed.
- `experimental`: cold-fill allowed only behind flag and budget.
- `runtime_cached_only`: cache miss records `card_deck_cache_miss` and stands
  down with 0 added calls.

Falsifier:

```text
If useful cards require live per-case LLM generation on most normal runs, the
cached-cards-first runtime is not viable as the first integration path.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

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
- Normal runtime reviewer calls remain 0 in every mode.
- The compiled key includes card schema, deck-builder version, lens pack
  versions, lens artifact hashes, conversation fixture hash, problem-state hash,
  rendered-hybrid anchor hash, V60 selected-item hashes, safety flags, and Step 6
  prompt-contract version.
- Static research fixtures do not carry live `ConversationIR` or real V60
  selected chunks; those fields are represented explicitly as research proxy or
  not-attached states.

Promotion read:

```text
The cached-cards-first runtime is plausible only as a cached/compiled path. A
normal runtime cache miss must not cold-generate cards. The next contract must
prove cards are generic before any cache hit can be meaningful.
```

### 2. Unified Ledger And V60 Redundancy

Experiment id: `design_preamble_ledger_overlap_v0`

Hypothesis:

```text
V60 chunks and reasoning cards can share one private-consideration ledger if
the hot context dedupes overlap for attention while the archive preserves every
source item for custody.
```

Smallest research-only change:

- Define `private_consideration_item.v1`.
- Add `overlap_group_id`, `primary_presented_item_id`, and `supporting_item_refs`.
- Add a fixture where a Bevelin card and a V60 chunk surface the same pressure.

Presentation policy:

```text
The hot context is deduped for attention.
The audit record is not deduped for custody.
```

Ledger disposition policy:

- `used`
- `rejected`
- `deferred`
- `not_considered`
- `private_guardrail`

Composition role policy:

- `solo`
- `combined`
- `confirming`
- `blocker`

Promotion read:

- Operator view shows one overlap group, not two unexplained duplicates.
- Source custody still shows both V60 and card sources.
- Step 6 ledger accounts for every presented representative and every
  supporting source item.

Falsifier:

```text
If overlap grouping either hides source custody or leaves Step 6 reading the
same pressure twice, the ledger design is not ready.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

```text
pre_step6_private_consideration_ledger_overlap.v1
private_consideration_item.v1
```

Files:

- `scripts/research/pre_step6_private_consideration_ledger.py`
- `tests/test_pre_step6_private_consideration_ledger.py`
- `research/pre-step6-private-consideration-ledgers/*.ledger-overlap.v1.json`

Result:

- The founder overlap fixture presents one hot-context representative:
  `reasoning_card:bevelin_card`.
- The unified ledger preserves both source items:
  `reasoning_card:bevelin_card` and
  `v60_chunk:overcommitment_without_evidence`.
- The overlap group records `single_representative_with_supporting_refs` for
  presentation and `all_source_items_preserved` for custody.
- Both items share one `overlap_group_id` and the V60-style item is marked
  `supporting_ref_not_repeated`.
- The V60 item is synthetic in this research slice; it tests schema shape, not a
  real V60 runtime selection.

Residual fixture coverage before design draft:

- Add a non-overlap fixture where a reasoning card and V60-style item both
  appear in hot context because they do not share a substantive pressure.
- Add a V60-only/no-deck fixture proving `private_consideration_item.v1` still
  works when no reasoning card is present.

2026-05-20 residual fixture result: `keep_research_only`.

- Non-overlap fixture:
  `founder-grant-marcus-equity.high-clutter.non-overlap.ledger-overlap.v1.json`.
  It keeps both `reasoning_card:polya_card` and
  `v60_chunk:absence_blocker_false_precision` in hot context with no shared
  `overlap_group_id`.
- V60-only/no-deck fixture:
  `synthetic-v60-only.ledger-overlap.v1.json`. It validates a single
  `v60_chunk:standalone_margin_of_safety` with `private_reasoning_cards: ""`.
- This proves overlap grouping is conditional, not a universal dedupe rule.

Promotion read:

```text
Hot context can be deduped without deleting source custody. The next contract
must prove deck-aware answers preserve anchor payload instead of introducing
critical omissions.
```

### 3. Critical-Omission Checklist

Experiment id: `design_preamble_payload_omission_v0`

Hypothesis:

```text
Critical omissions can be detected as omission candidates through a structured
must-keep payload checklist, with cognition reserved for severity judgment.
```

Smallest research-only change:

- Define `must_keep_payload.v1` with the six protected payload categories below.
- Extract or fixture category-level evidence from the anchor and deck answers.
- Compare deck-aware answer against anchor payload as a diff, not as an absolute
  completeness score.
- Emit introduced-omission candidates only where the category is live in the
  anchor and missing from the deck answer.
- Send only introduced-omission candidates to cognitive severity review in
  research mode.

Payload categories:

- dates or dated windows
- actor sequence
- named resources or channels
- communication boundaries
- tripwires, including explicit decision gates or stop/go conditions
- evidence checks

Activation and diff rule:

| Anchor | Deck | Judgment |
| --- | --- | --- |
| absent | absent | `case_n_a` |
| absent | present | `deck_added_payload` |
| present | present | `preserved` |
| present | absent | `introduced_omission` |

Only `introduced_omission` rows are omission-gate signals. The gate is not an
overall answer-completeness score.

Detection rule:

```text
Mechanistic first. Category-scoped cognition only when a finite detector cannot
decide a single category-level boolean. Never ask an LLM to grade overall
completeness.
```

The omission gate is a post-visibility safety net and promotion tripwire. It
must not choose between anchor and deck answers. If visibility policy says
deck-visible and the omission gate finds an introduced omission, the action is
`retest` or `defer`, not "deterministically pick the anchor."

Minimum category record:

```json
{
  "category": "dates_or_dated_windows",
  "anchor_present": true,
  "deck_present": false,
  "case_live": true,
  "judgment": "introduced_omission",
  "detector": "regex_date_pattern_v0",
  "anchor_evidence": ["..."],
  "deck_evidence": [],
  "missing_anchor_evidence": ["..."]
}
```

Promotion read:

- Deterministic checks flag category-level omission candidates.
- Cognitive review, if needed, classifies candidates as `critical`, `noncritical`,
  `intentionally_removed`, or `ambiguous`.
- Promotion fails on unresolved critical omissions.

Falsifier:

```text
If the checklist misses human-obvious critical omissions or flags so much noise
that reviewers ignore it, the omission gate is not usable.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

```text
pre_step6_payload_omission.v1
```

Files:

- `scripts/research/pre_step6_payload_omission_gate.py`
- `tests/test_pre_step6_payload_omission_gate.py`
- `research/pre-step6-payload-omission-gates/*.payload-omission.v1.json`

Result:

- The gate uses exactly six protected categories:
  dates/windows, actor sequence, named resources/channels, communication
  boundaries, tripwires/gates, and evidence checks.
- Activation is anchor-based: if the anchor lacks the category, the case is
  `case_n_a` rather than an omission.
- The gate is diff-based: only anchor-present/deck-absent rows become
  `introduced_omission`.
- Detection is mechanistic-first. A synthetic RED/GREEN test caught an overly
  broad named-resource detector that treated ordinary capitalized words as
  resources; the detector was narrowed to explicit resource/channel patterns.
- The omission gate does not decide visibility. It records
  `visibility_decision: not_decided_by_omission_gate`.
- Four fixed-suite fixtures validate. All four are `preserved` at the protected
  category level.

Interpretation:

```text
The current deck-aware answers did not subtract the six protected anchor
payload categories. The mother stand-down remains a phrasing/tightness and
sensitive-safety visibility result, not a protected-payload omission result.
```

Promotion read:

```text
The omission contract is useful as a promotion tripwire. It is not a visibility
selector and not a general completeness rubric.
```

### 4. Visibility Policy And Runtime Asymmetry

Experiment id: `design_preamble_visibility_asymmetry_v0`

Hypothesis:

```text
Runtime should be anchor-biased in public output while remaining broad in
private context. Research and experimental modes may retest once; normal
runtime should not run a live reviewer loop.
```

Smallest research-only change:

- Define mode-specific visibility policy.
- Encode tie/disagreement behavior.
- Add fixtures for anchor-confirmed, deck-confirmed, tie, and ledger/reviewer
  disagreement.

Runtime rule:

```text
Tie or unresolved means anchor visible, deck private, audit preserved.
```

Research/experimental rule:

```text
One bounded retest may run with a fresh blind shuffle, same rubric, and a
different model family if available.
```

Deck-visible threshold:

```text
The second reviewer must prefer the deck. Non-inferior keeps the deck alive for
research, but does not make it visible.
```

Promotion read:

- Normal runtime has no comparison loop.
- Research mode can study disagreement without infinite retries.
- False stand-down becomes the named failure mode to measure.

Falsifier:

```text
If anchor bias suppresses useful deck pressure without a measurable
false-stand-down audit path, the runtime policy is too conservative.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

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
- Research and experimental modes allow at most one retest.
- The second-reviewer policy is explicit: different model family if available,
  same rubric, fresh blind shuffle.
- Deck-visible after retest requires the second reviewer to prefer the deck.
  Non-inferior keeps the deck alive for research only.
- Fixtures cover runtime-unresolved, deck-confirmed, anchor-confirmed, tie, and
  ledger/reviewer disagreement.
- False stand-down is named as the primary runtime failure mode.

Promotion read:

```text
The runtime asymmetry is now explicit: broad private, anchor-biased public when
unresolved, no normal live reviewer loop. Calibration must measure whether this
creates false stand-downs.
```

### 5. Generic Card Interface

Experiment id: `design_preamble_card_interface_v0`

Hypothesis:

```text
Bevelin and Polya can be first implementations of a generic private-card
interface instead of hardcoded architecture.
```

Smallest research-only change:

- Define `private_reasoning_card.v1`.
- Validate existing clean-hybrid, Bevelin, and Polya cards through the generic
  schema.
- Add one synthetic future-card fixture to prove the deck builder is not
  Bevelin/Polya-specific.

Minimum card fields:

- `card_id`
- `card_type`
- `source_kind`
- `source_ref`
- `cognitive_role`
- `receipts`
- `handling_rule`
- `activation_scope`
- `misuse_guard`
- `standdown_condition`
- `public_hygiene_terms`
- `expansion_ref`

Promotion read:

- New cards can enter without changing visibility policy or ledger semantics.
- Public answer still hides card names and internal machinery.

Falsifier:

```text
If adding a third lens requires touching deck policy, visibility policy, and
ledger semantics, the card interface is not general enough.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

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
  `private_reasoning_card.v1` schema.
- The generic schema includes card type, source, receipts, cognitive role,
  handling rule, activation scope, misuse guard, stand-down condition, public
  hygiene terms, and expansion ref.
- A synthetic future card validates without adding visibility-policy or ledger
  fields.
- The interface read explicitly records that Bevelin/Polya are not
  special-cased and that a new card should not require policy or ledger changes.

Promotion read:

```text
The card interface is general enough for the next design slice. It does not yet
prove V60/card overlap handling, cache-hit usefulness, or runtime integration.
```

### 6. Calibration Floor And Stand-Down Recall

Experiment id: `design_preamble_calibration_floor_v0`

Hypothesis:

```text
The four-case suite is a seed suite, not calibration. Promotion needs a larger
case manifest plus explicit false-stand-down measurement.
```

Smallest research-only change:

- Define a calibration manifest with 12 to 20 cases.
- Require high-clutter, sequencing, sensitive/safety, negative-control, and V60
  on/off comparison buckets.
- Add stand-down audit fields.

Minimum buckets:

- at least 3 high-clutter cases
- at least 3 sequencing or problem-shape cases
- at least 3 sensitive/safety/legal cases
- at least 3 negative controls
- at least 2 cases run with V60 on and off to separate baseline effects

Stand-down classifications:

- `true_standdown`
- `false_standdown`
- `ambiguous_standdown`

Promotion read:

- Current four-case result remains promising but non-promotional.
- False stand-down rate is tracked by case type, card type, and V60 overlap.
- Runtime promotion remains blocked until stand-down recall is measured.

Falsifier:

```text
If stand-downs cluster in cases where card-deck pressure later proves useful,
the anchor bias is too strong or the card ledger is under-reporting additive
pressure.
```

2026-05-20 run result: `keep_research_only`.

Implemented research artifact:

```text
pre_step6_calibration_floor.v1
```

Files:

- `scripts/research/pre_step6_calibration_floor_manifest.py`
- `tests/test_pre_step6_calibration_floor_manifest.py`
- `research/pre-step6-calibration-floor/seed-suite.calibration-floor.v1.json`

Result:

- The current four-case suite is recorded as `seed_suite_not_calibration`.
- The manifest requires 12-20 total cases before promotion.
- Minimum buckets are explicit: 3 high-clutter, 3 sequencing/problem-shape, 3
  sensitive/safety/legal, 3 negative controls, and 2 V60 on/off comparison
  pairs.
- Current observed coverage is 1 high-clutter, 1 sequencing/problem-shape, 1
  sensitive/safety/legal, 2 negative controls, and 0 V60 on/off pairs.
- A V60 on/off pair is defined as the same case run twice with the same prompt
  contract and card-deck policy: once with V60 selected items available and
  once with V60 selected items withheld. "Substantive V60" versus "minimal V60"
  is a useful stratification label, not a substitute for same-case toggles.
- The manifest names the missing curation work instead of fabricating
  calibration cases.
- Stand-down recall is present but `not_calibrated`; mother is only a
  `true_standdown_candidate` with `seed_only` weight.
- Payload preservation now tracks
  `preserved_by_marker_anchor_entities_missing` as a calibration-time outcome.
  This records the limitation that the omission gate can preserve category
  markers while losing concrete anchor entities inside the category.
- The next bridge probe is pinned as `false_standdown_bridge_probe_v0`: 2-3
  deliberately dangerous non-promotional cases before full curation.
- `calibration_floor_met: false` and
  `promotion_read: runtime_promotion_blocked`.

Promotion read:

```text
The design-preamble contracts now exist, but integration remains blocked by
calibration evidence. The cheapest next learning step is a non-promotional
false-standdown bridge probe before full case-floor curation.
```

2026-05-21 bridge-probe result: `design_review_required`.

Implemented research artifacts:

```text
pre_step6_false_standdown_bridge_probe.v1
pre_step6_false_standdown_bridge_judgment.v1
pre_step6_false_standdown_bridge_result.v1
```

Files:

- `scripts/research/pre_step6_false_standdown_bridge_probe.py`
- `tests/test_pre_step6_false_standdown_bridge_probe.py`
- `research/pre-step6-false-standdown-bridge-probe/*.json`
- `research/pre-step6-false-standdown-bridge-probe/judgments/*.json`
- `research/pre-step6-false-standdown-bridge-probe-readout-2026-05-21.md`

Result:

- Three bridge cases were pre-registered with selection labels before live
  reviewer calls.
- `confirmed_false_standdown` required two reviewer judgments from different
  model families under the same rubric and fresh blind shuffles.
- All three cases were confirmed `false_standdown` by both `openai` and
  `google` reviewer families.
- Aggregate result is `design_review_required`.
- This is non-promotional packet-level evidence, not full runtime evidence.

Design consequence:

```text
Do not proceed to integration draft with a universal runtime unresolved ->
anchor_visible_deck_private policy. Run a visibility-policy redesign slice
that tests ledger-mediated runtime visibility without adding a reviewer loop.
```

2026-05-21 redesign result: `keep_research_only`.

Implemented research artifact:

```text
pre_step6_visibility_policy_redesign.v1
```

Files:

- `scripts/research/pre_step6_visibility_policy_redesign.py`
- `tests/test_pre_step6_visibility_policy_redesign.py`
- `research/pre-step6-visibility-policy-redesign/*.visibility-policy-redesign.v1.json`
- `research/pre-step6-visibility-policy-redesign-readout-2026-05-21.md`

Result:

- Legacy universal anchor fallback would suppress all three bridge
  false-standdown cases.
- The redesigned policy surfaces deck-aware output when cache is hit, Step 6
  records additive non-anchor pressure, and protected payload is preserved.
- Anchor/current-Step-6 fallback remains for private/confirming ledgers, missing
  or unclear ledgers, payload omission, and cache miss.
- Normal runtime reviewer calls remain 0.

Promotion read:

```text
The false-standdown policy flaw is fixed at contract level, but runtime remains
blocked. The next missing evidence is whether full Step 6 bridge replays produce
the additive ledger signals this policy depends on.
```

2026-05-21 bridge replay result: `keep_research_only`.

Implemented research artifacts:

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

- The three pre-registered bridge packets were replayed through a live
  Step-6-style call using `openai/gpt-5.1-chat`.
- All three produced `ledger_signal: additive_pressure_present`.
- Aggregate result:

```text
step6_additive_signal_supported
```

Promotion read:

```text
The visibility redesign's ledger dependency is supported for the bridge
packets. Runtime remains blocked because this does not yet prove full production
card compilation, cache-hit behavior, V60 overlap handling, payload preservation,
or calibrated false-standdown/false-promotion rates.
```

2026-05-21 integration design draft: `keep_research_only`.

Design artifact:

```text
research/pre-step6-ledger-mediated-integration-design-draft-2026-05-21.md
```

The draft converts the preamble contracts into a dormant integration shape:

```text
broad private deck -> Step 6 answer + private ledger -> deterministic guards -> visible answer decision
```

It defines:

- mode gates from `off` to blocked `runtime_on`;
- cache-hit-only deck availability;
- Step 6 prompt/ledger contract;
- unified ledger fields and overlap handling;
- visibility resolver table;
- payload gate as tripwire;
- archive and Observatory fields;
- no-reviewer-loop cost envelope;
- promotion gates and falsifiers.

Promotion read:

```text
The design preamble has enough evidence to support a dormant/shadow integration
slice. It still does not support runtime promotion.
```

2026-05-21 false-positive probe result: `continue_probe_with_not_observed`.

Implemented research artifacts:

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

- Step 6 stood down on Bevelin-temptation and Polya-temptation cases:
  `all_private_or_confirming`.
- The marker-preserved/entity-lost shape did not reach the failure mode because
  Step 6 preserved the concrete anchor entities and also stood down.
- Therefore the marker/entity-loss dimension is `not_observed`, not passed.
- No false positive was confirmed; no runtime or `SKILL.md` behavior changed.

Promotion read:

```text
The mirror false-positive direction is partly de-risked, but the known
marker-vs-content-loss weakness remains unclosed. A shadow implementation, if
started, should be ultra-dormant and visibility shadow-only; otherwise run a
focused marker/entity-loss follow-up first.
```

## Marker/Entity-Loss Follow-Up

2026-05-21 marker/entity-loss follow-up result: `not_observed`.

Implemented research artifacts:

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

- Three pre-registered construction attempts targeted resource generalization,
  tripwire compression, and actor-sequence blur.
- Step 6 emitted `all_private_or_confirming` on all three attempts.
- No reviewer calls were needed because no attempt reached
  `additive_pressure_present` plus marker-present/entity-lost output.
- Step 6 preserved the concrete anchor entities and treated generic deck
  pressure as rejected, private guardrail, or confirming support.

Promotion read:

```text
The marker/entity false-positive concern is further reduced, but the omission
gate weakness is still a calibration dimension because the failure shape was not
observed. The next implementation step can only be ultra-dormant and
shadow-only; runtime promotion remains blocked.
```

## Ultra-Dormant Shadow Portfolio Integration

2026-05-21 shadow implementation result:
`ultra_dormant_shadow_portfolio_integration_v0` has landed.

Implemented artifacts:

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

- Default runtime remains off.
- Shadow mode can be enabled with `--pre-step6-portfolio shadow` or
  `LOLLA_PRE_STEP6_PORTFOLIO=shadow`.
- Cached deck lookup is read-only; cache misses stand down to current Step 6.
- Normal runtime reviewer calls remain 0.
- Live card generation remains disallowed.
- Shadow decisions are never applied to the user-visible answer.
- Sidecars are archived as `pre_step6_shadow_portfolio.json`.
- Observatory renders `/audit/pre-step6` and the case API includes
  `pre_step6_shadow_portfolio`.
- `SKILL.md` behavior is unchanged.

Promotion read:

```text
keep_shadow_only
runtime_promotion_blocked
skill_update_blocked
```

Interpretation:

This is now an evidence-gathering instrument. It proves the runtime can preserve
the portfolio policy's audit surface without handing public visibility to the
deterministic layer. The next evidence should come from shadow archives, not
from widening the runtime gate.

## First Shadow Evidence Run

2026-05-21 evidence result: `shadow_evidence_run_v0` has run.

New files:

- `scripts/research/pre_step6_shadow_portfolio_evidence.py`
- `tests/test_pre_step6_shadow_portfolio_evidence.py`
- `research/pre-step6-shadow-portfolio-evidence/combined.shadow-evidence-result.v1.json`
- `research/pre-step6-shadow-evidence-run-readout-2026-05-21.md`

Result:

- Prior-result cache-miss arm: 8/8 cache misses stood down to current Step 6,
  with 0 visible applications.
- Fixed-suite cache-hit arm: 4/4 cache hits resolved in shadow.
- Founder, PhD, and consultant produced `additive_pressure_present` and
  `deck_visible_shadow_only`.
- Mother produced `all_private_or_confirming` and
  `anchor_visible_deck_private_shadow_only`.
- All decisions remained shadow-only.

Interpretation:

The system is now learning in the intended way. The broad private portfolio can
exist as cache evidence, Step 6's private ledger carries the cognitive signal,
and deterministic code only preserves custody and records the guarded shadow
decision.

## Consultant-Triggered False-Positive Probe

2026-05-21 probe result: `consultant_triggered_false_positive_probe_v0` has run.

New files:

- `scripts/research/pre_step6_consultant_triggered_false_positive_probe.py`
- `tests/test_pre_step6_consultant_triggered_false_positive_probe.py`
- `research/pre-step6-consultant-triggered-false-positive-probe/`
- `research/pre-step6-consultant-triggered-false-positive-probe-readout-2026-05-21.md`

Pre-run correction:

```text
mid-level-consultant-report-2
case_type_tags: sensitive_safety_legal
calibration_role: positive_seed
```

Result:

- Consultant produced `additive_pressure_present`.
- `openai/gpt-5.1-chat` reviewer returned `true_visible`.
- `google/gemini-3.1-flash-lite` reviewer returned `true_visible`.
- Bevelin temptation stood down at Step 6.
- Marker/entity-loss remained `not_observed`.
- Stop condition did not trigger.

Interpretation:

The shadow harness was correctly demoted to telemetry, but it surfaced the right
follow-up. Consultant should no longer be treated as a negative-control seed.
It is a positive sensitive/legal seed whose deck-visible result survived the
two-family false-positive check.

## Shadow-Triggered False-Positive Probe

2026-05-21 probe result: `shadow_triggered_false_positive_probe_v0` has run.

New files:

- `scripts/research/pre_step6_shadow_triggered_false_positive_probe.py`
- `tests/test_pre_step6_shadow_triggered_false_positive_probe.py`
- `research/pre-step6-shadow-triggered-false-positive-probe/`
- `research/pre-step6-shadow-triggered-false-positive-probe-readout-2026-05-21.md`

Result:

- The shadow harness now records per-category payload-preservation outcomes and
  flags `deck_visible_with_marker_entity_loss` candidates.
- The fixed-suite cache-hit arm surfaced founder, PhD, and consultant as
  shadow-triggered candidates.
- Fresh Step 6 stood down on PhD and consultant under the probe contract.
- Founder produced `additive_pressure_present`, but the aggregate result is
  `continue_probe_with_ambiguity`, not a clean pass.

Interpretation:

This slice found an evaluator problem worth keeping. The founder reviewers both
returned `true_visible`, but both blind winner arms pointed to
`anchor_visible`. One reviewer treated the deck as non-inferior; the other said
the deck missed critical context. The result builder now records
`reviewer_winner_arms`, `reviewer_non_inferiority_reads`, and
`reviewer_label_consistency`, and demotes tense `true_visible` cases to
`ambiguous_visibility`.

That preserves the philosophy: reviewers provide cognition, while deterministic
code checks custody. A tense reviewer label is not counted as a clean promotion
signal.

## Answer-Delta Specificity

2026-05-21 result: `answer_delta_specificity_v0` has run.

New files:

- `research/pre-step6-answer-delta-specificity-probe/`
- `research/pre-step6-answer-delta-specificity-readout-2026-05-21.md`

Changed contracts:

- Step 6 ledger items may now include structured `answer_delta`:
  `added_entities`, `removed_entities`, `reordered_sequences`, and
  `reframed_emphasis`.
- The shadow resolver derives `answer_delta_specificity`.
- Additive ledgers with no concrete delta fall to
  `anchor_visible_answer_delta_guardrail_shadow_only`.

Result:

- Historical fixed-suite additive replay ledgers now stand down because they
  lack structured concrete deltas.
- Fresh answer-delta live replay on founder, PhD, and consultant produced
  `all_private_or_confirming` for all three cases.

Interpretation:

The cheap-first failure response worked. We did not ask deterministic code to
judge whether a framing was wise. We asked Step 6 to account for concrete public
changes. When it could not name them, it stopped treating the deck as additive
visible payload.

## Experiment Order

Run the design track in this order:

1. `design_preamble_cost_cache_v0`
2. `design_preamble_card_interface_v0`
3. `design_preamble_ledger_overlap_v0`
4. `design_preamble_payload_omission_v0`
5. `design_preamble_visibility_asymmetry_v0`
6. `design_preamble_calibration_floor_v0`

The order is intentional. Cost and cache shape determines whether the design is
runtime-plausible. The generic card interface determines whether Bevelin and
Polya are implementations or infrastructure. Ledger overlap must be solved
before Observatory design. Omission and visibility policy come after those
contracts are stable. Calibration is the final promotion floor, not the first
thing to overfit.

## Design Preamble Exit Criteria

The design preamble can move from research track to integration draft only when
all are true:

- cache modes and cold-path behavior are explicit;
- generic card schema validates current and at least one future-card fixture;
- V60/card overlap is represented without duplicate hot-context bloat;
- critical omissions have a payload checklist and cognitive severity path;
- runtime asymmetry is explicit: deck-private default, deck-visible higher bar;
- tie and disagreement behavior is bounded by mode;
- calibration manifest exists and names false stand-down as the primary
  post-promotion failure mode.

Until then, the correct status is:

```text
keep_research_only
runtime_dormant
skill_update_blocked
```
