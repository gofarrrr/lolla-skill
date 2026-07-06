# Observatory Conversation Understanding Boundary v0

Status: design contract
Date: 2026-07-06
Decision gate: `proceed_to_observatory_decision_work_sidecar_status_adapter`

## Purpose

This slice answers a narrow product and architecture question before more
Observatory UX work:

```text
What conversation-understanding material already exists, what runs
automatically today, and how should Observatory present it without becoming
another everything-at-once telemetry wall?
```

The finding is conservative:

- live conversation capture and compact extraction are already part of the
  normal run path;
- richer Decision Work / Decision Trail conversation interpretation exists as
  offline, operator-driven, default-off machinery;
- Observatory should first expose Decision Work availability, receipts,
  blockers, and non-claims read-only;
- Observatory should not trigger semantic interpretation, write sidecars, call
  providers, run Lolla, or change runtime behavior from this product surface.

This does not run Lolla.
It does not invoke the Lolla skill.
It does not call providers or model APIs.
It does not create new runs, mutate archives, judge answer quality, authorize
action, or wire Lolla runtime behavior.

## Short Verdict

The user's intuition is mostly right, but there are two different systems that
must not be collapsed:

| Layer | Current state | Product meaning |
| --- | --- | --- |
| Live extraction | Already part of the normal run path | Captures and preserves a compact decision-context summary for the run |
| Observatory extraction audit | Already present at `/audit/extraction` | Lets a reviewer inspect extraction custody, warnings, quote validation, and missingness |
| Decision Trail report shell | Offline/read-only exporter | Can package a sparse custody-first report from structured archive artifacts |
| Decision Work sidecar chain | Offline/operator-driven internal v1 | Can attach validated Decision Work receipts to a completed-run archive through explicit operator steps |
| Post-archive Decision Work attachment hook | Implemented but default-off | Only runs when `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is explicitly enabled |

So the missing Observatory piece is not basic extraction. The missing piece is a
clear, user-comprehensible status surface for richer conversation
understanding:

```text
Was richer Decision Work requested?
Is it available, deferred, blocked, or absent?
What receipt can I read?
What is missing?
What should I not infer from it?
```

## Terms

### Conversation Capture

The raw captured conversation is the source material for a run. It is private
runtime material and should not become normal product copy.

### Live Extraction

Live extraction is the compact semantic extraction that normal runs already
use. It produces fields such as decision situation, live constraints,
synthesized position, reasoning passages, original framing, dropped threads,
capture adequacy, and quote validation.

Live extraction helps the system understand the current case. It is not a
complete customer-facing decision story.

### Conversation IR

The provenance-aware conversation IR can represent turns, spans, turn
references, frame anchors, user issue events, stance events, derivations, and
source provenance. The current production path remains conservative and does
not automatically turn every run into a rich decision story.

### Decision Trail

Decision Trail is the desired product story of how the conversation became a
decision artifact:

- what the user was deciding;
- which constraints and options were live;
- what the assistant accepted or pushed on;
- what changed between the initial and revised answer;
- what remains unresolved.

The current Decision Trail exporter is read-only and sparse in checked-in safe
mode. It does not infer missing semantic fields from private prose.

### Decision Work Sidecar

The Decision Work sidecar is an archive-adjacent record that can preserve a
validated Decision Work brief, user receipt, agent handoff packet, safe supply
summary, update packet, and write receipt.

Internal v1 is command-only, explicit-operator, no-overwrite, and not
default-on runtime behavior.

### Teacher Learn

Teacher Learn asks:

```text
What reasoning move can the user learn from this run?
```

Decision Work asks:

```text
What decision context and artifact trail should be preserved for this run?
```

Those surfaces may link to each other, but they should not duplicate or rename
each other.

## Current Flow

### What Runs Today

The current live flow already includes conversation extraction:

```text
captured conversation
  -> scripts/skill/run_extract_step.sh
  -> scripts/run_extract.py
  -> extraction.json
  -> engine/system_b/conversation_loader.py
  -> ConversationContext
  -> audit/runtime artifacts
  -> archive
