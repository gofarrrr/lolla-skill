# PR56 v18 Source Adequacy Ledger Pilot

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: human source-read pilot; no record rewrites; no runtime pickup

## Method

This pilot reviewed P0/P1 records plus selected P2/control records against:

- compiled v18 record fields;
- source Markdown operational-use sections;
- source Markdown limitation/risk sections;
- PR55 transaction-granularity criteria.

The pilot does not edit affordance records. It classifies what a later targeted v19 enrichment PR might need.

## Pilot Summary

| Model | Queue | Current shape | Pilot verdict | Why |
| --- | --- | ---: | --- | --- |
| `systems-thinking` | P0 | 4 aff / 0 abs | `needs_absence_enrichment`, `too_broad_for_runtime`, `packet_shape_blocker_only` | Source supports multiple current affordances, but zero absences and packet flattening are unsafe for broad runtime use. |
| `confidence-calibration` | P0 | 3 aff / 0 abs | `needs_absence_enrichment`, `packet_shape_blocker_only` | Current three affordances map to source clusters well; the missing piece is absence/overclaim treatment and flagged broad method affordance handling. |
| `inversion` | P0 | 3 aff / 0 abs | `needs_absence_enrichment`, `needs_affordance_rewrite`, `packet_shape_blocker_only` | Source supports anti-goal, disconfirmation, and obstacle-removal moves, but failure-mode absences are missing and one affordance is already flagged for rewrite review. |
| `price-discrimination` | P0 | 1 aff / 2 abs | `weak_support_confirmed`, `source_too_thin` | Current weak/medium posture is appropriate. Do not expand just to make the card look richer. |
| `devops-and-continuous-integration` | P1 | 1 aff / 2 abs | `weak_support_confirmed`, `source_too_thin` | Source is adjacent/generic enough that current weak posture should remain. |
| `theory-of-constraints` | P1 | 2 aff / 0 abs | `needs_absence_enrichment`, `packet_shape_blocker_only` | Current two affordances cover constraint-first intervention and constraint-shift retest; source warnings need first-class absence treatment. |
| `lindy-effect` | P1 | 1 aff / 0 abs | `complete_as_compressed` with zero-absence watch | Source has one dominant transaction: longevity prior with discontinuity check. |
| `premortem` | P1 | 1 aff / 0 abs | `complete_as_compressed` with zero-absence watch | Source supports one dominant transaction: simulated failure converted into plan changes. WWHB and de-risking are supporting mechanisms. |
| `principal-agent-problem` | P1 | 1 aff / 3 abs | `complete_as_compressed`, `medium_confidence_visible` | Source maps to one core transaction: delegated alignment drift audit. Absences are useful and should remain visible. |
| `sunk-cost-fallacy` | P1 | 1 aff / 0 abs | `complete_as_compressed` with zero-absence watch | Despite 18 source refs, current card captures one coherent transaction: future-value recommitment. |
| `chain-of-thought` | P2 | 1 aff / 2 abs | `split_candidate`, `needs_absence_enrichment` | Source may separate auditable decomposition from anti-rationalization / trace-as-proof controls. This is the strongest pilot split candidate. |
| `reasoning-mode-router` | P2 | 1 aff / 2 abs | `complete_as_compressed`, `too_broad_for_runtime`, `runtime_do_not_promote_yet` | Source modes are examples under one context-driven routing transaction. Danger is deterministic overuse, not missing positive affordance. |
| `antifragility` | P2 | 1 aff / 3 abs | `complete_as_compressed` | High source refs support one transaction: bounded stress learning design. Dropped risk/de-risking material is covered by absences or other models. |
| `base-rates` | P3/control | 1 aff / 1 abs | `complete_as_compressed` | Good control case: one strong reference-class transaction plus one thin-source absence. |

## Model Notes

### `systems-thinking`

Source signals:

