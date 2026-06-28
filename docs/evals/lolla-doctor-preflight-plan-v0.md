# Lolla Doctor / Preflight Plan v0

Status: PR56 docs-only plan
Date: 2026-06-28
Owner: Lolla maintainers

Implementation note: PR57 implements the smallest read-only CLI described here.
See `docs/evals/lolla-doctor-readonly-cli-v0.md`.

This plan defines a future read-only `lolla doctor` / preflight command. It
does not implement the command.

The purpose of the future doctor is narrow: help a user or maintainer verify
that local Lolla wiring is discoverable and safe enough to inspect before they
spend model tokens, run `$lolla`, export review data, or rely on high-stakes
readiness claims.

PR56 is documentation only. It adds no CLI, no runtime integration, no prompt
changes, no `SKILL.md` changes, no model calls, and no archive mutation.

## Problem

Lolla's product boundary is "probabilistic interpretation inside deterministic
custody." LLMs interpret messy conversations, generate audit pressure, and help
revise answers. Deterministic code preserves artifacts, validates schemas,
records run health, exports review data, and makes absence or presence visible.
Human reviewers decide whether the revised answer actually improved the
decision.

That architecture is useful only when the local wiring is legible before a run
starts. Today, a user can still reasonably worry about:

- wasting tokens because the skill or runtime is pointed at the wrong folder;
- discovering too late that the archive root was missing or mis-specified;
- misunderstanding provider-boundary, model, or cost behavior;
- relying on review-corpus manifests without seeing whether important counts
  are present, absent, old, or malformed;
- overclaiming high-stakes readiness when the corpus contains no real
  high-stakes reliance-present evidence;
- writing output into archive folders that should remain custody artifacts;
- printing private local content while trying to explain preflight state.

A doctor command should make those conditions visible before a user pays for a
run or mutates anything. It should answer "would the next run likely waste
tokens because the environment is miswired?" without becoming another runtime
surface.

## Inspiration

Semantica's `doctor` style is useful as a discipline: check local wiring,
surface missing pieces, and fail early before a costly pipeline starts.

Lolla should borrow that preflight discipline only. It should not copy
Semantica's broader graph, memory, governance, policy, ontology, or platform
scope. A Lolla doctor is a local deterministic readiness report for the Lolla
reasoning-audit harness, not a graph or governance subsystem.

## Future Command Shape

The first implementation should be boring and local. A possible PR57 entry
point is:

```bash
python3 scripts/lolla_doctor.py --archive-root ~/.local/share/lolla/runs --json
```

Optional future arguments could include:

```bash
python3 scripts/lolla_doctor.py \
  --archive-root ~/.local/share/lolla/runs \
  --review-manifest reviews/local/review-corpus-manifest.json \
  --output /tmp/lolla_doctor_report.json \
  --json
```

A later friendly alias could be:

```bash
lolla doctor --json
```

PR56 does not add any of these commands. It only defines the future contract.

## Read-Only Custody Rules

The future doctor must preserve these custody rules:

- It must not run `$lolla`.
- It must not call models.
- It must not execute extraction or audit pipeline helpers.
- It must not create, modify, delete, repair, or backfill archive files.
- It must not write output inside the archive root.
- It must not read raw transcripts, raw memos, raw revised answers, provider
  messages, or private ledgers.
- It may read filesystem metadata, environment-variable presence, selected repo
  paths, and explicitly supplied review-corpus manifest JSON.
- It may print path existence, sanitized path hints, file names, schema names,
  aggregate counts, and redacted configuration presence.
- It must never print credential values or private conversation content.

## Status Semantics

The future report should use four check statuses:

| Status | Meaning |
|---|---|
| `pass` | The check found the expected local wiring or safe absence state. |
| `warn` | The check found a non-blocking gap that could confuse a user, reduce inspectability, or make a future run less predictable. |
| `fail` | The check found a blocking condition that should stop a user before running `$lolla`, writing output, or trusting the environment. |
| `not_applicable` | The check was intentionally skipped because the user did not supply the relevant input or the local mode does not use that surface. |

