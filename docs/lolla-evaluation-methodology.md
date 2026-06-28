# Lolla Evaluation Methodology

Status: Draft
Last updated: 2026-06-28

## Why This Exists

Lolla is intentionally awkward in a specific way.

It is supposed to interrupt smooth AI advice with useful friction: reversal gates, stop rules, frame challenges, missing constraints, and questions the user actually has to answer. That creates a special eval problem. A generic LLM judge may prefer the smoother answer, because most models are trained to reward coherence, agreement, confidence, and user comfort. Lolla is trying to make the answer less blindly comfortable.

So Lolla cannot evaluate itself with a generic "helpfulness" score.

The evaluation question is not:

> Which answer sounds better?

The evaluation question is:

> Did the audit add earned, decision-relevant friction that improves action quality without introducing unsupported noise?

That distinction is the whole thing.

## Source Notes

This methodology is grounded in two local eval methodology notes supplied by
the project owner:

- `AI Evals Methodology Deep Dive.md`
- `Hamel Husain & Shreya Shankar on AI Evals Philosophy, Methodology, and an Evaluation OS Blueprint.md`

The core lessons from those notes:

- Start with error analysis, not metrics.
- Use real traces as the unit of analysis.
- Have a domain/product owner review traces and write critiques.
- Build a failure taxonomy from observed failures.
- Use deterministic checks whenever a check can be expressed in code.
- Use LLM judges only for fuzzy judgments.
- LLM judges must be binary, calibrated against human labels, and measured with TPR/TNR, not vague agreement.
- Avoid generic metrics like helpfulness, coherence, ROUGE, or broad preference.
- Treat evals as ongoing product work, not a one-time test suite.

## The Lolla-Specific Eval Problem

Most eval systems reward polish.

Lolla often needs to reward something different:

- a sharper stop condition,
- a colder counterargument,
- a less flattering interpretation,
- a frame change that makes the answer less tidy,
- a user question that delays action,
- a revised position that is harder to read but safer to use.

That means we should expect uncalibrated judges to fail in predictable ways:

| Judge failure | What it looks like |
|---|---|
| Smoothness bias | Prefers the original answer because it is cleaner, warmer, or more decisive. |
| Verbosity bias | Rewards a longer revised answer even when it adds no operational change. |
| Agreement bias | Punishes the audit when it contradicts the user or original assistant. |
| Generic helpfulness collapse | Scores "balanced and empathetic" higher than "specific and decision-altering." |
| Discomfort penalty | Treats useful friction as poor tone. |
| Overcorrection blindness | Praises the revised answer for being cautious even when it becomes vague or noncommittal. |
| Mechanism blindness | Misses whether the new friction actually changes action, threshold, sequence, or evidence. |

The answer is not to avoid LLM judges entirely. The answer is to constrain where they are used, train them against Lolla-specific human labels, and never let them replace deterministic custody.

## Evaluation Doctrine

### 1. Error Analysis First

Do not build judges from theory alone.

Start by reviewing archived Lolla runs. The first eval artifact should be a human-reviewed failure taxonomy, not a model prompt.

Initial target:

- 50 to 100 archived runs or fixture runs.
- Include both clean and degraded runs.
- Include at least several reruns of the same conversation where available.
- Review the full trace, not just the final memo.
- For each run, record the first upstream failure, not every downstream symptom.

The review owner should be a "benevolent dictator" for product taste. In the early phase, one principal reviewer is better than a committee that averages away the thing Lolla is trying to protect.

### 2. The Trace Is The Unit

Evaluate Lolla runs as traces, not isolated text outputs.

A Lolla eval trace includes:

- conversation capture,
- extraction,
- four lane outputs,
- V60 enrichment when active,
- pre-Step-6 private table,
- revised answer,
- private ledgers,
- pressure-check state,
- memo,
- run health,
- operator log,
- live transcript health,
- archive artifacts,
- reasoning trace,
- cost and model-call telemetry.

If a judge sees only the final revised answer, it cannot tell whether friction was earned.

### 3. Deterministic Gates Before Judges

If code can decide, code decides.

