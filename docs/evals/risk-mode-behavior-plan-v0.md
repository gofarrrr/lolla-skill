# Risk Mode Behavior Plan v0

Status: decision/design-only
Date: 2026-06-28
Review slice: `risk_mode_behavior_plan_v0`

PR36 decides what Lolla should mean by risk-sensitive operation before changing
runtime behavior.

This is not an implementation PR. It does not run `$lolla`, call models, change
runtime behavior, change prompts, change `SKILL.md`, mutate archives, change
`evaluation.py`, change `agent_result.py`, change `archive_run.py`, relax
`caller_action`, add a judge, add answer-quality scoring, populate labels
automatically, or add crisis/domain protocols as runtime behavior.

The decision question is:

```text
What should Lolla do differently, if anything, when a run is high-stakes or
risk-sensitive?
```

## Decision

Keep the existing `risk_mode` enum:

- `quick`
- `standard`
- `deep`
- `high_stakes`
- `stability`

Do not introduce incompatible mode names in PR36.

Risk mode should be a custody, reliance, and review-strictness layer. It should
not decide answer quality, approve actions, or turn Lolla into a legal,
medical, financial, security, crisis, employment, or domain-specific authority.

Higher-risk modes should raise the burden for human reliance:

- stricter artifact sufficiency expectations;
- stronger uncertainty and boundary language in human review;
- more attention to stop rules, evidence gates, stakeholder impact, and
  domain-expert questions;
- more conservative `safe_for_agent_use` labels;
- no relaxation of `caller_action`;
- no automatic action approval.

Current implementation remains mostly metadata-first. `LOLLA_AUDIT_MODE`
normalizes and persists `risk_mode` into artifacts. The current
`agent_result.json` contract already treats otherwise clean `high_stakes` runs
conservatively by returning `caller_action: ask_user_first`; PR36 does not
change, expand, or relax that behavior. Prompts, cost, Step 7, capture
strictness, replay behavior, domain policy, and `SKILL.md` remain unchanged.

## Evidence From PR30-PR35

PR30-PR33 showed that saved answer-level review and deterministic run custody
must remain separate. A revised answer can improve action quality while still
requiring human reliance.

PR31 and PR32 made the improvement question more specific: did Lolla change
action, threshold, sequence, evidence gates, stop rules, written terms, scope,
or user questions?

PR34 showed that values, priorities, tradeoffs, obligations, and
non-negotiables need explicit review context before they are used to support
risk-sensitive action.

PR35 showed that live-output hygiene is also a reliance/custody question:
`live_output_health: not_checked` can coexist with a passing saved answer, but
it keeps clean product-surface claims and agent reliance conservative.

PR36 applies the same doctrine to risk mode. Risk does not make the answer good
or bad by itself. It changes what evidence and review are required before
someone should rely on the answer.

## Mode Meanings

The current mode names should keep these meanings until a later implementation
PR changes behavior:

| `risk_mode` | intended use | PR36 policy read |
|---|---|---|
| `quick` | Low-stakes exploratory check where cost and speed matter. | May support compact future behavior, but should not lower custody or product-surface honesty. |
| `standard` | Default serious conversation. | Baseline behavior and review expectations. |
| `deep` | User or caller explicitly wants deeper review. | Stronger review intent, not automatically higher stakes. Future behavior may add optional pressure checks or offline review only after tests. |
| `high_stakes` | Decisions with legal, medical, financial, safety, severe career/family, irreversible, or reputation-sensitive consequences. | Reliance must be conservative; answer-level pass is not action approval; clean artifacts alone should not produce automatic use. |
| `stability` | Evaluation/regression/replay intent. | Should focus on comparison and repeatability, not immediate action approval. |

`excluded_or_requires_domain_review` should not be added as a `risk_mode` value
in PR36. It is a review/routing conclusion that can apply to a run when the
domain or crisis context is outside normal Lolla reliance.

## Risk Domains

Reviewers should treat these domains as risk-sensitive even when `risk_mode` is
not explicitly `high_stakes`:

- medical / clinical;
- legal / regulatory;
- financial / investment / employment-compensation;
- safety / security;
- child / family / care;
- irreversible business decision;
- confidential / reputation-sensitive;
- self-harm or crisis, as out-of-scope/escalation rather than normal Lolla
  handling.

These domains do not make Lolla an authority. They tell reviewers that
ordinary answer polish, complete artifacts, or a strong memo are not enough for
agent reliance.

## What Risk Mode Affects

Answer-level review:

Risk mode does not decide whether the revised answer improved. Human reviewers
can still label a high-stakes answer as improved when it adds a real action
delta. Reviewers should, however, inspect whether the improvement includes
risk-appropriate uncertainty, stop rules, evidence gates, written terms,
domain-expert questions, and stakeholder-protection language.

