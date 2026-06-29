# Evaluation Flywheel Action Plan v0

Status: action plan
Date: 2026-06-28

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

A plain-language current capability map now lives in:

```text
docs/evals/current-system-capabilities-v0.md
```

Use it as the first-read explanation of what the system can currently do, which
recorded cases demonstrate it, and why the evaluation layer stays human-owned
before judges.

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

Status: completed as a docs/eval-only fixture review.

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

Current result:

- all 11 original PR37 fixtures reviewed;
- one missing high-stakes values/priorities conflict fixture added and reviewed;
- 12 total fixtures now pass review;
- all fixtures are policy-aligned and useful as implementation gates;
- drift risk is `none` or `low`; no medium/high drift remains;
- the matrix is usable as a future implementation gate, but PR38 does not
  approve runtime enforcement, caller-action changes, automatic labels, domain
  protocols, or a judge.

### PR39: Risk Mode Implementation Plan v0

Maps to: PRD R2, R7, R8, R11.

Status: completed as a docs/design-only implementation plan.

Goal:

Design the smallest future risk-mode behavior change before any code is
written.

Candidate behavior:

- choose one narrow behavior to implement later, such as high-stakes reliance
  copy, implementation tests around `ask_user_first`, or a non-runtime review
  worksheet;
- cite PR36 policy, PR37 fixtures, and PR38 review;
- define exact fixtures that must pass unchanged;
- define required tests, contract docs, and rollback conditions;
- explicitly state whether `caller_action`, `evaluation.json`, `agent_result`,
  Observatory, or `SKILL.md` would need a later separate PR.

Acceptance:

- no runtime enforcement in the plan PR;
- no caller-action change;
- no prompt or `SKILL.md` change;
- no judge;
- clear go/no-go criteria for a later implementation PR.

Current result:

- smallest future behavior change named:
  `high_stakes` reliance/readiness tightening;
- first code-bearing slice should be a test-only contract lock, not runtime
  enforcement;
- future tests must prove current `high_stakes -> ask_user_first`, degraded-run
  blocking, standard-mode regression stability, and PR37/PR38 fixture
  expectations;
- contract impacts are mapped for `agent_result.json`, `evaluation.json`,
  review corpus records, human review workflow, Observatory, and `SKILL.md`;
- PR39 does not change runtime code, prompts, `SKILL.md`, `caller_action`,
  evaluation logic, archive behavior, automatic labels, domain protocols, or
  judges.

### PR40: Risk Mode Contract Lock Tests v0

Maps to: PRD R2, R7, R8, R11.

Status: completed as a test-only contract-lock slice.

Goal:

Lock current high-stakes reliance behavior in tests before changing behavior.

Candidate behavior:

- unit tests for `risk_mode` parsing and preservation;
- agent-result contract tests for otherwise clean
  `high_stakes -> ask_user_first`;
- degraded-run tests proving artifact failure still blocks reliance;
- regression tests proving clean `standard` behavior does not change;
- fixture-mapped tests for PR37/PR38 high-stakes and standard cases;
- no broad caller-action rewrite;
- no domain protocol;
- no judge.

Acceptance:

- tests pass without runtime behavior change;
- `caller_action` remains conservative;
- no prompt or `SKILL.md` change;
- no automatic `safe_for_agent_use`;
- fixture expectations remain intact.

Current result:

- added focused tests in `tests/test_risk_mode_contract.py`;
- locked otherwise clean `high_stakes -> ask_user_first`;
- locked clean `standard -> use_revised_answer`;
- locked degraded high-stakes reliance to
  `caller_action: do_not_use_run_degraded` and evaluation
  `caller_readiness: do_not_use`;
- locked `live_output_health: not_checked` as a caveat that keeps reliance
  inspect-first without claiming live output is clean;
- locked review-corpus preservation of `risk_mode`, `caller_action`, and
  `caller_readiness`;
- mapped core deterministic expectations to PR37/PR38 fixtures;
- no production code, runtime enforcement, prompt, `SKILL.md`, caller-action
  policy, automatic label, domain protocol, or judge change.

### PR41: Risk Mode Evaluation Artifact Clarity v0

Maps to: PRD R2, R7, R8, R11.

Status: completed as a narrow deterministic artifact-clarity slice.

Goal:

Use the PR40 contract-lock tests as a guardrail while deciding whether
`evaluation.json` should make high-stakes reliance caveats and degraded
reliance states more explicit.

Candidate behavior:

- add or clarify deterministic evaluation checks for high-stakes reliance
  caveats;
- document whether `evaluation.overall`, `caller_readiness`, or named checks
  should carry each reliance signal;
- preserve current `caller_action` behavior unless a separate contract PR is
  approved;
- keep answer quality, domain correctness, and `safe_for_agent_use` outside
  deterministic scoring.

Acceptance:

- PR40 tests stay green;
- no model calls;
- no prompt or `SKILL.md` change;
- no runtime enforcement;
- no domain approval or crisis protocol;
- no LLM judge.

Current result:

- added `risk_mode_reliance_policy` to `evaluation.json` checks for
  `risk_mode: high_stakes`;
- otherwise clean `high_stakes` now has an explicit reliance caveat while
  preserving `caller_action: ask_user_first` and `caller_readiness:
  inspect_first`;
