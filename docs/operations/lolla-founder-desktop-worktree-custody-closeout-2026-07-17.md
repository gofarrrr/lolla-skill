# Founder desktop worktree custody closeout — 2026-07-17

Status: complete, provider-free, restart-safe.

Decision: `preserve_strategic_package_noncanonically_restore_desktop_main`

## Result

The 64 modified or untracked entries formerly present in
`/Users/marcin/Desktop/lolla-skill-main` were one coherent July 14 strategic-
presentation package, not 64 unrelated changes.

The package was preserved exactly in:

- local and remote branch:
  `agent/founder-strategic-presentation-preservation-2026-07-14`;
- commit: `4162e3efa0cb919e8d4ac4504fedc1ff64950a4f`;
- parent: `d969e124cb359a398518119b24fc66bf749bb0aa`;
- tree: `5884dc492e4249d42299ef8818660a3d8273c2a5`.

The preservation branch is intentionally noncanonical. It is a restart-safe
historical checkpoint, not an open proposal to replace the newer Stage 0 and
Atlas public handoff. It should not be merged wholesale into `main`.

After preservation and remote verification, the Desktop worktree was switched
to clean canonical `main` at
`0a6a8a4895fb7eca2bd504a6047f032ec53dc3fa`, equal to `origin/main` at the time
of this closeout.

No file was deleted before it existed in the verified local and remote commit.
No stash, reset, clean, force-push, rebase, or history rewrite was used.

## Classification

### Noncanonical founder intent — preserve exactly

- `docs/conversation-understanding/lolla-founder-product-vision-2026-07-14.md`
  — SHA-256
  `dfd53588912165768837770e225352b3c556f91d1bdbfc99dc8222331905c984`;
- `docs/conversation-understanding/lolla-strategic-presentation-proposition-2026-07-14.md`
  — SHA-256
  `0789d85a544635e6efc6c56cc0030c0c6c9f510ce7349918005cb9120f7e73ab`.

These hashes exactly match the read-only founder-intent records in the
Constitution Stage 0 addendum audit. The documents remain valuable statements
of purpose and presentation direction, but the audit classified them as
noncanonical founder intent. Later canonical handoff documents incorporate and
bound parts of that direction.

### Superseded strategic front-door implementation — preserve historically

- `AGENTS.md`
- `HOW_IT_WORKS.md`
- `README.md`
- `docs/board/README.md`
- `docs/product/README.md`

These files implemented the July 14 presentation hierarchy and removed a large
historical catalog from the public front door. The direction was coherent, but
the exact versions predate the Constitution Stage 0 handoff, long-conversation
truthfulness repair, R4 closeout, and canonical Atlas baseline. Replacing
current entrypoints with them would regress current status and boundaries.

### Mechanical companion tests — preserve with the package

The package changed 56 existing tests and added one test. The dominant edit
removed `README.md` and `HOW_IT_WORKS.md` from assertions requiring every
historical Decision Work artifact to appear in the public front door. The new
test instead checked the intended concise presentation contract. This is a
coherent companion to the superseded front-door implementation, not a current
test-suite repair to transplant independently.

The exact 57 test paths were:

- `tests/test_balanced_batch_candidate_selector_readiness_builder_plan.py`
- `tests/test_balanced_offline_product_delta_evidence_batch_plan.py`
- `tests/test_decision_work_automatic_semantic_supply_prd.py`
- `tests/test_decision_work_automatic_semantic_supply_pre_runtime_v1_package_gate.py`
- `tests/test_decision_work_controlled_archive_sidecar_write_fixture.py`
- `tests/test_decision_work_controlled_archive_sidecar_write_fixture_package_gate.py`
- `tests/test_decision_work_controlled_archive_sidecar_write_fixture_plan.py`
- `tests/test_decision_work_controlled_archive_sidecar_write_fixture_review.py`
- `tests/test_decision_work_explicit_operator_sidecar_write.py`
- `tests/test_decision_work_explicit_operator_sidecar_write_package_gate.py`
- `tests/test_decision_work_explicit_operator_sidecar_write_review.py`
- `tests/test_decision_work_generated_read_brief_rendering_pilot.py`
- `tests/test_decision_work_generated_read_brief_supply.py`
- `tests/test_decision_work_generated_read_brief_two_case_pattern_review.py`
- `tests/test_decision_work_generated_read_brief_vs_existing_brief_review.py`
- `tests/test_decision_work_generated_read_resolver_supply.py`
- `tests/test_decision_work_generated_read_resolver_supply_plan.py`
- `tests/test_decision_work_generated_read_resolver_supply_review.py`
- `tests/test_decision_work_generated_read_second_brief_rendering_pilot.py`
- `tests/test_decision_work_generated_read_second_triage_pilot.py`
- `tests/test_decision_work_generated_read_to_brief_supply_plan.py`
- `tests/test_decision_work_generated_read_triage_generation_pilot.py`
- `tests/test_decision_work_generated_read_triage_pilot_review.py`
- `tests/test_decision_work_generated_read_triage_supply.py`
- `tests/test_decision_work_generated_read_triage_supply_plan.py`
- `tests/test_decision_work_generated_read_triage_two_case_pattern_review.py`
- `tests/test_decision_work_non_curated_completed_run_pilot.py`
- `tests/test_decision_work_non_curated_completed_run_pilot_plan.py`
- `tests/test_decision_work_non_curated_pilot_review.py`
- `tests/test_decision_work_offline_interpretation_queue.py`
- `tests/test_decision_work_offline_interpretation_queue_contract.py`
- `tests/test_decision_work_offline_operator_runner_plan.py`
- `tests/test_decision_work_operator_codex_generated_read_pilot.py`
- `tests/test_decision_work_operator_codex_interpretation_prompt_packet.py`
- `tests/test_decision_work_real_archive_sidecar_write.py`
- `tests/test_decision_work_real_archive_sidecar_write_package_gate.py`
- `tests/test_decision_work_real_archive_sidecar_write_plan.py`
- `tests/test_decision_work_real_archive_sidecar_write_review.py`
- `tests/test_decision_work_receipt_blocked_state_language_review.py`
- `tests/test_decision_work_resolver_candidate_sidecar_update_packet.py`
- `tests/test_decision_work_resolver_candidate_sidecar_update_plan.py`
- `tests/test_decision_work_runtime_sidecar_write_contract.py`
- `tests/test_decision_work_runtime_sidecar_write_plan.py`
- `tests/test_decision_work_second_non_curated_completed_run_pilot.py`
- `tests/test_decision_work_second_non_curated_pilot_review.py`
- `tests/test_decision_work_sidecar_automation_readiness_package_gate.py`
- `tests/test_decision_work_sidecar_automation_readiness_prd.py`
- `tests/test_decision_work_sidecar_internal_v1_completion_prd.py`
- `tests/test_decision_work_sidecar_internal_v1_current_state.py`
- `tests/test_decision_work_sidecar_internal_v1_operator_runbook.py`
- `tests/test_decision_work_sidecar_update_packet_prewrite_package_gate.py`
- `tests/test_decision_work_sidecar_update_packet_review.py`
- `tests/test_decision_work_sidecar_write_dry_run.py`
- `tests/test_decision_work_sidecar_write_dry_run_package_gate.py`
- `tests/test_decision_work_sidecar_write_dry_run_review.py`
- `tests/test_product_delta_evaluation_readiness_prd.py`
- `tests/test_strategic_presentation_entrypoints.py`

The complete authoritative inventory can be reproduced without relying on this
prose list:

```bash
git diff-tree --no-commit-id --name-status -r \
  4162e3efa0cb919e8d4ac4504fedc1ff64950a4f
```

## Verification

Before preservation:

- changed/untracked entries: 64;
- tracked files: 61;
- untracked files: 3;
- package test surface: 529 passed;
- `git diff --check`: passed;
- provider calls: 0;
- provider cost: `$0.00`.

After preservation:

- preservation worktree: clean;
- local branch and remote branch: exact commit equality;
- both founder-intent SHA-256 values: exact;
- Desktop `main` and `origin/main`: exact equality;
- Desktop worktree: clean.

## Restart instruction

A new session may now begin directly in:

```text
/Users/marcin/Desktop/lolla-skill-main
```

It should verify `git status -sb`, read `AGENTS.md`, `PROJECT_STATUS.md`, and
`docs/README.md`, and continue from canonical `main`. The preservation branch
should be consulted only when reviewing founder intent or the July 14 public-
presentation alternative. Its existence does not authorize implementation,
publication of its prose, or replacement of current entrypoints.
