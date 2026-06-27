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
| human-review labels | human-owned quality/taste labels | next |
| review findings note | summary of what passed, failed, and why | next |
| adversarial-pair fixtures | smoothness-bias traps for future judges | next |
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
`lolla.human_review.v0` as a human/product review seed.

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

The next active frontier is turning those labels into a rubric for actionable
delta, then reviewing additional records.

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

Goal:

Define what counts as a real Lolla improvement.

Output:

- a short rubric under `docs/evals/`;
- examples from the six complex baseline:
  - action changed;
  - threshold changed;
  - sequence changed;
  - evidence gate added;
  - stop rule added;
  - user question added;
  - no-op prose change.

Acceptance:

- reviewers can use the rubric consistently;
- the rubric rejects smoother prose, more warmth, longer answers, generic
  comprehensiveness, more caveats without action change, and judge-palatable
  blandness as improvement by themselves;
- the rubric can seed a later `actionable_delta` judge.

### PR32: Adversarial Pair Fixture Set v0

Maps to: PRD R8, R9.

Goal:

Create judge-trap fixtures where the smoother answer may be worse than the
rougher revised answer.

Output:

- local fixture JSONL or Markdown under `docs/evals/` or `tests/fixtures/`;
- pairs from the six complex baseline;
- labels explaining why the protective answer should win.

Acceptance:

- at least 6-12 pairs;
- each pair names the trap:
  - smoothness bias;
  - verbosity bias;
  - caution overcorrection;
  - ignored stakeholder;
  - missing gate;
  - unsupported new claim;
- no judge is run yet.

### PR33: Human Review Corpus Batch v0

Maps to: PRD R6, R9.

Goal:

Move beyond six examples toward the 50-100 trace target.

Scope:

- export review corpus;
- sample only reviewable records;
- include clean, warned, partial, degraded, and legacy-limited runs;
- keep raw transcript/memo/revised-answer out of corpus records;
- review manually or use synthetic review only as candidate notes.

Acceptance:

- 20-30 human-reviewed records as an interim batch;
- manifest says which records were full-modern versus legacy;
- taxonomy changes are proposed only when failures recur.

### PR34: First-Class User Values / Priorities Design v0

Maps to: PRD R5, conversation-understanding roadmap.

Goal:

Design, but do not implement, the extraction surface for the repeated
`user_values_or_priorities_signal: not_measured` gap.

Why this matters:

The current specialists improve live constraints, stance lineage, and dropped
threads. They do not extract user values or priorities. The corpus shows this
gap in every record.

Output:

- design note for `user_values_or_priorities_signal`;
- examples from complex baseline;
- custody rules;
- what counts as source evidence;
- what should stay `unclear` or `needs_review`.

Acceptance:

- does not reuse another specialist name;
- does not create a broad personal memory system;
- does not add runtime calls;
- defines how human review will decide whether the signal matters.

### PR35: Live Output Hygiene Decision v0

Maps to: PRD R7, R10.

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

### PR36: Risk Mode Behavior Plan v0

Maps to: PRD R2, R7, R8, R11.

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

### PR37: First Calibrated Binary Judge Prototype

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
- a documented actionable-delta rubric;
- first adversarial pair fixtures;
- at least one small human-reviewed corpus batch beyond the six examples;
- a clear decision on live-output hygiene;
- a design note for user-values/priorities extraction;
- no unresolved confusion between deterministic run readiness and answer
  quality.

That is the smallest flywheel that can improve Lolla run by run without turning
it into a vague critic or overbuilt memory system.
