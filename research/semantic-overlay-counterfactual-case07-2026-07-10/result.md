# Case 07 Semantic-Overlay Counterfactual Result

Date: 2026-07-10  
Status: three-call directional counterfactual complete; human review pending

## Question

Would the actual SK3 semantic overlay help a fresh reasoner on the known
unresolved-decision case, and would restoring the one source-reviewed omission
change the result?

The three blind arms were:

- full conversation with a strong reconsideration prompt;
- the same context plus all 27 actual SK3 selected semantic events;
- the same context plus those 27 events and the one reviewed missing
  self-correction.

The additional observation remained separate and diagnostic. It did not alter
SK3's score or become current-system output.

## Blind result

All three outputs correctly said Seattle remained undecided because all arms
still received the full transcript.

Blind ranking was:

```text
A approximately equal to C, both better than B
```

A directly used the user's statement that she kept claiming to have decided
when she had not. It also challenged the implied preference for Seattle.

B said the decision was open, but it did not explicitly take back the
assistant's “Seattle is the root decision” framing. Its answer was calibrated
and usable, but flatter and more aligned with the prior assistant's
organization.

C explicitly rejected the single-root framing, preserved multiple value
dimensions, and better incorporated the user's overwhelm. It repaired B's main
weakness but did not clearly beat A.

After reveal:

- A was the transcript-only strong control;
- B was the actual 27-event SK3 overlay;
- C was the overlay plus the one reviewed omission.

## Decision

Naive full-semantic-overlay integration is blocked.

The actual overlay was worse than the strong control on the exact issue the
test targeted. Restoring the omitted observation improved the overlay, which
confirms that the omission matters to the audit and can affect framing. But the
oracle arm only reached rough parity with the control. The strong reasoner had
already recovered the issue from the raw transcript.

This does not make the semantic kernel useless. It clarifies its roles:

- a complete semantic inventory can improve audit, navigation, and receipt
  fidelity;
- the same inventory should not be dumped wholesale into reconsideration;
- source validity is necessary but does not prevent attention distortion;
- raw conversation remains a critical defense against semantic-index misses;
- a reasoning projection must be smaller and consumer-specific.

The consumer-specific selection remains an LLM or human semantic job.
Deterministic code may validate exact evidence, enforce caps, preserve omitted
and rejected candidates, and transport the chosen packet. It must not use
keywords or layered gates to decide relevance.

## Cost and boundary

The diagnostic used three generation calls, 13,077 tokens, and an estimated
$0.03330 under the repository's 2026-05-25 pricing table. No evaluator calls or
retries were used.

No runtime, graph, or semantic-kernel integration is authorized. Paid calls
stop here while the minimal reasoning-projection requirements are defined from
existing evidence.

