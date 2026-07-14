# Affordable semantic operator selection — 2026-07-13

Status: affordable testing candidate selected; production default and full-pipeline reliability not established  
Date: 2026-07-13

## Decision

Use `google/gemini-3.1-flash-lite` through the pinned Google Vertex OpenRouter
endpoint as the current **testing candidate for small, decomposed semantic
microtasks**. Use low reasoning effort for the smallest classification tasks.

Do not use Gemini 3.5 Flash for routine development tests. Preserve its existing
outputs as a premium reference. A stronger, more expensive product tier may be
tested later only if users demand it, someone accepts the cost, and a frozen
comparison shows that it improves the dimensions that matter. Price and polish
alone are not sufficient.

This is not a production-model selection. It does not authorize the full
nine-mechanism expansion, pressure generation, runtime integration, or a claim
that the affordable path improves reasoning.

## What the comparison taught us

Model price was not the main problem. Task shape was.

- DeepSeek V4 Flash was extremely cheap, but the exact starting-position probe
  was slow, omitted required envelope fields, and changed evidence identity. It
  was not usable for this contract.
- Gemini 3.1 Flash Lite completed the same starting-position task faithfully.
- Gemini Lite failed when current and qualification work were combined, but
  passed when each role received one small job.
- An unconditional qualification extractor produced a false qualification on
  a quiet case. A small probabilistic presence/absence review followed by
  evidence-bounded detail passed both the unresolved and quiet cases.
- A monolithic nine-mechanism task failed validation and semantic review.
- One-mechanism tasks fixed structural overload, but one call still confused
  “the risk remains” with “the reasoning ignored the risk.”
- Splitting user-process judgment from assistant-coverage judgment repaired
  that failure. A repeat preserved the semantic result.
- On a separate stand-down case, medium reasoning consumed 909 of 984 completion
  tokens and truncated a tiny JSON object. The partial answer was also
  semantically inconsistent.
- Factoring the user judgment into `mechanism_observation` and
  `integration_status`, then using low reasoning, passed the transfer case.
  Code mapped those explicit semantic factors to `resolved`; it did not inspect
  conversation prose.

The current reference shape is therefore:

1. The LLM separately extracts starting and current position.
2. A small LLM review decides whether a distinct unresolved qualification is
   present.
3. Qualification detail is called only for the exact evidence selected by that
   review; an explicit negative review materializes empty qualification custody.
4. For each controlled reasoning mechanism, the LLM says whether the mechanism
   was observed and whether later user reasoning integrated it.
5. A separate LLM task says whether the assistant operationalized the pressure.
6. Deterministic code validates identities and schemas, derives the controlled
   status and routing disposition, and preserves custody. It does not infer
   conversational meaning from keywords, chronology, or hand-written prose rules.

This stays inside the constitution: probabilistic components interpret messy
meaning; deterministic components enforce declared contracts, identity,
budgets, routing policy, and replay.

## Cost evidence

The preserved Gemini 3.5 V1 campaign used 96 attempted calls, 87 operationally
successful calls, and `$3.1495905` in provider-reported spend.

The entire affordable-model investigation used 21 provider calls and
`$0.042771112`:

| operator | calls | provider-reported spend |
| --- | ---: | ---: |
| DeepSeek V4 Flash | 1 | `$0.001213362` |
| Gemini 3.1 Flash Lite | 20 | `$0.04155775` |
| total | 21 | `$0.042771112` |

That total includes failed combined tasks, the monolithic mechanism attempt,
the truncated transfer, and every successful repair. It is about 74 times less
than the premium V1 campaign in total spend, but the workloads differ, so this
is not a per-call or equal-quality comparison.

The final factored transfer reference used two calls and cost `$0.00175675`:

- user factors: `$0.00077925`, 97 reasoning tokens;
- assistant coverage: `$0.0009775`, 101 reasoning tokens.

The immediately preceding medium-reasoning user-status attempt alone cost
`$0.0019155`, spent 909 tokens on reasoning, and truncated. OpenRouter documents
that reasoning tokens are billed output tokens and that Gemini 3 reasoning
effort maps to Google's thinking levels. This supports low effort for tiny
structured tasks, while acknowledging that Google still determines the actual
thinking-token count. See [OpenRouter reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
and [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).

## What is proven and what is not

Supported by current evidence:

- Gemini 3.1 Flash Lite can perform the separated role, qualification-review,
  qualification-detail, user-factor, and assistant-coverage jobs on the tested
  cases.
- Strict schema, exact provider pinning, zero retries, zero fallbacks, preserved
  failure artifacts, and deterministic joins work.
- The difficult counterpressure classification passed source review, one repeat,
  and one separate stand-down transfer after factoring.
- Small jobs with low reasoning are materially cheaper than the prior combined
  jobs.

Not established:

- all nine mechanisms across all source strata;
- reliable activation of useful pressure rather than only correct stand-down;
- recovery of an unknown unknown absent from the role representation;
- end-to-end affordable operation on the full V1 corpus;
- graph contribution, reconsideration utility, real-user usefulness, or
  production stability;
- that Gemini 3.5 is worth a premium tier, or that Gemini Lite matches it on a
  frozen equal-workload comparison.

## Next bounded goal

Design the full-nine expansion provider-free before spending again. The design
should run one factored user task per controlled mechanism, call assistant
coverage only when the model-authored user factors make coverage applicable,
and join all results through the existing deterministic policy. It must expose
call ceilings and expected cost before execution.

Then freeze a small cross-stratum batch: one pressure-expected case, one
stand-down-expected case, and one park-expected case. The next paid batch must
answer two questions simultaneously:

1. Can the cheap operator preserve restraint on quiet and park cases?
2. Can the representation activate a source-grounded pressure on a pressure
   case?

If pressure still disappears because the role packet never represented the
off-frame dependency, do not buy a smarter model or add deterministic semantic
gates. Return to the probabilistic residual-challenge representation identified
by the V1 false-stand-down review.
