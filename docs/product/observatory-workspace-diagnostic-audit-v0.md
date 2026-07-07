# Observatory Workspace Diagnostic Audit

Status: diagnostic Codex-assisted audit, browser-grounded and not human
validation.

Date: 2026-07-07

Decision gate: `needs_information_hierarchy_revision_before_expansion`

## Purpose

This audit records what the current portable Observatory workspace shows, what
role each surface should play, and how the information should progress from a
simple user-facing story into optional evidence.

The audit exists because the workspace is no longer just files or telemetry. It
now combines selected-run outcome, Teacher learning, mental model pages,
relation pages, map navigation, receipts, and technical audit routes. Without a
clear information hierarchy, those pieces can feel like several products placed
together.

## Browser scope

The audit used the offline synthetic fixture server and clicked or opened these
routes:

- `/`
- `/workspace?case_id=launch-public-enterprise-beta#outcome`
- `/workspace?case_id=launch-public-enterprise-beta#learn`
- `/workspace?case_id=launch-public-enterprise-beta#models`
- `/workspace?case_id=launch-public-enterprise-beta#relations`
- `/workspace?case_id=launch-public-enterprise-beta#map`
- `/workspace?case_id=launch-public-enterprise-beta#receipts`
- `/review/observatory-workspace?case_id=launch-public-enterprise-beta`
- `/models/authority-bias?case_id=launch-public-enterprise-beta`
- `/relations/authority-bias__first-principles-thinking__antagonist?case_id=launch-public-enterprise-beta`
- `/audit/extraction`
- `/usage`
- `/audit`

Map controls were also checked:

- relation filter;
- model search;
- reset.

## Current user story

The current workspace story is:

Outcome -> Learn -> Models -> Relations -> Map -> Receipts

That path is now visible and mostly coherent. The user starts from a selected
run, turns the run into one reasoning move, opens the mental models behind that
move, reads one model relationship, uses the map for wayfinding, and checks
receipts only when they need custody, missingness, or non-claims.

## What We Are Showing

| Surface | Data currently shown | Current role | Main risk |
| --- | --- | --- | --- |
| Root / Outcome | Selected case, run status, Reading Path, missing revised-answer state | Selected-run anchor | If the revised answer is missing, the first product moment becomes absence rather than learning. |
| Learn | Thinking move, relation pair, plain-language correction loop, user action | Primary product value | Strongest surface, but it depends on the user trusting why this move was selected. |
| Models | Model cards with meaning, use-when, mislead risk, model-page links | Reusable knowledge layer | Primary/supporting/optional model roles are not yet visually distinct. |
| Relations | Relation story, why it matters, misread risk, practice prompt, model links | Lesson between models | Good story-first order, but relation type is not strongly explained as navigation rather than proof. |
| Map | Three-model neighborhood, one relation, search, relation filter, selected detail panel | Wayfinding and choosing data | The map works, but node roles and edge meaning need stronger hierarchy. |
| Receipts | Teacher packet status, Conversation Understanding status, Process Brief status, non-claims, review guide, technical links | Trust and missingness layer | Receipts can still look like the product if the user enters through technical links first. |
| Review Guide | Main review question, six-surface path, blank human form pointer, boundaries | Human review entry | Useful for review, not an end-user learning surface. |
| Model page | Model explanation, helps-notice, use-when, avoid-when, practice placeholder, run links | Model detail / library object | It mixes reusable model knowledge and selected-run context without a visible mode switch. |
| Relation page | Plain-language story, why it matters, misread risk, practice prompt, model links | Relation detail / library object | It is clear, but relation confidence and source status are intentionally not prominent yet. |
| Technical audit routes | Extraction missingness, usage missingness, telemetry panel index, lane/audit links | Optional inspection | These are useful for builders, but should remain behind Receipts or explicit audit entry. |

## Desired Information Hierarchy

The workspace should treat data in three layers.

### First-class product information

First-class information is what a cold user should understand without opening
technical inspection:

- the selected run or case anchor;
- the one-sentence outcome or explicit missing outcome state;
- the reasoning move to practice;
- the model pair or model stack behind the move;
- the relation story between the models;
- one practice rep;
- visible non-claims and missingness when needed.

This is the product. It should be short, readable, and explain why the user is
seeing it.

### Supporting knowledge information

Supporting information helps the user explore after the first read:

- model cards;
- model detail pages;
- relation detail pages;
- map neighborhood;
- search and relation filters;
- source/custody status summaries;
- review guide for human product review.

This layer should answer: what can I open next, and why?

### Inspection information

Inspection information should stay available but should not lead the product:

- extraction audit;
- usage summary;
- advanced audit index;
- lane details;
- route traces;
- graph survival;
- run events;
- raw telemetry-style evidence.

This layer should answer: what exists, what is missing, and what evidence can a
builder inspect?

## What Works

- The top-level path now gives a clear order.
- Learn is a real product moment because it offers a named thinking move and a
  concrete practice action.
- Model cards and model pages make mental models clickable and readable.
- Relation pages tell the story before taxonomy.
- The map has search, relation filters, reset, and explicit non-proof copy.
- Receipts separate trust status, non-claims, human review, and technical
  inspection.
- The review guide asks the right product question: does this feel like one
  Observatory product surface?

## What Still Feels Wrong

The strongest unresolved UX issue is not missing data. It is hierarchy.

The workspace currently has many useful pieces, but the page does not always
make clear which piece is:

- the user's main job;
- supporting knowledge;
- optional inspection;
- missing but expected;
- present but not evidence of correctness.

This matters because the same run can show Teacher content, model library
content, relation content, map navigation, receipts, missing sidecars, usage
missingness, and advanced telemetry. Those are not equal product objects.

## Recommended UX Direction

The next design revision should make the hierarchy explicit:

1. Make Outcome resilient when the answer artifact is missing.
   The user should see: "Outcome is unavailable for this fixture; continue to
   Learn to review the teaching surface." Missingness should not make the first
   product moment feel broken.

2. Label model roles.
   Models should distinguish primary model, contrast model, and supporting model
   when the packet knows those roles. If it does not know, it should say so.

3. Add a visible Library / Run-context distinction on model pages.
   A model page should let the user understand the model as reusable knowledge
   while also seeing how this run used it.

4. Keep technical audit behind Receipts.
   Audit pages are valuable, but they should stay second-class in the normal
   user journey.

5. Preserve the map as navigation.
   Search and filter are useful for choosing data. Edges should continue to be
   described as navigation and relation stories, not proof.

## Strongest Useful Signal

The strongest useful signal is that Observatory now has the shape of one
learnable run workspace:

selected run -> reasoning move -> model stack -> relation story -> graph
wayfinding -> receipts.

That is the right product direction.

## Strongest Unresolved Risk

The strongest unresolved risk is that first-class, supporting, and inspection
data are still close together. A user can understand the flow if guided, but a
cold user may still experience it as "everything at once" unless hierarchy,
role labels, and missingness states become more explicit.

## Boundary

This audit:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate or attach sidecars;
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
- does not treat relation confidence as certification.

## Next Gate

Recommended next gate:

`needs_information_hierarchy_revision_before_expansion`

The next PR should implement one small hierarchy revision, not a broad redesign.
The best first slice is likely Outcome missingness plus model role labels.