```

`observatory/serve_result.py` already has the advanced extraction route:

```text
/audit/extraction
```

That route renders extraction sidecar information, capture manifest details,
capture warnings, quote validation, live constraints, reasoning passages, and
dropped threads.

### What Does Not Run Automatically

The richer Decision Work path is not automatic for every skill run.

Current richer pieces include:

- `engine/system_b/decision_trail_report.py`;
- `engine/system_b/decision_work_brief_runtime_attachment.py`;
- offline Decision Work packet, intake, brief, triage, resolver, dry-run, and
  explicit sidecar-write modules;
- `docs/board/decision-work-sidecar-internal-v1-current-state.md`.

The runtime attachment hook is intentionally default-off. It only proceeds when
the environment explicitly enables:

```text
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE
```

When the flag is absent, the hook returns `not_requested` and writes no
Decision Work sidecar.

## Product Decision

Observatory remains the single post-run shell.

Conversation understanding should appear as a status and receipt layer inside
Observatory, not as a second app and not as another raw telemetry dump.

The first user-facing implementation should be:

```text
Selected run
  -> Receipts
  -> Conversation Understanding / Decision Work status
```

The section should answer:

1. What conversation-understanding artifacts exist for this run?
2. Is live extraction available?
3. Is a richer Decision Work sidecar present?
4. If absent, was it not requested, deferred, blocked, or unavailable?
5. If present, what safe receipt can the user read?
6. What missingness and non-claims travel with it?
7. Where can a technical reviewer inspect the advanced extraction audit?

This makes the missing piece visible without pretending it was generated.

## Information Architecture

### Primary Homes

| Information | Product home | May link from | Do not duplicate as |
| --- | --- | --- | --- |
| Revised answer | Outcome | Receipts, memo | Decision Work proof |
| Live extraction custody | Advanced `/audit/extraction` | Receipts | Teacher lesson copy |
| Compact case context | Outcome summary and Learn case anchor | Receipts | full raw conversation |
| Rich Decision Work receipt | Receipts / Conversation Understanding | Outcome status chip | Teacher lesson body |
| Teacher reasoning move | Learn | Outcome, Models, Relations | Decision Work brief |
| Canonical model explanation | Models | Learn, Relations, Map | extraction telemetry |
| Relation explanation | Relations | Learn, Map | graph edge proof |
| Sidecar health and blockers | Receipts | Advanced telemetry | product certification |

### First-Class Data In The New Section

The first Decision Work / Conversation Understanding section should present:

- availability state;
- source artifact status;
- attachment state;
- human-readable user receipt when present;
- blockers and deferred reasons;
- missingness;
- non-claims;
- links to `/audit/extraction` and raw sidecar inspection.

### Second-Class Data

The section may expose, behind inspectable details:

- `decision_work/attachment_status.json`;
- `decision_work/safe_supply_summary.json`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/sidecar_write_receipt.json`;
- `decision_work/user_receipt.md`;
- extraction adequacy status;
- quote validation status.

### Internal-Only Data

The section must not present as normal product copy:

- raw conversation text;
- local absolute archive paths;
- operator logs;
- private generated reads;
- raw Product Delta eval internals;
- raw provider text;
- raw routing internals;
- answer-quality or advice-correctness labels;
- resolver approval claims;
- agent or automatic action authorization.

## Proposed Observatory Shape

### Receipts Section

Add a `Conversation Understanding` block to Receipts:

```text
Conversation Understanding

Live extraction: available
Decision Work: not requested / deferred / blocked / available
Receipt: open when present
Missing: richer semantic read, resolver approval, human review
Non-claims: not proof, not validation, not action authorization
Inspect: /audit/extraction, sidecar files
```

This should be a product-readable status card, not a JSON dump.

### Selected-Run Custody Panel

The existing selected-run custody panel should add a Decision Work entry:

```text
decision_work/
```

Suggested safe files:

