# Decision Work Sidecar Internal v1 Completion PRD v0

Status: PR217 current-state / finish-line PRD
Date: 2026-07-04

Review artifact:
[Decision Work Sidecar Internal v1 Completion PRD review](../../reviews/codex-assisted/decision-work-sidecar-internal-v1-completion-prd-v0/review.json)

## Purpose

PR217 creates the current-state and finish-line anchor for Decision Work
Sidecar Internal v1 before the work crosses from controlled archive-shaped
fixtures into real completed-run archive mutation.

This PRD is not the real archive write plan and not a write adapter. It does
not mutate archives, write real `decision_work/` sidecars, edit the archive
hook, wire runtime, approve resolver refs, call providers or models, score
answer quality, claim product proof, claim human validation, validate advice
correctness, certify outputs, or authorize action.

## 1. Current State

The functional chain currently reaches:

```text
generated read
-> intake validation
-> brief supply
-> rendered Decision Work Brief
-> triage supply packet
-> generated triage read
-> resolver-supply candidate packet
-> sidecar update packet
-> dry-run sidecar preview
-> explicit operator sidecar write
-> controlled archive-shaped fixture write
```

Generated-read semantic supply exists only through checked-in-safe,
operator/Codex-assisted examples. The chain does not yet create semantic
interpretation for arbitrary completed runs.

Two generated-read path cases exercise the current path:

- `launch-public-enterprise-beta`;
- `deploy-assisted-intake-routing`.

Launch can reach write-ready and fixture-completed states. Deploy intentionally
preserves runtime and user-surface blocked state because its healthcare
workflow and compliance risks should not be smoothed into availability.

Controlled archive-shaped fixture writing exists. PR214 can write the PR209
allowed sidecar file set under a synthetic archive-like fixture directory when
the caller supplies a safe temp/operator root, a PR202 sidecar update packet,
and a matching PR206 dry-run result.

Real historical archive mutation does not exist yet. No current layer writes
to real completed-run folders as part of this automatic semantic supply path.

## 2. Recommended Internal v1 Finish Line

Decision Work Sidecar Internal v1 is complete when an operator can take safe
generated Decision Work artifacts from a completed run, validate them, dry-run
the sidecar, and explicitly write a `decision_work/` sidecar into a real
completed-run archive through a controlled command, with receipts and hard
non-claims.

The sidecar should contain exactly the PR209 allowed file set:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

Internal v1 must preserve these flags:

- `resolver_refs_approved: false` unless a later explicit resolver-approval PR
  exists;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_validated: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`.

Internal v1 is an internal operator capability. It is not a default runtime
behavior and not a product proof surface.

## 3. What This Internal v1 Is Not

Decision Work Sidecar Internal v1 is not:

- customer readiness;
- default-on runtime behavior;
- automatic arbitrary-run semantic interpretation;
- direct runtime interpretation;
- runtime model or provider calls;
- resolver approval;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- approval or certification;
- action authorization.

It also does not mean a sidecar-shaped file is safe for user surface or that a
candidate resolver packet is an approved resolver ref.

## 4. Remaining PR Plan To Internal v1

The recommended ballpark sequence from the current state is six PRs:

### PR218 Real Archive Sidecar Write Plan v0

Plan-only. Define real archive path recognition, write preconditions,
backups/restore expectations, refusal rules, receipt rules, and explicit
operator confirmation. No implementation.

Implemented follow-up:
[Decision Work Real Archive Sidecar Write Plan](decision-work-real-archive-sidecar-write-plan-v0.md)
defines that boundary and selects `proceed_to_real_archive_sidecar_write_adapter`
for PR219 while still not writing real archives from the plan.

### PR219 Real Archive Sidecar Write Adapter v0

First controlled explicit write into real completed-run archive directories.
Command-only, never runtime hook. Requires a dry-run result, sidecar update
packet, target archive directory, and explicit operator confirmation. Refuses
deploy/runtime-blocked packets unless writing a blocked-state sidecar is
explicitly allowed by PR218. Refuses unsafe content, private markers, local
path leaks, proof/action/scoring claims, and resolver approval. Writes only
the PR209 allowed file set and emits a write receipt.

Implemented follow-up:
[Decision Work Real Archive Sidecar Write Adapter](decision-work-real-archive-sidecar-write-adapter-v0.md)
implements the command-only adapter and selects
`proceed_to_real_archive_sidecar_write_review` for PR220.

### PR220 Real Archive Sidecar Write Review v0

Review actual temp/safe archive-write behavior. Inspect written sidecar files
and receipts. Confirm launch/deploy distinctions. Confirm no resolver approval
or runtime wiring.

### PR221 Real Archive Sidecar Write Package Gate v0

Package the controlled real archive write layer. No runtime wiring and no
default-on behavior.

### PR222 Internal Demo / Operator Runbook v0

Explain the end-to-end operator flow:

- generate or obtain a generated read;
- intake validate;
- build brief supply;
- render the brief;
- build triage supply;
- review or create the triage read;
- build resolver candidate supply;
- build the sidecar update packet;
- run the dry-run;
- perform the explicit archive write;
- inspect the receipt.

The runbook should include commands, expected artifacts, blocked/deferred
handling, and what an operator must not infer from sidecar presence.

### PR223 Current State / Limitations Narrative Refresh v0

Refresh the board/product narrative. Explain what works, what does not, and
why this is internal v1 rather than product v1.

Optional later phases after internal v1:

- queue worker;
- runtime hook integration;
- resolver approval policy;
- automatic semantic supply for arbitrary runs;
- user-facing UI/receipt;
- broader eval fixtures.

Those later phases should not be bundled into the internal v1 completion path.

## 5. PR Bundling Recommendation

Recommended future bundles:

- Bundle A: PR218 plan and PR219 adapter, stopping before review if the adapter
  exposes path-safety or archive-mutation concerns.
- Bundle B: PR220 review and PR221 package gate.
- Bundle C: PR222 runbook and PR223 narrative refresh.

Do not bundle runtime wiring, default-on behavior, resolver approval, queue
workers, or arbitrary-run semantic automation into this phase.

## 6. Acceptance Criteria For Internal v1

Internal v1 is acceptable when:

- a safe launch-like completed-run archive can receive a `decision_work/`
  sidecar through explicit operator command;
- a blocked or high-risk case can preserve blocked sidecar state without
  becoming available;
- all sidecar writes emit receipts;
- all written files are expected and inspectable;
- no raw or private conversation text is copied;
- no raw revised answer text is copied;
- no raw memo text is copied;
- no provider text is copied;
- no local absolute paths leak;
- resolver refs remain not approved;
- action, scoring, proof, and human-validation flags remain false;
- docs and the runbook explain how to continue later.

## 7. Risks

Important risks:

- archive mutation risk;
- boundary drift where candidate packets are mistaken for approval;
- sidecar-shaped files being mistaken for runtime success;
- generated-read fluency creating overtrust;
- deploy/healthcare/compliance case being overread;
- local or private context missingness;
- operator mistakes with target paths;
- future code treating blocked-state sidecars as available sidecars.

## 8. Stop Conditions

Stop if:

- target archive path safety cannot be proven;
- dry-run and sidecar update packet do not match;
- packet has runtime or user-surface block and the plan does not allow a
  blocked-state write;
- privacy, private, or provider markers appear;
- local absolute paths would leak;
- `resolver_refs_approved` is true without an explicit later resolver-approval
  PR;
- any proof, scoring, action, or human-validation claim appears;
- a future implementation would need to edit `scripts/archive_run.py` before a
  separate runtime or archive-hook plan authorizes it.

## 9. Decision Gate

PR217 selects one of:

- `proceed_to_real_archive_sidecar_write_plan`;
- `pause_for_review`;
- `revise_internal_v1_finish_line`;
- `stop_runtime_sidecar_work`.

Selected gate:

```text
proceed_to_real_archive_sidecar_write_plan
```

Recommended next PR:

```text
PR218 Real Archive Sidecar Write Plan v0
```

Do not implement PR218 from this PRD.

Implemented follow-up:
PR218 is now represented by
[Decision Work Real Archive Sidecar Write Plan](decision-work-real-archive-sidecar-write-plan-v0.md).
It defines the write boundary and recommends PR219, but PR217 itself remains
only the completion PRD.

## 10. Review JSON

The companion review JSON records:

- schema:
  `lolla.decision_work_sidecar_internal_v1_completion_prd_review.v0`;
- current state claim;
- internal v1 finish line;
- remaining PR count ballpark;
- recommended PR sequence;
- explicit non-claims;
- biggest risks;
- selected gate;
- recommended next PR;
- custody flags.

## Validation Strategy

Validate this PRD by:

- compiling the PR217 test;
- running focused PR217 tests and Product Delta boundary lint;
- parsing the review JSON with `jq`;
- running Product Delta evidence boundary lint over the PRD, review JSON, and
  touched overview docs;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, private-content, provider-text, and
  hidden-reasoning markers;
- confirming `SKILL.md`, `scripts/skill/*`, and `scripts/archive_run.py`
  remain untouched.

## Strongest Useful Signal

The finish line is now explicit: finish Internal v1 only when an operator can
perform a controlled real completed-run archive sidecar write with receipts and
hard non-claims, after validation and dry-run.

## Strongest Unresolved Risk

The next boundary is real archive mutation. Fixture and operator write success
can create false confidence if PR218 and PR219 do not make path safety,
explicit confirmation, receipts, and blocked-state handling boringly strict.
