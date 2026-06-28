# Current System Capabilities v0

Status: current-state explainer
Date: 2026-06-28

This note explains what Lolla can do now, what we have built around it, how the
pieces work together, and how the recorded cases show the system helping us.

It is a docs-only handoff. It does not run `$lolla`, call models, inspect raw
archive transcripts, mutate archives, change runtime behavior, change prompts,
change `SKILL.md`, add a judge, populate labels automatically, or approve
high-stakes use.

## Short Version

Lolla is now more than a one-off audit prompt. It is a local reasoning-audit
harness with:

- normal `$lolla` runs that produce revised answers and memos;
- archived run artifacts;
- deterministic run-readiness checks;
- machine-readable caller handoff;
- review-corpus export;
- human-owned review labels;
- actionable-delta rubric;
- fixture packs for future evaluation;
- risk-mode reliance visibility;
- read-only doctor/preflight checks for local wiring;
- human-owned user-values/priorities worksheet v0.

The key architecture is:

```text
probabilistic interpretation inside deterministic custody
```

LLMs are allowed to interpret messy conversation and generate audit pressure.
Deterministic code preserves artifacts, validates schemas, records health,
exports review data, and makes absence/presence visible. Human reviewers decide
whether the revised answer actually improved the decision.

## What The System Can Currently Do

### 1. Run A Reasoning Audit

For a serious conversation, normal `$lolla` can:

- capture the conversation;
- extract the decision situation, constraints, recommendation, and dropped
  threads;
- run the audit lanes;
- produce the strongest counterargument;
- write a revised answer;
- render a memo;
- archive the run.

This is still the main product surface.

### 2. Prove The Run Envelope Is Inspectable

The deterministic harness can now produce and check:

- `agent_result.json`;
- `evaluation.json`;
- `reasoning_trace.json`;
- `extraction_adequacy_report.json`;
- review-corpus JSONL and manifests;
- risk-mode reliance caveats;
- manifest-level counts for whether real high-stakes reliance evidence exists.
- `lolla.doctor_report.v0` preflight reports for local runtime/archive/provider
  wiring.

This layer does not judge advice quality. It answers:

```text
Did the run create the artifacts it claims, and can a reviewer inspect them?
```

The read-only doctor answers a separate pre-run question:

```text
Would a local run likely waste tokens because the environment is miswired?
```

It checks local paths, helper availability, provider/config presence, cost-table
visibility, optional manifest counts, output-path safety, runtime boundary
state, and privacy flags. It does not run `$lolla`, call models, read archive
payloads, mutate archives, approve high-stakes use, or judge answer quality.

### 3. Support Human/Product Review

Human review can now label whether a revised answer:

- passed answer-level review;
- added useful friction;
- avoided noisy friction;
- avoided missing friction;
- improved the decision surface;
- should remain `safe_for_agent_use: with_human_review` or lower;
- changed action, threshold, sequence, evidence gate, stop rule, written term,
  user question, scope, or overclaim.

The system validates and stores these labels, but it does not invent them.

### 4. Explain User Values And Priorities Without Automating Them

PR49 through PR54 built the user-values/priorities worksheet lane:

- worksheet plan;
- paraphrase-only fixtures;
- fixture review;
- blank deterministic worksheet helper;
- four human-filled worksheet pilots;
- pilot review / v0 decision.

The result is a human-owned review aid. It helps reviewers record values,
priorities, stakeholder obligations, tradeoffs, non-negotiables, and unresolved
conflicts. It does not extract values automatically, create memory, populate
labels, change runtime behavior, or approve agent reliance.

## Recorded Cases That Show What It Can Do

The system has a six-case complex baseline and a broader 14-record human-review
batch. The examples below use paraphrased review findings from those recorded
runs. They do not copy raw transcript, memo, revised-answer, model/provider, or
private-reasoning content.

| recorded case | run id | what Lolla changed | why it helps |
|---|---|---|---|
| `ceo-remove-founding-cofounder` | `20260627T093131Z_59d153` | Moved from a tidy reset conversation to real authority transfer, constrained transition terms, and stop-loss rules. | Shows Lolla can handle relationship pressure without preserving shadow authority. |
| `accept-operations-role-startup` | `20260627T132700Z_bae7f3` | Turned a resonant career choice into written operating-term tests and household-capacity evidence. | Shows Lolla can stop ambition/status language from overrunning spouse and family constraints. |
| `launch-public-enterprise-beta` | `20260627T104146Z_7bfe79` | Replaced marquee-customer aura with same-shape paid-pilot proof, procurement clarity, scope tolerance, and support-load gates. | Shows Lolla can turn status pressure into buyer-behavior evidence. |
| `pre-sell-undefined-consulting` | `20260627T133637Z_cad396` | Preserved one paid pilot while separating legitimate client-ready polish from premature scope expansion. | Shows useful friction is not always more skepticism; sometimes it retracts an overconfident psychological read. |
| `pivot-company-product-strategy` | `20260627T110450Z_5d2da7` | Put a 14-day capacity and obligation gate before a tempting higher-ACV market gate. | Shows Lolla can protect current customers and team capacity before market excitement takes over. |
| `deploy-assisted-intake-routing` | `20260627T130339Z_4cd3cb` | Compressed checklist theater into operable controls, a backlog diagnosis, and stop conditions. | Shows Lolla can make high-risk-like deployments more conservative without pretending to be a domain authority. |
| `implement-price-increase-three` | `20260627T083231Z_52724d` | Converted a broad price-increase question into account-level support economics and enforceable support boundaries. | Shows Lolla can distinguish pricing, support process, and customer-success problems. |
| `initiate-pre-sale-coffee-1` | `20260627T080708Z_1e8b85` | Converted brand-safe hesitation into a smaller cash-and-demand test with explicit stop-losses. | Shows Lolla can turn fuzzy launch anxiety into buyer-commitment evidence. |
| `launch-limited-beta-workflow` | `20260627T074306Z_7606f7` | Split launch into design-partner learning and a separate enterprise proof path. | Shows Lolla can find a safer third path instead of forcing launch-versus-delay. |