- degraded high-stakes keeps `caller_action: do_not_use_run_degraded` and
  `caller_readiness: do_not_use`;
- clean `standard` has no high-stakes caveat and remains `caller_action:
  use_revised_answer` / `caller_readiness: ready`;
- the check is deterministic run-readiness only: no domain correctness, answer
  quality, `safe_for_agent_use`, prompt, `SKILL.md`, or judge change.

### PR42: Risk Mode Review Surface Integration v0

Maps to: PRD R2, R6, R7, R8.

Status: completed as a review-corpus surface integration slice.

Goal:

Expose PR41's deterministic risk-mode reliance caveat in review/corpus surfaces
without changing runtime behavior or caller-action policy.

Candidate behavior:

- review corpus records surface the compact `risk_mode_reliance_policy` result
  when present;
- human-review workflow explains how reviewers should treat high-stakes clean
  artifacts, degraded artifacts, `live_output_health: not_checked`, unresolved
  values conflicts, and unsupported high-stakes domain claims;
- aggregate review reports may count risk-mode reliance caveats;
- `safe_for_agent_use` remains human-owned.

Acceptance:

- PR40 and PR41 tests stay green;
- no model calls;
- no prompt or `SKILL.md` change;
- no runtime enforcement;
- no caller-action change;
- no domain approval or crisis protocol;
- no LLM judge.

Current result:

- review-corpus records now include compact `risk_mode_reliance` metadata;
- high-stakes records with `risk_mode_reliance_policy` expose check status,
  caller action, caller readiness, human/domain review requirements, and
  `automatic_safe_for_agent_use: false`;
- standard records without the high-stakes caveat record `present: false`;
- no raw transcript, memo, revised answer, model/provider content, private
  reasoning, absolute archive path, secret, or credential content is copied
  into the risk-mode reliance surface;
- human-review workflow explains that this is a reliance caveat, not
  answer-quality failure, domain approval, or automatic `safe_for_agent_use`;
- `caller_action`, runtime behavior, prompts, `SKILL.md`, and judge behavior
  remain unchanged.

### PR43: Risk Mode Reliance Review Batch v0

Maps to: PRD R2, R6, R7, R8.

Goal:

Use the PR42 review-corpus field in a small local review batch to verify that
humans can consistently separate high-stakes reliance caveats from answer-level
quality and `safe_for_agent_use`.

Current result:

- read-only local corpus export found 80 records, all `risk_mode: standard`,
  with zero `risk_mode_reliance.present: true` records;
- PR43 therefore does not claim real high-stakes archive outcome evidence;
- [Risk Mode Reliance Review Batch v0](risk-mode-reliance-review-batch-v0.md)
  uses PR37/PR38 paraphrase-only risk-mode fixtures to validate the PR42 review
  surface;
- reviewers can interpret `risk_mode_reliance.present: true` as a reliance
  caveat without treating it as answer-quality failure, domain approval, or
  automatic `safe_for_agent_use`;
- workflow wording is sufficient for this fixture-backed batch;
- no taxonomy or rubric change is recommended yet.

Acceptance:

- no model calls;
- no prompt or `SKILL.md` change;
- no runtime enforcement;
- no caller-action change;
- no automatic labels;
- no domain approval or crisis protocol;
- no LLM judge.

### PR44: Review Corpus Reliance Manifest Counts v0

Maps to: PRD R2, R6, R8.

Status: completed as an additive review-corpus manifest visibility slice.

Goal:

Add deterministic manifest-level visibility for the absence or presence of
`risk_mode_reliance` caveats before any judge or real high-stakes archive
expansion.

Why:

PR43 showed that the local real archive corpus has zero high-stakes
reliance-present records, even though the PR42 per-record surface is ready. The
manifest should make that absence visible so future review batches cannot
accidentally imply high-stakes evidence where none exists.

Candidate behavior:

- add aggregate counts for `risk_mode_reliance.present`;
- count present/absent records by `risk_mode`;
- keep raw content, answer-quality labels, and human-review labels out of the
  manifest;
- preserve current per-record PR42 behavior.

Acceptance:

- no model calls;
- no prompt or `SKILL.md` change;
- no runtime enforcement;
- no caller-action change;
- no automatic labels;
- no domain approval or crisis protocol;
- no LLM judge;
- no archive mutation.

Current result:

- review-corpus manifests now include `risk_mode_reliance_present_counts`;
- review-corpus manifests now include
  `risk_mode_reliance_by_risk_mode_counts`;
- review-corpus manifests now include
  `risk_mode_reliance_check_status_counts`;
- the fields are additive and keep `lolla.review_corpus_manifest.v0`;
- per-record `risk_mode_reliance` remains unchanged;
- local export smoke still shows 80 records, all `risk_mode: standard`, with
  zero reliance-present records.

### PR45: Current State Anti-Drift Handoff v0

Maps to: PRD R2, R6, R8, R11, R12.

Status: completed as a docs-only current-state handoff.

Goal:

Create a compact first-read note so a fresh session can understand what Lolla is,
what PR30-PR54 built, what evidence is still missing, and what must not be built
until explicit approval gates.

Output:

- [Current State Anti-Drift Handoff v0](current-state-anti-drift-handoff-v0.md).

Current result:

- summarizes Lolla as probabilistic reasoning inside deterministic custody;
- records the PR30-PR54 evaluation/risk-mode/values visibility chain;
- records the current real corpus evidence: 80 records, all `risk_mode:
  standard`, with `risk_mode_reliance_present_counts` of `false: 80` and
  `true: 0`;
- states that the current corpus contains no real high-stakes
  reliance-present archive evidence;
- distinguishes fixture-backed review-surface validation from real archive
  outcome evidence;
- names the PR48 high-stakes gate, the PR49-PR54 values worksheet lane, and the
  live-output hygiene implementation gate;
- makes no code, runtime, prompt, archive, judge, scoring, or automatic-label
  change.

Next safe slice:

- PR46 Approved High-Stakes Evidence Seed Plan v0, docs-only and no runs.

### PR46: Approved High-Stakes Evidence Seed Plan v0

Maps to: PRD R2, R6, R8, R9.

Status: completed as a docs-only approval and custody plan.

Goal:

Define the exact plan for creating high-stakes archive evidence later, without
creating or running any conversations in this slice.

Output:

- [High-Stakes Evidence Seed Plan v0](high-stakes-evidence-seed-plan-v0.md).

Current result:

- defines nine candidate scenario categories;
- separates approved-with-approval reasoning-audit cases from excluded or
  domain-review-required cases;
- keeps clean high-stakes expected behavior conservative with
  `caller_action: ask_user_first`;
- keeps degraded high-stakes behavior dominated by
  `caller_action: do_not_use_run_degraded`;
- requires explicit approval of scenario list, run count, cost, custody,
  privacy treatment, reviewer, and operator procedure before any `$lolla` run;
- requires future evidence claims to be backed by review-corpus manifest counts
  showing high-stakes `risk_mode_reliance.present: true` records;
- makes no code, runtime, prompt, archive, judge, scoring, or automatic-label
  change.

Next safe slice:

- PR47 High-Stakes Evidence Fixture Pack v0, docs/eval JSON only and no runs.

### PR47: High-Stakes Evidence Fixture Pack v0

Maps to: PRD R2, R6, R8, R9.

Status: completed as a docs/eval-only fixture pack.

Goal:

Create paraphrase-only high-stakes evidence fixtures from the PR46 seed plan so
reviewers can test expectations before real high-stakes runs exist.

Output:

- [High-Stakes Evidence Fixtures v0](high-stakes-evidence-fixtures-v0.md);
- [high-stakes-evidence-fixtures-v0.json](high-stakes-evidence-fixtures-v0.json).

Current result:

- adds six paraphrase-only fixtures;
- covers clean high-stakes with `ask_user_first`;
- covers unresolved values and stakeholder conflict;
- covers unsupported domain claim despite otherwise clean custody;
- covers degraded high-stakes archive custody;
- covers trusted clean live output while preserving human-owned reliance;
- covers excluded crisis or out-of-scope cases;
- keeps fixtures separate from archive evidence, human labels, judge
  calibration truth, runtime behavior, and prompt changes.

### PR48: Review Corpus Evidence Readiness Analyzer v0

Maps to: PRD R2, R6, R8, R9.

Status: completed as offline deterministic tooling.

Goal:

Add a read-only analyzer for review-corpus manifests so future sessions can
answer whether a manifest actually contains high-stakes reliance-present
archive evidence.

Output:

- [Review Corpus Evidence Readiness v0](review-corpus-evidence-readiness-v0.md);
- `engine/system_b/review_corpus_evidence_readiness.py`;
- `scripts/analyze_review_corpus_evidence_readiness.py`;
- `tests/test_review_corpus_evidence_readiness.py`.

Current result:

- reads only manifest JSON;
- requires PR44 aggregate fields before making a readiness call;
- returns `insufficient_manifest_fields` for old or thin manifests;
- returns `no_high_stakes_reliance_evidence` when the manifest has zero
  `high_stakes|true` reliance-present records;
- returns `has_high_stakes_reliance_evidence` only when the manifest explicitly
  counts high-stakes reliance-present records;
- omits manifest paths, archive roots, raw transcript, memo, revised-answer,
  model/provider text, private reasoning, secrets, and credentials;
- makes no model calls and uses no LLM judge;
- does not change runtime behavior, prompts, `SKILL.md`, `caller_action`,
  provider-boundary policy, human-review labels, or answer-quality scoring.

Stop point:

- PR48 is the approval gate before any real high-stakes run work.
- Do not start real high-stakes archive evidence creation unless the maintainer
  explicitly approves the scenario list, run count, cost, custody path,
  reviewer, and operator procedure.
- The separate user-values/priorities worksheet lane is now paused at PR54
  unless explicitly reopened; it should not create high-stakes runs or runtime
  behavior by implication.

### PR49: User Values / Priorities Worksheet Plan v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a docs-only worksheet plan.

Goal:

Turn PR34's `user_values_or_priorities_signal` design into an actionable
human-review worksheet plan without implementing extraction, blank exports,
runtime behavior, memory, automatic labels, or judging.

Output:

- [User Values / Priorities Worksheet Plan v0](user-values-priorities-worksheet-plan-v0.md).

Current result:

