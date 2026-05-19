# Pre-Step-6 Judgment-Led Reviewer Protocol Contract

Date: 2026-05-19

Status: docs-only research containment contract. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, public output, workers, bundles, handoff modes, generator implementation,
deterministic selectors, or subagent orchestration.

Related:

```text
research/pre-step6-phd-judgment-led-handover-review-readout-2026-05-19.md
research/pre-step6-user-has-plan-judgment-led-no-handover-review-readout-2026-05-19.md
research/pre-step6-phd-adversarial-missed-decline-readout-2026-05-19.md
research/pre-step6-user-has-plan-static-decline-readout-2026-05-19.md
research/pre-step6-autoresearch-operating-loop-2026-05-19.md
research/pre-step6-replay-ledger-aggregate-readout-2026-05-18.md
```

## Decision

The next research shape is:

```text
judgment-led reviewer protocol with deterministic receipts
```

Not:

```text
deterministic admission selector
runtime generator
pre-Step-6 worker system
reasoning bundle
new handoff mode
product promotion
```

This contract exists to prevent the reviewer idea from sliding into machinery.
It defines what the protocol is allowed to mean before any implementation is
discussed.

## Core Thesis

The deterministic middle should not become the thinker.

The split is:

```text
LLM reviewers:
  make narrow judgment calls about loss, burden, and minimum useful handover

deterministic code:
  preserves source refs, reviewer outputs, gates, receipts, and audit trails

Step 6:
  remains the final synthesis point and may use, ignore, reinterpret, or reject the review
```

The reviewer protocol exists only to answer:

```text
Would Step 6 likely lose important reasoning pressure without a prepared handover?
```

It does not answer:

```text
What is the final advice?
Which pressure is true?
Which answer is correct?
What must Step 6 believe?
```

## Evidence Basis

Two manual judgment-led reviews define this contract.

PhD conflict:

```text
loss reviewer: prepared_handover_needed
burden reviewer: ambiguous, medium naturalness debt
minimal reviewer: one_compact_handover
result: one compact handover helps
```

Why:

```text
simple material could lose the unresolved Silva-vs-fallback tension
```

Consulting launch / `user_has_plan`:

```text
loss reviewer: no_handover_needed
burden reviewer: prepared_handover_too_costly
minimal reviewer: no_handover
result: no handover is better
```

Why:

```text
simple material already carries network-not-pipeline, spouse runway alignment,
paid-demand probing, and the 4-week checkpoint
```

The important evidence is not that reviewers can produce a handover. The
important evidence is that they can refuse one.

## When Reviewers Are Asked

Reviewers should be asked only when there is a real research question about
handover need:

```text
Step 6 may lose a live tension, boundary, caution, or reversal condition
simple material may be enough but the consequence of missing pressure is high
raw artifacts contain useful pressure but may also leak clutter or machinery
there is conflict between pressure preservation and naturalness debt
the research team is explicitly testing whether handover should be withheld
```

Reviewers should not be asked merely because:

```text
artifacts exist
a handover could add nuance
more structure would be inspectable
the case feels important
there is time to run more analysis
```

If there is no concrete suspected pressure loss, the default research posture
is:

```text
do not ask reviewers
```

## Source Packet

If reviewers are asked, they receive a small source packet:

```text
user question or case summary
simple/control material
raw artifact summary or selected raw answer core
existing rendered or decline evidence, if any
the exact reviewer question
forbidden moves
```

They should not receive the whole archive by default.

Forbidden moves:

```text
write final advice
create a new handoff mode
propose runtime wiring
propose a generator
propose a deterministic selector
launch more reviewers
create a bundle
turn the review into a playbook
```

## Three Reviewer Questions

Loss reviewer:

```text
What would Step 6 likely lose with simple material only?
```

This reviewer must name concrete pressure:

```text
live tension
hard boundary
evidence gate
reversal condition
overclaim caution
duplicate/misfit demotion
relationship or tone constraint
```

If no concrete pressure would likely be lost, the reviewer should say:

```text
no_handover_needed
```

Burden reviewer:

```text
What would a prepared handover risk making worse?
```

This reviewer looks for:

```text
naturalness debt
over-processing
procedural feel
source-looking authority without source strength
hidden checklist behavior
public answer bloat
loss of humane or situated judgment
```

