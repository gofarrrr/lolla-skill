# Observatory Global Product Experience And Data Flow v0

Status: global product and information-architecture design contract
Date: 2026-07-06
Decision gate: `proceed_to_observatory_portable_server_view_model_contracts`

## One Sentence

Observatory should become one selected-run product workspace where Outcome,
Learn, Models, Relations, Map, Receipts, and Advanced Audit each have a clear
job, a clear data contract, and a clear boundary.

## Why This Exists

Recent work added useful pieces:

- Mental Model Teacher product pages and relation pages;
- Teacher lesson objects;
- focused graph neighborhoods;
- a visible learner prototype;
- an Observatory integration design;
- selected-run learning packet planning;
- server-rendered Learn, model, relation, and graph navigation;
- Conversation Understanding / Decision Work receipt status;
- process brief opt-in planning and action surfaces.

That is progress, but it also creates the product risk the user noticed: if we
keep adding panels, every screen starts mixing teaching, model library content,
graph exploration, telemetry, receipts, review controls, and system status.

The product should not be:

```text
everything the system knows on one page
```

The product should be:

```text
one selected run
  -> one primary user question at a time
  -> one surface that owns each information type
  -> clear links to deeper explanation, custody, and audit
```

This document defines the global product shape before more UI is built.

Related design trail:

- [Mental Model Teacher Learner Experience Design](mental-model-teacher-learner-experience-design-v0.md)
- [Mental Model Teacher Observatory Integration Design](mental-model-teacher-observatory-integration-design-v0.md)
- [Mental Model Teacher Observatory Ownership and Portability Boundary](mental-model-teacher-observatory-ownership-portability-boundary-v0.md)
- [Observatory Conversation Understanding Boundary](observatory-conversation-understanding-boundary-v0.md)

## Product Thesis

Observatory is the single product shell.

Inside that shell:

- Outcome answers what changed in the run.
- Learn answers what reasoning move the user can learn.
- Models explains durable mental models.
- Relations explains model pairs and tensions.
- Map lets the user navigate a small selected-run neighborhood.
- Receipts shows custody, missingness, sidecar status, and non-claims.
- Advanced Audit lets reviewers inspect technical telemetry.

Teacher is not a second application. It is the Learn mode plus reusable Models,
Relations, and Map surfaces inside Observatory.

The core learning thesis remains:

```text
case is the anchor
reasoning move is the subject
model relationship is the lesson
practice rep is the product value
```

## Perspectives To Satisfy

### Normal User

The normal user wants to understand the completed run without becoming a system
operator.

They need:

- what run they are looking at;
- what changed in the answer;
- what matters most;
- what to learn from the run;
- where to inspect sources and missingness if they care.

They should not start inside raw extraction, route traces, graph survival
reports, provider logs, or curation metadata.

### Learner

The learner wants a guided reasoning lesson.

They need:

- a case anchor;
- a reasoning trap;
- a thinking move;
- the model relationship that teaches the move;
- a worked example;
- a practice rep;
- a do-not-overlearn boundary.

They should not need to decode telemetry vocabulary before they understand the
lesson.

### Library Browser

The library browser wants to move through durable knowledge.

They need:

- search for mental models;
- typed filters;
- model pages;
- relation pages;
- backlinks from models and relations to runs or lessons;
- graph neighborhoods as navigation.

The library should use run context when available, but durable model and
relation pages should not become case notes.

### Reviewer Or Maintainer

The reviewer wants to inspect whether a page overclaims or hides missingness.

They need:

- source refs;
- curation status;
- sidecar status;
- missing fields;
- review status;
- links to raw audit panels.

Their tools should be reachable without making the learner page carry every
technical artifact.

### System And Custody

The system needs deterministic rails around non-deterministic interpretation.

Those rails are:

- source custody;
- model and relation contracts;
- missingness;
- generated artifacts;
- receipts;
- review gates;
- explicit non-claims.

Those rails should be visible where trust is relevant, but they are not the
primary teaching copy.

### Implementation Owner

The implementation owner needs a source-of-truth map before changing more UI.

They need:

- which source path owns the Observatory shell;
- which adapters produce product-safe view models;
- which raw artifacts are advanced-only;
- which surfaces must not duplicate each other;
- which PR should happen next.

## Product Principles

1. One selected run is the product workspace.
2. One information type has one primary home.
3. Teaching, model study, relation study, graph navigation, receipts, and audit
   are separate jobs.
4. The graph is navigation, not proof.
5. Receipts are custody, not marketing.
6. Telemetry is advanced inspection, not the product living room.
7. Canonical mental model source can power pages, but raw Markdown is not the
   UI.