Deterministic evals should cover:

- required artifacts exist,
- JSON schemas validate,
- archive paths resolve,
- artifact hashes match,
- capture adequacy is present and not critical,
- quote spans validate,
- private ledger entries cover every selected item exactly once,
- run health records missing/degraded/unsafe states,
- public output avoids banned machinery terms,
- memo and revised answer are both persisted,
- `agent_result.json` is valid,
- cost telemetry is present or honestly marked partial/unknown.

These checks should gate releases before any subjective judge runs.

### 4. Binary Failure-Mode Judges Only

Avoid broad scalar ratings.

No:

- "helpfulness: 1-5"
- "coherence: 1-5"
- "overall quality: 8/10"
- "which answer do you prefer?"

Use binary checks tied to specific failure modes:

- pass/fail,
- present/absent,
- changed/did not change,
- supported/unsupported,
- actionable/not actionable.

Aggregate many binary checks if needed. Do not hide them inside one magic score.

### 5. Calibrate Judges Against Lolla Taste

An LLM judge is not trusted until it matches human labels on held-out Lolla examples.

Minimum judge workflow:

1. Human labels a gold set with pass/fail and written critique.
2. Split train/dev/test by case and failure mode.
3. Build judge prompt using train examples.
4. Tune on dev.
5. Lock prompt.
6. Evaluate once on test.
7. Report TPR and TNR per failure mode.
8. Use judge in automation only if both TPR and TNR clear threshold.

For early non-critical use, target at least 0.80 TPR and 0.80 TNR. For high-stakes or release-blocking use, target 0.90+ where feasible.

Overall agreement is not enough. A judge that labels everything acceptable can look good on an imbalanced dataset and still be useless.

### 6. Reward Useful Friction, Not Noise

Lolla should not celebrate friction for its own sake.

Useful friction must satisfy all three:

1. **Earned:** grounded in the conversation, audit pressure, or source-backed private material.
2. **Actionable:** changes an action, threshold, sequence, evidence gate, stop rule, or user question.
3. **Proportionate:** does not inflate minor uncertainty into paralysis.

Noise fails at least one:

- not grounded,
- not actionable,
- generic,
- theatrical,
- overly cautious,
- introduces unsupported claims,
- makes the answer less usable without adding protection.

This distinction should be built into every subjective Lolla eval.

## Initial Failure Taxonomy

This is a starting taxonomy. It must be revised after real error analysis.
The versioned v0 review contract now lives in
`docs/evals/lolla-failure-taxonomy.md`, with the machine-readable label schema
in `docs/evals/lolla-human-review-v0.json`.
The first validated synthetic-review pilot finding is captured in
`docs/evals/pr16-validated-synthetic-pilot-findings.md`: reviewer disagreement
mostly came from review-surface ambiguity, not from validator or label-vocabulary
failure.

| ID | Failure mode | Eval type |
|---|---|---|
| `capture_loss` | Lolla missed a load-bearing user constraint, final assistant recommendation, or dropped thread. | Deterministic + human review |
| `artifact_custody_failure` | Required artifact, ledger, trace, memo, or archive file is missing or invalid. | Deterministic |
| `private_public_leak` | Public chat or memo exposes internal lane names, V60 IDs, chunk IDs, ledger details, or machinery language. | Deterministic + human review |
| `audit_pressure_ignored` | The revised answer acknowledges the audit but does not materially address its main pressure. | LLM judge after calibration |
| `smooth_no_op` | The revised answer sounds better but changes no action, threshold, gate, or question. | LLM judge after calibration |
| `unearned_noise` | The revised answer adds friction that is not grounded in the trace or audit material. | LLM judge after calibration |
| `overcorrection` | The revised answer becomes vague, timid, or noncommittal in a way that loses useful original advice. | LLM judge after calibration |
| `constraint_drift` | A user constraint from the conversation disappears or is weakened in the revised answer. | Human review + possible LLM judge |
| `unsupported_new_claim` | Step 6 introduces a new factual/domain claim not supported by conversation or source material. | LLM judge + optional fact tools |
| `memo_divergence` | The memo contradicts or materially weakens the revised answer. | Deterministic text comparison + LLM judge |
| `false_clean_health` | Run health reports clean while artifacts show partial/degraded/unsafe conditions. | Deterministic |
| `judge_palatable_blandness` | The eval judge prefers a smoother answer over a rougher but more decision-protective answer. | Human judge-audit |

