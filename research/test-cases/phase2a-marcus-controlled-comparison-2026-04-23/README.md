# Controlled Marcus comparison — old path vs new path

**Date:** 2026-04-23
**Phase:** 2a (Lane 3 migration to `ConversationContext`)
**Purpose:** primary evidence that Phase 2a changes *what* Lane 3 audits, not just *how* findings are worded.

## The controlled setup

- **Same conversation:** `lolla_20260422T155622Z_conversation.txt` — a 9-turn real user dialogue (the Marcus founder-CEO equity case, the same one appearing in prior stability runs)
- **Same fresh extraction:** `marcus_fresh_extraction.json` — produced by a single `scripts/run_extract.py` invocation, used by both paths
- **Only difference between the two runs:** the Lane 3 input shape. Old path receives a collapsed `CritiqueRequest(query, vanilla_answer)`; new path receives a `ConversationContext` (turns + typed extraction + capture metadata).

Run sequence (see file mtimes: `18:29 / 18:30 / 18:31` on 2026-04-23):

```bash
python3 scripts/run_extract.py  --conversation-file lolla_20260422T155622Z_conversation.txt \
                                --output-file marcus_fresh_extraction.json

python3 scripts/run_pipeline.py --extraction-file marcus_fresh_extraction.json \
                                --conversation-file lolla_20260422T155622Z_conversation.txt \
                                --output-file marcus_old_path_result.json \
                                --skip-revision

python3 scripts/run_pipeline.py --extraction-file marcus_fresh_extraction.json \
                                --conversation-file lolla_20260422T155622Z_conversation.txt \
                                --output-file marcus_new_path_result.json \
                                --skip-revision --new-contract
```

Any qualitative difference in Lane 3 output between `marcus_old_path_result.json` and `marcus_new_path_result.json` is attributable to the input-shape change. Extraction is held constant; the pipeline uses temperature=0.2 so some per-run variance is expected, but the patterns below are structural, not stochastic.

## The Lane 3 outputs, side by side

### OLD path (legacy `CritiqueRequest`)

**Frame element 1 — `assumption` / `binary_collapse`:**
- **evidence_quote:** `"Whether the founder should grant Marcus 15% equity, CTO title, and board seat"`
- This is the extractor's `decision_situation` field, rendered in third person. Not Marcus's own words.

**Frame element 2 — `assumption` / `borrowed_premise`:**
- **evidence_quote:** `"assumes equity ask undervalues founder's founding effort"`
- This is the extractor's meta-labelled interpretation of Marcus's stance. A paraphrased summary of what the extractor thinks Marcus assumes.

**Reframing 1:** "What if the founder grants Marcus 8% equity with vesting, the CTO title, and a board observer seat instead of the full 15% package?"
**Reframing 2:** "How does Marcus's leadership of the 35-person engineering team and 40% technical capability compare to the founder's solo early efforts…"

### NEW path (`ConversationContext`)

**Frame element 1 — `assumption` / `single_actor_assumption`:**
- **evidence_quote:** `"Giving away 15% feels like giving away something I earned"` (verbatim user text; [Turn 1] USER)

**Frame element 2 — `assumption` / `single_actor_assumption`:**
- **evidence_quote:** `"This is MY company. I built it from nothing"` (verbatim user text; [Turn 2] USER)

**Reframing 1:** "What portion of the company's growth from $2M to $14M can be directly attributed to Marcus's contributions like the deployment pipeline and component framework…"
**Reframing 2:** "If Marcus had built the internal tooling and estimation framework as a cofounder from year two, would granting him 15% equity now align with typical founder-cofounder structures…"

## What this shows (not just wording — object of audit)

The old and new paths aren't producing different phrasings of the same finding. They're auditing **different things**:

- **Old path** cites the extractor's third-person *description* of the decision situation. Frame pressure gets applied to the decision space as the extractor reconstructed it ("Whether the founder should grant Marcus…"). The audit is one step removed from the user.
- **New path** cites Marcus's own first-person emotional framing ("feels like giving away something I earned", "MY company. I built it from nothing"). Frame pressure gets applied to the founder-possessiveness stance that *drives* Marcus's equity resistance. The audit is on the user's actual reasoning, not on the extractor's re-statement of it.

This matters because Lane 3's purpose is to surface embedded assumptions that shape the answer space *before reasoning begins*. The founder-possessiveness stance is that embedded assumption in Marcus's case. The old path couldn't anchor to it — the extractor's paraphrase had already smoothed it out into "whether to grant equity" as if it were a neutral decision question. The new path grounds in the first-person possessiveness and pressure-tests *that*.

Same decision. Different audit.

## Implications for Phase 2b / 2c / 2d

This finding is a hypothesis-level signal for the remaining lane migrations, not a prediction:

- **Lane 1 (Structural Pressure)** and **Lane 4 (Structural Coverage)** also consume the collapsed `CritiqueRequest`. They may see analogous audit-quality improvements when migrated — auditing what the user actually reasoned with rather than what the extractor reconstructed.
- **Lane 2 (Companion)** reads `vanilla_answer` more directly (the assistant's reasoning text in full) and does its own fingerprinting from that. The collapsing is less severe for Lane 2, so the expected impact of migration is smaller. Migration will still clarify the contract, but the qualitative delta may be muted.

Each Phase 2 PR will tell us whether the pattern generalizes or is Lane 3-specific. This PR sets the bar.

## Companion evidence in this PR

The controlled comparison above is the cleanest single piece of evidence. The PR also includes:

- **10-case corpus measurement** (`../phase2a-lane3-equivalence-2026-04-23/`) — same pattern across 10 synthetic cases, including the `real_estate` production-bug finding.
- **18 historical production runs** (`/tmp/lolla_2026042*_result.json`) — showing the old-path extractor-paraphrase pattern was present in real user output across multiple days.

Controlled comparison + scale measurement + historical production data = three independent angles on the same conclusion.
