# Observatory Focused Workspace Browser Review v0

Status: browser-grounded UX review after focused workspace narration
Date: 2026-07-06
Decision gate: `proceed_to_observatory_model_page_readability_slice`

## Purpose

This review checks the live browser behavior after
[Observatory Focused Workspace Narration](observatory-focused-workspace-narration-v0.md).

The question for this slice was:

```text
Did the focused workspace make Observatory feel like a guided product path,
or does it still feel like every artifact at once?
```

The answer is mixed in a useful way:

- the root and workspace now have a much clearer first read;
- one active surface is visible at a time in the browser;
- the map relation filter now focuses the relation edge;
- archived outcome summaries no longer expose Markdown headings;
- model pages and expanded receipt/source details are still too technical for
  a learner-facing product surface.

This review is diagnostic. It does not claim product proof, human validation,
answer correctness, or advice correctness.

## Browser Scope

The browser pass used the local portable Observatory server with an existing
demo result artifact. No provider calls, new Lolla runs, runtime wiring,
archive mutation, sidecar writing, or skill invocation were used.

Routes and controls inspected:

| Area | Browser action | What was checked |
| --- | --- | --- |
| Root workspace | opened `/` | start-here panel, active surface label, visible and hidden sections |
| Learn surface | opened `/workspace?case_id=lolla-audit#learn` | one-surface behavior and teaching first read |
| Models surface | opened `/workspace?case_id=lolla-audit#models` | model card density and action labels |
| Model detail | opened `/models/authority-bias?case_id=lolla-audit` | standalone model-page first read and boundary copy |
| Relations surface | opened `/workspace?case_id=lolla-audit#relations` | story-first relation order and relation action label |
| Map surface | opened `/workspace?case_id=lolla-audit#map` | focused map surface, graph labels, search behavior |
| Map search | typed `first` | selected panel follows the visible model |
| Map relation filter | clicked `antagonist` | selected panel switches to the relation edge |
| Receipts surface | opened `/workspace?case_id=lolla-audit#receipts` | trust summary and expanded source/custody density |
| Mobile viewport | emulated iPhone 14 | main-before-sidebar order and one-column start steps |
| Browser health | checked console and errors | no browser console errors or page errors |

## What Now Works

### Root First Read

The root page now starts with:

```text
Start here
Use this run as a short lesson.
```

The visible path is:

```text
Read outcome -> Practice lesson -> Inspect models -> Check receipts
```

The browser focus mode works: on `/`, only the Outcome section is visible. Learn,
Models, Relations, Map, and Receipts are hidden until selected.

This is a meaningful reduction in overload. The page no longer immediately
presents the whole product stack as one long report.

### Surface Switching

Opening `/workspace?case_id=lolla-audit#learn` shows only Learn. Opening
`/workspace?case_id=lolla-audit#models` shows only Models. Opening
`/workspace?case_id=lolla-audit#map` shows only Map.

The active surface label updates with the selected surface. This makes the
workspace feel more like a product workspace and less like a static audit file.

### Outcome Cleanup

The archived intake-routing sample no longer exposes Markdown headings such as
`## Updated position` inside the first-read Outcome card. The outcome starts
from the actual answer text:

```text
I would still recommend a limited release, not a broad launch.
```

This fixes a concrete mismatch between raw artifact format and product copy.

### Relations

Relations remain the strongest current product signal.

The visible order is still right:

```text
Plain Language Story
Why It Matters
Misread Risk
Practice prompt
Model links
Taxonomy, confidence, and custody
```

The relation page teaches the edge before showing taxonomy. That pattern should
continue to guide Learn, Map, and future model-neighborhood design.

### Map

The Map now behaves more like navigation:

- searching `first` selects First Principles Thinking;
- clicking `antagonist` selects the relation edge;
- the selected panel shows Relation and links to the relation page;
- visible browser labels expose human labels such as `Open model: Authority
  Bias` and `Open relation: Authority Bias and First Principles Thinking
  (antagonist)`.

