# Chat Output Format

## What this file is

The render specification for chat output across the four beats of a `/lolla` run. SKILL.md uses this file at two load points:

- **After Step 2 extract** — for Beat 1 (situation echo + audit promise).
- **At Step 4 onward** — for Beat 2 (counterargument lead), Beat 3 (updated position), Beat 4 (pressure check).

Load alongside `references/output-field-guide.md` (field definitions) and, at Step 6, `references/anchor-treatment.md` (anchor handling) and `references/presentation-voice.md` + `references/anti-bullshit-doctrine.md` (voice and content discipline).

The authoritative pattern body for this file is `plans/voice-examples-2026-04-30.md`. This file states the rules; the examples doc shows what good and bad output looks like across three test cases (Marcus, Mother, Short fixture). When in doubt, read the examples — they teach the voice better than any rule statement.

---

## Product voice rules

These apply across every beat and every receipt.

### Pronoun policy

- **"Lolla"** when describing the product doing work in functional receipts. *"Lolla captured the conversation"*, *"Lolla is auditing the answer."*
- **"I"** in substantive content beats because the orchestrator is reading and revising its own advice. *"I argued..."*, *"I closed Turn 4 with..."*, *"What I'd take back..."*
- **Avoid** "the assistant" and "the model" in user-facing chat. Both create a third-person distance the user does not need.

### No empathy theater

Do not write *"I understand this is complex"*, *"I can tell this is weighing on you"*, *"this is an important decision"*, *"that feeling is valid"*. The user proves we read the conversation by quoting them back and naming the actual constraint, not by mirroring affect.

### No status theater

Do not send *"still working"*, *"thinking carefully"*, or *"I'll be back shortly"* with no substance. A status receipt should say what phase just completed, what is happening next, and what the user will get from it.

### No machinery leak

Banned in user-facing chat: card names (*DeltaCard*, *CompanionCheatSheet*, *FramePressureCard*, *StructuralCoverageCard*), lane numbers (*Lane 1*, *Lane 2*, etc.), JSON field names, *sub-agents*, *the audit said*, *the pipeline*, *isolated review*, routing language, prompt/process talk. The user receives findings and counterarguments in human language; the mechanism is for the orchestrator, not the reader. See § Cross-cutting rules below for the grep checks.

### No early Observatory link

Before Step 9, do not say `http://localhost:8080` or any other Observatory URL. The server is not running until Step 9 launches it; pointing the user at a dead link quietly damages trust on every run. Beat 2 and Beat 4 use *"queued for the full breakdown once the reconsideration is complete"* / *"I'm opening the full breakdown now"* instead. Only the final functional receipt after Step 9/10 includes a live URL.

### Munger-adjacent voice

The voice should be plainspoken, mechanism-first, concrete in its antidotes, and proportionately blunt. *"The 15% number was Marcus's opening, not the price of admission to road two"* names the mechanism (an offer-anchor that smuggled itself into the recommendation) and offers a structural correction. Munger-adjacent does NOT mean Munger imitation: no aphorism delivery (*"Charlie would say…"*), no folksiness (*"the ancient pull of ownership"*), no performative bluntness (*"be brutally honest with yourself"*), no moralizing. See § Bad — Munger cosplay in `voice-examples-2026-04-30.md`.

### Forbidden phrases

The following phrases are sales/AI-marketing register and signal that the voice has drifted off-spec. They should never appear in chat output:

- *"compelling"*, *"powerful"*, *"unlock"*, *"deep dive"*, *"transform"*, *"leverage"* (as a verb)
- *"complex and nuanced"*, *"valuable insights"*, *"it is important to consider"*
- *"this highlights the need"*, *"a number of factors"*, *"a thoughtful approach"*

If grep against the rendered chat output returns any of these, the voice has slipped.

---

## Status receipts and beat map

The chat surface across a `/lolla` run has **four substantive content beats** and **two functional receipts**. They are different categories of output.

| Stage | Type | When | Word target (normal / thin) |
|-------|------|------|------|
| **Beat 1** — Readback + audit promise | Substantive content | After Step 2 extract | 120–170 / 70–110 |
| **Step 3 receipt** — Pre-pipeline status | Functional receipt | Before Step 3 launches | ~25–35 |
| **Beat 2** — Counterargument lead | Substantive content | After Step 3 returns | 220–300 / 140–220 |
| **Beat 3** — Updated position | Substantive content | After Step 6 | 550–800 (cap 900) |
| **Beat 4** — Pressure check | Substantive content | After Step 8 | ~200 |
| **Final receipt** — Operational close | Functional receipt | After Step 9/10 | ~25–40 |

