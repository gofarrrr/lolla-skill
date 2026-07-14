# R4 separated-surface experiment execution A1 result

Date: 2026-07-14

Status: terminal first failure; source-first review complete

Frozen decision: `semantic_result_not_evaluable`

Execution evidence remains local and unpublished.

## Executive result

The experiment did not complete its twelve-call matched comparison. The runner
completed six calls, then stopped correctly at ordinal 7 when the provider
returned `finish_reason: "error"` without a usable usage/cost payload. No call
was made after that failure, and no retry or replacement was attempted.

The six completed calls cover only the two difficult quiet controls. They show
a partial pattern: separated decision-gap calls returned correct zero for both
controls, while separated dependency calls continued to emit false positives.
The paired calls emitted false positives on both surfaces. This is useful
partial restraint evidence, but it cannot answer the scientific question
because neither positive case has a complete paired-versus-separated
comparison.

The exact frozen decision is therefore `semantic_result_not_evaluable`.

## Operational execution

- calls authorized: 12;
- calls attempted: 7;
- calls completed: 6;
- failed ordinal: 7;
- unattempted ordinals: 8–12;
- retries: 0;
- fallback models: 0;
- response healing: 0;
- model substitutions: 0;
- relationship/evaluator/embedding/graph/pipeline/runtime calls: 0;
- first-failure stop: satisfied;
- authorization: consumed;
- second execution authorized: no.

The raw execution was committed in
`9f1b308ca852b86d640e481a32bc6efc8f5320e9` before protected target access.

## Pre-transport official-practice check

On 2026-07-14, immediately before transport, the operator was rechecked against
official primary documentation without changing the frozen contract:

- Google model documentation:
  `https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite`;
- Google Gemini pricing:
  `https://ai.google.dev/gemini-api/docs/pricing`;
- OpenRouter model/provider page:
  `https://openrouter.ai/google/gemini-3.1-flash-lite/providers`;
- OpenRouter provider routing controls:
  `https://openrouter.ai/docs/guides/routing/provider-selection`;
- OpenRouter reasoning controls:
  `https://openrouter.ai/docs/guides/best-practices/reasoning-tokens`;
- OpenRouter usage accounting:
  `https://openrouter.ai/docs/cookbook/administration/usage-accounting`.

The exact model and Google Vertex route remained available; structured output,
minimal reasoning with returned reasoning excluded, required-parameter routing,
fallback prohibition, data-collection denial, ZDR routing, and provider usage
and cost custody remained documented. Published prompt and completion prices
remained `$0.25` and `$1.50` per million tokens, within the frozen maxima. The
dedicated Google model page described the exact operator as stable, and the
Google release notes distinguished it from the retired preview alias; no
operator conflict required a pre-transport stop.

## Provider, usage, and cost custody

All attempted responses identified the served model as
`google/gemini-3.1-flash-lite` and provider as `Google`. Completed responses
reported zero reasoning tokens and satisfied returned-reasoning exclusion.

| # | Arm | Generation ID | Prompt | Completion | Total | Cost USD | Status |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Case 01 paired | `gen-1784056664-groV6QayMr77qdPXHq0r` | 5,915 | 263 | 6,178 | 0.00187325 | complete |
| 2 | Case 01 separated decision | `gen-1784056667-UEIUX2keDEpy7FDudDMn` | 5,897 | 32 | 5,929 | 0.00152225 | complete |
| 3 | Case 01 separated dependency | `gen-1784056669-db8ElqgaZF2TCiQrmNiV` | 5,905 | 171 | 6,076 | 0.00173275 | complete |
| 4 | Case 02 separated decision | `gen-1784056671-R5UaLLu8cTCCIGZYC2Yl` | 5,825 | 102 | 5,927 | 0.00160925 | complete |
| 5 | Case 02 separated dependency | `gen-1784056672-S4Pz6ZxAN96DKkRVGn6J` | 5,833 | 316 | 6,149 | 0.00193225 | complete |
| 6 | Case 02 paired | `gen-1784056675-F0SRxhX1laSHWDnGHMgn` | 5,843 | 294 | 6,137 | 0.00190175 | complete |
| 7 | Case 03 separated dependency | `gen-1784056677-voLpj0iFo0TeaFObstpT` | unavailable | unavailable | unavailable | unavailable | terminal `error` |

Completed-call totals:

- prompt tokens: 35,218;
- completion tokens: 1,178;
- total tokens: 36,396;
- provider-reported cost: `$0.0105715`;
- Case 01 cost: `$0.00512825`;
- Case 02 cost: `$0.00544325`.

The failed ordinal supplied no provider-reported cost. `$0.0105715` is the
exact cost reported by the six completed calls, not a claim that ordinal 7 was
free. The run remained far below the `$0.30` anomaly ceiling.

## Per-case paired-versus-separated result

