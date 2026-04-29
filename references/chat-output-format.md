# Chat Output Format (Step 4)

## What this file is

The render specification for the Step 4 chat summary. SKILL.md tells you to load this file at the start of Step 4. Apply it after reading `output-field-guide.md`.

Step 4 produces a focused chat summary, not a full card dump. Detailed card rendering lives in the Observatory. The chat output uses a "finish/start/finish" structure: open with the single most important finding, walk through 2–3 highest-signal findings across all lanes, then hand off to Step 6 for the turn.

## Design principles

From presentation research (`references/presentation-research.md`):

- **BLUF**: the most important structural weakness in the first sentence.
- **Maximum 3–5 findings across ALL lanes combined** — pick by signal, not by lane completeness.
- **One bridge sentence per finding** — connects the abstract pattern to THIS conversation.
- **No template scaffolding**, no severity labels, no JSON field names in chat output.
- **No formatting overload** — bold for finding names only, not for every field label.
- **The user is the hero, not the system** — frame findings around their decision, not around pipeline mechanics.
- **Translate, don't display** — human language, not detection metadata.

## Bridge anti-bullshit constraints

These apply to every bridge sentence:

- No bridge that could stand alone without the finding (anti-empty-rhetoric).
- No bridge that softens a finding's force (anti-paltering).
- No "may," "could," "potentially," "largely," "arguably" (anti-weasel).
- No claims not traceable to a specific passage in the extraction (anti-unverified).

---

## Run-health surface (conditional)

Before the BLUF, read `run_health.overall` and `run_health.issues` from the result JSON. If `overall` is `degraded` or `critical` AND at least one *material* issue is present, insert ONE short line naming the degradation so the reader knows the audit was partial. Silent otherwise — clean delivery is the default, not an achievement.

**Material issues (surface these):**

- `capture_degraded` or `capture_critical` — *"⚠ Audit partially degraded: conversation capture missed assistant turns. Some reasoning wasn't audited."*
- `substrate_empty` — *"⚠ Curated knowledge base did not load for this run. This is a generic critique, not a Lolla audit."*
- `no_fingerprint` — *"⚠ No mental-model activations found in the reasoning — may indicate a very short conversation or a genuine gap."*
- `quote_fabrication` — *"⚠ Extraction partially degraded: [N] reasoning passages couldn't be verified as literal substrings of the transcript. Lane 2 companion analysis may be weaker than usual."* — substitute `N` from `run_health.quote_fabrication_count`. If `run_health.quote_retry_attempted` is true, append "(retry attempted)" to the line.
- `capture_truncated` — *"⚠ Long conversation truncated: [N] middle turns were omitted to fit the size cap. The audit ran on early + late slices; context from the middle may be missing."* — substitute `N` from `run_health.omitted_turns`.
- `lane3_all_dropped` — *"⚠ Frame pressure analysis produced no reframings — all [N] detected frame elements were dropped by the evidence-quote validator. This is different from 'no frame issues found'; the lane attempted but every candidate failed validation."* — substitute `N` from `run_health.lane3_frame_drops_count`.
- Multiple material issues — combine with a semicolon: *"⚠ Audit degraded: capture missed turns; no fingerprint."*

**Non-material (do NOT surface — these are soft signals, not audit-quality breaks):**

- `embeddings_off` — audit still works via deterministic routing.
- `pipeline_warnings` (alone) — flag only if combined with a material issue above.

Skip the block entirely when no material issue is present, even if `overall` is technically `degraded`.

---

## Opening line (the BLUF)

One sentence naming the single most important structural weakness found across all four lanes. This is your Sinatra Test — if this one finding lands, credibility for the whole audit follows. Pick the finding with the highest severity, the most specific passage match, and the most direct connection to the decision.

Example: *"Your recommendation commits to a 3-year vendor lock-in without naming a single condition that would make you walk away."*

---

## Finding blocks (2–4 additional)

Each as a short block. Select across finding types — don't dump all tendency findings before touching frame alternatives. Pick by signal strength, not by type. For each finding:

> **[Finding name]** — [bridge sentence connecting to this conversation]
>
> [One concrete detail: the challenge question, the reversal trigger, the reframed question, or the gap question. Pick whichever is most actionable for this finding. Quote verbatim from the JSON.]

That's it per finding. Do NOT include severity in parentheses like "(High severity)" or "(high)" after the finding name — severity informs your selection of which findings to show and in what order, not how you label them. No "Pattern found:" field markers, no chunk lists.