**Substantive content beats** present audit findings, counterarguments, position changes, and divergences. They follow the rules in their respective sections below.

**Functional receipts** state what just happened and what's next — nothing more. They are not opportunities for decorative prose, narrative summary, or sales register. Step 3 receipt names the work in human terms (e.g., *"Running the audit now: pressure points, frame assumptions, mental-model tensions, and uncovered dimensions. Usually 5–8 minutes."*). The final receipt names the artifacts and the cost (e.g., *"Observatory is live at http://localhost:8080. Memo at /tmp/lolla_*_memo.md. Total run cost: $X.XX. Archived to ~/.local/share/lolla/runs/<case>/<run_id>/."*).

Do not blur the categories. A Step 3 receipt that drifts into prose is status theater; a final receipt that drifts into narrative is the *"Audited your equity decision for Marcus..."* failure mode.

---

## Thin-material mode

Thin-material mode is **mechanical, not discretionary.** It activates per beat based only on data available at that point. The mode is *permission to compress*, not obligation to under-write — if one strong finding exists, spend the words there; if not, be brief and say what the audit did and did not find without inventing stakes.

### Pre-pipeline thin mode (Beat 1)

Activates when ANY is true:

- `captured_message_count <= 4` — total count of user messages + assistant responses (not `[Turn N]` exchange count; a 14-turn conversation is 28 messages).
- `extraction.reasoning_passages` < 3 items AND `extraction.live_constraints` < 3 items AND `extraction.dropped_threads` is empty.

### Post-pipeline thin mode (Beat 2)

Activates when EITHER pre-pipeline thin mode was active OR the audit itself is low-signal (conjunction across all four):

- `delta_card.top_findings` is empty
- AND `companion_cheat_sheet.anchors` < 3 entries
- AND `frame_pressure_card.reframings` is empty
- AND `structural_coverage_card` has no uncovered dimensions, or at most one weakly-covered uncovered dimension

The audit-low-signal trigger is conjunctive — one strong frame reframe or one good gap dimension keeps Beat 2 in normal mode.

### What thin mode permits

When thin mode is active for a beat, use the **lower target range** (Beat 1: 70–110 words; Beat 2: 140–220 words). Do not pad to the normal target. The §3 cap (3–4 shifts in Beat 3) **applies regardless of thin mode** — thin doesn't mean "more shifts allowed because less material elsewhere."

Beat 4 has no thin-mode-specific length but should be proportional to the divergences the audit produced — typically shorter on thin material.

See `voice-examples-2026-04-30.md` § Beat 1 / Short fixture (85 words) and § Beat 2 / Short fixture (190 words) for what thin-mode rendering looks like on a 4-message conversation.

---

## Beat 1 — Readback + audit promise

### Rule

After Step 2 extract returns `status: ok`, present a short readback that demonstrates the conversation was read and sets up the audit. **Length: 120–170 words normal mode; 70–110 thin mode; hard cap 200.**

### What goes in

