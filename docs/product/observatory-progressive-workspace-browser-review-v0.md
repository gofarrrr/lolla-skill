# Observatory Progressive Workspace Browser Review v0

Status: browser-grounded UX audit after progressive workspace slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_focused_workspace_narration_slice`

## Purpose

This review records what the portable Observatory workspace now shows after
[Observatory Progressive Workspace UX Slice](observatory-progressive-workspace-ux-slice-v0.md),
what still feels unclear, and what the next product slice should change.

The review is grounded in a local browser pass over the server-rendered
Observatory. It does not add a new surface and does not evaluate answer
correctness. The goal is to keep one Observatory experience while making the
teaching, mental-model, relation, map, receipts, and telemetry layers easier to
understand.

The desired user progression remains:

```text
selected run
  -> what changed in the answer
  -> what reasoning move can I practice
  -> which models explain the move
  -> which relation teaches the pair
  -> what small map helps me navigate it
  -> what can I trust or inspect
  -> advanced telemetry only when needed
```

## Browser Scope

The browser pass inspected the local portable Observatory server with an
existing demo result artifact. No provider calls, new Lolla runs, runtime
wiring, archive mutation, sidecar writing, or skill invocation were used.

Routes and controls clicked or opened:

| Area | Browser action | What was inspected |
| --- | --- | --- |
| Root workspace | opened `/` | top navigation, selected-run sidebar, hero, first-read cards, disclosure summaries |
| Learn tab | opened `/workspace?case_id=lolla-audit#learn` | active tab state, first-read teaching card, practice prompt, lesson expansion |
| Models tab | opened `/workspace?case_id=lolla-audit#models` | model cards, standalone model links, support disclosures |
| Model detail | opened `/models/authority-bias?case_id=lolla-audit` | selected-run model page shape and navigation back to workspace |
| Relations tab | opened `/workspace?case_id=lolla-audit#relations` | story-first relation card, model links, taxonomy/custody expansion |
| Relation detail | opened `/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit` | standalone relation page order |
| Map tab | opened `/workspace?case_id=lolla-audit#map` | search, relation filter, graph links, selected panel, detail link |
| Map search | typed `first` | selection reconciliation after filtering |
| Map relation filter | clicked `antagonist` | relation-type filtering and selected-panel behavior |
| Map no-results | typed `zzzz` | empty-state copy and disabled detail link |
| Receipts tab | opened `/workspace?case_id=lolla-audit#receipts` | trust summary, non-claims, advanced links, source details |
| Advanced Audit | opened `/audit` | advanced telemetry vocabulary and route family |
| Extraction | opened `/audit/extraction` | capture/extraction telemetry and source wording |
| Usage | opened `/usage` | vendor/model/prompt/cost telemetry |
| Archive sample | opened one archived run workspace | whether the flow generalizes to archived result content |

## What We Are Showing Now

### Workspace Shell

The workspace now shows:

| Data shown | Current product role | Current risk |
| --- | --- | --- |
| Outcome, Learn, Models, Relations, Map, Receipts navigation | normal product route family | good backbone, but all sections still exist on one long page |
| Advanced Audit link | advanced inspection path | still appears in the same nav row as product surfaces |
| Selected run sidebar | run context and archive switching | useful, but visually competes with the first task |
| Recent runs | switchable archive samples | powerful, but too early for a user who has not understood the current run |
| Hero copy and action chips | orientation and next steps | useful, but still mentions product architecture such as primary surfaces and rendering mode |
| Workspace status disclosure | custody and rendering status | correctly expandable, not first-read |

The shell is now coherent enough to see a single system. The next issue is not
missing routes. The next issue is focus: the first screen still renders the
whole workspace underneath the hero, so a user can quickly fall into too many
sections before knowing what job each section does.

### Outcome

The Outcome surface now starts with a first-read card:

```text
What happened in this run?
```

