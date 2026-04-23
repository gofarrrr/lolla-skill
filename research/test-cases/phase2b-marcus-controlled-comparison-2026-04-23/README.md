# Controlled Marcus comparison — Phase 2b Lane 4 (old path vs new path)

**Date:** 2026-04-23
**Phase:** 2b (Lane 4 Structural Coverage migration to `ConversationContext`)
**Purpose:** primary evidence that Phase 2b changes what Lane 4 cites as coverage evidence and how it grounds gap questions — matching the Phase 2a template for a controlled A/B on a real user conversation.

## The controlled setup

- **Same conversation:** `lolla_20260422T155622Z_conversation.txt` (the 9-turn Marcus founder-CEO equity case, same as Phase 2a's controlled comparison)
- **Same fresh extraction:** `marcus_fresh_extraction.json` (reused from Phase 2a — extraction hasn't changed between phases)
- **Only difference between the two pipeline runs:** the Lane 4 input shape. Old path receives a collapsed `CritiqueRequest`; new path receives a `ConversationContext` via `--new-contract`.

Run sequence:

```bash
# Old path (no --new-contract)
python3 scripts/run_pipeline.py --extraction-file marcus_fresh_extraction.json \
                                --conversation-file lolla_20260422T155622Z_conversation.txt \
                                --output-file marcus_old_path_result.json --skip-revision

# New path (--new-contract)
python3 scripts/run_pipeline.py --extraction-file marcus_fresh_extraction.json \
                                --conversation-file lolla_20260422T155622Z_conversation.txt \
                                --output-file marcus_new_path_result.json --skip-revision --new-contract
```

## Lane 4 outputs, side by side

### Question classification (both paths agree)

Both paths: `decision-evaluation`. Marcus is deciding whether to grant equity; no qtype shift on this case (unlike friendship_money and user_has_plan in the 10-case corpus where the user had already decided).

### Dimensions detected (roughly equivalent)

Both paths produced 8 dimensions, 4 gaps. Three of four gap dimensions overlap: `resource-allocation`, `risk-response`, `information-quality`. The fourth differs:

- **Old path** flags `existing-vs-new` (agency vs. platform tension)
- **New path** flags `stakeholder-alignment` (wife, head of design, Jake/Lina, clients)

Neither is wrong. Different reasonable reads of the same conversation.

### Coverage evidence — the architectural shift

**Old path `coverage_evidence` citations** read as summaries of the compiled `vanilla_answer`:

> "Mentions $80K platform sprint opportunity cost but does not identify displaced alternatives..."
>
> "Names risks (Marcus leaves, EBITDA drop, client loss) and sizes downside ($11M vs $5M exit) but does not distinguish mitigate (vesting/IP) vs adapt (succession)..."
>
> "Uses valuation math and constraints as fact without assessing bias..."

The citations describe abstract content. Subject implicit. Reads like analysis of a compiled text artifact, not of a specific reply.

**New path `coverage_evidence` citations** explicitly attribute to the assistant:

> "**Assistant mentions** wife (precedent concerns), head of design (potential precedent ask), Jake/Lina (follow Marcus), clients (trust Marcus), but does not identify positions/supports/opposes..."
>
> "**Assistant proposes** $80K platform sprint but does not identify displaced alternatives..."
>
> "**Assistant names** risks (Marcus leaves, EBITDA drops to $1.5M, 3-5x multiple) and sizes downside ($11M vs $5M exit), but does not distinguish mitigate vs adapt strategies..."

The subject is explicit ("Assistant mentions", "Assistant proposes", "Assistant names"). Lane 4 is citing the assistant's actual content, not the extractor's abstracted summary.

**This is Lane 4's analog to Phase 2a's Lane 3 finding.** Where Lane 3 cited user turns instead of extractor paraphrase, Lane 4 now cites assistant-turn content instead of `vanilla_answer`-style summaries. Same architectural mechanism (CONTEXT/SOURCE split; SOURCE as primary truth), different application point.

### Gap question specificity

New path's gap questions reference Marcus-conversation particulars more concretely:

- **New path stakeholder question:** "Who else in the company, like the **head of design or your wife**, needs to be on board with giving Marcus equity and a board seat before you can move forward?"
- **New path risk question:** "If Marcus leaves and starts a competitor, which clients or tools do you see as most vulnerable..."

These reference specific people + role (wife, head of design, Jake, Lina) and specific risks Marcus raised (Marcus starting a competitor, tools vulnerable). The old path's questions are also reasonable but more abstract.

### Gap question volume (tradeoff, not win)

- Old path: **12 gap questions** (3 per gap × 4 gaps)
- New path: **8 gap questions** (2 per gap × 4 gaps)

New path adheres more strictly to the 2-per-gap side of the "2-3 questions per gap" rule. The gap-question-generation prompt allows 2-3; new path tends to produce 2, old path tends to produce 3. This is volume-tradeoff, not quality regression: the 2 new-path questions are more specific to the Marcus conversation.

**Note on the 10-case corpus:** the gap_questions_mean reduction seen in `../phase2b-lane4-equivalence-2026-04-23/lane4-quality-report.md` aggregate (old 10.3 → new 9.57) is consistent with this pattern. Some cases see larger drops (multi_offer −30%, startup_pivot −44%), which is worth per-case diagnosis in the PR.

## What this shows (and doesn't)

**The architectural claim Phase 2b makes:**
- Old path's Lane 4 reads the extractor's compiled view of the conversation; citations read as analysis of a summary.
- New path's Lane 4 reads the actual assistant turns; citations explicitly attribute ("Assistant mentions", "Assistant proposes") and reference conversation particulars.
- Same-decision audit, different grounding. Matches Lane 3's Phase 2a architectural pattern (user-turn evidence there, assistant-turn evidence here).

**What this doesn't show:**
- That new path produces *more* gap output. It often produces less. The migration's value is in grounding, not volume.
- That new path is better on every case. On Marcus specifically, qtype agrees and dim set mostly overlaps; the win is in coverage_evidence language + gap-question specificity. On the 10-case corpus the picture is more mixed (see aggregate report).

## Companion evidence in this PR

The controlled A/B above is one evidence angle. The PR also includes:

- **10-case corpus measurement** (`../phase2b-lane4-equivalence-2026-04-23/`) — full N=3 per path × 10 cases + per-case patterns.
- **Architecture-vs-volume ablation** on `friendship_money` (see `scripts/phase2b_ablation_architecture_vs_volume.py` + commit `ca88c8e`) — confirms the qtype-shift architectural claim on one case.

Three angles: controlled A/B (Marcus, this directory) + scale measurement (10-case aggregate) + targeted ablation (friendship_money classifier isolation).
