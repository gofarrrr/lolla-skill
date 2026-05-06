# Reasoning Substrate Source Custody Backfill

## Relevant Files

- `data/model_sources/` - Repo-local canonical markdown custody directory.
- `data/model_sources/manifest.json` - SHA-256 source custody manifest, now expected to cover all 222 runtime models.
- `engine/system_b/source_custody.py` - Deterministic source custody report and validator helper.
- `tests/test_reasoning_substrate_source_custody.py` - Focused tests for full source custody coverage, local hashes, and canonical byte matching.
- `engine/system_b/reasoning_substrate_coverage.py` - Coverage audit module updated for post-PR26 source custody fields.
- `tests/test_reasoning_substrate_coverage.py` - Focused coverage tests updated for 222 source-custody coverage.
- `research/reasoning-substrate-source-custody-backfill-2026-05-06.md` - PR26 source custody report.
- `research/full-corpus-enrichment-coverage-audit-2026-05-06.md` - PR25 coverage audit updated with PR26 custody status.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap update for PR26 posture.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine update for PR26 posture.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Next-session handover update after PR26.

## Guardrails

- PR26 is source custody only.
- Do not extract new affordance records.
- Do not modify `data/compiled/model_affordances/affordances_v4.json`.
- Do not run paid model calls or judges.
- Do not wire live `/lolla`, prompts, Observatory, memo, Step 8, Step 6, or Lane 4 runtime.
- Do not build deterministic pressure selection or user-facing Decision Pressure output.
- Keep v4 depth distinct from source custody: 222 source files in custody does not mean 222 reviewed affordance records.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup
  - [x] 0.1 Merge PR25 into `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr26-source-custody-backfill`.

- [x] 1.0 Inspect source custody state
  - [x] 1.1 Confirm current manifest starts from 55 source-custody entries.
  - [x] 1.2 Confirm canonical source directory is accessible.
  - [x] 1.3 Confirm runtime graph has 222 source-file references.

- [x] 2.0 TDD source custody coverage
  - [x] 2.1 RED: add focused tests expecting 222 manifest model IDs.
  - [x] 2.2 RED: add focused tests for local source file existence, hashes, and byte counts.
  - [x] 2.3 RED: add focused tests for canonical byte/hash matching.
  - [x] 2.4 GREEN: add deterministic source custody report helper.

- [x] 3.0 Backfill source custody
  - [x] 3.1 Copy missing 167 runtime model source files into `data/model_sources/`.
  - [x] 3.2 Regenerate `data/model_sources/manifest.json` from runtime graph source files.
  - [x] 3.3 Preserve existing 55 source files unchanged when bytes already match canonical.

- [x] 4.0 Update coverage audit for post-PR26 custody
  - [x] 4.1 Add clear source-custody fields to `reasoning_substrate_coverage.py`.
  - [x] 4.2 Update coverage tests to expect 222 source-custody model IDs and 0 missing custody IDs.

- [x] 5.0 Update living docs narrowly
  - [x] 5.1 Add PR26 source custody report.
  - [x] 5.2 Update full-corpus coverage audit for PR26 custody status.
  - [x] 5.3 Update roadmap current-state/posture for PR26.
  - [x] 5.4 Update knowledge-use schema current-state/posture for PR26.
  - [x] 5.5 Update next-session handover for PR26 decision label.

- [x] 6.0 Verify and hand off
  - [x] 6.1 Run focused source custody and coverage tests.
  - [x] 6.2 Run packet tests to ensure the PR25 packet producer still works.
  - [x] 6.3 Run affordance schema/compiler tests because source custody touched manifest/files.
  - [x] 6.4 Run decision-pressure trace regression tests.
  - [x] 6.5 Run `git diff --check`.
  - [x] 6.6 Run drift scan for posture contradictions.
  - [x] 6.7 Summarize files changed, tests passed, and blocked live surfaces.
