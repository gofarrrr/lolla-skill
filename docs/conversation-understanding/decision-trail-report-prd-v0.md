# Decision Trail Report PRD v0

Status: PR86 design/schema contract
Date: 2026-06-29
Schema: `lolla.decision_trail_report.v0`

## Purpose

The Decision Trail report is a read-only process report for one completed Lolla
run. It is meant to travel beside, or sit near, the revised answer and explain
what process evidence exists around that answer:

- what conversation shape was captured;
- what decision question or likely action was visible;
- what audit pressure was applied;
- what changed structurally between the original and revised positions;
- what constraints, stakeholders, values, unresolved questions, and lost-value
  risks are visible;
- which fields are missing, redacted, private-only, malformed, unmeasured, or
  outside deterministic extraction.

The first version is deliberately conservative. It turns the existing artifact
chain into a report contract before any exporter exists.

## Problem

Lolla already creates useful artifacts: extraction output, audit cards, revised
answer, memo, `agent_result.json`, `evaluation.json`, `reasoning_trace.json`,
audit decision records, and offline Product Delta evidence. Those artifacts are
inspectable, but the user-facing story is scattered.

A person trying to decide whether to rely on a revised answer needs a compact
trail:

- what the answer was responding to;
- what the audit appears to have changed;
- what remains unresolved;
- which parts are first-class structured artifacts;
- which parts require messy interpretation by an LLM or a later reviewer;
- which parts are simply unavailable.

PR86 solves the design gap only. It defines the report and field ownership so
PR87 can implement a deterministic read-only exporter without inventing
semantics.

## What This Is Not

The Decision Trail report is not:

- the live Lolla runtime;
- a replacement for the revised answer or memo;
- an exporter implementation in PR86;
- a Product Delta review;
- an audit decision record clone;
- human validation;
- product proof;
- answer-quality scoring;
- an LLM judge;
- automatic labeling;
- agent action authorization;
- graph DB, memory, embeddings, chunking, or GraphRAG;
- proof that clean artifacts mean good advice.

The report is a custody and reporting surface. It can make thinness visible. It
must not make thinness look like certainty.

## Relationship To Existing Surfaces

| Surface | Relationship |
| --- | --- |
| Runtime | The runtime produces completed artifacts. The Decision Trail lane reads completed artifacts later. PR86 does not change runtime flow. |
| Revised answer | The report may point to the revised answer artifact, but checked-in safe mode must not copy the raw revised answer text. |
| Memo | The report may point to the memo artifact, but checked-in safe mode must not copy raw memo text. |
| `agent_result.json` | Supplies compact run health, caller-action posture, changed-advice summaries, take-backs, and human questions when present. The report must not convert those into reliance authorization. |
| `evaluation.json` | Supplies deterministic artifact/schema/custody/health status. It does not evaluate advice quality. |
| `reasoning_trace.json` | Supplies run-local custody pointers, artifact hashes, case metadata, trace adequacy, and source references without duplicating raw transcript text. |
| Audit decision record | Provides the strongest local pattern for status, empty meaning, source refs, and non-claims. The Decision Trail report borrows those patterns but covers a broader answer-plus-process story. |
| Product Delta | Studies whether Lolla changed strong-model answers in useful ways across cases. The Decision Trail explains one run. It may later point to Product Delta review artifacts when present, but it must not claim Product Delta proof. |
| Evaluation lane | Provides read-only lint and packaging patterns. PR86 uses those boundary patterns for schema tests and docs linting. |

## Field Ownership

Field ownership is part of the product. Every semantic section in the schema
has an `owner` and must say whether it requires LLM interpretation.

Recommended owner values:

- `deterministic_exporter`: artifact presence, schema versions, hashes,
  structured source refs, report mode, custody flags, malformed/missing status,
  and mechanical validation state.
- `existing_llm_runtime_artifact`: interpretation already produced by the
  current Lolla runtime, such as compact extraction fields or audit card text.
- `product_delta_review_artifact`: provisional offline review material when a
  report points to an existing Product Delta artifact.
- `future_llm_specialist`: semantic fields that need a bounded interpretive
  read before they can be honestly populated.
- `future_human_review`: fields whose authority belongs to a later reviewer,
  especially usefulness, lost value, values/priorities, stakeholder obligations,
  and reliance decisions.
- `mixed_sources`: fields assembled from multiple structured artifacts without
  creating new interpretation.
- `not_supplied`: fields intentionally left empty because no source is present.

Deterministic code owns custody. It does not own messy interpretation.

## Semantic Section Contract

Every semantic section supports the same core fields:

- `status`;
- `source_status`;
- `source_refs`;
- `value` or `items`;
- `empty_meaning`;
- `owner`;
- `requires_llm_interpretation`;
- `exporter_inferred_from_prose`.

The key rule is simple: if deterministic code cannot copy a value from a
structured artifact, it must preserve missingness or point to the source that
already supplied the interpretation. It must not read messy prose and decide
what the user values, which option is live, which friction is useful, what was
lost, who has obligations, what the likely next action is, or whether the answer
is good.

The shared status vocabulary is:

- `not_supplied`;
- `not_measured`;
- `not_applicable`;
- `available_from_structured_artifact`;
- `available_from_review_artifact`;
- `available_but_redacted_in_safe_mode`;
- `available_in_private_artifact_not_exported`;
- `requires_llm_interpretation`;
- `unavailable_missing_artifact`;
- `unavailable_malformed_artifact`;
- `unclear`.

