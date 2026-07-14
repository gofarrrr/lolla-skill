# Case 10 frozen downstream pair — 2026-07-10

Status: **Gates 4 and 5 complete; pair executed once and stopped**

This directory contains the first Case 10 strong-reconsideration-versus-Lolla
pair frozen completely before either downstream output existed.

Read in this order:

1. `contract.json` — frozen source, prompts, calls, schema, red lines, review
   contract, cost/time bounds, and stop rules;
2. `run/lolla_stage_b_case10_20260710_a1/run-summary.json` — mechanical result;
3. `run/lolla_stage_b_case10_20260710_a1/blind-outputs.json` — anonymous A/B
   outputs;
4. `blind-review-before-key.json` — review sealed at
   `c33e837f39da522ec961956dc16c80e4a3d114fd2e179e76c10206c3f03751cd`
   before the arm key was read;
5. `run/lolla_stage_b_case10_20260710_a1/arm-key.json` — reveal mapping;
6. `revealed-comparison.json` — blind findings mapped to arms without
   post-reveal regrading;
7. `decision.json` — Gate 4, Gate 5, and Gate 6 authorization decision;
8. `result.md` — concise interpretation.

Gate 4 passed mechanically: two successful calls, no retry, no evaluator, full
usage/model custody, 6,027 total tokens, `$0.021525` estimated cost, and no
failed gates.

Gate 5 found no unique answer improvement. The treatment did show provisional
accountable-consideration value and correct stand-down, but it was longer and
introduced a source-fidelity caveat. The paid pair is closed permanently.

Only a provider-free Gate 6 graph-attribution preflight is authorized next.
No new provider call, graph promotion, runtime change, Case 10 rerun, or answer
quality claim follows from this package.
