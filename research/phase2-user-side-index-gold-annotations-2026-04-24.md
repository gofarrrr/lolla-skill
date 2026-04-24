# Phase 2.0 — User-Side Index Gold Annotations

**Date:** 2026-04-24
**Purpose:** decide Phase 2 scope by manually annotating desired provenance on every user-side IR object the Phase 1 constructor emits from the 3 protected cases.
**Stop condition:** if annotations show most objects need extraction changes to be useful, we write a blocking memo rather than implementing Phase 2 blindly.

## Headline finding

**Zero of 20 extracted user-side objects have full-string exact substring support in their named source turn.**

That's not a measurement error. It's the current extraction layer's uniform behavior: every `live_constraint`, `dropped_thread`, and `original_framing` is a *summary paraphrase*, not a verbatim quote. The Phase 1 constructor's all-`turn_ref`-zero-`span` distribution wasn't noise — it's the extraction contract.

But there's nuance. Nearly every paraphrased object contains **embedded core assertions** that *are* exact substrings of the source turn (often as short phrases like `"6 weeks"`, `"8 months runway"`, `"teenage stuff"`, `"60-65%"`). The extractor wraps these in a summary prefix (`"Launch timeline:"`, `"Family financial stakes:"`) and adds interpretive content (`"aligned with Q3 planning end"`, `"nearing high school"`) that's inference, not quote.

This pattern opens a Phase 2 architectural option that doesn't require changing the extraction contract: **layer evidence-span anchoring on top of paraphrased text**. Discussed in §"Phase 2 scope options" below.

## Annotations

Format: one row per object, 3 cases × 5-7 objects each. Notation:
- **Text** is the extractor's exact string.
- **Source turn (declared)** is what the extraction JSON claims.
- **Source turn (actual)** is where the content actually lives after manual inspection — sometimes different from the declared turn.
- **Exact quote available** lists any verbatim substrings of the object text in any user turn.
- **Provenance tier** is the honest classification under Phase 1's taxonomy.
- **Phase 2 action** is what a reasonable implementation would do.

---

### `user_has_plan` (6 objects)

**P1.** `live_constraint` — "Pipeline: 4-5 informal network conversations, no signed commitments"
- Source turn (declared): 1 / Source turn (actual): **turn 2**
- Full-string exact match: ✗
- Exact substrings present in turn 2: `"Pipeline —"`, `"informal conversations with 4-5 former colleagues"`, `"if you were independent, we'd consider you"`, `"None of them have committed to actual engagements"`
- Provenance tier: **turn_ref_honest** (with wrong-turn attribution bug)
- Why: the content is verifiable in turn 2, but the extractor's phrasing ("Pipeline:", "no signed commitments") is paraphrase, not verbatim. Also: `introduced_turn=1` in the extraction is wrong — turn 1 doesn't mention pipeline; turn 2 does.
- Ambiguity: none
- **Phase 2 action:** (a) fix turn attribution to 2; (b) attach evidence_spans for the embedded quotes; (c) keep `text` as paraphrased summary.

**P2.** `live_constraint` — "Runway: 8 months at zero revenue"
- Source turn (declared): 1 / Source turn (actual): **both 1 and 2**
- Exact substrings present: turn 1 has `"I have 8 months runway saved"`; turn 2 has `"Runway —"`, `"8 months assumes zero revenue"`
- Provenance tier: **derivation** (synthesizes turn 1 + turn 2)
- Why: extractor's `"Runway: 8 months at zero revenue"` combines "Runway —" from turn 2 with "zero revenue" phrasing from turn 2, plus `"8 months"` verified in both turns.
- Ambiguity: none
- **Phase 2 action:** record as derivation with references to both turns; evidence_span `"8 months assumes zero revenue"` in turn 2.

