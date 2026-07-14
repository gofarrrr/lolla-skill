# Phase 3 bounded development result

Status: complete — material redesign required  
Date: 2026-07-11

## Simple result

The decomposed-reader direction is promising but did not pass.

The baseline used Gemini 3.1 Flash Lite through OpenRouter. Two calls completed;
the third encountered an OpenRouter rate limit and correctly stopped the
remaining baseline. The two reviewable outputs showed one protected target and
missed one earlier alternative because the prompt favored a minimal, salient
answer.

One prospectively allowed generic prompt repair then told every reader to scan
the full conversation and preserve up to four materially distinct items. All
five repair calls completed operationally. Four outputs were admitted and all
four recovered their protected target. The exploration output was quarantined:
it joined non-contiguous quotations with an ellipsis, and its recovered
volunteer alternative still omitted the protected limit that concrete ownership
might not supply all needed ownership. A position item also strengthened its
cited evidence into advice against expansion that the cited sentence did not
state.

Therefore the repair achieved 4/5 protected-target visibility but failed the
frozen typed-admission, exact-source, zero-overclaim, and no-critical-zero gates.
There is no second repair and no transfer to Phase 4.

## What we learned

- One narrow reader per process question is materially better than the previous
  broad synthesis designs.
- The authoritative conversation plus complete auxiliary ledger fit within the
  budget and did not need deterministic semantic pruning.
- The generic chronological scan recovered earlier minority material that the
  baseline missed.
- A universal item schema is still too weak. It can name an alternative without
  requiring the alternative's limiting condition, or describe a challenge
  without structurally requiring the response.
- Free-form exact quotations are fragile when a model inserts ellipses. The
  deterministic validator correctly rejected the output rather than healing it.
- Strict shape is not semantic completeness, and good protected-target recall
  does not excuse unsupported extra items.

## Preserved architecture

Keep:

- probabilistic readers for messy conversation meaning;
- deterministic hashes, exact evidence validation, budgets, dispositions, and
  append-only custody;
- the original conversation as primary context;
- five direct, bounded process questions;
- target-blind source-first evaluation;
- no graph or final-answer evaluation at this stage.

Do not add a global synthesizer, deterministic keyword gates, layered semantic
rules, or another prompt repair.

## Next technical design

The next work should be provider-free first:

1. replace the universal item output with five small view-specific contracts;
2. require the semantic roles each view actually needs—for example,
   alternative plus limit, challenge plus response, and position plus remaining
   qualification;
3. expose a lossless sentence-span table with visible stable IDs so the reader
   selects exact evidence instead of reproducing long quotations;
4. prove the new representation and budgets without calls before another
   one-case development probe.

This is a bounded redesign of the semantic interface, not an architectural
revolution.

## Accounting

- Baseline: 3 provider requests, 2 successful inferences, $0.0044435 estimated.
- Generic repair: 5 successful inferences, 4 admitted, $0.0142385 estimated.
- Total: 8 provider requests, $0.018682 estimated.
- Automatic retries, fallbacks, evaluators, embeddings, graph, pipeline, and
  runtime calls: zero.

The machine-readable terminal record is `decision.json`. Individual parsed
outputs, exact-source compilation, usage, cost, and provider diagnostics remain
under `baseline/calls/` and `repair/calls/`.
