# Structured extraction practices amendment — fan-in evidence

Status: standing amendment for future work  
Date: 2026-07-11

This document amends
`structured-extraction-practices-july-2026.md` without modifying that
hash-locked historical practice record.

## Refined decomposition target

The A–E evidence refined the next research architecture:

1. small-window local event harvesting;
2. deterministic source resolution and complete candidate custody;
3. bounded probabilistic consolidation of overlapping local observations;
4. fresh cross-turn synthesis for position ownership and thread trajectory;
5. local-context claim-strength classification plus global load-bearing
   selection;
6. deterministic validation and fail-closed handoff assembly.

The consolidation boundary is a research target, not implemented runtime
architecture. The first attempt skipped it and handed 88–95 overlapping raw
events to global synthesis, recreating the overload decomposition was meant to
remove.

## Budget fan-in, not only fan-out

A pipeline can contain individually small jobs and still fail when their
overlapping outputs create one large downstream task. Freeze and measure the
number of candidates, repeated source spans, serialized input tokens, and
schema-enumeration size at every fan-in boundary.

Do not solve fan-in overload with deterministic semantic relevance filters.
Use bounded probabilistic consolidation, preserve all inputs and dispositions,
and evaluate whether important minority signals survive.

## Label only what the task context can support

Local windows can identify directional content, claims, questions, concerns,
and locally observable moves. They cannot reliably decide conversation-wide
origin, ownership, acceptance, first introduction, or final disposition.
Source strength is best classified near the original attribution and modality;
global synthesis must not silently strengthen it.
