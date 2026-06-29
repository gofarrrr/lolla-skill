# Product Delta Evidence Thesis v0

Status: docs/design only
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR71 Product Delta Evidence Thesis v0

## Purpose

This note defines the lower-claim Product Delta Evidence phase after the
audit/accountability machinery closure gate.

The product claim is narrow:

```text
Lolla sits between fluent AI advice and real action. It applies structured
audit pressure to an actual strong-model conversation, produces a revised
decision answer, and preserves enough evidence for later humans to inspect
whether the delta was useful.
```

The current phase claim is narrower:

```text
We are not proving that Lolla improves decisions yet. We are building a
Codex-assisted provisional review scaffold so later humans can validate,
correct, or reject the candidate deltas efficiently.
```

This is docs/schema/review-scaffold work only. It does not implement runtime
integration, run Lolla, call models, mutate archives, change prompts, change
`SKILL.md`, add a judge, score answer quality, infer automatic labels, or add
agent approval.

## Background

PR70 closed the audit/accountability machinery lane as done enough for now.
The next product question is not whether Lolla can preserve artifacts. It is
whether Lolla can change what a serious person would do next in a way that a
later human reviewer can understand.

The existing durable background is:

- [Product Delta Evidence And Interpretation Adequacy v0](product-delta-evidence-and-interpretation-adequacy-v0.md)
- [Audit / Accountability Machinery Closure Gate v0](audit-accountability-machinery-closure-gate-v0.md)
- [Current System Capabilities v0](current-system-capabilities-v0.md)
- [Lolla Evaluation Methodology](../lolla-evaluation-methodology.md)

## Baseline

The baseline is an actual vanilla strong-model conversation where the user is
close to acting.

The baseline is not:

- a toy prompt;
- a weak-model answer;
- a synthetic fresh answer;
- a trap fixture;
- a second answer written only for eval;
- a summary invented after the fact.

The first comparison is:

```text
actual vanilla strong-model conversation/final answer
versus
Lolla revised decision answer
```

Both sides must remain review-safe in checked-in artifacts. The provisional
review may paraphrase likely action and decision deltas, but it must not copy
raw transcripts, raw memo text, raw revised-answer text, provider text,
private reasoning, secrets, or local absolute paths.

## First Wedge

The first wedge is founder/operator strategic decisions.

This wedge is useful because decisions are concrete enough to inspect and
messy enough to test whether Lolla actually understands the conversation:

- launch or delay a product surface;
- pick a customer, market, role, or partner path;
- move authority or ownership;
- set pricing or support boundaries;
- constrain a pilot or deployment;
- preserve momentum while adding a meaningful stop rule.

This wedge does not make Lolla a domain authority, legal adviser, medical
adviser, financial adviser, HR decision-maker, or agent approval system.

## Review Capacity Mode

The current review capacity mode is:

```text
codex_assisted_provisional
```

Codex-assisted provisional review may:

- read review-safe checked-in artifacts;
- produce candidate vanilla-vs-Lolla deltas;
- identify candidate useful friction, noisy friction, lost value, and
  interpretation adequacy issues;
- create review packets for later human inspection;
- surface uncertainty and human follow-up questions.

Codex-assisted provisional review must not:

- become a human review;
- become ground truth;
- become judge calibration data;
- become product proof;
- become agent approval;
- add automatic labels;
- add answer-quality scoring;
- infer `safe_for_agent_use`;
- treat clean artifacts as evidence that the advice was good.

## Required Non-Claims

Every Codex-assisted provisional review packet must preserve these non-claims:

- Codex-assisted findings are not human review.
- Codex-assisted findings are not ground truth.
- Codex-assisted findings are not judge calibration data.
- Codex-assisted findings are not product proof.
- Codex-assisted findings are not agent approval.
- Provisional subjective reads may be useful scaffolding, but humans remain
  responsible for product judgment.
- Deterministic custody checks remain separate from answer-quality judgment.

## Product Delta Concepts

`vanilla_likely_next_action`

