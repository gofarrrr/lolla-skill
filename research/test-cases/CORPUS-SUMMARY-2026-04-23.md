# Test-case corpus results — 2026-04-23

**What this document is:** aggregate findings from running the current shipped extractor against 10 synthetic conversations designed to stress different dimensions. Companion to `/research/test-cases/README.md` (design matrix) and the per-case evidence at `/research/test-cases/corpus-mode-c-2026-04-23/`.

## Headline finding

**Two of ten cases were declined at the strategic-gate** (parenting_teen, friendship_money). Both are personal/family/interpersonal situations with high stakes. The gate's strategic-vs-not definition is currently business-shaped; it excludes personal-life decisions even when those decisions have real material consequence. This is a scope bug, not an extraction bug.

For the 8 cases that did extract, the shipped extractor performs well on most axes — with specific failure modes that correlate with case properties in interpretable ways.

## Per-case Mode C N=3 results

| Case | Turns | decision_situation | original_framing | synthesized_position | live_constraints | reasoning_passages | dropped_threads | Fabricated total |
|---|---|---|---|---|---|---|---|---|
| oncologist | 9 | 0.890 | 0.231 | 0.397 | 0.144 | 0.342 | 0.000 | 0 |
| startup_pivot | 7 | **0.989** | 0.563 | 0.318 | 0.370 | 0.333 | 0.333 | **12** |
| real_estate | 6 | 0.859 | 0.506 | 0.421 | 0.000 | 0.524 | 0.000 | 2 |
| multi_offer | 15 | 0.942 | **0.948** | 0.124 | **0.667** | 0.524 | 0.333 | 0 |
| whistleblower | 14 | **1.000** ⚠ | 0.316 | 0.271 | 0.429 | 0.528 | 0.000 | 3 |
| phd_research | 22 | 0.991 | 0.538 | 0.264 | 0.217 | 0.443 | 0.000 | 1 |
| user_has_plan | 8 | 0.816 | 0.838 | **1.000** ⚠ | 0.200 | **1.000** ⚠ | 0.333 | 0 |
| messy_three_problems | 11 | 0.794 | 0.854 | 0.569 | 0.048 | 0.388 | 0.000 | 2 |

**⚠** = 1.0 Jaccard/similarity. Per the harness doctrine, this is a WARNING signal — it often means the extractor stopped doing semantic judgment and produced near-identical output across runs. For user_has_plan specifically, all 3 runs produced the same `synthesized_position` text verbatim and identical `reasoning_passages` — because the case is so crystallized ("user has decided, wants validation, AI pushes back on specific assumptions") that re-extraction converges trivially.

**Strategic-gate failures (not in table):**
- `parenting_teen`: declined — "personal parenting advice on handling a family crisis involving a minor's online interactions, not a strategic decision in business, professional, or material contexts"
- `friendship_money`: declined — "personal interpersonal dilemma about handling a loan request from a friend, not a strategic business, professional, or material decision"

## Bottleneck findings against the four axes the user named

### Axis 1: amount of information (turn count / total text)

**Not a bottleneck in the tested range (6–22 turns).** The 22-turn phd_research case produced strong decision_situation stability (0.991) and normal behavior across other fields. No truncation triggered on any case; all fit within 80K chars. If there's a length bottleneck, it's above 22 turns — we haven't tested it.

Counterintuitive: `live_constraints` Jaccard actually *improves* with more turns (multi_offer 15 turns = 0.667 Jaccard; real_estate 6 turns = 0.000 Jaccard). More constraints → more chances for overlap.

### Axis 2: amount of detail / density

**Partial bottleneck.** Dense detail correlates with fabrication rate:
- whistleblower (very dense, legal/ethical specifics): 3 fabrications
- phd_research (dense academic detail): 1 fabrication

But doesn't fully explain startup_pivot's 12 fabrications (below).

### Axis 3: messiness

**Real bottleneck on two sub-dimensions:**

