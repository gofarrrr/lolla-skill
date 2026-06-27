# Actionable Delta Rubric v0

Status: human-owned rubric seed
Date: 2026-06-27
Review slice: `actionable_delta_rubric_v0`

This note defines what counts as a real Lolla improvement after PR30's
six-run human/product review seed.

The purpose is narrow. PR31 does not judge new runs, implement a model judge,
change runtime behavior, change prompts, change `SKILL.md`, run `$lolla`, call
models, or automatically populate human-review labels. It gives reviewers a
shared language for explaining why a revised answer improved, failed, or merely
became nicer prose.

The central question:

```text
Did the revised answer change what the user should do, verify, ask, delay,
bound, stop, or write down?
```

If the answer is no, the revision may be better written, but it has not yet
shown a Lolla-specific actionable delta.

## Source Set

This rubric is grounded in PR30:

- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- `reviews/human/complex-baseline-v0/review.json`
- [Complex Conversation Baseline v0](../conversation-understanding/complex-conversation-baseline-v0.md)

PR30 reviewed six complex runs:

| case id | PR30 action-changing delta |
|---|---|
| `ceo-remove-founding-cofounder` | Authority moves before cooperation is tested; transition role becomes conditional and bounded. |
| `accept-operations-role-startup` | Both paths must produce written operating terms under deadline before the user chooses. |
| `launch-public-enterprise-beta` | Both prospects get the same written paid pilot shape; priority is earned by buyer behavior. |
| `pre-sell-undefined-consulting` | One paid pilot remains, but the scope becomes client-ready and polish is tightly bounded. |
| `pivot-company-product-strategy` | Capacity and current obligations must pass before market validation consumes the company. |
| `deploy-assisted-intake-routing` | The launch becomes four must-pass controls plus diagnosis and pause/rollback triggers. |

All six PR30 answer-level reviews passed and were labeled improved. All six
remain `safe_for_agent_use: with_human_review` because saved artifacts are
reviewable while `live_output_health` remains `not_checked`.

## Boundary

This rubric is not:

- a generic helpfulness score;
- an answer-quality score;
- a calibrated judge;
- an approval system;
- an automatic labeler;
- a replacement for `lolla.human_review.v0`;
- evidence that `evaluation.json` scores answer wisdom;
- evidence that `caller_action: use_revised_answer` is human approval.

This rubric is:

- a human reviewer aid;
- a language for PR30's recurring action-changing deltas;
- a filter against smooth no-op improvements;
- preparation for PR32 adversarial pair fixtures;
- a future calibration target if, and only if, enough human labels exist.

## How To Use This Rubric

Reviewers should first decide whether the revised answer has at least one
actionable delta. A revision can carry several labels. For example, the clinic
case has `scope_narrowed`, `threshold_changed`, `evidence_gate_added`, and
`stop_rule_added`.

Use the labels only when the delta is visible in the saved artifacts. The usual
supporting artifacts are:

- `conversation.txt` for the user's decision context and constraints;
- `extraction.json` for captured decision structure;
- `revised.txt` for the revised recommendation;
- `memo.md` for the product-facing rationale;
- `agent_result.json` for compact changed-advice summaries;
- `evaluation.json` for run-envelope caveats only;
- `extraction_adequacy_report.json` and `reasoning_trace.json` for custody and
  adequacy context.

Do not use `evaluation.json` as evidence that the advice is wise. It can say
whether the run envelope is ready enough to inspect; it cannot say whether the
answer-level delta is good.

## Improvement Standard

A real Lolla improvement changes at least one of these:

- what the user should do;
- what must happen before the user commits;
- what order actions should happen in;
- what proof is required;
- when the plan should stop or reverse;
- what agreement must become explicit;
- what question only the user or stakeholder can answer;
- what scope is honest enough to operate;
- what earlier overclaim should be retracted.

The following are not improvement by themselves:

- warmer prose;
- longer answer;
- smoother transitions;
- more balanced tone;
- more confident language;
- generic comprehensiveness;
- more caveats without action change;
- judge-palatable blandness.