**P3.** `live_constraint` — "Launch timeline: 6 weeks from now, aligned with Q3 planning end"
- Source turn (declared): 1 / Source turn (actual): **turn 1 + turn 2**
- Exact substrings present: turn 1 has `"Plan is to go independent starting in 6 weeks"`; turn 2 has `"6 weeks —"`, `"Q3 planning cycle ends mid-July"`, `"clean exit point"`
- Provenance tier: **derivation**
- Why: `"6 weeks"` and `"Q3 planning"` are from different turns; `"aligned with"` is extractor's connective.
- Ambiguity: none
- **Phase 2 action:** derivation with evidence_spans for both span fragments.

**P4.** `live_constraint` — "Spouse support: on board with concept, not specifics of financial pressure"
- Source turn (declared): 5 / Source turn (actual): 5 ✓
- Exact substrings present: `"Spouse is on board"` (close to "on board"), `"Hasn't been part of the runway discussion in specifics"`, `"I've kept that in my head"`
- Provenance tier: **turn_ref_honest**
- Why: content verified in turn 5; extractor paraphrases ("Spouse support:", "not specifics of financial pressure" is interpretive).
- Ambiguity: **constraint/concern** (matches annotation-gate item 4) — factual marital position + unresolved alignment issue.
- **Phase 2 action:** turn_ref with evidence_spans; kind_ambiguity=True flag.

**P5.** `dropped_thread` — "Tactical launch plan details (pricing, positioning, website, legal structure)"
- Source turn (declared): 1 (raised by user), acknowledged_then_dropped / superseded_by fundamentals
- Source turn (actual): turn 1 + turn 3
- Exact substrings present: turn 1 `"launch plan"`; turn 3 `"tactical advice on the launch plan"`; the enumeration `"(pricing, positioning, website, legal structure)"` is NOT in any user turn — it's the extractor's expansion of what "launch plan" typically contains.
- Provenance tier: **derivation** (the user's ask + extractor's expansion)
- Why: the user said "launch plan"; the specific enumeration is extractor inference about what that typically means.
- Ambiguity: none
- **Phase 2 action:** record as derivation; the enumeration shouldn't claim span provenance because the user didn't say those words.

