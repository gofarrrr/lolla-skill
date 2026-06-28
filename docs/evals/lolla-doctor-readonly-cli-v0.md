# Lolla Doctor Read-Only CLI v0

Status: PR57 code/tests/docs slice
Date: 2026-06-28
Owner: Lolla maintainers

PR57 implements the smallest local read-only doctor/preflight CLI planned in
PR56.

The doctor helps users and maintainers inspect local readiness before spending
tokens or running `$lolla`. It reports wiring, path, manifest, provider, cost,
and privacy/custody visibility. It does not judge answer quality and does not
approve any run for high-stakes use.

## Command Shape

Machine-readable JSON:

```bash
python3 scripts/lolla_doctor.py --archive-root ~/.local/share/lolla/runs --json
```

Optional manifest and external output:

```bash
python3 scripts/lolla_doctor.py \
  --archive-root ~/.local/share/lolla/runs \
  --manifest reviews/local/review-corpus-manifest.json \
  --json \
  --out /tmp/lolla_doctor_report.json
```

Optional explicit runtime root:

```bash
python3 scripts/lolla_doctor.py --runtime-root . --archive-root /tmp/lolla-runs --json
```

Default text mode prints a compact local summary. JSON mode is the stable
contract.

## Output Contract

Schema version:

```text
lolla.doctor_report.v0
```

High-level shape:

```json
{
  "schema_version": "lolla.doctor_report.v0",
  "status": "pass|warn|fail",
  "checks": [
    {
      "check_id": "runtime.discovery",
      "status": "pass|warn|fail|not_applicable",
      "summary": "Lolla runtime root is discoverable.",
      "details": {},
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
    "reads_manifest_json": false,
    "writes_archives": false,
    "model_calls": 0,
    "prints_secrets": false,
    "prints_raw_transcript": false,
    "prints_raw_memo": false,
    "prints_raw_revised_answer": false
  }
}
```

The report may inspect archive-root path metadata, but `reads_archives: false`
means it does not open run payload artifacts. If `--manifest` is supplied,
`reads_manifest_json` becomes `true`.

## Status Semantics

- `fail`: at least one blocking failure exists.
- `warn`: no blocking failures exist, but one or more warnings exist.
- `pass`: all applicable checks pass.
- `not_applicable`: a check is intentionally skipped because the relevant input
  was not supplied or the local mode does not use that surface.

The CLI exits with code `1` when the report status is `fail`, while still
rendering a deterministic report. It exits with `0` for `pass` or `warn`.

## Implemented Checks

| Check id | Purpose |
|---|---|
| `runtime.discovery` | Finds a Lolla runtime root from `--runtime-root`, the script location, current-directory parents, or common local skill locations. |
| `archive_root.discovery` | Checks whether an explicit or default archive root exists as a directory without reading run payloads. |
| `helper_scripts.availability` | Checks expected helper files exist without executing them. |
| `provider_config.presence` | Reports credential presence as booleans only. |
| `telemetry.cost_readiness` | Checks whether the configured OpenRouter model is known to the local pricing table. |
| `review_corpus.manifest_readable` | Parses an explicitly supplied review-corpus manifest as JSON object. |
| `risk_mode.reliance_counts` | Surfaces PR44 aggregate reliance count fields when present. |
| `high_stakes.evidence_visibility` | Reports high-stakes reliance-present count only when the manifest explicitly supports it. |
| `output.path_safety` | Rejects `--out` paths that resolve inside the archive root. |
| `archive_mutation.guard` | Records that doctor performs zero archive writes and no archive repair/backfill. |
| `repo_runtime.boundary` | Warns if `SKILL.md`, `engine`, `scripts`, or `observatory` are dirty in a git runtime root. |
| `privacy.output_safety` | Records that doctor output uses safe-to-print metadata only. |

## Read-Only Custody

PR57 preserves these boundaries:

- doctor is preflight only;
- doctor does not run `$lolla`;
- doctor does not call models;
- doctor does not load provider clients;
- doctor does not mutate archives;
- doctor does not execute helper scripts;
- doctor does not change prompts;
- doctor does not change `SKILL.md`;
- doctor does not change provider-boundary policy;
- doctor does not change `caller_action`;
- doctor does not approve high-stakes use;
- doctor does not judge answer quality;
- doctor only reports local readiness, custody, and config visibility.

## Privacy

Doctor output may include:

- statuses;
- schema names;
- relative or home-relative path hints;
- file names;
- provider/model names;
- booleans for credential presence;
- aggregate manifest counts.

Doctor output must not include:

- credential values;
- raw transcript text;
- raw memo text;
- raw revised-answer text;
- provider reasoning;
- private reasoning;
- checked-in local absolute archive paths.

## Blocking Failures

Current blocking examples:

- explicit runtime root is not found;
- runtime root is missing expected landmarks;
- required helper file is missing;
- explicit archive root is not a directory;
- explicit archive root points to a file;
- supplied manifest is malformed JSON;
- supplied manifest is not a JSON object;
- reliance count fields have invalid count shapes;
- output path resolves inside the archive root.

## Warnings

Current warning examples:

- provider credential is absent;
- no manifest is supplied;
- manifest lacks PR44 reliance fields;
- no high-stakes reliance-present evidence is visible;
- configured model is unknown to the local pricing table;
- runtime git boundary has local changes under checked runtime paths.

## Validation

PR57 validation:

```bash
python3 -m py_compile engine/system_b/lolla_doctor.py scripts/lolla_doctor.py tests/test_lolla_doctor.py
PYTHONPATH=. pytest -q tests/test_lolla_doctor.py
```

The PR57 tests cover stable JSON shape, deterministic archive-root failures,
output-path refusal inside archives, manifest parsing, PR44 reliance-count
visibility, malformed manifest failure, credential-value redaction, raw-content
exclusion, no provider-client import path, and external `--out` writes.

## Next Gate

The next approved slice after PR57 is:

```text
PR58 Audit Decision Record Design v0
```

PR58 should be docs/JSON design only. It should not implement an exporter,
change runtime behavior, run `$lolla`, call models, mutate archives, or create
high-stakes evidence.
