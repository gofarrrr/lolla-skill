# Decision Work Explicit Operator Sidecar Write Package Gate v0

Status: PR212 package gate
Date: 2026-07-04

Manifest:
[explicit operator sidecar write package manifest](decision-work-explicit-operator-sidecar-write-package-manifest-v0.json)

## Purpose

PR212 packages PR210 and PR211 as a narrow explicit operator sidecar write
capability.

This is a package gate. It does not write real historical archives, mutate
completed Lolla run folders, approve resolver refs, wire runtime, make runtime
attachment default-on, call providers/models, create workers, score answer
quality, claim product proof, claim human validation, validate advice
correctness, or authorize action.

## Narrow Explicit Operator Write v1 Claim

Decision Work Explicit Operator Sidecar Write v1 is functional as a controlled,
explicit, operator-directed sidecar write layer for safe fixture/operator target
directories. It uses validated PR202 sidecar update packets and matching PR206
dry-run results, writes sidecar-shaped files only under explicit safe
temp/output `decision_work` targets, and emits a fixture-only receipt.

That means the package can claim:

- a deterministic explicit operator write adapter exists;
- a fixture-only write receipt schema exists;
- launch-beta can produce `write_completed_fixture_only`;
- deploy-intake can produce `write_completed_blocked_state_fixture_only`;
- deploy-intake preserves runtime and user-surface blocking;
- generated sidecar-shaped files stay inside explicit safe target dirs;
- repo, archive-looking, and runtime-looking target paths are blocked;
- missing or mismatched dry-run inputs are blocked;
- privacy, provider-text, authority, proof, scoring, and action claims are
  blocked;
- review confirms the write layer remains fixture/operator output only.

It does not mean real archive mutation, runtime integration, resolver approval,
default-on behavior, arbitrary-run automation, customer readiness, product
proof, human validation, advice correctness, scoring, certification, or action
authorization.

## Functional Chain

The packaged explicit-operator write chain is:

```text
generated read
-> PR182 intake
-> PR186 brief supply
-> PR187 rendered brief
-> PR192 triage supply packet
-> PR193/PR195 generated triage read
-> PR198 resolver-supply candidate packet
-> PR202 sidecar update packet
-> PR206 sidecar write dry-run result
-> PR210 explicit operator fixture write
-> PR211 explicit operator fixture write review
```

The final artifact in this package is a fixture/output `decision_work`
directory and receipt. It is still not a real archive sidecar write and not
runtime sidecar availability.

## What Is Functional

Explicit Operator Sidecar Write v1 can:

- consume PR202 sidecar update packets;
- require matching PR206 dry-run results;
- write launch-beta fixture sidecar files;
- write deploy-intake blocked-state fixture sidecar files;
- preserve deploy-intake runtime and user-surface blocking;
- emit `lolla.decision_work_explicit_operator_sidecar_write_receipt.v0`;
- write only the PR209 allowed file set;
- reject archive-looking, runtime-looking, repo, relative, and non-temp target
  paths;
- reject privacy, local-path, provider-text, authority, proof, scoring, action,
  and real-write attempts;
- preserve that `real_archive_mutated`, `historical_archive_mutated`,
  `runtime_wiring_changed`, and `resolver_refs_approved` are false.

## What Remains Missing

Explicit Operator Sidecar Write v1 still does not provide:

- real historical archive writes;
- mutation of completed Lolla run folders;
- runtime wiring;
- post-archive hook integration;
- resolver approval;
- resolver refs marked usable;
- default-on behavior;
- production sidecar update automation;
- model calls;
- product proof;
- human validation;
- answer-quality scoring;
- advice-correctness validation;
- approval or certification;
- action authorization.

## Package Statuses

The package covers:

- `write_completed_fixture_only`;
- `write_completed_blocked_state_fixture_only`;
- `blocked_target_path_unsafe`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_not_matching_packet`;
- `blocked_packet_not_write_eligible`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_real_archive_path`;
- `blocked_runtime_path`;
- `failed_closed`.

## Fixture Target Safety

Writes are allowed only under an explicit caller-supplied safe temp/output
target named `decision_work`. The adapter blocks repo paths, archive-looking
paths, runtime-looking paths, non-absolute targets, and receipt outputs under
`decision_work`.

The fixture files are:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

These files are fixture/operator outputs only. They are not written into real
archive folders and cannot be treated as runtime sidecar availability.

## Boundary And Non-Claims

The package preserves these boundaries:

- fixture writes are not real historical archive writes;
- sidecar update packets are not approved refs;
- deploy-intake runtime and user-surface blockers travel forward;
- deterministic code may validate, normalize, copy safe refs, preserve
  blocked/deferred states, and write controlled fixture outputs;
- deterministic code must not infer new messy conversation meaning or decide
  the advice is correct;
- real archive mutation remains a separate future boundary.

## Validation Strategy

The package gate should be validated by:

- checking the package manifest schema;
- verifying every manifest-listed file exists;
- confirming forbidden paths are absent;
- running focused tests across PR178 through PR212;
- regenerating launch/deploy brief-supply, triage-supply, resolver-supply,
  sidecar-update, dry-run, and explicit write temp artifacts;
- confirming fixture sidecar files are written only under explicit safe
  `/tmp` or operator-output targets;
- parsing checked-in JSON artifacts and generated temp packets with `jq`;
- running Product Delta evidence boundary lint over touched docs/review JSON;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, raw/private-content, provider-text, and
  hidden-reasoning markers;
- confirming `SKILL.md`, `scripts/skill/*`, and runtime archive hooks remain
  untouched.

## Suggested Staging Pathspec

When this package is audited for a PR, use the manifest as the staging source
of truth. Do not stage broad directories.

Suggested shape:

```bash
git add -- $(python3 - <<'PY'
import json
from pathlib import Path

manifest_path = Path(
    "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-package-manifest-v0.json"
)
manifest = json.loads(manifest_path.read_text())
paths = []
for group in manifest["included_files"].values():
    paths.extend(group)
paths.append(str(manifest_path))
seen = set()
for path in paths:
    if path not in seen:
        seen.add(path)
        print(path)
PY
)
```

Then compare the staged set against the manifest-derived set before
committing.

## Decision Gate

Selected gate:

```text
explicit_operator_sidecar_write_v1_packaged
```

Recommended next PR:

```text
PR213 Controlled Archive Sidecar Write Fixture Plan v0
```

Do not implement PR213 from this package gate. The next phase must be a
plan/review gate for controlled archive-like fixture writes before any real
completed-run archive mutation is considered.

## Explicit Non-Claims

PR212 does not claim:

- runtime integration;
- default-on behavior;
- real archive mutation as normal behavior;
- arbitrary-run automation;
- resolver approval;
- approved resolver refs;
- resolver refs marked usable;
- user or customer readiness;
- production sidecar update automation;
- provider/model calls;
- queue workers or daemons;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent action authorization;
- automatic action authorization.
