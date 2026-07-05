# Mental Model Teacher Learner Experience Design v0

Status: design note
Date: 2026-07-05
Decision gate: `decide_learner_first_surface_before_more_ui_build`

## One Sentence

Mental Model Teacher should open as a guided learning experience: a user sees one
case, one reasoning move, the model relationship that teaches the move, and one
practice rep; model pages, relation pages, graph neighborhoods, source receipts,
and review tools are available, but they are not all shown at once.

## Why This Exists

The current roadmap has built useful substrate:

- inventory and exposure rules;
- product-safe contracts;
- pilot model and relation page data;
- Markdown renderers;
- Teacher lesson pages;
- graph-neighborhood data;
- a static graph prototype;
- three-case pilot lessons;
- review packets and package gates;
- a visible review surface.

That is not yet the user experience.

The visible review surface proved the problem: it mixes lesson content, model
data, relation data, graph data, source snapshots, review controls, non-claim
labels, and package status into one page. That may help us inspect artifacts,
but it does not teach. A learner needs sequence, narration, and progressive
disclosure.

This document defines the intended experience before more UI is built.

Reference synthesis:
[Mental Model Teacher PKM Reference Synthesis](mental-model-teacher-pkm-reference-synthesis-v0.md)

## Product Thesis

The product is not "show everything Lolla knows."

The product is:

```text
Here is a situation.
Here is the reasoning trap.
Here is the move that helps.
Here are the mental models in tension or support.
Here is how the relation teaches the move.
Here is a short rep so you can practice it.
Here is where this lesson stops.
```

The library exists so the user can then continue:

```text
What is this model?
What other models support or challenge it?
Where else did this relation appear?
How do I practice the distinction again?
```

## Primary Audience

The first product audience is a learner who wants to understand a reasoning move,
not an internal reviewer trying to audit a pipeline.

Secondary audiences:

- a reviewer checking whether the page overclaims;
- a builder checking source custody and missingness;
- a future curator deciding which model and relation pages need revision.

The UI must support those secondary audiences through modes, drawers, and review
pages, not by making the learner page carry everything.

## Design Principles

### One Screen, One Job

Every screen should have a primary job.

| Surface | Primary job |
|---|---|
| Teacher lesson | Teach one transferable reasoning move from a case |
| Mental model page | Explain one durable model and when it helps or misleads |
| Relation page | Explain why two models should be considered together |
| Graph neighborhood | Let the user explore nearby models and relations |
| Review mode | Let a human compare product copy against source artifacts |
| Receipts drawer | Show source custody without interrupting the lesson |

If a screen tries to teach, audit, review, and debug at the same time, it fails.

### Narration Before Navigation

The user should first understand what they are looking at. Navigation should come
after the first explanation, not before it.

Default order:

1. What case are we anchoring on?
2. What reasoning trap is present?
3. What move should I learn?
4. Which model relationship teaches the move?
5. What does the move look like in practice?
6. Where can I explore next?

### Relations Are Product Objects

The graph edge is not the product. The relation page is the product.

A relation must answer:

- What does this pair teach?
- Are the models allies, antagonists, guardrails, or a structured tension?
- Why does that matter in ordinary reasoning?
- How can I misread the relation?
- What short practice rep trains the distinction?

The taxonomy label should support the story; it should not be the first thing the
user has to decode.

### Graphs Are Maps, Not Arguments

The graph should help the user move around. It should not be asked to explain the
whole product by itself.

The graph default should be small:

- 3 to 10 nodes;
- one selected case or lesson;
- readable edge labels;
- a selected-node panel;
- a selected-edge panel;
- links to model and relation pages.

The graph should never present edge existence, edge confidence, or node proximity
as proof.

### Receipts Are Progressive Disclosure

Source custody, hashes, missingness, non-claims, review status, and raw artifact
links matter. They should exist, but they should not dominate the learner screen.

Default learner surface:

- show a compact "Boundary" block near the end;
- show a compact "Sources available" control;
- avoid long raw path lists;
- avoid walls of non-claim tags.

Reviewer or builder mode:

- expose source refs;
- expose missing fields;
- expose review controls;
- expose raw source snapshots when useful.

### Search, Backlinks, And Graph Are Separate Tools

Reference PKM projects consistently separate several ways of finding related
data:

- search finds a known or partially known object;
- filters narrow a typed collection;
- backlinks answer "where else does this appear?";
- graph shows neighborhood structure;
- semantic suggestions, if present later, suggest possible nearby material.

Mental Model Teacher should not ask the graph to do all of those jobs. It should
have typed search results, visible backlinks, and focused graph neighborhoods.

### Visibility Tiers Prevent Overload

The product should use four visibility tiers:

| Tier | Meaning | Examples |
|---|---|---|
| Primary | learner-facing content | situation, trap, move, model pair, practice |
| Context | useful navigation and explanation | model links, relation links, graph preview |
| Receipts | trust and custody | sources, missingness, curation status, non-claims |
| Internal | builder/debug only | raw JSON, validation logs, hashes, raw telemetry |

The current visible review surface failed because it treated too many tiers as
primary.

## Information Types

### Teaching Information

Teaching information is case-specific and narrative.

It answers:

- What happened in this kind of situation?
- What was tempting or misleading?
- What reasoning move should the user practice?
- What model relationship makes the move easier to understand?
- What should the user try once?
- What should the user not overlearn?

Teaching information belongs on Teacher lesson pages.

It should not read like telemetry, a run log, a review packet, a decision memo, or
a verdict about the correctness of an answer.

### Mental Model Information

Mental model information is durable and reusable.

It answers:

- What is this model in plain language?
- What does it help you notice?
- When should you use it?
- When should you avoid it?
- How is it commonly misused?
- What failure modes does it catch?
- What prompts or drills help you practice it?
- Which lessons used it?
- Which relations connect it to other models?

Mental model information belongs on model pages.

It should not be case-specific by default. A model page may include "appears in"
links to cases, but the page itself should teach the model as a reusable lens.

### Relation Information

Relation information is the connective teaching layer.

It answers:

- What is the plain-language story between these two models?
- Does one support, challenge, constrain, or repair the other?
- Why does this pair matter?
- What mistake happens if the user reads the relation too simply?
- What is a tiny practice rep for the pair?
- Which lessons used this relation?

Relation information belongs on relation pages and edge panels.

It should not be reduced to graph edge labels like `ally` or `antagonist`.

### Graph Information

Graph information is spatial navigation.

It answers:

- What models are near this lesson?
- Which relation is currently selected?
- Where can I click next?
- Which relation types are visible?

Graph information belongs on graph panels or map pages.

It should not be the first explanation of a lesson.

### Review And Custody Information

Review and custody information is evidence discipline.

It answers:

- What source artifacts powered this page?
- Which fields are missing?
- What has not been human-reviewed?
- What does the page explicitly not claim?
- What raw artifact does a reviewer need to inspect?

Review and custody information belongs in review mode, receipts drawers, and
builder-facing docs.

It should not be treated as learner-facing teaching copy.

## Product Modes

The product should have explicit modes. The mode switch is not cosmetic; it
changes the information hierarchy.

### Learn Mode

Default mode.

Purpose: teach one move from one case.

Primary surfaces:

- Teacher lesson page;
- inline model relationship strip;
- small graph preview;
- links to model and relation pages.

Hidden by default:

- raw Teacher card snapshots;
- review controls;
- source hash tables;
- long non-claim lists;
- package-gate language.

### Explore Models Mode

Purpose: browse durable model pages.

Primary surfaces:

- model library;
- search;
- filters;
- model pages;
- relation chips;
- lessons where the model appeared.

This mode answers "what is this mental model?" rather than "what happened in
this case?"

### Explore Relations Mode

Purpose: browse relation pages as first-class learning objects.

Primary surfaces:

- relation library;
- pair pages;
- relation-type filters;
- edge-story previews;
- practice prompts for model pairs.

This mode answers "what does this pair teach?"

### Map Mode

Purpose: navigate a focused graph neighborhood.

Primary surfaces:

- small graph;
- selected node panel;
- selected edge panel;
- search;
- relation-type filters.

The map should open with a selected relation, not an empty network.

### Review Mode

Purpose: let a reviewer judge clarity, overclaiming, and source fidelity.

Primary surfaces:

- product lesson;
- source artifact comparison;
- blank human review form;
- missingness;
- source refs;
- boundary checks.

Review mode should never be the default learner page.

### Builder/Receipts Mode

Purpose: let a builder inspect custody and generated artifacts.

Primary surfaces:

- source refs;
- hashes;
- object IDs;
- generated JSON links;
- field-level missingness;
- validation status.

Builder mode is product infrastructure, not product UX.

## Global Navigation

The first offline product prototype should use a restrained navigation model:

```text
Learn | Models | Relations | Map | Review
```

Rules:

- `Learn` is the default.
- `Models` opens the mental-model library.
- `Relations` opens the relation library.
- `Map` opens the selected lesson neighborhood, not a global graph.
- `Review` is visually distinct and marked as reviewer-only.

Within Learn mode, the user should be able to switch cases from a left rail or
compact case picker:

```text
Launch beta
Deploy routing
Founder/cofounder
```

The case picker should show short human labels, not raw case IDs as the primary
text.