It shows the revised answer summary first, then offers actions to practice the
lesson or open model cards. Support data such as pressure, model chips, and
missingness lives behind `Outcome support details`.

What works:

- The surface answers the first user question: what changed in this run?
- The first action points toward Learn instead of telemetry.
- Support data no longer dominates the first read.

What still fails:

- Archived runs can leak raw Markdown headings into the first-read card. In the
  sampled archive, the user sees repeated text such as `## Updated position`.
- The product does not yet explain why this outcome matters before inviting the
  user into the lesson.

### Learn

The Learn surface now starts with:

```text
What reasoning move can I practice?
```

The reviewed demo shows the move `Test The Authority, Not The Aura`, a short
practice instruction, the relation story, and links to relation and map views.
The step-by-step packet content is behind `Lesson steps and boundaries`.

What works:

- The Teacher product value is finally visible: practice one reasoning move.
- The case, move, model relationship, and practice rep are in the right order.
- Learn links outward to Relations and Map instead of duplicating all details.

What still fails:

- Expanded lesson details can show `Not available in this learning packet` as if
  it were part of the lesson. That is useful missingness, but it is not teaching.
- The first-read copy is still more like a generated packet than a guided lesson.
- The page should tell the user, in one sentence, what they are supposed to do
  next.

### Models

The Models surface now shows each selected-run mental model as a product-safe
card. The visible first-read label is:

```text
What This Model Helps You See
```

Each card includes a one-sentence meaning, helps-notice bullets, use-when
bullets, avoid-when bullets, an `Open standalone page` link, and expandable
practice/source sections.

What works:

- The user can click a mental model and get a durable model page.
- The card is not raw canonical Markdown.
- The page no longer overpromises with `Everything We Know`.

What still fails:

- Three model cards in one tab are still dense.
- `Open standalone page` is vague. The action should say `Open model page`.
- The standalone model page starts by explaining that it is a selected-run page
  before it explains why the model is useful.
- Extracted text still compresses list labels and list content, which points to
  a spacing/accessibility issue even if the visual layout is readable.

### Relations

The Relations surface is the strongest current product signal.

It starts with:

```text
Plain Language Story
```

Then it shows why the model pair matters, the misread risk, a practice prompt,
model links, and finally taxonomy, confidence, custody, missingness, and
non-claims.

What works:

- The relation page teaches the edge before naming the edge.
- The user can understand the model pair without reading internal taxonomy.
- The relation links back to both model pages.

What still fails:

- Expanded taxonomy and custody still expose machine phrasing and artifact
  labels.
- Confidence remains easy to misread unless the non-claim stays close to it.
- The relation page pattern should be reused more strongly inside Learn and Map.

### Map

The Map surface now shows a small selected-run neighborhood with search,
relation-type filters, SVG node/edge links, a selected-item panel, and detail
links to model or relation pages.

What works:

- Searching `first` selects `First Principles Thinking`.
- Searching `zzzz` shows `No visible map item`, explains that no model or
  relation matches, and disables the detail link.
- Graph edges remain navigation aids, not proof claims.

What still fails:

- SVG/link text can concatenate model names and object types, such as
  `First Principles Thinkingmental_model`.
- Clicking a relation-type filter keeps the selected model if the model remains
  visible. Mechanically this is valid, but narratively a relation filter should
  probably focus the relation edge.
- The map still needs a short "why this map matters" line before controls.

### Receipts

Receipts now starts with a trust summary:

```text
What can I trust or inspect?
Teacher packet: available
Conversation Understanding: available
Process brief: not_requested
Visible non-claims: not product proof, not human validation, not answer correctness, no runtime action authorized
```

What works:

- The first layer tells the user what exists and what is not claimed.
- Advanced links are available from Receipts.
- Source refs and missing fields are behind an expansion.

What still fails:

- Expanded source refs are still a wall of artifact names.
- Status chips can visually read as compressed text in extraction.
- The page should distinguish "for you to trust the product boundary" from
  "for a maintainer to inspect artifacts."

