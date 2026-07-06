# Mental Model Teacher Observatory Packet Adapter v0

Status: read-only Observatory adapter
Date: 2026-07-06
Decision gate: `proceed_to_observatory_teacher_learn_tab_ui`

## Purpose

This slice makes the checked-in Teacher learning packets consumable by
Observatory as selected-run data.

The adapter lives in:

```text
engine/system_b/mental_model_teacher_observatory_packet_adapter.py
```

The Observatory route is:

```text
/api/case/<id>/teacher-learning
```

It does not run Lolla. It does not invoke the Lolla skill. It does not call providers or model APIs, create new runs, mutate archives, judge answer quality, authorize action, or wire Lolla runtime behavior.

It does not render the Learn tab UI. It only gives the future UI a stable,
tab-ready payload.

## Product Role

This adapter is the bridge between:

- the selected run in Observatory;
- the offline Teacher learning packet package;
- the future single-shell Teacher presentation.

The target tab set remains:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

The adapter keeps `Advanced` separate from primary tabs.

## API Shape

For a selected case with a matching Teacher learning packet, the endpoint
returns:

- `available: true`;
- `packet_id`;
- `run_ref`;
- `observatory_tabs`;
- `default_tab`;
- `packet_summary`;
- `tab_payloads`;
- `advanced`;
- `single_home_rules`;
- `visibility_policy`;
- `missingness`;
- `non_claims`;
- false product/runtime/proof flags.

For a selected case without a matching packet, the endpoint returns:

- `available: false`;
- `unavailable_reason`;
- the expected Observatory tab list;
- explicit missingness;
- false product/runtime/proof flags.

This lets the future UI show a clean empty state instead of failing or inventing
Teacher content.

## Tab Mapping

The adapter maps packet objects into tab payloads:

| Tab | Adapter payload | Ownership rule |
|---|---|---|
| Outcome | compact Teacher learning summary | Outcome owns revised answer and structural pressure, not the Teacher lesson body |
| Learn | Teacher Lesson Product object | Teacher reasoning move lives here |
| Models | Mental Model Product Page objects | Canonical model explanations live here |
| Relations | Relation Product Page objects | Relation explanations live here |
| Map | Visual Graph object | Graph is navigation, not proof |
| Receipts | source refs, artifact refs, missingness, non-claims | Receipts are custody, not proof |
| Advanced | advanced-only artifact refs | Raw audit/review material stays outside primary tabs |

Primary tabs do not own receipt `artifact_refs`, raw telemetry, usage summaries,
or audit summaries.

## Case Matching

The adapter can match a packet by:

- selected archive case id and run id;
- run id alone for the current loaded Observatory result;
- case id alone as a fallback for direct offline review.

For example, this selected case id:

```text
archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79
```

matches the packet whose run reference has:

```text
case_id = launch-public-enterprise-beta
run_id = 20260627T104146Z_7bfe79
```

## Existing Case API Summary

The standard case payload now includes a compact `teacher_learning` summary.

That summary is intentionally small. It tells the SPA whether Teacher learning
is available and gives counts plus the lesson summary, but it does not embed the
full tab payload. The full payload is loaded through:

```text
/api/case/<id>/teacher-learning
```

## Stop Line

This PR stops before:

- rendering the Learn tab;
- changing the compiled Observatory SPA bundle;
- adding browser graph UI;
- creating new Lolla runs;
- provider or model calls;
- runtime wiring;
- product proof claims;
- human validation claims;
- answer or advice correctness scoring;
- action authorization.

Recommended next gate:

```text
proceed_to_observatory_teacher_learn_tab_ui
```
