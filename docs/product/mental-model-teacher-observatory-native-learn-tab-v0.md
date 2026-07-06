# Mental Model Teacher Observatory Native Learn Tab v0

Status: Observatory-native Learn UX slice
Date: 2026-07-06
Decision gate: `proceed_to_interactive_observatory_teacher_graph`

## Purpose

This slice changes the visible Teacher learning surface from a readable but
document-like page into an Observatory-native review experience.

The user should no longer feel that Teacher material, model pages, relation
pages, receipts, and telemetry are all being dumped into one undifferentiated
pile.

The route stays:

```text
/teacher-learning
```

The read-only packet route stays:

```text
/api/case/<id>/teacher-learning
```

This does not run Lolla.
It does not invoke the Lolla skill.
It does not call providers or model APIs.
It does not create new runs, mutate archives, judge answer quality, authorize
action, or wire Lolla runtime behavior.

## Design Decision

The Learn page now borrows directly from the existing Observatory aesthetic:

- deep indigo Observatory shell;
- Inter body text;
- JetBrains Mono metadata and controls;
- teal primary affordances;
- thin translucent borders;
- compact tabs;
- dense but readable cards;
- right-side contextual rail;
- drawer-style detail panels.

The compiled SPA bundle is still not changed in this slice. The implementation
uses the same server-rendered portability pattern as `/audit` and `/usage`.

## Information Architecture

The primary reading path is:

```text
case anchor -> thinking move -> model stack -> practice rep -> model pages -> relation page -> map
```

The secondary/supporting path is:

```text
run context -> missingness -> receipts -> non-claims -> telemetry
```

That split matters. Teacher is not telemetry. Telemetry is not the lesson.
Receipts are custody, not product proof.

## Clickable Detail

This slice adds product-safe clickthroughs without creating a second app:

- clickable mental model detail drawers;
- clickable relation detail drawers;
- source custody inside detail drawers;
- missingness inside detail drawers;
- non-claims inside detail drawers.

The mental model drawer is the first real answer to the product question:

```text
When I click a mental model, can I see what we know about this model?
```

In v0, the answer is yes, but only through translated product-safe fields:

- one-sentence meaning;
- helps notice;
- use when;
- avoid when;
- common misuse when present;
- failure modes;
- premortem questions;
- heuristics;
- reasoning types;
- source refs;
- missingness;
- non-claims.

Raw canonical Markdown is not rendered as the user interface. It remains source
custody.

## Relation Treatment

Relation pages still explain the story before taxonomy.

The visible order is:

1. plain-language story;
2. why it matters;
3. misread risk;
4. practice prompt;
5. relation type and confidence;
6. source reference;
7. missingness and non-claims.

Confidence is an exposure hint, not proof or certification.

## What This Still Is Not

This is not a customer-ready product claim.

It is not:

- product proof;
- human validation;
- answer correctness scoring;
- advice correctness scoring;
- action authorization;
- runtime integration;
- provider or model calls;
- a full compiled SPA rebuild;
- a full-corpus graph.

## Stop Line

This PR stops before:

- interactive browser graph UI;
- full corpus graph;
- compiled SPA source rebuild;
- runtime wiring;
- live Lolla runs;
- provider or model calls;
- product readiness claims;
- human validation claims.

Recommended next gate:

```text
proceed_to_interactive_observatory_teacher_graph
```
