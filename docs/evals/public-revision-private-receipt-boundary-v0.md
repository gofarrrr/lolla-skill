# Public revision / private receipt evaluation boundary v0

Status: active evaluation contract; no runtime change  
Date: 2026-07-10  
Governing runtime doctrine:
`references/private-enrichment-treatment.md`

## Why this exists

The live Step 6 doctrine already has the right product boundary:

> privately test the material hard; publicly show only the decision-relevant
> improvement; leave a ledger so reviewers can see what happened.

The first frozen Case 10 pair did not preserve that boundary cleanly in its
evaluation measurements. Each generator returned one JSON object containing
both public-style revision fields and the private `pressure_dispositions`
receipt. Treatment used 959 completion tokens and control used 640, but much of
that difference was the treatment-only private receipt.

Therefore the honest measurement is:

- treatment created more **total generation and receipt volume**;
- treatment created a materially richer accountability object;
- the experiment did **not** isolate public-answer length;
- the 49.8% total-completion difference must not be presented as a measured
  49.8% public-answer bloat result.

The frozen blind review and decision remain unchanged. This document records
the evaluation correction prospectively.

## Required two-surface shape

Future reconsideration experiments must preserve two typed surfaces even when
one model call produces both.

### Public revision

This is the only surface eligible to become the primary user answer. It may
contain:

- the end-of-conversation decision state;
- what useful reasoning survived;
- what unsupported claim is taken back or bounded;
- at most three or four material shifts;
- the smallest useful next actions;
- decision-relevant uncertainty.

It must not contain:

- pressure, chunk, card, packet, lane, ledger, arm, or experiment IDs;
- a list proving how much machinery ran;
- one paragraph per supplied pressure;
- generic diligence added only to show activity;
- a forced visible delta when private consideration correctly stands down.

### Private consideration receipt

This surface is retained for later agents, human inspection, and accountability.
For every supplied pressure it records:

- immutable pressure or chunk identity;
- strongest plausible application;
- use, rejection, deferral, private-guardrail, or technical-failure state;
- the condition that passed or failed;
- visible effect, if any;
- private guardrail, if any;
- risk if forced;
- risk if ignored;
- source and transformation lineage.

The receipt may be longer than the public revision when the packet contains
material worth hearing. That is not automatically bloat. It becomes an
operability problem when its calls, tokens, latency, attention demand, or
failure surface are disproportionate to the pressure preserved.

## Separate measurement vectors

Never combine these into one quality score.

| surface | measure |
| --- | --- |
| Public revision | visible tokens/words, source fidelity, preserved value, unique actionable delta, forcing, clarity, deadline fit, no-op correctness |
| Private receipt | exact identity coverage, serious dispositions, rejection quality, lineage, false stand-down, unknown pressure preserved |
| Whole run | calls, prompt/completion tokens, cost, wall time, failures, retries, artifact volume, reviewer attention |

A complete private receipt does not prove a better public answer. A public no-op
does not prove the graph or pressure packet was useless. A long receipt does not
prove deep reasoning.

## Source-fidelity red lines

Future contracts must distinguish three different requirements:

1. `must_not_contradict` — facts that can be omitted from a concise answer but
   cannot be changed;
2. `must_explicitly_preserve` — constraints or values that must remain visible
   because omitting them changes the decision;
3. `must_not_invent` — market, financial, legal, insurance, repair, causal,
   psychological, stakeholder, or outcome facts that are absent.

This prevents a concise answer from failing merely because it did not repeat
every number, while still protecting load-bearing facts.

## Deadline and action-horizon rule

Case 10 exposed a different failure: both arms recommended contractor,
insurance, and liquidity checks without separating what could happen before the
tomorrow-noon bid deadline from what could happen only after acceptance or
closing.

Future high-stakes contracts must supply the hard deadline as a
`must_explicitly_preserve` constraint. Proposed actions should be typed by the
generator as one of:

- `before_decision_deadline`;
- `conditional_after_acceptance`;
- `post_closing`;
- `unknown_or_requires_user_confirmation`.

Deterministic code may validate identity, presence, and allowed values. It must
not decide whether a messy real-world action is semantically feasible. That
remains an LLM/human source-review judgment.

## Gate consequence

No Case 10 arm is rerun and no prompt is tuned against its outputs. This
boundary applies only to future contracts.

A future graph-specific test is eligible only when:

- an exact graph relationship chunk is source-reviewed and individually
  dispositionable;
- the comparison arm removes or fairly shuffles that exact graph contribution;
- both arms share the same public-revision schema;
- private receipts are compared separately;
- public bloat is measured only from the rendered public fields;
- hard deadlines and load-bearing source values survive.

## Non-claims

This is not a runtime redesign, a new semantic gate, a public proof-of-work
badge, a quality score, graph promotion, or authorization for autonomous action.
