# Lolla R3 fresh-consumer result

Status: complete negative operational result; semantic proof not reached

Date: 2026-07-13

Provider attempts: 1

Successful generations: 0

Quiet-control attempts: 0

## Plain-language outcome

R3 built the experiment we intended, froze it, and spent its one authorized
attempt. The request reached Google through OpenRouter, but Google rejected it
as an invalid argument before the model generated an answer.

That means R3 did **not** tell us whether the fresh reasoner can use Lolla's
pressure well. There is no reconsidered answer to score. It did tell us that
the new operational safety boundary works: one attempt was recorded before
transport, the exact request remained hash-locked, the failure was preserved,
there was no retry, fallback, response healing, or premium model, and the quiet
control did not run after the pressure gate failed.

The result is therefore useful but narrow. It is a failed provider request, not
a failed reasoning result and not evidence against Lolla's product thesis.

## What was frozen before the call

The checked-in R3 contract fixes:

- the complete 12-turn Case 01 conversation and original final answer;
- the current R2 constitutional graph portfolio;
- nine active pressure items: six direct and one antagonist, tension, and ally;
- separate reserve custody for three direct and 23 graph candidates;
- the prompt, strict response schema, model, endpoint, seed, output ceiling,
  provider policy, and all relevant hashes;
- one Gemini 3.1 Flash-Lite attempt through OpenRouter's pinned Google Vertex
  endpoint;
- no fallback, retry, healing, or parallel call;
- a maximum estimated and accounted cost below `$0.01`.

The full conversation was not replaced with a fact-stripped summary. R3 kept
the source conversation and original advice for the final reasoner. The
fact-stripped graph abstraction remains only the deterministic pressure path,
consistent with the constitution.

## What happened

The call returned HTTP 400. OpenRouter identified Google as the provider, and
Google's raw status was `INVALID_ARGUMENT` with no offending field named. No
generation ID, candidate, token usage, or exact cost was returned.

Cost must therefore be stated carefully:

- exact provider-reported cost: unavailable;
- conservative budget accounting: `$0.00816425`, the full pre-reserved
  worst-case amount;
- frozen total budget: `$0.01`;
- claim about what the provider actually charged: none.

The original raw error is retained locally outside Git because it contained a
private account identifier. The repository contains a hash-linked redacted
copy. This preserves exact local custody without publishing account data.

## Evaluation vector

R3 does not collapse this result into a quality score.

| Dimension | Result | Meaning |
| --- | --- | --- |
| Source grounding | not evaluable | No candidate was generated. |
| Apply/reject/park quality | not evaluable | No dispositions were generated. |
| Non-forced graph contribution | not evaluable | No reconsideration occurred. |
| Original-advice preservation | not evaluable | No revised answer exists. |
| Unsupported-claim leakage | not evaluable | No generated claims exist. |
| Private over-absorption | not evaluable | No generated answer exists. |
| Public bloat and hedging | not evaluable | No generated answer exists. |
| Exact cost and failure custody | partial | Failure custody and bounded accounting passed; exact cost was unavailable. |

The R3 semantic exit condition was not met. The quiet control was correctly not
authorized.

## Provider-free diagnosis

The evidence identifies a problem class, not an exact cause.

Established:

- Gemini 3.1 Flash-Lite supports structured output and has returned valid
  strict-schema results in smaller Lolla probes;
- the request reached the selected Google provider, so this was not a model
  name or provider-selection miss;
- the frozen R3 row schema asks for 14 properties and repeats 11 `minLength`
  and 11 `maxLength` constraints;
- Google rejected the request before inference and named no offending field.

Current Google documentation says Gemini structured output supports only a
JSON Schema subset. For strings it documents `enum` and `format`, not length
constraints, and it warns that large or deeply constrained schemas can be
rejected. OpenRouter likewise documents that invalid schemas can cause request
failure. See [Google's structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output)
and [OpenRouter's structured-output documentation](https://openrouter.ai/docs/guides/features/structured-outputs).

The most likely class is therefore Google structured-schema subset or
complexity interoperability. We cannot claim that `minLength`, `maxLength`,
schema size, the reasoning configuration, or any other single argument caused
the failure because the provider did not identify it and smaller historical
requests used some of the same constraints successfully.

## What works and what remains unknown

Works now:

- complete source and original-answer preservation;
- current R2 pressure-portfolio replay;
- bounded active and reserve custody;
- exact prompt/schema/request hashing;
- one-call and one-cent enforcement;
- durable started-before-transport evidence;
- failure preservation, privacy-safe publication, and no automatic recovery;
- vector review gating that refuses to score an absent answer.

Still unknown:

- whether the cheap fresh reasoner applies, rejects, or parks pressure well;
- whether graph pressure contributes without being forced;
- whether useful original advice survives;
- whether the public answer stays compact and decisive;
- whether a quiet case demonstrates restraint;
- whether the pressure path adds value beyond a strong fresh neutral control.

## Next boundary

Return provider-free before R4 or another R3 attempt:

1. Project the response contract onto Google's currently documented JSON
   Schema subset and move text-length enforcement into deterministic local
   validation.
2. Reduce schema complexity without reducing semantic custody. Keep all nine
   pressure identities and dispositions, but do not ask one provider schema to
   encode every business rule.
3. Add a local provider-compatibility lint and fixtures derived from the
   successful smaller Gemini requests already in this repository.
4. Rebuild and freeze a new request under the same no-retry, no-fallback,
   no-healing, no-premium, one-cent boundary.
5. Require new explicit authorization before any further provider attempt.

This is a transport repair, not permission to redesign the architecture or add
deterministic semantic gates.

## Evidence

- Frozen contract: `docs/evals/lolla-r3-fresh-consumer-pressure-contract-v1.json`
- Authorization: `docs/evals/lolla-r3-fresh-consumer-pressure-authorization-v1.json`
- Preflight bundle: `research/lolla-r3-fresh-consumer-2026-07-13/preflight/pressure-bundle.json`
- Preserved call result: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r1/pressure-call-result.json`
- Redacted provider error: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r1/provider-error-redacted.json`
- Vector closeout: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r1/failure-closeout.json`
- Terminal R3 result: `research/lolla-r3-fresh-consumer-2026-07-13/pressure-r1/r3-result.json`