If a revision sounds more polished but leaves action, evidence, sequence,
threshold, scope, and risk handling unchanged, label it `no_op_prose_change`.

## Useful, Noisy, And Missing Friction

Useful friction is pressure that is earned by the trace and changes an action,
threshold, sequence, evidence requirement, stop rule, written term, scope, or
user question. It makes the decision harder to trust blindly in a way the user
can act on.

Noisy friction is pressure that sounds critical but is not well supported by
the trace, inflates process burden, adds generic caveats, introduces
unsupported claims, or overreads motives/status psychology without changing a
better action. The consulting case is a useful warning: the PR30 revision
passed partly because it retracted an overconfident status read instead of
doubling down on it.

Missing friction is a trace-supported pressure that should have changed action
but did not appear in the revised answer. In PR30, no material missing friction
was found at answer level, but future reviewers should watch for ignored
capacity constraints, stakeholder obligations, untested buyer proof, authority
ambiguity, and operational rollback gaps.

## Labels

### `action_changed`

Definition: The revised answer would make the user do something materially
different from the original answer, not merely feel differently about the same
plan.

Positive PR30 examples:

- `ceo-remove-founding-cofounder`: move authority before testing cooperation.
- `accept-operations-role-startup`: require concrete terms from both options
  before choosing.
- `launch-public-enterprise-beta`: assign prospect priority by buyer behavior
  rather than by prospect size.

Negative or no-op example: "Have a clearer conversation with the cofounder" is
not enough if the authority structure and next action remain unchanged.

Evidence should show: original action shape, revised action shape, and the
artifact-supported reason the revised action is different.

Invalid if: the change is only emotional framing, confidence level, prose
organization, or a different explanation for the same next step.

### `threshold_changed`

Definition: The revised answer adds or changes a concrete gate, deadline,
metric, condition, minimum proof level, or acceptance criterion.

Positive PR30 examples:

- `accept-operations-role-startup`: current-role and startup options both need
  written terms under explicit near-term deadlines.
- `pivot-company-product-strategy`: a 14-day capacity and obligation gate must
  pass before the market gate.
- `deploy-assisted-intake-routing`: a 48-hour backlog diagnosis becomes a
  launch prerequisite.

Negative or no-op example: "Be careful before committing" is not a threshold
unless it says what must be true, by when, and what happens if it is not true.

Evidence should show: the threshold text in `revised.txt` or `memo.md`, plus
the user constraint or audit pressure that made the threshold relevant.

Invalid if: the threshold is vague, decorative, impossible to observe, or not
tied to a decision.

### `sequence_changed`

Definition: The revised answer changes what must happen first, second, or only
after another condition is met.

Positive PR30 examples:

- `pivot-company-product-strategy`: capacity and obligations come before market
  validation.
- `ceo-remove-founding-cofounder`: authority moves before a transition role is
  tested.
- `deploy-assisted-intake-routing`: diagnosis and must-pass controls precede a
  broader AI deployment claim.

Negative or no-op example: Reordering paragraphs is not a sequence change if
the user would still execute the same actions in the same order.

Evidence should show: a before/after order of operations, with a reason the
new order protects the decision.

Invalid if: the sequence is inferred only from prose order and not from an
explicit dependency, prerequisite, or timing instruction.

### `evidence_gate_added`

Definition: The revised answer requires proof before commitment, expansion,
selection, or public claim.

Positive PR30 examples:

- `launch-public-enterprise-beta`: both prospects must accept the same paid
  pilot shape, and priority is based on payment/procurement/scope evidence.
- `pivot-company-product-strategy`: market validation waits until capacity and
  obligation evidence is gathered.
- `deploy-assisted-intake-routing`: backlog diagnosis must show whether an AI
  pilot addresses the actual bottleneck.

Negative or no-op example: "Validate the idea" is not an evidence gate unless
it names the proof source and what decision the proof controls.

Evidence should show: proof required, proof source, and the action that depends
on the proof.

Invalid if: the evidence requirement is generic diligence, optional research,
or a fact-finding task that does not change commitment.

### `stop_rule_added`

Definition: The revised answer defines when to pause, reverse, kill, rollback,
or refuse to continue.

