# PR 2: Detection Quality

**Branch:** `fix/detection-quality`
**Issues:** #2 (fingerprint fuzzy matching), #3 (BI fact registry context)
**Scope:** Detection accuracy — companion fingerprinting, bullshit index context grounding

## Relevant Files

- `engine/system_b/companion_routing.py` - Contains `validate_fingerprint_moves()` (line 111-137, fuzzy matching), `_quote_in_answer()` (line 102-108, substring check), `_tokenize()` (line 47-52, reusable), `_quotes_overlap()` (line 34-44, 60% threshold for dedup — distinct from the 80% validation threshold)
- `engine/system_b/bullshit_index.py` - Contains `evaluate_text()` (line 379-427, accepts `context_summary`), `SYSTEM_PROMPT` (line 134-208), `_CONTEXT_BLOCK` template (line 210-216)
- `scripts/run_pipeline.py` - Contains `_run_bullshit_index()` (line 363-377, context truncation at line 375), `_extract_user_turns()` (line 74-89), main flow that passes extraction dict (line 247)
- `tests/test_fuzzy_matching.py` - **NEW** — Tests for fuzzy quote matching fallback
- `tests/test_bi_context.py` - **NEW** — Tests for fact registry context building

### Notes

- Unit tests should be placed in the `tests/` directory.
- Use `python3 -m pytest tests/ -v` to run tests.
- The fingerprint fuzzy matching adds a fallback layer — exact match is still preferred. The `_tokenize()` function already exists in `companion_routing.py` and can be reused.
- The BI fact registry replaces raw conversation truncation with structured facts from the extraction JSON. The extraction's `live_constraints` and `dropped_threads` fields are the source.
- Both changes improve recall without sacrificing precision — fuzzy matching uses a high overlap threshold (80%), fact registry is more precise than raw text.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout branch: `git checkout -b fix/detection-quality`