## Teacher Lesson Page

### First Viewport

The first viewport must answer four questions without scrolling:

1. What situation are we learning from?
2. What mental move is being taught?
3. Which model relationship teaches it?
4. What should I do next?

Suggested layout:

```text
Top nav: Learn | Models | Relations | Map | Review

Left rail:
  Case picker
  Current lesson step

Main column:
  Situation
  "The tempting read"
  "The move"
  Model relationship strip
  Primary action: Start practice rep

Right column:
  You are learning
  Model A -> relation -> Model B
  Tiny graph preview
  Links: model pages, relation page
```

### Lesson Narrative Template

Use this sequence:

1. `Situation`: one or two plain sentences about the case anchor.
2. `The trap`: the tempting first read or pressure pattern.
3. `The move`: one sentence that names the reasoning action.
4. `Why this move helps`: two or three sentences.
5. `Model relationship`: explain the pair before naming the taxonomy.
6. `Worked example`: weak first read, better question, stronger answer.
7. `Practice rep`: one short prompt and one concrete user action.
8. `Do not overlearn`: boundary language.
9. `Explore next`: links to models, relation page, and graph.
10. `Receipts`: collapsed by default.

### Lesson Page Copy Rules

- Use sentences, not label piles.
- Use case IDs only in receipts or URLs.
- Avoid raw artifact names in the main narrative.
- Keep non-claims readable as boundaries, not a tag wall.
- Do not show raw source snapshots in Learn mode.
- Do not present human review controls in Learn mode.
- Do not claim the lesson proves an answer, advice, or decision was correct.

## Mental Model Page

### Purpose

The model page teaches one reusable mental model independent of a particular
case.

### Page Template

1. `Meaning`: one sentence.
2. `What it helps you notice`: bullets with clear observable signals.
3. `Use it when`: situations where the model is helpful.
4. `Be careful when`: situations where the model can mislead.
5. `Common misuse`: one or more common failure patterns.
6. `Practice`: short prompts.
7. `Connections`: allies, antagonists, guardrails, and tensions.
8. `Appears in lessons`: case-based Teacher lesson links.
9. `Receipts and boundaries`: collapsed by default.

### Model Page Interaction

The user should be able to:

- search within the library;
- filter by reasoning type or situation type;
- click relation chips;
- click lesson examples;
- open source receipts;
- return to the lesson they came from.

### Model Page Product Rule

A model page is not a raw canonical Markdown dump. Canonical Markdown can power
the page, but the product page should be structured for learning.

## Relation Page

### Purpose

The relation page teaches a model pair.

### Page Template

1. `Pair headline`: "When [model A] meets [model B]..."
2. `Plain-language story`: explain the relationship before the taxonomy.
3. `Relation type`: ally, antagonist, structured tension, antidote, guardrail,
   or practice companion.
4. `Why it matters`: when this pair changes the user's reasoning.
5. `Misread risk`: how the pair can be oversimplified.
6. `Practice prompt`: a short drill for the pair.
7. `Used in lessons`: Teacher lessons that rely on the relation.
8. `Open in map`: focused graph around the pair.
9. `Receipts and boundaries`: collapsed by default.

### Relation Page Interaction

The user should be able to:

- move to either model page;
- return to the lesson where the relation appeared;
- open the graph with this edge selected;
- filter other relations of the same type.

### Relation Page Product Rule

The relation page should make the graph edge understandable. The graph edge
should not be asked to carry the relation explanation by itself.

## Map Page

### Purpose

The map helps exploration after the user understands the lesson.

### Default State

The map should open around a selected lesson or relation:

- the lesson case is named in the header;
- the primary relation is selected;
- a side panel explains the selected relation;
- node and edge counts are small and readable;
- filters are available but not required.

### Map Controls

Required controls:

- search models;
- filter relation types;
- reset focus;
- open selected model page;
- open selected relation page;
- return to lesson.

### Map Product Rule

The map is not the homepage for v0. It is a secondary exploration surface.

## Review Mode

### Purpose

Review mode answers: "Is this product page clear, source-faithful, and
appropriately bounded?"

### Review Template

1. Product page preview.
2. Source artifacts used.
3. Field-level missingness.
4. Human review form.
5. Overclaiming checklist.
6. Reviewer notes.

### Review Rule

Do not mix Review mode into Learn mode. A learner should not have to inspect raw
Teacher cards, render lint, generated manifests, or blank review controls to
understand the lesson.

## Receipts Drawer

Receipts should be available from every product page, but collapsed by default.

Suggested sections:

- source summary;
- curation status;
- missing fields;
- non-claims;
- generated object link;
- reviewer status.

