# Observatory Workspace Product Flow Audit v0

Status: browser-grounded product-flow audit and progressive disclosure plan
Date: 2026-07-06
Decision gate: `proceed_to_observatory_progressive_workspace_ux_slice`

## Purpose

This audit records what the portable Observatory workspace currently shows,
what the product should show, how the information should be layered, and what
the next implementation slice should change.

The goal is not to add another surface. The goal is to make the existing
selected-run Observatory workspace easier to understand:

```text
start from the run
  -> explain what changed
  -> teach one reasoning move
  -> let the user inspect models and relations
  -> let the user explore a small map
  -> keep custody and telemetry behind receipts and advanced audit
```

The user should not have to understand JSON, curation artifacts, route traces,
provider usage, prompt hashes, or review files before the page is useful.

## Browser Audit Scope

The audit used the local portable Observatory server and clicked through the
current server-rendered route family.

Routes and controls inspected:

| Area | Clicked or opened | What was recorded |
| --- | --- | --- |
| Root workspace | `/` | top nav, selected-run sidebar, first-screen text, available links |
| Workspace tabs | Outcome, Learn, Models, Relations, Map, Receipts | active tab behavior, visible section text, section actions |
| Model pages | selected-run model detail pages | page headings, durable model content, links back to workspace |
| Relation page | selected-run relation detail page | story-first order, model links, taxonomy, confidence, custody |
| Map controls | search, relation filter, node selection, edge selection | graph result counts, selected panel behavior, detail links |
| Receipts | receipts section and advanced links | custody status, missingness, non-claims, advanced entry points |
| Advanced Audit | audit index, extraction, usage | telemetry vocabulary, empty states, raw inspection concepts |
| Archive sample | one archived run from the run picker | whether the same product flow generalizes beyond the current run |

No provider calls, new Lolla runs, runtime wiring, archive mutation, or skill
invocation were used for this audit.

## Current Surface Inventory

### Workspace Shell

The shell currently shows:

| Item | Current presentation | Product role |
| --- | --- | --- |
| Top navigation | Outcome, Learn, Models, Relations, Map, Receipts, Advanced Audit, status | primary route family plus advanced inspection |
| Sidebar selected run | selected case id | run context |
| Sidebar recent runs | current run and archived run titles | run switching |
| Sidebar surface homes | short definitions for Outcome, Learn, Models, Relations, Receipts | navigation helper |
| Hero | selected run, run id, health, rendering mode, primary surfaces, advanced surface | workspace orientation |

What works:

- The selected run stays visible while the user moves between surfaces.
- Root and workspace now belong to the same portable server-rendered family.
- The surface list reflects the one-system rule.

What is risky:

- The first screen is still product architecture copy, not user narration.
- The sidebar competes with the content before the user knows what to do.
- `Advanced Audit` appears as a peer of `Outcome` and `Learn`, although it is
  a different layer.
- The hero shows implementation words such as rendering mode and surface list.
  Those are useful receipts, not first-read product value.

### Outcome

Outcome currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Revised answer | compact headline plus body excerpt | first-class answer outcome |
| Strongest pressure | one pressure summary when available | bridge from answer to learning |
| Model chips | selected-run models | optional path into model pages |
| Missingness | compact status line | support data |
| Boundary copy | "Outcome owns run result summary; Learn owns the reasoning lesson" | useful but should be quieter |

What works:

- Outcome answers the first user question: what changed in this run?
- Model chips give a path into the mental model layer.

What is risky:

- Archive samples can show Markdown-like text such as repeated headings.
- The first action is not obvious. The user does not get a simple "read this,
  then practice this" progression.
- The strongest pressure is sometimes missing, and the empty state is visible
  too early.

### Learn

Learn currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Case anchor | visible step | first-class teaching context |
| Reasoning trap | visible step, sometimes missing | first-class when present, quiet empty state when absent |
| Thinking move | visible step | first-class lesson subject |
| Model relationship | visible step | first-class relation lesson |
| Worked example | visible step, sometimes missing | first-class when present |
| Practice rep | visible block with user action and boundary | primary product value |
| Do-not-overlearn | visible list | safety boundary |
| Model and relation links | chips | expansion paths |

What works:

- The Learn surface is the correct place for Teacher.
- The sequence matches the product thesis: case anchor, thinking move, model
  relationship, practice rep.
- It links out to models and relations instead of duplicating everything.

What is risky:

- Missing fields are shown in the same narrative position as completed fields.
  A learner sees "Not supplied" before understanding the lesson.
- The step labels are system-neutral, but the copy still reads like a generated
  packet rather than a teacher guiding the user.
- There is no compact first-read lesson card. The user must parse multiple
  blocks before knowing what the lesson is.

### Models

