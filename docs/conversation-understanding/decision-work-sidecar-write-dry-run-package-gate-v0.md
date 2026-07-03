# Decision Work Sidecar Write Dry-Run Package Gate v0

Status: PR208 package gate
Date: 2026-07-03

Manifest:
[sidecar write dry-run package manifest](decision-work-sidecar-write-dry-run-package-manifest-v0.json)

## Purpose

PR208 packages PR206 and PR207 as a narrow dry-run sidecar-write capability.

This is a package gate. It does not write sidecars, mutate archives, approve
resolver refs, wire runtime, make runtime attachment default-on, call
providers/models, create workers, score answer quality, claim product proof,
claim human validation, validate advice correctness, or authorize action.

## Narrow Dry-Run v1 Claim

Decision Work Sidecar Write Dry-Run v1 is functional as an offline,
deterministic preview layer that can show what would be written from a sidecar
update packet while preserving actual-write, archive-mutation,
resolver-approval, runtime-wiring, proof, scoring, and action-authorization
prohibitions.

That means the package can claim:

- a dry-run sidecar-write adapter exists;
- a dry-run review exists;
- launch-beta can produce `dry_run_ready`;
- deploy-intake can produce `dry_run_packet_with_runtime_block`;
- preview files can be written under an explicit safe preview directory;
- archive-like and `decision_work/` paths are blocked;
- dry-run status, source refs, uncertainty, privacy limits, custody flags, and
  non-claims travel forward;
- review confirms the preview remains temp/output-only.

It does not mean actual sidecar writes, archive mutation, resolver approval,
runtime wiring, default-on behavior, product proof, human validation,
advice-correctness validation, scoring, or action authorization.

## Functional Chain

The packaged dry-run chain is:

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
-> PR207 sidecar write dry-run review
```

The final artifact in this package is a dry-run result and optional preview
directory. It is still not an archive `decision_work/` sidecar write.

## What Is Functional

Dry-Run v1 can:

- consume PR202 sidecar update packets;
- produce a dry-run result for launch-beta;
- preserve runtime and user-surface blocking for deploy-intake;
- write preview files only under an explicit safe output directory;
- reject archive-like and `decision_work/` output or preview paths;
- reject or block privacy, local-path, authority, proof, scoring, action, and
  actual-write attempts;
- preserve that `actual_sidecar_write_performed`, `archive_mutated`,
  `runtime_wiring_changed`, and `resolver_refs_approved` are false;
- keep deploy-intake inspectable while still runtime-blocked.

## What Remains Missing

Dry-Run v1 still does not provide:

- actual sidecar writes;
- archive mutation;
- runtime wiring;
- resolver approval;
- resolver refs marked usable;
- default-on behavior;
- production sidecar update automation;
- model calls;
- product proof;
- human validation;
- answer-quality scoring;
- advice-correctness validation;
- action authorization.

## Dry-Run Statuses

The package covers:

- `dry_run_ready`;
- `dry_run_packet_with_runtime_block`;
- `blocked_not_sidecar_update_packet`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_actual_write_attempt`;
- `blocked_archive_path`;
- `blocked_missing_required_fields`;
- `requires_operator_repair`.

## Preview Directory Safety

Preview files are allowed only under an explicit caller-supplied output
directory. The adapter rejects archive-like or `decision_work/` preview paths.

The preview files are:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`.

These files are dry-run previews only. They are not written into archive
folders and cannot be treated as runtime sidecar availability.

## Boundary And Non-Claims

The package preserves these boundaries:

- dry-run outputs are proposed previews, not writes;
- sidecar update packets are not approved refs;
- deploy-intake runtime and user-surface blockers travel forward;
- deterministic code may validate, normalize, copy safe refs, preserve
  blocked/deferred states, and write temp previews;
- deterministic code must not infer new messy conversation meaning or decide
  the advice is correct;
- actual archive mutation remains a separate future boundary.

## Validation Strategy

The package gate should be validated by:

- checking the package manifest schema;
- verifying every manifest-listed file exists;
- confirming forbidden paths are absent;
- running focused tests across PR178 through PR208;
- regenerating launch/deploy brief-supply, triage-supply, resolver-supply,
  sidecar-update, and dry-run temp artifacts;
- confirming preview files are written only under explicit safe output dirs;
- parsing checked-in JSON artifacts and generated temp packets with `jq`;
- running Product Delta evidence boundary lint over touched docs/review JSON;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, raw/private-content, provider-text, and
  hidden-reasoning markers;
- confirming `SKILL.md` and `scripts/skill/*` remain untouched.

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
    "decision-work-sidecar-write-dry-run-package-manifest-v0.json"
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
sidecar_write_dry_run_v1_packaged
```

Recommended next implementation PR:

```text
PR209 Runtime Sidecar Write Contract v0
```

Do not implement sidecar write code from this package gate. The next phase is
a write contract only, before any explicit operator write adapter or archive
mutation can be considered.

## Explicit Non-Claims

PR208 does not claim:

- actual sidecar writes;
- archive mutation;
- runtime wiring;
- resolver approval;
- approved resolver refs;
- resolver refs marked usable;
- default-on behavior;
- production sidecar update automation;
- provider/model calls;
- queue workers or daemons;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- agent action authorization;
- automatic action authorization.