The receipt drawer is the compromise between product trust and product clarity:
the evidence is there, but it does not consume the lesson.

## Visual Tone

The product should feel like a learning tool, not a marketing site and not an
internal dashboard.

Visual direction:

- quiet, readable, work-focused;
- moderate density;
- strong hierarchy;
- short section headings;
- compact top navigation;
- left rail for cases or library filters;
- main content column for narration;
- right context column for model pair, graph preview, and next links.

Avoid:

- huge raw data tables on the first screen;
- tag walls of non-claims;
- raw local paths in learner copy;
- review controls beside teaching content;
- global graph as the first impression;
- decorative visual noise.

## Switching Model

The user should understand where they are by the active mode:

```text
Learn: "I am learning a move from a case."
Models: "I am studying a reusable model."
Relations: "I am studying how two models interact."
Map: "I am exploring nearby models and relations."
Review: "I am checking source fidelity and product safety."
```

Switching should preserve context when possible:

- from a lesson, opening `Models` can highlight the lesson's models;
- from a lesson, opening `Relations` can highlight the lesson's relation;
- from a relation page, opening `Map` selects that edge;
- from a model page, opening `Learn` shows lessons where the model appeared;
- from any page, opening `Review` compares the current product object to source.

## Example First-Run Flow

1. User opens Mental Model Teacher.
2. Default view is Learn mode on one case.
3. Header says: "Learn the move: Ask what evidence remains if the authority
   signal is removed."
4. The page explains the situation and the trap in plain language.
5. The relation strip shows:

   ```text
   Authority Bias -> antagonist -> First Principles Thinking
   ```

   with a one-sentence story:

   ```text
   Authority Bias names the pull of prestige; First Principles asks what remains
   when prestige stops counting as evidence.
   ```

6. User clicks "Start practice rep."
7. User answers a short prompt.
8. User clicks the relation strip to open the relation page.
9. User clicks a model to learn the durable concept.
10. User opens Map only after understanding the pair.

## What Existing Artifacts Become

| Current artifact | Future role |
|---|---|
| Three-case lesson Markdown | Source for Learn mode narrative, but should be rewritten into a clearer page sequence |
| Pilot model Markdown pages | Seed for durable model pages |
| Pilot relation Markdown pages | Seed for relation pages |
| Three-case graph JSON | Source for Map mode neighborhoods |
| Visible review surface | Should become Review mode, not learner UI |
| UX review packet | Reviewer workflow, not learner UI |
| Package gate | Build/release governance, not learner UI |
| Source refs and hashes | Receipts drawer |
| Non-claim lists | Boundary section plus receipts drawer |

## Acceptance Criteria For The Next UI Slice

A successful next slice should pass these checks:

- A first-time viewer can say what the page is teaching within 10 seconds.
- The first viewport contains a case anchor, a reasoning trap, a thinking move,
  and a model relationship.
- The learner screen does not show raw source snapshots, package gates, generated
  JSON, validation logs, or review controls.
- Model pages answer "what is this model?" without needing a case.
- Relation pages answer "what does this pair teach?" without needing the graph.
- The graph opens with a selected relation and a plain-language edge panel.
- Receipts are present but collapsed.
- Human review remains pending unless actually completed.
- No page claims product proof, answer correctness, advice correctness, runtime
  integration, or action authorization.

## Recommended Next Slice

Create a new slice before expanding the corpus:

```text
PR-P12A Learner-First Mental Model Teacher Experience Prototype
```

Scope:

- one static HTML prototype;
- Learn mode as the default;
- three case picker;
- one polished lesson narrative using existing three-case product objects;
- relation strip and graph preview;
- links to existing or placeholder model and relation pages;
- receipts drawer collapsed by default;
- Review mode separated from Learn mode.

Stop before:

- full corpus graph;
- runtime integration;
- provider/model calls;
- human validation claims;
- product proof claims.

## Open Product Questions

- Should the first prototype optimize for a beginner who has never heard of
  mental models, or for an existing Lolla user who understands the audit context?
- Should practice reps accept typed input locally, or should they be presented as
  read-only prompts until a later interactive slice?
- How much case detail is enough to anchor the lesson without turning the page
  into Decision Work?
- Should relation pages be written for every three-case edge before another
  visual prototype, or can the prototype use a small number of polished relation
  pages first?
- What vocabulary should we use for relation types if `ally`, `antagonist`, and
  `structured tension` feel too internal?

## Boundary

This design note does not implement UI, call providers or models, run Lolla,
invoke the Lolla skill, create new Lolla runs, wire runtime behavior, claim
product proof, claim human validation, claim answer correctness, claim advice
correctness, score output quality, treat graph edges as proof, treat embeddings
as validated relations, or authorize action.
