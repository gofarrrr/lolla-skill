# Observatory Portable View Model Adapters v0

Status: read-only adapter layer
Date: 2026-07-06
Decision gate: `proceed_to_observatory_server_rendered_root_workspace`

## Purpose

This slice adds the first read-only adapter layer for the portable
server-rendered Observatory direction.

The adapter lives in:

```text
observatory/product_view_adapters.py
```

It translates existing selected-run and Teacher-learning payloads into the
product-safe contracts from:

```text
observatory/product_views.py
```

The adapter does not render UI, change routes, mutate archives, write sidecars,
invoke Lolla, create a new run, call providers or model APIs, touch
`observatory/build/*`, or revive the legacy Svelte root app.

## Input Shape

The adapter can consume:

- selected Observatory case id;
- existing `result.json` payload when supplied by the server;
- optional `result_path` for read-only sidecar discovery;
- existing Teacher learning packet adapter response;
- existing Decision Work status adapter response.

When the Teacher response is not supplied, the adapter calls the existing
checked-in Teacher packet adapter:

```text
engine/system_b/mental_model_teacher_observatory_packet_adapter.py
```

When the Decision Work status is not supplied, the adapter calls the existing
read-only sidecar status adapter:

```text
engine/system_b/observatory_decision_work_status.py
```

Those calls are local and deterministic. They do not generate interpretation or
call providers.

## Output Shape

The public function is:

```text
build_observatory_product_view_response(...)
```

It returns an adapter wrapper:

- `available: true` with a validated `product_workspace` when a matching Teacher
  learning packet exists;
- `available: false` with explicit missingness when no matching Teacher packet
  exists.

The unavailable response deliberately does not fake a workspace. If the data
needed for Learn, Models, Relations, and Map is absent, the UI should show a
clear missingness state instead of placeholder lesson content.

## Adapted Surfaces

| Surface | Adapter source | Product-safe output |
| --- | --- | --- |
| Selected run summary | case id, result metadata, run health | `selected_run_summary` |
| Outcome | revised answer, delta card, compact Teacher model list | `outcome_summary` |
| Learn | Teacher lesson object | `learning_packet` |
| Models | Teacher model product objects | `model_page[]` |
| Relations | Teacher relation product objects | `relation_page[]` |
| Map | Teacher graph object | `graph_neighborhood` |
| Receipts | Teacher receipts plus Decision Work status | `receipt_summary` |
| Advanced Audit | result artifact presence plus Decision Work artifacts | `advanced_audit_index` |

## Important Translation Rules

The adapter keeps the single-home rules from the global Observatory design:

- revised answer stays in Outcome;
- Teacher reasoning move stays in Learn;
- canonical model explanation becomes Models;
- relation explanation becomes Relations;
- graph neighborhood becomes Map;
- source custody and process status become Receipts;
- raw telemetry remains Advanced Audit.

It also normalizes links into product routes:

```text
/models/<model_id>
/relations/<relation_id>
/runs/<case_id>#learn
```

That means graph edges can resolve to relation pages and model chips can resolve
to model pages without exposing raw review paths as the primary route.

## Missingness Handling

The adapter preserves missingness instead of filling absent product copy with
new claims.

Examples:

- if the selected result has no revised answer, Outcome says that the revised
  answer artifact is absent and marks `revised_answer` missing;
- if the current Teacher packet does not include a reasoning trap or worked
  example, Learn marks those fields missing;
- if no Decision Work sidecar is present, Receipts reports process brief status
  as `not_requested`;
- if no Teacher packet matches the selected case, the adapter returns
  `available: false` and no workspace.

## Boundary Guards

Each adapter response carries guard flags:

- `read_only: true`;
- `provider_or_model_calls: false`;
- `lolla_skill_invoked: false`;
- `new_lolla_run_created: false`;
- `runtime_behavior_changed: false`;
- `archive_mutated: false`;
- `ui_rendering_added: false`;
- `legacy_spa_or_bundle_touched: false`.

The adapter also validates the composed workspace through
`validate_workspace(...)`, so graph affinity/ranking fields, product proof
claims, local paths, and non-portable rendering directions are rejected before a
future renderer can consume the object.

## PR Stop Line

This PR stops before:

- adding an Observatory route for the workspace response;
- changing `/api/case/<id>`;
- root workspace rendering;
- rendering model pages or relation pages;
- graph UI work;
- archive writes;
- runtime integration;
- provider/model calls;
- Lolla invocation;
- new Lolla runs;
- legacy Svelte source changes;
- compiled bundle edits;
- product proof claims;
- human validation claims.

Recommended next gate:
`proceed_to_observatory_server_rendered_root_workspace`