Models currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Model display name | visible card title and standalone route title | first-class object identity |
| One-sentence meaning | visible under "Everything We Know" | first-read definition |
| Helps notice | visible bullets | core model explanation |
| Use when | visible bullets | core model explanation |
| Avoid when | visible bullets | core model explanation |
| Common misuse | visible, sometimes missing | expandable detail |
| Failure modes | visible, sometimes missing | expandable detail |
| Practice prompts | visible | learning utility |
| Curation/source/missingness/non-claims | visible lower page | receipts layer |

What works:

- Clicking a mental model opens a durable selected-run model page.
- The model page is not a raw Markdown dump.
- The data shape is close to a useful mental model card.

What is risky:

- The phrase "Everything We Know" overpromises and creates the expectation of a
  complete canonical library entry.
- The first-read definition should be stronger than the custody/scaffolding.
- Missing-source bullets are useful for review, but they should not dominate
  the learner's first encounter with the model.
- The model page is selected-run scoped. It should make that clear without
  implying a full public corpus page.

### Relations

Relations currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Relation title | source model and target model | first-class object identity |
| Plain-language story | first major section | primary relation lesson |
| Why it matters | visible section | relation value |
| Misread risk | visible section | boundary |
| Practice prompt | visible section | user action |
| Model links | visible links to both models | expansion |
| Taxonomy and confidence | visible lower section | support data |
| Custody/missingness/non-claims | visible lower section | receipts layer |

What works:

- Story comes before taxonomy.
- The relation page clearly teaches a model pair rather than only naming an
  edge.
- It links to both model pages.

What is risky:

- Confidence and "reviewed" language are easy to misread as certification.
- Relation IDs and relation labels can leak machine naming, especially in chip
  labels.
- The relation page should answer "what does this pair teach?" before showing
  any audit vocabulary.

### Map

Map currently shows:

| Data or control | Current presentation | Desired role |
| --- | --- | --- |
| Graph scope | selected-run neighborhood | first-class navigation context |
| Nodes | model names in SVG and list | map targets |
| Edges | relation type and link | relation targets |
| Search | filters visible nodes | finding mechanism |
| Relation filters | filter by relation type | narrowing mechanism |
| Selection panel | selected node or edge summary | local preview before opening detail |
| Detail link | opens model or relation route | expansion |
| Source and non-claims | visible below map | receipts layer |

What works:

- The Map is now interactive, not a static list.
- Search, filters, selected panel, and durable detail links work.
- The page states that edges are navigation, not proof.

What is risky:

- After searching, a hidden prior selection can remain in the selection panel.
  Example: searching for `first` leaves only First Principles Thinking visible,
  while the selection panel can still describe Authority Bias.
- Some SVG/link accessible labels join words such as `Authority Biasmental_model`.
- The map is visually interesting but still needs a clearer "why this map
  matters" narration.
- Source custody and non-claim chips are too visible for first-read map use.

### Receipts

Receipts currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Teacher packet status | available | trust summary |
| Conversation Understanding status | available | process status |
| Process brief status | not requested | process status |
| Non-claims | visible list | boundary |
| Advanced links | extraction, usage, audit | drill-down |
| Source custody | relative artifact refs | inspection detail |
| Missingness | detailed status | inspection detail |

What works:

- Receipts is the correct home for custody, missingness, sidecar status, and
  non-claims.
- It prevents the product from implying proof, validation, or action
  authorization.

What is risky:

- It currently exposes too much technical detail at once.
- Source refs are useful but visually noisy.
- Receipts should first answer "what can I trust or inspect?" and only then
  reveal artifact-level details.

### Advanced Audit

Advanced Audit currently shows:

| Data | Current presentation | Desired role |
| --- | --- | --- |
| Audit index | many telemetry panels | maintainer/reviewer navigation |
| Extraction | decision structure, capture manifest, quote validation, constraints | technical receipt |
| Usage | vendor/model/token/cost tables, prompt hashes | operational telemetry |
| Lane panels | route traces and model selection internals | maintainer inspection |

What works:

- Advanced Audit remains available for technical inspection.
- Empty states are explicit when older artifacts do not have full telemetry.

What is risky:

- The vocabulary is not user-facing: lane, route trace, prompt hash, provider,
  capture manifest, quote validation, V60, graph survival.
- It should not sit visually as equal to the teaching/product surfaces.
- It must remain a drill-down path from Receipts or an advanced link.

## First-Class, Second-Class, And Internal Data

| Tier | Should be first-read | Should be expandable | Should stay advanced-only |
| --- | --- | --- | --- |
| Outcome | revised answer, strongest pressure, run identity | model chips, missingness | raw result JSON |
| Learn | case anchor, thinking move, relation story, practice rep | do-not-overlearn, model links, relation links | packet construction details |
| Models | display name, one-sentence meaning, helps-notice, use/avoid | misuse, failure modes, practice prompts, source refs | raw canonical Markdown, curation JSON |
| Relations | plain-language story, why it matters, misread risk, practice prompt | taxonomy, confidence, source refs | raw relation extraction or unsupported speculation |
| Map | small neighborhood, search, filters, selection panel | source status, missingness | embeddings, full corpus, graph survival |
| Receipts | status summary, non-claims, advanced links | source refs, missing fields | local paths, provider internals |
| Advanced Audit | none for normal first-read | selected technical panels | internal debugging by default |

