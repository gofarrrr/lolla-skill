# Mental Model Teacher Observatory Learning Packet Contract v0

Status: contract layer
Date: 2026-07-06
Decision gate: `proceed_to_observatory_teacher_learning_packet_builder`
Example:
[Observatory Teacher learning packet example](mental-model-teacher-observatory-learning-packet-example-v0.json)

## Purpose

This slice defines the selected-run learning packet that lets Observatory mount
Mental Model Teacher as one mode inside the existing post-run workspace.

The contract lives in:

```text
engine/system_b/mental_model_teacher_observatory_learning_packet.py
```

It does not build packets, render UI, alter Observatory, run Lolla, invoke the
Lolla skill, call providers, create a run, judge answer quality, or wire runtime
behavior.

It does not build product data. That belongs to the next builder slice.

## Product Role

The packet is the bridge between the existing run/custody artifacts and the
future Observatory tabs:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

It composes the existing product-safe contracts:

- Teacher Lesson Product object;
- Mental Model Product Page object;
- Relation Product Page object;
- Visual Graph object.

Then it adds selected-run ownership:

- run reference;
- exact Observatory tab list;
- default tab;
- single-home rules;
- visibility policy;
- receipts;
- missingness;
- non-claims.

## Required Top-Level Fields

- `schema_version`;
- `packet_id`;
- `run_ref`;
- `observatory_tabs`;
- `default_tab`;
- `lesson`;
- `models`;
- `relations`;
- `graph`;
- `receipts`;
- `single_home_rules`;
- `visibility_policy`;
- `missingness`;
- `non_claims`;
- `product_proof`;
- `human_validated`;
- `runtime_integration_authorized`;
- `provider_or_model_calls_used`.

The schema version is:

```text
lolla.observatory_teacher.learning_packet.v0
```

## Tab Contract

The packet must declare exactly:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

`default_tab` may be `Outcome` or `Learn`. The final product default remains a
UX decision; the contract only prevents unsupported tab names.

## Single-Home Rules

The packet must preserve these ownership rules:

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

This is the main anti-duplication guardrail. Other tabs may link to an object,
but they should not become its home.

## Visibility Policy

The packet must state:

- raw telemetry is not shown in primary tabs;
- raw canonical Markdown is not shown in primary tabs;
- review controls are not shown in the Learn tab;
- advanced telemetry remains separate;
- receipts are custody, not proof;
- graph edges are navigation, not proof.

## Receipts

Receipts carry:

- `source_refs`;
- `artifact_refs`;
- `missingness`;
- `non_claims`.

Receipt artifacts must be assigned to either:

- `Receipts`;
- `Advanced`.

They must not be assigned to `Outcome`, `Learn`, `Models`, `Relations`, or
`Map`. Those primary tabs may summarize or link to receipts, but they do not own
raw sidecars, traces, usage telemetry, graph-survival reports, or evaluation
artifacts.

## Rejection Rules

The validator rejects packets that:

- use a wrong schema;
- omit any required field;
- use unsupported tabs;
- turn product proof, human validation, runtime integration, or provider/model
  calls on;
- omit required non-claims;
- include absolute/local private paths;
- expose forbidden approval, certification, winner, runtime hook, or score keys;
- place receipt artifacts outside Receipts or Advanced;
- violate nested model, relation, lesson, or graph contracts.

## Stop Line

This PR stops before:

- data builders;
- Observatory endpoints;
- Observatory UI;
- runtime wiring;
- provider/model calls;
- live Lolla runs;
- answer/advice correctness scoring;
- product proof or human validation claims.

Recommended next gate:

```text
proceed_to_observatory_teacher_learning_packet_builder
```
