# Phase 5: Live-Constraints Specialist Extraction

**Future branch:** `feat/conversation-first-phase-5-live-constraints`
**Roadmap:** `plans/conversation-first-context-engineering-roadmap.md` -> Phase 5
**Phase 5.0 gate:** `research/phase5-user-side-specialist-annotation-gate-2026-04-24.md` (PASS: 75% span / 0% NONE / 87.5% kind)
**Phase 2 blocking memo:** `research/phase2-user-side-index-gold-annotations-2026-04-24.md` (10-case study: 0/71 full spans, 11% evidence spans)
**Phase 3b precedent:** `engine/system_b/stance_extraction.py`, `scripts/phase3b_stance_extraction_eval.py`
**Scope:** add an injectable LLM-backed `live_constraints` specialist that emits `UserIssueEvent` objects with `SpanProvenance` (verbatim user-turn substrings) or `DerivationProvenance` (cross-turn synthesis). Do not touch `dropped_threads`, `original_framing`, or `decision_situation` — each of those gets its own gate + specialist in a later phase. Do not change lane behavior, the constructor's deterministic path, or the monolith extractor.

## Why This Phase

Phase 2's 10-case study established that current extraction is architecturally paraphrase-first: **0 of 71** user-side objects have a full exact substring in their declared source turn, only **8 of 71 (11%)** have even a 4-word evidence fragment. The monolith extractor cannot produce the verbatim anchors downstream consumers need.

Phase 5.0's annotation gate proved that **the task is learnable at the span level**: two reviewers independently picked converging spans on 75% of 20 `live_constraint` candidates, with 0% non-recoverable and 87.5% kind agreement. The gate also surfaced a real pattern — **25% of paraphrased `live_constraints` are cross-turn derivations**, not single-span — which the specialist must accommodate.

Phase 5 builds the first specialist extractor and the pattern for the next four. It mirrors Phase 3b's approach (stance extraction) which shipped successfully at 60% recall / 97% validation / 0% fabrication.

## Approved Phase 5 Decisions

From the Phase 5.0 gate + Phase 2 memo:

- **Scope strictly `live_constraints`.** Other user-side fields deferred. Each gets its own gate before its specialist is built.
- **Two output modes, one prompt:** `span` (single verbatim substring from one user turn) OR `derivation` (issue synthesized across 2+ user turns). The LLM picks; the validator enforces each.
- **Reuse Phase 1 provenance union.** `UserIssueEvent.provenance` already accepts `SpanProvenance | TurnRefProvenance | DerivationProvenance`. No IR schema changes.
- **SOURCE = user turns only.** Assistant turns appear in CONTEXT for understanding what the user responded to but are never quotable (constraints are user-side facts).
- **Kind vocabulary: `constraint` | `concern` | `open_loop`** — the Phase 1 three-kind taxonomy. Specialist prompt carries the same definitions as the gate doc.
- **`kind_ambiguity: bool = False`** on the emitted `UserIssueEvent`. Set when the span genuinely carries both `constraint` and `concern` semantics. Primary kind stays single (dominant reading).
- **Validation is substring-based** via `find_substring_tolerant` (from PR #22). Paraphrase/hallucination fails validation and gets dropped + counted.
- **Derivation validation** is weaker: the LLM must provide `turn_refs` pointing to existing user turns, and for each turn a `span_excerpt` that passes substring validation on that turn. No turn without a verifiable excerpt.
- **Injectable via constructor hook**, same pattern as Phase 3b's `stance_extractor=`. Default `None` preserves deterministic Phase 1 behavior.
- **Monolith extractor stays.** Phase 5 runs in addition. When the specialist emits events, they REPLACE the monolith's paraphrased `live_constraints` output in the IR (constructor logic). No dual-write.
- **Gold set:** the 20 Phase 5.0 gate items become eval gold. 15 single-span items score span convergence; 5 cross-turn items score derivation correctness.
- **No Phase 5b iteration before ship.** The Phase 3b experience (prompt iteration bought marginal recall, lost commitment recall on other items) argues for accepting a first-pass baseline and moving on unless a specific downstream consumer needs higher recall.

## Relevant Files

- `engine/system_b/live_constraints_extraction.py` — **NEW**. LLM-backed specialist. Mirrors `stance_extraction.py` structure.
- `engine/system_b/ir_constructor.py` — extend with an optional `live_constraints_extractor` hook. When provided, specialist output replaces the monolith's `live_constraints` mapping.
- `engine/system_b/ir.py` — read only. `UserIssueEvent.provenance` already accepts the full union.
- `engine/system_b/boundary_validation.py` — read only. `coerce_str` and `require_list_of_dicts` reused from Phase 3b.
- `engine/system_b/text_matching.py` — read only. `find_substring_tolerant` reused.
- `engine/system_b/conversation_context.py` — read only. `ConversationContext` as input.
- `engine/system_b/boundary_provider.py` — read only. `load_boundary_client_from_env` for the eval script.
- `scripts/phase5_live_constraints_eval.py` — **NEW**. Live eval against the 20 gate items. Writes `research/phase5-live-constraints-eval-2026-04-24.md`.
- `tests/test_live_constraints_extraction.py` — **NEW**. Mocked-boundary unit tests: prompt shape, parse + validation logic, span and derivation modes, constructor integration.
- `research/phase5-user-side-specialist-annotation-gate-2026-04-24.md` — read only. Gate doc contains the 20 gold spans.

### Notes

- Do not start implementation until PM approves this task file.
- Do not create a new branch until task 0.0 begins.
- Do not add new IR fields or provenance tiers — the Phase 1 union covers both output modes.
- Do not migrate `dropped_threads`, `original_framing`, or `decision_situation` in this PR, even opportunistically. Each needs its own gate.
- Do not mutate the monolith extractor's prompt. Phase 5 runs as an additional layer; the monolith remains for the fields Phase 5 doesn't yet own.
- Do not add CLI flags or runtime toggles — the injection point is constructor-level.
- Do not lower the validation threshold to "accept paraphrase that looks close." Validation stays substring-exact (case-tolerant).

## Testing Approach

Vertical TDD slices, mirroring Phase 3b:

1. RED: one behavior test (mocked boundary).
2. GREEN: smallest code to pass.
3. REFACTOR: clean only after the slice is green.

Good TDD targets:

- prompt shape (CONTEXT / SOURCE split, user-turns-only in SOURCE, kind taxonomy named, output JSON schema fixed)
- parse + validation for `span` output mode (substring-tolerant match against the claimed user turn)
- parse + validation for `derivation` output mode (turn_refs list, each with verifiable excerpt)
- kind vocabulary enforcement
- `kind_ambiguity` flag carry-through
- SpanRef exact-char position computation (identical to `stance_extraction.py` pattern)
- constructor integration (replaces monolith's paraphrased `live_constraints` mapping when extractor is injected; untouched when not)
- constructor resilience (extractor exception → WARNING log + empty events, rest of IR still builds)
- deterministic `issue_id` for stable test assertions

Not TDD'd:

- live LLM calls. The eval script measures against the 20 gate items as a separate gated step.
- exact recall/validation/kind-agreement numbers. Those are live measurements, reported in the eval artifact.
- prompt wording. Measured via eval, iterated only if a kill-criterion is tripped.

## Acceptance Gate

| Axis | Target | How to measure |
|---|---|---|
| Structural artifact | `live_constraints_extraction.py`, `scripts/phase5_live_constraints_eval.py`, `tests/test_live_constraints_extraction.py`, constructor hook | file existence + unit tests |
| Unit tests | all mocked-boundary tests pass | `pytest tests/test_live_constraints_extraction.py -q` |
| Substring validation | every emitted span-mode event's `text` resolves via `find_substring_tolerant` against the named user turn | in-function assertion + unit test |
| Derivation validation | every emitted derivation-mode event's `turn_refs` all exist; each has a valid `span_excerpt` | in-function assertion + unit test |
| Recall on 20 gold | ≥55% (matches Phase 3b ship baseline; 11/20 items minimum) | `scripts/phase5_live_constraints_eval.py` |
| Validation pass rate | ≥90% of LLM outputs survive validation (dropped count <10%) | eval script metric |
| Kind agreement vs reviewer consensus | ≥75% of matched events have correct primary kind | eval script metric |
| Span convergence vs gate gold | for single-span gold (15 items), ≥60% of LLM spans pass reviewer span-convergence scoring | eval script metric |
| Derivation recall | for cross-turn gold (5 items), ≥40% get recognized as derivation-mode events | eval script metric |
| Constructor no-harm | existing tests pass with default (no extractor injected) | `pytest tests -q` |
| Lane behavior | unchanged | existing pipeline tests stay green |
| Cost/latency | one specialist call per run; local p50 recorded in eval artifact; no new runtime dependencies | eval report |
| Kill criteria | recall <45% OR validation <85% OR fabrication >5% → STOP, blocker memo; do NOT iterate the prompt more than twice | PM gate |

## Tasks

- [ ] 0.0 Create feature branch and verify baseline
  - [ ] 0.1 Confirm current branch and clean tree: `git branch --show-current` and `git status --short`.
  - [ ] 0.2 Confirm Phase 5.0 gate artifact exists and passed: `research/phase5-user-side-specialist-annotation-gate-2026-04-24.md` committed at `cfae277`.
  - [ ] 0.3 Create and check out: `git switch -c feat/conversation-first-phase-5-live-constraints`.
  - [ ] 0.4 Run baseline: `python3 -m pytest tests/test_ir.py tests/test_stance_extraction.py tests/test_pipeline_shim_equivalence.py -q`. Record pass count in this task file.

- [ ] 1.0 Define specialist module scaffolding (TDD)
  - [ ] 1.1 RED: add `tests/test_live_constraints_extraction.py::test_system_prompt_names_the_three_kinds_exactly` using the `VALID_KINDS` constant tuple.
  - [ ] 1.2 GREEN: create `engine/system_b/live_constraints_extraction.py` with module docstring, `VALID_KINDS = ("constraint", "concern", "open_loop")`, and `LIVE_CONSTRAINTS_SYSTEM_PROMPT` placeholder.
  - [ ] 1.3 RED: test the system prompt requires verbatim-substring evidence (string matches "substring" and mentions "user turns").
  - [ ] 1.4 GREEN: draft the system prompt. Mirror `STANCE_EXTRACTION_SYSTEM_PROMPT` structure: task framing, include/exclude rules, three-kind taxonomy with the same definitions as the gate doc, composite `kind_ambiguity` handling, output JSON schema with both `span` and `derivation` modes.
  - [ ] 1.5 RED: test the system prompt explicitly supports derivation mode (string mentions "derivation" or "cross-turn").
  - [ ] 1.6 GREEN: include the derivation-mode schema in the system prompt.
  - [ ] 1.7 RED: test `_format_user_prompt(context)` produces CONTEXT + SOURCE split; SOURCE contains user turns only; assistant turns appear in CONTEXT prefixed as context-only.
  - [ ] 1.8 GREEN: implement `_format_user_prompt`. Mirror `stance_extraction.py:120-149` pattern but invert the speaker split: assistant = CONTEXT, user = SOURCE.
  - [ ] 1.9 Run `pytest tests/test_live_constraints_extraction.py -q`. Expect early tests green.

- [ ] 2.0 Implement span-mode parse + validation (TDD)
  - [ ] 2.1 RED: test `extract_live_constraints(context=ctx, boundary=_FakeBoundary(...))` with a canned span-mode payload returns one `UserIssueEvent` with `SpanProvenance`, correct kind, and exact-char-position `SpanRef`.
  - [ ] 2.2 GREEN: implement `extract_live_constraints`. Start with span-mode only: parse `{"live_constraints": [{"mode": "span", "text": ..., "turn_index": ..., "kind": ..., "kind_ambiguity": ...}]}`; validate kind in `VALID_KINDS`; validate `text` as substring of the claimed user turn via `find_substring_tolerant`; compute `SpanRef` positions; emit `UserIssueEvent(provenance=SpanProvenance(span_ref=...))`.
  - [ ] 2.3 RED: test invalid kind is dropped with `dropped_invalid_kind` incremented.
  - [ ] 2.4 GREEN: add kind validation + drop counter.
  - [ ] 2.5 RED: test non-substring `text` is dropped with `dropped_not_substring` incremented.
  - [ ] 2.6 GREEN: add substring drop counter.
  - [ ] 2.7 RED: test `turn_index` pointing at an assistant turn is dropped with `dropped_invalid_turn` incremented.
  - [ ] 2.8 GREEN: add user-speaker check + drop counter.
  - [ ] 2.9 RED: test case-tolerant match preserves the transcript's original casing (pattern from `stance_extraction.py:231-240`).
  - [ ] 2.10 GREEN: reuse the `find_substring_tolerant` → `turn_text.find(matched)` fallback pattern verbatim.
  - [ ] 2.11 RED: test `kind_ambiguity=True` from the LLM payload is preserved on the emitted `UserIssueEvent`.
  - [ ] 2.12 GREEN: propagate the flag.
  - [ ] 2.13 Run `pytest tests/test_live_constraints_extraction.py -q`.

- [ ] 3.0 Implement derivation-mode parse + validation (TDD)
  - [ ] 3.1 RED: test a canned derivation-mode payload `{"mode": "derivation", "turn_refs": [{"turn_index": 1, "span_excerpt": "..."}, {"turn_index": 2, "span_excerpt": "..."}], "kind": ..., "text": "combined paraphrase label"}` returns one `UserIssueEvent` with `DerivationProvenance`.
  - [ ] 3.2 GREEN: implement derivation-mode parse. `DerivationProvenance` requires at least one `turn_ref`; store the combined paraphrase in `UserIssueEvent.text` (this is the only object where `text` is NOT substring-validated because it is an intentional label).
  - [ ] 3.3 RED: test each `span_excerpt` must substring-validate against its claimed turn; excerpts that fail are dropped and if none survive, the whole derivation event is dropped with `dropped_derivation_no_valid_excerpt`.
  - [ ] 3.4 GREEN: validate excerpts per-turn; reject event if zero valid excerpts remain.
  - [ ] 3.5 RED: test a derivation event referencing only one turn is downgraded to span mode (re-emit as `SpanProvenance` using that one excerpt; don't waste a derivation tier on single-turn content).
  - [ ] 3.6 GREEN: implement the downgrade path.
  - [ ] 3.7 RED: test a `turn_ref` pointing at an assistant turn is dropped with `dropped_invalid_turn` incremented; if it was the only turn_ref, the whole event is dropped.
  - [ ] 3.8 GREEN: assistant-turn filter for derivation mode.
  - [ ] 3.9 RED: test derivation events carry `kind_ambiguity` identically to span mode.
  - [ ] 3.10 GREEN: propagate.
  - [ ] 3.11 Run `pytest tests/test_live_constraints_extraction.py -q`.

- [ ] 4.0 Observability: stats + deterministic issue_id (TDD)
  - [ ] 4.1 RED: test `extract_live_constraints` returns a `_ValidationStats` tuple with fields `raw_count`, `validated_count`, `span_mode_count`, `derivation_mode_count`, `dropped_invalid_kind`, `dropped_invalid_turn`, `dropped_not_substring`, `dropped_derivation_no_valid_excerpt`.
  - [ ] 4.2 GREEN: implement the dataclass and populate counters.
  - [ ] 4.3 RED: test `issue_id` is deterministic: two runs on the same `(turn_index, kind, text_hash)` input produce identical ids.
  - [ ] 4.4 GREEN: implement id like `live_constraint_t{turn}_{kind}_{hash12}` (hash excerpt of text) for span mode; derivation uses `live_constraint_derivation_{hash12}` over the combined turn_refs + text.
  - [ ] 4.5 RED: test an INFO-level log fires with raw/validated/per-drop counts.
  - [ ] 4.6 GREEN: emit the log via `_LOGGER = logging.getLogger("system_b.live_constraints_extraction")`.

- [ ] 5.0 Constructor integration (TDD)
  - [ ] 5.1 RED: test `construct_conversation_ir(context, live_constraints_extractor=None)` leaves `user_issue_events` populated from the monolith's `live_constraints` (today's behavior).
  - [ ] 5.2 GREEN: confirm default None preserves Phase-1 path.
  - [ ] 5.3 RED: test `construct_conversation_ir(context, live_constraints_extractor=my_specialist)` REPLACES the monolith's `live_constraint` → `UserIssueEvent` mapping with the specialist's output. `dropped_threads` → `UserIssueEvent` mapping remains from the monolith.
  - [ ] 5.4 GREEN: thread the hook into the constructor. When provided: skip the `context.extraction.live_constraints` loop; run the specialist; reduce the returned events onto the IR. `dropped_threads` still map from the monolith.
  - [ ] 5.5 RED: test the specialist-emitted events have `speaker="user"` and preserve `kind_ambiguity` end-to-end.
  - [ ] 5.6 GREEN: set `speaker="user"` in the specialist emit path.
  - [ ] 5.7 RED: test constructor continues when specialist raises (WARNING log, empty `live_constraint` events from specialist path, rest of IR still builds).
  - [ ] 5.8 GREEN: wrap specialist call in try/except like the `stance_extractor` pattern (`ir_constructor.py:142-149`).
  - [ ] 5.9 RED: test `ConversationIR.provenance_tier_counts()` reflects the specialist's mix of `span` and `derivation` events when injected.
  - [ ] 5.10 GREEN: no code change needed if reducers are correct; test serves as the integration invariant.
  - [ ] 5.11 Run `pytest tests/test_live_constraints_extraction.py tests/test_ir.py -q`.

- [ ] 6.0 Eval harness on 20 gate items
  - [ ] 6.1 Create `scripts/phase5_live_constraints_eval.py` mirroring `scripts/phase3b_stance_extraction_eval.py` structure.
  - [ ] 6.2 Hard-code the 20 gold items from the gate doc: `GOLD = {case: [(item_id, expected_kind, expected_span_snippet, mode), ...]}`. For single-span items (15), mode is `span` and `expected_span_snippet` is a ≥8-token excerpt from the reviewer-convergent span. For cross-turn items (5), mode is `derivation` and the gold carries a tuple of turn_indexes with excerpts.
  - [ ] 6.3 For each of the 5 cases, run `extract_live_constraints(context, boundary=live_openrouter)` and match LLM output against gold.
  - [ ] 6.4 Score: recall (gold items found), validation pass rate (raw vs validated), kind agreement (matched items), span convergence (single-span gold — ≥30% shared tokens with reviewer span), derivation recall (cross-turn gold — specialist emitted as derivation mode).
  - [ ] 6.5 Write `research/phase5-live-constraints-eval-2026-04-24.md` with aggregates + per-case breakdown + mismatches.
  - [ ] 6.6 Cost: ~$1-3 across 5 LLM calls. Do NOT run until the task file is PM-approved and branch is created.

- [ ] 7.0 Gate check against acceptance thresholds
  - [ ] 7.1 Run `scripts/phase5_live_constraints_eval.py`.
  - [ ] 7.2 Confirm: recall ≥55%, validation ≥90%, kind agreement ≥75%, span convergence ≥60%, derivation recall ≥40%.
  - [ ] 7.3 If any threshold fails: STOP, write a blocker memo summarizing what failed and why, and return to PM. Do not iterate the prompt more than twice in total before PM review.
  - [ ] 7.4 If fabrication (events that fail substring validation) exceeds 5% of raw output: STOP, the specialist is not safe to ship.
  - [ ] 7.5 Record measured numbers in this task file and in the eval artifact.

- [ ] 8.0 Verification + documentation
  - [ ] 8.1 Run specialist unit tests: `pytest tests/test_live_constraints_extraction.py -q`.
  - [ ] 8.2 Run IR + constructor tests: `pytest tests/test_ir.py tests/test_ir_drillback.py tests/test_stance_extraction.py -q`.
  - [ ] 8.3 Run full suite: `pytest tests -q`. Expect zero new failures relative to baseline.
  - [ ] 8.4 Verify lane output surfaces unchanged (pipeline shim + runtime contract tests green).
  - [ ] 8.5 Update `HOW_IT_WORKS.md` with a short Phase 5 paragraph after the Phase 3b / IR section.
  - [ ] 8.6 Update `plans/conversation-first-context-engineering-roadmap.md` only if implementation materially changed the approved Phase 5 shape.
  - [ ] 8.7 Write a Phase 5 acceptance note summarizing: recall, validation, kind agreement, span convergence, derivation recall, latency, cost per run, residual risks.
  - [ ] 8.8 Stop for PM review before PR creation if any gate is ambiguous.
  - [ ] 8.9 Commit and open PR after all gates are satisfied.

## Phase 6-7 Preview (Do Not Do In This PR)

- **Phase 5 (next): dropped_threads specialist.** Needs its own annotation gate first. Structure identical to Phase 5.
- **Phase 5 (after): original_framing specialist.** Multi-turn synthesis — likely derivation-only. Needs its own gate.
- **Phase 5 (last): decision_situation specialist.** Similar to original_framing.
- **Phase 6: remove legacy CritiqueRequest shim** once all four specialists ship.
- **Phase 7: split pipeline.py**.

These are out of scope for Phase 5 v1.

## Risks

1. **LLM plateaus.** Phase 3b's experience: prompt iteration gave marginal recall gains and Pareto trade-offs. If live measurement shows recall below 55%, resist prompt-wrestling; consider narrowing the `live_constraint` definition or deferring the cross-turn mode instead.
2. **Mode confusion.** If the LLM emits derivation-mode for things that are trivially single-span (or vice versa), validation will accept them but provenance tiering becomes noisy. The 5-item derivation gold set is specifically sized to catch this.
3. **Span-scope kind ambiguity.** Gate finding: `kind_ambiguity=yes` correlates with longer spans. The specialist's kind judgment should be anchored to the span it's emitting, not the surrounding context.
4. **Monolith drift.** Phase 5 does not touch the monolith prompt, but the two extractors can disagree (monolith says 4 constraints, specialist says 6). Constructor logic makes the specialist authoritative when injected. Monitor observability for large count deltas — may indicate either specialist over-emission or monolith under-emission.
5. **Substring validation false negatives.** `find_substring_tolerant` handles case folding but not punctuation or whitespace drift. If recall is low and many drops are "close but not exact" substrings, the fix is a tighter LLM prompt, not a looser validator.
6. **Derivation abuse.** If the LLM over-uses derivation mode to work around substring validation (emitting loose paraphrases + vague turn_refs), span convergence will be fine but recall on single-span gold will collapse. The 15-item single-span gold catches this.
7. **Integration regressions.** The constructor change is the riskiest seam. Default-None path must stay byte-identical to current output; a unit test enforces this.
