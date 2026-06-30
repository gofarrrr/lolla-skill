# Decision Trail Readiness Audit v0

Status: internal audit

Date: 2026-06-29

Scope: docs-only current-state audit of whether Lolla currently captures enough conversation understanding to support the intended Decision Trail product surface.

This audit did not run `$lolla`, did not invoke the Lolla skill, did not call providers or models, did not mutate archives, and did not inspect private archive content. It reads the current repository state and the merged/tracked design, eval, and conversation-understanding docs.

## Short Verdict

Decision: REVISE BEFORE PRODUCTIZING THE DECISION TRAIL.

The direction is right. The current system has real primitives: conversation capture, compact semantic extraction, audit lanes, revised answer persistence, archive artifacts, doctor/preflight work, audit decision records, Product Delta eval scaffolding, and a coherent non-claim boundary.

But the full Decision Trail vision is not live yet.

Today, Lolla can produce an audited revised answer and preserve multiple artifacts that make the run inspectable. It does not yet produce a single first-class customer-facing report that explains the whole decision trail:

- what conversation produced the answer;
- what the system understood;
- which options and constraints were live;
- what was pushed back on;
- what was abandoned;
- what changed between vanilla and revised;
- what evidence was missing;
- what remains unresolved;
- what can be safely consumed by another agent.

The pieces exist, but they are scattered. The next product-shaped move should be a Decision Trail report design and read-only exporter, not more broad infrastructure.

## Contradicting Evidence First

The strongest reason to slow down is this:

Lolla can now create careful artifacts faster than it can prove those artifacts contain the right decision story.

That is the same failure mode we have been trying to avoid. A polished report can become a trust costume if it makes a weak or incomplete interpretation feel authoritative.

The current live extraction is intentionally compact. It captures:

- decision situation;
- live constraints;
- synthesized position;
- reasoning passages;
- original framing;
- dropped threads.

That is useful, but not enough for the full Decision Trail. Several fields that matter for review are not first-class in the live extraction:

- live options and option status;
- user values and priorities;
- stakeholder obligations;
- assistant influence and stance shifts;
- abandoned alternatives;
- evidence used versus missing;
- load-bearing assumptions;
- lost value from the original answer;
- useful versus noisy friction;
- unresolved questions as product review inputs.

The Product Delta phase helps us reason about these fields offline, but it is not part of the skill runtime and it is not product proof. It is an internal eval lane over checked-in safe artifacts.

The specialist extractor research is promising, but it is not merged as runtime behavior. It remains a research/design lane with explicit integration blockers.

## Big Picture

Lolla's product thesis is:

> Serious AI-assisted decisions need the answer plus the process trail.

The final memo is not enough. A reviewer should be able to inspect how the answer came into being:

- what the conversation contained;
- what the assistant accepted;
- what the audit challenged;
- what changed;
- what remained uncertain;
- what should not be overclaimed.

This fits the core architecture:

> probabilistic interpretation inside deterministic custody

LLMs interpret messy conversation and apply pressure. Deterministic code preserves artifacts, schemas, source status, missingness, custody flags, and non-claims.

Human reviewers remain responsible for deciding whether the revised answer actually helped.

Agents may eventually consume structured metadata, but only as inspection and routing material, not as approval.

## What Is Merged And Live Today

The current merged/tracked system includes these layers.

| Layer | Current state | What it gives us |
| --- | --- | --- |
| Lolla skill runtime | Built | Captures the current conversation, runs extraction and audit pipeline helpers, produces revised answer, persists local artifacts, renders memo, finalizes archive. |
| Compact extraction | Built | Produces `ConversationContext` with decision situation, live constraints, synthesized position, reasoning passages, original framing, and dropped threads. |
| Audit lanes | Built | Applies structured pressure through the existing runtime lanes and produces audit artifacts. |
| Archive artifacts | Built | Preserves run outputs such as revised answer, memo, `agent_result.json`, `evaluation.json`, `reasoning_trace.json`, extraction artifacts, and health metadata. |
| Agent result and evaluation | Built | Gives deterministic run-readiness, caller action, artifact health, capture adequacy, risk mode, and custody status. |
| Doctor/preflight | Built | Read-only local readiness surface. |
| Audit decision record exporter | Built | Read-only exporter for a safe accountability shell around a run, with explicit field status and non-claims. |
| Product Delta eval lane | Built as offline internal eval | PR71-PR85 provide thesis, protocol, readiness, lint, specialist contracts, packets, traps, provisional reads, disagreement report, and package gate. |
| Conversation IR code | Partly built | `ConversationIR` and constructor exist, with provenance-aware turns, spans, frame anchors, user issue events, and stance events. Default production construction is conservative. |
| Specialist extractor probes | Researched, not integrated | Existing specialist extractors improved span grounding in approved probes, but runtime integration remains blocked. |
| User values worksheet lane | Built as human-owned review aid | Helps reviewers think about values and priorities without automatic extraction or labels. |