## Desired Product Progression

The product progression should become:

```text
1. Orient
   What run am I looking at?

2. Understand outcome
   What changed or survived in the answer?

3. Learn one move
   What reasoning move can I practice from this case?

4. Inspect the tools
   Which models and relation explain the move?

5. Explore the neighborhood
   What small graph helps me navigate the model context?

6. Check trust
   What is present, missing, reviewed, or explicitly not claimed?

7. Inspect internals
   What telemetry exists for maintainers and reviewers?
```

The first screen should not try to show all seven layers. It should orient the
user and offer clear next actions:

```text
Read the outcome
Practice the lesson
Open the model cards
Explore the map
Check receipts
```

## Critical Findings

### Finding 1: The Route Family Is Right

The current route family is the right backbone:

```text
/workspace?case_id=<id>#outcome
/workspace?case_id=<id>#learn
/workspace?case_id=<id>#models
/workspace?case_id=<id>#relations
/workspace?case_id=<id>#map
/workspace?case_id=<id>#receipts
/models/<id>?case_id=<id>
/relations/<id>?case_id=<id>
/audit
```

The product should keep this shape. The next work should improve hierarchy,
copy, and progressive disclosure instead of inventing another app.

### Finding 2: The Page Is Still Too Dense For A Normal User

The current workspace is one long page with every surface rendered. That is
useful for validation, but it can overwhelm a user because all layers are
present before the user understands the job of each layer.

The fix should not hide the data. It should make each surface start with a
short, readable first-read card and move supporting detail behind expansion.

### Finding 3: Teacher Needs A More Guided First Read

The Learn surface has the right ingredients, but the product should lead with a
clear teaching sentence:

```text
In this run, the useful move is to test authority pressure by asking what
evidence remains after status, confidence, or prestige stops counting.
```

Only after that should it show case anchor, model relationship, worked example,
practice rep, and boundary.

### Finding 4: Model Pages Need A Library Card Shape

The model page should read like:

```text
Authority Bias
What it helps you notice
When to use it
When it misleads
Practice this
Sources and missingness
```

It should avoid phrases that sound absolute, such as "Everything We Know", at
least until there is a full corpus library page with canonical completeness
rules.

### Finding 5: Relations Are The Best Current Product Signal

The relation page is closest to the desired teaching product because it starts
with a plain-language story and then explains why the pair matters. This is the
strongest useful signal from the current UI.

The next slice should preserve that story-first relation pattern and reuse it
inside Learn and Map.

### Finding 6: Receipts Are Correct But Too Loud

Receipts must exist, but their current form still feels like the system showing
its file cabinet. The first layer should be a trust summary:

```text
Teacher packet: available
Conversation understanding: available
Process brief: not requested
Human review: not claimed
Product proof: not claimed
```

Artifact refs, missing fields, and advanced links should be available behind a
clear "inspect details" expansion.

### Finding 7: Advanced Audit Must Be Visually Demoted

Advanced Audit is not wrong. It is a different audience. It should remain
available, but the normal user flow should not treat it as the seventh ordinary
tab.

Recommendation: keep the route, but visually label it as advanced inspection
and link it primarily from Receipts.

### Finding 8: Map Interaction Has One Immediate UX Bug

The map search/filter behavior can leave the selection panel pointing at an
item that is no longer visible. The next UI slice should update selection after
filters:

- if the selected node remains visible, keep it;
- if it becomes hidden, select the first visible node or edge;
- if nothing remains, show a no-results state.

## Recommended Next Slice

Next PR:
`Add Observatory progressive workspace UX hierarchy`

Decision gate:
`proceed_to_observatory_progressive_workspace_ux_slice`

Scope:

1. Keep the current portable Python/server-rendered Observatory owner.
2. Keep the existing route family.
3. Add first-read cards for Outcome, Learn, Models, Relations, Map, and
   Receipts.
4. Move technical support data behind `<details>` or equivalent server-rendered
   disclosure blocks.
5. Rename or visually demote Advanced Audit in the top navigation.
6. Change model page heading language from "Everything We Know" to a less
   absolute product label.
7. Fix stale Map selection after search/filter.
8. Keep relation pages story-first.
9. Keep source custody and non-claims visible but not dominant.

Stop before:

- full corpus library browsing;
- full corpus graph;
- runtime integration;
- default-on Conversation Understanding generation;
- provider/model API calls;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.

## Boundary Confirmation

This audit:

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

## Product Decision

Proceed to a progressive workspace UX slice before adding more data surfaces.

The current backbone is sufficient. The next risk is not missing data. The next
risk is information hierarchy: the product needs to teach users what to look at
first, what to open next, and what belongs only in receipts or advanced audit.