: A provisional paraphrase of what the user would likely do after the actual
  vanilla strong-model conversation or final answer. This is reviewer-inferred
  unless a review-safe source makes the action explicit.

`lolla_likely_next_action`

: A provisional paraphrase of what the user would likely do after the Lolla
  revised decision answer. This is also not proof that the user should do it.

`material_difference`

: Whether the two likely actions differ in a way that could matter to a real
  decision. A wording change, warmer tone, longer caveat, or cleaner artifact
  is not enough.

`structural_delta`

: The specific structure that changed: action, threshold, sequence, evidence
  gate, stop rule, written term, scope, overclaim, or user-answerable question.

`decision_leverage`

: A provisional read on how much the delta could change action quality. The
  allowed shape is qualitative: `none`, `low`, `medium`, `high`, or `unclear`.
  It is not a score.

`useful_friction`

: Pressure that is grounded, actionable, and proportionate.

`noisy_friction`

: Caution, process, caveats, structure, or hesitation without decision
  leverage.

`lost_value`

: Anything useful the revised answer may have weakened, such as momentum,
  courage, clarity, user-specific ambition, simplicity, actionability, or
  useful original advice.

`interpretation_adequacy`

: Whether Lolla understood the actual conversation well enough for the audit to
  be trusted as a review object. This is a reviewability question, not a proof
  of advice quality.

`first_upstream_failure`

: The first surface where the provisional review sees trouble, such as the
  vanilla answer, conversation interpretation, audit pressure, revised answer,
  artifact custody, review surface, no observed failure, or unclear evidence.

`net_decision_read_provisional`

: A provisional candidate read on the pair, using labels such as
  `material_improvement_candidate`, `partial_improvement_candidate`,
  `no_material_change_candidate`, `lolla_added_noise_candidate`,
  `lolla_worse_candidate`, or `inconclusive`.

## Friction Doctrine

Useful friction must satisfy all three tests:

1. Grounded: it is supported by the conversation, audit, or review-safe source.
2. Actionable: it changes action, threshold, sequence, evidence gate, stop
   rule, written term, scope, or a user-answerable question.
3. Proportionate: it does not inflate uncertainty into paralysis or generic
   caution.

Noisy friction may look responsible. It may add caution, process, structure, or
hesitation. It fails if it does not change decision leverage, is not grounded,
or makes the decision harder without making it wiser.

## Stop Rule

The Codex-assisted provisional scaffold is done enough when:

- the thesis exists;
- the vanilla-vs-Lolla provisional review protocol exists;
- 6-10 safe cases can be provisionally reviewed;
- uncertainty is explicit in every subjective section;
- later human review can validate, correct, or reject the packets efficiently;
- no judge, score, automatic label, `safe_for_agent_use` automation, runtime
  integration, prompt change, archive mutation, or product-proof claim has been
  added.

At that point, stop building machinery and route the scaffold to a future human
reviewer.

## Follow-On Slices

The immediate PR71-PR74 bundle is:

- PR71: this thesis.
- PR72: [Vanilla-vs-Lolla Provisional Review Protocol v0](vanilla-vs-lolla-provisional-review-protocol-v0.md).
- PR73: [Codex-Assisted Paired Review Dry Run v0](codex-assisted-paired-review-dry-run-v0.md).
- PR74: [Provisional Product Delta Failure Taxonomy v0](provisional-product-delta-failure-taxonomy-v0.md).

PR75 then exercises the scaffold as a read-only deterministic eval lane:
[Product Delta Eval Readiness And Provisional Run v0](product-delta-eval-readiness-and-provisional-run-v0.md).

PR76 fills the ready PR75 shells with Codex-assisted provisional semantic
reads: [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md).

PR77 summarizes PR75 and PR76 as one provisional state-of-evidence package:
[Product Delta Provisional Report v0](product-delta-provisional-report-v0.md).

PR78 adds deterministic evidence-boundary lint before any broader specialist
review architecture: [Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).

PR79 defines that broader architecture without implementing it:
[Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md).
Do not add human-label claims, judges, scores, runtime integration, archive
mutation, automatic labels, or `safe_for_agent_use` automation from the
provisional package alone.
