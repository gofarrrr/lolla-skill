# Lolla Product Constitution v0

Status: binding development house rules
Date: 2026-07-10

This document prevents the product from drifting while individual experiments
optimize one local problem. It consolidates the governing principles already
present in:

- `docs/how-it-works/problem-and-thesis.md`;
- `references/private-enrichment-treatment.md`;
- `plans/lolla-solver-control-layer-prd-2026-05-19.md`;
- `research/pre-step6-reasoning-portfolio-contract-2026-05-20.md`;
- `docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`;
- `docs/conversation-understanding/lolla-evaluation-doctrine-v0.md`.

## Product goal

Lolla is not an answer optimizer and does not promise a better conclusion.

Its job is to make a serious reasoning process less likely to remain trapped
inside the smooth path created by the original conversation. It preserves the
conversation, surfaces structurally different pressure from a curated
substrate, makes that pressure difficult to dismiss silently, and records how
the reasoner used, rejected, deferred, or privately guarded against it.

The desired output is not agreement with Lolla. It is accountable
reconsideration.

```text
Lolla supplies different pressure.
The reasoner retains freedom of conclusion.
The human retains responsibility for the decision.
The receipt preserves what happened without certifying the outcome.
```

## The house rules

### 1. The raw conversation remains authoritative

No summary, semantic index, graph projection, or receipt replaces the complete
conversation. Compression is navigation and attention control, not a new
source of truth.

### 2. Cap prose, not possibility

The governing portfolio doctrine is:

> Broad availability, compact representation, delayed rejection.

The system may reduce inline detail. It must not silently erase source-backed
or graph-surfaced edge material merely because an intermediate model considers
it low-fit, strange, or unlikely to change the answer.

### 3. Preserve a portfolio, not only a shortlist

The private Step 6 context should distinguish:

- a small active working set with detailed pressure;
- a compact edge/latticework reserve for off-frame or contrarian pressure;
- weak and negative-space receipts;
- parked-but-preserved items with reactivation conditions;
- expansion references to the full archive.

The system should prefer:

```text
Step 6 saw an edge receipt and rejected it with a reason.
```

over:

```text
An upstream selector removed the edge receipt because it did not fit the
current narrative.
```

### 4. Pressure is a hypothesis, not a verdict

Graph paths, embeddings, model chunks, and mental-model labels explain why an
item became available. They do not prove that it applies. Every pressure must
carry a strongest plausible application, a cheap or concrete test, a boundary,
a risk if forced, and a risk if ignored.

### 5. Freedom of conclusion, not freedom from consideration

The reasoning consumer may use, reject, defer, or keep a candidate private. It
may not dismiss selected material with an empty “not relevant.” A valid
rejection names the attempted application, the failed condition, and what
would go wrong if the lens were forced.

`not_considered` is reserved for a real custody failure: malformed,
inaccessible, or technically unusable material. A readable item judged
duplicate, already covered, or irrelevant was considered and must be recorded
as a grounded rejection. The ledger may not launder semantic judgment into an
apparent inability to inspect the material.

### 6. Deterministic code does not understand messy meaning

LLMs and humans interpret language, relevance, ambiguity, and applicability.
Deterministic code validates exact evidence, hashes, schemas, caps, source and
graph references, custody, replay, protected diversity slots, and ledgers.

No keyword gate, reader-family hierarchy, event-count rule, or multi-stage
state machine may masquerade as semantic judgment.

### 7. The strange lens has protected intellectual permission

Some of Lolla's value is deliberately low-base-rate: most off-frame pressure
may be unhelpful, while one unusual denominator, incentive, inversion,
disconfirmation, opportunity-cost, lollapalooza, or negative-space lens may
break the entire frame.

Protected slots preserve diversity of inspection. They do not force public
advice or claim equal relevance.

### 8. Unknown-unknown pressure produces questions, not invented facts

Lolla may ask what external shock, omitted dependency, regime change, supply
constraint, stakeholder, or second-order effect would break the analysis. It
must not assert that a war, shortage, election result, market event, or other
unstated fact exists. External claims require an explicit factual retrieval or
verification path.

### 9. Private breadth and public discipline are different goals

The private reasoning portfolio may be broad. The public answer should contain
only pressure that improves the decision, names a useful unresolved question,
or explains a valuable rejection. Public model-name parades, machinery
language, generic caution, and procedural bloat are failures.

### Discovery noise and visible friction have different bars

At the private discovery/portfolio stage, deliberate noise is allowed. A
candidate does not need to be proven actionable before the final reasoner sees
it. It needs valid custody, a structurally different possibility, a plausible
test, a force boundary, an ignore boundary, and a recoverable source path.
Most candidates may be rejected after serious consideration.

At the public revised-answer stage, the existing eval rule applies: visible
friction must be earned, actionable, and proportionate. A strange candidate
that fails those tests stays private or is rejected; its private presence is
not itself product failure.

```text
candidate-stage success = preserve inspectable possibility
consumer-stage success = serious accountable disposition
public-stage success = earned, actionable, proportionate friction
```

### 10. A receipt proves process, not wisdom