- recurring event-level failures: `Systems_Thinking_rag.md:67`;
- architecture rewrite misdiagnosis: `Systems_Thinking_rag.md:73`, `Systems_Thinking_rag.md:83`;
- limitation around broad-stroke explanatory depth: `Systems_Thinking_rag.md:79`;
- mitigation around testing the social system before redesign: `Systems_Thinking_rag.md:133`.

Adequacy read:

The source does support several distinct operational moves, and v18 already has four affordances. The issue is not obvious under-extraction. The issue is that this broad card has zero absence records and current packet display would flatten four affordances into one visible detail line.

PR56 action:

- Do not add more positive affordances by default.
- Add or review absences for broad-overlay misuse, explanatory-depth theater, and architecture-as-misdiagnosis if a v19 record-update PR is approved.
- Keep `systems-thinking.structure-over-events` non-promotable until grouped packet and rewrite review exist.

### `confidence-calibration`

Source signals:

- commitment sizing and boundary conditions: `Confidence_Calibration_rag.md:61`, `Confidence_Calibration_rag.md:63`;
- precise-looking metrics from weak samples: `Confidence_Calibration_rag.md:67`, `Confidence_Calibration_rag.md:129`, `Confidence_Calibration_rag.md:131`;
- learning/mastery fluency trap: `Confidence_Calibration_rag.md:45`, `Confidence_Calibration_rag.md:75`;
- danger when calibration replaces commitment: `Confidence_Calibration_rag.md:81`.

Adequacy read:

The three current affordances map to the source clusters: commitment sizing, instrument trust, and method-first self-interrogation. This looks more like display/absence hardening than missing positive affordance.

PR56 action:

- Keep the three-affordance structure under grouped packet requirements.
- Add absence candidates for caveat theater and endless calibration if v19 enrichment is approved.
- Preserve existing non-promotion flag for `method-first-self-interrogation`.

### `inversion`

Source signals:

- anti-goal / failure mechanism: `Inversion_rag.md:7`, `Inversion_rag.md:33`, `Inversion_rag.md:41`;
- disconfirmation of preferred assumption: `Inversion_rag.md:67`, `Inversion_rag.md:103`, `Inversion_rag.md:139`;
- obstacle removal plus forward execution balance: `Inversion_rag.md:79`, `Inversion_rag.md:135`;
- failure modes around straw-man inversion and checklist delusion: `Inversion_rag.md:136`, `Inversion_rag.md:137`.

Adequacy read:

The source supports the three existing affordance clusters. The risk is not missing another positive cluster; it is that zero absences hide important misuse boundaries. The existing `obstacle-removal-before-added-force` flag still looks right: it may be a sub-affordance or rewrite candidate before runtime promotion.

PR56 action:

- Treat as `needs_absence_enrichment`.
- Do not split further unless real cases show obstacle removal and anti-goal mapping need separate receiver actions.
- Keep rewrite-review flag.

### `price-discrimination`

Source signals:

- segment offer shape by value evidence: `Price_Discrimination_rag.md:51`, `Price_Discrimination_rag.md:53`, `Price_Discrimination_rag.md:55`;
- buyer psychology examples: `Price_Discrimination_rag.md:57`;
- risk transparency / lower-tier limitations: `Price_Discrimination_rag.md:128`;
- illusion of understanding willingness to pay: `Price_Discrimination_rag.md:118`.

Adequacy read:

The current weak-support card is appropriately cautious. The source contains adjacent offer strategy and risk framing, but the support is not strong enough to upgrade this into a richer pricing doctrine. The right move is to preserve weak support and avoid cosmetic enrichment.

PR56 action:

- Mark `weak_support_confirmed`.
- Do not split without stronger source custody.
- Runtime handoff must visibly warn that this is tentative.

### `devops-and-continuous-integration`

Source signals:

- delivery speed and reliability coexistence: `Devops_and_Continuous_Integration_rag.md:63`;
- integration friction: `Devops_and_Continuous_Integration_rag.md:65`;
- weak/generic mental-model limitations: `Devops_and_Continuous_Integration_rag.md:69`, `Devops_and_Continuous_Integration_rag.md:83`, `Devops_and_Continuous_Integration_rag.md:85`.

Adequacy read:

The current weak-support posture is right. The source does not support a full DevOps/CI doctrine. Expanding this card would be inference, not extraction.

PR56 action:

- Mark `source_too_thin`.
- Preserve weak/medium confidence.
- Do not enrich unless source material changes.

### `theory-of-constraints`

Source signals:

- named bottleneck with quantified limit: `Theory_Of_Constraints_rag.md:55`;
- sequencing and constraint-shift cadence: `Theory_Of_Constraints_rag.md:61`, `Theory_Of_Constraints_rag.md:136`;
- unstable bottleneck warning: `Theory_Of_Constraints_rag.md:83`, `Theory_Of_Constraints_rag.md:141`;
- bottleneck theater without measurement: `Theory_Of_Constraints_rag.md:93`, `Theory_Of_Constraints_rag.md:137`;
- stakeholder bottleneck skipped: `Theory_Of_Constraints_rag.md:142`.

Adequacy read:

The two affordances are plausible and distinct. The missing part is not necessarily a third positive affordance; it is absence pressure around false bottleneck certainty, visible-work optimization, and stakeholder/ownership constraints.

PR56 action:

- Mark `needs_absence_enrichment`.
- Recheck whether stakeholder bottleneck is a separate affordance only if replay cases require a different receiver action.

### `lindy-effect`

Source signals:

- longevity prior use: `Lindy_Effect_rag.md:41`, `Lindy_Effect_rag.md:43`, `Lindy_Effect_rag.md:45`;
- novelty/discontinuity trap: `Lindy_Effect_rag.md:57`, `Lindy_Effect_rag.md:91`, `Lindy_Effect_rag.md:97`.

Adequacy read:

This is a good one-affordance record. The do-not-use boundaries already carry the discontinuity check. Zero absences are worth noting but not a proof of under-extraction.

PR56 action:

- Mark `complete_as_compressed`.
- No positive split recommended.

### `premortem`

Source signals:

- simulated future failure: `Premortem_rag.md:7`, `Premortem_rag.md:51`;
- pre-commitment and social pressure: `Premortem_rag.md:53`;
- conjunctive failure and weak links: `Premortem_rag.md:55`;
- danger of worry lists without owner/mitigation/action: `Premortem_rag.md:65`;
- WWHB and de-risking as mechanisms: `Premortem_rag.md:15`, `Premortem_rag.md:33`.

Adequacy read:

The record is compressed appropriately. WWHB, de-risking, and dialectic material look like supporting mechanics inside the simulated-failure-to-plan-change transaction, not separate premortem affordances.

PR56 action:

- Mark `complete_as_compressed`.
- No split recommended.

### `principal-agent-problem`

Adequacy read:

The one affordance captures delegated alignment drift. The three absences are important: bad-faith suspicion, micromanagement-as-control, and standalone AI-agent orchestration should remain non-promoted. Medium confidence should be visible in any future handoff.

PR56 action:

- Mark `complete_as_compressed`.
- Keep confidence visible.

### `sunk-cost-fallacy`

Source signals:

- prior investment distorting forward-looking choice: `Sunk_Cost_Fallacy_rag.md:63`;
- history still sitting in the room: `Sunk_Cost_Fallacy_rag.md:65`;
- reckless abandonment misuse: `Sunk_Cost_Fallacy_rag.md:79`;
- cash-flow / future economics framing: `Sunk_Cost_Fallacy_rag.md:39`.

Adequacy read:

Despite high source-reference count, this is one coherent transaction: separate irretrievable past expenditure from the next unit of future value. The source's reckless-abandonment warning is already in the current do-not-use boundary.

PR56 action:

- Mark `complete_as_compressed`.
- No split recommended.

### `chain-of-thought`

