# Controlled Marcus comparison — Phase 2c Lane 1 (old path vs new path)

**Date:** 2026-04-24
**Phase:** 2c (Lane 1 Structural Pressure migration to `ConversationContext`)
**Purpose:** primary evidence that Phase 2c changes what Lane 1 attends to when auditing the assistant's reasoning — matching the 2a/2b template of a controlled A/B on a real user conversation.

## The controlled setup

- **Same conversation:** `lolla_20260422T155622Z_conversation.txt` (9-turn Marcus founder-CEO equity case, reused from Phase 2a/2b).
- **Same fresh extraction:** `marcus_fresh_extraction.json` (extraction hasn't changed since 2a; reusing keeps the variable isolated).
- **Same pipeline code path downstream of Lane 1:** routing + compound detection + DeltaCard assembly are shape-invariant to input shape — they operate on DeepCheckResult objects whose structure does not depend on Pass 1/Pass 2 prompt shape.
- **The ONLY changed variable:** whether Lane 1's Pass 1 + Pass 2 consume the legacy `query + vanilla_answer` shape or the new `ConversationContext` shape with CONTEXT/SOURCE split and turn-structured assistant content.

Artifacts:
- `marcus_old_path_result.json` — `--skip-revision` (no flag passed for `--new-contract`)
- `marcus_new_path_result.json` — `--skip-revision --new-contract`

## Lane 1 output comparison

### Old path (legacy `CritiqueRequest`)

- **detected_tendencies:** `['availability-misweighing-tendency', 'inconsistency-avoidance-tendency']`
- **findings:** 2 total, both severity=`high`, both in top_findings
- **compound_groups:** 0
- **selected_model_ids:** 6 (`base-rates`, `statistics-concepts`, `scientific-method-evidence-testing`, `status-quo-bias`, `step-back`, `tradition-vs-innovation-balance`)

**Finding 1** — `availability-misweighing-tendency` / `vivid-proof-substitution` / high
> Using Tom's departure to inform the Marcus decision is like saying 'I got a flat tire once so I know what a car accident…

**Finding 2** — `inconsistency-avoidance-tendency` / `status-quo-protection` / high
> Both of these cannot be true at the same time. If Marcus is truly responsible for 40% of your technical capability…

### New path (ConversationContext + CONTEXT/SOURCE)

- **detected_tendencies:** `['deprival-superreaction-tendency', 'availability-misweighing-tendency', 'contrast-misreaction-tendency']`
- **findings:** 3 total, all severity=`medium`, 1 in top_findings
- **compound_groups:** 0
- **selected_model_ids:** 7 (`expected-value`, `probabilistic-thinking`, `base-rates`, `statistics-concepts`, `scientific-method-evidence-testing`, `constraints`, `formal-reasoning`)

**Finding 1** — `availability-misweighing-tendency` / `vivid-proof-substitution` / medium
> The Tom situation. You're using Tom as a data point, but it's the wrong comparison. Tom was a senior designer. Marcus is…

**Finding 2** — `deprival-superreaction-tendency` / `general` / medium
> The difference between an $11M exit and a $5M exit is $6M. You're worried about giving away $1.3-2M to protect $6M of va…

**Finding 3** — `contrast-misreaction-tendency` / `general` / medium
> The difference between an $11M exit and a $5M exit is $6M. You're worried about giving away $1.3-2M to protect $6M of va…

## What the architectural shift changes

### Shared (both paths)

- Both detect `availability-misweighing-tendency` with the same sub_pattern (`vivid-proof-substitution`). The Tom analogy is the clearest failure mode in the assistant's reasoning; both paths see it.
- Both paths produce a non-trivial `selected_model_ids` set (6 vs 7) that overlaps on 3 models (`base-rates`, `statistics-concepts`, `scientific-method-evidence-testing`).

### Where the paths diverge

1. **New path picks up financial-framing tendencies the old path missed:**
   - `deprival-superreaction-tendency`: assistant frames the $6M gap as "protecting $6M" — an explicit loss-aversion move.
   - `contrast-misreaction-tendency`: same passage, seen through a comparison-frame lens ($11M vs $5M anchoring).
   - Both cite a specific numerical passage from an assistant turn: "$11M exit and a $5M exit is $6M. You're worried about giving away $1.3-2M to protect $6M…" This is the kind of verbatim quantitative reasoning that gets smoothed into paraphrase when the assistant turns are concatenated into `vanilla_answer`.

2. **Old path picks up inconsistency-avoidance that new path doesn't:**
   - `inconsistency-avoidance-tendency` / `status-quo-protection`: "Both of these cannot be true at the same time. If Marcus is truly responsible for 40%..."
   - This is the assistant naming the user's own inconsistency. The new path's Pass 1 / Pass 2 may have classified this as commentary-about-the-user rather than a tendency in the assistant's own reasoning.

3. **Evidence-passage grounding shifts toward verbatim assistant turns:**
   - Old-path passages read as flattened narrative extracts ("Using Tom's departure to inform the Marcus decision is like saying…").
   - New-path passages read as verbatim assistant turns ("The Tom situation. You're using Tom as a data point…") — the turn structure is visible in the evidence.
   - Same architectural mechanism as 2a Lane 3's shift from extractor-paraphrase to user-turn substrings, and 2b Lane 4's coverage_evidence shift to "Assistant mentions…". Applied one lane deeper into the critique pipeline.

4. **Severity calibration looks different:**
   - Old path: both findings `high`.
   - New path: all three findings `medium`.
   - Not a regression — the new path detects more tendencies but flags each at lower confidence / severity. This is consistent with the LLM being more calibrated when it audits specific assistant-turn evidence rather than a synthesized flat text.

### Anti-echo cascade (Lane 1 → Lanes 2/3/4)

- `selected_model_ids` shifts from 6 models to 7, with partial overlap. Downstream anti-echo sets will differ.
- New path adds `expected-value`, `probabilistic-thinking`, `constraints`, `formal-reasoning`; drops `status-quo-bias`, `step-back`, `tradition-vs-innovation-balance`.
- This cascade is observable in the 10-case measurement's Lane 2/3/4 per-run counts.

## How to read this vs 2a/2b's Marcus A/B

- **2a (Lane 3):** architectural win was mechanically provable — drop-rate for unsupported frame elements went from 33% to 0% via substring validation. Clean binary evidence.
- **2b (Lane 4):** architectural claim was attribution-language (coverage_evidence citations attributed to assistant turns instead of paraphrases). Cleanest single-case evidence was same gap_qs count + same dim_ids with ONLY the attribution language differing after prompt iteration.
- **2c (Lane 1):** the architectural claim is that **turn-structured assistant content changes WHAT Lane 1 attends to** — the financial-framing tendencies (deprival + contrast) live in a specific numerical passage that's visible as a discrete assistant turn but blurs when concatenated. This is a more qualitative-judgment piece of evidence than 2a or 2b. It is strongest when read as "what the new path sees that the old path misses, and vice versa."

## Open question for PM review

The old path's `inconsistency-avoidance` detection and the new path's `deprival-superreaction` + `contrast-misreaction` detections are both plausible; neither is obviously wrong. On Marcus specifically, is "the assistant frames $6M as loss to protect" (new) more or less material than "the assistant calls out user's inconsistent 40%-value framing" (old)?

Both are real signals in the assistant's reasoning. The new path produces more coverage (3 vs 2 findings), at the cost of lower per-finding severity calibration. Net: more breadth, less per-finding weight. The 10-case aggregate shows whether that tradeoff holds corpus-wide.