8. Activation evidence can explain why something appeared in a run, but it is
   not a durable model definition.
9. Relation semantics can power relation pages and graph edges, but unsupported
   relation speculation must not be surfaced.
10. Embedding similarity is suggestion-only until reviewed.
11. Product Delta and eval internals do not become user-facing proof.
12. No Observatory surface should claim product proof, human validation, answer
    correctness, advice correctness, or action authorization.

## Global Information Architecture

### No Selected Run

The root experience should answer:

```text
What can I open?
```

Candidate areas:

- recent runs;
- archived runs;
- search by case title or run id;
- library entry points for Models and Relations;
- advanced audit links for operators.

The no-run state should not pretend to be the same as a selected-run workspace.
It can show library browsing, but it should make clear that Learn, Outcome, Map,
and Receipts become meaningful once a run is selected.

### Selected Run

After a run is selected, Observatory should use one primary workspace:

```text
Run header
Outcome | Learn | Models | Relations | Map | Receipts
Advanced Audit
```

The header should hold:

- run title;
- current or archived state;
- run health;
- risk mode when available;
- learning packet status;
- process brief status;
- links to Receipts and Advanced Audit.

The default tab can remain Outcome for existing users until product testing says
otherwise. Learn should be one click away and should be visibly framed as the
reasoning lesson from the selected run.

### Advanced Audit

Advanced Audit is not a primary product tab for normal users.

It should remain available for:

- extraction audit;
- route traces;
- run events;
- evaluation artifacts;
- usage;
- graph survival;
- sidecar inspection;
- maintainer debugging.

Advanced Audit can be linked from Receipts, but it should not compete with
Outcome or Learn as the first product surface.

## Surface Ownership

| Surface | Primary user question | Should show | Should not show |
| --- | --- | --- | --- |
| Outcome | What happened in this run? | revised answer, strongest pressure, compact model chips, run health | full canonical model pages, raw curation, relation taxonomy wall |
| Learn | What reasoning move can I learn? | case anchor, trap, thinking move, relation story, worked example, practice rep, boundary | raw telemetry, all graph nodes, review controls, full receipt tables |
| Models | What does this mental model mean? | canonical explanation, helps-notice, use/avoid, misuse, failure modes, practice prompts, backlinks | case-specific lesson as the model identity, routing internals |
| Relations | What does this model pair teach? | plain-language story, why it matters, misread risk, practice prompt, source refs, links to both models | naked edge labels, confidence as proof |
| Map | How can I navigate the neighborhood? | small graph, selected node panel, selected edge panel, filters, search, links to model and relation pages | full corpus by default, graph edges as proof, embedding neighbors as validated relations |
| Receipts | What can I trust, inspect, or treat as missing? | source refs, sidecar status, missingness, non-claims, learning packet status, process brief status | primary teaching narration, product marketing, approval labels |
| Advanced Audit | What happened inside the system? | raw audit panels, extraction details, route traces, usage, graph survival, debug status | learner onboarding, product claims, answer correctness labels |

## Single-Home Rules

The goal is not to hide information. The goal is to prevent the same data from
appearing with different meanings.

| Information | Single home | May link from | Do not duplicate as |
| --- | --- | --- | --- |
| Revised answer | Outcome | Receipts, memo, Advanced Audit | Teacher lesson body |
| Teacher reasoning move | Learn | Outcome summary, Models backlinks, Relations backlinks | telemetry panel copy |
| Canonical model explanation | Models | Outcome, Learn, Relations, Map | model activation evidence |
| Model activation evidence | Outcome or Receipts | Models | durable model definition |
| Relation explanation | Relations | Learn, Map | graph edge label only |
| Graph neighborhood | Map | Outcome preview, Learn preview | separate Teacher graph app |
| Conversation Understanding status | Receipts | Outcome header, Advanced Audit | Teacher lesson body |
| Source custody | Receipts | Models, Relations, Learn drawers | primary lesson narration |
| Usage or cost telemetry | Advanced Audit | Receipts | learner-facing proof |
| Graph survival and eval artifacts | Advanced Audit or Receipts | Map caveat | product marketing |

## Visibility Tiers

| Tier | Meaning | Examples |
| --- | --- | --- |
| First-class product data | user-facing content that carries the experience | revised answer, thinking move, mental model page, relation page, graph neighborhood, practice rep |
| Second-class support data | useful context that supports trust or navigation | model activation evidence, source refs, missingness, sidecar availability, run health, backlinks |
| Receipts and review data | custody, review, and non-claim material | curation status, source hashes, user receipt, attachment status, review gates |
| Internal-only data | implementation or private material | raw conversation, local absolute paths, provider text, raw routing internals, raw embeddings, Product Delta internals |
| Future or suggestion-only data | potentially useful material that is not yet reviewed | semantic neighbors, full corpus graph, AI-discovered relations, embedding similarity clusters |

