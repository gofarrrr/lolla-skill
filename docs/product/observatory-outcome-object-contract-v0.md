# Observatory Outcome Object Contract v0

Status: product view contract implemented.

Date: 2026-07-07

Decision gate: `proceed_to_outcome_first_viewport_redesign`

Related planning doc:
[Observatory Outcome User Value PRD](observatory-outcome-user-value-prd-v0.md)

Related contract bundle:
[Observatory portable product view contract examples](observatory-portable-product-view-contract-examples-v0.json)

## Purpose

This slice turns the browser-grounded Outcome complaint into a concrete
product-view object:

```text
outcome_value
```

The current Outcome page already has a compact `outcome_summary`, but that
shape is too thin for the first screen. It can show a headline, clipped answer,
hidden pressure, and model chips. It cannot carry the full user answer, why the
answer changed, what reasons matter, what would change confidence, and what the
user should inspect next.

`outcome_value` is the stronger contract the next UI slice should render.

## Product Job

Outcome should answer:

```text
What did the run conclude, why, what changed, what should I inspect next,
and what would change confidence?
```

It should not become:

- the Learn lesson;
- the model library;
- the relation taxonomy;
- the graph surface;
- the receipts inventory;
- the raw audit console.

## Contract Fields

Required fields:

- `schema_version`;
- `run_id`;
- `case_id`;
- `outcome_headline`;
- `stance`;
- `plain_language_answer`;
- `what_changed`;
- `primary_reasons`;
- `confidence_boundary`;
- `recommended_next_moves`;
- `source_refs`;
- `missingness`;
- `non_claims`.

The object is validated by:

```text
observatory/product_views.py::validate_outcome_value
```

It is built read-only by:

```text
observatory/product_view_adapters.py
```

## Data Mapping

| Product field | Source | User value | If missing |
| --- | --- | --- | --- |
| `plain_language_answer` | `result.revised_answer` | Shows the actual run answer without clipping it into a card. | Say the revised answer artifact is absent. |
| `outcome_headline` | first complete answer sentence | Gives the user the result before details. | Say no revised answer artifact is available. |
| `stance` | deterministic label from answer wording | Helps UI style the answer as hold, stage, gated launch, or unknown. | Use `missing_revised_answer`. |
| `what_changed` | `memo_what_changed`, change-reason fields, then strongest pressure | Explains why the result moved or what pressure mattered. | Name the absent change artifact. |
| `primary_reasons` | full revised answer sentences, then strongest pressure | Gives the user reasons without opening Advanced Audit. | Name the missing reason artifact. |
| `confidence_boundary` | answer sentences containing evidence, risk, gate, readiness, support, diligence, or confidence terms | Tells the user what would change the conclusion or where reliance is bounded. | Name the missing confidence-boundary artifact. |
| `recommended_next_moves` | fixed portable routes | Sends the user to Learn, Receipts, or Download MD for the right next job. | Still present, because navigation routes are deterministic. |
| `source_refs` | portable selected-run result reference | Preserves custody without exposing local paths. | Validator rejects empty refs. |
| `missingness` | deterministic adapter notes | Keeps absent artifacts visible instead of hidden behind ceremony. | Validator rejects missing state. |
| `non_claims` | common Observatory non-claims | Prevents Outcome from looking like proof, validation, correctness scoring, or action authorization. | Validator rejects missing non-claims. |

## What This Means For The Page

The next Outcome UI should start with:

1. the selected case/run context;
2. `outcome_value.outcome_headline`;
3. `outcome_value.plain_language_answer`;
4. `outcome_value.what_changed`;
5. `outcome_value.primary_reasons`;
6. `outcome_value.confidence_boundary`;
7. two or three next moves.

The current reading-path panels, duplicate navigation cards, run inventory, and
status chips should move below the result or into their proper surfaces.

## Stop Line

This PR stops before:

- Outcome page rendering;
- first-viewport layout changes;
- root workspace navigation changes;
- graph UI changes;
- runtime integration;
- provider/model calls;
- Lolla invocation;
- new Lolla runs;
- archive mutation;
- `SKILL.md`;
- `scripts/skill/*`;
- `scripts/archive_run.py`;
- `observatory/build/*`.

## Non-Claims

This contract does not claim:

- product proof;
- human validation;
- answer correctness;
- advice correctness;
- runtime integration authorization;
- action authorization;
- graph edge proof;
- embedding-similarity validation.

In particular, it does not claim answer correctness or advice correctness. The
object organizes what the run already produced; it does not certify that the
answer is right.

## Recommended Next PR

`PR-O2 Outcome First Viewport Redesign`

Use `outcome_value` as the source of truth for the center Outcome surface. Keep
`outcome_summary` only as a compact compatibility object until the old layout
no longer needs it.
