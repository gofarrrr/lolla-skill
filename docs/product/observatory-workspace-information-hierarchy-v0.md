# Observatory Workspace Information Hierarchy v0

Status: implemented hierarchy slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_legacy_teacher_renderer_cleanup`

## Purpose

This slice audits the visible Observatory workspace after the Teacher, model,
relation, map, and receipts surfaces were merged into one portable
server-rendered product path.

The problem found in browser review was not missing data. It was too much data
competing for the same level of attention. Observatory now has enough substrate
to show Outcome, Learn, Models, Relations, Map, Receipts, and Advanced Audit,
but not all of those surfaces belong in the same first-read navigation.

The design goal for this slice is:

```text
Start with the selected run.
Explain what changed.
Teach the reasoning move.
Let the user inspect models and relations.
Use the map for wayfinding.
Use receipts for trust and missingness.
Keep technical audit behind explicit inspection.
```

This slice does not run Lolla, does not invoke the Lolla skill, does not call
providers or model APIs, does not create new Lolla runs, does not wire runtime
behavior, and does not edit `observatory/build`.

## User Flow

The primary Observatory flow is now six surfaces:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

### Outcome

Question answered:

```text
What happened in this selected run?
```

This is the starting point because the user first needs to understand the run
they are looking at. It should show the revised answer, key run summary, and
only enough support detail to orient the user.

### Learn

Question answered:

```text
What reasoning move can I practice from this run?
```

Teacher content belongs here. The case is the anchor, the reasoning move is the
subject, the model relationship is the lesson, and the practice rep is the
product value.

### Models

Question answered:

```text
Which mental models are relevant here, and what does each help me notice?
```

This surface should not be a dump of canonical Markdown, activation routing, or
intervention metadata. Those sources can power the page, but the visible model
card should read as a mental model explanation:

- meaning;
- helps notice;
- use when;
- avoid when;
- practice prompt;
- source and missingness after the first read.

### Relations

Question answered:

```text
How do the selected mental models interact?
```

Relations are the strongest current product signal because they show why the
Teacher lesson is not just a list of models. The visible order should stay:

```text
plain-language story -> why it matters -> misread risk -> practice prompt -> taxonomy/custody
```

Taxonomy and confidence are useful after the relation story. They are not proof
or certification.

### Map

Question answered:

```text
Where am I in this small learning neighborhood?
```

The map is wayfinding, not proof. It should help the user move between models
and relation pages without implying that graph position or edge confidence is
validated truth.

This slice adds a reset control and a visible filter note because search and
relation filters can combine into a narrowed or empty-looking graph. The user
should be told what happened and how to recover.

### Receipts

Question answered:

```text
What exists, what is missing, and what can I inspect if I need evidence?
```

Receipts are the trust layer. They should start with simple status chips and
visible non-claims. Source refs, missingness, and raw audit routes are available
after that.

### Advanced Audit

Question answered:

```text
What happened inside the system?
```

Advanced Audit remains available for reviewers and maintainers, but it is no
longer a primary workspace tab. It is an inspection path linked from Receipts,
not a normal learner surface.

## Information Tiers

| Tier | Examples | Where it appears | Rule |
| --- | --- | --- | --- |
| First-class product data | Outcome summary, thinking move, model meaning, relation story, practice rep | Outcome, Learn, Models, Relations, Map selection panel | Show in plain language before support details. |
| Second-class support data | Missingness, source families, curation status, non-claims | Receipts and collapsed disclosure blocks | Keep available, but do not lead with it. |
| Technical inspection data | Extraction audit, usage telemetry, artifact status rows, raw audit index | Receipts technical links and Advanced Audit | Do not present as product copy or user proof. |
| Internal-only data | Provider mechanics, raw telemetry internals, embeddings, eval machinery | Advanced Audit or not surfaced | Never treat as learner-facing explanation. |

## Implemented Changes

### Product Navigation

The workspace status bar now lists only the six product surfaces:

```text
Outcome
Learn
Models
Relations
Map
Receipts
```

Advanced Audit is still reachable from Receipts, but it no longer appears as a
peer of Learn or Models.

### Receipts Hierarchy

Receipts now starts with a plain-language explanation:

```text
Use Receipts to understand what exists for this run before opening technical evidence.
```

The first-read order is:

```text
trust summary -> status chips -> visible non-claims -> technical inspection links
```

The collapsed support labels are now user-readable:

- Source and missingness details.
- Technical audit index.
- Workspace boundary notes.

### Map Filter Recovery

The Map now includes:

- a Reset control;
- a filter note explaining that search and relation filters combine;
- a dynamic empty-state explanation when filters hide all visible relations.

This protects the user from interpreting a narrowed graph as missing data or a
broken UI.

## Browser Check

The local browser pass used a packet-backed offline fixture for
`launch-public-enterprise-beta`. It did not create a Lolla run and did not call
providers or model APIs.

Checked in the browser:

- root workspace primary navigation;
- Map search, relation filter, and Reset;
- Receipts first-read copy and technical inspection links.

Observed browser state:

```text
primary nav = Outcome, Learn, Models, Relations, Map, Receipts
receipts links = Extraction audit, Usage, Advanced audit
map default = 3 models, 1 relation
map filtered empty-relation explanation = visible
map reset = returns to 3 models, 1 relation
```

The browser check also confirmed a remaining presentation risk: raw text
extraction can still see hidden workspace sections and embedded scripts even
though the interactive visible snapshot is clean. That is not a blocker for this
slice, but a future accessibility/text-extraction pass should reduce hidden
technical noise.

## What The User Should Understand

At the most general level, the user should be able to say:

```text
This is the run.
This is what changed.
This is the reasoning lesson.
These are the models.
This is how the models relate.
This map helps me move around.
These receipts tell me what exists and what is missing.
```

The user should not have to understand raw JSON, canonical source custody,
artifact identifiers, provider telemetry, or evaluation machinery to get value
from the first read.

## Strongest Useful Signal

The strongest useful signal is that Observatory now has a clearer information
ladder. It can keep technical custody without forcing every user through the
technical layer.

## Strongest Unresolved Risk

The legacy Teacher renderer still exists as a code-level fixture even though
the public route redirects into the selected-run workspace. The next cleanup
should decide whether to keep it only as a test fixture, replace its tests with
workspace tests, or remove the legacy renderer after coverage is migrated.

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

## Decision Gate

Proceed to:

```text
proceed_to_observatory_legacy_teacher_renderer_cleanup
```

Stop before:

- full-corpus graph;
- runtime integration;
- provider or model API calls;
- default-on generation;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.