- `decision_work/attachment_status.json`;
- `decision_work/user_receipt.md`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/safe_supply_summary.json`;
- `decision_work/sidecar_write_receipt.json`.

If the directory is absent, the panel should say `not present` or
`not requested`, not `failed`.

### API

The first code slice should add a read-only selected-run endpoint:

```text
/api/case/<id>/decision-work
```

The endpoint should return only safe summary fields:

```json
{
  "schema_version": "lolla.observatory_decision_work_status.v0",
  "case_id": "...",
  "decision_work_status": "not_requested",
  "live_extraction_status": "available",
  "source_artifacts": [],
  "receipt": null,
  "blockers": [],
  "missingness": [],
  "links": {},
  "non_claims": {}
}
```

It should read existing archive sidecars only. It should not create sidecars,
run the offline operator, call providers, or invoke Lolla.

### Advanced Audit Route

A later slice may add:

```text
/audit/decision-work
```

That route should remain an inspection surface, similar to `/audit/extraction`.
It should not be the first place a normal user is sent.

## State Model

Use simple state labels that a user can understand:

| State | Meaning | User copy direction |
| --- | --- | --- |
| `live_extraction_available` | The normal run extraction exists | "The run has captured case context." |
| `decision_work_not_present` | No `decision_work/` sidecar exists | "No richer Decision Work receipt is attached." |
| `decision_work_not_requested` | Default-off hook or operator path was not requested | "This run did not request richer Decision Work." |
| `decision_work_deferred` | Inputs are missing or not ready | "A richer receipt is deferred until safe inputs exist." |
| `decision_work_blocked` | Privacy, risk, mismatch, or blocker state | "A richer receipt is blocked and should not be shown as available." |
| `decision_work_available` | Safe sidecar and receipt exist | "A Decision Work receipt is available for inspection." |
| `decision_work_failed_closed` | Hook failed in non-blocking mode | "The optional attachment failed closed; runtime output is not blocked." |

Do not use approval, certification, correctness, or readiness labels.

## Relation To Teacher Learn

Teacher Learn should be allowed to use compact case context as an anchor, but
it should not become a Decision Work surface.

Teacher should show:

```text
case anchor -> reasoning move -> model relationship -> practice rep
```

Conversation Understanding should show:

```text
captured context -> extraction status -> optional Decision Work receipt -> missingness
```

This prevents one tab from mixing teaching content, telemetry, raw sidecars,
and review artifacts in the same visual stack.

## Recommended PR Sequence

### PR-CU1

Document and validate the Observatory conversation-understanding boundary.

Stop before code changes.

### PR-CU2

Add a read-only Decision Work status adapter for selected runs.

Expected output:

- helper that detects `decision_work/` sidecar files;
- `/api/case/<id>/decision-work`;
- tests for absent, deferred, blocked, available, and malformed sidecars;
- no sidecar writes;
- no runtime hook changes.

Stop before UI rendering.

### PR-CU3

Add the Decision Work status to the selected-run custody panel and Receipts
surface.

Expected output:

- product-readable status card;
- links to `/audit/extraction`;
- links to available sidecar files;
- visible non-claims;
- no semantic generation.

Stop before first-class Decision Trail UX.

### PR-CU4

Render existing `decision_work/user_receipt.md` read-only when present.

Expected output:

- receipt display;
- blocker display;
- missingness display;
- clear distinction from Teacher Learn and Outcome.

Stop before generating receipts.

### PR-CU5

Only after review, design whether a first-class `Decision Trail` mode belongs
beside Outcome and Learn.

This must remain blocked until richer semantic supply is validated for arbitrary
runs without product-proof, human-validation, correctness, or action claims.

## Stop Line

This boundary stops before:

- running `$lolla`;
- invoking the Lolla skill;
- provider or model API calls;
- new Lolla runs;
- runtime wiring;
- archive mutation;
- automatic semantic interpretation;
- automatic sidecar writes;
- queue workers;
- resolver approval;
- human validation;
- product proof;
- answer-quality scoring;
- advice-correctness scoring;
- approval or certification labels;
- agent or automatic action authorization;
- treating Decision Work as Teacher Learn;
- treating extraction as a complete Decision Trail.

Recommended next gate:

```text
proceed_to_observatory_decision_work_sidecar_status_adapter
```