- defines the worksheet as a human-owned review artifact, not a model output;
- records explicit values, inferred priorities, tradeoff willingness,
  non-negotiables, stakeholder obligations, conflicts, unclear values,
  user-answerable questions, and answer treatment;
- proposes a future `lolla.user_values_priorities_worksheet.v0` shape without
  adding production JSON or schema enforcement;
- explains how worksheet notes can support PR31 labels such as
  `user_question_added`, `scope_narrowed`, `threshold_changed`,
  `evidence_gate_added`, `stop_rule_added`, and `overclaim_retracted`;
- keeps high-stakes unresolved values/stakeholder conflicts conservative
  without changing `risk_mode`, `caller_action`, `safe_for_agent_use`, review
  corpus export, or evaluation logic;
- recommends PR50 as a paraphrase-only worksheet fixture pack before a blank
  exporter or extraction work.

Stop point:

- PR49 stops after docs and validation.
- Do not implement a worksheet exporter, extraction, runtime integration,
  `conversation_understanding_ir.v0`, automatic labels, or a judge in this
  slice.

### PR50: User Values / Priorities Worksheet Fixture Pack v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a docs/eval-only fixture pack.

Goal:

Create paraphrase-only filled worksheet examples that test whether the PR49
worksheet shape is understandable and useful for human review before exporter,
validator, extraction, runtime, memory, or judge work.

Output:

- [User Values / Priorities Worksheet Fixtures v0](user-values-priorities-worksheet-fixtures-v0.md);
- [user-values-priorities-worksheet-fixtures-v0.json](user-values-priorities-worksheet-fixtures-v0.json).

Current result:

- adds six paraphrase-only fixtures from existing PR30/PR33 review patterns;
- covers cofounder authority transfer, career/family written terms, enterprise
  beta buyer proof, consulting pre-sale scoped pilot, product pivot capacity
  gate, and clinic controls high-risk deployment;
- records values items, conflicts, answer treatment, expected review read,
  rubric connections, failure traps, and custody flags;
- keeps all raw transcript, memo, revised-answer, model/provider, private
  reasoning, local absolute path, secret, and credential content out of the
  fixture pack;
- keeps high-stakes-like safety/adoption tensions conservative without creating
  real high-stakes archive evidence or changing `risk_mode`, `caller_action`,
  review-corpus export, evaluation logic, `safe_for_agent_use`, or runtime
  behavior;
- handed off to PR51 for docs/eval-only human/product review.

Stop point:

- PR50 stopped after docs/JSON fixtures and validation.
- PR50 did not implement a blank worksheet exporter, extraction, runtime
  integration, `conversation_understanding_ir.v0`, automatic labels, or a judge.

### PR51: User Values / Priorities Worksheet Fixture Review v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a docs/eval-only fixture review.

Goal:

Review the six PR50 user-values/priorities worksheet fixtures for clarity,
overclaim risk, stakeholder-obligation handling, conflict preservation, PR31
usefulness, high-stakes conservatism, and readiness for later blank
worksheet/export structure.

Output:

- [User Values / Priorities Worksheet Fixture Review v0](user-values-priorities-worksheet-fixture-review-v0.md);
- [review.json](../../reviews/human/user-values-priorities-worksheet-fixture-review-v0/review.json).

Current result:

- reviews all six PR50 fixtures;
- marks all six as `pass`;
- records `clear: 6` worksheet clarity;
- records `preserved: 6` stakeholder-obligation handling;
- records `preserved: 6` conflict preservation;
- records `yes: 6` overclaim control;
- records `useful: 6` PR31 usefulness;
- records `yes: 1` and `not_applicable: 5` high-stakes conservatism;
- records `none: 6` primary issues;
- recommends PR52 as narrow blank worksheet/export structure, not extraction.

Stop point:

- PR51 stopped after docs/JSON review and validation.
- PR51 did not implement extraction, runtime integration,
  `conversation_understanding_ir.v0`, automatic labels, or a judge.

### PR52: User Values / Priorities Blank Worksheet Export v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a narrow deterministic code/docs slice.

Goal:

Create a local helper for generating blank
`lolla.user_values_priorities_worksheet.v0` JSON from compact metadata, without
reading archives, extracting values, populating labels, changing runtime
behavior, or adding a judge.

Output:

- [User Values / Priorities Blank Worksheet Export v0](user-values-priorities-blank-worksheet-export-v0.md);
- [user_values_priorities_worksheet.py](../../engine/system_b/user_values_priorities_worksheet.py);
- [build_user_values_priorities_worksheet.py](../../scripts/build_user_values_priorities_worksheet.py);
- [test_user_values_priorities_worksheet.py](../../tests/test_user_values_priorities_worksheet.py).

Current result:

- adds deterministic blank worksheet construction;
- adds deterministic blank worksheet validation;
- adds a CLI requiring `--out` and accepting optional compact `--case-id`,
  `--run-id`, and `--archive-relpath`;
- rejects absolute paths, parent traversal, home shorthand, path-shaped
  case/run identifiers, and private/raw-content marker strings in metadata;
- keeps `values_items`, `conflicts`, answer-treatment arrays, and
  reviewer notes empty;
- keeps reviewer-summary fields `unfilled`;
- keeps all raw/private/model/judge/source inclusion flags conservative;
- recommends PR53 as a local human worksheet pilot, not extraction.