- [ ] 1.0 Add fuzzy quote matching fallback to fingerprint validation (Issue #2)
  - [x] 1.1 Read `engine/system_b/companion_routing.py` — study `validate_fingerprint_moves()` (line 111-137), `_quote_in_answer()` (line 102-108), `_tokenize()` (line 47-52), and `_quotes_overlap()` (line 34-44). Note: `_quotes_overlap` uses 60% for dedup; validation needs 80%
  - [x] 1.2 RED: Write test in `tests/test_fuzzy_matching.py` — when a quote is an exact substring of the answer, `validate_fingerprint_moves` returns it as validated (existing behavior, baseline)
  - [x] 1.3 GREEN: This should already pass. Run `python3 -m pytest tests/test_fuzzy_matching.py -v` to confirm
  - [x] 1.4 RED: Write test — when a quote is a minor paraphrase (same tokens, slightly reordered or with filler words) with ≥80% token overlap against the answer, the move is validated (not dropped)
  - [x] 1.5 GREEN: Add `_fuzzy_quote_in_answer(quote: str, answer_text: str, threshold: float = 0.80) -> bool` in `companion_routing.py`. It tokenizes both via `_tokenize()`, then checks `len(quote_tokens & answer_tokens) / len(quote_tokens) >= threshold`. In `validate_fingerprint_moves()`, change the `fabricated_quote` branch (line 132-133): after exact match fails, try fuzzy match before dropping
  - [x] 1.6 RED: Write test — when a quote has <80% token overlap (genuinely fabricated), the move is still dropped with reason `"fabricated_quote"`
  - [x] 1.7 GREEN: Verify the threshold gate in `_fuzzy_quote_in_answer` rejects low-overlap quotes. Should pass from 1.5 implementation
  - [x] 1.8 RED: Write test — when a move is rescued by fuzzy matching, the drop reason changes to `"fuzzy_match_rescued"` (or it's not in dropped at all). Verify the move appears in `validated` list, not `dropped`
  - [x] 1.9 GREEN: Ensure fuzzy-rescued moves go into `validated`, not `dropped`. If you want to track fuzzy rescues for observability, add an optional `match_type` field to validated entries or log it
  - [x] 1.10 RED: Write test — `_fuzzy_quote_in_answer` handles edge cases: empty quote returns False, empty answer returns False, single-word quote returns False (too short to fuzzy match meaningfully)
  - [x] 1.11 GREEN: Add guards to `_fuzzy_quote_in_answer`: `if not quote_tokens or len(quote_tokens) < 3: return False`
  - [x] 1.12 REFACTOR: Run all tests `python3 -m pytest tests/ -v`. Clean up any duplication between `_quotes_overlap` (dedup, 60%) and `_fuzzy_quote_in_answer` (validation, 80%) — they share `_tokenize()` but serve different purposes, so keep them separate

- [ ] 2.0 Replace BI context truncation with fact registry (Issue #3)
  - [x] 2.1 Read `scripts/run_pipeline.py` — study `_run_bullshit_index()` (line 363-377), specifically the `bi_context[:4000]` truncation at line 375. Study how `_conversation_context` is built from `_extract_user_turns()` (line 74-89) and how the extraction dict is available (line 247)
  - [x] 2.2 Read `engine/system_b/bullshit_index.py` — study `evaluate_text()` (line 379-427, `context_summary` parameter), `_CONTEXT_BLOCK` template (line 210-216), and `evaluate_passage()` (line 314-344) to understand how context flows to the LLM judge
  - [x] 2.3 RED: Write test in `tests/test_bi_context.py` — `_build_fact_registry(extraction)` returns a string containing all `live_constraints[].constraint` values from the extraction dict
  - [x] 2.4 GREEN: Add `_build_fact_registry(extraction: dict) -> str` in `run_pipeline.py`. Extract `extraction["extraction"]["live_constraints"]` list, format each as `"- [constraint] (weight: [weight], status: [status])"`. Return joined string. Handle missing keys gracefully (return empty string)
  - [x] 2.5 RED: Write test — fact registry also includes `dropped_threads[].thread` with their `status` (e.g. `"acknowledged_then_dropped"`)
  - [x] 2.6 GREEN: Extend `_build_fact_registry` to also extract `extraction["extraction"]["dropped_threads"]`, format as `"- DROPPED: [thread] (status: [status])"`. Append after constraints with a section header
  - [x] 2.7 RED: Write test — fact registry includes `decision_situation` as the opening context line
  - [x] 2.8 GREEN: Prepend `extraction["extraction"]["decision_situation"]` as the first line of the fact registry output
  - [x] 2.9 RED: Write test — `_run_bullshit_index` uses fact registry when extraction is available, falls back to truncated conversation when extraction is None
  - [x] 2.10 GREEN: Modify `_run_bullshit_index()` in `run_pipeline.py`: accept `extraction` dict parameter. If extraction is available, call `_build_fact_registry(extraction)` and use result as `context_summary` (no truncation needed — structured facts are compact). Fall back to `bi_context[:4000]` only when extraction is None. Update the call site in `main()` to pass `extraction`
  - [x] 2.11 REFACTOR: Run all tests. Verify the fact registry string is well under 4000 chars for the test extraction (it should be ~500-800 chars — much more precise than raw conversation truncation)

- [x] 3.0 Verify both changes with the existing run data
  - [x] 3.1 Verified: 3 fabricated_quote drops in existing result; 8 quotes across all 3 would be rescued by fuzzy matching (significant recall improvement)
  - [x] 3.2 Verified: fact registry is 1566 chars capturing 4 constraints + 2 dropped threads + decision situation; vs 4000-char raw truncation
  - [ ] 3.3 Run the full pipeline with both fixes — SKIPPED: requires API keys
  - [x] 3.4 Verified offline: all 3 fabricated drops would become validated (8/8 quotes pass fuzzy threshold)
  - [x] 3.5 Verified offline: fact registry gives BI judge precise grounded facts instead of truncated raw conversation
