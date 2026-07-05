# Mental Model Teacher Observatory Integration Design v0

Status: design contract
Date: 2026-07-05
Decision gate: `proceed_to_observatory_teacher_shell_prototype`

## One Sentence

Mental Model Teacher should become a learner layer inside Observatory, not a
second UX: after a run, the user sees one post-run workspace with Outcome,
Learn, Models, Relations, Map, Receipts, and Advanced telemetry areas.

## Why This Exists

The Mental Model Teacher roadmap produced a useful learner-first prototype, but
it currently lives outside Observatory. Observatory already exists as the
post-run surface for a Lolla run. If both surfaces continue independently, the
product will ask the user to choose between two versions of the same run:

- Observatory explains what happened in the audit.
- Teacher explains what the user can learn from the audit.
- Both surfaces touch the same case, selected models, model relationships,
  graph neighborhoods, source custody, and non-claims.

Those should not be two products.

The integration principle is:

```text
Observatory is the house.
Teacher is a room in the house.
The mental model library is a reusable shelf in that room.
Telemetry is the utility closet, not the living room.
```

## Current Surfaces

### Observatory Today

Observatory is the local post-run shell. It already provides:

- case/archive selection;
- run health;
- revised answer display;
- structural pressure;
- model companion;
- frame pressure;
- structural coverage;
- reasoning graph;
- knowledge substrate stats;
- family browsing;
- model detail drawer;
- selected-run custody artifact links;
- server-rendered audit and usage panels.

Relevant current routes and APIs:

| Area | Current shape | Product meaning |
|---|---|---|
| `/` | Observatory SPA | Primary post-run workspace |
| `/api/cases` | Current plus archived runs | Choose a run |
| `/api/case/<id>` | Run summary payload | Feed the post-run workspace |
| `/api/case/<id>/graph` | Current reasoning graph | Run activation neighborhood |
| `/api/model/<model_id>` | Model detail from knowledge graph | Existing model detail drawer |
| `/api/families` | Family clusters | Browse model groupings |
| `/audit/*` | Server-rendered telemetry | Advanced custody/debug surface |
| `/usage` | Cost/call telemetry | Advanced run telemetry |

Observatory's current limitation is not that it lacks a shell. It has one. The
problem is that it currently treats learning as fragments inside audit cards
rather than as a guided post-run mode.

### Teacher Prototype Today

The learner-first Teacher prototype proves a better presentation sequence:

```text
case anchor -> reasoning trap -> thinking move -> model relationship -> practice rep
```

It also separates:

- `Learn`: case-specific teaching;
- `Models`: durable mental model pages;
- `Relations`: model-pair pages;
- `Map`: focused graph neighborhood;
- `Review`: source checks and missingness.

That mode split should move into Observatory. The standalone prototype should
remain a design reference, not the final product shell.

## Product Decision

Use one post-run workspace:

```text
Observatory
  Run picker
  Selected run header
  Primary tab set:
    Outcome
    Learn
    Models
    Relations
    Map
    Receipts
  Advanced:
    Telemetry / audit / usage
```

Do not ship a separate `Teacher` app beside Observatory.

Do not make a second static product page that duplicates Observatory's selected
run, graph, model detail, or receipts.

## User Flow

### Flow 1: Normal Post-Run User

1. User runs Lolla.
2. Observatory opens on the selected run.
3. Header answers:
   - What run am I looking at?
   - Is run health OK, degraded, or partial?
   - Was this current or archived?
4. Default tab is `Outcome`.
5. User sees the revised answer and the major audit pressure.
6. User can switch to `Learn` to understand the transferable reasoning move.
7. User can click a model to open the durable model page.
8. User can click a relation to understand a model pair.
9. User can open `Map` to see the small neighborhood.
10. User can open `Receipts` for source custody and missingness.
11. Advanced users can open `/audit` or `/usage`.

The normal user should not need to inspect raw telemetry to understand what to
do next.

### Flow 2: Learner Mode

In `Learn`, the selected run becomes a teaching object:

```text
This was the situation.
This was the reasoning trap.
This is the move worth learning.
These models explain the move.
This relation is the lesson.
Try this short practice rep.
Do not overlearn beyond this boundary.
```

The user should see one lesson at a time. Teacher should not present all
artifacts, all model cards, all graph nodes, all receipts, and all review data
on the same screen.

### Flow 3: Model Study

The user clicks a model from Outcome, Learn, Relations, Map, or Families.

The model page answers:

- What is this model?
- What does it help notice?
- When should it be used?
- When should it be avoided?
- What are common failure modes?
- What practice prompts train it?
- Where did it appear in this run?
- What other lessons or relations link to it?

It should not be a raw canonical Markdown dump. It should be a formatted product
object powered by canonical source and curation.

### Flow 4: Relation Study

The user clicks a model pair or graph edge.

The relation page answers:

- What does this pair teach?
- Are the models allies, antagonists, guardrails, or in structured tension?
- Why did this relation matter in the selected run?
- How might the user misread the relation?
- What short practice rep trains the distinction?
- Which model pages and lessons link back to it?