## Data Flow

The safe data flow should be:

```text
raw run artifacts
  -> read-only adapters
  -> product-safe view models
  -> Observatory UI surfaces
```

The UI should not casually consume raw telemetry in primary product surfaces.
Advanced Audit may inspect raw artifacts because that is its job.

### Raw Run Artifacts

The current run/archive layer may include:

- `result.json`;
- `agent_result.json`;
- `reasoning_trace.json`;
- `evaluation.json`;
- `run_events.json`;
- `memo.md`;
- `extraction.json`;
- `graph_survival_report.*`;
- `decision_work/*` when present.

These are source and custody artifacts. They should feed adapters.

### Knowledge Substrate

The existing substrate may include:

- `data/model_sources`;
- `data/model_sources/manifest.json`;
- `data/curation`;
- `data/curation/intervention_semantics`;
- `data/curation/relation_semantics`;
- `data/knowledge_graph.json`;
- `data/relationship_graph.json`;
- `data/embeddings.db`;
- `data/curated`;
- `data/family_semantics`;
- `data/compiled/model_affordances/affordances_v60.json`.

This substrate is not a UI. It should be translated into product-safe model,
relation, graph, and receipt objects.

### Product View Models

The selected-run Observatory product should converge on typed view models:

| View model | Feeds | Job |
| --- | --- | --- |
| `selected_run_summary` | Header, Outcome | identify the selected run and status |
| `outcome_summary` | Outcome | present revised answer and major pressure |
| `learning_packet` | Learn | teach one reasoning move from the run |
| `model_page` | Models, drawers, backlinks | explain one durable mental model |
| `relation_page` | Relations, edge panel | explain one model relationship |
| `graph_neighborhood` | Map | navigate selected-run model and relation structure |
| `receipt_summary` | Receipts, header status chips | show custody, missingness, sidecars, non-claims |
| `advanced_audit_index` | Advanced Audit | enumerate raw inspection routes and artifact status |

### Product Rule

Primary UI surfaces consume product-safe view models.

Advanced Audit can consume raw telemetry.

Receipts can bridge the two by showing status, source refs, missingness, and
links to advanced inspection without turning raw telemetry into teaching copy.

## Search, Switching, And Picking Data

Observatory should support several ways of finding relevant data. They should
not be collapsed into one graph.

| Mechanism | User job | Data it should use | Boundary |
| --- | --- | --- | --- |
| Run picker | open a completed run | archive index, recent/current run metadata | no raw conversation preview by default |
| Tab switcher | change the current question | selected run workspace state | do not remount unrelated products |
| Model search | find a known or approximate model | product-safe model index | raw canonical files remain hidden |
| Relation search | find a model pair or relation type | product-safe relation index | relation confidence is not proof |
| Backlinks | see where a model or relation appears | reviewed run, lesson, relation, and graph refs | do not imply validation beyond source status |
| Map filters | narrow visible graph structure | graph neighborhood object | graph proximity is navigation only |
| Receipts links | inspect custody | source refs and sidecar status | keep advanced details out of primary lesson copy |

## Primary User Flows

### Flow 1: Open A Run

1. User opens Observatory.
2. User chooses a recent or archived run.
3. Header confirms run identity and health.
4. Outcome opens by default.
5. User can move to Learn, Models, Relations, Map, or Receipts without losing
   the selected run context.

### Flow 2: Learn From The Run

1. User opens Learn.
2. Page narrates the case anchor.
3. Page names the reasoning trap.
4. Page teaches one thinking move.
5. Page explains the model relationship.
6. Page gives a worked example and a practice rep.
7. Page shows a do-not-overlearn boundary.
8. Page links to model pages, relation page, Map, and Receipts.

### Flow 3: Click A Mental Model

1. User clicks a model chip from Outcome, Learn, Relations, or Map.
2. Observatory opens the Models surface or a model drawer.
3. The page shows product-formatted canonical model information.
4. It separates durable model meaning from selected-run activation evidence.
5. It links to related relations, lessons, and graph views.

### Flow 4: Click A Relation

1. User clicks a relation from Learn, Relations, or Map.
2. Observatory opens the Relations surface or relation drawer.
3. The page explains the pair in plain language before taxonomy.
4. It shows why the relation mattered in the selected run.
5. It shows misread risk, practice prompt, source refs, and links to both model
   pages.

### Flow 5: Explore The Map

1. User opens Map.
2. Map defaults to a small selected-run neighborhood.
3. User can toggle run activation and learning neighborhood when both exist.
4. User can filter relation types.
5. User can search nodes.
6. Node and edge panels link back to Models and Relations.
7. The surface states that graph structure is navigation, not proof.

