# Phase 5.5: Dropped-Threads Specialist Extraction

**Future branch:** `feat/conversation-first-phase-5.5-dropped-threads`
**Roadmap:** `plans/conversation-first-context-engineering-roadmap.md` -> Phase 5
**Phase 5.5 gate:** `research/phase5.5-dropped-threads-annotation-gate-2026-04-24.md` (PASS: 94% span / 0% NONE / 100% speaker / 83% kind)
**Phase 5 precedent:** `engine/system_b/live_constraints_extraction.py`, `scripts/phase5_live_constraints_eval.py`
**Scope:** add an injectable LLM-backed `dropped_threads` specialist that emits `UserIssueEvent` objects with `SpanProvenance` (verbatim user- or assistant-turn substrings) plus `status` + `superseded_by` label passthrough. Do not change Phase 5's `live_constraints` specialist or touch `original_framing` / `decision_situation`.

## Why This Phase

Phase 5 shipped the `live_constraints` specialist at 70% recall. Phase 5.5 applies the proven pattern to the second field. The gate confirmed 94% span convergence on 9 corpus items, unanimous speaker agreement, and zero non-recoverable items — implementation should be low-risk.

## Approved Phase 5.5 Decisions

From the Phase 5.5 gate:

- **Single-span mode only for v1.** All 9 gate items are single-turn; no cross-turn derivation observed. The Phase 5 derivation code path remains available for future specialists but is not exercised here.
- **Dual-speaker SOURCE.** Both user AND assistant turns go in SOURCE, each labeled by speaker. 1 of 9 corpus items is assistant-raised; the specialist must support this.
- **Emit `speaker` field** on the `SpanRef` matching the source turn's speaker.
- **Emit `status`** defaulting to `"acknowledged_then_dropped"` (the only value observed in monolith output across 10 cases).
- **Emit `superseded_by` label** as a paraphrase string — NOT substring-validated. This is the "what replaced this thread" summary.
- **Default `kind="open_loop"`.** `kind_ambiguity` flag for threads that read as live concern despite being acknowledged-then-dropped.
- **Forbid paraphrase expansion.** Gate surfaced 2 cases (RE-D1, UHP-D1) where the monolith's paraphrase added content not in the source turn. The specialist prompt must explicitly instruct against enumerations or content not in the quoted span.
- **Replace monolith mapping when injected.** Same architectural pattern as Phase 5's `live_constraints_extractor` hook. When the specialist is provided, it REPLACES the monolith's `dropped_threads → UserIssueEvent` mapping. `live_constraints`, `original_framing` unaffected.
- **Gold set:** the 9 Phase 5.5 gate items become eval gold.

## Relevant Files

- `engine/system_b/dropped_threads_extraction.py` — **NEW**. Copy-adapt from `live_constraints_extraction.py`.
- `engine/system_b/ir_constructor.py` — extend with an optional `dropped_threads_extractor` hook parallel to `live_constraints_extractor`.
- `engine/system_b/ir.py` — read only. `UserIssueEvent` already has `status`, `superseded_by`, and span/derivation provenance support.
- `scripts/phase5.5_dropped_threads_eval.py` — **NEW**. Copy-adapt from `phase5_live_constraints_eval.py`, using the 9 gate items as gold.
- `tests/test_dropped_threads_extraction.py` — **NEW**. Copy-adapt from `test_live_constraints_extraction.py` with speaker-field tests added.

## Acceptance Gate

| Axis | Target | How to measure |
|---|---|---|
| Structural artifact | 3 new files + constructor hook | file existence + unit tests |
| Unit tests | all mocked-boundary tests pass | `pytest tests/test_dropped_threads_extraction.py -q` |
| Substring validation | every emitted event's `text` resolves against the named speaker's turn | in-function assertion + unit test |
| Speaker validation | emitted event's span speaker matches the claimed `raised_by` | unit test |
| Recall on 9 gold | ≥55% | eval script |
| Validation pass rate | ≥90% | eval script |
| Kind agreement vs reviewer consensus | ≥75% | eval script |
| Speaker agreement vs gold | ≥90% | eval script |
| Constructor no-harm (default None) | existing tests pass | `pytest tests -q` |
| Kill criteria | recall <45% OR validation <85% OR fabrication >5% → STOP | PM gate |

## Tasks

- [ ] 0.0 Branch + baseline
- [ ] 1.0 Module scaffolding (prompt tests)
- [ ] 2.0 Span-mode parse + validation + speaker validation
- [ ] 3.0 Observability stats + deterministic issue_id
- [ ] 4.0 Constructor integration (parallel to Phase 5)
- [ ] 5.0 Eval harness on 9 gate items
- [ ] 6.0 Gate check + acceptance memo + docs
- [ ] 7.0 Commit + push + PR

## Risks

1. **Assistant-speaker dimension is new territory.** Only 1 of 9 corpus items is assistant-raised. The specialist might over- or under-emit assistant threads in the wild. Monitor eval extras.
2. **`superseded_by` label quality.** Unlike `text`, this field isn't substring-validated. The LLM can produce anything here. Prompt should constrain it to short paraphrase only.
3. **Paraphrase expansion temptation.** The gate surfaced 2 monolith cases of extractor invention (RE-D1 $950K, UHP-D1 enumeration). The specialist is at risk of the same failure mode; prompt must forbid it explicitly and validation should ignore the display label (which is the exact `text` span, not a paraphrase).
