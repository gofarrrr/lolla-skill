# Decision Work Sidecar Automation Readiness Package Gate v0

Status: PR233 package gate
Date: 2026-07-04

Manifest:
[automation readiness package manifest](decision-work-sidecar-automation-readiness-package-manifest-v0.json)

## Purpose

PR233 packages PR224 through PR232 as a narrow offline/operator-runner
automation-readiness milestone.

This is a package gate. It does not add runtime wiring, make runtime
attachment default-on, approve resolver refs, create a queue worker or daemon,
call providers/models, generate or repair semantic interpretation, write
sidecars, mutate archives, score answer quality, claim product proof, claim
human validation, validate advice correctness, certify outputs, or authorize
action.

## Narrow Automation Readiness v1 Claim

Decision Work Sidecar Automation Readiness v1 is functional as an offline,
command-only operator-runner layer that can orchestrate deterministic Decision
Work artifacts from explicit paths, stop safely on missing semantic inputs,
and reach dry-run readiness when safe semantic inputs already exist.

That means the package can claim:

- an automation-readiness PRD and offline runner plan exist;
- a one-shot offline operator runner and CLI exist;
- the runner accepts explicit inputs rather than discovering private/archive
  data;
- the runner emits `lolla.decision_work_offline_operator_runner.v0` summaries;
- missing semantic input defers visibly;
- missing generated triage defers visibly;
- existing checked-in-safe semantic input can reach dry-run readiness;
- launch/deploy-style risk differences remain preserved;
- non-curated pilot coverage includes one missing-semantic-input fixture and
  one existing-safe-semantic-input fixture;
- write, archive, runtime, resolver, action, proof, validation, and scoring
  flags stay closed;
- no actual sidecar write is performed by the runner.

It does not mean arbitrary-run semantic generation, fresh non-curated semantic
understanding proof, queue-worker automation, runtime hook integration,
default-on behavior, resolver approval, automatic sidecar write, checked-in
sidecar outputs, real historical archive mutation, customer readiness, product
proof, human validation, advice correctness, answer-quality scoring,
certification, or action authorization.

## Functional Chain

The packaged automation-readiness chain is:

```text
completed-run archive input
-> explicit generated read input
-> explicit generated triage input
-> offline operator runner
-> generated read intake
-> brief supply
-> rendered brief
-> triage supply
-> resolver-supply candidate packet
-> sidecar update packet
-> sidecar write dry-run
-> runner summary
```

The runner stops before any explicit write. PR233 packages that no-write
automation-readiness layer. It does not implement PR234 receipt or
blocked-state language review.

## What Is Functional

Automation Readiness v1 can:

- run as a one-shot offline operator command;
- consume explicit generated-read, generated-triage, completed-archive,
  case-id, and safe-output path inputs;
- orchestrate existing deterministic Decision Work CLIs through dry-run
  readiness;
- write generated intermediate artifacts only to operator-supplied temp/safe
  output paths during execution;
- emit `runner_summary.json`;
- surface `missing_required_inputs`, `deferred_reasons`, `blocker_reasons`,
  and `operator_attention_items`;
- return `deferred_missing_semantic_read` when the generated read is absent;
- return `deferred_missing_triage` when the generated triage is absent;
- return `sidecar_ready_for_explicit_write` when existing safe semantic inputs
  allow the deterministic chain to reach dry-run readiness;
- return `sidecar_ready_blocked_state` for blocked/high-risk inputs that
  preserve runtime and user-surface blocking;
- stop before explicit write even when write flags are supplied;
- preserve false write/archive/runtime/resolver/action/proof/scoring flags.

## What Remains Missing

Automation Readiness v1 still does not provide:

- arbitrary-run semantic generation;
- proof that a fresh non-curated conversation was semantically understood;
- generated read or generated triage creation for missing cases;
- queue workers or daemons;
- runtime hook integration;
- default-on behavior;
- resolver approval;
- automatic sidecar writes;
- checked-in runner summaries, dry-run outputs, preview files, or sidecar
  outputs;
