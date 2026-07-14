# Safe holdout pool v1 preflight

Status: **one generation call authorized after provider-free preflight**  
Date: 2026-07-10

## Why a new pool is necessary

The twelve-case core corpus is exhausted for the current causal program. The
only mechanically untouched core case is already excluded for legal,
employment, regulatory, and retaliation risk. The only other local transcript
is the old Marcus fixture, which appears in four historical controlled-
comparison directories and is not genuinely new.

Reusing those conversations would give us more activity, not cleaner evidence.

## Pool design

The pool contract fixes five low-risk domains before generation:

1. small product-team scope;
2. creative collaboration and credit;
3. adult nonprofit program scale;
4. non-safety-critical research-tool release;
5. community arts portfolio.

Each case must contain exactly twelve alternating messages. Cases may contain
messy values, corrections, changing context, and naturally imperfect advice,
but no hidden answer key, expected pressure, mental-model term, graph target,
or deliberate factual trap.

## Anti-selection control

The complete candidate order was computed before any conversation exists:

```text
1. pool1-case03-nonprofit-program-scale
2. pool1-case05-community-arts-portfolio
3. pool1-case02-creative-collaboration
4. pool1-case04-research-tool-release
5. pool1-case01-product-scope
```

The order is the ascending SHA-256 digest of
`public_seed + ":" + case_id`. The generation prompt does not contain the seed
or ranking. After generation, review may reject a case only for a named safety
or contract defect. It may not choose the case most likely to activate Lolla,
the graph, a useful mental model, or an answer delta.

## Proposed call boundary

- one OpenRouter call to `google/gemini-3.1-flash-lite`;
- zero retries;
- zero evaluator calls;
- at most 10,000 output tokens;
- `$0.06` estimated-cost ceiling;
- no Stage A or downstream call;
- exact output, usage, served model, prompt hashes, and conversation hashes
  preserved.

The generation model is from a different family than the planned downstream
`openai/gpt-5.1-chat` consumer. It is still synthetic-model-authored evidence,
not a substitute for later real conversations or human usefulness review.

## Authorization condition

The runner tests passed, final prompt hashes replaced their placeholders, the
dry run passed, the output directory was absent, and every hash lock was
current. `call-authorization.json` authorizes exactly one generation call with
no retry or evaluator. It does not authorize Stage A.

## Final status

This preflight lineage is now closed. V1 failed on unsupported reasoning
configuration, v2 failed on an over-strict unstated ID format, and the
prospectively repaired v3 received a preserved provider rate-limit error. No
pool or case was admitted. See `result.md` and `decision.json`; do not restart
generation from this preflight.