Calls, tokens, graph edges, dispositions, hashes, and a polished audit trail
prove activity and custody. They do not prove depth, correctness, safety, or
decision quality. The human remains accountable for the action and its
consequences.

### 11. Separate the builder from the grader

The reasoner that produced an answer has trajectory and self-justification
risk. Where feasible, downstream evaluation uses a fresh context and a blind
reviewer. The reviewer sees actual outputs and tries to falsify the claim; it
does not inherit the builder's explanation of why the work should pass.

### 12. Give agents the goal, house rules, and bar—not brittle recipes

Development agents should receive the product goal, these non-negotiable house
rules, a hard evidence bar, a bounded call budget, and authority to choose the
implementation path. They should not be micromanaged into adding special-case
gates. They continue autonomously until the bar is met or a genuinely
user-owned decision blocks progress.

## Product evils

These are failure modes to resist, even when a local metric improves.

### Premature relevance pruning

An LLM or deterministic gate removes strange pressure before the final
reasoner can inspect it. This creates false stand-down and converts Lolla into
another smooth-context summarizer.

### Context dumping

Every semantic event, graph candidate, and chunk is injected at equal weight.
Source-valid material can still distort attention, reinforce prior framing, or
drown out the decisive correction.

### Compactness Goodhart

Smaller packets are praised because they are easier to read, even when they
lost the off-frame receipt that justified building Lolla.

### Mandatory-consideration absorption

The final reasoner assumes that selected material must be true or publicly
visible. A high use rate is not success. Grounded rejection and private
guardrails are valid outcomes.

### Semantic non-consideration laundering

The consumer reads enough of a candidate to call it duplicate, irrelevant, or
already covered, but records `not_considered`. This hides a real semantic
disposition inside a custody-status label and weakens the receipt's proof of
what received a serious hearing.

### Answer-delta monoculture

The system receives credit only when the final recommendation changes. This
misses discovery value: a new falsifier, unresolved question, alternative
frame, verification need, or defensible rejection can improve the process even
when the action remains the same.

### Friction theater

The answer adds gates, checklists, caveats, or “critical thinking” language
that looks rigorous but is generic, unsupported, non-actionable, or
paralyzing.

The inverse failure also matters: applying the public actionability bar before
the final reasoner has inspected the candidate. That is premature relevance
pruning, not noise control.

### Smoothness and caution bias

A reviewer rewards polished coherence or timid balance over a rougher but more
decision-protective challenge. Lolla should not hedge the user into “it
depends.” It should make dependencies specific.

### Post-hoc mental-model storytelling

A plausible model name is used to rationalize advice after the fact. Labels
are retrieval and compression handles, not diagnoses or proof.

### Deterministic cognitive machinery

Code accumulates semantic gates until it pretends to understand the
conversation. This is brittle, hides judgment, and discards the strengths of
the probabilistic layer.

### False proof of work and trust inflation

Volume, cost, complexity, or receipt polish is presented as evidence that the
reasoning is good or safe for autonomous action.

### Same-context self-justification

The original reasoner receives pressure inside the same trajectory and talks
itself back into the original position. A fresh-session consumer is the
preferred future architecture; the current skill must record this limitation.

### Unknown-unknown fabrication

The desire for outside-the-frame thinking becomes unsupported factual claims.
Lolla should generate verification targets and conditional break scenarios,
not confident fiction.

## What good looks like

No single score represents success. A run should expose at least these
separate reads:

1. Was the full conversation preserved?
2. What direct pressure was made active?
3. What off-frame pressure remained available in the edge reserve?
4. What weak, negative-space, or parked material remained recoverable?
5. Did the consumer seriously consider each presented item?
6. Which items were used, rejected, deferred, or kept private, and why?
7. Did anything create a novel falsifier, question, frame, condition, or
   decision change beyond a strong fresh baseline?
8. Did the packet cause over-absorption, hedging, answer bloat, unsupported
   claims, or loss of useful original value?
9. Was a potentially decisive edge item suppressed before inspection?
10. Can a cold future reader reconstruct the reasoning work without mistaking
    the receipt for certification?

## Current architecture consequence

`lolla.reasoning_pressure_handoff.v0` is retained as a research candidate for
the **active working set only**. Its three pressure items and two preservation
items are not the complete future Step 6 portfolio.

The next shadow design should reuse the already implemented research contracts
for `reasoning_affordance.v1` and `step6_attention_map.v1` rather than invent a
new selector. It should bind the active handoff to:

- a compact edge/latticework reserve;
- weak or negative-space receipts;
- parked items and reactivation conditions;
- expansion refs to the full source-backed archive.

No live runtime or skill change is authorized by this constitution.

## Four-batch evidence consequence — 2026-07-10

The paired downstream, protected-edge, and reasoning-invariance batches do not
authorize promotion of the research portfolio or pattern-routing path.

- A treatment can add structurally useful pressure beyond a strong control,
  but a shared unsupported claim still blocks a clean result.
- A candidate can be seriously retained as a private guardrail without public
  bloat, but the receipt must preserve its exact identity and honestly report
  whether its effect was private or visible.
