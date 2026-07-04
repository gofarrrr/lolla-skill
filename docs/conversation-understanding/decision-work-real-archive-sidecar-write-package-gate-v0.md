# Decision Work Real Archive Sidecar Write Package Gate v0

Status: PR221 package gate
Date: 2026-07-04

Manifest:
[real archive sidecar write package manifest](decision-work-real-archive-sidecar-write-package-manifest-v0.json)

## Purpose

PR221 packages PR218 through PR220 as a narrow command-only real archive
sidecar write capability.

This is a package gate. It does not add runtime wiring, edit the archive hook,
make runtime attachment default-on, approve resolver refs, mark refs usable,
create queue workers, call providers/models, score answer quality, claim
product proof, claim human validation, validate advice correctness, certify
outputs, or authorize action.

## Narrow Real Archive Sidecar Write v1 Claim

Decision Work Real Archive Sidecar Write v1 is functional as a command-only,
explicit-operator, no-overwrite sidecar write layer for archive-markered
completed-run directories, validated against synthetic completed-run archive
directories.

That means the package can claim:

- a real archive write plan exists;
- a deterministic command-only write adapter and CLI exist;
- writes require explicit operator confirmation;
- writes require a matching PR202 sidecar update packet and PR206 dry-run
  result;
- writes require completed-run archive markers;
- writes refuse existing `decision_work/` sidecars in v1;
- launch-beta can produce `real_archive_sidecar_write_completed`;
- deploy-intake can produce `real_archive_sidecar_write_completed_blocked_state`;
- deploy-intake preserves runtime and user-surface blocking;
- only the PR209 allowed `decision_work/` file set is written;
- repo paths, missing archive markers, missing confirmation, mismatched
  packet/dry-run inputs, privacy markers, resolver approval, proof, scoring,
  and action claims are blocked;
- review confirms the adapter remains command-only and separate from runtime
  integration.

It does not mean runtime wiring, archive-hook integration, default-on behavior,
resolver approval, resolver refs marked usable, arbitrary-run automation,
customer readiness, product proof, human validation, advice correctness,
scoring, certification, or action authorization.

## Functional Chain

The packaged real archive sidecar write chain is:

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
-> PR219 command-only real archive sidecar write
-> PR220 real archive sidecar write review
```

PR221 packages that chain segment for Internal v1 planning. It does not
implement the PR222 operator runbook.

## What Is Functional

Real Archive Sidecar Write v1 can:

- consume PR202 sidecar update packets;
- require matching PR206 dry-run results;
- require explicit operator confirmation;
- require archive-markered completed-run target directories;
- write launch-beta sidecar files into a supplied archive directory;
- write deploy-intake blocked-state sidecar files into a supplied archive
  directory;
- preserve deploy-intake runtime and user-surface blocking;
- emit `lolla.decision_work_real_archive_sidecar_write_receipt.v0`;
- write only the PR209 allowed file set;
- refuse existing `decision_work/` sidecars;
- refuse missing archive markers, repo paths, broad paths, runtime-looking
  paths, missing dry-runs, packet/dry-run mismatches, privacy markers,
  local-path leaks, resolver approval, proof, scoring, and action claims;
- keep archive-hook edits, runtime wiring, resolver approval, resolver refs
  marked usable, proof, validation, scoring, advice-correctness, and action
  authorization false.

## What Remains Missing

Real Archive Sidecar Write v1 still does not provide:

- an end-to-end operator runbook;
- a current-state narrative refresh;
- runtime hook integration;
- post-archive hook integration;
- default-on runtime attachment;
- resolver approval;
- resolver refs marked usable;
- queue workers or daemons;
- production arbitrary-run automation;
- model/provider calls;
- product proof;
- human validation;
- answer-quality scoring;
- advice-correctness validation;
- approval or certification;
- agent or automatic action authorization.

## Package Statuses

The package covers:

- `real_archive_sidecar_write_completed`;
- `real_archive_sidecar_write_completed_blocked_state`;
- `blocked_operator_confirmation_missing`;
- `blocked_target_archive_invalid`;
- `blocked_archive_markers_missing`;
- `blocked_existing_decision_work_sidecar`;
- `blocked_target_path_unsafe`;
- `blocked_repo_path`;
- `blocked_packet_not_write_eligible`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_mismatch`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `failed_closed`.

## Target Safety

Writes are allowed only when a caller supplies an explicit completed-run
archive directory that passes archive-shape and marker checks. v1 refuses
existing sidecars by default. It also refuses repo source/docs/tests paths,
runtime-looking paths, broad parent directories, targets that point directly at
`decision_work/`, unsafe packet/dry-run inputs, and authority or privacy risks.

Validation for this package uses synthetic completed-run archive directories.
Generated sidecar files and write receipts are not checked into the repo.

## Boundary And Non-Claims

The package preserves these boundaries:

- command-only writes are not runtime integration;
- sidecar update packets are not approved resolver refs;
- deploy-intake runtime and user-surface blockers travel forward;
- deterministic code may validate, copy allowed fields, preserve refs/status,
  and write the allowed sidecar file set when explicit preconditions pass;
- deterministic code must not decide that advice is correct, that Lolla
  improved a decision, or that an agent may act;
- operator runbook and narrative refresh remain separate follow-up work.

## Validation Strategy

The package gate should be validated by:

- checking the package manifest schema;
- verifying every manifest-listed file exists;
- confirming forbidden paths are absent;
- running focused tests across PR178 through PR221;
- regenerating launch/deploy brief-supply, triage-supply, resolver-supply,
  sidecar-update, dry-run, and real archive sidecar write temp artifacts;
- confirming launch writes `real_archive_sidecar_write_completed`;
- confirming deploy writes `real_archive_sidecar_write_completed_blocked_state`;
- confirming deploy `attachment_status.json` preserves runtime/user-surface
  blocking;
- parsing checked-in JSON artifacts and generated temp packets with `jq`;
- running Product Delta evidence boundary lint over touched docs/review JSON;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, raw/private-content, provider-text, and
  hidden-reasoning markers;
- confirming `SKILL.md`, `scripts/skill/*`, and `scripts/archive_run.py`
  remain untouched.

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
    "decision-work-real-archive-sidecar-write-package-manifest-v0.json"
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

Then compare the staged set against the manifest-derived set before committing.

## Decision Gate

Selected gate:

```text
real_archive_sidecar_write_v1_packaged
```

Recommended next PR:

```text
PR222 Internal Demo / Operator Runbook v0
```

PR222 should explain the end-to-end operator flow and expected artifacts. It
should not wire runtime, edit archive hooks, approve resolver refs, default
anything on, call models, score, prove, certify, or authorize action.

## Implemented Follow-Up

PR222 implements the runbook as
[Decision Work Sidecar Internal v1 Operator Runbook](decision-work-sidecar-internal-v1-operator-runbook-v0.md).
It documents the internal operator command flow from generated read intake
through sidecar write receipt inspection and selects
`proceed_to_current_state_limitations_narrative_refresh` for PR223.

## Explicit Non-Claims

PR221 does not claim:

- runtime wiring;
- archive-hook integration;
- default-on behavior;
- resolver approval;
- resolver refs marked usable;
- automatic arbitrary-run semantic interpretation;
- queue worker behavior;
- customer/user-surface readiness;
- production automation;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent action authorization;
- automatic action authorization.
