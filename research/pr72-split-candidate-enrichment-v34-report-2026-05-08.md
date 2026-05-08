# PR72 v34 Split-Candidate Enrichment Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr72-split-candidate-v34`

## Verdict

PASS as dormant reviewed substrate.

PR72 is not a runtime pickup change. It does not touch live `/lolla`, prompting, packet rendering, lane adapters, or product behavior. It is a compact corpus-quality pass that tests the post-v33 question:

> When a source has more than one operational use, which material deserves a separate affordance identity, and which material should remain a guard or routing absence?

The result is deliberately small:

- Positive affordances added: 3
- Absence/routing guards added: 3
- Runtime imports: 0
- Source quote rejections: 0

## Why This PR Exists

PR71 established a minimum absence floor for previously thin high-confidence cards. After that, the next risk was under-extraction, not missing coverage. Some records still compress multiple source-supported operational moves into one model card.

The split rule used here was strict:

> Add a positive affordance only if the split changes the downstream transaction: use, reject, defer, merge, evidence gate, treatment requirement, or misuse guard.

The PR intentionally rejects tempting broad splits when adjacent records already own the transaction.

## Source Files Fully Re-Read

The source review used the canonical Markdown files directly, not only compiled JSON:

- `MM_CANONICAL_216/Inversion_rag.md`
- `MM_CANONICAL_216/Leverage_Points_rag.md`
- `MM_CANONICAL_216/Second_Order_Thinking_rag.md`

Adjacent ownership was also checked before promoting borderline material:

- `root-cause-analysis.machine-level-recurrence-diagnosis`
- `systems-thinking.structure-over-events`
- `survivorship-bias.recover-hidden-denominator-selection`
- `curse-of-knowledge.audience-starting-state-reconstruction`

## Positive Splits Added

### `inversion.zero-base-continuation-test`

Why it earned a positive split:

This is not just generic anti-goal inversion. The receiver action is different: reset the continuation baseline and ask what would be chosen if the current path did not already exist.

Transaction identity:

- Activation: inherited path, prior commitment, continuation default, consistency pressure.
- Evidence: current path, goal, clean-sheet alternative, optionality/switching-cost/obligation constraints.
- Treatment: compare inherited baseline against clean-sheet alternative; end in continue, modify, or exit criteria.
- Guard: do not erase real constraints, accumulated capabilities, valid future value, or switching costs.

Why it is not opportunity-cost/endowment/sunk-cost:

Those adjacent records own displaced alternatives, ownership attachment, and prior-investment pressure. This affordance owns the clean-sheet continuation baseline reset.

### `inversion.survivor-absence-signal`

Why it earned a narrow positive split:

The RAF example is not only hidden-denominator recovery. It changes where the intervention should land. The absence of marks becomes the signal because the non-returning cases cannot appear.

Transaction identity:

- Activation: visible survivor evidence points to an obvious fix, but missing non-survivors could reverse the target.
- Evidence: survivor sample, absent non-survivors, selection mechanism, decision that changes.
- Treatment: infer the missing failure point and change the intervention target.
- Guard: route generic hidden-denominator recovery to survivorship-bias unless absence reverses the intervention target.

Risk:

This is the most borderline positive split in PR72. It is kept only because the treatment requires a reversed target, not merely "who is missing?"

### `leverage-points.value-driver-sensitivity-tree`

Why it earned a positive split:

The source explicitly supports Return on Capital Trees, driver decomposition, and what-if scenario analysis. This is distinct from generic structural leverage because the transaction is measurable driver sensitivity.

Transaction identity:

- Activation: measurable business, operating, financial, or growth outcome.
- Evidence: driver tree, directional or quantitative sensitivity, actor influence over the driver.
- Treatment: compare drivers before calling an intervention high leverage.
- Guard: do not confuse mathematical sensitivity with practical influence.

Why it is not expected-value/probabilistic-thinking/MCDA:

Those records own uncertain payoffs or option weighting. This affordance owns identifying which decomposed value driver is the leverage point.

## Positive Splits Rejected

### `leverage-points.core-message-leverage`

Why rejected as a positive split:

The source support is real, but the transaction is too easy to duplicate better-owned records unless a future domain-specific packet proves the need.

Risk:

It could become a generic "make this clearer" card.

Guard added instead:

- `standalone-communication-core-affordance`

Routing:

- Skipped-premise repair: `curse-of-knowledge`
- Signal-preserving compression: `information-theory`
- Context before an ask: `pre-suasion`

### `second-order-thinking.machine-level-cause-diagnosis`

Why rejected as a positive split:

The source mentions machine-level and case-at-hand diagnosis, but generic recurrence diagnosis is already owned by `root-cause-analysis` and `systems-thinking`.

Guard added instead:

- `machine-level-diagnosis-without-downstream-consequence`

Promotion rule:

Use second-order-thinking only when the machine-level diagnosis is tied to downstream reversal, delayed cost, adaptation, incentive distortion, or recovery-path loss.

### `second-order-thinking.audience-mental-state-consequence`

Why rejected as a positive split:

The source mentions audience mental state and message effects, but generic audience reconstruction is already owned by `curse-of-knowledge`, and stakeholder-feeling evidence is better owned by empathy/motivation records.

Guard added instead:

- `audience-modeling-without-downstream-message-effect`

Promotion rule:

Use second-order-thinking only when the message creates a downstream consequence chain: audience interpretation, later behavior or adaptation, and delayed system effect.

## v34 Artifact Summary

Compiled artifact:

- `data/compiled/model_affordances/affordances_v34.json`
- `data/compiled/model_affordances/quality_report_v34.md`

Metadata:

- Artifact: `model_affordances_v34`
- Status: `draft_review_only`
- Records: 222
- Affordances: 271
- Absence records: 498
- Schema failures: 0
- Source hash failures: 0
- Source quote rejections: 0

Delta from v33:

- Affordances: 268 -> 271
- Absences: 495 -> 498

Target record shapes:

- `inversion`: 5 affordances, 3 absences
- `leverage-points`: 4 affordances, 2 absences
- `second-order-thinking`: 1 affordance, 4 absences

## Why This Is Not Bloat

The PR removed three initially tempting positive splits before compiling:

- `leverage-points.core-message-leverage`
- `second-order-thinking.machine-level-cause-diagnosis`
- `second-order-thinking.audience-mental-state-consequence`

Those were converted into absence/routing guards because the source material was real but not safely transaction-distinct inside these records.

The final positive additions survive because each has a separable downstream treatment:

- zero-base continuation reset;
- reversed intervention target from survivor absence;
- measurable value-driver sensitivity tree.

## Runtime Safety

This PR remains dormant substrate only.

No live runtime path imports v34. The PR72 test scans:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

The expected result is that `affordances_v34` and `model_affordances_v34` appear only in tests and compiled artifact files, not in live runtime paths.

## Verification

Planned verification for the PR:

```bash
pytest tests/test_pr72_v34_split_candidate_enrichment.py \
  tests/test_pr71_v33_low_absence_guard_enrichment.py \
  tests/test_model_affordance_compiler.py

rg -n "affordances_v34|model_affordances_v34" engine scripts tests -g '*.py'

git diff --check
```

## Next Corpus Frontier

PR72 should not trigger broad splitting. It is a proof of method.

The next enrichment pass should sample one-affordance records where the canonical source contains visibly different operational modes, but should keep the same standard:

> Split only when the downstream card transaction changes.

Good candidates are records where one affordance currently bundles:

- a diagnostic use and a treatment use;
- a decision gate and a communication gate;
- a structural system move and a human adoption move;
- a data/evidence move and a misuse-containment move.

The danger remains richness theater. The corpus should become more useful, not louder.
