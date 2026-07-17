# How Lolla Works

This document explains the current Lolla skill from product boundary to local
archive. It describes live behavior as of 2026-07-14. Research-only readers,
future product surfaces, and historical experiments are labeled rather than
presented as runtime features.

For the short product story, start with [README.md](README.md). For binding
development rules, read
[Product Constitution v5](docs/conversation-understanding/lolla-product-constitution-v5.md).

## The System Contract

Lolla combines probabilistic interpretation with deterministic custody. The
split is about authority, not ideology:

```text
LLMs interpret messy conversational meaning.
Deterministic code owns identity, custody, exact evidence, bounds, replay,
budgets, graph traversal, and ledgers.
The graph introduces pressure; it does not certify relevance.
The reasoner may apply, reject, or park pressure.
The receipt proves what process occurred, not that the result is wise.
The human owns the decision and its consequences.
```

Two errors sit on either side of this design.

A brittle system tries to decide human meaning with keywords, turn counts, or
nested rules. A vague system gives an LLM the entire job and cannot prove what
source, context, pressure, provider action, or omission shaped the result.

Lolla uses LLMs where language remains genuinely messy. It uses deterministic
machinery where exactness is possible and necessary.

## The Whole System

```text
complete available conversation
        │
        ├── authoritative conversation.txt
        └── declared bounded processing view, if needed
        ↓
bounded LLM interpretation
  position · constraints · passages · dropped threads · frames · gaps
        ↓
four pressure lanes
  structural · companion · frame · coverage
        ↓
deterministic identity and graph recall
  direct candidates · allies · antagonists · tensions · reserve
        ↓
constitutional pressure portfolio
  no silent probabilistic deletion after admission
        ↓
reconsidering reasoner
  apply · reject · park
        ↓
updated position · Markdown memo · Observatory
        ↓
local archive · usage custody · process receipts
        ↓
human decision
```

The current live skill usually asks the same orchestrator that participated in
the conversation to reconsider its answer. That preserves rich context but
also preserves trajectory and self-justification risk. Fresh-context consumers
are evaluated separately in frozen research experiments; they are not the
default live runtime.

## Who Owns What

| Question | Owner | What the result proves |
|---|---|---|
| What is this conversation about now? | Bounded LLM interpretation | A source-referenced, fallible read |
| Which constraint is live, weakened, or unresolved? | Bounded LLM interpretation | A candidate semantic judgment, not a fact created by schema |
| What is the stable identity of a source, model, pressure, or record? | Deterministic code | Exact identity and custody |
| Which bounded graph neighbors follow from admitted canonical IDs? | Deterministic traversal | Reproducible recall, not relevance |
| Is a recalled pressure useful in this case? | Reconsidering reasoner | A visible apply, reject, or park judgment |
| Did the recorded process occur as claimed? | Deterministic receipt | Artifact, request, response, hash, bound, and ledger evidence |
| Is the revised answer wise enough to act on? | Human judgment | Nothing automatic; the human keeps authority |

A strict response schema proves that the response has the expected shape. It
does not prove that the model understood the conversation. A clean receipt
proves that the required process evidence exists. It is not a quality badge.

## The Core Objects

Lolla becomes easier to follow when five objects remain distinct.

### 1. The authoritative conversation

The complete available prose exchange between user and assistant. Tool output,
system reminders, and skill machinery are excluded from the product source.
The original prose remains authoritative even when a shorter processing view
is needed.

### 2. Semantic interpretations

Fallible LLM-authored views of the decision situation: current position,
constraints, reasoning passages, dropped threads, frames, gaps, and other
roles. Each view should declare its source, scope, uncertainty, and missingness.

### 3. Pressure

A bounded possibility placed in front of the reasoner. Pressure can come from
a tendency finding, a verified companion model, a frame shift, a coverage gap,
or the relationship graph. It is a hypothesis to inspect, not an instruction
to obey.

### 4. Disposition

The reasoner's response to admitted pressure:

- `apply` — the pressure earns a test, condition, alternative, reversal rule,
  private guardrail, or visible change;
- `reject` — the strongest plausible application fails, with the failed
  condition and risk of forcing it recorded;
- `park` — the pressure may matter later, with a specific reopen condition.

### 5. Receipt

Evidence about the process: what source existed, which view was used, which
calls occurred, which model and route served them, what they cost, what failed,
which pressure reached the reasoner, and whether every required disposition
was recorded.

