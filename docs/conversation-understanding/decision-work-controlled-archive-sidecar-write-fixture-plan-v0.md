# Decision Work Controlled Archive Sidecar Write Fixture Plan v0

Status: PR213 plan gate
Date: 2026-07-04

Review artifact:
[controlled archive sidecar write fixture plan review](../../reviews/codex-assisted/decision-work-controlled-archive-sidecar-write-fixture-plan-v0/review.json)

## Purpose

PR213 defines the next sidecar-write boundary after
[Decision Work Explicit Operator Sidecar Write Package Gate](decision-work-explicit-operator-sidecar-write-package-gate-v0.md).

PR210 through PR212 proved a controlled explicit operator can write
sidecar-shaped files into safe temp/output `decision_work` targets. PR213 does
not broaden that into real archive mutation. It defines a narrower next step:
write the same allowed sidecar files into synthetic archive-shaped fixture
directories that look like completed-run archive folders only for test and
operator review.

This is a plan/review/test gate only. It does not implement a fixture adapter,
write real historical archives, mutate completed Lolla run folders, edit the
archive hook, wire runtime, approve resolver refs, call providers/models, score
answer quality, claim proof, claim human validation, validate advice
correctness, or authorize action.

## Boundary Being Introduced

The next layer may use controlled archive-like fixture directories such as:

```text
tmp/decision_work_archive_fixture_launch/archive/cases/example-run
```

Those fixture dirs may intentionally resemble archive shape so future code can
prove where `decision_work` would land. They must remain synthetic, temporary,
or operator-output fixtures.

The fixture adapter must refuse:

- real completed-run archive folders;
- existing historical archive paths;
- repository source, docs, tests, and review paths;
- runtime paths;
- non-explicit targets;
- targets outside the supplied fixture root;
- target dirs that already contain untrusted sidecar-like files;
- inputs with privacy markers, local-path leaks, provider text, proof/scoring
  language, resolver approval, or action authorization.

## Planned Input Contract

The future adapter should consume:

- a PR202 sidecar update packet;
- a matching PR206 dry-run result;
- an explicit synthetic archive-like fixture directory;
- an optional stable source ref for the packet and dry-run result;
- explicit operator/fixture mode.

The fixture directory is not a completed-run archive. It is a controlled output
directory that simulates archive shape.

## Planned Output Contract

The future adapter should emit:

```text
lolla.decision_work_controlled_archive_sidecar_write_fixture.v0
```

The output should include:

- source case;
- source sidecar update packet ref;
- source dry-run result ref;
- fixture archive dir ref;
- fixture sidecar dir ref;
- fixture write status;
- files written;
- blocker reasons;
- runtime and user-surface status;
- source refs;
- privacy and uncertainty summaries;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

## Planned Statuses

The future adapter should use these statuses:

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

Expected launch-beta behavior:

```text
fixture_write_completed
```

Expected deploy-intake behavior:

```text
fixture_write_completed_blocked_state
```

Deploy-intake must preserve runtime and user-surface blocked state.

## Allowed File Set

The future fixture adapter may write only the PR209 allowed sidecar file set
under the controlled fixture's `decision_work` directory:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

No generated fixture sidecar files should be checked into the repository.

## Deterministic Allowances

The future adapter may:

- validate sidecar update packet and dry-run schemas;
- verify packet and dry-run source refs match;
- validate the target fixture root;
- create a synthetic archive-shaped fixture directory under a safe temp or
  operator-output root;
- copy the same allowed sidecar-shaped payloads used by PR210;
- preserve blocked/deferred runtime and user-surface state;
- emit a fixture write receipt.

The future adapter must not:

- infer new conversation meaning;
- decide whether the advice is correct;
- approve resolver refs;
- mark resolver refs usable;
- write a real completed-run archive folder;
- wire runtime;
- update the post-archive hook;
- make runtime attachment default-on.

## Required Receipt Flags

Every successful or blocked future fixture receipt must keep:

- `real_archive_mutated: false`;
- `historical_archive_mutated: false`;
- `runtime_wiring_changed: false`;
- `resolver_refs_approved: false`;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_claimed: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`.

The receipt may say fixture files were written only when the target is a
synthetic fixture directory and every source/path check passes.

## Validation Requirements

The future implementation should prove:

- launch writes `fixture_write_completed`;
- deploy writes `fixture_write_completed_blocked_state`;
- deploy preserves runtime and user-surface blocked state;
- the written file set is exactly the PR209 allowed file set;
- target paths inside the repo are blocked;
- real archive-looking paths are blocked;
- existing historical archive paths are blocked;
- mismatched dry-run and packet inputs are blocked;
- missing dry-run input is blocked;
- privacy markers and local-path leaks are blocked;
- proof, scoring, resolver approval, and action-authorization claims are
  blocked;
- no repo `decision_work` sidecar is written;
- no real completed-run archive is modified;
- `SKILL.md`, `scripts/skill/*`, and the archive hook remain untouched.

## Decision Gate

Selected gate:

```text
proceed_to_controlled_archive_sidecar_write_fixture_adapter
```

Recommended next PR:

```text
PR214 Controlled Archive Sidecar Write Fixture Adapter v0
```

Do not implement real archive writes from this plan. PR214 should remain a
synthetic archive-shaped fixture adapter only.

## Implemented Follow-Up

PR214 implements the adapter as
[Decision Work Controlled Archive Sidecar Write Fixture Adapter](decision-work-controlled-archive-sidecar-write-fixture-adapter-v0.md).
The adapter writes only synthetic archive-shaped fixture outputs under explicit
safe temp/operator roots, preserves deploy-intake runtime and user-surface
blocking, and still refuses real archive paths, existing historical archive
paths, repo paths, runtime paths, resolver approval, proof claims, scoring, and
action authorization.

## Explicit Non-Claims

PR213 does not claim:

- real historical archive writes;
- mutation of completed Lolla run folders;
- runtime wiring;
- post-archive hook integration;
- default-on behavior;
- resolver approval;
- resolver refs marked usable;
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
