# Safe holdout pool v1 result

Status: **no pool admitted; new source input required**  
Date: 2026-07-10

## Simple result

The existing core corpus contains no safe untouched holdout, so we tried to
create one neutral five-case synthetic pool. Domains and case order were fixed
before any conversation existed. The generator never received the selection
order or any Lolla, graph, mental-model, or expected-answer target.

No pool was admitted:

1. **v1 failed before generation.** We requested unsupported Gemini reasoning
   effort `none`. The provider returned an error with no positive usage. The
   original runner also failed to preserve the provider's exact diagnostic.
2. **v2 generated five complete cases but failed its frozen scorer.** Every
   case had twelve alternating messages and complete usage custody. The only
   failures were 60 message-ID format mismatches: the model used `1…12`, while
   the validator demanded a case-prefixed format that the prompt never stated.
   This is an F8 scorer mismatch, not an observed conversation-quality failure.
   V2 remains failed and its text was not selected or repaired.
3. **v3 fixed the architecture but hit a provider rate limit.** Canonical IDs
   became deterministic code's job, while prompts, domains, and selection stayed
   identical. OpenRouter returned a preserved `429 rate_limit_exceeded` before
   positive usage. The terminal rule stopped further generation.

## Cost and calls

- three attempted generation calls across prospectively frozen contracts;
- zero automatic retries;
- zero evaluator calls;
- v2 known usage: 7,393 tokens and `$0.009792`;
- v1 and v3 usage/cost: unknown, not numeric zero;
- zero Stage A, Stage B, graph, or runtime calls.

Provider-free verification passed 12 focused pool tests and 18 combined pool-
and-governance tests. The non-network repository suite passed 4,051 tests with
one skip and 93 subtests under Python 3.12. The live-embedding stability module
was excluded to avoid unbudgeted provider calls.

## What we learned

The important engineering correction is durable: identifiers are deterministic
custody, not LLM judgment. Asking a model to satisfy an unstated ID format and
then failing the whole semantic artifact is exactly the brittle hybrid drift
the project constitution rejects.

The v3 runner now preserves bounded provider diagnostics and provider-envelope
hashes, and it assigns canonical message IDs without changing conversation
content. That machinery passed provider-free tests, but no successful v3 pool
exists.

## Current boundary

There is no selected new holdout. The five v2 conversations are frozen failed
fixtures and cannot become causal evidence through post-hoc scorer repair.
Additional pool-generation calls, Stage A, Stage B, graph testing, and runtime
integration are blocked.

The next requirement is a genuinely new safe conversation source under a new
source strategy—for example, founder-provided anonymized or explicitly
synthetic conversations fixed before Lolla review.