Minimal handover reviewer:

```text
What is the smallest useful handover, if any?
```

This reviewer must prefer:

```text
no handover
```

unless a concrete likely-lost pressure is named.

If handover is justified, the default maximum is:

```text
one compact handover
```

If the reviewer thinks more than one compact handover is needed, the proper
output is usually:

```text
stop / insufficient justification
```

not a larger handover plan.

## Valid Outcomes

Outcome 1:

```text
no_handover
```

Meaning:

```text
simple material already carries the important pressure
prepared handover would mostly add naturalness debt or procedure
no concrete lost pressure was named
Step 6 is better served by less machinery
```

Outcome 2:

```text
one_compact_handover
```

Meaning:

```text
simple material would likely lose a concrete pressure
handover can preserve that pressure without becoming a mini-answer
burden is real but acceptable
handover is narrow enough for Step 6 to reject
```

Outcome 3:

```text
stop_insufficient_justification
```

Meaning:

```text
reviewers disagree materially
the handover need is vague
the proposed handover starts becoming a playbook
the review cannot separate pressure preservation from answer planning
the safest move is to stop rather than produce machinery
```

## Overproduction

The protocol is failing if handover is justified by:

```text
generic clarity
generic nuance
generic structure
source-looking texture
procedural completeness
visible diligence
extra playbook material
the mere existence of artifacts
reviewer desire to be useful
```

None of these count unless tied to a specific pressure Step 6 would likely
lose.

The Bevelin-style hygiene question is:

```text
How could this protocol be fooling us into mistaking more work for better judgment?
```

## No-Handover Success

No-handover is a positive research outcome when:

```text
simple material already carries the important pressure
handover would add medium or higher naturalness debt
no concrete likely-lost pressure is named
reviewers can state what would reactivate handover
Step 6 remains better served by less machinery
```

No-handover is not absence of work. It is an explicit judgment with a receipt.

## Deterministic Code May Do

Deterministic code may:

```text
record source refs
record reviewer questions
record reviewer judgments
record confidence and disagreement
record why handover was declined, limited, or stopped
record reactivation conditions
enforce research-only gates
enforce product/runtime blocks
preserve receipts for later audit
```

This is custody.

## Deterministic Code May Not Do

Deterministic code may not:

```text
decide final advice
decide which pressure is true
force Step 6 to use a handover
turn reviewer judgment into a formula
score handover need
promote a generator
create a selector
create runtime workers
create a bundle
create a new handoff mode
update SKILL.md
update HOW_IT_WORKS.md
update product docs
wire anything into /lolla
```

## Step 6 Freedom

Step 6 remains free to:

```text
use reviewer output
ignore reviewer output
reinterpret reviewer output
soften reviewer output
reject reviewer output
ask for raw evidence if needed
write an answer that differs from the review
```

Reviewer output is pressure, not verdict.

## Failure Modes

Pause the protocol if:

```text
reviewers usually recommend handover
reviewers justify handover with generic clarity or nuance
reviewers produce playbook material
reviewers write final-answer content
reviewers ignore naturalness debt
reviewer outputs become longer than the handover they are judging
deterministic code starts converting reviewer output into rules
Step 6 starts obeying review output as instruction rather than pressure
```

Stop the protocol if:

```text
no-handover stops being treated as a valid success
one compact handover becomes a default
runtime integration is proposed before broader evidence
the system needs more roles to make the first three roles work
```

## Evidence Needed Before Runtime Work

Runtime work remains blocked.

Before implementation is discussed, research would need evidence that:

```text
reviewers can say no across more than one decline case
reviewers can say one compact handover across more than one conflict/clutter case
reviewers can produce stop_insufficient_justification
reviewer outputs stay compact
Step 6 uses or rejects reviewer pressure without machinery leakage
naturalness debt does not rise when reviewers are used
source/overclaim audits still pass after reviewer-informed answers
the protocol improves or simplifies final answer quality versus simpler controls
```

Even then, any implementation discussion must start off-default and
research-only.

## Current PM Verdict

The research question is now coherent:

```text
not deterministic selector
not runtime generator
not worker system
yes reviewer protocol with deterministic receipts
```

This contract is the stopping point for the current round.

Next action:

```text
pause implementation
use this contract for PM review
do not build machinery from it without a new explicit decision
```
