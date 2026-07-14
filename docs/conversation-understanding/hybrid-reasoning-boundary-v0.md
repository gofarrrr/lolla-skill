# Hybrid Reasoning Boundary v0

Status: binding architecture rule for new core work  
Date: 2026-07-10  
Applies to: conversation interpretation, reasoning-pattern projection, graph
recall, pressure application, reconsideration, and the one-run receipt  
Machine-readable contract: `hybrid-reasoning-boundary-v0.json`

## Governing rule

> LLMs interpret messy meaning. Deterministic systems constrain claims,
> preserve evidence, perform declared reproducible transformations, and keep
> the process auditable.

The deterministic middle is a courier, validator, and accountant. It is not a
substitute semantic reasoner.

This is a consolidation of existing Lolla doctrine, not a new product
direction. Earlier plans already state that semantic extraction must be
LLM-driven, that Python must not infer semantic fields from keywords, and that
activation judgment belongs to the LLM. This document makes that boundary
canonical and applies it to the semantic-kernel work after the 12-case corpus.

The design is also consistent with the architecture described in
[*Dive into Claude Code: The Design Space of Today’s and Future AI Agent
Systems*](https://arxiv.org/html/2604.14228v1): model judgment is given broad
latitude inside an operational harness responsible for enforcement, routing,
context, recovery, and persistence. Lolla adopts the separation, not every
implementation choice in that paper.

## Three authorities

### 1. Semantic authority: probabilistic

An LLM or human reviewer owns judgments that require reading meaning in
context, including:

- what the user is deciding;
- which question is currently operative;
- whether a later statement corrects, pressures, or changes an earlier frame;
- what an assistant passage commits to, qualifies, revises, defers, or gates;
- whether a topic was answered, superseded, under-carried, or unresolved;
- what is weak evidence, an unknown, a value, or an obligation;
- which abstract reasoning mechanisms are plausibly present;
- whether a recalled mental model actually applies to the case;
- how selected pressure should affect reconsideration.

These outputs are interpretations. Structure, repetition, or model confidence
does not turn them into facts.

### 2. Structural authority: deterministic

Deterministic code owns operations whose correctness can be specified without
interpreting the case:

- capture, hashing, versioning, and append-oriented persistence;
- exact quote and offset validation;
- schema, enum, cardinality, and reference-integrity checks;
- stable IDs, deterministic deduplication of identical objects, and sorting;
- retry limits, budgets, caps, and failure recording;
- graph traversal and candidate expansion under a declared graph and config;
- lookup and delivery of source-backed model affordances;
- fact-leak and privacy lint over the sealed routing projection;
- run comparison, reproducibility checks, and trace assembly;
- release, custody, and review-status enforcement.

Deterministic success proves that a declared operation was followed. It does
not prove that the upstream interpretation was semantically correct.

### 3. Decision authority: human or designated reasoning agent

The final judgment remains with the user or the explicitly designated
reasoning agent. Lolla presents source-linked pressure and uncertainty; it does
not claim that a graph route, mental model, or revised answer is true merely
because the process was valid.

## Boundary table

| Job | Semantic owner | Deterministic owner |
| --- | --- | --- |
| Read the conversation | Interpret questions, pressure, stances, uncertainty, and thread treatment | Preserve source and verify cited evidence |
| Build semantic events | Propose meaning, labels, relations, confidence, and alternatives | Validate shape, evidence, identifiers, and allowed vocabulary |
| Resolve ambiguity | Judge context or preserve multiple plausible readings | Prevent silent conflict deletion; record disagreement |
| Build reasoning patterns | Propose abstract mechanisms from source-linked semantics | Validate references and remove prohibited factual content |
| Use the graph | Judge whether recalled material applies | Reproducibly recall and expand candidate models/relations |
| Apply pressure | Explain relevance, set aside weak candidates, and reconsider | Deliver reviewed substrate and record disposition |
| Preserve the run | Explain interpretations and non-claims | Hash, serialize, link, and render the complete lineage |

## End-to-end boundary

```text
authoritative conversation
  -> LLM semantic proposals
  -> deterministic evidence/contract validation
  -> ambiguity-preserving semantic ledger
  -> LLM reasoning-pattern hypotheses
  -> deterministic fact-leak validation and sealed projection
  -> deterministic graph candidate recall/expansion
  -> LLM applicability judgment and pressure wording
  -> contextual reconsideration
  -> deterministic lineage and receipt assembly
```

No stage may silently replace the authoritative conversation. Every projection
must retain a path back to its source or explicitly declare that it is an
unsupported hypothesis.

## Focused probabilistic decomposition

The probabilistic side must not become monolithic merely because semantic
judgment belongs to an LLM. When independently addressable semantic jobs
compete inside one prompt, instruction load can reduce both coverage and
stability. Lolla therefore applies context engineering inside the semantic
authority:

- each reader receives the authoritative conversation but only the
  instructions and output schema for its assigned semantic job;
- outputs that share a real interpretive dependency may be grouped, while
  unrelated fields should not compete in the same response merely to reduce
  call count;
- deterministic fan-in validates shapes, evidence, references, and custody;
  it does not reconcile meaning or repair a weak reader with semantic rules;
- emitting a candidate and choosing among a wider hypothesis set are distinct
  semantic jobs. Unless a separate selection read is justified and measured,
  the ledger must say that unreturned hypotheses and explicit disposition are
  unobserved;
- decomposition granularity is an empirical choice. It must be tested through
  bounded ablations rather than assumed from framework fashion;
- parallel execution is a later latency optimization, not evidence of semantic
  quality. It should be introduced only after reader contracts are stable.

This rule is informed by the supplied essay [*Your LLM Pipeline Is Slow
Because Your Agents Do Too Much*](https://www.sully.ai/research/context-engineering-over-iteration)
and, more importantly, by Lolla's SK3 corpus result: the four-job joint reader
increased output volume while semantic stability fell. Lolla adopts the narrow
context and typed fan-in principle, not a general multi-agent architecture.

Step 6 reconsideration is not an iterative correction loop for semantic
extraction. It is the product's user-facing pressure step after deterministic
model recall. The decomposition evidence does not authorize removing or
expanding Step 6.

## What deterministic code must not do

Deterministic code must not:

- assign the current operative question from recency or question marks;
- infer that the user changed their mind;
- infer a correction, value, concern, obligation, or relationship constraint
  from keywords;
- decide whether an assistant passage is a revision or qualification;
- decide whether a topic was emotionally or logically under-carried;
- evaluate natural-language `use_when` or `do_not_use_when` affordances against
  case text;
- choose the finally applicable mental model by topic or example similarity;
- merge semantically similar interpretations merely to make output stable;
- fill missing semantic fields with generic defaults;
- turn a corpus annotation or prior case into a production rule;
- convert an evaluation threshold into a runtime claim of semantic truth.

If deterministic code must read the natural-language meaning of the case to
perform its job, that job is presumptively on the wrong side of the boundary.

## What deterministic code may reject

The harness may reject or quarantine an output when the failure is mechanical:

- quote not found in the claimed source turn;
- invalid speaker, turn, offset, object ID, or source hash;
- malformed schema or unsupported controlled-vocabulary value;
- dangling or circular reference where the contract forbids one;
- factual or private content inside a fact-free graph projection;
- missing required provenance for a routing-eligible pattern;
- budget, retry, custody, or release-policy violation.

Rejection must retain a reason. The harness must not replace the rejected
semantic content with its own interpretation.

## Ambiguity and loss policy

Ambiguity is data, not a validation failure.

- Multiple plausible current questions may coexist.
- A stance may carry a primary relation and credible alternatives.
- A topic may be plausibly under-carried without being provably dropped.
- Cross-turn derivations must preserve every supporting excerpt or offset.
- Candidate interpretations must not disappear merely because a later reader
  prefers another interpretation.
- Invalid evidence may be quarantined, but the rejection event remains in the
  trace.

The preferred representation is an append-oriented candidate ledger plus a
current interpreted projection. Reconciliation adds relations and status; it
does not destructively rewrite source or erase dissenting candidates.

## Graph-specific rule

The graph is a deterministic source of structured difference, not a semantic
judge.

It may:

- receive only the sealed, fact-free reasoning-pattern projection;
- traverse declared nodes and edges;
- expand neighboring or conflicting candidate models;
- enforce candidate budgets and record paths;
- return the same candidate set for the same packet, graph, and config.

It may not:

- parse the original messy conversation;
- treat graph proximity as applicability or truth;
- use factual topic similarity as reasoning-pattern evidence;
- decide the final pressure or recommendation;
- hide candidates that an LLM set aside or rejected.

“Selected by the graph” means mechanically recalled under declared rules. It
does not mean semantically applicable. Applicability remains an LLM/human
judgment with a recorded disposition.

## Evaluation boundary

Evaluation may be deterministic even when the evaluated object is semantic.
For example, code may compute exact-span recall, repeatability, citation
validity, and fact leakage. Those measurements are evidence about a reader;
they are not a replacement reader.

No single metric is a quality certificate:

- exact-span recall favors inspectability and may under-credit faithful
  paraphrase;
- repeatability may repeatedly select the wrong item;
- schema validity says nothing about semantic adequacy;
- a complete receipt proves observable process, not good reasoning;
- corpus thresholds are research promotion gates, not runtime semantics.

Semantic promotion decisions require the metrics together with source-first
inspection and explicit review of failure clusters.

## Audit, verification, and proof language

Research on human trust in fluent AI output adds a product-level constraint:
the audit itself can become a second persuasive narrative. More structure,
explanation, graph detail, or receipt completeness may increase trust without
improving the underlying decision.

Lolla therefore uses these terms narrowly:

- **audited** means the declared capture, interpretation, pressure, and
  accountability process ran and left inspectable artifacts;
- **source-grounded** means a claim or interpretation has declared evidence
  that passed the applicable custody checks;
- **verified** is reserved for the specific fact, constraint, or operation
  checked by an identified external source, tool, formal rule, human, or
  domain reviewer;
- **proof of work** may describe observable process custody, but never proof
  that the reasoning was deep, useful, correct, or safe.

The receipt must expose non-claims, missing verification, rejected or
incomplete provenance, and independent-review status. It must not collapse
those dimensions into a quality badge. Critique is not verification, graph
consistency is not truth, and process completeness is not decision approval.

## Drift tests for every new core change

Before merging a new deterministic rule, answer:

1. Can the rule be evaluated without understanding natural-language case
   meaning?
2. Does it validate, transport, recall, budget, or account rather than judge?
3. Does it preserve ambiguity and rejected candidates?
4. Would new phrasing with the same meaning break it?
5. Is it being added to compensate for an LLM weakness that should instead be
   addressed with better material, context, or evaluation?
6. Can its output be described without claiming semantic correctness?
7. Is one LLM call being asked to perform independently addressable semantic
   jobs that could be tested with narrower instructions and schemas?

If answers 1–3 are no, or 4–5 are yes, stop and redesign the boundary.

## Change control

This document governs new core work. Historical reports remain historical.
When a newer plan conflicts with this boundary, the boundary wins unless the
founder explicitly approves a versioned replacement that explains:

- why the semantic/structural allocation changes;
- what failure the change addresses;
- why probabilistic judgment plus deterministic validation is insufficient;
- how brittleness, bloat, and casuistry are prevented;
- how the change will be falsified and rolled back.

## Existing doctrine consolidated here

- `plans/conversation-first-context-engineering-roadmap.md`, “Keep
  probabilistic edges and deterministic middle”
- `plans/knowledge-substrate-roadmap-2026-05-04.md`, “Non-Negotiable Doctrine”
  and “Affordance Records Are Knowledge Documents, Not Matching Rules”
- `plans/knowledge-use-schema-2026-05-04.md`, “Activation Judgment Belongs to
  the LLM, Not to Python”
- `plans/lolla-core-reasoning-audit-assessment-and-prd-2026-07-09.md`, intended
  deterministic boundary and Layer C–E design
- `docs/conversation-understanding/reasoning-pattern-packet-v0.md`,
  “Determinism boundary”
