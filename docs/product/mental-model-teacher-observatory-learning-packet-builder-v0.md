# Mental Model Teacher Observatory Learning Packet Builder v0

Status: offline builder
Date: 2026-07-06
Decision gate: `proceed_to_observatory_teacher_packet_adapter`
Output package:
[Observatory Teacher learning packets](mental-model-teacher-observatory-learning-packets-v0/manifest.json)

## Purpose

This slice makes the Teacher and Observatory integration concrete without
mounting anything in Observatory yet.

The builder lives in:

```text
engine/system_b/mental_model_teacher_observatory_learning_packet_builder.py
```

It builds selected-run `teacher_learning_packet.v0` objects from checked-in
Teacher case artifacts and existing canonical model substrate.

It does not run Lolla, invoke the Lolla skill, call providers, create runs,
alter Observatory routes, render UI, judge answer quality, authorize action, or
wire runtime behavior. In other words, it does not alter Observatory routes or
turn the packet into a live endpoint.

## Product Role

The packet builder answers the information-flow problem:

```text
One selected run -> one Observatory shell -> one Teacher learning packet
```

Each packet feeds the future Observatory tabs:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

The builder does not decide the final visual layout. It decides what product
objects are allowed to enter the layout and where they belong.

## Inputs

For each case, the builder reads the checked-in Teacher source package under:

```text
reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/<case-id>/
```

It uses:

- `mental_model_teacher_lesson.json` for the Teacher Lesson Product object;
- `mental_model_teacher_relation_deep_dive.json` for the Relation Product Page
  object;
- `mental_model_teacher_model_deep_dive.json` and related source files as
  receipt material;
- existing canonical model source, activation curation, intervention semantics,
  relation semantics, and source hashes to build durable Mental Model Product
  Page objects;
- the existing lesson graph builder to build the Visual Graph object.

The current pilot cases are:

- `launch-public-enterprise-beta`;
- `deploy-assisted-intake-routing`;
- `ceo-remove-founding-cofounder`.

## Output Shape

The builder writes:

```text
docs/product/mental-model-teacher-observatory-learning-packets-v0/
  manifest.json
  packets/
    launch-public-enterprise-beta.learning-packet.json
    deploy-assisted-intake-routing.learning-packet.json
    ceo-remove-founding-cofounder.learning-packet.json
```

Each packet contains:

- `lesson`: the selected-run Teacher lesson for `Learn`;
- `models`: canonical model page objects for `Models`;
- `relations`: relation page objects for `Relations`;
- `graph`: the small lesson neighborhood for `Map`;
- `receipts`: source and advanced artifact custody for `Receipts` and
  `Advanced`;
- `single_home_rules`: the anti-duplication ownership map;
- `visibility_policy`: the primary-tab versus advanced-material policy;
- `missingness` and `non_claims`.

## Information Ownership

The builder preserves the single-home rules from the packet contract:

| Information | Home |
|---|---|
| revised answer | Outcome |
| structural pressure findings | Outcome |
| Teacher reasoning move | Learn |
| canonical model explanation | Models |
| model activation evidence | Outcome |
| relation explanation | Relations |
| graph neighborhood | Map |
| source custody | Receipts |
| usage/cost telemetry | Advanced |
| graph survival/evals | Advanced |

This matters because the old failure mode was one screen containing lesson
copy, source custody, model fragments, telemetry, review data, and graph
material at once. The packet builder does not solve the UI, but it gives the UI
a clean set of compartments.

## Model Identity Rule

Mental model pages use canonical model identity.

For example:

```text
Authority Bias
```

is the model page identity, while:

```text
Test The Authority, Not The Aura
```

remains a lesson or practice label. The builder must not turn lesson slogans
into canonical model names.

## Receipts And Advanced Material

Receipt artifacts are assigned only to:

- `Receipts`, for source custody that a reviewer or user may inspect;
- `Advanced`, for audit/review/supporting artifacts.

They are not assigned to `Outcome`, `Learn`, `Models`, `Relations`, or `Map`.

That means raw Teacher notes, review artifacts, traces, conformance checks, and
audit files can remain inspectable without becoming the learner-facing page.
Telemetry and review/audit artifacts are Receipts or Advanced material, not the
primary teaching surface.

## Missingness

The packets are intentionally partial.

Known missing pieces include:

- Observatory endpoint or static adapter;
- Observatory UI mount;
- selected-run Outcome binding;
- human review;
- live run binding.

Those are recorded as missingness. They are not papered over with copy.

## Stop Line

This PR stops before:

- Observatory endpoints;
- Observatory UI;
- runtime integration;
- provider or model calls;
- live Lolla runs;
- answer or advice correctness scoring;
- product proof claims;
- human validation claims;
- action authorization.

Recommended next gate:

```text
proceed_to_observatory_teacher_packet_adapter
```
