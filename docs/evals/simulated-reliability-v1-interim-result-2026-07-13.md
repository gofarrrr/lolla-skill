# Simulated reliability V1 interim result

Status: all transfer cases attempted; paid continuation paused; provider-free review complete enough for a V2 direction  
Date: 2026-07-13

## Plain-language result

We built a demanding simulated test rather than assuming that thoughtful-looking
outputs mean the system works. The system received long, ambiguous, multi-turn
conversations; extracted the user's changing position and qualifications;
classified nine controlled reasoning mechanisms; deterministically assembled
canonical mental-model pressure; and either produced fresh reconsiderations or
stood down. Every attempt, failure, prompt result, cost, and public arm was kept
in a self-contained receipt.

The custody machinery is substantially stronger than the semantic machinery.
The system can preserve what it did and fail closed. It is not yet reliable at
deciding when a strong-looking conversation still needs pressure. In the seven
operationally complete transfer cases it stood down seven times. Evidence-based
source review judged five of those stand-downs defensible and two false. The
false stand-downs reveal an upstream interpretation problem: the current role
packet represents positions and explicit qualifications well, but can miss an
important challenge that neither speaker has named. In one case the opportunity
never entered the role packet; in another it entered the broader interpretation
but the answer-coverage classifier treated the concern as already
operationalized.

This is directly related to Lolla's intended value. A system designed to expose
unknown unknowns cannot rely only on a compact restatement of already stated
positions and qualifications. The repair must remain probabilistic and
source-grounded; adding brittle chronological or keyword gates would violate
the constitution.

## What worked

- Twelve naturalistic simulated transfer conversations were frozen before use.
- Seven cases completed the frozen extraction, mechanism, routing, and public-
  arm path with no between-case tuning.
- Five completed cases correctly stood down, showing that the system does not
  manufacture pressure merely to appear useful.
- Deterministic identity, graph traversal, candidate bounds, ordering, hashing,
  and custody remained separate from probabilistic interpretation.
- Failures were not hidden, healed, retried, or converted into valid-empty
  results.
- All twelve JSON and Markdown receipts pass source, contract, call-artifact,
  usage, failure, and self-containment integrity checks.
- The receipts deny a proof-of-work score, trust score, quality badge, or claim
  that process custody proves wisdom.

## What did not work

- Two of seven complete cases falsely stood down.
- One case failed the role join because the starting-position task admitted no
  record even though current-position and qualification records existed.
- Four cases stopped at their first call when OpenRouter credit could not cover
  the frozen 6,000-token ceiling. Lowering the ceiling or retrying would have
  changed the sealed experiment.
- The seven complete cases produced no active pressure arm, so transfer did not
  test direct-versus-graph contribution.
- The exact blinded comparative review contract was frozen only after T1 began.
  T1 can support diagnosis, not a clean causal usefulness claim.
- Fresh-reader comprehension and human receipt usefulness are still untested.

## Cost and model decision

The screenshot's `$3.15` for Gemini 3.5 Flash matches the experiment ledger:

| stage | attempted calls | operationally `ok` | provider-reported cost |
| --- | ---: | ---: | ---: |
| calibration and repairs | 62 | 57 | `$2.179059` |
| untouched transfer T1 | 34 | 30 | `$0.9705315` |
| total | 96 | 87 | `$3.1495905` |

Three additional calibration calls reached the provider and incurred cost but
failed local semantic or shape validation; two calibration attempts were HTTP
400 failures. Four transfer attempts were HTTP 402 failures with no positive
cost. The exact ledger therefore reconciles the dashboard spend without
treating paid responses as successful product work.

Gemini 3.5 Flash was a defensible experimental choice because the cheaper
Gemini 3.1 Flash Lite had already shown combined schema and semantic-boundary
problems, and V1 intentionally held one model constant across semantic stages.
The result does **not** justify Gemini 3.5 Flash as the production default. The
model was expensive largely because calibration legitimately exposed and
repaired contracts before transfer. It still produced false stand-downs,
variance, one role failure, and costly invalid outputs.

No more paid V1 calls are authorized until the founder chooses whether to fund
the exact frozen continuation. A future production-model choice must be a
separate price/reliability comparison on the already frozen task contracts. It
must compare semantic fidelity, restraint, schema compliance, variance, and
cost—not price alone and not answer polish.

## What the receipts prove—and do not prove

The receipts now prove that the recorded conversation, interpretation,
deterministic candidate custody, routing decision, public arms, provider calls,
usage, and failures have not been silently changed. They make the run auditable.