Stop point:

- PR52 stopped after blank helper, CLI, tests, docs, and validation.
- PR52 did not implement filled worksheets, extraction, runtime integration,
  `conversation_understanding_ir.v0`, automatic labels, or a judge.

### PR53: User Values / Priorities Worksheet Human Pilot v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a docs/local-review pilot.

Goal:

Pilot human-filled `lolla.user_values_priorities_worksheet.v0` artifacts against
existing reviewed records, using paraphrase-only notes and no raw archive
content.

Output:

- [User Values / Priorities Worksheet Human Pilot v0](user-values-priorities-worksheet-human-pilot-v0.md);
- [worksheets.json](../../reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json).

Current result:

- fills four worksheets by hand from existing reviewed summaries and local
  human-review records;
- covers cofounder authority transfer, career/family written terms, enterprise
  beta buyer proof, and clinic controls deployment;
- records 16 value items, 8 conflicts, and 16 confirmation-needed items;
- records `values_surface_sufficient_for_review: yes` for all four worksheets;
- records no actionable-delta label changes from the worksheet itself;
- keeps one high-risk-like clinic worksheet more conservative for
  `safe_for_agent_use_impact`;
- keeps all raw/private/model/judge/source inclusion flags conservative;
- recommends PR54 as a pilot review / v0 decision, not extraction.

Stop point:

- PR53 stops after docs/JSON local review and validation.
- Do not implement extraction, runtime integration,
  `conversation_understanding_ir.v0`, automatic labels, or a judge from PR53.

### PR54: User Values / Priorities Pilot Review v0

Maps to: PRD R6, R8, conversation-understanding roadmap.

Status: completed as a docs/local-review decision.

Goal:

Review the PR53 human-filled worksheet pilot and decide whether the v0
worksheet lane is complete enough to pause or needs a small patch.

Output:

- [User Values / Priorities Pilot Review v0](user-values-priorities-pilot-review-v0.md);
- [review.json](../../reviews/human/user-values-priorities-pilot-review-v0/review.json).

Current result:

- reviews four PR53 worksheets and marks all four `pass`;
- confirms `values_surface_sufficient_for_review: yes` in all four;
- confirms conflict preservation, stakeholder-obligation handling, overclaim
  control, and PR31 usefulness in all four;
- preserves the conservative stance that all 16 PR53 value items still need
  user confirmation;
- records one expected conservative reliance impact for the clinic-controls
  worksheet;
- does not change PR31 labels, populate `lolla.human_review.v0`, change
  `safe_for_agent_use`, or approve agent reliance.

Stop point:

- the user-values/priorities worksheet lane is complete for v0 human-owned
  review and paused;
- do not add extraction, runtime/archive integration, memory,
  `conversation_understanding_ir.v0`, automatic labels, `safe_for_agent_use`
  automation, answer-quality scoring, or a judge without a new explicit gate.

Later judge work can resume only after human-owned labels and high-stakes
review evidence are present enough to calibrate a narrow advisory judge. When
it resumes, it should still require a named dataset, train/dev/test split,
separately reported TPR/TNR, adversarial pairs, documented failure examples,
and advisory-only use.

### PR55: Semantica Comparative Architecture Note / Accountability PRD v0

Maps to: R6, R9, conversation-understanding/accountability roadmap.

Status: completed as a docs-only planning artifact.

Goal:

Preserve the useful parts of the Semantica comparison without turning Lolla into
a generic context graph, memory, policy, compliance, or judge product.

Output:

- [Semantica-Inspired Accountability PRD v0](../conversation-understanding/semantica-inspired-accountability-prd-v0.md).

Current result:

- records why Semantica is useful as accountability architecture: decision
  records, provenance, conflict records, preflight diagnostics, graph-shaped
  accountability views, and pipeline discipline;
- makes the Lolla distinction explicit: Lolla is a local reasoning-audit
  harness, not a graph database product, embeddings system, chunking pipeline,
  global memory layer, policy engine, compliance platform, generic agent safety
  layer, domain authority, LLM judge, or answer-quality scoring product;
- defines a selective borrowing rule for ideas that improve local
  inspectability, preserve human semantic judgment, can begin as docs/fixtures
  or read-only exports, and remain useful without a future judge;
- preserves the primitive queue:
  `lolla.audit_decision_record.v0`, `lolla.provenance_map.v0`,
  `lolla.review_conflict_register.v0`, `lolla doctor / preflight`, and
  `lolla.case_graph.v0`;
- records PR56 through PR65 as an implementation queue, not approval for code.

Stop point:

- PR55 only lands the plan.
- Do not implement doctor/preflight, decision records, provenance maps,
  conflict registers, case graph exports, runtime behavior, model calls,
  archive mutation, prompts, `SKILL.md`, graph DB, embeddings, memory, policy
  enforcement, automatic labels, answer-quality scoring, or judges from this
  slice.
- PR56 has now landed as the docs-only doctor/preflight plan, PR57 has now
  implemented the smallest read-only doctor CLI, PR58 has now designed the
  audit decision record shape, and PR59 has now reviewed six paraphrase-only
  decision-record fixtures. PR60 has now designed the provenance map shape.

### PR56: Lolla Doctor / Preflight Plan v0

