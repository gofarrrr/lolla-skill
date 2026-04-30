# Chat Delivery and Memo Upgrade — Implementation Spec

**Date:** 2026-04-30
**Branch:** `chore/skill-md-progressive-disclosure` (continued)
**Status:** Local-only contract. Sign off on §6 calls before any code lands.

---

## 1. Why now

After the progressive-disclosure refactor and the 3-case validation, the live chat surface still under-delivers:

1. **Chat output and progress.** Step 4 is verdict-shaped, dashboard-dense, mental-model jargon, ~9 elements competing for attention. It lands as a system report instead of a counterargument the user can engage with. The 6+ minute pipeline wait is silent, so the product feels frozen even when the skill is doing real work.
2. **Memo (`render_memo.py`) — secondary.** 7 deterministic section dumps. No narrative connecting tissue. Headline is a category title (`"# Reasoning Audit: [situation]"`) — Minto-violation. "Halfway there. Too dry." User won't open it twice.

The chat cannot become Observatory in miniature. It should feel like the working conversation: *I read the situation; I am checking the pressure points; here is the one thing that most changes the advice; now I am going to revise what I said.* Observatory remains the instrument panel. The memo remains the portable artifact.

**Strategic intent:** the chat surface should make the user feel that Lolla is actively working on *their* conversation, not emitting a dry audit packet. It should provide useful pressure without sounding like sales copy, therapy copy, or AI-generated report prose. The right posture is Munger-adjacent: plainspoken, mechanism-first, concrete, occasionally sharp, never theatrical. The system proposes additional angles that make the user think twice; it does not try to convince them.

---

## 2. Scope and constraints

**In scope:**

- `SKILL.md` — Steps 2.5 / 3 / 4 / 6 / 8 / 9 / 10 (chat behavior, status receipts, final handoff)
- `references/chat-output-format.md` — full rewrite around product status receipts + four-beat shape
- `references/anchor-treatment.md` — minor update to align with §3 cap
- `references/memo-narrative.md` — Phase 2 only; new file specifying memo orientation narrative
- `scripts/render_memo.py` — Phase 2 only; accepts new field, renders narrative before findings, drops one redundancy
- `plans/chat-and-memo-upgrade-spec-2026-04-30.md` — this file

**Out of scope (not touched):**

- Observatory (entire `observatory/` dir)
- Engine (`engine/system_b/*`)
- Other scripts (`run_extract.py`, `run_pipeline.py`, `archive_run.py`)
- `HOW_IT_WORKS.md` (user-facing reference)
- Other reference files (`presentation-voice.md`, `anti-bullshit-doctrine.md`, `output-field-guide.md`, etc.) — left alone

**Doctrinal constraints (from `research/minto-mckinsey-presentation-interpretation-2026-04-28.md` §2):**

- Curated knowledge IS the product. Generic synthesis on top of curated chunks is anti-pattern.
- Lens, not verdict. The system surfaces pressure; the user decides.
- Process artifacts never in user-facing surfaces.
- The user is the hero, the system is the guide.
- Determinism is part of trust — but a clearly marked Claude-written orientation section is acceptable when the rest stays deterministic.
- Chat must never point to an Observatory URL before the server is actually launched.
- "Munger-inspired" means mechanism, concrete antidote, and proportionate bluntness. It does not mean imitation, aphorism-writing, folksiness, or moralizing.
- Better writing is for salience, not persuasion. Avoid language like "compelling," "persuasive," "make the user want," unless the claim is about the memo artifact itself and is still grounded in usefulness rather than sales.

---

## 3. Target shape — chat (product beats + status receipts)

The chat experience is restructured from "one dump after pipeline" to **a guided product run**: short status receipts at natural pauses, plus four content beats that progressively move from readback → challenge → revised position → pressure check.

This is not streaming pipeline internals. Phase 1 can improve perceived liveness without engine changes by speaking at the pauses the skill already has. True in-flight heartbeat messages during the long Step 3 call require background execution or pipeline status events and stay out of Phase 1 unless explicitly pulled in.

### Product voice rules

