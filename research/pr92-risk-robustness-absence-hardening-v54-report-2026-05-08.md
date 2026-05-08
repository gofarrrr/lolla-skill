# PR92 Risk Robustness Absence Hardening v54 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr92-risk-robustness-v54`

## Verdict

PR92 is an absence-first hardening pass, not a positive-affordance expansion.

The risk robustness ring is already strong as compressed positive cards. The current one-affordance records are not thin; most contain several treatment requirements and explicit do-not-use boundaries. The audit did find real source richness, but the added value is mostly in making misuse boundaries first-class so future packet display and receiver review cannot flatten broad risk vocabulary into generic wisdom.

## Scope

Reviewed records:

- `antifragility`
- `calculated-risk-taking`
- `margin-of-safety`
- `resilience`
- `risk-assessment`
- `risk-vs-uncertainty`

Reviewed sources:

- `Antifragility_rag.md`
- `Calculated_Risk_Taking_rag.md`
- `Margin_Of_Safety_rag.md`
- `Resilience_rag.md`
- `Risk_Assessment_rag.md`
- `Risk_Vs_Uncertainty_rag.md`

## Decision Standard

The split rule remained strict:

> Add a positive affordance only when source material creates a distinct downstream transaction: different activation, evidence, do-not-use boundary, treatment requirement, and likely receiver use/reject/defer decision.

The audit did not find enough evidence for new positive affordances in this ring. It did find 11 negative rails that are likely to matter when broad cards are rendered compactly.

## Positive Split Decisions

No new positive affordances were added.

### `margin-of-safety`

Kept compressed as `margin-of-safety.evidence-sized-operating-buffer`.

Rejected positive splits:

- dynamic buffer resize;
- premortem/simulation buffer sizing;
- generic downside analysis.

Reason: these are methods inside the same safety-factor design transaction. The receiver should ask whether the plan has evidence-sized slack, where it is placed, and when it must be resized. Splitting dynamic resize into a second positive card would make the card set noisier without giving the receiver a distinct use/reject/defer choice.

### `risk-vs-uncertainty`

Kept compressed as `risk-vs-uncertainty.commitment-sizing-under-unknowns`.

Rejected positive splits:

- post-outcome decision-quality review;
- known-unknown de-risking map;
- betting/expected-value treatment.

Reason: post-outcome decision-quality review is a real transaction, but it is better owned by adjacent hindsight, true-uncertainty, or outcome-bias records. Adding it here would make an already broad model more attractive under packet caps. De-risking and betting are supporting methods for commitment sizing, not separate identities in this record.

### `calculated-risk-taking`

Kept compressed as `calculated-risk-taking.pressure-tested-bounded-wager`.

Rejected positive splits:

- sensitivity flip threshold;
- adversarial scenario simulation;
- decision-tree or cost-benefit calculation;
- process-over-outcome review.

Reason: the existing record already has treatment requirements for framing as a bet, pressure-testing assumptions, and bounding downside through flip thresholds. Splitting these would create tool taxonomy rather than better downstream decision grammar.

### `risk-assessment`

Kept compressed as `risk-assessment.thresholded-downside-governance`.

Rejected positive splits:

- knowns/unknowns de-risking map;
- conjunctive/disjunctive structure check;
- human-system personal-data risk.

Reason: these are all inputs or methods for downside governance unless the receiver can convert them into mitigations, thresholds, monitoring, safeguards, or decision changes.

### `resilience`

Kept compressed as `resilience.disciplined-recovery-with-continued-function`.

Rejected positive splits:

- self-script stress management;
- optimistic explanation style;
- bias-resistant recovery learning.

Reason: self-scripting is too narrow; optimistic explanation style is dangerous as a standalone positive card; bias-resistant recovery learning is already a treatment requirement and overlaps confirmation-bias/scientific-method ownership.

### `antifragility`

Kept compressed as `antifragility.bounded-stress-learning-design`.

Rejected positive splits:

- portfolio experimentation;
- known-unknown de-risking before scale;
- disruptive idea "what must be true" testing.

Reason: these moves are coupled inside one antifragile transaction: bounded stress, feedback, comparison, and design update. Outside that mechanism they belong to experimentation, risk-assessment, calculated-risk-taking, or first-principles records.

## Added Absence Rails

Added 11 absence records:

- `cold-rationality-as-complete-calculation`
- `familiar-framework-as-calculated-risk`
- `fat-tail-false-precision-as-calculated-risk`
- `fear-uncertainty-doubt-without-risk-evidence`
- `mean-or-base-case-as-risk-envelope`
- `optimistic-base-case-as-margin-of-safety`
- `optimistic-explanation-style-as-risk-blindness`
- `resilience-as-overload-normalization`
- `static-buffer-as-durable-margin`
- `stress-exposure-without-feedback-update`
- `unknown-unknowns-as-exhaustively-mapped`

These rails prevent predictable future misuse:

- a best-case forecast being mislabeled as margin of safety;
- a static buffer being treated as durable despite changing exposure;
- unknown unknowns being declared exhaustively mapped;
- a base case or mean being treated as the whole risk envelope;
- a clean calculation ignoring tacit or emotional information;
- a familiar frame being relabeled as calculated risk;
- fat-tail precision theater;
- fear language masquerading as risk assessment;
- resilience being used to normalize overload;
- optimistic resilience hiding risk blindness;
- antifragility being invoked without feedback or design update.

## Compile Result

Artifact: `model_affordances_v54`

Status: `draft_review_only`

Compiled results:

- Records: `222`
- Affordances: `298`
- Absence records: `594`
- Schema failures: `0`
- Source quote rejections: `0`

Delta from v53:

- Positive affordances: `+0`
- Absence records: `+11`

## Runtime Safety

No runtime path was changed.

The v54 artifact remains dormant. Tests assert that `affordances_v54` and `model_affordances_v54` are not imported by live runtime paths.

## Why This Is Not Bloat

This PR adds more absence rails than PR91, but it is still bounded. Risk vocabulary is unusually prone to authoritative theater: "risk assessment," "resilience," "antifragility," and "calculated risk" sound like mature judgment even when they are being misused.

The PR therefore adds negative controls where a future receiver could plausibly overtrust a broad card:

- not every buffer is a margin;
- not every scenario list maps uncertainty;
- not every calculation is complete;
- not every warning is risk evidence;
- not every endurance story is resilience;
- not every exposure to stress is antifragility.

That is exactly the kind of corpus enrichment that should help the deterministic substrate remain useful without becoming louder than the LLM's judgment.

## Follow-Up For Packet Stress

Future packet review should check whether these absence rails survive rendering:

- Are negative rails visible enough when a risk card is nominated?
- Do broad risk cards crowd out narrower probability, outcome, or implementation cards?
- Does the receiver defer when the rail says a card is too broad or falsely precise?
- Does antifragility require feedback/update language before use?
- Does resilience avoid normalizing overload?

If replay cases show a receiver repeatedly needs a rejected submove as a separate use/reject/defer decision, that would justify a later positive split. PR92 did not find that at source-review level.
