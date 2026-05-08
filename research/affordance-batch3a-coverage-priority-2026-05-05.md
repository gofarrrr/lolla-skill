# Affordance Batch 3a Coverage Priority

**Date:** 2026-05-05
**Status:** Docs-only coverage-priority report. No extraction performed.

**Inputs:**
- `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
- `research/gate4-3case-product-readout-2026-05-05.md`
- `research/gate4-3case-claude-code-review-2026-05-05.md`
- `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/summary.json`
- `data/evaluations/gate4_edge_probes/summary.json`
- `data/compiled/model_affordances/affordances_v3.json`
- `data/curation/*.json` for source-shape context where model source files are not resident in `data/model_sources/`
- `plans/knowledge-substrate-roadmap-2026-05-04.md`
- `plans/knowledge-use-schema-2026-05-04.md`

**Non-goals:**
- No paid model calls.
- No judge calls.
- No live `/lolla`.
- No runtime, prompt, validator, or affordance-record changes.
- No broad Batch 3.
- No new lane.
- No second public Pressure Check.

**Rule:** Coverage expansion is subordinate to the Decision Pressure surface.

Doctrine line: Surface pulls extraction. Extraction does not push the product.

## Recommendation

Recommendation: `extract_5`.

Batch 3a should be a **targeted coverage patch**, not corpus expansion.

This is a conditional extraction recommendation, not an instruction to extract
immediately. The dry surface still needs a selection-stability review before
Batch 3a becomes the clean next implementation move. If a second reviewer cannot
select a similar 1-3 pressure surface from the same packet and gates, extraction
would be premature because the surface pull is not stable enough yet.

Recommended Batch 3a model IDs:

1. `opportunity-cost`
2. `true-uncertainty-navigation`
3. `falsifiability`
4. `principal-agent-problem`
5. `probabilistic-thinking`

Changed extraction standard:

> Extract Decision Pressure-ready operational constraints, not general model explanations.

That means the extractor should prioritize:

- treatment requirements;
- case evidence needed;
- misuse guards;
- do-not-use conditions;
- dismissal logic;
- tripwires, stop conditions, and operational constraints.

The goal is not to improve coverage statistics. The goal is to improve future
selection, dismissal, and coverage honesty for compact Decision Pressures.

## Evidence Base

Current v3 corpus shape:

- model records: `50`
- affordances: `86`
- absence records: `83`

Full 10-case dry-run:

- artifact: `data/evaluations/gate4_edge_probes/summary.json`
- cases: `10`
- routes: `39`
- v3-covered candidate appearances: `165/205`
- missing candidate appearances: `40`
- budget-driven omissions: `0`
- status: `dry_run`

3-case calibration:

- artifact: `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/summary.json`
- cases: `3`
- routes: `12`
- judge calls: `0`
- missing candidate appearances: `14`
- trust-critical gap: `third-year-phd-student / competitive-dynamics`, where all five candidates were missing and Arm C generated phantom traces.

The full 10-case summary is the missing-frequency evidence. The 3-case dry
surface is the product-relevance evidence.

Verification note:

- The full dry-run coverage math was recomputed from the `omissions` list:
  `165` covered candidate appearances, `40` missing appearances, `205` total,
  `0` budget omissions, or `80.49%` coverage.
- The missing-frequency counts below were checked against the committed
  `data/evaluations/gate4_edge_probes/summary.json` artifact.
- These counts are coverage evidence only. They do not override the product
  sequence: selection stability first, extraction second.

## Starting Candidate Set

The current PR13 starting candidate set is:

- `opportunity-cost`
- `principal-agent-problem`
- `true-uncertainty-navigation`
- `probabilistic-thinking`
- `falsifiability`
- `batna`
- `game-theory-payoffs`
- `nash-equilibrium`
- `prisoners-dilemma`
- `red-queen-effect`

The full 10-case dry-run also shows missing records outside that starting set:

- `commitment-bias`
- `lock-in`
- `path-dependence`
- `switching-costs`
- `creative-destruction`
- `lean-startup-methodology`

Those are recorded below, but they are not recommended for Batch 3a because the
PR13 product surface was calibrated on the 3-case packet and the top five
starting candidates already cover the repeated resource, uncertainty,
incentive, and information-quality gaps.

## Missing Frequency

| Model ID | Full 10-case missing frequency | 3-case missing frequency | Routes/cases affected | Full-route coverage-gap risk |
| --- | ---: | ---: | --- | --- |
| `opportunity-cost` | 7 | 2 | resource-allocation across Marcus/equity/PhD/fintech/oncology; one existing-vs-new route | No full route, but repeated high-importance partial gaps |
| `true-uncertainty-navigation` | 5 | 2 | uncertainty-type across mother/PhD/fintech/oncology/protect-year | No full route, but repeated 60% route coverage |
| `probabilistic-thinking` | 5 | 2 | uncertainty-type across the same routes as true uncertainty | No full route, but repeated 60% route coverage |
| `falsifiability` | 4 | 1 | information-quality across Marcus/equity/oncology | No full route, but high Decision Pressure relevance |
| `principal-agent-problem` | 4 | 2 | incentive-alignment across mother/PhD/oncology/protect-year | No full route, but repeated alignment gaps |
| `commitment-bias` | 2 | 0 | commitment-reversibility in two consultant cases | Severe partial-route risk, outside starting set |
| `lock-in` | 2 | 0 | commitment-reversibility in two consultant cases | Severe partial-route risk, outside starting set |
| `path-dependence` | 2 | 0 | commitment-reversibility in two consultant cases | Severe partial-route risk, outside starting set |
| `switching-costs` | 2 | 0 | commitment-reversibility in two consultant cases | Severe partial-route risk, outside starting set |
| `batna` | 1 | 1 | PhD competitive-dynamics | Yes, part of 0/5 route |
| `creative-destruction` | 1 | 0 | Marcus existing-vs-new | Partial route, outside starting set |
| `game-theory-payoffs` | 1 | 1 | PhD competitive-dynamics | Yes, part of 0/5 route |
| `lean-startup-methodology` | 1 | 0 | Marcus existing-vs-new | Partial route, outside starting set |
| `nash-equilibrium` | 1 | 1 | PhD competitive-dynamics | Yes, part of 0/5 route |
| `prisoners-dilemma` | 1 | 1 | PhD competitive-dynamics | Yes, part of 0/5 route |
| `red-queen-effect` | 1 | 1 | PhD competitive-dynamics | Yes, part of 0/5 route |

## Decision-Priority Ranking

This ranking is not coverage-statistical. It weights missing frequency,
full-route risk, route/product importance, Decision Pressure relevance, likely
high-value fields, absence-record likelihood, and whether extraction would
improve the compact surface.

| Rank | Model ID | Decision Pressure relevance | Likely high-value field yield | Absence record may be correct? | Decision |
| ---: | --- | --- | --- | --- | --- |
| 1 | `opportunity-cost` | Very high. Repeated resource-allocation gaps; directly affects what the user sacrifices, delays, funds, or stops. | `treatment_requirements`, `case_evidence_needed`, dismissal logic, stop conditions around displaced alternatives. | Low. Existing curation source shape is operational: `trade-off pricing check`. | Extract in Batch 3a. |
| 2 | `true-uncertainty-navigation` | Very high. Repeated uncertainty-type gaps and directly relevant to safety, oncology, fintech, and PhD commitments. | `misuse_guards`, `do_not_use_when`, treatment requirements for robust action, tripwires for uncertainty theater. | Low to medium. Some fields may become absence records if source supports scenario discipline but not exact tripwires. | Extract in Batch 3a. |
| 3 | `falsifiability` | Very high. Lower frequency than probability models, but directly supplies dismissal logic and kill criteria. | `case_evidence_needed`, disconfirming tests, dismissal conditions, tripwires / kill criteria. | Low. Existing curation source shape is `disconfirming test design`. | Extract in Batch 3a. |
| 4 | `principal-agent-problem` | High. Repeated incentive-alignment gap; useful where compliance, hidden action, or agent incentives matter. | `treatment_requirements`, `misuse_guards`, case evidence for alignment, dismissal logic around observed voluntary alignment. | Low to medium. Avoid if the source would only restate incentives/information-asymmetry records. | Extract in Batch 3a. |
| 5 | `probabilistic-thinking` | High. Frequency is high, but generic-number risk is also high. Useful if extracted as false-precision discipline, not forecast theater. | `do_not_use_when`, misuse guards, probability-range evidence, sensitivity checks, tripwires against exact-looking numbers. | Medium. Some desired tripwires may be unsupported and should become absence records. | Extract in Batch 3a with strict anti-fake-precision guard. |
| 6 | `lock-in` | Medium-high. Severe partial commitment-reversibility gaps in the full dry-run, but not part of the 3-case product calibration. | Reversibility constraints, hidden switching friction, do-not-use conditions for defending inertia. | Low. Existing curation source shape is operational. | Defer; watchlist for a later commitment-reversibility patch. |
| 7 | `switching-costs` | Medium-high. Similar commitment-reversibility value, outside PR13 starting set. | Exit sequencing, coexistence drag, hidden switching cost evidence, dismissal logic. | Low. Existing curation source shape is operational. | Defer; not Batch 3a. |
| 8 | `path-dependence` | Medium. Useful for installed constraints, but can become generic history explanation. | Operational constraints and anti-romantic-history do-not-use conditions. | Medium. Extract only if source supports action constraints. | Defer. |
| 9 | `commitment-bias` | Medium. Strong anti-escalation relevance, but risks overlapping sunk-cost/lock-in and can become moralizing. | Recommit-or-exit checks, stop rules, misuse guards against public-commitment defense. | Medium. Some value may already be covered by existing sunk-cost and optionality records. | Defer. |
| 10 | `batna` | Medium. Low frequency, but highly operational and could help competitive/negotiation pressures. | Walk-away evidence, minimum terms, no-go thresholds, dismissal conditions. | Low. Existing curation source shape is operational. | Defer; only one current appearance. |
| 11 | `game-theory-payoffs` | Medium. Full-route gap, but high abstraction risk and only one current appearance. | Player/payoff map, countermove evidence, do-not-use conditions against recursive speculation. | Medium. Extract only if source supports bounded, user-action constraints. | Defer; zero-output is currently better. |
| 12 | `red-queen-effect` | Medium-low. Could produce tripwires around pace and adaptation, but only one current appearance. | Stop conditions against speed theater, adaptation thresholds, monitoring constraints. | Medium. Might be source-thin for Decision Pressure use. | Defer. |
| 13 | `lean-startup-methodology` | Medium-low. Operational source shape, but outside starting set and one appearance. | Experiment thresholds, validated-learning kill criteria, do-not-use for safety/compliance shortcuts. | Low to medium. | Defer. |
| 14 | `creative-destruction` | Low-medium. Could be powerful but risks boldness theater. | Misuse guards against novelty theater, replacement evidence requirements. | Medium-high. | Defer. |
| 15 | `nash-equilibrium` | Low-medium. Full-route gap, but likely abstract and easy to misuse as faux rigor. | Stable-response map, do-not-use conditions, bounded-player constraints. | Medium-high. | Defer. |
| 16 | `prisoners-dilemma` | Low-medium. Full-route gap, but risks imposing hostile defection framing. | Cooperation design, enforcement gaps, do-not-use conditions against adversarial overframing. | Medium-high. | Defer. |

## Recommended Batch 3a Scope

Batch 3a should extract only:

- `opportunity-cost`
- `true-uncertainty-navigation`
- `falsifiability`
- `principal-agent-problem`
- `probabilistic-thinking`

This is the smallest patch that addresses the repeated high-value missing
patterns in the current evidence:

- resource-allocation routes repeatedly miss `opportunity-cost`;
- uncertainty-type routes repeatedly miss `true-uncertainty-navigation` and `probabilistic-thinking`;
- incentive-alignment routes repeatedly miss `principal-agent-problem`;
- information-quality routes repeatedly miss `falsifiability`;
- the dry surface selected or suppressed pressures that would benefit from
  these records without requiring a new lane or broad corpus expansion.

Execution gate:

Do not start Batch 3a solely from this coverage report. Start it only after one
of these is true:

- PR14 selection-stability review confirms the same compact Decision Pressure
  shape; or
- Marcin explicitly accepts the product risk of extracting before selection
  stability is tested.

## How Each Recommended Model Helps The Compact Surface

### `opportunity-cost`

Surface gap helped:

- Makes resource-allocation pressures more honest about what the user is
  sacrificing when they say yes to a sprint, equity grant, launch path, or
  clinical path.

High-value extraction target:

- treatment requirements for naming the next-best alternative;
- case evidence needed to show a sacrifice is real and executable;
- dismissal logic when alternatives are not available;
- tripwires for when the current yes should stop.

### `true-uncertainty-navigation`

Surface gap helped:

- Strengthens uncertainty-type pressures where the current surface can say
  "instrument trust" or "confidence calibration" but cannot yet draw from the
  missing model that should govern robust action under genuine ambiguity.

High-value extraction target:

- robust-action treatment requirements;
- misuse guards against scenario theater;
- do-not-use conditions when uncertainty work would not change the next move;
- monitoring or commitment-sizing tripwires.

### `falsifiability`

Surface gap helped:

- Directly improves dismissal paths and kill criteria for platform sprints,
  PhD shaping phases, and other hypothesis-bearing recommendations.

High-value extraction target:

- disconfirming evidence requirements;
- what would reverse the recommendation;
- hypothesis under-review constraints;
- tripwires and stop conditions that are user-verifiable.

### `principal-agent-problem`

Surface gap helped:

- Improves incentive-alignment pressures where hidden divergence or delegated
  incentives matter, without forcing all such material through moral hazard or
  information asymmetry.

High-value extraction target:

- alignment evidence requirements;
- misuse guards against assuming bad faith;
- dismissal logic when voluntary alignment is observed;
- accountability redesign constraints.

### `probabilistic-thinking`

Surface gap helped:

- Improves uncertainty surfaces when the useful move is a probability range,
  sensitivity check, or false-precision guard rather than a narrative.

High-value extraction target:

- do-not-use conditions against exact-looking numbers without evidence;
- sensitivity checks;
- confidence-range evidence requirements;
- tripwires for when probability language is postponing commitment rather than
  improving it.

## Deferred Starting-Set Models

The five competitive-dynamics starting candidates are not recommended for
Batch 3a:

- `batna`
- `game-theory-payoffs`
- `nash-equilibrium`
- `prisoners-dilemma`
- `red-queen-effect`

Reason:

- They produce a full-route gap in the 3-case calibration, which is important.
- But each appears only once in the full 10-case dry-run.
- The current dry surface did not need a competitive-dynamics pressure.
- The failed PhD competitive route is better handled as coverage transparency
  than as a reason to extract a five-model cluster immediately.
- Several of these models have high abstraction or hostile-frame risk. A weak
  extraction would make future surfaces smoother but less trustworthy.

Deferred extraction trigger:

- Extract this cluster later only if a reviewed dry surface shows that
  competitive-dynamics gaps repeatedly block product-worthy Decision Pressures,
  or if users/operators repeatedly need a negotiation/counterparty pressure
  where zero-output is no longer adequate.

## Other Missing Models Outside The Starting Set

The full 10-case dry-run also flags commitment-reversibility models:

- `commitment-bias`
- `lock-in`
- `path-dependence`
- `switching-costs`

These are not Batch 3a, but they are the next watchlist after the PR13 patch.
They appear in two consultant commitment-reversibility routes with severe
partial coverage. They may deserve a later targeted patch if commitment
reversibility becomes a recurring Decision Pressure surface.

`creative-destruction` and `lean-startup-methodology` are also missing once.
`lean-startup-methodology` has obvious experiment-gate potential, but one
appearance outside the current 3-case calibration is not enough to pull it into
Batch 3a. `creative-destruction` should be handled carefully because it can
easily become novelty theater unless the source yields concrete replacement
constraints and do-not-use guards.

## Warning Against Coverage Theater

Do not extract models merely because they are missing.

Missing coverage is useful evidence only when it blocks a compact,
source-backed, dismissible Decision Pressure. A missing model that would mostly
produce a general explanation should remain absent or receive an absence record.

The correct outputs for a targeted extraction pass include:

- a strong affordance record;
- a thin record with one or two narrow affordances;
- an absence record saying the source does not support Decision
  Pressure-ready operational constraints;
- a recommendation to keep the model Observatory-only.

The wrong output is a smooth model record that makes coverage look complete
while weakening the trace.

## Extraction Standard For Batch 3a

For each recommended model, the extractor should read the canonical source and
produce only constraints that can eventually answer:

- What should the user verify?
- What would make the pressure live?
- What would dismiss it?
- What tripwire, stop condition, sequencing change, or operational constraint
  follows?
- When should the model not be used because it would create theater, fake
  precision, or overreach?

Do not extract:

- general model definitions;
- broad examples without operational constraints;
- relationship edges as substitute affordances;
- fields that only make the schema look full;
- runtime instructions that would bypass reviewer judgment.

## If Extraction Is Deferred Later

If the team decides not to run Batch 3a after this report, the evidence that
would make extraction worthwhile later is:

- repeated zero-output routes where operators believe a compact pressure was
  lost only because v3 records were missing;
- repeated suppression of otherwise strong candidates due to missing coverage;
- a two-reviewer dry surface where both reviewers identify the same missing
  model as blocking the best Decision Pressure;
- user or memo evaluation showing that the compact surface needs one of these
  records to produce clearer next action.

Until then, the product can honestly say no source-backed pressure cleared the
bar.