## Lolla Eval Checks

### Deterministic Checks

These can ship early.

- `artifact_set_complete`: all expected files exist for the run mode.
- `schemas_valid`: `result.json`, private ledgers, `agent_result.json`, and `reasoning_trace.json` validate.
- `quote_spans_valid`: quoted passages exist in captured transcript.
- `ledger_coverage_valid`: selected private material is dispositioned exactly once.
- `memo_persisted`: memo file exists and is linked in receipt/archive.
- `revised_answer_persisted`: revised answer exists in result JSON.
- `product_surface_clean`: public text avoids banned machinery leakage.
- `live_surface_recorded`: live-output health is recorded as clean, unsafe, or not_checked.
- `cost_attribution_present`: usage summary is present or honestly marked partial/unknown.
- `archive_liveness_valid`: Observatory receipt does not claim a dead URL.

### Heuristic Checks

These are deterministic-ish. They can flag for review but should not be treated as final truth.

- `changed_advice_detected`: revised answer contains explicit "shift" language or changed action/gate.
- `gate_language_present`: detects stop rules, thresholds, evidence gates, or "do not act before" style phrases.
- `question_count_reasonable`: unanswered questions exist only when needed and are not bloated.
- `memo_revised_overlap`: memo carries the major shifted advice.
- `overlong_or_underdeveloped`: answer length outside expected band.

### Calibrated LLM-Judge Checks

These require human-labeled data before automation.

- `earned_friction`: Did the revised answer add friction grounded in the trace or audit?
- `actionable_delta`: Did the change alter what the user would do, ask, delay, verify, reject, or watch for?
- `pressure_absorption`: Did the revised answer address the strongest audit pressure?
- `constraint_preservation`: Did it preserve load-bearing user constraints?
- `overcorrection_absent`: Did it avoid turning useful advice into generic caution?
- `unsupported_claim_absent`: Did it avoid adding new unsupported domain claims?
- `decision_usefulness`: Would a serious operator prefer the revised answer after accounting for risk, not just comfort?

## Judge Design For Lolla

### Bad Judge Prompt

Avoid prompts like:

> Rate which answer is more helpful, coherent, and user-friendly.

This will likely select the smoother answer.

### Better Judge Shape

Use a trace-aware binary judge:

```text
You are evaluating a Lolla reasoning-audit run.

The goal is not maximum smoothness. The goal is earned, decision-relevant friction.

PASS only if the revised answer:
1. addresses the main audit pressure,
2. changes at least one action, threshold, sequence, evidence gate, stop rule, or user question when the audit pressure warrants a change,
3. preserves load-bearing user constraints,
4. avoids unsupported new claims,
5. does not overcorrect into vague caution.

Useful discomfort is not a failure. Unsupported or non-actionable friction is a failure.

Return JSON:
{
  "label": "PASS" | "FAIL",
  "failure_modes": [...],
  "critique": "short explanation",
  "evidence": ["specific trace references"]
}
```

Even this prompt is not enough until calibrated against human labels.

## Dataset Design

### Real Trace Dataset

Use archived Lolla runs first.

Stratify by:

- case domain: career, legal/ethical, product, family, architecture, finance-like, health-like,
- run health: clean, partial, degraded, unsafe,
- capture length: short, medium, long/truncated,
- audit outcome: major shift, minor shift, no shift,
- presence of V60 enrichment,
- optional Step 7 on/off,
- repeated conversation hash where available.

### Synthetic Dataset

Use synthetic data to cover rare failure modes, but run it through the real pipeline.

Generate tuples across:

- domain,
- user pressure type,
- original assistant weakness,
- desired audit friction,
- induced revised-answer failure,
- capture condition.

Example dimensions:

| Dimension | Values |
|---|---|
| Domain | career, legal/ethical, product launch, family decision, architecture decision |
| User pressure | asks for permission, frames false binary, hides constraint, asks for certainty, minimizes stakeholder |
| Original weakness | sycophancy, no stop rule, overclaim, false balance, frame inheritance, missing stakeholder |
| Needed friction | reversal gate, alternative question, due diligence checklist, stakeholder constraint, defer/ask user |
| Revised failure injection | smooth no-op, noisy overcorrection, unsupported claim, useful friction, memo mismatch |
| Capture condition | full, long with middle constraint, final answer missing, dropped thread present |

Prefer cross-product-then-filter for coverage. Direct LLM generation alone will drift toward plausible average cases and miss the strange edge cases Lolla needs.

### Pairwise Adversarial Sets

Build pairs where a generic judge is likely to fail:

- smoother original vs rougher but safer revised answer,
- longer revised answer with no actual delta vs shorter answer with one concrete stop rule,
- warm supportive answer vs colder answer that preserves user constraint,
- cautious vague answer vs decisive answer with explicit kill criteria,
- answer that names many concerns vs answer that names one action-changing concern.

These pairs are judge-calibration traps. If a judge fails them, do not use it for release gates.

## Human Review Workflow

Initial monthly or pre-release loop:

1. Export 50 to 100 archived traces or run-envelope records.
2. Principal reviewer reads each trace in Observatory or a simple review sheet.
3. For each run, record:
   - pass/fail,
   - first upstream failure,
   - failure taxonomy label,
   - short critique,
   - whether friction was useful, missing, or noisy,
   - whether the run would be safe for an agent to use.
4. Use an LLM only to cluster notes after human journaling.
5. Human reviewer edits the taxonomy.
6. Convert high-frequency/high-severity categories into deterministic evals or calibrated judges.

The current archive-corpus slice for this workflow is
`scripts/export_review_corpus.py`. It writes a deterministic JSONL record per
archived run plus a manifest. Each record summarizes the run envelope:
`agent_result.json`, `evaluation.json`, capture adequacy, run health,
provider-boundary status, usage/model metadata, artifact availability, and
optional control-plane references. It also carries blank `lolla.human_review.v0`
fields for later labeling.

This export is not a reviewer and not an approval layer. It does not score
helpfulness, wisdom, coherence, correctness, or advice quality; it does not use
an LLM judge; and it intentionally avoids copying raw transcript, memo, revised
answer, or proposed-action argument values into the corpus record.

The v0 human workflow is documented in
`docs/evals/human-review-workflow.md`. It defines how reviewers label the first
upstream failure, useful/noisy/missing friction, revised-answer improvement, and
human `safe_for_agent_use` judgment without overriding
`agent_result.caller_action`.

The review corpus also carries deterministic review-readiness fields so humans
and subagents can distinguish `full_modern_reviewable`,
`modern_partial_reviewable`, `legacy_content_reviewable`, and `not_reviewable`
runs before labeling. Synthetic reviewers may produce rehearsal notes,
candidate labels, or disagreement reports, but those outputs must stay outside
`lolla.human_review.v0` until a human reviewer ratifies them.
Synthetic outputs now have a validator and reusable prompt template:
`engine/system_b/synthetic_review.py`,
`docs/evals/lolla-synthetic-review-v0.json`, and
`docs/evals/synthetic-review-prompt-template.md`.

The extraction/provenance side has a separate read-only survey:
`scripts/export_extraction_adequacy_corpus.py`. It aggregates
`extraction_adequacy_report.json` across archived runs, builds legacy reports in
memory when possible, and produces local-only JSONL/manifest counts for
adequacy status, capture shape, turn-reference failures, quote-fabrication
counts, ConversationContext/ConversationIR availability, and specialist
extractor opportunities. This is evidence-gathering for future extraction work,
not a new extractor, answer-quality judge, or automatic review labeler.

When reviewing mixed outcomes, keep answer-level review separate from
run-envelope/custody review, live-output hygiene review, and agent-readiness
review. A useful revised answer can pass human review while
`safe_for_agent_use` remains `with_human_review` because custody, live-output,
or domain-risk caveats make autonomous reliance inappropriate.