This makes the map useful as a small neighborhood navigator instead of a raw
graph artifact.

### Mobile Layout

On an iPhone 14 viewport:

- the main workspace content appears before the selected-run sidebar;
- the start path collapses to one column;
- only Outcome is visible by default.

This is the right structural direction for mobile, though a visual pass is
still needed before adding more dense controls.

## What Still Feels Heavy

### Recent Runs Compete With The Lesson

The sidebar still lists many recent runs on the first screen. This is useful
for archive switching, but it competes with the learner's first task.

The next UX move should make run switching less dominant until the user wants
it. A `Switch run` disclosure or compact picker would fit the current portable
server-rendered direction.

### Advanced Audit Is Still Too Near The Primary Tabs

Advanced Audit is visually marked as advanced, but it still sits beside Outcome,
Learn, Models, Relations, Map, and Receipts.

The route is correct. The placement is still a risk. Advanced Audit should feel
like a secondary inspection path, not the seventh ordinary product tab.

### Model Pages Still Lead With System Boundary Copy

The standalone model page for Authority Bias begins with:

```text
A selected-run mental model page. It formats the product-safe model object...
```

That boundary is true, but it should not be the first product read. A learner
should first see what the model helps them notice, when to use it, when it can
mislead, and a simple practice move. Source/custody boundaries should be
available after that.

### Model Cards Are Still Dense

The Models surface is focused now, but each model card still contains a lot of
bullets at once. It is better than raw JSON or raw Markdown, but it is not yet
an elegant learning card.

The next implementation should give model pages a stronger first-read hierarchy:

```text
model name
one-sentence meaning
helps notice
use when
avoid when
practice this
source/status boundary
```

### Receipts Expansion Is Still An Artifact Wall

Receipts works as a first-read trust summary. Once expanded, source refs still
read like an artifact list:

```text
teacher_lesson_source
teacher_card_source
canonical_model_markdown
activation_curation
intervention_semantics
```

This is useful for maintainers, but too dense for product review. It needs a
two-level receipt shape:

```text
user trust summary
  -> reviewable source families
  -> raw artifact refs only for advanced inspection
```

### SVG Text Extraction Still Sees Type Suffixes

Interactive browser snapshots now show cleaner map controls, but lower-level
text extraction can still see text such as `Authority Biasmental_model`.

The current `aria-label` improvement is helpful. A later cleanup should separate
visible SVG labels from technical type metadata more completely.

## Product Assessment

The focused workspace slice is a real improvement. The product now has an
understandable first path:

```text
start with the selected run
read the outcome
practice the lesson
inspect models and relations
use the map to navigate
check receipts when trust matters
open Advanced Audit only for technical inspection
```

The remaining overload is concentrated in three places:

- sidebar archive switching;
- standalone model-page framing;
- expanded receipts/source refs.

That is useful because the problem is now localized. Earlier, everything was
overwhelming at once.

## Recommended Next Slice

Next PR:
`Add Observatory model page readability slice`

Decision gate:
`proceed_to_observatory_model_page_readability_slice`

Scope:

1. Keep the portable Python/server-rendered Observatory owner.
2. Keep the route family and selected-run scope.
3. Make standalone model pages lead with learning value, not boundary copy.
4. Add a compact model-page first-read block:
   - what this model helps you see;
   - when to use it;
   - when it misleads;
   - practice this.
5. Move selected-run boundary and source/custody language below the learning
   first read.
6. Consider collapsing Recent Runs into a `Switch run` disclosure if the change
   stays small and clearly reduces first-screen competition.
7. Preserve Receipts and Advanced Audit as inspection paths, not proof systems.

Stop before:

- full corpus mental model library browsing;
- full corpus graph;
- runtime integration;
- default-on Conversation Understanding generation;
- provider/model API calls;
- product readiness claims;
- human validation claims;
- answer/advice correctness claims;
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