**P6.** `original_framing` — "User seeks tactical launch plan for independent consulting starting in 6 weeks, assuming 8-month runway and network conversations as sufficient pipeline"
- Source turn: multi-turn synthesis (turn 1 + turn 2)
- Exact substrings present: `"starting in 6 weeks"` (turn 1), `"8-month runway"` (close to turn 1's "8 months runway"), fragments from turn 2
- Provenance tier: **derivation**
- Why: it's a synthesis across the first 2 user turns; extractor framing prose ("User seeks tactical launch plan for..." is structural paraphrase).
- Ambiguity: none
- **Phase 2 action:** derivation with references to contributing turns; no single-span provenance.

---

### `whistleblower` (7 objects)

**W1.** `live_constraint` — "Active regulatory audit on client account"
- Source turn (declared): 1 / actual: 1
- Exact substrings present: `"active audit"`, `"account is in active audit with a major regulato[r]"`
- Full-string match: ✗ (extractor says "regulatory audit"; user says "audit with a major regulator")
- Provenance tier: **turn_ref_honest**
- Ambiguity: none
- **Phase 2 action:** turn_ref; evidence_span `"active audit with a major regulator"`.

**W2.** `live_constraint` — "Senior partner shredding 3 boxes of financial docs/emails at 6am non-shred location"
- Source turn: 1
- Exact substrings present: `"6am"`, `"senior partner shredding documents"`, `"multiple boxes"`, `"non-shred-room location"` (note: extractor says "non-shred location"; user says "non-shred-room location")
- Provenance tier: **turn_ref_honest**
- Ambiguity: none
- **Phase 2 action:** turn_ref with multiple evidence_spans for each verified fragment.

**W3.** `live_constraint` — "60-65% confidence in general counsel handling"
- Source turn: 6
- Exact substrings present: `"I'd say 60-65%"`; `"general counsel"` (from turn 5)
- Provenance tier: **turn_ref_honest** (the number is verified; the "confidence in... handling" framing is extractor's interpretation of what the 60-65% refers to).
- Ambiguity: none substantive (annotation exercise marked constraint)
- **Phase 2 action:** turn_ref; evidence_span for "60-65%".

**W4.** `live_constraint` — "Family financial stakes: mortgage, two kids nearing high school"
- Source turn: 4
- Exact substrings present: `"mortgage, two kids"`, `"about to start high school"`; "nearing" is extractor's substitution for user's "about to start"
- Provenance tier: **turn_ref_honest**
- Ambiguity: none
- **Phase 2 action:** turn_ref; evidence_span for `"mortgage, two kids"`.

**W5.** `dropped_thread` — "Legitimate explanations for shredding (duplicates, personal work)" — **raised by assistant**
- Source turn (declared): 2, raised_by assistant, acknowledged_then_dropped / superseded by obstruction focus
- **This is not actually user-side content.** It's an assistant-raised alternative hypothesis that was dropped. The Phase 1 constructor emits this as `UserIssueEvent` but it's really an *assistant-raised concern* (or dropped_thread from assistant speech).
- Provenance tier: **turn_ref_honest** (content is in turn 2 assistant text, not any user turn)
- Ambiguity: the **object family itself** is ambiguous — is `UserIssueEvent` the right home for assistant-raised threads?
- **Phase 2 action:** recommend either (a) renaming to `IssueEvent` with a `raised_by` field, or (b) promoting assistant-raised threads into Phase 3's assistant-trajectory objects. For Phase 2 narrow scope, leave as-is but flag the taxonomy ambiguity.

**W6.** `dropped_thread` — "Internal reporting to trusted general counsel/audit committee" — raised by user turn 5, superseded
- Source turn: 5
- Exact substrings present: `"internal reporting"`, `"I trust our general counsel"`, `"audit committee"`, `"a direct line to the audit committee"`
- Provenance tier: **turn_ref_honest** (good core assertion support)
- Ambiguity: none
- **Phase 2 action:** turn_ref with evidence_spans for each fragment; lifecycle fields preserved (raised_turn=5, status=acknowledged_then_dropped, superseded_by present).

**W7.** `original_framing` — "User seeks advice on whether to report senior partner's suspicious early-morning shredding of client documents during active regulatory audit, assuming..."
- Source turn: multi-turn (primarily turn 1)
- Exact substrings present: `"senior partner shredding documents"`, `"active audit with a major regulator"`, `"6am"`
- Provenance tier: **derivation**
- Ambiguity: none
- **Phase 2 action:** derivation; evidence_spans for verified fragments.

---

### `parenting_teen` (7 objects)

**T1.** `live_constraint` — "Daughter shut down, avoiding mother for 4 days"
- Source turn (declared): 1 / actual: 1 + later turns
- Exact substrings present: turn 1 `"she just shut down completely"`, `"Won't come out of her room"`; "4 days" — needs search across later turns
- Provenance tier: **derivation** (turn 1 + "4 days" likely elsewhere)
- Ambiguity: annotation exercise marked concern (not constraint); constructor emits as constraint. kind_ambiguity=True.
- **Phase 2 action:** derivation with evidence_spans; kind_ambiguity flag set.

**T2.** `live_constraint` — "Divorced co-parent minimizing situation as 'teenage stuff'"
- Source turn: 1
- Exact substrings present: `"we're divorced, share custody"`, `"teenage stuff"` (both exact in turn 1)
- Provenance tier: **turn_ref_honest**
- Ambiguity: none (annotation exercise: constraint)
- **Phase 2 action:** turn_ref; evidence_spans for the two fragments.

**T3.** `live_constraint` — "Ongoing secret phone surveillance for months"
- Source turn: 5
- Exact substrings present: `"going through her phone for months"`, `"She doesn't know this"`
- Provenance tier: **turn_ref_honest**
- Ambiguity: **constraint/concern** (user's own self-acknowledged ethical unease — "I know, I know"). kind_ambiguity=True.
- **Phase 2 action:** turn_ref; kind_ambiguity flag; evidence_spans.

**T4.** `live_constraint` — "RAINN: reporting viable but risks legal process, witness trauma, jurisdictional issues"
- Source turn: 7
- Exact substrings present: `"legal case"`, `"she becomes a witness"`, `"jurisdictional stuff is complicated"`
- Provenance tier: **turn_ref_honest** (with multiple evidence spans)
- Ambiguity: **constraint/concern** (information integrated into decision model AND active unresolved risks). kind_ambiguity=True.
- **Phase 2 action:** turn_ref; kind_ambiguity flag; evidence_spans for the three verified fragments.

**T5.** `dropped_thread` — "Should I block the 19-year-old or take the phone?" — raised by user turn 3, superseded
- Source turn: 3
- Exact substrings present: `"do I take it?"`, `"Do I block him?"`, `"19-year-old guy"` (from turn 1), `"take the phone"` — not exact; user said "take it"
- Provenance tier: **turn_ref_honest** / **derivation** (combines turn 3 with 19-year-old reference from turn 1)
- Ambiguity: none
- **Phase 2 action:** derivation; evidence_spans for verified fragments.

**T6.** `dropped_thread` — "Calling Mia's mom about potential similar risk" — raised by user turn 9, superseded
- Source turn: 9
- Exact substrings present: `"Do I call Mia's mom?"`, `"what if Mia is in a similar situation"`
- Provenance tier: **turn_ref_honest**
- Ambiguity: none
- **Phase 2 action:** turn_ref; evidence_spans.

**T7.** `original_framing` — "Mother seeks advice on handling daughter's secret Instagram use and intimate DMs with 19-year-old..."
- Source turn: multi-turn (primarily turn 1)
- Exact substrings present: `"19-year-old guy"`, fragments of turn 1
- Provenance tier: **derivation**
- Ambiguity: none
- **Phase 2 action:** derivation.

---

## Scoring

| Bucket | Count | % of 20 |
|---|---:|---:|
| **span_ready** (extraction text is a full exact substring of declared source turn) | **0** | 0% |
| **turn_ref_honest** (paraphrased, source turn verified, core assertions embedded as evidence_spans) | **12** | 60% |
| **derivation** (multi-turn synthesis, no single source turn owns the full text) | **8** | 40% |
| **needs_specialist_extraction** (content cannot be recovered from current fields) | 0 | 0% |

The annotation reveals no objects unrecoverable from current extraction, but also no objects that are cleanly span-backed under the current contract. The 60/40 split between turn_ref and derivation mirrors the actual extraction behavior: simple single-turn assertions get summarized into `turn_ref`, multi-turn syntheses become `derivation`.

**Important secondary finding:** at least 1 of the 20 objects has a **turn attribution bug** (user_has_plan P1 — extraction says introduced_turn=1, actual source is turn 2). This is not a Phase 2 architectural issue but a latent extraction-correctness issue worth flagging.

**Secondary finding #2:** 1 of the 20 objects (whistleblower W5) is an **assistant-raised dropped_thread** classified as `UserIssueEvent`. The Phase 1 constructor doesn't distinguish raised_by for UserIssueEvent. Flag as latent taxonomy issue for Phase 3 or a later cleanup; not a Phase 2 blocker.

**Secondary finding #3:** 4 of the 20 objects have `kind_ambiguity` between `constraint` and `concern` (P4 spouse, T1 daughter-shutdown, T3 surveillance, T4 RAINN). This matches the annotation-gate result (3 of 17 previously identified; slightly higher here because we included T1 which was judged ambiguous this pass). The `kind_ambiguity` flag added in Phase 1 is the designed handling.

## Phase 2 scope options

**Option A — Layered evidence spans.** Phase 2's key addition: objects keep `text` (paraphrased) + `provenance tier` (turn_ref/derivation) but gain an **optional `evidence_spans: list[SpanRef]`** that lists verified verbatim substrings from source turns. The constructor algorithmically finds these by searching each object's text for multi-word substrings (e.g., ≥4 words) that appear case-tolerantly in the declared source turn.

Benefits:
- **No extraction contract change.** The old monolithic extractor keeps working.
- **Provides real drill-back granularity** even while text is paraphrased. Observatory / memo rendering / lane packets (Phase 4) can highlight the actual user quotes that support each object.
- **Self-documenting**: if an object has 0 evidence_spans, that's honest signal that it's pure paraphrase or multi-turn derivation, not verbatim quote.
- **Addresses the turn-attribution bug naturally**: if evidence_spans come back empty for the declared turn but non-empty for a different turn, the constructor can flag or self-correct.

Costs:
- Slightly more complex IR shape (extra optional field).
- Algorithmic substring search needs to be robust to case-folding (already have `find_substring_tolerant`), whitespace normalization, and the "short match = likely spurious" boundary.

**Option B — Leave as-is, wait for Phase 5.** Phase 2 does NOT add evidence_spans. Provenance stays turn_ref/derivation with no span-level enrichment. Phase 5 specialist extraction eventually emits fields designed for exact-span representation.

Benefits:
- Smallest scope.
- No algorithmic span-search complexity.

Costs:
- Observatory drill-back stays coarse (whole-turn granularity).
- Phase 4 packet builders have less to project.
- We know Phase 5 is at least months away; waiting loses ground.

**Option C — Add evidence_spans AND fix the known bugs.** Option A + the turn-attribution bug fix + the assistant-raised dropped_thread taxonomy cleanup.

Benefits:
- Addresses multiple findings at once.
- Self-correcting constructor (evidence_spans empty on declared turn → try other turns).

Costs:
- Scope creep risk — once we start "fixing bugs in the constructor" the scope expands.

## Phase 2 recommendation

**Option A, tightly scoped.** Add `evidence_spans: tuple[SpanRef, ...] = ()` to UserIssueEvent and FrameAnchor. Constructor algorithmically finds multi-word substrings of the object's text (≥4 consecutive words matching case-tolerantly) in the declared source turn. If found, attach as evidence_spans. If not found, leave empty.

Do NOT:
- Change the extraction prompt or contract
- Fix the turn-attribution bug in the constructor itself (surface it in logs but don't silently rewrite turns)
- Reclassify assistant-raised dropped_threads
- Implement packet builders
- Add evidence_spans to StanceEvent (separate concern, Phase 3)

This gives us:
- A 60% bump in drill-back granularity without touching extraction
- An honest signal for the 40% that remain turn_ref/derivation-only
- Phase 3's assistant-side work unaffected
- Phase 5's eventual specialist extraction can emit primary `span` provenance cleanly, with the Phase 2 algorithmic fallback remaining as resilience

## Kill criteria for Phase 2

- If the multi-word-substring search proves unreliable (too many false positives where a common phrase like "the advice" matches coincidentally), narrow the minimum match length or add stopword filtering before shipping.
- If Observatory/memo rendering can't meaningfully consume `evidence_spans` (unclear visual story, user confusion), defer until Phase 4 packet builders have a use for it.
- If the algorithmic search pattern starts looking brittle across new cases added to the corpus, defer and wait for Phase 5.

## Phase 2 task file outline (to be drafted after PM review)

1. Add `evidence_spans` field to `UserIssueEvent` and `FrameAnchor`
2. Implement multi-word substring search helper (≥4 words, case-tolerant, whitespace-normalized)
3. Extend `ir_constructor.py` to populate `evidence_spans` on build
4. Extend `test_ir.py` for evidence_spans field presence + absence cases
5. Extend `test_ir_drillback.py` for evidence_span-based drill-back
6. Add provenance observability counter: how many objects got ≥1 evidence_span vs 0
7. Update HOW_IT_WORKS with a brief evidence_spans paragraph
8. Acceptance note with before/after provenance distribution on the 3 fixtures

Expected Phase 2 delivery size: ~half the size of Phase 1. One PR, one branch, ~1-2 days of coder work.

## Summary for PM go/no-go

- **Go:** Phase 2 is scoped, useful, non-extraction-changing, and builds on Phase 1 cleanly. Option A above.
- **No-go would mean:** skip Phase 2, go straight to Phase 3 or Phase 5. Cost: we lose the opportunity to add drill-back granularity from current extraction without waiting for specialist extraction.

Recommend: Go. Option A as the Phase 2 shape.
