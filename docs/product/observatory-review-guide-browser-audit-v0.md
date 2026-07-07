# Observatory Review Guide Browser Audit

Status: diagnostic Codex-assisted browser audit, not human validation.

Date: 2026-07-07

Decision gate: `ready_for_human_hierarchy_review`

## Purpose

This audit records what the portable Observatory workspace shows after the
Review Guide gained explicit hierarchy prompts. It answers four product
questions:

- what data is visible;
- what the product wants the user to understand;
- how the user should move from general information into detail;
- where technical or supporting information can still overwhelm the learning
  journey.

This is not a human review result. It is a browser-grounded diagnostic record
that makes the next human review more precise.

## Browser Method

The audit used a fixture-backed local Observatory server for the selected case:

`launch-public-enterprise-beta`

The audit started at:

`/review/observatory-workspace?case_id=launch-public-enterprise-beta`

Then it clicked through:

- Review Guide -> Outcome;
- Outcome -> Learn;
- Learn -> Models;
- Models -> model detail;
- Model detail -> Relations;
- Relations -> relation detail;
- Relation detail -> Map;
- Map search;
- Map relation filter;
- Map reset;
- Map -> Receipts;
- Receipts -> Extraction audit;
- Extraction audit -> Usage;
- direct open of Advanced audit.

No run was created and no provider or model API was called.

## Current Progression

The visible product progression is:

```text
Review Guide -> Outcome -> Learn -> Models -> Relations -> Map -> Receipts -> Audit only if needed
```

The normal learner progression remains:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

Audit routes remain available from Receipts, but they are inspection surfaces,
not primary learning surfaces.

## What The Review Guide Now Shows

The Review Guide now starts with a general product question and then forces the
reviewer to check the hierarchy:

- `primary: Outcome and Learn`
- `supporting: Models, Relations, and Map`
- `inspection: Receipts and Audit`

It asks the reviewer to record:

- the first thing they thought the workspace was for;
- the first surface or link they wanted to open next;
- where product content blurred into receipts, audit, or telemetry;
- whether Library view and selected-run context were hard to separate;
- whether technical detail pulled attention away from the learning journey.

Useful signal: the guide now asks the right diagnostic question.

Remaining risk: the guide itself is not the product experience. It can direct a
reviewer, but it does not prove that a cold learner will understand the
workspace without that review framing.

## Visible Surface Audit

| Surface | What is visible | What the user should understand | Progression role | Overload risk |
| --- | --- | --- | --- | --- |
| Outcome | selected case, run id, health, start panel, missing outcome state | start with the selected run; if the outcome artifact is missing, continue to Learn | primary entry | missingness can still feel like absence unless the user accepts it as a state |
| Learn | reasoning move, model pair, relation story, practice action | this is the transferable teaching value of the run | primary product value | strongest page, but the selection reason is still mostly implicit |
| Models | three model cards, role cues, use-when, mislead risk, model links | models are reusable tools behind the lesson | supporting knowledge | role cues help, but the page still has many text blocks |
| Model detail | Library view, Run context, not-proof cue, helps-notice, use/avoid, practice placeholder | model knowledge comes first; selected-run role is context, not a score | drill-down support | still long enough that a user may not know where to stop reading |
| Relations | pair story, why it matters, misread risk, practice prompt, model links | the relationship is the lesson between models | supporting knowledge | relation type remains background; good, but source/confidence is intentionally quiet |
| Relation detail | plain-language story, why it matters, misread risk, practice prompt | a relation page teaches the edge before naming the edge | drill-down support | low current risk; it is focused and story-first |
| Map | small neighborhood, search, relation filter, reset, selected detail panel, non-proof copy | map is for wayfinding and choosing data | supporting navigation | graph visuals can still invite proof-reading, so non-proof copy must stay visible |
| Receipts | status chips, non-claims, human review link, technical inspection links | receipts answer what exists, what is missing, and what is not claimed | inspection and custody | if entered first, Receipts can look like the product instead of the support layer |
| Extraction audit | audit navigation, extraction missingness, sidecar status | this is builder inspection, not learner narration | advanced inspection | dense telemetry nav can overwhelm a learner |
| Usage | usage missingness | usage is run telemetry, not product value | advanced inspection | low risk if only reachable from inspection |
| Advanced audit | telemetry index, lane links, routing, treatment audit, graph survival, events | this is the system trace behind the run | advanced inspection | highest overload risk; should remain behind Receipts or explicit audit entry |

## Information Flow

The user should encounter information in this order:

1. General: what run or case am I looking at?
2. Product value: what reasoning move can I learn?
3. Support: which models and relations explain the move?
4. Navigation: where can I jump next?
5. Custody: what exists, what is missing, and what is not claimed?
6. Inspection: what technical evidence can a builder audit?

This is the simplest product story currently supported by the workspace.

## What Works Now

- The Review Guide makes the hierarchy question explicit.
- Outcome missingness points the user toward Learn instead of faking an answer.
- Learn has a clear named reasoning move: `Test The Authority, Not The Aura`.
- Models are clickable and carry role cues that say navigation cue, not proof.
- Model detail separates Library view from selected-run context.
- Relations and relation detail are story-first.
- Map search, relation filter, and reset work as data-picking controls.
- Map copy explicitly says edges are navigation, not proof.
- Receipts places Human review before Technical inspection.
- Technical audit routes remain separate and visibly denser than product pages.

## What Still Needs Human Review

The next human reviewer should decide whether a cold user can understand:

- that Outcome and Learn are primary;
- that Models, Relations, and Map are support;
- that Receipts and Audit are inspection;
- that a missing Outcome artifact is a real state, not a broken product;
- that model role labels are navigation cues, not scores;
- that Map edges are navigation, not proof;
- that the Advanced audit is not the main user journey.

The audit can confirm these cues exist. It cannot confirm that they work for a human learner.

## Strongest Useful Signal

The strongest useful signal is that the current Observatory surface now has a testable hierarchy. A reviewer can follow the page from Review Guide to Outcome,
then through Learn, Models, Relations, Map, Receipts, and into Audit only when
needed.

## Strongest Unresolved Risk

The strongest unresolved risk is still cognitive overload. The workspace has
the right objects, but a cold user may still read supporting model detail,
receipts, and audit routes as equal to the core teaching journey unless the
first human hierarchy review says otherwise.

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

`ready_for_human_hierarchy_review`

The next PR should either collect the first human hierarchy review using the blank form or make one small UI change if the human reviewer cannot understand the first-read hierarchy.