The receipt does not decide whether the underlying recommendation is correct.

## How The Knowledge Substrate Was Built

The substrate is not a list of model names generated during a run. It is a
compiled body of source-shaped material prepared before the user's
conversation.

```text
roughly 200 books and related source study
        ↓
222 canonical Markdown model articles
        ↓
LLM-assisted semantic curation with human review
        ↓
activation · intervention · relation · reframing semantics
        ↓
compiled graph · runtime cards · affordances · absence records
        ↓
optional precomputed embeddings
```

### Source articles

The research program produced one canonical Markdown article for each of 222
mental models. LLMs assisted reading and synthesis. Reviewed curation then
turned those articles into explicit runtime material.

The accurate description is **LLM-assisted, source-shaped, reviewed, and
compiled**. It is not spontaneous runtime commentary. It is also not purely
human-authored text.

### Curation layers

The compiled substrate carries several different kinds of meaning:

- **Activation semantics** — when a model helps, when it should not be used,
  and what input and output shape it expects.
- **Intervention semantics** — failure modes, mitigations, heuristics, and
  premortem questions.
- **Relationship semantics** — allies, antagonists, and structured tensions
  between models, with activation conditions.
- **Reframing semantics** — patterns in a question that can route to a model
  capable of challenging the frame.
- **Affordances** — source-backed reasoning transactions a model can
  legitimately support.
- **Absence records** — tempting interpretations that the source does not
  support, including ownership boundaries and misuse blocks.

### Current compiled inventory

| Artifact | Current inventory | Status and role |
|---|---|---|
| Canonical registry | 222 models | Stable canonical IDs and display names |
| Cognitive-tendency layer | 25 tendencies | Adapted from Munger for human–LLM reasoning transactions |
| Model relationship graph | 1,358 edges | 523 allies, 344 antagonists, 491 structured tensions |
| Tendency bindings | 384 links | 61 core, 82 dynamic, and 241 antidote links |
| Complete graph | 1,742 edges | Relationships plus tendency links |
| Prerequisite graph | 15 edges | Learning and dependency order |
| V60 affordance artifact | 222 model records, 306 affordances, 697 absence records | `draft_review_only`; live private enrichment can use it, but it is not a truth oracle |
| Embedding store | Source chunks, model signals, tendency guidance, relation activation conditions | Optional query-time redundancy; direct OpenAI key required |

The counts describe compiled material, not product quality. A graph with more
edges can produce more noise. An affordance can be source-backed and still be
irrelevant to the current conversation.

### Why relationships matter

Nearest-neighbor similarity is not enough for reasoning pressure.

An ally can strengthen an existing model. An antagonist can expose what it
suppresses. A structured tension can preserve two models that should not be
collapsed into one answer. The graph is useful because it can introduce a
different relationship, not because it mathematically proves that the related
model belongs in the case.

## Conversation Custody

### Capture

The skill captures the complete available prose conversation into
`conversation.txt`. It records speaker turns and capture metadata. It excludes
tool calls, file reads, search output, system reminders, and discussion about
the skill itself.

The capture is the authority for later inspection. A summary is never allowed
to replace it silently.

### Long conversations

The authoritative conversation is not pre-truncated at 100 turns.

The extraction boundary has an 80,000-character processing cap. Above that
cap, `run_extract.py` creates:

- `conversation_processing_view.txt`, containing the first three and last
  fifteen parsed turn blocks plus an omission marker;
- `conversation_processing_view.json`, carrying hashes, lengths, turn counts,
  and exact omission metadata.

The derivative is explicitly partial and non-authoritative. The complete
available conversation remains archived unchanged.

This is bounded context without lost custody.

### Extraction

The first semantic job reads the conversation and proposes a compact decision
structure. Current fields include:

- decision situation;
- current synthesized position;
- live constraints;
- reasoning passages tied to source text;
- original framing;
- dropped threads;
- capture and provider metadata.

The extractor is probabilistic. Deterministic validation can reject malformed
shape, fabricated quotation, broken source custody, or missing required fields.
It cannot invent the missing interpretation or repair its meaning.

The current extractor centers the most developed or recent strategic thread.
It is not yet a complete representation of every parallel thread in a long,
ambiguous conversation.

## The Runtime Flow

The public product can be understood as eight stages. The live skill contains
more internal checkpoints, but those exist to preserve custody rather than to
create eight separate user experiences.

### Stage 1: Activation and preflight

