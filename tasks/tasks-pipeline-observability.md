# PR 1: Pipeline Observability

**Branch:** `fix/pipeline-observability`
**Issues:** #1 (triage trigger source tracking), #4 (empty frame evidence validation)
**Scope:** Engine internals — audit trace schema, frame element validation

## Relevant Files

- `engine/system_b/pipeline.py` - Contains `_select_triggered_tendencies()` (trigger source tracking), `AuditTrace` dataclass (schema change), `_embedding_tendency_signal()` (swiss cheese layer)
- `engine/system_b/frame_pressure.py` - Contains `_parse_frame_extraction()` (empty evidence validation), `ExtractedFrameElement` dataclass, `FramePressureCard` dataclass (dropped elements tracking)
- `engine/system_b/triage.py` - Contains `TriageScore` dataclass (unchanged, but referenced by trigger source)
- `scripts/run_pipeline.py` - Serializes audit trace to JSON output (needs to serialize new fields)
- `tests/test_trigger_source.py` - **NEW** — Tests for trigger source tracking logic
- `tests/test_frame_validation.py` - **NEW** — Tests for frame element empty-evidence rejection and drop tracking

### Notes

- Unit tests should be placed in the `tests/` directory.
- Use `python3 -m pytest tests/ -v` to run tests.
- The embedding swiss cheese layer (`_embedding_tendency_signal`) is the mechanism that triggers tendencies with triage score 0. The fix adds observability, not behavior change.
- Frame element validation is a strictness change — elements that previously passed silently with empty evidence will now be rejected and tracked.
- TDD vertical slices: write ONE test, implement to pass, repeat. Do not write all tests upfront.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout branch: `git checkout -b fix/pipeline-observability`

- [ ] 1.0 Add trigger source tracking to the audit trace (Issue #1)
  - [x] 1.1 Read `engine/system_b/pipeline.py` — study `_select_triggered_tendencies()` (line 1086), `AuditTrace` dataclass (line 180), and how `embedding_tendency_hits` feeds into the trigger list (line 1116-1122)
  - [x] 1.2 Read `scripts/run_pipeline.py` — study how `audit_summary.triggered_tendencies` is serialized (line 158)
  - [x] 1.3 RED: Write test in `tests/test_trigger_source.py` — when a tendency exceeds triage threshold, `_select_triggered_tendencies` returns it with `source: "triage"` and the triage score
  - [x] 1.4 GREEN: Create a `TriggeredTendency` dataclass (tendency_id, source, score) in `pipeline.py`. Modify `_select_triggered_tendencies` to return `tuple[TriggeredTendency, ...]` instead of `tuple[str, ...]`. Set `source="triage"` and `score=triage_score` for triage-path entries
  - [x] 1.5 RED: Write test — when a tendency comes from embedding swiss cheese (not in triage >= threshold), it gets `source: "embedding"` with the cosine score
  - [x] 1.6 GREEN: In the embedding hits loop (line 1117-1122), create `TriggeredTendency` with `source="embedding"` and `score=embedding_score`
  - [x] 1.7 RED: Write test — when a tendency comes from `always_include`, it gets `source: "always_include"` with score 0
  - [x] 1.8 GREEN: In the always_include loop (line 1104-1114), create `TriggeredTendency` with `source="always_include"` and `score=0`
  - [x] 1.9 Update `AuditTrace.triggered_tendencies` type from `tuple[str, ...]` to `tuple[TriggeredTendency, ...]`. Fix all callers that iterate over triggered_tendencies expecting strings — search for `triggered_tendencies` across the codebase
  - [x] 1.10 REFACTOR: Verify all existing tests still pass after the type change. Run `python3 -m pytest tests/ -v`

- [ ] 2.0 Add frame element validation — reject empty evidence/pattern (Issue #4)
  - [x] 2.1 Read `engine/system_b/frame_pressure.py` — study `_parse_frame_extraction()` (line 268), specifically the empty evidence guard at line 274 and the element construction at line 281-289
  - [x] 2.2 RED: Write test in `tests/test_frame_validation.py` — an element with empty `evidence_quote` is rejected (not included in the returned tuple)
  - [x] 2.3 GREEN: In `_parse_frame_extraction()`, add `if not evidence:` guard before the try block (after line 279) that logs a warning and `continue`s
  - [x] 2.4 RED: Write test — an element with empty `frame_pattern` is rejected
  - [x] 2.5 GREEN: Add `pattern = coerce_str(item.get("frame_pattern"))` check, reject if empty
  - [x] 2.6 RED: Write test — rejected elements are returned as a second value from `_parse_frame_extraction()` with drop reasons (`"missing_evidence"`, `"missing_pattern"`)
  - [x] 2.7 GREEN: Change `_parse_frame_extraction` signature to return `tuple[tuple[ExtractedFrameElement, ...], list[dict]]`. Collect dropped elements with `{"element_text": ..., "drop_reason": ...}`
  - [x] 2.8 RED: Write test — `FramePressureCard` has a `dropped_frame_elements` field that carries the dropped list through to the card
  - [x] 2.9 GREEN: Add `dropped_frame_elements: tuple[dict, ...] = ()` to `FramePressureCard`. Update `run_frame_extraction()` to pass dropped elements through. Update `to_payload()` to serialize them
  - [x] 2.10 Update the caller in `pipeline.py` — `run_frame_extraction` now returns the card with dropped elements. No behavior change for the pipeline, just richer data
  - [x] 2.11 REFACTOR: Run all tests, clean up any duplication

- [x] 3.0 Serialize new fields in pipeline output
  - [x] 3.1 RED: Write test — serialized result JSON contains `triggered_tendency_sources` array with `tendency_id`, `source`, and `score` fields for each triggered tendency
  - [x] 3.2 GREEN: Update `_serialize_result()` in `run_pipeline.py` to serialize `TriggeredTendency` objects from `audit.triggered_tendencies` into `triggered_tendency_sources` list. Keep the flat `triggered_tendencies` string list for backward compatibility
  - [x] 3.3 RED: Write test — serialized `frame_pressure_card` contains `dropped_frame_elements` when elements were dropped
  - [x] 3.4 GREEN: The `FramePressureCard.to_payload()` change from 2.9 should handle this. Verify serialization path in `run_pipeline.py`
  - [x] 3.5 REFACTOR: Verify the full serialized JSON schema is consistent. Check that Observatory `serve_result.py` doesn't break with new fields (it should pass through unknown fields)

- [x] 4.0 Verify with a real run
  - [ ] 4.1 Run the existing test conversation through the pipeline: `python3 scripts/run_pipeline.py --extraction-file /tmp/lolla_20260413T193743Z_extraction.json --conversation-file /tmp/lolla_20260413T193743Z_conversation.txt --output-file /tmp/test_observability_result.json --skip-revision` — SKIPPED: requires API keys; verified offline with existing result JSON
  - [x] 4.2 Inspect the output JSON — verified existing result has 5 triggered tendencies (incl. inconsistency-avoidance from embedding swiss cheese); new code will surface source info
  - [x] 4.3 Inspect `frame_pressure_card.dropped_frame_elements` — verified: existing result has 1 element that new validation would catch (missing evidence + missing pattern)
  - [x] 4.4 Start the Observatory with the new result: verified serve_result.py is a JSON passthrough — new fields won't break it
