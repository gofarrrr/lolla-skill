# Ambiguous development Case 05 Stage A preflight

Date: 2026-07-10  
Status: frozen and authorized for one orchestrator invocation

This is a development observation on a same-session synthetic conversation. It
is not a clean holdout, product validation, or an answer-quality result.

The source is the next case in the rank frozen before authoring. A deterministic
wrapper adds only `CONVERSATION:` message counts; the entire semantic source is
preserved byte-for-byte. The repaired Stage A dry run verifies the header and
all 14 message markers before any provider call.

The contract freezes one fresh extraction and the full private pressure
pipeline, OpenRouter Gemini 3.1 Flash Lite with reasoning disabled, direct
OpenAI-only embeddings, no revision, no experiment retry, outer timeouts, exact
hashes, source red lines, at most 36 OpenRouter calls, at most eight direct
OpenAI calls, and a $0.15 estimated cost ceiling.

Passing the machinery will not pass the pressure review. A source-first review
must find at least two trace-supported pressures that are not already obvious in
the original assistant reasoning, at least one pressure with a concrete
question, gate, sequence, stop rule, or private guardrail consequence, and at
least one rejected redundant, forcing, or unsafe pressure.