The skill activates through `/lolla`, `$lolla`, or a matching audit request.
The preamble resolves the skill directory, loads environment configuration,
checks the OpenRouter key, verifies the graph and runtime engine, creates a run
ID, initializes the live transcript and operator log, and reports the model and
embedding mode.

A fatal preflight stops before model calls.

### Stage 2: Capture and extraction

The complete conversation is captured. The extractor creates the decision
structure and source-linked passages. Capture health, provider identity, usage,
and any bounded processing view are recorded before the four lanes run.

The user receives a short readback in ordinary language. Internal field names
and audit machinery stay out of the product narration.

### Stage 3: Four pressure lanes

`run_pipeline.py` receives the extraction and authoritative conversation
together through `ConversationContext`. All four lanes audit the conversation
transaction, not isolated assistant prose.

The current skill passes `--skip-revision` because the orchestrating Claude or
Codex writes the updated position later with the full conversational context.

### Stage 4: Bounded private pressure assembly

The pipeline assembles the four public cards, optional V60 private material,
and the constitutional graph-survival portfolio.

A compact pre-Step-6 private table organizes material already produced by the
run. It adds no OpenRouter calls and cannot select the visible answer.

### Stage 5: Counterargument and reconsideration

The user first sees the strongest case against the settled answer in plain
language and tied to a source passage. The orchestrator then reads the complete
pressure material privately and updates its position.

Every active graph pressure receives an apply, reject, or park disposition.
The public answer does not need to mention model names or include rejected
pressure.

### Stage 6: Persistence and ledger finalization

The revised position is persisted into `result.json`. Constitutional graph,
private-table, and V60 consideration ledgers are finalized against their exact
skeletons.

A missing or invalid required ledger stops later completion. The system does
not infer that omitted pressure was semantically rejected.

### Stage 7: Memo and optional deeper review

Optional pressure-check sub-agents are off by default. If a user explicitly
enables deeper review, only non-empty lanes may be sent and their usage is
recorded separately. The default path records that the deeper review was
intentionally skipped.

After the pressure-check state is final, a deterministic renderer creates the
Markdown memo. No LLM call is needed to render it.

### Stage 8: Observatory and archive

The local Observatory opens only after the updated position, ledgers, and memo
exist. The archive finalizer runs product-output and live-output hygiene checks,
copies the run artifacts to the local case folder, creates the agent and
evaluation receipts, indexes the reasoning trace, and returns a functional
receipt with URL, memo, cost, and archive location.

## The Four Lanes In Detail

### Lane 1: Structural Pressure

**Purpose:** identify recurring cognitive tendencies that may be distorting the
human–LLM reasoning transaction.

The first pass uses six family-clustered LLM calls rather than asking one model
to score all 25 tendencies at once. The optional embedding layer supplies a
second signal. Confirmed candidates then receive isolated deep checks.

Deterministic routing maps admitted tendencies to canonical corrective models
and graph neighbors. The result is a DeltaCard with the detected pattern,
source passage, challenge, corrective model, and possible reversal condition.

The LLM can miss or confuse adjacent tendencies. Embeddings reduce dependence
on one signal; they do not make detection certain.

### Lane 2: Model Companion

**Purpose:** identify which mental models are already active in the reasoning
and where their normal strengths can become failure modes.

An LLM fingerprints candidate models from source-linked passages. A separate
verification call checks candidate presence. Deterministic lookup attaches
source-shaped failure modes, premortem questions, allies, antagonists, and
tensions.

This lane is not a recommendation to add more models. It asks what is already
organizing the answer and what that structure may hide.

### Lane 3: Frame Pressure

**Purpose:** inspect the question before accepting its solution space.

An LLM extracts embedded assumptions, suppressed counterfactuals, mutable
constraints, and default categories. The compiled reframing layer supplies
candidate models and alternative questions.

A frame can be challenged without being discarded. The output is an
invitation to test what changes when one assumption is relaxed.

### Lane 4: Structural Coverage

**Purpose:** identify structural territory the answer did not enter.

The lane classifies the question, checks relevant dimensions, and generates
discovery questions for material gaps. These questions are not answered by the
system. They are reserved for information only the decision-maker can supply.

The output can be empty. A grounded zero is different from a failed lane.

### Bullshit Index

The Bullshit Index is a bounded delivery-audit pass, not a fifth pressure lane.
It inspects passages for patterns adapted from the Machine Bullshit project.
Long answers are compacted into at most twelve evaluation passages without
silently selecting source passages away; localization becomes coarser when
compaction occurs.