Source signals:

- problem disaggregation and logical structure: `Chain_Of_Thought_rag.md:33`, `Chain_Of_Thought_rag.md:53`, `Chain_Of_Thought_rag.md:55`;
- trace-as-truth danger: `Chain_Of_Thought_rag.md:67`;
- analysis paralysis and implementation gap: `Chain_Of_Thought_rag.md:69`, `Chain_Of_Thought_rag.md:118`;
- post-hoc rationalization: `Chain_Of_Thought_rag.md:73`;
- confirmation bias after selecting a structure: `Chain_Of_Thought_rag.md:114`.

Adequacy read:

This is the strongest provisional split candidate in the pilot. The current affordance covers auditable stepwise reasoning. But source material also supports a different transaction: detecting when a reasoning trace has become proof theater, rationalization, or a substitute for external checks/action.

Possible targeted v19 move:

- Keep `chain-of-thought.audit-stepwise-reasoning`.
- Consider a second affordance only if it can be written as a distinct receiver transaction, such as `chain-of-thought.trace-as-proof-audit` or `chain-of-thought.anti-rationalization-check`.
- Alternatively, if not split, enrich absence/misuse guards for post-hoc rationalization and implementation gap.

PR56 action:

- Mark `split_candidate`.
- Require split proof before editing records.

### `reasoning-mode-router`

Source signals:

- different reasoning modes and wrong-path cost: `Reasoning_Mode_Router_rag.md:57`, `Reasoning_Mode_Router_rag.md:59`, `Reasoning_Mode_Router_rag.md:61`;
- risk of familiar-frame routing: `Reasoning_Mode_Router_rag.md:79`, `Reasoning_Mode_Router_rag.md:126`;
- routing debate overhead: current v18 absence captures this source-side danger.

Adequacy read:

The source's many modes are examples under one routing transaction. Splitting by mode would likely create exactly the deterministic case-type router the absence record forbids.

PR56 action:

- Mark `complete_as_compressed`.
- Keep `too_broad_for_runtime`.
- Do not promote into deterministic routing.

### `antifragility`

Source signals:

- bounded stress and learning: `Antifragility_rag.md:55`, `Antifragility_rag.md:57`, `Antifragility_rag.md:59`;
- experiments and feedback: `Antifragility_rag.md:33`, `Antifragility_rag.md:89`;
- inverse goals and de-risking: `Antifragility_rag.md:31`, `Antifragility_rag.md:35`;
- ruinous stress warning is covered by current do-not-use and absence.

Adequacy read:

High source-reference count does not imply under-extraction here. The source points toward one dominant transaction: expose a system to bounded, learnable stress while protecting against ruin. Dropped de-risking/risk-inventory material is correctly handled as absence or other-model territory.

PR56 action:

- Mark `complete_as_compressed`.
- No split recommended.

### `base-rates`

Source signals:

- reference class correction: `Base_Rates_rag.md:43`, `Base_Rates_rag.md:45`, `Base_Rates_rag.md:47`;
- reference-class mismatch danger: `Base_Rates_rag.md:65`;
- advertising example is thin: current absence covers this.

Adequacy read:

This is a clean control record. One affordance is enough because the source's dominant transaction is outside-view reference-class anchoring before case-specific updating.

PR56 action:

- Mark `complete_as_compressed`.
- Use as a positive example for future reviews.

## Pilot Conclusions

The pilot does not support a blanket v19 expansion.

It supports targeted next work:

1. Finish P0/P1 source ledger.
2. Treat weak-support records as source-thin unless stronger source custody appears.
3. Add absence-enrichment candidates before positive splits for broad/multi records.
4. Treat `chain-of-thought` as the first serious split-candidate proof case.
5. Preserve complete-as-compressed records; do not punish concise extraction.

## Bottom Line

One affordance is sometimes enough.

But it should be enough because the source has one downstream reasoning transaction, not because the extraction phase needed to finish coverage.