- **Pronoun policy.** Status receipts can say "Lolla" when describing the product doing work. Reconsideration uses "I" because the orchestrator is revising its own advice. Avoid "the assistant" and "the model" in user-facing chat.
- **No empathy theater.** Do not write "I understand this is complex" or "this is an important decision." Prove the conversation was read by naming the actual constraint, quote, or unresolved tradeoff.
- **No status theater.** Do not send "still working" with no substance. A status receipt should say what phase just completed, what is happening next, and what the user will get from it.
- **No machinery leak.** No card names, lane numbers, JSON fields, scores, routing language, "sub-agents," or prompt/process talk.
- **No early Observatory link.** Before Step 9, say the full breakdown will open after reconsideration is complete. Only give `http://localhost:8080` after the server is launched.
- **Munger-adjacent voice.** Lead with the mechanism in the reasoning, not the category label. Give one concrete antidote or alternate question. Be plain enough that a busy decision-maker can use it tomorrow.

### Beat 1 — Readback + audit promise (after Step 2 extract; ~1 min in)

**New content. Doesn't exist today.**

What it does: shows that the skill captured the specific decision, not just the topic; sets up the long audit call; gives the user a useful reason to wait.

What goes in:
- One line naming the decision (from `extraction.decision_situation`)
- A 2–3 sentence readback of the user's framing, **with at least one exact quote from the captured transcript**
- A 1–2 sentence readback of what the orchestrator argued back, with an exact assistant quote only if it earns its place
- A one-sentence dropped-thread note only when `extraction.dropped_threads` contains something material
- A closing status receipt: *"Now I’m testing the part of my answer that sounded most settled: what would make it fail, what frame it accepted, and what it left uncovered. This usually takes 5–8 minutes."*

What does NOT go in: card names, lane numbers, audit machinery, predictions about what the audit will find, or generic reassurance.

**Length target:** 120–170 words. Hard cap: 200. The failure mode is "therapeutic recap" or extraction regurgitation.

### Beat 2 — Counterargument lead (after Step 3 pipeline; ~8 min in)

**Replaces today's full Step 4 dashboard.**

What it does: lands the strongest counterargument as a story tied to the user's own words, offers one alternative the conversation did not price, and tells the user what happens next.

What goes in:
- *Run-health line, conditional* (only when `run_health.overall` ≠ healthy AND material issue present — same rule as today)
- **One exact user-or-assistant quote** that anchors the strongest finding. **Turn-number rule:** include a turn reference in the format *"In Turn N, you wrote: '[exact quote]'"* or *"In Turn N, I closed with: '[exact quote]'"* when the quote is from a specific identifiable turn in the captured transcript. Drop turn numbers when the quote spans turns or is paraphrased. Use turn numbers as **light source attribution only — never as heading style** (no *"Finding 1 — Turn 4 Evidence Quote"*). The user can inspect referenced turns in two places: the captured transcript at `/tmp/lolla_${LOLLA_RUN_ID}_conversation.txt` and the Observatory's conversation view, both of which use `[Turn N]` markers. Memo navigation is not part of this contract.
- **One paragraph (3–5 sentences)** making the case against that move. Specific. Names the structural error in human terms. Avoids machinery vocabulary.
- **One alternative-question or alternative-instrument** the audit pushed onto the table. Verbatim from `frame_pressure_card.reframings[0].reframed_question` if it serves; otherwise a sharp paraphrase of the strongest cross-lane alternative.
- **One queued-breakdown line** without a URL: *"There are X more challenge points and Y unanswered dimensions queued for the full breakdown once the reconsideration is complete."*
- One transition sentence: *"Now I’m using this to revise my own answer, not just report the audit. ~3 minutes."*

What does NOT go in:
- Mental-models-active list (removed entirely from chat)
- Structural-gaps list (count mention only in the queued-breakdown line)
- Delivery-check line (removed entirely — Observatory only)
- Three-finding-block dashboard (replaced with one strong push + one alternative)
- Live Observatory URL before Step 9

**Length target:** 220–300 words. Hard cap: 350.

**Fallback rule when no single quote anchors the critique:** lead with paraphrased user-position framing — *"The answer treated X as settled before testing Y."* Exact quote preferred; paraphrase acceptable if the quote would be awkward or misleading.

### Beat 3 — Updated position (after Step 6; ~11 min in)

**Replaces today's freely-sized Step 6 output.**

What it does: presents the orchestrator's reconsidered position. Compressed. Anchor-naming invariant satisfied. Cap on §3.

What goes in:
- §1 What survived — 1–2 paragraphs, names what holds
- §2 What I'd take back — 1–2 paragraphs, names what to set aside with reason
- §3 What actually shifted — **capped at 3–4 distinct shifts**. Each ~3–4 sentences. Anchors woven in by name where they ground the shift.
- Optional: one closing line landing the road choice or actionable summary