## What Is Designed But Not Live

These are important, but should not be described as live customer product behavior:

| Item | Status | Current meaning |
| --- | --- | --- |
| First-class Decision Trail report | Not implemented | The product surface we likely need next. |
| `conversation_understanding_ir.v0` archive artifact | Designed, not implemented | Proposed offline/archive projection, not a runtime replacement. |
| Specialist runtime integration | Designed, blocked | Research supports the direction, but normal `$lolla` should not run specialists by default yet. |
| Provenance map exporter | Designed | Accountability design exists, but exporter is not implemented. |
| Review conflict register exporter | Designed | Accountability design exists, but exporter is not implemented. |
| Case graph exporter | Designed | Design exists, but implementation is intentionally deferred. |
| Automatic ADR generation inside `$lolla` | Deferred | Manual/read-only exporter exists, but no runtime integration. |
| Agent-facing approval label | Rejected | Agents can inspect and route; they must not receive an automatic "good advice" label. |

## What Is Not Merged Into The Current Stage

The working tree has unrelated untracked notes, plans, and synthetic review files. They are not part of the committed Product Delta package and should not be treated as the current system state unless explicitly reviewed and staged later.

In practical terms:

- the committed current Product Delta package is PR71-PR85;
- unrelated local notes are not authoritative;
- synthetic review folders outside the committed package are not part of the present evidence lane;
- pitch or comparative notes outside the committed docs should not drive implementation until reconciled.

## Current Live Conversation Understanding

The live extraction shape is useful but compressed.

Current runtime extraction captures:

- `decision_situation`;
- `live_constraints`;
- `synthesized_position`;
- `reasoning_passages`;
- `original_framing`;
- `dropped_threads`;
- capture adequacy and quote validation metadata.

The current provenance-aware IR can represent:

- turns;
- spans;
- turn references;
- frame anchors;
- user issue events;
- stance events;
- derivation and source provenance.

But the default path is conservative. It does not automatically create a full rich decision story from every conversation.

## Desired Decision Trail Fields

A customer-facing Decision Trail report would likely need these fields.

| Desired field | Current best source | Live today? | Gap |
| --- | --- | --- | --- |
| Decision question | Extraction, memo, agent result | Partial | Often compact; needs field status and source refs. |
| Vanilla likely next action | Product Delta eval | Offline only | Not live; often inferred from safe summaries. |
| Revised likely next action | Revised answer, memo, Product Delta eval | Partial | Needs structured delta report. |
| Live options | Conversation text, Product Delta reads | Weak | Not first-class in live extraction. |
| Option status | Not first-class | No | Need considered, active, rejected, deferred, unknown. |
| Constraints | Live constraints | Partial | Needs current/superseded/contradicted and better span grounding. |
| Stakeholders | Conversation text, memo | Weak | Not first-class. |
| Values and priorities | Worksheet lane, review docs | Mostly offline | Avoid automatic over-inference. |
| Assistant influence | Stance extractor research | Not live | Critical for sycophancy and framing pressure. |
| Evidence provided | Conversation, artifacts | Weak | Not first-class as evidence ledger. |
| Evidence missing | Structural coverage, memo, eval reads | Partial | Scattered. |
| Audit pressure applied | Audit artifacts | Partial | Exists, but not packaged into simple story. |
| Alternatives abandoned | Dropped threads, Product Delta | Partial | Dropped threads exists, but options are not first-class. |
| Useful friction | Product Delta eval | Offline only | Not runtime/product surface. |
| Noisy friction | Product Delta eval | Offline only | Must be preserved to avoid rewarding caveat bloat. |
| Lost value | Product Delta eval | Offline only | Important but not live. |
| Changed action/threshold/sequence/gate | Product Delta eval, revised answer | Partial/offline | Needs structured delta report. |
| Unresolved questions | Memo, Product Delta, ADR | Partial | Scattered and needs status semantics. |
| Artifact health | Agent result, evaluation, ADR | Yes | Strongest deterministic layer. |
| Source status | ADR, Product Delta schemas | Partial | Needs unification in Decision Trail. |
| Non-claims | ADR, PR78 lint, Product Delta docs | Yes/offline | Strong design, needs product surface. |

## Research Outcomes So Far

