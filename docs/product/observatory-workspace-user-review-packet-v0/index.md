# Observatory Workspace User Review Packet v0

Status: ready for human review
Date: 2026-07-06

## What To Review

Review the selected-run Observatory workspace as one product surface.

Use an existing completed run already available to Observatory. Do not create a
new run for this review. Do not run Lolla. Do not use provider or model calls.

Review the flow in this order:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The main review question:

```text
Does the workspace help a user move from the run outcome to one learnable
reasoning move, then to the models, relation, map, and receipts behind it?
```

## First Impression

Open the workspace and spend no more than ten seconds on the first screen.

Answer:

- What do you think this page is for?
- What would you click next?
- Does the page feel like one product or several artifacts pasted together?
- Is the first screen explaining the flow, or overwhelming it?

## Information Ladder

The intended ladder is:

```text
first read -> optional support -> drill-down page -> receipts/audit
```

Use this ladder to judge every surface.

First read should be understandable without technical context.

Optional support should help a curious user without becoming the main product.

Drill-down pages should carry deeper model or relation detail.

Receipts and audit routes should preserve custody, missingness, and inspection
without becoming marketing or proof.

## Surface Review

### Outcome

Expected job:

- show what changed or survived in the run;
- anchor the learning flow in the selected case;
- offer a clear next action into Learn or Models.

Review prompts:

- Can you tell what happened in the run?
- Is the next step obvious?
- Is anything technical shown too early?
- Does the page avoid claiming the answer is correct?

### Learn

Expected job:

- teach one case-anchored reasoning move;
- make the practice rep the product value;
- explain the model relationship enough to motivate practice.

Review prompts:

- Can you explain the reasoning move in one sentence?
- Do you know what to practice?
- Does the lesson feel connected to the case?
- Does it avoid pretending the lesson proves the answer?

### Models

Expected job:

- let the user choose reusable mental model concepts;
- show enough to decide which model to open;
- avoid turning the workspace into an encyclopedia.

Review prompts:

- Can you tell why each model is relevant?
- Is the model card short enough to scan?
- Does the model page feel like the right place for deeper detail?
- Is canonical-source-derived material readable as product copy?

### Relations

Expected job:

- explain the lesson between model pairs;
- put plain-language story before taxonomy;
- avoid treating confidence or relation type as proof.

Review prompts:

- Can you tell how the models interact?
- Does the relation story come before technical labels?
- Is the misread risk useful?
- Does the relation page avoid overclaiming?

### Map

Expected job:

- provide small-neighborhood wayfinding;
- let the user move between models and relations;
- make edges navigational, not evidentiary.

Review prompts:

- Can you tell what the map is showing?
- Can you click a node or edge and understand the detail panel?
- Do search and filters feel like controls for exploration?
- Does the map avoid implying graph edges are proof?

### Receipts

Expected job:

- show what exists, what is missing, and what is not claimed;
- keep audit routes reachable;
- prevent the learning product from becoming a proof system.

Review prompts:

- Can you tell what is available and what is deferred?
- Are non-claims visible enough?
- Are technical links useful without leading the product?
- Does Receipts keep Decision Work and technical audit separate from Learn?

## What Should Not Happen

The workspace should not:

- show raw JSON as the main product surface;
- expose raw telemetry as the first read;
- present graph edges as proof;
- present relation confidence as certification;
- imply product proof or human validation;
- claim answer correctness or advice correctness;
- authorize automatic action;
- feel like a duplicate Teacher product outside Observatory.

## Review Output

Complete the blank human review form only after clicking through the surfaces.

Useful review notes should identify:

- which surface confused you first;
- which sentence or label caused the confusion;
- what you expected to click next;
- what should be hidden, renamed, moved, or expanded;
- whether the product feels like Observatory with Learn nested inside it.

Do not mark the review positive by default. A useful negative or partial review
is a successful review outcome.