### Advanced Audit, Extraction, And Usage

Advanced Audit shows maintainer/reviewer telemetry:

- extraction;
- memo;
- Lane 1, Lane 2, Lane 4;
- anti-echo;
- routing;
- treatment audit;
- expansions;
- stakeholders;
- V60;
- graph survival;
- reasoning trace;
- run events;
- usage.

Extraction shows decision structure, capture manifest, quote validation, live
constraints, reasoning passages, and dropped threads.

Usage shows vendor, model, token, cost, prompt hash, and empty telemetry states.

This is valuable, but it is not product teaching UI. It should remain a
drill-down path from Receipts and advanced navigation. It should not be the
normal next step for a learner.

## First-Class, Expandable, And Advanced Data

| Layer | First-class user data | Expandable support data | Advanced-only data |
| --- | --- | --- | --- |
| Workspace shell | selected run, next action | run status, archive switching | rendering mode |
| Outcome | what changed in the answer | pressure, model chips, missingness | raw result artifact |
| Learn | reasoning move, relation story, practice rep | packet steps, do-not-overlearn, missingness | packet construction detail |
| Models | model name, meaning, helps notice, use/avoid | misuse, failure modes, source refs, curation status | raw Markdown and curation JSON |
| Relations | story, why it matters, misread risk, practice | taxonomy, confidence, source refs | unsupported relation speculation |
| Map | small neighborhood, search, selected preview | graph source status and non-claims | embeddings, full corpus graph, graph survival |
| Receipts | trust summary and explicit non-claims | source refs and missing fields | local artifact inspection |
| Advanced Audit | none for normal first-read | selected maintainer panels | lane internals, provider usage, prompt hashes |

## Product Assessment

The current work has moved from "everything at once" to "one coherent route
family with first-read cards." That is real progress.

The remaining problem is not that we lack data. The problem is that the page
still lacks a focused narration mode. The user should not have to scroll through
Outcome, Learn, Models, Relations, Map, Receipts, archive switching, and
advanced links all in one default view.

The strongest useful signal is the relation page pattern:

```text
plain-language story
  -> why it matters
  -> misread risk
  -> practice prompt
  -> model links
  -> taxonomy and custody
```

That is the clearest expression of the product thesis:

```text
case is the anchor
reasoning move is the subject
model relationship is the lesson
practice rep is the product value
```

The strongest unresolved UX risk is that Observatory still behaves like a full
artifact browser with product cards layered on top. A learner needs a focused
path through the selected run, not a visible inventory of every possible layer.

## Recommended Next Slice

Next PR:
`Add Observatory focused workspace narration`

Decision gate:
`proceed_to_observatory_focused_workspace_narration_slice`

Scope:

1. Keep the portable Python/server-rendered Observatory owner.
2. Keep the existing route family.
3. Add a focused "Start here" workspace mode that shows the selected run, one
   short explanation, and the next best action before the full section stack.
4. Make workspace navigation feel like switching surfaces, not like exposing one
   long internal report.
5. Rename user actions:
   - `Open standalone page` -> `Open model page` or `Open relation page`;
   - `Advanced Audit` should remain visibly advanced, preferably more strongly
     separated from the product tabs.
6. Clean first-read outcome excerpts so Markdown headings do not leak into the
   learner-facing summary.
7. Fix SVG/accessibility labels so model names and object types do not
   concatenate.
8. When a relation filter is selected, prefer selecting the first visible edge
   over keeping a visible model selected.
9. Add a one-sentence "why this map matters" note before map controls.
10. Keep Receipts as the trust layer and Advanced Audit as the maintainer layer.

Stop before:

- full corpus mental model library browsing;
- full corpus graph;
- runtime integration;
- default-on Conversation Understanding generation;
- provider/model API calls;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.

## Boundary Confirmation

This review:

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