Positive PR30 examples:

- `ceo-remove-founding-cofounder`: transition is bounded by explicit stop-loss
  rules.
- `launch-public-enterprise-beta`: gates become owner-threshold-stop tripwires.
- `deploy-assisted-intake-routing`: launch controls include pause/rollback
  triggers.

Negative or no-op example: "Monitor risk" is not a stop rule unless it says
which condition stops the plan and what the user should do next.

Evidence should show: the stopping condition, the protected risk, and the
action after the condition fires.

Invalid if: the stop rule is not observable, not connected to a risk in the
trace, or so broad that it could justify any choice.

### `written_term_added`

Definition: The revised answer turns vague alignment, trust, ambition, or
verbal agreement into written operating terms, scope, ownership, payment, or
acceptance criteria.

Positive PR30 examples:

- `accept-operations-role-startup`: both career paths must produce written
  operating terms.
- `launch-public-enterprise-beta`: both prospects get the same written paid
  pilot shape.
- `pre-sell-undefined-consulting`: the pilot becomes a client-ready scoped
  brief, with polish constrained to support rather than define the offer.
- `pivot-company-product-strategy`: nonprofit obligations become a staffed,
  date-bounded maintenance promise.

Negative or no-op example: "Make sure everyone is aligned" is not a written
term unless it specifies what must be written down and who must accept it.

Evidence should show: the written object, the parties or owner, and the
decision risk the written term reduces.

Invalid if: the term is bureaucratic theater, unrelated to the core decision,
or a document request with no effect on action.

### `user_question_added`

Definition: The revised answer surfaces a question only the user or a named
stakeholder can answer, and the answer to that question changes the decision.

Positive PR30 examples:

- `accept-operations-role-startup`: can each option produce real operating
  authority and household capacity evidence under deadline?
- `launch-public-enterprise-beta`: which buyer will accept paid pilot terms and
  procurement clarity rather than just signal interest?
- `deploy-assisted-intake-routing`: is the backlog actually an AI-routing
  problem or a simpler operational bottleneck?

Negative or no-op example: "Ask more questions" is not enough if the questions
do not control a choice, gate, sequence, or stop rule.

Evidence should show: the stakeholder-answerable question and how its answer
changes the recommended action.

Invalid if: the question is rhetorical, generic, answerable from public facts,
or not tied to the user's decision.

### `scope_narrowed`

Definition: The revised answer narrows ambition, audience, launch shape, offer,
or operational burden to a safer and more honest path.

Positive PR30 examples:

- `pre-sell-undefined-consulting`: keep one paid pilot and limit agency polish
  to a tiny support role.
- `deploy-assisted-intake-routing`: replace broad AI launch language with a
  narrow operational pilot and four controls.
- `launch-public-enterprise-beta`: move from public enterprise posture toward
  private paid proof.

Negative or no-op example: A shorter answer is not a narrower scope. The scope
must change what the user will attempt, promise, sell, launch, or support.

Evidence should show: the original broader scope, revised narrower scope, and
the risk or constraint that makes narrowing useful.

Invalid if: narrowing becomes timidity, removes the useful core of the
original advice, or avoids the hard decision without creating a better one.

### `overclaim_retracted`

Definition: The revised answer takes back a too-clean psychological,
strategic, causal, or status-based read and replaces it with a more precise
operating distinction.

Positive PR30 examples:

- `pre-sell-undefined-consulting`: professional polish is not dismissed as pure
  status spending; a small credibility surface can be legitimate.
- `accept-operations-role-startup`: startup title and current-company safety
  are both denied automatic evidentiary weight.
- `launch-public-enterprise-beta`: the larger prospect is no longer treated as
  the default better buyer by aura.

Negative or no-op example: Softening a claim with "maybe" is not a retraction
unless the revised answer changes what the user should infer or do.

Evidence should show: the overclaim or over-clean read, the replacement
distinction, and the action consequence.

Invalid if: the revised answer retracts a grounded warning merely to sound
fair, or if the supposed overclaim cannot be located in the original/revision
comparison.

### `no_op_prose_change`

