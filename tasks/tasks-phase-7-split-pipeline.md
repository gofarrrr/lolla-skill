# Phase 7 — Split `pipeline.py`

**Future branch:** `feat/phase-7-split-pipeline-<submodule>` (one branch per submodule)
**Risk:** Medium — pure refactor, no behavior change. Risk is import cycles + test plumbing.
**Estimated time:** ~4-6 hours total, but split across multiple PRs (one per submodule).
**Prerequisite:** Phase 4d ideally done (smaller surface to extract).

## Why this phase

`engine/system_b/pipeline.py` is ~2200 lines. It contains:
- Pipeline orchestrator class (`SystemBPipeline.run`)
- Pass 1 (triage) helpers
- Pass 2 (deep checks) helpers
- Lane orchestration helpers (`_run_companion`, `_run_frame_pressure`, `_run_structural_coverage`, `_run_pass2_*`)
- Audit trace assembly
- Boundary call tracing helpers
- Embedding tendency reader

Splitting reduces cognitive load for future work. Each split is a SAFE refactor — move code to a new module, update imports, run tests.

## Approved decisions

- **One submodule per PR.** Don't bundle. Each PR's diff should be: extract one cohesive set of functions to a new module, update imports, no behavior change.
- **No public API changes.** Symbols stay importable from the same place. If `engine/system_b/pipeline.py` previously exported X, after the split it should re-export X (or be available from `engine.system_b`).
- **Tests stay green throughout.** If a refactor breaks tests, the refactor is wrong; revert.

## Out of scope

- **Do NOT change behavior.** No new features, no bug fixes (even ones you find — flag to PM, don't silently fix).
- **Do NOT touch the IR or packet builder.**
- **Do NOT remove anything.** Cleanup is Phase 4d/6, not 7.

## Suggested submodule extractions, in order

Roughly small-to-large. Each is its own PR.

### 7.1 Boundary tracing helpers

- Functions: `_metadata_to_boundary_call_trace`, `_capture_boundary_call`, possibly `BoundaryCallTrace` dataclass
- Target: `engine/system_b/boundary_tracing.py`
- Estimated: ~30 min

### 7.2 Pass 1 (triage) helpers

- Functions: `_run_pass1_clusters_parallel` and any helpers not used outside Pass 1
- Target: `engine/system_b/pass1_runner.py`
- Estimated: ~45 min

### 7.3 Pass 2 (deep checks) helpers

- Functions: `_run_pass2_single`, `_run_pass2_parallel`
- Target: `engine/system_b/pass2_runner.py`
- Estimated: ~45 min

### 7.4 Lane orchestrators

- Methods on `SystemBPipeline`: `_run_companion`, `_run_frame_pressure`, `_run_structural_coverage`
- Target: keep on the class, OR extract to free functions in `engine/system_b/lane_orchestrators.py` taking the pipeline as a parameter.
- This one's larger; estimate ~1.5h. Consider doing it last.

### 7.5 Audit trace assembly

- The block that constructs `AuditTrace` after all lanes run
- Target: `engine/system_b/audit_assembly.py`
- Estimated: ~30 min

## Tasks per submodule (template)

Apply this template to each of 7.1-7.5.

### 0.0 Branch + baseline

- [ ] `git switch -c feat/phase-7-<submodule-name>`
- [ ] `pytest tests -q` — record pass count.

### 1.0 Identify the cohesive group

- [ ] Read the target functions in `pipeline.py`. Confirm they don't depend on `SystemBPipeline` instance state (or if they do, identify what to pass as parameters).
- [ ] List dependencies (imports, types) the new module will need.

### 2.0 Extract

- [ ] Create the new module file.
- [ ] Move the functions/classes verbatim.
- [ ] Add necessary imports to the new module.
- [ ] In `pipeline.py`, import the moved symbols from the new module.
- [ ] Run `pytest tests -q`. Pass count must match baseline.

### 3.0 Verify symbol availability

- [ ] If the moved symbols were previously importable from `engine.system_b.pipeline`, ensure they still are (re-export from `pipeline.py` if needed).
- [ ] `grep -rn "from engine.system_b.pipeline import <SYMBOL>" tests/ engine/` — confirm all imports still work.

### 4.0 Final verify + PR

- [ ] Full suite green at baseline pass count.
- [ ] Diff: should be roughly "remove N lines from pipeline.py, add N+5 lines in new module" (the +5 is module docstring + imports).
- [ ] Open PR with title `refactor: Phase 7.<N> — extract <submodule> to <file>`.

## How to detect circular imports

If after extraction `pytest` fails with `ImportError: cannot import name X from partially initialized module Y`:
- The new module probably imports something from `pipeline.py` that imports from the new module
- Fix: move the shared symbol to a third module, or restructure so the dependency is one-way

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hidden state passed via `self` | Read each function's body; if it touches `self.X`, decide: pass X as param OR keep on class |
| Test imports break | Re-export from `pipeline.py`; don't rely on tests updating their import paths |
| Type circular references | Use `from __future__ import annotations` and string-form type hints if needed |
| Subtle behavior change from reordering imports | Always run full suite after each extraction; revert if anything fails |

## What to ask Marcin (PM) about

- If a function appears to belong to two submodules → ask which.
- If extracting requires changing the function's signature in any way → STOP. The phase says "no behavior change". Signature changes belong in a different phase.
- If you find a circular import that requires a third module to break → propose the third module's name + scope before creating it.