Across the 12 counted positive human-review records in PR33:

| signal | count |
|---|---:|
| `review_status: pass` | 12 |
| `revised_answer_improved: yes` | 12 |
| `useful_friction: present` | 12 |
| `safe_for_agent_use: with_human_review` | 12 |
| `evidence_gate_added` | 11 |
| `threshold_changed` | 10 |
| `scope_narrowed` | 8 |
| `written_term_added` | 7 |
| `action_changed` | 6 |
| `no_op_prose_change` | 0 |

That pattern is the important product signal. The revised answers were not only
longer or smoother. They repeatedly changed what a serious user would do next.

## How This Helps Us

### It Gives Us A Product-Taste Baseline

We now have concrete examples of what "better Lolla output" means:

- an action changed;
- a sequence changed;
- a threshold became explicit;
- a stop rule appeared;
- a written term was required;
- a scope got narrower;
- an overclaim was retracted.

That keeps future evaluation from drifting into generic helpfulness or
smoothness scoring.

### It Separates Run Health From Answer Quality

`evaluation.json` and run health tell us whether the run envelope is
inspectable. Human review tells us whether the revised answer helped.

This separation prevents a brittle mistake:

```text
clean artifacts = good advice
```

Clean artifacts only mean the run can be reviewed. They do not approve the
answer.

### It Makes Absence Visible

The review-corpus manifest now shows that the current real corpus has 80
records, all `risk_mode: standard`, and zero high-stakes
`risk_mode_reliance.present: true` records.

That helps us avoid overclaiming. We can say:

```text
We have fixtures and readiness gates for high-stakes behavior.
We do not yet have real high-stakes archive evidence.
```

### It Makes Values Reviewable Without Creating Memory

The user-values/priorities worksheet lets reviewers record things like family
capacity, stakeholder safety, customer trust, authority clarity, and unresolved
tradeoffs. But it keeps inferred values confirmation-needed and local to the
review.

That helps us study values without building a user-profile or memory product by
accident.

### It Gives Future Automation A Gate

The current artifacts can support future automation only when repeated human
review justifies it. A later narrow judge or heuristic must start from:

- named human-reviewed examples;
- a single binary failure mode;
- adversarial fixtures;
- measured false positives and false negatives;
- advisory use first.

That is how the system can improve without becoming a brittle judge.

## How It Works Inside The System

The current loop is:

```text
conversation
-> probabilistic extraction and audit pressure
-> revised answer and memo
-> deterministic archive and run-readiness artifacts
-> review-corpus export
-> human/product review
-> rubrics, fixtures, manifest counts, and future gates
```

The system roles are intentionally split:

| layer | allowed to do | not allowed to do |
|---|---|---|
| LLM audit | interpret conversation, challenge framing, revise answer | approve its own quality or act as final judge |
| deterministic harness | validate artifacts, schemas, custody, health, risk-mode fields, manifests | decide whether advice is wise |
| human review | decide useful friction, missing/noisy friction, values handling, safe-for-agent-use | silently become automatic labels |
| future automation | help only after repeated reviewed patterns | replace human/domain approval by default |

This is why the system is not a brittle deterministic evaluator of messy
output. Deterministic code checks what it can actually know. Human and
probabilistic layers handle semantic judgment with explicit custody and review
boundaries.

## What It Still Cannot Do

The system still cannot:

- automatically judge answer quality;
- automatically extract user values;
- approve high-stakes use;
- create real high-stakes evidence without explicit runs;
- act as a legal, medical, financial, safety, crisis, or domain expert;
- populate `safe_for_agent_use` automatically;
- replace human review;
- use `evaluation.json` as wisdom scoring;
- treat `caller_action: use_revised_answer` as human approval.

## Current Decision Point

The current safe state is:

```text
Use the harness and review artifacts as a stable evaluation baseline.
Do not add automation by default.
```

The next product decision should be explicit. Good candidates are:

- approve a real high-stakes evidence seed under the PR46/PR48 gates;
- expand human review toward the 50-100 record target;
- plan a narrow judge-calibration package from existing human labels;
- design trusted live-output hygiene implementation;
- pause and use the current system as the baseline before changing runtime.

The default should remain conservative: evidence first, automation later.
