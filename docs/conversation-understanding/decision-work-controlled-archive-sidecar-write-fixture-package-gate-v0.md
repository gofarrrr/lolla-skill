# Decision Work Controlled Archive Sidecar Write Fixture Package Gate v0

Status: PR216 package gate
Date: 2026-07-04

Manifest:
[controlled archive sidecar write fixture package manifest](decision-work-controlled-archive-sidecar-write-fixture-package-manifest-v0.json)

## Purpose

PR216 packages PR213 through PR215 as a narrow controlled archive-shaped
fixture capability.

This is a package gate. It does not write real historical archives, mutate
completed Lolla run folders, edit the archive hook, wire runtime, make runtime
attachment default-on, approve resolver refs, call providers/models, create
workers, score answer quality, claim product proof, claim human validation,
validate advice correctness, or authorize action.

## Narrow Controlled Archive Fixture v1 Claim

Decision Work Controlled Archive Sidecar Write Fixture v1 is functional as a
synthetic archive-shaped fixture write layer. It can write the PR209 allowed
sidecar file set into controlled temp/operator fixture directories that
intentionally resemble completed-run archive layout, using validated PR202
sidecar update packets and matching PR206 dry-run results.

That means the package can claim:

- a deterministic controlled archive-shaped fixture adapter exists;
- a fixture receipt schema exists;
- launch-beta can produce `fixture_write_completed`;
- deploy-intake can produce `fixture_write_completed_blocked_state`;
- deploy-intake preserves runtime and user-surface blocking;
- generated sidecar-shaped files stay inside explicit safe fixture dirs;
- repo, runtime, real archive-looking, and existing historical archive target
  paths are blocked;
- missing or mismatched dry-run inputs are blocked;
- privacy, provider-text, authority, proof, scoring, and action claims are
  blocked;
- review confirms the write layer remains synthetic fixture output only.

It does not mean real archive mutation, runtime integration, archive-hook
integration, resolver approval, default-on behavior, arbitrary-run automation,
customer readiness, product proof, human validation, advice correctness,
scoring, certification, or action authorization.

## Functional Chain

The packaged controlled archive fixture chain is:

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
-> PR212 explicit operator sidecar write package
-> PR214 synthetic archive-shaped fixture write
-> PR215 synthetic archive-shaped fixture review
```

The final artifact in this package is a synthetic archive-shaped fixture
directory with a `decision_work` child directory and receipt. It is still not a
real archive sidecar write and not runtime sidecar availability.

## What Is Functional

Controlled Archive Sidecar Write Fixture v1 can:

- consume PR202 sidecar update packets;
- require matching PR206 dry-run results;
- write launch-beta synthetic archive-shaped fixture sidecar files;
- write deploy-intake blocked-state synthetic archive-shaped fixture sidecar
  files;
- preserve deploy-intake runtime and user-surface blocking;
- emit `lolla.decision_work_controlled_archive_sidecar_write_fixture.v0`;
- write only the PR209 allowed file set;
- reject repo, runtime, real archive-looking, existing historical archive,
  relative, and non-temp target paths;
- reject privacy, local-path, provider-text, authority, proof, scoring, action,
  and real-write attempts;
- preserve that `real_archive_mutated`, `historical_archive_mutated`,
  `archive_hook_changed`, `runtime_wiring_changed`, and
  `resolver_refs_approved` are false.

## What Remains Missing

Controlled Archive Sidecar Write Fixture v1 still does not provide:

- real historical archive writes;
- mutation of completed Lolla run folders;
- archive-hook integration;
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

- `fixture_write_completed`;
- `fixture_write_completed_blocked_state`;
- `blocked_real_archive_path`;
- `blocked_repo_path`;
- `blocked_existing_archive_path`;
- `blocked_target_path_unsafe`;
- `blocked_packet_not_write_eligible`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_mismatch`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `failed_closed`.

## Fixture Target Safety

Writes are allowed only under an explicit caller-supplied safe temp/operator
fixture root that has archive shape and an explicit fixture marker. The adapter
blocks repo paths, runtime-looking paths, real archive-looking paths without a
fixture marker, existing historical archive paths, non-absolute targets, and
untrusted existing `decision_work` contents.

The fixture files are:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

These files are synthetic fixture outputs only. They are not written into real
archive folders and cannot be treated as runtime sidecar availability.

## Boundary And Non-Claims

The package preserves these boundaries:

- synthetic archive-shaped fixture writes are not real historical archive
  writes;
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
- running focused tests across PR178 through PR216;
- regenerating launch/deploy brief-supply, triage-supply, resolver-supply,
  sidecar-update, dry-run, explicit write, and controlled archive fixture temp
  artifacts;
- confirming fixture sidecar files are written only under explicit safe `/tmp`
  or operator-output synthetic fixture targets;
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
    "decision-work-controlled-archive-sidecar-write-fixture-package-manifest-v0.json"
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
controlled_archive_sidecar_write_fixture_v1_packaged
```

Recommended next PR:

```text
PR217 Real Archive Sidecar Write Plan v0
```

Do not implement PR217 from this package gate. The next phase must be a
plan/review gate for real archive sidecar writes before any completed-run
archive mutation is considered.

## Explicit Non-Claims

PR216 does not claim:

- real historical archive writes;
- mutation of completed Lolla run folders;
- archive-hook integration;
- runtime integration;
- default-on behavior;
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
