# Observatory Outcome User Value PRD v0

Status: planning PRD.

Date: 2026-07-07

Decision gate: `proceed_to_outcome_user_value_redesign`

Related implemented surfaces:

- [Observatory Server Rendered Root Workspace](observatory-server-rendered-root-workspace-v0.md)
- [Observatory Run Contents Panel](observatory-run-contents-panel-v0.md)
- [Observatory Run Inventory Receipt Panel](observatory-run-inventory-receipt-panel-v0.md)
- [Observatory Model Local Neighborhoods](observatory-model-local-neighborhoods-v0.md)

## Purpose

This PRD records a browser-grounded product problem before the team adds more
UI around it:

```text
The Observatory Outcome surface is not yet useful enough for the user.
```

The current page explains the intended reading path, repeats navigation, shows
status chips, and describes what the workspace can contain. The visible user
value is much thinner: one truncated recommendation sentence, one truncated
support paragraph, and a hidden pressure line.

That is backwards. Outcome should be the user's result page.

## Browser Evidence

The live Observatory was audited in browser on the launch public enterprise beta
run:

`/workspace?case_id=archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79#outcome`

The user also supplied screenshots from the same surface. The screenshots and
browser click-through showed the same issue:

- top navigation repeats the same six surfaces;
- left sidebar repeats the same six surfaces with descriptions;
- center page repeats the same reading path again as cards and buttons;
- `Run contents` explains what is available before the user gets the result;
- the first real outcome content appears below the fold or near the bottom of
  the first view;
- the outcome text is truncated with ellipses;
- the strongest pressure is hidden under `Outcome support details`;
- useful product content is stronger in Learn, Models, Relations, and Receipts
  than it is in Outcome.

## What The Browser Actually Shows

| Surface | Useful visible content | Overhead or mismatch | Product gap |
| --- | --- | --- | --- |
| Outcome | A truncated stance: `I would still tell you not to launch a public Enterprise Beta next month...`; a hidden strongest pressure; three model chips. | Top nav, left reading path, center start card, center action cards, run contents, and status chips all compete with the result. | The user cannot quickly answer: what is the answer, why, what changed, what should I do next, and what would change confidence? |
| Learn | A concrete move: `Test The Authority, Not The Aura`; relation story; practice action; do-not-overlearn boundary. | Missingness and internal labels appear inside the expanded lesson detail. | Learn is closer to a product surface than Outcome, but should not carry the burden of explaining the run result. |
| Models | Three readable model cards with use/mislead cues and role context. Model detail pages now show reviewed local neighborhoods. | Still some role-cue ceremony and support disclosures. | Models are useful after the user understands the outcome, not as a substitute for the outcome. |
| Relations | Plain-language relation story, why it matters, misread risk, and practice prompt. | Relation detail mostly repeats the card, then exposes taxonomy/custody labels. | Relation pages are useful but should be reached from a clear result story. |
| Map | Small selected-run graph with search/filter and honest non-claim that edges are navigation, not proof. | Only 3 models and 1 relation, so search/filter can collapse to 1 node and 0 relations. | This is wayfinding, not the broader mental model graph and not the outcome. |
| Receipts | Trust summary, Download MD, inventory counts, grouped inventory, non-claims, technical links. | Too much for first read. | Receipts should remain the accountable inspection layer, not be used to compensate for a weak outcome. |

## Core Product Principle

Outcome is not an orientation page.

Outcome should answer:

```text
What did the run conclude, why, what changed, what should I inspect next,
and what would change confidence?
```

The reading path belongs in navigation. The data inventory belongs in Receipts.
The teaching move belongs in Learn. The model explanations belong in Models.
Outcome owns the result.

## User Questions Outcome Must Answer

The first Outcome viewport should answer these questions without opening a
disclosure:

1. What is the current answer or stance?
2. What changed from the original answer or first frame?
3. Why did it change?
4. What are the main reasons, risks, or constraints?
5. What would change confidence?
6. What should the user inspect or do next?
7. What is missing or uncertain?
8. What is not being claimed?

The page can still link to Learn, Models, Relations, Map, Receipts, and the
private Markdown export, but those links should support the result rather than
replace it.

## Required Product Shape

### First Viewport

The first viewport should show:

- compact case/run context;
- one full outcome headline with no ellipsis;
- one readable answer summary, not a clipped paragraph;
- `Why this answer changed` as 2 to 4 bullets;
- `What would change confidence` as 1 to 3 bullets;
- primary next action links limited to the two most relevant paths.

The first viewport should not show:

- a large central reading-path card;
- a second set of all six navigation options;
- status chips before result content;
- broad claims like `We captured enough...` before the user sees what was
  captured;
- telemetry, JSON-looking labels, source refs, or internal taxonomy.

### Result Body

After the first viewport, Outcome should show:

- `Decision stance`: the full stance in plain language.
- `Reasoning delta`: what changed or what pressure altered the answer.
- `Evidence and constraints`: the few facts or assumptions the answer depends
  on.