The graph edge is a navigation affordance. The relation page is the explanation.

### Flow 5: Reviewer Or Maintainer

The reviewer opens `Receipts` or Advanced telemetry to inspect:

- source refs;
- missingness;
- curation status;
- run health;
- selected-run sidecars;
- evaluation artifact;
- reasoning trace;
- graph survival report;
- usage/cost telemetry.

This material should be reachable, but it should not compete with the learner
surface for primary attention.

## Primary Navigation

After a run is selected, Observatory should use this primary tab set:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Advanced telemetry remains reachable through:

```text
Advanced telemetry
Audit panels
Usage
Raw sidecars
```

The label `Telemetry` should not be the main product tab for the normal user.
It should remain a specialized inspection path.

## Responsibilities By Area

| Area | Primary job | Should show | Should not show |
|---|---|---|---|
| Outcome | What changed in the answer | revised answer, strongest pressure, run status, compact model chips | full canonical model pages, raw curation, relation taxonomy wall |
| Learn | Teach one reasoning move | situation, trap, move, relation story, practice rep, boundary | raw telemetry, raw Teacher notes, review controls, full graph |
| Models | Explain reusable models | model pages, use/avoid, failure modes, practice, backlinks | case-specific lesson as the main identity |
| Relations | Explain model pairs | plain-language relation story, why it matters, misuse risk, practice | naked edge labels without explanation |
| Map | Navigate the neighborhood | small graph, selected node/edge panel, filters, links | proof language, full corpus as default |
| Receipts | Show custody and missingness | source refs, sidecars, non-claims, status | primary teaching narration |
| Advanced | Debug and audit | `/audit/*`, `/usage`, raw traces | learner-facing onboarding |

## What Must Not Be Presented Twice

The goal is not to hide information. The goal is to assign each information type
one home and link to it from other homes.

| Information | Single home | May link from | Do not duplicate as |
|---|---|---|---|
| Revised answer | Outcome | Receipts, memo | Teacher lesson body |
| Structural pressure findings | Outcome | Learn, Receipts | Relation page proof |
| Teacher reasoning move | Learn | Outcome summary, model backlinks | telemetry panel copy |
| Canonical model explanation | Models | Outcome, Learn, Relations, Map | model companion chunks |
| Model activation evidence | Outcome or Receipts | Models | durable model definition |
| Relation explanation | Relations | Learn, Map | graph edge label only |
| Graph neighborhood | Map | Outcome preview, Learn preview | separate Teacher graph app |
| Run health | Header and Receipts | Advanced telemetry | repeated warning tags in every tab |
| Source custody | Receipts | Models, Relations, Learn drawers | primary lesson copy |
| Usage/cost telemetry | Advanced `/usage` | Receipts | learner-facing proof |
| Graph survival/evals | Advanced or Receipts | Map caveat | product marketing |
| Family clusters | Models/Families area | Map | second model library |

## Information Flow

### Existing Run Data

Observatory already reads:

```text
result.json
agent_result.json
reasoning_trace.json
evaluation.json
run_events.json
memo.md
graph_survival_report.*
knowledge_graph.json
family_semantics/*.json
```

Those remain the custody and runtime artifacts.

### New Product-Safe Learning Data

Teacher integration should introduce a selected-run learning packet:

```text
teacher_learning_packet.v0
```

The packet should be derived from existing run artifacts and the knowledge
substrate. It should not call providers, run Lolla, judge answer quality, or
change runtime behavior.

Suggested top-level shape:

```json
{
  "schema_version": "lolla.observatory_teacher.learning_packet.v0",
  "run_id": "...",
  "case_id": "...",
  "lesson": {},
  "models": [],
  "relations": [],
  "graph": {},
  "receipts": {},
  "non_claims": {}
}
```

### API Shape

The eventual Observatory endpoints should be selected-run scoped:

| Endpoint | Purpose |
|---|---|
| `/api/case/<id>/learning` | Teacher lesson for this run |
| `/api/case/<id>/learning/models` | Product-safe model objects used in this run |
| `/api/case/<id>/learning/relations` | Product-safe relation objects used in this run |
| `/api/case/<id>/learning/graph` | Teacher-focused graph neighborhood |
| `/api/case/<id>/learning/receipts` | Source refs and missingness for learning packet |

These endpoints should return product-safe translated objects, not raw
Observatory telemetry and not raw canonical Markdown.

## Relationship To Existing Observatory Components

### Structural Pressure

Structural Pressure belongs in `Outcome`.

It answers:

```text
What pressure did Lolla apply to the original answer?
```

Teacher may refer to the same model IDs, but Teacher answers a different
question:

```text
What reasoning move can I learn from this?
```

Do not copy Structural Pressure text into Learn mode. Summarize the learning
move separately.

### Model Companion

Model Companion currently explains selected model chunks and evidence from the
run. It is evidence and routing context.

It should not become the durable model page.

Future split:

- `Outcome`: compact model companion / why these models fired.
- `Models`: durable model page / what the model means and how to use it.
- `Receipts`: selected chunks and custody details.

