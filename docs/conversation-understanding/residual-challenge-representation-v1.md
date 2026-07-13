# Residual Challenge Representation v1

Status: provider-free contract passes local structural and adversarial tests; no model-backed recall evidence and no runtime effect  
Date: 2026-07-13

## Why this lane exists

The affordable full-nine program established two different facts:

- Case 07 showed that the factored mechanism path can recognize a well-treated
  conversation and stand down for about one cent.
- Case 01 showed that the same path can faithfully classify every represented
  mechanism and still miss the product's valuable pressure. The post-grant
  operating horizon and later service or land-use expectations were not in the
  starting, current, or qualification records and were not targets of the nine
  controlled mechanisms.

That is a representation failure, not evidence that Gemini 3.1 Flash Lite is
too weak. A larger model cannot be fairly blamed or credited for information
and a target it never receives.

This new lane does not replace position roles, qualifications, or controlled
reasoning mechanisms. It represents a different question:

> Given the user's own evidence and intended path, what source-grounded
> dependency, second-order effect, affected party, time horizon, or break
> condition may still deserve a question?

## Deliberate architecture

```text
authoritative conversation evidence
  ├─ existing role + mechanism lane (unchanged)
  └─ residual lane
       1. user-evidence-only candidate discovery (probabilistic)
       2. full-joint-conversation coverage review per candidate (probabilistic)
       3. evidence, identity, cap, and completeness validation (deterministic)
       4. explicit portfolio tier from declared coverage (deterministic policy)
       5. later fact-free abstraction and graph recall (not yet built)
```

Discovery does not see the prior assistant answer or compact role summaries.
That protects the chance to formulate a structurally different question before
the prior conversational frame can domesticate it. Discovery may return at
most three candidates and may return zero. Every candidate must:

- cite exact supplied user-evidence IDs;
- remain a question or conditional hypothesis, not an external factual claim;
- name an applicability condition;
- state the risk if ignored;
- state the boundary that prevents the lens from being forced;
- use a small controlled kind vocabulary without inventing a mental-model name.

Coverage is a separate semantic job. It receives one candidate plus the full
joint evidence and declares exactly one of:

- `operationalized`;
- `acknowledged_only`;
- `not_covered`;
- `ambiguous`.

The deterministic join reads only that explicit model-authored label:

| joint coverage | portfolio tier | active pressure eligible |
| --- | --- | --- |
| `not_covered` | `active_working_set` | yes |
| `acknowledged_only` | `active_working_set` | yes |
| `ambiguous` | `edge_reserve` | no, but preserved and inspectable |
| `operationalized` | `covered_receipt` | no, but preserved and inspectable |

This tier is attention policy, not a quality or relevance verdict. No candidate
is deleted. The covered and ambiguous items remain available in the private
portfolio and receipt.

## Deterministic boundary

`engine/system_b/residual_challenge_representation_v1.py` may:

- validate packet hashes and exact evidence identities;
- require discovery evidence to belong to user messages;
- reject duplicate, missing, invented, or out-of-order candidate IDs;
- enforce candidate and citation caps;
- require one coverage result for every discovered candidate;
- map explicit coverage values to declared portfolio tiers;
- preserve a model-authored empty result as empty rather than inventing work.

It may not:

- decide whether the candidate is sensible from its words;
- search for case keywords or chronological patterns;
- infer that a topic was covered from transcript prose;
- silently delete covered or ambiguous candidates;
- route case-local prose directly into the deterministic mental-model graph.

The current `graph_handoff` is deliberately blocked. A separate probabilistic
abstraction must later turn any case-local residual question into a fact-free
reasoning pattern before deterministic graph recall. This prevents facts from
driving graph traversal while avoiding a brittle hand-written translator.

## Local evidence

The contract currently passes 10 provider-free tests plus the existing
mechanism regression set. The tests cover:

- exact discovery evidence custody;
- exclusion of assistant-only evidence from discovery;
- candidate identity gaps and packet tampering;
- separate coverage and complete joins;
- uncovered active pressure;
- ambiguous edge preservation;
- operationalized covered-receipt preservation;
- invalid or missing coverage citations;
- honest model-authored empty output;
- failure-closed behavior when a candidate lacks coverage.

Two tests use the actual frozen naturalized evidence:

- Case 01 can represent the missed recurring operating-capacity question as
  an active, source-grounded, non-factual pressure.
- Case 07 can represent the recurring-hours/permanent-staffing question and
  preserve it as already operationalized rather than manufacturing public
  pressure.

These are hand-authored provider-free fixtures. They prove that the contract
can carry the required distinctions. They do not prove that a model will
discover the Case 01 candidate, avoid noise on Case 07, or produce useful fresh
reconsideration.

## Cost and next evidence boundary

No provider call was used to design or test this contract. Gemini 3.5 remains
disallowed for routine testing. The next possible paid experiment is one
frozen Case 01 discovery call with Gemini 3.1 Flash Lite and, only for returned
candidates, separate minimal-reasoning coverage calls. The prospective ceiling
should be four calls and `$0.01`, with zero retries, fallbacks, or response
healing.

That call is not yet authorized. Before authorization, freeze exact source
bytes, request hashes, schemas, seeds, the expected source-review opportunities,
and these stop rules:

1. If discovery omits both Case 01 protected opportunities, stop prompt tuning
   and reclassify model or representation capability.
2. If discovery floods the quiet Case 07 source with generic warnings, do not
   add deterministic relevance gates; refine the probabilistic target or stop.
3. If Case 01 passes, freeze one quiet transfer before changing the prompt.
4. Do not build fact-free abstraction, graph mapping, fresh reconsideration,
   or runtime integration until candidate recall and restraint both pass.

## Claims not made

This contract does not establish useful pressure, mental-model selection,
graph value, reconsideration value, real-user usefulness, production
reliability, or a premium product tier. It adds a locally valid place for the
missing kind of question to exist.
