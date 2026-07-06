# Observatory Model Page Readability And Visible Surface Audit v0

## Purpose

This slice audits what the portable Observatory currently shows to a user and
turns the most obvious confusion into a small UI correction.

The product problem was not "missing data." The product problem was that the
same page family mixed learning material, run telemetry, custody language, and
review language before the user had a simple reason to care.

This slice keeps the source owner unchanged: the portable Python/server-rendered
Observatory remains the implementation path for now. It does not move work into
the legacy app source, does not edit the compiled SPA bundle, and does not wire
runtime behavior.

## User Progression We Want

The user should be able to move through one selected run in this order:

1. Outcome: what changed or survived in the answer.
2. Learn: the reasoning move worth practicing.
3. Models: the canonical mental models used in the lesson.
4. Relations: why two models belong together in this lesson.
5. Map: a small wayfinding graph for jumping between models and relations.
6. Receipts: what exists, what is missing, and what is not claimed.
7. Advanced Audit: technical telemetry only when the user chooses to inspect it.

This makes the information hierarchy explicit:

- case is the anchor;
- reasoning move is the subject;
- model relationship is the lesson;
- practice rep is the product value.

## Browser Audit

The audit opened the portable Observatory locally against an existing demo
result. It used browser navigation and did not create or mutate a run.

| Surface | Route or control | What it presented | Product judgment |
| --- | --- | --- | --- |
| Root workspace | `/` | Selected run, start-here card, quick actions, Outcome card, run context, surface homes | Good primary path. Before this slice, Recent Runs competed with the lesson. This slice collapses run switching behind `Switch run`. |
| Learn | `/workspace?case_id=lolla-audit#learn` | Lesson title `Test The Authority, Not The Aura`, practice action, relation story summary | Good. The title is a Teacher lesson move, not a canonical mental model. The UI needs to keep that distinction visible. |
| Models | `/workspace?case_id=lolla-audit#models` | Authority Bias, Information Asymmetry, First Principles Thinking | Useful but dense. This slice makes cards start with a compact first read and moves full model details into progressive sections. |
| Model detail | `/models/authority-bias?case_id=lolla-audit` | Full selected-run model page for Authority Bias | Before this slice it led with implementation copy: "A selected-run mental model page..." This slice makes it lead with learning value. |
| Relations | `/workspace?case_id=lolla-audit#relations` | Authority Bias and First Principles Thinking relation story | Good. Relation story appears before taxonomy and confidence. |
| Relation detail | `/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit` | Relation story, why it matters, misread risk, practice prompt, links to model pages | Mostly good. This slice softens the lede so it reads like a lesson, not an artifact description. |
| Map | `/workspace?case_id=lolla-audit#map` | Search, relation-type filter, small graph, selected-node or selected-edge panel | Good as wayfinding. Search plus relation filter can intersect to zero visible relations; later UX should explain active filters. |
| Receipts | `/workspace?case_id=lolla-audit#receipts` | Teacher packet status, Conversation Understanding status, process brief status, visible non-claims, inspection links | Good if kept secondary. Expanded source refs and advanced inspection remain too dense for the primary product story. |
| Advanced Audit | `/audit` and `/audit/extraction` | Telemetry index, extraction tables, capture status, quote validation, lanes, events | Correctly technical. It should stay behind inspection links and should not become Learn or model-page copy. |
| Legacy Teacher Learn | `/teacher-learning` | Separate full Teacher page with lesson, model stack, models, relation, map, receipts, non-claims | Strong unresolved risk. It now duplicates the workspace product flow in a different hierarchy. It should be consolidated in a follow-up PR rather than left as a second Teacher UX. |

## Data Hierarchy

### First-Class User Data

First-class data is what the user should see without opening technical details:

- selected-run outcome summary;
- lesson thinking move;
- practice action;
- canonical model names;
- one-sentence model meaning;
- when to use a model;
- when a model misleads;
- relation story;
- why the relation matters;
- misread risk;
- visible non-claims.

### Second-Class User Data

Second-class data can be useful, but should be expandable or below the first
read:

- full `helps_notice`, `use_when`, and `avoid_when` lists;
- common misuse;
- failure modes;
- extra practice prompts;
- source refs;
- missingness;
- curation status;
- run switching;
- advanced inspection links.

### Internal-Only Data

Internal data should not dominate user pages:

- raw JSON objects;
- raw canonical Markdown as UI;
- raw local file paths;
- route traces;
- activation-routing internals;
- confidence as proof;
- graph or embedding similarity as validation;
- Product Delta or eval internals as product copy.

## Implemented UI Changes

### Model Detail Starts With Learning Value

The standalone model page now opens with:

> Learn what this model helps you notice, when to use it, where it can mislead,
> and one practice rep for this selected run.

That replaces the old implementation-first lede. Source custody and non-claims
remain present, but they now appear after the learning read.

### Compact Model First Read

Each model now starts with a first-read block:

- What This Model Helps You See;
- Use when;
- When it misleads;
- Practice this.

The model card still preserves the full product-safe object. Full details are
progressive so the Models surface does not read like a raw data dump.

### Run Switching Is Secondary

The sidebar now keeps the selected run visible but collapses archive switching
behind `Switch run`. This preserves function while reducing first-screen
competition.

### Relation Pages Remain Story First

Relation detail pages keep the plain-language story before taxonomy. The lede
now describes the relation as a lesson, not just a selected-run artifact.

## What Still Needs Product Work

### Single Teacher Route

`/teacher-learning` remains a separate full Teacher page. It is historically
useful and still covered by tests, but it creates two user experiences:

- `/workspace?case_id=<id>#learn` as the new selected-run Observatory flow;
- `/teacher-learning` as the older all-in-one Teacher page.

The next serious PR should decide whether `/teacher-learning` becomes a
compatibility redirect, a thin wrapper around the workspace Learn surface, or a
documented legacy route hidden from primary navigation.

### Model Library Beyond The Selected Run

The current model pages are selected-run pages, not a global always-online
model library. A later slice can add global model pages, but it should not
expose raw canonical Markdown as product UI and should not claim relation proof.

### Map Filter Clarity

The Map works as wayfinding, but active search plus active relation filters can
make the graph look empty. Later UX should explain active filters and provide a
clear reset action.

## Boundary Confirmation

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new Lolla runs;
- does not wire runtime behavior;
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

## Decision Gate

Recommended gate:

`proceed_to_observatory_teacher_route_consolidation_slice`

Recommended next PR:

Add a compatibility-safe route consolidation plan or implementation so the
workspace remains the primary Observatory product experience and `/teacher-learning`
does not continue as a competing Teacher UI.