Its findings are diagnostic. They do not approve or reject the answer.

## Constitutional Graph Survival

The graph-survival path corrects a subtle product failure.

An earlier architecture allowed a probabilistic applicability pass to remove
graph candidates before the final reasoner saw them. That made the output
cleaner, but it also made the graph dependent on another model agreeing that a
non-obvious pressure already looked relevant. Externally supplied pressure was
being domesticated by the frame it was meant to challenge.

The current path behaves differently:

1. Controlled canonical IDs enter after deterministic and optional embedding
   recall.
2. Direct recall and relationship recall keep separate provenance.
3. Up to six direct candidates enter the detailed active set. Where available,
   bounded antagonist, structured-tension, and ally slots add relationship
   pressure.
4. Overflow remains in a compact reserve with exact suppression reasons.
5. A formatter may compact presentation, but no probabilistic applicability
   judgment can silently delete an admitted active candidate.
6. Every active item carries its strongest plausible application, a concrete
   test, force and ignore boundaries, provenance, a stable pressure ID, and a
   consumer locator.
7. The reconsidering reasoner applies, rejects, or parks every active item.

The active and reserve envelopes have frozen runtime ceilings of 6,000 and
12,000 estimated tokens. Bounds prevent “preserve possibility” from turning
into context dumping.

Reserve is custody, not rejection. The reasoner does not disposition reserve
items during the current run.

The older verifier and companion cards still provide interpretation telemetry.
Their applicability fields do not control constitutional survival.

## Reconsideration Without Forced Use

Pressure is successful when it is seriously considered, not when its name
appears in the final answer.

For each active pressure, the reasoner first attempts the strongest plausible
application. It then records:

- what concrete condition makes the pressure useful;
- what condition failed if it is rejected;
- what future evidence would reopen it if parked;
- whether it changed the public answer, remained a private guardrail, or had no
  material effect.

This structure protects two outcomes that a naive audit loses:

1. **Grounded rejection.** A strange or tempting model was inspected and found
   inapplicable without being forced into prose.
2. **Public stand-down.** The private process can be substantive even when the
   correct visible answer remains concise or unchanged.

`not_considered` is not a semantic disposition for an active item. It is a
technical custody failure.

## Artifacts And Custody

The default archive root is `~/.local/share/lolla/runs/`. Runs are grouped into
case folders using the exact conversation hash first, then an extraction-based
fingerprint. Renaming a case folder does not break matching because the
manifest owns identity.

### Core run artifacts

| Artifact | Purpose | What it does not prove |
|---|---|---|
| `conversation.txt` | Complete available authoritative prose source | That the external application exposed text it never supplied |
| `conversation_processing_view.{txt,json}` | Declared bounded derivative and omissions | Completeness |
| `extraction.json` | Fallible semantic view and source passages | Semantic correctness |
| `provider_budget.json` | Run call and cost envelope | Provider billing by itself |
| `result.json` | Four lanes, health, graph portfolio, revised answer, usage | Wisdom or safety |
| `constitutional_graph_survival_ledger.json` | Apply/reject/park custody for active pressure | That the dispositions are correct |
| `revised.txt` | Persisted updated position | That it is better than the original |
| `memo.md` | Readable Markdown run record | Complete future Decision Trail reconstruction |
| Private-table and V60 ledgers | What private material was used, rejected, deferred, or guarded | Public answer quality |
| `live_transcript.txt` | Captured product narration when available | Completeness unless supplied as a trusted full capture |

### Generated archive artifacts

| Artifact | Purpose |
|---|---|
| `agent_result.json` | Compact `lolla_agent_result.v2` handoff with neutral `review_revised_answer` action |
| `evaluation.json` | Deterministic run-readiness receipt for artifacts, schemas, custody, hygiene, capture, and caller conservatism |
| `reasoning_trace.json` | Local-only manifest of paths, hashes, health, usage, pressure state, and model-call telemetry |
| `graph_survival_report.{json,md}` | Operator/research view of candidates, recalls, dispositions, and visible/private survival |
| `extraction_adequacy_report.json` | What provenance survived or weakened across source, extraction, and runtime representations |
| `control_result.json` | Optional wrapper when an external control input exists; it does not approve an action |

The archive preserves raw artifacts by reference and hash. Compact receipts do
not duplicate the full conversation.