| Case | Paired result | Separated decision | Separated dependency | Source-first conclusion |
| --- | --- | --- | --- | --- |
| Case 01 cave rescue | Three false positives across both surfaces | Correct zero | Two false positives | Separation quieted the decision surface but not the dependency surface |
| Case 02 observatory | Two false positives across both surfaces | Correct zero | Two false positives | Same partial pattern; governed dependency errors persist |
| Case 03 performance tour | Not attempted | Not attempted | Terminal failure, no admitted result | Genuine present gap and companion comparison not evaluable |
| Case 04 seed preservation | Not attempted | Not attempted | Not attempted | Genuine future dependency and companion comparison not evaluable |

## Record-level source-first verdicts

Every admitted record is a false positive:

1. Case 01 paired decision: the committee's reserved authority above a
   contingency cap was mislabeled as a current ownership gap. Aliases `e019`
   and assistant question `e020` do not establish an actual above-cap request.
2. Case 01 paired dependency: the signed radio threshold and activated reserve
   procedure (`e007`, `e023`) were mislabeled as outside machinery.
3. Case 01 paired dependency: the signed Ridge Cavern substitution (`e011`,
   `e025`) was mislabeled as a premise-breaking dependency.
4. Case 01 separated dependency: the radio joint check (`e023`) was extracted
   without the adoption and fallback evidence that makes it governed.
5. Case 01 separated dependency: the route substitution (`e011`, `e025`) was
   again mislabeled as residual.
6. Case 02 separated dependency: the signed noise threshold (`e021`) was
   mislabeled despite its automatic response and surviving alternatives.
7. Case 02 separated dependency: the board's reserved adjournment procedure
   (`e025`) was converted into an external dependency.
8. Case 02 paired decision: the deliberately scheduled 14 November choice
   (`e005`, `e007`, `e017`) was mislabeled as a present gap.
9. Case 02 paired dependency: governed noise, budget, fire, and volunteer-hour
   bounds (`e017`, `e021`) were mislabeled as residual dependencies.

Ownership was generally named correctly, but the model repeatedly converted
owned thresholds, fallback authority, and scheduled governance into missing or
reopening work. Modal and temporal language was often superficially accurate;
the semantic placement was not. No admitted record depends solely on assistant
authority, although Case 01's first paired record cites an assistant question
alongside the decisive user evidence.

## Quiet controls and genuine findings

The two separated decision-gap calls correctly returned zero. This is the only
clean restraint improvement observed. It is not enough to establish a repair:
both separated dependency calls still produced two false positives, and the
paired quiet controls failed both surfaces.

The genuine Case 03 present finding and Case 04 future dependency were not
tested under a complete matched design. Missing calls are recorded as missing,
not semantic zero and not false negatives.

## Scientific decision

`semantic_result_not_evaluable` applies because a terminal mechanical/provider
result prevented the full matched comparison. In particular:

- paired positive-case companion behavior was not observed because the paired
  positive calls were never attempted;
- separated suppression of those companions cannot be measured;
- genuine Case 03 sensitivity cannot be measured;
- genuine Case 04 sensitivity cannot be measured.

The partial quiet-control evidence suggests that task separation may reduce
decision-gap overgeneration while leaving reconsideration-dependency semantics
unsafe. That observation is not the frozen causal conclusion.

## Evidence custody

- aggregate terminal result SHA-256:
  `6ffea9213241b857f3515758c2787a436ed6b92c32316dd1edb2d2a84cad8e31`;
- raw evidence manifest SHA-256:
  `bb75c2a72e27be10b99063419f5e45dd1244bf29832901a21a1752c7b6c504be`;
- authorization-consumption SHA-256:
  `fff7d23f4a20fa9884dfca19a8ca1408ed4b46ba298097ed8259776b862a2bef`;
- raw closeout SHA-256:
  `936cf549f257807e3537ce07aaadf8d56cb2e6fe422088aec6fdd50dd0ee0363`;
- source-first review SHA-256:
  `b1f4b48f6f8c49b2f715708f57aaaeeb3e1ff83f36896d02db2d356e50dc114b`;
- execution closeout SHA-256:
  `925e096855c609308c956b9d50fc81f423d06a1c2b1b14ea359e0e4bf7bf4e70`;
- complete execution evidence manifest SHA-256:
  `c26fc1f609ba30c174e889463c1864576ae042da2d8cfef58e943b5afa011e6b`;
- temporary authorization SHA-256:
  `e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf`.

The temporary authorization was removed before the raw commit and was not
committed. No provider key value was printed or preserved.

## What this establishes and does not establish

This run establishes that the frozen runner enforced first-failure custody and
that the two separated decision-gap calls were quieter than their paired
counterparts on the two controls. It also establishes that separated dependency
calls retained governed-machinery false positives.

It does not establish whether task separation suppresses opposite-surface
companions on positive cases. It does not establish reader safety, product
usefulness, real-conversation transfer, or permission to integrate.

## Next founder decision

The only next decision is whether to publish this terminal execution evidence.
No retry or second execution is authorized. Any future paid run would require a
new founder decision that explicitly confronts whether the mechanical failure
justifies another full execution or whether the persistent dependency-surface
errors already make further spend scientifically unattractive.