- `Risks and caveats`: where the answer can fail or be misread.
- `Confidence boundary`: what evidence would change the conclusion.
- `Next useful moves`: links to Learn, Models, Relation, Receipts, and Download
  MD, each with a reason.

### Details

Details should remain expandable:

- source/custody;
- strongest pressure;
- model chips;
- missingness;
- non-claims;
- technical inspection links.

But details should not be the only place where the useful result appears.

## Proposed Outcome Object

The UI needs a product-facing outcome object that is stronger than the current
headline-plus-summary shape.

```json
{
  "case_id": "archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
  "outcome_headline": "Do not launch the public Enterprise Beta next month until enterprise-proof evidence is stronger.",
  "stance": "hold_or_stage_launch",
  "plain_language_answer": "A full readable answer written for the user, not clipped for a card.",
  "what_changed": [
    "The run challenged whether authority, polish, or enterprise posture was standing in for proof."
  ],
  "primary_reasons": [
    "Enterprise proof must survive diligence, not just sound credible.",
    "The launch decision needs evidence that remains persuasive after authority cues are removed."
  ],
  "confidence_boundary": [
    "Confidence would change if there is concrete enterprise diligence evidence, support readiness, and a bounded beta scope."
  ],
  "recommended_next_moves": [
    {
      "label": "Practice the reasoning move",
      "href": "#learn",
      "reason": "Learn how to test authority signals against evidence."
    },
    {
      "label": "Inspect receipts",
      "href": "#receipts",
      "reason": "Check what artifacts exist and what is not claimed."
    }
  ],
  "missingness": {
    "status": "partial",
    "notes": [
      "Outcome text is sourced from run artifacts and may lack a fully structured options analysis."
    ]
  },
  "non_claims": [
    "not_product_proof",
    "not_human_validation",
    "not_answer_correctness",
    "not_advice_correctness",
    "not_action_authorization"
  ]
}
```

This object can be built deterministically from existing run artifacts when
fields exist. If a field is absent, the UI should show missingness plainly
rather than filling the gap with ceremony.

## Source Inputs To Reuse

The redesign should reuse existing completed-run artifacts only:

- `result.json` and current product view adapters;
- `revised_answer` or equivalent outcome text;
- `memo_what_changed` when present;
- `delta_card` pressure fields, including `challenge_statement`;
- `extraction` decision situation and conversation framing;
- Teacher learning packet for the next reasoning move;
- model/relation product pages for relevant links;
- run inventory receipt for what exists and what is missing;
- agent memory Markdown export for private agent review.

No provider calls are needed.

## Interaction Requirements

- Clicking `Outcome` should land directly on the answer, not on an explanation
  of how to use the workspace.
- The sidebar reading path can remain, but the center page must not repeat the
  same six choices.
- The page should never have two identical `Open model cards` links visible in
  the same context. The browser audit found this creates ambiguous interaction.
- `Download MD` can remain visible, but it should be framed as an export action,
  not the primary way to understand the result.
- `Outcome support details` should be renamed to something user-readable such
  as `Why this changed and what is uncertain`.
- Any truncated text in Outcome must be a preview only. The full outcome answer
  must be readable without opening a technical route.

## Acceptance Criteria

The next implementation PR should pass these checks:

- On a 1920px desktop viewport, the first Outcome screen contains the full
  outcome headline, primary answer summary, why-it-changed bullets, confidence
  boundary, and at most two primary next actions.
- The first Outcome screen does not contain the central six-card reading path.
- The first Outcome screen does not start with status chips or inventory claims.
- Outcome has no ellipsis in the primary answer text.
- Outcome details include strongest pressure, model chips, missingness, and
  non-claims, but those are below the useful result.
- Browser automation can click each primary Outcome action without strict-mode
  ambiguity from duplicate visible labels.
- Learn, Models, Relations, Map, and Receipts remain reachable from the global
  navigation.
- The implementation does not change runtime behavior or create new runs.

## Stop Conditions

Stop before:

- provider/model API calls;
- Lolla runtime wiring;
- automatic sidecar generation;
- action authorization;
- product-proof claims;
- human-validation claims;
- answer/advice correctness scoring;
- full graph redesign.

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

## Proposed PR Sequence

### PR-O1 Outcome Object Audit And Contract

Create a product-facing outcome view object with explicit fields for answer,
what changed, reasons, confidence boundary, next moves, missingness, source
refs, and non-claims.

Stop before renderer changes.

### PR-O2 Outcome First Viewport Redesign

Replace the center reading-path/start panel on Outcome with the useful outcome
object.

Keep the global nav and sidebar available. Remove duplicate center navigation.

Stop before Learn/Model/Relation/Map redesign.

### PR-O3 Outcome Browser Review Packet

Run browser-grounded checks over Outcome, Learn, Models, Relations, Map, and
Receipts. Compare old vs new first viewport and record what is visible, hidden,
or deferred.

Stop before any product readiness claim.

## Recommended Next Gate

`proceed_to_outcome_user_value_redesign`

Reason: the strongest current UX miss is not lack of graph or lack of model
data. It is that the first product surface, Outcome, does not yet present the
result as useful user-facing information.