3a — **Personal/emotional content hits the strategic-gate.** parenting_teen and friendship_money were both high-stakes with clear decisions; both declined. The gate prompt enumerates business contexts ("business strategy, architecture choices, hiring, investment, product direction…") and the LLM reads this list as exclusive. If `/lolla` is meant to handle personal strategic decisions (and based on the user's corpus design, it is), the gate definition needs expansion — possibly framed as "decisions with material consequences that benefit from structured reasoning" rather than a list of domains.

3b — **Topic-jumping / no-clear-primary-decision degrades live_constraints.** messy_three_problems had `live_constraints` Jaccard 0.048 (near-zero) despite having substantial content. When the conversation has 3 entangled decisions, each run of the extractor picks a different subset as "the constraints," producing almost no overlap across runs.

### Axis 4: size of query / output complexity

**Not observed.** Didn't hit truncation on any case. The long phd_research (22 turns) fit fine and produced healthy extraction. This axis probably kicks in above ~60+ turns or at very long per-turn content. Worth testing at some point but not a PR-blocker.

## The startup_pivot anomaly

`startup_pivot` produced **12 total fabrications across 3 runs** (6, 6, 0 — median 6). This is 3-6× the rate on other cases. Distinguishing features:
- Shortest conversation (7 turns) that PASSED the gate
- Very clean structure (no tangents, no frustration, advisor-style back-and-forth)
- Mostly short assistant turns
- First Mode C run also had 0 reasoning_passages in the final output (all fabricated, retry didn't help)

**Hypothesis:** when the AI responses are short and conversational (rather than prose-heavy), there are fewer long literal substrings the LLM can quote as `reasoning_passages`. The LLM falls back to paraphrasing what the AI said, which is caught as fabrication and dropped.

**This is a specific failure mode of the current retry-then-drop mechanism on short/clean cases.** It's distinct from the saturation pattern we hit on PR #1b/#2/#3. Worth knowing: clean, short conversations stress the fabrication-validation path rather than the stability path.

## The user_has_plan anomaly

`user_has_plan` had `synthesized_position` and `reasoning_passages` at exactly 1.0 Jaccard across runs. The case features a user who has already decided ("I'm quitting to start a consulting practice, help me launch") and asks for tactical advice. The AI pushes back and the user admits foundational gaps.

When all 3 extractions produce identical synthesized_position strings verbatim, the extractor is operating in identity-extraction mode rather than synthesis mode. For this case, the AI's recommendations are so crisp and pointed that there's a single obvious synthesis. That's not necessarily wrong, but the harness doctrine's "1.0 is a warning" applies — it means if the conversation were slightly different in a way that genuinely changed the synthesis, the extractor might not notice.

This isn't a failure per se; it's a case of the extractor being deterministic on a case where the ground truth is narrow. Worth documenting as "case-shape correlated with determinism" for future test design.

## What generalizes from Marcus to the broader corpus

**Clean generalizations (hold across 8/8 passing cases):**
- decision_situation terse-form rule (PR #4a) works — all 8 cases produce decision_situation under 200 chars on first runs, with strong Mode C similarity (0.79–1.00).
- live_constraints ≤120-char rule (PR #1) generally works — constraint text is consistently terse.
- fabricated-quote mechanism fires when it should (short/clean cases) — though it fires too much on startup_pivot, it correctly catches paraphrased content.

**Partial generalizations (hold in some cases but not others):**
- original_framing first-turn-anchor rule (PR #4b) — works on some cases (multi_offer 0.948, user_has_plan 0.838) but not others (oncologist 0.231, whistleblower 0.316). The variance correlates with conversation structure: cases where the opening user turn is a clean single question produce stable original_framing; cases where the opening turn is a messy context dump produce highly variable original_framing across runs.
- dropped_threads count — zero on 5/8 cases, same as Marcus. Confirms the field is inversely correlated with AI-response thoroughness.

**Doesn't generalize (failure modes specific to corpus cases):**
- Strategic-gate excludes personal/family cases (new finding — not visible in Marcus-only testing).
- fabrication rate varies by 10× across cases — Marcus-only testing showed 0-3 fabrications per run set, never 6+ per run.
- 1.0-on-synthesized_position is possible on crystallized cases — never observed on Marcus.

## Specific bottlenecks worth naming (for decision-making about next work)

1. **Strategic-gate bias against personal decisions.** Fixable with a single prompt-text update to the gate definition. Low-risk change, clear benefit. Could ship as PR #11 without touching the extraction prompts at all.

2. **Fabrication rate on short/clean cases.** The retry-then-drop mechanism is too aggressive when the AI's turns don't contain long quotable prose. Either the mechanism needs a fuzzy-match fallback (0.80 token overlap passes), or the extraction prompt needs a different rule for short conversations (e.g., "if no 50+ char verbatim substrings exist, return fewer passages rather than paraphrased ones").

3. **original_framing instability on context-dump opening turns.** The first-turn-anchor rule works when the first user turn is a clean question but not when it's a paragraph of background + question. Fixable by anchoring more specifically: "capture the question or ambiguity in the first user turn, not the background content."

4. **messy/multi-thread conversations produce unstable live_constraints.** No quick fix via prompt-engineering given the saturation pattern we hit earlier. This is a case shape where Track A decomposition would likely help — each specialist extracts its field independently, removing the attention-competition problem that's particularly bad on multi-thread cases.

## Recommended next steps (not acting yet — surfacing for user decision)

**Ordered by cost/benefit:**

1. **Ship PR #11 — update strategic-gate to include personal strategic decisions.** Very cheap (one prompt edit to the gate text). Unblocks 20% of real-world cases. Low pollution risk (gate text is separate from field extractions).

2. **Investigate startup_pivot fabrication pattern.** Diagnostic work, not a PR. Understand whether it's a general short-conversation issue or specific to this case's style. If general, may motivate a retry-mechanism enhancement.

3. **Wait on Track A.** The messy-conversation bottleneck and the saturation patterns we hit earlier both point at the same architectural unblock. Don't re-attempt paused PRs until Track A exists.

4. **Expand the corpus as real non-Marcus cases accumulate.** This synthetic corpus gave directional signal; real cases will eventually test whether synthetic biases matter.

## Evidence directories

- Per-case Mode C outputs: `/research/test-cases/corpus-mode-c-2026-04-23/<case>/drift.json|md|runs.txt|config.json`
- Case conversations: `/research/test-cases/case_<name>_conversation.txt`
- This summary: `/research/test-cases/CORPUS-SUMMARY-2026-04-23.md`
- Design matrix: `/research/test-cases/README.md`
