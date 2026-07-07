# Observatory Content Progression PRD v0

Status: planning PRD.

Date: 2026-07-07

Decision gate: `proceed_to_observatory_content_progression_implementation`

Depends on:

- [Observatory Run Data Visibility Matrix](observatory-run-data-visibility-matrix-v0.md)
- [Observatory Run Inventory Receipt Panel](observatory-run-inventory-receipt-panel-v0.md)
- [Observatory Outcome User Value PRD](observatory-outcome-user-value-prd-v0.md)
- [Observatory Outcome First Viewport](observatory-outcome-first-viewport-v0.md)

## Purpose

This PRD defines the global Observatory content progression before we add more
UI.

The current product risk is not lack of data. The risk is that the selected run,
Teacher lesson, mental model library, relation pages, graph, receipts, agent
memory, and technical audit can all appear to have the same priority. When that
happens, the page feels like everything at once: product, telemetry, review,
and implementation notes mixed together.

The product goal is:

```text
start from the selected run
  -> understand the outcome
  -> learn one reasoning move
  -> inspect the mental models
  -> understand the model relationship
  -> navigate the small map
  -> account for receipts, missingness, export, and audit
```

This is not a request to hide gathered data. The rule is:

```text
If we gather it, the user should be able to account for it.
```

But accountable does not mean first-read. Some data belongs as a visible
summary, some as expandable product detail, some as a receipt, some as private
Markdown export, some as technical inspection, and some as future design.

## Core Product Thesis

The Observatory is the selected-run home after the skill produces a result.

It should preserve the earlier product thesis:

```text
case is the anchor
reasoning move is the subject
model relationship is the lesson
practice rep is the product value
```

The corresponding Observatory thesis is:

```text
selected run is the anchor
outcome is the first read
Teacher is the practice layer
models are reusable concepts
relations are model-pair lessons
map is navigation
receipts are accountability
Download MD is private agent memory
Advanced Audit is technical inspection
```

In plain language: Outcome is the first read, Teacher is the practice layer,
models are reusable concepts, relations are model-pair lessons, map is
navigation, receipts are accountability, Download MD is private agent memory,
and Advanced Audit is technical inspection.

## Non-Goals

This PRD does not ask us to:

- rebuild the old SPA;
- revive Svelte as the product owner;
- create a second runtime;
- call providers or model APIs;
- run Lolla;
- create new Lolla runs;
- wire default runtime behavior;
- generate Teacher packets from missing data;
- treat graph edges as proof;
- treat embedding similarity as validated relation semantics;
- claim product proof, human validation, answer correctness, or advice
  correctness.

## Content Counts

The current design should track three different counts:

| Count | Meaning | Product implication |
| --- | --- | --- |
| 48 broad data/source families | The existing visibility matrix names the broader universe of gathered or known substrate families. | This is the accountability universe, not a first screen. |
| 29 current run-inventory UI families | The Receipts inventory groups the currently implemented selected-run and substrate families into UI-accountable cards. | These should be discoverable through Receipts, export, or technical inspection. |
| 8 first-read product-path families | Selected run context, Outcome, strongest pressure, Teacher lesson, practice rep, model pages, relation pages, and selected-run map. | These are the only families allowed to compete for normal product attention. |

The first-read goal is therefore not "show 29 things." The goal is:

```text
show the 8 product-path families in a readable order
account for the other 21 current UI families through Receipts/export/audit
preserve the broader 48-family matrix as the source-of-truth inventory
```

## Current 29-Family UI Accounting

The current Receipts inventory groups 29 families:

| Group | Count | Families |
| --- | ---: | --- |
| First-read product path | 8 | Selected run context, Outcome summary, Strongest pressure, Teacher lesson, Practice rep, Mental model pages, Relation pages, Selected-run map |
| Conversation and interpretation | 4 | Conversation transcript, Conversation Understanding, Reasoning trace, Suppressed or unadjudicated signals |
| Memory, receipts, and sidecars | 4 | Agent memory Markdown, Memo artifact, Process brief sidecar, Source custody and non-claims |
| Technical and operator inspection | 8 | Result object, Agent result object, Evaluation artifact, Run events, Usage telemetry, Graph survival, Private tables and ledgers, Operator log |
| Library substrate accounted for | 5 | Canonical model Markdown, Activation and intervention curation, Relation semantics, Relationship graph substrate, Knowledge graph and embeddings |

