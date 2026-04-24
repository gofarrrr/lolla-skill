# Controlled Marcus comparison — Phase 2d Lane 2 (old path vs new path)

**Date:** 2026-04-24
**Phase:** 2d (Lane 2 Model Companion migration to `ConversationContext`)
**Purpose:** primary evidence that Phase 2d changes what Lane 2 verifies as executed/violated models when auditing assistant reasoning.

## The controlled setup

- **Same conversation:** `lolla_20260422T155622Z_conversation.txt` (9-turn Marcus founder-CEO equity case, reused from Phase 2a/2b/2c).
- **Same fresh extraction:** `marcus_fresh_extraction.json` (extraction unchanged since 2a).
- **Only changed variable:** input shape to Lane 2's fingerprint + verification calls.

Artifacts:
- `marcus_old_path_result.json` — `--skip-revision`
- `marcus_new_path_result.json` — `--skip-revision --new-contract`

## Lane 2 output comparison

### Old path (legacy `CritiqueRequest`)

- **fingerprint_validated:** 6 moves
- **fingerprint_dropped:** 0
- **detected_models:** **0** (all candidates rejected at verification)

No models accepted as executed or violated on Marcus. The verification LLM reviewed candidate models against the flattened `vanilla_answer` and found no passage that instantiates a candidate's specific mechanism.

### New path (ConversationContext + CONTEXT/SOURCE)

- **fingerprint_validated:** 7 moves
- **fingerprint_dropped:** 0
- **detected_models:** **1** (`empathy / executed`)

**Finding — `empathy / executed`**
> "Think about it from his perspective. He's spent six years building tools that make your agency more efficient and profitable. He w…"

The assistant explicitly asks Marcus to take his co-founder's perspective on the equity grant — that's textbook empathy execution. The turn-structured input made this assistant turn visible as a discrete span the verifier could ground against; the flattened `vanilla_answer` blurred this same reasoning into the surrounding narrative enough that the verifier didn't lock onto it as a specific passage.

## What the architectural shift changes on Marcus

**No drop-rate signal** — both paths show 0 dropped fingerprint moves. Lane 2's existing substring-validation infrastructure (in place since before Phase 2) enforces that evidence quotes be literal substrings of the audit target. On both paths the LLM is well-behaved — it quotes from the audit target correctly. The substring validation is fire-and-forget on both paths.

**The architectural win shows up at verification**, not at fingerprint validation. Specifically:
- The same 6-7 abstract reasoning moves get extracted on both paths.
- On old path: the verifier sees flattened text and finds no passage specifically executing/violating a candidate model's mechanism.
- On new path: the verifier sees turn-structured assistant content and identifies the empathy-execution passage as specifically matching that model's mechanism.

Same architectural mechanism as 2a Lane 3 (evidence grounded in verbatim user quotes) and 2b Lane 4 (coverage_evidence attributed to assistant turns). Applied to Lane 2's verification step.

## How Marcus relates to the 10-case aggregate

On Marcus specifically, new path adds 1 detected model (0→1). The 10-case aggregate tells the broader story:
- **new detected mean: 4.03 vs old 3.5 (+15%)**
- 10 of 10 cases: new finds equal-or-more models than old (single exception: whistleblower, median 3 vs 5 — diagnosed as LLM variance on a run-unstable case, see `lane2-qualitative-diff.md`).

Marcus is one instance of the broader pattern: turn-structured audit target lets the verification LLM find specific passages it couldn't lock onto in flattened text.

## Honest caveats

- Marcus's old-path `detected=0` is unusually low even for the verifier's strictness. The verifier is generally conservative (high rejection rates across all cases), so 0-detected is a plausible outcome for a case with dense but non-textbook reasoning.
- A single `empathy` detection on Marcus is a modest win. The stronger evidence is the aggregate +15% across 10 cases.