The repository already did meaningful research.

### 1. Conversation understanding research

The design survey concluded that Lolla should copy accountability primitives from memory/graph/context-engineering systems, not their platform shape.

Useful ideas:

- provenance;
- temporal evolution;
- source refs;
- typed artifacts;
- field status;
- graph-shaped inspection when helpful;
- context engineering and specialist decomposition.

Rejected directions:

- graph database;
- memory layer;
- embeddings/chunking platform;
- GraphRAG;
- Semantica clone;
- automatic domain authority.

### 2. Extraction adequacy findings

The current extraction path became much safer over time:

- capture adequacy exists;
- quote validation and replay work found and reduced quote issues;
- modern clean samples are quote-clean and capture-clean.

The remaining problem is not just mechanical capture. It is semantic adequacy:

> Did we preserve the parts of the conversation needed to understand the decision?

### 3. Semantic coverage findings

Semantic coverage reports showed that important evidence exists but is scattered:

- decision;
- live constraints;
- user values/priorities signal;
- changed constraints;
- dropped threads;
- assistant stance lineage;
- counter-pressure;
- revised-answer change reason;
- unanswered dimensions;
- actionability boundaries.

This supports a Decision Trail report. It also shows why raw artifact presence is not enough.

### 4. Specialist extractor probes

Existing specialist extractors improved span grounding in approved offline probes:

- live constraints;
- dropped threads;
- assistant stance/recommendation lineage.

That is strong evidence that narrower context-engineered interpretation can help.

But it does not yet justify default runtime integration. The probes also left important gaps:

- provider-boundary warnings;
- mixed-custody samples;
- limited modern full-run evidence;
- no solved user-values extraction;
- no proof that integration improves customer-facing review.

### 5. Product Delta evidence phase

PR71-PR85 built a non-human, offline Product Delta evidence lane.

It gives us:

- a product-delta thesis;
- a provisional review protocol;
- readiness checks;
- boundary lint;
- specialist contracts;
- packet builders;
- trap fixtures;
- Codex-assisted provisional specialist reads;
- fan-in/disagreement report;
- package manifest.

The healthiest signal was a downgrade:

`accept-operations-role-startup` moved from `material_improvement_candidate` to `partial_improvement_candidate` under specialist review pressure.

That matters because the system became less self-flattering when lost value and interpretation uncertainty were made explicit.

The strongest unresolved risk remains:

- thin real-case sample;
- prior-positive case selection;
- compressed checked-in safe context;
- no human validation.

## Current Evaluation Boundary

The Product Delta eval lane is not the Lolla skill.

It does not:

- run `$lolla`;
- invoke the skill;
- call providers;
- mutate archives;
- change prompts;
- change runtime behavior;
- score answer quality;
- create automatic labels;
- authorize agents.

It reads existing safe artifacts and asks:

> Can we conservatively inspect the difference between the vanilla conversation outcome and the Lolla revised outcome?

For now, the Product Delta lane is an internal harness. It helps us understand the system. It is not a user-facing claim.

## What We Are Missing

The missing piece is not a bigger judge.

The missing piece is a first-class decision-trail extraction and reporting surface that can make conversation understanding reviewable without pretending certainty.

The current system needs a bridge from:

```text
scattered artifacts
```

to:

```text
a single structured report that says:
- what the decision was;
- what changed;
- why it changed;
- what was preserved;
- what was lost;
- what remains unknown;
- what artifacts support the report;
- what is not being claimed.
```

## Main Product Risk

The main risk is overtrust.

If Lolla produces a beautiful Decision Trail report, users may treat it as proof that the advice is good.

That must be blocked in the product language, schema, and UI:

- no approval field;
- no quality score;
- no "safe for agent use";
- no "Lolla certified";
- no implication that artifact health equals advice quality;
- no automatic values extraction treated as fact;
- no hidden judge.

The report should make review easier, not remove responsibility.

## Main Technical Risk

The main technical risk is interpretation inadequacy.

If Lolla misunderstands the conversation, then every downstream artifact can become well-custodied bad premises.

Bad interpretation leads to:

- wrong audit pressure;
- wrong revised answer;
- tidy artifacts around the wrong issue;
- misleading review surface;
- false confidence.

So the next system work should not simply add more artifacts. It should improve our ability to inspect whether the conversation was understood well enough.

## What Would Have To Be True For The Vision To Work

The Decision Trail direction depends on several assumptions.