- real historical archive mutation;
- customer/user-facing readiness;
- product proof;
- human validation;
- answer-quality scoring;
- advice-correctness validation;
- approval or certification;
- agent or automatic action authorization.

## Covered Statuses

The package covers these runner statuses:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`;
- `deferred_missing_semantic_read`;
- `deferred_missing_triage`;
- `blocked_privacy_risk`;
- `blocked_source_depth_insufficient`;
- `blocked_schema_or_custody_failure`;
- `blocked_runtime_or_user_surface_risk`;
- `stopped_before_explicit_write`;
- `runner_failed_closed`.

These are routing, custody, and missingness statuses. They are not quality
labels, approval labels, customer-readiness labels, or action authorization.

## Pilot Evidence

PR229 and PR231 provide the package's non-curated pilot evidence:

- PR229 used a synthetic/sanitized non-curated completed-run-like fixture with
  no generated read or generated triage. The runner stopped at
  `generated_read` with `deferred_missing_semantic_read`.
- PR231 used a synthetic non-curated fixture with existing checked-in-safe
  launch-like semantic inputs. The runner completed deterministic steps through
  sidecar write dry-run and stopped at `dry_run_complete` with
  `sidecar_ready_for_explicit_write`.

Together, they show the runner can both stop honestly on missing semantic
input and go deep when existing safe semantic inputs are supplied. Together,
they still do not show arbitrary non-curated semantic automation.

## Boundary And Non-Claims

The package preserves these boundaries:

- explicit operator inputs are required;
- the runner is not a queue worker, daemon, or runtime hook;
- the runner does not auto-discover private/archive data;
- missing semantic input is deferred, not guessed;
- existing safe semantic input is preserved, not generated;
- dry-run readiness is not actual sidecar write;
- sidecar-ready status is not user/customer readiness;
- resolver refs remain not approved;
- runtime use and user-surface state remain separate from operator readiness;
- deterministic code may orchestrate existing CLIs and preserve refs/statuses;
- deterministic code must not decide that advice is correct, that Lolla
  improved a decision, or that an agent may act.

## Validation Strategy

The package gate should be validated by:

- checking the package manifest schema;
- verifying every manifest-listed file exists;
- confirming forbidden paths are absent;
- running focused tests across PR224 through PR233;
- running broader relevant Decision Work regression when practical;
- parsing checked-in JSON artifacts with `jq`;
- running Product Delta evidence boundary lint over touched docs/review JSON;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, raw/private-content, provider-text, and
  hidden-reasoning markers;
- confirming no checked-in `runner_summary.json`, dry-run output, preview file,
  sidecar output, or `decision_work/` directory exists;
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
    "decision-work-sidecar-automation-readiness-package-manifest-v0.json"
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
automation_readiness_v1_packaged
```

Recommended next PR:

```text
PR234 Receipt / Blocked-State Language Review v0
```

PR234 should review whether `sidecar_ready_for_explicit_write`,
`sidecar_ready_blocked_state`, dry-run readiness, receipts, and blocked-state
language remain legible without implying product readiness, advice
correctness, resolver approval, sidecar availability, or action authorization.
It should not implement runtime wiring, queue workers, automatic writes,
resolver approval, model/provider calls, scoring, proof claims, certification,
or action authorization.

## Implemented Follow-Up

PR234 implements that review as
[Decision Work Receipt / Blocked-State Language Review](decision-work-receipt-blocked-state-language-review-v0.md).
It keeps the Automation Readiness v1 terms acceptable with explicit caveats
preserved and selects `proceed_to_product_delta_evaluation_readiness_prd` for a
separate next phase.

## Explicit Non-Claims

PR233 does not claim:

- arbitrary-run semantic generation;
- fresh non-curated semantic understanding proof;
- direct runtime interpretation;
- queue worker or daemon behavior;
- runtime hook integration;
- default-on behavior;
- resolver approval;
- automatic sidecar writes;
- checked-in sidecar outputs;
- real historical archive mutation;
- customer/user-facing readiness;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent action authorization;
- automatic action authorization.