### Reasoning Graph

The current reasoning graph is a run-activation graph:

- companion models;
- chunk-referenced models;
- KG neighbors;
- tendencies;
- edges from knowledge graph.

Teacher Map is a learning graph:

- selected lesson models;
- selected relation objects;
- practice-oriented neighborhood;
- links to relation pages.

There should not be two separate graph products. Use one `Map` area with
view/filter modes:

```text
Run activation | Learning neighborhood
```

The graph component can support both, but the user should not see duplicate
graph widgets in separate parts of the product.

### Families

Families are useful model-library navigation. They should live under `Models` or
as a secondary top-level browsing mode before a run is selected.

They should not be a separate product that competes with model pages.

### Audit Panels

`/audit/*` remains advanced telemetry.

It should not be renamed into Teacher. It should not be asked to teach. It
should answer:

```text
What happened in the system?
What artifacts exist?
What was complete, partial, missing, or degraded?
```

## Proposed Layout

### Run Header

Always visible after run selection:

```text
Run title
Run health
Risk mode
Current/archive status
Open receipts
Open advanced telemetry
```

### Outcome Tab

Default for existing Lolla users.

Content order:

1. Short run summary.
2. Revised answer.
3. Strongest pressure / key finding.
4. Compact selected model chips.
5. Link: "Learn the reasoning move from this run."
6. Link: "Inspect receipts."

### Learn Tab

Default candidate for new learning-oriented users.

Content order:

1. Case anchor.
2. Reasoning trap.
3. Thinking move.
4. Model relationship story.
5. Practice rep.
6. Do-not-overlearn boundary.
7. Explore next: model pages, relation page, map.
8. Collapsed receipts.

### Models Tab

Content order:

1. Models used in this run.
2. Search/filter model library.
3. Selected model detail.
4. Appears in this run / related lessons.
5. Related models and relations.
6. Receipts drawer.

### Relations Tab

Content order:

1. Relations used in this run.
2. Selected relation explanation.
3. Why it mattered here.
4. Misread risk.
5. Practice prompt.
6. Links to the two model pages.
7. Open in Map.

### Map Tab

Content order:

1. Toggle: Run activation / Learning neighborhood.
2. Small graph.
3. Selected node panel.
4. Selected edge panel.
5. Relation-type filters.
6. Links to model/relation pages.
7. Clear caveat: graph is navigation, not proof.

### Receipts Tab

Content order:

1. Learning packet status.
2. Source refs.
3. Missingness.
4. Non-claims.
5. Selected-run sidecars.
6. Link to advanced telemetry.

## Copy Boundaries

Use product words in primary tabs:

- situation;
- trap;
- reasoning move;
- model;
- relationship;
- practice;
- boundary;
- source.

Keep system words in Receipts or Advanced:

- ledger;
- sidecar;
- V60;
- chunk;
- reranker;
- extraction call;
- eval artifact;
- graph survival;
- raw trace.

Do not make the learner decode telemetry vocabulary before they understand the
lesson.

## Implementation Sequence

### PR-O1 Design Contract

Add this document and tests.

Stop before UI changes.

### PR-O2 Learning Packet Contract

Define selected-run `teacher_learning_packet.v0` objects:

- lesson;
- model cards;
- relation cards;
- graph neighborhood;
- receipts;
- non-claims.

Use small fixtures. No provider calls. No runtime wiring.

### PR-O3 Offline Learning Packet Builder

Build packet from archived run artifacts and existing knowledge substrate.

Stop before Observatory UI.

### PR-O4 Observatory API Endpoints

Expose selected-run learning endpoints from Observatory.

Stop before changing the SPA.

### PR-O5 Observatory Shell Prototype

Add visible tab integration in Observatory:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Use fixture or generated learning packet.

### PR-O6 Merge Model Detail Behavior

Make current model drawer/page use the product-safe model object, while retaining
model activation evidence in Outcome/Receipts.

### PR-O7 Merge Map Behavior

Unify the current reasoning graph and Teacher graph into one Map area with
filters/layers.

## Stop Conditions

Stop if implementation would require:

- running Lolla;
- invoking the Lolla skill;
- provider/model API calls;
- creating a new Lolla run;
- changing runtime behavior;
- authorizing action;
- claiming product proof;
- claiming human validation;
- claiming answer or advice correctness;
- treating graph edges as proof;
- treating embedding similarity as validated relation semantics.

## Open Design Questions

1. Should `Outcome` or `Learn` be the default tab for a fresh post-run user?
2. Should archived runs without a learning packet show a disabled Learn tab or
   generate a packet on demand?
3. Should `Families` remain a pre-run/library browsing mode, or become a
   subsection of `Models` only?
4. Should `Receipts` be a tab, a drawer, or both?
5. Should Advanced telemetry remain a FAB, move into Receipts, or stay both?

## Decision Gate

Recommended next gate:

```text
proceed_to_observatory_teacher_learning_packet_contract
```

The key decision is that Teacher joins Observatory as a selected-run learning
mode. We do not build or maintain two separate UX/UI products for the same run.
