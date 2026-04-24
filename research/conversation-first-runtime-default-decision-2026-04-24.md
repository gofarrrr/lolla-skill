# Conversation-first runtime default decision

**Date:** 2026-04-24
**Status:** Implemented; verification pending.

## Context read

- `SKILL.md` Step 3 currently invokes `scripts/run_pipeline.py` with `--extraction-file`, `--conversation-file`, `--output-file`, and `--skip-revision`, but without `--new-contract`.
- `scripts/run_pipeline.py` currently defaults to the legacy `CritiqueRequest(query, vanilla_answer)` path; it only builds `ConversationContext` when `--new-contract` is present.
- `HOW_IT_WORKS.md` Step 3 currently documents `--new-contract` as the way to route through `ConversationContext`.
- The context-engineering roadmap says main is materially conversation-first, but the next move is to stabilize the current migration and make raw transcript plus provenance the architectural baseline.
- The legacy PR archaeology says provenance-backed conversation structure is supposed to replace synthetic identifiers and summary-first extraction patches.

## Intended CLI contract

Errors below should use the existing `run_pipeline.py` structured error style: print JSON with `{"status": "error", "error": "..."}` and exit with status code `1`.

| Invocation shape | Intended behavior |
|---|---|
| `--extraction-file X --conversation-file Y` with no contract flag | Default production path. Load `ConversationContext` from `X` and `Y` via `load_conversation_context(...)`, then pass that object to `SystemBPipeline.run()`. Continue using the extraction's `query` and `vanilla_answer` only for output compatibility and non-lane surfaces that already require them. |
| `--extraction-file X --conversation-file Y --legacy-contract` | Explicit old-path opt-out. Build `CritiqueRequest(query, vanilla_answer)` and pass that object to `SystemBPipeline.run()`. The conversation file may still be used for existing non-lane context surfaces such as BI/fact-registry behavior, but it must not make the lane input a `ConversationContext`. |
| `--extraction-file X --conversation-file Y --new-contract` | Deprecated compatibility alias for the new default. It should behave the same as the no-flag default path for one release. Documentation and help text should say this flag is deprecated and no longer needed. |
| `--extraction-file X --conversation-file Y --new-contract --legacy-contract` | Error. The flags request contradictory runtime contracts. |
| `--extraction-file X` without `--conversation-file`, no contract flag | Error. The default runtime requires the raw conversation transcript so production cannot silently fall back to the legacy lane input. Suggested error text: `--extraction-file requires --conversation-file for the default ConversationContext runtime; pass --legacy-contract to run the legacy CritiqueRequest path intentionally.` |
| `--extraction-file X --legacy-contract` without `--conversation-file` | Allowed compatibility path. Build and run `CritiqueRequest(query, vanilla_answer)`. This preserves deliberate file-only legacy runs while keeping the opt-out explicit. |
| `--extraction-file X --new-contract` without `--conversation-file` | Error. The deprecated alias still requires the files needed to build `ConversationContext`. |
| `--extraction-json JSON` without `--legacy-contract` | Error. Inline JSON has no stable extraction path and no raw transcript path, so it cannot build `ConversationContext`; callers must opt into the legacy contract explicitly. Suggested error text: `--extraction-json is only supported with --legacy-contract because ConversationContext requires extraction and conversation files.` |
| `--extraction-json JSON --legacy-contract` | Allowed compatibility path. Parse the inline JSON and run `CritiqueRequest(query, vanilla_answer)`. If `--conversation-file` is also supplied, it may continue feeding existing non-lane context surfaces, but lane input remains `CritiqueRequest`. |
| `--extraction-json JSON --new-contract` | Error. Inline JSON cannot build `ConversationContext`; use `--extraction-file X --conversation-file Y` for the default path. |

## `--new-contract` compatibility decision

Keep `--new-contract` as a deprecated no-op alias for one release.

Rationale:

- Phase 2 measurement scripts and artifacts still name the old/new comparison in terms of `--new-contract`; accepting the flag avoids unnecessary churn while the default is flipped.
- The flag should no longer be required or recommended in production docs.
- The new explicit old-path spelling is `--legacy-contract`; measurement scripts should move old-path commands to `--legacy-contract` and new-path commands to no contract flag.
- A hard rejection of `--new-contract` can be revisited after this runtime-default change has shipped and downstream scripts/docs no longer depend on the flag.

## Production invariant

`/lolla` production invocations must exercise the same `ConversationContext` path that Phase 2 measurements exercised whenever both extraction and conversation files exist; the legacy `CritiqueRequest` path is an explicit compatibility opt-out only.

## Caller inventory before implementation

| Caller / reference | Current invocation shape | Classification before default flip | Follow-up |
|---|---|---|---|
| `SKILL.md` Step 3 | `--extraction-file` + `--conversation-file` + `--output-file` + `--skip-revision`, no contract flag | Production caller currently relies on the legacy default. This is the intended default flip, not an accidental break. | Task 4.1 must document that this no-flag production shape now runs `ConversationContext`. |
| `scripts/phase2a_lane3_quality_check.py` | Always passes `--extraction-file` + `--conversation-file`; appends `--new-contract` only for `new_contract=True` | Old-path measurements currently rely on the legacy default and would silently flip without an explicit flag. New-path measurements already pass an explicit, deprecated alias. | Task 3.2 must make old path append `--legacy-contract` and make new path use no contract flag. |
| `scripts/phase2b_lane4_quality_check.py` | Same old/new command construction as Phase 2a | Same as Phase 2a. | Task 3.3. |
| `scripts/phase2c_lane1_quality_check.py` | Same old/new command construction as Phase 2a | Same as Phase 2a. | Task 3.4. |
| `scripts/phase2d_lane2_quality_check.py` | Same old/new command construction as Phase 2a | Same as Phase 2a. | Task 3.5. |
| `scripts/stability_check.py` Mode B rerun driver | `--extraction-file` + `--output-file` + `--skip-revision`; adds `--conversation-file` only when supplied; no contract flag | With a conversation file, it currently relies on the legacy default and will intentionally follow production default after the flip unless Task 3.6 chooses otherwise. Without a conversation file, it would hit the approved no-conversation-file error unless Mode B opts into legacy or requires a conversation file. | Task 3.6 must make the Mode B choice explicit and update command construction accordingly. |
| `HOW_IT_WORKS.md` Step 3 | Example includes `--new-contract` | Explicit new-path example; no runtime break, but stale once new path is default. | Task 4.2 must remove the flag from production examples and document the escape hatch. |
| Research Phase 2 README examples under `research/test-cases/phase2*/` | Historical examples compare with/without `--new-contract` | Shipped evidence artifacts, not active callers. They describe the historical measurement setup and should not be edited during this task. | Reference only. |
| Historical task/research docs | Mentions of `run_pipeline.py`, `--new-contract`, or old default behavior | Historical references, not active callers. | Leave unless Task 4.5 identifies stale wording in active docs/scripts/tests that must be updated. |
| Tests / CI fixtures | No active test or CI caller of `scripts/run_pipeline.py` found in the grep inventory. | No immediate break found. | Task 2 adds explicit contract tests. |

## Downstream implementation notes after approval

- `scripts/run_pipeline.py --help` should present `ConversationContext` as the default for file-based conversation runs, `--legacy-contract` as the escape hatch, and `--new-contract` as deprecated compatibility.
- Measurement scripts should compare old/new by using `--legacy-contract` for old and no contract flag for new.
- `SKILL.md` and `HOW_IT_WORKS.md` should remove the implication that production needs `--new-contract`.
- Initial lean for `scripts/stability_check.py` Task 3.6: when a conversation file is available, Mode B should follow the new production default; any old-path stability comparison should use an explicit legacy option. Final decision stays in Task 3.6.
- `--new-contract` deprecation should be tied to a concrete removal trigger: remove it when Phase 6 legacy-shim removal lands, or in one follow-up PR after all active scripts/docs have moved to the default/`--legacy-contract` spelling, whichever comes first.
- `--extraction-file` and `--extraction-json` remain mutually exclusive via argparse; Task 2 should include a small inherited-parser error-path test so this stays visible.

