# Evaluation Flywheel Action Plan v0

Status: action plan
Date: 2026-06-27

This note turns the current PRD, evaluation methodology, control-layer notes,
conversation-understanding evidence, and six-case complex baseline into an
actionable evaluation path.

It does not propose a runtime change. It does not add an LLM judge. It does not
approve specialist integration. It does not expand `SKILL.md`.

The goal is to make the next work clear:

> Use real Lolla traces to learn what "better reasoning" means, then convert
> repeated findings into deterministic checks, human-review labels, fixtures,
> and eventually calibrated binary judges.

## Product Boundary

Lolla's job is reasoning quality, not total agent safety.

The control stack around an agent may include:

- input/output guardrails;
- tool permission hooks;
- human approvals;
- outbound proxies;
- sandboxes;
- identity/secret scopes;
- observability and eval suites.

Lolla fits beside those layers. Its native question is:

```text
Did the reasoning frame deserve trust before this answer, plan, or action became
operational?
```

It should not become:

- a policy engine;
- a firewall;
- a sandbox;
- an approval authority;
- a credential broker;
- a domain expert;
- a generic judge;
- a memory product.

## Deterministic And Probabilistic Contract

The core architecture is:

```text
probabilistic interpretation inside deterministic custody
```

LLMs may do:

- read messy multi-turn conversations;
- infer the decision frame;
- identify pressure points;
- generate counterarguments;
- revise the answer;
- propose candidate review notes in explicitly synthetic contexts.

Deterministic code must do:

- capture the source conversation;
- preserve artifacts;
- validate schemas;
- validate quote presence;
- record capture adequacy;
- record run health;
- classify provider-boundary state;
- preserve local archive custody;
- index artifacts in `reasoning_trace.json`;
- generate `evaluation.json` as run-readiness, not wisdom;
- export local-only corpora;
- prevent synthetic labels from becoming human labels.

Human reviewers must do:

- decide whether friction was useful, noisy, or missing;
- decide whether the revised answer improved action quality;
- decide whether a run is safe for agent use;
- revise taxonomy from observed failures;
- approve any subjective judge calibration set.

## What The System Should Produce

### Per Normal Run

A completed modern run should produce:

| artifact | role | current status |
|---|---|---|
| `conversation.txt` | raw source conversation | shipped |
| `extraction.json` | probabilistic decision extraction plus quote validation | shipped |
| `result.json` | full pipeline output and audit pressure | shipped |
| `revised.txt` | saved revised answer | shipped |
| `memo.md` | portable memo | shipped |
| `agent_result.json` | compact machine handoff | shipped |
| `extraction_adequacy_report.json` | deterministic extraction/provenance report | shipped |
| `evaluation.json` | deterministic run-readiness receipt | shipped |
| `reasoning_trace.json` | local artifact custody manifest | shipped |

Current important limitation:

`evaluation.json` does not decide whether the revised answer is good. It decides
whether the run envelope is inspectable and internally consistent.

### Per Review / Evaluation Batch

The evaluation layer should produce:

| artifact | role | next action |
|---|---|---|
| review-corpus JSONL | compact local run-envelope corpus | shipped |
| human-review labels | human-owned quality/taste labels | PR30 seed shipped |
| review findings note | summary of what passed, failed, and why | PR30 shipped |
| actionable-delta rubric | human-owned definition of real improvement | PR31 shipped |
| adversarial-pair fixtures | smoothness-bias traps for future judges | PR32 seed shipped |
| human-review corpus batch | broader local batch using PR30/PR31 labels | PR33 shipped |
| taxonomy revision note | evidence-backed changes to failure modes | after labels |
| deterministic check proposal | repeated failures that code can catch | after labels |
| judge calibration packet | train/dev/test labels for one binary judge | later |
| stability report | repeated-run variance and regressions | later |

### Per Future Integration

Only after evidence supports it, future artifacts may include:

- optional specialist-enrichment reports;
- persisted semantic coverage reports;
- a conversation-understanding projection;
- risk-mode behavior receipts;
- calibrated judge outputs.

None of these are approved for normal runtime by this plan.

## Evaluation Ladder

Evaluation should advance in layers. Do not skip layers.

### Layer 0: Deterministic Run Readiness

Question:

```text
Did the run produce the artifact envelope it claims to have produced?
```