## State And Missingness

Absence is not one state.

Semantic readers and evaluation contracts distinguish:

| State | Meaning |
|---|---|
| `complete` | Required work ran and returned admitted records |
| `completed_zero` | Required work ran successfully and found no records |
| `partial` | Some required work or evidence is present, but the view is incomplete |
| `failed` | The attempted job did not produce an admissible result |
| `missing` | No result is available or no attempt occurred |

The live run-health envelope uses `healthy`, `partial`, `degraded`, and
`critical`. The agent handoff uses `healthy`, `partial`, `degraded`, and
`incomplete`. These describe different layers and should not be collapsed into
one score.

A missing reader result is not evidence that no issue exists. A
`completed_zero` result is not a failure. A clean schema can coexist with a
wrong interpretation.

## Models, Providers, And Bounds

### Current LLM route

The default operator is `google/gemini-3.1-flash-lite` through OpenRouter. For
that model, the default route is pinned to `google-vertex/global`, fallbacks are
off, required parameters are enforced, and data collection defaults to
`deny`. ZDR is requested only when `LOLLA_OPENROUTER_REQUIRE_ZDR` is explicitly
enabled. A request flag is recorded as a request, not claimed as endpoint proof.

`LOLLA_OPENROUTER_MODEL` can override the model. Overrides are useful for
experiments, but models should not be described as behaviorally interchangeable.

The current economical model is an experimental operator, not a production
selection or quality ceiling. More expensive models may improve semantic work
while worsening restraint, cost, or apparent false-positive confidence.

### Embeddings

Embeddings use the direct OpenAI key. They support:

- tendency-signal redundancy;
- companion recall;
- model-source chunk retrieval;
- narrow activation-condition tie-breaking.

If `OPENAI_API_KEY` is absent, embeddings are disabled and recorded as off.
The pipeline continues through LLM interpretation and deterministic graph
routing. It does not silently send embedding work to OpenRouter or another
provider.

### Calls, retries, and ceilings

A typical core run makes roughly 18–25 OpenRouter calls. The Bullshit Index may
add up to twelve calls. Each boundary request has a stage output ceiling and a
run-level call and estimated-cost envelope.

Boundary failures are preserved. The provider client does not perform an
internal automatic retry loop. The one application-level exception is the
documented extraction retry for quote fabrication; its first result and retry
custody remain visible.

Frozen evaluation contracts can be stricter: exact call maximum, USD ceiling,
model, provider, schema, seed, output cap, retry policy, and stop rule are fixed
before execution.

### Cost custody

Every run maintains a `usage_summary` with vendor and stage attribution. It
records:

- attempted calls;
- prompt, completion, cache, and total tokens when supplied;
- requested and served model identity;
- provider response ID;
- exact provider-reported cost when available;
- versioned local estimate;
- routing and privacy-policy fields;
- price-table date and budget state.

The provider dashboard remains the account-level billing source of truth. See
[Cost and Telemetry](docs/cost-and-telemetry.md).

## Privacy Boundary

The raw conversation is sensitive by default.

The configured OpenRouter model receives conversation-derived material for
extraction and pressure lanes. When embeddings are on, OpenAI receives
query-expansion and embedding inputs. Local archives can contain the complete
conversation, revised answer, memo, provider responses, and detailed traces.

Lolla records the declared request policy, route, fallback state, response
identity, cost, and ZDR request state. It does not copy API keys into artifacts
or claim a privacy property solely because it was requested.

Before using sensitive material, review the provider's current policy and the
local archive location. Changing a provider, route, model, or data policy is a
real product change, not a cosmetic environment override.

## Failure And Degraded Behavior

| Situation | Current behavior |
|---|---|
| Missing OpenRouter key, graph, or engine | Fatal preflight; no model call |
| Conversation is ordinary code debugging | Extraction returns `not_strategic`; the skill declines politely |
| Very long conversation | Complete source preserved; declared first-three/last-fifteen processing view used above 80K characters |
| Multiple strategic threads | Extractor centers the most developed or recent thread; other threads may be underrepresented |
| Lane returns a grounded zero | Valid empty result, distinct from failure |
| OpenRouter timeout or HTTP failure | Boundary metadata and partial/failed state preserved; no hidden healing |
| Extraction is malformed or misses required meaning | Semantic artifact stays error; deterministic code does not invent the missing read |
| OpenAI key missing | Embeddings off; other paths continue |
| V60 missing or disabled | Four lanes continue; status becomes disabled or failed visibly |
| Required active-pressure ledger missing | Completion stops before memo, Observatory, or archive can look clean |
| Product output leaks internal machinery | Run health degrades and the leak is recorded |
| Trusted live transcript unavailable | Live-output cleanliness remains missing or `not_checked`, not silently clean |

