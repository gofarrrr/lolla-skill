# Observatory Workspace Content Audit And Simplification v0

Status: browser-audited design slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_model_relation_content_simplification`

## Purpose

This slice records what the selected-run Observatory workspace currently shows,
what each surface is supposed to do, and how information should progress from a
simple first read into optional detail.

The product problem is not only routing. The problem is meaning:

- what data are we showing;
- why should the user care;
- what should be shown first;
- what should be expanded only when needed;
- what belongs in Receipts or Advanced Audit instead of the learning product.

This is a design/audit PR. It does not change runtime behavior or rendering.

## Product Frame

The selected-run Observatory should be the single home after a skill run.

It should answer, in order:

1. What changed or survived in the run?
2. What reasoning move can I practice?
3. Which mental models help explain that move?
4. What relationship between models is the lesson?
5. How do I navigate the small neighborhood?
6. What can I trust, inspect, or treat as missing?

The information progression remains:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

## Data Classes

### First-Class Product Data

First-class product data is what a user should understand without becoming an
operator:

- the selected run outcome;
- the Teacher practice move;
- mental model names and one-sentence meaning;
- relation story in plain language;
- small graph wayfinding;
- visible non-claims.

### Second-Class Support Data

Second-class support data can help a curious user, but should not lead:

- source refs;
- missingness;
- curation status;
- confidence labels;
- model ids and relation ids;
- run id and health status;
- source-backed failure/practice details.

These belong behind disclosure blocks or on drill-down pages.

### Technical Inspection Data

Technical inspection data is for review, debugging, or custody:

- audit routes;
- extraction detail;
- usage;
- raw artifact status;
- packet API shape;
- graph source artifacts;
- sidecar status.

These belong in Receipts or Advanced Audit, not in the first learning view.

## Current Surface Audit

### Workspace Shell

Current browser evidence:

- default route: `/workspace?case_id=lolla-audit`;
- visible section: Outcome;
- visible top navigation: Outcome, Learn, Models, Relations, Map, Receipts;
- persistent Start Here card: Read outcome, Practice lesson, Open model cards,
  Check receipts;
- sidebar: run context and surface homes.

Intended role:

- orient the user;
- make the sequence easy to follow;
- make switching surfaces predictable.

Keep:

- the shared top navigation;
- the Start Here path;
- one active section at a time.

Watch:

- the sidebar still uses compact operator language. It is acceptable for now,
  but later it should become less technical or collapse on small screens.

### Outcome

Current browser evidence:

- heading: Outcome;
- first read: answer headline and summary;
- actions: Practice the lesson, Open model cards;
- support details: strongest pressure, model chips, missingness.

Intended role:

- answer: "what happened in this run?";
- anchor the rest of the learning surface in the actual case;
- provide only enough context to make Learn meaningful.

First read should show:

- outcome headline;
- short plain-language summary;
- two next actions: practice lesson and inspect models.

Expandable detail should show:

- strongest pressure;
- supporting model chips;
- missingness.

Do not show:

- raw result JSON;
- full audit details;
- proof or correctness labels.

### Learn

Current browser evidence:

- heading: Learn;
- practice title: Test The Authority, Not The Aura;
- links to relation lesson and map;
- model links: Authority Bias, Information Asymmetry, First Principles Thinking;
- relation link: authority bias plus first principles thinking plus antagonist.

Intended role:

- teach a reasoning move from this case;
- make the practice rep the product value;
- explain the model relationship enough to motivate the rep.

Teacher information differs from model information:

- Teacher is case anchored;
- Teacher is about a reasoning move;
- Teacher asks the user to practice;
- Teacher should not pretend the lesson proves the answer was correct.

First read should show:

- one practice title;
- one short explanation of the move;
- one user action.

Expandable detail should show:

- case anchor;
- reasoning trap;
- thinking move;
- model relationship;
- worked example;
- do-not-overlearn boundary.

Do not show:

- every model detail;
- raw source custody;
- confidence as certification.

### Models

Current browser evidence:

- heading: Models;
- three model cards;
- each card says What This Model Helps You See;
- each card links to Open model page.

Intended role:

- let the user browse reusable mental model knowledge;
- make each model recognizable before opening the full page;
- avoid turning the Learn page into a model encyclopedia.

Model information differs from Teacher information:

- model pages are reusable concepts;
- model pages should be independent of one case;
- model pages can expose canonical-source-derived use/avoid/failure detail;
- model pages should preserve source custody and missingness.

First read should show:

- model display name;
- one-sentence meaning;
- use-when cue;
- mislead cue;
- one click to full model page.

Expandable or drill-down detail should show:

- helps notice;
- use when;
- avoid when;
- common misuse;
- failure modes;
- practice prompts;
- source/status/boundaries.

Next simplification:

- the Models surface should become a lighter model index, not three near-full
  model pages stacked in the workspace.
- the full model detail should live primarily on `/models/<model-id>`.

### Model Page

Current browser evidence:

- example route: `/models/authority-bias?case_id=lolla-audit`;
- title: Authority Bias;
- first read: What This Model Helps You See;
- detail headings: Use when, When it misleads, Practice this, Missingness.

Intended role:

- present everything product-safe that we know about one canonical model;
- format canonical Markdown and curated fields as a readable product page;
- remain separate from the case-specific Teacher lesson.

Keep:

- clean first read;
- full model page route;
- source and missingness after the user understands the model.

Improve later:

- add clearer canonical-source sections when the full model-source Markdown is
  product-safe to expose;
- avoid repeating the model title twice in the first viewport.

### Relations

Current browser evidence:

- heading: Relations;
- relation: Authority Bias and First Principles Thinking;
- first detail: Plain Language Story;
- then Why It Matters, Misread Risk, Practice prompt, Taxonomy;
- link to Open relation page.

Intended role:

- teach why a pair of models matters;
- make the edge understandable before taxonomy;
- support the Teacher move without turning the edge into proof.

Relation information differs from model information:

- relation pages are about a pair, not a concept;
- relation pages should explain the interaction;
- relation pages can carry confidence and curation status, but those are support
  details.

First read should show:

- plain-language story;
- why it matters;
- misread risk;
- practice prompt.

Expandable detail should show:

- taxonomy;
- confidence;
- source refs;
- missingness;
- non-claims.

Next simplification:

- the Relations surface can stay story-first, but taxonomy should remain behind
  disclosure unless the user opens the relation page.

### Relation Page

Current browser evidence:

- example route:
  `/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit`;
- title: Authority Bias and First Principles Thinking;
- headings: Plain Language Story, Why It Matters, Misread Risk, Practice
  prompt, Taxonomy, Missingness;
- links back to both model pages.

Intended role:

- present the edge as a lesson;
- explain the pair before exposing the technical relation type;
- keep confidence clearly non-certifying.

Keep:

- story before taxonomy;
- model links;
- explicit non-claims and missingness.

Improve later:

- reduce duplicate relation title repetition in the first viewport.

### Map

Current browser evidence:

- heading: Map;
- graph controls: search, All, antagonist, Reset;
- selected node panel;
- model and relation links;
- edge copy: edges are navigation, not proof.

Intended role:

- give spatial wayfinding for one small lesson neighborhood;
- let the user jump to models and relation pages;
- help the user see "this lesson is a relationship", not a pile of cards.

First read should show:

- why the map exists;
- the selected model or relation;
- basic controls.

Do not show:

- full-corpus graph;
- ranking or affinity as truth;
- embedding similarity as relation validation.

### Receipts

Current browser evidence:

- heading: Receipts;
- trust summary: What can I trust or inspect?;
- status chips: Teacher packet, Conversation Understanding, Process brief;
- visible non-claims;
- technical links: Extraction audit, Usage, Advanced audit.

Intended role:

- keep custody and missingness visible without overwhelming the learning path;
- make technical inspection reachable;
- stop product pages from pretending to be proof.

First read should show:

- availability status;
- non-claims;
- inspection links.

Expandable detail should show:

- source refs;
- missingness;
- technical audit index;
- workspace boundary notes.

## Simplification Decisions

The product should not show everything at once.

Use this ladder:

```text
first read -> expandable support -> drill-down page -> receipts/audit
```

Rules:

- Outcome is the case anchor.
- Learn is the reasoning move.
- Models are reusable concept pages.
- Relations are pair lessons.
- Map is navigation.
- Receipts are custody and missingness.
- Advanced Audit is technical inspection.

Do not duplicate:

- a standalone Teacher page outside the workspace;
- full model detail inside the Learn surface;
- raw telemetry in the first read;
- confidence as a proof label;
- graph edges as evidence of correctness.

## Recommended Next Implementation PR

Proceed to:

```text
proceed_to_observatory_model_relation_content_simplification
```

Implement:

- make the Models workspace surface a lighter model index of cards;
- keep full canonical-source-derived detail on `/models/<model-id>`;
- keep Relations story-first and push taxonomy/custody behind disclosure;
- reduce duplicated model/relation titles in first viewports;
- preserve Receipts and Advanced Audit links.

Stop before:

- runtime integration;
- full corpus graph;
- provider or model API calls;
- new Lolla runs;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.

## Boundaries

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new Lolla runs;
- does not wire runtime behavior;
- does not mutate archives;
- does not write sidecars;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.