---

## Mental models active (conditional)

If the companion cheat sheet surfaced anchors, name them explicitly in one line before any reframing or gap lines:

> **Mental models active:** [display_name_1], [display_name_2], [display_name_3] — see Observatory for failure modes, premortem questions, and curated antagonists.

Use each anchor's `display_name` **verbatim** (not paraphrased). This primes the reader to recognize the models you'll reference in Step 6. Skip this line if `companion_cheat_sheet.anchors` is empty or absent. Do not add commentary on each model — this is a naming line, not a findings block.

---

## Alternative question (conditional)

If the audit found a strong reframing (from frame pressure analysis), include one:

> **Alternative question:** "[reframed_question from frame_pressure_card.reframings]"
> [what_opens — one line on what this reframing changes]

---

## Structural gaps (conditional)

If structural coverage found gaps, name them in a single line:

> **Structural gaps:** [dimension_name_1], [dimension_name_2] — [N] questions to answer before deciding (see Observatory for full list)

---

## Delivery audit (Bullshit Index, conditional)

Read `bullshit_profile` from the result JSON. If `summary.total_clear > 0`, add one line after the findings:

> **Delivery check:** [total_clear] patterns of weak delivery detected in the original advice — [name the most significant subtype and a short quote]. Full profile in Observatory.

If `summary.total_clear` is 0: **skip — don't mention it.** Clean delivery is the default, not an achievement.

---

## Run cost line (always shown)

Read `usage_summary` from the result JSON and render one line. Pull `estimated_total_cost_usd` from the top, and from `vendors.openrouter` pull `calls` and `cache_hit_rate`. The Anthropic sub-agent portion is appended later by Step 8b — at this point in the run it is zero, so phrase the line as a pre-subagent figure:

> **Run cost so far:** $X.XX • Y OpenRouter calls (Z.Z% prompt cache hit) • Sub-agent cost added after Step 8b.

If `usage_summary` is absent (e.g., older pipeline run): skip the line silently.

---

## Closing line

One sentence pointing to Observatory for the full picture:

> *Open the Observatory to explore all [N] findings, [N] mental model connections, and [N] structural dimensions in detail. Cost & call breakdown at <code>http://localhost:8080/usage</code>.*

---

## Zero detections across all lanes

> "No material structural weaknesses detected. The reasoning appears structurally sound across tendency detection, model companion, frame pressure, and structural coverage."

---

## What NOT to put in chat

These belong in Observatory only. Read them from the JSON to inform Step 6 reasoning, but do NOT render them in the chat:

**Process artifacts (never in chat):** card names (DeltaCard, CompanionCheatSheet, FramePressureCard, StructuralCoverageCard), pipeline stages, lane numbers (Lane 1, Lane 2, etc.), triage scores, boundary call counts, fingerprint diagnostics, audit trace internals, JSON field names, embedding scores, prompt versions.

**Detail artifacts (Observatory only):** full finding blocks with all fields, companion anchor chunk lists (failure_mode, premortem, antagonist, ally, heuristic, identity, prerequisite_gap), frame element blocks with evidence_quote and fragility_signal, dimension-by-dimension structural gap listings, compound pattern groups, secondary/low-severity findings, bullshit profile passage-by-passage breakdown.

**The rule:** process artifacts never appear in chat. Product artifacts (findings, challenge questions, reframings, gap questions, mental model connections) are presented in human language — no field names, no card names, no lane numbers.

---

## Card structure (for your Step 6 reasoning)

You still need to understand the full card structures to write a good Step 6 reconsideration and to know what the Observatory will show. Read the JSON fields below to inform your reasoning, but do not render them in chat. Field-by-field documentation lives in `references/output-field-guide.md` — load it at the start of Step 4 alongside this file.

**Understanding what the cards contain and where they come from:**

1. **Source layer.** 222 canonical articles, each a deep treatment of one mental model. These are the only semantic root.
2. **Curation.** Each article's operational knowledge extracted and validated: activation semantics, failure modes, relationship edges, reframing patterns, prerequisite orderings.
3. **Compilation.** Compiled into a knowledge graph: models as nodes, typed relationships as edges, chunks attached to each node.
4. **This run.** The pipeline extracted which reasoning patterns are active from the conversation, then walked the knowledge graph to retrieve failure modes, tensions, antagonists, and premortems that travel with those patterns.