These statuses are intentionally more important than a polished report. A sparse
honest report is better than a full report that silently guessed.

## Checked-In Safe Mode And Local Private Mode

The schema supports three report modes:

- `checked_in_safe_mode`;
- `local_private_mode`;
- `future_runtime_mode_not_implemented`.

`checked_in_safe_mode` is for committed docs, fixtures, and review artifacts. It
must exclude raw transcript text, raw memo text, raw revised-answer text,
provider text, private reasoning, local absolute paths, secrets, and private
local content. It may include paths relative to a run, schema versions,
artifact statuses, hashes, source refs, and conservative summaries already
present in structured artifacts.

`local_private_mode` is for future local operator use. It may read more private
local artifacts when explicitly requested by the operator, but the generated
report remains read-only and must still record custody flags honestly. Local
private output should not be checked in.

`future_runtime_mode_not_implemented` reserves vocabulary for a possible later
runtime-generated report. PR86 and PR87 do not implement that mode.

## Redaction Versus Missingness

Redaction and missingness must be different states.

`unavailable_missing_artifact` means the source artifact was not present.

`unavailable_malformed_artifact` means the source artifact existed but could
not be parsed or trusted structurally.

`not_supplied` means the artifact chain did not supply that field.

`not_measured` means the current system does not measure that field.

`available_but_redacted_in_safe_mode` means the source may exist but the report
mode cannot expose it.

`available_in_private_artifact_not_exported` means a local private artifact may
contain the material, but this report did not export it.

The exporter must prefer these distinctions over flattening every empty field
to `null` or `[]`.

## Trace Context

The schema includes optional future-compatible trace fields:

- `trace_context.status`;
- `trace_context.source_refs`;
- `trace_context.external_trace_id`;
- `trace_context.otel_genai_semconv_status`;
- `source_artifacts[*].activity_kind`;
- `source_artifacts[*].generated_by`;
- `source_artifacts[*].used_by`.

Allowed trace statuses:

- `not_used`;
- `future_compatible`;
- `experimental_mapping`.

These fields do not adopt OpenTelemetry, OpenInference, OpenAI Agents tracing,
or any external tracing package. They leave a small mapping surface for later
interop if it becomes useful. PR86 adds no dependency.

## Why Deterministic Code Must Not Fill Messy Fields

The Decision Trail is useful only if readers can see the difference between
custody and interpretation.

Deterministic code may preserve:

- artifact presence;
- schema versions;
- hashes;
- source references;
- source status;
- report mode;
- custody flags;
- malformed/missing state;
- validation results;
- explicit non-claims;
- structured values already produced by existing artifacts.

Deterministic code must not infer from messy prose:

- user values or priorities;
- live option status;
- useful versus noisy friction;
- lost value;
- stakeholder obligations;
- likely next action;
- assistant influence;
- answer quality;
- Product Delta usefulness.

Those fields need either an existing structured source, a bounded LLM
interpretation step in a later PR, or human review. Otherwise the report should
say `requires_llm_interpretation`, `not_supplied`, or `not_measured`.

## Expected PR87 Exporter Behavior

PR87 should implement a deterministic read-only exporter at a design level like
this:

1. Accept a completed run directory and explicit output path outside the run
   directory.
2. Read only custody-safe structured artifacts by default:
   `agent_result.json`, `evaluation.json`, `reasoning_trace.json`, extraction
   adequacy reports, and optional existing review artifacts supplied by path.
3. Record every expected source artifact as present, missing, malformed,
   redacted, or not read.
4. Populate only structured fields that already exist.
5. Mark semantic gaps with the shared status vocabulary and `empty_meaning`.
6. Set `exporter_inferred_from_prose: false` for deterministic population.
7. Preserve `model_calls: 0`, `archive_mutated: false`,
   `runtime_invoked: false`, and `skill_invoked: false`.
8. Write a report that validates against `decision-trail-report-v0.json`.

PR87 should not run `$lolla`, invoke the skill, call providers, mutate archives,
change prompts, add review fixtures beyond a tiny safe fixture if needed, add
model calls, add a judge, score answers, create automatic labels, or make agent
reliance decisions.

## Validation

PR86 validation should include:

- `jq . docs/conversation-understanding/decision-trail-report-v0.json`;
- focused schema/contract tests if a test file is added;
- Product Delta boundary lint over the PR86 docs/schema;
- `git diff --check`;
- local Markdown link check over touched Markdown;
- trailing whitespace scan over touched files;
- privacy/content marker scan over touched docs, JSON, and tests.

These checks validate contract hygiene. They do not validate product usefulness.

## Non-Claims

A valid Decision Trail report does not claim:

- the advice is good;
- the answer is safe to rely on;
- a human reviewed the run;
- a judge calibrated the result;
- Product Delta evidence proves the case;
- empty fields mean no issue exists;
- clean custody means good advice;
- the runtime generated this report today.

The report can make review easier. It cannot replace review.

## PR86 Done State

PR86 is complete when the repo contains:

- this PRD;
- `docs/conversation-understanding/decision-trail-report-v0.json`;
- focused schema tests, if useful;
- light discoverability links in the existing docs.

The next recommended PR is PR87: Decision Trail Read-Only Exporter v0.
