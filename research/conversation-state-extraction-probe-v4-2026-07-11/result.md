# Conversation-state extraction probe result

Status: **closed; failed on the first semantic case**

## Simple result

We made the extractor operational, but it did not understand the conversation
well enough to pass custody. The first case returned complete JSON with normal
usage and no reasoning tokens. Deterministic validation then found unsupported
joint ownership and a fabricated exact quote, so the frozen stop rule prevented
the second call.

This is useful negative evidence. The obstacle is no longer merely API wiring.
The model still compresses a messy conversation in exactly the ways Lolla is
trying to prevent: it loses joint development, substitutes different threads
for the focal trajectory, merges claims with different source strength, drops
most constraints, and loses the assistant's final qualification.

## What the sequence taught us

- V1: provider-side typed schema failed before inference.
- V2: replacing `const` with `enum` did not fix the provider rejection.
- V3: JSON wire mode reached inference, but the schema was not visible in the
  prompt, so the model returned the wrong shape.
- V4: showing the schema produced the required shape, exposing the actual
  semantic and grounding failures.

V4 used one OpenRouter call, 4,057 total tokens, and an estimated $0.002488.
There was no retry, second-case call, evaluator, graph, or full pipeline.

## What not to claim

This result does not show that the minimal state representation is wrong. The
provider-free five-case replay already showed that the representation can carry
the reviewed state. It shows that this prompt/model extraction path cannot yet
populate it reliably—even on the only reviewed resolved-thread case.

The quarantined invalid packet remains useful for diagnosis, but it is not an
accepted observed state packet. The v4 custody wrapper attempted to prevent
invalid persistence but only suppressed empty packets; the non-empty invalid
packet still received a path. That implementation defect is preserved and must
be fixed prospectively.

## Next step

Do provider-free design work before another call:

1. make focal-thread and contribution coverage explicit candidate obligations;
2. preserve atomic claim strength rather than invite merged constraints;
3. reject every packet with validation errors before assigning an observed path;
4. replay the revised contract against reviewed packets and adversarial
   synthetic outputs;
5. only then decide whether a new, bounded multi-case call is worth authorizing.

Do not run Case 04 from this contract, tune only to Case 03, grow the graph, or
launch a full development pipeline.