Maps to: R6/R9 accountability and readiness inspectability.

Status: completed as a docs-only planning artifact.

Goal:

Define the future read-only doctor/preflight surface before adding any CLI.
The doctor should help users and maintainers verify local wiring, provider/cost
readiness, review-corpus manifest visibility, high-stakes evidence
absence/presence, output-path safety, and privacy boundaries before they spend
tokens or run `$lolla`.

Output:

- [Lolla Doctor / Preflight Plan v0](lolla-doctor-preflight-plan-v0.md).

Current result:

- defines the future command shape, including a possible
  `python3 scripts/lolla_doctor.py --archive-root ~/.local/share/lolla/runs --json`
  entry point and later `lolla doctor` alias;
- defines planned check groups for runtime discovery, archive-root discovery,
  helper script availability, provider configuration presence, model/provider
  cost telemetry, review-corpus export availability, manifest readability,
  risk-mode reliance counts, high-stakes evidence visibility, output-path
  safety, archive mutation guard expectations, repo/runtime boundary checks,
  and privacy-safe output;
- defines deterministic `pass`, `warn`, `fail`, and `not_applicable` semantics;
- sketches the future `lolla.doctor_report.v0` JSON shape with zero model
  calls, no archive writes, no `$lolla` run, and safe-to-print check details;
- distinguishes blocking failures from warnings so missing local wiring does
  not become wasted model calls.

Stop point:

- PR56 only lands the plan.
- Do not add the doctor CLI, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, change provider-boundary policy, change
  `caller_action`, approve high-stakes runs, add judges, add scoring, add
  automatic labels, or begin Semantica-style platform work from this slice.
- PR57 has now implemented the smallest local read-only doctor CLI. PR58 has
  now designed `lolla.audit_decision_record.v0`. The next possible slice is
  PR59 Audit Decision Record Fixture Review v0, still docs/eval-only.

### PR57: Lolla Doctor Read-Only CLI v0

Maps to: R6/R9 deterministic readiness inspectability.

Status: completed as a read-only code/tests/docs slice.

Goal:

Add the smallest local preflight command from the PR56 plan so users and
maintainers can inspect wiring before spending tokens or running `$lolla`.

Output:

- [Lolla Doctor Read-Only CLI v0](lolla-doctor-readonly-cli-v0.md).
- `engine/system_b/lolla_doctor.py`
- `scripts/lolla_doctor.py`
- `tests/test_lolla_doctor.py`

Current result:

- implements `lolla.doctor_report.v0`;
- checks runtime discovery, archive-root discovery, helper script availability,
  provider configuration presence, model/provider cost-table readiness,
  review-corpus manifest readability, risk-mode reliance counts, high-stakes
  evidence visibility, output-path safety, archive mutation guard expectations,
  repo/runtime boundary state, and privacy-safe output;
- supports JSON output as the stable contract and compact text output for local
  use;
- refuses `--out` paths inside archive roots;
- preserves `model_calls: 0`, `archives_mutated: false`, and
  `would_run_lolla: false`;
- tests that provider credential values, raw transcript/memo/revised-answer
  fields, and provider-client import paths are not exposed.

Stop point:

- PR57 only implements the read-only doctor CLI.
- Do not use doctor output as high-stakes approval, answer-quality judgment,
  `safe_for_agent_use` automation, or evidence that a future `$lolla` answer is
  good.
- Do not add decision-record exporters, provenance maps, conflict registers,
  case graph exports, runtime integration, prompt changes, `SKILL.md` changes,
  provider-boundary policy changes, caller-action changes, graph DB, embeddings,
  chunking, memory, policy engines, automatic labels, answer-quality scoring,
  or judges from this slice.
- PR58 has now designed `lolla.audit_decision_record.v0`. The next possible
  slice is PR59 Audit Decision Record Fixture Review v0, docs/eval-only.

### PR58: Audit Decision Record Design v0

Maps to: R6/R9 accountable review projections.

Status: completed as a docs/JSON design slice.

Goal:

Define `lolla.audit_decision_record.v0` as a compact local accountability
projection over existing Lolla artifacts before any exporter exists.

Output:

- [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md).
- [audit-decision-record-v0.json](../conversation-understanding/audit-decision-record-v0.json).

Current result:

- defines a paraphrase-only record for the audited decision, original
  recommendation summary, revised recommendation summary, PR31
  actionable-delta buckets, values/stakeholder conflicts, unresolved
  questions, source artifacts, review refs, custody flags, and limitations;
- maps the shape to PR31 labels such as `action_changed`,
  `threshold_changed`, `sequence_changed`, `evidence_gate_added`,
  `stop_rule_added`, `written_term_added`, `user_question_added`,
  `scope_narrowed`, `overclaim_retracted`, and `no_op_prose_change`;
- explains why the record is not `conversation_understanding_ir.v0`, answer
  scoring, a judge, automatic labels, or `safe_for_agent_use` automation;
- includes one checked-in paraphrase-only JSON example from an already reviewed
  case.

Stop point:

- PR58 only designs the record and example.
- Do not implement an exporter, run `$lolla`, call models, mutate archives,
  change prompts, change `SKILL.md`, change provider-boundary policy, approve
  high-stakes runs, add judges, add scoring, add automatic labels, or begin
  Semantica-style platform work from this slice.