Run-envelope / custody review:

Higher-risk modes raise the cost of missing or degraded artifacts. A
high-stakes run with clean saved artifacts can still be answer-reviewable, but
capture warnings, artifact gaps, provider-boundary issues, or live-output
caveats should keep reliance conservative.

Live-output hygiene:

For normal runs, `live_output_health: not_checked` is an honest caveat, not an
answer failure. For high-stakes or public product examples, `not_checked`
should be treated as a stronger reliance caveat. A run should not be called a
clean high-stakes product-surface example without trusted live-output evidence.

`safe_for_agent_use`:

Risk mode should push human labels toward conservatism. `high_stakes` usually
means `with_human_review` or `no`, not automatic `yes`. A `yes` label would
require explicit human/domain ratification and clean custody; PR36 does not
automate that pathway.

`caller_action` / caller readiness:

PR36 does not relax or change `caller_action`. Existing behavior remains:
degraded or unsafe runs should not be used; otherwise clean `high_stakes` runs
return the conservative caller hint `ask_user_first`. Any future caller-action
change requires a separate PR, tests, and contract documentation.

Human-review requirements:

High-stakes or risk-sensitive runs should require human review before agent
reliance. Some domains should require domain review, not merely Lolla review.
Self-harm or crisis content should route outside ordinary Lolla use.

Memo language:

Risk-sensitive memos should avoid domain assurance. They should name
uncertainty, decision gates, stop conditions, unresolved stakeholder questions,
and the limits of the audit. They should not say that Lolla has cleared a
legal, clinical, financial, security, or crisis action.

Artifact sufficiency:

For higher-risk reliance, required artifacts should include the normal custody
chain plus clean or explainable product-output health, capture adequacy, and
review-surface sufficiency. Missing `memo.md`, missing `revised.txt`, critical
capture, degraded product output, or unsafe live output should block reliance.

Future deeper-review triggers:

`deep` may later trigger optional review paths. `high_stakes` may later require
domain-boundary warnings, stricter artifact gates, or explicit human/domain
ratification. `stability` may later require repeated-run comparison. None of
that is implemented by PR36.

Future runtime behavior:

Runtime behavior should change only after fixtures, tests, cost/custody notes,
and contract docs exist. The default `standard` mode must remain stable.

## Decision Table

| case | condition | answer-level review | run envelope | `safe_for_agent_use` | caller action policy |
|---|---|---|---|---|---|
| A | `risk_mode: standard`; artifacts clean. | Can pass or fail on answer merits. | Clean if deterministic checks pass. | `yes` or `with_human_review` only by human label. | Existing policy. |
| B | `risk_mode: deep`; artifacts clean. | Can pass; reviewer checks whether deeper-review intent was actually satisfied. | Clean if deterministic checks pass; no implied Step 7 unless explicitly run. | No stronger than human label; often `with_human_review` until deeper path exists. | No relaxation. |
| C | `risk_mode: high_stakes`; artifacts clean. | Can pass. | Clean custody may still be inspect-first for reliance. | Usually `with_human_review` or `no`; domain review or explicit human ratification before action. | Do not relax because artifacts are clean; current contract uses `ask_user_first`. |
| D | `risk_mode: high_stakes`; saved artifacts clean; `live_output_health: not_checked`. | Can pass. | Warn / inspect first; not a clean product-surface example. | `with_human_review` or `no`; never automatic `yes`. | No relaxation. |
| E | `risk_mode: high_stakes`; artifact degradation, critical capture, or unsafe product/live output. | Usually not reliance-ready even if answer has useful ideas. | Degraded for reliance. | `no` unless a human/domain reviewer explicitly scopes limited use. | `do_not_use_run_degraded` or equivalent existing policy. |
| F | Excluded domain, crisis, or unsupported high-stakes situation. | Normal Lolla review is not enough. | Out of ordinary Lolla reliance. | `no` for autonomous agent use. | Use refusal/escalation/domain protocol outside Lolla; do not make Lolla the handler. |

## What Can Be Determined Today

Deterministically available today:

- selected `risk_mode` from `LOLLA_AUDIT_MODE`;
- whether the value is one of `quick`, `standard`, `deep`, `high_stakes`, or
  `stability`;
- artifact presence and schema health;
- capture adequacy status;
- product-output health;
- provider-boundary status;
- live-output health status;
- current `agent_result.json` `caller_action`;
- whether a control-plane sidecar supplied external risk metadata.

Not deterministically available today:

- whether conversation content belongs to a high-stakes domain when the caller
  did not label it;
- whether a domain expert has ratified the answer;
- whether a crisis protocol was followed;
- whether the revised answer is legally, clinically, financially, or
  operationally correct;