Already shipped through `evaluation.json`, reasoning trace, capture adequacy,
quote validation, provider-boundary health, and corpus exporters.

Failure examples:

- missing artifact;
- schema invalid;
- capture critical;
- quote fabrication;
- run health says clean while artifacts disagree;
- private/public leak.

This layer can block or warn deterministically.

### Layer 1: Human Trace Review

Question:

```text
Did the audit add earned, decision-relevant friction?
```

Current status:

PR30 reviewed the six clean complex baseline runs with
`lolla.human_review.v0` as a human/product review seed. PR33 expanded that
review to a 14-record local batch: 12 counted positive answer-level reviews,
one partial boundary record, and one degraded exclusion.

Human labels should capture:

- answer-level pass/fail;
- primary failure mode;
- severity;
- useful friction;
- noisy friction;
- missing friction;
- revised-answer improvement;
- safe-for-agent-use;
- action-changing delta;
- artifact sufficiency notes.

The current active frontier is still human-owned evidence expansion and review
surface design, not judging. PR31 defines actionable delta, PR32 defines seed
adversarial pairs, and PR33 tests the labels on a broader batch.

### Layer 2: Heuristic Signals

Question:

```text
Can simple non-authoritative signals help reviewers find likely issues?
```

Possible later checks:

- revised answer changed an action/threshold/gate;
- memo carries the same main shift as revised answer;
- answer contains stop conditions or evidence gates;
- answer became much longer without a clearer decision delta;
- live-output hygiene remains not checked.

These should flag for review, not decide quality.

### Layer 3: Calibrated Binary Judges

Question:

```text
Can an LLM judge match human labels on one narrow failure mode?
```

Allowed only after human labels exist.

First candidate judge families:

- `actionable_delta`;
- `earned_friction`;
- `pressure_absorption`;
- `constraint_preservation`;
- `overcorrection_absent`;
- `unsupported_claim_absent`.

Requirements:

- one binary label;
- named dataset;
- train/dev/test split by case;
- TPR/TNR reported separately;
- adversarial smoothness-bias pairs included;
- advisory first, blocking only after calibration.

### Layer 4: Regression / Release Gates

Question:

```text
Does a proposed Lolla change improve or preserve behavior across known traces?
```

Future release gates should combine:

- deterministic artifact tests;
- fixed archive replay or comparison;
- human-reviewed fixture set;
- calibrated binary judge only if approved;
- cost/mode/provider telemetry;
- privacy and archive-mutation checks.

## The Flywheel

The flywheel should look like this:

```text
1. Run Lolla on real or fixture conversations.
2. Archive every artifact locally.
3. Deterministically check run readiness.
4. Export compact local corpora.
5. Human-review selected traces.
6. Update taxonomy and identify repeated failure modes.
7. Convert repeated deterministic failures into code checks.
8. Convert repeated fuzzy failures into labeled examples.
9. Build adversarial pairs and calibrated binary judges only when labels exist.
10. Use the corpus as a regression gate before prompt/runtime/mode changes.
11. Feed the lessons back into capture, prompts, docs, or runtime only when the
    evidence justifies the change.
```

The flywheel should upgrade Lolla through trace evidence, not taste drift.

## Actionable Missing Work

### PR30: Complex Baseline Human Review v0

Maps to: PRD R6, R8 prerequisite, R9.

Status: completed as the current human/product review seed.

Goal:

Use the six clean complex runs as the first human-reviewed evaluation seed.

Inputs:

- `docs/conversation-understanding/complex-conversation-baseline-v0.md`
- archived runs listed there;
- `docs/evals/lolla-human-review-v0.json`;
- `docs/evals/lolla-failure-taxonomy.md`;
- `docs/evals/human-review-workflow.md`.

Output:

- `docs/evals/complex-baseline-human-review-v0.md`;
- local review JSON under `reviews/human/complex-baseline-v0/`.

Acceptance:

- all six runs have human-owned labels;
- each run has an action-changing delta recorded;
- each run says whether current artifacts were sufficient for the label;
- candidate adversarial-pair lessons are listed;
- no synthetic label is treated as human review.

Non-goals:

- no model calls;
- no LLM judge;
- no runtime change;
- no prompt change;
- no new extraction;
- no automatic labels.