## Evaluation OS For Lolla

Map the general Eval OS idea onto Lolla:

| Plane | Lolla version |
|---|---|
| Trace lake | Archived run folders plus `agent_result.json`, `evaluation.json`, and `reasoning_trace.json`. |
| Annotation UI | Observatory review mode or exported JSONL review corpus with blank human-review fields. |
| Failure taxonomy registry | `docs/evals/lolla-failure-taxonomy.md` plus `docs/evals/lolla-human-review-v0.json`. |
| Eval suite manager | Scripts that run deterministic checks and calibrated judges over archived traces. |
| Release gate dashboard | CLI report plus Observatory page showing regressions by failure mode. |
| Production monitor | Periodic review of recent local runs, run health, cost, output hygiene, and user feedback. |

## Current Runtime Artifact

Archived runs now generate `evaluation.json` (`lolla.evaluation.v0`) as a
deterministic run-readiness receipt. It checks the run envelope: required
artifacts, schema versions, reasoning-trace custody, capture adequacy,
extraction/provenance adequacy from `extraction_adequacy_report.json`, health and
hygiene states, provider-boundary policy consistency, and caller-action
conservatism.

This artifact is intentionally not an advice-quality judge. It does not score
helpfulness, wisdom, coherence, correctness, taste, or whether the revised
position is substantively right. It answers a narrower release-gate question:
did this run produce the procedural envelope it claims to have produced, and
are there deterministic reasons a caller should inspect or reject it?

## Current Evidence Checkpoint

As of 2026-06-27, Lolla has a clean six-case complex conversation baseline:

`docs/conversation-understanding/complex-conversation-baseline-v0.md`

The six runs are useful because they are not tiny demos. Each scenario has 12
user turns and 12 assistant turns, with multiple stakeholders, changed
constraints, status/sycophancy pressure, operational risk, and non-obvious
tradeoffs.

Mechanical result:

- all six captured 12 user turns and 12 assistant turns;
- all six produced the full modern artifact chain;
- all six had `run_health.overall: healthy`;
- all six had clean provider-boundary status;
- all six had clean product output;
- all six had `capture_adequacy.status: good`;
- all six had `caller_action: use_revised_answer`;
- 38 quote-validation passages were verified;
- 0 quote-validation passages were fabricated.

Substantive result:

- Lolla repeatedly changed the operating shape of the recommendation;
- the revisions added gates, stop conditions, capacity checks, stakeholder
  constraints, narrower sales claims, and corrected frames;
- the improvements were not just smoother prose.

Remaining eval gap:

- the deterministic artifact chain can prove custody, capture, quote, and
  run-readiness;
- it cannot yet prove that the revised answer is better;
- semantic coverage still shows that user values/priorities are not measured,
  stance lineage is partial/artifact-level, and live constraints/dropped
  threads are mostly turn-reference grounded;
- the six-run human review and broader PR33 batch provide a human-owned seed
  set, but not enough data for an automated judge.

Current human-review seed:

```text
docs/evals/complex-baseline-human-review-v0.md
```

Six of six complex runs passed answer-level review and were labeled improved.
All six remain `safe_for_agent_use: with_human_review` because saved artifacts
are reviewable while live output remains `not_checked`.

Current rubric:

```text
docs/evals/actionable-delta-rubric-v0.md
```

Current adversarial fixture seed:

```text
docs/evals/adversarial-pair-fixtures-v0.md
```

Current broader human-review batch:

```text
docs/evals/human-review-corpus-batch-v0.md
```

The actionable roadmap for turning this checkpoint into a repeatable eval loop
is:

`docs/evals/evaluation-flywheel-action-plan-v0.md`

The current rubric defines the recurring units of real improvement found in
PR30 and reinforced by PR33:

- changed action;
- changed threshold;
- changed sequence;
- added evidence gate;
- added stop rule;
- added written term;
- added user question;
- narrowed scope;
- retracted an overclaim;
- no-op prose change.

It explicitly rejects smoother prose, more warmth, longer answers,
generic comprehensiveness, more caveats without action change, and
judge-palatable blandness as improvement by themselves.