**Length target:** 550–800 words total. Hard cap: 900. (Today the average is 1100–1400.)

The cap is the operational version of "reconsider, don't elaborate." More shifts only when the audit produced more *independent* evidence — not when there's more sub-agent material to draw from.

**Shift definition (enforces the cap):** A shift is a change to the substantive advice the user would experience as different guidance: a different action, threshold, sequence, condition, risk treatment, or decision question. If it does not change what the user would do, delay, verify, reject, ask, or watch for, it is not a shift.

**Tail-addition rule:** "One more thing," "two smaller adjustments," "related notes," and "minor caveats" count against the §3 cap if they change advice. If they do not change advice, they belong in §1 (with survival framing) or §2 (with set-aside framing) — not in a §3 tail-section. The cap is enforced on shifts as defined above; it cannot be evaded by re-labeling shifts as adjustments. This same definition lives in `references/anchor-treatment.md`.

### Beat 4 — Pressure check (after Step 8; ~13 min in)

**Tone-reset on existing element.**

What it does: surfaces what the independent pressure check caught that the orchestrator missed. Frames divergences as *"one more angle worth surfacing"* instead of *"mostly aligned with the assessment above."*

What goes in:
- Opening sentence: *"One more angle worth surfacing"* / *"A fresh read pushed on something I underweighted"* / *"Two things the position above softened or skipped"* — counter-frame, not coda.
- 1–4 divergences, each one sentence + 2–3 sentences of substance.
- Closing before Step 9: *"Audit complete. I’m opening the full breakdown now."*
- Final functional receipt after Step 9/10: *"Observatory is live at [link]. Memo at [path]. Total run cost: $X.XX. Archived to [path]."*

**No closing narrative summary** ("Audited your equity decision for Marcus. Found 3 patterns…"). The functional close above replaces it.

### Thin-material mode

Thin-material mode is **mechanical, not discretionary.** It activates per beat based only on data available at that point. The mode is *permission to compress*, not obligation to under-write — if one strong finding exists, spend the words there; if not, be brief and say what the audit did and did not find without inventing stakes.

**Pre-pipeline thin mode** applies to Beat 1 when ANY of these is true:

- `captured_message_count <= 4`, where `captured_message_count` = total count of user messages + assistant responses (not `[Turn N]` exchange count — a 14-turn conversation is 28 messages, not 14).
- `extraction.reasoning_passages` has fewer than 3 items AND `extraction.live_constraints` has fewer than 3 items AND `extraction.dropped_threads` is empty.

**Post-pipeline thin mode** applies to Beat 2 when EITHER pre-pipeline thin mode was active OR the audit itself is low-signal:

- `delta_card.top_findings` is empty
- AND `companion_cheat_sheet.anchors` has fewer than 3 entries
- AND `frame_pressure_card.reframings` is empty
- AND `structural_coverage_card` has no uncovered dimensions, or at most one weakly-covered uncovered dimension

The audit-low-signal trigger is a **conjunction across all four criteria** (every one must be true to fire). One useful frame reframe or one good gap dimension is enough to keep Beat 2 in normal-mode.

**Lower target ranges when thin mode is active:** Beat 1 may be 70–110 words; Beat 2 may be 140–220 words. Do not pad to the normal target. The §3 cap (3–4 shifts) applies regardless of thin mode — thin doesn't mean "more shifts allowed because less material elsewhere."

---

## 4. Target shape — memo (Phase 2: orientation narrative + tightened sections)

The memo change is Phase 2. It should not land until the chat delivery change has been validated. The memo gets a Claude-written orientation narrative at the top, then deterministic curated sections, then a tightened close. The non-orientation sections stay deterministic.

### New structure

1. **Heading** — replaced. Currently `"# Reasoning Audit: [decision_situation truncated]"`. Becomes **a substantive title** that names the audit's headline observation, not the case category. Format: `"# [Substantive headline derived from BLUF]"`. Source: Claude writes it as part of the memo orientation narrative.
2. **Orientation narrative** — NEW SECTION, Claude-written, 180–260 words. Renders before any other section.
3. **Key Findings** — kept. Deterministic. Sorted by severity.
4. **Mental Model Connections** — kept. Deterministic.
5. **Frame Alternatives** — kept. Deterministic.
6. **Structural Gaps** — kept. Deterministic.
7. **Delivery Check** — kept (informational here, even though removed from chat). Deterministic.
8. **Updated Position** — **kept but trimmed.** Today renders the full `revised_answer` verbatim. New rule: render only the Beat 3 §3 ("What actually shifted") section if the full revised answer exceeds 600 words. Otherwise render in full. Avoids verbatim duplication of what's already in the chat transcript.
9. **Pressure Check** — kept. Deterministic.