Definition: The revised answer sounds warmer, smoother, longer, more balanced,
or more comprehensive but does not change action, threshold, sequence,
evidence, stop rule, written term, user question, scope, or overclaim handling.

Positive examples of this label, framed as PR30-derived fixture candidates:

- `ceo-remove-founding-cofounder`: a smoother version that urges a thoughtful
  reset conversation but leaves authority and transition rights unchanged.
- `deploy-assisted-intake-routing`: a longer safety checklist that looks
  responsible but does not create operable controls, diagnosis, or rollback
  triggers.
- `accept-operations-role-startup`: more resonant language about identity and
  aliveness that does not require written operating terms from either option.

Negative PR30 examples: all six PR30 revised answers were labeled improved
because each changed action, threshold, sequence, proof, scope, or written
terms. They are not `no_op_prose_change` examples.

Evidence should show: absence of material delta after comparing original
answer, revised answer, memo, and changed-advice summary.

Invalid if: the revision contains any supported action-changing delta. A
revision can be stylistically smoother and still be real improvement if it
changes a decision-relevant unit.

## Combining Labels

Most useful improvements carry more than one label:

| case id | likely PR31 labels |
|---|---|
| `ceo-remove-founding-cofounder` | `action_changed`, `sequence_changed`, `stop_rule_added`, `scope_narrowed` |
| `accept-operations-role-startup` | `threshold_changed`, `written_term_added`, `user_question_added`, `overclaim_retracted` |
| `launch-public-enterprise-beta` | `action_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed`, `overclaim_retracted` |
| `pre-sell-undefined-consulting` | `scope_narrowed`, `written_term_added`, `overclaim_retracted`, `evidence_gate_added` |
| `pivot-company-product-strategy` | `sequence_changed`, `threshold_changed`, `evidence_gate_added`, `written_term_added` |
| `deploy-assisted-intake-routing` | `scope_narrowed`, `threshold_changed`, `evidence_gate_added`, `stop_rule_added`, `user_question_added` |

The labels are not scores. More labels does not mean a better answer. A single
clear stop rule may matter more than five weak labels.

## Reviewer Decision Rules

Use these rules before marking a revised answer improved:

1. Name the smallest action-changing unit. If the reviewer cannot name it,
   suspect `no_op_prose_change`.
2. Tie the unit to an artifact. If the support lives only in reviewer
   intuition, mark it speculative.
3. Separate answer quality from run custody. `evaluation.json` can warn about
   live-output health without making the answer-level delta fail.
4. Prefer concrete deltas over adjectives. "More robust" is not a label;
   "adds a 14-day capacity gate" is.
5. Treat friction as useful only when it is both earned and usable.
6. Treat extra caution as noisy when it increases burden without changing a
   better decision.
7. Treat an omitted obvious gate, stop rule, or stakeholder term as missing
   friction when the trace supports it.

## PR32 Fixture Implications

PR32 should turn this rubric into adversarial pair fixtures. Candidate traps:

- smoother original versus rougher but safer revision;
- long checklist versus usable operating controls;
- emotional/status framing versus written operating terms;
- market excitement versus capacity/obligation gate;
- professional polish as legitimate signal versus status spending;
- broad AI launch language versus narrow operational pilot;
- marquee customer aura versus buyer-behavior proof;
- founder loyalty versus authority ambiguity.

Each fixture should force a future reviewer or judge to pick the answer with
the stronger actionable delta, not the answer with smoother prose.

## What This Does And Does Not Justify

This does justify:

- using PR30's six runs as rubric examples;
- asking reviewers to label actionable delta explicitly;
- preparing PR32 adversarial pair fixtures;
- later testing whether a narrow `actionable_delta` judge can match human
  labels.

This does not justify:

- a generic LLM judge;
- a calibrated judge yet;
- answer-quality scoring;
- automatic human labels;
- runtime integration;
- prompt rewrite;
- `conversation_understanding_ir.v0`;
- graph DB, embeddings, chunking, or memory;
- agent approval.

## Review Receipt

- PR31 is docs/eval-only.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No judge implementation.
- No automatic labels.
- PR32 Adversarial Pair Fixture Set v0 is next.