Overall status should be deterministic:

- `fail` if any check has `status: "fail"`;
- `warn` if there are no failures but at least one warning;
- `pass` only if all applicable checks pass.

Warnings must not be hidden by an overall pass. Failures must explain the
blocking condition without printing private content.

## Planned Check Groups

| Check group | Future check id | Pass | Warn | Fail |
|---|---|---|---|---|
| Runtime discovery | `runtime.discovery` | The skill/runtime root is discoverable from the current repo or an explicit argument, and expected runtime landmarks exist. | Multiple plausible roots exist, or the discovered root is not the current repo but is still readable. | The runtime skill directory cannot be found or required landmarks are missing. |
| Archive root discovery | `archive_root.discovery` | The archive root argument or default location resolves to a directory, or the user explicitly asks for manifest-only mode. | No archive root is supplied and the default root is absent, but no archive-read check was requested. | The archive root argument points to a file, an unreadable path, or a path that cannot be resolved safely. |
| Helper script availability | `helper_scripts.availability` | Expected local helpers such as `scripts/skill/setup.sh`, `scripts/skill/run_extract_step.sh`, `scripts/skill/run_pipeline_step.sh`, `scripts/export_review_corpus.py`, and `scripts/analyze_review_corpus_evidence_readiness.py` are present. | Optional review/evidence helpers are absent, but the basic runtime helpers are present. | A required setup or runtime helper is missing. |
| Environment/provider configuration presence | `provider_config.presence` | Required provider-related environment variable names are present, reported only as present/absent. | Provider credentials are absent, but doctor is not running models and can still finish. | The only way to explain state would require printing a credential value; doctor must fail instead. |
| Model/provider/cost telemetry readiness | `telemetry.cost_readiness` | Cost and usage telemetry surfaces are inspectable, and configured provider/model names can be summarized without exposing credentials. | A configured provider/model is not recognized for cost estimation, or live-output health remains `not_checked`. | A supplied telemetry config is malformed in a way that prevents deterministic reporting. |
| Review-corpus export availability | `review_corpus.export_available` | The review-corpus export helper is present and discoverable. | The helper is absent or not executable, but no export is being run. | A required helper path is explicitly supplied and points to a file that cannot be read. |
| Review-corpus manifest readability | `review_corpus.manifest_readable` | An explicitly supplied manifest parses as JSON and exposes expected aggregate fields. | No manifest is supplied, or the manifest is old and lacks newer readiness/count fields. | An explicitly supplied manifest is malformed JSON or not a manifest object. |
| Risk-mode reliance counts visibility | `risk_mode.reliance_counts` | Manifest counts for `risk_mode_reliance.present` and reliance-check status are visible. | Counts are absent, so high-stakes reliance absence/presence cannot be summarized from that manifest. | Counts are present but use invalid shapes or non-numeric values. |
| High-stakes evidence absence/presence visibility | `high_stakes.evidence_visibility` | The report can state whether high-stakes reliance-present evidence is absent or present based on manifest counts. | No high-stakes evidence is present, or the manifest cannot support a readiness claim. | The manifest is supplied but too malformed to distinguish absence from unreadability. |
| Output path safety | `output.path_safety` | Output goes to stdout or to a resolved path outside the archive root. | No output path is supplied, so JSON is stdout-only. | The output path resolves inside the archive root or aliases an archive path. |
| Archive mutation guard expectations | `archive_mutation.guard` | The command plan and future implementation declare zero archive writes and no archive repair/backfill behavior. | The platform cannot prove read-only behavior for a custom wrapper, but the built-in command remains read-only. | The doctor would create, modify, delete, repair, backfill, or normalize archive files. |
| Repo/runtime boundary check | `repo_runtime.boundary` | The repo/runtime surface has no unexpected changes in `SKILL.md`, `engine`, `scripts`, or `observatory`. | The worktree has unrelated untracked docs or local review files outside the runtime boundary. | The runtime surface is dirty in a way that could change doctor or `$lolla` behavior. |
| Privacy/content safety of doctor output | `privacy.output_safety` | The report contains only safe-to-print metadata, path hints, file names, schema names, counts, statuses, and redacted presence flags. | A value is omitted or redacted because it is sensitive. | Doctor would need to print a credential value or raw conversation/revision content to explain state. |