Current result:

- six of six answer-level reviews passed;
- six of six revised answers were labeled improved;
- six of six runs remain `safe_for_agent_use: with_human_review`;
- the shared caveat is not answer failure, but agent-readiness/custody caution:
  saved artifacts are clean while live output remains `not_checked`.
- `evaluation.json` remains deterministic run-readiness, not answer-quality
  scoring;
- `caller_action: use_revised_answer` remains caller guidance, not human
  approval.

### PR31: Actionable Delta Rubric v0

Maps to: PRD R6, R8 prerequisite.

Status: completed as the current human-owned actionable-delta rubric.

Goal:

Define what counts as a real Lolla improvement.

Output:

- `docs/evals/actionable-delta-rubric-v0.md`;
- optional compact label list:
  `docs/evals/actionable-delta-rubric-v0.json`;
- examples from the six complex baseline:
  - action changed;
  - threshold changed;
  - sequence changed;
  - evidence gate added;
  - stop rule added;
  - written term added;
  - user question added;
  - scope narrowed;
  - overclaim retracted;
  - no-op prose change.

Acceptance:

- reviewers can use the rubric consistently;
- the rubric rejects smoother prose, more warmth, longer answers, generic
  comprehensiveness, more caveats without action change, and judge-palatable
  blandness as improvement by themselves;
- the rubric can seed a later `actionable_delta` judge.

Current result:

- PR31 is docs/eval-only;
- the rubric is human-owned, not a judge;
- real improvement requires a decision-relevant delta in action, threshold,
  sequence, evidence, stop rule, written term, user question, scope, or
  overclaim handling;
- `no_op_prose_change` captures nicer prose that changes none of those units;
- PR32 uses the rubric to create adversarial pair fixtures, not a judge.

### PR32: Adversarial Pair Fixture Set v0

Maps to: PRD R8, R9.

Status: completed as the first seed fixture set.

Goal:

Create judge-trap fixtures where the smoother answer may be worse than the
rougher revised answer.

Output:

- `docs/evals/adversarial-pair-fixtures-v0.md`;
- `docs/evals/adversarial-pair-fixtures-v0.json`;
- pairs from the six complex baseline;
- labels explaining why the protective answer should win.

Acceptance:

- at least 6-12 pairs;
- each pair names the trap:
  - smoothness bias;
  - length/comprehensiveness bias;
  - status/aura bias;
  - checklist theater bias;
  - generic balance bias;
  - confidence/warmth bias;
  - market-excitement bias;
  - authority/loyalty ambiguity bias;
- no judge is run yet.

Current result:

- six fixtures exist, one per PR30 complex case;
- every fixture cites PR31 rubric labels;
- every fixture names why `revised_answer` should win;
- every fixture names a trap and invalid preference reason;
- the fixture set is paraphrase-only and excludes raw transcript, memo,
  revised-answer, model/provider, and private reasoning text;
- this is seed fixture material, not calibration and not a benchmark claim.

### PR33: Human Review Corpus Batch v0

Maps to: PRD R6, R9.

Status: completed as the first broader local human-review batch.

Goal:

Move beyond six examples toward the 50-100 trace target.

Scope:

- use the existing review workflow and PR31 rubric;
- sample reviewable full-modern records plus boundary records;
- include clean, warned, partial, and degraded examples where useful;
- keep raw transcript/memo/revised-answer out of corpus records;
- review manually; do not use synthetic review as ground truth.

Output:

- `docs/evals/human-review-corpus-batch-v0.md`;
- `reviews/human/corpus-batch-v0/review.json`.

Acceptance:

- 12 or more human-reviewed records if enough safe local records exist;
- every reviewed record has a `lolla.human_review.v0` object;
- every record has artifact sufficiency and actionable-delta status;
- aggregate counts are included;
- boundary records are separated from positive eval evidence;
- no raw transcript/memo/revised-answer text is copied.

Current result:

- 14 records reviewed;
- 12 records counted as positive answer-level eval evidence;
- all 12 counted positives passed, were labeled improved, and had useful
  friction present;
- one older partial record is `needs_followup` because content is readable but
  modern custody sidecars are absent;
- one degraded record is `exclude_from_eval` because the deterministic envelope
  is not eval-ready;