- Deterministic code can seal a fact-free controlled projection and replay a
  declared seed map, but the first LLM abstraction was not invariant to
  irrelevant factual substitution.

The product consequence is focused continuation, not architecture growth:

1. keep the current live core experimental and unchanged;
2. keep SK3 overlay, expanded portfolio handoff, and pattern-only routing in
   research;
3. harden exact identity, references, and custody deterministically;
4. judge disposition-effect consistency probabilistically or by human review;
5. define future routing hypotheses as unresolved weaknesses in the joint
   conversation trajectory, not every actor-local pattern;
6. use new cases for the next holdout and invariance work rather than tuning
   the completed evidence.

This decision preserves the constitution's central division: a semantic miss
is not repaired with a Python meaning rule.

## Accountability-cycle consequence — 2026-07-10

The next cycle strengthens custody but still does not authorize semantic or
graph promotion.

- Exact pressure IDs must survive from packet to disposition exactly once;
  control arms must not receive treatment IDs.
- Structural ledgers must copy the full supplied skeleton and declare visible
  or private effects. Deterministic validation checks those claims are present
  and internally compatible; it does not decide whether the revised prose
  truly reflects them.
- Semantic effect consistency remains a separate LLM/human review tied to the
  reviewed output hash.
- The joint-process target is now the weakness that remains unresolved after
  the complete exchange. Temporary actor-local patterns remain audit evidence
  and do not automatically route.
- New fixture evidence passed fact invariance and reasoning-change sensitivity
  at the routing surface, but the frozen exact-history scorer failed one
  defensible `not_observed` versus `resolved_in_conversation` distinction.
- Two downstream holdout attempts stopped at Stage A custody gates. No third
  case is sampled until extraction admission itself passes a frozen smoke.

Operational repairs for output-path readiness, literal quote-delimiter
recovery, and transitive hash locks may ship because they validate custody
without judging meaning. Joint-process interpretation and routing remain
research-only.

## Extraction-admission smoke consequence — 2026-07-10

The frozen Case 12 non-holdout smoke confirmed output-path readiness and full
capture, then failed when the provider boundary produced an empty parsed
object missing the required extraction fields. The extractor honestly
persisted `status: error`, but the same terminal path lost its provider call
record. Call count, tokens, served model, and cost are therefore unknown—not
zero—and another paired holdout remains blocked.

The constitutional response is deliberately mechanical. Persist the boundary
record on every terminal path, distinguish call attempt from admissible
extraction, enforce a frozen outer wall-clock ceiling, and keep semantic
interpretation with the LLM. Do not infer missing semantic fields with Python,
add a deterministic conversation-meaning gate, or rerun the failed case.

The repair now follows that boundary. It preserves the list-shaped sidecar for
existing consumers, writes it atomically after each extraction boundary,
records an explicit custody block in the extraction artifact, uses unknown
rather than numeric zero when evidence is absent, and gives future smoke
contracts a hard outer time limit. Provider-free tests, not prompt tuning,
verify the paths. At that repair checkpoint the live graph and reconsideration
remained unchanged and a paired holdout remained blocked pending a different
non-holdout smoke.

That different smoke has now passed on the already-used Case 01 fixture. The
result is deliberately narrow: the trustworthy mechanical layer worked once
under live conditions, while conversation meaning was left to the unchanged
LLM extractor. The next constitutional move is not architecture growth. It is
one prospectively frozen untouched Stage A case testing extraction plus the
existing pipeline. Control/treatment generation remains blocked until Stage A
passes and the treatment packet is frozen before either arm.

## First untouched Stage A consequence — 2026-07-10

The mechanically selected Case 05 attempt remains formally failed and will not
be rerun. Extraction and pipeline subprocesses both exited zero, every capture,
quote, call, model, embedding, cost, table, and V60 observation was inside its
frozen envelope, but the runner emitted `extractor_exit_zero` while the sealer
requested `extraction_exit_zero`. A trustworthy process cannot rename that
field after seeing the result and declare a pass.

This is exactly where deterministic machinery belongs: one shared execution
fact, one name, one integration test, and an honest stop. It is not a reason to
add semantic gates or change the graph. The private result also reported one
Lane 3 candidate dropped and no main delta findings; because Stage A failed,
those observations are not upgraded into semantic conclusions.

Gate 4 remains blocked. The prospective next move is a no-provider custody
repair followed by a newly frozen untouched case, not a Case 05 rerun or
retroactive reseal.

That prospective repair now uses a shared execution-envelope field contract
and a real runner-to-sealer integration test. The next case in the predeclared
digest order, Case 10, passed full Stage A in one attempt. Its source-first
review deliberately rejected duplicate model labels, a source-conflicting
renovation-delay reframe, a forced three-option requirement, and an unsupported
endowment diagnosis.

Three narrower pressures survived: replace invented buffer ranges with verified
inputs, prevent regret and loss framing from substituting for economics, and
apply a non-diagnostic clean-sheet all-in acquisition test. This authorizes
construction of a separately frozen Gate 4 pair, not either call. The empty
main delta card and the fact that useful candidates came from the companion/V60
reserve remain important architectural evidence for later ablation, not proof
that the graph is necessary.