1. **One line naming the decision** (from `extraction.decision_situation`).
2. **2–3 sentence readback of the user's framing**, with at least one **exact quote** from a user turn.
3. **1–2 sentence readback of what the orchestrator argued back**, with an exact assistant quote only if it earns its place. (Often the assistant's argument is best summarized rather than quoted; a verbatim quote is for moments where one sentence captures the position.)
4. **One-sentence dropped-thread note** only when `extraction.dropped_threads` contains something material. No filler line when the field is empty or the threads are weak.
5. **Closing operational status receipt:** *"Now I'm testing the part of my answer that sounded most settled: what would make it fail, what frame it accepted, and what it left uncovered. This usually takes 5–8 minutes."*

### What does NOT go in

- Card names, lane numbers, audit machinery, predictions about what the audit will find.
- Generic reassurance, empathy theater, or pre-finding teases.
- Observatory URL.

### Examples

- **Good (normal):** `voice-examples-2026-04-30.md` § Beat 1 / Marcus (155 words) and § Beat 1 / Mother (170 words).
- **Good (thin):** § Beat 1 / Short fixture (85 words).
- **Failure mode:** § Bad — therapy recap.

---

## Beat 2 — Counterargument lead

### Rule

After Step 3 pipeline returns, present the strongest counterargument as a story tied to the user's own words, plus one alternative the conversation didn't price. **Length: 220–300 words normal; 140–220 thin; hard cap 350.**

### What goes in

1. **Run-health line, conditional.** Only when `run_health.overall ≠ healthy` AND a material issue is present (`capture_degraded`, `capture_critical`, `substrate_empty`, `no_fingerprint`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`). Silent on healthy runs.
2. **One exact quote** anchored to a specific turn, format *"In Turn N, you wrote: '...'"* or *"In Turn N, I closed with: '...'"*. Drop turn numbers when the quote spans turns or is paraphrased. Use turn numbers as **light source attribution only — never as heading style** (no *"Finding 1 — Turn 4 Evidence Quote"*). The user can inspect referenced turns via the captured transcript at `/tmp/lolla_${LOLLA_RUN_ID}_conversation.txt` and the Observatory's conversation view (both use `[Turn N]` markers); memo navigation is not part of this contract.
3. **One paragraph (3–5 sentences) making the case against that move.** Specific. Names the structural error in plain language. Avoids machinery vocabulary (no *"deprival-superreaction"*, *"loss aversion pattern"*, etc. — those models go in Beat 3 §3 where they earn context).
4. **One alternative-question or alternative-instrument** the audit pushed onto the table. Verbatim from `frame_pressure_card.reframings[0].reframed_question` if it serves; otherwise a sharp paraphrase of the strongest cross-lane alternative. **Fallback rule:** when no single user passage anchors the critique, lead with paraphrased user-position framing (*"The answer treated X as settled before testing Y"*). Exact quote preferred; paraphrase acceptable when the verbatim would be awkward or misleading.
5. **One queued-breakdown line WITHOUT URL:** *"There are X more challenge points and Y unanswered dimensions queued for the full breakdown once the reconsideration is complete."*
6. **One transition sentence:** *"Now I'm using this to revise my own answer, not just report the audit. ~3 minutes."*

### What does NOT go in

- Mental-models-active list (removed entirely from chat — the anchors get woven into Beat 3 §3 where they ground the shift).
- Structural-gaps list (count mention only in the queued-breakdown line).
- Delivery-check line (Observatory only — not user-facing in chat).
- Three-finding-block dashboard (replaced with one strong push + one alternative).
- Live Observatory URL before Step 9.

### Examples

- **Good (normal):** § Beat 2 / Marcus (250 words) and § Beat 2 / Mother (265 words).
- **Good (thin):** § Beat 2 / Short fixture (190 words).
- **Failure mode:** § Bad — dashboard report.

---

## Beat 3 — Updated position

### Rule

After Step 6 reconsideration is written, present the orchestrator's revised position. Three-section structure: §1 What survived / §2 What I'd take back / §3 What actually shifted. **Length: 550–800 words total; hard cap 900.**

### Structure

- **§1 What survived** — 1–2 paragraphs, names what holds.
- **§2 What I'd take back** — 1–2 paragraphs, names what to set aside with reason.
- **§3 What actually shifted** — **capped at 3–4 distinct shifts**. Each ~3–4 sentences. Anchors woven in by name where they ground the shift.
- Optional: one closing line landing the road choice or actionable summary.

### Operational shift definition (enforces the cap)

A **shift** is a change to the substantive advice the user would experience as different guidance: a different action, threshold, sequence, condition, risk treatment, or decision question. If it does not change what the user would do, delay, verify, reject, ask, or watch for, it is not a shift.

**Tail-addition rule:** *"one more thing,"* *"two smaller adjustments,"* *"related notes,"* *"minor caveats"*, *"final caveat"* count against the §3 cap if they change advice. If they do not change advice, they belong in §1 (with survival framing) or §2 (with set-aside framing) — not in a §3 tail-section. The cap is enforced on shifts as defined above; it cannot be evaded by re-labeling shifts as adjustments.

### Anchor-naming invariant

Every anchor in `companion_cheat_sheet.anchors[]` must land in §1, §2, or §3 — verbatim by `display_name`. Under the §3 cap, weak anchors (set-aside category) are acknowledged briefly in §2 with a one-line reason rather than promoted into §3 to satisfy the invariant. Making weak anchors load-bearing in §3 to fill quota is the failure mode. See `references/anchor-treatment.md` for the three rhetorical modes (primary pressure / secondary lens / set aside).

### Examples (§3-only excerpts)

- **Good (normal):** § Beat 3 / Marcus §3 (4 shifts, 340 words) and § Beat 3 / Mother §3 (3 shifts, 290 words).
- **Good (thin):** § Beat 3 / Short fixture §3 (2 shifts, 190 words). Thin material does not pad to hit the cap's upper bound.
- **Failure mode:** § Bad — cap evasion. Shows the *"three things shifted"* + *"two smaller adjustments"* + *"one related note"* + *"final caveat"* pattern that hides 6+ actual shifts under tail framing.

---

## Beat 4 — Pressure check

### Rule

After Step 8 sub-agent comparison, surface what the independent pressure-check caught that Step 6 missed. Frame as a counter-frame, never as alignment. **Length: ~200 words.**

### What goes in

1. **Counter-frame opening sentence.** Use one of: *"One more angle worth surfacing"*, *"A fresh read pushed on something I underweighted"*, *"Two things the position above softened or skipped"*. **Never** *"mostly aligned"*, *"all incorporated above"*, or *"the rest is in the position above."* See § Watch for Question-3 suppression below.
2. **1–4 divergences**, each one sentence + 2–3 sentences of substance. Each divergence should name a concrete alternative mechanism (alternative reporting channel, contractual instrument, stakeholder forum, tripwire pattern, legal-instrumental framing) — not a vague "consider also" gesture.
3. **Closing before Step 9:** *"Audit complete. I'm opening the full breakdown now."*
4. **Final functional receipt after Step 9/10:** *"Observatory is live at [link]. Memo at [path]. Total run cost: $X.XX. Archived to [path]."* This appears only after the Observatory server is actually launched.

### Watch for Question-3 suppression

If the draft pressure check contains *"mostly aligned"*, *"all incorporated above"*, *"already covered"*, or similar — re-read the sub-agent outputs for any **named alternative mechanism** that Step 6 §3 didn't enumerate. A named alternative the sub-agent surfaced that §3 didn't list IS a Question-3 divergence (*"a connection I didn't make"*) — surface it even when the underlying *concern* was addressed structurally. Confident closure that suppresses named alternatives is the failure mode this beat exists to defeat.

### What does NOT go in

- "Mostly aligned" closure or any variant.
- *"Sub-agents"*, *"lanes"*, *"isolated review"*, *"the pipeline flagged"* — attribute the *argument*, not its source. Step 7 runs behind the scenes; the user never hears about it.
- Narrative summary close (*"Audited your equity decision for Marcus. Found 3 patterns…"*) — the functional close above replaces it.

### Examples

- **Good:** § Beat 4 / Marcus (200 words), § Beat 4 / Mother (210 words), § Beat 4 / Short fixture (145 words).
- **Failure mode:** § Bad — "mostly aligned" closure.

---

## Cross-cutting rules and forbidden failure modes

### Machinery-leak grep

Before delivering any beat, mentally grep for these patterns. If any appear, the beat has machinery leak:

- *"sub-agent"*, *"the pipeline"*, *"the audit said"* (vs. *"the audit"* in §2 set-aside framing, which is borderline-acceptable when explaining a dismissal — context-dependent)
- *"DeltaCard"*, *"CompanionCheatSheet"*, *"FramePressureCard"*, *"StructuralCoverageCard"*
- *"Lane 1"*, *"Lane 2"*, *"Lane 3"*, *"Lane 4"*
- *"isolated review"*, *"the verifier"*, *"the boundary call"*, *"prompt versions"*
- JSON field names (*"specific_passage"*, *"display_name"*, *"frame_pattern"*, etc.)

### Munger cosplay warning

The voice contract is Munger-*adjacent* — mechanism, concrete antidote, proportionate bluntness. It is NOT Munger imitation. If the draft contains Munger quotations, *"invert, always invert"* delivery, *"the ancient pull of"* phrasing, *"be brutally honest"* address, or extended business-luminary parallels (*"Sam Walton"*, *"Buffett would..."*), the voice has slipped into cosplay. See § Bad — Munger cosplay in `voice-examples-2026-04-30.md`.

### Forbidden phrases (full grep list)

These phrases never appear in chat:

- Sales/marketing: *"compelling"*, *"powerful"*, *"unlock"*, *"deep dive"*, *"transform"*, *"leverage"* (verb form)
- Generic AI register: *"complex and nuanced"*, *"valuable insights"*, *"it is important to consider"*, *"this highlights the need"*, *"a number of factors"*, *"a thoughtful approach"*, *"a multifaceted issue"*
- Empathy theater: *"I hear you"*, *"I understand this is"*, *"that feeling is valid"*, *"I want to honor"*
- Status theater: *"still working"*, *"thinking carefully"*, *"I'll be back shortly"* (without substantive context)

### Anchor-naming invariant cross-reference

Every anchor in `companion_cheat_sheet.anchors[]` must appear verbatim in Beat 3 (§1, §2, or §3). The full doctrine and three-treatment vocabulary lives in `references/anchor-treatment.md` and applies inside Beat 3, not in Beat 1 / Beat 2 / Beat 4 (anchors do not appear as a list in those beats).
