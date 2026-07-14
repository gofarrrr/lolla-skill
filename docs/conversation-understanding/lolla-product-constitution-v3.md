# Lolla Product Constitution v3

Status: binding development house rules  
Date: 2026-07-12

This amendment incorporates
`docs/conversation-understanding/lolla-product-constitution-v2.md` in full. V0,
v1, and v2 remain immutable because completed evidence packages hash-lock them.
If this amendment conflicts with an earlier version, v3 governs future work;
historical runs remain governed by the constitution hash frozen in their
contracts.

## House rule 15 — Persistent failure triggers problem-class research

Current-practice review is not only a preflight. When a technical problem
survives bounded local attempts, produces contradictory or dubious evidence,
or begins consuming substantial time without a stable causal explanation,
development must pause local tuning and research the broader problem class.

This trigger applies when any of the following is true:

- the same material failure survives two prompt, schema, model, provider, or
  implementation variants;
- a stronger or more expensive component does not improve the target behavior;
- structural success and semantic success diverge in a way the current
  explanation does not predict;
- a provider or framework emits an opaque error that local validation cannot
  explain;
- the team is considering another architecture layer because the current path
  remains ambiguous rather than because evidence requires it.

The research must use the exact observed signature, not a generic technology
search. It should check, in proportion to the problem:

- current provider or model-lab documentation and limitations;
- recent primary research on the failure mechanism;
- maintained reference implementations, benchmarks, repositories, or issue
  reports showing how practitioners reproduce or mitigate it;
- whether the external case is genuinely analogous to Lolla or only shares
  surface language;
- solutions that were tried elsewhere, including their costs, failure modes,
  and assumptions.

The result is a dated problem-class note recording search questions, sources,
local-to-external evidence mapping, practices adopted, practices rejected, and
remaining unknowns. Another paid call, prompt variant, provider swap, or
architecture layer is not authorized until that note explains what new
information the action can produce.

External popularity does not override Lolla's probabilistic/deterministic
boundary. Retries, judges, multi-agent layers, schema splitting, free-form
reasoning, constrained decoding, or new frameworks are adopted only when they
fit the product, preserve custody, and earn their additional calls and fan-in.

## Product evil — Local reinvention loops

The team repeatedly tunes prompts, swaps models, simplifies schemas, or adds
pipeline stages while treating a known industry or research problem as a unique
local mystery. Work accumulates, but causal understanding does not. Conversely,
the team may copy a fashionable external solution without checking whether its
evidence scale, task, privacy boundary, or product objective matches Lolla.

## Additional “what good looks like” questions

- Did persistent or contradictory failure trigger a dated search for the exact
  problem class before more local tuning?
- Does the proposed next action follow from both local evidence and a genuinely
  analogous external result?
- Are external mitigations treated as hypotheses with explicit local gates,
  rather than as borrowed proof?
