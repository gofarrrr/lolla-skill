# Independent useful-case mechanism probe result

Status: closed without retry; partial contract evidence, not promotion evidence  
Date: 2026-07-12

## Question

Can the fact-free probabilistic bridge recognize the useful case's protected
reasoning mechanism across harmless role-record variation, and stop recognizing
it when that meaning is removed?

The protected mechanism was `status_signal_used_as_evidence`. The case concerns
a prestigious retailer pilot whose selection risked being treated as evidence
of product demand beyond that retailer's context.

## Run

- Frozen contract:
  `docs/evals/independent-useful-mechanism-probe-contract-v1.json`
- Result:
  `research/independent-useful-mechanism-probe-2026-07-12/result.json`
- Model/provider: `deepseek/deepseek-v4-flash` through the pinned Alibaba
  OpenRouter provider
- Calls: 3
- Automatic or semantic retries: 0
- Estimated cost: USD 0.00090916
- Operational and complete nine-mechanism coverage: yes
- Scalar score: none

## What passed

The protected mechanism was `unresolved` in both the source-authored and
provider-produced role-record arms. It became `not_observed` after the status
meaning was removed while the rest of the role structure was retained.

This is useful causal evidence. The bridge responded to the reasoning meaning
we intended to test rather than merely emitting the same label in every arm.

## What failed

The frozen result is correctly marked `one_or_more_gates_fail`:

- `acknowledged_constraint_not_gated` appeared only in the source-authored arm;
- `counterpressure_acknowledged_not_integrated` and
  `missing_reversal_condition` persisted in the provider and ablation arms;
- the source-authored arm emitted four additional unresolved mechanisms, above
  the prospective cap of two;
- therefore the secondary-mechanism invariance and bounded-noise gates failed.

The source and provider role records are semantically similar, not identical.
Requiring all plausible secondary readings to be identical would turn a useful
variance diagnostic into a demand for brittle semantic uniformity. This probe
does not establish broad mechanism stability, but its protected causal test is
valid.

## Decision

Do not retry, repair the gold, add keyword gates, or tune another prompt on this
case. Preserve the failed contract.

For the independent downstream product test, use the actual provider-produced
projection and route every unresolved mechanism it emitted. Do not take an
intersection with the source arm and do not let another model pre-filter the
portfolio. The fresh-context reasoner must inspect and disposition all graph
candidates. The product-level question is now whether the portfolio yields the
prospectively named independent-demand pressure without unsupported facts or
forced absorption.

This decision authorizes a bounded Phase 5 experiment, not mechanism-bridge
promotion, runtime integration, or a production claim.