## Output Contract Draft

The future JSON schema name should be:

```text
lolla.doctor_report.v0
```

Draft shape:

```json
{
  "schema_version": "lolla.doctor_report.v0",
  "status": "pass|warn|fail",
  "checks": [
    {
      "check_id": "runtime.discovery",
      "status": "pass|warn|fail|not_applicable",
      "summary": "Runtime root discoverable.",
      "details": {
        "safe_path_hint": "repo-relative or home-relative path only",
        "expected_landmarks_present": true
      },
      "safe_to_print": true
    }
  ],
  "summary": {
    "blocking_failures": 0,
    "warnings": 0,
    "model_calls": 0,
    "archives_mutated": false,
    "would_run_lolla": false,
    "would_spend_tokens": false
  },
  "custody_flags": {
    "reads_archives": false,
    "reads_archive_payloads": false,
    "reads_manifest_json": true,
    "writes_archives": false,
    "model_calls": 0,
    "prints_secrets": false,
    "prints_raw_transcript": false,
    "prints_raw_memo": false,
    "prints_raw_revised_answer": false
  }
}
```

`reads_archives: false` means the doctor does not open run payload artifacts or
scan raw archive contents. It may inspect archive-root path metadata and may
parse a manifest JSON file when the user supplies one. If PR57 needs a more
precise flag, it should add an additive field rather than weakening the
read-only rule.

Every `details` object must be safe to print. For paths, prefer repo-relative,
home-relative, or basename-only hints. For provider configuration, report only
presence, absence, provider/model names, and known/unknown cost-estimation
status.

## Blocking, Warning, And Passing Examples

Blocking failures:

- Runtime skill directory is not found.
- A required setup helper is missing.
- The archive-root argument points to a file.
- The output path would be inside the archive root.
- An explicitly supplied manifest is malformed JSON.
- The doctor would need to print a credential value to explain local state.

Warnings:

- Provider credentials are missing, but doctor is not running models.
- Review-corpus manifest is absent.
- No high-stakes evidence is present.
- The worktree has unrelated untracked docs.
- Live-output health is `not_checked`.
- The configured provider/model is not recognized for cost estimation.

Passing examples:

- Required local paths are discoverable.
- Expected helper scripts exist.
- Output path is outside the archive root.
- Review manifest aggregate counts parse.
- Risk-mode reliance counts are visible.
- No raw/private content appears in doctor output.

## Non-Goals

PR56 does not approve any of the following:

- `$lolla` runs;
- model calls;
- archive mutation;
- runtime integration;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- LLM judge work;
- answer-quality scoring;
- automatic labels;
- graph database work;
- embeddings;
- chunking;
- memory;
- policy engine work;
- Semantica-style platform work.

The future doctor must stay a deterministic readiness report. It must not become
an evaluator, judge, policy layer, governance system, archive repair tool,
runtime orchestrator, or high-stakes approval surface.

## PR57 Implementation

PR57 has implemented:

```text
python3 scripts/lolla_doctor.py
```

The implementation remains read-only, local, deterministic, and
model-call-free. It emits `lolla.doctor_report.v0`, writes only to stdout or an
explicit safe external `--out` path, and refuses `--out` inside the archive
root.

The next possible slice is:

```text
PR58 Audit Decision Record Design v0
```

PR58 should be docs/JSON design only and must not implement a decision-record
exporter.

Before extending doctor later, maintainers should confirm:

- the PR56 output contract is still the desired shape;
- the initial check list is small enough to implement without runtime drift;
- all doctor output remains privacy-safe;
- archive-root and output-path safety are tested;
- no implementation requires `$lolla`, model calls, prompt edits, `SKILL.md`
  edits, provider-boundary policy changes, or archive mutation.