This is the shape the UI should teach gradually, not throw at the user as a
table.

## Surface Responsibilities

Each surface needs one job.

| Surface | First question it answers | What it should show first | What can expand | What it must not become |
| --- | --- | --- | --- | --- |
| Header and run picker | Which run is this? | Case/run identity, health, current/archive state | Run switching, availability status | A telemetry dashboard |
| Outcome | What did the run conclude or change? | Full result, what changed, main reasons, confidence boundary, next moves | strongest pressure, model chips, missingness, non-claims | A navigation tutorial or audit index |
| Learn | What reasoning move can I practice? | Case anchor, thinking move, relation story, practice rep, do-not-overlearn boundary | worked example, model/relation links | A second answer engine |
| Models | What do these mental models mean? | Display name, one-sentence meaning, helps-notice, use/avoid cue | canonical-source translation, failures, premortems, practice prompts, source custody | Raw Markdown dump or proof label |
| Relations | How do these models interact? | Plain-language relation story, why it matters, misread risk, practice prompt | taxonomy, confidence, source refs, model links | Graph-edge proof or confidence certification |
| Map | Where can I navigate next? | Small selected-run neighborhood, search, filters, selected node/edge panel | model/relation links, local neighborhoods | Full-corpus truth graph |
| Receipts | What exists, what is missing, what is private, and what is not claimed? | Trust summary, status chips, inventory counts, visible non-claims | grouped inventory, source refs, missingness, advanced links | Primary product copy |
| Download MD | How can a future agent understand this run? | One explicit button with hover/focus help | private Markdown with source map and raw transcript when present | Default-on generation or public-safe proof |
| Advanced Audit | What exactly happened under the hood? | Optional technical route index | extraction, usage, trace, events, eval, graph survival | User-facing product path |
| Operator inspection | What does a maintainer need to debug? | Nothing by default | private ledgers, vectors, provider-private bodies, logs | Normal user UI |

## Default User Progression

The normal user path should be:

1. `Outcome`: read what the run concluded or changed.
2. `Learn`: practice the reasoning move if a Teacher packet exists.
3. `Models`: open the reusable mental models behind the lesson.
4. `Relations`: understand the model-pair story before graph language.
5. `Map`: navigate the small model/relation neighborhood.
6. `Receipts`: check what exists, what is missing, what is private, and what is
   not claimed.
7. `Download MD`: export a private memory file when a future agent needs the
   full run.
8. `Advanced Audit`: inspect technical evidence only when needed.

The page should not present this as repeated ceremony in the center. Navigation
can show the path. The center should show the selected surface.

## Expansion Ladder

Every gathered family needs a depth assignment.

| Depth | Name | User experience | Examples |
| --- | --- | --- | --- |
| 0 | First read | visible without opening anything | selected run context, full Outcome answer, confidence boundary |
| 1 | Primary surface | one click from top nav | Learn, Models, Relations, Map, Receipts |
| 2 | Product detail | expandable section or detail route | model page, relation page, local model neighborhood |
| 3 | Receipt | status/count/source/missingness accounting | run inventory, non-claims, Teacher packet status |
| 4 | Private export | explicit download action | Conversation Memory Markdown, raw 1:1 transcript when present |
| 5 | Technical inspection | audit route | extraction, usage, reasoning trace, run events, graph survival |
| 6 | Operator inspection | local/operator-only detail | private ledgers, provider-private bodies, embeddings/vectors |
| 7 | Future design | acknowledged but not yet productized | global graph, semantic-neighbor browsing, V60 affordance pages |

This ladder lets us "show everything" without placing everything on the same screen.

## What Users Should See By Default

Default Outcome viewport:

- selected run context;
- visible `Download MD`;
- outcome headline;
- full plain-language answer;
- what changed;
- main reasons;
- confidence boundary;
- two or three next useful moves;
- a short availability signal if Teacher surfaces are missing.

Default Learn viewport:

- the teachable move;
- the case anchor;
- the relation story;
- the practice rep;
- the do-not-overlearn boundary.

Default Models viewport:

- model cards, not full model files;
- enough meaning to know whether to open a model;
- clear separation between selected-run context and reusable model meaning.

Default Relations viewport:

- relation story first;
- why it matters;
- misread risk;
- practice prompt;
- links to both model pages.