### Memo orientation narrative — what it is

A 180–260 word **vivid, specific, conversational** opener. Claude writes it after Step 6 / Step 8 are done. It is **NOT** a summary of the sections below; it is a narrative orientation to the audit's *most important pushback* with the user's own words quoted. The voice should feel like a sharp memo lede, not a report abstract and not product marketing.

What it includes:
- The substantive title (one line, names the audit's strongest observation)
- 2–3 paragraphs:
  - Para 1: the user's decision and what they argued for, anchored by one verbatim user quote
  - Para 2: the strongest pushback, with the user's or orchestrator's quoted move and the structural error
  - Para 3: one alternative the conversation didn't price + a closing sentence pointing to what's below

What it is NOT:
- A list of sections to come ("Below you'll find Findings, Mental Models, etc.")
- A neutral framing ("This memo audits the decision regarding…")
- A repeat of revised_answer
- Process narrative ("The audit ran four lanes…")
- Sales language ("compelling," "powerful," "unlock," "transform," "deep dive")

### Why a Claude-written orientation is OK here

The memo's deterministic curated sections still carry the curated knowledge as-is (failure modes, premortem questions, gap questions). The orientation narrative is a navigation aid into that curated content: it names why this memo exists before the section dumps begin. Adding ~220 words of Claude prose at the top costs determinism in one section and gains salience across the whole memo. The trade is acceptable because:

- The curated content below is still deterministic
- The narrative is grounded in exact conversation quotes; if a quote cannot be verified against the captured transcript, paraphrase instead
- The narrative does NOT make new claims — it re-tells findings the curated layer surfaced

This is allowed by the interpretation file's §4.1: *"orientation block at the top of the memo… Fully derivable from the result JSON. No verdict, no synthesis."* The narrative is the orientation block, voiced.

---

## 5. Files and changes

### `SKILL.md` (518 → ~555 lines)

**New: Step 2.5 (Beat 1 — readback + audit promise).** After Step 2 extraction returns `status: ok`, add a short instruction block:

> Before launching the pipeline (Step 3), present **Beat 1** — a 120–170 word readback + audit promise per `references/chat-output-format.md` § Beat 1. This fills the pipeline wait with a concrete product receipt: what Lolla captured, what it is about to test, and how long it will take.

**Step 3 status receipt.** Immediately before the long pipeline call, say one short line naming the work in human terms: *"Running the audit now: pressure points, frame assumptions, mental-model tensions, and uncovered dimensions. Usually 5–8 minutes."* Do not promise mid-call updates unless true background/polling support is implemented.

**Step 4 (Beat 2 — Counterargument lead).** Slim further. Body becomes: "Read `chat-output-format.md` § Beat 2. Present the counterargument lead. ~220–300 words. Do not link to Observatory yet; it is not live until Step 9."

**Step 6 (Beat 3 — §3 cap with operational shift definition).** Add: *"§3 caps at 3–4 distinct shifts. A shift is a change to the substantive advice the user would experience as different guidance: a different action, threshold, sequence, condition, risk treatment, or decision question. If it does not change what the user would do, delay, verify, reject, ask, or watch for, it is not a shift. Tail-additions ('one more thing', 'two smaller adjustments', 'related notes', 'minor caveats') count against the cap if they change advice; if they do not change advice, they belong in §1 or §2."*

**Step 6c (Phase 2 only: Memo orientation narrative).** New sub-step before render. After `revised_answer` is persisted, **before** running `render_memo.py`, Claude writes the memo orientation narrative per `references/memo-narrative.md` and persists it to result JSON via the same merge pattern Step 6b uses (new field `memo_orientation_narrative`, `memo_substantive_title`, `memo_narrative_written_at`).

**Step 8 (Beat 4 — tone reset).** Body strengthened: *"Frame the pressure check as 'one more angle worth surfacing' / 'a fresh read pushed on something I underweighted' / 'two things the position above softened or skipped' — never 'mostly aligned'. The Question-3 suppression watch is the same."*

**Step 9/10 — Closing.** Replace the narrative-summary close with the functional receipt: *"Observatory is live at [link]. Memo at [path]. Total run cost: $X.XX. Archived to [path]."* This only appears after the Observatory is actually launched.

### `references/chat-output-format.md` (157 → ~220 lines)

Full rewrite around product voice rules, status receipts, and four beats. Old material on run-health surface, BLUF, anchor-naming line, alternative-question line, structural-gaps line, delivery-check line, run-cost line, closing line — restructured into Beat 1 / Beat 2 / Beat 3 / Beat 4 specifications. Drops the anchor-list, structural-gaps line, delivery-check line as chat elements (Observatory only). Adds explicit no-early-Observatory-link rule and exact-quote rule.

### `references/anchor-treatment.md` (106 → ~115 lines)

Update the "anchor-naming invariant" section to align with the §3 cap. Currently the invariant says every anchor must land in §1, §2, or §3. The cap implies: weak anchors (set-aside category) acknowledge briefly in §2 with reason; only load-bearing anchors take a slot in the capped §3.

Add a paragraph: *"Under the §3 cap (3–4 shifts), anchors that don't drive a load-bearing shift are acknowledged in §2 with a one-line reason rather than promoted into §3 to satisfy the invariant. The invariant is satisfied by §1, §2, or §3 mention; making weak anchors load-bearing in §3 to fill quota is the failure mode."*

### `references/memo-narrative.md` (NEW, Phase 2 only, ~90 lines)

Specifies the memo orientation narrative. Sections:
- What this file is (memo opener spec)
- When Claude writes it (after Step 6, before render_memo.py)
- Voice rules (vivid, specific, conversational, grounded in exact quotes, not salesy)
- What goes in (substantive title + 2–3 paragraphs with the structure named in §4)
- What does NOT go in (lists of sections to come, neutral framing, revised_answer repeat, process narrative)
- Length cap (180–260 words)
- Examples (one good, one bad, applied to a hypothetical case)

### `scripts/render_memo.py` (247 → ~270 lines)

Three changes:

1. **Heading replacement.** Read `result.memo_substantive_title` if present; fall back to current `"# Reasoning Audit: [decision_situation]"` for older runs.
2. **Orientation narrative section.** Read `result.memo_orientation_narrative` if present; render as an unheaded narrative block after the title and before Key Findings.
3. **Updated Position trimming.** If `revised_answer` exceeds 600 words, render only the §3 ("What actually shifted") section. Otherwise render in full. Detect §3 by header match (`### What actually shifted` or equivalent).

Backward compat: missing `memo_substantive_title` → fall back to old heading. Missing `memo_orientation_narrative` → skip the section. Missing or short `revised_answer` → render in full. Old result JSONs render with the old shape.

---

## 6. Calls I need from you before implementation

### 6.1 Sequencing — chat first, memo later

**The call:** Phase 1 should be chat delivery only. Memo work moves to Phase 2 after chat validates.

**The trade:** slower total roadmap, cleaner attribution. The current user pain is in the live chat: the run feels silent, dry, and report-like. Memo prose may matter, but it should not steal focus from fixing the product surface users actually feel during the audit.

**My recommendation:** sequence. Phase 1 = status receipts + Beat 1 / Beat 2 / Beat 3 / Beat 4 + anchor cap. Phase 2 = memo orientation narrative + render changes.

### 6.2 Progress receipts vs. true in-flight heartbeat

**The call:** do we keep Phase 1 to natural-pause status receipts, or expand scope to true mid-call heartbeat/progress during Step 3?

**Receipt-only version:** no engine change. The skill speaks after extraction, before the long pipeline call, after the pipeline returns, before reconsideration, and after completion. This makes the product feel intentional at the boundaries but cannot speak during the 5–8 minute blocking call.

**True heartbeat version:** requires background execution/polling or pipeline-emitted progress events. This gives real "something is happening" reminders during the wait, but it touches execution flow and belongs in a separate implementation slice.

**My recommendation:** receipt-only in Phase 1. If reader review still says the wait feels dead, write a separate Step 3 heartbeat spec.

**Escalation trigger (observable, not vibe):** if Phase 1 reader review on **2/4 cases** reports any of the following, write a separate Step 3 heartbeat/progress spec:

- User uncertainty about whether the run is still active during the 5–8 minute Step 3 wait.
- User desire to interrupt or re-run the audit mid-Step 3.
- Reviewer note that the pre-Step 3 status receipt did not carry the wait — i.e., the user-facing experience felt dead between minute 1.5 and minute 8 even after the receipt landed.

If none of those signals appear in 3+ cases, receipt-only is sufficient and heartbeat work is deferred indefinitely.

### 6.3 Beat 1 length and risk

**The call:** Beat 1 becomes 120–170 words, not 150–200.

**The trade:** slightly less "seen" effect, much lower risk of soft recap. The user wants approachable and product-like, not a therapy mirror.

**My recommendation:** 120–170 words with exact transcript quotes, plus good/bad examples in `chat-output-format.md`. The bar is "specific enough that the user trusts capture worked," not "lush enough to feel literary."

### 6.4 Voice contract — Munger-inspired, not Munger cosplay

**The call:** make the voice rule explicit: mechanism-first, concrete antidotes, proportionate bluntness, no aphorism factory, no sales language.

**The trade:** stronger constraints may make the chat less "beautiful," but beauty is not the point. The product needs useful cognitive friction.

**My recommendation:** add this rule. Good Lolla chat should sound like a smart operator who read the situation and knows where reasoning fails. It should not sound like a brand, a therapist, a management consultant, or an AI writing a "thoughtful reflection."

### 6.5 Memo orientation narrative — accept later?

**The call:** in Phase 2, OK to add a Claude-written 180–260 word orientation narrative at the top of the memo, with the rest of the memo staying deterministic?

**The trade:** the memo's first ~220 words become non-reproducible per run. Everything below stays deterministic. The orientation block can make the memo more readable, but it must not become persuasion copy or new synthesis.

**My recommendation:** yes, but only after Phase 1. Determinism in the *evidence* is what builds trust; a strictly grounded orientation paragraph can help the user enter the evidence without turning the memo into a sales artifact.

**The call is binary.** Either:

- **Claude-written orientation narrative** (the recommended path), tightly grounded in exact quotes and audit findings, ~180–260 words at top of memo.
- **No memo opener change yet** — keep the current deterministic memo shape until a stronger deterministic alternative is proposed.

A counts/severity/run-health rollup block is explicitly NOT an alternative — it is metadata wearing a better hat, and it is exactly the dry artifact this work is trying to escape. No "heavier deterministic template" unless someone proposes an actually good deterministic orientation, not a counts block.

### 6.6 Memo title and trimming

**The call:** in Phase 2, Claude writes a substantive title, and the memo trims the full `revised_answer` when it exceeds 600 words.

**Title rule:** the title is a structural observation, not a recommendation. Example: `"# Equity decision hung on a tail outcome"` is acceptable. `"# Do not give Marcus equity"` is not.

**Trim rule:** if `revised_answer` exceeds 600 words, render only §3 ("What actually shifted") plus a one-line pointer that §1/§2 live in the chat transcript/result JSON. This avoids duplicating the chat while preserving context for standalone memo readers.

**My recommendation:** accept both in Phase 2.

---

## 7. Test plan

Use the 3-case corpus from the previous spec, plus one deliberately short case:

1. `founder-grant-marcus-equity` (full load — 5 anchors baseline, 3 in last refactor run)
2. `mid-level-consultant-report-1` (degraded health on baseline)
3. `mother-deciding-protect-year` (Lane 1 empty in our last run)
4. `short-strategic-conversation` (new fixture: 2–4 user/assistant turns, enough for extraction but thin enough to test whether Beat 1 / Beat 2 over-write)

### Phase 1 invariant checklist (chat changes)

- [ ] Beat 1 rendered after Step 2 extract; contains exact user quote and exact assistant quote only when the assistant quote earns its place
- [ ] Beat 1 length 120–170 words (normal mode) OR 70–110 words (thin mode); hard cap 200
- [ ] Beat 1 names dropped threads only when material; no filler line when `dropped_threads` is empty or weak
- [ ] Thin-mode trigger applied correctly: pre-pipeline thin mode fires only when `captured_message_count <= 4` OR `(reasoning_passages < 3 AND live_constraints < 3 AND dropped_threads empty)` — not by orchestrator discretion
- [ ] Step 3 has a short pre-run status receipt; does not promise mid-call updates unless background/polling exists
- [ ] Beat 2 leads with exact quote or clearly labeled paraphrased position framing
- [ ] Beat 2 turn-number rule: turn references appear in the format *"In Turn N, you wrote: '...'"* when the quote is from a specific identifiable turn; turn numbers dropped when quote spans turns or is paraphrased; never used as heading style
- [ ] Beat 2 contains one alternative question or instrument
- [ ] Beat 2 mentions queued full breakdown counts but does NOT link to Observatory before Step 9
- [ ] Beat 2 does NOT contain anchor-list, structural-gaps line, or delivery-check line
- [ ] Beat 2 length 220–300 words (normal mode) OR 140–220 words (thin mode); hard cap 350
- [ ] Post-pipeline thin mode applied correctly: fires only when pre-pipeline thin was active OR all four audit-low-signal criteria are conjunctively true — never by orchestrator discretion
- [ ] Beat 3 §3 has 3–4 *shifts* as defined (a change to substantive advice the user would experience as different guidance); tail-additions like "one more thing" count against the cap if they change advice
- [ ] Beat 3 total length 550–800 words, hard cap 900
- [ ] Beat 3 anchor-naming invariant: every anchor named verbatim in §1, §2, or §3
- [ ] Beat 4 opens with counter-frame phrase ("one more angle" / "fresh read pushed on" / "two things the position softened"), NOT "mostly aligned"
- [ ] Beat 4 does not mention "sub-agents" or "lanes"; it attributes the argument, not the machinery
- [ ] Final close appears only after Step 9/10 and includes live Observatory link, memo path when present, total cost, and archive path
- [ ] No machinery leaks across all four beats
- [ ] No sales/product-marketing language ("compelling," "unlock," "powerful," "deep dive," "transform")
- [ ] No generic AI phrasing ("it is important to consider," "this highlights the need," "complex and nuanced," "valuable insights")
- [ ] Disk-staging from refactor still gone (no `lane*_prompt.txt` etc. in /tmp/)

### Phase 2 invariant checklist (memo changes)

- [ ] `result.json` contains `memo_orientation_narrative` and `memo_substantive_title` fields after Step 6c
- [ ] Memo `# Heading` is substantive (action-shaped), not category-shaped
- [ ] Memo orientation narrative present, 180–260 words, contains at least one exact quote from conversation
- [ ] Memo orientation narrative is a lens, not a sales lede and not a new verdict
- [ ] Memo Updated Position section trimmed when `revised_answer` > 600 words
- [ ] Backward compat: old archived runs (without new fields) render without error in old shape
- [ ] All curated sections (Findings, Mental Models, Frame Alternatives, Structural Gaps, Delivery Check, Pressure Check) still render

### Quality criteria (subjective, reader review)

- [ ] Beat 1 makes the user feel seen — quotes back the situation in their own words
- [ ] Beat 2 lands as counter-argument, not verdict
- [ ] Beat 3 doesn't pad; every shift earns its slot
- [ ] The run feels alive at natural boundaries even without true Step 3 streaming
- [ ] The voice is plainspoken and specific enough to feel product-grade, not report-grade
- [ ] Memo is meaningfully more vivid than the current dry section dump
- [ ] Memo orientation narrative makes the rest easier to enter without adding ungrounded claims

---

## 8. Decision criteria

**Phase 1 ships to merge if:** all 4 cases pass the structural checklist AND at least 3/4 pass the quality criteria, with no early Observatory link and no generic AI/report prose in the reviewed transcript.

**Phase 2 ships to merge if:** all 4 cases pass the structural checklist AND the memo reads substantively better than the current version on a reader-review pass.

**Either phase fails:** identify which rule wasn't internalized, strengthen the inline instruction, re-test that case only.

**Both phases fail repeatedly:** the rules need to be inline in SKILL.md rather than in references. Pull the spec back inline.

---

## 9. Reversibility

Same as the earlier refactor:

- All changes on `chore/skill-md-progressive-disclosure`.
- No `git push` until both phases pass.
- Each phase as separate commit (or commits) — bisectable.
- Backward compat in render_memo.py means old archived runs still render.
- If abandoned: `git reset` back to `3864688` (last validated commit).

---

## 10. Out of scope (intentional)

- Observatory changes (separate effort)
- Engine changes
- Other reference files (presentation-voice.md, anti-bullshit-doctrine.md, output-field-guide.md) — left alone
- True in-flight heartbeat/streaming during Step 3 (requires background execution/polling or run_pipeline.py status events; deferred unless §6.2 changes)
- Claude-rendered memo (full LLM rewrite of curated sections) — explicitly rejected; only the narrative section is Claude-written