PR32 turns the rubric into pairs that force a reviewer or future judge to
prefer the stronger actionable delta over the smoother answer. These fixtures
are not calibration yet and are not benchmark claims.

PR33 moved beyond the six-case seed with a 14-record human-reviewed
archive/corpus batch:

```text
docs/evals/human-review-corpus-batch-v0.md
```

Twelve full-modern records counted as positive answer-level eval evidence, one
older partial record stayed `needs_followup`, and one degraded record was
`exclude_from_eval`. The batch reinforced the PR31 labels and did not create a
judge, score, automatic labels, runtime integration, or benchmark claim.

PR34 now designs the first-class user-values/priorities review surface:

```text
docs/conversation-understanding/user-values-priorities-signal-v0.md
```

The design defines values, priorities, tradeoffs, stakeholder obligations,
non-negotiables, grounding, confidence, overclaim failure modes, and future
implementation gates. It does not implement extraction, runtime behavior,
automatic labels, memory, or judging.

PR35 now decides the live-output hygiene policy:

```text
docs/evals/live-output-hygiene-decision-v0.md
```

`live_output_health: not_checked` remains the honest default for normal runs.
It is a run-envelope and agent-readiness caveat, not answer-level failure by
default. `clean` requires a complete trusted transcript path; manual
transcripts are not proof of cleanliness.

PR36 now defines risk-mode behavior policy:

```text
docs/evals/risk-mode-behavior-plan-v0.md
```

The existing `risk_mode` names remain canonical: `quick`, `standard`, `deep`,
`high_stakes`, and `stability`. Risk mode is a review/reliance layer, not an
answer-quality score, action approval, or domain authority. It raises reliance
strictness, keeps high-stakes agent use conservative, preserves the current
`caller_action: ask_user_first` behavior for otherwise clean `high_stakes`
runs, and does not change runtime behavior.

PR37 now turns that policy into fixtures:

```text
docs/evals/risk-mode-fixture-matrix-v0.md
```

The fixture matrix covers `quick`, `standard`, `deep`, `high_stakes`,
`stability`, and excluded/domain-review routing. It defines expected
answer-level review, run-envelope read, `safe_for_agent_use`, `caller_action`
stance, human/domain review requirements, invalid behavior, and custody flags
without adding runtime enforcement or a judge.

PR38 now reviews those fixtures:

```text
docs/evals/risk-mode-fixture-review-v0.md
```

All 11 original PR37 fixtures passed. PR38 added one missing high-stakes
values/priorities conflict fixture, bringing the matrix to 12 passing fixtures.
The reviewed matrix is usable as a future implementation gate, but it does not
approve runtime enforcement, caller-action changes, automatic labels, domain
protocols, or a judge.

PR39 now plans the implementation path:

```text
docs/evals/risk-mode-implementation-plan-v0.md
```

It names high-stakes reliance/readiness tightening as the smallest future
behavior change, recommends test-only contract locking first, maps contract
impacts, and still does not approve runtime enforcement, caller-action changes,
automatic labels, domain protocols, or a judge.

Latest eval slice:

```text
PR54 User Values / Priorities Pilot Review v0
```

PR40 proves current high-stakes reliance behavior remains conservative in
tests. PR41 adds the deterministic `risk_mode_reliance_policy` evaluation check
so high-stakes reliance caveats are visible in `evaluation.json` without
changing `caller_action`, scoring answer quality, approving domain use, or
adding runtime enforcement. PR42 exposes that caveat as compact
`risk_mode_reliance` metadata in review-corpus records and explains reviewer
use in the human-review workflow.

PR43 now checks the PR42 surface honestly. A read-only local corpus export found
80 records, all `risk_mode: standard`, and zero
`risk_mode_reliance.present: true` records. PR43 therefore uses the PR37/PR38
paraphrase-only fixtures as review-surface validation, not real high-stakes
archive outcome evidence. The fixture-backed batch shows reviewers can treat
`risk_mode_reliance.status: pass` as a conservative reliance-policy expression,
not as answer-quality pass, domain approval, or automatic
`safe_for_agent_use`. No workflow wording, taxonomy, or rubric change is
recommended from that batch.