## Implementation summary

- `scripts/run_pipeline.py` now selects `ConversationContext` by default when the caller supplies both `--extraction-file` and `--conversation-file`.
- `--legacy-contract` is the explicit opt-out that preserves the old `CritiqueRequest` lane input.
- `--new-contract` remains accepted as a deprecated compatibility alias for the default path, but it errors if combined with `--legacy-contract`.
- `--extraction-file` without `--conversation-file` now errors unless `--legacy-contract` is supplied.
- `--extraction-json` now requires `--legacy-contract`; inline JSON cannot build `ConversationContext`.
- The inherited argparse mutual exclusion between `--extraction-file` and `--extraction-json` is covered by a contract test.
- Phase 2 measurement scripts now compare old/new by using `--legacy-contract` for old and no contract flag for new.
- `scripts/stability_check.py` Mode B follows the production default when a conversation file is supplied and exposes `--legacy-contract` for explicit legacy reruns or extraction-only compatibility.
- `SKILL.md`, `HOW_IT_WORKS.md`, and CLI help text now describe the no-flag file-based production path as the `ConversationContext` runtime.

## Deviations from approved contract

No intentional deviations. The only parser-level edge case not expressed as JSON is the pre-existing argparse mutual-exclusion error when callers provide both `--extraction-file` and `--extraction-json`; this remains an argparse usage error and is covered by `tests/test_run_pipeline_contract_default.py`.

## Verification results

Offline verification completed on 2026-04-24:

| Check | Result |
|---|---|
| New runtime contract tests: `python3 -m pytest tests/test_run_pipeline_contract_default.py -q` | Passed: `6 passed in 0.21s` |
| Existing conversation/context tests: `python3 -m pytest tests/test_conversation_loader.py tests/test_pipeline_shim_equivalence.py tests/test_lane1_contextual.py tests/test_lane2_contextual.py tests/test_frame_pressure_contextual.py tests/test_structural_coverage_contextual.py -q` | Passed: `83 passed in 0.45s` |
| Full test suite: `python3 -m pytest tests -q` | Passed: `243 passed, 1 warning, 93 subtests passed in 7.39s` |
| CLI help: `python3 scripts/run_pipeline.py --help` | Passed: help text says file-based extraction + conversation inputs use `ConversationContext` by default, names `--legacy-contract` as explicit legacy, and labels `--new-contract` as deprecated alias. |
| Production-path live smoke without `--new-contract` | Not run: requires live OpenRouter credentials/network and explicit budget approval. |
| Explicit `--legacy-contract` live smoke on same case | Not run: requires live OpenRouter credentials/network and explicit budget approval. |

The full-suite warning is an existing `datetime.utcnow()` deprecation warning in `scripts/stability_check.py`; it is not caused by the runtime contract switch.

## Known residual risks

- Live OpenRouter behavior was not smoke-tested in this pass, so offline tests verify command construction, input selection, parsing, and existing lane context behavior, not provider availability.
- `--new-contract` remains accepted intentionally as a deprecated alias; follow-up cleanup must remove it when the agreed removal trigger is reached.
- The inherited argparse mutual-exclusion error for `--extraction-file` plus `--extraction-json` is not converted to the JSON error envelope.

## Rollback path

- Immediate operator rollback: add `--legacy-contract` to a file-based invocation to force `CritiqueRequest`.
- Script rollback for measurements: old-path commands already use `--legacy-contract`; new-path commands can temporarily add `--legacy-contract` if PM needs a legacy-only diagnostic.
- Code rollback: revert the `scripts/run_pipeline.py` contract selection/validation change plus the measurement-script command updates. The compatibility alias means callers still using `--new-contract` remain protected during the rollback window.
