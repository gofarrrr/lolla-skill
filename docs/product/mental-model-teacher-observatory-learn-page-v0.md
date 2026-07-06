# Mental Model Teacher Observatory Learn Page v0

Status: first visible Observatory learning page
Date: 2026-07-06
Decision gate: `proceed_to_compiled_observatory_learn_tab_integration`

## Purpose

This slice gives the Teacher work a visible place inside Observatory without
rebuilding the compiled SPA bundle yet.

The page lives at:

```text
/teacher-learning
```

It uses the read-only Teacher packet adapter:

```text
/api/case/<id>/teacher-learning
```

It does not run Lolla. It does not invoke the Lolla skill. It does not call providers or model APIs, create new runs, mutate archives, judge answer quality, authorize action, or wire Lolla runtime behavior.

## User Experience

The page is intentionally narrative:

```text
case anchor -> thinking move -> model stack -> relation story -> practice rep
```

It then provides durable learning surfaces:

- model explanations;
- relation explanation;
- small graph neighborhood as navigation;
- receipts and missingness;
- non-claims.

This prevents the earlier failure mode where lesson text, telemetry, review
artifacts, source custody, graph data, and raw notes appeared as one undifferentiated
pile.

## Observatory Shell

The server-rendered Observatory nav now includes:

```text
Learn | Audit Index | Extraction | Memo | ... | Usage
```

The SPA root also receives a small `LEARN` affordance through the same
serve-time injection pattern as the existing `TELEMETRY` affordance. The bundle
on disk is not modified.

## Information Order

The page renders sections in this order:

1. Lesson;
2. Model stack;
3. Practice rep;
4. Do-not-overlearn boundary;
5. Models;
6. Relation;
7. Map;
8. Receipts;
9. Non-claims.

Relation explanation is shown before taxonomy details. Receipts are available
but do not compete with the lesson.

## What This Still Is Not

This is not the final compiled Observatory tab UI.

It is a portable server-rendered page, similar to `/audit` and `/usage`, so the
product can be reviewed before we touch the separate compiled SPA source.

## Stop Line

This PR stops before:

- compiled SPA changes;
- client-side tab switching;
- browser graph interaction;
- provider or model calls;
- live Lolla runs;
- runtime wiring;
- product proof claims;
- human validation claims;
- answer or advice correctness scoring;
- action authorization.

Recommended next gate:

```text
proceed_to_compiled_observatory_learn_tab_integration
```