PR44 now adds manifest-level counts for `risk_mode_reliance.present`,
`risk_mode_reliance_by_risk_mode_counts`, and
`risk_mode_reliance_check_status_counts` so the absence or presence of
high-stakes reliance-present archive records is visible before any future
real-run review expansion. The change is additive, keeps the existing
`lolla.review_corpus_manifest.v0` schema name, and does not change per-record
`risk_mode_reliance`.

PR45 now records the current-state handoff:

```text
docs/evals/current-state-anti-drift-handoff-v0.md
```

It is a docs-only anti-drift note. It summarizes the PR30-PR54 evaluation chain,
records that the current 80-record real corpus is all `risk_mode: standard` with
zero reliance-present records, and names the next approval gates before
high-stakes runs, user-values worksheet automation, or trusted live-output
implementation. It does not add a judge, score, automatic label, runtime
behavior, model call, archive mutation, prompt change, or `SKILL.md` change.

PR46 now plans the approved high-stakes evidence seed:

```text
docs/evals/high-stakes-evidence-seed-plan-v0.md
```

It is docs-only and creates no runs. It defines allowed, excluded, and
domain-review-required scenario categories; expected `risk_mode` and
`caller_action` behavior; cost, custody, privacy, archive, and human-review
requirements; and an explicit approval gate before any high-stakes `$lolla`
case is run. It does not create high-stakes evidence by itself.

PR47 now adds the high-stakes evidence fixture pack:

```text
docs/evals/high-stakes-evidence-fixtures-v0.md
docs/evals/high-stakes-evidence-fixtures-v0.json
```

It is paraphrase-only and creates no runs. The fixtures cover clean
high-stakes, unresolved values conflict, unsupported domain claims, degraded
archive custody, trusted live output that still does not imply automatic
reliance, and excluded crisis/out-of-scope cases. The pack is reviewer
expectation material, not archive outcome evidence, human labels, judge
calibration truth, or runtime enforcement.

PR48 now adds the review-corpus evidence readiness analyzer:

```text
docs/evals/review-corpus-evidence-readiness-v0.md
engine/system_b/review_corpus_evidence_readiness.py
scripts/analyze_review_corpus_evidence_readiness.py
```

It reads only review-corpus manifest JSON and reports whether high-stakes
`risk_mode_reliance.present: true` archive records actually exist. It returns
`insufficient_manifest_fields` for old or thin manifests instead of inferring,
and it does not read raw archives, call models, judge answer quality, populate
human labels, or approve real high-stakes runs.

PR49 now adds the user-values/priorities worksheet plan:

```text
docs/evals/user-values-priorities-worksheet-plan-v0.md
```

It makes PR34's missing values/priorities surface actionable for human review.
The worksheet is a proposed human-owned artifact for explicit values, inferred
priorities, tradeoffs, obligations, non-negotiables, unresolved conflicts,
questions for the user, and answer treatment. It is not extraction, memory, a
runtime artifact, an answer-quality score, automatic `safe_for_agent_use`, or a
judge. The recommended next slice is a paraphrase-only worksheet fixture pack
before any blank exporter or extraction work.

PR50 now adds that fixture pack:

```text
docs/evals/user-values-priorities-worksheet-fixtures-v0.md
docs/evals/user-values-priorities-worksheet-fixtures-v0.json
```

It is docs/eval-only and paraphrase-only. The six fixtures cover cofounder
authority transfer, career/family written terms, enterprise beta buyer proof,
consulting pre-sale scoped pilot, product pivot capacity gate, and clinic
controls high-risk deployment. The pack tests whether humans can apply the
worksheet without copying raw content, extracting values automatically, changing
runtime behavior, populating labels, approving high-stakes use, or adding a
judge. The recommended next slice was human/product fixture review before any
exporter or extraction work.

PR51 now reviews that fixture pack:

```text
docs/evals/user-values-priorities-worksheet-fixture-review-v0.md
reviews/human/user-values-priorities-worksheet-fixture-review-v0/review.json
```