- PR59 has now reviewed audit decision record fixtures. PR60 has now designed
  the provenance map shape.

### PR59: Audit Decision Record Fixture Review v0

Maps to: R6/R9 accountable review projections.

Status: completed as a docs/eval-only fixture review.

Goal:

Test whether the PR58 decision record shape is understandable and useful on
existing reviewed cases before any exporter is built.

Output:

- [Audit Decision Record Fixtures v0](audit-decision-record-fixtures-v0.md).
- [audit-decision-record-fixtures-v0.json](audit-decision-record-fixtures-v0.json).
- [review.json](../../reviews/human/audit-decision-record-fixture-review-v0/review.json).

Current result:

- creates six paraphrase-only fixtures from existing reviewed cases;
- reviews all six as `pass`;
- confirms decision delta clarity is `clear` in five fixtures and
  `mostly_clear` in one;
- confirms PR31 mapping is useful in all six;
- confirms reviewers can use all six without raw content;
- marks the shape ready for a future read-only exporter design prototype with
  caveats about relative paths, custody flags, no labels, no scoring, and no
  approval claims.

Stop point:

- PR59 only reviews fixtures.
- Do not implement an exporter, run `$lolla`, call models, mutate archives,
  change prompts, change `SKILL.md`, change provider-boundary policy, approve
  high-stakes runs, add judges, add scoring, add automatic labels, or begin
  Semantica-style platform work from this slice.
- PR60 has now designed the provenance map shape. Do not infer exporter or
  runtime work from PR59 or PR60.

### PR60: Provenance Map Design v0

Maps to: R6/R9 local artifact-lineage inspectability.

Status: completed as a docs/JSON design slice.

Goal:

Define `lolla.provenance_map.v0` as a local artifact-lineage map before any
exporter or runtime integration exists.

Output:

- [Provenance Map v0](../conversation-understanding/provenance-map-v0.md).
- [provenance-map-v0.json](../conversation-understanding/provenance-map-v0.json).

Current result:

- defines entities, activities, agents, and relationships for Lolla artifact
  lineage;
- maps current artifact roles such as captured conversation, extraction, audit
  result, revised answer, memo, agent result, evaluation, reasoning trace, and
  human review;
- keeps the checked-in example raw-content-safe, relative-path-only, and free
  of real archive hashes;
- differentiates artifact lineage from answer quality;
- rejects RDF requirements, PROV-O/W3C compliance claims, graph DB, memory,
  source quote dumps, domain approval, and runtime integration.

Stop point:

- PR60 only designs the provenance map and example.
- Do not implement an exporter, add tests, add schemas under `engine/`, add CLI
  support, read archives, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, add graph DB, add memory, score answer quality,
  or begin Semantica-style platform work from this slice.
- Implemented next as PR61 Review Conflict Register Design v0, docs/JSON
  design only.

### PR61: Review Conflict Register Design v0

Maps to: R6/R9 human-review-owned conflict preservation.

Status: completed as a docs/JSON design slice.

Goal:

Define `lolla.review_conflict_register.v0` as a local register of unresolved
conflicts visible in a Lolla run or review projection.

Output:

- [Review Conflict Register v0](review-conflict-register-v0.md).
- [review-conflict-register-v0.json](review-conflict-register-v0.json).

Current result:

- defines human-owned conflict rows with category, status, paraphrase-only
  summary, sides, review owner, decision impact, related PR31 labels, and raw
  content exclusion;
- covers user-values, stakeholder-obligation, live-constraint,
  recommendation-action, risk-mode reliance, artifact-health,
  provider-boundary, unresolved-question, human-review disagreement,
  provenance-gap, and decision-record-flattening conflicts;
- keeps categories descriptive rather than executable;
- preserves conflict detail as review context rather than resolution,
  severity automation, policy enforcement, answer-quality scoring, labels, or
  judge output;
- uses a checked-in example that is paraphrase-only and relative-reference
  safe.

Stop point:

- PR61 only designs the review conflict register and example.
- Do not implement an exporter, add tests, add schemas under `engine/`, add CLI
  support, read archives, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, resolve conflicts, automate severity, enforce
  policy, create labels, score answer quality, or begin Semantica-style
  platform work from this slice.
- Implemented next as PR62 Case Graph Export Design v0, docs/JSON design only.
  It describes a future export/view shape without implying an exporter exists.

### PR62: Case Graph Export Design v0

Maps to: R6/R9 run-local review orientation.

Status: completed as a docs/JSON design slice.

Goal:

Define `lolla.case_graph.v0` as a future run-local case graph export/view shape
over existing review-safe artifacts.

Output:

- [Case Graph Export Design v0](../conversation-understanding/case-graph-export-v0.md).
- [case-graph-export-v0.json](../conversation-understanding/case-graph-export-v0.json).

Current result:

- defines node types for decisions, original/revised recommendation shape,
  actionable deltas, evidence gates, thresholds, sequence changes, stop rules,
  written terms, user questions, values/priorities, stakeholders, unresolved
  conflicts, artifacts, provenance activities, review records, doctor checks,
  and limitations;
- defines edge types for review-safe relationships such as changed-by,
  adds-gate, raises-question, has-conflict, preserves-conflict,
  supported-by-artifact, reviewed-by, derived-from, used-by, generated-by, and
  has-limitation;