The system prefers an inspectable failure to an apparently complete artifact
created by retry, fallback, response healing, or invented meaning.

## What The Current Evidence Supports

The project has substantial mechanical evidence:

- source, model, pressure, request, response, and cost custody;
- complete-conversation preservation and declared compaction;
- bounded graph survival and disposition ledgers;
- provider-free fixtures for strange pressure, rejection, parking, tamper,
  missingness, and cap behavior;
- frozen controls, matched requests, protected targets, and source-first review;
- a full local test suite covering runtime and evaluation contracts.

Development cases show that pressure can produce decision-relevant additions
and grounded rejections. Other cases show false positives, role confusion,
schema failures, over-absorption, quiet-case failure, and no unique advantage
over a fresh control.

The latest leakage-corrected R4 matched holdout recovered genuine residual gaps
in both arms. The residual repair still failed both quiet controls. The frozen
decision is `residual_task_repair_insufficient`; the reader is not integrated
into the runtime.

The supported conclusion is narrow:

> Lolla has a real reasoning-pressure and custody system. Whether it reliably
> creates useful unique pressure for real users remains an open product and
> evaluation question.

Lolla does not currently support claims of reasoning-quality certification,
automatic reliance, scalar scoring, production-model selection, or proven
decision improvement.

See the
[current constitutional audit](docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md),
[current roadmap](plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md),
and
[latest matched-holdout result](docs/conversation-understanding/lolla-r4-matched-holdout-v2-execution-result-2026-07-14.md).

## Design Lineage

Charlie Munger's latticework and Psychology of Human Misjudgment supplied the
root idea: failures compound, and important judgment needs more than one
disciplinary frame.

Kahneman and Tversky's fast/slow distinction is used as a design metaphor for
an external pause. It is not a literal claim about LLM cognition.

The authors of *Framers* informed Lane 3's focus on the question and its
suppressed alternatives. Balaji Srinivasan's distinction between probabilistic
AI and deterministic computing helped sharpen the authority split. His warning
captures the design tension: “0% AI is slow, but 100% AI is slop.”

Andrej Karpathy's
[knowledge-wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
informed the separation between raw sources and persistent compiled Markdown
knowledge. The founder's legal background supplied the adversarial reading
method: preserve the record, test the burden of proof, and distinguish
persuasive language from supported reasoning.

These influences explain design choices. They do not validate Lolla's results.

## Detailed References

- [Founder Product Vision](docs/conversation-understanding/lolla-founder-product-vision-2026-07-14.md)
  — the human purpose, Markdown-memory principle, and future Teacher boundary.
- [Product Constitution v5](docs/conversation-understanding/lolla-product-constitution-v5.md)
  — binding rules, product evils, and evaluation boundaries.
- [Live Flow](docs/how-it-works/live-flow.md) — step-by-step skill behavior and
  operator checkpoints.
- [Pipeline Lanes](docs/how-it-works/pipeline-lanes.md) — prompts, routing,
  cards, and diagnostics for the four lanes.
- [Knowledge Substrate](docs/how-it-works/knowledge-substrate.md) — compiled
  files, curation history, graph, embeddings, and V60 inventory.
- [Operations and Limits](docs/how-it-works/operations-and-limits.md) —
  environment variables, edge cases, cost shape, and known limitations.
- [Architecture and Evolution](docs/how-it-works/architecture-and-evolution.md)
  — current modules and the history of major migrations.
- [Skill Steps](docs/skill/STEPS.md) — exact orchestration procedure.
- [Agent Result Contract](docs/lolla-agent-result-contract.md) — machine-facing
  handoff and neutral caller action.
- [Evaluation Index](docs/evals/README.md) — current evaluation doctrine,
  frozen experiments, and human-review boundaries.
- [Board and Product History](docs/board/README.md) — the historical Decision
  Work and product-development catalog removed from these root entry points.
- [Cost and Telemetry](docs/cost-and-telemetry.md) — vendor accounting,
  response identity, and price-table maintenance.

Historical plans and results remain useful evidence. They are not live behavior
unless the newest current entrypoint says so.