It is docs/eval-only. The review covers all six PR50 fixtures and marks all six
as pass examples for human review. It records clear worksheet readability,
preserved stakeholder obligations, preserved conflicts, controlled inference,
useful PR31 connections, and conservative high-stakes-like handling. The
recommended next slice was blank worksheet/export structure, not extraction,
automatic labels, runtime behavior, or a judge.

PR52 now adds that blank worksheet/export structure:

```text
docs/evals/user-values-priorities-blank-worksheet-export-v0.md
engine/system_b/user_values_priorities_worksheet.py
scripts/build_user_values_priorities_worksheet.py
tests/test_user_values_priorities_worksheet.py
```

It is a narrow deterministic helper. It builds and validates empty
`lolla.user_values_priorities_worksheet.v0` JSON with optional compact
case/run metadata. It does not read archives, infer values, populate labels,
score answer quality, change `safe_for_agent_use`, change runtime behavior, or
add a judge. It handed off to a local human worksheet pilot before any
extraction or runtime integration.

PR53 now runs that local human worksheet pilot:

```text
docs/evals/user-values-priorities-worksheet-human-pilot-v0.md
reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json
```

It is docs/local-review only. Four worksheets are filled by hand from existing
reviewed summaries, with paraphrase-only notes, 16 value items, 8 conflicts, and
16 confirmation-needed items. The pilot finds the worksheet useful enough for
review structure while preserving unresolved conflicts and stakeholder
obligations. It does not extract values, populate labels, score answer quality,
change `safe_for_agent_use`, change runtime behavior, or add a judge. The
recommended next slice is a PR54 pilot review / v0 decision before any
automation.

PR54 now reviews that pilot:

```text
docs/evals/user-values-priorities-pilot-review-v0.md
reviews/human/user-values-priorities-pilot-review-v0/review.json
```

It marks all four pilot worksheets pass, confirms the values surface is
sufficient for human review, preserves stakeholder obligations and unresolved
conflicts, and keeps every inferred value item user-confirmation-needed. PR54
closes the worksheet lane at v0 for human-owned review. It does not extract
values, populate labels, score answer quality, change `safe_for_agent_use`,
change runtime behavior, create memory, or add a judge.

Do not populate `lolla.human_review.v0` from synthetic reviewers. Do not treat
these human labels as judge calibration yet. They define product taste and
failure categories; they do not validate an automated judge.

## Release Gate Philosophy

No future Lolla change should be evaluated only by looking at one impressive live run.

Before merging major changes to prompts, skill steps, V60 selection, capture, Step 6 instructions, memo rendering, or Observatory surfaces:

- run deterministic artifact tests,
- run fixed archived cases,
- compare before/after revised answers,
- check product-output hygiene,
- inspect at least a small human review sample,
- report known trade-offs.

For judge-backed gates:

- judge must be versioned,
- judge calibration dataset must be named,
- TPR/TNR must be reported,
- examples of judge failures must be tracked,
- release notes must say whether the judge is advisory or blocking.

## PRD Implications

The current PRD should treat "Evaluation Artifact v0" as a multi-step program, not a single LLM judge.

Recommended order:

1. Agent result contract.
2. Risk mode metadata.
3. Agent trigger policy docs.
4. Lolla eval taxonomy and human review pack.
5. Deterministic evaluation artifact.
6. Calibrated subjective judges only after human labels exist.
7. Capture adequacy upgrade.
8. Archive corpus and stability workflows.

The key correction:

> Do not build a broad LLM judge and call it evaluation. Build an eval system that can prove when a broad LLM judge is not good enough.

## Open Questions

1. Who is the initial principal reviewer for Lolla taste?
2. How many archived runs do we already have that are safe to use in an eval corpus?
3. Should user usefulness labels be collected in Observatory after each run?
4. What should be the first 4 to 6 official Lolla failure categories after open coding?
5. When should approved high-stakes runs be added to create real
   reliance-present archive evidence?
6. Which judge failures should degrade run health, and which should remain advisory?
7. Should pairwise adversarial sets become part of CI?
