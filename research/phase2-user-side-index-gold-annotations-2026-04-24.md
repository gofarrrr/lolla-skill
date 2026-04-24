# Phase 2.0 — User-Side Index Gold Annotations

**Date:** 2026-04-24
**Purpose:** decide Phase 2 scope by manually annotating desired provenance on every user-side IR object the Phase 1 constructor emits from the 3 protected cases.
**Stop condition:** if annotations show most objects need extraction changes to be useful, we write a blocking memo rather than implementing Phase 2 blindly.

## Headline finding

**Zero of 20 extracted user-side objects have full-string exact substring support in their named source turn.**

That's not a measurement error. It's the current extraction layer's uniform behavior: every `live_constraint`, `dropped_thread`, and `original_framing` is a *summary paraphrase*, not a verbatim quote. The Phase 1 constructor's all-`turn_ref`-zero-`span` distribution wasn't noise — it's the extraction contract.

But there's nuance in the 3 protected cases. Many paraphrased objects contain **embedded core assertions** that *are* exact substrings of the source turn (often as short phrases like `"6 weeks"`, `"8 months runway"`, `"teenage stuff"`, `"60-65%"`). The extractor wraps these in a summary prefix (`"Launch timeline:"`, `"Family financial stakes:"`) and adds interpretive content (`"aligned with Q3 planning end"`, `"nearing high school"`) that's inference, not quote.

That pattern initially suggested a Phase 2 architectural option: layer evidence-span anchoring on top of paraphrased text. The later 10-case widening below supersedes that initial read and rejects implementation for now.

## Annotations

Format: one row per object, 3 cases × 5-7 objects each. Notation:
- **Text** is the extractor's exact string.
- **Source turn (declared)** is what the extraction JSON claims.
- **Source turn (actual)** is where the content actually lives after manual inspection — sometimes different from the declared turn.
- **Exact quote available** lists any verbatim substrings of the object text in any user turn.
- **Provenance tier** is the honest classification under Phase 1's taxonomy.
- **Phase 2 action** records the initial 3-case implementation instinct. These per-object action notes are retained for evidence history but are superseded by the 10-case widening and revised decision below.

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

## Ten-case widening

After PM review, this 3-case artifact was widened to the full 10-case corpus.
That wider check materially changed the recommendation.

| Measure | Count | % of 71 |
|---|---:|---:|
| Full-string span match | 1 | 1% |
| Has at least 1 evidence span (>=4 words) | 8 | 11% |
| No useful evidence span available | 63 | 89% |

Per-case breakdown:

| Case | Total objects | Full-string span | Has evidence span | No evidence span |
|---|---:|---:|---:|---:|
| `phd_research` | 7 | 0 | 3 | 4 |
| `friendship_money` | 6 | 0 | 1 | 5 |
| `multi_offer` | 8 | 0 | 1 | 7 |
| `oncologist` | 10 | 0 | 1 | 9 |
| `real_estate` | 9 | 1 | 1 | 8 |
| `user_has_plan` | 6 | 0 | 1 | 5 |
| `messy_three_problems` | 6 | 0 | 0 | 6 |
| `parenting_teen` | 6 | 0 | 0 | 6 |
| `startup_pivot` | 6 | 0 | 0 | 6 |
| `whistleblower` | 7 | 0 | 0 | 7 |

The 3-case result overestimated the value of algorithmic evidence spans. It
counted short fragments such as `"6 weeks"`, `"teenage stuff"`, and `"60-65%"`
as meaningful embedded assertions. At 10-case scale, with a safer >=4-word
threshold, useful evidence-span coverage falls to 11%.

More importantly, coverage collapses on the complex/high-value cases where
drill-back quality matters most:

- `messy_three_problems`: 0 / 6
- `parenting_teen`: 0 / 6
- `startup_pivot`: 0 / 6
- `whistleblower`: 0 / 7

## Superseded recommendation

The earlier recommendation in this artifact was:

> Add `evidence_spans: tuple[SpanRef, ...] = ()` to `UserIssueEvent` and
> `FrameAnchor`, then populate it algorithmically by finding multi-word
> substrings from object text in the source turn.

That recommendation is **rejected** after the 10-case widening.

Reasons:

- The full-corpus benefit is too small: 8 / 71 objects get useful span anchors.
- The benefit is concentrated in simpler cases, not the cases where fidelity is
  most valuable.
- A mostly-empty `evidence_spans` field risks false progress and future packet
  builder fallback clutter.
- Observatory or memo rendering could misread empty arrays as "missing evidence"
  rather than the honest outcome of paraphrase-first extraction.
- Phase 5 specialist extraction, or the first packet builder with a concrete
  consumer need, may want a different field shape.

## Revised decision

**No Phase 2 implementation PR now.**

Do not add dormant `evidence_spans` fields. Do not implement algorithmic
evidence-span search. Do not change extraction prompts, constructor behavior,
lane behavior, or output serialization for Phase 2.

Phase 2's no-code finding is:

- user-side context is recoverable from current extraction at `turn_ref` /
  `derivation` granularity
- current extraction is structurally paraphrase-first
- exact-span enrichment requires a real semantic quote producer
- the likely producer is Phase 5 specialist extraction, or a Phase 4 packet
  builder that proves a concrete use for quote-level anchors

## Falsification conditions

Revisit `evidence_spans` or an equivalent field only if one of these becomes
true:

- a stricter non-spurious matcher reaches roughly 35-40% useful coverage on the
  10-case corpus
- a semantic quote-selection pass emits exact user quotes at high precision
  within an approved cost budget
- a Phase 4 packet builder has a concrete consumer need for quote-level anchors
- Observatory or memo rendering has a clear UX that distinguishes "honest
  paraphrase" from "missing evidence"

## Next move

Move to Phase 3.0: assistant trajectory annotation/design gate.

Reason: assistant turns are raw source text, so stance candidates can be exact
assistant spans. The hard question shifts from "can we recover quote anchors
from paraphrased user-side extraction?" to "can reviewers agree on what counts
as a `StanceEvent` and which relation it has?"