- shows how audit decision record, provenance map, review conflict register,
  values/priorities worksheet, human review, doctor reports where relevant, and
  artifacts can appear as nodes or edges;
- keeps the checked-in example paraphrase-only, relative-reference-only, and
  free of real archive hashes;
- states that the graph is a view, not source of truth, graph DB, memory,
  GraphRAG, entity resolution, answer-quality scoring, automatic labels, or
  domain approval.

Stop point:

- PR62 only designs the case graph export/view shape and example.
- Do not implement an exporter, add tests, add schemas under `engine/`, add CLI
  support, read archives, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, add graph DB, add embeddings, add memory, add
  GraphRAG, add entity resolution, score answer quality, create labels, or
  begin Semantica-style platform work from this slice.
- PR63 was not runtime work; it was implemented next as a docs/JSON-only
  accountability-view fixture pack after PR60 through PR62 existed.

Implemented next as the broader PR63 Accountability View Fixture Pack v0.

### PR63: Accountability View Fixture Pack v0

Maps to: R6/R9 combined accountability-view evidence.

Status: completed as a docs/JSON fixture slice.

Goal:

Create paraphrase-only fixture bundles that show audit decision record,
provenance map, review conflict register, and case graph views together before
any exporter exists.

Output:

- [Accountability View Fixtures v0](accountability-view-fixtures-v0.md).
- [accountability-view-fixtures-v0.json](accountability-view-fixtures-v0.json).

Current result:

- creates three fixture bundles for `launch-public-enterprise-beta`,
  `deploy-assisted-intake-routing`, and `ceo-remove-founding-cofounder`;
- includes all four accountability views in each fixture bundle;
- keeps the examples paraphrase-only and based on checked-in review summaries;
- uses relative artifact references and placeholder hashes only;
- keeps every raw/private/local-path custody flag safe;
- tests whether a reviewer can see the decision delta, artifact lineage,
  unresolved conflict, and graph-shaped relationship view together without
  mistaking clean structure for advice quality.

Stop point:

- PR63 only creates fixture bundles.
- Do not implement an exporter, add tests, add schemas under `engine/`, add CLI
  support, read archives, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, add graph DB, add embeddings, add memory, add
  GraphRAG, add entity resolution, score answer quality, create labels, or
  begin Semantica-style platform work from this slice.
- Implemented next as PR64 Accountability View Fixture Review v0, docs/eval-only.

### PR64: Accountability View Fixture Review v0

Maps to: R6/R9 combined accountability-view evidence gate.

Status: completed as docs/eval-only fixture review.

Output:

- [Accountability View Fixture Review v0](accountability-view-fixture-review-v0.md).
- [review.json](../../reviews/human/accountability-view-fixture-review-v0/review.json).

Current result:

- reviews all three PR63 fixture bundles;
- marks 3 pass, 0 revise, 0 exclude;
- finds `audit_decision_record` high value on all three fixtures and ready for a
  later exporter-design decision;
- finds `provenance_map` medium value and needing more fixtures;
- finds `review_conflict_register` high value but needing more fixtures before
  helper/exporter design;
- holds `case_graph` before implementation because graph-shaped views carry
  decorative-structure, memory, graph DB, and source-of-truth drift risk.

Stop point:

- PR64 only reviews fixture bundles.
- Do not implement exporters, add tests, add schemas under `engine/`, add CLI
  support, read archives, run `$lolla`, call models, mutate archives, change
  prompts, change `SKILL.md`, add graph DB, add embeddings, add memory, add
  GraphRAG, add entity resolution, score answer quality, create labels, add
  judges, or begin Semantica-style platform work from this slice.
- The next slice is PR65 Accountability Implementation Decision Gate v0,
  docs-only.

## What Not To Build Yet

- broad answer-quality score;
- generic helpfulness/coherence judge;
- judge before human labels;
- automatic human-review population;
- runtime specialist integration;
- archive specialist artifacts;
- graph DB;
- embeddings-first memory;
- high-stakes archive evidence claims before approved high-stakes runs exist;
- Semantica-style graph DB, embeddings, chunking, memory, policy engine,
  compliance platform, generic agent safety layer, or answer-quality authority;
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
- a human-review worksheet plan for that signal;
- paraphrase-only worksheet fixtures for that signal;
- a clear decision on live-output hygiene;
- a clear decision on risk-mode reliance policy;
- risk-mode fixture examples;
- human/product review of risk-mode fixtures;
- no unresolved confusion between deterministic run readiness and answer
  quality.

That is the smallest flywheel that can improve Lolla run by run without turning
it into a vague critic or overbuilt memory system.

The next conservative accountability step is PR65 Accountability Implementation
Decision Gate v0. It should make one docs-only decision about what, if anything,
deserves a future implementation slice. It should not implement an exporter, add
tests, add schemas under `engine/`, add CLI support, read archives, run
`$lolla`, call models, mutate archives, change prompts, change `SKILL.md`,
change provider-boundary policy, add graph DB, add embeddings, add memory, add
entity resolution, add GraphRAG, resolve conflicts automatically, score answer
quality, add judges, add automatic labels, or start any Semantica-style
platform work.
