# Decomposition design check against the supplied pipeline article

Status: accepted with Lolla-specific revision  
Date: 2026-07-11

## Source considered

The founder supplied “Your LLM Pipeline Is Slow Because Your Agents Do Too
Much,” by Muratcan Koylan and Amit Kumthekar. It is used as architecture context,
not as proof that the same decomposition will work for Lolla.

## What the article confirms

The article's central production finding matches Lolla's completed experiment
evidence:

- overloaded first passes create attribution, omission, routing, and schema
  failures;
- judge/refinement loops repair some local errors while introducing others;
- focused agents with small output contracts can make first-pass quality more
  reliable;
- fan-out should be parallel where tasks are independent;
- deterministic typed interfaces make fan-in tractable;
- one bounded cross-output QA pass is preferable to open-ended iteration;
- prompt versions, model identity, cost, latency, and failure custody must be
  observable per component;
- decomposition granularity is empirical and must be evaluated rather than
  assumed.

These points support Lolla's constitution: probabilistic systems interpret
messy meaning; deterministic systems own identity, custody, validation,
composition, and explicit stop rules.

## Where Lolla must revise the article's pattern

Clinical note sections are relatively independently addressable. Lolla's
conversation state is not:

- position ownership depends on contributions across turns;
- a thread introduced early may be qualified, generalized, or resolved late;
- a constraint's importance may emerge only after the current plan changes;
- user and assistant contributions jointly form the process being audited.

Therefore, “one arbitrary transcript chunk per final field” would destroy the
trajectory we need to preserve. Lolla requires two semantic levels:

1. **small-window harvesting** — narrow calls identify possible local events;
2. **fresh-context synthesis** — separate calls interpret the complete ordered
   candidate ledger for current position, thread trajectory, and atomic source
   strength.

The raw transcript is not repeatedly handed to every synthesis task. Synthesis
receives stable event candidates, their speaker/turn identities, and
deterministically retrieved exact source text.

## Revised architecture

```text
seven user/assistant turn-pair windows
        |
        +-- contribution-event harvester
        +-- thread-event harvester
        +-- constraint-claim harvester
        |
deterministic candidate ledger (no semantic gating)
        |
        +-- fresh position/ownership synthesizer
        +-- fresh thread/trajectory synthesizer
        +-- narrow per-claim source-strength classifier
        |
deterministic validated conversation-state compiler
        |
reasoning-pattern abstraction (only after state gates pass)
        |
deterministic graph (never receives factual state directly)
```

## Non-negotiable implementation rules

- Harvesters return stable span IDs, not copied excerpts.
- Deterministic code retrieves exact text and speaker/turn metadata.
- Harvesting favors recall and preserves extra plausible candidates.
- No deterministic relevance gate decides which messy events matter.
- Every harvested and synthesized candidate receives terminal ledger custody.
- Synthesis runs in a fresh context and cannot see prior model prose.
- One generic repair round is the maximum within any frozen evaluation stage.
- No hidden retry, response healing, majority vote, or composite quality score.
- Parallel execution is an optimization only after semantic contracts pass.
- The live skill, graph, and downstream answer path remain unchanged until the
  relevant evidence gates pass.

## Decision

Proceed with Phases A–E using small-window harvesting plus fresh ledger
synthesis. Do not implement arbitrary chunk summaries, a monolithic QA loop, or
another one-call-per-family prompt repair.