| Assumption | Risk | How to test |
| --- | --- | --- |
| Users care about process, not only the final memo | They may only want the answer | Show concise before/after report examples and test whether reviewers find missing context faster. |
| Current artifacts can populate a useful v0 report | Fields may be too scattered or thin | Build a read-only exporter and measure missingness by field. |
| More granular conversation interpretation improves audit usefulness | It may add complexity without leverage | Compare broad extraction versus specialist packets on real cases. |
| Agents can safely consume metadata | Agents may overread it as approval | Keep strict non-claim schema and routing-only semantics. |
| A report can show process without leaking private content | Reports may copy too much context | Separate checked-in safe mode from local private mode. |
| Values/priorities can be represented safely | LLMs may over-infer motives | Use explicit/user-stated/status fields and human-owned correction. |

## Pre-Mortem

If this direction fails, likely causes are:

1. The Decision Trail becomes too impressive-looking.

   Users trust the package because it is structured, not because the reasoning is actually better.

2. We overbuild the interpretation layer.

   A giant conversation IR appears before we know which fields actually improve review.

3. The report becomes unreadable.

   It contains every possible field, but no one can quickly see what changed or what matters.

4. Specialist reads become a hidden judge.

   Multiple narrow LLM reads get treated like votes or authority.

5. The values layer over-infers.

   The system starts claiming what users care about instead of recording what was explicit, inferred, unclear, or disputed.

6. Privacy boundaries blur.

   A customer-facing report copies too much conversation detail or raw provider text.

7. The eval lane becomes self-confirming.

   We only review cases where Lolla already looks good.

## Recommended Next Sequence

Do not jump straight to runtime integration.

The next safe sequence is specified in
[Decision Trail PR86-PR89 PRD v0](decision-trail-pr86-pr89-prd-v0.md).

In short:

### PR86: Decision Trail Report PRD v0

Docs and JSON schema only.

Define `lolla.decision_trail_report.v0` as the customer-facing process report.

It should include:

- report metadata;
- source refs;
- conversation summary;
- decision question;
- vanilla likely next action;
- revised likely next action;
- option map;
- constraints;
- stakeholders;
- values/priorities with source status;
- assistant influence;
- audit pressure summary;
- structural delta;
- useful/noisy friction;
- lost value;
- unresolved questions;
- artifact health;
- non-claims.

It must not include:

- approval;
- quality score;
- automatic labels;
- agent authorization;
- raw/private content in checked-in safe mode.

### PR87: Decision Trail Read-Only Exporter v0

Code and tests.

Build a read-only exporter from existing artifacts into an external report file.

Initial mode should be conservative:

- no model calls;
- no archive mutation;
- no runtime integration;
- no raw text copying into checked-in examples;
- every field gets status: supplied, inferred, missing, unavailable, unclear, or not_applicable.

### PR88: Decision Trail Fixture Review v0

Docs/data/review.

Export a small set of safe example reports and review:

- which fields populate well;
- which fields remain missing;
- whether the report is understandable;
- whether it increases or reduces overtrust;
- whether it helps identify the real delta.

### PR89: Conversation Interpretation Gap Decision v0

Docs-only decision gate.

Use PR88 field missingness to decide whether to:

- add narrow offline specialist enrichment;
- design `conversation_understanding_ir.v0`;
- strengthen extraction prompts;
- add local-private mode only;
- or stop and simplify the report.

Only after this should runtime integration be considered.

## What Not To Build Next

Do not build next:

- a broad "Did Lolla improve this?" judge;
- a product score;
- automatic agent approval;
- default runtime specialist calls;
- graph database;
- memory layer;
- embeddings/chunking;
- GraphRAG;
- full conversation-understanding ontology;
- case graph exporter;
- provenance/conflict exporters unless they directly serve the Decision Trail;
- dashboard before the Markdown/report shape proves useful.

## Practical Product Shape

The eventual user-facing package should be:

1. Revised answer

   The answer the user may act on, still requiring human responsibility.

2. Decision Trail report

   A compact process report explaining what changed and what remains unknown.

3. Machine-readable audit envelope

   Structured fields for agent inspection, routing, custody, source status, and missingness.

4. Non-claim boundary

   Clear reminders that the report is not approval, certification, proof, or a quality score.

## Bottom Line

Lolla is on the right path, but the next important product primitive is not another abstract accountability artifact.

The next important primitive is the Decision Trail:

> a readable and machine-inspectable report that travels with the revised answer and explains how the decision moved.

Today, the system has enough ingredients to design and export a conservative v0.

It does not yet have enough to claim that the full decision trail is live, complete, or validated.

The correct next step is a narrow read-only Decision Trail report, followed by field-missingness review, before any runtime integration or broader conversation-understanding build.