### Flow 6: Inspect Receipts

1. User opens Receipts.
2. Receipts show learning packet status.
3. Receipts show source refs and missingness.
4. Receipts show Conversation Understanding / Decision Work status.
5. Receipts show visible non-claims.
6. Receipts link to Advanced Audit for technical inspection.

## Teaching Versus Model Library Versus Relation Library

These three information types are related, but they are not the same product
object.

| Type | Anchor | User question | Reuse level |
| --- | --- | --- | --- |
| Teaching lesson | selected case/run | What move can I learn here? | case-specific |
| Mental model page | one model | What does this model help me notice? | durable and reusable |
| Relation page | two models plus relation type | What does this pair teach? | reusable with run-specific examples |

The lesson can link to model and relation pages. Model and relation pages can
link back to lessons where they appeared. They should not be collapsed into one
giant page.

## Current-State Gap

The current repository has a portable Python Observatory server and a compiled
frontend bundle. The source of the compiled bundle is not present in this repo.

Recent work has therefore improved the portable server-rendered and injected
surfaces first. That is useful, but ad hoc injection is not the final global UX
architecture.

The current root experience can still feel like an old case list followed by
new surfaces. The product direction should be one coherent selected-run
workspace rendered by the portable Observatory server, not a stack of
independently added pages and not a return to the old app-era source by default.

## Source Ownership Decision Resolved

The source audit resolved the near-term direction:

- `observatory/serve_result.py` owns the active portable skill-presentation
  surface;
- `Lolla-system-b/observatory/svelte-app` is verified as historical legacy
  source for the old root SPA;
- `observatory/build/*` is a distribution artifact, not source;
- the current product direction is portable Python/server-rendered Observatory;
- a Svelte revival or bundle sync would require a separate explicit decision.

Therefore, the next PR should define product-safe view models for the portable
server-rendered shell, not port the global shell to Svelte.

## Implementation Sequence

### PR-G1 Global Product And Data Flow Contract

Add this document, a review JSON, and tests.

Stop before UI changes.

### PR-G2 Observatory Source Ownership Audit

Resolved the near-term source question: portable server rendering is the
current product direction; the Svelte app is historical legacy source, not the
default future UI owner.

Stop before UI rebuild.

### PR-G3 Portable Product View Model Contracts

Define typed view models for selected run summary, outcome summary, learning
packet, model page, relation page, graph neighborhood, receipt summary, and
advanced audit index.

Stop before rendering.

### PR-G4 Server-Rendered Root Workspace IA

Plan the portable selected-run workspace in the Python server:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Stop before legacy bundle edits.

### PR-G5 Model And Relation Page Consolidation

Make mental model clicks resolve to product-safe model pages or drawers, and
make relation clicks resolve to product-safe relation pages or drawers.

Stop before full corpus graph.

### PR-G6 Map Consolidation

Unify run activation and learning neighborhood into one Map surface with view
filters.

Stop before treating graph edges as proof.

### PR-G7 Receipts Consolidation

Make Receipts the single home for source custody, missingness, Decision Work
status, process brief status, and non-claims.

Stop before runtime opt-in defaults.

### PR-G8 UX Review Packet

Create a reviewer packet comparing the global flow against the current
fragmented flow.

Stop before product readiness or human validation claims.

## Stop Conditions

Stop if implementation would require:

- running Lolla;
- invoking the Lolla skill;
- provider/model API calls;
- creating a new Lolla run;
- wiring or changing runtime behavior;
- mutating archives by default;
- exposing raw private conversation text as product copy;
- exposing raw local paths;
- claiming product proof;
- claiming human validation;
- claiming answer or advice correctness;
- adding answer-quality scoring;
- adding approval or certification labels;
- authorizing agent or automatic action;
- treating graph edges as proof;
- treating embedding similarity as validated relation semantics;
- turning Product Delta or eval internals into user-facing product copy.

## Open Product Questions

1. Should Outcome or Learn be the default tab for a new user after the run
   opens?
2. Should Models be a selected-run-only surface first, or also a global library
   entry point before a run is selected?
3. Should Relations behave like pages, drawers, or both?
4. Should Receipts be a permanent tab, a drawer, or both?
5. Should Conversation Understanding remain only in Receipts, or also appear as
   a compact header status?
6. Should Map default to learning neighborhood or run activation when both are
   present?

## Decision Gate

Recommended next gate:

```text
proceed_to_observatory_portable_server_view_model_contracts
```

The decision is global: stop expanding Observatory through isolated product
patches until the portable product view-model layer is clear.