- whether a `deep` run actually deserves more reliance than a `standard` run;
- whether stability across runs means correctness.

These require human review, domain review, or later explicitly approved model
classification. They must not be inferred from smooth prose.

## What Remains Metadata-First For Now

PR36 does not change:

- extraction strictness;
- prompt text;
- model selection;
- cost policy;
- Step 7 pressure-check behavior;
- memo renderer behavior;
- live-output finalizer behavior;
- archive contents;
- evaluation scoring;
- `agent_result.json` schema;
- `caller_action` policy;
- Observatory behavior;
- `SKILL.md`.

Risk mode is now policy-designed, but most behavior remains unimplemented.

## Human Review Mapping

Human reviewers should use existing `lolla.human_review.v0` labels:

- `review_status` answers whether the reviewed surface passes;
- `primary_failure_mode` records the most material taxonomy issue;
- `severity` should rise when stakes make the failure reliance-relevant;
- `useful_friction` can be true when Lolla adds risk-appropriate gates;
- `noisy_friction` can be true when Lolla adds broad disclaimers without
  changing action;
- `missing_friction` can be true when high-stakes runs lack stop rules, expert
  questions, or evidence gates;
- `revised_answer_improved` remains about action-quality delta, not domain
  approval;
- `safe_for_agent_use` carries the reliance consequence.

For high-stakes or domain-sensitive runs, reviewer notes should name the mixed
surface plainly:

```text
Surfaces: answer=pass; custody=clean; risk=high_stakes; reliance=with_human_review.
```

## Drift Signals

Treat these as policy drift:

- saying `high_stakes` means Lolla validated a legal, medical, financial, or
  safety decision;
- treating `deep` as automatically better or more correct;
- treating `stability` as truth rather than repeatability evidence;
- letting clean artifacts override missing human/domain review;
- converting `safe_for_agent_use` to `yes` automatically;
- changing `caller_action` without a separate contract PR and tests;
- adding runtime model calls because a risk mode was selected, without cost and
  custody documentation;
- adding broad cautionary prose without action, threshold, stop-rule, or
  evidence-gate changes;
- using crisis or excluded-domain cases as ordinary Lolla success examples.

## Future Implementation Gates

A later implementation PR would need:

- fixtures covering `standard`, `deep`, `high_stakes`, `stability`, and
  excluded-domain reads;
- examples from PR30-PR33 where risk domains are visible in paraphrase-safe
  form;
- tests for current `high_stakes` `ask_user_first` behavior before changing
  anything;
- tests showing no behavior change in `standard`;
- explicit cost and latency expectations for any `deep` behavior;
- capture and live-output expectations for high-stakes reliance;
- `agent_result.json` and `evaluation.json` contract updates if policy fields
  or readiness outcomes change;
- Observatory copy only after the policy and enum mapping are stable;
- separate `SKILL.md` conductor-contract PR if live instructions change;
- separate caller-action PR if any new automatic action is proposed.

Do not enforce runtime behavior until those gates exist.

## What This Does And Does Not Justify

This does justify:

- using existing `risk_mode` names as the policy vocabulary;
- treating risk mode as review/reliance context;
- keeping `high_stakes` reliance conservative;
- requiring human or domain review before high-stakes agent use;
- using PR31 labels to inspect whether risk-sensitive friction changed action;
- building risk-mode fixtures before enforcement.

This does not justify:

- runtime behavior changes;
- prompt changes;
- `SKILL.md` changes;
- `evaluation.py`, `agent_result.py`, or `archive_run.py` changes;
- caller-action relaxation;
- domain assurance;
- crisis handling by Lolla;
- automatic domain classification;
- automatic `safe_for_agent_use`;
- answer-quality scoring;
- an LLM judge;
- graph DB, embeddings, chunking, memory, or specialist runtime integration.

## Recommended Next Slice

PR37 now creates the fixture matrix that this note recommended:

```text
docs/evals/risk-mode-fixture-matrix-v0.md
```

Why PR37 and not enforcement: PR36 defines the policy, but before runtime
enforcement or judge work, the project needs concrete paraphrase-only fixtures
that show how the same answer-level result should be treated differently under
`quick`, `standard`, `deep`, `high_stakes`, `stability`, and excluded-domain
review conditions. The fixtures test whether reviewers preserve the difference
between answer improvement, run readiness, and action approval.

The next slice should be:

```text
PR38 Risk Mode Fixture Review v0
```

That review should sanity-check the fixture expectations before any risk-mode
runtime behavior, caller-action change, or judge proposal.

## Review Receipt

- PR36 is docs/eval/design-only.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No risk-mode behavior implemented.
- No evaluation, archive, or agent-result code changed.
- No caller-action relaxation.
- No judge or answer-quality score added.
- No automatic labels added.