Default Map viewport:

- a small graph;
- search;
- relation filters;
- selected node/edge panel;
- links to model/relation pages;
- visible non-claim that edges are navigation, not proof.

Default Receipts viewport:

- trust summary;
- Teacher packet status;
- Conversation Understanding status;
- process brief status;
- inventory counts;
- `Download MD`;
- visible non-claims.

## What Should Not Be First-Read UI

The following should be discoverable but not first-read product copy:

- raw JSON;
- raw canonical Markdown;
- local absolute paths;
- schema fields;
- hashes;
- prompt/provider details;
- usage telemetry;
- routing internals;
- evaluation internals;
- private tables and ledgers;
- raw embeddings/vectors;
- provider-private reasoning bodies;
- Product Delta/eval internals;
- CodeRabbit or internal review prompts;
- product-readiness or validation labels.

## Teacher vs Model vs Relation Information

Teacher information is case anchored.

Teacher asks:

```text
What reasoning move can the user practice because of this run?
```

Teacher should show case anchor, thinking move, relation story, practice rep,
worked example when available, and a do-not-overlearn boundary.

Model information is concept anchored.

Model pages ask:

```text
What does this mental model help me notice, when should I use it, and when can it mislead me?
```

Model pages should translate canonical Markdown and curation into readable
sections. They should not expose raw Markdown as the product UI.

Relation information is interaction anchored.

Relation pages ask:

```text
What does this pair of models teach together?
```

Relation pages should lead with plain-language story and practice, then show
taxonomy, confidence, custody, and non-claims later.

## Missingness Behavior

Missingness is not failure if it is clear and honest.

If a Teacher packet is absent:

- Outcome still renders from the selected run when a result exists;
- Receipts still renders status, inventory, non-claims, and export;
- Learn, Models, Relations, and Map show explicit missing source-artifact
  sections;
- the UI must not invent a lesson, model page, relation story, or graph.

If `revised_answer` is absent:

- Outcome should say the outcome artifact is unavailable;
- other available artifacts can still be accounted for;
- the page should not fill the gap with reading-path ceremony.

If Raw transcript exists:

- Receipts should show that it exists;
- `Download MD` can include it by explicit private export;
- the normal UI should not dump the full transcript by default.

## Library And Graph Progression

The graph should come after content responsibilities are clear.

Near-term progression:

1. model detail pages show reviewed local neighborhoods from the relationship
   graph where source-backed relation data exists;
2. relation pages remain the target for edge meaning;
3. selected-run Map remains a small navigation surface;
4. global graph remains future design until search, filtering, density, and
   relation review rules are ready.

The relationship graph can fix the "only one connection" problem on model
pages, but it should do so as a local reviewed neighborhood before becoming a
full-corpus graph.

## Implementation Requirements For Next UI Slice

The next implementation PR should:

- keep Outcome as the default center surface;
- keep `Download MD` visible on the main page;
- show first-read content before inventory or telemetry;
- make unavailable Teacher surfaces explicit without blocking Outcome;
- use the 29-family receipt as the current UI accounting surface;
- preserve the 48-family visibility matrix as the broader accountability
  source;
- avoid a giant table in user-facing UI;
- make product detail expandable from readable cards;
- leave advanced audit and operator inspection out of the normal path.

## Review Questions

Before another graph or detail-heavy UI slice, review:

1. Are the 8 first-read product-path families the right first-read set?
2. Should `Download MD` remain in the hero, or should it move to a persistent
   utility position?
3. Should run contents remain inside Outcome or move fully into Receipts?
4. Should model pages start with reusable canonical meaning or selected-run
   role context? Current recommendation: reusable meaning first, selected-run
   role second.
5. Should the next graph work be model-detail local neighborhoods before a
   global graph? Current recommendation: yes.
6. Which of the 48 broad families should remain consolidated rather than
   becoming separate UI cards?
7. Which fields are agent-useful but human-overwhelming and therefore belong
   mainly in `Download MD`?

## Boundary

This PRD:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.

## Recommended Next Gate

`proceed_to_observatory_content_progression_implementation`

Reason: this PRD gives the next implementation slice a product rulebook. The
next PR should implement only one UI change against this progression, likely a
first-read/Receipts refinement or a model-detail local-neighborhood refinement,
not a global graph.