They do not prove that the interpretation was accurate, that enough reasoning
work was done, that pressure was useful, that the recommendation was correct,
or that a future reader should trust the output. That distinction is the reason
the integrity report contains no scalar score. A frozen cold-reader contract
now covers one correct stand-down, one false stand-down, one role failure, and
one credit failure; actual fresh-agent and human comprehension remain pending.

## V2 direction, without architectural drift

1. Preserve V1 unchanged as evidence. Do not tune transfer outputs after seeing
   them.
2. Redesign only the probabilistic representation boundary so it can propose
   source-grounded residual challenges and omitted decision dependencies in
   addition to stated positions and qualifications.
3. Keep the deterministic layer limited to canonical identity, graph traversal,
   structural bounds, ordering, provenance, replay, and custody. It must not
   decide messy conversational meaning.
4. Locally test the new representation against the two false stand-downs, five
   correct stand-downs, and adversarial fixtures before any provider call.
5. Run a small frozen model/value comparison for each microtask before choosing
   a production default; a stronger model may be reserved for the narrow stages
   where it earns its cost.
6. Only then run a new untouched transfer and the prospectively frozen blind and
   cold-reader reviews.

The immediate decision is deliberately narrow: either add enough OpenRouter
credit to complete the remaining four cases under the already frozen Gemini
3.5 contract, or close T1 as a valuable but incomplete V1 and move to the
provider-free V2 representation redesign. Changing the model or token ceiling
inside T1 would invalidate the comparison.

The continuation is now frozen separately in
`docs/evals/simulated-reliability-v1-credit-continuation-contract-v1.json`.
It admits only Cases 09–12, preserves the exact V14 model, provider, prompts,
schemas, task limits, graph rules, and numeric primary seed, and keeps the
original HTTP 402 artifacts intact. Case 06 is explicitly excluded because its
semantic join failure is real evaluation evidence, not a funding interruption.
The continuation permits at most 24 calls and `$2.00` provider-reported cost,
but currently authorizes zero calls until the founder cost decision and
sufficient credit are present.

## Completion audit and stability repair

The requirement-by-requirement evidence matrix is at
`research/simulated-reliability-v1-evaluation-2026-07-13/evidence-matrix.json`.
It distinguishes supported mechanism evidence from mixed, partial, and untested
product claims. Its current conclusion is intentionally not a score: corpus,
hybrid mechanism, integrity, receipt construction, and non-scalar evaluation
are supported; runtime freeze, transfer execution, restraint, attribution, and
operability are partial or mixed; usefulness, stability, and V1 receipt
reconstruction are not established.

The audit also found that the V1 plan called for a cross-stratum repeat subset,
but V14 named only the primary run and never prospectively selected the subset.
That omission cannot be rewritten away. A bounded repair contract is now frozen
before any repeat call. It selects one case per prospective stratum by the
lexicographically smallest frozen source hash: Case 01 for pressure, Case 07 for
stand-down, and Case 12 for park. It uses `repeat_2`, seed 202, the unchanged
Gemini 3.5 runtime, at most 18 calls, no retries, and a `$2.00` provider-cost
ceiling. The contract currently authorizes zero calls and states that selection
occurred after T1 results were visible, so it can measure observed variance but
cannot create a clean pre-primary stability claim.

The original V1 plan is hash-locked by the runtime contract and remains byte-
exact. Current findings live only in new dated artifacts; historical evidence
is not edited to look more complete than it was.

## Later affordable-operator addendum — 2026-07-13

The founder subsequently authorized a separate, bounded affordable-model
investigation. It does not reopen, repair, or overwrite T1. Its result is
documented in
`docs/evals/simulated-reliability-v1-affordable-model-selection-result-2026-07-13.md`.

Gemini 3.1 Flash Lite is now the testing candidate for small decomposed semantic
microtasks, with low reasoning for tiny classification schemas. The full
initial investigation used 21 provider calls and `$0.042771112`, including
failures. Later full-nine validation brought the cumulative affordable campaign
to 45 calls and `$0.065948112`.
The current mechanism reference separates model-authored observation and
integration factors from assistant coverage, then derives controlled status and
routing in deterministic code. Case 07 passed full-nine stand-down review. Case
01 passed per-mechanism source and evidence review but did not activate the
source-review pressure because the residual long-term dependency was absent
from the bounded role/mechanism representation. This is a representation gap,
not current evidence for a more expensive model. No production model or premium
product tier has been selected. Existing Gemini 3.5 outputs remain preserved
reference evidence and should not be used for routine development testing.