- no new failure mode was needed beyond `artifact_custody_failure`;
- the next slice was PR34 First-Class User Values / Priorities Design v0, not
  a judge.

### PR34: First-Class User Values / Priorities Design v0

Maps to: PRD R5, conversation-understanding roadmap.

Status: completed as a design-only semantic coverage/review surface.

Goal:

Design, but do not implement, the extraction surface for the repeated
`user_values_or_priorities_signal: not_measured` gap.

Why this matters:

The current specialists improve live constraints, stance lineage, and dropped
threads. They do not extract user values or priorities. The corpus shows this
gap in every record.

Output:

- `docs/conversation-understanding/user-values-priorities-signal-v0.md`;
- examples from complex baseline;
- custody rules;
- what counts as source evidence;
- what should stay `unclear` or `needs_review`.

Acceptance:

- does not reuse another specialist name;
- does not create a broad personal memory system;
- does not add runtime calls;
- defines how human review will decide whether the signal matters.

Current result:

- `user_values_or_priorities_signal` is defined as a future semantic coverage
  field;
- the design distinguishes explicit values, inferred priorities, constraints,
  preferences, fears, identity statements, stakeholder obligations, tradeoff
  willingness, and non-negotiables;
- the proposed schema includes status, items, conflicts, open questions,
  grounding, confidence, and review flags;
- derived values must be marked as inferred, lower-confidence, and
  review-needed;
- deterministic validation is limited to schema, ids, refs, grounding/status
  consistency, corpus-safe text boundaries, and conflict references;
- probabilistic extraction and human review remain future work;
- no runtime extraction, report builder, judge, automatic label, memory layer,
  prompt change, or `SKILL.md` change is approved.

### PR35: Live Output Hygiene Decision v0

Maps to: PRD R7, R10.

Status: completed as a design-only live-output hygiene policy.

Goal:

Decide whether `live_output_health: not_checked` should remain an honest
warning or become a bounded check.

Options:

- keep `not_checked` as the default and document it clearly;
- add a deterministic scan over `live_transcript.txt`;
- add a human-review surface for live-output hygiene;
- only check live output in `deep` or `high_stakes` modes later.

Acceptance:

- no false claim that live chat was clean unless it was checked;
- saved artifact quality remains separate from live-output hygiene.

Current result:

- `live_output_health: not_checked` remains the honest default for normal runs;
- `not_checked` is a run-envelope and agent-readiness caveat, not answer-level
  failure by default;
- a complete trusted transcript can be a future bounded path to
  `live_output_health: clean`;
- a manually maintained transcript is not sufficient to claim `clean`;
- live-output issues should keep human `safe_for_agent_use` conservative;
- live-output cleanliness does not relax `caller_action`;
- no runtime capture, finalizer, archive, evaluation, agent-result,
  `SKILL.md`, prompt, or Observatory behavior changes are approved.

### PR36: Risk Mode Behavior Plan v0

Maps to: PRD R2, R7, R8, R11.

Status: completed as a design-only risk-mode behavior policy.

Goal:

Decide what `deep`, `high_stakes`, and `stability` should actually change
after evaluation labels exist.

Candidate behavior:

- `deep`: optional human/specialist review path, cost-gated;
- `high_stakes`: stricter capture, stronger domain boundary language, human
  review required before agent reliance;
- `stability`: compare repeated archived runs rather than rerun by default.

Acceptance:

- no behavior change without cost/latency/custody documentation;
- no high-stakes domain assurance claim;
- `standard` remains stable.

Current result:

- existing `risk_mode` names remain canonical: `quick`, `standard`, `deep`,
  `high_stakes`, and `stability`;
- risk mode is review/reliance context, not answer-quality scoring or action
  approval;
- higher-risk modes should raise artifact, live-output, human-review, and
  domain-review expectations;
- otherwise clean `high_stakes` runs remain conservative through the existing
  `caller_action: ask_user_first` contract behavior;
- PR36 does not relax `caller_action`;
- PR36 does not change prompts, runtime behavior, capture, evaluation,
  agent-result schema, Observatory, or `SKILL.md`.

### PR37: Risk Mode Fixture Matrix v0

Maps to: PRD R2, R7, R8, R11.

Status: completed as a docs/eval-only fixture matrix.

Goal:

Turn PR36's policy into paraphrase-only fixtures that test whether reviewers
and future evaluators preserve the distinction between answer improvement, run
readiness, risk-sensitive reliance, and action approval.

Candidate behavior:

- fixture rows for `standard`, `deep`, `high_stakes`, `stability`, and excluded
  or domain-review-required cases;
- risk-domain examples drawn from PR30-PR33 only as paraphrase-safe patterns;
- expected `safe_for_agent_use` and `caller_action` reads without changing
  runtime code;
- traps around clean artifacts, smooth prose, generic disclaimers, and domain
  assurance.

Acceptance:

- no runtime enforcement;
- no new `risk_mode` enum;
- no domain protocol implementation;
- no automatic labels;
- no judge.

Current result:

- eleven paraphrase-only fixtures now cover `quick`, `standard`, `deep`,
  `high_stakes`, `stability`, and excluded/domain-review routing;
- every fixture names expected answer-level review, run-envelope read,
  `safe_for_agent_use`, `caller_action` stance, human/domain review
  requirement, invalid behavior, source policy refs, and custody flags;
- the fixtures test clean-artifact overtrust, live-output overtrust,
  high-stakes domain-assurance drift, quick-mode overclaim, stability-as-truth
  drift, unsupported domain claims, and `deep`-mode overconfidence;
- PR37 does not implement runtime enforcement, caller-action changes,
  automatic labels, domain protocols, or a judge.

### PR38: Risk Mode Fixture Review v0

Maps to: PRD R2, R7, R8, R11.

Goal:

Human/product review of the PR37 fixture matrix before runtime enforcement or
judge work.

Candidate behavior:

- check whether the eleven fixtures cover the main risk-mode failure traps;
- verify that expected `safe_for_agent_use` labels are conservative enough;
- verify that `caller_action` expectations match the current contract;
- decide whether any fixture should be split, renamed, removed, or added;
- decide whether any high-stakes fixture needs domain-review language before
  implementation.

Acceptance:

- no runtime enforcement;
- no caller-action change;
- no automatic labels;
- no judge;
- clear recommendation for whether risk-mode implementation can start or
  whether more fixture/eval work is required.

### PR39: First Calibrated Binary Judge Prototype

Maps to: PRD R8.

Goal:

Prototype one advisory judge only after enough human labels exist.

Recommended first judge:

`actionable_delta`

Why:

It is narrower than "good answer" and central to Lolla's product thesis.

Acceptance:

- named dataset;
- train/dev/test split;
- TPR/TNR reported separately;
- adversarial pairs included;
- failure examples documented;
- advisory only.

## What Not To Build Yet

- broad answer-quality score;
- generic helpfulness/coherence judge;
- judge before human labels;
- automatic human-review population;
- runtime specialist integration;
- archive specialist artifacts;
- graph DB;
- embeddings-first memory;
- broad conversation-understanding IR;
- prompt rewrite based only on vibes;
- quote-validation repair without fresh failures;
- control-plane enforcement;
- agent approval system.

## Decision Rules

Use these rules to avoid drift:

1. If the failure is artifact/custody/quote/capture/schema, prefer
   deterministic code.
2. If the failure is semantic but repeatedly visible, label it with humans
   before automating.
3. If a judge is proposed, ask which human labels it was calibrated against.
4. If a runtime model call is proposed, ask which offline evidence justifies the
   cost and provider-boundary exposure.
5. If a new artifact is proposed, ask what current artifact cannot answer.
6. If an integration is proposed, ask whether Lolla is replacing a control
   layer instead of feeding it.
7. If an improvement sounds like smoother prose, ask what action, threshold,
   sequence, gate, stop rule, or user question changed.

## Near-Term Definition Of Done

Before building judges or runtime semantic enrichment, Lolla should have:

- six complex runs human-reviewed through PR30;
- a documented actionable-delta rubric through PR31;
- first adversarial pair fixtures through PR32;
- at least one small human-reviewed corpus batch beyond the six examples;
- a design note for the user-values/priorities signal;
- a clear decision on live-output hygiene;
- a clear decision on risk-mode reliance policy;
- risk-mode fixture examples;
- no unresolved confusion between deterministic run readiness and answer
  quality.

That is the smallest flywheel that can improve Lolla run by run without turning
it into a vague critic or overbuilt memory system.
